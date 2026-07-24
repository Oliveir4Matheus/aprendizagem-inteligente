# Arquitetura de Estudo — Orquestrador + NotebookLM + FSRS

> Como as peças conversam para transformar qualquer fonte (PDF/slides/apostila) em aprendizado com retenção de longo prazo. O **agente orquestrador** (Antigravity CLI ou Claude Code) prepara material no **NotebookLM**, você estuda lá, e o **workspace** guarda o progresso.

---

## 1. Visão geral — quem é quem

```
┌───────────────────────────────────────────────────────────────────────┐
│  WORKSPACE:  aprendizado-inteligente   (o repo que o agente opera)      │
│                                                                         │
│   documentos/<sua-fonte>.pdf          ← conteúdo bruto (fonte)          │
│   progresso/<materia>.md              ← LEDGER (estado + 80/20 + log)   │
│   progresso/srs.db                    ← FSRS = fonte da verdade do que  │
│                                          você domina                    │
│   GUIA_NOTEBOOKLM.md                  ← persona + método (referência)   │
│   .agents/                                                              │
│     ├── skills/professor/SKILL.md ← O CÉREBRO (persona + loop 3 fases)  │
│     └── mcp_config.json           ← liga o MCP com privilégio mínimo    │
└───────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴───────────────┐
                    │   AGENTE ORQUESTRADOR         │  ← lê a skill + o ledger
                    │   (Antigravity CLI / Claude)  │     e conduz o loop
                    └──────────────┬───────────────┘
                                   │  (protocolo MCP)
                    ┌──────────────┴───────────────┐
                    │  MCP  "notebooklm"            │  pinado num commit auditado
                    │  • só grupos: notebooks,      │  • conta Google DEDICADA
                    │    sources, studio, chat, auth│  • cookie 0600, local só
                    │  • sharing/automation OFF     │  • fala só com google.com
                    └──────────────┬───────────────┘
                                   │  (dirige sua sessão real)
                    ┌──────────────┴───────────────┐
                    │   NOTEBOOKLM  (conta dedicada)│  ← onde VOCÊ estuda
                    │   áudio · quiz · study guide  │
                    └───────────────────────────────┘
```

---

## 2. O loop de 3 fases (o coração de tudo)

```
  FASE 1 — PREP  (agente faz, sozinho)
  ─────────────────────────────────────────────────────────────
  lê ledger da matéria → pega `retomar_em` + `pontos_fracos`
      │
      ▼  via MCP notebooklm:
  garante notebook  →  sobe a fonte  →  gera Áudio + Quiz + Study Guide
                                         FOCADOS no tópico e nas fraquezas
      │
      ▼
  te avisa: "tópico X, o 80/20 é Y, material pronto no NotebookLM"


  FASE 2 — STUDY  (VOCÊ faz)
  ─────────────────────────────────────────────────────────────
  NotebookLM: áudio no deslocamento · responde o quiz · tira dúvida
  (agente espera seu retorno)


  FASE 3 — PROGRESS  (agente faz, escrevendo no workspace)
  ─────────────────────────────────────────────────────────────
  mini-recall rigoroso: NO MÍNIMO 7 PERGUNTAS  (mesmo que já tenha feito o quiz)
      │
      ├─► atualiza LEDGER: status do tópico, retomar_em, pontos_fracos
      ├─► atualiza srs.db: rating 1-4 + FSRS → próxima data de revisão
      └─► cria cards novos (dos erros) + linha no Log de aprendizado
```

> **Regra fixa:** na Fase 3 o agente faz **no mínimo 7 perguntas rigorosas** (produção ativa, não reconhecimento), com rigor +20% — nome técnico + exemplo concreto + distinção entre conceitos parecidos.

> **Único elo manual:** o resultado do quiz nasce *dentro* do NotebookLM e o MCP não lê esse "mastery" de forma confiável. Então na Fase 3 **você reporta** o placar/o que travou — o agente faz o resto.

---

## 3. Responsabilidades — cada peça faz uma coisa

| Peça | Papel | Por que é ela |
|---|---|---|
| **Agente orquestrador** | Conduz o loop, lê/escreve arquivos | Agente com acesso ao workspace |
| **`SKILL.md`** | O "cérebro": persona, 80/20, rigor, as 3 fases | Instruções que o agente segue |
| **MCP `notebooklm`** | Ponte código→NotebookLM (criar/subir/gerar) | Único caminho sem API oficial |
| **NotebookLM** | Superfície de estudo (áudio/quiz/consumo) | O forte dele: consolidar a fonte |
| **`srs.db` (FSRS)** | Fonte da verdade do progresso + timing das revisões | Repetição espaçada de verdade |
| **`<materia>.md`** | Estado da matéria + 80/20 + log + pontos fracos | Memória que sobrevive entre sessões |

---

## 4. Na prática — exemplo genérico

Digamos que você está estudando o tópico **T** da matéria **M**, e o ledger registra que você confunde os conceitos **A** e **B**.

1. **PREP:** o agente lê isso → via MCP gera um **Áudio Overview do tópico T** + um **Quiz** que insiste na distinção **A vs B**.
2. **STUDY:** você ouve o áudio no trânsito e responde o quiz no NotebookLM.
3. **PROGRESS:** você volta; o agente te faz **no mínimo 7 perguntas rigorosas** (ex.: "diferença técnica entre A e B, com exemplo concreto"), avalia, grava no `srs.db` a próxima revisão, e marca o tópico como `dominado` se o recall fechar.

---

## 5. Guardrails de segurança embutidos

- MCP **pinado** num commit auditado (código limpo) · roda de um clone local, não do PyPI "latest".
- **Conta Google dedicada** → se o cookie vazar, expõe só seus materiais de estudo.
- **Privilégio mínimo** (`.agents/mcp_config.json`): `sharing` e `automation` desligados → sem compartilhamento público acidental.
- Cookie **local, permissão `0600`**, e todo egress vai só pra `google.com`.

Resumo da auditoria do MCP (ver `COOKBOOK.md`): licença MIT · deps mainstream · **zero** `eval/exec/os.system/shell`/`pickle` · **zero** telemetria · rede só pro Google.

---

## 6. O que falta pra ligar

Configuração one-time do MCP (login no browser) — passo a passo na **Parte A** do [`COOKBOOK.md`](COOKBOOK.md).
