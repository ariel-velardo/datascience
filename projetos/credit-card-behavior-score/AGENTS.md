# AGENTS.md

## Projeto

Credit Card Behavior Score

Antes de modificar qualquer código, leia:

1. docs/PROJECT_CONTEXT.md
2. docs/MODELING_PLAN.md
3. docs/DECISIONS.md

Esses documentos são a fonte principal das decisões metodológicas do projeto.

---

## Regras Gerais

Não alterar silenciosamente a metodologia.

Caso uma implementação exija uma decisão ainda não documentada:

1. interromper a alteração;
2. explicar a decisão necessária;
3. solicitar validação;
4. atualizar docs/DECISIONS.md somente após aprovação.

---

## Idioma

Preferir português para:

- nomes de variáveis internas;
- funções desenvolvidas no projeto;
- docstrings;
- comentários;
- análises;
- gráficos;
- tabelas;
- documentação.

Não traduzir nomes originais das colunas da base.

---

## Dados

Nunca modificar arquivos originais em:

data/raw/

Nunca versionar bases raw, interim ou processed.

Não inventar significados de negócio para variáveis anonimizadas.

Não substituir valores especiais antes de investigar seu comportamento.

Prevenir vazamento de dados.

Qualquer:

- imputador;
- codificador;
- padronizador;
- seletor;
- modelo

deverá ser ajustado somente com dados da amostra apropriada de desenvolvimento.

---

## Modelagem

Benchmark principal:

Regressão Logística.

Challenger principal:

CatBoost.

Não adicionar modelos apenas para aumentar a quantidade de algoritmos testados.

Não otimizar utilizando a amostra OOT.

A amostra OOT é destinada à avaliação final fora do tempo.

---

## Avaliação

Não utilizar acurácia como métrica principal de seleção.

Dar suporte a:

- ROC-AUC;
- Gini;
- KS;
- PR-AUC;
- Brier Score;
- calibração;
- lift;
- captura acumulada;
- desempenho por faixa de score;
- PSI.

As funções de métricas deverão possuir testes quando pertinente.

---

## Código

Utilizar principalmente:

- Python;
- pandas;
- NumPy;
- scikit-learn;
- scipy;
- matplotlib;
- CatBoost quando necessário;
- SHAP quando necessário.

Priorizar:

- código explícito;
- funções pequenas;
- type hints quando úteis;
- docstrings;
- sementes aleatórias fixas;
- reprodutibilidade.

Evitar:

- abstração desnecessária;
- heranças complexas;
- infraestrutura prematura de MLOps;
- estado oculto de notebooks.

---

## Estrutura

Lógica reutilizável:

src/behavior_score/

Exploração:

notebooks/

Figuras:

reports/figures/

Tabelas:

reports/tables/

Modelos:

artifacts/models/

Métricas e resultados de experimentos:

artifacts/metrics/

---

## Notebooks

Notebooks de desenvolvimento podem ser exploratórios.

O notebook final deverá ser conciso e coerente.

Arquivo final:

notebooks/credit_card_behavior_score.ipynb

Quando relevante, utilizar:

Comentário Técnico:

Análise/Interpretação:

Não deixar perguntas analíticas sem resposta no notebook final.

---

## Visualização

Utilizar funções compartilhadas de:

src/behavior_score/visualization.py

Não criar estilos visuais conflitantes dentro de notebooks individuais.

Os gráficos devem:

- possuir títulos claros;
- identificar os eixos;
- evitar elementos decorativos desnecessários;
- enfatizar a conclusão analítica;
- ser adequados para reutilização na apresentação executiva.

---

## Testes

Testes pertencem a:

tests/

Prioridades:

- Gini;
- KS;
- PSI;
- transformação de score;
- direção do score;
- limites da escala.

---

## Uso de IA

Contribuições relevantes de IA deverão ser registradas em:

docs/AI_USAGE.md

Código gerado por IA deverá ser revisado antes de ser aceito.
