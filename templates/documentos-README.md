# estudo/documentos/

Coloque aqui a **fonte da matéria** que você está estudando: PDF do livro, slides,
apostila, artigo, etc. Um conjunto de arquivos por matéria.

> Nada nesta pasta vai para o git — ela está dentro de `estudo/`.

## Como o agente usa

Na Fase 1 (PREP) o agente **não sobe o arquivo bruto inteiro** para o NotebookLM.
Ele recorta do material só o conteúdo da etapa atual do roadmap e salva um
`<materia>-<topico>.md` curado aqui — é esse recorte que vira source. Isso mantém os
artefatos focados na etapa e impede a IA de vazar para etapas futuras.

> Formatos que o NotebookLM aceita bem: **PDF, Google Docs, texto, URLs, YouTube**.

Depois de adicionar uma fonte, registre-a no `fontes:` do ledger da matéria
(`estudo/progresso/<materia>.md`).
