# Manual do Sistema de Aprendizagem Inteligente

> **O que é este documento.** A referência completa do sistema: o que ele faz, como está
> estruturado, **por que cada decisão foi tomada** e qual evidência a sustenta, como operá-lo,
> e onde ele ainda está devendo.
>
> **Para quem.** Para quem vai usar o sistema a sério e quer entender o mecanismo, não só a
> interface — e para quem quer encontrar pontos de melhoria com fundamento. A Parte VII existe
> especificamente para isso.
>
> Versão do sistema descrita: `97f342e`.

---

## Índice

- **Parte I — [O que é e por que existe](#parte-i--o-que-é-e-por-que-existe)**
- **Parte II — [Fundamentos: por que funciona assim](#parte-ii--fundamentos-por-que-funciona-assim)**
- **Parte III — [Arquitetura](#parte-iii--arquitetura)**
- **Parte IV — [Operação](#parte-iv--operação)**
- **Parte V — [Configuração](#parte-v--configuração)**
- **Parte VI — [Como o sistema foi avaliado](#parte-vi--como-o-sistema-foi-avaliado)**
- **Parte VII — [Pontos em aberto e como investigá-los](#parte-vii--pontos-em-aberto-e-como-investigá-los)**
- **Apêndices** — [Glossário](#apêndice-a--glossário) · [Referências](#apêndice-b--referências) · [Comandos](#apêndice-c--comandos)

---

# Parte I — O que é e por que existe

## 1.1 O problema

Estudar sozinho falha por três motivos previsíveis, e nenhum deles é falta de material:

1. **Consumo passivo parece estudo.** Ler, assistir, ouvir e grifar produzem forte sensação de
   domínio e pouca retenção. A sensação é o problema — ela desliga o esforço justamente quando
   ele seria produtivo.
2. **Sem espaçamento, tudo evapora.** Conteúdo revisto uma vez desaparece em semanas. O intervalo
   certo entre revisões não é intuitivo e depende de quanto tempo você precisa lembrar.
3. **O autodidata não sabe o que não sabe.** Sozinho, ele decide o que revisar pela sensação de
   saber — que é enviesada para cima exatamente nos conteúdos mal aprendidos.

Ferramentas de IA resolvem bem o primeiro terço do problema (gerar material) e agravam os outros
dois, porque produzem material infinito e agradável de consumir.

## 1.2 A proposta

Um **tutor orquestrador** que separa três papéis e não deixa nenhum invadir o outro:

| Peça | Papel | Por que ela |
|---|---|---|
| **Agente orquestrador** (Claude Code / Antigravity) | Conduz o loop, ensina, testa, registra | É quem tem acesso ao workspace e à conversa |
| **NotebookLM** | Superfície de consumo: áudio, infográfico, mapa mental, slides, quiz | Ancoragem na fonte com citação; é o forte dele |
| **FSRS** (`srs.db`) | Repetição espaçada: **quando** cada coisa volta | Modelo adaptativo real, com estabilidade por item |

**A decisão fundadora:** o desempenho no NotebookLM é *secundário e descartável*. Quem arbitra o
que o aluno domina é o banco FSRS, alimentado por recuperação ativa conduzida pelo agente. Isso
existe porque medir engajamento no lugar de retenção é o erro mais comum e mais caro em produtos
de aprendizagem.

## 1.3 O escopo — e o que não é responsabilidade do sistema

**Isto é um tutor.** A responsabilidade de aparecer para estudar é do aluno, e deve ser. O sistema
não persegue ninguém, não manda notificação, não premia assiduidade. Ele se julga por uma pergunta
só: **quando o aluno senta, o que acontece com a memória dele?**

Consequência prática: mecanismos como o gatilho de Fase 2 e o modo reentrada existem para **não
perder o fio pedagógico**, não para caçar o aluno. Se ele sumir, o sistema espera.

## 1.4 O que foi deliberadamente recusado

Entender o que um sistema recusa diz mais sobre ele do que o que ele oferece.

| Recusado | Por quê |
|---|---|
| **Estilos de aprendizagem** (visual/auditivo/cinestésico) | A hipótese do casamento entre instrução e estilo declarado não tem suporte empírico <a name="ref18-1"></a>[[18]](#r18)[[19]](#r19) |
| **Streak / recompensa por assiduidade** | Premia comparecimento, não aprendizado. O badge do sistema sai por **etapa dominada**, não por dias seguidos |
| **Quiz como medida de domínio** | Múltipla escolha é reconhecimento, não recuperação. Fica como consumo, nunca como árbitro |
| **Dica que entrega a resposta** | Anula o esforço de recuperação, que é a fonte do ganho duradouro [[1]](#r1) |
| **Instalar o MCP do PyPI `latest`** | Código de terceiro dirigindo uma sessão real do Google. Só de clone pinado e auditado |
| **Atualizar o MCP automaticamente** | Mesma razão. Achado de severidade alta bloqueia a atualização |

---

# Parte II — Fundamentos: por que funciona assim

## 2.1 A lente: as duas forças

Todo o desenho se apoia numa distinção do modelo de Bjork [[1]](#r1):

- **Força de recuperação** — o quanto você consegue acessar aquilo *agora*.
- **Força de armazenamento** — o quanto aquilo está de fato aprendido.

As duas frequentemente andam em **direções opostas**. Condições que facilitam a recuperação no
momento (reler, ter a resposta à vista, estudar um tema de cada vez) reduzem o ganho duradouro. O
ganho em armazenamento é **função do esforço de recuperação bem-sucedida**.

Isso tem uma consequência desconfortável que o sistema assume: **a sessão boa não é a que parece
boa**. Se o aluno sai sentindo que foi fácil, provavelmente aprendeu menos.

A demonstração mais direta disso está em Rohrer & Taylor [[9]](#r9): prática intercalada **triplicou**
a nota final (63% vs. 20%) e ao mesmo tempo **piorou o desempenho durante a prática** (60% vs. 89%,
d = 1,06). Fluência e aprendizado, medidos em direções opostas, no mesmo experimento.

## 2.2 As sete alavancas

O sistema é avaliado — e foi construído — contra sete mecanismos com evidência própria.

### Alavanca 1 · Recuperação ativa

**O que é.** O aluno puxa da memória em vez de reconhecer. Produção, não seleção.

**Evidência.** Meta-análise de Adesope et al. [[3]](#r3) sobre 253 estudos: **g = 0,61** [0,58–0,65]
para prática de recuperação contra outras práticas, com efeito equivalente em laboratório (0,62) e
em sala de aula (0,67). Roediger & Karpicke [[2]](#r2) mostram o padrão temporal: restudo vence em
prova imediata, **perde de forma acentuada** em prova adiada — e aumenta a confiança do aluno.
Dunlosky et al. [[4]](#r4) classificam como **alta utilidade**.

**Como o sistema implementa.** Mínimo de 7 perguntas de produção por etapa, obrigatórias **mesmo
que o quiz do NotebookLM já tenha sido feito**. Formato de texto lacunado (cloze), nunca múltipla
escolha.

**Nuance que o sistema respeita.** O mesmo trabalho reporta 0,53 para *transferência* contra 0,63
para *retenção* [[3]](#r3). Recuperação ajuda a transferir, mas menos do que ajuda a lembrar — por
isso transferência tem cota própria, em vez de ser esperada como subproduto.

### Alavanca 2 · Prática espaçada

**O que é.** Revisões em intervalos crescentes, calculados por um modelo do esquecimento.

**Evidência.** Cepeda et al. [[5]](#r5), 839 avaliações em 317 experimentos: o intervalo ótimo
**cresce junto com o horizonte de retenção desejado**, e intervalos expansivos superam uniformes.

**Como o sistema implementa.** FSRS-5 com 19 parâmetros, estabilidade e dificuldade por item,
gravados em `srs.db`. O agendamento é a fonte da verdade do progresso.

**Onde ele fica devendo.** A retenção pedida está em `0.95`, que é alto. A documentação do FSRS
recomenda minimizar a razão esforço/conhecimento, o que costuma pousar entre 0,85 e 0,90 [[6]](#r6).
Simulação com os pesos do modelo, acervo de 120 cards:

| Retenção pedida | Revisões/ano | Horas/ano | Primeiros intervalos |
|---|---|---|---|
| **0,95** (atual) | 1 080 | **27 h** | 1, 3, 6, 13, 26, 49 |
| 0,90 | 600 | 15 h | 3, 11, 36, 107 |
| 0,85 | 480 | 12 h | 5, 25, 109, 417 |

Doze horas por ano de diferença. Ver [7.3](#73-decisões-que-são-inferência-não-resultado).

### Alavanca 3 · Intercalação

**O que é.** Misturar conceitos na prática, de modo que o aluno precise **decidir qual se aplica**.

**Evidência.** Rohrer et al. [[7]](#r7), ensaio randomizado com 787 alunos: **d = 0,83** [0,68–0,97].
Taylor & Rohrer [[8]](#r8): 77% vs. 38% na prova do dia seguinte (d = 1,21). Rohrer & Taylor
[[9]](#r9): nota triplicada, prática pior.

**O problema que o sistema tinha.** A trava que impede o material gerado de vazar para etapas
futuras (injetar a lista de conceitos da etapa em todo pedido de artefato) **também tornava a
prática em blocos obrigatória**. E o nível 3 de rigor cobra distinguir conceitos parecidos —
discriminação é justamente o que bloco não treina, porque nunca há dois conceitos concorrendo.

**Como o sistema resolve, em três peças distintas:**

| Peça | Onde age | O que faz |
|---|---|---|
| **Amarra retrospectiva** | ao ensinar | abre ligando ao que já foi dominado, via `conecta_com` do roadmap |
| **Cotas no recall** | ao testar | 2 perguntas de etapas dominadas + 1 de síntese. **É aqui que a intercalação de fato acontece** |
| **Prévia estruturante** | ao fechar | apresenta o que vem, via `prepara_para` |

> **Distinção que importa.** Só a segunda peça é intercalação no sentido técnico. Exposição não
> intercala — só **recuperação sob competição** intercala, porque é ela que obriga a decidir.
> Apresentar temas futuros é organizador prévio [[14]](#r14), com valor próprio e mecanismo
> diferente. Confundi-las leva a achar que basta mostrar o que vem para ter os ganhos da
> intercalação, e não basta: não há o que recuperar em algo ainda não aprendido.

**Ressalva metodológica.** Parte do ganho atribuído à intercalação pode vir do **espaçamento
embutido** — intercalar garante que duas práticas do mesmo conteúdo não sejam consecutivas
[[7]](#r7). Isso não muda a recomendação prática; muda o que se pode afirmar sobre o mecanismo.

### Alavanca 4 · Dificuldade desejável

**O que é.** Calibrar o esforço para o ponto em que a recuperação é difícil mas bem-sucedida.

**Evidência.** Bjork & Bjork [[1]](#r1): o ganho em armazenamento é função do esforço de recuperação.

**Como o sistema implementa** — e esta é a parte mais fina do desenho:

1. **Cloze progressivo.** A lacuna encolhe conforme o nível de rigor, criando um contínuo real
   entre recuperação com pista e recuperação livre.
2. **A dica devolve contexto, não a resposta.** Ela rebaixa a questão um nível (N4→N3→N2→N1). O
   esforço é reduzido, não anulado.
3. **Acerto após dica vale no máximo nota 2.** Separa, no registro, *lembrar* de *lembrar com
   ajuda* — a distinção entre as duas forças, implementada em uma linha de regra.

O item 3 importa porque o próprio aluno não faz essa distinção: julgamentos de aprendizagem inflam
justamente quando a informação está presente no estudo e ausente no teste [[10]](#r10).

### Alavanca 5 · Calibração metacognitiva

**O que é.** O aluno saber o que ele **não** sabe.

**Evidência.** Koriat & Bjork [[10]](#r10) descrevem o **viés de premonição**: o julgamento de
aprendizagem infla porque, no momento do estudo, a resposta está à vista. O achado decisivo é o
remédio — o viés **é atenuado por experiência de teste** e por adiar o julgamento. Castel et al.
[[11]](#r11) convergem sobre a superestimação sistemática.

**Por que isso é vital aqui.** O sistema serve a um autodidata. Ele decide sozinho o que revisar,
quando parar e quando avançar — e toma essas decisões pela sensação de saber. Um tutor pode
corrigir cada resposta com perfeição e ainda devolver ao mundo alguém que continua sem saber se
avaliar.

**Como o sistema implementa.** Antes de revelar qualquer resposta:

```
Antes de eu te dizer: você acha que acertou essa?
  (a) vou acertar   (b) mais ou menos   (c) não vou acertar
```

Grava em `review_log.confianca` (2 / 1 / 0). Ao fim do recall, devolve o desencontro em uma linha.
Relatório acumulado em `status.py --calibracao`, com **dois números**:

- **Erro de calibração** — o quanto a previsão erra, em qualquer direção (magnitude)
- **Viés** — para que lado ela erra (direção)

> **Por que dois e não um.** Somar desvios com sinal faz o excesso numa faixa cancelar a falta em
> outra: um aluno que erra 25% para cima e 30% para baixo apareceria como bem calibrado. **Erro
> alto com viés perto de zero é o pior caso** — não há correção simples, porque a sensação de saber
> tem pouca relação com o que se sabe.

O relatório fecha listando os **acertos previstos que deram errado**. É a lista mais importante do
sistema: ali mora o que o aluno não sabe que não sabe.

### Alavanca 6 · Carga cognitiva

**O que é.** Não desperdiçar memória de trabalho com o que não é o aprendizado em si.

**Evidência.** Sweller [[12]](#r12): carga estranha consome capacidade que deveria ir para a
construção do esquema. Kirschner, Sweller & Clark [[13]](#r13): orientação mínima falha com quem
ainda não tem esquema formado.

**Como o sistema implementa.**

- **Recorte curado da fonte.** O PDF inteiro nunca vira source. O agente extrai só o trecho da
  etapa e salva um `.md` organizado pelos conceitos obrigatórios. A memória de trabalho deixa de
  gastar capacidade localizando o que importa.
- **Um conceito por vez** ao ensinar (mas não ao testar — ver alavanca 3).
- **Traves de segurança nos métodos.** O socrático cai para o método de apoio após 3 perguntas sem
  progresso. É [[13]](#r13) escrito como condição de saída, no mesmo lugar que o roteiro.

### Alavanca 7 · Transferência

**O que é.** Aplicar o conceito a um caso de **superfície diferente**, reconhecendo a estrutura
profunda sob uma aparência que não combina com nenhum exemplo visto.

**Evidência.** Gick & Holyoak [[15]](#r15): a transferência falha quando o aluno codifica a
superfície; múltiplos exemplos com superfícies distintas induzem o esquema. Barnett & Ceci
[[16]](#r16) sistematizam as dimensões de distância — "transferência" sem especificar a distância
não diz nada.

**O problema.** O padrão de rigor (N3) exige nome técnico, exemplo e distinção. Tudo isso acontece
*dentro da linguagem do domínio*. Ancorar no contexto de trabalho do aluno fixa melhor, mas é
elaboração no mesmo contexto de codificação — não transferência.

**Como o sistema implementa.**

- **Cota fixa**: ao menos 1 item de transferência em todo recall, independente do nível de rigor.
- **Portão N4**: para marcar uma etapa como `dominada`, o aluno passa em ≥2 itens de cenário
  aberto, sustentados sob contestação, **sem dica**.

> **Por que não subir o rigor padrão para N4.** Transferência distante logo após a aquisição produz
> principalmente fracasso: o esquema ainda não consolidou. Rigor alto **no portão** sobe a barra
> onde ela decide algo — no significado da palavra "dominado" — sem transformar cada pergunta do
> dia em uma banca. **Esta é uma inferência, não um resultado**; ver [7.3](#73-decisões-que-são-inferência-não-resultado).

---

# Parte III — Arquitetura

## 3.1 A fronteira: harness × conteúdo

O repositório tem **duas metades com regras opostas**.

| | **Raiz** — harness | **`estudo/`** — conteúdo |
|---|---|---|
| O que é | Como o sistema funciona e como o agente age | Quem é o aluno e o que ele estudou |
| Vai pro git? | **Sim** — é isso que é publicado | **Nunca** — está no `.gitignore` |
| Exemplos | método, rigor, loop, setup, segurança | perfil, roadmap, ledger, `srs.db`, badge, PDFs |

**O teste do clone:** *se outra pessoa clonasse este repo para estudar algo completamente
diferente, essa informação continuaria útil?* Sim → harness. Não → `estudo/`.

Isso é o que permite **melhorar o sistema com o uso e publicar só isso**. Você corrige o agente,
ele escreve a correção no arquivo de harness certo, e no dia do commit sobe só a evolução da
arquitetura — nunca a matéria.

Regras derivadas, todas em `AGENTS.md`:
- Nunca escrever nome de matéria ou conceito de disciplina específica em arquivo da raiz.
- Nunca usar `git add -f` para forçar algo de `estudo/`.
- Roadmap de matéria mora em `estudo/progresso/<materia>-roadmap.md`, nunca no `GUIA_NOTEBOOKLM.md`.

## 3.2 Mapa de arquivos

### Harness — versionado

| Arquivo | O que é | Quem lê |
|---|---|---|
| `AGENTS.md` | Ponto de entrada. O que fazer ao abrir a sessão, e a regra de onde escrever cada coisa | agente, no boot |
| `.agents/skills/professor/SKILL.md` | **O cérebro.** Persona, loop de 3 fases, protocolo de recall | agente, toda sessão |
| `METODOS_DE_ENSINO.md` | Os 6 métodos, a escala de rigor, as 5 posturas, calibração, integração, transferência | agente, sob demanda |
| `COOKBOOK.md` | Runbook: onboarding, setup, atualização do MCP, operação do loop | agente |
| `GUIA_NOTEBOOKLM.md` | Persona/método — **sobe como fonte no NotebookLM** | agente + NotebookLM |
| `REVISAO_IA.md` | Protocolo da revisão (cloze, rigor, rating, calibração) — a mecânica do banco fica no `scripts/revisar.py` | agente, na Fase 3 |
| `ARQUITETURA.md` | Visão geral + 4 diagramas | humano |
| `README.md` | Quickstart | humano |
| `.agents/mcp_config.json` | MCP com privilégio mínimo | runtime do agente |
| `.agents/mcp_pin.json` | Commit auditado do MCP + histórico de atualizações | `setup.py`, `mcp_update.py` |
| `scripts/` | Ver [3.4](#34-os-scripts) | agente e humano |
| `artefatos/` | Regras de formato dos artefatos do NotebookLM — um arquivo por tipo + índice + referências | agente lê antes de gerar |
| `templates/` | Modelos copiados para `estudo/` no setup | `setup.py` |
| `docs/` | Diagramas em PNG, avaliações, este manual | humano |

### Conteúdo — ignorado (`estudo/`)

| Arquivo | O que é | Quem escreve |
|---|---|---|
| `PERFIL.md` | **Fonte única de configuração**: método, postura, rigor, idioma, artefatos, ritmo | onboarding; sobe como source |
| `progresso/_index.md` | Mapa de todas as matérias | agente |
| `progresso/<materia>.md` | **Ledger**: estado, tópicos, retomar_em, pontos fracos, log | agente, toda sessão |
| `progresso/<materia>-roadmap.md` | **Trilha**: etapas, conceitos obrigatórios, `conecta_com`, `prepara_para` | agente propõe, aluno aprova |
| `progresso/srs.db` | Cards + FSRS + sessões + log de revisão | agente e scripts |
| `progresso/jornada_do_heroi.jpg` | Badge de conquista | agente |
| `JORNADA.md` | Mapa visual da jornada | agente |
| `documentos/` | Fontes brutas + recortes curados por etapa | aluno e agente |

## 3.3 O modelo de dados

`estudo/progresso/srs.db`, SQLite, três tabelas. Esquema em `templates/srs_schema.sql`.

### `cards` — o que o aluno está aprendendo

| Coluna | Papel |
|---|---|
| `front` / `back` | pergunta e resposta. O `front` é reescrito como cloze no momento da pergunta |
| `tags` / `deck` / `subject` | organização. **`deck` é o que a fila intercalada usa** para alternar tópicos |
| `state` | 0 New · 1 Learning · 2 Review · 3 Relearning |
| `difficulty` / `stability` | parâmetros FSRS por item. `stability` é o que ordena a fila do modo reentrada |
| `due_date` | quando volta. **É a fonte da verdade do progresso** — só é reescrita em massa com autorização explícita |
| `reps` / `lapses` | histórico agregado |

### `review_log` — como cada resposta aconteceu

Além do resultado, guarda o **contexto**. As quatro últimas colunas existem por motivos distintos:

| Coluna | Por que existe |
|---|---|
| `rating` 1–4 | nota atribuída pelo agente |
| `confianca` 0/1/2 | **calibração**: o aluno previu antes de saber o resultado |
| `tentativas`, `usou_dica` | **auditabilidade**: fatos objetivos ao lado de um julgamento subjetivo. Se a proporção de notas altas subir sem que o uso de dica caia, a avaliação afrouxou — e essa é a única forma de perceber |
| `tipo_item` | mede se as **cotas** de intercalação e transferência estão sendo cumpridas de verdade |
| `stability`, `difficulty`, `state`, `elapsed_days`, `interval_days` | estado do FSRS no momento da revisão |

### `study_sessions` — tempo cronometrado

| Coluna | Papel |
|---|---|
| `inicio` / `fim` / `duracao_min` | o cronômetro. `fim IS NULL` = sessão aberta |
| `bloco_min` / `blocos_alvo` / `blocos_feitos` | configuração de foco daquela sessão |
| `interrompida` | 1 quando o aluno esqueceu de fechar. **Excluída de toda estatística** — a duração é ficção |
| `absorvido` | o que o aluno disse que ficou |
| `tipo` | study · recall · revisao |

> **Regra inegociável desta tabela:** tempo **nunca** é reportado sozinho. Toda leitura sai cruzada
> com o `review_log` da mesma data, no indicador **minutos por conceito retido**. Celebrar "2h de
> estudo hoje" seria a mesma armadilha de medir engajamento que o resto do sistema existe para
> evitar.

### Migração

`workspace.abrir_db()` aplica o esquema (todo `CREATE` é `IF NOT EXISTS`) e roda `_migrar()`, que
adiciona colunas faltantes via `ALTER TABLE`. Quem já usava o sistema ganha tabelas e colunas novas
sem fazer nada.

## 3.4 Os scripts

Todos em Python 3.9+, **só biblioteca padrão**, rodando igual em Windows, Linux e macOS.

| Script | O que faz | Quando roda |
|---|---|---|
| **`status.py`** | **Passo zero de toda sessão.** Lê ledger + banco e decide por onde começar | início de cada sessão |
| **`revisar.py`** | **Único ponto de escrita no `srs.db`**: FSRS-5, criação de cards, backlog | durante a revisão e a Fase 3 |
| **`grafo.py`** | Grafo de conhecimento navegável: conceitos + FSRS → HTML autocontido | Fase 3, a cada conceito dominado |
| `sessao.py` | Cronômetro em blocos de foco (`iniciar` / `fim` / `agora`) | quando o aluno diz "iniciar" |
| `setup.py` | Passos 1–8 do setup: uv, clone, auditoria, pin, `estudo/`, privilégio, login | uma vez por máquina |
| `mcp_update.py` | Checa atualização do MCP e **audita o diff antes de aplicar** | periodicamente |
| `workspace.py` | Módulo compartilhado: leitura de ledger/perfil/banco, migração, fila intercalada | importado pelos outros |
| `mnemo.py` | Barra de progresso, arte do tutor, cores e UTF-8 multiplataforma | importado pelos outros |

### Por que `revisar.py` é um script e não um snippet no `REVISAO_IA.md`

Até esta versão, a fórmula do FSRS-5 — os 19 pesos, os três ramos de estado, o cálculo do
intervalo — vivia como um bloco de Python **dentro do `REVISAO_IA.md`**, para o agente
retranscrever e executar a cada card revisado. Isso tem três problemas que só aparecem com o
tempo:

1. **O resultado depende de qual modelo está rodando.** Um snippet copiado é um snippet que
   pode ser adaptado, encurtado ou "corrigido" na hora. O bug do `W[15]` zerado (§6.3), que
   congelava para sempre o intervalo de todo card avaliado com rating 2, nasceu exatamente de
   uma edição bem-intencionada num índice solto.
2. **Não há idempotência.** Se a sessão cai no meio e o agente reexecuta, o card é recalculado
   e uma segunda linha entra no `review_log` — o histórico que alimenta o relatório de
   calibração fica errado, silenciosamente.
3. **Não dá para testar.** Prosa não roda em CI, nem responde "isto ainda funciona?".

Com a mecânica no script, o `REVISAO_IA.md` fica com o que de fato é julgamento do agente —
montar o cloze, decidir a lacuna, escolher quando a dica entra, atribuir o rating. A divisão é
essa: **julgamento é prompt, mecânica é código.**

As travas que o script dá de graça: `revisar` recusa uma segunda gravação do mesmo card no
mesmo dia; `criar` deduplica por `front`; `espalhar` exige `--confirmar`; `UPDATE` + `INSERT`
saem numa transação só, com rollback. `python3 scripts/test_revisar.py` cobre a fórmula e as
travas — inclusive uma regressão específica para o `W[15]`.

### Por que a nota do nó é a explicação do aluno

O grafo de conhecimento (`grafo.py`) tem um nó por conceito, e cada nó abre uma anotação.
A pergunta de projeto foi **de quem é o texto dessa anotação** — e a resposta muda o que o
artefato vale.

O caminho fácil seria gerar o resumo a partir da fonte, ou pedir ao NotebookLM. Sai
preciso, sai com citação, e sai rápido. Mas seria o **único artefato modo-reconhecimento**
de um sistema inteiro construído sobre produção ativa: o recall é cloze porque múltipla
escolha é reconhecimento (§2.2 alavanca 1), o portão exige defesa sob contestação, o quiz
do NotebookLM foi recusado como árbitro. Uma nota copiada contradiz tudo isso — e ainda
abre a porta para o **vício de coleção**, o modo de falha clássico do Obsidian e do Zettelkasten:
um acervo bonito que dá a sensação de domínio e substitui a recuperação.

A anotação é, então, **a explicação que o aluno deu no item de portão aprovado**. Três
propriedades caem de graça:

1. **É geração.** O texto existe porque ele produziu, não porque leu.
2. **Carrega prova.** O nó só ganha nota depois de o conceito ser sustentado sob contestação,
   sem dica. Nó com nota é nó que passou.
3. **É a melhor pista de recuperação disponível.** Reler a própria explicação bem-sucedida
   reinstala o contexto da recuperação original; reler uma definição de livro não.

E custa **zero trabalho novo** — é captura de algo que já acontece na Fase 3.

**O risco, e a mitigação.** Salvar a explicação sem conferir é pior que não salvar: uma nota
fluente com o critério errado, gravada como canônica, vira erro ensaiado. O risco não é
teórico neste projeto — o ledger registra o padrão em letras garrafais (*"acerta a
lógica/ação central de primeira, mas erra o CRITÉRIO EXATO que decide"*). Por isso o
NotebookLM entra como **conferente, não como autor**: o agente submete a explicação do aluno
para verificação ancorada na fonte, com citação, e só grava se casar. Divergência vira
`pontos_fracos` — não nota.

O campo `nota_origem` mantém isso auditável: `aluno` é o alvo, `ledger` é dívida de migração
e aparece no nó como "síntese provisória", com aviso explícito no painel. `grafo.py --validar`
separa **problema** (grafo quebrado) de **pendência** (dívida esperada) exatamente para o
comando não viver vermelho e ser ignorado.

### Por que o nó desbota

Um grafo de conhecimento **só cresce** — e é aí que ele mente. Nó verde de três semanas atrás
parece idêntico a nó verde de ontem, então o desenho acumula troféus e some com o
esquecimento. É a mesma armadilha que este sistema recusa para tempo de estudo (§4.5: minuto
isolado mede esforço, não retenção); não faria sentido recusá-la ali e aceitá-la aqui.

Como o `srs.db` guarda estabilidade por item, o grafo pinta a **retrievability** do FSRS:
a opacidade do nó dominado é `0,34 + 0,66 · R`, e nó com card vencido pulsa. O grafo cresce
**e apaga** — deixa de ser vitrine e passa a ser instrumento de retenção. Um mapa desbotando
é o gatilho de revisão mais honesto que o sistema tem.

Dois detalhes de honestidade no cálculo:

- A retenção do conceito é a do **card mais fraco**, não a média. Um conceito vale o elo que
  já cedeu; média esconderia justamente o card que precisa voltar.
- Card **nunca revisado** não tem curva de esquecimento, então fica fora da conta — e o
  painel diz quantos ficaram de fora. Sem isso, um conceito com dois cards frescos e dois
  nunca vistos exibiria "99%" e pareceria seguro.

### Por que `status.py` é um script e não uma instrução

O gatilho de Fase 2 abandonada e o modo reentrada são exatamente o tipo de verificação que um
agente com o contexto cheio deixa de fazer — e a falha é **silenciosa**, porque ninguém sente falta
de uma checagem que não aconteceu. Tirando a decisão da memória do agente e colocando numa saída de
terminal, ela passa a acontecer mesmo quando ele está distraído. E fica visível na transcrição,
portanto auditável por um humano depois.

Saídas possíveis, em ordem de precedência:

| `acao` | Significado |
|---|---|
| `fechar_sessao` | há sessão cronometrada aberta |
| `reentrada` | 10+ dias ausente ou backlog > 15 cards. **Tem precedência sobre tudo** |
| `fase2_expirada` | material entregue há 7+ dias sem retorno |
| `fase2_pendente` | material entregue há 3+ dias |
| `revisao` | cards vencidos |
| `fase2_recente`, `sem_materia`, `loop` | casos normais |

## 3.5 Segurança

O MCP do NotebookLM é **código de terceiro que dirige uma sessão real do Google**. As defesas:

| Defesa | Como |
|---|---|
| Conta Google **dedicada** | se o cookie vazar, expõe só os materiais de estudo |
| Commit **pinado** | `.agents/mcp_pin.json`; instalado de clone local em `vendor/`, não do PyPI `latest` |
| **Privilégio mínimo** | `sharing` e `automation` desligados. O setup **falha** (passo 7) se alguém religar |
| Cookie local | `0600` em Linux/macOS; no Windows, ACL do perfil |
| **Atualização auditada** | ver abaixo |
| Fronteira do repo | `estudo/` ignorado: perfil e progresso nunca vão para o git |

### A auditoria de atualização

`mcp_update.py` compara o pin com o upstream e analisa **só as linhas adicionadas**:

| Severidade | Procura por |
|---|---|
| **ALTA** — bloqueia `--apply` | `eval`/`exec`, `os.system`, `shell=True`, `pickle.loads`, import dinâmico, `compile(..., "exec")` |
| **MÉDIA** — pede revisão | ofuscação base64, `ctypes`, leitura de `~/.ssh`/`~/.aws`, varredura de `os.environ`, persistência (crontab, LaunchAgents, registro) |
| **INFO** | endpoints de rede fora de Google/GitHub/PyPI |

Também compara **dependências novas** em `pyproject.toml`/`requirements.txt` — o vetor de supply
chain mais comum — e sinaliza arquivos sensíveis tocados.

**Testado com código malicioso plantado**: 5 achados ALTA, `--apply` recusado, pin intacto. Só
`--force-approve` passa por cima, e o motivo fica gravado no `historico` do `mcp_pin.json`.

---

# Parte IV — Operação

## 4.1 Setup — 21 passos numerados

Numeração contínua de propósito, para o aluno enxergar um setup só:

```
passos  1–8   MÁQUINA      → scripts/setup.py faz sozinho
passos  9–21  ENTREVISTA   → o agente conduz, na conversa
```

**Parte de máquina** (`python3 scripts/setup.py`, ou `py scripts\setup.py` no Windows):

| # | Passo |
|---|---|
| 1 | Detectar sistema; validar Python 3.9+ e git |
| 2 | Garantir o `uv` (comando certo por SO) |
| 3 | Clonar o MCP para `vendor/` |
| 4 | Checar atualização e **relatar a auditoria** — nunca atualiza sozinho |
| 5 | Instalar do clone pinado |
| 6 | Criar `estudo/` a partir de `templates/` e o `srs.db` |
| 7 | **Falhar** se `sharing` ou `automation` estiverem ligados |
| 8 | Disparar `nlm login`, aguardar, confirmar |

Flags: `--dry-run` (sem rede nem instalação global), `--skip-login`, `--skip-audit`, `--pin <commit>`.

**Entrevista** (passos 9–21, conduzida pelo agente): identidade, background, objetivo, estilo,
método de ensino, método de apoio, 4 cenários situacionais de postura, nível de rigor, idioma +
artefatos, ritmo de foco. Detalhe em `COOKBOOK.md` Parte 0.

## 4.2 Começar uma matéria

1. **[humano]** Ponha a fonte em `estudo/documentos/`.
2. **[agente]** Propõe o **roadmap**: 4 a 8 etapas, cada uma com conceitos obrigatórios, fora de
   escopo, `conecta_com` e `prepara_para`.
3. **[humano]** Aprova, ajusta ou refaz. **Nada é gravado antes do OK.**
4. **[agente]** Grava roadmap + ledger, registra no `_index.md`.

> **Por que o roadmap existe.** Sem trilho declarado, o material gerado pela IA vaza para tópicos de
> fases futuras. Os conceitos da etapa atual entram no `focus_prompt` de **todo** artefato, com
> proibição explícita de avançar. É a solução para um problema observado, não teórico.

> **Por que o material é por subtópico e não por etapa.** Um artefato para a etapa inteira trata
> cinco conceitos como se fossem um: 20 minutos de áudio com 3 minutos em cada coisa, deck de 40
> slides, quiz com uma pergunta por conceito. Duas evidências desmontam esse formato. A
> **segmentação** — material fatiado em unidades autocontidas — tem efeito consistente sobre
> transferência (g ≈ 0,32–0,36 em meta-análise de 56 estudos), e o efeito é **maior justamente em
> tratamentos curtos**. E o **engajamento** em material audiovisual satura em torno de 6 minutos
> independentemente da duração total: acima de 12 minutos, o aluno médio consome menos de um
> quarto. O que passa disso é produção jogada fora.
>
> Há um ganho de diagnóstico junto: o subtópico é a **menor unidade que se cobra sozinha** no
> recall da Fase 3. Quando o artefato mistura cinco conceitos, o erro do aluno não aponta para
> nada — não dá para saber qual material reabrir. Com um artefato por subtópico, erro no card
> aponta para o subtópico, que aponta para o guia, o áudio e o deck exatos.
>
> A exceção são os **integradores** (`mind_map`, `data_table`, quiz integrador): eles existem
> para mostrar como os subtópicos se ligam, e fatiá-los destruiria a única coisa que produzem.
> Um mapa mental de um conceito só é um retângulo. Regras e evidência completas em
> `artefatos/` — um arquivo por tipo, com o `[FORMATO]` que o agente copia para o `focus_prompt`.

## 4.3 O loop de 3 fases

### Passo zero (sempre)

```bash
python3 scripts/status.py
```

Siga o `próximo passo` que ele imprimir. Não improvise por onde começar quando o script já decidiu.

### Fase 1 — PREP (agente, sozinho)

1. Lê ledger: `retomar_em` + `pontos_fracos`.
2. Lê roadmap: conceitos obrigatórios, fora de escopo, `conecta_com`, `prepara_para`.
3. Define o 80/20 e **abre amarrando no que já foi dominado**.
4. **Recorta a fonte** → `estudo/documentos/<materia>-<etapa>.md`. Não sobe o PDF inteiro.
4b. **Decompõe a etapa em 3 a 6 subtópicos** e grava no roadmap (congelados até a etapa fechar).
5. Via MCP: garante notebook → `source_add` (recorte + `PERFIL.md` + `GUIA_NOTEBOOKLM.md`) →
   `studio_create` **por subtópico** de cada tipo padrão, com os conceitos **daquele subtópico**
   no `focus_prompt` e o bloco de formato copiado de `artefatos/<tipo>.md` → depois, os
   integradores da etapa (`mind_map`, `data_table`, quiz integrador) → renomeia tudo.
6. Avisa o aluno, **dá a ordem de consumo por subtópico** e entrega o **prompt calibrado** para
   o chat.
7. **Grava `fase2_iniciada_em` no ledger.**
8. Convida a cronometrar: *"quando for começar, me diga **iniciar**"*.

### Fase 2 — STUDY (o aluno faz)

O agente não conduz, mas não some:

```bash
python3 scripts/sessao.py iniciar                       # ao dizer "iniciar"
python3 scripts/sessao.py iniciar --bloco 50 --pausa 10 # ritmo diferente hoje
python3 scripts/sessao.py fim --absorvido "..."         # ao voltar
```

**No retorno, o agente pergunta uma coisa só:** *"me diga um conceito que você não conseguiria
explicar agora"*. Pedir relatório na porta de entrada só reduz a chance de o aluno voltar.

Se ele não voltar: 3 dias → a próxima sessão começa por aqui. 7 dias → material dado como não
consumido, com oferta de fazer o recall assim mesmo ou regenerar.

### Fase 3 — PROGRESS (agente, escrevendo)

**Composição do recall** — a partir da etapa 3, não podem ser 7 perguntas da etapa atual:

| Cota | Tipo | De onde sai |
|---|---|---|
| 3 | `recall` | conceitos da etapa atual |
| 2 | `intercalado` | etapas dominadas, via `conecta_com` |
| 1 | `sintese` | combina a etapa atual com uma anterior |
| 1 | `transferencia` | mesmo conceito, superfície nova |

Etapas 1 e 2: 5 `recall` + 2 `transferencia`.

**Por item:** pergunta a confiança → apresenta o cloze no tamanho do nível → dica se pedida
(rebaixa um nível, limita a nota a 2) → avalia → grava `confianca`, `tentativas`, `usou_dica`,
`tipo_item`.

**Ao fim:** devolve o desencontro de calibração, atualiza ledger, FSRS, roadmap, `ultima_sessao`,
limpa `fase2_iniciada_em`. Se passou no **portão N4** (2 itens de cenário aberto sem dica), a etapa
vira `dominada`, sai badge + `JORNADA.md` + **prévia estruturante** do que vem.

## 4.4 Modo reentrada

Dispara com **10+ dias sem sessão** ou **backlog > 15 cards**. Precedência sobre revisão normal.

| | Sessão normal | Modo reentrada |
|---|---|---|
| Quantidade | até 20 cards | **teto de 8** |
| Ordem | mais vencido primeiro | **maior estabilidade primeiro** |
| Conteúdo novo | permitido após revisão | **nenhum** |
| Dica | conforme o nível | **1 tentativa antes** |
| Régua do rating | conforme o nível | **inalterada** |

> **Por que a régua não muda.** Baixar o rigor inflaria a nota, que infla o intervalo, que esconde
> a lacuna. Adiantar a dica dá o mesmo alívio **sem mentir para o agendamento**: dica já limita a
> nota a 2, então o FSRS recebe o sinal correto de "lembrou com ajuda".

**Válvula de escape:** se o aluno disser que quer seguir mesmo assim, o agente atende sem discutir.
Uma recomendação que não aceita "não" vira paternalismo.

**Backlog restante:** só é reagendado com autorização explícita. `due_date` é a fonte da verdade.

## 4.5 Relatórios

```bash
python3 scripts/status.py                # estado + por onde começar
python3 scripts/status.py --calibracao   # o aluno sabe o que não sabe?
python3 scripts/status.py --fila         # fila de hoje, intercalada por tópico
python3 scripts/status.py --performance  # tempo cruzado com retenção
python3 scripts/status.py --json         # para consumo programático
```

---

# Parte V — Configuração

Tudo vem de `estudo/PERFIL.md`. O ledger da matéria pode sobrescrever o rigor pelo campo `rigor:`.

## 5.1 Os 6 métodos de ensino

Cada um tem **roteiro executável** e **trave de segurança** em `METODOS_DE_ENSINO.md` §1.

| Método | Quando rende | Trave |
|---|---|---|
| `socratico` | aluno com base, gosta de ser desafiado | máx. 3 perguntas sem progresso → cai para o apoio |
| `instrucao_direta` | conteúdo novo com terminologia própria | se acerta tudo e entedia, suba o rigor |
| `exemplos_trabalhados` | conteúdo procedimental | 2 exemplos fechados sem ajuda → avance |
| `baseado_em_problema` | profissional da área, objetivo de aplicação | sem base, vira adivinhação → recue |
| `descoberta_guiada` | há uma intuição errada comum a derrubar | o erro precisa ser produtivo, não humilhante |
| `mastery` | conteúdo cumulativo ou certificação | máx. 3 ciclos; depois registre e espace |

> **A escolha é do aluno, mas a validade é fraca.** Preferência declarada é um preditor fraco, e as
> pessoas preferem os métodos que produzem sensação de facilidade [[18]](#r18). Os 4 cenários
> situacionais são um instrumento melhor que a pergunta direta, mas 4 itens para inferir duas
> dimensões é pouco. Ver [7.2](#72-onde-os-dados-existem-e-ninguém-os-lê).

## 5.2 Os 4 níveis de rigor

Um número controla três coisas.

| | N1 Acolhedor | N2 Padrão | N3 Rigoroso (+25%) | N4 Banca |
|---|---|---|---|---|
| **Profundidade** | recall e definição | aplicação de rotina | raciocínio estratégico | investigação estendida |
| **O que cobra** | a ideia, com as palavras dele | nome técnico + exemplo | nome + exemplo **do contexto do aluno** + distinção | cenário aberto + defesa sob contestação |
| **Tamanho da lacuna** | uma palavra num parágrafo | várias lacunas curtas | uma justificativa inteira | o raciocínio todo |
| **Dica entra** | ao hesitar | após 1 tentativa | após 2 | após 2, rebaixando para N3 |
| **Imprecisão terminológica** | não penaliza | derruba para 2 | derruba para 2 | derruba para 1 |

**Padrão do projeto: N3 no dia a dia, N4 no portão de fechamento de etapa.**

## 5.3 As 5 posturas

Postura é **como o tutor se porta**; método é **o que ele faz**. Independentes: dá para ser
socrático com postura de especialista ou de facilitador, com resultados bem diferentes.

`especialista` · `autoridade_formal` · `modelo_pessoal` · `facilitador` · `delegador`

Inferidas de 4 cenários situacionais, não de autodiagnóstico.

## 5.4 Ritmo

25/5 é o pomodoro clássico, **não é lei**. Bloco de 50 ou 90 serve melhor a quem entra em
profundidade; bloco curto a quem tem janelas picadas.

Campos: bloco de foco, pausa curta, pausa longa, blocos até a pausa longa, blocos por sessão.
Sobrescrevíveis por flag: `sessao.py iniciar --bloco 50 --pausa 10 --blocos 3`.

## 5.5 Produção no NotebookLM

Tipos que o MCP realmente gera: `audio`, `video`, `infographic`, `mind_map`, `slide_deck`, `quiz`,
`flashcards`, `report`, `data_table`.

O perfil separa **conjunto padrão** (gerado a cada etapa, sem pedir) de **sob demanda**.

> **Cuidado ao configurar.** Quatro das cinco peças do conjunto padrão típico são *recepção*.
> Ver [7.1](#71-lacunas-conhecidas).

---

# Parte VI — Como o sistema foi avaliado

Dois pareceres em [`docs/avaliacoes/`](avaliacoes/), de lentes diferentes.

## 6.1 Qualidade de aprendizagem — parecer principal

Rubrica das 7 alavancas, 0 a 5, com fonte e **grau de evidência** por afirmação.

| Alavanca | 1ª emissão | Atual |
|---|---|---|
| Recuperação ativa | 5 | 5 |
| Prática espaçada | 4 | 4 |
| Intercalação | **1** | **4** |
| Dificuldade desejável | 5 | 5 |
| Calibração metacognitiva | **1** | **4** |
| Carga cognitiva | 4 | 4 |
| Transferência | **2** | **4** |
| **Média** | **3,1** | **4,3** |

Veredito atual: *"um tutor que agora ensina e mede de acordo com a evidência — e cuja última
fragilidade é não saber onde o aluno começa."*

## 6.2 Usabilidade

Avalia por **pontos de fuga**. Vale a ressalva registrada no próprio parecer de aprendizagem: parte
dessa crítica cobra comportamento de produto de engajamento, e a responsabilidade de aparecer para
estudar é do aluno. Leia com esse desconto.

Achados fechados: gatilho de Fase 2 (F-04), modo reentrada (F-05), comando de status (F-10).
Achado que continua de pé: **F-01 — quem executa o protocolo é quem avalia se ele foi cumprido**.

## 6.3 Bugs encontrados nas avaliações

Registrados porque o **padrão** importa mais que o defeito: os três eram silenciosos e produziam
resultado pior sem sintoma visível.

| Bug | Efeito | Como foi achado |
|---|---|---|
| `W[15] = 0.0` no FSRS | card avaliado com nota 2 **congelava para sempre** no mesmo intervalo | simulação de 6 revisões |
| Índice de calibração com sinal | aluno que erra para os dois lados aparecia como bem calibrado | teste com 3 perfis sintéticos |
| Sessão interrompida na estatística | poluía o custo por conceito retido — o indicador criado como antídoto contra métrica de vaidade | teste com dia misto |

---

# Parte VII — Pontos em aberto e como investigá-los

> Esta parte existe para você encontrar melhorias com fundamento. Está organizada por **tipo de
> problema**, porque o tipo determina como atacá-lo.

## 7.1 Lacunas conhecidas

### L1 · Não há sondagem de conhecimento prévio

**O quê.** Treze perguntas sobre quem o aluno é e nenhuma sobre o que ele já domina. O roadmap é
derivado da fonte, não do aluno: a etapa 1 é a etapa 1 do livro, para todo mundo.

**Por que importa.** Conhecimento prévio é o preditor isolado mais forte de aprendizagem nova
[[17]](#r17). E há o **efeito de reversão pela expertise** [[20]](#r20): apoio instrucional que
ajuda o novato atrapalha quem já tem esquema formado. Consequências opostas e igualmente ruins:
quem já sabe a etapa 1 conclui que o sistema é lento; quem não tem o pré-requisito da etapa 3
conclui que o problema é ele.

**Como atacar.** Seis a oito itens em cloze ao iniciar a matéria, cobrindo os conceitos-âncora de
todas as etapas. Não vale nota, não entra no agendamento — posiciona o ponto de partida e marca
como dominado o que o aluno demonstrar. **O instrumento já existe**: é o mesmo formato de recall,
apontado para outro momento.

### L2 · A composição do material favorece recepção

**O quê.** Do conjunto padrão típico, quatro peças são recepção (podcast, infográfico, mapa mental,
slides) e uma é reconhecimento (quiz). Estimativa de tempo por etapa: ~48% recepção, ~17%
reconhecimento, ~34% produção ativa.

**Por que importa.** A proporção está invertida em relação ao que a evidência recomenda [[3]](#r3)
[[4]](#r4). E o sistema *sabe* disso — declara o quiz secundário — mas continua alocando a maior
parte dos minutos na parte que ele mesmo considera secundária.

**Em defesa do podcast:** ele ocupa tempo morto (deslocamento) que de outra forma não seria estudo
nenhum. O problema é proporção, não existência.

**Como atacar.** Reduzir o padrão a duas peças de recepção (o áudio + uma peça visual de estrutura)
e realocar para uma **segunda passada de recuperação**, espaçada da primeira em 1–2 dias. Duas
recuperações espaçadas rendem mais que uma recuperação e três materiais a mais.

### L3 · Nenhum instrumento independente verifica o cumprimento do protocolo

**O quê.** `status.py` produz um julgamento fora do agente — mas o elo final é voluntário. O script
imprime "MODO REENTRADA, teto de 8"; nada impede o agente de conduzir 30. E a nota de cada resposta
continua sendo dada pela mesma entidade que decide se o aluno avança.

**Por que importa.** Uma nota generosa não produz só um elogio imerecido: ela é a **entrada de um
modelo matemático** que decide quando o conteúdo volta. Nota alta → intervalo longo → menos chance
de o erro ser descoberto. **O viés se auto-oculta.**

**O que já foi feito.** `tentativas` e `usou_dica` são registrados: fatos objetivos ao lado do
julgamento. Torna o viés **visível**, não impossível.

**Como atacar.** Um verificador de fim de sessão comparando o que o protocolo pedia com o que o
banco registra: quantos registros novos entraram em `review_log` hoje, se alcança o mínimo do
perfil, se as cotas de `tipo_item` foram cumpridas, se alguma etapa virou `dominada` sem os 2 itens
`portao`.

### L4 · O erro é registrado como nota, não como diagnóstico — e o raciocínio se perde

**Status: em backlog.** Ideia levantada e validada contra a literatura em 2026-07-29; implementação
adiada por decisão do aluno. Este registro existe para a pesquisa não precisar ser refeita.

**O quê.** Hoje o erro deixa três rastros: o `rating` no `review_log`, uma linha em `pontos_fracos`
no ledger, e um `⚠️` no nó do grafo. Nenhum dos três guarda **o raciocínio que levou ao erro** — o
*porquê* daquela resposta ter parecido certa. E `pontos_fracos` é prosa num ledger: não dá para
contar, filtrar nem medir se a lacuna foi tampada.

**Por que importa.** É a única recomendação da revisão de Metcalfe [[21]](#r21) que o sistema ainda
não implementa, e ela é dita no abstract: *"Corrective feedback, including **analysis of the
reasoning leading up to the mistake**, is crucial."* Registrar esse raciocínio é também um prompt de
**auto-explicação**, cuja meta-análise mede **g = 0,55** em 69 tamanhos de efeito [[22]](#r22) — na
mesma faixa das alavancas que este sistema já usa. E feedback **elaborado** supera a simples
verificação de acerto/erro [[23]](#r23).

**O desenho que a evidência sugere** (e onde ele difere da versão intuitiva):

| Decisão | Por quê |
|---|---|
| Taxonomia **fechada** + texto livre, não só texto livre | O objetivo é medir se a lacuna fechou. Prosa não agrega; a categoria conta, o texto ensina. Precisa dos dois. |
| A taxonomia separa **comissão relacionada** de **chute sem base** | Erro de comissão semanticamente ligado ao alvo melhora a recuperação posterior; palpite sem relação **não traz benefício** [[21]](#r21). Logo o chute pede **reensinar**, não reagendar — remédios opostos. |
| Fechar a lacuna **só por recuperação espaçada**, nunca por declaração | O aluno é metacognitivamente cego ao próprio ganho: mesmo após 20% de vantagem medida, participantes acreditavam que a condição sem erro tinha sido melhor [[21]](#r21). A sensação de "já sei isso" não serve de critério. |
| Erro de **confiança alta** exige mais evidência para fechar | É o mais corrigível agora (hipercorreção) **e** o que mais reaparece depois: o efeito persiste uma semana, mas o erro de alta confiança volta quando a resposta correta é esquecida [[24]](#r24). O sistema já registra `confianca` — o dado existe. |
| Anotar **depois** de revelar a resposta | Feedback não precisa ser imediato: atrasá-lo até uma semana deu resultado equivalente em universitários [[21]](#r21). Anotar durante a tentativa só somaria carga sem ganho. |

**O que a evidência NÃO sustenta.** A prática em si — "caderno de erros", *after-action review* — tem
pouca pesquisa experimental direta. Metcalfe é explícita sobre o AAR: *"there is little experimental
research on this method, there appears, nevertheless, to be considerable consensus about its
efficacy."* O que é sólido são os **mecanismos** (auto-explicação, feedback elaborado, mirar o erro
confiante), não o artefato. Consequência de projeto: se o registro não gerar uma **próxima pergunta
melhor**, é engajamento, não aprendizado — e aí não vale implementar. Material promocional circulando
com números tipo "melhora até 18%" não tem fonte rastreável e não foi usado como base.

**Como atacar quando sair do backlog.** Tabela nova no `srs.db` (uma linha por lacuna, com
`card_id`, tipo, nota, `confianca` do erro que a originou, contador de acertos limpos e
`reaberturas`), o movimento dessas linhas acoplado à **mesma transação** de `revisar.py revisar`, uma
fila `pendentes --lacunas` para a revisão focada, e a contagem de lacunas abertas no nó do grafo. O
esqueleto chegou a ser escrito e revertido em 2026-07-29; a lógica não-óbvia é que acerto no **mesmo
dia** não conta (não é evidência espaçada) e que erro **zera** a contagem, senão alternar acerto e
erro fecharia qualquer coisa.

## 7.2 Onde os dados existem e ninguém os lê

**Este é o padrão mais produtivo para procurar melhorias.** O sistema já coleta o necessário para
responder suas próprias perguntas em aberto.

### D1 · O método escolhido está funcionando?

Gravado como preferência no dia 1 e nunca confrontado. A validade da escolha por autorrelato é
fraca [[18]](#r18)[[19]](#r19).

```sql
-- taxa de acerto sem dica, por período — compare antes e depois de trocar de método
SELECT substr(review_date,1,7) mes,
       COUNT(*) itens,
       ROUND(100.0*SUM(CASE WHEN rating>=3 THEN 1 ELSE 0 END)/COUNT(*),1) pct_acerto,
       ROUND(100.0*SUM(COALESCE(usou_dica,0))/COUNT(*),1) pct_com_dica
FROM review_log GROUP BY mes ORDER BY mes;
```

### D2 · A avaliação está derivando?

Se `pct_acerto` sobe enquanto `pct_com_dica` fica igual ou sobe, alguma coisa afrouxou. A query
acima já responde — falta alguém rodá-la periodicamente.

### D3 · Qual bloco de foco rende mais para este aluno?

```sql
SELECT s.bloco_min,
       SUM(s.duracao_min) min_total,
       (SELECT COUNT(*) FROM review_log r
        WHERE r.review_date = date(s.inicio) AND r.rating >= 3) retidos
FROM study_sessions s
WHERE s.fim IS NOT NULL AND s.interrompida = 0
GROUP BY s.bloco_min;
```

Custo por conceito retido, por tamanho de bloco. Responde empiricamente o que hoje é preferência.

### D4 · As cotas estão sendo cumpridas?

```sql
SELECT tipo_item, COUNT(*) n,
       ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM review_log WHERE tipo_item IS NOT NULL),1) pct
FROM review_log WHERE tipo_item IS NOT NULL GROUP BY tipo_item;
```

Esperado a partir da etapa 3: ~43% `recall`, ~29% `intercalado`, ~14% `sintese`, ~14%
`transferencia`. Desvio grande significa que o agente não está montando o recall como manda o
protocolo — é a checagem mais barata de [L3](#l3--nenhum-instrumento-independente-verifica-o-cumprimento-do-protocolo).

### D5 · A miscalibração poderia dirigir a revisão

Hoje o relatório de calibração é retrospectivo. O card que o aluno **errou estando confiante** é o
que mais merece voltar cedo — e o modelo FSRS sozinho não sabe disso, porque só vê a nota.

```sql
SELECT c.id, c.front, c.due_date
FROM review_log l JOIN cards c ON c.id = l.card_id
WHERE l.confianca = 2 AND l.rating <= 2
ORDER BY l.review_date DESC;
```

Nenhum sistema que eu conheça faz isso. É o passo natural depois de medir calibração.

## 7.3 Decisões que são inferência, não resultado

Registradas separadamente porque são onde o sistema é **mais frágil a uma crítica bem-feita** — e
portanto onde vale investigar primeiro.

| Decisão | Fundamento | O que falta |
|---|---|---|
| **Não subir o rigor padrão para N4** | transferência distante logo após a aquisição produz principalmente fracasso; decorre de [[17]](#r17) e [[16]](#r16) | nenhum ensaio comparou exatamente estas duas políticas |
| **Retenção pedida em 0,95** | escolha do projeto; a recomendação técnica pousa em 0,85–0,90 [[6]](#r6) | não há medição no uso real deste aluno |
| **Cotas 3/2/1/1** | proporção plausível dada a evidência de intercalação e transferência | os números exatos são arbitrados, não derivados |
| **Gatilhos de reentrada (10 dias, 15 cards)** | plausíveis | nunca calibrados contra comportamento real |
| **Dica antecipada na reentrada** | mantém o sinal honesto porque a nota já é limitada a 2 | não testado |

## 7.4 Perguntas que só o uso responde

Nada de análise de código responde estas. Elas exigem **seis a oito semanas de dado real**:

- O custo por conceito retido sobe depois do segundo bloco de foco?
- O método declarado no dia 1 é mesmo o que produz melhor recall?
- A sessão de reentrada de fato traz alguém de volta, ou só adia o abandono?
- A calibração do aluno melhora com a devolutiva, e em quanto tempo?
- Os itens de transferência têm taxa de acerto sistematicamente menor — e ela sobe com o tempo?

## 7.5 Verificação que ainda não foi feita

| Área | Estado |
|---|---|
| Setup em clone limpo, banco, migração, auditoria de segurança, lógica de decisão, agendamento FSRS | **executado e verificado** |
| **Windows e macOS** | só leitura de código. A lógica de plataforma está escrita corretamente, mas ninguém rodou |
| Loop pedagógico com aluno real ao longo de semanas | nenhuma evidência |
| Qualidade do que o NotebookLM efetivamente gera | nenhuma evidência |

**Peça a alguém que rode em Windows antes de considerar essa parte pronta.**

---

# Apêndice A — Glossário

| Termo | Significado |
|---|---|
| **Harness** | a metade versionada do repo: como o sistema funciona |
| **Ledger** | `estudo/progresso/<materia>.md` — o "save game" da matéria |
| **Roadmap** | a trilha da matéria: etapas, conceitos obrigatórios, conexões |
| **Cloze** | texto lacunado que o aluno completa; formato padrão do recall |
| **Cota** | a divisão obrigatória das perguntas do recall por tipo |
| **Portão N4** | 2 itens de cenário aberto, sem dica, para fechar uma etapa |
| **Prévia estruturante** | apresentação breve do que vem; organizador prévio, não aula |
| **Modo reentrada** | protocolo especial para quem volta depois de sumir |
| **Força de recuperação** | o quanto você consegue acessar agora |
| **Força de armazenamento** | o quanto está de fato aprendido |
| **Dificuldade desejável** | o esforço que reduz o desempenho hoje e aumenta o aprendizado |
| **Viés de premonição** | julgar que sabe porque a resposta está à vista no estudo |
| **Erro de calibração / viés** | magnitude e direção do desencontro entre previsão e resultado |

# Apêndice B — Referências

<a name="r1"></a>**[1]** Bjork, R. A., & Bjork, E. L. — *A new theory of disuse and an old theory of stimulus fluctuation* (1992); *Making things hard on yourself, but in a good way* (2011). Força de armazenamento × força de recuperação; dificuldades desejáveis.

<a name="r2"></a>**[2]** Roediger, H. L., & Karpicke, J. D. (2006). *Test-Enhanced Learning.* Psychological Science, 17(3), 249–255. — [link](https://journals.sagepub.com/doi/10.1111/j.1467-9280.2006.01693.x)

<a name="r3"></a>**[3]** Adesope, O. O., Trevisan, D. A., & Sundararajan, N. (2017). *Rethinking the Use of Tests: A Meta-Analysis of Practice Testing.* Review of Educational Research, 87(3). g = 0,61; 0,63 retenção vs. 0,53 transferência. — [link](https://www.researchgate.net/publication/315706448_Rethinking_the_Use_of_Tests_A_Meta-Analysis_of_Practice_Testing)

<a name="r4"></a>**[4]** Dunlosky, J. et al. (2013). *Improving Students' Learning With Effective Learning Techniques.* PSPI, 14(1). Recuperação e espaçamento como alta utilidade.

<a name="r5"></a>**[5]** Cepeda, N. J. et al. (2006). *Distributed practice in verbal recall tasks.* Psychological Bulletin, 132(3). — [PDF](https://augmentingcognition.com/assets/Cepeda2006.pdf)

<a name="r6"></a>**[6]** Open Spaced Repetition — *The Optimal Retention.* Documentação técnica do FSRS. — [link](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-optimal-retention)

<a name="r7"></a>**[7]** Rohrer, D. et al. (2020). *A randomized controlled trial of interleaved mathematics practice.* JEP, 112(1). d = 0,83, n = 787. — [PDF](https://gwern.net/doc/psychology/spaced-repetition/2019-rohrer.pdf)

<a name="r8"></a>**[8]** Taylor, K., & Rohrer, D. (2010). *The effects of interleaved practice.* Applied Cognitive Psychology, 24(6). — [PDF](http://uweb.cas.usf.edu/~drohrer/pdfs/Taylor&Rohrer2010ACP.pdf)

<a name="r9"></a>**[9]** Rohrer, D., & Taylor, K. (2007). *The shuffling of mathematics problems improves learning.* Instructional Science, 35. Nota triplicada, prática pior.

<a name="r10"></a>**[10]** Koriat, A., & Bjork, R. A. (2005; 2006). Viés de premonição e seu remédio. — [PDF](https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/07/Koriat_RBjork_2005.pdf) · [PubMed](https://pubmed.ncbi.nlm.nih.gov/17128596/)

<a name="r11"></a>**[11]** Castel, A. D., McCabe, D. P., & Roediger, H. L. (2007). *Illusions of competence…* Psychonomic Bulletin & Review, 14(1). — [PDF](http://psychnet.wustl.edu/memory/wp-content/uploads/2018/04/Castel-et-al-2007_PBR.pdf)

<a name="r12"></a>**[12]** Sweller, J. (1988; 2011). *Cognitive load theory.*

<a name="r13"></a>**[13]** Kirschner, P. A., Sweller, J., & Clark, R. E. (2006). *Why Minimal Guidance During Instruction Does Not Work.* Educational Psychologist, 41(2). — [PDF](https://www.tandfonline.com/doi/pdf/10.1207/s15326985ep4102_1)

<a name="r14"></a>**[14]** Ausubel, D. P. (1960) — organizadores prévios; Mayer, R. E. — princípio do pré-treinamento.

<a name="r15"></a>**[15]** Gick, M. L., & Holyoak, K. J. (1983). *Schema induction and analogical transfer.* Cognitive Psychology, 15(1).

<a name="r16"></a>**[16]** Barnett, S. M., & Ceci, S. J. (2002). *When and where do we apply what we learn? A taxonomy for far transfer.* Psychological Bulletin, 128(4).

<a name="r17"></a>**[17]** Ausubel, D. P. (1968). *Educational Psychology: A Cognitive View.* Conhecimento prévio como fator isolado mais importante.

<a name="r18"></a>**[18]** Pashler, H., McDaniel, M., Rohrer, D., & Bjork, R. (2008). *Learning Styles: Concepts and Evidence.* PSPI, 9(3). — [link](https://journals.sagepub.com/doi/10.1111/j.1539-6053.2009.01038.x)

<a name="r19"></a>**[19]** Rogowsky, B. A., Calhoun, B. M., & Tallal, P. (2015). *Matching Learning Style to Instructional Method.* JEP, 107(1). — [PDF](https://www.apa.org/pubs/journals/features/edu-a0037478.pdf)

<a name="r20"></a>**[20]** Kalyuga, S. et al. (2003). *The Expertise Reversal Effect.* Educational Psychologist, 38(1).

<a name="r21"></a>**[21]** Metcalfe, J. (2017). *Learning from Errors.* Annual Review of Psychology, 68, 465–489. — [link](https://www.annualreviews.org/content/journals/10.1146/annurev-psych-010416-044022) · [PDF](https://files.eric.ed.gov/fulltext/ED574569.pdf) — revisão que reúne hipercorreção, erro de comissão × omissão, exigências do feedback e a cegueira metacognitiva ao benefício de errar.

<a name="r22"></a>**[22]** Bisra, K., Liu, Q., Nesbit, J. C., Salimi, F., & Winne, P. H. (2018). *Inducing Self-Explanation: a Meta-Analysis.* Educational Psychology Review, 30. — [link](https://link.springer.com/article/10.1007/s10648-018-9434-x) — g = 0,55 sobre 69 tamanhos de efeito.

<a name="r23"></a>**[23]** Shute, V. J. (2008). *Focus on Formative Feedback.* Review of Educational Research, 78(1). — [link](https://journals.sagepub.com/doi/10.3102/0034654307313795) — feedback elaborado supera a verificação simples de acerto/erro.

<a name="r24"></a>**[24]** Butler, A. C., Fazio, L. K., & Marsh, E. J. (2011). *The hypercorrection effect persists over a week, but high-confidence errors return.* Psychonomic Bulletin & Review, 18(6), 1238–1244. — [link](https://link.springer.com/article/10.3758/s13423-011-0173-y)

# Apêndice C — Comandos

```bash
# Setup
python3 scripts/setup.py                      # Linux/macOS  (py scripts\setup.py no Windows)
python3 scripts/setup.py --dry-run            # validar ambiente sem instalar nada

# Toda sessão
python3 scripts/status.py                     # PASSO ZERO: estado + por onde começar

# Cronômetro
python3 scripts/sessao.py iniciar
python3 scripts/sessao.py iniciar --bloco 50 --pausa 10 --blocos 3
python3 scripts/sessao.py agora
python3 scripts/sessao.py fim --absorvido "..."

# Relatórios
python3 scripts/status.py --calibracao
python3 scripts/status.py --fila
python3 scripts/status.py --performance
python3 scripts/status.py --json

# Manutenção do MCP
python3 scripts/mcp_update.py                 # checa e audita, não altera nada
python3 scripts/mcp_update.py --apply         # aplica se a auditoria permitir
nlm doctor                                    # diagnóstico da sessão do Google
nlm login                                     # renovar autenticação (a cada 2-4 semanas)
```

---

*Para o mapa visual das peças, ver [`ARQUITETURA.md`](../ARQUITETURA.md) e os PNGs em
[`docs/diagramas/`](diagramas/). Para o detalhe pedagógico, [`METODOS_DE_ENSINO.md`](../METODOS_DE_ENSINO.md).
Para o runbook operacional, [`COOKBOOK.md`](../COOKBOOK.md).*
