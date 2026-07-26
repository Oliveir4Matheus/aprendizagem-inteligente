# Instrução para IA — Sistema de Revisão Interativa com FSRS v5

Este arquivo é auto-suficiente. Qualquer modelo de IA (Claude, GPT, Gemini, etc.) pode lê-lo e conduzir uma sessão de revisão interativa usando o banco SQLite deste projeto.

---

## Contexto

O aluno (perfil completo em `estudo/PERFIL.md`) usa este sistema de revisão assim:

1. A IA busca os flashcards vencidos no banco SQLite
2. Pergunta um card por vez — em **cloze progressivo**, no tamanho de lacuna do nível de rigor
3. O aluno completa a lacuna com suas próprias palavras
4. A IA avalia a resposta e atribui um rating 1-4
5. A IA computa o próximo intervalo com FSRS v5 e salva no banco
6. Repete até acabar os cards devidos

**Estilo:** direto, técnico, sem enrolação. Valide respostas com precisão — o objetivo é retenção real, não aprovação fácil.

**Rigor:** o nível (1 a 4) vem de `estudo/PERFIL.md` (ou do campo `rigor:` do ledger da matéria, que tem precedência). A escala completa está em [`METODOS_DE_ENSINO.md`](METODOS_DE_ENSINO.md) §2 e define três coisas: quanta lacuna o card mostra, quando a dica entra, e quão severo é o rating.

---

## Banco de dados

**Arquivo:** `estudo/progresso/srs.db` (SQLite, relativo à raiz do projeto)

**Tabela `cards`:**

| coluna      | tipo    | descrição                                              |
|-------------|---------|--------------------------------------------------------|
| id          | INTEGER | chave primária                                         |
| front       | TEXT    | pergunta mostrada ao aluno                             |
| back        | TEXT    | resposta correta (a IA vê, o aluno não vê antes)      |
| tags        | TEXT    | JSON array de tags: `["<materia>","<topico>"]`               |
| deck        | TEXT    | nome do deck: `Estudos::<Materia>::<Topico>`   |
| subject     | TEXT    | matéria: `"<Matéria>"`                   |
| state       | INTEGER | 0=New 1=Learning 2=Review 3=Relearning                |
| difficulty  | REAL    | dificuldade FSRS (1-10, começa em 0 para New)         |
| stability   | REAL    | estabilidade FSRS em dias (0 para New)                |
| due_date    | TEXT    | data de vencimento ISO: `"2026-07-18"`                |
| last_review | TEXT    | data da última revisão (NULL se nunca revisado)       |
| reps        | INTEGER | total de revisões                                     |
| lapses      | INTEGER | total de erros (rating=1)                             |

**Tabela `review_log`:** histórico de cada revisão (card_id, date, rating, elapsed_days, interval_days, stability, difficulty, state)

---

## Como usar Python para acessar o banco

A IA deve usar Python inline via Bash (ou equivalente no seu ambiente):

```python
import sqlite3, json
from datetime import date, datetime, timedelta

DB = './estudo/progresso/srs.db'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
```

---

## Passo a passo da sessão

### 1. Buscar cards devidos

```python
today = str(date.today())
rows = conn.execute(
    "SELECT * FROM cards WHERE due_date <= ? ORDER BY state DESC, due_date ASC LIMIT 20",
    (today,)
).fetchall()
cards = [dict(r) for r in rows]
print(f"{len(cards)} cards para revisar hoje")
```

Se `len(cards) == 0`: dizer ao aluno que não há revisões pendentes e sugerir estudar conteúdo novo.

#### 1b. Modo reentrada — quando o aluno volta depois de sumir

`python3 scripts/status.py` dispara este modo sozinho quando faz **10+ dias** sem sessão **ou** o backlog passa de **15 cards**. Não ignore o aviso.

A sessão de volta é a mais frágil de todas: quem some três semanas volta e erra muito, porque três semanas sem revisar é exatamente o desenho do esquecimento. Se a primeira sessão de retorno for uma demonstração de fracasso, não há segunda. **O objetivo dela é reacender o hábito, não quitar a dívida.**

