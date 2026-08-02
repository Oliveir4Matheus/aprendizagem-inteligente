# COOKBOOK — Setup e operação (executado pelo AGENTE)

Este runbook é feito para **o agente executar**. Legenda: **[AGENTE]** = o orquestrador roda; **[HUMANO]** = ação do aluno.

O setup é **uma numeração contínua de 21 passos**:

```
passos  1–8   parte de MÁQUINA      → scripts/setup.py faz sozinho
passos  9–21  ENTREVISTA (onboarding) → o agente conduz, na conversa
```

A barra de progresso é a mesma nos dois trechos, para o aluno enxergar um setup só.
Contexto completo em [`ARQUITETURA.md`](ARQUITETURA.md).

---

## PARTE A — Setup de máquina (passos 1–8)

### A0. [HUMANO] Pré-requisito
Uma **conta Google DEDICADA só para estudo** (não a principal). É o maior redutor de risco: se o cookie vazar, expõe só os notebooks de estudo.

### A1. [AGENTE] Rode o script

```bash
python3 scripts/setup.py      # Linux / macOS
```
```powershell
py scripts\setup.py           # Windows
```

Ele executa, com barra de progresso, os passos 1–8:

| # | Passo | O que faz |
|---|---|---|
| 1 | Detectar o sistema | valida Python 3.9+ e `git` nos 3 SOs |
| 2 | Garantir o `uv` | instala com o comando certo do SO (`install.sh` ou `install.ps1`) |
| 3 | Baixar o MCP | clona para `vendor/notebooklm-mcp` (dentro do workspace, ignorado pelo git) |
| 4 | Checar atualização | roda a auditoria de segurança e **relata** — nunca atualiza sozinho |
| 5 | Instalar pinado | `git checkout <pin>` + `uv tool install --force ./vendor/...` |
| 6 | Preparar `estudo/` | copia de `templates/` o que ainda não existe e cria o `srs.db` |
| 7 | Privilégio mínimo | falha se `sharing` ou `automation` estiverem ligados |
| 8 | Autenticar | dispara o `nlm login`, o aluno loga no browser, e o script confirma sozinho |

**Flags úteis:**

| Flag | Quando usar |
|---|---|
| `--dry-run` | validar o ambiente sem tocar a rede nem instalar nada global |
| `--skip-login` | reexecução quando a sessão já está válida |
| `--skip-audit` | pular a checagem de atualização nesta rodada |
| `--pin <commit>` | forçar um commit específico do MCP |

> O passo 8 **abre o navegador e espera**. Diga ao aluno: *"vai abrir o Google no navegador — entre com a conta dedicada; eu continuo sozinho quando você terminar."* O script confirma com `nlm doctor`; não pergunte se ele terminou.

### A2. [AGENTE] Se o `nlm login` não puder rodar do seu lado

Alguns ambientes não deixam o agente abrir browser. Nesse caso peça ao aluno para rodar
ele mesmo no terminal e siga em frente:

```bash
nlm login
```

> Cookies ficam em `~/.notebooklm-mcp-cli/` (permissão `0600` no Linux/macOS; no Windows a proteção é a ACL do perfil do usuário) e duram ~2–4 semanas.
> O MCP usa o **profile ativo**; `nlm login` sem flag = profile `default`. Para isolar: `nlm login --profile estudo` + `nlm login switch estudo`.

### A3. [AGENTE] Nunca registre o MCP por fora

Use **este** `.agents/mcp_config.json`. **Não** rode `nlm setup add` nem `claude mcp add` — eles registram o server sem o bloco `env` de privilégio mínimo, reabrindo `sharing`/`automation`.

---

## PARTE 0 — Onboarding: a entrevista (passos 9–20)

Roda quando `estudo/PERFIL.md` não existe ou tem campos com placeholder `_(...)_`.
**O agente conduz na conversa**, não o script. Se apresente primeiro:

```
     ___
    (o,o)      M N E M O
    /)_)       guardião da memória
     " "

  Sou o MNEMO. Vou te acompanhar nos estudos e, mais importante,
  vou lembrar do que você aprendeu quando você já tiver esquecido.
  São 13 perguntas para eu saber como te ensinar.
```

