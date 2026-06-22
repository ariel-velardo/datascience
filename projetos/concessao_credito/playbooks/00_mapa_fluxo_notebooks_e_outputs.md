# Playbook — Mapa do fluxo dos notebooks e outputs

## 1. Objetivo

Este playbook descreve o fluxo completo do projeto de concessão de crédito.

Ele deve orientar qualquer IA ou pessoa que vá trabalhar no repositório, deixando claro:

* qual notebook faz o quê;
* quais arquivos cada etapa consome;
* quais arquivos cada etapa gera;
* quais decisões metodológicas já foram tomadas;
* qual é a fonte rastreável das métricas do modelo;
* onde o notebook 06 deve começar;
* quais outputs sustentam a apresentação gerencial final.

---

## 2. Fluxo geral

```text
00_validacao_ambiente
→ 01_diagnostico_bases
→ 02_target_inadimplencia_12m
→ 03_eda_credito
→ 04_modelagem_pd
→ 05_politica_concessao_credito
→ 06_cenarios_politica_recomendacao
→ 99_relatorio_final
```

A lógica do projeto é:

```text
bases brutas
→ diagnóstico
→ target de inadimplência 12m
→ EDA orientada à política
→ modelo de PD
→ score/rating interno
→ política de limite
→ cenários de apetite de risco
→ recomendação final
→ apresentação gerencial
```

---

## 3. Notebook 00 — Validação do ambiente

### Objetivo

Validar se o ambiente local está pronto para executar o projeto.

### Entradas

```text
data/raw/concessao.csv
data/raw/inadimplencia.csv
```

### Validações

* versão do Python;
* imports principais;
* estrutura de diretórios;
* leitura das bases;
* configuração visual do Plotly;
* funcionamento de gráficos.

### Saídas esperadas

Não gera base analítica principal.

Serve como sanity check do projeto.

---

## 4. Notebook 01 — Diagnóstico das bases

### Objetivo

Entender a estrutura e a qualidade inicial das bases brutas.

### Entradas

```text
data/raw/concessao.csv
data/raw/inadimplencia.csv
```

### Principais achados

```text
concessao: 30.000 linhas
inadimplencia: 257.960 linhas
duplicadas: 0 nas duas bases
clientes únicos em concessao: 30.000
clientes com acompanhamento: 28.700
clientes só em concessao: 1.300
janela concessao: 2019-08-20 a 2022-08-18
janela inadimplencia: 2019-09-30 a 2022-07-31
nulos em escolaridade: 414
```

### Tratamentos importantes

* padronização de escolaridade com `.str.strip()`;
* criação de variáveis diagnósticas;
* verificação de cobertura entre bases;
* validação de duplicidades;
* avaliação da janela temporal disponível.

### Saídas

```text
data/interim/concessao_diagnostico.parquet
data/interim/inadimplencia_diagnostico.parquet
```

---

## 5. Notebook 02 — Target de inadimplência 12m

### Objetivo

Criar o target principal de inadimplência 12 meses após a concessão.

### Entradas

```text
data/interim/concessao_diagnostico.parquet
data/interim/inadimplencia_diagnostico.parquet
```

### Lógica

Para cada concessão:

1. calcular data de referência 12 meses após a concessão;
2. ajustar para fim de mês;
3. verificar se existe janela completa de acompanhamento;
4. buscar inadimplência no mês 12;
5. criar `target_inadimplente_12m`;
6. separar operações sem janela completa.

### Saídas

```text
data/processed/base_concessao_com_target_12m.parquet
data/processed/base_modelagem_12m.parquet
data/processed/base_scoring_sem_janela_12m.parquet
```

### Resultado principal

```text
operações totais: 30.000
operações com janela completa: 19.558
operações sem janela suficiente: 10.442
taxa de inadimplência 12m: aproximadamente 12,3%
```

### Observação metodológica

Quando havia janela suficiente, mas não havia registro exatamente no mês 12, foi adotada a premissa de cliente adimplente/quitado naquele ponto.

Essa premissa deve permanecer documentada.

O target `target_inadimplente_12m` deve ser usado apenas para modelagem e backtest, nunca como regra operacional de decisão de crédito.

---

## 6. Notebook 03 — EDA orientada à política de crédito

### Objetivo

Identificar quais variáveis ajudam a explicar risco e podem apoiar uma política de concessão.

### Entrada

```text
data/processed/base_modelagem_12m.parquet
```

### Variáveis analisadas

