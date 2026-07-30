---
# ===== NÓ DO GRAFO DE CONHECIMENTO =====
# Um arquivo por conceito, em estudo/progresso/<materia>-conceitos/<id>.md.
# scripts/grafo.py lê esta pasta + o srs.db e monta o grafo navegável.
#
# O formato é markdown com frontmatter de propósito: é o mesmo formato de um vault
# do Obsidian. Se um dia você quiser o Obsidian de verdade, aponte o vault para a
# pasta de conceitos — os [[wikilinks]] do corpo já constroem o grafo lá também.

id: <id-em-kebab-case>          # igual ao nome do arquivo, sem .md — é a chave das arestas
nome: <Nome do Conceito>        # o rótulo que aparece no nó
etapa: <N>                      # etapa do roadmap a que ele pertence
status: nao_iniciado            # nao_iniciado | ensinando | recall_feito | dominado
dominado_em:                    # data ISO — preenchida só quando a etapa passa no portão
ponto_fraco: false              # true enquanto houver ⚠️ ativo para este conceito
cards: []                       # ids dos cards do srs.db que cobrem este conceito

# De quem é o texto da seção "O que é":
#   aluno  → é a SUA explicação, dita no portão N4 e conferida na fonte. É o alvo.
#   ledger → síntese provisória, montada do ledger/roadmap pelo agente. Serve para o
#            grafo não nascer vazio, mas é DÍVIDA: some no próximo portão do conceito.
# O grafo marca o nó com "síntese provisória" enquanto for ledger — porque uma nota
# que você não produziu não tem o valor de recuperação de uma que você produziu.
nota_origem: aluno

# Aresta SÓLIDA — olha para TRÁS: conceitos anteriores (ou vizinhos) de que este
# depende, ou com que ele contrasta. Mesma semântica do `conecta_com` do roadmap.
# O grafo desenha X --> este. Prefira conexões de CONTRASTE ("é o oposto de",
# "costuma ser confundido com") às de mera vizinhança temática — é o contraste que
# treina discriminação, e a aresta sem o `porque` não ensina nada.
conecta_com:
  - id: <id-do-conceito-anterior>
    porque: <em uma linha, o que liga um ao outro ou o que os separa>

# Aresta TRACEJADA (ponte) — olha para FRENTE: onde este conceito REAPARECE numa
# etapa futura. Mesma semântica do `prepara_para` do roadmap. O grafo desenha
# este ╌╌> Y. É o que impede as etapas de virarem silos.
prepara_para:
  - id: <id-do-conceito-futuro>
    etapa: <N>
    porque: <por que este conceito é pré-requisito daquele>

# Declarar a ligação de um lado só já basta: o grafo normaliza as duas pontas no
# sentido do fluxo de conhecimento e funde a duplicata numa aresta só.
---

## O que é

_(Preenchido pelo agente com **a explicação do próprio aluno** no item de portão N4
aprovado — não com um resumo da fonte. O texto é conferido contra a fonte via
NotebookLM antes de entrar aqui; divergência vira `pontos_fracos` no ledger, não nota.
Ver `docs/MANUAL.md` → "Por que a nota do nó é a explicação do aluno".)_

## Não confunda com

- **<conceito vizinho>** — <o critério exato que separa um do outro>

## Histórico

<!-- Uma linha por marco: quando foi ensinado, quando passou no portão, quando
     falhou e voltou. Mais recente embaixo. -->