Antes de cada pergunta, desenhe a barra — mesma numeração da parte de máquina:

```bash
python3 scripts/mnemo.py bar 13 "Método de ensino"
```
ou escreva na mão, no mesmo formato: `[13/20 ] Método de ensino  ██████████░░░░░░  65%`

### Os 13 passos

| # | Pergunta | Grava em `PERFIL.md` |
|---|---|---|
| 9 | Como te chamo? | Identidade → Como chamar |
| 10 | Seu nível/experiência e sua área/background? (para ancorar exemplos) | Identidade → Nível, Área |
| 11 | Qual a meta do estudo e o contexto? (retenção / prova / aplicar no trabalho) | Objetivo |
| 12 | O que funciona com você e o que te irrita numa explicação? | Estilo de aprendizagem |
| 13 | **Como você aprende melhor?** — apresente os 6 métodos | Método principal |
| 14 | E quando esse método travar, para onde eu caio? | Método de apoio |
| 15 | **Cenário 1** — você travou numa questão. O que eu faço? | (infere postura) |
| 16 | **Cenário 2** — você acertou a ideia mas errou o nome técnico. | (infere postura) |
| 17 | **Cenário 3** — tópico totalmente novo, você prefere… | (infere postura) |
| 18 | **Cenário 4** — sobre ritmo, o que mais te incomoda? | (infere postura) |
| 19 | **Quão rigoroso eu devo ser?** — apresente os 4 níveis | Rigor + mínimo de perguntas |
| 20 | Em que **idioma** eu produzo, e quais **artefatos** eu sempre gero? | Produção no NotebookLM |
| 21 | **Qual seu ritmo?** — bloco de foco, pausa curta, pausa longa | Ritmo da sessão |

**Passo 13 — os 6 métodos** (roteiro completo em [`METODOS_DE_ENSINO.md`](METODOS_DE_ENSINO.md) §1):

```
a) SOCRÁTICO            pergunta que puxa pergunta; você chega sozinho
b) INSTRUÇÃO DIRETA     explicação enxuta e estruturada primeiro, prática depois
c) EXEMPLOS TRABALHADOS você me vê resolvendo passo a passo, depois imita
d) BASEADO EM PROBLEMA  o caso real vem antes da teoria
e) DESCOBERTA GUIADA    você explora, erra de propósito, e aí consolida
f) MASTERY              não avanço enquanto o anterior não fechar 100%
```

**Passos 15–18 — os 4 cenários** estão escritos em `METODOS_DE_ENSINO.md` §3, com o mapeamento de cada alternativa para uma das 5 posturas. A mais marcada vira **dominante**; a segunda, **secundária**. Empate → pergunte qual descreve melhor um bom professor que ele já teve.

**Passo 19 — os 4 níveis de rigor** (escala completa em `METODOS_DE_ENSINO.md` §2):

```
N1 ACOLHEDOR   aceita a ideia com suas palavras; dica assim que você hesita
N2 PADRÃO      exige nome técnico + um exemplo; dica após 1 tentativa
N3 RIGOROSO    +25%: nome + exemplo do SEU contexto + distinguir do conceito vizinho
N4 BANCA       cenário aberto, contestação; você defende a resposta
```
Deixe claro que **dica existe em todos os níveis** — o que muda é quando aparece — e que o padrão do projeto é **N3**.

**Passo 20 — artefatos.** Os tipos que o MCP realmente gera: `audio`, `video`, `infographic`, `mind_map`, `slide_deck`, `quiz`, `flashcards`, `report`, `data_table`. Pergunte quais entram no **conjunto padrão** (gerados a cada etapa, sem pedir) e quais ficam **sob demanda**. Confirme a duração preferida do áudio.

**Passo 21 — ritmo da sessão.** Todo tempo de estudo é cronometrado em blocos de foco por `scripts/sessao.py`. Pergunte os quatro números — **e deixe claro que 25/5 é só o pomodoro clássico, não uma regra**:

```
Bloco de foco             25 min é o clássico. 50 ou 90 servem melhor a
                          quem gosta de entrar fundo; 15 a quem tem
                          janelas picadas do dia.
Pausa curta               entre blocos — padrão 5 min
Pausa longa               depois de vários blocos — padrão 15 min
Blocos até a pausa longa  padrão 4
Blocos por sessão         quantos você costuma fazer de uma vez — padrão 2
```

