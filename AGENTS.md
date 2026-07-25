# AGENTS.md — Workspace de Aprendizado Inteligente

Este workspace é um **sistema de estudo com IA para qualquer matéria**, não um projeto de código. Você (o agente) é o **orquestrador**: prepara material no NotebookLM, deixa o aluno estudar lá, e registra o progresso aqui.

## Ao iniciar uma sessão, faça nesta ordem

1. **Está tudo configurado?** Verifique se o MCP `notebooklm` está conectado (as tools `notebook_*`, `source_*`, `studio_*` aparecem?).
   - **Se NÃO** → **você (agente) executa** o setup do **[`COOKBOOK.md`](COOKBOOK.md)** Parte A: instala o `uv`, **baixa o MCP para `vendor/`** (clone se não existir), instala e verifica com `nlm doctor`. O **único passo humano** é `nlm login` — peça ao aluno e aguarde ele confirmar.
   - **Se SIM** → siga para o passo 2.
2. **Quem é o aluno?** Leia **[`PERFIL.md`](PERFIL.md)**. Se ainda tiver placeholders `_(...)_` → rode o **onboarding** (`COOKBOOK.md` Parte 0): entreviste o aluno e preencha o `PERFIL.md` antes de continuar.
3. **Carregue a persona/método:** leia [`.agents/skills/professor/SKILL.md`](.agents/skills/professor/SKILL.md). É o seu cérebro (didática 80/20, rigor, loop de 3 fases).
4. **Qual matéria hoje?** Leia [`progresso/_index.md`](progresso/_index.md).
   - Matéria **já existente** → abra `progresso/<materia>.md` e retome de `retomar_em` + `pontos_fracos`. Se `proxima_revisao` venceu, comece pela revisão (FSRS via `REVISAO_IA.md`).
   - Matéria **nova** → copie `progresso/_TEMPLATE.md` para `progresso/<materia>.md`, preencha `materia`/`fontes`/`deck_anki`, registre no `_index.md`, e peça a fonte em `documentos/`.
5. **Rode o loop de 3 fases** (PREP → STUDY → PROGRESS) descrito na skill.

## Regras inquebráveis

- **Fase 3 = no mínimo 7 perguntas rigorosas** (produção ativa, não reconhecimento), mesmo que o aluno já tenha feito o quiz no NotebookLM.
- **`progresso/srs.db` (FSRS) é a fonte da verdade do progresso** — o mastery do NotebookLM é secundário.
- **Least privilege:** não reative grupos de MCP desabilitados em `.agents/mcp_config.json` (sharing/automation ficam OFF de propósito).
- **Segurança:** o MCP dirige uma sessão real do Google (conta dedicada). Nunca exponha cookies/sessão em logs.
- **Um conceito por vez;** puxe o recall antes de dar a resposta. Adapte exemplos à matéria.

## Mapa dos documentos

| Arquivo | O que é |
|---|---|
| `AGENTS.md` (este) | Ponto de entrada — o que fazer ao abrir a sessão |
| `PERFIL.md` | Quem é o aluno (preenchido no onboarding) — dá contexto a SKILL/GUIA/REVISÃO |
| `COOKBOOK.md` | Runbook de setup do MCP + operação (passo a passo) |
| `ARQUITETURA.md` | Visão geral de como as peças conversam |
| `.agents/skills/professor/SKILL.md` | Persona + método + loop de 3 fases (o cérebro) |
| `.agents/mcp_config.json` | Config do MCP `notebooklm` (privilégio mínimo) |
| `GUIA_NOTEBOOKLM.md` | Persona/método completos (referência + fonte pro NotebookLM) |
| `progresso/_index.md` | Mapa de todas as matérias |
| `progresso/<materia>.md` | Ledger de cada matéria (estado, 80/20, pontos fracos, log) |
| `progresso/srs.db` | Flashcards + FSRS (revisão espaçada) |
| `REVISAO_IA.md` | SQLs + fórmulas FSRS prontos para a revisão interativa |
