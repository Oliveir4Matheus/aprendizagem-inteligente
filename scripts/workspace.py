#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workspace.py — leitura do estado do workspace, compartilhada pelos scripts.

Não é executável: é o módulo que status.py e sessao.py usam para achar a matéria
ativa, ler o frontmatter do ledger e abrir o banco. Só biblioteca padrão.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import date, datetime
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
ESTUDO = WS / "estudo"
PROGRESSO = ESTUDO / "progresso"
PERFIL = ESTUDO / "PERFIL.md"
DB = PROGRESSO / "srs.db"
SCHEMA = WS / "templates" / "srs_schema.sql"

# Gatilhos do modo reentrada e do escalonamento da Fase 2 (ver METODOS_DE_ENSINO.md / SKILL.md)
REENTRADA_DIAS = 10
REENTRADA_BACKLOG = 15
REENTRADA_TETO = 8
FASE2_LEMBRAR = 3     # dias: a partir daqui a sessão COMEÇA pela Fase 2 pendente
FASE2_EXPIRA = 7      # dias: a partir daqui assume-se que o consumo não vai acontecer


# ── banco ──────────────────────────────────────────────────────────────────


#: Colunas acrescentadas ao review_log depois da versão inicial do esquema.
#: `CREATE TABLE IF NOT EXISTS` não altera tabela existente, então elas precisam
#: de ALTER explícito — é isto que migra o banco de quem já usava o sistema.
COLUNAS_NOVAS = {
    "review_log": {
        "confianca": "INTEGER",
        "tentativas": "INTEGER",
        "usou_dica": "INTEGER",
        "tipo_item": "TEXT",
    },
}


def _migrar(con: sqlite3.Connection) -> list[str]:
    aplicadas = []
    for tabela, colunas in COLUNAS_NOVAS.items():
        existe = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela,)
        ).fetchone()
        if not existe:
            continue
        atuais = {r["name"] for r in con.execute(f"PRAGMA table_info({tabela})")}
        for coluna, tipo in colunas.items():
            if coluna not in atuais:
                con.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
                aplicadas.append(f"{tabela}.{coluna}")
    if aplicadas:
        con.commit()
    return aplicadas


def abrir_db(criar: bool = True) -> sqlite3.Connection:
    """Abre o srs.db aplicando o esquema e as migrações de forma idempotente.

    Quem já usava o sistema ganha as tabelas e colunas novas sem fazer nada.
    """
    if not DB.exists() and not criar:
        raise FileNotFoundError(f"banco não encontrado: {DB}")
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    if SCHEMA.exists():
        con.executescript(SCHEMA.read_text(encoding="utf-8"))
        con.commit()
    _migrar(con)
    return con


# ── calibração e composição do recall ──────────────────────────────────────

#: Probabilidade que cada resposta de confiança declara implicitamente.
#: Usada para medir o desencontro entre o que o aluno previu e o que aconteceu.
CONFIANCA = {0: ("não vou acertar", 0.20), 1: ("mais ou menos", 0.50), 2: ("vou acertar", 0.85)}

#: Composição do recall a partir da etapa 3 (antes disso não há material anterior
#: suficiente para intercalar). Somam o mínimo de perguntas definido no PERFIL.
COTAS = {"recall": 3, "intercalado": 2, "sintese": 1, "transferencia": 1}
COTAS_INICIAIS = {"recall": 5, "transferencia": 2}
PORTAO_MIN_N4 = 2   # itens em formato N4, sem dica, para marcar a etapa como dominada


def fila_intercalada(cards: list) -> list:
    """Reordena a fila para alternar tópicos em vez de agrupá-los.

    Mesma quantidade de trabalho, distribuída de forma a forçar discriminação:
    o aluno precisa decidir QUAL conceito se aplica, em vez de responder no piloto
    automático porque só existe um em jogo.
    """
    grupos: dict[str, list] = {}
    for c in cards:
        chave = (c["deck"] if isinstance(c, sqlite3.Row) else c.get("deck")) or "—"
        grupos.setdefault(chave, []).append(c)
    # maiores grupos primeiro, para que o rodízio não termine com um bloco só
    ordem = sorted(grupos.values(), key=len, reverse=True)
    saida = []
    while any(ordem):
        for g in ordem:
            if g:
                saida.append(g.pop(0))
    return saida


# ── frontmatter ────────────────────────────────────────────────────────────


def frontmatter(caminho: Path) -> str:
    """Devolve o bloco entre os dois `---` do topo, ou string vazia."""
    if not caminho.exists():
        return ""
    txt = caminho.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*$", txt, re.S | re.M)
    return m.group(1) if m else ""


