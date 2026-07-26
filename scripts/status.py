#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
status.py — o estado do estudo em poucas linhas, e o que fazer agora.

    python3 scripts/status.py                # estado + próximo passo
    python3 scripts/status.py --performance  # tempo cruzado com retenção
    python3 scripts/status.py --json         # para consumo do agente

Por que existe: o agente é instruído a rodar isto como PRIMEIRA ação da sessão.
O gatilho de retorno da Fase 2 e o modo reentrada não podem depender de o agente
lembrar de checar — precisam estar impressos na cara dele antes de qualquer coisa.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mnemo  # noqa: E402
import workspace as ws  # noqa: E402


def coletar() -> dict:
    con = ws.abrir_db()
    hoje = date.today().isoformat()

    venc = con.execute(
        "SELECT COUNT(*), MIN(due_date) FROM cards WHERE due_date <= ?", (hoje,)
    ).fetchone()
    total_cards = con.execute("SELECT COUNT(*) FROM cards").fetchone()[0]

    aberta = con.execute(
        "SELECT * FROM study_sessions WHERE fim IS NULL ORDER BY inicio DESC LIMIT 1"
    ).fetchone()
    semana = con.execute(
        "SELECT COALESCE(SUM(duracao_min),0), COUNT(*) FROM study_sessions "
        "WHERE fim IS NOT NULL AND date(inicio) >= date('now','-7 day')"
    ).fetchone()
    ultima_sessao_db = con.execute(
        "SELECT MAX(date(inicio)) FROM study_sessions WHERE fim IS NOT NULL"
    ).fetchone()[0]
    ultimo_recall = con.execute("SELECT MAX(review_date) FROM review_log").fetchone()[0]

    m = ws.materia_ativa() or {}
    # A "última sessão" é a mais recente entre o que o ledger diz e o que o banco viu.
    candidatos = [c for c in (m.get("ultima_sessao"), ultima_sessao_db, ultimo_recall) if c]
    ultima = max(candidatos) if candidatos else None

    d = {
        "materia": m.get("materia"),
        "ledger": m["arquivo"].relative_to(ws.WS).as_posix() if m.get("arquivo") else None,
        "etapa": m.get("retomar_topico"),
        "proxima_acao": m.get("proxima_acao"),
        "dominados": m.get("dominados", 0),
        "total_topicos": m.get("total_topicos", 0),
        "rigor": int(m["rigor"]) if (m.get("rigor") or "").isdigit() else ws.nivel_rigor(),
        "cards_total": total_cards,
        "cards_vencidos": venc[0] or 0,
        "atraso_max_dias": ws.dias_desde(venc[1]) if venc[1] else None,
        "fase2_iniciada_em": m.get("fase2_iniciada_em"),
        "fase2_dias": ws.dias_desde(m.get("fase2_iniciada_em")),
        "ultima_sessao": ultima,
        "dias_sem_sessao": ws.dias_desde(ultima),
        "min_7dias": semana[0] or 0,
        "sessoes_7dias": semana[1] or 0,
        "sessao_aberta": dict(aberta) if aberta else None,
        "ritmo": ws.ritmo(),
    }

    ausente = (d["dias_sem_sessao"] or 0) >= ws.REENTRADA_DIAS
    acumulado = d["cards_vencidos"] >= ws.REENTRADA_BACKLOG
    d["reentrada"] = bool(d["cards_total"] and (ausente or acumulado))
    d["reentrada_motivo"] = (
        "ausência" if ausente and not acumulado else
        "backlog" if acumulado and not ausente else
        "ausência + backlog" if ausente and acumulado else None
    )
    d["proximo_passo"] = decidir(d)
    con.close()
    return d


