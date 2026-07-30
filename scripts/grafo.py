#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafo.py — monta o grafo de conhecimento navegável da matéria ativa.

Lê `estudo/progresso/<materia>-conceitos/*.md` (um arquivo por conceito) e cruza com
o `srs.db` para gerar `estudo/progresso/<materia>-grafo.html`: um grafo clicável, com
a anotação de cada nó num modal central.

    python3 scripts/grafo.py                    # matéria ativa (a de ledger mais recente)
    python3 scripts/grafo.py --materia <slug>   # uma matéria específica
    python3 scripts/grafo.py --validar          # só checa integridade, não gera nada
    python3 scripts/grafo.py --json             # despeja os nós/arestas resolvidos

Duas decisões que o resto do arquivo depende:

1. **O nó desbota.** O grafo do Obsidian só cresce — ele não mente sobre crescimento,
   mas mente sobre domínio, porque nó verde de três semanas atrás parece igual a nó
   verde de ontem. Aqui a cor do nó dominado é escalada pela *retrievability* do FSRS
   (`revisar.retrievability`): conceito decaindo perde saturação, conceito vencido
   pulsa. O grafo cresce E apaga — é instrumento de retenção, não vitrine de troféu.
   Sem isso ele viraria a mesma armadilha que este projeto evita para tempo de estudo
   (ver `docs/MANUAL.md` → tempo isolado é métrica de vaidade).

2. **Nada aqui sabe o nome da matéria.** É harness: a matéria vem do ledger via
   `workspace.materia_ativa()`, os conceitos vêm da pasta, e nenhum termo de nenhuma
   disciplina aparece neste arquivo. O mesmo script serve qualquer matéria do workspace.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mnemo  # noqa: E402
import revisar  # noqa: E402
import workspace as ws  # noqa: E402

STATUS_VALIDOS = ("nao_iniciado", "ensinando", "recall_feito", "dominado")

#: Seções esperadas no corpo do arquivo de conceito (ver templates/conceito.md).
SECAO_NOTA = "O que é"


# ── leitura dos arquivos de conceito ────────────────────────────────────────


