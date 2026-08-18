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

Status: concluída.

---

## Etapa 1 — Auditoria dos Dados

Notebook:

00_data_audit.ipynb

Status: concluída tecnicamente, sujeita à revisão humana final.

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

## Etapa 2 — Diagnóstico Temporal e Delineamento Amostral

Notebook:

01_eda_temporal.ipynb

Status: concluída; cenário 8/2/3 aprovado na decisão D017.

Objetivos:

- confirmar cronologia e granularidade;
- diagnosticar evolução de volume, target e missing;
- investigar temporalmente os códigos especiais;
- calcular PSI exploratório com bins fixados pela referência;
- aprofundar riscos de leakage temporal;
- comparar os cenários 8/2/3 e 9/2/2 sem utilizar modelos.

Gate:

- o split 8/2/3 está aceito;
- o OOT está congelado;
- o OOT não poderá orientar feature selection, tratamento guiado pelo target,
  tuning, hiperparâmetros ou escolha do champion;
- avaliações futuras deverão reportar resultados agregados e por safra,
  especialmente 2020-01.

---

## Etapa 3 — EDA orientada à modelagem

Implementação:

Seção lógica do notebook `credit_card_behavior_score.ipynb`.

Status: concluída preliminarmente no desenvolvimento, sujeita à revisão humana.

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

## Gate metodológico — Aprovação do delineamento das amostras

Definir:

TREINO

VALIDAÇÃO

TESTE FORA DO TEMPO — OOT

Princípio:

separação cronológica.

O delineamento aprovado na decisão D017 é: treino de 2019-01 a 2019-08,
validação de 2019-09 a 2019-10 e OOT de 2019-11 a 2020-01.

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

Implementação:

Seção lógica do notebook `credit_card_behavior_score.ipynb`.

Status: concluída preliminarmente no desenvolvimento, sujeita à revisão humana.

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

Implementação:

Seção lógica do notebook `credit_card_behavior_score.ipynb`.

Status: benchmark refitado no Desenvolvimento com a especificação final e avaliado
no OOT conforme D019; permanece benchmark, sujeito à revisão humana final.

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

Implementação:

Seção lógica do notebook `credit_card_behavior_score.ipynb`.

Status: candidato CatBoost congelado, refitado no Desenvolvimento e avaliado no
OOT conforme D019, sem tuning ou recalibração; sujeito à revisão humana final.

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

Implementação:

Seção lógica do notebook `credit_card_behavior_score.ipynb`.

Status: comparação de Desenvolvimento e avaliação OOT concluídas conforme o
protocolo D019, definido antes da primeira predição OOT nesta execução. O OOT
não orientou seleção, tuning, features ou
recalibração; a revisão humana final permanece pendente.

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

Implementação:

Seção lógica do notebook `credit_card_behavior_score.ipynb`.

Status: concluída. A fórmula log-odds/PDO e a convenção operacional aprovada na
decisão D020 — Base Score = 600, PDO = 50 e Base Odds = 20:1 — foram aplicadas
às probabilidades congeladas de Desenvolvimento e OOT.

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

Status: concluída conforme D021, sem uso de target ou OOT para definir cortes.

Criar cinco faixas operacionais a partir dos decis de risco já congelados nas
probabilidades do Desenvolvimento:

- decis 1–2: Muito Alto Risco;
- decis 3–4: Alto Risco;
- decis 5–6: Médio Risco;
- decis 7–8: Baixo Risco;
- decis 9–10: Muito Baixo Risco.

O decil 1 representa a maior probabilidade do evento e o menor score. Os cortes
serão convertidos para limites de score com precisão completa e aplicados sem
alteração ao OOT. O target não será usado para escolher ou otimizar limites.

Avaliar cada faixa por:

- população;
- taxa observada;
- probabilidade prevista;
- lift;
- captura;
- intervalo de score.

A estabilidade e a monotonicidade observada serão avaliadas como diagnósticos.
Nenhum corte será redesenhado para forçar monotonicidade no Desenvolvimento ou
no OOT.

---

## Etapa 11 — Estabilidade

Status: concluída para distribuição mensal do score e PSI do score, com
Desenvolvimento como referência congelada.

Avaliar mensalmente:

- quantidade de clientes;
- taxa do evento;
- AUC/Gini;
- KS;
- score médio;
- PSI do score;
- PSI das principais variáveis.

Investigar deteriorações entre safras.

Para o PSI do score, os bins serão aprendidos exclusivamente no Desenvolvimento
e reaplicados sem alteração ao OOT agregado e às safras 2019-11, 2019-12 e
2020-01. O PSI será utilizado como ferramenta diagnóstica e não como regra
absoluta isolada.

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

Arquivo único de entrega técnica:

credit_card_behavior_score.ipynb

Os notebooks `00_data_audit.ipynb` e `01_eda_temporal.ipynb` são auxiliares de
desenvolvimento. Nenhum novo notebook separado será criado para as etapas
seguintes. A sequência metodológica será implementada no arquivo final com a
seguinte estrutura lógica:

1. contexto e objetivo;
2. dados;
3. auditoria;
4. diagnóstico temporal;
5. delineamento das amostras;
6. EDA orientada à modelagem;
7. análise e seleção de features;
8. preparação dos dados;
9. Regressão Logística;
10. CatBoost;
11. comparação dos modelos;
12. calibração;
13. explicabilidade;
14. avaliação OOT;
15. score 0–1000;
16. faixas de risco;
17. estabilidade;
18. aplicação ao negócio;
19. limitações;
20. conclusão.

Na execução atual, o desenvolvimento, o congelamento do candidato, a avaliação
OOT, o cálculo do score 0–1000, as cinco faixas de risco e os diagnósticos de
estabilidade e PSI do score foram concluídos. A próxima fase cobre a consolidação
da interpretação para aplicação ao negócio e a apresentação executiva.

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
