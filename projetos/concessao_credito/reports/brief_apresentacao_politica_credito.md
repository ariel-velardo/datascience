# Brief — Apresentação Executiva: Política de Concessão de Crédito

---

## Contexto do case

O projeto parte de uma base histórica de 30.000 operações de crédito concedidas, cruzada com dados de inadimplência posterior. A partir dessa base, foi criado o target de inadimplência em 12 meses, treinado um modelo supervisionado de probabilidade de default (PD) e, sobre o score resultante, construída uma política de concessão com quatro saídas de decisão possíveis.

O trabalho está estruturado em seis etapas: diagnóstico das bases, construção do target, análise exploratória orientada à política, modelagem de PD, política inicial e, por fim, comparação de cenários com recomendação final.

A base de validação da política contém **4.862 operações** com janela completa de acompanhamento em 12 meses. A taxa histórica de inadimplência nessa base é de **12,30%**.

---

## Objetivo da apresentação

Apresentar e defender uma política de concessão de crédito construída sobre dados históricos, demonstrando:

- como o score de risco foi construído e validado;
- como o score é transformado em decisão de crédito;
- por que o cenário recomendado equilibra crescimento e controle de risco;
- quais são as limitações da política e o que precisa ser validado antes da produção.

A apresentação não defende apenas um modelo — defende uma política de crédito operável e auditável.

---

## Produto tratado

Empréstimo bancário parcelado para pessoa física com relacionamento bancário.

As variáveis disponíveis — valor da parcela, prazo, taxa, renda, comprometimento de renda — são consistentes com esse tipo de produto. A base não contém descrição comercial explícita do produto. Em produção, o enquadramento seria confirmado pela área de crédito.

---

## Público tratado

Pessoa física com relacionamento bancário. As variáveis disponíveis indicam esse perfil: renda, data de nascimento, escolaridade, data de abertura de conta, tempo de conta, indicador de cliente ativo e restritivos financeiros. Não há variáveis típicas de pessoa jurídica.

---

## Limitações dos dados

| Limitação | Impacto |
|---|---|
| Sem propostas recusadas | Fronteira de recusa não observada diretamente (survivorship bias) |
| Sem garantia ou colateral | Não é possível calcular LGD nem perda esperada em R$ |
| Sem score externo de bureau | Modelo depende exclusivamente de dados internos do banco |
| Sem histórico detalhado de atrasos | Poder preditivo pode ser subestimado em perfis limítrofes |
| Variáveis sensíveis (idade, escolaridade) | Exigem análise de fairness e validação jurídica antes da produção |
| Validado em backtest, não em produção | Performance real pode diferir do simulado em condições novas |

Todas as limitações foram mapeadas explicitamente. A política não as oculta — define o que precisa ser complementado antes de avançar para produção.

---

## Cenário recomendado

**Nome gerencial:** Expansivo com controle de risco

| Indicador | Valor |
|---|---|
| Aprovação automática | 86,65% |
| Análise manual | 3,33% |
| Recusa | 10,02% |
| Inadimplência dos aprovados | 6,74% |
| Exposição aprovada | 52,93% |
| Taxa histórica de inadimplência (base) | 12,30% |
| Score gerencial ponderado | 0,600 |

O cenário foi escolhido por um scorecard com quatro critérios: controle de inadimplência (40%), preservação da aprovação automática (30%), preservação da exposição aprovada (20%) e eficiência operacional (10%).

---

## Comparativo dos cenários simulados

| Métrica | Conservador | Equilibrado | Expansivo (rec.) |
|---|---|---|---|
| Aprovação automática | 74,89% | 74,97% | **86,65%** |
| Análise manual | 14,99% | 14,99% | **3,33%** |
| Recusa | 10,12% | 10,04% | **10,02%** |
| Inadimplência aprovados | 3,90% | 3,90% | **6,74%** |
| Exposição aprovada | 36,37% | 42,16% | **52,93%** |
| Valor médio aprovado | R$ 6.453 | R$ 7.473 | **R$ 8.116** |

---

## Lógica da política

```
PD score → faixa de risco → capacidade de pagamento → redutores → valor máximo sugerido → decisão final
```

**Cinco camadas sequenciais:**

1. **Rating interno:** `pd_score` classifica a proposta nas faixas A (baixo) a E (muito alto risco).
2. **Capacidade de pagamento:** percentual máximo de parcela sobre renda, definido por faixa de risco.
3. **Restritivos financeiros:** fator multiplicativo conforme `restritivos_sobre_renda` (sem penalização até redução de 50%).
4. **Relacionamento:** fator por inatividade e tempo de conta.
5. **Valor máximo sugerido:** conversão da parcela máxima em limite financeiro via fórmula de valor presente.

**Decisão final:**
- Aprovar valor solicitado
- Aprovar valor reduzido
- Análise manual
- Recusar

---

## Estrutura de redutores do cenário recomendado

| Variável | Faixa | Fator aplicado |
|---|---|---|
| Restritivos / renda | Sem restritivos | 100% (sem penalização) |
| Restritivos / renda | Até 2% | 95% |
| Restritivos / renda | Até 5% | 85% |
| Restritivos / renda | Até 10% | 70% |
| Restritivos / renda | Acima de 10% | 50% |
| Atividade do cliente | Inativo | 90% |
| Tempo de conta | Menos de 1 ano | 92% |
| Tempo de conta | 1 a 3 anos | 98% |
| Tempo de conta | 3 anos ou mais | 100% (sem penalização) |

---

## Frase central da recomendação

> **"O modelo estima risco. A política transforma risco em decisão."**

A política recomendada usa o score interno de PD como rating de risco e combina essa informação com capacidade de pagamento, restritivos financeiros e relacionamento com o banco para definir aprovação, aprovação com valor reduzido, análise manual ou recusa. Como a base não informa garantias, recuperação ou propostas recusadas, a recomendação deve ser tratada como uma política inicial simulada, sujeita à validação da área de crédito e calibração conforme o apetite de risco da instituição.
