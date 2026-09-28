# Minhas anotações

## Step 0

Antes de começar a trabalhar em qualquer um dos passos propostos, vou primeiro estudar o dataset.

Depois de uma primeira análise, identifiquei alguns problemas:

- Existe uma entrada de uma pessoa com 14 anos. Suponho que a idade mínima deveria ser 18 anos, então provavelmente há algum erro nessa entrada. A questão é: o erro está apenas na idade ou a entrada inteira está incorreta? Basicamente, devo remover essa entrada ou mantê-la?
- O PDF diz que existem apenas 6 etapas no "funil" e, como ele descreve cada uma delas, presumo que essa informação esteja correta. O problema é que existe uma entrada com o valor 7. Novamente, preciso descobrir se apenas essa variável está errada ou se a entrada inteira está incorreta. Nesse caso, deve ser mais fácil verificar: vou analisar o `status_final`. Se for "Contratada", acredito que seja seguro assumir que o valor correto de `etapa_max_funil` deveria ser 6.
- Vou precisar normalizar `canal_origem`, pois existem entradas equivalentes escritas de maneiras diferentes. Isso não deve ser um problema muito grande. Só preciso definir exatamente como quero fazer essa normalização. De qualquer forma, considerando que a normalização é necessária, é uma questão relativamente simples.
- `taxa_juros_aa` e `data_assinatura` só são preenchidos quando `status_final` é "Contratada". Tenho certeza de que isso não é um erro, então estou apenas documentando esse comportamento.
- `valor_imovel` está como `str`. Vou precisar entender o motivo disso e corrigir, pois precisarei fazer cálculos com esse valor para obter o LTV.
- Já que mencionei o LTV, o PDF cita essa métrica algumas vezes, mas ela não está presente no dataset. Isso não deve ser um problema, pois o cálculo deve ser relativamente simples de fazer.
- Nem todos as entradas de data_entrada seguem o mesmo padrão, vou precisar normalizar, seguirei o padrão aaaa-mm-dd

Depois de uma análise rápida, descobri que a entrada em que `etapa_max_funil` era 7 tinha `status_final` como "Contratada". Portanto, acredito que seja seguro assumir que foi um erro de digitação e que o valor correto deveria ser 6. Para confirmar, verifiquei a linha inteira e ela parecia estar correta, o que reforça essa hipótese.

Voltando a `idade_cliente`, verifiquei a linha inteira da entrada com valor 14. A princípio, ela parece estar correta. Porém, não tenho certeza se devo confiar nesse valor, pois, diferente do caso de `etapa_max_funil`, não consigo usar as outras variáveis para verificar qual deveria ser o valor correto. Vou deixar esse caso em aberto por enquanto.

- Como a única coisa que parece estar errada nessa entrada é a idade, vou assumir que foi um erro de digitação e corrigir apenas esse valor, mantendo o restante da linha.

Por fim, voltando ao `valor_imovel`, o problema era bem simples: existem algumas entradas em que o valor está no formato `"R$ xxxx"`. São essas entradas que fazem com que a coluna inteira seja interpretada como `str`.

Analisando data_entrada, há três entradas com o formato errado, ao invés de aaaa-mm-dd usam dd/mm/aaaa, irei normalizar elas para o formato correto. Após a normalização, irei fazer mais testes com as datas.
Ainda na data_entrada, há uma instância em que a data_assinatura ocorreu antes da data_entrada, analisando a linha completa, esses valores parecem ser os únicos errados, portanto, presumo que estão invertidos. Irei trocá-los de ordem e utilizar a linha normalmente.
### Tempo: Aproximadamente 1h30

## Step 1

Temos quatro objetivos:

- 1.1 - Em qual etapa perdemos mais dinheiro?

- 1.2 - O que a liderança considera adequado? A taxa de aceitação está diminuindo?

- 1.3 - Qual característica está mais relacionada à contratação?

- 1.4 - Três recomendações.

Acredito que 1.3 seja a tarefa mais simples do primeiro passo, então vou começar por ela.

Para isso, pretendo utilizar `Mutual Information`, já que temos uma combinação de variáveis numéricas e categóricas.

Vantagens dessa abordagem

- MI pode ser utilizada com diferentes tipos de dados e, como nosso dataset possui tanto variáveis numéricas quanto categóricas, isso é importante para a análise;

- Ela consegue identificar tanto dependências lineares quanto não lineares, o que pode ser útil para entender melhor a relação entre as variáveis.

Desvantagens dessa abordagem

- Não escala tão bem, podendo ser mais custosa computacionalmente do que uma correlação simples;

- Talvez seja necessário converter o resultado para uma métrica mais específica para facilitar sua interpretação;

- Se houver muitos outliers, o resultado de MI pode ficar mais ruidoso.

- Não indica direção da relação.

Foi utilizado `ordinalEncoder` para representar as variáveis categóricas numericamente (e.g: `Curitiba = 0` e `São Paulo = 1`.
Esses valores servem apenas como uma representação, não tendo uma ordem de grandeza.

Além disso, foi calculado a taxa e contratação para cada variável.

### Tempo: Aproximadamente 2h30
