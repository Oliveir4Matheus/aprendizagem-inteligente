---
artifact_type: infographic
granularidade: subtopico
papel: consolidacao
---

# `infographic` — Infográfico

> Leia junto com [`_index.md`](_index.md). Referências em [`REFERENCIAS.md`](REFERENCIAS.md).

## 1. Granularidade: **um por subtópico**

Um infográfico por subtópico, **um mecanismo por imagem**. Infográfico de etapa inteira vira
pôster: muita coisa, nada legível, e o aluno olha por três segundos. A imagem tem um orçamento
de atenção pequeno e não negociável — gaste tudo num conceito só.

## 2. Para que serve

O infográfico é a peça de **codificação dupla** (Paivio): a mesma informação entra pela via
verbal e pela via imagética, e material assim codificado é consistentemente mais lembrado —
efeitos tipicamente entre 0,5 e 1,0 DP (Clark & Paivio, 1991).

Mas o ganho só existe se a imagem **fizer trabalho cognitivo**. Imagem que ilustra o que o
texto já disse não é dupla codificação: é redundância, e redundância atrapalha.

**Conteúdo que rende infográfico:**

| Rende | Não rende |
|---|---|
| Processo em passos | Definição isolada |
| Relação de causa e efeito | Texto conceitual abstrato sem estrutura espacial |
| Estrutura hierárquica (o que contém o quê) | Lista de itens sem relação entre si |
| Comparação de duas coisas em eixos claros | Argumento longo |
| Fluxo de decisão (se X, então Y) | — |

Se o subtópico não tem estrutura espacial, **não gere infográfico** — gere `report`. Forçar o
tipo produz uma lista bonita com ícones, que é exatamente o material que o princípio da
coerência reprova.

## 3. Base científica

| Regra | Fundamento |
|---|---|
| Um mecanismo por imagem | Segmentação (Rey et al., 2019) + limite de atenção da peça visual |
| Imagem carrega estrutura, texto carrega nome | Codificação dupla (Paivio, 1986; Clark & Paivio, 1991) |
| Rótulo colado ao elemento, nunca em legenda | **Contiguidade espacial, g ≈ 0,74 — o maior efeito da CTML** |
| Zero ícone decorativo, zero fundo temático | Princípio da coerência |
| Máximo ~7 elementos | Limite da memória de trabalho (Sweller, 1988) |
| Texto só em rótulo e frase curta | Redundância: parágrafo dentro de imagem é o pior dos dois mundos |

## 4. Estrutura obrigatória

| Zona | O que tem |
|---|---|
| **Título** | Uma frase completa afirmando o ponto (mesma lógica do `slide_deck`) |
| **Corpo** | O diagrama: no máximo 7 elementos, com as relações desenhadas (setas rotuladas) |
| **Rótulos** | Colados aos elementos, dentro da figura |
| **Rodapé** | Uma linha: o critério que distingue este conceito do parecido |

## 5. Bloco `[FORMATO]` do `focus_prompt`

```
[FORMATO]
Produza UM infográfico sobre este subtópico, cobrindo UM mecanismo só.

TÍTULO: uma frase completa que afirma o ponto do infográfico (sujeito, verbo, complemento).
Não use um substantivo temático como título.

CORPO — a imagem precisa fazer trabalho cognitivo, não ilustrar:
- Represente a ESTRUTURA do conceito: os passos do processo, a cadeia de causa e efeito, a
  hierarquia, ou os dois lados da comparação.
- No máximo 7 elementos no total. Se precisar de mais, o subtópico está grande demais.
- Toda relação entre elementos é uma SETA COM RÓTULO dizendo qual é a relação. Seta sem
  rótulo não ensina nada — só sugere vizinhança.
- Ponha cada rótulo COLADO ao elemento que ele nomeia, dentro da figura. NUNCA use legenda
  separada, numeração de referência, ou lista de nomes fora do desenho.

TEXTO:
- Só rótulos e frases de no máximo uma linha. Nenhum parágrafo dentro da imagem.
- Não escreva em texto o que a imagem já mostra.

PROIBIDO: ícone decorativo, fundo temático, ilustração de pessoas, paleta chamativa,
elemento gráfico que não representa nada do conteúdo.

RODAPÉ: uma linha com o critério que distingue este conceito daquele com que ele é confundido.
```

## 6. Parâmetros do `studio_create`

```python
studio_create(
    notebook_id = <id>,
    artifact_type = "infographic",
    focus_prompt = <[ESCOPO] + [IDIOMA] + [ALUNO] + [FORMATO]>,
    infographic_style = "auto_select",   # opções: studio_status(action="list_types")
    visual_style = "auto_select",
    orientation = "portrait",            # infográfico é lido de cima para baixo
    language = <idioma do PERFIL>,
)
```

Renomeie para `E<n>.<m> · <Subtópico> — Infográfico`.

## 7. O que invalida o artefato

- Mais de ~7 elementos → ilegível.
- Rótulos em legenda separada → perde o maior efeito disponível.
- Setas sem rótulo.
- Ícones decorativos, ilustrações de pessoas, fundo temático.
- Parágrafo dentro da imagem.
- Subtópico sem estrutura espacial → tipo errado; era `report`.

## 8. Checklist

- [ ] Um infográfico por subtópico, um mecanismo só
- [ ] Título é frase completa
- [ ] ≤ 7 elementos, todas as setas rotuladas
- [ ] Rótulos colados aos elementos
- [ ] Zero decoração
- [ ] Rodapé com o critério de distinção
- [ ] Idioma do PERFIL, título no padrão
