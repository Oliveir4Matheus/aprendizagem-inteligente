# Diagramas

PNGs gerados a partir dos blocos mermaid do [`ARQUITETURA.md`](../../ARQUITETURA.md).
Os `.mmd` ao lado são as fontes extraídas — o original continua sendo o `ARQUITETURA.md`.

| Arquivo | O que mostra |
|---|---|
| `01-classes.png` | Estrutura: quem resolve o quê em tempo de execução |
| `02-sequencia.png` | Uma sessão de estudo do "oi" ao card agendado |
| `03-atividade-instalacao.png` | Instalação e configuração — roda uma vez por máquina |
| `04-atividade-ciclo-de-estudo.png` | O ciclo de estudo — roda toda sessão |

## Como regerar

Depois de editar um diagrama no `ARQUITETURA.md`:

```bash
npm install @mermaid-js/mermaid-cli
echo '{"executablePath":"/usr/bin/google-chrome","args":["--no-sandbox"]}' > puppeteer.json
mmdc -i diagrama.mmd -o diagrama.png -p puppeteer.json -b white -s 3 -t neutral
```

O `-s 3` é a escala; `-b white` evita fundo transparente, que some em visualizador escuro.
