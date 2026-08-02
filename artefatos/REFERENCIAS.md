# Base científica dos artefatos

> Referências citadas pelos arquivos de `artefatos/`. Cada regra de formato deste diretório
> aponta para uma linha daqui — regra sem referência é opinião, e opinião não sobrevive a
> revisão. Quando uma regra for julgamento de engenharia e não achado empírico, ela é marcada
> como tal no arquivo do tipo.

## Segmentação e carga cognitiva — a base do "um artefato por subtópico"

| Chave | Referência | O que sustenta |
|---|---|---|
| Rey et al., 2019 | Rey, G. D., Beege, M., Nebel, S., et al. *A Meta-analysis of the Segmenting Effect.* Educational Psychology Review, 31, 389–419. | Fatiar material em unidades autocontidas melhora retenção e transferência (g ≈ 0,32–0,36). Efeito **maior em tratamentos curtos**. |
| Mayer, 2021 | Mayer, R. E. *Multimedia Learning* (3ª ed.). Cambridge University Press. | Teoria Cognitiva da Aprendizagem Multimídia (CTML): dois canais, capacidade limitada, processamento ativo. Origem dos princípios de segmentação, sinalização, coerência, redundância, contiguidade e personalização. |
| Meta-análise CTML, 2025 | *A Meta-Analysis of Richard Mayer's Multimedia Learning Research.* Educational Research Review. | Tamanhos de efeito por princípio: contiguidade g ≈ 0,74; multimídia g ≈ 0,39; sinalização g ≈ 0,38; segmentação g ≈ 0,32. |
| Guo et al., 2014 | Guo, P. J., Kim, J., & Rubin, R. *How video production affects student engagement: an empirical study of MOOC videos.* ACM L@S. | O tempo mediano de engajamento satura em ~6 minutos, **independente** da duração total do vídeo. Acima de 12 min, o aluno médio assiste menos de um quarto. |
| Sweller, 1988 | Sweller, J. *Cognitive Load During Problem Solving.* Cognitive Science, 12(2), 257–285. | Carga cognitiva extrínseca compete com a aprendizagem pela mesma memória de trabalho. |

## Recuperação, teste e espaçamento

| Chave | Referência | O que sustenta |
|---|---|---|
| Roediger & Karpicke, 2006 | Roediger, H. L., & Karpicke, J. D. *Test-Enhanced Learning.* Psychological Science, 17(3), 249–255. | Recuperar da memória produz retenção muito superior a reler, e a vantagem **cresce** com o intervalo até o teste final. |
| Little et al., 2012 | Little, J. L., Bjork, E. L., Bjork, R. A., & Angello, G. *Multiple-Choice Tests Exonerated, at Least of Some Charges.* Psychological Science, 23(11), 1337–1344. | Múltipla escolha com **distratores plausíveis e competitivos** aciona recuperação produtiva — ganho comparável ao de resposta curta e superior ao de releitura. Com distratores fracos, o ganho some. |
| Dunlosky et al., 2013 | Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., & Willingham, D. T. *Improving Students' Learning With Effective Learning Techniques.* Psychological Science in the Public Interest, 14(1), 4–58. | **Alta utilidade:** teste prático e prática distribuída. **Utilidade moderada:** interrogação elaborativa, autoexplicação, intercalação. **Baixa utilidade: resumir e grifar.** |
| Wozniak, 1999 | Wozniak, P. *Effective learning: Twenty rules of formulating knowledge.* SuperMemo. | Princípio da informação mínima: um fato por card; material simples é retido de forma desproporcionalmente melhor sob repetição espaçada. |

## Formato dos artefatos

| Chave | Referência | O que sustenta |
|---|---|---|
| Alley & Neeley, 2005 | Alley, M., & Neeley, K. A. *Rethinking the Design of Presentation Slides.* Technical Communication, 52(4). | Estrutura **asserção-evidência**: título é uma frase completa afirmando o ponto; corpo é evidência visual, não lista de tópicos. |
| Garner & Alley, 2013 | Garner, J. K., & Alley, M. *How the Design of Presentation Slides Affects Audience Comprehension.* International Journal of Engineering Education. | Alunos expostos a slides asserção-evidência recordaram mais e compreenderam mais fundo; a vantagem **persistiu no teste adiado de uma semana**. |
| Brame, 2016 | Brame, C. J. *Effective Educational Videos.* CBE—Life Sciences Education, 15(4), es6. | Vídeo eficaz = carga cognitiva controlada + engajamento + aprendizagem ativa embutida (pausa com pergunta). |
| Paivio, 1986 / Clark & Paivio, 1991 | Paivio, A. *Mental Representations: A Dual Coding Approach.* / Clark, J. M., & Paivio, A. *Dual Coding Theory and Education.* Educational Psychology Review, 3(3), 149–210. | Material codificado em duas vias (verbal + imagética) é consistentemente mais memorável; tamanhos de efeito tipicamente entre 0,5 e 1,0 DP. |
| Nesbit & Adesope, 2006 | Nesbit, J. C., & Adesope, O. O. *Learning With Concept and Knowledge Maps: A Meta-Analysis.* Review of Educational Research, 76(3), 413–448. | 67 tamanhos de efeito, 55 estudos, 5.818 participantes: diagramas nó-aresta aumentam retenção frente a texto corrido. |
| Schroeder et al., 2018 | Schroeder, N. L., Nesbit, J. C., Anguiano, C. J., & Adesope, O. O. *Studying and Constructing Concept Maps: a Meta-Analysis.* Educational Psychology Review, 30, 431–455. | Confirma e expande o achado (142 tamanhos de efeito); construir o mapa supera apenas estudá-lo. |
| Schwartz & Bransford, 1998 | Schwartz, D. L., & Bransford, J. D. *A Time for Telling.* Cognition and Instruction, 16(4), 475–522. | **Casos contrastantes**: comparar exemplos que diferem em uma característica profunda prepara o aluno para aprender com a explicação seguinte. Base da tabela comparativa e do par contrastivo. |
| Mayer, personalização | Mayer, R. E. *Personalization, Voice, and Image Principles*, in Multimedia Learning. | Estilo conversacional (2ª pessoa, informal) superou o formal em 11 de 11 testes de transferência, mediana d ≈ 1,11. |

## Como estas referências entram no sistema

- **Segmentação + saturação de atenção** → um artefato por subtópico (`_index.md` §1).
- **Casos contrastantes** → par contrastivo é um subtópico só, e existe a `data_table` da etapa.
- **Teste prático (alta utilidade)** → `quiz` e `flashcards` são artefatos de primeira classe,
  não extras; e o recall da Fase 3 acontece mesmo quando o quiz já foi feito.
- **Resumir tem baixa utilidade** → o `report` **não** é resumo para reler: é guia de perguntas
  (ver `report.md` §1). Esta é a decisão de projeto mais contraintuitiva do diretório.
- **Prática distribuída** → não é papel de nenhum artefato; é do FSRS (`srs.db`).
