# Playbook — Metodologia para cenários de política de crédito

## 1. Objetivo

Este playbook orienta a construção do notebook `06_cenarios_politica_recomendacao.ipynb`.

O notebook deve transformar a política inicial criada no notebook 05 em uma comparação estruturada de cenários, permitindo escolher uma recomendação final com base no trade-off entre:

* inadimplência dos aprovados;
* taxa de aprovação;
* exposição financeira aprovada;
* volume enviado para análise manual;
* concentração de risco em recusas e análise manual.

---

## 2. Arquivo de entrada

O notebook 06 deve partir da base exportada no final do notebook 05:

```text
data/processed/base_politica_validacao_com_score.parquet
```

Essa base deve conter, no mínimo:

* `id_operacao`;
* `id_cliente`;
* `pd_score`;
* `faixa_risco`;
* `valor_renda`;
* `valor_emprestado`;
* `valor_parcela`;
* `valor_taxa`;
* `valor_prazo`;
* `valor_restritivos`;
* `restritivos_sobre_renda`;
* `comprometimento_renda`;
* `tempo_conta_anos`;
* `flag_cliente_ativo`;
* `target_inadimplente_12m`.

Se o arquivo não existir, verificar se o notebook 05 salvou uma base equivalente em `data/processed`.

---

## 3. Contrato de dados

Antes de simular cenários, validar:

1. existência das colunas obrigatórias;
2. tipos das variáveis principais;
3. percentual de nulos;
4. presença de valores negativos indevidos;
5. distribuição de `pd_score`;
6. consistência de `faixa_risco`;
7. taxa histórica de inadimplência;
8. soma de exposição original.

Criar uma tabela de contrato de dados com:

* coluna;
* tipo;
* percentual de nulos;
* papel na política;
* observação.

Papel possível:

* risco;
* capacidade;
* relacionamento;
* restritivo;
* operação;
* avaliação;
* identificador.

---

## 4. Diagnóstico inicial

Antes de criar novos cenários, reproduzir a leitura da política inicial.

Indicadores mínimos:

* quantidade de operações;
* taxa histórica de inadimplência;
* taxa de aprovação automática;
* taxa de análise manual;
* taxa de recusa;
* inadimplência dos aprovados;
* valor original total;
* valor aprovado total;
* percentual de exposição aprovada;
* redução de exposição;
* valor médio aprovado.

Se as colunas da política inicial existirem, usar:

* `decisao_politica`;
* `valor_aprovado`;
* `valor_maximo_sugerido`.

Se não existirem, documentar que a política inicial será reconstruída como cenário conservador.

---

## 5. Variáveis de política

As variáveis devem ser organizadas em blocos.

### Risco

* `pd_score`;
* `faixa_risco`.

### Capacidade de pagamento

* `valor_renda`;
* `valor_parcela`;
* `comprometimento_renda`.

### Restritivos

* `valor_restritivos`;
* `restritivos_sobre_renda`.

### Relacionamento

* `flag_cliente_ativo`;
* `tempo_conta_anos`.

### Operação

* `valor_emprestado`;
* `valor_taxa`;
* `valor_prazo`.

### Avaliação

* `target_inadimplente_12m`.

---

## 6. Variáveis que não podem ser usadas como feature de decisão

Não usar como entrada da regra:

* inadimplência posterior;
* target;
* qualquer variável criada após o evento de concessão;
* decisões simuladas anteriores como insumo de decisão;
* dados da base de inadimplência posteriores à concessão.

O target só pode ser usado para backtest.

---

## 7. Classificação de restritivos

Criar uma variável auxiliar de classe de restritivo sobre renda.

Sugestão:

```text
sem_restritivo: restritivos_sobre_renda <= 0 ou nulo
ate_2pct:       0 < restritivos_sobre_renda <= 0.02
ate_5pct:       0.02 < restritivos_sobre_renda <= 0.05
ate_10pct:      0.05 < restritivos_sobre_renda <= 0.10
acima_10pct:    restritivos_sobre_renda > 0.10
```

Essa variável deve alimentar redutores de limite.

---

