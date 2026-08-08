# Instrução para IA — Sistema de Revisão Interativa com FSRS v5

Este arquivo é auto-suficiente. Qualquer modelo de IA (Claude, GPT, Gemini, etc.) pode lê-lo e conduzir uma sessão de revisão interativa neste projeto.

> **Você não escreve no banco digitando SQL.** Toda leitura e toda escrita em
> `estudo/progresso/srs.db` passa por **`scripts/revisar.py`**. A fórmula do FSRS-5, os
> 19 pesos, o dedupe e as travas de idempotência vivem lá — testados uma vez, chamados
> por linha de comando. Isso existe para que o resultado seja o mesmo **independente de
> qual agente ou modelo** conduzir a sessão: um snippet retranscrito na hora é um snippet
> que uma hora sai errado (ver `docs/MANUAL.md` §6.3 — o bug do `W[15]` zerado, que
> congelava para sempre todo card avaliado com rating 2, nasceu exatamente assim).
>
> **O que continua sendo seu:** conduzir o cloze, escolher a lacuna, decidir quando a
> dica entra, julgar a resposta e atribuir o rating. Isso é julgamento — não dá para
> virar script. O resto é mecânica, e mecânica é código.

---

## Contexto

O aluno (perfil completo em `estudo/PERFIL.md`) usa este sistema de revisão assim:

1. A IA busca os flashcards vencidos (`revisar.py pendentes`)
2. Pergunta um card por vez — em **cloze progressivo**, no tamanho de lacuna do nível de rigor
3. O aluno completa a lacuna com suas próprias palavras
4. A IA avalia a resposta e atribui um rating 1-4
5. A IA grava a revisão (`revisar.py revisar`) — o script calcula o FSRS e o próximo intervalo
6. Repete até acabar os cards devidos

**Estilo:** direto, técnico, sem enrolação. Valide respostas com precisão — o objetivo é retenção real, não aprovação fácil.

**Rigor:** o nível (1 a 4) vem de `estudo/PERFIL.md` (ou do campo `rigor:` do ledger da matéria, que tem precedência). A escala completa está em [`METODOS_DE_ENSINO.md`](METODOS_DE_ENSINO.md) §2 e define três coisas: quanta lacuna o card mostra, quando a dica entra, e quão severo é o rating.

---

## Os comandos

```bash
python3 scripts/revisar.py pendentes                 # fila de hoje, intercalada por tópico
python3 scripts/revisar.py pendentes --reentrada     # teto de 8, maior estabilidade primeiro
python3 scripts/revisar.py pendentes --json          # mesma fila, com front/back, para você ler

python3 scripts/revisar.py revisar --card-id 12 --rating 3 \
    --confianca 2 --tentativas 1 --usou-dica 0 --tipo-item recall

python3 scripts/revisar.py criar --front "..." --back "..." \
    --deck "Estudos::<Materia>::<Topico>" --subject "<Matéria>" --tags "<materia>,<topico>"
python3 scripts/revisar.py criar --json novos.json   # lote

python3 scripts/revisar.py espalhar --dias 5 --confirmar
```

**Garantias que o script dá e que você não precisa reimplementar:**

| Garantia | Como |
|---|---|
| Revisar o mesmo card 2× no mesmo dia não duplica nada | `revisar` checa o `review_log` do dia e sai avisando, sem alterar o card |
| Criar o mesmo card 2× não duplica | `criar` deduplica por `front` e reporta quantos pulou |
| Espalhar backlog nunca acontece por acidente | `espalhar` sem `--confirmar` recusa e explica |
| O banco existe e está migrado | `abrir_db()` aplica o esquema e as colunas novas sozinho |
| Escrita parcial não corrompe | `UPDATE cards` + `INSERT review_log` num commit só, com rollback |

Nenhum comando pede caminho de banco: todos usam `estudo/progresso/srs.db`.

---

## Banco de dados

**Arquivo:** `estudo/progresso/srs.db` (SQLite). Esquema completo em `templates/srs_schema.sql`.

**Tabela `cards`:**

