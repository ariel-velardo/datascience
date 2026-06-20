# Estrutura de Slides — Política de Concessão de Crédito

**10 slides | Cenário recomendado: Expansivo com controle de risco**

---

## Slide 1 — Contexto e objetivo da política

**Título:** "Política de concessão de crédito: da estimativa de risco à decisão"

**Objetivo:** Estabelecer o problema de negócio e deixar claro o que a apresentação entrega — não um modelo isolado, mas uma política de crédito operável com quatro saídas de decisão.

**Mensagem principal:** O banco precisa de uma regra que diga, para cada proposta, quem aprova, quanto aprova e em que condições. Este trabalho constrói essa regra a partir de dados históricos do case.

**Visual recomendado:** Diagrama com uma proposta de crédito no centro e quatro saídas possíveis: aprovar valor solicitado / aprovar valor reduzido / análise manual / recusar. Destacar em rodapé os dois números de âncora: 4.862 operações de validação e 12,30% de inadimplência histórica.

**Tabelas e gráficos:** Nenhum neste slide. Visual esquemático apenas.

---

## Slide 2 — Bases disponíveis e limitações

**Título:** "O que tínhamos para construir a política"

**Objetivo:** Mostrar transparência sobre as variáveis disponíveis e enquadrar corretamente as limitações antes que a banca pergunte.

**Mensagem principal:** A partir da base histórica disponibilizada no case, construímos o score interno de PD; além disso, usamos renda, valor da parcela, comprometimento de renda, restritivos financeiros e relacionamento com o banco. Não havia bureau externo, garantia, LGD nem propostas recusadas.

**Visual recomendado:** Tabela em dois blocos lado a lado.

- Bloco esquerdo — "O que estava disponível": pd_score (construído internamente), renda, comprometimento de renda, restritivos financeiros, tempo de conta, flag de atividade do cliente.
- Bloco direito — "O que não estava disponível": score externo de bureau, garantia ou colateral, LGD, EAD, propostas recusadas, histórico detalhado de atrasos anteriores.

**Tabelas e gráficos:** Tabela de variáveis disponíveis e ausentes (extraída conceitualmente de `docs/06_contexto_politica_credito.md`, seções 8 e 9).

---

## Slide 3 — Fluxo metodológico do projeto

**Título:** "Seis etapas: da base bruta à política recomendada"

**Objetivo:** Mostrar que a política é resultado de um pipeline metodológico rigoroso, não de uma regra ad hoc.

**Mensagem principal:** O score de PD foi construído do zero, validado fora da amostra de treino e aplicado à política somente depois. O target de inadimplência foi usado apenas em treino e backtest — nunca como variável de decisão.

**Visual recomendado:** Diagrama de fluxo horizontal com seis etapas:

```
Diagnóstico das bases
→ Construção do target (12m)
→ EDA orientada à política
→ Modelagem de PD
→ Política inicial
→ Cenários e recomendação
```

Destacar com cor ou ícone que o `target_inadimplente_12m` entra apenas nas etapas de treino e backtest, nunca na regra de decisão.

**Tabelas e gráficos:** Nenhum dado quantitativo neste slide. Fluxograma conceitual.

---

## Slide 4 — Modelo não é política

**Título:** "O modelo estima risco. A política transforma risco em decisão."

**Objetivo:** Estabelecer a separação conceitual central que sustenta toda a apresentação.

**Mensagem principal:** O pd_score responde "qual a probabilidade de inadimplência desta proposta". A política responde "o que o banco deve fazer com essa proposta, dado o risco estimado, a capacidade de pagamento, os restritivos e o relacionamento do cliente".

**Visual recomendado:** Dois quadros conectados por seta.

- Quadro esquerdo — Modelo: input: variáveis da proposta → output: pd_score (probabilidade de inadimplência em 12 meses).
- Quadro direito — Política: input: pd_score + renda + restritivos + relacionamento → output: decisão + valor máximo sugerido.

**Tabelas e gráficos:** Nenhum. Visual conceitual apenas.

---

## Slide 5 — Lógica da decisão de crédito

**Título:** "A decisão passa por cinco camadas — e o valor é limitado pela capacidade de pagamento"

**Objetivo:** Tornar a estrutura da política compreensível e auditável para uma audiência não técnica.

**Mensagem principal:** Cada proposta percorre cinco camadas sequenciais antes de receber uma decisão. A decisão não é binária e o valor concedido é calculado, não arbitrário.