## 8. Classificação de relacionamento

Criar uma variável auxiliar para tempo de conta.

Sugestão:

```text
relacionamento_curto: tempo_conta_anos < 1
relacionamento_medio: 1 <= tempo_conta_anos < 3
relacionamento_longo: tempo_conta_anos >= 3
```

Essa variável pode alimentar redutores ou bônus controlados.

Não criar bônus agressivo por relacionamento. Em política conservadora, relacionamento deve reduzir restrição, não eliminar risco.

---

## 9. Cenários mínimos

Criar três cenários.

### 9.1 Conservador

Objetivo:

* proteger carteira;
* reduzir inadimplência dos aprovados;
* reduzir exposição em faixas de maior risco.

Parâmetros sugeridos:

```text
A - Baixo risco:       35% da renda
B - Médio-baixo risco: 30% da renda
C - Médio risco:       25% da renda
D - Alto risco:        análise manual
E - Muito alto risco:  recusa
```

Redutores mais fortes para restritivos e cliente inativo.

### 9.2 Equilibrado

Objetivo:

* preservar aprovação;
* manter inadimplência controlada;
* evitar redução excessiva de exposição.

Parâmetros sugeridos:

```text
A - Baixo risco:       40% da renda
B - Médio-baixo risco: 35% da renda
C - Médio risco:       30% da renda
D - Alto risco:        análise manual
E - Muito alto risco:  recusa
```

Redutores moderados.

### 9.3 Expansivo

Objetivo:

* ampliar concessão;
* aceitar maior risco;
* testar limite de apetite comercial.

Parâmetros sugeridos:

```text
A - Baixo risco:       45% da renda
B - Médio-baixo risco: 40% da renda
C - Médio risco:       35% da renda
D - Alto risco:        aprovar reduzido ou análise manual, conforme restritivos
E - Muito alto risco:  recusa
```

Redutores mais leves, mas nunca zerar governança sobre restritivos.

---

## 10. Cálculo da parcela máxima

A fórmula-base da política deve ser:

```text
parcela_maxima =
    valor_renda
    × pct_max_parcela_renda_cenario
    × redutor_restritivo
    × redutor_cliente_ativo
    × redutor_tempo_conta
```

Cuidados:

* renda nula ou zero deve gerar limite zero;
* percentual máximo depende da faixa de risco;
* redutores devem ser multiplicativos;
* redutor nunca deve aumentar limite acima do percentual-base, salvo decisão explícita e documentada.

---

## 11. Conversão da parcela máxima em valor máximo

Usar fórmula de valor presente de uma anuidade:

```text
valor_maximo_sugerido =
    parcela_maxima × ((1 - (1 + taxa)^(-prazo)) / taxa)
```

Tratamentos:

* se taxa <= 0, substituir por valor mínimo técnico, como 0.0001;
* se prazo <= 0, substituir por 1;
* se valor máximo calculado for negativo, truncar em zero;
* se valor máximo for maior que o solicitado, aprovar no máximo o solicitado.

---

## 12. Decisão da política

A decisão deve seguir a hierarquia:

1. risco extremo;
2. restritivos severos;
3. capacidade de pagamento;
4. valor mínimo operacional;
5. análise manual.

Sugestão de decisões:

```text
Aprovar valor solicitado:
    valor_maximo_sugerido >= valor_emprestado
    e faixa elegível para aprovação automática

Aprovar valor reduzido:
    valor_maximo_sugerido < valor_emprestado
    e valor_maximo_sugerido >= valor_minimo_aprovacao
    e faixa elegível para aprovação reduzida

Análise manual:
    risco alto
    ou restritivo relevante
    ou cliente inativo com proposta relevante
    ou caso próximo da fronteira

Recusar:
    risco muito alto
    ou valor máximo abaixo do mínimo operacional
    ou restritivo severo conforme cenário
```

---

## 13. Métricas de comparação dos cenários

Para cada cenário, calcular:

