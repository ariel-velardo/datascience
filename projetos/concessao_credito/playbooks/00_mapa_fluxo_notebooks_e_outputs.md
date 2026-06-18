# Playbook — Mapa do fluxo dos notebooks e outputs

## 1. Objetivo

Este playbook descreve o fluxo completo do projeto de concessão de crédito.

Ele deve orientar qualquer IA ou pessoa que vá trabalhar no repositório, deixando claro:

* qual notebook faz o quê;
* quais arquivos cada etapa consome;
* quais arquivos cada etapa gera;
* quais decisões metodológicas já foram tomadas;
* onde o notebook 06 deve começar.

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
* verificação de cobertura entre bases.

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
* teste temporal final preservado para avaliação fora da amostra.

### Modelo candidato

```text
gradient_boosting_optuna
```

### Métricas principais

```text
AUC teste: aproximadamente 0,8752
KS teste: aproximadamente 0,5919
Average Precision: aproximadamente 0,5547
Brier Score: aproximadamente 0,0768
Log Loss: aproximadamente 0,2563
```

### Interpretação

O score ordenou bem o risco.

A análise por decis mostrou concentração de inadimplentes nas faixas de maior risco.

### Saídas esperadas

```text
outputs/models/modelo_pd_gradient_boosting_optuna.joblib
outputs/tables/modelagem_metricas_modelos.csv
outputs/tables/modelagem_decis_score_teste.csv
```

Os nomes exatos podem variar, mas o notebook 05 deve ter conseguido carregar o pipeline candidato.

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

A política inicial é coerente, mas conservadora.

Ela deve ser tratada como um cenário de referência, não necessariamente como recomendação final.

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

---

## 9. Notebook 06 — Cenários de política e recomendação final

### Objetivo

Comparar diferentes cenários de apetite de risco e escolher uma política final recomendada.

### Entrada principal

```text
data/processed/base_politica_validacao_com_score.parquet
```

### O que o notebook 06 deve fazer

1. validar contrato de dados;
2. diagnosticar a política inicial;
3. documentar variáveis disponíveis e ausentes;
4. construir cenários conservador, equilibrado e expansivo;
5. simular cada cenário;
6. comparar aprovação, inadimplência e exposição;
7. escolher cenário recomendado;
8. gerar tabela de política final;
9. documentar limitações e próximos passos.

### Saídas esperadas

```text
data/processed/base_simulacao_cenarios_politica.parquet

outputs/tables/politica_contrato_dados_cenarios.csv
outputs/tables/politica_variaveis_disponiveis_limitacoes.csv
outputs/tables/politica_resumo_cenarios.csv
outputs/tables/politica_resumo_decisoes_cenarios.csv
outputs/tables/politica_score_decisao_cenarios.csv
outputs/tables/politica_final_recomendada.csv

outputs/figures/06_tradeoff_cenarios_politica.html
outputs/figures/06_taxas_decisao_por_cenario.html
outputs/figures/06_inadimplencia_aprovados_por_cenario.html
outputs/figures/06_exposicao_aprovada_por_cenario.html
outputs/figures/06_decisoes_por_faixa_risco.html
```

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
* interpretação;
* política recomendada;
* limitações;
* próximos passos.

---

## 11. Regras para continuidade do projeto

Qualquer IA ou pessoa trabalhando no projeto deve seguir estas regras:

1. não alterar notebooks anteriores sem autorização;
2. não alterar dados brutos;
3. não recriar o target se ele já existe;
4. não retreinar modelo no notebook 06;
5. não usar target como feature;
6. não usar inadimplência posterior como variável de política;
7. não inventar variáveis de garantia, PJ, CNAE ou bureau;
8. manter o padrão visual do projeto;
9. salvar todas as saídas relevantes;
10. documentar limitações explicitamente.

---

## 12. Resumo executivo do fluxo

O projeto já construiu uma base de modelagem, treinou um modelo de PD e criou uma política inicial.

O notebook 06 não deve recomeçar o case.

Ele deve partir da base com score, simular cenários de política e escolher uma recomendação final para concessão de crédito.