**Visual recomendado:** Tabela de camadas com critério e output de cada etapa.

| Camada | Critério | Output |
|---|---|---|
| Rating interno | pd_score | Faixa A a E |
| Capacidade de pagamento | % máx. parcela/renda por faixa | Parcela máxima bruta |
| Restritivos financeiros | restritivos_sobre_renda | Fator de 50% a 100% |
| Relacionamento | inatividade + tempo de conta | Parcela máxima final |
| Valor máximo sugerido | Fórmula de valor presente | Limite em R$ |
| Decisão | Limite vs. valor solicitado + faixa | Aprovar / Reduzir / Manual / Recusar |

**Tabelas e gráficos:** Tabela de camadas acima. Extraída de `outputs/tables/politica_estrutura_consolidada_decisao.csv`.

---

## Slide 6 — Performance do score/rating interno

**Título:** "Score interno com AUC 0,8752 e KS 0,5919: base técnica robusta"

**Objetivo:** Estabelecer a credibilidade do score antes de apresentar os cenários de política.

**Mensagem principal:** O modelo discrimina bem entre bons e maus pagadores. Na faixa A, inadimplência mínima. Na faixa E, a inadimplência observada chega a aproximadamente 56%, confirmando que o rating concentra corretamente os perfis de maior risco.

**Visual recomendado:** Dois painéis.

- Painel esquerdo: tabela de faixas com intervalo de PD estimada e distribuição de volume.
- Painel direito: gráfico de barras com bad rate observado por faixa (escada crescente de A a E).

| Faixa | PD estimada | Volume aprox. |
|---|---|---|
| A — Baixo risco | 0,47% a 4,25% | ~40% das operações |
| B — Médio-baixo | 4,26% a 8,23% | ~20% das operações |
| C — Médio risco | 8,23% a 14,65% | ~15% das operações |
| D — Alto risco | 14,67% a 35,04% | ~15% das operações |
| E — Muito alto | 35,05% a 92,14% | ~10% das operações |

**Tabelas e gráficos:** Tabela acima + gráfico de barras com bad rate por faixa. Extraído de `outputs/tables/politica_resumo_cenarios.csv` e `outputs/tables/politica_final_recomendada.csv`.

---

## Slide 7 — Comparação dos cenários

**Título:** "Três cenários, um trade-off: aprovação automática, inadimplência e exposição aprovada"

**Objetivo:** Demonstrar que a recomendação foi escolhida entre alternativas reais e quantificadas.

**Mensagem principal:** O cenário expansivo amplia a aprovação automática em 12 pontos percentuais em relação ao conservador, mantém a inadimplência dos aprovados aproximadamente 45% abaixo da taxa histórica e captura 52,93% da exposição aprovada — contra 36,37% no conservador. Os cenários mais conservadores têm bad rate de aprovados menor, mas restringem significativamente a aprovação automática e a exposição aprovada.

**Visual recomendado:** Tabela comparativa com destaque visual no cenário expansivo + gráfico de dispersão posicionando os três cenários no plano aprovação automática × inadimplência dos aprovados. Marcar a taxa histórica (12,30%) como linha de referência horizontal.

| Métrica | Conservador | Equilibrado | **Expansivo** |
|---|---|---|---|
| Aprovação automática | 74,89% | 74,97% | **86,65%** |
| Análise manual | 14,99% | 14,99% | **3,33%** |
| Recusa | 10,12% | 10,04% | **10,02%** |
| Inadimplência aprovados | 3,90% | 3,90% | **6,74%** |
| Exposição aprovada | 36,37% | 42,16% | **52,93%** |
| Valor médio aprovado | R$ 6.453 | R$ 7.473 | **R$ 8.116** |
| Taxa histórica (ref.) | 12,30% | 12,30% | 12,30% |

**Tabelas e gráficos:** `outputs/tables/politica_resumo_cenarios.csv` + `outputs/tables/politica_tabela_executiva_recomendacao.csv` + gráfico de trade-off `outputs/figures/06_tradeoff_cenarios_politica.html`.

---

## Slide 8 — Cenário recomendado

**Título:** "Recomendação: Expansivo com controle de risco"

**Objetivo:** Defender a escolha do cenário com base no scorecard gerencial e nos números de backtest.

