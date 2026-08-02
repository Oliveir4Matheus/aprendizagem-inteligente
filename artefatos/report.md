---
artifact_type: report
granularidade: subtopico
papel: consolidacao
---

# `report` — Guia de estudo / relatório

> Leia junto com [`_index.md`](_index.md). Referências em [`REFERENCIAS.md`](REFERENCIAS.md).

## 1. A decisão contraintuitiva: este artefato **não é um resumo**

Dunlosky et al. (2013) avaliaram dez técnicas de estudo e colocaram **resumir e grifar na
categoria de baixa utilidade** — não porque não funcionem nunca, mas porque o ganho não se
sustenta entre materiais, alunos e tipos de prova. Um resumo bem escrito para reler é
exatamente o material que produz a **ilusão de fluência**: o texto está claro, então o aluno
conclui que sabe. Ele sabe reconhecer. Não sabe recuperar.

Então o `report` deste sistema é construído como **instrumento de recuperação e elaboração**,
não como texto para reler:

- toda seção **abre com uma pergunta** e o aluno é instruído a responder antes de ler adiante;
- a explicação responde **por que**, não só **o que** (interrogação elaborativa, utilidade
  moderada — Dunlosky et al., 2013);
- fecha com um bloco em que o aluno **escreve com as próprias palavras** (autoexplicação).

O nome do artefato no NotebookLM continua sendo "report". O formato que ele carrega é **guia de
estudo com perguntas**.

> Se o aluno quiser mesmo uma apostila de leitura corrida, ele pode pedir — mas então é escolha
> declarada dele, não o padrão do sistema. O padrão é o que a evidência sustenta.

## 2. Granularidade: **um por subtópico**

3 a 6 páginas equivalentes. Um guia por subtópico mantém a correspondência 1:1 com o card e com
a pergunta de recall — quando o aluno erra, ele sabe exatamente qual guia reabrir.

## 3. Base científica

| Regra | Fundamento |
|---|---|
| Não é resumo para reler | Resumir e grifar = **baixa utilidade** (Dunlosky et al., 2013) |
| Cada seção abre com pergunta a ser respondida antes da leitura | Efeito do teste, **alta utilidade**; interrogação elaborativa |
| Explicar o **porquê**, não só o que | Interrogação elaborativa e autoexplicação, utilidade moderada |
| Bloco final de escrita com as próprias palavras | Autoexplicação; produção ativa vence reconhecimento |
| Par contrastivo explícito | Casos contrastantes (Schwartz & Bransford, 1998) |
| Sem digressão, sem "contexto histórico" não pedido | Princípio da coerência |

## 4. Estrutura obrigatória

| Seção | Conteúdo |
|---|---|
| **A pergunta central** | A pergunta que o subtópico responde + instrução: *tente responder antes de continuar* |
| **A resposta curta** | 3 a 5 linhas. É o que o aluno precisa conseguir dizer de cor |
| **Por que é assim** | O mecanismo. A parte que transforma decoreba em entendimento |
| **Exemplo trabalhado** | Um caso do contexto do aluno, resolvido passo a passo com o raciocínio visível |
| **O que se confunde com isto** | O par contrastivo e o **critério** que separa os dois |
| **Perguntas de recuperação** | 5 perguntas com resposta **no fim do documento**, nunca ao lado |
| **Explique com suas palavras** | 2 comandos de produção ativa, sem resposta nenhuma |

O detalhe do "resposta no fim, nunca ao lado" é operacional e importa: resposta visível na
mesma tela converte o teste em leitura.

## 5. Bloco `[FORMATO]` do `focus_prompt`

```
[FORMATO]
Produza um GUIA DE ESTUDO deste subtópico — NÃO um resumo. A diferença é essencial: um resumo
serve para reler, e reler produz sensação de domínio sem domínio. Este documento serve para o
aluno TESTAR e EXPLICAR o que sabe.

ESTRUTURA (nesta ordem, com estes títulos):
1. A PERGUNTA CENTRAL — a pergunta que este subtópico responde, seguida da instrução:
   "Tente responder antes de continuar lendo."
2. A RESPOSTA CURTA — 3 a 5 linhas. O que o aluno precisa conseguir dizer de memória.
3. POR QUE É ASSIM — o mecanismo por trás. Explique a causa, não só o fato. Esta seção
   responde "por quê", não "o quê".
4. EXEMPLO TRABALHADO — um caso do contexto <background do aluno>, resolvido passo a passo,
   com o raciocínio de cada passo visível.
5. O QUE SE CONFUNDE COM ISTO — o conceito parecido e, explicitamente, o CRITÉRIO que decide
   qual dos dois se aplica.
6. PERGUNTAS DE RECUPERAÇÃO — 5 perguntas abertas. Coloque TODAS as respostas juntas no FIM
   do documento, nunca ao lado da pergunta.
7. EXPLIQUE COM SUAS PALAVRAS — 2 comandos do tipo "explique <X> para alguém que nunca ouviu
   falar disso, sem usar o termo técnico". Sem resposta.

REGRAS:
- Nada de introdução histórica, contexto de mercado ou curiosidade que não seja necessária
  para responder à pergunta central.
- Não grife nem destaque em negrito frases inteiras: destaque só termos técnicos na primeira
  aparição.
- Prosa curta. Se um parágrafo passa de 5 linhas, quebre.
```

## 6. Parâmetros do `studio_create`

```python
studio_create(
    notebook_id = <id>,
    artifact_type = "report",
    focus_prompt = <[ESCOPO] + [IDIOMA] + [ALUNO] + [FORMATO]>,
    report_format = "Study Guide",   # opções: studio_status(action="list_types")
    detail_level = "standard",
    language = <idioma do PERFIL>,
)
```

Depois: `studio_status(action="rename", ..., new_title="E<n>.<m> · <Subtópico> — Guia")`.

## 7. O que invalida o artefato

- Saiu como texto corrido sem perguntas → é resumo; regere.
- Respostas ao lado das perguntas.
- Cobre a etapa inteira em vez do subtópico.
- Abre com contexto histórico ou "importância do tema".
- Repete literalmente o roteiro do `audio` do mesmo subtópico → redundância entre canais.

## 8. Checklist

- [ ] Um guia por subtópico, 3–6 páginas
- [ ] Abre com pergunta + instrução de responder antes
- [ ] Tem a seção "por que é assim" (mecanismo, não fato)
- [ ] Tem exemplo trabalhado no contexto do aluno
- [ ] Tem o par contrastivo com critério explícito
- [ ] 5 perguntas com respostas só no fim + 2 comandos de autoexplicação sem resposta
- [ ] Idioma do PERFIL, título no padrão