* safra;
* renda;
* valor emprestado;
* parcela;
* comprometimento de renda;
* valor de restritivos;
* restritivos sobre renda;
* prazo;
* taxa;
* idade;
* tempo de conta;
* escolaridade;
* cliente ativo;
* agência.

### Principais achados

```text
taxa média de inadimplência: aproximadamente 12,3%
renda isolada não separa bem bons e maus pagadores
comprometimento de renda é relevante
restritivos são relevantes
cliente inativo tem inadimplência acima da média
pouco tempo de conta tem inadimplência acima da média
idade mais baixa apresenta maior risco
agência deve ser usada para monitoramento, não como regra direta
escolaridade pode ajudar no modelo, mas exige cautela
```

### Conclusão operacional

A política não deve depender apenas de renda.

A política deve combinar:

```text
PD estimada
+ capacidade de pagamento
+ restritivos
+ relacionamento
+ limite máximo sugerido
```

---

## 7. Notebook 04 — Modelagem de PD

### Objetivo

Treinar um modelo para estimar a probabilidade de inadimplência em 12 meses.

### Entrada

```text
data/processed/base_modelagem_12m.parquet
```

### Target

```text
target_inadimplente_12m
```

### Variáveis principais

Numéricas:

```text
valor_emprestado
valor_parcela
valor_taxa
valor_prazo
valor_renda
valor_restritivos
idade_concessao
tempo_conta_anos
comprometimento_renda
restritivos_sobre_renda
```

Categóricas:

```text
cat_escolaridade
flag_cliente_ativo
```

### Decisões metodológicas

* split temporal;
* treino com concessões mais antigas;
* teste com concessões mais recentes;
* Optuna apenas dentro do treino;
* teste temporal final preservado para avaliação fora da amostra;
* `target_inadimplente_12m` usado apenas como variável resposta;
* variáveis posteriores à concessão não devem entrar como features;
* `cod_agencia` não deve ser usado como regra de decisão de crédito.

### Modelos candidatos

```text
gradient_boosting
random_forest
logistica
```

### Modelo escolhido

O modelo escolhido para alimentar a política é o:

```text
gradient_boosting
```

Esse modelo gera o `pd_score` usado posteriormente para construir o rating interno e simular a política de concessão.

### Métricas comparativas do notebook 04

O arquivo:

```text
outputs/tables/modelagem_metricas_modelos.csv
```

registra as métricas comparativas dos modelos avaliados no notebook 04.

Na execução rastreável do projeto, a linha do modelo `gradient_boosting` apresenta aproximadamente:

```text
AUC treino: 0,9041
AUC teste: 0,8720
Average Precision teste: 0,5433
KS teste: 0,5915
Brier Score teste: 0,0778
Log Loss teste: 0,2589
```

Essas métricas são úteis para comparar os modelos candidatos.

### Métricas rastreáveis do score usado na política

A apresentação gerencial e a recomendação final devem usar como referência principal as métricas recalculadas diretamente sobre a base de score usada na política:

```text
data/processed/base_politica_validacao_com_score.parquet
```

usando:

```text
target_inadimplente_12m
pd_score
```

Métricas recalculadas sobre a base efetivamente usada para rating e política:

```text
n validação: 4.862 operações/propostas
bad rate da base de validação: 12,30%

AUC teste: aproximadamente 0,8739
KS teste: aproximadamente 0,5900
Average Precision: aproximadamente 0,5494
Brier Score: aproximadamente 0,0774
Log Loss: aproximadamente 0,2591

PD mínima: aproximadamente 0,0047
PD média: aproximadamente 0,1237
PD máxima: aproximadamente 0,9214
```

Essas métricas devem ser salvas em:

```text
outputs/tables/modelagem_metricas_score_politica.csv
```

### Interpretação

O score ordena bem o risco.

A análise por decis/rating mostra concentração de inadimplentes nas faixas de maior risco.

O modelo deve ser tratado como uma camada de mensuração de risco, não como a política de crédito em si.

### Observação de rastreabilidade

Para evitar inconsistência entre código, tabelas e apresentação:

* a apresentação deve usar AUC ≈ 0,874 e KS ≈ 0,590;
* não usar métricas antigas ou não rastreáveis no deck;
* quando houver divergência entre números arredondados, priorizar a métrica recalculada diretamente sobre `base_politica_validacao_com_score.parquet`;
* qualquer nova versão da apresentação deve citar as métricas do score efetivamente usado na política.