| coluna      | tipo    | descrição                                              |
|-------------|---------|--------------------------------------------------------|
| id          | INTEGER | chave primária                                         |
| front       | TEXT    | pergunta mostrada ao aluno                             |
| back        | TEXT    | resposta correta (a IA vê, o aluno não vê antes)      |
| tags        | TEXT    | JSON array de tags: `["<materia>","<topico>"]`               |
| deck        | TEXT    | nome do deck: `Estudos::<Materia>::<Topico>`   |
| subject     | TEXT    | matéria: `"<Matéria>"`                   |
| state       | INTEGER | 0=New 1=Learning 2=Review 3=Relearning                |
| difficulty  | REAL    | dificuldade FSRS (1-10, começa em 0 para New)         |
| stability   | REAL    | estabilidade FSRS em dias (0 para New)                |
| due_date    | TEXT    | data de vencimento ISO: `"2026-07-18"`                |
| last_review | TEXT    | data da última revisão (NULL se nunca revisado)       |
| reps        | INTEGER | total de revisões                                     |
| lapses      | INTEGER | total de erros (rating=1)                             |

**Tabela `review_log`:** o resultado **e o contexto** de cada revisão — `card_id`, `review_date`, `rating`, `elapsed_days`, `interval_days`, `stability`, `difficulty`, `state`, mais `confianca`, `tentativas`, `usou_dica` e `tipo_item` (§6).

Leitura só de consulta (estatística, auditoria) pode ser feita direto com `sqlite3`, à vontade. **Escrita, nunca** — use os comandos.

---

## Passo a passo da sessão

### 0. Pergunte quem conduz — antes de qualquer card

Toda revisão (e todo recall de Fase 3) começa com a mesma pergunta ao aluno:

> *"Quer fazer a revisão comigo aqui, ou prefere que eu gere um prompt para você fazer com um agente externo e depois me trazer o resultado?"*

A escolha é dele, sempre — não presuma nenhuma das duas. Se ele escolher o agente externo, gere o prompt a partir de [`templates/recall-externo.md`](templates/recall-externo.md) e salve em `estudo/atividades/`.

**O que a via externa NÃO muda:** os cards já precisam existir no banco (o resultado volta por `card_id`), a régua do rigor vai escrita dentro do prompt, e **a escrita continua sendo sua** — `revisar.py revisar` card a card, com os mesmos campos. Ao receber o bloco, confira a coerência: `usou_dica=1` com rating acima de 2 é erro do agente externo, rebaixe para 2 e avise o aluno.

### 1. Buscar cards devidos

```bash
python3 scripts/revisar.py pendentes --json
```

Devolve a lista com `id`, `front`, `back`, `deck`, `state`, `difficulty`, `stability` — já **intercalada por tópico** (§"Fila intercalada"). Lista vazia: diga ao aluno que não há revisões pendentes e sugira conteúdo novo.

#### 1b. Modo reentrada — quando o aluno volta depois de sumir

`python3 scripts/status.py` dispara este modo sozinho quando faz **10+ dias** sem sessão **ou** o backlog passa de **15 cards**. Não ignore o aviso — nesse caso a fila vem de:

```bash
python3 scripts/revisar.py pendentes --reentrada --json
```

A sessão de volta é a mais frágil de todas: quem some três semanas volta e erra muito, porque três semanas sem revisar é exatamente o desenho do esquecimento. Se a primeira sessão de retorno for uma demonstração de fracasso, não há segunda. **O objetivo dela é reacender o hábito, não quitar a dívida.**

O que muda:

| | Sessão normal | Modo reentrada |
|---|---|---|
| Quantidade | até 20 cards | **teto de 8** (`--reentrada`) |
| Ordem | intercalada por tópico | **maior estabilidade primeiro** — os que ele ainda acerta |
| Conteúdo novo | permitido depois da revisão | **nenhum** |
| Dica | conforme o nível de rigor | **1 tentativa antes do normal** |
| Régua do rating | conforme o nível | **inalterada** |

> **Por que a régua não muda.** Seria tentador baixar o rigor na volta para o aluno se sentir melhor. Isso infla o rating, que infla o intervalo, que esconde a lacuna — o problema volta maior daqui a duas semanas. Adiantar a dica dá o mesmo alívio **sem mentir para o agendamento**: a dica já limita o rating a 2, então o FSRS recebe exatamente o sinal correto, "lembrou com ajuda".

