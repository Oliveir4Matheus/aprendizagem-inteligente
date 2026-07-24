# 🧠 Aprendizado Inteligente

Um **sistema de estudo com IA** para **qualquer matéria**. Um agente orquestrador
(Antigravity CLI ou Claude Code) prepara o material no **NotebookLM**, você estuda
lá, e o progresso fica registrado aqui — com **repetição espaçada (FSRS)** de verdade.

Não é um projeto de código: é um **workspace de estudo reutilizável**.

## ⚡ Quickstart

```bash
# 1) Configurar o MCP do NotebookLM (uma vez) — abre o browser p/ login
bash scripts/setup.sh

# 2) Começar uma matéria
cp progresso/_TEMPLATE.md progresso/minha-materia.md   # edite materia/fontes
#    e ponha o PDF/slides em documentos/

# 3) Abra o agente (Antigravity CLI / Claude Code) NESTE diretório.
#    Ele lê o AGENTS.md e conduz o resto. Diga: "siga o AGENTS.md".
```

## O método (base científica)

Técnicas de estudo com maior evidência (Dunlosky et al. 2013):
**recordação ativa** + **repetição espaçada** + **Feynman** + **elaboração** + **80/20**.
Cada tópico roda um loop: ensinar enxuto → você explica de volta → **mini-teste de ≥7
perguntas rigorosas** → vira flashcard → revisão espaçada.

## As 3 ferramentas (cada uma no que faz melhor)

| Ferramenta | Papel |
|---|---|
| **Orquestrador** (Antigravity/Claude Code) | Conduz o loop, prepara material, registra progresso |
| **NotebookLM** | Superfície de estudo: áudio, quiz, study guide, Q&A com citação |
| **FSRS** (`progresso/srs.db`) | Repetição espaçada — o timing das revisões |

Visão completa em [`ARQUITETURA.md`](ARQUITETURA.md).

## Como usar

1. **Configure o MCP do NotebookLM uma vez** → siga [`COOKBOOK.md`](COOKBOOK.md) (Parte A).
2. **Comece uma matéria** → copie `progresso/_TEMPLATE.md` para `progresso/<materia>.md`,
   registre em `progresso/_index.md`, e ponha a fonte (PDF/slides) em `documentos/`.
3. **Abra o agente neste workspace** → ele lê o [`AGENTS.md`](AGENTS.md) e conduz o resto.

## Estrutura

```
aprendizado-inteligente/
├── AGENTS.md            ← entrada auto-lida pelo agente
├── COOKBOOK.md          ← setup do MCP + como operar o loop
├── ARQUITETURA.md       ← mapa das peças
├── GUIA_NOTEBOOKLM.md   ← persona + método (e fonte pro NotebookLM)
├── REVISAO_IA.md        ← SQLs + FSRS da revisão interativa
├── .agents/
│   ├── mcp_config.json          ← MCP com privilégio mínimo
│   └── skills/professor/SKILL.md ← o cérebro (persona + loop 3 fases)
├── documentos/          ← suas fontes (um conjunto por matéria)
└── progresso/
    ├── _index.md        ← mapa das matérias
    ├── _TEMPLATE.md     ← modelo de ledger por matéria
    └── srs.db           ← flashcards + FSRS (vazio no template)
```

> **Requer** o MCP do NotebookLM (não oficial, MIT). Auditoria e hardening no `COOKBOOK.md` / `ARQUITETURA.md`.
