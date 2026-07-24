# COOKBOOK — Setup e operação (executado pelo AGENTE)

Este runbook é feito para **o agente executar** via shell. Legenda: **[AGENTE]** = o orquestrador roda; **[HUMANO]** = ação do aluno.

> **O único passo humano do setup é `nlm login`** (abre o browser). Todo o resto — instalar, baixar o MCP, configurar, verificar — o agente faz sozinho seguindo os passos abaixo.

Contexto completo em [`ARQUITETURA.md`](ARQUITETURA.md).

---

## PARTE A — Setup do MCP (o AGENTE executa; 1x por máquina)

### A0. Pré-requisito humano
Uma **conta Google DEDICADA só para estudo** (não a principal). É o maior redutor de risco: se o cookie vazar, expõe só os notebooks de estudo.

### A1. [AGENTE] Garantir o `uv`
```bash
command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

### A2. [AGENTE] Baixar o MCP PARA DENTRO do workspace (clone se não existir) e pinar
```bash
MCP_DIR="vendor/notebooklm-mcp"        # dentro desta pasta de estudo
if [ ! -d "$MCP_DIR/.git" ]; then
  git clone https://github.com/jacob-bd/notebooklm-mcp-cli.git "$MCP_DIR"
fi
git -C "$MCP_DIR" checkout b2ab425      # commit auditado (pin)
```
> `vendor/` é ignorado pelo git (tem git próprio + é código de terceiro). Fica **dentro** do workspace por auto-contenção.

### A3. [AGENTE] Instalar a partir do clone pinado
```bash
uv tool install --force ./vendor/notebooklm-mcp   # expõe `nlm` e `notebooklm-mcp` no PATH
```

### A4. [AGENTE] Diagnóstico
```bash
nlm doctor        # mostra o estado da instalação e se falta login
```

### A5. [HUMANO — única ação manual do setup] Login no browser
Peça ao aluno para rodar (ele mesmo, no terminal dele):
```bash
nlm login          # abre o Chrome → logar com a CONTA DEDICADA de estudo
```
Aguarde ele confirmar. (Cookies ficam em `~/.notebooklm-mcp-cli/`, permissão `0600`, duram ~2–4 semanas.)
> O MCP usa o **profile ativo**; `nlm login` sem flag = profile `default`. Isolar: `nlm login --profile estudo` + `nlm login switch estudo`.

### A6. [AGENTE] Confirmar e travar o privilégio mínimo
```bash
nlm doctor         # deve passar agora
```
Confirme que `.agents/mcp_config.json` mantém os grupos perigosos desligados:
```json
"NOTEBOOKLM_DISABLED_GROUPS": "query_multi,organization,automation,notes,sharing,research"
```
> ⚠️ Use **este** `.agents/mcp_config.json` do workspace. **Não** rode `nlm setup add` nem `claude mcp add` — eles registram o server sem o bloco `env` de privilégio mínimo (reabririam sharing/automation).

### A7. Checklist de segurança
- [ ] Conta Google **dedicada** (não a principal)
- [ ] MCP **baixado em `vendor/`** e instalado do clone pinado, não do PyPI
- [ ] `sharing` e `automation` **desligados** no config
- [ ] Rodar o MCP **só durante o estudo**; revogar sessão em *myaccount.google.com → Segurança* de vez em quando

> **Atalho:** `bash scripts/setup.sh` executa A1–A4 de uma vez (não faz o login — esse é o passo humano A5).

---

## PARTE B — Começar uma matéria nova

1. [AGENTE] Copie o modelo de ledger: `cp progresso/_TEMPLATE.md progresso/<materia>.md`
2. [AGENTE] Preencha `materia`, `fontes`, `deck_anki`; registre a linha em `progresso/_index.md`.
3. [HUMANO] Ponha a fonte (PDF/slides/apostila) em `documentos/`.
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

### C3. [HUMANO] FASE 2 — STUDY
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
| Não sei o que está errado | — | rodar `nlm doctor` (diagnóstico embutido) |
| `nlm` não encontrado | `~/.local/bin` fora do PATH | `export PATH="$HOME/.local/bin:$PATH"` ou novo terminal |
| Tools do NotebookLM não aparecem | auth expirada (2–4 semanas) | `nlm login` de novo |
| MCP não conecta no agente | config errado | conferir `command: "notebooklm-mcp"` em `.agents/mcp_config.json`; recarregar |
| Quero reinstalar o MCP | — | reexecutar A2–A3 (o clone em `vendor/` é reaproveitado) |
| "Compartilhar" não funciona | é de propósito (least privilege) | manter desligado |