```python
TETO = 8
rows = conn.execute(
    "SELECT * FROM cards WHERE due_date <= ? "
    "ORDER BY stability DESC, due_date ASC LIMIT ?",   # MAIOR estabilidade primeiro
    (today, TETO)
).fetchall()
```

O que muda:

| | Sessão normal | Modo reentrada |
|---|---|---|
| Quantidade | até 20 cards | **teto de 8** |
| Ordem | mais vencido primeiro | **maior estabilidade primeiro** — os que ele ainda acerta |
| Conteúdo novo | permitido depois da revisão | **nenhum** |
| Dica | conforme o nível de rigor | **1 tentativa antes do normal** |
| Régua do rating | conforme o nível | **inalterada** |

> **Por que a régua não muda.** Seria tentador baixar o rigor na volta para o aluno se sentir melhor. Isso infla o rating, que infla o intervalo, que esconde a lacuna — o problema volta maior daqui a duas semanas. Adiantar a dica dá o mesmo alívio **sem mentir para o agendamento**: a dica já limita o rating a 2, então o FSRS recebe exatamente o sinal correto, "lembrou com ajuda".

Abra dizendo o que está acontecendo. Algo como: *"você sumiu 23 dias e tem 41 cards vencidos. Não vamos ver os 41 hoje — vamos ver 8, começando pelos que você provavelmente ainda sabe."*

#### 1c. Espalhar o backlog — só com autorização

Ao fim de uma sessão de reentrada, **ofereça** redistribuir o que sobrou pelos próximos dias. Nunca faça sozinho: `due_date` é a fonte da verdade do progresso, e reescrevê-la sem o aluno mandar contradiz o princípio central do sistema.

```python
# Só rode depois de um "pode espalhar" explícito.
# Mexe apenas em due_date — stability e difficulty ficam intactas,
# então o modelo FSRS não é corrompido, só a fila é reordenada no tempo.
DIAS = 5
restantes = conn.execute(
    "SELECT id FROM cards WHERE due_date <= ? ORDER BY stability DESC", (today,)
).fetchall()
for i, r in enumerate(restantes):
    nova = date.today() + timedelta(days=i % DIAS)
    conn.execute("UPDATE cards SET due_date=? WHERE id=?", (str(nova), r["id"]))
conn.commit()
print(f"{len(restantes)} cards espalhados pelos próximos {DIAS} dias")
```

Registre no `## Log de aprendizado` do ledger que houve redistribuição, com a data e a quantidade.

### 2. Para cada card — apresentar em cloze

Mostrar apenas `card["front"]`, reescrito como **texto lacunado** no tamanho do nível de rigor. NÃO mostrar `card["back"]` antes da resposta.

```
N1  uma palavra lacunada num parágrafo inteiro
N2  várias lacunas curtas na mesma frase
N3  a lacuna é uma justificativa inteira, ancorada no contexto real do aluno
N4  só o cenário é dado; a lacuna é o diagnóstico completo + defesa sob contestação
```

### 3. Aguardar resposta do aluno

O aluno completa a lacuna com as próprias palavras.

**Dica:** existe em todos os níveis. Ela **devolve contexto** (rebaixa a questão um nível: N4→N3, N3→N2, N2→N1) e nunca entrega a resposta. Quando entra: N1 ao primeiro sinal de hesitação, N2 após 1 tentativa, N3 e N4 após 2.

### 4. Avaliar e atribuir rating

Compare a resposta do aluno com `card["back"]` usando julgamento de IA:

| rating | quando usar                                                     |
|--------|-----------------------------------------------------------------|
| 1      | Errou completamente, em branco, ou confundiu com outro conceito |
| 2      | Lembrou a ideia geral mas faltou nome técnico ou detalhe chave  |
| 3      | Resposta correta com algum esforço ou pequena imprecisão        |
| 4      | Correto, preciso e instantâneo — sem hesitação                  |

**A barra do rating 3 (domínio) sobe com o nível de rigor:**

| | vale 3 quando… | imprecisão terminológica |
|---|---|---|
| **N1** | acertou a ideia central | não penaliza |
| **N2** | acertou a ideia **e** o nome técnico | derruba para 2 |
| **N3** | nome + exemplo + distinção do conceito vizinho, sem dica | derruba para 2 |
| **N4** | sustentou o diagnóstico sob contestação, sem dica | derruba para 1 |

