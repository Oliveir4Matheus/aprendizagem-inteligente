# 🧠 Aprendizagem Inteligente

Um **sistema de estudo com IA** para **qualquer matéria**. Um agente orquestrador
(Antigravity CLI ou Claude Code) prepara o material no **NotebookLM**, você estuda
lá, e o progresso fica registrado aqui — com **repetição espaçada (FSRS)** de verdade.

Não é um projeto de código: é um **workspace de estudo reutilizável**.

## ⚡ Quickstart

O **agente faz o setup** seguindo o `COOKBOOK.md` — você só faz o `nlm login` (browser) quando ele pedir.

```text
1) Abra o agente (Antigravity CLI / Claude Code) NESTE diretório e diga:
   "configure o setup seguindo o COOKBOOK.md"
   → na 1ª vez ele te ENTREVISTA (onboarding) e preenche o PERFIL.md.
   → instala o uv, baixa o MCP para ./vendor/ e instala, sozinho.
   → quando ele pedir, rode você:  nlm login   (conta dedicada)

2) "comece a matéria X" — ele copia o _TEMPLATE, registra no _index e pede a fonte.
   (você põe o PDF/slides em documentos/)

3) "rode o loop de estudo" — PREP → você estuda no NotebookLM → PROGRESS.
```

> Alternativa manual: `bash scripts/setup.sh` faz a parte de máquina (tudo menos o `nlm login`).

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
├── PERFIL.md            ← quem é o aluno (preenchido no onboarding)
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