def _dividir(txt: str) -> tuple[str, str]:
    """Separa frontmatter e corpo. Sem frontmatter, devolve ('', texto inteiro)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", txt, re.S)
    return (m.group(1), m.group(2)) if m else ("", txt)


def _escalar(valor: str):
    """Converte um valor de frontmatter para bool/int/lista/None/str."""
    v = re.sub(r"\s+#.*$", "", valor).strip()   # comentário à direita (só ' #', não '#')
    if not v:
        return None
    if v in ("true", "false"):
        return v == "true"
    if v.startswith("[") and v.endswith("]"):
        dentro = v[1:-1].strip()
        if not dentro:
            return []
        return [int(x) if x.strip().lstrip("-").isdigit() else x.strip().strip("\"'")
                for x in dentro.split(",")]
    if v.lstrip("-").isdigit():
        return int(v)
    return v.strip("\"'")


def _parse_frontmatter(fm: str) -> dict:
    """Parser estreito, do mesmo espírito do workspace.campo: não é YAML.

    Entende exatamente as duas formas que o template usa — `chave: valor` e uma lista
    de objetos indentada (`- id: X` / `porque: Y`). Qualquer outra coisa é ignorada em
    silêncio, de propósito: arquivo malformado deve degradar, não explodir, para o
    agente ainda conseguir trabalhar sem o script.
    """
    dados: dict = {}
    lista_atual: list | None = None
    item_atual: dict | None = None
    pendente: str | None = None   # `chave:` sem valor — só vira lista se vier um item

    for linha in fm.splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue

        # item novo de lista
        m = re.match(r"^\s+-\s*(\w+):\s*(.*)$", linha)
        if m:
            if pendente is not None:
                # agora sim: a chave em aberto era mesmo uma lista
                lista_atual = []
                dados[pendente] = lista_atual
                pendente = None
            if lista_atual is not None:
                item_atual = {m.group(1): _escalar(m.group(2))}
                lista_atual.append(item_atual)
                continue

        # campo de um item já aberto
        m = re.match(r"^\s+(\w+):\s*(.*)$", linha)
        if m and item_atual is not None:
            item_atual[m.group(1)] = _escalar(m.group(2))
            continue

        # chave de topo
        m = re.match(r"^(\w+):\s*(.*)$", linha)
        if m:
            chave, resto = m.group(1), m.group(2)
            lista_atual, item_atual = None, None
            if resto.strip() == "":
                # Ainda não se sabe se é lista vazia ou escalar vazio. Assume escalar
                # (None) e só promove a lista se a próxima linha trouxer um item — assim
                # `dominado_em:` vazio não vira [] só por estar do lado de `conecta_com:`.
                dados[chave] = None
                pendente = chave
            else:
                pendente = None
                dados[chave] = _escalar(resto)
    return dados


def _secao(corpo: str, titulo: str) -> str:
    """Devolve o texto sob `## titulo`, até o próximo `##` ou o fim."""
    m = re.search(rf"^##\s+{re.escape(titulo)}\s*$\n(.*?)(?=^##\s|\Z)", corpo, re.S | re.M)
    return m.group(1).strip() if m else ""


def _placeholder(txt: str) -> bool:
    """Texto que ainda é o do template (entre _( )_ ou com marcador <...>)."""
    limpo = txt.strip()
    return (not limpo) or limpo.startswith("_(") or bool(re.fullmatch(r"<[^>]*>", limpo))


def carregar_conceitos(pasta: Path) -> list[dict]:
    if not pasta.is_dir():
        return []
    conceitos = []
    for p in sorted(pasta.glob("*.md")):
        if p.name.startswith("_"):
            continue
        fm, corpo = _dividir(p.read_text(encoding="utf-8"))
        d = _parse_frontmatter(fm)
        nota = _secao(corpo, SECAO_NOTA)
        conceitos.append({
            "id": d.get("id") or p.stem,
            "arquivo": p.name,
            "nome": d.get("nome") or p.stem,
            "etapa": d.get("etapa") if isinstance(d.get("etapa"), int) else 0,
            "status": d.get("status") if d.get("status") in STATUS_VALIDOS else "nao_iniciado",
            "dominado_em": d.get("dominado_em"),
            "ponto_fraco": bool(d.get("ponto_fraco")),
            "nota_origem": d.get("nota_origem") if d.get("nota_origem") in ("aluno", "ledger")
                           else "aluno",
            "cards": [c for c in (d.get("cards") or []) if isinstance(c, int)],
            "conecta_com": [x for x in (d.get("conecta_com") or []) if x.get("id")],
            "prepara_para": [x for x in (d.get("prepara_para") or []) if x.get("id")],
            "nota": "" if _placeholder(nota) else nota,
            "nao_confunda": _secao(corpo, "Não confunda com"),
        })
    return conceitos


# ── cruzamento com o SRS ────────────────────────────────────────────────────


def anexar_srs(conceitos: list[dict], hoje: date) -> dict:
    """Acrescenta a cada conceito o estado dos cards que o cobrem.

    A retrievability do CONCEITO é a do seu card mais fraco, não a média: um conceito
    vale o quanto vale o elo que já cedeu. Média esconderia exatamente o card que
    precisa de revisão.
    """
    con = ws.abrir_db()
    linhas = {r["id"]: r for r in con.execute(
        "SELECT id, stability, last_review, due_date, reps, lapses FROM cards")}
    con.close()

    hoje_s = hoje.isoformat()
    orfaos = []
    for c in conceitos:
        rs, vencidos, sem_historico, proxima = [], 0, 0, None
        for cid in c["cards"]:
            row = linhas.get(cid)
            if row is None:
                orfaos.append((c["id"], cid))
                continue
            r = revisar.retrievability(row["stability"], row["last_review"], hoje)
            if r is None:
                sem_historico += 1      # nunca revisado: não tem curva de esquecimento
            else:
                rs.append(r)
            if row["due_date"] <= hoje_s:
                vencidos += 1
            if proxima is None or row["due_date"] < proxima:
                proxima = row["due_date"]
        c["n_cards"] = len([1 for cid in c["cards"] if cid in linhas])
        c["retrievability"] = round(min(rs), 4) if rs else None
        c["vencidos"] = vencidos
        # Card nunca revisado fica fora do cálculo de retenção — e é justamente por
        # isso que o número precisa vir acompanhado da contagem. Sem ela, um conceito
        # com 2 cards frescos e 2 nunca vistos exibe "99%" e parece seguro.
        c["sem_historico"] = sem_historico
        c["proxima_revisao"] = proxima
        c["proxima_no_passado"] = bool(proxima and proxima < hoje_s)
    return {"cards_orfaos": orfaos, "total_cards_no_banco": len(linhas)}


# ── validação ──────────────────────────────────────────────────────────────


def validar(conceitos: list[dict], meta: dict) -> tuple[list[str], list[str]]:
    """Devolve (problemas, pendências).

    A distinção é o que mantém o comando útil: **problema** é o grafo quebrado — aresta
    para um id que não existe, conceito dominado sem nota, id duplicado. **Pendência** é
    dívida honesta e esperada, como nota que ainda é síntese do ledger. Se as duas
    saíssem na mesma lista, o `--validar` viveria vermelho logo depois de uma migração e
    ninguém olharia mais para ele — que é exactly como um lint deixa de ser usado.
    """
    ids = {c["id"] for c in conceitos}
    problemas: list[str] = []
    pendencias: list[str] = []

    vistos: dict[str, str] = {}
    for c in conceitos:
        if c["id"] in vistos:
            problemas.append(f"id duplicado '{c['id']}': {vistos[c['id']]} e {c['arquivo']}")
        vistos[c["id"]] = c["arquivo"]

    for c in conceitos:
        for campo in ("conecta_com", "prepara_para"):
            for aresta in c[campo]:
                if aresta["id"] not in ids:
                    problemas.append(
                        f"{c['arquivo']}: {campo} aponta para '{aresta['id']}', que não existe")
                if not aresta.get("porque"):
                    problemas.append(
                        f"{c['arquivo']}: aresta para '{aresta['id']}' sem 'porque' — "
                        "aresta sem motivo não ensina nada")
        if c["status"] == "dominado" and not c["nota"]:
            problemas.append(
                f"{c['arquivo']}: está 'dominado' mas a seção '{SECAO_NOTA}' está vazia — "
                "o nó dominado precisa da explicação do aluno")
        if c["status"] == "dominado" and not c["cards"]:
            problemas.append(f"{c['arquivo']}: 'dominado' sem nenhum card no srs.db — "
                             "conceito fechado que a repetição espaçada não está cobrindo")
        if c["status"] == "dominado" and c["nota_origem"] == "ledger":
            pendencias.append(
                f"{c['arquivo']}: nota ainda é síntese do ledger — trocar pela sua "
                "explicação no próximo portão deste conceito")
        if c["etapa"] == 0:
            problemas.append(f"{c['arquivo']}: sem 'etapa' — o nó não tem onde ser agrupado")

    for conceito_id, card_id in meta["cards_orfaos"]:
        problemas.append(f"{conceito_id}: card #{card_id} não existe no srs.db")
    return problemas, pendencias


# ── nota: markdown mínimo -> HTML ──────────────────────────────────────────


def nota_para_html(txt: str) -> str:
    """Converte o subconjunto de markdown que a nota usa. Escapa antes de formatar.

    Deliberadamente pequeno: negrito, código, itálico, lista e [[wikilink]]. Nota é
    parágrafo curto de explicação, não documento — um conversor completo aqui seria
    dependência nova para resolver problema que não existe.
    """
    if not txt:
        return ""
    saida, lista_aberta = [], False
    for linha in txt.splitlines():
        crua = linha.strip()
        if not crua:
            if lista_aberta:
                saida.append("</ul>")
                lista_aberta = False
            continue
        item = re.match(r"^[-*]\s+(.*)$", crua)
        conteudo = html.escape(item.group(1) if item else crua)
        conteudo = re.sub(r"\[\[([^\]|]+)\]\]",
                          r'<a href="#" data-ir-para="\1">\1</a>', conteudo)
        conteudo = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", conteudo)
        conteudo = re.sub(r"`(.+?)`", r"<code>\1</code>", conteudo)
        conteudo = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", conteudo)
        if item:
            if not lista_aberta:
                saida.append("<ul>")
                lista_aberta = True
            saida.append(f"<li>{conteudo}</li>")
        else:
            if lista_aberta:
                saida.append("</ul>")
                lista_aberta = False
            saida.append(f"<p>{conteudo}</p>")
    if lista_aberta:
        saida.append("</ul>")
    return "\n".join(saida)


# ── montagem do payload ────────────────────────────────────────────────────


def _arestas(conceitos: list[dict], ids: set[str]) -> list[dict]:
    """Normaliza tudo no sentido do fluxo de conhecimento: quem alimenta → quem recebe.

    O roadmap declara as duas pontas com semânticas OPOSTAS — `conecta_com` olha para
    trás (de que etapas anteriores este conceito depende) e `prepara_para` olha para
    frente (onde ele reaparece). Se as duas fossem guardadas como vêm, a seta do grafo
    apontaria para lados diferentes dependendo de qual arquivo declarou a ligação. Aqui
    `conecta_com: X` em C vira X→C, e `prepara_para: Y` em C vira C→Y.

    O mesmo par costuma ser declarado dos dois lados (A diz que prepara para B, B diz
    que conecta com A) — é a mesma relação vista de duas pontas, então vira UMA aresta.
    Em conflito de tipo fica `ponte`: atravessar etapas é a informação mais útil de ver.
    """
    por_par: dict[tuple[str, str], dict] = {}
    for c in conceitos:
        candidatas = (
            [(a["id"], c["id"], "dependencia", a.get("porque") or "") for a in c["conecta_com"]]
            + [(c["id"], a["id"], "ponte", a.get("porque") or "") for a in c["prepara_para"]]
        )
        for de, para, tipo, porque in candidatas:
            if de not in ids or para not in ids or de == para:
                continue
            chave = (de, para)
            atual = por_par.get(chave)
            if atual is None:
                por_par[chave] = {"de": de, "para": para, "tipo": tipo, "porque": porque}
                continue
            if tipo == "ponte":
                atual["tipo"] = "ponte"
            if len(porque) > len(atual["porque"]):
                atual["porque"] = porque
    return list(por_par.values())


def montar(conceitos: list[dict], materia: dict, meta: dict, hoje: date) -> dict:
    ids = {c["id"] for c in conceitos}
    nos = []
    for c in conceitos:
        nos.append({
            "id": c["id"], "nome": c["nome"], "etapa": c["etapa"], "status": c["status"],
            "dominado_em": c["dominado_em"], "pontoFraco": c["ponto_fraco"],
            "notaOrigem": c["nota_origem"],
            "nCards": c.get("n_cards", 0), "r": c.get("retrievability"),
            "vencidos": c.get("vencidos", 0), "proximaRevisao": c.get("proxima_revisao"),
            "proximaNoPassado": c.get("proxima_no_passado", False),
            "semHistorico": c.get("sem_historico", 0),
            "nota": nota_para_html(c["nota"]),
            "naoConfunda": nota_para_html(c["nao_confunda"]),
            "arquivo": c["arquivo"],
        })

    arestas = _arestas(conceitos, ids)
    dominados = sum(1 for c in conceitos if c["status"] == "dominado")
    return {
        "materia": materia["materia"],
        "etapaAtual": materia.get("etapa_atual"),
        "geradoEm": hoje.isoformat(),
        "resumo": {
            "total": len(conceitos), "dominados": dominados,
            "emAndamento": sum(1 for c in conceitos
                               if c["status"] in ("ensinando", "recall_feito")),
            "pontosFracos": sum(1 for c in conceitos if c["ponto_fraco"]),
            "vencidos": sum(c.get("vencidos", 0) for c in conceitos),
            "cardsNoBanco": meta["total_cards_no_banco"],
        },
        "nos": nos, "arestas": arestas,
    }


# ── HTML ───────────────────────────────────────────────────────────────────

TEMPLATE = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Grafo de conhecimento — __MATERIA__</title>
<style>
/* Tema escuro, mesma paleta dos outros artefatos de estudo. Cores de status vêm da
   paleta reservada (good/warning/serious) e SEMPRE andam com rótulo — a cor nunca
   carrega o significado sozinha. Contraste conferido contra #0d1520. */
:root{
  /* Superfícies e tinta NEUTRAS — sem viés de matiz. O azul dava ao painel um
     ar de "janela de aplicativo" que competia com o grafo; preto puxa o olho
     para o conteúdo. Para a variante clara, troque só estas 6 linhas:
     modal #f7f7f6 · line rgba(0,0,0,.12) · ink #101010 · ink-2 #3d3d3c ·
     ink-muted #6e6e6b · e o `color-scheme` abaixo para `light`. */
  --surface:#0d1116; --modal:#08090a; --line:rgba(255,255,255,.11);
  --ink:#ffffff; --ink-2:#d2d2d0; --ink-muted:#8e8e8b;
  --dominado:#2ecc71; --andamento:#fab219; --fraco:#ec835a; --futuro:#566573;
  --gold:#e8c87a;
  color-scheme:dark;
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%}
body{
  background:var(--surface); color:var(--ink); overflow:hidden;
  font:14px/1.5 "Helvetica Neue",Arial,"DejaVu Sans",sans-serif;
  -webkit-font-smoothing:antialiased;
}
#app{height:100%}
#palco{position:relative;height:100%}
canvas{display:block;width:100%;height:100%;cursor:grab}
canvas.arrastando{cursor:grabbing}

/* topo */
#topo{
  position:absolute;top:0;left:0;right:0;padding:14px 18px;
  display:flex;align-items:center;gap:18px;flex-wrap:wrap;
  background:linear-gradient(180deg,rgba(13,21,32,.94),rgba(13,21,32,0));
  pointer-events:none;
}
#topo h1{font-size:15px;font-weight:700;letter-spacing:.2px}
#topo h1 small{display:block;font-size:11px;font-weight:400;color:var(--ink-muted);letter-spacing:.4px}
.kpis{display:flex;gap:14px;font-size:11.5px;color:var(--ink-2)}
.kpis b{color:var(--ink);font-weight:700}
.legenda{display:flex;gap:12px;margin-left:auto;font-size:11px;color:var(--ink-2);flex-wrap:wrap}
.legenda i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:baseline}
#escala{color:var(--ink-muted)}
.controles{position:absolute;bottom:14px;left:18px;display:flex;gap:8px;flex-wrap:wrap}
.controles button{
  font:inherit;font-size:11.5px;color:var(--ink-2);cursor:pointer;
  background:rgba(255,255,255,.05);border:1px solid var(--line);
  border-radius:7px;padding:5px 10px;
}
.controles button[aria-pressed="true"]{color:var(--surface);background:var(--ink-2);border-color:var(--ink-2);font-weight:700}
.dica{position:absolute;bottom:14px;right:18px;font-size:10.5px;color:var(--ink-muted)}

/* tooltip da aresta / do nó */
#tip{
  position:absolute;pointer-events:none;max-width:280px;z-index:5;
  background:var(--modal);border:1px solid var(--line);border-radius:8px;
  padding:8px 10px;font-size:11.5px;color:var(--ink-2);
  box-shadow:0 8px 24px rgba(0,0,0,.5);opacity:0;transition:opacity .12s;
}
#tip b{color:var(--ink)}

/* Modal central. 40% da largura, com piso e teto: abaixo de ~430px a tabela de
   arestas quebra, acima de ~760px a linha fica longa demais para leitura. */
#veu{
  position:fixed;inset:0;z-index:20;display:none;
  align-items:center;justify-content:center;
  background:rgba(0,0,0,.62);backdrop-filter:blur(2px);
}
#veu.aberto{display:flex}
#painel{
  position:relative;   /* âncora do botão de fechar — sem isto ele vai para o véu */
  width:40vw;min-width:min(430px,92vw);max-width:760px;max-height:84vh;
  background:var(--modal);border:1px solid var(--line);border-radius:14px;
  box-shadow:0 24px 70px rgba(0,0,0,.65);
  display:flex;flex-direction:column;overflow:hidden;
}
.fechar{
  position:absolute;top:12px;right:14px;width:28px;height:28px;
  font:inherit;font-size:17px;line-height:1;color:var(--ink-muted);
  background:rgba(255,255,255,.06);border:1px solid var(--line);
  border-radius:8px;cursor:pointer;
}
.fechar:hover{color:var(--ink);background:rgba(255,255,255,.12)}

/* Gaveta da lista — o canvas ganhou a largura toda, então a lista passa a ser
   sob demanda em vez de ocupar 392px permanentes. */
#gaveta{
  position:absolute;top:0;right:0;bottom:0;width:330px;z-index:10;
  background:var(--modal);border-left:1px solid var(--line);
  display:none;flex-direction:column;
}
#gaveta.aberta{display:flex}
.pnl-topo{padding:18px 54px 14px 22px;border-bottom:1px solid var(--line);position:relative}
.pnl-topo .etapa{font-size:10.5px;letter-spacing:.9px;color:var(--ink-muted);font-weight:700}
.pnl-topo h2{font-size:21px;font-weight:700;margin-top:5px;line-height:1.25}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}
.chip{font-size:10px;font-weight:700;letter-spacing:.4px;padding:2px 7px;border-radius:9px;border:1px solid}
.chip.ok{color:var(--dominado);border-color:rgba(46,204,113,.45);background:rgba(46,204,113,.12)}
.chip.wip{color:var(--andamento);border-color:rgba(250,178,25,.45);background:rgba(250,178,25,.12)}
.chip.fut{color:var(--futuro);border-color:rgba(86,101,115,.5);background:rgba(86,101,115,.12)}
.chip.warn{color:var(--fraco);border-color:rgba(236,131,90,.45);background:rgba(236,131,90,.12)}
.pnl-corpo{padding:18px 22px;overflow-y:auto;flex:1}
.pnl-corpo h3{
  font-size:10.5px;letter-spacing:.9px;color:var(--gold);
  font-weight:700;margin:18px 0 7px;text-transform:uppercase;
}
.pnl-corpo h3:first-child{margin-top:0}
.pnl-corpo p{font-size:13.5px;color:var(--ink-2);margin-bottom:8px}
.pnl-corpo ul{margin:0 0 8px 16px}
.pnl-corpo li{font-size:12.5px;color:var(--ink-2);margin-bottom:4px}
.pnl-corpo code{background:rgba(255,255,255,.07);padding:1px 4px;border-radius:4px;font-size:12px}
.pnl-corpo a{color:var(--dominado);text-decoration:none;border-bottom:1px dotted}
.vazio{font-size:12.5px;color:var(--ink-muted);font-style:italic}
.aviso{
  font-size:11.5px;color:var(--ink-muted);border-left:2px solid var(--futuro);
  padding-left:9px;margin:9px 0 0;
}
.medidor{margin-top:6px}
.medidor .trilha{height:7px;border-radius:4px;background:#245a44;overflow:hidden}
.medidor .trilha i{display:block;height:100%;border-radius:4px;background:var(--dominado)}
.medidor .rot{display:flex;justify-content:space-between;font-size:10.5px;color:var(--ink-muted);margin-top:4px}
.arestas li{list-style:none;margin-bottom:9px;font-size:12.5px;color:var(--ink-2)}
.arestas li a{font-weight:700}
.arestas li span{display:block;color:var(--ink-muted);font-size:11.5px;margin-top:1px}
.meta{font-size:10.5px;color:var(--ink-muted);border-top:1px solid var(--line);padding:12px 22px}

/* lista de conceitos — a visão em tabela, e o jeito de achar um nó sem caçar no grafo */
#lista{padding:16px 18px;overflow-y:auto;flex:1}
#lista h3{font-size:10.5px;letter-spacing:.9px;color:var(--gold);font-weight:700;margin:16px 0 7px}
#lista h3:first-child{margin-top:0}
#lista button{
  display:block;width:100%;text-align:left;font:inherit;font-size:12.5px;
  background:none;border:0;color:var(--ink-2);cursor:pointer;
  padding:5px 7px;border-radius:6px;
}
#lista button:hover{background:rgba(255,255,255,.05);color:var(--ink)}
#lista button i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px}
#lista button em{font-style:normal;color:var(--ink-muted);font-size:11px;float:right}
.voltar{
  font:inherit;font-size:11.5px;color:var(--ink-muted);background:none;border:0;
  cursor:pointer;padding:0;margin-bottom:10px;
}
.voltar:hover{color:var(--ink)}
</style>
</head>
<body>
<div id="app">
  <div id="palco">
    <canvas id="c"></canvas>
    <div id="topo">
      <h1>__MATERIA__<small>GRAFO DE CONHECIMENTO &middot; GERADO EM __GERADO__</small></h1>
      <div class="kpis" id="kpis"></div>
      <div class="legenda">
        <span><i style="background:#2ecc71"></i>dominado</span>
        <span><i style="background:#fab219"></i>em andamento</span>
        <span><i style="background:#566573"></i>não iniciado</span>
        <span><i style="background:#ec835a"></i>ponto fraco</span>
        <span>— dependência</span>
        <span>&middot;&middot;&middot; ponte (reaparece adiante)</span>
        <span id="escala">anéis: etapa 1 no centro &rarr; etapa N na borda</span>
      </div>
    </div>
    <div class="controles">
      <button id="btPontes" aria-pressed="true">pontes</button>
      <button id="btFuturos" aria-pressed="true">nós futuros</button>
      <button id="btDesbota" aria-pressed="true">desbotar por esquecimento</button>
      <button id="btAnel" aria-pressed="false">anéis por etapa</button>
      <button id="btRecolocar">recolocar</button>
      <button id="btEnquadrar">enquadrar</button>
      <button id="btLista" aria-pressed="false">lista de conceitos</button>
    </div>
    <div class="dica" id="dica">arraste um nó para girar no anel &middot; arraste o fundo para deslocar &middot; roda dá zoom &middot; clique abre a anotação</div>
    <div id="tip"></div>
    <aside id="gaveta"></aside>
  </div>
  <div id="veu"><div id="painel" role="dialog" aria-modal="true" aria-label="Conceito"></div></div>
</div>

<script>
const DADOS = __DADOS__;
const CORES = {dominado:"#2ecc71", ensinando:"#fab219", recall_feito:"#fab219",
               nao_iniciado:"#566573", fraco:"#ec835a"};

/* ── estado ─────────────────────────────────────────────────────────────── */
const nos = DADOS.nos.map((n,i) => ({...n,
  x: 0, y: 0, vx: 0, vy: 0,
  raio: 9 + Math.min(5, (n.nCards||0)) * 1.6,
  _i: i,
}));
const porId = new Map(nos.map(n => [n.id, n]));
const arestas = DADOS.arestas
  .map(a => ({...a, a: porId.get(a.de), b: porId.get(a.para)}))
  .filter(a => a.a && a.b);

/* Força da repulsão no modo livre. Alta de propósito: o pedido é o espaçamento
   generoso do Obsidian, não um grafo compacto. */
const REPULSAO = 13000;
let opc = {pontes:true, futuros:true, desbota:true, anel:false};
let selecionado = null, hover = null, arrastando = null, pan = {x:0,y:0}, zoom = 1;
let t0 = performance.now();

/* ── layout: um anel por etapa ───────────────────────────────────────────
   A etapa é a dimensão que organiza a matéria, então ela organiza o desenho:
   fundação no centro, etapas seguintes em anéis para fora. Sem essa restrição a
   simulação embola tudo num novelo — as arestas ficam certas e o desenho fica
   ilegível, que é o pior dos dois mundos. O anel prende o RAIO e deixa o ÂNGULO
   livre, então as molas ainda aproximam quem se conecta. */
const ETAPAS = [...new Set(nos.map(n => n.etapa))].sort((p,q) => p-q);
let centro = {x:0, y:0}, larguraAnel = 100;

function medirAneis(){
  const cv = document.getElementById("c");
  centro = {x: cv.clientWidth/2, y: cv.clientHeight/2};
  larguraAnel = Math.min(centro.x, centro.y) * 0.92 / ETAPAS.length;
}
const raioDaEtapa = e => larguraAnel * (ETAPAS.indexOf(e) + 1);

function recolocar(){
  medirAneis();
  medirCaixas();
  if (!opc.anel){
    /* Espalhamento em filotaxia (ângulo de ouro): distribui de forma uniforme e
       determinística, sem os aglomerados que uma posição aleatória produz — a
       simulação começa de um estado já arejado em vez de ter que desentupir. */
    nos.forEach((n, i) => {
      const ang = i * 2.39996, r = 52 * Math.sqrt(i);
      n.x = centro.x + Math.cos(ang)*r;
      n.y = centro.y + Math.sin(ang)*r;
      n.vx = n.vy = 0;
    });
    t0 = performance.now();
    return;
  }
  ETAPAS.forEach(e => {
    const doGrupo = nos.filter(n => n.etapa === e);
    const raio = raioDaEtapa(e);
    doGrupo.forEach((n, k) => {
      n.ang = (k / doGrupo.length) * Math.PI*2 - Math.PI/2 + ETAPAS.indexOf(e)*0.7;
      n.vang = 0;
      aplicarAngulo(n, raio);
      n.vx = n.vy = 0;
    });
  });
  t0 = performance.now();
}
function aplicarAngulo(n, raio){
  const r = raio === undefined ? raioDaEtapa(n.etapa) : raio;
  n.x = centro.x + Math.cos(n.ang)*r;
  n.y = centro.y + Math.sin(n.ang)*r;
}
/** Diferença angular de a para b, normalizada em [-PI, PI] (caminho mais curto). */
function difAng(a, b){
  let d = (b - a) % (Math.PI*2);
  if (d >  Math.PI) d -= Math.PI*2;
  if (d < -Math.PI) d += Math.PI*2;
  return d;
}

/* ── simulação ────────────────────────────────────────────────────────────
   Dois modos, e o padrão é o LIVRE (force-directed, estilo Obsidian): nó não fica
   preso em órbita, e a vizinhança se organiza por quem se conecta com quem.

   O que faz o livre funcionar aqui é a colisão pela CAIXA DO RÓTULO. Repulsão
   calibrada pelo raio do círculo parece certa e entrega nomes se atropelando —
   porque num grafo de conceitos o que ocupa espaço é o texto, não a bolinha. Com a
   caixa medida e uma separação posicional, a sobreposição é resolvida no mesmo
   quadro em vez de depender de a simulação convergir.

   O modo ANEL fixa o raio na etapa e simula só o ângulo (uma variável por nó em vez
   de duas). Fica como opção porque responde a outra pergunta — a progressão da
   matéria, fundação no centro e etapas para fora — que o layout livre não mostra.

   O(n²) é de sobra nos dois para <300 nós. */
function passoAnel(){
  const vis = nos.filter(visivel);
  const SEP = 0.52;                    // separação angular mínima confortável

  for (let i=0;i<vis.length;i++){
    const a = vis[i];
    for (let j=i+1;j<vis.length;j++){
      const b = vis[j];
      const dr = Math.abs(raioDaEtapa(a.etapa) - raioDaEtapa(b.etapa));
      if (dr > larguraAnel*1.2) continue;             // anéis distantes não se atrapalham
      const g = difAng(a.ang, b.ang);
      const perto = SEP * (a.etapa === b.etapa ? 1 : 0.62);
      if (Math.abs(g) >= perto) continue;
      const f = (perto - Math.abs(g)) * 0.045 * Math.sign(g || 1);
      a.vang -= f; b.vang += f;
    }
  }
  for (const e of arestas){
    if (!arestaVisivel(e)) continue;
    const g = difAng(e.a.ang, e.b.ang);
    const k = e.tipo === "ponte" ? 0.010 : 0.020;   // ponte puxa mais frouxo
    e.a.vang += g*k; e.b.vang -= g*k;
  }
  for (const n of vis){
    if (n === arrastando){ n.vang = 0; aplicarAngulo(n); continue; }
    n.vang *= 0.80;
    n.ang += n.vang;
    aplicarAngulo(n);
  }
}

/* O que ocupa espaço num nó é o RÓTULO, não a bolinha. Repulsão calibrada só pelo
   raio do círculo deixa os nomes se atropelando — foi o que aconteceu. Então cada nó
   carrega a caixa medida do seu texto, e a separação é resolvida sobre a caixa. */
function medirCaixas(){
  ctx.font = '12.5px "Helvetica Neue",Arial,sans-serif';
  for (const n of nos){
    n.linhas = quebrar(n.nome, 17);
    const larguraTexto = Math.max(...n.linhas.map(l => ctx.measureText(l).width));
    n.meiaL = Math.max(n.raio, larguraTexto/2) + 9;                  // meia-largura
    n.meiaA = (n.raio + 5 + n.linhas.length*14) / 2 + 5;             // meia-altura
    n.centroY = n.raio + 5 + n.linhas.length*14;                     // caixa começa no topo
  }
}

/** Empurra pares cujas caixas se sobrepõem, pelo eixo de menor penetração.
 *  É posicional, não força: sobreposição some no mesmo quadro em vez de depender
 *  de a simulação convergir. É o que garante "nunca sobrepõe". */
function resolverColisoes(vis, passes){
  for (let p=0;p<passes;p++){
    let houve = false;
    for (let i=0;i<vis.length;i++){
      const a = vis[i];
      for (let j=i+1;j<vis.length;j++){
        const b = vis[j];
        const dx = b.x-a.x, dy = (b.y + b.meiaA) - (a.y + a.meiaA);
        const penX = (a.meiaL + b.meiaL) - Math.abs(dx);
        if (penX <= 0) continue;
        const penY = (a.meiaA + b.meiaA) - Math.abs(dy);
        if (penY <= 0) continue;
        houve = true;
        if (penX < penY){
          const s = (dx >= 0 ? 1 : -1) * penX/2;
          if (a !== arrastando) a.x -= s;
          if (b !== arrastando) b.x += s;
        } else {
          const s = (dy >= 0 ? 1 : -1) * penY/2;
          if (a !== arrastando) a.y -= s;
          if (b !== arrastando) b.y += s;
        }
      }
    }
    if (!houve) break;
  }
}

function passoLivre(){
  const vis = nos.filter(visivel);

  for (let i=0;i<vis.length;i++){
    const a = vis[i];
    for (let j=i+1;j<vis.length;j++){
      const b = vis[j];
      let dx = b.x-a.x, dy = b.y-a.y;
      let d2 = dx*dx + dy*dy;
      if (d2 < 1) { dx = (Math.random()-.5); dy = (Math.random()-.5); d2 = 1; }
      const d = Math.sqrt(d2);
      // Repulsão forte e com piso de distância: dá o "ar" do Obsidian em vez de
      // um novelo apertado. O piso evita força explosiva quando dois nós coincidem.
      const f = REPULSAO / Math.max(d2, 900);
      const fx = (dx/d)*f, fy = (dy/d)*f;
      a.vx -= fx; a.vy -= fy; b.vx += fx; b.vy += fy;
    }
  }
  for (const e of arestas){
    if (!arestaVisivel(e)) continue;
    const dx = e.b.x-e.a.x, dy = e.b.y-e.a.y;
    const d = Math.hypot(dx,dy) || 1;
    // O alvo da mola respeita as caixas dos dois nós, senão nome comprido puxa
    // vizinho para dentro do próprio texto.
    const folga = e.a.meiaL + e.b.meiaL;
    const alvo = (e.tipo === "ponte" ? 95 : 34) + folga;
    const f = (d-alvo) * 0.0055;
    const fx = (dx/d)*f, fy = (dy/d)*f;
    e.a.vx += fx; e.a.vy += fy; e.b.vx -= fx; e.b.vy -= fy;
  }
  for (const n of vis){
    n.vx += (centro.x-n.x)*0.0012; n.vy += (centro.y-n.y)*0.0012;   // centro, bem fraco
    if (n === arrastando) { n.vx = n.vy = 0; continue; }
    n.vx *= 0.88; n.vy *= 0.88;
    n.x += n.vx; n.y += n.vy;
  }
  resolverColisoes(vis, 3);
}

const passoFisico = () => opc.anel ? passoAnel() : passoLivre();

const visivel = n => opc.futuros || n.status !== "nao_iniciado";
const arestaVisivel = e => visivel(e.a) && visivel(e.b) &&
                           (opc.pontes || e.tipo !== "ponte");

/* Alpha do nó dominado = retrievability. É o que faz o grafo apagar junto com a
   memória, em vez de só acumular verde. */
function alphaDe(n){
  if (!opc.desbota || n.status !== "dominado" || n.r === null) return 1;
  return 0.34 + 0.66*Math.max(0, Math.min(1, n.r));
}
function corDe(n){ return CORES[n.status] || CORES.nao_iniciado; }

/* ── desenho ────────────────────────────────────────────────────────────── */
const cv = document.getElementById("c"), ctx = cv.getContext("2d");
function ajustar(){
  const r = window.devicePixelRatio || 1;
  cv.width = cv.clientWidth*r; cv.height = cv.clientHeight*r;
  ctx.setTransform(r,0,0,r,0,0);
}

function desenhar(){
  const agora = performance.now();
  ctx.clearRect(0,0,cv.clientWidth,cv.clientHeight);
  ctx.save(); ctx.translate(pan.x,pan.y); ctx.scale(zoom,zoom);

  /* Anéis ao fundo, sem rótulo no canvas de propósito: um "ETAPA N" por anel
     colide com os nomes dos nós justamente na região mais densa, e a lista
     lateral já agrupa por etapa. A escala fica explicada uma vez, no topo. */
  if (opc.anel) for (const e of ETAPAS){
    ctx.beginPath(); ctx.arc(centro.x,centro.y,raioDaEtapa(e),0,Math.PI*2);
    ctx.strokeStyle = "rgba(255,255,255,.085)"; ctx.lineWidth = 1; ctx.stroke();
  }

  for (const e of arestas){
    if (!arestaVisivel(e)) continue;
    const aceso = selecionado && (e.a.id===selecionado.id || e.b.id===selecionado.id);
    ctx.beginPath();
    ctx.setLineDash(e.tipo==="ponte" ? [3,5] : []);
    ctx.strokeStyle = aceso ? "rgba(232,200,122,.85)"
                            : (e.tipo==="ponte" ? "rgba(255,255,255,.16)" : "rgba(255,255,255,.26)");
    ctx.lineWidth = aceso ? 2 : 1;
    ctx.moveTo(e.a.x,e.a.y); ctx.lineTo(e.b.x,e.b.y); ctx.stroke();
  }
  ctx.setLineDash([]);

  for (const n of nos){
    if (!visivel(n)) continue;
    const cor = corDe(n), a = alphaDe(n);

    if (n.vencidos > 0){                      // vencido pulsa: revisão pedindo passagem
      const p = 0.5 + 0.5*Math.sin(agora/430);
      ctx.beginPath(); ctx.arc(n.x,n.y,n.raio+6+p*4,0,Math.PI*2);
      ctx.strokeStyle = `rgba(250,178,25,${0.16+0.30*p})`; ctx.lineWidth = 2; ctx.stroke();
    }
    if (n.pontoFraco){                        // anel de ponto fraco
      ctx.beginPath(); ctx.arc(n.x,n.y,n.raio+3.5,0,Math.PI*2);
      ctx.strokeStyle = CORES.fraco; ctx.lineWidth = 2; ctx.stroke();
    }
    const sel = selecionado && selecionado.id === n.id;
    if (sel || hover === n){
      ctx.beginPath(); ctx.arc(n.x,n.y,n.raio+(sel?8:5),0,Math.PI*2);
      ctx.fillStyle = "rgba(232,200,122,.16)"; ctx.fill();
    }
    ctx.globalAlpha = a;
    ctx.beginPath(); ctx.arc(n.x,n.y,n.raio,0,Math.PI*2);
    ctx.fillStyle = cor; ctx.fill();
    ctx.globalAlpha = 1;
    ctx.lineWidth = sel ? 2.5 : 1.2;
    ctx.strokeStyle = sel ? "#e8c87a" : "rgba(13,21,32,.85)";
    ctx.stroke();

    ctx.globalAlpha = Math.max(.45, a);
    ctx.fillStyle = "#e8edf2";
    ctx.font = `${sel||hover===n ? "700 " : ""}12.5px "Helvetica Neue",Arial,sans-serif`;
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    (n.linhas || quebrar(n.nome, 17)).forEach((ln,k) =>
      ctx.fillText(ln, n.x, n.y + n.raio + 5 + k*14));
    ctx.globalAlpha = 1;
  }
  ctx.restore();
}
function quebrar(txt, max){
  const out = []; let linha = "";
  for (const p of txt.split(" ")){
    if ((linha+" "+p).trim().length > max && linha){ out.push(linha); linha = p; }
    else linha = (linha+" "+p).trim();
  }
  if (linha) out.push(linha);
  return out.slice(0,3);
}

/** Ajusta zoom e deslocamento para o grafo inteiro caber na tela. Com espaçamento
 *  generoso o desenho passa da viewport, então enquadrar deixa de ser conveniência
 *  e vira parte do layout. */
function enquadrar(){
  const vis = nos.filter(visivel);
  if (!vis.length) return;
  let x0=Infinity, y0=Infinity, x1=-Infinity, y1=-Infinity;
  for (const n of vis){
    x0 = Math.min(x0, n.x - n.meiaL);          x1 = Math.max(x1, n.x + n.meiaL);
    y0 = Math.min(y0, n.y - n.raio - 6);       y1 = Math.max(y1, n.y + n.centroY + 6);
  }
  const margem = 46, topo = 112;               // topo reservado ao cabeçalho
  const larg = Math.max(1, cv.clientWidth - margem*2);
  const alt  = Math.max(1, cv.clientHeight - topo - margem);
  zoom = Math.max(0.8, Math.min(1.15, Math.min(larg/(x1-x0), alt/(y1-y0))));
  pan.x = margem + (larg - (x1-x0)*zoom)/2 - x0*zoom;
  pan.y = topo   + (alt  - (y1-y0)*zoom)/2 - y0*zoom;
}

/** Roda a simulação sem desenhar, para a primeira tela já aparecer assentada. */
function preAquecer(n){
  for (let i=0;i<n;i++) passoFisico();
  if (!opc.anel) resolverColisoes(nos.filter(visivel), 12);
  enquadrar();
}

let esfriou = false;
function laco(){
  if (performance.now() - t0 < 7000){ passoFisico(); esfriou = false; }
  else if (!esfriou){ esfriou = true; }
  desenhar();
  requestAnimationFrame(laco);
}

/* ── interação ──────────────────────────────────────────────────────────── */
function paraMundo(ev){
  const r = cv.getBoundingClientRect();
  return {x:(ev.clientX-r.left-pan.x)/zoom, y:(ev.clientY-r.top-pan.y)/zoom};
}
function noEm(p){
  for (const n of nos){
    if (!visivel(n)) continue;
    if (Math.hypot(n.x-p.x, n.y-p.y) <= n.raio+5) return n;
  }
  return null;
}
let arrastandoPan = null;
cv.addEventListener("mousedown", ev => {
  const p = paraMundo(ev), n = noEm(p);
  if (n){ arrastando = n; }
  else { arrastandoPan = {x:ev.clientX-pan.x, y:ev.clientY-pan.y}; }
  cv.classList.add("arrastando");
});
cv.addEventListener("mousemove", ev => {
  const p = paraMundo(ev);
  if (arrastando){
    if (opc.anel){
      arrastando.ang = Math.atan2(p.y-centro.y, p.x-centro.x);
      aplicarAngulo(arrastando);
    } else { arrastando.x = p.x; arrastando.y = p.y; }
    t0 = performance.now();
  }
  else if (arrastandoPan){ pan.x = ev.clientX-arrastandoPan.x; pan.y = ev.clientY-arrastandoPan.y; }
  else {
    const n = noEm(p);
    if (n !== hover){ hover = n; mostrarTip(n, ev); }
    else if (n) posicionarTip(ev);
  }
});
window.addEventListener("mouseup", () => {
  arrastando = null; arrastandoPan = null; cv.classList.remove("arrastando");
});
cv.addEventListener("click", ev => {
  const n = noEm(paraMundo(ev));
  if (n) abrir(n.id); else selecionado = null;
});
cv.addEventListener("wheel", ev => {
  ev.preventDefault();
  const f = ev.deltaY < 0 ? 1.1 : 0.9;
  zoom = Math.max(0.35, Math.min(2.6, zoom*f));
}, {passive:false});

const tip = document.getElementById("tip");
function posicionarTip(ev){
  const r = cv.getBoundingClientRect();
  tip.style.left = (ev.clientX-r.left+14)+"px";
  tip.style.top  = (ev.clientY-r.top+14)+"px";
}
function mostrarTip(n, ev){
  if (!n){ tip.style.opacity = 0; return; }
  const partes = [`<b>${n.nome}</b>`, `etapa ${n.etapa} &middot; ${rotulo(n.status)}`];
  if (n.nCards) partes.push(`${n.nCards} card(s)` +
      (n.r !== null ? ` &middot; ${Math.round(n.r*100)}% de retenção estimada` : ""));
  if (n.vencidos) partes.push(`<b>${n.vencidos} card(s) vencido(s)</b>`);
  tip.innerHTML = partes.join("<br>");
  tip.style.opacity = 1; posicionarTip(ev);
}
const rotulo = s => ({dominado:"dominado", ensinando:"em andamento",
                      recall_feito:"recall feito", nao_iniciado:"não iniciado"}[s] || s);

/* ── painel ─────────────────────────────────────────────────────────────── */
const painel = document.getElementById("painel");
const veu = document.getElementById("veu");
const gaveta = document.getElementById("gaveta");
function abrir(id){
  const n = porId.get(id);
  if (!n) return;
  selecionado = n;
  const cls = n.status === "dominado" ? "ok" : (n.status === "nao_iniciado" ? "fut" : "wip");
  const entram = arestas.filter(e => e.para === id);
  const saem   = arestas.filter(e => e.de === id);

  const medidor = (n.r !== null) ? `
    <h3>Retenção estimada agora</h3>
    <div class="medidor">
      <div class="trilha"><i style="width:${Math.round(n.r*100)}%"></i></div>
      <div class="rot"><span>${Math.round(n.r*100)}% de chance de lembrar hoje</span>
      <span>${n.proximaRevisao
        ? (n.proximaNoPassado ? "vencido desde "+n.proximaRevisao : "próx. "+n.proximaRevisao)
        : ""}</span></div>
      ${n.semHistorico ? `<p class="aviso">${n.semHistorico} card(s) deste conceito nunca
        foram revisados — ficam de fora da conta, porque não existe curva de esquecimento
        antes da primeira recuperação. A porcentagem cobre só os ${n.nCards - n.semHistorico}
        que já passaram por recall.</p>` : ""}
    </div>` : "";

  veu.classList.add("aberto");
  painel.innerHTML = `
    <button class="fechar" onclick="fechar()" aria-label="Fechar">&times;</button>
    <div class="pnl-topo">
      <div class="etapa">ETAPA ${n.etapa}</div>
      <h2>${n.nome}</h2>
      <div class="chips">
        <span class="chip ${cls}">${rotulo(n.status).toUpperCase()}</span>
        ${n.pontoFraco ? '<span class="chip warn">&#9888; PONTO FRACO</span>' : ""}
        ${n.vencidos ? `<span class="chip wip">${n.vencidos} VENCIDO(S)</span>` : ""}
        ${n.nota && n.notaOrigem === "ledger" ? '<span class="chip fut">SÍNTESE PROVISÓRIA</span>' : ""}
      </div>
    </div>
    <div class="pnl-corpo">
      <h3>${n.notaOrigem === "aluno" && n.nota ? "O que é &mdash; nas suas palavras" : "O que é"}</h3>
      ${n.nota || '<p class="vazio">Sem anotação ainda. Ela é gravada quando você explica o conceito no portão N4 e a explicação passa pela conferência na fonte.</p>'}
      ${n.nota && n.notaOrigem === "ledger" ? '<p class="aviso">Este texto é uma síntese do ledger, não a sua explicação. Ele sai daqui no próximo portão deste conceito — reler resumo alheio não tem o valor de recuperação de reler o que você mesmo produziu.</p>' : ""}
      ${n.naoConfunda ? "<h3>Não confunda com</h3>"+n.naoConfunda : ""}
      ${medidor}
      ${saem.length ? "<h3>Sustenta / reaparece em</h3><ul class='arestas'>"+saem.map(e =>
        `<li><a href="#" data-ir-para="${e.para}">${porId.get(e.para).nome}</a>
         ${e.tipo==="ponte" ? " &middot;&middot;&middot; ponte" : ""}
         <span>${e.porque}</span></li>`).join("")+"</ul>" : ""}
      ${entram.length ? "<h3>Depende de / vem de</h3><ul class='arestas'>"+entram.map(e =>
        `<li><a href="#" data-ir-para="${e.de}">${porId.get(e.de).nome}</a>
         <span>${e.porque}</span></li>`).join("")+"</ul>" : ""}
    </div>
    <div class="meta">${n.nCards} card(s) no SRS
      ${n.dominado_em ? " &middot; dominado em "+n.dominado_em : ""}
      &middot; <code>${n.arquivo}</code></div>`;
  ligarLinks();
}
function fechar(){
  veu.classList.remove("aberto");
  selecionado = null;
  renderLista();
}
window.fechar = fechar;

/* Fecha pelo véu e pelo Esc — modal que só fecha no X irrita. O clique é filtrado
   pelo próprio véu para não fechar quando o alvo está dentro do painel. */
veu.addEventListener("click", ev => { if (ev.target === veu) fechar(); });
window.addEventListener("keydown", ev => {
  if (ev.key !== "Escape") return;
  if (veu.classList.contains("aberto")) fechar();
  else if (gaveta.classList.contains("aberta")) alternarLista(false);
});

function alternarLista(mostrar){
  const b = document.getElementById("btLista");
  const abrir_ = mostrar === undefined ? !gaveta.classList.contains("aberta") : mostrar;
  gaveta.classList.toggle("aberta", abrir_);
  b.setAttribute("aria-pressed", String(abrir_));
}

function renderLista(){
  const porEtapa = new Map();
  for (const n of nos){
    if (!porEtapa.has(n.etapa)) porEtapa.set(n.etapa, []);
    porEtapa.get(n.etapa).push(n);
  }
  const blocos = [...porEtapa.keys()].sort((a,b)=>a-b).map(e => {
    const itens = porEtapa.get(e).map(n => `
      <button data-ir-para="${n.id}">
        <i style="background:${corDe(n)};opacity:${alphaDe(n).toFixed(2)}"></i>${n.nome}
        <em>${n.vencidos ? n.vencidos+" venc." : (n.r!==null ? Math.round(n.r*100)+"%" : "")}</em>
      </button>`).join("");
    return `<h3>ETAPA ${e}</h3>${itens}`;
  }).join("");
  gaveta.innerHTML = `<div id="lista">${blocos ||
    '<p class="vazio">Nenhum conceito ainda.</p>'}</div>
    <div class="meta">A visão em tabela do grafo — dá para achar um conceito sem
    caçar no desenho.</div>`;
  ligarLinks(gaveta);
}
function ligarLinks(escopo){
  (escopo || painel).querySelectorAll("[data-ir-para]").forEach(el => {
    el.addEventListener("click", ev => {
      ev.preventDefault(); abrir(el.getAttribute("data-ir-para"));
    });
  });
}

/* ── controles e KPIs ───────────────────────────────────────────────────── */
const r = DADOS.resumo;
document.getElementById("kpis").innerHTML = `
  <span><b>${r.dominados}</b>/${r.total} dominados</span>
  <span><b>${r.emAndamento}</b> em andamento</span>
  <span><b>${r.pontosFracos}</b> pontos fracos</span>
  <span><b>${r.vencidos}</b> cards vencidos</span>`;

/* As dicas descrevem o modo ativo. Antes eram fixadas no HTML com o texto do modo
   anel, então abriam mentindo — o padrão passou a ser o livre. */
function atualizarDicas(){
  document.getElementById("escala").style.visibility = opc.anel ? "visible" : "hidden";
  document.getElementById("dica").textContent = opc.anel
    ? "arraste um nó para girar no anel · arraste o fundo para deslocar · roda dá zoom · clique abre a anotação"
    : "arraste qualquer nó · arraste o fundo para deslocar · roda dá zoom · clique abre a anotação";
}

function alternar(idBotao, chave){
  const b = document.getElementById(idBotao);
  b.addEventListener("click", () => {
    opc[chave] = !opc[chave];
    b.setAttribute("aria-pressed", String(opc[chave]));
    t0 = performance.now();
    if (!selecionado) renderLista();
  });
}
alternar("btPontes","pontes"); alternar("btFuturos","futuros"); alternar("btDesbota","desbota");
alternar("btAnel","anel");
document.getElementById("btAnel").addEventListener("click", () => {
  atualizarDicas();
  recolocar();
  preAquecer(opc.anel ? 200 : 300);
});
document.getElementById("btRecolocar").addEventListener("click", () => {
  recolocar(); preAquecer(260);
});
document.getElementById("btEnquadrar").addEventListener("click", enquadrar);
document.getElementById("btLista").addEventListener("click", () => alternarLista());

window.addEventListener("resize", () => { ajustar(); medirCaixas(); enquadrar(); });
ajustar(); medirAneis(); atualizarDicas(); recolocar(); preAquecer(300); renderLista(); laco();
</script>
</body>
</html>
"""