> **Regra fixa em qualquer nível: acerto após dica vale no máximo rating 2.** Lembrou com apoio não é lembrar sozinho — e o espaçamento precisa refletir isso para não inflar o intervalo.

### 5. Calcular novo intervalo com FSRS v5

Execute este snippet Python substituindo os valores de `state, d, s, elapsed, rating`:

```python
import math

# Pesos padrão do FSRS-5 (19 parâmetros).
# ⚠️ NÃO edite índices soltos aqui. W[15] é a penalidade de "Hard" e multiplica o
#    GANHO de estabilidade quando rating=2 — se virar 0, todo card avaliado com 2
#    congela no mesmo intervalo para sempre (bug real que já existiu neste arquivo).
W = [0.40255, 1.18385, 3.173,   15.69105, 7.1949,  0.5345,  1.4604,
     0.0046,  1.54575, 0.1192,  1.01925,  1.9395,  0.11,    0.29605,
     2.2698,  0.2315,  2.9898,  0.51655,  0.6621]
DECAY=-0.5; FACTOR=0.9**(1/DECAY)-1
REQUESTED_RETENTION = 0.95 # Define a retenção desejada (0.95 encurta os intervalos em ~54% para revisões mais frequentes)

# ── substituir ──────────────────────────────────────────────────────────────
state   = card["state"]       # 0=New 1=Learning 2=Review 3=Relearning
d       = card["difficulty"]  # 0 se New
s       = card["stability"]   # 0 se New
last    = card["last_review"] # None se nunca revisado
today_s = str(date.today())
elapsed = (date.today() - date.fromisoformat(last)).days if last else 0
rating  = RATING              # 1/2/3/4 conforme avaliação acima
# ────────────────────────────────────────────────────────────────────────────

r = (1 + FACTOR * elapsed / s)**DECAY if s > 0 else 0.0

if state in (0, 1, 3):  # New / Learning / Relearning
    nd = min(10, max(1, W[4] - math.exp(W[5]*(rating-1)) + 1)) if state == 0 \
         else min(10, max(1, (d - W[6]*(rating-3)) + W[7]*(W[4]-(d-W[6]*(rating-3)))))
    ns = W[rating-1] if state == 0 else max(0.1, s)
    if rating == 1:
        new_state, interval = 1, 1
    else:
        new_state = 2
        interval = max(1, round(ns * (REQUESTED_RETENTION**(1/DECAY) - 1) / FACTOR))
else:  # Review
    nd = min(10, max(1, (d - W[6]*(rating-3)) + W[7]*(W[4]-(d-W[6]*(rating-3)))))
    if rating == 1:
        ns = max(0.1, W[11]*d**(-W[12])*((s+1)**W[13]-1)*math.exp(W[14]*(1-r)))
        new_state, interval = 3, 1
    else:
        hp = W[15] if rating==2 else 1.0
        eb = W[16] if rating==4 else 1.0
        ns = max(0.1, s*(math.exp(W[8])*(11-d)*s**(-W[9])*(math.exp(W[10]*(1-r))-1)*hp*eb+1))
        new_state = 2
        interval = max(1, round(ns * (REQUESTED_RETENTION**(1/DECAY) - 1) / FACTOR))

next_due = str(date.today() + timedelta(days=interval))
```

### 6. Gravar no banco

```python
lapses = card["lapses"] + (1 if rating == 1 else 0)
today_s = str(date.today())

conn.execute(
    "UPDATE cards SET state=?,difficulty=?,stability=?,due_date=?,"
    "last_review=?,reps=reps+1,lapses=? WHERE id=?",
    (new_state, nd, ns, next_due, today_s, lapses, card["id"])
)
conn.execute(
    "INSERT INTO review_log(card_id,review_date,rating,elapsed_days,"
    "interval_days,stability,difficulty,state) VALUES(?,?,?,?,?,?,?,?)",
    (card["id"], today_s, rating, elapsed, interval, ns, nd, new_state)
)
conn.commit()
```

### 7. Feedback ao aluno

Após cada card, mostrar:
- Se acertou: breve confirmação + o que foi bem
- Se errou/parcial: correção precisa + o que estava faltando
- Próxima revisão: `f"Próxima revisão deste card: {next_due} ({interval} dias)"`

