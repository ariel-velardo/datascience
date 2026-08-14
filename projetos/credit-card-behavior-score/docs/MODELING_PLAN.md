# Plano de Modelagem

## Etapa 0 — Estruturação do Projeto

Objetivos:

- estruturar o repositório;
- documentar premissas metodológicas;
- definir instruções para agentes de IA;
- estabelecer padrões de reprodutibilidade;
- estabelecer padrão visual.

Entregáveis:

- PROJECT_CONTEXT.md
- MODELING_PLAN.md
- DECISIONS.md
- AI_USAGE.md
- AGENTS.md
- CLAUDE.md

Status: em andamento.

---

## Etapa 1 — Auditoria dos Dados

Notebook:

00_data_audit.ipynb

Perguntas principais:

1. Qual é a dimensão real da base?
2. Quais colunas existem?
3. Quais são os tipos das variáveis?
4. Quantas safras existem?
5. A base está ordenada por safra?
6. Os IDs são únicos?
7. Um mesmo cliente aparece em múltiplas safras?
8. Existem registros duplicados?
9. Qual é a distribuição da variável alvo?
10. Como a taxa do evento evolui entre as safras?
11. Quais variáveis possuem valores ausentes?
12. O percentual de ausência varia ao longo do tempo?
13. Existem valores especiais nas variáveis numéricas?
14. Qual é a cardinalidade das variáveis categóricas?
15. Existem categorias que surgem ou desaparecem entre safras?
16. Existem variáveis constantes ou quase constantes?
17. Alguma variável apresenta relação suspeita ou excessivamente forte com o alvo?

Atenção especial:

Investigar valores incomuns como 99997, 99998 e 99999 antes de decidir se representam:

- valores válidos;
- códigos de ausência;
- estados comportamentais;
- outros códigos especiais.

Nenhuma transformação será realizada antes dessa investigação.

Saídas esperadas:

- tabela de estrutura da base;
- tabela de safras;
- distribuição do alvo;
- taxa do evento por safra;
- tabela de ausência;
- análise de valores especiais;
- cardinalidade das categorias;
- principais achados de qualidade.

Marco de decisão:

Somente após esta etapa será definida a divisão temporal exata.

---

## Etapa 2 — Análise Exploratória

Notebook:

01_eda.ipynb

A EDA deverá apoiar decisões de modelagem.

### Variável alvo

Analisar:

- taxa global do evento;
- taxa por safra;
- evolução temporal;
- possíveis mudanças de população.

### Variáveis numéricas

Analisar:

- distribuição;
- percentis;
- valores extremos;
- valores especiais;
- ausência;
- relação com o alvo;
- comportamento temporal.

### Variáveis categóricas

Analisar:

- frequência;
- categorias ausentes;
- categorias raras;
- taxa do evento por categoria;
- estabilidade temporal das categorias.

### Relações entre variáveis

Analisar:

- correlação de Spearman;
- redundância;
- possíveis proxies;
- relações suspeitas.

As análises devem priorizar descobertas que afetem:

- modelagem;
- risco de vazamento;
- estabilidade;
- seleção de variáveis.

---

## Etapa 3 — Delineamento das Amostras

Definir:

TREINO

VALIDAÇÃO

TESTE FORA DO TEMPO — OOT

Princípio:

separação cronológica.

Não definir as safras exatas antes da auditoria dos dados.

Treino:

maior janela de desenvolvimento, composta pelas safras mais antigas.

Validação:

safras posteriores utilizadas para:

- decisões sobre variáveis;
- otimização;
- comparação entre modelos.

OOT:

safras mais recentes.

A amostra OOT não deverá ser utilizada para ajuste do modelo.

Documentar para cada conjunto:

- quantidade de observações;
- taxa do evento;
- quantidade de safras;
- período coberto.

---

## Etapa 4 — Análise e Seleção de Variáveis

Notebook:

02_feature_analysis.ipynb

Análises candidatas:

- ausência;
- valores especiais;
- Information Value como diagnóstico;
- AUC/Gini univariado;
- correlação de Spearman;
- estabilidade temporal;
- PSI;
- coeficientes da Regressão Logística;
- importância por permutação;
- SHAP.

Toda exclusão de variável deverá ser documentada.

Possíveis motivos:

- identificador;
- vazamento;
- instabilidade excessiva;
- ausência de variação;
- ausência excessiva;
- redundância;
- ausência de contribuição preditiva.

Manter uma tabela de decisão contendo:

variável

tipo

percentual de ausência

sinal preditivo

estabilidade

decisão

justificativa

---

## Etapa 5 — Modelo de Referência

Notebook:

03_modeling.ipynb

Modelo:

Regressão Logística.

Objetivos:

- criar benchmark interpretável;
- estabelecer desempenho de referência;
- compreender relações lineares;
- fornecer referência de governança.

