#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mnemo.py — identidade visual e barra de progresso do tutor, iguais nos 3 sistemas.

Usado por scripts/setup.py e scripts/mcp_update.py. O agente também pode chamar
direto para desenhar a barra durante a entrevista de onboarding:

    python3 scripts/mnemo.py bar 9 "Como te chamo?"
    python3 scripts/mnemo.py hello
    python3 scripts/mnemo.py say "Etapa concluída."

Sem dependências externas — só a biblioteca padrão.
"""
from __future__ import annotations

import os
import sys

# ── O setup é uma numeração contínua: 1–8 fazem a máquina (setup.py) e
#    9–21 são as perguntas da entrevista, conduzidas pelo agente. ────────────
TOTAL_STEPS = 21
MACHINE_STEPS = 8

# ── Terminal: descobre o que dá para desenhar ───────────────────────────────


def _enable_windows_ansi() -> bool:
    """Liga o processamento de sequências ANSI no console do Windows 10+."""
    if os.name != "nt":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        # -11 = STD_OUTPUT_HANDLE, 0x4 = ENABLE_VIRTUAL_TERMINAL_PROCESSING
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x4))
    except Exception:
        return False


def _supports_unicode() -> bool:
    enc = (getattr(sys.stdout, "encoding", None) or "").lower()
    if not enc:
        return False
    try:
        "█░─╭╮╰╯".encode(enc)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


# No Windows o console costuma abrir em cp1252 e engasgar no box-drawing.
if os.name == "nt":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass

_COLOR = _enable_windows_ansi() and sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
_UNICODE = _supports_unicode()

FULL, EMPTY = ("█", "░") if _UNICODE else ("#", "-")


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def dim(t: str) -> str:
    return _c("2", t)


def bold(t: str) -> str:
    return _c("1", t)


def green(t: str) -> str:
    return _c("32", t)


def yellow(t: str) -> str:
    return _c("33", t)


def red(t: str) -> str:
    return _c("31", t)


def cyan(t: str) -> str:
    return _c("36", t)


# ── A cara do tutor ────────────────────────────────────────────────────────

MNEMO_ART = r"""
     ___
    (o,o)      M N E M O
    /)_)       guardiao da memoria
     " "
"""

MNEMO_ART_UTF = r"""
     ___
    (o,o)      M N E M O
    /)_)       guardião da memória
     " "
"""


def hello(subtitle: str = "vamos configurar seu ambiente de estudo") -> None:
    """Abertura do setup."""
    art = MNEMO_ART_UTF if _UNICODE else MNEMO_ART
    print(cyan(art))
    print(f"    {dim(subtitle)}\n")


def bar(step: int, label: str, detail: str | None = None, width: int = 16) -> None:
    """Uma linha de progresso: [ 4/20 ] Instalando o MCP  ████░░░░░░░░  20%"""
    step = max(0, min(step, TOTAL_STEPS))
    pct = int(round(step * 100 / TOTAL_STEPS))
    filled = int(round(step * width / TOTAL_STEPS))
    track = FULL * filled + EMPTY * (width - filled)
    counter = f"[{step:>2}/{TOTAL_STEPS} ]"
    print(f"{dim(counter)} {label:<30.30} {green(track)} {pct:>3}%")
    if detail:
        print(f"         {dim('→ ' + detail)}")


def ok(msg: str) -> None:
    print(f"         {green('✓' if _UNICODE else 'OK')} {msg}")


def warn(msg: str) -> None:
    print(f"         {yellow('!' )} {msg}")


def fail(msg: str) -> None:
    print(f"         {red('✗' if _UNICODE else 'X')} {msg}")


def say(msg: str) -> None:
    """Fala do tutor, destacada do resto."""
    print(f"\n  {cyan('MNEMO')} {dim('·')} {msg}\n")


def rule(title: str = "") -> None:
    line = ("─" if _UNICODE else "-") * 60
    print(dim(line if not title else f"{line[:3]} {title} {line[len(title) + 5:]}"))


def handoff() -> None:
    """Fecha a parte de máquina e passa a bola para a entrevista do agente."""
    print()
    rule()
    say(
        "Parte de máquina concluída (passos 1–%d).\n"
        "  Os passos %d–%d são a entrevista de onboarding — quem conduz é o agente,\n"
        "  na conversa. Diga a ele: \"rode o onboarding\"." % (MACHINE_STEPS, MACHINE_STEPS + 1, TOTAL_STEPS)
    )


def _cli() -> int:
    args = sys.argv[1:]
    if not args:
        hello()
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "hello":
        hello(*rest[:1])
    elif cmd == "bar":
        if len(rest) < 2:
            print("uso: mnemo.py bar <passo> <rótulo> [detalhe]", file=sys.stderr)
            return 2
        bar(int(rest[0]), rest[1], rest[2] if len(rest) > 2 else None)
    elif cmd == "say":
        say(" ".join(rest))
    elif cmd in ("ok", "warn", "fail"):
        {"ok": ok, "warn": warn, "fail": fail}[cmd](" ".join(rest))
    else:
        print(f"comando desconhecido: {cmd}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
