---
artifact_type: quiz
granularidade: subtopico + integrador da etapa
papel: teste
---

# `quiz` — Teste de múltipla escolha

> Leia junto com [`_index.md`](_index.md). Referências em [`REFERENCIAS.md`](REFERENCIAS.md).

## 1. Granularidade: **um por subtópico + um integrador da etapa**

Este é o único tipo com granularidade dupla, e o motivo é pedagógico:

| Quiz | Escopo | Função | Nº de itens |
|---|---|---|---|
| **Por subtópico** | um subtópico | Diagnóstico: o aluno pegou **este** conceito? | 5 a 8 |
| **Integrador da etapa** | todos os subtópicos misturados | Discriminação: ele sabe **qual** conceito se aplica? | 10 a 12 |

Quiz só por subtópico treina em blocos: como só existe um conceito em jogo, o aluno acerta no
piloto automático sem precisar decidir nada. O integrador é o que força a intercalação — e
intercalar é o que produz discriminação (Dunlosky et al., 2013, utilidade moderada; é a mesma
lógica das cotas do recall da Fase 3 na `SKILL.md`).

Gere o integrador **depois** de todos os de subtópico.

## 2. A regra que decide se o quiz vale alguma coisa: distratores competitivos

Múltipla escolha tem má fama merecida — quando os distratores são fracos. Little et al. (2012)
mostraram o outro lado: com **distratores plausíveis e competitivos**, o item obriga o aluno a
recuperar por que a alternativa certa é certa **e** por que cada errada é errada. O ganho fica
comparável ao de resposta curta e superior ao de releitura.

Ou seja: **o valor do quiz está nos distratores, não no enunciado.** Distrator óbvio
transforma o item em reconhecimento, e reconhecimento não produz retenção.

**De onde vem um bom distrator:**

| Fonte | Exemplo de padrão |
|---|---|
| O par contrastivo | a resposta correta **para o conceito vizinho** |
| O erro de etapa | o critério certo aplicado na situação errada |
| `pontos_fracos` do ledger | o erro que **este aluno** já cometeu |
| A confusão clássica da área | a definição popular imprecisa do termo |

Nunca: alternativas absurdas, "todas as anteriores", "nenhuma das anteriores", opções de
comprimento muito diferente das demais (o comprimento vira dica).

## 3. Base científica

| Regra | Fundamento |
|---|---|
| Quiz é artefato de primeira classe, não extra | Teste prático = **alta utilidade** (Dunlosky et al., 2013) |
| Distratores plausíveis e competitivos | Little et al., 2012 |
| Feedback explicando por que cada errada é errada | Idem — é onde a recuperação produtiva acontece |
| Quiz integrador com itens misturados | Intercalação; discriminação não se treina em bloco |
| Itens de aplicação, não de definição | Recuperação de significado supera recuperação de rótulo |

## 4. Estrutura obrigatória

**Cada item tem:**

- enunciado que apresenta **uma situação**, não pede uma definição;
- 4 alternativas, todas com comprimento e nível de detalhe semelhantes;
- 3 distratores, cada um vindo de uma confusão real (ver tabela acima);
- feedback que explica a correta **e cada uma das erradas**.

**Composição do quiz de subtópico (5–8 itens):** pelo menos 1 item de aplicação em cenário e
pelo menos 1 item de discriminação contra o par contrastivo. O resto pode ser recuperação
direta.

**Composição do integrador (10–12 itens):** ao menos 1 item por subtópico, mais 3 itens que
só se resolvem decidindo **entre** subtópicos, e 1 item de transferência (mesmo conceito,
superfície nova).

## 5. Bloco `[FORMATO]` do `focus_prompt`

**Quiz de subtópico:**

