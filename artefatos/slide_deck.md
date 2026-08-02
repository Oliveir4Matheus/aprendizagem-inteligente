---
artifact_type: slide_deck
granularidade: subtopico
papel: aquisicao
---

# `slide_deck` — Apresentação

> Leia junto com [`_index.md`](_index.md). Referências em [`REFERENCIAS.md`](REFERENCIAS.md).

## 1. Granularidade: **um por subtópico**

**6 a 12 slides por subtópico.** Um deck de etapa inteira chega a 40 slides, e a essa altura o
formato já se rendeu: vira lista de tópicos rolando, que é exatamente o formato que a evidência
reprova.

## 2. A decisão de formato: asserção-evidência, não tópicos

Esta é a regra mais importante do arquivo, e a que mais contraria o hábito.

**Slide tradicional:** título é um substantivo (`Tipos de X`), corpo é uma lista de bullets.
**Slide asserção-evidência:** título é uma **frase completa que afirma o ponto**, corpo é **uma
evidência visual** que sustenta aquela frase. Sem lista.

| | Tópico-subtópico | Asserção-evidência |
|---|---|---|
| Título | `Características de <X>` | `<X> falha quando <condição>, porque <mecanismo>` |
| Corpo | 5 bullets | um diagrama, gráfico ou esquema com rótulos colados |
| O que o aluno leva | uma palavra-chave | uma proposição que ele consegue repetir |

**Por quê.** Alley et al. mostraram que princípios colocados no título-frase são recordados mais
do que os mesmos princípios colocados em bullets. Garner & Alley (2013) foram além: o grupo
asserção-evidência recordou melhor o processo, entendeu mais fundo, e a vantagem **persistiu no
teste adiado de uma semana** — em todos os tipos de questão. Retenção adiada é justamente o que
este sistema otimiza.

O bullet perde por um motivo mecânico: ele obriga o aluno a inferir a proposição que liga os
itens. Quem já sabe infere; quem está aprendendo, não — e é ele que está na frente do slide.

## 3. Base científica

| Regra | Fundamento |
|---|---|
| Título é frase completa afirmando o ponto | Alley & Neeley, 2005; Garner & Alley, 2013 |
| Corpo é evidência visual, não lista | Idem + princípio multimídia, g ≈ 0,39 |
| Uma ideia por slide | Segmentação (Rey et al., 2019) |
| Rótulo colado ao elemento da figura | Contiguidade espacial, g ≈ 0,74 — o maior efeito da CTML |
| Sem texto que só repita o que já está na figura | Princípio da redundância |
| Sem imagem decorativa, sem ícone de enfeite | Princípio da coerência |
| Slide final de recuperação | Efeito do teste (Roediger & Karpicke, 2006) |

## 4. Estrutura obrigatória do deck

| # | Slide | Título |
|---|---|---|
| 1 | **Pergunta** | A pergunta que o subtópico responde (é o único slide cujo título é pergunta) |
| 2 | **Ancoragem** | Uma asserção ligando ao conceito já dominado |
| 3…n-2 | **Asserções** | Uma por slide, cada uma com sua evidência visual |
| n-1 | **Contraste** | `<X> se distingue de <Y> por <critério>` — com os dois lado a lado |
| n | **Recuperação** | 3 perguntas, **sem as respostas** |

O slide de recuperação não traz resposta de propósito. Resposta na tela transforma recuperação
em reconhecimento, e reconhecimento não é o que produz retenção.

## 5. Bloco `[FORMATO]` do `focus_prompt`

```
[FORMATO]
Produza uma apresentação de 6 a 12 slides sobre este subtópico, na estrutura
ASSERÇÃO-EVIDÊNCIA:

REGRA CENTRAL — vale para TODOS os slides de conteúdo:
- O TÍTULO de cada slide é uma FRASE COMPLETA que afirma o ponto daquele slide (sujeito,
  verbo, complemento). Nunca um substantivo ou rótulo temático.
  Errado: "Características de <X>"
  Certo:  "<X> falha quando <condição>, porque <mecanismo>"
- O CORPO é UMA evidência visual que sustenta o título: diagrama, esquema, gráfico ou
  comparação. NÃO use lista de tópicos. NÃO use bullets em nenhum slide.
- Uma única ideia por slide. Se precisar de duas frases-título, são dois slides.

ESTRUTURA:
1. Slide 1: a pergunta que este subtópico responde.
2. Slide 2: uma asserção ligando ao que o aluno já domina: <conceito anterior + ligação>.
3. Slides seguintes: uma asserção por conceito do subtópico, cada uma com sua evidência.
4. Penúltimo slide: o contraste — "<X> se distingue de <Y> por <critério>" — com os dois
   representados lado a lado na mesma imagem.
5. Último slide: 3 perguntas de recuperação, SEM as respostas.

REGRAS VISUAIS:
- Ponha cada rótulo COLADO ao elemento que ele nomeia dentro da figura. Nada de legenda
  separada, nada de numeração que obrigue o olho a ir e voltar.
- Não escreva no corpo um texto que apenas repita o que a figura já mostra.
- Sem imagem decorativa, sem ícone de enfeite, sem fundo temático.
```

## 6. Parâmetros do `studio_create`

```python
studio_create(
    notebook_id = <id>,
    artifact_type = "slide_deck",
    focus_prompt = <[ESCOPO] + [IDIOMA] + [ALUNO] + [FORMATO]>,
    slide_format = "detailed_deck",  # opções: studio_status(action="list_types")
    slide_length = "default",
    orientation = "landscape",
    language = <idioma do PERFIL>,
)
```

Depois: `studio_status(action="rename", ..., new_title="E<n>.<m> · <Subtópico> — Slides")`.

> `studio_revise` permite corrigir **slides individuais** sem regerar o deck. Se só o slide de
> contraste saiu errado, revise aquele slide — não jogue fora um deck inteiro que estava bom.

## 7. O que invalida o artefato

- Qualquer slide com lista de tópicos → regere; é o erro que o formato existe para evitar.
- Título substantivo (`Tipos de X`) em slide de conteúdo.
- Mais de 12 slides → o subtópico está grande demais, ou o deck é de etapa.
- Rótulos em legenda separada da figura.
- Slide de recuperação com as respostas visíveis.

## 8. Checklist

- [ ] 6–12 slides, um deck por subtópico
- [ ] **Zero** bullets no deck inteiro
- [ ] Todo título de conteúdo é frase completa afirmando o ponto
- [ ] Toda asserção tem evidência visual, com rótulos colados
- [ ] Slide de contraste presente
- [ ] Slide final com 3 perguntas sem resposta
- [ ] Idioma do PERFIL, título no padrão
