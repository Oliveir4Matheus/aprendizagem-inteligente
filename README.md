# 🧠 Aprendizagem Inteligente

```
     ___
    (o,o)      M N E M O
    /)_)       guardião da memória
     " "
```

Um **sistema de estudo com IA** para **qualquer matéria**. Um agente orquestrador
(Claude Code ou Antigravity CLI) prepara o material no **NotebookLM**, você estuda lá,
e o progresso fica registrado aqui — com **repetição espaçada (FSRS)** de verdade.

Não é um projeto de código: é um **workspace de estudo reutilizável**.
Roda igual em **Linux, macOS e Windows**.

---

## ⚡ Quickstart

**1. Abra o agente neste diretório.** Ele lê o `AGENTS.md` sozinho e assume a persona do tutor.

> O setup instala programas, clona código e abre o navegador — então o agente vai pedir
> sua aprovação algumas vezes ao longo do caminho. É esperado: leia o que ele vai rodar
> e aprove. São poucas confirmações, todas no começo.

**2. Diga a ele:**

```
configure o setup seguindo o COOKBOOK.md
```

Ele executa os **passos 1–8** (máquina) e emenda nos **9–20** (a entrevista), com uma
barra de progresso contínua:

```
[ 2/20 ] Garantindo o uv                ██░░░░░░░░░░░░░░  10%
[ 5/20 ] Instalando o MCP pinado         ████░░░░░░░░░░░░  25%
[ 8/20 ] Autenticando no NotebookLM      ██████░░░░░░░░░░  40%
[13/20 ] Método de ensino                ██████████░░░░░░  65%
[19/20 ] Rigor do tutor                  ███████████████░  95%
[20/20 ] Tudo pronto                     ████████████████ 100%
```

No passo 8 o navegador abre para você entrar no Google — **use uma conta dedicada só
para estudo**, nunca a principal. O resto o agente confirma sozinho.

**3. Comece:**

```
quero começar a matéria X        → ele propõe um roadmap e espera seu OK
rode o loop de estudo            → PREP → você estuda no NotebookLM → PROGRESS
```

> **Prefere rodar na mão?** `python3 scripts/setup.py` (Linux/macOS) ou
> `py scripts\setup.py` (Windows) faz os passos 1–8. Use `--dry-run` para só validar o
> ambiente sem instalar nada.

---

## O método (base científica)

Técnicas de estudo com maior evidência (Dunlosky et al. 2013):
**recordação ativa** + **repetição espaçada** + **Feynman** + **elaboração** + **80/20**.

O tutor não é genérico — ele é **configurado no onboarding**:

| O que você escolhe | Efeito |
|---|---|
| **Método de ensino** (6 opções) | socrático, instrução direta, exemplos trabalhados, baseado em problema, descoberta guiada ou mastery — cada um vira um roteiro que o agente executa passo a passo |
| **Postura** (5 opções) | inferida de 4 cenários, não de autodiagnóstico |
| **Rigor** (4 níveis) | Webb DOK × standards-based grading: controla a profundidade da pergunta, o tamanho da lacuna no recall e a severidade do rating |
| **Idioma e artefatos** | o que o NotebookLM sempre gera, e em que língua |

Catálogo completo em [`METODOS_DE_ENSINO.md`](METODOS_DE_ENSINO.md).

**O recall é em texto lacunado** (cloze progressivo): o tutor escreve o parágrafo e você
completa. A lacuna encolhe conforme o rigor — no nível 4 sobra só o cenário e a lacuna é
o diagnóstico inteiro. Dica existe em todos os níveis; ela devolve contexto em vez de
entregar a resposta, e limita o rating a 2.

## As 3 ferramentas (cada uma no que faz melhor)

