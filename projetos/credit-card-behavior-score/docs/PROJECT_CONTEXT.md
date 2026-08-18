# Credit Card Behavior Score — Contexto do Projeto

## 1. Objetivo

Desenvolver uma solução de score comportamental de risco de crédito para uma carteira de clientes já existentes de cartão de crédito.

O modelo deverá estimar o risco relativo futuro dos clientes e converter sua saída em um score operacional entre 0 e 1000, sendo:

- 1000: clientes de menor risco estimado;
- 0: clientes de maior risco estimado.

O score deverá servir como instrumento analítico para apoiar decisões relacionadas a:

- aumento de limite;
- manutenção de limite;
- congelamento de limite;
- redução de limite;
- segmentação comportamental de risco;
- estratégias de relacionamento;
- potenciais ações de cross-sell e up-sell quando combinadas com outras informações de negócio.

O modelo será tratado como um instrumento de ordenação de risco e não, isoladamente, como uma política completa de crédito.

---

## 2. Tipo de Problema

Problema supervisionado de classificação binária com estrutura temporal.

Variável alvo:

Ever30Mob6

A documentação disponibilizada não apresenta a definição formal da variável Ever30Mob6.

Portanto:

- não inventar sua definição de negócio;
- considerar alvo = 1 como ocorrência do evento adverso observado;
- qualquer interpretação adicional deverá ser explicitamente identificada como hipótese.

---

## 3. Base de Dados

Estrutura esperada:

- aproximadamente 200 mil observações;
- 13 safras mensais;
- 15 variáveis explicativas;
- 10 variáveis numéricas;
- 5 variáveis categóricas;
- 1 variável alvo binária;
- identificador de cliente;
- safra de referência.

Campos que inicialmente não devem ser utilizados como atributos preditivos:

- index;
- id;
- data_ref_safra.

A safra será utilizada principalmente para:

- análises temporais;
- divisão das amostras;
- validação fora do tempo;
- análises de estabilidade.

---

## 4. Princípios de Modelagem

### 4.1 Validação temporal

Uma divisão aleatória entre treino e teste não será a abordagem principal.

O desenho preferencial será:

safras mais antigas -> treino

safras intermediárias -> validação

safras mais recentes -> teste fora do tempo (OOT)

As janelas exatas somente serão definidas depois da auditoria dos dados.

### 4.2 Prevenção de vazamento de informação

Todos os parâmetros de preparação dos dados devem ser aprendidos utilizando somente a amostra de treino.

Isso inclui:

- estatísticas de imputação;
- codificadores;
- parâmetros de padronização;
- critérios de seleção de variáveis;
- otimização de hiperparâmetros.

Variáveis suspeitas e valores especiais devem ser investigados antes de qualquer transformação.

### 4.3 Começar simples antes de aumentar a complexidade

Modelo de referência:

Regressão Logística.

Principal modelo challenger inicialmente considerado:

CatBoost.

Outros modelos somente serão adicionados quando responderem a uma pergunta analítica específica.

O objetivo não é maximizar a quantidade de algoritmos testados.

### 4.4 Avaliação dos modelos

O modelo não será selecionado apenas por acurácia.

As principais dimensões de avaliação serão:

- discriminação;
- capacidade de ordenação;
- calibração;
- estabilidade temporal;
- interpretabilidade;
- aplicabilidade ao negócio.

Métricas candidatas:

- ROC-AUC;
- Gini;
- KS;
- PR-AUC;
- Brier Score;
- curva de calibração;
- lift;
- captura acumulada de eventos;
- taxa de evento por faixa de score.

### 4.5 Seleção de variáveis

A seleção deverá considerar conjuntamente:

- contribuição preditiva;
- redundância;
- estabilidade temporal;
- ausência de dados;
- comportamento de valores especiais;
- risco de vazamento;
- interpretabilidade.

Nenhuma variável deverá ser removida apenas por causa de uma única estatística univariada.

### 4.6 Desbalanceamento de classes

O desbalanceamento deverá primeiro ser medido.

Técnicas de reamostragem não serão aplicadas automaticamente.

Caso pesos ou reamostragem sejam avaliados, deverão ser novamente analisadas:

- calibração das probabilidades;
- representatividade da população;
- desempenho fora do tempo.

### 4.7 Explicabilidade

A interpretabilidade é parte central da solução.

Técnicas candidatas:

- coeficientes da Regressão Logística;
- análises univariadas;
- importância por permutação;
- SHAP para modelos não lineares;
- dependência parcial quando agregar interpretação.

### 4.8 Estabilidade

A estabilidade será avaliada entre as diferentes safras.

Monitorar:

- taxa do evento;
- AUC/Gini;
- KS;
- score médio;
- distribuição do score;
- PSI;
- distribuição das principais variáveis.

