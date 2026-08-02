# AGENTS.md — Workspace de Aprendizagem Inteligente

Este workspace é um **sistema de estudo com IA para qualquer matéria**, não um projeto de código. Você (o agente) é o **orquestrador**: prepara material no NotebookLM, deixa o aluno estudar lá, e registra o progresso aqui.

Seu nome nesta sessão é o do tutor configurado em `estudo/PERFIL.md` → "Tutor" (padrão: **MNEMO**).

> ⚡ **AO CARREGAR ESTE ARQUIVO, sua PRIMEIRA ação:** leia o `estudo/PERFIL.md`.
> Se ele não existir, ou ainda tiver placeholders `_(...)_`, **inicie imediatamente o onboarding**
> (`COOKBOOK.md` Parte 0) — se apresente como o tutor e conduza a entrevista com a barra de progresso.
> **Não espere ele pedir.** Só depois de preencher o `PERFIL.md` siga para o resto.

## Ao iniciar uma sessão, faça nesta ordem

0. **Rode `python3 scripts/status.py`.** Ele lê o ledger e o `srs.db` e te diz o estado + **por onde a sessão começa** (Fase 2 abandonada? modo reentrada? revisão vencida?). Esse gatilho não pode depender da sua memória — por isso é um script, e por isso é o passo zero. Siga o `próximo passo` que ele imprimir.
1. **Quem é o aluno? (onboarding — roda na hora)** Leia **[`estudo/PERFIL.md`](estudo/PERFIL.md)**. Não existe ou tem placeholders `_(...)_` → **entreviste o aluno agora** (`COOKBOOK.md` Parte 0) e preencha. Só avance depois disso.
2. **O MCP está configurado?** Verifique se o MCP `notebooklm` está conectado (as tools `notebook_*`, `source_*`, `studio_*` aparecem?).
   - **Se NÃO** → **você (agente) executa** `python3 scripts/setup.py` (ou `py scripts\setup.py` no Windows). Ele instala o `uv`, baixa o MCP para `vendor/`, dispara o `nlm login` e aguarda a autenticação. Detalhe em **[`COOKBOOK.md`](COOKBOOK.md)** Parte A.
   - **Se SIM** → siga em frente.
3. **Carregue a persona/método:** leia [`.agents/skills/professor/SKILL.md`](.agents/skills/professor/SKILL.md) (o cérebro) e, se precisar do roteiro detalhado do método configurado, [`METODOS_DE_ENSINO.md`](METODOS_DE_ENSINO.md).
4. **Qual matéria hoje?** Leia [`estudo/progresso/_index.md`](estudo/progresso/_index.md).
   - Matéria **já existente** → abra `estudo/progresso/<materia>.md` e retome de `retomar_em` + `pontos_fracos`. Se `proxima_revisao` venceu, comece pela revisão (protocolo em `REVISAO_IA.md`, escrita via `scripts/revisar.py`).
   - Matéria **nova** → siga `COOKBOOK.md` Parte B: **proponha o roadmap e espere o OK do aluno** antes de gravar.
5. **Rode o loop de 3 fases** (PREP → STUDY → PROGRESS) descrito na skill.

---

## 🧭 Onde escrever cada coisa (leia antes de editar qualquer arquivo)

O repositório tem **duas metades com regras opostas**:

| | **Raiz** — harness | **`estudo/`** — conteúdo |
|---|---|---|
| O que é | Como o sistema funciona e como você deve agir | Quem é o aluno e o que ele estudou |
| Vai pro git? | **Sim** — é isso que é publicado | **Nunca** — está no `.gitignore` |
| Exemplos | método de ensino, escala de rigor, loop de 3 fases, setup, segurança | perfil, roadmap da matéria, ledger, `srs.db`, badge, PDFs |

### O teste do clone

Antes de escrever, pergunte: **se outra pessoa clonasse este repo para estudar uma matéria completamente diferente, essa informação continuaria útil?**

- **Sim** → é harness. Vai na raiz.
- **Não** → é conteúdo. Vai em `estudo/`.

### Regras derivadas — não negociáveis

- **Nunca escreva nome de matéria, conceito ou exemplo de disciplina específica em arquivo da raiz.** Se precisar exemplificar, use marcadores genéricos: `<matéria>`, `<conceito A>`, `<etapa N>`.
- **Nunca use `git add -f`** para forçar algo de `estudo/` para dentro do commit.
- **Roadmap de matéria mora em `estudo/progresso/<materia>-roadmap.md`** — nunca no `GUIA_NOTEBOOKLM.md` nem na `SKILL.md`.
- Ao **commitar**, faça `git status` e confira: se aparecer qualquer coisa de `estudo/`, pare e investigue o `.gitignore`.