Abra dizendo o que está acontecendo. Algo como: *"você sumiu 23 dias e tem 41 cards vencidos. Não vamos ver os 41 hoje — vamos ver 8, começando pelos que você provavelmente ainda sabe."*

#### 1c. Espalhar o backlog — só com autorização

Ao fim de uma sessão de reentrada, **ofereça** redistribuir o que sobrou pelos próximos dias. Nunca faça sozinho: `due_date` é a fonte da verdade do progresso, e reescrevê-la sem o aluno mandar contradiz o princípio central do sistema.

```bash
# Só rode depois de um "pode espalhar" explícito. Sem --confirmar o comando recusa.
python3 scripts/revisar.py espalhar --dias 5 --confirmar
```

Mexe apenas em `due_date` — `stability` e `difficulty` ficam intactas, então o modelo FSRS não é corrompido, só a fila é reordenada no tempo.

Registre no `## Log de aprendizado` do ledger que houve redistribuição, com a data e a quantidade.

### 2. Para cada card — apresentar em cloze

Mostrar apenas o `front`, reescrito como **texto lacunado** no tamanho do nível de rigor. NÃO mostrar o `back` antes da resposta.

```
N1  uma palavra lacunada num parágrafo inteiro
N2  várias lacunas curtas na mesma frase
N3  a lacuna é uma justificativa inteira, ancorada no contexto real do aluno
N4  só o cenário é dado; a lacuna é o diagnóstico completo + defesa sob contestação
```

### 2b. Perguntar a confiança — ANTES de revelar

```
Antes de eu te dizer: você acha que acertou essa?
  (a) vou acertar   (b) mais ou menos   (c) não vou acertar
```

Guarde para passar em `--confianca` como **2 / 1 / 0**. Este passo não é formalidade: é a única parte do protocolo que treina o aluno a **julgar o próprio conhecimento** — a competência que ele vai precisar exercer sozinho quando não houver tutor. Sem previsão registrada não há como medir calibração depois.

### 3. Aguardar resposta do aluno

O aluno completa a lacuna com as próprias palavras.

**Contestação (obrigatória em N4):** antes de aceitar a resposta, devolva uma pergunta que force reconsiderar ("tem certeza? por quê? o que muda se X?") — **zero conteúdo novo**, só pergunta. Contestação não é dica: mesmo que o aluno precise de várias rodadas para sustentar ou completar a resposta, se nada foi revelado por você, ele chegou sozinho e a régua normal do rating vale (pode ser 3 ou 4). Só vira dica no momento em que você entrega um termo, uma categoria ou parte do raciocínio.

**Dica:** existe em todos os níveis. Ela **devolve contexto** (rebaixa a questão um nível: N4→N3, N3→N2, N2→N1) e nunca entrega a resposta. Quando entra: N1 ao primeiro sinal de hesitação, N2 após 1 tentativa, N3 e N4 após 2.

### 4. Avaliar e atribuir rating

Compare a resposta do aluno com o `back` usando julgamento de IA:

| rating | quando usar                                                     |
|--------|-----------------------------------------------------------------|
| 1      | Errou completamente, em branco, ou confundiu com outro conceito |
| 2      | Lembrou a ideia geral mas faltou nome técnico ou detalhe chave  |
| 3      | Resposta correta com algum esforço ou pequena imprecisão        |
| 4      | Correto, preciso e instantâneo — sem hesitação                  |

**A barra do rating 3 (domínio) sobe com o nível de rigor:**

| | vale 3 quando… | imprecisão terminológica |
|---|---|---|
| **N1** | acertou a ideia central | não penaliza |
| **N2** | acertou a ideia **e** o nome técnico | derruba para 2 |
| **N3** | nome + exemplo + distinção do conceito vizinho, sem dica | derruba para 2 |
| **N4** | sustentou o diagnóstico sob contestação, sem dica | derruba para 1 |

> **Regra fixa em qualquer nível: acerto após dica vale no máximo rating 2.** Lembrou com apoio não é lembrar sozinho — e o espaçamento precisa refletir isso para não inflar o intervalo.

### 5. Gravar a revisão

Um comando. Ele calcula o FSRS-5, atualiza `cards` e insere em `review_log` na mesma transação, e imprime a próxima data.

