#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup.py — parte de MÁQUINA do setup (passos 1–8 de 20).

    Linux / macOS :  python3 scripts/setup.py
    Windows       :  py scripts\\setup.py

Os passos 9–20 são a entrevista de onboarding e quem conduz é o agente, na conversa
(ver COOKBOOK.md Parte 0). A numeração é contínua de propósito: você enxerga um único
setup do começo ao fim.

Opções:
    --skip-login     não dispara o `nlm login` (útil em CI ou reexecução)
    --skip-audit     não checa atualização do MCP nesta rodada
    --pin <commit>   força um commit específico do MCP
    --dry-run        só o que não toca a rede nem instala nada globalmente
                     (checa ambiente, cria estudo/, confere privilégio mínimo)

Roda igual em Windows, Linux e macOS. Sem dependências externas.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mnemo  # noqa: E402

WS = Path(__file__).resolve().parent.parent
TEMPLATES = WS / "templates"
ESTUDO = WS / "estudo"
PIN_FILE = WS / ".agents" / "mcp_pin.json"
MCP_CONFIG = WS / ".agents" / "mcp_config.json"
MCP_DIR = Path(os.environ.get("MCP_DIR", WS / "vendor" / "notebooklm-mcp"))

IS_WINDOWS = os.name == "nt"
GRUPOS_PERIGOSOS = {"sharing", "automation"}


# ── helpers ────────────────────────────────────────────────────────────────


def run(cmd: list[str] | str, *, shell: bool = False, check: bool = True,
        capture: bool = True, timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, shell=shell, check=False, timeout=timeout,
        capture_output=capture, text=True, encoding="utf-8", errors="replace",
    )


def tem(exe: str) -> str | None:
    return shutil.which(exe)


def acrescentar_ao_path(*dirs: Path) -> None:
    """Deixa o PATH desta sessão enxergar o que o instalador acabou de criar."""
    atual = os.environ.get("PATH", "").split(os.pathsep)
    for d in dirs:
        s = str(d)
        if d.is_dir() and s not in atual:
            atual.insert(0, s)
    os.environ["PATH"] = os.pathsep.join(atual)


def bin_dirs() -> list[Path]:
    home = Path.home()
    if IS_WINDOWS:
        return [home / ".local" / "bin",
                home / "AppData" / "Roaming" / "uv" / "tools",
                home / ".cargo" / "bin"]
    return [home / ".local" / "bin", home / ".cargo" / "bin"]


# ── passos ─────────────────────────────────────────────────────────────────


def passo1_ambiente() -> None:
    so = f"{platform.system()} {platform.release()}"
    mnemo.bar(1, "Detectando o sistema", f"{so} · Python {platform.python_version()}")
    if sys.version_info < (3, 9):
        mnemo.fail(f"Python 3.9+ é necessário (você tem {platform.python_version()}).")
        raise SystemExit(1)
    if not tem("git"):
        mnemo.fail("git não encontrado. Instale o git e rode de novo.")
        if IS_WINDOWS:
            print("         https://git-scm.com/download/win")
        raise SystemExit(1)
    mnemo.ok("git e Python OK")


def passo2_uv(dry: bool = False) -> None:
    mnemo.bar(2, "Garantindo o uv")
    acrescentar_ao_path(*bin_dirs())
    if tem("uv"):
        mnemo.ok("uv já instalado")
        return
    if dry:
        mnemo.warn("uv ausente — instalação pulada por --dry-run")
        return
    if IS_WINDOWS:
        cmd = ('powershell -ExecutionPolicy ByPass -NoProfile -c '
               '"irm https://astral.sh/uv/install.ps1 | iex"')
    else:
        cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"
    mnemo.bar(2, "Garantindo o uv", cmd)
    r = run(cmd, shell=True)
    acrescentar_ao_path(*bin_dirs())
    if not tem("uv"):
        mnemo.fail("não consegui instalar o uv automaticamente.")
        print((r.stderr or r.stdout or "").strip()[:600])
        print("         Instale manualmente: https://docs.astral.sh/uv/getting-started/installation/")
        raise SystemExit(1)
    mnemo.ok("uv instalado")