Se o aluno não fizer ideia, grave os padrões e diga que dá para mudar a qualquer momento no `PERFIL.md` ou por flag na hora (`sessao.py iniciar --bloco 50 --pausa 10`).

### Fechamento

1. [AGENTE] Escreva tudo em `estudo/PERFIL.md` (substitua os placeholders).
2. [AGENTE] Confirme: `python3 scripts/setup.py --dry-run` deve parar de listar campos pendentes.
3. [AGENTE] Feche com a barra em `[21/21 ] Tudo pronto  ████████████████ 100%` e pergunte qual matéria começar.

> Esse perfil dá contexto ao `SKILL.md`, `GUIA_NOTEBOOKLM.md` e `REVISAO_IA.md`. Na Fase PREP, suba `estudo/PERFIL.md` + `GUIA_NOTEBOOKLM.md` como fontes no NotebookLM.

---

## PARTE B — Começar uma matéria nova

1. [HUMANO] Ponha a fonte (PDF/slides/apostila) em `estudo/documentos/`.
2. [AGENTE] **Proponha o roadmap.** Leia a fonte (e pesquise a ementa/edital, se for certificação) e monte 4 a 8 etapas. Para cada uma: **conceitos obrigatórios** + o que fica **fora de escopo**.
3. [HUMANO] Aprova, ajusta ou refaz.
4. [AGENTE] Só então grave em `estudo/progresso/<materia>-roadmap.md` (modelo: `templates/roadmap.md`).
5. [AGENTE] Copie `templates/ledger.md` → `estudo/progresso/<materia>.md`; preencha `materia`, `roadmap`, `fontes`, `deck_anki` e os `topicos` a partir das etapas.
6. [AGENTE] Registre a linha em `estudo/progresso/_index.md` (ledger + roadmap).
7. [AGENTE] Rode o loop (Parte C) a partir da etapa 1.

---

## PARTE C — Operar o loop (toda sessão)

Siga o cérebro em [`.agents/skills/professor/SKILL.md`](.agents/skills/professor/SKILL.md). Resumo executável:

### C0. [AGENTE] Passo zero — sempre

```bash
python3 scripts/status.py
```

Lê o ledger e o `srs.db` e imprime o estado + **por onde a sessão começa**. Rode isto antes de qualquer coisa: o gatilho de Fase 2 abandonada e o modo reentrada não podem depender de o agente lembrar de checar.

```
     ___
   (o,o)   MNEMO · <Matéria>
   /)_)    etapa 2/6 · <Nome da Etapa>
     " "

  Cards vencidos      6             o mais antigo há 1 dia  ·  6 no total
  Fase 2              há 4 dias     material entregue em 2026-07-22
  Última sessão       há 4 dias     2026-07-22
  Tempo (7 dias)      75 min        em 2 sessões  ·  bloco de 25 min
  Rigor               nível 3

───  PRÓXIMO PASSO  ────────────────────────────────────────

  Fase 2 aberta há 4 dias. COMECE por ela: pergunte pelo material
  antes de qualquer conteúdo novo.
```

Ações possíveis e o que fazer com cada uma: tabela na [`SKILL.md`](.agents/skills/professor/SKILL.md) → "Abrir a sessão".

### C1. [AGENTE] Retomar
Leia `estudo/progresso/<materia>.md` → `retomar_em` + `pontos_fracos`. Se houver revisão FSRS vencida, ela vem **antes** de conteúdo novo (`REVISAO_IA.md`) — salvo em modo reentrada, que tem regras próprias.