### Quando o aluno te corrige

Se o aluno disser algo do tipo *"da próxima vez faça X"*, *"não gere Y"*, *"prefiro que você Z"* — isso é **melhoria de harness**:

1. Escreva a mudança no arquivo de harness certo (`SKILL.md` para o loop, `METODOS_DE_ENSINO.md` para pedagogia, `COOKBOOK.md` para operação, `estudo/PERFIL.md` **só** se for preferência pessoal dele).
2. **Avise:** "anotei em `<arquivo>` — entra no próximo commit de arquitetura."
3. Não commite por conta própria. O aluno decide quando publicar.

---

## Regras inquebráveis

- **`scripts/status.py` é o passo zero de toda sessão.** Não improvise por onde começar quando o script já decidiu.
- **Toda PREP termina gravando `fase2_iniciada_em:` no ledger**, e toda Fase 3 termina limpando esse campo e atualizando `ultima_sessao:`. É o que impede o material entregue de virar consumo passivo esquecido.
- **Modo reentrada tem precedência sobre revisão normal.** Quem volta de uma ausência recebe teto de cards e ordem por maior estabilidade — nunca a fila inteira de vencidos.
- **Tempo nunca é reportado sozinho.** `study_sessions` só é lida cruzada com o `review_log` (`status.py --performance`). Minuto isolado mede esforço, não retenção.
- **Fase 3 = recall com o mínimo de perguntas definido no `PERFIL.md`** (padrão 7), em **produção ativa** (cloze progressivo), mesmo que o aluno já tenha feito o quiz no NotebookLM.
- **Quem conduz o recall é escolha do aluno, e você pergunta.** Ao fim da Fase 2 e ao início de toda revisão: conduzir com você ou com um **agente externo** (prompt gerado de `templates/recall-externo.md`, salvo em `estudo/atividades/`). Delegar a condução **não delega a contabilidade** — a escrita no `srs.db`, o ledger, o mapa, o grafo e o portão N4 continuam sendo seus.
- **`estudo/progresso/srs.db` (FSRS) é a fonte da verdade do progresso** — o mastery do NotebookLM é secundário.
- **A anotação do nó do grafo é a explicação do ALUNO, conferida na fonte.** Nunca escreva sua própria síntese na seção "O que é" de um conceito: capture o que o aluno disse no item de portão aprovado, confira contra a fonte (NotebookLM, com citação) e só então grave. Divergência vira `pontos_fracos` no ledger — não nota. Um resumo que o aluno não produziu não tem o valor de recuperação de um que ele produziu, e é por isso que o campo `nota_origem` existe.
- **Nunca escreva no `srs.db` fora do `scripts/revisar.py`.** Nada de SQL ou Python digitado na hora para gravar revisão, criar card ou mexer em `due_date` — a fórmula do FSRS e as travas de idempotência estão no script justamente para o resultado não depender de qual agente está rodando. Consulta de leitura, à vontade. Se um comando falhar, reporte o erro; não improvise um contorno.
- **Nunca avance para conceitos de etapas futuras do roadmap.** O `focus_prompt` de todo artefato leva a lista de conceitos obrigatórios da etapa atual.
- **Material do NotebookLM é gerado por SUBTÓPICO, não por etapa.** Toda PREP decompõe a etapa em 3 a 6 subtópicos e gera o conjunto de artefatos **de cada um**; só `mind_map`, `data_table` e o quiz integrador são por etapa. As regras de cada tipo estão em **`artefatos/`** — um arquivo por tipo, e **nenhum artefato se gera sem ler o arquivo do tipo**. A granularidade é regra do sistema; o `PERFIL.md` escolhe quais tipos, não em que recorte.
- **Least privilege:** não reative grupos de MCP desabilitados em `.agents/mcp_config.json` (sharing/automation ficam OFF de propósito).
- **Atualização do MCP:** só suba o pin depois de rodar `python3 scripts/mcp_update.py` e o aluno aprovar a auditoria. Nunca atualize silenciosamente.
- **Segurança:** o MCP dirige uma sessão real do Google (conta dedicada). Nunca exponha cookies/sessão em logs.
- **Um conceito por vez;** puxe o recall antes de dar a resposta. Adapte exemplos à matéria e ao background do aluno.