def passo3_clonar(cfg: dict) -> None:
    mnemo.bar(3, "Baixando o MCP para vendor/", str(MCP_DIR.relative_to(WS)))
    if (MCP_DIR / ".git").is_dir():
        mnemo.ok("clone já existe — reaproveitando")
        return
    MCP_DIR.parent.mkdir(parents=True, exist_ok=True)
    r = run(["git", "clone", "--quiet", cfg["repo"], str(MCP_DIR)])
    if r.returncode != 0 or not (MCP_DIR / ".git").is_dir():
        mnemo.fail("falha ao clonar o MCP.")
        print((r.stderr or "").strip()[:600])
        raise SystemExit(1)
    mnemo.ok(f"clonado de {cfg['repo']}")


def passo4_auditar(cfg: dict, pin_forcado: str | None, pular: bool) -> None:
    mnemo.bar(4, "Checando atualização do MCP")
    if pin_forcado:
        mnemo.warn(f"pin forçado por --pin: {pin_forcado} (auditoria pulada)")
        return
    if pular:
        mnemo.warn("auditoria pulada por --skip-audit")
        return
    r = run([sys.executable, str(WS / "scripts" / "mcp_update.py"), "--quiet"], capture=True)
    saida = (r.stdout or "") + (r.stderr or "")
    if r.returncode == 0 and "Já está na versão mais recente" in saida:
        mnemo.ok("MCP já está na versão auditada mais recente")
        return
    print(saida.rstrip())
    if r.returncode == 0:
        mnemo.ok("há versão nova e a auditoria passou limpa")
    else:
        mnemo.warn("há versão nova COM pontos de atenção — leia acima")
    print(f"         {mnemo.dim('O setup segue no pin auditado. Para atualizar: python3 scripts/mcp_update.py --apply')}")


def passo5_instalar(cfg: dict, pin_forcado: str | None) -> None:
    pin = pin_forcado or cfg["pin"]
    mnemo.bar(5, "Instalando o MCP pinado", f"commit {pin}")
    r = run(["git", "-C", str(MCP_DIR), "checkout", "--quiet", pin])
    if r.returncode != 0:
        run(["git", "-C", str(MCP_DIR), "fetch", "--quiet", "origin", "--tags"])
        r = run(["git", "-C", str(MCP_DIR), "checkout", "--quiet", pin])
        if r.returncode != 0:
            mnemo.fail(f"não consegui pinar o commit {pin}.")
            print((r.stderr or "").strip()[:400])
            raise SystemExit(1)
    r = run(["uv", "tool", "install", "--force", str(MCP_DIR)])
    if r.returncode != 0:
        mnemo.fail("falha ao instalar o MCP com o uv.")
        print((r.stderr or r.stdout or "").strip()[:600])
        raise SystemExit(1)
    acrescentar_ao_path(*bin_dirs())
    mnemo.ok("`nlm` e `notebooklm-mcp` instalados a partir do clone pinado")


def passo6_estrutura() -> None:
    mnemo.bar(6, "Preparando a pasta estudo/")
    (ESTUDO / "progresso").mkdir(parents=True, exist_ok=True)
    (ESTUDO / "documentos").mkdir(parents=True, exist_ok=True)

    copias = [
        (TEMPLATES / "PERFIL.md", ESTUDO / "PERFIL.md"),
        (TEMPLATES / "_index.md", ESTUDO / "progresso" / "_index.md"),
        (TEMPLATES / "documentos-README.md", ESTUDO / "documentos" / "README.md"),
    ]
    criados = []
    for origem, destino in copias:
        if destino.exists():
            continue
        if not origem.exists():
            mnemo.warn(f"template ausente: {origem.name}")
            continue
        shutil.copy2(origem, destino)
        criados.append(destino.relative_to(WS).as_posix())

    db = ESTUDO / "progresso" / "srs.db"
    if not db.exists():
        schema = (TEMPLATES / "srs_schema.sql").read_text(encoding="utf-8")
        con = sqlite3.connect(db)
        try:
            con.executescript(schema)
            con.commit()
        finally:
            con.close()
        criados.append(db.relative_to(WS).as_posix())

    if criados:
        mnemo.ok("criado: " + ", ".join(criados))
    else:
        mnemo.ok("estrutura já existia — nada foi sobrescrito")

    pendentes = campos_pendentes(ESTUDO / "PERFIL.md")
    if pendentes:
        mnemo.warn(f"PERFIL.md tem {len(pendentes)} campo(s) por preencher — a entrevista "
                   f"(passos 9–20) resolve: {', '.join(pendentes[:3])}"
                   + (" …" if len(pendentes) > 3 else ""))


