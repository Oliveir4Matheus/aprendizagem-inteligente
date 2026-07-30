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
    # Sessões interrompidas (o aluno esqueceu de fechar) ficam de fora de toda
    # estatística: a duração delas é ficção e contaminaria min/conceito-retido.
    semana = con.execute(
        "SELECT COALESCE(SUM(duracao_min),0), COUNT(*) FROM study_sessions "
        "WHERE fim IS NOT NULL AND interrompida = 0 AND date(inicio) >= date('now','-7 day')"
    ).fetchone()
    ultima_sessao_db = con.execute(
        "SELECT MAX(date(inicio)) FROM study_sessions WHERE fim IS NOT NULL AND interrompida = 0"
    ).fetchone()[0]
    interrompidas = con.execute(
        "SELECT COUNT(*) FROM study_sessions WHERE interrompida = 1 "
        "AND date(inicio) >= date('now','-7 day')"
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
        "interrompidas_7dias": interrompidas,
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
                         "Revisão FSRS antes de conteúdo novo: "
                         "scripts/revisar.py pendentes (protocolo em REVISAO_IA.md)."}

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
    obs = (f"em {ws.plural(d['sessoes_7dias'], 'sessão', 'sessões')}  ·  "
           f"bloco de {d['ritmo']['bloco_min']} min")
    if d["interrompidas_7dias"]:
        obs += f"  ·  {d['interrompidas_7dias']} interrompida(s), fora da conta"
    linha("Tempo (7 dias)", f"{d['min_7dias']} min", obs)
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
        WHERE s.fim IS NOT NULL AND s.interrompida = 0
        GROUP BY dia ORDER BY dia DESC LIMIT 21
    """).fetchall()
    perdidas = con.execute(
        "SELECT COUNT(*) FROM study_sessions WHERE interrompida = 1").fetchone()[0]

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
    if perdidas:
        print(f"  {mnemo.dim(f'{perdidas} sessão(ões) interrompida(s) fora da conta — duração não confiável.')}")
    print()
    con.close()
    return 0


def calibracao() -> int:
    """O aluno sabe o que ele não sabe?

    Compara o que ele PREVIU antes de saber o resultado com o que aconteceu. É a
    única métrica aqui que fala sobre a capacidade do aluno de se julgar — que é
    justamente o que ele precisa levar embora quando o tutor não estiver mais lá.
    """
    con = ws.abrir_db()
    linhas = con.execute("""
        SELECT confianca, COUNT(*) n,
               SUM(CASE WHEN rating >= 3 THEN 1 ELSE 0 END) acertos
        FROM review_log WHERE confianca IS NOT NULL
        GROUP BY confianca ORDER BY confianca DESC
    """).fetchall()
    sem = con.execute("SELECT COUNT(*) FROM review_log WHERE confianca IS NULL").fetchone()[0]

    mnemo.rule(" CALIBRAÇÃO METACOGNITIVA ")
    print()
    if not linhas:
        print(f"  {mnemo.dim('Nenhuma previsão registrada ainda.')}")
        print(f"  {mnemo.dim('O tutor deve perguntar a confiança ANTES de revelar cada resposta.')}")
        if sem:
            print(f"  {mnemo.dim(f'({sem} revisões antigas sem previsão — normal, é anterior a esta regra.)')}")
        print()
        return 0

    print(f"  {'você previu':<20}{'itens':>7}{'acertou':>9}{'previsto':>10}{'real':>8}{'desvio':>9}")
    print(f"  {mnemo.dim('─' * 63 if mnemo._UNICODE else '-' * 63)}")
    # Dois números, não um. Erro e viés medem coisas diferentes e um esconde o outro:
    # somar desvios com sinal faz o excesso numa faixa cancelar a falta em outra, e
    # um aluno mal calibrado nos dois sentidos apareceria como bem calibrado.
    soma_abs = soma_sinal = total = 0.0
    for r in linhas:
        rotulo, p = ws.CONFIANCA.get(r["confianca"], ("?", 0.5))
        real = r["acertos"] / r["n"]
        desvio = real - p
        cor = mnemo.green if abs(desvio) <= 0.10 else (mnemo.yellow if abs(desvio) <= 0.25 else mnemo.red)
        print(f"  {rotulo:<20}{r['n']:>7}{r['acertos']:>9}{p * 100:>9.0f}%{real * 100:>7.0f}%"
              f"{cor(f'{desvio * 100:>+8.0f}%')}")
        soma_abs += abs(desvio) * r["n"]
        soma_sinal += (p - real) * r["n"]
        total += r["n"]
    print(f"  {mnemo.dim('─' * 63 if mnemo._UNICODE else '-' * 63)}")

    erro = soma_abs / total          # magnitude: o quanto você erra ao se julgar
    vies = soma_sinal / total        # direção: para que lado você erra

    cor_e = mnemo.green if erro <= 0.10 else (mnemo.yellow if erro <= 0.20 else mnemo.red)
    rotulo_e = "preciso" if erro <= 0.10 else ("impreciso" if erro <= 0.20 else "muito impreciso")
    print(f"  {mnemo.bold('Erro de calibração:')} {cor_e(f'{erro * 100:.0f}% — {rotulo_e}')}"
          f"   {mnemo.dim('(o quanto sua previsão erra, em qualquer direção)')}")

    if vies > 0.08:
        cor_v, rotulo_v = mnemo.red, "excesso de confiança"
        recado = ("Você tende a achar que sabe mais do que sabe. É o viés mais comum e o mais "
                  "caro: leva a parar de revisar cedo demais, justamente no que ainda não firmou.")
    elif vies < -0.08:
        cor_v, rotulo_v = mnemo.yellow, "confiança baixa demais"
        recado = ("Você sabe mais do que acha. Custa tempo revisando o que já está firme e "
                  "desgasta a motivação sem necessidade.")
    else:
        cor_v, rotulo_v = mnemo.green, "sem viés claro"
        recado = "Você não pende sistematicamente para nenhum lado."
    print(f"  {mnemo.bold('Viés:')}               {cor_v(f'{vies * 100:+.0f}% — {rotulo_v}')}"
          f"   {mnemo.dim('(para que lado você erra)')}")
    print()
    if erro > 0.20 and abs(vies) <= 0.08:
        recado = ("Atenção: seu viés parece pequeno porque os erros se cancelam — você erra "
                  "muito para os dois lados. Isso é pior que um viés consistente, porque não "
                  "há uma correção simples: sua sensação de saber está pouco relacionada ao "
                  "que você de fato sabe.")
    for pedaco in _quebrar(recado, 72):
        print(f"  {mnemo.dim(pedaco)}")
    print()

    piores = con.execute("""
        SELECT c.front, l.review_date FROM review_log l JOIN cards c ON c.id = l.card_id
        WHERE l.confianca = 2 AND l.rating <= 2 ORDER BY l.review_date DESC LIMIT 5
    """).fetchall()
    if piores:
        print(f"  {mnemo.bold('Onde você errou estando confiante')} "
              f"{mnemo.dim('— é aqui que mora o que você não sabe que não sabe:')}")
        for p in piores:
            print(f"    {mnemo.dim('·')} {p['front'][:66]}")
        print()
    con.close()
    return 0


def fila() -> int:
    """A fila de revisão de hoje, já reordenada para alternar tópicos."""
    con = ws.abrir_db()
    hoje = date.today().isoformat()
    cards = con.execute(
        "SELECT * FROM cards WHERE due_date <= ? ORDER BY state DESC, due_date ASC LIMIT 40",
        (hoje,),
    ).fetchall()
    if not cards:
        print("nenhum card vencido hoje")
        return 0
    ordenada = ws.fila_intercalada(cards)
    print(f"{len(ordenada)} cards · ordem intercalada (alterna tópicos para forçar discriminação)\n")
    anterior = None
    for i, c in enumerate(ordenada, 1):
        deck = c["deck"] or "—"
        marca = " " if deck != anterior else mnemo.yellow("↑ mesmo tópico seguido")
        print(f"  {i:>2}. [{deck[:38]:<38}] {c['front'][:44]}  {marca}")
        anterior = deck
    con.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Estado do estudo e o que fazer agora.")
    ap.add_argument("--json", action="store_true", help="saída estruturada")
    ap.add_argument("--performance", action="store_true", help="tempo cruzado com retenção")
    ap.add_argument("--calibracao", action="store_true", help="previsão do aluno x resultado real")
    ap.add_argument("--fila", action="store_true", help="fila de hoje, intercalada por tópico")
    args = ap.parse_args()

    if args.performance:
        return performance()
    if args.calibracao:
        return calibracao()
    if args.fila:
        return fila()

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
