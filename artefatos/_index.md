# Artefatos do NotebookLM — regras de geração

> **Este diretório é harness.** Cada arquivo descreve *como estruturar um tipo de artefato*,
> nunca *o que* está sendo estudado. Nome de matéria, conceito ou exemplo de disciplina
> específica **não entram aqui** — ver `AGENTS.md` → "Onde escrever cada coisa".
>
> Um arquivo por tipo, nomeado com o `artifact_type` exato do MCP, para o agente não ter de
> traduzir nome nenhum na hora de chamar a ferramenta.
>
> **Quem vai gerar lê dois arquivos: este índice + o arquivo do tipo.** Nunca só um.
> A base científica de todas as regras está em [`REFERENCIAS.md`](REFERENCIAS.md).

---

## 1. A regra que governa tudo: um artefato por SUBTÓPICO

Um artefato por **etapa** trata 5 conceitos como se fossem um só. O resultado é o material
raso que todo mundo conhece: o áudio de 20 minutos que passa 3 minutos em cada coisa, o deck
de 40 slides que ninguém termina, o quiz que faz uma pergunta por conceito e não descobre nada.

O padrão deste sistema é o oposto:

```
etapa  →  decompõe em 3 a 6 subtópicos  →  gera o conjunto de artefatos DE CADA subtópico
                                        →  gera os artefatos integradores DA ETAPA
```

**Por que.** É o **princípio da segmentação** (Mayer): material fatiado em unidades
autocontidas, no ritmo do aluno, produz ganho consistente de transferência
(g ≈ 0,32–0,36 em meta-análise de 56 estudos — Rey et al., 2019). O efeito é **maior em
tratamentos curtos**, que é exatamente o caso aqui. Some a isso o dado de engajamento: o tempo
mediano de atenção em material audiovisual satura em ~6 minutos, independente da duração total
(Guo et al., 2014). Um artefato de etapa inteira desperdiça tudo que passa disso.

O ganho não é só de atenção — é de **testabilidade**. Um subtópico é a menor unidade que dá
para cobrar sozinha no recall da Fase 3. Se o artefato mistura cinco, o erro do aluno não
aponta para lugar nenhum.

---

## 2. Como decompor uma etapa em subtópicos

Os subtópicos saem dos **conceitos obrigatórios da etapa** no roadmap — não são um recorte novo,
são um agrupamento daquilo que já foi aprovado pelo aluno.

**Os quatro testes.** Um subtópico só é válido se passar nos quatro:

| Teste | Pergunta | Se falhar |
|---|---|---|
| **Autonomia** | Dá para explicar isto sem precisar de um subtópico **posterior**? | Reordene, ou funda com o que ele depende |
| **Tamanho** | Cabe em ~6 minutos de explicação contínua? | Quebre em dois |
| **Testabilidade** | Gera pelo menos uma pergunta de recall que **não** serve para os outros subtópicos? | Não é subtópico — é detalhe de outro |
| **Contraste** | Se dois conceitos só existem em oposição (X vs. Y), eles estão **juntos**? | Funda os dois num subtópico só |

O teste do contraste é o que mais se erra. Separar em dois artefatos um par que só faz sentido
comparado destrói justamente a discriminação que o aluno precisa treinar (Schwartz & Bransford,
1998). Par contrastivo é **um** subtópico, com os dois lados dentro.

**Quantidade: 3 a 6 por etapa.**
Menos de 3 quase sempre significa que a etapa está grande demais e deveria ser duas.
Mais de 6, idem — ou os subtópicos estão fatiados fino demais e viraram tópicos frasais.

**Ordem = dependência.** O subtópico 1 é o que não depende de nenhum outro. O aluno consome
na ordem numerada.

**Onde os subtópicos ficam registrados.** No roadmap, dentro da etapa (campo `subtopicos`).
Eles são propostos na primeira PREP da etapa e **não mudam** enquanto a etapa estiver aberta —
se mudassem, os artefatos já gerados deixariam de casar com o recall.

---

## 3. Matriz de granularidade — o que é por subtópico e o que é por etapa

Nem todo artefato deve ser fatiado. Existem dois papéis, e confundi-los é o erro clássico:

- **Artefato de aquisição** — ensina *uma* coisa. Ganha com o corte. → **um por subtópico**
- **Artefato integrador** — mostra como as coisas *se ligam*. Cortado, perde a razão de existir.
  Um mapa mental de um conceito só é um retângulo. → **um por etapa, cobrindo todos os subtópicos**

