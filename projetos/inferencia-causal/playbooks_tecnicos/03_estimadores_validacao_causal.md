# Playbook de Estimadores e Validação Causal

## 1. Objetivo

Este playbook orienta a escolha, validação e interpretação de estimadores causais em projetos aplicados.

O foco é garantir que a estratégia de modelagem seja compatível com:

- desenho dos dados;
- mecanismo de tratamento;
- assumptions;
- objetivo de decisão;
- risco de viés;
- disponibilidade de controle;
- necessidade de heterogeneidade.

---

## 2. Assumptions principais

### Consistência

O outcome observado para uma unidade tratada corresponde ao outcome potencial sob o tratamento recebido.

Risco:

- múltiplas versões do tratamento;
- intensidade variável;
- canal diferente;
- execução operacional inconsistente.

---

### Exchangeability / ignorabilidade

Condicionalmente às covariáveis observadas, o tratamento é independente dos outcomes potenciais.

Risco:

- confundidores não observados;
- seleção operacional;
- targeting prévio;
- regras de negócio não capturadas nos dados.

---

### Positividade / overlap

Para cada perfil relevante, deve existir probabilidade positiva de receber e não receber o tratamento.

Risco:

- alguns grupos sempre tratados;
- alguns grupos nunca tratados;
- propensities próximas de 0 ou 1.

---

### SUTVA

O tratamento de uma unidade não afeta o outcome de outra, e não existem versões múltiplas não modeladas do tratamento.

Risco:

- efeito de rede;
- contaminação entre usuários;
- comunicação entre clientes;
- spillover geográfico;
- interferência operacional.

---

## 3. Diagnósticos antes da modelagem

Antes de estimar efeito:

- comparar tratados e controles;
- avaliar distribuição de covariáveis;
- estimar propensity score;
- checar overlap;
- avaliar balanceamento;
- verificar missing por grupo;
- verificar outcome bruto por período;
- verificar tratamento por tempo;
- identificar mudanças de política;
- validar elegibilidade.

---

## 4. Escolha do estimador

### Experimento randomizado

Quando usar:

- tratamento randomizado;
- grupo controle explícito;
- assignment conhecido.

Estimadores:

- diferença de médias;
- regressão ajustada;
- regressão com interação;
- análise por estratos;
- uplift por decil.

Cuidados:

- checar SRM;
- checar balanceamento;
- checar attrition;
- checar contaminação;
- checar múltiplos testes.

---

### Regressão ajustada

Quando usar:

- dado observacional com bons controles;
- relação aproximadamente bem especificada;
- necessidade de baseline interpretável.

Cuidados:

- sensível à especificação;
- não resolve confundimento não observado;
- pode extrapolar em regiões sem overlap.

---

### Propensity Score Matching

Quando usar:

- necessidade de comparar unidades similares;
- tratamento binário;
- overlap razoável.

Cuidados:

- perda de amostra;
- sensível ao modelo de propensão;
- não resolve confundimento não observado.

---

### IPW

Quando usar:

- objetivo de reponderar população;
- bom modelo de propensão;
- overlap aceitável.

Cuidados:

- pesos extremos;
- alta variância;
- necessidade de estabilização/trimming.

---

### Doubly Robust

Quando usar:

- combinar modelo de outcome e propensity;
- aumentar robustez;
- contexto observacional.

Cuidados:

- ainda depende de ignorabilidade;
- exige validação de ambos os modelos.

---

### S-Learner

Quando usar:

- baseline simples;
- tratamento com efeito forte;
- bom volume de dados.

Risco:

- modelo pode regularizar o tratamento para zero;
- pode subestimar uplift sutil.

---

### T-Learner

Quando usar:

- bons volumes em tratado e controle;
- efeitos diferentes entre grupos;
- simplicidade desejada.

Risco:

- alta variância;
- instabilidade se grupos forem desbalanceados.

---

### X-Learner

Quando usar:

- forte desbalanceamento entre tratados e controles;
- necessidade de imputar contrafactuais;
- foco em CATE.

Risco:

- implementação mais complexa;
- sensível aos modelos base.

---

### DML

Quando usar:

- muitos controles;
- alta dimensionalidade;
- objetivo de reduzir viés de regularização;
- dado observacional com bons confundidores.

Risco:

- assumptions continuam necessárias;
- mais difícil de explicar;
- exige validação cuidadosa.

---

### Causal Forest

Quando usar:

- foco em heterogeneidade;
- efeitos não lineares;
- muitos segmentos potenciais.

Risco:

- interpretação mais complexa;
- precisa de amostra suficiente;
- efeitos locais podem ser instáveis.

---

## 5. Validação causal

A avaliação deve incluir:

- estimativa média;
- heterogeneidade;
- balanceamento;
- overlap;
- sensibilidade;
- estabilidade temporal;
- análise por segmento;
- intervalos de confiança, quando aplicável;
- comparação com baseline;
- interpretação substantiva.

---

## 6. O que não reportar de forma isolada

Evitar vender como evidência causal:

- acurácia;
- F1;
- ROC-AUC;
- feature importance pura;
- correlação;
- ranking de propensão;
- diferença bruta sem ajuste em dado observacional.

Essas métricas podem ser úteis em modelagem preditiva, mas não validam causalidade.