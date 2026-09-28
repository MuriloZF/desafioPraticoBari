# Parte 3 — extração dos laudos com agente na nuvem

`scripts/extracao.py` usa o **Codex CLI autenticado com ChatGPT** como agente para extrair um laudo por execução. É independente de qualquer outro script de extração e não requer chave da API nem pacote Python adicional. O script recusa autenticação que não seja ChatGPT e remove variáveis de chave da API do processo filho. O uso consome a franquia do Codex do plano ChatGPT e pode estar sujeito a limites ou créditos da conta; não é uma chamada à API cobrada por token.

## Como rodar

Na raiz deste projeto, confira o login e faça um teste com os cinco laudos da referência manual:

```bash
codex login status
python -m scripts.extracao --reference-only
```

Depois processe todos os 17, reaproveitando os cinco já concluídos:

```bash
python -m scripts.extracao --resume
```

Se o Codex não estiver autenticado, rode `codex login` e escolha **Sign in with ChatGPT**. O padrão é `gpt-5.6-terra`; `--model` permite fixar outro modelo disponível na sua conta. Use `--limit 1` para um teste rápido, `--timeout 300` se a conexão for lenta e `--help` para ver todas as opções. Cada laudo tem um limite de tempo independente. Uma falha fica registrada no JSON e pode ser tentada novamente com `--resume`.

O resultado fica em `avaliacao_laudos/resultado_cloud.json`, salvo de forma atômica após cada laudo. Ele contém os 15 campos padronizados, evidências copiadas literalmente do texto, avisos por documento, erros, hashes dos arquivos de entrada, modelo, versão do CLI e hashes do prompt e do esquema. `--resume` só reaproveita uma extração bem-sucedida quando o arquivo, modelo, prompt, esquema e versão do CLI coincidem; respostas com erro são reprocessadas. A execução é repetível como **procedimento auditável**, mas um modelo em nuvem não garante respostas idênticas em duas chamadas.

## Como lida com ausência, conflito e qualidade

Cada campo tem `valor`, `estado`, `evidencias` e `motivo_revisao`. O estado é `encontrado`, `ausente`, `nao_aplicavel`, `conflito` ou `revisar`. Campo não informado fica com `valor: null` e `estado: ausente`. Dados incompatíveis ficam com `valor: null`, `estado: conflito` e ambos os trechos em `evidencias`. O script rejeita evidências que não sejam substrings literais do laudo e marca como `revisar` respostas incompletas, estados inválidos, valores fora do tipo/faixa ou datas inválidas. Também detecta dois valores de área total na mesma linha. A validação automática **não prova** que todo valor extraído está semanticamente correto; campos `revisar`, conflitos e ônus devem ser conferidos por uma pessoa antes do uso decisório.

`avaliacao_laudos/referencia.json` é uma referência preenchida manualmente antes da extração. Ela cobre 49 critérios em cinco documentos com casos completos, ausentes, não aplicáveis e contraditórios. O agente recebe somente o texto de um laudo e um esquema JSON; a referência nunca é enviada ao agente. Para recalcular a métrica sem chamada à nuvem:

```bash
python -m scripts.extracao --evaluate-only avaliacao_laudos/resultado_cloud.json
```

Na execução de verificação de 28/09/2026, os cinco casos da amostra tiveram **49/49 critérios corretos**, sem falhas de chamada. Isso não estima a acurácia estatística nos outros 12 documentos; a referência pode ser ampliada para medi-la melhor.

O conteúdo dos laudos é enviado ao serviço de nuvem. O agente roda num diretório temporário isolado, com configuração do usuário ignorada, sem gravação de sessão e com sandbox somente de leitura. O prompt manda tratar instruções dentro do laudo como dados. Ainda assim, para documentos não confiáveis ou sensíveis, revise as políticas de privacidade e os resultados antes de usar em produção.