### C2. [AGENTE] FASE 1 — PREP (via MCP)
1. Abra o roadmap → extraia os **conceitos obrigatórios da etapa atual** e o que está fora de escopo.
2. **Recorte a fonte:** salve `estudo/documentos/<materia>-<etapa>.md` só com o conteúdo da etapa. **Não suba o PDF inteiro.**
2b. **Decomponha a etapa em 3 a 6 subtópicos** (`artefatos/_index.md` §2). Etapa já aberta → use os que estão no roadmap. Primeira PREP da etapa → proponha, grave no campo `subtopicos` da etapa e congele até ela fechar.
3. `notebook_list` / `notebook_create` → garanta o notebook da matéria.
4. `source_add` → o `.md` recortado **+ `estudo/PERFIL.md` + `GUIA_NOTEBOOKLM.md`**.
5. `studio_create` → **um por artefato POR SUBTÓPICO**, mais os integradores da etapa no fim:

   | Por subtópico | Por etapa (depois de todos) |
   |---|---|
   | `audio` · `video` · `slide_deck` · `report` · `infographic` · `quiz` · `flashcards` | `mind_map` · `data_table` · quiz integrador |

   Antes de disparar, faça a conta: `(tipos por subtópico × nº subtópicos) + tipos por etapa`. Passou de 12, avise o aluno; passou de 20, pare e pergunte.

   O `focus_prompt` de cada um segue o esqueleto do `artefatos/_index.md` §5 — o bloco `[FORMATO]` é **copiado do arquivo do tipo** em `artefatos/<tipo>.md`, não improvisado. Em **todo** `[ESCOPO]`: conceitos **do subtópico** + proibição de citar os outros subtópicos e etapas futuras + `language` do perfil.

   Acompanhe com `studio_status` e renomeie tudo: `studio_status(action="rename", ...)` → `E<etapa>.<subtópico> · <Nome> — <Tipo>`.
6. Avise: etapa, **quais são os subtópicos e em que ordem consumir**, 80/20, o que ficou pronto, e entregue o **prompt calibrado** para o chat. Lista numerada por subtópico, não agrupada por tipo.
7. **Grave `fase2_iniciada_em: <hoje>` no ledger.** Sem isso o material entregue pode virar consumo passivo esquecido, sem ninguém notar.
8. Convide a cronometrar: *"quando for começar, me diga **iniciar**."*

### C3. [HUMANO] FASE 2 — STUDY
Estude no NotebookLM: áudio no deslocamento, responda o quiz, tire dúvidas com citação.

**Cronometrando.** Diga "iniciar" e o agente roda:

```bash
python3 scripts/sessao.py iniciar
python3 scripts/sessao.py iniciar --bloco 50 --pausa 10 --blocos 3   # ritmo diferente hoje
python3 scripts/sessao.py agora                                      # o que está aberto
python3 scripts/sessao.py fim --absorvido "<conceito A> ficou; <conceito B> ainda confuso"
```

Ele imprime o horário de cada bloco e pausa e sai do caminho — não há contagem regressiva ocupando o terminal. Os padrões vêm do `PERFIL.md` → "Ritmo da sessão".

> O tempo gravado só é lido cruzado com o recall (`status.py --performance`). Ver `REVISAO_IA.md` → "Performance: tempo cruzado com retenção".

**No retorno, o agente pergunta uma coisa só:** *"me diga um conceito que você não conseguiria explicar agora"*. Placar e detalhe saem do recall da Fase 3 — pedir relatório na porta de entrada só reduz a chance de o aluno voltar.

### C4. [AGENTE] FASE 3 — PROGRESS

1. **Recall em cloze progressivo**, no mínimo o nº de perguntas do perfil (padrão 7), com o tamanho de lacuna do nível de rigor. Dica rebaixa a questão um nível e limita o rating a 2.

   **Composição por cotas** — a partir da etapa 3, não podem ser 7 perguntas da etapa atual:

   | Cota | Tipo | De onde sai |
   |---|---|---|
   | 3 | `recall` | conceitos da etapa atual |
   | 2 | `intercalado` | etapas dominadas, via `conecta_com` do roadmap |
   | 1 | `sintese` | combina a etapa atual com uma anterior |
   | 1 | `transferencia` | mesmo conceito, superfície nova |

   Etapas 1 e 2: 5 `recall` + 2 `transferencia`. Detalhe em `METODOS_DE_ENSINO.md` §5 e §6.

   **Antes de revelar cada resposta, pergunte a confiança** (`vou acertar` / `mais ou menos` / `não vou acertar`) e registre. Ao fim, devolva o desencontro em uma linha.