def campos_pendentes(perfil: Path) -> list[str]:
    """Campos do PERFIL cujo VALOR ainda é um placeholder `_(...)_`.

    Só olha a posição de valor (`- **Campo:** _(...)_`) — parênteses explicativos no
    meio de uma frase não contam.
    """
    if not perfil.exists():
        return ["arquivo inexistente"]
    padrao = re.compile(r"^\s*-\s*\*\*(?P<campo>[^*]+?):?\*\*\s*_\(", re.MULTILINE)
    return [m.group("campo").strip() for m in padrao.finditer(perfil.read_text(encoding="utf-8"))]


def passo7_privilegio() -> None:
    mnemo.bar(7, "Conferindo o privilégio mínimo")
    if not MCP_CONFIG.exists():
        mnemo.fail(f"{MCP_CONFIG.relative_to(WS)} não encontrado.")
        raise SystemExit(1)
    cfg = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    env = cfg.get("mcpServers", {}).get("notebooklm", {}).get("env", {})
    desligados = {g.strip() for g in env.get("NOTEBOOKLM_DISABLED_GROUPS", "").split(",") if g.strip()}
    faltando = GRUPOS_PERIGOSOS - desligados
    if faltando:
        mnemo.fail(f"grupos perigosos NÃO desligados: {', '.join(sorted(faltando))}")
        print(f"         {mnemo.dim('corrija NOTEBOOKLM_DISABLED_GROUPS em .agents/mcp_config.json')}")
        raise SystemExit(1)
    mnemo.ok(f"desligados: {', '.join(sorted(desligados))}")


def autenticado() -> bool | None:
    """True/False, ou None quando o diagnóstico não é conclusivo."""
    if not tem("nlm"):
        return None
    r = run(["nlm", "doctor"], timeout=60)
    txt = ((r.stdout or "") + (r.stderr or "")).lower()
    negativos = ("not authenticated", "no credentials", "not_configured", "não autenticado",
                 "run `nlm login`", "run 'nlm login'", "nlm login", "expired", "stale")
    positivos = ("authenticated", "configured", "logged in", "auth ok", "credentials found")
    if any(n in txt for n in negativos):
        return False
    if r.returncode == 0 and any(p in txt for p in positivos):
        return True
    return True if r.returncode == 0 else None