def decidir(d: dict) -> dict:
    """A única decisão que o script toma: por onde a sessão começa."""
    if d["sessao_aberta"]:
        ini = d["sessao_aberta"]["inicio"]
        return {"acao": "fechar_sessao",
                "texto": f"Há uma sessão aberta desde {ini[:16].replace('T', ' ')}. "
                         "Pergunte se terminou e feche com `sessao.py fim` antes de seguir."}

    if d["reentrada"]:
        return {"acao": "reentrada",
                "texto": f"MODO REENTRADA ({d['reentrada_motivo']}). Teto de {ws.REENTRADA_TETO} cards, "
                         "ordem por MAIOR estabilidade, dica 1 tentativa antes do normal, "
                         "e nenhum conteúdo novo hoje. Não reagende o backlog sem autorização."}

    f2 = d["fase2_dias"]
    if f2 is not None and f2 >= ws.FASE2_EXPIRA:
        return {"acao": "fase2_expirada",
                "texto": f"Fase 2 aberta há {ws.plural(f2, 'dia', 'dias')} — assuma que o material não "
                         "foi consumido. Ofereça: fazer o recall assim mesmo (revela o que ficou) "
                         "ou regenerar os artefatos."}
    if f2 is not None and f2 >= ws.FASE2_LEMBRAR:
        return {"acao": "fase2_pendente",
                "texto": f"Fase 2 aberta há {ws.plural(f2, 'dia', 'dias')}. COMECE por ela: "
                         "pergunte pelo material antes de qualquer conteúdo novo."}

    if d["cards_vencidos"]:
        return {"acao": "revisao",
                "texto": f"{ws.plural(d['cards_vencidos'], 'card vencido', 'cards vencidos')}. "
                         "Revisão FSRS antes de conteúdo novo (REVISAO_IA.md)."}

    if f2 is not None:
        return {"acao": "fase2_recente",
                "texto": "Fase 2 aberta há pouco. Mencione o material e siga o que o aluno pedir."}

    if not d["materia"]:
        return {"acao": "sem_materia",
                "texto": "Nenhuma matéria registrada. Ofereça começar uma (COOKBOOK.md Parte B)."}

    return {"acao": "loop",
            "texto": f"Sem pendências. Siga o loop a partir de: {d['proxima_acao'] or d['etapa'] or 'retomar_em'}"}


def imprimir(d: dict) -> None:
    titulo = d["materia"] or "nenhuma matéria registrada"
    sub = (f"etapa {min(d['dominados'] + 1, d['total_topicos'])}/{d['total_topicos']} · {d['etapa']}"
           if d["total_topicos"] and d["etapa"] else "")
    # cabeçalho montado aqui (e não a partir de mnemo.MNEMO_ART) para o texto
    # ficar ao lado da coruja em vez de colidir com ela
    olhos, corpo = ("(o,o)", '/)_)') if mnemo._UNICODE else ("(o,o)", "/)_)")
    print()
    print(f"   {mnemo.cyan('  ___')}")
    print(f"   {mnemo.cyan(olhos)}   {mnemo.bold('MNEMO')} {mnemo.dim('·')} {mnemo.bold(titulo)}")
    print(f"   {mnemo.cyan(corpo)}    {mnemo.dim(sub)}")
    print(f"   {mnemo.cyan('  \" \"')}")
    print()

    def linha(rot: str, val: str, obs: str = "") -> None:
        print(f"  {rot:<20}{val:<14}{mnemo.dim(obs)}".rstrip())

    atraso = (f"o mais antigo há {ws.plural(d['atraso_max_dias'], 'dia', 'dias')}"
              if d["cards_vencidos"] and d["atraso_max_dias"] else "")
    linha("Cards vencidos", str(d["cards_vencidos"]), f"{atraso}  ·  {d['cards_total']} no total")

    f2 = d["fase2_dias"]
    if f2 is None:
        linha("Fase 2", "fechada", "nenhum material aguardando consumo")
    else:
        linha("Fase 2", "aberta hoje" if f2 == 0 else f"há {ws.plural(f2, 'dia', 'dias')}",
              f"material entregue em {d['fase2_iniciada_em']}")

    dss = d["dias_sem_sessao"]
    linha("Última sessão",
          "hoje" if dss == 0 else (f"há {ws.plural(dss, 'dia', 'dias')}" if dss is not None else "nunca"),
          d["ultima_sessao"] or "")
    linha("Tempo (7 dias)", f"{d['min_7dias']} min",
          f"em {ws.plural(d['sessoes_7dias'], 'sessão', 'sessões')}  ·  "
          f"bloco de {d['ritmo']['bloco_min']} min")
    linha("Rigor", f"nível {d['rigor']}", "")

    if d["sessao_aberta"]:
        print()
        mnemo.warn(f"sessão #{d['sessao_aberta']['id']} ainda aberta")

    print()
    mnemo.rule(" PRÓXIMO PASSO ")
    p = d["proximo_passo"]
    cor = mnemo.red if p["acao"] == "reentrada" else (
        mnemo.yellow if p["acao"].startswith("fase2") and p["acao"] != "fase2_recente" else mnemo.green)
    print()
    for pedaco in _quebrar(p["texto"], 74):
        print(f"  {cor(pedaco)}")
    print()


