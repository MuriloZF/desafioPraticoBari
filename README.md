# Desafio Bari — AI & Data Lab

Análise do funil de crédito, relatório semanal automatizado e extração estruturada de 17 laudos. Todos os dados fornecidos são sintéticos.

## Como rodar

Na raiz do projeto, com Python instalado:

```bash
python -m pip install -r requirements.txt
```

Parte 1 — análises e gráficos:

```bash
python -m scripts.valorFunil
python -m scripts.desempenho
python -m scripts.relacao
python -m scripts.recomendacao
```

Parte 2 — relatório HTML e log em `relatorios/`:

```bash
python -m scripts.automacao --as-of 2025-07-07
```

Sem `--as-of`, a rotina apura a última semana completa. Como o CSV fornecido é de 2025, use uma data daquele período para ver propostas no relatório.

Parte 3 — o resultado dos 17 laudos já está em `avaliacao_laudos/resultado_cloud.json`. Para conferir a avaliação sem usar a nuvem:

```bash
python -m scripts.extracao --evaluate-only avaliacao_laudos/resultado_cloud.json
```

Para refazer a extração, instale o Codex CLI, entre com `codex login` usando sua conta ChatGPT e rode `python -m scripts.extracao`. A execução consome a franquia do Codex; `--resume` reaproveita laudos já concluídos.

## Arquivos

- `data/`: CSV bruto e 17 laudos; `scriptsDataset/`: limpeza e auditoria da base.
- `scripts/valorFunil.py`, `desempenho.py`, `relacao.py` e `recomendacao.py`: análises da Parte 1; `graficos/` e `recomendacoes.md`: resultados.
- `scripts/automacao.py` e `instrucoesAutomacao.md`: rotina semanal e instruções da Parte 2; `relatorios/`: HTMLs e log.
- `scripts/extracao.py`, `EXTRACAO.md` e `avaliacao_laudos/`: extração, instruções, referência manual e resultados da Parte 3.
- `notes.md`: decisões e tratamento dos dados; `DIARIO.md`: uso de IA, aprendizados e autocrítica.

Tempo registrado em `notes.md`: aproximadamente **10h20** nas etapas 0 a 3, sem contar a revisão final da documentação.
