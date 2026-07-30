#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_grafo.py — cobre o parser dos arquivos de conceito, a normalização das arestas
e a integridade do HTML gerado.

    python3 scripts/test_grafo.py

Roda contra uma pasta temporária de conceitos e um banco temporário; nunca toca em
estudo/. Só biblioteca padrão.

Dois testes aqui existem por causa de bugs reais que já aconteceram neste arquivo:

· `teste_js_sem_erro_de_sintaxe` — o grafo é montado por um template de JS dentro de
  uma string Python. Um erro de sintaxe ali produz uma **página em branco**, não uma
  exceção: o Python roda felizes, escreve o HTML, e o navegador engole o erro no
  console. Já aconteceu com uma colisão de nome (`passoAnel` como variável e como
  função). Inspeção visual pega isso tarde; `node --check` pega na hora. Se o node
  não existir na máquina, o teste é PULADO, não falha — o node é conveniência de
  desenvolvimento, não dependência do projeto.

· `teste_direcao_das_arestas` — as duas pontas da ligação são declaradas com
  semânticas opostas (`conecta_com` olha para trás, `prepara_para` para frente). Se a
  normalização inverter, a seta do grafo passa a ensinar a dependência ao contrário.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import workspace as ws  # noqa: E402

_TMP = tempfile.TemporaryDirectory()
RAIZ = Path(_TMP.name)
ws.DB = RAIZ / "srs_test.db"
ws.PROGRESSO = RAIZ / "progresso"
ws.PROGRESSO.mkdir(parents=True, exist_ok=True)

import grafo  # noqa: E402  (depois de redirecionar os caminhos)
import revisar  # noqa: E402

HOJE = date(2026, 7, 29)
CONCEITOS = ws.PROGRESSO / "materia-teste-conceitos"
falhas: list[str] = []


def checa(condicao: bool, descricao: str) -> None:
    print(f"  {'ok  ' if condicao else 'FALHA'} {descricao}")
    if not condicao:
        falhas.append(descricao)


def pula(descricao: str) -> None:
    print(f"  pulado {descricao}")


def escrever(nome: str, corpo: str) -> None:
    CONCEITOS.mkdir(parents=True, exist_ok=True)
    (CONCEITOS / nome).write_text(corpo, encoding="utf-8")


def cenario() -> list[dict]:
    """Dois conceitos ligados, um dominado com card e um futuro."""
    if CONCEITOS.exists():
        shutil.rmtree(CONCEITOS)
    escrever("base.md", """---
id: base
nome: Conceito Base
etapa: 1
status: dominado          # comentário à direita deve ser ignorado
dominado_em: 2026-07-20
ponto_fraco: true
cards: [1, 2]
nota_origem: aluno
conecta_com: []
prepara_para:
  - id: futuro
    etapa: 3
    porque: é onde a base reaparece com outro nome
---

## O que é

A explicação, com **negrito**, `código` e um link para [[futuro]].

- item de lista

## Não confunda com

- **A** × **B** — o critério que separa.
""")
    escrever("futuro.md", """---
id: futuro
nome: Conceito Futuro
etapa: 3
status: nao_iniciado
dominado_em:
ponto_fraco: false
cards: []
nota_origem: aluno
conecta_com:
  - id: base
    porque: depende da base para fazer sentido
prepara_para: []
---

## O que é

_(ainda não ensinado — placeholder do template)_
""")
    return grafo.carregar_conceitos(CONCEITOS)


def semear_banco() -> None:
    con = ws.abrir_db()
    con.execute("DELETE FROM cards")
    ontem = (HOJE - timedelta(days=1)).isoformat()
    con.execute("INSERT INTO cards(id, front, back, due_date, created_at, state, "
                "difficulty, stability, last_review) VALUES(1,'f1','b1',?,?,2,5.0,10.0,?)",
                (ontem, ontem, (HOJE - timedelta(days=3)).isoformat()))
    con.execute("INSERT INTO cards(id, front, back, due_date, created_at) "
                "VALUES(2,'f2','b2',?,?)", (ontem, ontem))   # nunca revisado
    con.commit()
    con.close()


# ── parser ───────────────────────────────────────────────────────────────────


