#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_revisar.py — cobre a fórmula do FSRS-5 e as travas de idempotência do revisar.py.

    python3 scripts/test_revisar.py

Roda contra um banco temporário; nunca toca em estudo/progresso/srs.db. Só
biblioteca padrão — sem pytest, sem instalar nada, igual ao resto dos scripts.

Este arquivo existe porque a fórmula saiu da prosa e virou código: código dá para
testar, prosa não. O caso mais importante daqui é `teste_rating2_nao_congela` — a
regressão do W[15], o bug que já existiu neste projeto e que só aparecia semanas
depois, na forma de um card que nunca mais mudava de intervalo.
"""
from __future__ import annotations

import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import workspace as ws  # noqa: E402

_TMP = tempfile.TemporaryDirectory()
ws.DB = Path(_TMP.name) / "srs_test.db"

import revisar  # noqa: E402  (importado DEPOIS de redirecionar o banco)

HOJE = date(2026, 7, 29)
falhas: list[str] = []


def checa(condicao: bool, descricao: str) -> None:
    print(f"  {'ok  ' if condicao else 'FALHA'} {descricao}")
    if not condicao:
        falhas.append(descricao)


class Args:
    """Substitui o Namespace do argparse com defaults iguais aos do CLI."""

    def __init__(self, **kw):
        padrao = dict(json=None, reentrada=False, front=None, back=None, tags=None,
                      deck=None, subject=None, card_id=None, rating=None, confianca=None,
                      tentativas=1, usou_dica=0, tipo_item=None, dias=5, confirmar=False)
        padrao.update(kw)
        self.__dict__.update(padrao)


# ── a fórmula ────────────────────────────────────────────────────────────────


def teste_funcao_pura():
    a = revisar.calcular_fsrs(2, 5.0, 10.0, "2026-07-19", 3, HOJE)
    b = revisar.calcular_fsrs(2, 5.0, 10.0, "2026-07-19", 3, HOJE)
    checa(a == b, "calcular_fsrs é pura — mesma entrada, mesma saída")


def teste_rating_invalido():
    for r in (0, 5, -1):
        try:
            revisar.calcular_fsrs(0, 0, 0, None, r, HOJE)
            checa(False, f"rating {r} deveria ser recusado")
        except ValueError:
            checa(True, f"rating {r} recusado com ValueError")


def teste_rating2_nao_congela():
    """Regressão do W[15]: 'Hard' penaliza o ganho, não o zera.

    Com W[15] = 0 a estabilidade nova vira `max(0.1, s * (0 + 1)) == s`, o card
    volta com o mesmo intervalo para sempre e o aluno nunca progride nele. Este
    teste é a razão principal de a fórmula ter saído do REVISAO_IA.md.
    """
    s0 = 10.0
    r = revisar.calcular_fsrs(2, 5.0, s0, (HOJE - timedelta(days=10)).isoformat(), 2, HOJE)
    checa(r["stability"] > s0, f"rating 2 aumenta a estabilidade ({s0} → {r['stability']})")
    checa(r["interval"] > 1, f"rating 2 gera intervalo > 1 dia (veio {r['interval']})")
    checa(revisar.W[15] > 0, "W[15] continua positivo")


def teste_ordem_dos_intervalos():
    """Nota melhor nunca pode render intervalo menor."""
    base = dict(state=2, difficulty=5.0, stability=10.0,
                last_review=(HOJE - timedelta(days=10)).isoformat(), hoje=HOJE)
    i = {n: revisar.calcular_fsrs(rating=n, **base)["interval"] for n in (2, 3, 4)}
    checa(i[2] <= i[3] <= i[4], f"intervalo cresce com o rating: {i[2]} ≤ {i[3]} ≤ {i[4]}")


def teste_lapso():
    r = revisar.calcular_fsrs(2, 5.0, 30.0, (HOJE - timedelta(days=30)).isoformat(), 1, HOJE)
    checa(r["state"] == 3, "rating 1 em Review manda o card para Relearning (state 3)")
    checa(r["interval"] == 1, "rating 1 reagenda para o dia seguinte")


def teste_card_novo():
    r = revisar.calcular_fsrs(0, 0, 0, None, 3, HOJE)
    checa(r["state"] == 2 and r["interval"] >= 1, "card novo com rating 3 entra em Review")
    checa(r["due_date"] == (HOJE + timedelta(days=r["interval"])).isoformat(),
          "due_date bate com o intervalo calculado")


# ── as travas ────────────────────────────────────────────────────────────────


def _um_card(front="P1") -> int:
    revisar.cmd_criar(Args(front=front, back="R1", deck="D::T", subject="S"))
    con = ws.abrir_db()
    cid = con.execute("SELECT id FROM cards WHERE front=?", (front,)).fetchone()["id"]
    con.close()
    return cid


def teste_criar_deduplica():
    revisar.cmd_criar(Args(front="dup", back="x", deck="D::T", subject="S"))
    revisar.cmd_criar(Args(front="dup", back="x", deck="D::T", subject="S"))
    con = ws.abrir_db()
    n = con.execute("SELECT COUNT(*) c FROM cards WHERE front='dup'").fetchone()["c"]
    con.close()
    checa(n == 1, f"criar duas vezes o mesmo front deixa 1 card (achou {n})")


def teste_revisar_idempotente():
    cid = _um_card("idem")
    revisar.cmd_revisar(Args(card_id=cid, rating=3, confianca=2, tipo_item="recall"))
    con = ws.abrir_db()
    antes = dict(con.execute("SELECT * FROM cards WHERE id=?", (cid,)).fetchone())
    con.close()

    revisar.cmd_revisar(Args(card_id=cid, rating=1, confianca=0, tipo_item="recall"))
    con = ws.abrir_db()
    depois = dict(con.execute("SELECT * FROM cards WHERE id=?", (cid,)).fetchone())
    logs = con.execute("SELECT COUNT(*) c FROM review_log WHERE card_id=?", (cid,)).fetchone()["c"]
    con.close()

    checa(antes == depois, "segunda revisão no mesmo dia não altera o card")
    checa(logs == 1, f"segunda revisão não duplica o review_log (linhas: {logs})")


def teste_revisar_card_inexistente():
    checa(revisar.cmd_revisar(Args(card_id=999999, rating=3)) == 2,
          "revisar card inexistente sai com código 2, sem escrever nada")


def teste_espalhar_exige_confirmacao():
    checa(revisar.cmd_espalhar(Args(dias=5)) == 2,
          "espalhar sem --confirmar recusa (código 2)")


def teste_espalhar_preserva_modelo():
    con = ws.abrir_db()
    antes = {r["id"]: (r["stability"], r["difficulty"])
             for r in con.execute("SELECT id, stability, difficulty FROM cards")}
    con.close()

    revisar.cmd_espalhar(Args(dias=5, confirmar=True))

    con = ws.abrir_db()
    depois = {r["id"]: (r["stability"], r["difficulty"])
              for r in con.execute("SELECT id, stability, difficulty FROM cards")}
    con.close()
    checa(antes == depois, "espalhar mexe só em due_date — stability e difficulty intactas")


# ── runner ───────────────────────────────────────────────────────────────────


def main() -> int:
    grupos = {
        "fórmula FSRS-5": [teste_funcao_pura, teste_rating_invalido, teste_rating2_nao_congela,
                           teste_ordem_dos_intervalos, teste_lapso, teste_card_novo],
        "travas de escrita": [teste_criar_deduplica, teste_revisar_idempotente,
                              teste_revisar_card_inexistente, teste_espalhar_exige_confirmacao,
                              teste_espalhar_preserva_modelo],
    }
    for titulo, testes in grupos.items():
        print(f"\n{titulo}")
        for t in testes:
            t()

    print()
    if falhas:
        print(f"✗ {len(falhas)} falha(s):")
        for f in falhas:
            print(f"    · {f}")
        return 1
    print("✓ tudo passou")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
