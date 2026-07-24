# COOKBOOK — Configurar e operar o setup de estudo (Orquestrador + NotebookLM MCP)

Runbook passo a passo. Legenda: **[VOCÊ]** = ação humana; **[AGENTE]** = o orquestrador faz.
Contexto completo em [`ARQUITETURA.md`](ARQUITETURA.md).

---

## PARTE A — Setup one-time do MCP (só na primeira vez, por máquina)

### A0. Pré-requisitos
- Este workspace (`aprendizado-inteligente`).
- Uma **conta Google DEDICADA só para estudo** (não a principal). É o maior redutor de risco: se o cookie vazar, expõe só os notebooks de estudo.

### A1. [VOCÊ] Obter e pinar o código do MCP (auditado)
```bash
# clonar o MCP do NotebookLM (não oficial, MIT) e travar no commit auditado
git clone https://github.com/jacob-bd/notebooklm-mcp-cli.git ~/workspace/notebooklm-mcp-audit
cd ~/workspace/notebooklm-mcp-audit && git checkout b2ab425
```
> Antes de usar de verdade, revise o código (é seu direito e o sentido de "pinar"). Resumo da auditoria feita aqui: MIT · deps mainstream (`httpx`, `fastmcp`, `pydantic`...) · **zero** `eval/exec/os.system/shell`/`pickle` · **zero** telemetria · rede só pro Google · cookies locais com permissão `0600`.

### A2. [VOCÊ] Instalar a partir do código pinado
```bash
# uv (gerenciador que o projeto usa), se ainda não tiver:
curl -LsSf https://astral.sh/uv/install.sh | sh
# instalar do CLONE LOCAL (não do PyPI "latest"):
uv tool install ~/workspace/notebooklm-mcp-audit
```
> Isso expõe os comandos `nlm` e `notebooklm-mcp` em `~/.local/bin`. Se `nlm` não for encontrado, adicione `~/.local/bin` ao PATH ou abra um novo terminal.
> **Atalho:** `bash scripts/setup.sh` faz A1–A3 de uma vez.

### A3. [VOCÊ] Autenticar com a conta dedicada
```bash
nlm login          # abre o Chrome → logue com a CONTA DEDICADA de estudo
nlm doctor         # diagnóstico: confirma login + instalação
```
> O MCP usa o **profile ativo**. `nlm login` sem flag = profile `default` (o server usa esse). Para isolar num profile próprio: `nlm login --profile estudo` e depois `nlm login switch estudo`.
> Cookies ficam locais em `~/.notebooklm-mcp-cli/` (permissão `0600`). Duram ~2–4 semanas; quando expirar, rode `nlm login` de novo.

### A4. [AGENTE] Conferir o privilégio mínimo
Confirme que `.agents/mcp_config.json` mantém os grupos perigosos desligados:
```json
"NOTEBOOKLM_DISABLED_GROUPS": "query_multi,organization,automation,notes,sharing,research"
```
Não reative `sharing` nem `automation`. Se algo estiver diferente, avise antes de mexer.

> ⚠️ Use **este** `.agents/mcp_config.json` do workspace. **Não** rode `nlm setup add` nem `claude mcp add` — eles registram o server sem o bloco `env` de privilégio mínimo (reabririam sharing/automation).

### A5. [VOCÊ] Verificar no orquestrador
O agente lê `.agents/mcp_config.json` do workspace. No Antigravity CLI use `/mcp` e confirme o server **`notebooklm` verde**; no Claude Code, `/mcp` também lista. Se vermelho: cheque o entrypoint (`notebooklm-mcp` no PATH), refaça o `auth`, reveja `command`/`args`.

### A6. Checklist de segurança
- [ ] Conta Google **dedicada** (não a principal)
- [ ] Instalado do **clone local** pinado, não do PyPI
- [ ] `sharing` e `automation` **desligados** no config
- [ ] Rodar o MCP **só durante o estudo**; revogar sessão em *myaccount.google.com → Segurança* de vez em quando

---

## PARTE B — Começar uma matéria nova

1. [VOCÊ ou AGENTE] Copie o modelo de ledger:
   ```bash
   cp progresso/_TEMPLATE.md progresso/<materia>.md
   ```
2. [AGENTE] Preencha `materia`, `fontes`, `deck_anki` no frontmatter; registre a linha em `progresso/_index.md`.
3. [VOCÊ] Ponha a fonte (PDF/slides/apostila) em `documentos/`.
4. [AGENTE] Rode o loop (Parte C) a partir do tópico 1.

---

## PARTE C — Operar o loop (toda sessão)

Siga o cérebro em [`.agents/skills/professor/SKILL.md`](.agents/skills/professor/SKILL.md). Resumo executável:

### C1. [AGENTE] Retomar
Leia `progresso/<materia>.md` → `retomar_em` + `pontos_fracos`. Se `proxima_revisao` vencida → rode a revisão FSRS (`REVISAO_IA.md`) primeiro.

### C2. [AGENTE] FASE 1 — PREP (via MCP)
1. `notebook_list` / `notebook_get` → achar o notebook da matéria; se não existir, `notebook_create`.
2. `source_add` → garantir que a fonte em `documentos/` está no notebook.
3. `studio_create` → gerar **Audio Overview**, **Study Guide** e **Quiz** focados no tópico atual **e nos `pontos_fracos`**. Acompanhe com `studio_status`.
4. Avise o aluno: tópico, o 80/20, e o que ficou pronto.

> Nomes/campos exatos das tools: inspecione via `/mcp` (o server só expõe os grupos habilitados).

### C3. [VOCÊ] FASE 2 — STUDY
Estude no NotebookLM: áudio no deslocamento, responda o quiz, tire dúvidas com citação.

### C4. [AGENTE] FASE 3 — PROGRESS
1. **Mini-teste de recall: NO MÍNIMO 7 perguntas rigorosas** (produção ativa, não reconhecimento) — mesmo que o quiz já tenha sido feito. Rigor +20%: nome técnico + exemplo + distinção entre conceitos parecidos.
2. Atualize o **ledger** (com `Edit`): `topicos[].status`, `passo_loop`, `retomar_em`; **todo erro vira item em `pontos_fracos`**.
3. Atualize o **FSRS** em `progresso/srs.db` (`REVISAO_IA.md`): rating 1–4, novo intervalo, grave em `cards` + `review_log`; crie cards novos dos erros (sem duplicar pelo `front`).
4. Adicione linha no `## Log de aprendizado` + atualize `atualizado:` e `_index.md`.

---

## PARTE D — Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `/mcp` mostra "notebooklm" vermelho | binário fora do PATH ou config errado | conferir `command: "notebooklm-mcp"`, reinstalar, recarregar |
| Tools do NotebookLM não aparecem | auth expirada (2–4 semanas) | rodar `nlm login` de novo |
| Não sei o que está errado | — | rodar `nlm doctor` (diagnóstico embutido) |
| Falta uma tool que preciso | grupo desabilitado no config | avaliar se vale reabilitar — **nunca** reative `sharing`/`automation` sem discutir |
| "Compartilhar" não funciona | é de propósito (least privilege) | manter desligado |
