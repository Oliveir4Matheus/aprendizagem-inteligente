# COOKBOOK — Setup e operação (executado pelo AGENTE)

Este runbook é feito para **o agente executar**. Legenda: **[AGENTE]** = o orquestrador roda; **[HUMANO]** = ação do aluno.

O setup é **uma numeração contínua de 20 passos**:

```
passos  1–8   parte de MÁQUINA      → scripts/setup.py faz sozinho
passos  9–20  ENTREVISTA (onboarding) → o agente conduz, na conversa
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
  São 12 perguntas para eu saber como te ensinar.
```

Antes de cada pergunta, desenhe a barra — mesma numeração da parte de máquina:

```bash
python3 scripts/mnemo.py bar 13 "Método de ensino"
```
ou escreva na mão, no mesmo formato: `[13/20 ] Método de ensino  ██████████░░░░░░  65%`

### Os 12 passos

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

### Fechamento

1. [AGENTE] Escreva tudo em `estudo/PERFIL.md` (substitua os placeholders).
2. [AGENTE] Confirme: `python3 scripts/setup.py --dry-run` deve parar de listar campos pendentes.
3. [AGENTE] Feche com a barra em `[20/20 ] Tudo pronto  ████████████████ 100%` e pergunte qual matéria começar.

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

### C1. [AGENTE] Retomar
Leia `estudo/progresso/<materia>.md` → `retomar_em` + `pontos_fracos`. Se houver revisão FSRS vencida, ela vem **antes** de conteúdo novo (`REVISAO_IA.md`).

### C2. [AGENTE] FASE 1 — PREP (via MCP)
1. Abra o roadmap → extraia os **conceitos obrigatórios da etapa atual** e o que está fora de escopo.
2. **Recorte a fonte:** salve `estudo/documentos/<materia>-<etapa>.md` só com o conteúdo da etapa. **Não suba o PDF inteiro.**
3. `notebook_list` / `notebook_create` → garanta o notebook da matéria.
4. `source_add` → o `.md` recortado **+ `estudo/PERFIL.md` + `GUIA_NOTEBOOKLM.md`**.
5. `studio_create` → um por artefato do conjunto padrão do `PERFIL.md`. Acompanhe com `studio_status`. Em **todo** `focus_prompt`: a lista de conceitos da etapa + proibição de avançar + `language` do perfil.
6. Avise: etapa, 80/20, o que ficou pronto, e entregue o **prompt calibrado** para o chat.

### C3. [HUMANO] FASE 2 — STUDY
Estude no NotebookLM: áudio no deslocamento, responda o quiz, tire dúvidas com citação.

### C4. [AGENTE] FASE 3 — PROGRESS
1. **Recall em cloze progressivo**, no mínimo o nº de perguntas do perfil (padrão 7), com o tamanho de lacuna do nível de rigor. Dica rebaixa a questão um nível e limita o rating a 2.
2. Atualize o **ledger** (`Edit`): `topicos[].status`, `passo_loop`, `retomar_em`; **todo erro vira `pontos_fracos`**.
3. Atualize o **FSRS** em `estudo/progresso/srs.db` (`REVISAO_IA.md`): rating 1–4, novo intervalo, `cards` + `review_log`; crie cards dos erros (sem duplicar pelo `front`).
4. Atualize o **roadmap** (`etapa_atual`, status da etapa) e o `_index.md`.
5. Linha nova no `## Log de aprendizado` + `atualizado:`.
6. Etapa dominada → gere o **badge** `estudo/progresso/jornada_do_heroi.jpg` e atualize `estudo/JORNADA.md`.

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