* quantidade de operações;
* taxa histórica de inadimplência;
* taxa de aprovação automática;
* taxa de análise manual;
* taxa de recusa;
* inadimplência observada dos aprovados;
* PD média dos aprovados;
* valor original total;
* valor aprovado total;
* percentual de exposição aprovada;
* redução de exposição;
* valor médio aprovado;
* valor médio aprovado reduzido;
* inadimplência em análise manual;
* inadimplência nos recusados;
* percentual de inadimplentes capturados em recusa/análise manual.

---

## 14. Gráficos obrigatórios

Criar e salvar os seguintes gráficos:

1. Trade-off entre aprovação e inadimplência dos aprovados;
2. Taxa de aprovação, análise manual e recusa por cenário;
3. Inadimplência dos aprovados por cenário;
4. Exposição aprovada por cenário;
5. Distribuição das decisões por faixa de risco;
6. Comparativo de valor original versus valor aprovado.

Todos os gráficos devem seguir o padrão visual do projeto.

---

## 15. Critério de recomendação

Criar uma tabela de decisão gerencial com score ponderado.

Sugestão de pesos:

```text
controle de inadimplência: 40%
preservação da aprovação: 30%
preservação da exposição: 20%
eficiência operacional: 10%
```

Normalizar métricas:

* menor inadimplência dos aprovados é melhor;
* maior aprovação automática é melhor;
* maior exposição aprovada é melhor;
* menor análise manual é melhor, desde que o risco esteja controlado.

O cenário recomendado deve ser escolhido pelos resultados, não por preferência prévia.

Se o cenário equilibrado tiver inadimplência substancialmente abaixo da taxa histórica e preservar mais exposição que o conservador, ele tende a ser a recomendação principal.

---

## 16. Política final proposta

Após escolher o cenário recomendado, gerar tabela final com:

* faixa de risco;
* intervalo de PD;
* ação principal;
* percentual máximo de parcela/renda;
* tratamento de restritivos;
* tratamento de cliente inativo;
* tratamento de tempo de conta;
* regra de limite;
* observação de negócio.

Essa tabela será a principal saída gerencial do notebook.

---

## 17. Limitações e governança

A conclusão deve registrar:

* ausência de propostas recusadas;
* ausência de garantia;
* ausência de LGD e EAD formais;
* ausência de score externo;
* ausência de histórico anterior detalhado de atraso;
* uso de variáveis sensíveis ou potencialmente sensíveis exige governança;
* necessidade de validação com área de política;
* necessidade de monitoramento pós-implantação.

---

## 18. Monitoramento recomendado

Sugerir monitoramento periódico de:

* taxa de aprovação;
* taxa de recusa;
* taxa de análise manual;
* inadimplência por safra;
* bad rate por faixa de risco;
* KS;
* AUC;
* PSI das principais variáveis;
* estabilidade do `pd_score`;
* concentração de decisões por grupos;
* valor aprovado;
* perda observada, caso disponível.

---

## 19. Saídas esperadas

O notebook deve gerar:

```text
data/processed/base_simulacao_cenarios_politica.parquet

outputs/tables/politica_contrato_dados_cenarios.csv
outputs/tables/politica_variaveis_disponiveis_limitacoes.csv
outputs/tables/politica_resumo_cenarios.csv
outputs/tables/politica_resumo_decisoes_cenarios.csv
outputs/tables/politica_resumo_faixas_cenarios.csv
outputs/tables/politica_score_decisao_cenarios.csv
outputs/tables/politica_final_recomendada.csv

outputs/figures/06_tradeoff_cenarios_politica.html
outputs/figures/06_taxas_decisao_por_cenario.html
outputs/figures/06_inadimplencia_aprovados_por_cenario.html
outputs/figures/06_exposicao_aprovada_por_cenario.html
outputs/figures/06_decisoes_por_faixa_risco.html
outputs/figures/06_valor_original_vs_aprovado.html
```

---

## 20. Frase de fechamento do notebook

A política recomendada deve ser apresentada como uma política inicial baseada em evidência histórica, não como regra definitiva de produção.

A recomendação final deve deixar claro que o score de PD é uma camada de mensuração de risco e que a decisão de concessão combina risco, capacidade de pagamento, restritivos e relacionamento.
