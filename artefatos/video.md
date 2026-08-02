---
artifact_type: video
granularidade: subtopico
papel: aquisicao
---

# `video` — Video Overview

> Leia junto com [`_index.md`](_index.md). Referências em [`REFERENCIAS.md`](REFERENCIAS.md).

## 1. Granularidade: **um por subtópico**

Este é o tipo com a evidência mais direta a favor do corte. Guo et al. (2014), analisando
milhões de sessões de vídeo, encontraram engajamento mediano saturando em ~6 minutos
**independentemente da duração total** — e alunos assistindo a menos de um quarto de vídeos
com mais de 12 minutos. Vídeo de etapa inteira não é um vídeo longo: é um vídeo curto seguido
de material que ninguém viu.

**Alvo de duração: 4 a 6 minutos.** Acima de 8, quebre o subtópico em dois.

## 2. Para que serve — e para que não serve

O vídeo é o único artefato com **os dois canais simultâneos e sincronizados**. Ele deve ser
gasto onde isso importa: processo, sequência temporal, transformação, causa e efeito — coisas
que mudam ao longo do tempo e por isso não cabem numa imagem parada.

Se o conteúdo do subtópico é uma definição, uma taxonomia ou uma lista de critérios, o vídeo é
o artefato **errado**: use `infographic` ou `report`. Vídeo de conteúdo estático é slide caro.

## 3. Base científica

| Regra | Fundamento |
|---|---|
| 4–6 min por vídeo, um por subtópico | Guo et al., 2014; segmentação (Rey et al., 2019) |
| Narração explica, imagem estrutura — nunca os dois dizendo o mesmo | Princípio da redundância; texto na tela idêntico à narração piora a aprendizagem |
| Sinalizar o que olhar (destaque, seta, cor) | Princípio da sinalização, g ≈ 0,38 |
| Rótulo colado no elemento, não em legenda separada | Princípio da contiguidade espacial — **o maior efeito da CTML**, g ≈ 0,74 |
| Nada de música de fundo, transição elaborada ou imagem decorativa | Princípio da coerência (Mayer; Sweller, 1988) |
| Pausa com pergunta no meio | Aprendizagem ativa embutida (Brame, 2016); efeito do teste (Roediger & Karpicke, 2006) |
| Tom conversacional | Princípio da personalização, mediana d ≈ 1,11 |

## 4. Estrutura obrigatória

| Bloco | Duração | O que tem |
|---|---|---|
| **Pergunta-título** | ~15 s | A tela abre com a pergunta que o vídeo responde |
| **Ancoragem** | ~20 s | Ligação ao que o aluno já domina |
| **Desenvolvimento** | 3–4 min | O processo, em passos visíveis. Cada passo aparece na tela **enquanto** é narrado |
| **Pausa ativa** | ~20 s | Uma pergunta na tela, com alguns segundos de silêncio antes da resposta |
| **Fecho** | ~30 s | O critério que distingue este conceito do que se confunde com ele |

## 5. Bloco `[FORMATO]` do `focus_prompt`

```
[FORMATO]
Produza um vídeo explicativo de 4 a 6 minutos sobre este subtópico.

ESTRUTURA:
1. Abra com a pergunta que o vídeo responde, escrita na tela (~15s).
2. Ancore no que o aluno já domina: <conceito anterior + natureza da ligação> (~20s).
3. Desenvolva o mecanismo em passos visíveis (3-4 min). Cada passo aparece na tela no momento
   exato em que é narrado.
4. No meio, faça UMA pausa ativa: uma pergunta na tela e alguns segundos de silêncio antes da
   resposta.
5. Feche com o critério que distingue este conceito daquele com que ele é confundido (~30s).

REGRAS VISUAIS (obrigatórias):
- A narração explica; a imagem estrutura. NUNCA ponha na tela o mesmo texto que está sendo
  narrado — texto idêntico à fala atrapalha a compreensão em vez de reforçar.
- Texto na tela: só rótulos e palavras-chave. Nada de parágrafo.
- Ponha o rótulo COLADO ao elemento que ele nomeia. Não use legenda separada nem numeração
  que obrigue o olho a ir e voltar.
- Sinalize o que olhar: destaque, seta ou cor no elemento em foco a cada momento.
- Sem música de fundo, sem transições elaboradas, sem imagem decorativa. Todo pixel que não
  ensina está tirando espaço de memória de trabalho de quem está aprendendo.

Tom da narração: conversacional, segunda pessoa.
```

## 6. Parâmetros do `studio_create`

```python
studio_create(
    notebook_id = <id>,
    artifact_type = "video",
    focus_prompt = <[ESCOPO] + [IDIOMA] + [ALUNO] + [FORMATO]>,
    video_format = "explainer",   # opções: studio_status(action="list_types")
    video_style_prompt = "diagramas limpos, rótulos colados aos elementos, sem imagem decorativa",
    language = <idioma do PERFIL>,
)
```

Depois: `studio_status(action="rename", ..., new_title="E<n>.<m> · <Subtópico> — Vídeo")`.

## 7. O que invalida o artefato

- Passa de 8 minutos.
- A tela repete a narração palavra por palavra → redundância; regere com a regra explícita.
- Rótulos em legenda separada do desenho → perde o efeito maior da CTML.
- Conteúdo estático (definição, taxonomia) num vídeo → tipo errado de artefato.
- Sem pausa ativa → consumo passivo.

## 8. Checklist

- [ ] Um vídeo por subtópico, 4–6 min
- [ ] Conteúdo é processo/sequência (senão, o tipo está errado)
- [ ] Narração e tela dizem coisas **diferentes e complementares**
- [ ] Rótulos colados aos elementos
- [ ] Uma pausa ativa com pergunta
- [ ] Idioma do PERFIL, título no padrão
