---
artifact_type: audio
granularidade: subtopico
papel: aquisicao
---

# `audio` — Áudio Overview (podcast)

> Leia junto com [`_index.md`](_index.md). Referências em [`REFERENCIAS.md`](REFERENCIAS.md).

## 1. Granularidade: **um por subtópico**

Um episódio por subtópico, não por etapa. O tempo mediano de engajamento em material
audiovisual satura em torno de 6 minutos independentemente da duração total (Guo et al., 2014):
um episódio de etapa inteira gasta a atenção do aluno no primeiro conceito e entrega os outros
quatro para uma cabeça que já saiu do ar.

**Alvo de duração: 5 a 10 minutos por episódio.**

## 2. Para que serve — e para que não serve

O áudio é o artefato de **canal ocioso**: ele existe porque o aluno tem deslocamento, academia,
louça. É a única peça que o pega quando os olhos estão ocupados.

Isso define o que ele pode ser: **autocontido e narrativo**. Ele não pode depender de nada
visual — nem "como você vê no diagrama", nem "olhe a tabela". Se a explicação precisa de uma
imagem para existir, ela não é material de áudio; é `infographic` ou `slide_deck`.

Ele **não** é o lugar de cobrir tudo. É o lugar de o aluno ouvir a mesma ideia dita de um jeito
que ele não leu — elaboração, não repetição do `report`.

## 3. Base científica

| Regra | Fundamento |
|---|---|
| Um episódio por subtópico, 5–10 min | Segmentação, g ≈ 0,32–0,36 (Rey et al., 2019); saturação em ~6 min (Guo et al., 2014) |
| Tom conversacional, 2ª pessoa | Princípio da personalização: 11 de 11 testes de transferência a favor, mediana d ≈ 1,11 (Mayer) |
| Nada de digressão nem curiosidade solta | Princípio da coerência: material extrínseco compete pela mesma memória de trabalho (Mayer; Sweller, 1988) |
| Abrir com a pergunta que o episódio responde | Interrogação elaborativa — utilidade moderada (Dunlosky et al., 2013) |
| Fechar com 3 perguntas de recuperação, com pausa antes da resposta | Efeito do teste — alta utilidade (Roediger & Karpicke, 2006; Dunlosky et al., 2013) |
| Não repetir literalmente o texto do `report` | Princípio da redundância: mesma informação nos dois canais atrapalha em vez de somar |

## 4. Estrutura obrigatória do episódio

| Bloco | Duração | O que tem |
|---|---|---|
| **Gancho** | ~30 s | A pergunta que este subtópico responde, dita como problema real, não como definição |
| **Ancoragem** | ~30 s | Uma frase ligando ao que o aluno **já domina** (vem do `conecta_com` do roadmap) |
| **Explicação** | 3–6 min | O mecanismo. Um conceito por vez, na ordem em que dependem uns dos outros |
| **Caso concreto** | ~1 min | Um exemplo ancorado no background do aluno |
| **Erro clássico** | ~30 s | Com o que este conceito costuma ser confundido, e qual é o critério que separa |
| **Recuperação** | ~1 min | 3 perguntas. Fazer a pergunta → **pausar** → dar a resposta |

O bloco de recuperação não é enfeite de fechamento: é a única parte do episódio que produz
retenção por si só. Áudio sem ele é consumo passivo com boa produção.

## 5. Bloco `[FORMATO]` do `focus_prompt`

```
[FORMATO]
Produza um episódio de áudio de 5 a 10 minutos sobre este subtópico, com esta estrutura:
1. GANCHO (~30s): abra com a pergunta prática que este subtópico responde. Não comece por
   definição nem por "hoje vamos falar sobre".
2. ANCORAGEM (~30s): ligue explicitamente ao que o ouvinte já sabe: <conceito já dominado e a
   natureza da ligação — mesmo mecanismo? oposto? costuma ser confundido?>.
3. EXPLICAÇÃO (3-6 min): o mecanismo, um conceito por vez, na ordem de dependência.
4. CASO CONCRETO (~1 min): um exemplo do contexto <background do aluno>.
5. ERRO CLÁSSICO (~30s): com o que isto é confundido e qual critério separa os dois.
6. RECUPERAÇÃO (~1 min): faça 3 perguntas. Depois de CADA pergunta, faça uma pausa audível de
   alguns segundos antes de responder — o ouvinte precisa tentar lembrar primeiro.

Tom: conversacional, segunda pessoa, informal. Fale com o ouvinte, não sobre o assunto.
Nunca faça referência a nada visual: sem "como você vê", sem "na tabela", sem "no slide".
O episódio precisa funcionar de olhos fechados.
Não use digressão, curiosidade lateral nem analogia decorativa: tudo que não serve ao
subtópico é ruído que ocupa memória de trabalho.
```

## 6. Parâmetros do `studio_create`

```python
studio_create(
    notebook_id = <id>,
    artifact_type = "audio",
    focus_prompt = <[ESCOPO] + [IDIOMA] + [ALUNO] + [FORMATO]>,
    audio_length = "short",      # o alvo é 5-10 min, não o deep dive de 20+
    audio_format = "deep_dive",  # formatos disponíveis: studio_status(action="list_types")
    language = <idioma do PERFIL>,
)
```

Depois: `studio_status(action="rename", ..., new_title="E<n>.<m> · <Subtópico> — Áudio")`.

## 7. O que invalida o artefato

- Passa de ~12 minutos → virou episódio de etapa; regere com escopo apertado.
- Cita conceito de outro subtópico "para contextualizar" → a segmentação deixou de existir.
- Termina sem as 3 perguntas → é consumo passivo.
- Faz referência a qualquer coisa visual.
- Repete frase por frase o `report` do mesmo subtópico → redundância, não reforço.

## 8. Checklist

- [ ] Um episódio por subtópico, entre 5 e 10 minutos
- [ ] Abre com pergunta, não com definição
- [ ] Tem a ancoragem no que já foi dominado
- [ ] Termina com 3 perguntas **com pausa** antes da resposta
- [ ] Nenhuma referência visual, nenhum conceito de outro subtópico
- [ ] Idioma do PERFIL, título no padrão