def teste_parse_escalares():
    cs = {c["id"]: c for c in cenario()}
    b = cs["base"]
    checa(b["nome"] == "Conceito Base", "lê `nome`")
    checa(b["etapa"] == 1, "lê `etapa` como int")
    checa(b["status"] == "dominado", "comentário à direita não entra no valor")
    checa(b["ponto_fraco"] is True, "lê booleano true")
    checa(cs["futuro"]["ponto_fraco"] is False, "lê booleano false")
    checa(b["cards"] == [1, 2], "lê lista inline de ints")
    checa(cs["futuro"]["cards"] == [], "lista vazia `[]` vira []")
    checa(cs["futuro"]["dominado_em"] is None, "campo vazio vira None")


def teste_parse_listas_de_objetos():
    cs = {c["id"]: c for c in cenario()}
    p = cs["base"]["prepara_para"]
    checa(len(p) == 1 and p[0]["id"] == "futuro", "lê item de lista com `- id:`")
    checa(p[0]["etapa"] == 3, "lê campo extra do item")
    checa("reaparece" in (p[0]["porque"] or ""), "lê o `porque` inteiro")
    checa(cs["base"]["conecta_com"] == [], "`conecta_com: []` vira lista vazia")


def teste_placeholder_nao_conta_como_nota():
    cs = {c["id"]: c for c in cenario()}
    checa(cs["futuro"]["nota"] == "", "texto `_(...)_` do template não vira nota")
    checa(cs["base"]["nota"] != "", "nota de verdade é lida")
    checa("Não confunda" not in cs["base"]["nota"],
          "a seção seguinte não vaza para dentro da nota")


def teste_status_invalido_degrada():
    cenario()
    escrever("torto.md", "---\nid: torto\nnome: Torto\netapa: 2\nstatus: inventado\n---\n")
    cs = {c["id"]: c for c in grafo.carregar_conceitos(CONCEITOS)}
    checa(cs["torto"]["status"] == "nao_iniciado",
          "status inválido cai para nao_iniciado em vez de explodir")


def teste_arquivo_sem_frontmatter_nao_explode():
    cenario()
    escrever("cru.md", "só texto, sem frontmatter nenhum\n")
    try:
        cs = {c["id"]: c for c in grafo.carregar_conceitos(CONCEITOS)}
        checa(cs["cru"]["nome"] == "cru", "arquivo sem frontmatter cai no nome do arquivo")
    except Exception as e:
        checa(False, f"arquivo sem frontmatter explodiu: {e}")


# ── arestas ──────────────────────────────────────────────────────────────────


def teste_direcao_das_arestas():
    """Regressão: `conecta_com` olha para TRÁS, `prepara_para` para FRENTE."""
    conceitos = cenario()
    arestas = grafo._arestas(conceitos, {c["id"] for c in conceitos})
    checa(len(arestas) == 1,
          f"as duas pontas da mesma ligação viram UMA aresta (achou {len(arestas)})")
    a = arestas[0]
    checa(a["de"] == "base" and a["para"] == "futuro",
          "aresta aponta base → futuro (sentido do fluxo de conhecimento)")
    checa(a["tipo"] == "ponte", "em conflito de tipo, fica ponte")
    checa(bool(a["porque"]), "a aresta carrega o porquê")


def teste_aresta_orfa_nao_entra():
    cenario()
    escrever("solto.md", "---\nid: solto\nnome: Solto\netapa: 1\nstatus: nao_iniciado\n"
                         "conecta_com:\n  - id: nao-existe\n    porque: x\n---\n")
    conceitos = grafo.carregar_conceitos(CONCEITOS)
    arestas = grafo._arestas(conceitos, {c["id"] for c in conceitos})
    checa(all("nao-existe" not in (a["de"], a["para"]) for a in arestas),
          "aresta para id inexistente não entra no grafo")
    problemas, _ = grafo.validar(conceitos, {"cards_orfaos": []})
    checa(any("nao-existe" in p for p in problemas), "e é reportada como problema")


# ── SRS ──────────────────────────────────────────────────────────────────────


def teste_retrievability_do_elo_mais_fraco():
    conceitos = cenario()
    semear_banco()
    grafo.anexar_srs(conceitos, HOJE)
    base = next(c for c in conceitos if c["id"] == "base")
    checa(base["n_cards"] == 2, "conta os cards que existem no banco")
    checa(base["sem_historico"] == 1, "conta separado o card nunca revisado")
    r_esperado = revisar.retrievability(10.0, (HOJE - timedelta(days=3)).isoformat(), HOJE)
    checa(abs(base["retrievability"] - round(r_esperado, 4)) < 1e-6,
          "retenção vem só dos cards com histórico")
    checa(base["vencidos"] == 2, "conta os dois cards vencidos")
    checa(base["proxima_no_passado"] is True,
          "data mais antiga no passado é marcada como vencida, não como 'próxima'")