| Ferramenta | Papel |
|---|---|
| **Orquestrador** (Claude Code / Antigravity) | Conduz o loop, prepara material, registra progresso |
| **NotebookLM** | Superfície de estudo: áudio, quiz, infográfico, mapa mental, slides, Q&A com citação |
| **FSRS** (`estudo/progresso/srs.db`) | Repetição espaçada — o timing das revisões |

Visão completa e diagramas em [`ARQUITETURA.md`](ARQUITETURA.md).

---

## 🧭 A estrutura: duas metades com regras opostas

Este repositório separa **como o sistema funciona** de **o que você estudou**.
É o que permite melhorar o harness com o uso e publicar só isso — seu conteúdo de
estudo nunca sai da sua máquina.

```
aprendizagem-inteligente/
│
├── ▲ HARNESS — versionado, é isso que sobe pro git
│   ├── AGENTS.md              ← entrada auto-lida pelo agente
│   ├── METODOS_DE_ENSINO.md   ← os 6 métodos, o rigor DOK 1–4, as 5 posturas
│   ├── COOKBOOK.md            ← setup, onboarding, atualização do MCP, loop
│   ├── ARQUITETURA.md         ← mapa das peças + diagramas
│   ├── GUIA_NOTEBOOKLM.md     ← persona/método (sobe como fonte no NotebookLM)
│   ├── REVISAO_IA.md          ← SQLs + FSRS da revisão interativa
│   ├── .agents/
│   │   ├── mcp_config.json          ← MCP com privilégio mínimo
│   │   ├── mcp_pin.json             ← commit auditado do MCP
│   │   └── skills/professor/SKILL.md ← o cérebro (persona + loop 3 fases)
│   ├── scripts/               ← setup.py · mcp_update.py · mnemo.py
│   └── templates/             ← modelos copiados para estudo/ no setup
│
└── ▼ estudo/ — IGNORADO pelo git, nunca sai da sua máquina
    ├── PERFIL.md              ← quem você é + como o tutor deve agir
    ├── JORNADA.md             ← mapa visual da sua jornada
    ├── documentos/            ← suas fontes (PDF/slides) e os recortes por etapa
    └── progresso/
        ├── _index.md          ← mapa das matérias
        ├── <materia>.md       ← ledger: estado, 80/20, pontos fracos, log
        ├── <materia>-roadmap.md ← trilha: etapas + conceitos obrigatórios
        ├── srs.db             ← flashcards + FSRS
        └── jornada_do_heroi.jpg ← badge de conquista pro LinkedIn
```

**O teste do clone:** se outra pessoa clonasse este repo para estudar algo
completamente diferente, essa informação ainda seria útil? **Sim** → harness, vai na
raiz. **Não** → conteúdo, vai em `estudo/`.

Na prática: você usa o sistema, corrige o agente (*"da próxima vez não gere X"*), ele
escreve isso no arquivo de harness certo — e no dia do commit sobe só a evolução da
arquitetura. Nunca a matéria. A regra completa está em [`AGENTS.md`](AGENTS.md) →
*"Onde escrever cada coisa"*.

---

## 🔒 Segurança

O MCP do NotebookLM é **código de terceiro que dirige uma sessão real do Google**.
As defesas embutidas:

- **Conta Google dedicada** — se o cookie vazar, expõe só seus materiais de estudo.
- **Commit pinado e auditado** (`.agents/mcp_pin.json`), instalado de um clone local em `vendor/` — não do PyPI `latest`.
- **Privilégio mínimo** — `sharing` e `automation` desligados; o setup **falha** se alguém religar.
- **Cookie local**, `0600` no Linux/macOS.
- **Atualização auditada:** `python3 scripts/mcp_update.py` lê o diff antes de aplicar e procura execução dinâmica de código, shell, desserialização insegura, ofuscação, leitura de credenciais, persistência e dependências novas. Achado de severidade **ALTA bloqueia** a atualização.

> O MCP é não oficial, licença MIT. Detalhes de auditoria e hardening no [`COOKBOOK.md`](COOKBOOK.md) Parte D.