Ao final da sessão: resumo com total de cards revisados, % de acerto, e os pontos fracos que surgiram.

---

## Adicionar cards novos ao banco

Durante o ensino de conteúdo novo, a IA pode salvar cards diretamente:

```python
import sqlite3, json
from datetime import date, datetime

conn = sqlite3.connect('./estudo/progresso/srs.db')
cards_novos = [
    {
        "front": "Pergunta aqui",
        "back":  "Resposta aqui",
        "tags":  ["<materia>","<topico>"],
        "deck":  "Estudos::<Materia>::<Topico>",
        "subject": "<Matéria>"
    },
    # ... mais cards
]
today = str(date.today())
now   = str(datetime.now())
added = 0
for c in cards_novos:
    exists = conn.execute("SELECT id FROM cards WHERE front=?", (c["front"],)).fetchone()
    if exists:
        continue
    conn.execute(
        "INSERT INTO cards(front,back,tags,deck,subject,due_date,created_at) VALUES(?,?,?,?,?,?,?)",
        (c["front"], c["back"], json.dumps(c["tags"]), c["deck"], c["subject"], today, now)
    )
    added += 1
conn.commit()
print(f"{added} cards adicionados ao SRS")
```

---

## Ver estatísticas rápidas

```python
conn = sqlite3.connect('./estudo/progresso/srs.db')
row = conn.execute("""
    SELECT
        COUNT(*) total,
        SUM(CASE WHEN due_date <= date('now') THEN 1 ELSE 0 END) due_hoje,
        SUM(CASE WHEN state=0 THEN 1 ELSE 0 END) novos,
        SUM(CASE WHEN state=2 THEN 1 ELSE 0 END) em_revisao
    FROM cards
""").fetchone()
print(f"Total: {row[0]} | Vencidos hoje: {row[1]} | Novos: {row[2]} | Em revisão: {row[3]}")
```

---

---

## Performance: tempo cruzado com retenção

```bash
python3 scripts/status.py --performance
```

A tabela `study_sessions` guarda o tempo cronometrado por `scripts/sessao.py`. **Ela nunca é lida sozinha.** Minuto isolado mede esforço, não aprendizado — celebrar "2h de estudo hoje" é exatamente a armadilha de medir engajamento no lugar de retenção, que o resto deste sistema existe para evitar.

A leitura correta cruza tempo com o `review_log` da mesma data:

```python
linhas = conn.execute("""
    SELECT date(s.inicio) dia,
           SUM(s.duracao_min) minutos,
           (SELECT COUNT(*) FROM review_log r WHERE r.review_date = date(s.inicio)) revisados,
           (SELECT COUNT(*) FROM review_log r WHERE r.review_date = date(s.inicio) AND r.rating >= 3) retidos
    FROM study_sessions s WHERE s.fim IS NOT NULL
    GROUP BY dia ORDER BY dia DESC LIMIT 21
""").fetchall()
# custo por conceito retido = minutos / retidos
```

O número que interessa é **minutos por conceito retido**. Ele responde perguntas acionáveis:

- O custo sobe depois do segundo bloco? → a sessão está longa demais para este aluno.
- Blocos de 50 min custam menos por conceito que os de 25? → ajuste o **Bloco de foco** no `PERFIL.md`.
- O custo disparou nesta matéria? → o material está mal recortado ou a etapa está grande demais.

Precisa de algumas semanas de dado para dizer qualquer coisa. Antes disso, mostre a tabela mas **não tire conclusão** — n pequeno em série temporal é ruído com aparência de tendência.

---

## Notas importantes

- **Nunca** mostrar o `back` antes do aluno responder
- **Sempre** confirmar se o DB existe em `./estudo/progresso/srs.db` antes de começar
- Em caso de dúvida no rating, pedir ao aluno para reformular — o objetivo é calibração honesta
- Siga as preferências do `estudo/PERFIL.md` (por padrão: perguntas que exijam nome técnico + exemplo concreto + distinção entre conceitos parecidos — não só a ideia geral)
- Intervalo `= round(stability)` dias — não precisa de fórmula complexa para o intervalo final
