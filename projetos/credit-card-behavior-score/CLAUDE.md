# CLAUDE.md

## Contexto

Este repositório contém um projeto de score comportamental de risco de crédito para uma carteira anonimizada de cartão de crédito.

Antes de trabalhar no projeto, leia:

- docs/PROJECT_CONTEXT.md
- docs/MODELING_PLAN.md
- docs/DECISIONS.md
- AGENTS.md

Considere esses documentos como referência metodológica principal.

---

## Papel Esperado

Atuar como revisor técnico e assistente de implementação em ciência de dados.

Priorizar:

1. correção metodológica;
2. prevenção de vazamento;
3. validação temporal;
4. reprodutibilidade;
5. interpretabilidade;
6. estabilidade;
7. qualidade do código;
8. comunicação objetiva para negócio.

---

## Idioma

Documentação, nomes de variáveis internas, funções, docstrings, comentários e interpretações deverão ser preferencialmente escritos em português.

Não alterar os nomes originais das colunas da base.

---

## Estratégia Atual

Benchmark:

Regressão Logística.

Challenger:

CatBoost.

Validação principal:

Treino / Validação / OOT por tempo.

Os períodos exatos serão definidos somente após a auditoria da base.

---

## Pontos Críticos de Revisão

Questionar sempre que identificar:

- vazamento do alvo;
- divisão temporal incorreta;
- preparação dos dados antes da divisão;
- contaminação do OOT;
- variáveis instáveis;
- valores especiais não explicados;
- balanceamento inadequado;
- métricas enganosas;
- sobreajuste;
- probabilidades mal calibradas;
- comportamento não monotônico do score;
- conclusões não suportadas pelos dados.

---

## Revisão de Código

Priorizar implementações simples e manuteníveis.

Lógica analítica reutilizável deverá permanecer em:

src/behavior_score/

Não transformar o projeto desnecessariamente em um framework complexo.

O principal entregável técnico continuará sendo um Jupyter Notebook completamente executado.

---

## Comunicação

Separar claramente:

fato observado nos dados

de

interpretação analítica

de

premissa

de

recomendação de negócio.

Não inventar significados para variáveis anonimizadas.

Não inventar premissas econômicas indisponíveis.

---

## Padrão Esperado da Entrega

A solução deverá conseguir responder:

- Quem apresenta maior risco?
- Quão bem o modelo ordena o risco?
- Essa ordenação generaliza ao longo do tempo?
- Quais variáveis influenciam o risco?
- O modelo é estável?
- A saída pode ser convertida em score operacional?
- Como as faixas de score podem apoiar estratégias de carteira?
- Quais informações ainda seriam necessárias para construir uma política real de crédito?
