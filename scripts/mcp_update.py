#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mcp_update.py — checa se o MCP do NotebookLM tem versão nova e, ANTES de aplicar,
audita o que mudou. O pin só sobe com aprovação explícita.

    python3 scripts/mcp_update.py              # checa e audita, não altera nada
    python3 scripts/mcp_update.py --apply      # aplica, mas só se a auditoria passar
    python3 scripts/mcp_update.py --apply --force-approve
                                               # aplica mesmo com achados (o aluno assume o risco)
    python3 scripts/mcp_update.py --target <commit>   # audita/aplica um commit específico

Roda igual em Windows, Linux e macOS. Sem dependências externas.

Por que isso existe: o MCP é código de terceiro que dirige uma sessão real do Google.
Atualizar às cegas é o caminho mais curto para rodar código malicioso com a sua sessão
autenticada na mão. Aqui a atualização é sempre: buscar → ler o diff → decidir.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mnemo  # noqa: E402

WS = Path(__file__).resolve().parent.parent
PIN_FILE = WS / ".agents" / "mcp_pin.json"
MCP_DIR = Path(os.environ.get("MCP_DIR", WS / "vendor" / "notebooklm-mcp"))

# ── Padrões de auditoria ───────────────────────────────────────────────────
# Cada regra: (severidade, rótulo, regex, por que importa)
ALTA = "ALTA"
MEDIA = "MÉDIA"
INFO = "INFO"

REGRAS = [
    (ALTA, "execução dinâmica de código",
     r"\b(eval|exec)\s*\(",
     "roda string como código — é como um payload chega sem aparecer no diff"),
    (ALTA, "shell do sistema",
     r"\b(os\.system|os\.popen|commands\.getoutput)\s*\(",
     "executa comando arbitrário do sistema operacional"),
    (ALTA, "subprocess com shell=True",
     r"shell\s*=\s*True",
     "injeção de comando fica trivial"),
    (ALTA, "desserialização insegura",
     r"\b(pickle|marshal|dill)\.(loads?|Unpickler)",
     "desserializar dado não confiável executa código"),
    (ALTA, "import dinâmico",
     r"\b__import__\s*\(|importlib\.import_module\s*\(",
     "carrega módulo decidido em tempo de execução"),
    (ALTA, "compilação em runtime",
     r"\bcompile\s*\(.*?,\s*['\"]<?\w*>?['\"]\s*,\s*['\"]exec['\"]",
     "compila e roda código gerado na hora"),
    (MEDIA, "ofuscação por base64",
     r"base64\.(b64decode|b85decode|urlsafe_b64decode)\s*\(",
     "usado para esconder string/payload do diff"),
    (MEDIA, "acesso a memória via ctypes",
     r"\bimport\s+ctypes|\bctypes\.(CDLL|windll|cdll)",
     "sai do sandbox do Python"),
    (MEDIA, "leitura de credenciais fora do escopo",
     r"(\.ssh/|\.aws/|id_rsa|\.netrc|keychain|Credentials?\.sqlite|Login\s?Data)",
     "o MCP só precisa da sessão do NotebookLM"),
    (MEDIA, "variáveis de ambiente varridas",
     r"os\.environ(?:\.copy\(\)|\s*\.items\(\)|\s*\)\s*$)",
     "exfiltração de segredos costuma começar aqui"),
    (MEDIA, "escrita fora do diretório do app",
     r"(crontab|/etc/|LaunchAgents|Startup|HKEY_|reg\s+add)",
     "tentativa de persistência na máquina"),
    (INFO, "novo endpoint de rede",
     r"https?://(?!(?:[\w.-]*\.)?(?:google\.com|googleusercontent\.com|gstatic\.com|googleapis\.com|github\.com|pypi\.org|python\.org|astral\.sh)\b)[\w.-]+",
     "o MCP deveria falar só com o Google"),
]

ARQUIVOS_SENSIVEIS = re.compile(
    r"(pyproject\.toml|requirements[\w.-]*\.txt|setup\.py|setup\.cfg|LICEN[CS]E|"
    r"\.github/workflows/|Makefile|Dockerfile|\.pre-commit-config\.yaml)",
    re.IGNORECASE,
)


# ── Utilidades ─────────────────────────────────────────────────────────────