| `artifact_type` | Arquivo | Granularidade | Por quê |
|---|---|---|---|
| `audio` | [`audio.md`](audio.md) | **subtópico** | Segmentação + saturação de atenção em ~6 min |
| `video` | [`video.md`](video.md) | **subtópico** | Idem, com evidência direta de engajamento (Guo et al., 2014) |
| `slide_deck` | [`slide_deck.md`](slide_deck.md) | **subtópico** | Uma asserção por slide só funciona com escopo estreito |
| `report` | [`report.md`](report.md) | **subtópico** | Guia de estudo por conceito, não apostila de etapa |
| `infographic` | [`infographic.md`](infographic.md) | **subtópico** | Um mecanismo por imagem; dois viram poluição visual |
| `quiz` | [`quiz.md`](quiz.md) | **subtópico** + **1 integrador da etapa** | Diagnóstico por conceito + um final que força discriminação |
| `flashcards` | [`flashcards.md`](flashcards.md) | **subtópico** | Um fato por card; o deck espelha o subtópico |
| `mind_map` | [`mind_map.md`](mind_map.md) | **etapa** | O valor está nas arestas **entre** subtópicos |
| `data_table` | [`data_table.md`](data_table.md) | **etapa** | Existe para contrastar subtópicos entre si |

Quais tipos entram no conjunto padrão é decisão do aluno (`estudo/PERFIL.md` → "Produção no
NotebookLM"). **A granularidade não é** — ela é regra do sistema, não preferência.

---

## 4. Controle de volume — antes de gerar, faça a conta

```
total = (tipos_por_subtópico × nº de subtópicos) + tipos_por_etapa
```

Cinco tipos por subtópico com cinco subtópicos são 25 artefatos: tempo de geração longo, e um
aluno olhando para uma lista que ele não vai consumir. Material que não se consome não ensina.

| Total | O que fazer |
|---|---|
| ≤ 12 | Gere direto |
| 13 a 20 | Gere, mas **avise o volume** e diga a ordem de consumo recomendada |
| > 20 | **Pare e pergunte.** Proponha cortar tipos por subtópico (mantendo 2–3) ou dividir a etapa |

**Recomendação de conjunto enxuto:** 2 a 3 tipos por subtópico — um de exposição (`audio`,
`video` ou `slide_deck`), um de consolidação (`report` ou `infographic`) e um de teste (`quiz`
ou `flashcards`) — mais os integradores da etapa. Isso cobre aquisição, elaboração e recuperação
sem inflar a fila.

---

## 5. O esqueleto do `focus_prompt` — comum a todos os tipos

Todo `focus_prompt` é montado assim. Os blocos `[ESCOPO]`, `[IDIOMA]` e `[ALUNO]` são
**idênticos** para qualquer tipo; só o `[FORMATO]` muda, e ele vem do arquivo do tipo.

```
[ESCOPO]
Este material cobre EXCLUSIVAMENTE o subtópico "<subtópico>" da etapa <N> de <matéria>.
Cubra TODOS estes pontos, sem exceção: <conceitos do subtópico>.
NÃO mencione, nem de passagem, nem como comparação: <conceitos dos OUTROS subtópicos desta
etapa> e <o que está fora de escopo da etapa, do roadmap>.
Se algo necessário não estiver nas fontes, diga que não está — não complete por conta própria.

[IDIOMA]
Produza 100% do conteúdo em <idioma do PERFIL>. Títulos, rótulos e legendas incluídos.

[ALUNO]
Nível: <nível>. Background: <área>. Ancore os exemplos nesse contexto.
Não explique: <o que evitar, do PERFIL>.

[FORMATO]
<bloco específico — copiado do arquivo do tipo em artefatos/>
```

**As três travas que nunca saem:**

1. **A lista fechada de conceitos do subtópico** — sem ela o artefato divaga.
2. **A proibição explícita de citar os outros subtópicos** — é o que faz a segmentação existir
   de fato. Sem essa linha, o modelo "contextualiza" e reintroduz a etapa inteira em cada peça,
   e você volta a ter um artefato único, só que repetido N vezes.
3. **O idioma** — passe também no parâmetro `language` do `studio_create`, não só no texto.

---

## 6. Operação

**Nomeie tudo.** Com 15 artefatos na tela, nome importa mais que conteúdo. Logo após criar,
renomeie com `studio_status(action="rename", artifact_id=..., new_title=...)` no padrão:

```
E<etapa>.<subtópico> · <Nome do subtópico> — <Tipo>
E2.3 · <Subtópico> — Slides
E2 · Mapa mental da etapa            ← integradores não levam número de subtópico
```

**Dispare em lote, depois verifique em lote.** Chame todos os `studio_create` do subtópico e só
então varra com `studio_status`. Não bloqueie esperando um a um.

**Entregue com ordem de consumo.** A lista para o aluno sai numerada por subtópico, não agrupada
por tipo — ele consome o subtópico 1 inteiro antes do 2.

---

## 7. Checklist de aceite (vale para qualquer tipo)

Antes de dizer ao aluno que o material está pronto:

- [ ] Existe **um artefato por subtópico** de cada tipo marcado como "por subtópico" no PERFIL
- [ ] Os integradores da etapa foram gerados **depois** e cobrem **todos** os subtópicos
- [ ] Nenhum artefato de subtópico cita conceito de outro subtópico ou de etapa futura
- [ ] Todos saíram no idioma do PERFIL
- [ ] Todos foram renomeados no padrão `E<n>.<m> · <subtópico> — <tipo>`
- [ ] A conta do volume foi feita e, se passou de 12, o aluno foi avisado
- [ ] `fase2_iniciada_em` foi gravado no ledger