def gerar_html(payload: dict) -> str:
    return (TEMPLATE
            .replace("__MATERIA__", html.escape(payload["materia"]))
            .replace("__GERADO__", payload["geradoEm"])
            .replace("__DADOS__", json.dumps(payload, ensure_ascii=False)))


# ── CLI ────────────────────────────────────────────────────────────────────


def _resolver_materia(slug: str | None) -> tuple[dict, str] | None:
    if slug:
        p = ws.PROGRESSO / f"{slug}.md"
        if not p.exists():
            mnemo.fail(f"não achei o ledger {p.name} em estudo/progresso/.")
            return None
        fm = ws.frontmatter(p)
        return {"materia": ws.campo(fm, "materia") or slug,
                "etapa_atual": None}, slug
    m = ws.materia_ativa()
    if not m:
        mnemo.fail("nenhuma matéria no workspace ainda — comece uma pelo COOKBOOK.md Parte B.")
        return None
    return m, m["arquivo"].stem


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Grafo de conhecimento navegável, montado dos conceitos + do srs.db.")
    ap.add_argument("--materia", help="slug do ledger (padrão: a matéria ativa)")
    ap.add_argument("--validar", action="store_true", help="só checa integridade")
    ap.add_argument("--json", action="store_true", help="despeja o payload resolvido")
    args = ap.parse_args()

    alvo = _resolver_materia(args.materia)
    if alvo is None:
        return 2
    materia, slug = alvo

    pasta = ws.PROGRESSO / f"{slug}-conceitos"
    conceitos = carregar_conceitos(pasta)
    if not conceitos:
        mnemo.fail(f"nenhum conceito em {pasta.relative_to(ws.WS)}/. "
                   "Copie templates/conceito.md para lá (um arquivo por conceito).")
        return 2

    hoje = date.today()
    meta = anexar_srs(conceitos, hoje)
    problemas, pendencias = validar(conceitos, meta)

    if args.validar:
        if problemas:
            mnemo.fail(f"{len(problemas)} problema(s) no grafo de {materia['materia']}:")
            for p in problemas:
                print(f"    · {p}")
        else:
            mnemo.ok(f"{len(conceitos)} conceito(s) — estrutura íntegra.")
        if pendencias:
            print()
            mnemo.warn(f"{len(pendencias)} pendência(s) — dívida esperada, não erro:")
            for p in pendencias:
                print(f"    · {p}")
        return 1 if problemas else 0

    payload = montar(conceitos, materia, meta, hoje)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    saida = ws.PROGRESSO / f"{slug}-grafo.html"
    saida.write_text(gerar_html(payload), encoding="utf-8")

    r = payload["resumo"]
    mnemo.ok(f"{saida.relative_to(ws.WS)} — {r['dominados']}/{r['total']} dominados · "
             f"{len(payload['arestas'])} conexões · {r['vencidos']} card(s) vencido(s)")
    if problemas:
        mnemo.fail(f"{len(problemas)} problema(s) estrutural(is) — rode --validar.")
    elif pendencias:
        mnemo.warn(f"{len(pendencias)} nota(s) ainda são síntese do ledger — rode --validar.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print()
        raise SystemExit(130)