2. Atualize o **ledger** (`Edit`): `topicos[].status`, `passo_loop`, `retomar_em`; **todo erro vira `pontos_fracos`**.
3. Atualize o **FSRS** com `python3 scripts/revisar.py revisar --card-id <id> --rating <1-4> --confianca <0-2> --tentativas <n> --usou-dica <0|1> --tipo-item <tipo>` (o script calcula o intervalo e grava `cards` + `review_log`); crie cards dos erros com `revisar.py criar`. **Nunca por SQL na mão** — ver `REVISAO_IA.md`.
4. Atualize o **roadmap** (`etapa_atual`, status da etapa) e o `_index.md`. A etapa só vira `dominada` se passar no **portão N4** — 2 itens de cenário aberto, sem dica.
5. Linha nova no `## Log de aprendizado`, atualize `atualizado:` e `ultima_sessao:`, e **limpe `fase2_iniciada_em:`** — a Fase 2 se fechou.
6. Etapa dominada → **prévia estruturante** do que vem (2-3 frases, via `prepara_para`), gere o **badge** `estudo/progresso/jornada_do_heroi.jpg` e atualize `estudo/JORNADA.md`.

**Relatórios de acompanhamento:**

```bash
python3 scripts/status.py --calibracao    # o aluno sabe o que não sabe?
python3 scripts/status.py --fila          # fila de hoje, intercalada por tópico
python3 scripts/status.py --performance   # tempo cruzado com retenção
```

**Escrita no `srs.db` — sempre por `scripts/revisar.py`:**

```bash
python3 scripts/revisar.py pendentes --json           # fila de hoje (com back, para o agente)
python3 scripts/revisar.py pendentes --reentrada      # teto de 8, maior estabilidade primeiro
python3 scripts/revisar.py revisar --card-id 12 --rating 3 --confianca 2 \
    --tentativas 1 --usou-dica 0 --tipo-item recall
python3 scripts/revisar.py criar --front "..." --back "..." --deck "..." --subject "..."
python3 scripts/revisar.py espalhar --dias 5 --confirmar
```

Os comandos são idempotentes: revisar o mesmo card duas vezes no mesmo dia não duplica nem recalcula, e `criar` deduplica por `front`.

**Grafo de conhecimento** (nós = conceitos, arestas = dependências e pontes):

```bash
python3 scripts/grafo.py              # regera estudo/progresso/<materia>-grafo.html
python3 scripts/grafo.py --validar    # problemas (conserte) x pendências (dívida)
python3 scripts/grafo.py --materia <slug>   # outra matéria que não a ativa
```

Cada nó é um arquivo em `estudo/progresso/<materia>-conceitos/` (modelo: `templates/conceito.md`). A anotação do nó é **a explicação do aluno no portão, conferida na fonte** — ver `SKILL.md` Fase 3 passo 5c. O nó **desbota** conforme a retenção do FSRS cai e **pulsa** quando há card vencido, então o grafo cresce e apaga em vez de só acumular verde.

### C5. Modo reentrada — quando o aluno volta depois de sumir

Disparado automaticamente pelo `status.py` com **10+ dias sem sessão** ou **backlog acima de 15 cards**. Tem precedência sobre a revisão normal.

| | Sessão normal | Modo reentrada |
|---|---|---|
| Quantidade | até 20 cards | **teto de 8** |
| Ordem | mais vencido primeiro | **maior estabilidade primeiro** |
| Conteúdo novo | permitido após a revisão | **nenhum** |
| Dica | conforme o nível de rigor | **1 tentativa antes** |
| Régua do rating | conforme o nível | **inalterada** |

A régua não muda de propósito: baixar o rigor inflaria o rating, que infla o intervalo, que esconde a lacuna. Adiantar a dica acolhe sem mentir para o agendamento — dica já limita o rating a 2.

Ao fim, **ofereça** espalhar o backlog restante pelos próximos dias: `python3 scripts/revisar.py espalhar --dias 5 --confirmar`. O `--confirmar` é obrigatório justamente porque `due_date` é a fonte da verdade do progresso — sem ele o comando recusa (`REVISAO_IA.md` §1c).

---

## PARTE D — Atualizar o MCP com segurança

