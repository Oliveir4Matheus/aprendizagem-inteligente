# Instrução para IA — Sistema de Revisão Interativa com FSRS v5

Este arquivo é auto-suficiente. Qualquer modelo de IA (Claude, GPT, Gemini, etc.) pode lê-lo e conduzir uma sessão de revisão interativa usando o banco SQLite deste projeto.

---

## Contexto

O aluno (perfil completo em `PERFIL.md`) usa este sistema de revisão assim:

1. A IA busca os flashcards vencidos no banco SQLite
2. Pergunta um card por vez (mostra só a frente)
3. O aluno responde com suas próprias palavras
4. A IA avalia a resposta e atribui um rating 1-4
5. A IA computa o próximo intervalo com FSRS v5 e salva no banco
6. Repete até acabar os cards devidos

**Estilo:** direto, técnico, sem enrolação. Valide respostas com precisão — o objetivo é retenção real, não aprovação fácil.

---

## Banco de dados

**Arquivo:** `progresso/srs.db` (SQLite, relativo à raiz do projeto)

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

DB = './progresso/srs.db'
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

### 2. Para cada card — mostrar a frente

Mostrar apenas `card["front"]`. NÃO mostrar `card["back"]` antes da resposta.

### 3. Aguardar resposta do aluno

O aluno escreve a resposta com as próprias palavras.

### 4. Avaliar e atribuir rating

Compare a resposta do aluno com `card["back"]` usando julgamento de IA:

| rating | quando usar                                                     |
|--------|-----------------------------------------------------------------|
| 1      | Errou completamente, em branco, ou confundiu com outro conceito |
| 2      | Lembrou a ideia geral mas faltou nome técnico ou detalhe chave  |
| 3      | Resposta correta com algum esforço ou pequena imprecisão        |
| 4      | Correto, preciso e instantâneo — sem hesitação                  |

**Seja rigoroso:** exija nome técnico correto, não só a ideia. Distinções entre conceitos parecidos contam.

### 5. Calcular novo intervalo com FSRS v5

Execute este snippet Python substituindo os valores de `state, d, s, elapsed, rating`:

```python
import math

W = [0.4072,1.1829,3.1262,15.4722,7.2102,0.5316,1.0651,0.0589,
     1.5330,0.1544,0.9858,1.9555,0.1157,0.1628,0.2746,0.0,2.9898,0.51,1.0651]
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

conn = sqlite3.connect('./progresso/srs.db')
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
conn = sqlite3.connect('./progresso/srs.db')
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

## Notas importantes

- **Nunca** mostrar o `back` antes do aluno responder
- **Sempre** confirmar se o DB existe em `./progresso/srs.db` antes de começar
- Em caso de dúvida no rating, pedir ao aluno para reformular — o objetivo é calibração honesta
- Siga as preferências do `PERFIL.md` (por padrão: perguntas que exijam nome técnico + exemplo concreto + distinção entre conceitos parecidos — não só a ideia geral)
- Intervalo `= round(stability)` dias — não precisa de fórmula complexa para o intervalo final