```
[FORMATO]
Produza um teste de múltipla escolha com 5 a 8 itens sobre este subtópico.

REGRA CENTRAL — os distratores decidem se este teste ensina ou não:
- Cada item tem 4 alternativas: 1 correta e 3 distratores PLAUSÍVEIS.
- Um distrator plausível é aquele que alguém que estudou mas entendeu parcialmente escolheria.
  Construa cada um a partir de uma confusão real: a resposta correta para o conceito vizinho;
  o critério certo aplicado na situação errada; a definição popular imprecisa do termo.
- PROIBIDO: alternativa absurda, "todas as anteriores", "nenhuma das anteriores", alternativa
  visivelmente mais longa ou mais detalhada que as outras.
- As 4 alternativas devem ter comprimento e nível de detalhe semelhantes.

ENUNCIADOS:
- Apresente uma SITUAÇÃO e pergunte o que se aplica. Não peça a definição do termo.
- Pelo menos 1 item deve ser de aplicação num cenário do contexto <background do aluno>.
- Pelo menos 1 item deve exigir distinguir este conceito daquele com que ele é confundido.

FEEDBACK (obrigatório em todo item):
- Explique por que a correta é correta.
- Explique, uma a uma, por que CADA errada é errada. É aqui que o teste ensina.
```

**Quiz integrador da etapa** — troque o bloco `[ESCOPO]` para abranger todos os subtópicos e
use:

```
[FORMATO]
Produza um teste de múltipla escolha com 10 a 12 itens cobrindo TODOS os subtópicos desta
etapa, misturados — nunca agrupados por subtópico.

COMPOSIÇÃO:
- Ao menos 1 item de cada subtópico.
- 3 itens que só podem ser resolvidos decidindo QUAL dos subtópicos se aplica ao cenário
  apresentado. Estes são o objetivo do teste: o aluno precisa escolher a ferramenta, não
  aplicar a que já lhe foi entregue.
- 1 item de transferência: o mesmo conceito numa superfície nova (outro setor, outra escala,
  outro domínio).

Valem todas as regras de distratores e de feedback do teste de subtópico.
Embaralhe a ordem dos itens para que subtópicos consecutivos não fiquem juntos.
```

## 6. Parâmetros do `studio_create`

```python
# por subtópico
studio_create(notebook_id=<id>, artifact_type="quiz",
              focus_prompt=<...>, question_count=8, difficulty="medium",
              language=<idioma>)

# integrador da etapa
studio_create(notebook_id=<id>, artifact_type="quiz",
              focus_prompt=<...>, question_count=12, difficulty="hard",
              language=<idioma>)
```

Renomeie para `E<n>.<m> · <Subtópico> — Quiz` e `E<n> · Quiz integrador`.

## 7. Relação com o recall da Fase 3 — não confunda os dois

O quiz do NotebookLM **não substitui** o recall da Fase 3, e o `PERFIL.md` não deve ser lido
como se substituísse. São coisas diferentes:

| | Quiz (NotebookLM) | Recall (Fase 3, agente) |
|---|---|---|
| Formato | Reconhecimento entre 4 opções | **Produção ativa** (cloze progressivo) |
| Quem conduz | O aluno, sozinho | O agente, com dica calibrada |
| Vai para o `srs.db`? | Não | **Sim** — é a fonte da verdade |

O quiz é ensaio; o recall é a medida. O mastery do NotebookLM continua secundário
(`AGENTS.md` → regras inquebráveis).

## 8. O que invalida o artefato

- Distrator que ninguém escolheria → o item não testa nada.
- "Todas as anteriores" em qualquer item.
- Enunciado pedindo definição em vez de aplicação.
- Feedback que só diz qual é a correta.
- Integrador agrupado por subtópico → deixou de ser intercalado.

## 9. Checklist

- [ ] Um quiz por subtópico (5–8 itens) + um integrador da etapa (10–12 itens)
- [ ] Todo distrator vem de uma confusão real e nomeável
- [ ] Nenhum "todas/nenhuma das anteriores"
- [ ] Feedback explica cada alternativa errada
- [ ] Integrador tem 3 itens de escolha entre subtópicos + 1 de transferência
- [ ] Idioma do PERFIL, títulos no padrão