def passo8_login(pular: bool) -> None:
    mnemo.bar(8, "Autenticando no NotebookLM")
    if not tem("nlm"):
        mnemo.fail("`nlm` não está no PATH.")
        alvo = "%USERPROFILE%\\.local\\bin" if IS_WINDOWS else '$HOME/.local/bin'
        print(f"         {mnemo.dim(f'adicione {alvo} ao PATH e rode de novo')}")
        raise SystemExit(1)

    estado = autenticado()
    if estado is True:
        mnemo.ok("sessão do Google já ativa")
        endurecer_permissao_cookie()
        return
    if pular:
        mnemo.warn("login pulado por --skip-login. Rode `nlm login` quando quiser.")
        return

    mnemo.say(
        "Vou abrir o navegador para você entrar no Google.\n"
        "  Use a CONTA DEDICADA de estudo — nunca a sua conta principal.\n"
        "  Terminou de logar no navegador? O setup continua sozinho."
    )
    try:
        # stdio herdado de propósito: o `nlm` precisa falar com você direto.
        subprocess.run(["nlm", "login"], check=False, timeout=600)
    except subprocess.TimeoutExpired:
        mnemo.warn("o login passou de 10 minutos e foi interrompido.")
    except KeyboardInterrupt:
        mnemo.warn("login cancelado.")

    estado = autenticado()
    if estado is True:
        mnemo.ok("autenticado")
        endurecer_permissao_cookie()
    elif estado is False:
        mnemo.fail("ainda sem sessão válida. Rode `nlm login` manualmente e repita o setup.")
        raise SystemExit(1)
    else:
        mnemo.warn("não consegui confirmar o login. Cheque com: nlm doctor")


def endurecer_permissao_cookie() -> None:
    """A sessão do Google fica em ~/.notebooklm-mcp-cli/. Só o dono deve ler."""
    d = Path.home() / ".notebooklm-mcp-cli"
    if not d.is_dir():
        return
    if IS_WINDOWS:
        mnemo.warn("no Windows a proteção do cookie é a ACL do seu perfil de usuário — "
                   "não deixe a pasta do usuário compartilhada")
        return
    try:
        os.chmod(d, 0o700)
        for p in d.rglob("*"):
            if p.is_file():
                os.chmod(p, 0o600)
        mnemo.ok("permissões da sessão restritas (0600)")
    except OSError as e:
        mnemo.warn(f"não consegui ajustar permissões: {e}")


# ── fluxo ──────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description="Setup do workspace de Aprendizagem Inteligente.")
    ap.add_argument("--skip-login", action="store_true")
    ap.add_argument("--skip-audit", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="não usa rede nem instala nada globalmente")
    ap.add_argument("--pin")
    args = ap.parse_args()

    mnemo.hello("vamos configurar seu ambiente de estudo")
    if args.dry_run:
        mnemo.warn("--dry-run: nada de rede, clone ou instalação global nesta execução")

    if not PIN_FILE.exists():
        mnemo.fail(f"não achei {PIN_FILE.relative_to(WS)} — o repo está incompleto.")
        return 1
    cfg = json.loads(PIN_FILE.read_text(encoding="utf-8"))

    passo1_ambiente()
    passo2_uv(args.dry_run)
    if args.dry_run:
        mnemo.bar(3, "Baixando o MCP para vendor/", "pulado (--dry-run)")
        mnemo.bar(4, "Checando atualização do MCP", "pulado (--dry-run)")
        mnemo.bar(5, "Instalando o MCP pinado", "pulado (--dry-run)")
    else:
        passo3_clonar(cfg)
        passo4_auditar(cfg, args.pin, args.skip_audit)
        passo5_instalar(cfg, args.pin)
    passo6_estrutura()
    passo7_privilegio()
    if args.dry_run:
        mnemo.bar(8, "Autenticando no NotebookLM", "pulado (--dry-run)")
    else:
        passo8_login(args.skip_login)

    print()
    mnemo.rule(" CHECKLIST DE SEGURANÇA ")
    for item in (
        "Conta Google DEDICADA (não a principal)",
        f"MCP instalado do clone pinado em vendor/ ({cfg['pin']}), não do PyPI 'latest'",
        "sharing e automation desligados no .agents/mcp_config.json",
        "Rodar o MCP só durante o estudo; revogar a sessão de tempos em tempos "
        "em myaccount.google.com → Segurança",
        "Atualizar o MCP só via scripts/mcp_update.py (audita antes de aplicar)",
    ):
        print(f"    [ ] {item}")

    mnemo.handoff()
    print(f"    {mnemo.dim('Auditoria do MCP a qualquer momento:')} python3 scripts/mcp_update.py")
    print(f"    {mnemo.dim('Data desta execução:')} {date.today()}")
    print()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print()
        raise SystemExit(130)