```bash
python3 scripts/revisar.py revisar --card-id 12 --rating 3 \
    --confianca 2 --tentativas 1 --usou-dica 0 --tipo-item recall
```

| flag | valor |
|---|---|
| `--card-id` | o `id` que veio de `pendentes` |
| `--rating` | 1 · 2 · 3 · 4 conforme §4 |
| `--confianca` | 2 = vou acertar · 1 = mais ou menos · 0 = não vou acertar (§2b) |
| `--tentativas` | quantas vezes o aluno tentou antes de fechar |
| `--usou-dica` | 0 ou 1 — dica limita a nota a 2 |
| `--tipo-item` | `recall` · `intercalado` · `sintese` · `transferencia` · `portao` |

Se você rodar o mesmo card duas vezes no mesmo dia, o script avisa e **não altera nada** — não recalcula o FSRS nem duplica a linha do log. Pode chamar sem medo depois de uma interrupção de sessão.

> **As quatro últimas flags não são opcionais.** `confianca` alimenta o relatório de calibração. `tentativas` e `usou_dica` são **fatos objetivos ao lado de um julgamento subjetivo**: se a proporção de notas 3 e 4 subir ao longo do tempo sem que o uso de dica caia, a avaliação afrouxou — e essa é a única forma de perceber. `tipo_item` mede se as cotas de intercalação e transferência estão sendo cumpridas de verdade.

### 6. Feedback ao aluno

Após cada card, mostrar:
- Se acertou: breve confirmação + o que foi bem
- Se errou/parcial: correção precisa + o que estava faltando
- Próxima revisão: a data e o intervalo que o comando imprimiu

Ao final da sessão: resumo com total de cards revisados, % de acerto, e os pontos fracos que surgiram.

---

## Adicionar cards novos ao banco

Durante o ensino de conteúdo novo, a IA salva cards com:

```bash
python3 scripts/revisar.py criar \
    --front "Pergunta aqui" --back "Resposta aqui" \
    --tags "<materia>,<topico>" \
    --deck "Estudos::<Materia>::<Topico>" --subject "<Matéria>"
```

Em lote, escreva um JSON com uma lista de objetos e passe o arquivo:

```json
[
  {"front": "...", "back": "...", "tags": ["<materia>","<topico>"],
   "deck": "Estudos::<Materia>::<Topico>", "subject": "<Matéria>"}
]
```

```bash
python3 scripts/revisar.py criar --json novos.json
```

O dedupe por `front` é automático — o comando reporta quantos adicionou e quantos pulou. Rodar o mesmo lote duas vezes é seguro.

---

## Variar cards já dominados

Quando um card recebe **rating 4** numa revisão, ou um tópico é marcado `dominado` no
ledger, gere **até 2 cards variantes** do mesmo conceito — mesma resposta correta,
cenário/fraseado diferente do original. O objetivo é reforçar sem deixar o aluno
decorar a redação literal do `front` em vez do conceito.

> **O card original NUNCA é removido nem substituído.** Ele continua na fila normal
> de repetição espaçada, com seu próprio `due_date`/`stability`, exatamente como
> antes. Os variantes são cards **novos e independentes**, adicionados ao lado dele —
> a ideia é ter 3 ângulos do mesmo conceito circulando no SRS, não trocar 1 por 1.
> Se um variante falhar mesmo com o original dominado, é sinal de que a lacuna era
> de redação/decoreba, não do conceito.

- Variante muda o **cenário de superfície** (outro setor, outro exemplo), não o
  conceito nem a resposta certa.
- Respeite o teto de 2 — mais que isso infla o banco sem ganho de retenção.
- Crie com `revisar.py criar` como qualquer outro card; o dedupe por `front` já vale.
- Registre a origem: `--tags` da variante inclui o mesmo tópico do card original, para
  o relatório de calibração conseguir agrupá-los.

---

## Ver estatísticas rápidas

```bash
python3 scripts/status.py
```

Estado geral do estudo, backlog, gatilho de reentrada e **por onde a sessão começa**. É o passo zero de toda sessão — não improvise por cima dele.

---

## Fila intercalada — a ordem importa

