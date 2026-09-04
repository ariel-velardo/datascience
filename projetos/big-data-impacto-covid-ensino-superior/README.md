# Big Data Analytics do impacto da COVID-19 no ensino superior brasileiro

Projeto desenvolvido no contexto da disciplina de **Big Data & Analytics**, utilizando dados públicos oficiais do Inep.

## Objetivo

Investigar padrões de permanência, conclusão e desistência no ensino superior brasileiro e avaliar se a pandemia de COVID-19 produziu um impacto diferencial sobre a desistência em cursos presenciais, em comparação com cursos que já operavam na modalidade a distância.

## Pergunta principal

**Qual foi o impacto diferencial da pandemia de COVID-19 sobre a desistência em cursos presenciais do ensino superior brasileiro, comparativamente aos cursos EAD?**

A interpretação causal dependerá da validação dos pressupostos do desenho de pesquisa, especialmente tendências paralelas, overlap e estabilidade da composição dos grupos.

## Estrutura metodológica

O projeto será desenvolvido em três camadas principais:

1. **Big Data Analytics**
   - aquisição e integração de dados oficiais do Inep;
   - processamento de múltiplas coortes;
   - tratamento e validação;
   - armazenamento analítico em Parquet.

2. **Descriptive & Longitudinal Analytics**
   - permanência;
   - conclusão;
   - desistência;
   - diferenças por modalidade, área, instituição, região e categoria administrativa;
   - evolução das trajetórias acadêmicas.

3. **Inferência Causal**
   - pandemia de COVID-19 como choque externo;
   - comparação entre cursos presenciais e EAD;
   - Difference-in-Differences;
   - Event Study;
   - testes de pré-tendências;
   - análises de robustez e sensibilidade.

## Fonte dos dados

Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira — INEP.

Principais fontes previstas:

- Indicadores de Trajetória da Educação Superior;
- Microdados do Censo da Educação Superior contemporâneos às coortes analisadas.

## Status

Em fase de auditoria metodológica e construção da base analítica.

Nenhuma alegação causal será feita antes da validação dos pressupostos de identificação.