---

## 5. Construção do Score

A probabilidade estimada pelo modelo será convertida para uma escala:

0 a 1000.

Direção:

0 -> maior risco estimado

1000 -> menor risco estimado

A transformação deverá:

- preservar a ordem do modelo sem inversões, admitindo apenas empates nas caudas
  quando houver clipping;
- ser determinística;
- ser documentada;
- evitar interpretações arbitrárias.

A transformação log-odds/PDO foi aprovada com a seguinte convenção operacional:

- Base Score = 600;
- PDO = 50;
- Base Odds = 20:1;
- odds = `(1 - p) / p`;
- clipping operacional em [0, 1000].

Os parâmetros foram escolhidos exclusivamente pelo diagnóstico da distribuição
das probabilidades do Desenvolvimento, sem target e sem uso do OOT. A
transformação não altera as probabilidades, a discriminação ou a ordenação do
modelo antes de eventuais empates nas caudas causados pelo clipping.

---

## 6. Segmentação do Score

O score final será analisado por faixas de risco.

Para cada faixa serão avaliados:

- participação da população;
- taxa observada do evento adverso;
- probabilidade média prevista;
- score médio;
- lift;
- captura acumulada de eventos.

Comportamento desejável:

score maior -> menor taxa observada do evento adverso.

---

## 7. Interpretação de Negócio

O modelo deverá permitir segmentações como:

Muito Baixo Risco

Baixo Risco

Médio Risco

Alto Risco

Muito Alto Risco

Possíveis ações ilustrativas:

- crescimento;
- manutenção;
- congelamento;
- revisão;
- redução.

Essas ações serão apresentadas como possibilidades analíticas e não como política ótima.

A base não contém informações suficientes para otimizar economicamente uma política de crédito, pois não estão disponíveis variáveis como:

- exposição;
- rentabilidade;
- utilização;
- LGD;
- receita;
- custo de capital;
- restrições da política.

---

## 8. Entregáveis

Principal artefato técnico:

notebooks/credit_card_behavior_score.ipynb

O notebook final deverá conter:

- todas as células executadas;
- outputs;
- gráficos;
- comentários técnicos;
- análises e interpretações.

Quando pertinente, utilizar as marcações solicitadas:

"Comentário Técnico:"

"Análise/Interpretação:"

Artefato executivo:

apresentação com no máximo 5 slides principais.

Slides adicionais poderão existir como apoio, caso necessário.

---

## 9. Filosofia do Projeto

O objetivo não é construir o modelo mais complexo possível.

O objetivo é construir a solução analítica mais defensável possível.

Prioridades:

1. formulação correta do problema;
2. qualidade dos dados;
3. prevenção de vazamento;
4. validação temporal;
5. capacidade discriminatória;
6. estabilidade;
7. explicabilidade;
8. utilidade do score;
9. comunicação de negócio;
10. reprodutibilidade.

---

## 10. Fora do Escopo Principal

O projeto não priorizará:

- desenvolvimento de API de produção;
- implantação em nuvem;
- Kubernetes;
- inferência em tempo real;
- feature store;
- infraestrutura extensa de MLOps;
- teste indiscriminado de dezenas de modelos.

Uma arquitetura de produção poderá ser discutida conceitualmente caso agregue valor, mas não é o objetivo central da entrega.

---

## 11. Status Atual

As etapas de auditoria, diagnóstico temporal, desenvolvimento, congelamento do
candidato e avaliação final OOT foram concluídas tecnicamente.

O split temporal 8/2/3 está aprovado:

- Treino: 2019-01 a 2019-08;
- Validação: 2019-09 a 2019-10;
- OOT: 2019-11 a 2020-01.

O candidato CatBoost foi congelado antes da abertura do OOT. A especificação
final utiliza 13 features originais, com `var12` representada por
`var12_estado`. O refit final foi realizado em todo o Desenvolvimento — Treino
mais Validação — com 611 árvores, sem recalibração e sem linhas OOT no ajuste.

A avaliação OOT foi concluída sem alterar modelo, features, tratamentos,
hiperparâmetros, calibração ou protocolo. O resultado técnico foi classificado
como **B — boa capacidade de ordenação fora do tempo, com variabilidade temporal
material**.

A convenção da escala também está aprovada: Base Score = 600, PDO = 50 e Base
Odds = 20:1, com odds `(1 - p) / p`, score maior indicando menor risco estimado e
clipping operacional em [0, 1000].

O score, as cinco faixas de risco definidas em D021, a estabilidade temporal e o
PSI do score foram implementados e avaliados. A fase seguinte é a consolidação da
camada ilustrativa de aplicação ao negócio e da apresentação executiva.
