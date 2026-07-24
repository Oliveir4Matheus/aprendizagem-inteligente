#!/usr/bin/env bash
# Setup one-time do MCP do NotebookLM (auditado + pinado) para o Aprendizado Inteligente.
# Uso:  bash scripts/setup.sh
# Faz: garante uv -> clona+pina o MCP -> instala do clone -> login -> diagnostico.
set -euo pipefail

MCP_DIR="${MCP_DIR:-$HOME/workspace/notebooklm-mcp-audit}"
MCP_PIN="${MCP_PIN:-b2ab425}"
MCP_REPO="https://github.com/jacob-bd/notebooklm-mcp-cli.git"

echo "==> 1/5  Garantindo o uv (gerenciador de pacotes)"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"

echo "==> 2/5  Clonando + pinando o MCP no commit ${MCP_PIN}"
if [ ! -d "${MCP_DIR}/.git" ]; then
  git clone "${MCP_REPO}" "${MCP_DIR}"
fi
git -C "${MCP_DIR}" checkout "${MCP_PIN}"

echo "==> 3/5  Instalando do clone pinado (nao do PyPI 'latest')"
uv tool install --force "${MCP_DIR}"

echo "==> 4/5  Login no NotebookLM (abre o browser -> use a CONTA DEDICADA de estudo)"
nlm login

echo "==> 5/5  Diagnostico"
nlm doctor || true

cat <<'DONE'

OK. Setup do MCP concluido.
Proximos passos:
  1) Abra o agente (Antigravity CLI / Claude Code) NESTE diretorio.
  2) Ele le o AGENTS.md. Diga: "siga o COOKBOOK.md" (1a vez) ou "rode o loop de estudo".
Config do MCP: .agents/mcp_config.json (privilegio minimo).
NAO use 'nlm setup add' nem 'claude mcp add' -- eles ignoram esse privilegio minimo.
DONE
