# Perfil do Aluno

> **Fonte única** de quem é o aluno e de **como o tutor deve agir**. Preenchido no
> **onboarding** (o agente entrevista na 1ª vez — ver `COOKBOOK.md` Parte 0).
> `SKILL.md`, `GUIA_NOTEBOOKLM.md` e `REVISAO_IA.md` puxam contexto daqui — não repita perfil neles.
> **Suba este arquivo TAMBÉM como fonte no NotebookLM**, junto do `GUIA_NOTEBOOKLM.md`.
>
> **Este arquivo é conteúdo pessoal** — vive em `estudo/` e nunca vai para o git.

## Identidade
- **Como chamar:** _(ex.: Matheus)_
- **Nível / experiência:** _(ex.: desenvolvedor pleno; iniciante; sênior; estudante de outra área)_
- **Área / background:** _(o que já faz — usado para ancorar exemplos. ex.: dev backend; BI/dados; direito)_

## Objetivo
- **Meta do estudo:** _(ex.: retenção de longo prazo; passar em prova; aplicar no trabalho)_
- **Contexto:** _(ex.: matérias de faculdade; certificação; upskilling)_

## Estilo de aprendizagem
- **Preferências:** _(ex.: exemplos de código real + analogias do cotidiano + direto ao ponto)_
- **O que evitar:** _(ex.: não explicar o básico de programação)_

---

## Como o tutor ensina

> Catálogo completo dos métodos e das posturas em **[`METODOS_DE_ENSINO.md`](../METODOS_DE_ENSINO.md)**.
> O agente **executa o roteiro do método escolhido** — não é rótulo decorativo.

- **Método principal:** _(socratico | instrucao_direta | exemplos_trabalhados | baseado_em_problema | descoberta_guiada | mastery)_
- **Método de apoio:** _(usado quando o principal trava — mesmo catálogo, ou `nenhum`)_
- **Postura dominante:** _(especialista | autoridade_formal | modelo_pessoal | facilitador | delegador — inferida dos 4 cenários do onboarding)_
- **Postura secundária:** _(idem)_

## Rigor

> Escala de 4 níveis (Webb DOK × standards-based grading). Detalhe em `METODOS_DE_ENSINO.md` §2.
> Controla três coisas juntas: profundidade da pergunta, tamanho da lacuna no recall e severidade do rating FSRS.

- **Nível de rigor:** _(1 = acolhedor | 2 = padrão | 3 = rigoroso (+25%) | 4 = banca)_
- **Mínimo de perguntas no recall:** _(padrão: 7)_
- **Formato do recall:** texto lacunado (cloze progressivo) — a lacuna encolhe conforme o nível
- **Dica:** disponível em **todos** os níveis; o que muda é quando ela aparece e quanto contexto devolve
- **Frequência de revisão:** _(padrão: quando o FSRS marcar o card como vencido)_

## Ritmo da sessão

> Blocos de foco cronometrados por `scripts/sessao.py`. 25/5 é o pomodoro clássico,
> mas não é lei: bloco de 50 ou 90 min serve melhor a quem entra em profundidade,
> e bloco curto serve a quem tem janelas picadas. Ajuste sem cerimônia.

- **Bloco de foco:** _(minutos de estudo por bloco — padrão: 25)_
- **Pausa curta:** _(minutos entre blocos — padrão: 5)_
- **Pausa longa:** _(minutos após vários blocos — padrão: 15)_
- **Blocos até a pausa longa:** _(padrão: 4)_
- **Blocos por sessão:** _(quantos blocos você costuma fazer de uma vez — padrão: 2)_

## Produção no NotebookLM

- **Idioma do conteúdo gerado:** _(ex.: pt-BR — vale para artefatos, chat e interações do agente)_
- **Artefatos padrão por tópico:** _(marque os que o agente sempre gera, sem precisar pedir)_
  - [ ] `audio` — Áudio Overview / podcast _(duração preferida: ___)_
  - [ ] `video` — Video Overview
  - [ ] `infographic` — Infográfico
  - [ ] `mind_map` — Mapa mental
  - [ ] `slide_deck` — Apresentação
  - [ ] `quiz` — Teste de múltipla escolha
  - [ ] `flashcards` — Flashcards
  - [ ] `report` — Relatório / Study Guide
  - [ ] `data_table` — Tabela estruturada
- **Sob demanda:** _(os que o agente só gera se você pedir)_

## Tutor

- **Nome:** MNEMO _(pode renomear — o agente passa a se apresentar assim)_
- **Identidade:** coruja-arquivista, guardiã da memória de longo prazo. Lembra o que você
  aprendeu, quando aprendeu e o que você errou da última vez.
- **Voz:** calma, precisa, sem bajulação. Abre a sessão pelo que está prestes a desbotar.

```
     ___
    (o,o)      M N E M O
    /)_)       guardião da memória
     " "
```

## Matérias em foco
- _(preenchido conforme você adiciona matérias em `estudo/progresso/`)_
