#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
revisar.py — único ponto de escrita no srs.db: revisão FSRS, criação de cards,
redistribuição de backlog.

Substitui o padrão antigo de REVISAO_IA.md (SQL/Python digitado na hora pelo
agente a cada sessão): a fórmula do FSRS-5 e as escritas no banco ficam num só
lugar, testado uma vez, chamado por CLI — em vez de retranscritas por qualquer
agente/modelo que conduzir o protocolo. É assim que uma revisão vira idempotente
de verdade: rodar o mesmo comando duas vezes não duplica review_log nem reaplica
o cálculo do FSRS.

    python3 scripts/revisar.py pendentes
    python3 scripts/revisar.py pendentes --reentrada
    python3 scripts/revisar.py revisar --card-id 12 --rating 3 --confianca 2 \\
        --tentativas 1 --usou-dica 0 --tipo-item recall
    python3 scripts/revisar.py criar --front "..." --back "..." \\
        --deck "Estudos::Materia::Topico" --subject "Materia"
    python3 scripts/revisar.py criar --json novos.json
    python3 scripts/revisar.py espalhar --dias 5 --confirmar
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mnemo  # noqa: E402
import workspace as ws  # noqa: E402

# Pesos padrão do FSRS-5 (19 parâmetros).
# ⚠️ NÃO edite índices soltos aqui. W[15] é a penalidade de "Hard" e multiplica o
#    GANHO de estabilidade quando rating=2 — se virar 0, todo card avaliado com 2
#    congela no mesmo intervalo para sempre (bug real que já existiu neste projeto,
#    ver docs/MANUAL.md §6.3, quando a fórmula vivia solta em REVISAO_IA.md).
W = [0.40255, 1.18385, 3.173, 15.69105, 7.1949, 0.5345, 1.4604,
     0.0046, 1.54575, 0.1192, 1.01925, 1.9395, 0.11, 0.29605,
     2.2698, 0.2315, 2.9898, 0.51655, 0.6621]
DECAY = -0.5
FACTOR = 0.9 ** (1 / DECAY) - 1
# Retenção-alvo: decisão do projeto, não recomendação técnica — ver docs/MANUAL.md
# §2.2 alavanca 2 (a documentação do FSRS recomenda algo entre 0.85 e 0.90).
RETENCAO_ALVO = 0.95


def retrievability(stability: float, last_review: str | None, hoje: date) -> float | None:
    """R(t) do FSRS: probabilidade estimada de lembrar o card HOJE.

    1.0 = revisado agora; cai conforme o tempo passa, mais devagar quanto maior a
    estabilidade. Devolve None para card nunca revisado — não existe curva de
    esquecimento antes da primeira recuperação, e chutar 0 ali faria o grafo pintar
    conteúdo novo como esquecido.

    Vive aqui, e não no grafo.py, porque a fórmula do FSRS tem UM dono neste projeto.
    """
    if not last_review or stability <= 0:
        return None
    elapsed = (hoje - date.fromisoformat(last_review)).days
    return (1 + FACTOR * max(0, elapsed) / stability) ** DECAY


def calcular_fsrs(state: int, difficulty: float, stability: float,
                   last_review: str | None, rating: int, hoje: date) -> dict:
    """Aplica FSRS-5. Função pura: mesma entrada, sempre a mesma saída."""
    if rating not in (1, 2, 3, 4):
        raise ValueError(f"rating deve ser 1-4, veio {rating}")
    elapsed = (hoje - date.fromisoformat(last_review)).days if last_review else 0
    s, d = stability, difficulty
    r = (1 + FACTOR * elapsed / s) ** DECAY if s > 0 else 0.0

    def _intervalo(ns: float) -> int:
        return max(1, round(ns * (RETENCAO_ALVO ** (1 / DECAY) - 1) / FACTOR))

    if state in (0, 1, 3):  # New / Learning / Relearning
        if state == 0:
            nd = min(10, max(1, W[4] - math.exp(W[5] * (rating - 1)) + 1))
            ns = W[rating - 1]
        else:
            nd = min(10, max(1, (d - W[6] * (rating - 3)) + W[7] * (W[4] - (d - W[6] * (rating - 3)))))
            ns = max(0.1, s)
        if rating == 1:
            new_state, interval = 1, 1
        else:
            new_state, interval = 2, _intervalo(ns)
    else:  # Review
        nd = min(10, max(1, (d - W[6] * (rating - 3)) + W[7] * (W[4] - (d - W[6] * (rating - 3)))))
        if rating == 1:
            ns = max(0.1, W[11] * d ** (-W[12]) * ((s + 1) ** W[13] - 1) * math.exp(W[14] * (1 - r)))
            new_state, interval = 3, 1
        else:
            hp = W[15] if rating == 2 else 1.0
            eb = W[16] if rating == 4 else 1.0
            ns = max(0.1, s * (math.exp(W[8]) * (11 - d) * s ** (-W[9])
                     * (math.exp(W[10] * (1 - r)) - 1) * hp * eb + 1))
            new_state, interval = 2, _intervalo(ns)

    return {
        "state": new_state, "difficulty": round(nd, 4), "stability": round(ns, 4),
        "interval": interval, "due_date": (hoje + timedelta(days=interval)).isoformat(),
        "elapsed": elapsed,
    }


