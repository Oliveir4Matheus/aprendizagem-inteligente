-- Esquema do banco de repetição espaçada (FSRS v5).
-- O setup usa este arquivo para criar estudo/progresso/srs.db vazio.
-- Regras de uso (SQLs + fórmulas FSRS) estão em REVISAO_IA.md.

CREATE TABLE IF NOT EXISTS cards (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    front       TEXT    NOT NULL,
    back        TEXT    NOT NULL,
    tags        TEXT    NOT NULL DEFAULT "[]",
    deck        TEXT    NOT NULL DEFAULT "",
    subject     TEXT    NOT NULL DEFAULT "",
    state       INTEGER NOT NULL DEFAULT 0,
    difficulty  REAL    NOT NULL DEFAULT 0,
    stability   REAL    NOT NULL DEFAULT 0,
    due_date    TEXT    NOT NULL,
    last_review TEXT,
    reps        INTEGER NOT NULL DEFAULT 0,
    lapses      INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS review_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id       INTEGER NOT NULL,
    review_date   TEXT    NOT NULL,
    rating        INTEGER NOT NULL,
    elapsed_days  INTEGER NOT NULL,
    interval_days INTEGER NOT NULL,
    stability     REAL,
    difficulty    REAL,
    state         INTEGER,
    FOREIGN KEY(card_id) REFERENCES cards(id)
);

CREATE INDEX IF NOT EXISTS idx_due ON cards(due_date, state);
