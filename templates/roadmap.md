---
# ===== TRILHA DA MATÉRIA (o roteiro que impede a IA de "vazar" pra frente) =====
materia: Nome da Matéria
aprovado_em: AAAA-MM-DD        # data em que o aluno aprovou esta trilha
etapa_atual: 1
total_etapas: 6
---

# Roadmap — <Nome da Matéria>

> **Como este arquivo nasce:** ao começar uma matéria, o agente lê a fonte em
> `estudo/documentos/` (e, se precisar, pesquisa a ementa/edital da certificação),
> **propõe** esta trilha, e só grava depois do seu OK. Ver `COOKBOOK.md` → Parte B.
>
> **Como ele é usado:** o agente extrai daqui os **conceitos obrigatórios da etapa
> atual**, agrupa-os nos **subtópicos** declarados na etapa, e injeta a lista de cada
> subtópico no `focus_prompt` dos artefatos daquele subtópico e nas perguntas do recall.
> É o trilho que impede o material de avançar para etapas futuras.
>
> **Este arquivo é conteúdo de estudo** — vive em `estudo/` e nunca vai para o git.

O estudo segue estas etapas **em ordem**, sem pular nem adiantar conceitos de etapas
posteriores. Mas as etapas **não são silos**: cada uma declara com quais anteriores ela
se conecta e para quais futuras ela prepara. Essas conexões não são enfeite — o agente
as usa para montar o recall (ver abaixo).

> ## Como as conexões são usadas
>
> | Campo | Para que serve |
> |---|---|
> | `conecta_com` | De onde saem as perguntas **intercaladas** do recall. O aluno precisa decidir *qual* conceito se aplica — é isso que treina discriminação, e é isso que a prática em blocos não treina. |
> | `prepara_para` | A **prévia estruturante** no fim da etapa: uma apresentação de 2–3 frases do que vem, para o aluno ter onde pendurar o próximo conteúdo. Só apresentação — não se ensina nem se cobra o que ainda não foi dado. |
> | ambos | As perguntas de **síntese**, que exigem combinar esta etapa com uma anterior. É o quebra-cabeça fechando. |

## Etapa 1 — <Nome da etapa>

**Status:** `em_andamento`  <!-- nao_iniciada | em_andamento | dominada -->

Conceitos obrigatórios (o artefato e o recall precisam cobrir **todos**):

- **<Conceito A>**: <o que exatamente o aluno precisa saber sobre ele>
- **<Conceito B>**: <idem — inclua a distinção contra o conceito que costuma ser confundido>
- **<Conceito C>**: <idem>

**subtopicos:** _(preenchido na primeira PREP da etapa; congelado até ela fechar)_

| # | Subtópico | Conceitos que ele cobre |
|---|---|---|
| 1 | <Subtópico 1> | <Conceito A> |
| 2 | <Subtópico 2> | <Conceito B>, <Conceito C> |

> **Como agrupar** (`artefatos/_index.md` §2): 3 a 6 subtópicos, cada um autônomo (não depende
> de subtópico posterior), do tamanho de ~6 min de explicação, e testável sozinho no recall.
> **Par que só existe em contraste (X vs. Y) fica junto, num subtópico só** — separá-lo destrói
> a discriminação que o aluno precisa treinar.
>
> É a partir daqui que o material é gerado: **um conjunto de artefatos por subtópico**, mais os
> integradores da etapa. Trocar os subtópicos com a etapa aberta desalinha o material já
> entregue do recall que vai cobrá-lo.

**Fora de escopo nesta etapa:** <o que NÃO pode aparecer ainda, para o material não vazar>

**conecta_com:** _(primeira etapa — nada anterior)_

**prepara_para:**
- Etapa 2 → **<Conceito da etapa 2>**: <em uma frase, por que o que ele aprendeu agora é pré-requisito daquilo>

## Etapa 2 — <Nome da etapa>

**Status:** `nao_iniciada`

- **<Conceito A>**: <...>
- **<Conceito B>**: <...>

**Fora de escopo nesta etapa:** <...>

**conecta_com:**
- Etapa 1 → **<Conceito X>**: <natureza da conexão — é o mesmo mecanismo? é o oposto? um é caso particular do outro? é o que costuma ser confundido com este?>

**prepara_para:**
- Etapa 3 → **<Conceito Y>**: <...>

<!--
Repita o bloco por etapa. Recomendado: 4 a 8 etapas.
Cada etapa deve caber em 1–2 sessões do loop de 3 fases.

Ao escrever `conecta_com`, prefira conexões de CONTRASTE ("é o oposto de", "costuma
ser confundido com") às de mera vizinhança temática. Contraste é o que gera boa
pergunta intercalada; "também é sobre qualidade" não gera nada.
-->
