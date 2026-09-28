# Recomendações

Com base nas análises realizadas sobre o funil de propostas e nas características relacionadas à contratação, foram definidas três recomendações acionáveis. A priorização considera principalmente o impacto potencial observado nos dados e a possibilidade de atuação sobre cada ponto.

## 1. Recuperar o volume de propostas

O volume de propostas apresentou uma queda acentuada ao longo de 2025. O maior volume foi registrado em março, com 527 propostas, enquanto dezembro apresentou apenas 27, uma redução de 500 propostas, equivalente a 94,88%.

Dessa forma, a primeira recomendação é investigar as causas dessa redução e priorizar ações para recuperar o volume de propostas qualificadas.

Como cenário de impacto, considerando a recuperação de 10% da diferença entre o pico e o menor volume observado, seriam recuperadas aproximadamente 50 propostas. Mantendo a taxa geral de contratação de 19,39%, isso representaria aproximadamente 9,7 contratações adicionais.

**Premissas:**

* 10% da diferença entre o pico e o menor volume seria recuperada.
* As propostas recuperadas teriam a mesma taxa de contratação observada no conjunto geral (19,39%).
* O aumento de volume não alteraria a qualidade média das propostas nem a taxa de contratação das demais propostas.

## 2. Priorizar clientes com maior score de crédito

O `score_credito` apresentou a maior Mutual Information entre as características analisadas, com valor de 0,0143. Além disso, existe uma diferença relevante nas taxas de contratação entre as faixas de score.

Clientes com score acima de 733 apresentaram taxa de contratação de 30,06%, enquanto a taxa geral foi de 19,39%. Isso indica uma associação entre score de crédito e contratação e sugere que esse critério pode ser considerado na priorização e qualificação das propostas.

Como cenário de impacto, um aumento de 10% no número de propostas desse grupo representaria aproximadamente 126 novas propostas. Mantendo a taxa de contratação observada de 30,06%, seriam aproximadamente 38 contratações adicionais.

**Premissas:**

* O número de propostas com score acima de 733 aumentaria em 10%.
* As novas propostas teriam a mesma taxa de contratação observada no grupo (30,06%).
* A relação observada entre score e contratação se manteria para as novas propostas.
* A Mutual Information indica associação, não causalidade.

## 3. Entender a baixa taxa de contratação dos correspondentes

O canal correspondente apresentou a menor taxa de contratação entre os canais analisados: 14,28%, contra uma taxa geral de 19,39%. Foram observadas 1.772 propostas nesse canal, das quais 253 foram contratadas.

A recomendação é investigar as características dessas propostas e o processo de atuação dos correspondentes para identificar os fatores associados à diferença de conversão. Essa análise deve considerar que a queda geral observada no período não pode ser atribuída exclusivamente a esse canal.

Como cenário de impacto, caso as 1.772 propostas dos correspondentes apresentassem a taxa geral de contratação de 19,39%, seriam esperadas aproximadamente 344 contratações, ou cerca de 91 a mais do que as 253 observadas.

**Premissas:**

* O volume de propostas dos correspondentes permaneceria em 1.772.
* A taxa de contratação passaria de 14,28% para 19,39%.
* As demais características das propostas permaneceriam constantes.
* O cálculo representa um cenário contrafactual, e não uma estimativa causal de resultado.

## Resumo

| Prioridade | Recomendação                                   | Evidência principal                                         | Impacto estimado |
| ---------- | ---------------------------------------------- | ----------------------------------------------------------- | ---------------: |
| 1          | Recuperar o volume de propostas qualificadas   | Queda de 527 propostas em março para 27 em dezembro de 2025 |   +9,7 contratos |
| 2          | Priorizar clientes com score > 733             | Taxa de contratação de 30,06% no grupo                      |  +38,0 contratos |
| 3          | Entender a baixa conversão dos correspondentes | 14,28% de contratação contra 19,39% na média geral          |  +90,6 contratos |

Os impactos apresentados são cenários calculados a partir dos dados disponíveis, com as premissas descritas acima. Eles não representam previsões de resultado, principalmente porque o dataset não permite estabelecer causalidade entre as características analisadas e a contratação.

