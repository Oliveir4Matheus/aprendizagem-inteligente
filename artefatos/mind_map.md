---
artifact_type: mind_map
granularidade: etapa
papel: integrador
---

# `mind_map` — Mapa mental

> Leia junto com [`_index.md`](_index.md). Referências em [`REFERENCIAS.md`](REFERENCIAS.md).

## 1. Granularidade: **um por ETAPA** — e este é o ponto do arquivo

Todos os outros artefatos de aquisição são fatiados por subtópico. Este **não é**, e a razão é
estrutural: o valor de um mapa está nas **arestas entre os subtópicos**. Um mapa mental de um
subtópico isolado é um nó central com três folhas — não ensina relação nenhuma, porque não há
relação para mostrar.

Fatiar o integrador destrói exatamente aquilo que ele existe para produzir.

> **Regra:** gere o mapa **depois** de todos os artefatos de subtópico da etapa. Ele é o fecho,
> não a abertura. Antes de existirem as partes, não há o que integrar.

## 2. Base científica

| Regra | Fundamento |
|---|---|
| O mapa vale a pena | Nesbit & Adesope (2006): 67 tamanhos de efeito, 55 estudos, 5.818 participantes — diagramas nó-aresta aumentam retenção frente a texto corrido |
| Construir supera só olhar | Schroeder et al. (2018), 142 tamanhos de efeito |
| Um por etapa, não por subtópico | O ganho está na estrutura relacional entre conceitos |
| Toda aresta tem rótulo | Aresta sem rótulo comunica vizinhança temática, não relação — e vizinhança não é conhecimento |
| Incluir pontes para etapas anteriores | Conhecimento novo adere ao existente; é o `conecta_com` do roadmap |

O achado de que **construir** supera **estudar** o mapa tem uma consequência direta neste
sistema: o mapa gerado pelo NotebookLM é o material de conferência, e o mapa que o **aluno**
constrói é `estudo/progresso/<materia>-mapa.md` (Fase 3, passo 5b da `SKILL.md`). Não confunda
os dois — ver §5.

## 3. Estrutura obrigatória

```
                    <nó raiz: a etapa>
                            │
      ┌──────────┬──────────┼──────────┬──────────┐
   subtóp.1   subtóp.2   subtóp.3   subtóp.4   subtóp.5
      │           │          │          │          │
   conceitos   conceitos  conceitos  conceitos  conceitos
      └────────── arestas rotuladas entre subtópicos ─────┘
                            ╎
                   ╎ pontes tracejadas ╎
                            ╎
              conceitos de etapas ANTERIORES
```

| Elemento | Regra |
|---|---|
| Raiz | O nome da etapa |
| Nível 1 | **Um nó por subtópico** — a estrutura do mapa espelha a decomposição |
| Nível 2 | Os conceitos obrigatórios de cada subtópico |
| Arestas laterais | Ligações **entre** subtópicos, sempre com rótulo dizendo a relação |
| Pontes | Ligações para conceitos de etapas anteriores (`conecta_com`), marcadas como tal |

## 4. Bloco `[FORMATO]` do `focus_prompt`

O `[ESCOPO]` deste artefato é a **etapa inteira** — liste todos os subtópicos, e mantenha a
proibição de avançar para etapas futuras.

```
[FORMATO]
Produza UM mapa mental da etapa inteira.

ESTRUTURA:
- Nó raiz: <nome da etapa>.
- Primeiro nível: um nó para CADA subtópico desta etapa: <lista dos subtópicos>.
- Segundo nível: os conceitos obrigatórios dentro de cada subtópico.

AS ARESTAS SÃO O CONTEÚDO — não a hierarquia:
- Toda ligação precisa de um RÓTULO dizendo QUAL é a relação: "é pré-requisito de",
  "é o oposto de", "é caso particular de", "costuma ser confundido com", "causa",
  "é medido por". Aresta sem rótulo comunica apenas proximidade temática, e proximidade
  temática não é conhecimento.
- Desenhe explicitamente as ligações ENTRE subtópicos diferentes, não só de cima para baixo.
  São elas que impedem a etapa de virar cinco assuntos soltos na cabeça do aluno.
- Marque como PONTE as ligações para conceitos de etapas anteriores: <conceitos já dominados
  e a natureza da ligação>.

PROIBIDO: incluir conceito de etapa futura; criar nó sem conteúdo só para equilibrar o
desenho; usar cor ou ícone que não signifique nada.
```

## 5. Não confunda com o mapa conceitual do aluno

| | `mind_map` (NotebookLM) | `<materia>-mapa.md` (workspace) |
|---|---|---|
| Quem constrói | A IA, a partir das fontes | O **agente**, registrando o que o aluno dominou |
| Escopo | Uma etapa | A **matéria inteira**, cumulativo |
| Quando muda | Regerado a cada etapa | Cresce **a cada conceito dominado**, nunca é reescrito |
| Para que serve | Conferir se a estrutura da etapa fecha | Mostrar ao aluno onde o novo encaixa no que ele já sabe |

O do NotebookLM é descartável. O do workspace, não — e a regra de nunca reescrevê-lo do zero
continua valendo (`SKILL.md`, Fase 3, passo 5b).

Uso prático do mapa gerado: **comparar** com o mapa do aluno. Aresta que a IA desenhou e o
aluno não tem é uma relação que ele ainda não enxergou — vira pergunta de síntese no recall.

## 6. Parâmetros do `studio_create`

```python
studio_create(
    notebook_id = <id>,
    artifact_type = "mind_map",
    focus_prompt = <[ESCOPO da etapa] + [IDIOMA] + [ALUNO] + [FORMATO]>,
    title = "E<n> · Mapa mental da etapa",
    language = <idioma do PERFIL>,
)
```

## 7. O que invalida o artefato

- Um mapa por subtópico → não é integrador; é um nó com folhas.
- Arestas sem rótulo.
- Só hierarquia vertical, nenhuma ligação entre subtópicos.
- Conceito de etapa futura no mapa.
- Gerado antes dos artefatos de subtópico.

## 8. Checklist

- [ ] **Um** mapa para a etapa, gerado por último
- [ ] Primeiro nível = um nó por subtópico
- [ ] Toda aresta tem rótulo de relação
- [ ] Existem ligações entre subtópicos, não só verticais
- [ ] Pontes para etapas anteriores marcadas
- [ ] Comparado com `<materia>-mapa.md`; divergências viraram pergunta de síntese
- [ ] Idioma do PERFIL, título no padrão
