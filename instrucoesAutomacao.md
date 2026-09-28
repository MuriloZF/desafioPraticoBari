# Parte 2 — relatório semanal do funil

A rotina em `scripts/automacao.py` lê a extração bruta, aplica o tratamento de `scriptsDataset/cleanDataset.py` e cria um HTML para a última semana **completa** (segunda a domingo). As propostas são agrupadas pela data de entrada. A conversão usa o status final disponível **no momento da extração**, que pode ter mudado depois daquela semana; portanto, não mede contratos assinados naquela semana.

## Como executar

Na raiz do projeto, depois de instalar as dependências de `requirements.txt`:

```bash
python -m scripts.automacao
```

O padrão lê `data/propostas_credito.csv`, grava `relatorios/funil_AAAA-MM-DD.html` (data da segunda-feira da semana apurada) e acrescenta o registro da execução a `relatorios/automacao.log`. Abra o HTML no navegador para revisar antes de enviar. O processo retorna código `0` em caso de sucesso e `1` se a entrada não puder ser usada.

Para testar uma semana presente na base fictícia:

```bash
python -m scripts.automacao --as-of 2025-07-07
```

Esse exemplo apura 30/06 a 06/07/2025. Como a base fornecida termina em dezembro de 2025, uma execução na data atual produzirá uma semana sem propostas e um aviso explícito de extração desatualizada. Em produção, substitua o CSV pela extração atualizada antes de cada execução. `python -m scripts.automacao --help` mostra também `--input` e `--output-dir`.

Para agendar às 08h de toda segunda-feira em Linux, use uma entrada `crontab` como esta, substituindo o caminho pelo do projeto:

```cron
0 8 * * 1 cd /caminho/do/projeto && /caminho/do/projeto/.venv/bin/python -m scripts.automacao
```

Quem opera a rotina deve verificar o código de saída, o `automacao.log` e os avisos no HTML antes do envio. Uma nova execução para a mesma semana substitui o HTML daquela semana somente após a geração bem-sucedida. Se houver erro, um HTML antigo da mesma semana pode continuar na pasta; ele não deve ser enviado como resultado da execução com falha.

## Contrato da entrada e falhas

Colunas obrigatórias: `id_proposta`, `data_entrada`, `canal_origem`, `valor_imovel`, `valor_solicitado`, `etapa_max_funil` e `status_final`. Se faltar uma delas, a execução falha, registra os nomes no log e não gera um novo relatório. As colunas `idade_cliente` e `data_assinatura_contrato` podem faltar; nesse caso são deixadas vazias e o log registra o fato. Colunas extras são preservadas e registradas, sem alterar as métricas.

Aceita CSV UTF-8 com vírgula ou ponto e vírgula, datas `AAAA-MM-DD` ou `DD/MM/AAAA` e valores monetários como `1234.56`, `1234,56` ou `R$ 1.234,56`. Cabeçalhos e status novos, datas ou números ilegíveis, IDs duplicados e etapas desconhecidas interrompem a execução com mensagem no log. Não há descarte silencioso de linhas. Se não houver propostas na semana, o relatório mostra zero e deixa a conversão em branco (`—`), com aviso; isso também pode indicar arquivo antigo ou semana escolhida incorretamente.

Para verificar os cenários de coluna ausente e formato novo:

```bash
python -m unittest discover -s tests -v
```
