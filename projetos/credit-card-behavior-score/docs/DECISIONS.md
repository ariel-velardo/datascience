# Registro de Decisões

Este documento registra decisões metodológicas e de engenharia do projeto.

Nenhum agente de IA deverá alterar silenciosamente decisões registradas aqui.

---

## D001 — Nome neutro do projeto

Decisão:

Utilizar:

credit-card-behavior-score

Evitar nomes de empresas em:

- caminho do projeto;
- módulos Python;
- notebooks;
- README público;
- commits.

Motivo:

Manter o projeto genérico, reutilizável e adequado para portfólio profissional.

Status:

Aceito.

---

## D002 — Enquadramento como Behavior Score

Decisão:

Tratar o problema como score comportamental de risco de crédito para clientes já existentes de cartão.

Status:

Aceito.

---

## D003 — Semântica da variável alvo

Decisão:

Não inventar o significado de Ever30Mob6 enquanto não existir documentação que confirme sua definição.

Utilizar preferencialmente:

"evento adverso"

ou

"evento de risco".

Status:

Aceito.

---

## D004 — Validação temporal

Decisão:

Utilizar separação cronológica entre:

treino;

validação;

teste fora do tempo — OOT.

Não utilizar divisão aleatória como desenho principal.

As safras exatas serão definidas depois da auditoria dos dados.

Status:

Aceito.

---

## D005 — Identificadores

Decisão:

Não utilizar como variáveis preditivas:

- index;
- id.

A safra será utilizada principalmente para controle temporal e estabilidade.

Status:

Aceito.

---

## D006 — Estratégia de modelos

Decisão inicial:

1. Regressão Logística como benchmark;
2. CatBoost como challenger não linear.

Outros modelos exigirão justificativa analítica.

Status:

Aceito.

---

## D007 — Desbalanceamento

Decisão:

Não aplicar automaticamente:

- SMOTE;
- undersampling;
- oversampling.

Primeiro avaliar o desbalanceamento e o comportamento dos modelos na distribuição natural da população.

Status:

Aceito.

---

## D008 — Seleção de variáveis

Decisão:

Não remover ou selecionar variáveis utilizando apenas uma métrica.

Considerar conjuntamente:

- sinal preditivo;
- redundância;
- estabilidade;
- risco de vazamento;
- interpretabilidade.

Status:

Aceito.

---

## D009 — Direção do score

Decisão:

Escala:

0 a 1000.

Score maior significa menor risco estimado.

Status:

Aceito.

---

## D010 — Versionamento dos dados

Decisão:

Bases raw, interim e processed não serão versionadas no Git.

Status:

Aceito.

---

## D011 — Ativos de marca

Decisão:

Imagens e logos utilizados como referência visual permanecerão locais.

O código público utilizará apenas uma identidade visual genérica baseada em uma paleta definida no projeto.

Status:

Aceito.

---

## D012 — Consistência visual

Decisão:

Utilizar um único módulo reutilizável de visualização.

Gráficos do notebook final e da apresentação deverão compartilhar:

- tipografia;
- cores;
- padrões de títulos;
- padrões de exportação.

Status:

Aceito.

---

## D013 — Notebook final

Decisão:

Durante o desenvolvimento poderão existir múltiplos notebooks.

Artefato técnico final:

notebooks/credit_card_behavior_score.ipynb

O notebook deverá ser autocontido e estar completamente executado.

Status:

Aceito.

---

## D014 — Governança de IA Generativa

Decisão:

Ferramentas de IA poderão apoiar:

- implementação;
- revisão;
- documentação;
- testes;
- comunicação.

A validação humana continuará obrigatória para decisões metodológicas e conclusões.

Status:

Aceito.

---

## D015 — Idioma do projeto

Decisão:

Documentação, análises, interpretações, títulos dos gráficos, nomes de variáveis internas e funções desenvolvidas neste projeto deverão ser preferencialmente escritos em português.

Exceções:

- nomes originais das colunas da base;
- nomes oficiais de bibliotecas;
- nomes oficiais de algoritmos ou métricas quando a tradução prejudicar clareza;
- nomes estruturais já estabelecidos no repositório.

Status:

Aceito.

---

## D016 — Biblioteca de visualização

Decisão:

Utilizar Plotly como biblioteca principal de visualização do projeto.

Os notebooks deverão priorizar gráficos interativos e os mesmos objetos gráficos poderão ser exportados para formatos estáticos para utilização na apresentação executiva.

Matplotlib e Seaborn não serão utilizados como padrão.

Motivos:

- interatividade durante a exploração;
- qualidade visual adequada para comunicação executiva;
- reutilização entre notebook e apresentação;
- padronização visual centralizada;
- redução da necessidade de reconstruir gráficos posteriormente.