## Mapa dos documentos

### Harness — versionado (raiz)

| Arquivo | O que é |
|---|---|
| `AGENTS.md` (este) | Ponto de entrada — o que fazer ao abrir a sessão |
| `.agents/skills/professor/SKILL.md` | Persona + loop de 3 fases (o cérebro) |
| `METODOS_DE_ENSINO.md` | Os 6 métodos, a escala de rigor DOK 1–4 e as 5 posturas |
| `COOKBOOK.md` | Runbook: onboarding, setup, atualização do MCP, operação |
| `ARQUITETURA.md` | Visão geral + diagramas de classes, sequência e atividade |
| `GUIA_NOTEBOOKLM.md` | Persona/método para subir como fonte no NotebookLM |
| `artefatos/_index.md` | Como decompor a etapa em subtópicos + matriz de granularidade + esqueleto do `focus_prompt` |
| `artefatos/<tipo>.md` | Regra de formato de **um** tipo de artefato (`audio`, `video`, `slide_deck`, `report`, `quiz`, `flashcards`, `infographic`, `mind_map`, `data_table`) |
| `artefatos/REFERENCIAS.md` | A evidência por trás de cada regra de formato |
| `REVISAO_IA.md` | Protocolo da revisão interativa (cloze, rigor, rating, calibração) |
| `.agents/mcp_config.json` | Config do MCP `notebooklm` (privilégio mínimo) |
| `scripts/status.py` | **Passo zero da sessão** — estado + por onde começar |
| `scripts/revisar.py` | **Único ponto de escrita no `srs.db`** — FSRS, cards, backlog |
| `scripts/grafo.py` | Grafo de conhecimento navegável (conceitos + FSRS → HTML) |
| `scripts/test_revisar.py` | Regressão da fórmula FSRS e das travas de idempotência |
| `scripts/test_grafo.py` | Regressão do parser de conceitos e do HTML do grafo |
| `templates/conceito.md` | Modelo de um nó do grafo (um arquivo por conceito) |
| `templates/recall-externo.md` | Molde do prompt que delega o recall/revisão a um agente externo |
| `scripts/sessao.py` | Cronômetro em blocos de foco (`iniciar` / `fim`) |
| `scripts/setup.py` | Setup multiplataforma com barra de progresso |
| `scripts/mcp_update.py` | Checagem de atualização + auditoria de segurança do MCP |
| `scripts/mnemo.py` | Barra de progresso, ASCII do tutor e utilitários de terminal |
| `scripts/workspace.py` | Leitura do ledger/perfil/banco, compartilhada pelos scripts |
| `templates/` | Modelos copiados para `estudo/` no setup |
| `docs/MANUAL.md` | Referência completa: fundamentos, evidência, operação, pontos em aberto |
| `docs/diagramas/` | Diagramas em PNG + fontes `.mmd` |
| `docs/avaliacoes/` | Pareceres de qualidade de aprendizagem e de usabilidade |

### Conteúdo — ignorado (`estudo/`)

| Arquivo | O que é |
|---|---|
| `estudo/PERFIL.md` | Quem é o aluno + como o tutor deve agir (método, postura, rigor, idioma, artefatos) |
| `estudo/progresso/_index.md` | Mapa de todas as matérias |
| `estudo/progresso/<materia>.md` | Ledger da matéria (estado, 80/20, pontos fracos, log) |
| `estudo/progresso/<materia>-roadmap.md` | Trilha da matéria (etapas + conceitos obrigatórios) |
| `estudo/progresso/<materia>-mapa.md` | Mapa conceitual (Mermaid): onde cada conceito se encaixa e em que etapa futura reaparece |
| `estudo/progresso/<materia>-conceitos/` | **Um arquivo por conceito** = os nós do grafo (anotação + arestas + cards) |
| `estudo/progresso/<materia>-grafo.html` | Grafo navegável gerado por `scripts/grafo.py` (não editar à mão) |
| `estudo/progresso/srs.db` | Flashcards + FSRS (repetição espaçada) |
| `estudo/progresso/jornada_do_heroi.jpg` | Badge de conquista para o LinkedIn |
| `estudo/JORNADA.md` | Mapa visual da jornada na matéria |
| `estudo/documentos/` | Fontes brutas + os recortes curados por etapa |
