# Credit Card Behavior Score

Projeto de modelagem de risco comportamental aplicado a uma carteira anonimizada de clientes de cartão de crédito.

O objetivo é estimar o risco futuro dos clientes, construir um score operacional entre 0 e 1000 e avaliar como esse score pode apoiar decisões de gestão da carteira.

## Escopo Analítico

O projeto contempla:

- auditoria e qualidade dos dados;
- análise exploratória;
- validação temporal;
- seleção de variáveis;
- modelo de referência interpretável;
- modelo challenger não linear;
- discriminação e calibração;
- explicabilidade;
- construção do score;
- segmentação de risco;
- estabilidade temporal;
- interpretação para negócio.

## Filosofia de Modelagem

O projeto prioriza:

- prevenção de vazamento de dados;
- capacidade de generalização temporal;
- interpretabilidade;
- estabilidade;
- reprodutibilidade;
- aplicabilidade ao negócio.

O objetivo não é testar a maior quantidade possível de algoritmos, mas construir uma solução defensável de score comportamental de risco.

## Estrutura do Repositório

credit-card-behavior-score/
- data/
- docs/
- notebooks/
- src/behavior_score/
- tests/
- artifacts/
- reports/
- presentation/

## Principal Entregável Técnico

notebooks/credit_card_behavior_score.ipynb

## Status

Etapa 0 — Estruturação do projeto e definição metodológica.

Próxima etapa:

Etapa 1 — Auditoria dos Dados.

## Observação

O projeto utiliza uma base fictícia e anonimizada para demonstração analítica.

O score resultante deverá ser interpretado como instrumento de ordenação de risco e não como uma política completa de crédito sem informações econômicas, operacionais e de governança adicionais.