# ── pendentes ────────────────────────────────────────────────────────────────


def cmd_pendentes(args) -> int:
    con = ws.abrir_db()
    hoje = date.today().isoformat()
    if args.reentrada:
        cards = con.execute(
            "SELECT * FROM cards WHERE due_date <= ? ORDER BY stability DESC, due_date ASC LIMIT ?",
            (hoje, ws.REENTRADA_TETO),
        ).fetchall()
    else:
        cards = con.execute(
            "SELECT * FROM cards WHERE due_date <= ? ORDER BY state DESC, due_date ASC LIMIT 20",
            (hoje,),
        ).fetchall()
        cards = ws.fila_intercalada(cards)
    con.close()

    saida = [dict(c) for c in cards]
    if args.json:
        print(json.dumps(saida, ensure_ascii=False, indent=2))
        return 0

    if not saida:
        print("nenhum card vencido hoje")
        return 0
    modo = "reentrada (maior estabilidade primeiro)" if args.reentrada else "intercalada"
    print(f"{len(saida)} cards vencidos · ordem {modo}\n")
    for c in saida:
        print(f"  #{c['id']:<4} [{(c['deck'] or '—')[:34]:<34}] {c['front'][:50]}")
    return 0


# ── revisar ──────────────────────────────────────────────────────────────────


def cmd_revisar(args) -> int:
    con = ws.abrir_db()
    card = con.execute("SELECT * FROM cards WHERE id=?", (args.card_id,)).fetchone()
    if not card:
        mnemo.fail(f"card #{args.card_id} não existe.")
        con.close()
        return 2

    hoje = date.today()
    hoje_s = hoje.isoformat()
    ja_existe = con.execute(
        "SELECT rating FROM review_log WHERE card_id=? AND review_date=?",
        (args.card_id, hoje_s),
    ).fetchone()
    if ja_existe:
        mnemo.warn(f"card #{args.card_id} já tem revisão registrada hoje (rating {ja_existe['rating']}). "
                   "Nada foi alterado — comando é idempotente.")
        con.close()
        return 0

    try:
        r = calcular_fsrs(card["state"], card["difficulty"], card["stability"],
                           card["last_review"], args.rating, hoje)
    except ValueError as e:
        mnemo.fail(str(e))
        con.close()
        return 2

    lapses = card["lapses"] + (1 if args.rating == 1 else 0)
    try:
        con.execute(
            "UPDATE cards SET state=?, difficulty=?, stability=?, due_date=?, "
            "last_review=?, reps=reps+1, lapses=? WHERE id=?",
            (r["state"], r["difficulty"], r["stability"], r["due_date"], hoje_s, lapses, args.card_id),
        )
        con.execute(
            "INSERT INTO review_log(card_id, review_date, rating, elapsed_days, interval_days, "
            "stability, difficulty, state, confianca, tentativas, usou_dica, tipo_item) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (args.card_id, hoje_s, args.rating, r["elapsed"], r["interval"],
             r["stability"], r["difficulty"], r["state"],
             args.confianca, args.tentativas, args.usou_dica, args.tipo_item),
        )
        con.commit()
    except Exception:
        con.rollback()
        con.close()
        raise
    con.close()

    mnemo.ok(f"card #{args.card_id} · rating {args.rating} · "
             f"próxima revisão em {r['due_date']} ({r['interval']} dia(s))")
    return 0


# ── criar ────────────────────────────────────────────────────────────────────