```bash
python3 scripts/revisar.py pendentes      # já vem intercalada
python3 scripts/status.py --fila          # mesma fila, na visão do status
```

A fila crua (`ORDER BY state DESC, due_date ASC`) tende a **agrupar** cards do mesmo tópico, porque cards do mesmo tópico foram criados juntos e vencem juntos. Isso é prática em bloco: o aluno responde no piloto automático, porque só existe um conceito em jogo.

A fila intercalada faz rodízio entre os decks, alternando tópicos. **Mesma quantidade de trabalho**, distribuída de forma a obrigar o aluno a decidir *qual* conceito se aplica — que é o que treina discriminação. O `pendentes` já aplica isso sozinho.

> Exceção: em **modo reentrada** (`--reentrada`) a ordem é por maior estabilidade (§1b). Ali o objetivo é reacender o hábito, e empilhar dificuldade em cima de quem já está fragilizado pela ausência é o caminho errado.

---

## Calibração: o aluno sabe o que não sabe?

```bash
python3 scripts/status.py --calibracao
```

Cruza a **previsão** do aluno (§2b) com o resultado real, e devolve **dois números que medem coisas diferentes**:

| Número | O que diz |
|---|---|
| **Erro de calibração** | o quanto a previsão erra, em qualquer direção (magnitude) |
| **Viés** | para que lado ela erra — excesso ou falta de confiança (direção) |

Manter os dois separados é necessário: somar desvios com sinal faz o excesso numa faixa cancelar a falta em outra, e um aluno que erra 25% para cima e 30% para baixo apareceria como bem calibrado. **Erro alto com viés perto de zero é o pior caso** — não há correção simples, porque a sensação de saber tem pouca relação com o que se sabe.

O relatório termina listando os **acertos previstos que deram errado**. É a lista mais importante do sistema: ali mora o que o aluno não sabe que não sabe.

Ao fim de cada recall, devolva o desencontro em uma linha, sem sermão:

> *"Você previu acerto em 6 e acertou 4. Nos dois que errou, estava confiante — e os dois eram sobre \<tema\>."*

---

## Performance: tempo cruzado com retenção

```bash
python3 scripts/status.py --performance
```

A tabela `study_sessions` guarda o tempo cronometrado por `scripts/sessao.py`. **Ela nunca é lida sozinha.** Minuto isolado mede esforço, não aprendizado — celebrar "2h de estudo hoje" é exatamente a armadilha de medir engajamento no lugar de retenção, que o resto deste sistema existe para evitar.

A leitura correta cruza tempo com o `review_log` da mesma data, e é o que o `--performance` faz: minutos do dia, quantos cards foram revisados e quantos ficaram (rating ≥ 3).

> **Sessões interrompidas ficam de fora.** Quando o aluno esquece de fechar a sessão, o script a encerra no dia seguinte com duração não confiável. Incluir essas linhas infla a contagem de sessões e polui o custo médio — o número passa a medir esquecimento em vez de estudo.

O número que interessa é **minutos por conceito retido**. Ele responde perguntas acionáveis:

- O custo sobe depois do segundo bloco? → a sessão está longa demais para este aluno.
- Blocos de 50 min custam menos por conceito que os de 25? → ajuste o **Bloco de foco** no `PERFIL.md`.
- O custo disparou nesta matéria? → o material está mal recortado ou a etapa está grande demais.

Precisa de algumas semanas de dado para dizer qualquer coisa. Antes disso, mostre a tabela mas **não tire conclusão** — n pequeno em série temporal é ruído com aparência de tendência.

---

## Notas importantes

- **Nunca** escreva no `srs.db` por fora do `revisar.py` — nem com `sqlite3` inline, nem com Python na hora. Consulta pode; escrita, não.
- **Nunca** mostrar o `back` antes do aluno responder
- Se um comando falhar, **não contorne escrevendo SQL** — reporte o erro ao aluno. Um contorno improvisado é exatamente o que o script existe para evitar.
- Em caso de dúvida no rating, pedir ao aluno para reformular — o objetivo é calibração honesta
- Siga as preferências do `estudo/PERFIL.md` (por padrão: perguntas que exijam nome técnico + exemplo concreto + distinção entre conceitos parecidos — não só a ideia geral)