### Saídas esperadas

```text
outputs/models/modelo_pd_gradient_boosting.joblib
outputs/tables/modelagem_metricas_modelos.csv
outputs/tables/modelagem_decis_score_teste.csv
outputs/tables/modelagem_metricas_score_politica.csv
```

Os nomes exatos dos artefatos podem variar, mas o notebook 05 deve conseguir carregar ou aplicar o pipeline candidato que gera o `pd_score`.

---

## 8. Notebook 05 — Política inicial e interpretação

### Objetivo

Transformar o score de PD em uma política inicial de concessão e validar a coerência do modelo.

### Entradas

```text
data/processed/base_modelagem_12m.parquet
outputs/models/modelo_pd_*.joblib
```

### Etapas

1. aplicar modelo de PD;
2. gerar `pd_score`;
3. criar faixas de risco;
4. definir percentuais máximos de parcela/renda;
5. aplicar redutores por restritivos e relacionamento;
6. calcular valor máximo sugerido;
7. classificar decisão da política;
8. simular resultado histórico;
9. interpretar modelo com permutation importance e SHAP.

### Faixas de risco

```text
A - Baixo risco
B - Médio-baixo risco
C - Médio risco
D - Alto risco
E - Muito alto risco
```

### Decisões da política inicial

```text
Aprovar valor solicitado
Aprovar valor reduzido
Análise manual
Recusar
```

### Resultado da política inicial

```text
taxa histórica de inadimplência: aproximadamente 12,3%
aprovação automática simulada: aproximadamente 74,95%
inadimplência dos aprovados: aproximadamente 3,9%
redução simulada de exposição: aproximadamente 60,66%
```

### Interpretação do modelo

A interpretação indicou que o modelo está usando sinais coerentes:

* escolaridade;
* comprometimento de renda;
* cliente ativo;
* valor de restritivos;
* tempo de conta;
* restritivos sobre renda;
* idade.

### Conclusão

A política inicial é coerente, mas conservadora/diagnóstica.

Ela deve ser tratada como um cenário de referência, não como recomendação final.

A política final recomendada é construída no notebook 06, com uma camada mais completa de limite por rating, renda, capacidade de pagamento, teto e fatores de ajuste.

### Saída obrigatória para o notebook 06

```text
data/processed/base_politica_validacao_com_score.parquet
```

Essa base deve conter:

```text
pd_score
faixa_risco
decisao_politica
valor_maximo_sugerido
valor_aprovado
variáveis de renda, restritivos, operação e relacionamento
target_inadimplente_12m
```

A base `base_politica_validacao_com_score.parquet` é a fonte canônica para:

* rating interno;
* simulação dos cenários;
* métricas do score usado na política;
* backtest da política final.

---

## 9. Notebook 06 — Cenários de política e recomendação final

### Objetivo

Comparar diferentes cenários de apetite de risco e escolher uma política final recomendada.

### Entrada principal

```text
data/processed/base_politica_validacao_com_score.parquet
```

### Princípio metodológico

O notebook 06 não deve recomeçar o case.

Ele deve partir da base com `pd_score` e `faixa_risco`, gerada pelo notebook 05, e transformar o rating em uma política de limite.

O notebook 06 não deve:

* retreinar modelo;
* recriar target;
* usar target como regra de decisão;
* usar inadimplência posterior como variável de política;
* usar `cod_agencia` como regra de decisão;
* criar variáveis inexistentes, como LGD, EAD formal, garantia, colateral ou bureau externo completo.

### O que o notebook 06 deve fazer

1. validar contrato de dados;
2. diagnosticar a política inicial;
3. documentar variáveis disponíveis e ausentes;
4. caracterizar o público por rating, renda, relacionamento e restritivos;
5. validar o rating por PD e bad rate observado;
6. construir cenários conservador, equilibrado e expansivo;
7. simular cada cenário;
8. comparar aprovação, inadimplência e exposição;
9. escolher cenário recomendado;
10. gerar tabela de política final;
11. gerar tabelas de auditoria;
12. documentar limitações e próximos passos.

### Política final recomendada

O cenário recomendado na versão final do projeto é:

```text
Expansivo controlado
```

Indicadores principais do cenário recomendado:

```text
valor aprovado total: aproximadamente R$ 20,84 mi
exposição aprovada: aproximadamente 32,26%
aprovação automática total: aproximadamente 60,86%
aprovação integral: aproximadamente 23,53%
aprovação com valor reduzido: aproximadamente 37,33%
análise manual: aproximadamente 29,10%
recusa: aproximadamente 10,04%
bad rate observado dos aprovados: aproximadamente 2,23%
taxa histórica de inadimplência da base: aproximadamente 12,30%
```

### Interpretação da recomendação

O cenário Expansivo controlado amplia a exposição aprovada em relação ao Base/Equilibrado, mas mantém controles relevantes:

```text
C com controles adicionais
D em análise manual
E recusado
```

O incremento de valor aprovado do cenário Expansivo controlado versus Base/Equilibrado é de aproximadamente:

```text
Total: +R$ 3,70 mi
A: +R$ 1,93 mi
B: +R$ 1,54 mi
C: +R$ 0,22 mi
D: R$ 0
E: R$ 0
A+B: aproximadamente 93,9% do incremento
```

Essa decomposição sustenta a leitura de que a expansão não vem da cauda de maior risco.

### Saídas principais esperadas

Base simulada:

```text
data/processed/base_simulacao_cenarios_politica.parquet
```

Tabelas de contrato, público e política:

```text
outputs/tables/politica_contrato_dados_cenarios.csv
outputs/tables/politica_variaveis_disponiveis_limitacoes.csv
outputs/tables/politica_publico_faixa_renda_rating.csv
outputs/tables/politica_publico_rating_tempo_relacionamento.csv
outputs/tables/politica_publico_rating_pd_bad_rate.csv
outputs/tables/politica_publico_rating_exposicao.csv
outputs/tables/politica_publico_rating_restritivos.csv
outputs/tables/politica_parametros_limite_cenarios.csv
outputs/tables/politica_impacto_financeiro_cenarios.csv
outputs/tables/politica_impacto_por_rating.csv
outputs/tables/politica_impacto_por_decisao.csv
outputs/tables/politica_score_gerencial_cenarios.csv
outputs/tables/politica_final_recomendada_limites.csv
```

Tabelas adicionais de auditoria e defesa da política:

```text
outputs/tables/politica_exposicao_incremental_por_rating.csv
outputs/tables/politica_aprovacao_integral_reduzida_por_rating.csv
outputs/tables/politica_manual_por_rating.csv
outputs/tables/politica_capacidade_comprometimento_por_rating.csv
outputs/tables/politica_auditoria_resumo_executivo.csv
outputs/tables/politica_backtest_integral_reduzido.csv
outputs/tables/politica_risco_ponderado_exposicao.csv
outputs/tables/politica_unidade_analise_validacao.csv
```

Figuras esperadas:

```text
outputs/figures/06_publico_distribuicao_rating.html
outputs/figures/06_publico_bad_rate_rating.html
outputs/figures/06_publico_renda_rating.html
outputs/figures/06_impacto_exposicao_cenarios.html
outputs/figures/06_impacto_por_rating.html
outputs/figures/06_tradeoff_aprovacao_inadimplencia.html
outputs/figures/06_valor_solicitado_vs_aprovado.html
```

### Limitações específicas do backtest da política

O notebook 06 deve registrar explicitamente:

* base contém apenas operações concedidas;
* ausência de propostas recusadas limita reject inference;
* performance fora da política histórica precisa de piloto controlado;
* sem LGD, EAD formal, garantia conhecida ou margem;
* sem bureau externo completo;
* capacidade considera a nova parcela simulada sobre a renda informada, não o endividamento externo total;
* para aprovações com valor reduzido, o backtest usa o desfecho observado da operação originalmente concedida;
* a performance da operação reduzida deve ser validada em piloto;
* bad rate dos aprovados é medido por operação aprovada;
* risco incremental em valor deve ser monitorado por rating e exposição aprovada;
* parâmetros finais precisam ser validados com a área de política de crédito.

---

## 10. Notebook 99 — Relatório final

### Objetivo

Consolidar o case em formato de relatório comentado.

Esse notebook deve ser feito depois do notebook 06.

### Conteúdo esperado

* contexto do problema;
* descrição das bases;
* criação do target;
* EDA;
* modelagem de PD;
* métricas rastreáveis do score usado na política;
* interpretação;
* política recomendada;
* impacto financeiro;
* limitações;
* próximos passos.

### Métricas do modelo a usar no relatório final

O relatório final deve priorizar as métricas recalculadas sobre a base de score da política:

```text
outputs/tables/modelagem_metricas_score_politica.csv
```