def _inserir_card(con, c: dict, hoje_s: str, agora_s: str) -> bool:
    existe = con.execute("SELECT id FROM cards WHERE front=?", (c["front"],)).fetchone()
    if existe:
        return False
    con.execute(
        "INSERT INTO cards(front, back, tags, deck, subject, due_date, created_at) "
        "VALUES(?,?,?,?,?,?,?)",
        (c["front"], c["back"], json.dumps(c.get("tags", []), ensure_ascii=False),
         c.get("deck", ""), c.get("subject", ""), c.get("due_date", hoje_s), agora_s),
    )
    return True


def cmd_criar(args) -> int:
    if args.json:
        cards = json.loads(Path(args.json).read_text(encoding="utf-8"))
        if not isinstance(cards, list):
            mnemo.fail("--json precisa conter uma lista de objetos {front, back, tags, deck, subject}.")
            return 2
    else:
        if not args.front or not args.back:
            mnemo.fail("informe --front e --back, ou --json <arquivo>.")
            return 2
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        cards = [{"front": args.front, "back": args.back, "tags": tags,
                  "deck": args.deck or "", "subject": args.subject or ""}]

    con = ws.abrir_db()
    hoje_s = date.today().isoformat()
    agora_s = datetime.now().isoformat(timespec="seconds")

    adicionados = pulados = 0
    for c in cards:
        if _inserir_card(con, c, hoje_s, agora_s):
            adicionados += 1
        else:
            pulados += 1
    con.commit()
    con.close()

    mnemo.ok(f"{adicionados} card(s) adicionado(s)." + (f" {pulados} já existia(m) (mesmo front) — pulado(s)."
              if pulados else ""))
    return 0


# ── espalhar ─────────────────────────────────────────────────────────────────


def cmd_espalhar(args) -> int:
    if not args.confirmar:
        mnemo.fail("espalhar exige autorização explícita do aluno. Rode de novo com --confirmar.")
        return 2

    con = ws.abrir_db()
    hoje = date.today()
    restantes = con.execute(
        "SELECT id FROM cards WHERE due_date <= ? ORDER BY stability DESC",
        (hoje.isoformat(),),
    ).fetchall()
    if not restantes:
        mnemo.ok("nenhum card vencido para espalhar.")
        con.close()
        return 0

    for i, row in enumerate(restantes):
        nova = (hoje + timedelta(days=i % args.dias)).isoformat()
        con.execute("UPDATE cards SET due_date=? WHERE id=?", (nova, row["id"]))
    con.commit()
    con.close()

    mnemo.ok(f"{len(restantes)} card(s) espalhado(s) pelos próximos {args.dias} dia(s). "
             "stability e difficulty ficaram intactas — só a fila mudou no tempo.")
    return 0


# ── CLI ────────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Escreve no srs.db: revisão FSRS, criação de cards, redistribuição de backlog.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("pendentes", help="cards vencidos hoje")
    p.add_argument("--reentrada", action="store_true", help="teto e ordem do modo reentrada")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_pendentes)

    r = sub.add_parser("revisar", help="grava uma revisão e recalcula o FSRS")
    r.add_argument("--card-id", type=int, required=True, dest="card_id")
    r.add_argument("--rating", type=int, required=True, choices=(1, 2, 3, 4))
    r.add_argument("--confianca", type=int, choices=(0, 1, 2))
    r.add_argument("--tentativas", type=int, default=1)
    r.add_argument("--usou-dica", type=int, choices=(0, 1), default=0, dest="usou_dica")
    r.add_argument("--tipo-item", choices=("recall", "intercalado", "sintese", "transferencia", "portao"),
                   dest="tipo_item")
    r.set_defaults(fn=cmd_revisar)

    c = sub.add_parser("criar", help="cria card(s) novo(s), com dedupe por front")
    c.add_argument("--front")
    c.add_argument("--back")
    c.add_argument("--tags", help="separadas por vírgula")
    c.add_argument("--deck")
    c.add_argument("--subject")
    c.add_argument("--json", help="arquivo com lista de cards para criar em lote")
    c.set_defaults(fn=cmd_criar)

    e = sub.add_parser("espalhar", help="redistribui due_date do backlog vencido")
    e.add_argument("--dias", type=int, default=5)
    e.add_argument("--confirmar", action="store_true", help="obrigatório — autorização explícita do aluno")
    e.set_defaults(fn=cmd_espalhar)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print()
        raise SystemExit(130)
