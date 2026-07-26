#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sessao.py — cronômetro da sessão de estudo, em blocos de foco.

    python3 scripts/sessao.py iniciar                  # começa a contar
    python3 scripts/sessao.py iniciar --bloco 50 --pausa 10 --blocos 3
    python3 scripts/sessao.py iniciar --tipo recall
    python3 scripts/sessao.py fim                      # fecha e resume
    python3 scripts/sessao.py fim --absorvido "RTY e COPQ ficaram; SIPOC não"
    python3 scripts/sessao.py agora                    # o que está aberto

Não há contagem regressiva no terminal: isso travaria o shell e o agente, e você
não vai estudar olhando para ele. O script grava início e fim e te diz a que horas
cada bloco fecha — o relógio é o seu.

O tamanho do bloco, das pausas e a quantidade de blocos vêm do `estudo/PERFIL.md`
e podem ser sobrescritos por flag nesta execução.

> Tempo sozinho não quer dizer nada. Esta tabela existe para ser cruzada com o
> review_log e responder "quanto custou cada conceito retido" — nunca para dizer
> "você estudou 2h hoje". Ver `python3 scripts/status.py --performance`.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mnemo  # noqa: E402
import workspace as ws  # noqa: E402

TIPOS = ("study", "recall", "revisao")


def sessao_aberta(con):
    return con.execute(
        "SELECT * FROM study_sessions WHERE fim IS NULL ORDER BY inicio DESC LIMIT 1"
    ).fetchone()


def plano_de_blocos(inicio: datetime, cfg: dict) -> list[str]:
    """Horários de término de cada bloco, já contando as pausas."""
    linhas, t = [], inicio
    for i in range(1, cfg["blocos_alvo"] + 1):
        fim = t + timedelta(minutes=cfg["bloco_min"])
        linhas.append(f"bloco {i}  {t:%H:%M} → {fim:%H:%M}")
        longa = i % cfg["blocos_ate_pausa_longa"] == 0
        pausa = cfg["pausa_longa_min"] if longa else cfg["pausa_min"]
        if i < cfg["blocos_alvo"]:
            rotulo = "pausa longa" if longa else "pausa"
            linhas.append(f"          {fim:%H:%M} → {fim + timedelta(minutes=pausa):%H:%M}  {rotulo} ({pausa} min)")
            t = fim + timedelta(minutes=pausa)
    return linhas


def cmd_iniciar(args) -> int:
    con = ws.abrir_db()
    aberta = sessao_aberta(con)
    if aberta:
        desde = ws.dias_desde(aberta["inicio"])
        mnemo.warn(f"já existe uma sessão aberta (#{aberta['id']}, iniciada em {aberta['inicio'][:16]}).")
        if desde and desde >= 1:
            mnemo.warn("ela ficou aberta de um dia para o outro — vou fechá-la como interrompida.")
            con.execute("UPDATE study_sessions SET fim=?, interrompida=1 WHERE id=?",
                        (aberta["inicio"], aberta["id"]))
            con.commit()
        else:
            print(f"         {mnemo.dim('feche com: python3 scripts/sessao.py fim')}")
            return 1

    cfg = ws.ritmo()
    if args.bloco:
        cfg["bloco_min"] = args.bloco
    if args.pausa:
        cfg["pausa_min"] = args.pausa
    if args.pausa_longa:
        cfg["pausa_longa_min"] = args.pausa_longa
    if args.blocos:
        cfg["blocos_alvo"] = args.blocos

    m = ws.materia_ativa()
    materia = args.materia or (m["materia"] if m else "")
    etapa = args.etapa or (m["retomar_topico"] if m else None)

    agora = datetime.now()
    cur = con.execute(
        "INSERT INTO study_sessions(materia,etapa,tipo,inicio,bloco_min,blocos_alvo) "
        "VALUES(?,?,?,?,?,?)",
        (materia, etapa, args.tipo, agora.isoformat(timespec="seconds"),
         cfg["bloco_min"], cfg["blocos_alvo"]),
    )
    con.commit()

    total = cfg["bloco_min"] * cfg["blocos_alvo"]
    mnemo.say(f"Sessão #{cur.lastrowid} iniciada — {materia or 'sem matéria'}"
              + (f" · {etapa}" if etapa else ""))
    print(f"    {mnemo.bold('Foco')} {cfg['bloco_min']} min · "
          f"{mnemo.bold('pausa')} {cfg['pausa_min']} min · "
          f"{mnemo.bold('pausa longa')} {cfg['pausa_longa_min']} min a cada {cfg['blocos_ate_pausa_longa']} blocos")
    print()
    for linha in plano_de_blocos(agora, cfg):
        print(f"    {linha}")
    print()
    print(f"    {mnemo.dim(f'{total} min de foco no total. Ao terminar:')} python3 scripts/sessao.py fim")
    return 0


