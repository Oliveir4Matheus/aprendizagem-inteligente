---
artifact_type: data_table
granularidade: etapa
papel: integrador
---

# `data_table` — Tabela estruturada

> Leia junto com [`_index.md`](_index.md). Referências em [`REFERENCIAS.md`](REFERENCIAS.md).

## 1. Granularidade: **uma por ETAPA**

Como o `mind_map`, este é um artefato **integrador**: ele existe para pôr os subtópicos lado a
lado. Uma tabela de um subtópico só tem uma linha, e uma tabela de uma linha é uma lista.

## 2. Para que serve: casos contrastantes

Uma tabela comparativa não é um resumo tabulado — é um **instrumento de contraste**.

Schwartz & Bransford (1998) mostraram que comparar casos que diferem em uma característica
profunda, com as demais mantidas constantes, prepara o aluno para aprender com a explicação
seguinte de um jeito que a explicação sozinha não consegue. É por isso que a tabela vem
**depois** dos artefatos de aquisição: ela não ensina os conceitos, ela força a percepção da
diferença entre conceitos já vistos.

**A consequência de projeto é uma regra simples e rigorosa:**

> **Toda coluna precisa ser um critério em que pelo menos duas linhas DIFEREM.**
> Coluna em que todas as linhas dizem a mesma coisa não ensina nada — ocupa espaço e dilui o
> contraste que é o único motivo de a tabela existir.

Isso elimina de saída as colunas inúteis que a IA adora gerar: "Importância", "Aplicações",
"Benefícios" — todas preenchidas com a mesma vaguidão em todas as linhas.

## 3. Base científica

| Regra | Fundamento |
|---|---|
| A tabela é instrumento de contraste, não de resumo | Casos contrastantes (Schwartz & Bransford, 1998) |
| Uma por etapa, comparando subtópicos | O contraste exige ao menos dois casos alinhados |
| Toda coluna diferencia ao menos duas linhas | Corolário direto do desenho de casos contrastantes |
| Gerada depois dos artefatos de aquisição | Contraste opera sobre material já visto |
| Coluna final de "quando escolher" | Discriminação aplicada; é o que o quiz integrador vai cobrar |

## 4. Estrutura obrigatória

| | Regra |
|---|---|
| **Linhas** | Um por subtópico (ou por conceito, quando dois conceitos do mesmo subtópico se confundem) |
| **Colunas** | 4 a 6 critérios, todos diferenciadores |
| **Célula** | Uma frase curta e comparável. Se a célula precisa de parágrafo, o critério está mal escolhido |
| **Última coluna** | Sempre: **"quando escolher este / gatilho de uso"** |

**Colunas que costumam funcionar** (escolha as que diferenciam, não todas):

- Que problema resolve
- Qual é a **condição de uso** (o gatilho)
- Que dado ou insumo exige
- O que produz como saída
- Quando **não** usar
- Com o que é confundido, e por qual critério se separa

## 5. Bloco `[FORMATO]` do `focus_prompt`

O `[ESCOPO]` aqui é a **etapa inteira**.

```
[FORMATO]
Produza UMA tabela comparativa cobrindo todos os subtópicos desta etapa.

LINHAS: um por subtópico: <lista dos subtópicos>. Se dois conceitos dentro de um mesmo
subtópico costumam ser confundidos entre si, dê uma linha a cada um.

COLUNAS: de 4 a 6 critérios. REGRA OBRIGATÓRIA — cada coluna precisa ser um critério em que
pelo menos DUAS linhas dão respostas DIFERENTES. Se uma coluna ficar com o mesmo conteúdo em
todas as linhas, remova-a e escolha outro critério: ela não diferencia nada e só dilui a
comparação. NÃO use colunas genéricas como "importância", "benefícios" ou "aplicações".

Critérios preferidos: que problema resolve · qual a condição/gatilho de uso · que insumo
exige · o que produz · quando NÃO usar · com o que é confundido e por qual critério se separa.

ÚLTIMA COLUNA (obrigatória): "Quando escolher este" — a condição prática que faz o aluno
optar por esta linha e não pelas outras.

CÉLULAS: uma frase curta e diretamente comparável com as das outras linhas da mesma coluna.
Use a mesma unidade de comparação na coluna inteira. Se uma célula precisa de parágrafo, o
critério está mal escolhido — troque o critério.
```

## 6. Parâmetros do `studio_create`

```python
studio_create(
    notebook_id = <id>,
    artifact_type = "data_table",
    focus_prompt = <[ESCOPO da etapa] + [IDIOMA] + [ALUNO] + [FORMATO]>,
    detail_level = "standard",
    language = <idioma do PERFIL>,
)
```

Renomeie para `E<n> · Tabela comparativa`.

## 7. Como a tabela alimenta o resto do sistema

Ela não é material de leitura — é **matéria-prima de item de teste**:

| A tabela dá | Vira |
|---|---|
| Uma coluna com respostas diferentes entre linhas | Um item de discriminação no quiz integrador |
| A coluna "quando escolher" | Uma pergunta `intercalado` do recall da Fase 3 |
| Uma célula que o aluno não soube preencher | Um `ponto_fraco` no ledger |

**Uso mais forte que ler a tabela:** entregar a tabela **com uma coluna em branco** e pedir que
o aluno preencha antes de comparar com a versão completa. Produção ativa em vez de
reconhecimento — o mesmo motivo pelo qual o `report` não é um resumo.

## 8. O que invalida o artefato

- Uma tabela por subtópico → não é integrador.
- Qualquer coluna com o mesmo conteúdo em todas as linhas.
- Colunas genéricas ("importância", "benefícios").
- Células com parágrafos ou com unidades de comparação diferentes na mesma coluna.
- Falta da coluna "quando escolher este".

## 9. Checklist

- [ ] **Uma** tabela por etapa, gerada depois dos artefatos de aquisição
- [ ] Uma linha por subtópico (ou por conceito confundível)
- [ ] 4–6 colunas, **todas** diferenciando ao menos duas linhas
- [ ] Última coluna é "quando escolher este"
- [ ] Células curtas e comparáveis
- [ ] Idioma do PERFIL, título no padrão
