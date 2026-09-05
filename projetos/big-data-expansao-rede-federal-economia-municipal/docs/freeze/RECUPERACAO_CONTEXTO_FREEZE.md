# Recuperação do contexto metodológico da fase exploratória

## Natureza deste documento

Este documento NÃO é uma cópia do arquivo original
FREEZE_METODOLOGICO_VIABILIDADE_CAUSAL.md.

O projeto exploratório original não estava versionado no Git e sua
pasta local foi removida durante uma reorganização do repositório.

Este documento registra as decisões metodológicas recuperadas a partir
do contexto salvo da fase exploratória.

Ele existe para preservar rastreabilidade e impedir que decisões já
tomadas sejam redefinidas com base nos resultados da fase acadêmica.

---

## Status congelado

STATUS = FASE_EXPLORATORIA_ENCERRADA

VIABILIDADE_CAUSAL = PROMISSORA_COM_RESSALVAS

EFEITO_CAUSAL_ESTIMADO = NAO

DECISAO = DESENVOLVER_PROJETO

---

## Política

Expansão da Rede Federal de Educação Profissional, Científica e
Tecnológica, com foco na Expansão Fase II.

---

## Unidade de análise

Município-ano.

---

## Tratamento

Primeira presença federal de EPT observada no município associada à
Expansão Fase II.

O timing utilizado é uma proxy anual de primeira presença operacional
observada no Censo Escolar.

Não deve ser chamado automaticamente de data de:

- inauguração;
- criação;
- autorização.

---

## População Fase II

144 municípios únicos.

Tratados principais inicialmente identificados entre 2010 e 2013:

- 2010: 37
- 2011: 65
- 2012: 14
- 2013: 3

Total: 119 municípios.

---

## Common support

Tratados originais: 119.

Tratados em common support: 53.

A validade externa do futuro estimando é, portanto, restrita à
subpopulação de municípios tratados com suporte comum.

---

## Matching exploratório congelado

Especificação selecionada:

- nearest-neighbor;
- K = 1;
- com reposição;
- restrição exata por UF;
- somente informação pré-tratamento.

Resultados aproximados:

- 53 tratados matched;
- 51 controles únicos;
- ESS dos controles ≈ 49,3;
- mediana |SMD| ≈ 0,0225;
- máximo |SMD| ≈ 0,2248.

GATE_MATCHING = ALERTA.

---

## Amostra causal core candidata

Coortes principais:

2010 e 2011.

Composição:

- 2010: 17 tratados;
- 2011: 30 tratados.

Total: 47 pares tratado-controle.

Coortes 2012 e 2013 permanecem reservadas para sensibilidade.

---

## Pré-tendências

A janela balanceada principal exploratória utilizou:

k = -3, -2, -1.

Os resultados foram considerados promissores, mas não constituem prova
de tendências paralelas.

P-valores altos não devem ser interpretados como evidência de ausência
de pré-tendência.

---

## Alertas de placebo

Foram observados sinais pré-tratamento não desprezíveis, especialmente
em algumas combinações de coorte e outcome.

Isso pode refletir antecipação, erro de timing, seleção dinâmica,
choques locais prévios ou instabilidade amostral.

Nenhuma dessas explicações foi estabelecida.

GATE_ESTATISTICO_FINAL = PROMISSOR_COM_ALERTAS.

---

## Gate estrutural

Na amostra causal core de 47 municípios:

CORE_QUALQUER_ESCOLA_FEDERAL_2007 = 0

CORE_EPT_FEDERAL_NOME_2007 = 0

CORE_CANDIDATO_LEGADO_MEC = 0

CORE_EVIDENCIA_FORTE_LEGADO_MEC = 0

CORE_CONTAMINACAO_FORTE_TOTAL = 0

GATE_ESTRUTURAL_FINAL = PASSA_ESTRUTURAL.

---

## Regras de integridade

Não modificar retroativamente, em função dos resultados pós-tratamento:

- tratamento;
- população;
- janela temporal;
- common support;
- matching;
- critério de exclusão;
- outcome primário.

Qualquer alteração futura deve possuir justificativa substantiva
independente dos resultados encontrados.

---

## Próxima fase

A sequência acadêmica prevista é:

1. revisão de literatura;
2. reconstrução histórica e institucional;
3. DAG;
4. definição formal do estimando;
5. definição do outcome primário;
6. definição da população principal;
7. definição formal do tratamento e timing;
8. antecipação;
9. spillovers;
10. estratégia de controle;
11. escolha do estimador staggered DiD;
12. validação externa do timing;
13. pipeline reproduzível;
14. análise descritiva;
15. estimação;
16. inferência;
17. robustez;
18. sensibilidade;
19. heterogeneidade;
20. validade interna e externa;
21. redação acadêmica.

Nenhum efeito causal deve ser estimado antes da formalização dessas
decisões.