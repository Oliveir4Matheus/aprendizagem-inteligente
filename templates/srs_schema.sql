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

-- review_log guarda, além do resultado, o CONTEXTO em que a resposta aconteceu.
-- As quatro últimas colunas existem por dois motivos distintos:
--   · confianca  → calibração metacognitiva: o aluno previu antes de saber o resultado?
--   · tentativas e usou_dica → tornam a nota auditável. São fatos objetivos ao lado de
--     um julgamento subjetivo; se a proporção de notas altas subir sem que as dicas
--     caiam, alguma coisa afrouxou na avaliação e isso fica visível.
--   · tipo_item  → mede se as cotas de intercalação e transferência estão sendo cumpridas.
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
    confianca     INTEGER,          -- 0 = não vou acertar · 1 = mais ou menos · 2 = vou acertar
    tentativas    INTEGER,          -- quantas vezes o aluno tentou antes de fechar
    usou_dica     INTEGER,          -- 0 | 1 — dica limita a nota a 2
    tipo_item     TEXT,             -- recall | intercalado | sintese | transferencia | portao
    FOREIGN KEY(card_id) REFERENCES cards(id)
);

-- Sessões de estudo cronometradas (scripts/sessao.py).
-- Existe para responder UMA pergunta: quanto tempo custou cada conceito retido.
-- Tempo isolado é métrica de vaidade — toda leitura desta tabela sai cruzada com
-- o review_log da mesma data. Ver REVISAO_IA.md → "Performance: tempo x retenção".
CREATE TABLE IF NOT EXISTS study_sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    materia       TEXT    NOT NULL DEFAULT "",
    etapa         TEXT,
    tipo          TEXT    NOT NULL DEFAULT "study",  -- study | recall | revisao
    inicio        TEXT    NOT NULL,                  -- ISO datetime local
    fim           TEXT,                              -- NULL = sessão ainda aberta
    duracao_min   INTEGER,
    bloco_min     INTEGER,                           -- tamanho do bloco de foco configurado
    blocos_alvo   INTEGER,
    blocos_feitos INTEGER,
    interrompida  INTEGER NOT NULL DEFAULT 0,
    absorvido     TEXT                               -- o que o aluno diz que ficou
);

CREATE INDEX IF NOT EXISTS idx_due ON cards(due_date, state);
CREATE INDEX IF NOT EXISTS idx_sessao_inicio ON study_sessions(inicio);
CREATE INDEX IF NOT EXISTS idx_sessao_aberta ON study_sessions(fim);
CREATE INDEX IF NOT EXISTS idx_log_data ON review_log(review_date);