def cmd_fim(args) -> int:
    con = ws.abrir_db()
    s = sessao_aberta(con)
    if not s:
        mnemo.warn("nenhuma sessão aberta.")
        print(f"         {mnemo.dim('inicie com: python3 scripts/sessao.py iniciar')}")
        return 1

    inicio = datetime.fromisoformat(s["inicio"])
    agora = datetime.now()
    dur = max(1, round((agora - inicio).total_seconds() / 60))
    feitos = args.blocos_feitos
    if feitos is None:
        feitos = max(1, round(dur / (s["bloco_min"] or 25)))

    con.execute(
        "UPDATE study_sessions SET fim=?, duracao_min=?, blocos_feitos=?, absorvido=? WHERE id=?",
        (agora.isoformat(timespec="seconds"), dur, feitos, args.absorvido, s["id"]),
    )
    con.commit()

    mnemo.say(f"Sessão #{s['id']} fechada — {dur} min em {ws.plural(feitos, 'bloco', 'blocos')}"
              + (f" · {s['materia']}" if s["materia"] else ""))

    hoje = agora.date().isoformat()
    tot = con.execute(
        "SELECT COALESCE(SUM(duracao_min),0), COUNT(*) FROM study_sessions WHERE date(inicio)=?",
        (hoje,),
    ).fetchone()
    revs = con.execute("SELECT COUNT(*) FROM review_log WHERE review_date=?", (hoje,)).fetchone()[0]
    print(f"    Hoje: {tot[0]} min em {ws.plural(tot[1], 'sessão', 'sessões')} · "
          f"{ws.plural(revs, 'card revisado', 'cards revisados')}")

    if s["tipo"] == "study" and revs == 0:
        print()
        mnemo.warn("estudo registrado, mas nenhum recall ainda — o material não vira retenção sozinho.")
        print(f"         {mnemo.dim('Diga ao agente: \"terminei, pode fazer o recall\".')}")
    return 0


def cmd_agora(args) -> int:
    con = ws.abrir_db()
    s = sessao_aberta(con)
    if not s:
        print("nenhuma sessão aberta")
        return 0
    inicio = datetime.fromisoformat(s["inicio"])
    dur = round((datetime.now() - inicio).total_seconds() / 60)
    bloco = s["bloco_min"] or 25
    print(f"sessão #{s['id']} · {s['materia'] or 'sem matéria'} · tipo {s['tipo']}")
    print(f"aberta há {dur} min · bloco de {bloco} min · "
          f"{dur // bloco} bloco(s) completo(s) de {s['blocos_alvo'] or '?'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Cronômetro da sessão de estudo em blocos de foco.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("iniciar", help="começa a contar")
    i.add_argument("--tipo", choices=TIPOS, default="study")
    i.add_argument("--materia")
    i.add_argument("--etapa")
    i.add_argument("--bloco", type=int, help="minutos de foco (sobrescreve o PERFIL)")
    i.add_argument("--pausa", type=int, help="minutos de pausa curta")
    i.add_argument("--pausa-longa", type=int, dest="pausa_longa", help="minutos de pausa longa")
    i.add_argument("--blocos", type=int, help="quantos blocos nesta sessão")
    i.set_defaults(fn=cmd_iniciar)

    f = sub.add_parser("fim", help="fecha a sessão aberta")
    f.add_argument("--absorvido", help="o que ficou, nas suas palavras")
    f.add_argument("--blocos-feitos", type=int, dest="blocos_feitos")
    f.set_defaults(fn=cmd_fim)

    a = sub.add_parser("agora", help="mostra a sessão aberta")
    a.set_defaults(fn=cmd_agora)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print()
        raise SystemExit(130)
