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
> atual** e os injeta no `focus_prompt` de cada artefato do NotebookLM e nas perguntas
> do recall. É o trilho que impede o material de avançar para etapas futuras.
>
> **Este arquivo é conteúdo de estudo** — vive em `estudo/` e nunca vai para o git.

O estudo segue estas etapas **em ordem**, sem pular nem adiantar conceitos de etapas
posteriores.

## Etapa 1 — <Nome da etapa>

**Status:** `em_andamento`  <!-- nao_iniciada | em_andamento | dominada -->

Conceitos obrigatórios (o artefato e o recall precisam cobrir **todos**):

- **<Conceito A>**: <o que exatamente o aluno precisa saber sobre ele>
- **<Conceito B>**: <idem — inclua a distinção contra o conceito que costuma ser confundido>
- **<Conceito C>**: <idem>

**Fora de escopo nesta etapa:** <o que NÃO pode aparecer ainda, para o material não vazar>

## Etapa 2 — <Nome da etapa>

**Status:** `nao_iniciada`

- **<Conceito A>**: <...>
- **<Conceito B>**: <...>

**Fora de escopo nesta etapa:** <...>

<!--
Repita o bloco por etapa. Recomendado: 4 a 8 etapas.
Cada etapa deve caber em 1–2 sessões do loop de 3 fases.
-->