def teste_card_inexistente_e_orfao():
    cenario()
    escrever("base.md", (CONCEITOS / "base.md").read_text(encoding="utf-8")
             .replace("cards: [1, 2]", "cards: [1, 2, 999]"))
    conceitos = grafo.carregar_conceitos(CONCEITOS)
    semear_banco()
    meta = grafo.anexar_srs(conceitos, HOJE)
    checa(("base", 999) in meta["cards_orfaos"], "card que não existe no banco é órfão")


def teste_pendencia_nao_e_problema():
    cenario()
    escrever("base.md", (CONCEITOS / "base.md").read_text(encoding="utf-8")
             .replace("nota_origem: aluno", "nota_origem: ledger"))
    conceitos = grafo.carregar_conceitos(CONCEITOS)
    problemas, pendencias = grafo.validar(conceitos, {"cards_orfaos": []})
    checa(any("síntese do ledger" in p for p in pendencias),
          "nota do ledger entra em PENDÊNCIAS")
    checa(not any("síntese do ledger" in p for p in problemas),
          "e não entra em PROBLEMAS — senão o --validar vive vermelho e ninguém olha")


# ── HTML ─────────────────────────────────────────────────────────────────────


def _html() -> str:
    conceitos = cenario()
    semear_banco()
    meta = grafo.anexar_srs(conceitos, HOJE)
    payload = grafo.montar(conceitos, {"materia": "Matéria Teste"}, meta, HOJE)
    return grafo.gerar_html(payload)


def teste_html_autocontido():
    h = _html()
    externos = re.findall(r'(?:src|href)\s*=\s*["\'](?!#)([^"\']+)', h)
    checa(not externos, f"nenhum recurso externo (achou {externos})")
    checa("__DADOS__" not in h and "__MATERIA__" not in h,
          "todos os marcadores do template foram substituídos")
    checa("Matéria Teste" in h, "o nome da matéria entra no HTML")


def teste_html_escapa_conteudo():
    cenario()
    escrever("base.md", (CONCEITOS / "base.md").read_text(encoding="utf-8")
             .replace("A explicação", "<script>alert(1)</script> A explicação"))
    conceitos = grafo.carregar_conceitos(CONCEITOS)
    nota = grafo.nota_para_html(next(c for c in conceitos if c["id"] == "base")["nota"])
    checa("<script>" not in nota, "HTML na nota é escapado, não injetado")
    checa("&lt;script&gt;" in nota, "e aparece como texto")


def teste_markdown_minimo():
    saida = grafo.nota_para_html("um **forte** e `cod`\n\n- a\n- b\n")
    checa("<strong>forte</strong>" in saida, "negrito vira <strong>")
    checa("<code>cod</code>" in saida, "backtick vira <code>")
    checa(saida.count("<li>") == 2 and "<ul>" in saida, "lista vira <ul>/<li>")
    wiki = grafo.nota_para_html("liga em [[outro]]")
    checa('data-ir-para="outro"' in wiki, "[[wikilink]] vira link navegável")


def teste_js_sem_erro_de_sintaxe():
    if shutil.which("node") is None:
        pula("node não encontrado — checagem de sintaxe do JS não rodou")
        return
    js = re.search(r"<script>\n(.*?)\n</script>", _html(), re.S)
    if not js:
        checa(False, "não achei o bloco <script> no HTML")
        return
    arq = RAIZ / "grafo.js"
    arq.write_text(js.group(1), encoding="utf-8")
    r = subprocess.run(["node", "--check", str(arq)], capture_output=True, text=True)
    checa(r.returncode == 0,
          "o JS do grafo compila" + ("" if r.returncode == 0 else f" — {r.stderr.strip()[:200]}"))


# ── runner ───────────────────────────────────────────────────────────────────


def main() -> int:
    grupos = {
        "parser dos conceitos": [teste_parse_escalares, teste_parse_listas_de_objetos,
                                 teste_placeholder_nao_conta_como_nota,
                                 teste_status_invalido_degrada,
                                 teste_arquivo_sem_frontmatter_nao_explode],
        "arestas": [teste_direcao_das_arestas, teste_aresta_orfa_nao_entra],
        "cruzamento com o SRS": [teste_retrievability_do_elo_mais_fraco,
                                 teste_card_inexistente_e_orfao,
                                 teste_pendencia_nao_e_problema],
        "HTML gerado": [teste_html_autocontido, teste_html_escapa_conteudo,
                        teste_markdown_minimo, teste_js_sem_erro_de_sintaxe],
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