def campo(bloco: str, chave: str, sob: str | None = None) -> str | None:
    """Lê `chave: valor` do frontmatter. Com `sob`, lê a chave indentada abaixo dela.

    Deliberadamente estreito: não é um parser de YAML, é uma extração dos poucos
    campos que os scripts precisam. Frontmatter malformado devolve None em vez de
    explodir — o agente ainda consegue trabalhar sem o script.
    """
    if sob:
        m = re.search(rf"^{re.escape(sob)}:\s*$\n((?:[ \t]+.*\n?)*)", bloco, re.M)
        if not m:
            return None
        bloco = m.group(1)
    m = re.search(rf"^[ \t]*{re.escape(chave)}:[ \t]*(.*)$", bloco, re.M)
    if not m:
        return None
    v = m.group(1).strip().strip('"').strip("'")
    if v.startswith("#") or not v:
        return None
    return v.split("#")[0].strip() or None


def topicos(bloco: str) -> list[tuple[str, str]]:
    """[(nome, status)] a partir da lista `topicos:` do ledger."""
    m = re.search(r"^topicos:\s*$\n((?:[ \t]+.*\n?)*)", bloco, re.M)
    if not m:
        return []
    saida, nome = [], None
    for linha in m.group(1).splitlines():
        n = re.match(r"^\s*-\s*nome:\s*(.+?)\s*$", linha)
        if n:
            if nome:
                saida.append((nome, "nao_iniciado"))
            nome = n.group(1).strip().strip('"')
            continue
        s = re.match(r"^\s+status:\s*(\w+)", linha)
        if s and nome:
            saida.append((nome, s.group(1)))
            nome = None
    if nome:
        saida.append((nome, "nao_iniciado"))
    return saida


# ── matéria ativa ──────────────────────────────────────────────────────────


def ledgers() -> list[Path]:
    if not PROGRESSO.is_dir():
        return []
    return [
        p for p in sorted(PROGRESSO.glob("*.md"))
        if not p.name.startswith("_") and not p.name.endswith("-roadmap.md")
    ]


def materia_ativa() -> dict | None:
    """O ledger com o `atualizado:` mais recente. None se não há matéria."""
    melhor, melhor_data = None, ""
    for p in ledgers():
        fm = frontmatter(p)
        d = campo(fm, "atualizado") or ""
        if d >= melhor_data:
            melhor, melhor_data = p, d
    if melhor is None:
        return None
    fm = frontmatter(melhor)
    tops = topicos(fm)
    return {
        "arquivo": melhor,
        "materia": campo(fm, "materia") or melhor.stem,
        "atualizado": campo(fm, "atualizado"),
        "ultima_sessao": campo(fm, "ultima_sessao") or campo(fm, "atualizado"),
        "fase2_iniciada_em": campo(fm, "fase2_iniciada_em"),
        "rigor": campo(fm, "rigor"),
        "roadmap": campo(fm, "roadmap"),
        "retomar_topico": campo(fm, "topico", sob="retomar_em"),
        "proxima_acao": campo(fm, "proxima_acao", sob="retomar_em"),
        "topicos": tops,
        "dominados": sum(1 for _, s in tops if s == "dominado"),
        "total_topicos": len(tops),
    }


# ── perfil ─────────────────────────────────────────────────────────────────


def perfil_campo(rotulo: str) -> str | None:
    """Lê `- **Rótulo:** valor` do PERFIL.md."""
    if not PERFIL.exists():
        return None
    m = re.search(
        rf"^\s*-\s*\*\*{re.escape(rotulo)}:?\*\*\s*(.+?)\s*$",
        PERFIL.read_text(encoding="utf-8"), re.M | re.I,
    )
    if not m:
        return None
    v = m.group(1).strip()
    return None if v.startswith("_(") else v


def num_do_perfil(rotulo: str, padrao: int) -> int:
    v = perfil_campo(rotulo) or ""
    m = re.search(r"(\d+)", v)
    return int(m.group(1)) if m else padrao


def ritmo() -> dict:
    """Configuração de blocos de foco, toda vinda do PERFIL.md.

    Nada aqui é fixo: 25/5 é só o padrão clássico. Bloco longo (50 ou 90) serve
    melhor para quem entra em profundidade; bloco curto, para quem está voltando
    de uma ausência ou tem janelas picadas.
    """
    return {
        "bloco_min": num_do_perfil("Bloco de foco", 25),
        "pausa_min": num_do_perfil("Pausa curta", 5),
        "pausa_longa_min": num_do_perfil("Pausa longa", 15),
        "blocos_ate_pausa_longa": num_do_perfil("Blocos até a pausa longa", 4),
        "blocos_alvo": num_do_perfil("Blocos por sessão", 2),
    }


def nivel_rigor() -> int:
    v = perfil_campo("Nível de rigor") or ""
    m = re.search(r"[1-4]", v)
    return int(m.group(0)) if m else 3


# ── datas ──────────────────────────────────────────────────────────────────


def dias_desde(iso: str | None) -> int | None:
    if not iso:
        return None
    try:
        d = datetime.fromisoformat(iso).date()
    except ValueError:
        try:
            d = date.fromisoformat(iso[:10])
        except ValueError:
            return None
    return (date.today() - d).days


def plural(n: int, um: str, muitos: str) -> str:
    return f"{n} {um if n == 1 else muitos}"