**Mensagem principal:** Com 86,65% de aprovação automática, 6,74% de inadimplência dos aprovados — aproximadamente 45% abaixo do histórico — e 52,93% de exposição aprovada, o cenário recomendado expande a concessão mantendo o risco controlado.

**Visual recomendado:** Três métricas em destaque grande no topo (86,65% / 6,74% / 52,93%). Abaixo, scorecard com os quatro critérios de seleção e respectivos pesos.

| Critério | Peso | Lógica |
|---|---|---|
| Controle de inadimplência | 40% | Menor bad rate dos aprovados é melhor |
| Preservação da aprovação automática | 30% | Maior aprovação automática é melhor |
| Preservação da exposição aprovada | 20% | Maior exposição aprovada é melhor |
| Eficiência operacional | 10% | Menor análise manual é melhor |

**Score gerencial do cenário recomendado: 0,600**

**Tabelas e gráficos:** `outputs/tables/politica_tabela_executiva_recomendacao.csv` + `outputs/figures/06_taxas_decisao_por_cenario.html` + `outputs/figures/06_inadimplencia_aprovados_por_cenario.html`.

---

## Slide 9 — Política final por faixa de risco

**Título:** "A política em tabela: regras por faixa, capacidade de pagamento e redutores"

**Objetivo:** Tornar a política operacional, concreta e auditável — demonstrar que pode ser implementada como conjunto de regras explícitas.

**Mensagem principal:** A política recomendada é uma tabela de decisão transparente, não uma caixa preta. Cada variável tem papel definido e cada fator tem valor explícito.

**Visual recomendado:** Tabela completa da política por faixa de risco.

| Faixa | PD estimada | Ação principal | % máx. parcela/renda | Restritivos (fator) | Inativo | Tempo de conta |
|---|---|---|---|---|---|---|
| A — Baixo risco | 0,47% a 4,25% | Aprovação automática | 45% | sem=100%; ≤2%=95%; ≤5%=85%; ≤10%=70%; >10%=50% | ×90% | <1a: ×92%; 1–3a: ×98%; ≥3a: ×100% |
| B — Médio-baixo | 4,26% a 8,23% | Aprovação automática | 40% | idem | ×90% | idem |
| C — Médio risco | 8,23% a 14,65% | Aprovação automática | 35% | idem | ×90% | idem |
| D — Alto risco | 14,67% a 35,04% | Reduzido cond. / Manual | 25% | idem | ×90% | idem |
| E — Muito alto | 35,05% a 92,14% | Recusar | — | — | — | — |

**Tabelas e gráficos:** `outputs/tables/politica_final_recomendada.csv` + `outputs/figures/06_decisoes_por_faixa_risco.html` + `outputs/figures/06_valor_original_vs_aprovado.html`.

---

## Slide 10 — Limitações, governança e próximos passos

**Título:** "Fronteiras da política: o que validar antes da produção"

**Objetivo:** Demonstrar maturidade metodológica e apresentar um plano concreto para a fase seguinte.

**Mensagem principal:** As ausências de bureau externo, propostas recusadas, LGD e garantia não invalidam a política — definem o que precisa ser complementado antes da produção. A política recomendada é uma proposta inicial baseada em evidência histórica, sujeita à validação da área de crédito.

**Visual recomendado:** Dois blocos lado a lado.

Bloco esquerdo — Limitações e impacto:

| Limitação | Impacto |
|---|---|
| Sem propostas recusadas | Fronteira de recusa não observada diretamente |
| Sem garantia / LGD / EAD | Perda esperada em R$ não calculável |
| Sem score externo | Modelo depende apenas de dados internos |
| Sem histórico detalhado de atrasos | Poder preditivo pode ser subestimado |
| Variáveis sensíveis (idade, escolaridade) | Exigem análise de fairness e validação jurídica |
| Validado em backtest | Performance real pode diferir do simulado |

Bloco direito — Próximos passos:

- Validar produto, valor mínimo operacional e teto de comprometimento de renda com área de crédito
- Definir tratamento de restritivos: redutor ou recusa automática?
- Definir tratamento de cliente inativo: análise manual ou recusa?
- Análise de fairness por grupos demográficos
- Definir apetite máximo de bad rate para carteira aprovada
- Monitorar por safra após implantação: bad rate, AUC, KS, PSI do score

**Tabelas e gráficos:** Nenhum gráfico adicional. Tabela de limitações extraída de `docs/06_contexto_politica_credito.md`, seção 15.