def git(*args: str, check: bool = True) -> str:
    r = subprocess.run(
        ["git", "-C", str(MCP_DIR), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} falhou:\n{r.stderr.strip()}")
    return r.stdout


def carregar_pin() -> dict:
    if not PIN_FILE.exists():
        raise SystemExit(f"não achei {PIN_FILE} — rode o setup primeiro.")
    return json.loads(PIN_FILE.read_text(encoding="utf-8"))


def salvar_pin(dados: dict) -> None:
    PIN_FILE.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def branch_padrao() -> str:
    """Descobre o branch principal do remoto sem assumir 'main' nem 'master'."""
    try:
        saida = git("remote", "show", "origin")
        m = re.search(r"HEAD branch:\s*(\S+)", saida)
        if m:
            return m.group(1)
    except RuntimeError:
        pass
    for cand in ("main", "master"):
        if git("rev-parse", "--verify", f"origin/{cand}", check=False).strip():
            return cand
    return "main"


# ── Auditoria ──────────────────────────────────────────────────────────────


def auditar(base: str, alvo: str) -> tuple[list[dict], dict]:
    """Analisa SÓ as linhas adicionadas entre base e alvo."""
    diff = git("diff", "--unified=0", f"{base}..{alvo}")
    achados: list[dict] = []
    arquivo_atual = "?"
    linhas_add = 0

    for linha in diff.splitlines():
        if linha.startswith("+++ b/"):
            arquivo_atual = linha[6:]
            continue
        if not linha.startswith("+") or linha.startswith("+++"):
            continue
        conteudo = linha[1:]
        linhas_add += 1
        # comentários e docstrings raramente são o vetor, mas não vamos ignorar cegamente
        for sev, rotulo, padrao, porque in REGRAS:
            if re.search(padrao, conteudo):
                achados.append({
                    "severidade": sev,
                    "regra": rotulo,
                    "arquivo": arquivo_atual,
                    "trecho": conteudo.strip()[:160],
                    "porque": porque,
                })

    nomes = [n for n in git("diff", "--name-only", f"{base}..{alvo}").splitlines() if n]
    resumo = {
        "arquivos_alterados": len(nomes),
        "linhas_adicionadas": linhas_add,
        "commits": len([c for c in git("log", "--oneline", f"{base}..{alvo}").splitlines() if c]),
        "arquivos_sensiveis": [n for n in nomes if ARQUIVOS_SENSIVEIS.search(n)],
    }
    return achados, resumo


def diff_dependencias(base: str, alvo: str) -> list[str]:
    """Dependências que apareceram do nada — o vetor de supply chain mais comum."""
    novas: list[str] = []
    for arq in ("pyproject.toml", "requirements.txt"):
        try:
            antes = git("show", f"{base}:{arq}", check=False)
            depois = git("show", f"{alvo}:{arq}", check=False)
        except RuntimeError:
            continue
        if not depois:
            continue
        pat = re.compile(r"^\s*[\"']?([A-Za-z0-9._-]+)\s*(?:[><=~!\[]|[\"']?\s*[,\]]|$)")
        def pacotes(txt: str) -> set[str]:
            return {
                m.group(1).lower()
                for ln in txt.splitlines()
                if (m := pat.match(ln)) and not ln.strip().startswith("#")
            }
        for p in sorted(pacotes(depois) - pacotes(antes)):
            novas.append(f"{arq}: {p}")
    return novas


# ── Relatório ──────────────────────────────────────────────────────────────


def relatar(base: str, alvo: str, achados: list[dict], resumo: dict, deps: list[str]) -> int:
    mnemo.rule(" AUDITORIA DE SEGURANÇA ")
    print()
    print(f"  {mnemo.bold('Pin atual')}   {base}")
    print(f"  {mnemo.bold('Candidato')}   {alvo}")
    print(f"  {mnemo.bold('Mudança')}     {resumo['commits']} commits · "
          f"{resumo['arquivos_alterados']} arquivos · +{resumo['linhas_adicionadas']} linhas")
    print()

    if resumo["arquivos_sensiveis"]:
        print(f"  {mnemo.yellow('Arquivos sensíveis tocados:')}")
        for n in resumo["arquivos_sensiveis"]:
            print(f"    · {n}")
        print()

    if deps:
        print(f"  {mnemo.yellow('Dependências novas:')}")
        for d in deps:
            print(f"    · {d}   {mnemo.dim('(confira no PyPI antes de aceitar)')}")
        print()

    altas = [a for a in achados if a["severidade"] == ALTA]
    medias = [a for a in achados if a["severidade"] == MEDIA]
    infos = [a for a in achados if a["severidade"] == INFO]

    if not achados:
        print(f"  {mnemo.green('Nenhum padrão suspeito nas linhas adicionadas.')}")
    else:
        for grupo, cor, titulo in ((altas, mnemo.red, "ALTA"), (medias, mnemo.yellow, "MÉDIA"), (infos, mnemo.dim, "INFO")):
            if not grupo:
                continue
            print(f"  {cor(f'{titulo} — {len(grupo)} achado(s)')}")
            for a in grupo:
                print(f"    · [{a['regra']}] {a['arquivo']}")
                print(f"      {mnemo.dim(a['trecho'])}")
                print(f"      {mnemo.dim('por quê: ' + a['porque'])}")
            print()

    print(f"  {mnemo.dim('Diff completo:')} git -C {MCP_DIR} diff {base}..{alvo}")
    print()
    mnemo.rule()

    if altas:
        mnemo.fail(f"BLOQUEADO — {len(altas)} achado(s) de severidade ALTA. Leia um a um antes de qualquer coisa.")
        return 2
    if medias or deps:
        mnemo.warn(f"REVISAR — {len(medias)} achado(s) MÉDIA e {len(deps)} dependência(s) nova(s). "
                   "Nada bloqueia, mas confira antes de aprovar.")
        return 1
    if infos or resumo["arquivos_sensiveis"]:
        mnemo.ok(f"SEM BLOQUEIOS — nenhum padrão de risco. Restam {len(infos)} ponto(s) informativo(s)"
                 + (f" e {len(resumo['arquivos_sensiveis'])} arquivo(s) sensível(is) tocado(s)"
                    if resumo["arquivos_sensiveis"] else "") + ", vale a olhada.")
        return 0
    mnemo.ok("LIMPA — nenhum achado.")
    return 0


# ── Fluxo ──────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description="Checa e audita atualizações do MCP do NotebookLM.")
    ap.add_argument("--apply", action="store_true", help="sobe o pin se a auditoria permitir")
    ap.add_argument("--force-approve", action="store_true",
                    help="aplica mesmo com achados — o aluno assume o risco explicitamente")
    ap.add_argument("--target", help="commit/tag específico a auditar (padrão: HEAD do remoto)")
    ap.add_argument("--quiet", action="store_true", help="só o essencial")
    args = ap.parse_args()

    if not (MCP_DIR / ".git").is_dir():
        mnemo.fail(f"MCP não encontrado em {MCP_DIR}. Rode: python3 scripts/setup.py")
        return 3

    cfg = carregar_pin()
    base = cfg["pin"]

    if not args.quiet:
        mnemo.say("Buscando atualizações do MCP no repositório de origem…")
    git("fetch", "--quiet", "origin", "--tags")

    alvo = args.target or f"origin/{branch_padrao()}"
    sha_base = git("rev-parse", "--short", base).strip()
    sha_alvo = git("rev-parse", "--short", alvo).strip()

    if sha_base == sha_alvo:
        mnemo.ok(f"Já está na versão mais recente ({sha_base}). Nada a fazer.")
        return 0

    achados, resumo = auditar(base, alvo)
    deps = diff_dependencias(base, alvo)
    codigo = relatar(sha_base, sha_alvo, achados, resumo, deps)

    if not args.apply:
        print()
        mnemo.say(
            "Isto foi só a checagem. Para aplicar depois de ler:\n"
            "    python3 scripts/mcp_update.py --apply"
        )
        return codigo

    if codigo != 0 and not args.force_approve:
        mnemo.fail("Atualização NÃO aplicada — a auditoria levantou pontos.")
        print(f"  {mnemo.dim('Se você leu tudo e quer seguir mesmo assim:')}")
        print(f"  {mnemo.dim('python3 scripts/mcp_update.py --apply --force-approve')}")
        return codigo

    # ── aplica ──
    git("checkout", "--quiet", sha_alvo)
    cfg.setdefault("historico", []).append({
        "de": sha_base, "para": sha_alvo, "em": str(date.today()),
        "achados_altos": len([a for a in achados if a["severidade"] == ALTA]),
        "achados_medios": len([a for a in achados if a["severidade"] == MEDIA]),
        "aprovado_com_ressalva": bool(codigo != 0 and args.force_approve),
    })
    cfg["pin"] = sha_alvo
    cfg["auditado_em"] = str(date.today())
    cfg["auditado_por"] = "scripts/mcp_update.py" + (" (--force-approve)" if args.force_approve else "")
    salvar_pin(cfg)

    mnemo.ok(f"Pin atualizado: {sha_base} → {sha_alvo}")
    r = subprocess.run(["uv", "tool", "install", "--force", str(MCP_DIR)],
                       capture_output=True, text=True)
    if r.returncode == 0:
        mnemo.ok("MCP reinstalado a partir do clone pinado.")
    else:
        mnemo.warn("Pin atualizado, mas a reinstalação falhou. Rode: "
                   f"uv tool install --force {MCP_DIR}")
    mnemo.say("Reinicie o agente para recarregar o MCP.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print()
        raise SystemExit(130)
    except RuntimeError as e:
        mnemo.fail(str(e))
        raise SystemExit(3)