Todo o pré-processamento deverá fazer parte de uma esteira reprodutível.

Possíveis tratamentos das variáveis numéricas:

- tratamento de valores especiais, caso justificado;
- imputação;
- transformação;
- padronização quando necessária.

Possíveis tratamentos das variáveis categóricas:

- categoria de ausência;
- codificação.

Todos os tratamentos deverão ser ajustados exclusivamente na amostra de treino.

---

## Etapa 6 — Modelo Challenger

Principal candidato:

CatBoost.

Motivos:

- bom desempenho em dados tabulares;
- captura de relações não lineares;
- tratamento nativo de variáveis categóricas;
- capacidade de trabalhar com valores ausentes;
- forte referência de comparação.

O CatBoost não será considerado champion automaticamente.

Será comparado à Regressão Logística.

A otimização de hiperparâmetros deverá ser controlada e proporcional ao tamanho do problema.

Evitar buscas exaustivas sem necessidade.

---

## Etapa 7 — Avaliação dos Modelos

Avaliar em:

TREINO

VALIDAÇÃO

OOT

### Discriminação

- ROC-AUC
- Gini
- KS
- PR-AUC

### Calibração

- Brier Score
- curva de calibração
- risco previsto versus observado

### Ordenação para o negócio

- decis;
- faixas de score;
- lift;
- captura acumulada de eventos.

### Generalização

Comparar deterioração entre:

TREINO -> VALIDAÇÃO -> OOT

A escolha do champion não poderá ser baseada em apenas uma métrica.

---

## Etapa 8 — Explicabilidade

Para Regressão Logística:

- direção dos coeficientes;
- magnitude;
- variáveis selecionadas.

Para modelo não linear:

- importância global por SHAP;
- comportamento das principais variáveis;
- exemplos locais apenas quando agregarem valor.

Perguntas principais:

- Quais variáveis mais influenciam o risco?
- As direções são coerentes?
- Os efeitos são estáveis?
- Existe dependência excessiva de uma única variável?
- Valores especiais ou ausentes estão dominando as previsões?

---

## Etapa 9 — Construção do Score

Notebook:

04_scoring_stability.ipynb

Converter a saída do modelo para:

score entre 0 e 1000.

Requisitos:

- maior score = menor risco;
- monotonicidade em relação à probabilidade;
- transformação determinística;
- documentação completa.

Avaliar:

- distribuição do score;
- percentis;
- score médio por safra;
- taxa do evento por faixa de score.

---

## Etapa 10 — Faixas de Risco

Criar faixas operacionais de score.

Metodologias iniciais candidatas:

- quantis;
- pontos de mudança de risco;
- comportamento da taxa observada.

Avaliar cada faixa por:

- população;
- taxa observada;
- probabilidade prevista;
- lift;
- captura;
- intervalo de score.

As faixas finais deverão favorecer:

- interpretação;
- estabilidade;
- monotonicidade.

---

## Etapa 11 — Estabilidade

Avaliar mensalmente:

- quantidade de clientes;
- taxa do evento;
- AUC/Gini;
- KS;
- score médio;
- PSI do score;
- PSI das principais variáveis.

Investigar deteriorações entre safras.

O PSI será utilizado como ferramenta diagnóstica e não como regra absoluta isolada.

---

## Etapa 12 — Camada de Negócio

Traduzir o resultado do modelo em suporte à decisão.

Estrutura ilustrativa:

Muito Baixo Risco -> potencial estratégia de crescimento

Baixo Risco -> crescimento ou manutenção

Médio Risco -> manutenção

Alto Risco -> congelamento ou revisão

Muito Alto Risco -> estratégia mais restritiva

Não afirmar limites economicamente ótimos sem variáveis econômicas adicionais.

---

## Etapa 13 — Notebook Final

Arquivo:

credit_card_behavior_score.ipynb

Narrativa planejada:

1. problema de negócio;
2. dados disponíveis;
3. qualidade dos dados;
4. desenho temporal;
5. principais achados da EDA;
6. decisões sobre variáveis;
7. modelos;
8. comparação dos modelos;
9. explicabilidade;
10. construção do score;
11. segmentação;
12. estabilidade;
13. implicações de negócio;
14. limitações;
15. conclusão.

Remover análises exploratórias que não contribuam para a narrativa final.

---

## Etapa 14 — Apresentação Executiva

Máximo:

5 slides principais.

Narrativa preliminar:

Slide 1 — Problema e abordagem analítica

Slide 2 — Dados, desenho temporal e principais achados

Slide 3 — Desempenho do modelo e explicabilidade

Slide 4 — Behavior Score e segmentação de risco

Slide 5 — Aplicação no negócio, estabilidade e próximos passos

Os gráficos executivos serão gerados durante a análise e armazenados em:

reports/figures/

Evitar reconstruir manualmente análises dentro da apresentação.
