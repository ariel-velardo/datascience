# Impacto da Expansão da Rede Federal sobre a Atividade Econômica Municipal

Projeto desenvolvido no contexto da disciplina de Big Data & Analytics.

## Pergunta de pesquisa

Qual foi o efeito da chegada de novos campi da Rede Federal de Educação Profissional, Científica e Tecnológica, associados à Expansão Fase II, sobre a atividade econômica dos municípios brasileiros?

## Objetivo

Avaliar se a chegada de novos campi da Rede Federal esteve associada a mudanças na atividade econômica dos municípios tratados, utilizando dados públicos oficiais e métodos modernos de inferência causal para tratamentos escalonados no tempo.

## Status

FASE_EXPLORATORIA = ENCERRADA

VIABILIDADE_CAUSAL = PROMISSORA_COM_RESSALVAS

EFEITO_CAUSAL_ESTIMADO = NAO

FASE_ATUAL = DESENVOLVIMENTO_ACADEMICO

Nenhuma afirmação causal final foi estabelecida.

## Unidade de análise

Município-ano.

## Política analisada

Expansão da Rede Federal de Educação Profissional, Científica e Tecnológica, com foco na chamada Expansão Fase II.

## Tratamento

Primeira presença federal de EPT observada no município associada à Expansão Fase II.

O timing principal deve ser interpretado como proxy anual de primeira presença operacional observada no Censo Escolar.

Não deve ser interpretado automaticamente como data de criação, autorização ou inauguração do campus.

## Outcomes candidatos

- pessoal ocupado assalariado;
- pessoal ocupado total;
- número de unidades locais;
- salário médio mensal.

O outcome primário ainda será definido ex ante na fase acadêmica.

## Estratégia causal

O tratamento é escalonado no tempo.

Estimadores TWFE ingênuos não serão utilizados como especificação causal principal.

Métodos candidatos incluem:

- Callaway–Sant'Anna;
- Sun–Abraham;
- outros estimadores apropriados para staggered adoption.

O estimador principal ainda não foi definido.

## Limitação central de validade externa

A fase exploratória mostrou suporte comum limitado.

A população causal principal candidata não representa automaticamente todos os municípios tratados pela Expansão Fase II.

## Estrutura

- `data/raw`: fontes originais;
- `data/interim`: dados intermediários;
- `data/processed`: bases analíticas;
- `docs/freeze`: registro das decisões congeladas;
- `docs/methodology`: decisões metodológicas da fase acadêmica;
- `docs/literature`: revisão de literatura;
- `docs/institutional`: reconstrução histórica e institucional;
- `notebooks`: análises exploratórias e acadêmicas;
- `src`: pipeline reproduzível;
- `outputs`: tabelas e figuras finais.

## Integridade metodológica

As decisões da fase exploratória não devem ser alteradas retroativamente com base nos resultados pós-tratamento.

Mudanças substantivas futuras devem possuir justificativa metodológica independente dos efeitos encontrados.