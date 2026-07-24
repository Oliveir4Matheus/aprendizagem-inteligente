#!/usr/bin/env bash
# Parte de MÁQUINA do setup do MCP do NotebookLM (auditado + pinado), DENTRO do workspace.
# O AGENTE pode rodar isto. NÃO faz login (esse é o único passo humano).
# Uso:  bash scripts/setup.sh
set -euo pipefail

WS="$(cd "$(dirname "$0")/.." && pwd)"
MCP_DIR="${MCP_DIR:-$WS/vendor/notebooklm-mcp}"
MCP_PIN="${MCP_PIN:-b2ab425}"
MCP_REPO="https://github.com/jacob-bd/notebooklm-mcp-cli.git"

echo "==> 1/4  Garantindo o uv"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"

echo "==> 2/4  Baixando o MCP para dentro do workspace (${MCP_DIR}) e pinando em ${MCP_PIN}"
if [ ! -d "${MCP_DIR}/.git" ]; then
  git clone "${MCP_REPO}" "${MCP_DIR}"
fi
git -C "${MCP_DIR}" checkout "${MCP_PIN}"

echo "==> 3/4  Instalando do clone pinado (nao do PyPI 'latest')"
uv tool install --force "${MCP_DIR}"

echo "==> 4/4  Diagnostico (nlm doctor)"
nlm doctor || true

cat <<'DONE'

OK (parte de maquina concluida).
>> UNICO PASSO HUMANO: se o diagnostico acima indicar falta de login, rode:
       nlm login
   (abre o browser; use a CONTA DEDICADA de estudo)
>> Depois, abra o agente NESTE diretorio e diga: "rode o loop de estudo".
>> Config do MCP: .agents/mcp_config.json (privilegio minimo).
   NAO use 'nlm setup add' nem 'claude mcp add' -- eles ignoram esse privilegio.
DONE
