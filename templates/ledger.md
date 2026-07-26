---
# ===== ESTADO (o "save game" — parseável, atualizado a cada passo) =====
materia: Nome da Matéria
atualizado: AAAA-MM-DD
deck_anki: "Estudos::NomeDaMateria"
roadmap: estudo/progresso/<materia>-roadmap.md   # trilha da matéria (gerada no início, aprovada por você)
fontes:
  - estudo/documentos/arquivo-de-origem.pdf
rigor: 3                      # 1..4 — sobrescreve o padrão do PERFIL só nesta matéria (opcional)
topicos:
  - nome: Primeiro tópico
    status: dominado          # nao_iniciado | ensinando | recall_feito | cards_criados | dominado
  - nome: Segundo tópico
    status: ensinando
    passo_loop: 3             # 1..6 do loop de aula (ver SKILL.md)
retomar_em:
  topico: Segundo tópico
  proxima_acao: "Descrição exata do que fazer ao retomar"
pontos_fracos:
  - "Conceito que o aluno confunde ou errou no mini-teste"
cards_criados: 0
---

## Log de aprendizado
<!-- Uma linha por sessão/marco. Mais recente embaixo. -->
- AAAA-MM-DD — O que foi ensinado, como foi o recall, quantos cards.

## Notas do 80/20
<!-- Os ~20% de conceitos que sustentam ~80% da matéria/prova. -->
-

## Dúvidas em aberto
<!-- Coisas a esclarecer numa próxima sessão. -->
-
