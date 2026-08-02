---
artifact_type: flashcards
granularidade: subtopico
papel: teste
---

# `flashcards` — Flashcards

> Leia junto com [`_index.md`](_index.md). Referências em [`REFERENCIAS.md`](REFERENCIAS.md).

## 1. Granularidade: **um baralho por subtópico**

**6 a 12 cards por subtópico.** A correspondência 1:1 entre baralho e subtópico não é estética:
é ela que permite, quando o aluno erra um card no FSRS, saber exatamente qual artefato reabrir
e qual conceito do roadmap está fraco.

## 2. A regra fundadora: um fato por card

**Princípio da informação mínima** (Wozniak, 1999): material simples é retido de forma
desproporcionalmente melhor sob repetição espaçada. Um card com dois fatos no verso não é um
card difícil — é dois cards mal feitos, e o FSRS não consegue agendar os dois separadamente,
porque recebe um rating só para os dois.

**O teste:** se a resposta tem "e" ligando duas informações independentes, são dois cards.

**Consequências práticas:**

| Não faça | Faça |
|---|---|
| Card com lista ("cite as 5 etapas de X") | Um card por etapa, ou cloze encadeado |
| Card com resposta de parágrafo | Card com resposta de uma linha |
| Card que pergunta "o que é X?" e responde com a definição do manual | Card que pergunta pelo **critério de uso** de X |
| Card ambíguo (mais de uma resposta correta cabe) | Enunciado que fecha a resposta |

## 3. Cloze: quando ajuda e quando vicia

Cloze (frase com lacuna) é a forma mais rápida de respeitar a informação mínima, e por isso é o
formato padrão do sistema — é o mesmo formato do recall da Fase 3 (`REVISAO_IA.md`).

**O risco é real:** com uma frase memorizada e sempre a mesma lacuna, o aluno aprende a
reconhecer a *forma* da frase em vez do conteúdo — casamento de padrão. Duas travas:

1. **Não lacune a única palavra técnica de uma frase decorável.** Lacune o **critério**, a
   **condição** ou a **consequência** — a parte que exige entender.
2. **Varie a formulação** entre cards do mesmo conceito, para a pista ser o significado e não
   o ritmo da frase.

**Quando NÃO usar cloze:** mecanismo, relação causal e processo pedem pergunta-e-resposta
aberta, que produz aprendizagem mais profunda. Cloze é para termo, critério e valor.

## 4. Base científica

| Regra | Fundamento |
|---|---|
| Flashcards são artefato de primeira classe | Teste prático + prática distribuída = **alta utilidade** (Dunlosky et al., 2013) |
| Um fato por card | Princípio da informação mínima (Wozniak, 1999) |
| Formato cloze como padrão | Mesmo formato do recall; converte texto em item recuperável |
| Pergunta aberta para mecanismo | Recuperação de significado supera recuperação de rótulo |
| O agendamento não é papel do card | Prática distribuída é do FSRS (`srs.db`) |

## 5. Composição do baralho (6–12 cards)

| Quantidade | Tipo de card |
|---|---|
| 2–3 | **Termo/critério** (cloze): a condição que define o conceito |
| 2–3 | **Mecanismo** (pergunta aberta): *por que* funciona assim |
| 1–2 | **Discriminação**: dado um cenário, qual dos dois conceitos parecidos se aplica |
| 1–2 | **Aplicação**: cenário do contexto do aluno → o que fazer |
| 1 | **Erro clássico**: a afirmação falsa que parece verdadeira, e por que é falsa |

## 6. Bloco `[FORMATO]` do `focus_prompt`

```
[FORMATO]
Produza de 6 a 12 flashcards sobre este subtópico.

REGRA CENTRAL — um fato por card:
- Cada card testa UMA informação. Se a resposta tem "e" ligando duas informações
  independentes, divida em dois cards.
- Resposta de UMA linha. Nunca um parágrafo, nunca uma lista.
- Nada de "cite as N etapas/tipos/características". Listas viram um card por item.
- O enunciado precisa fechar a resposta: se mais de uma resposta correta couber, reescreva.

COMPOSIÇÃO:
- 2 a 3 cards de TERMO/CRITÉRIO, em formato de lacuna. Lacune o critério, a condição ou a
  consequência — nunca a única palavra técnica de uma frase que dá para decorar pelo ritmo.
- 2 a 3 cards de MECANISMO, em pergunta aberta: "por que <X> acontece quando <Y>?"
- 1 a 2 cards de DISCRIMINAÇÃO: um cenário, e a pergunta é qual dos dois conceitos parecidos
  se aplica e por qual critério.
- 1 a 2 cards de APLICAÇÃO num cenário do contexto <background do aluno>.
- 1 card de ERRO CLÁSSICO: uma afirmação que parece verdadeira mas é falsa, com o porquê.

Varie a formulação entre cards do mesmo conceito. Se todos seguirem o mesmo molde de frase,
o aluno aprende o molde e não o conteúdo.
```

## 7. Parâmetros do `studio_create`

```python
studio_create(
    notebook_id = <id>,
    artifact_type = "flashcards",
    focus_prompt = <[ESCOPO] + [IDIOMA] + [ALUNO] + [FORMATO]>,
    question_count = 10,
    difficulty = "medium",
    language = <idioma do PERFIL>,
)
```

Renomeie para `E<n>.<m> · <Subtópico> — Flashcards`.

## 8. Ponte com o `srs.db` — quem manda é o script

Os flashcards do NotebookLM são **rascunho**. O que agenda revisão é o `srs.db`, e ele só é
escrito por `scripts/revisar.py` (`AGENTS.md` → regras inquebráveis).

Fluxo, na Fase 3:

```bash
python3 scripts/revisar.py criar --front "..." --back "..." \
    --deck "Estudos::<Materia>::<Etapa>::<Subtopico>" \
    --subject "<Matéria>" --tags "<materia>,<etapa>,<subtopico>"
```

- **`--deck` é o campo que importa, e o subtópico entra nele.** É por `deck` que
  `workspace.fila_intercalada()` alterna os cards na revisão — se o subtópico não estiver no
  deck, a fila agrupa tudo do mesmo tópico e a intercalação vira letra morta. `--subject`
  continua sendo a **matéria** (convenção em `REVISAO_IA.md` §2).
- O dedupe por `front` é automático — reimportar não duplica.
- Card de erro do recall tem prioridade sobre card bonito do NotebookLM: o que o aluno errou
  vale mais do que o que a IA achou importante.

## 9. O que invalida o artefato

- Card com lista no verso.
- Resposta de parágrafo.
- Cloze na única palavra técnica de uma frase decorável.
- Card ambíguo (duas respostas corretas possíveis).
- Baralho cobrindo a etapa inteira em vez do subtópico.

## 10. Checklist

- [ ] Um baralho por subtópico, 6–12 cards
- [ ] Todo card tem um fato só, resposta de uma linha
- [ ] A composição cobre termo, mecanismo, discriminação, aplicação e erro clássico
- [ ] Nenhum card de lista
- [ ] Cards que valem foram para o `srs.db` com o **subtópico dentro do `--deck`**
- [ ] Idioma do PERFIL, título no padrão