A confiabilidade das análises continuará dependendo da metodologia, dos dados e das métricas, e não da biblioteca de visualização.

Status:

Aceito.

---

## D017 — Delineamento temporal

Decisão:

Adotar o cenário A — 8/2/3:

- treino de 2019-01 a 2019-08;
- validação de 2019-09 a 2019-10;
- OOT de 2019-11 a 2020-01.

O cenário B — 9/2/2 foi avaliado como alternativa e não foi adotado. A partir
desta aprovação, o OOT fica congelado e não pode ser utilizado para seleção de
features, tratamentos orientados pelo target, tuning, escolha de
hiperparâmetros, calibração ou seleção do champion. Sua abertura ocorrerá
somente após a escolha definitiva do modelo para avaliação final fora do tempo.

Status:

Aceito.

---

## D018 — Estratégia do Notebook Final

Decisão:

A entrega técnica será composta por um único notebook:

`notebooks/credit_card_behavior_score.ipynb`

Os notebooks `00_data_audit.ipynb` e `01_eda_temporal.ipynb` permanecem como
artefatos auxiliares de desenvolvimento e não constituem a entrega final.

Status:

Aceito.

---

## D019 — Protocolo final de avaliação OOT

Decisão:

1. O candidato CatBoost, suas 13 features originais, a representação categórica
   `var12_estado`, os tratamentos, os hiperparâmetros e a ausência de calibração
   foram congelados antes da abertura do OOT, no commit pré-OOT `0c5c6a7`.
2. O modelo final será reajustado utilizando toda a população de Desenvolvimento,
   formada por Treino de 2019-01 a 2019-08 e Validação de 2019-09 a 2019-10.
3. Nenhuma linha de 2019-11, 2019-12 ou 2020-01 será utilizada no fit.
4. A quantidade de árvores do refit será fixa e igual ao atributo `tree_count_`
   lido programaticamente do objeto `modelo_candidato` congelado. O valor não será
   inferido de `best_iteration` nem informado manualmente.
5. O refit final não utilizará early stopping nem OOT como `eval_set`.
6. Não haverá tuning, seleção de modelo ou alteração de hiperparâmetros usando OOT.
7. Não haverá recalibração usando OOT.
8. Não haverá alteração de features, representação ou tratamento usando OOT.
9. Os resultados OOT serão utilizados exclusivamente para avaliação final de
   generalização, estabilidade, calibração, ordenação e explicabilidade.
10. A Regressão Logística com `C = 0.1` e regularização L2 será refitada em todo o
    Desenvolvimento, com a especificação final de features, apenas como benchmark.
    Seu resultado OOT não poderá substituir o champion congelado.

Definições do protocolo estabelecidas antes da primeira predição OOT nesta execução:

- `PR-AUC` preserva a definição de desenvolvimento por `average_precision_score`;
- `ECE` usa 10 faixas equipopulacionais determinísticas, como no desenvolvimento;
- viés de calibração absoluto é `probabilidade média - taxa observada`, em pontos
  de probabilidade e com sinal; viés relativo divide esse valor pela taxa observada;
- os intervalos de confiança de 95% usam 500 reamostragens bootstrap
  estratificadas pelo target, seed 42 e percentis 2,5% e 97,5%;
- os cortes dos decis de risco são os quantis das probabilidades do Desenvolvimento
  produzidas pelo modelo final refitado; empates não serão resolvidos com o target e
  cortes internos duplicados interromperão a execução em vez de redefinir faixas;
- o PSI usa Desenvolvimento como referência, com cortes/categorias aprendidos
  exclusivamente nessa população e aplicados sem alteração ao OOT agregado e mensal;
- resultados por safra com apenas uma classe terão métricas de discriminação
  indisponíveis, sem imputação de valor; as contagens e métricas de calibração
  permanecerão reportadas quando definidas.

Status:

Aceito.

---

## D020 — Convenção operacional da escala do Behavior Score

Decisão:

Adotar definitivamente a transformação log-odds/PDO já implementada em
`src/behavior_score/scoring.py`, com os seguintes parâmetros:

- Base Score = 600;
- PDO = 50;
- Base Odds = 20:1;
- odds = `(1 - p) / p`;
- score maior = menor risco estimado;
- clipping operacional no intervalo [0, 1000].

A escolha é uma convenção operacional de escala. Foi realizada a partir do
diagnóstico da distribuição das probabilidades do Desenvolvimento, sem utilizar
o target para escolher os parâmetros e sem utilizar o OOT. A configuração
apresentou boa dispersão operacional no Desenvolvimento, mediana próxima de 600
e ausência de clipping nessa população.

A transformação é monotônica e não cria um novo modelo, não altera as
probabilidades produzidas, a discriminação ou o ranking do modelo antes do
eventual empate introduzido pelo clipping nas caudas.