Números de referência:

```text
AUC teste: aproximadamente 0,8739
KS teste: aproximadamente 0,5900
Average Precision: aproximadamente 0,5494
Brier Score: aproximadamente 0,0774
Log Loss: aproximadamente 0,2591
```

### Política final a usar no relatório

O relatório deve usar como política final a tabela:

```text
outputs/tables/politica_final_recomendada_limites.csv
```

E como principais tabelas de impacto:

```text
outputs/tables/politica_impacto_financeiro_cenarios.csv
outputs/tables/politica_impacto_por_rating.csv
outputs/tables/politica_impacto_por_decisao.csv
outputs/tables/politica_exposicao_incremental_por_rating.csv
outputs/tables/politica_auditoria_resumo_executivo.csv
```

---

## 11. Regras para continuidade do projeto

Qualquer IA ou pessoa trabalhando no projeto deve seguir estas regras:

1. não alterar notebooks anteriores sem autorização;
2. não alterar dados brutos;
3. não recriar o target se ele já existe;
4. não retreinar modelo no notebook 06;
5. não usar target como feature;
6. não usar inadimplência posterior como variável de política;
7. não inventar variáveis de garantia, PJ, CNAE, faturamento, LGD, EAD formal ou bureau externo completo;
8. manter o padrão visual do projeto;
9. salvar todas as saídas relevantes;
10. documentar limitações explicitamente;
11. manter rastreabilidade entre notebook, CSV, HTML e apresentação;
12. não usar métricas antigas ou não rastreáveis na apresentação;
13. não usar `cod_agencia` como regra de concessão;
14. não afirmar maximização de retorno econômico sem LGD, EAD, margem e precificação;
15. não tratar simulação histórica como política definitiva de produção.

---

## 12. Regras de consistência da política final

A política final deve respeitar:

```text
valor aprovado nunca supera valor solicitado
análise manual tem valor aprovado automático zero
recusa tem valor aprovado automático zero
rating D não possui aprovação automática
rating E é recusado
não há teto infinito
target é usado apenas no backtest
agência não é usada como regra de decisão
```

Aprovação automática total deve ser entendida como:

```text
Aprovar valor solicitado
+
Aprovar valor reduzido
```

No cenário recomendado:

```text
aprovação automática total: aproximadamente 60,86%
aprovação integral: aproximadamente 23,53%
aprovação com valor reduzido: aproximadamente 37,33%
```

---

## 13. Pontos de atenção para apresentação gerencial

A apresentação final deve estar alinhada aos outputs rastreáveis.

### Métricas do slide de modelo/rating

Usar:

```text
AUC teste: 0,874
KS teste: 0,590
```

Evitar usar:

```text
AUC 0,8752
KS 0,5919
gap treino-teste 0,0126
```

a menos que esses números estejam claramente rastreáveis a uma nova execução documentada.

### Público analisado

Preferir o termo:

```text
4.862 operações/propostas de crédito PF
```

em vez de:

```text
4.862 correntistas pessoa física
```

caso a base esteja em nível de operação/proposta.

### Bad rate dos aprovados

Explicar que:

```text
bad rate é medido por operação aprovada
```

e que:

```text
risco incremental em valor deve ser acompanhado por rating, conforme apêndice
```

### Aprovação com valor reduzido

Registrar a limitação:

```text
Para aprovações com valor reduzido, o backtest usa o desfecho observado da operação originalmente concedida; a performance da operação reduzida deve ser validada em piloto.
```

### Exposição incremental por rating

Manter a leitura:

```text
93,9% do incremento de valor aprovado está concentrado em A/B
D/E não recebem incremento automático
```

---

## 14. Resumo executivo do fluxo

O projeto construiu uma base de modelagem, treinou um modelo de PD, gerou um score/rating interno e simulou uma política de concessão baseada em limite.

A política final recomendada é o cenário:

```text
Expansivo controlado
```

Essa política combina:

```text
rating interno
+ renda
+ multiplicador de renda
+ capacidade de pagamento
+ teto por rating
+ fatores de ajuste de limite
+ decisão automática/manual/recusa
+ impacto financeiro
```

O score de PD é uma camada de mensuração de risco.

A política de concessão transforma esse score em uma decisão acionável de crédito, com limite em reais e impacto financeiro mensurável.

A recomendação final deve ser tratada como política inicial baseada em evidência histórica e precisa ser validada com a área de política de crédito antes de qualquer uso produtivo.