def _quebrar(txt: str, largura: int) -> list[str]:
    saida, atual = [], ""
    for p in txt.split():
        if len(atual) + len(p) + 1 > largura:
            saida.append(atual)
            atual = p
        else:
            atual = f"{atual} {p}".strip()
    if atual:
        saida.append(atual)
    return saida


def performance() -> int:
    """Tempo SEMPRE cruzado com retenção. Minuto isolado é métrica de vaidade."""
    con = ws.abrir_db()
    linhas = con.execute("""
        SELECT date(s.inicio) dia,
               SUM(s.duracao_min) minutos,
               COUNT(*) sessoes,
               (SELECT COUNT(*) FROM review_log r WHERE r.review_date = date(s.inicio)) revisados,
               (SELECT COUNT(*) FROM review_log r WHERE r.review_date = date(s.inicio) AND r.rating >= 3) retidos
        FROM study_sessions s
        WHERE s.fim IS NOT NULL
        GROUP BY dia ORDER BY dia DESC LIMIT 21
    """).fetchall()

    mnemo.rule(" TEMPO x RETENÇÃO ")
    print()
    if not linhas:
        print(f"  {mnemo.dim('Nenhuma sessão cronometrada ainda.')}")
        print(f"  {mnemo.dim('Comece uma com: python3 scripts/sessao.py iniciar')}")
        print()
        return 0

    print(f"  {'dia':<12}{'min':>6}{'sessões':>9}{'revisados':>11}{'retidos':>9}{'min/retido':>12}")
    print(f"  {mnemo.dim('─' * 59 if mnemo._UNICODE else '-' * 59)}")
    tot_min = tot_ret = 0
    for r in linhas:
        custo = f"{r['minutos'] / r['retidos']:.1f}" if r["retidos"] else "—"
        print(f"  {r['dia']:<12}{r['minutos']:>6}{r['sessoes']:>9}"
              f"{r['revisados']:>11}{r['retidos']:>9}{custo:>12}")
        tot_min += r["minutos"] or 0
        tot_ret += r["retidos"] or 0
    print(f"  {mnemo.dim('─' * 59 if mnemo._UNICODE else '-' * 59)}")
    media = f"{tot_min / tot_ret:.1f} min" if tot_ret else "—"
    print(f"  {mnemo.bold('Custo médio por conceito retido:')} {media}")
    print()
    print(f"  {mnemo.dim('Retido = rating 3 ou 4 no recall daquele dia. É o único número que importa aqui —')}")
    print(f"  {mnemo.dim('minutos sozinhos medem esforço, não aprendizado.')}")
    print()
    con.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Estado do estudo e o que fazer agora.")
    ap.add_argument("--json", action="store_true", help="saída estruturada")
    ap.add_argument("--performance", action="store_true", help="tempo cruzado com retenção")
    args = ap.parse_args()

    if args.performance:
        return performance()

    d = coletar()
    if args.json:
        d.pop("ritmo", None)
        print(json.dumps(d, ensure_ascii=False, indent=2, default=str))
        return 0
    imprimir(d)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileNotFoundError as e:
        mnemo.fail(str(e))
        print(f"         {mnemo.dim('rode primeiro: python3 scripts/setup.py')}")
        raise SystemExit(2)
    except KeyboardInterrupt:
        print()
        raise SystemExit(130)