O MCP é código de terceiro que dirige uma sessão real do Google. **Nunca atualize às cegas.**

```bash
python3 scripts/mcp_update.py             # checa e audita — não altera nada
python3 scripts/mcp_update.py --apply     # aplica, se a auditoria permitir
```

O que a auditoria olha **só nas linhas adicionadas** entre o pin atual e o candidato:

| Severidade | Exemplos |
|---|---|
| **ALTA** — bloqueia o `--apply` | `eval`/`exec`, `os.system`, `shell=True`, `pickle.loads`, import dinâmico, `compile(..., "exec")` |
| **MÉDIA** — pede revisão | ofuscação por base64, `ctypes`, leitura de `~/.ssh`/`~/.aws`, varredura de `os.environ`, persistência (crontab, LaunchAgents, registro) |
| **INFO** | endpoints de rede fora do Google/GitHub/PyPI |

Também compara **dependências novas** em `pyproject.toml`/`requirements.txt` (o vetor de supply chain mais comum) e sinaliza arquivos sensíveis tocados (licença, workflows de CI, `Dockerfile`).

**Regra:** com achado ALTA, `--apply` é bloqueado. Só `--force-approve` passa por cima — e o motivo fica gravado no `historico` do `.agents/mcp_pin.json`. O agente **nunca** usa essa flag sozinho.

Depois de aplicar, **reinicie o agente** para recarregar o MCP.

> ⚠️ O projeto upstream se renomeou de *NotebookLM MCP* para *Gemini Notebook MCP* (repo `gemini-notebook-mcp-cli`). A URL antiga ainda funciona por redirect do GitHub. Se um dia o clone falhar, atualize `repo` em `.agents/mcp_pin.json`.

---

## PARTE E — Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| Não sei o que está errado | — | `python3 scripts/setup.py --dry-run` e depois `nlm doctor` |
| `nlm` não encontrado | `~/.local/bin` fora do PATH | Linux/macOS: `export PATH="$HOME/.local/bin:$PATH"` · Windows: adicione `%USERPROFILE%\.local\bin` ao PATH e abra outro terminal |
| Tools do NotebookLM não aparecem | auth expirada (2–4 semanas) | `nlm login` de novo |
| MCP não conecta no agente | config errado | conferir `command: "notebooklm-mcp"` em `.agents/mcp_config.json`; recarregar |
| `uv` não instala no Windows | política do PowerShell | rode o comando do passo 2 num PowerShell com `-ExecutionPolicy ByPass` |
| Acentos viram lixo no terminal do Windows | console em cp1252 | `chcp 65001` antes de rodar, ou use o Windows Terminal |
| Quero reinstalar o MCP | — | `python3 scripts/setup.py` (o clone em `vendor/` é reaproveitado) |
| "Compartilhar" não funciona | é de propósito (least privilege) | manter desligado |
| Artefato saiu no idioma errado | `language` não foi passado | conferir o `language` do perfil no `studio_create` e se `PERFIL.md` está como source |
| O material avançou pra etapa futura | `focus_prompt` sem o trilho | reincluir a lista de conceitos da etapa + a proibição explícita |
| Saiu 1 artefato só, cobrindo a etapa inteira | PREP pulou a decomposição em subtópicos | refazer o passo C2.2b e regerar por subtópico (`artefatos/_index.md`) |
| Todo artefato de subtópico repete a etapa inteira "pra contextualizar" | faltou a 2ª trava do `[ESCOPO]` | reincluir a proibição de citar os **outros subtópicos**, nomeando-os |
| Deck saiu como lista de tópicos | `focus_prompt` sem o bloco `[FORMATO]` do tipo | copiar o bloco de `artefatos/slide_deck.md`; regerar ou usar `studio_revise` nos slides ruins |
| Guia de estudo saiu como resumo corrido | idem | copiar o bloco de `artefatos/report.md` — o formato é guia de perguntas, não resumo |
| Quiz fácil demais, o aluno acerta tudo | distratores fracos | `artefatos/quiz.md` §2: distrator tem de vir de uma confusão real e nomeável |
| Volume de artefatos assustou o aluno | conta de volume não foi feita | cortar para 2–3 tipos por subtópico (`artefatos/_index.md` §4) |