Status:

Aceito.

---

## D021 — Cinco faixas operacionais de risco

Decisão:

Construir as cinco faixas exclusivamente a partir dos decis de risco congelados
no Desenvolvimento conforme D019, agregando-os dois a dois:

- decis 1–2: Muito Alto Risco;
- decis 3–4: Alto Risco;
- decis 5–6: Médio Risco;
- decis 7–8: Baixo Risco;
- decis 9–10: Muito Baixo Risco.

O decil 1 representa a maior probabilidade do evento e o menor score. Na
conversão dos cortes congelados de probabilidade para limites de score:

- selecionar os quatro cortes pelos índices `[8, 6, 4, 2]`;
- verificar por asserção que esses cortes caem nos decis `[3, 5, 7, 9]`;
- preservar internamente os limites com precisão completa;
- utilizar `right=False` no recorte em score;
- exigir concordância registro a registro entre a agregação direta dos decis e a
  classificação pelos limites convertidos de score.

Os cortes serão aprendidos exclusivamente no Desenvolvimento e permanecerão
congelados para aplicação sem alteração ao OOT. O target não será utilizado para
escolher ou otimizar os limites; poderá ser usado somente depois da definição
para avaliar as faixas. Estabilidade e monotonicidade observada serão tratadas
apenas como diagnósticos, sem redesenho de cortes no Desenvolvimento ou no OOT.

Status:

Aceito.

---

## D022 — Rubrica da classificação técnica

Decisão:

Formalizar, após a avaliação, uma rubrica qualitativa em três níveis para tornar
auditável o rótulo de classificação técnica. A rubrica não foi definida antes da
avaliação e não constitui critério retroativo de seleção, aprovação ou troca do
modelo. Ela organiza a comunicação dos resultados já produzidos e não altera o
protocolo, as métricas ou o champion congelado.

A classificação deve ser sustentada, de forma verificável, pela leitura conjunta
das evidências registradas nos artefatos do projeto em três dimensões:

- discriminação: métricas fora do tempo, ordenação, lift, captura e comparação
  com o benchmark;
- estabilidade temporal: diferenças entre Desenvolvimento e OOT, variação entre
  safras, monotonicidade por decis ou faixas e PSI;
- calibração: Brier Score, ECE, viés agregado e diferença entre probabilidade
  média prevista e taxa observada por faixa.

Os níveis são:

- **A — desempenho forte e consistente:** a discriminação fora do tempo preserva
  uma ordenação forte, não há ressalva temporal material documentada para a
  leitura agregada ou por período, e a calibração é coerente no agregado e nas
  faixas operacionais;
- **B — boa capacidade de ordenação fora do tempo, com variabilidade temporal
  material:** a discriminação sustenta o uso do modelo para ordenação, mas existe
  ao menos uma ressalva material documentada de estabilidade temporal ou
  calibração, que deve ser declarada e monitorada; o nível não equivale a
  aprovação operacional;
- **C — evidência insuficiente para o uso proposto:** a discriminação fora do
  tempo não sustenta adequadamente a ordenação, ou a instabilidade temporal ou
  os desvios de calibração comprometem o uso pretendido, exigindo revisão antes
  de qualquer adoção operacional.

Na ausência de limiares quantitativos previamente aprovados, esta rubrica não
cria cortes numéricos retrospectivos. Toda atribuição deve registrar as
evidências e as ressalvas das três dimensões. Para esta avaliação, mantém-se o
nível **B**, conforme a descrição já adotada no notebook: boa capacidade de
ordenação fora do tempo, com variabilidade temporal material.

Status:

Aceito.

---

## D023 — Extração pós-freeze da derivação de `var12_estado`

Decisão:

Registrar explicitamente que a derivação de `var12_estado` foi extraída do
notebook para `src/behavior_score/features.py` no commit `85b10d2`, posterior ao
freeze `0c5c6a7`. A extração preservou a partição dos estados observados, mas o
rótulo reservado à ausência passou de `__MISSING__` para `MISSING`.

Nesta base, essa categoria é vazia. `reports/tables/00_missing.csv` registra zero
valores ausentes em `var12` nos 200.043 registros, e
`reports/tables/final_var12_caracterizacao.csv` registra
`ausencia_original = 0.0` em Treino e Validação. Portanto, nenhum registro é
afetado pela mudança do rótulo e não há efeito numérico possível sobre split,
estatística de target, predição ou métrica.

Este registro reconhece expressamente que a extração ocorreu após o freeze. A
conclusão de neutralidade é específica desta base e decorre da ausência observada
de valores ausentes em `var12`; ela não apresenta a extração como anterior ao
freeze nem autoriza outras alterações posteriores.

Status:

Aceito.
