# Playbook — Contrato de dados do notebook 06

## 1. Objetivo

Este playbook define o contrato de dados mínimo para o notebook `06_cenarios_politica_recomendacao.ipynb`.

Ele deve evitar que a IA ou o analista use variáveis erradas, assuma colunas inexistentes ou reconstrua etapas anteriores sem necessidade.

---

## 2. Base principal esperada

O notebook 06 deve ler preferencialmente:

```text
data/processed/base_politica_validacao_com_score.parquet
```

Essa base é a saída do notebook 05 e deve conter a safra de validação enriquecida com score de PD, faixas de risco e política inicial.

---

## 3. Colunas obrigatórias

A base de entrada deve conter estas colunas:

```text
id_cliente
pd_score
faixa_risco
valor_renda
valor_emprestado
valor_parcela
valor_taxa
valor_prazo
valor_restritivos
restritivos_sobre_renda
comprometimento_renda
tempo_conta_anos
flag_cliente_ativo
target_inadimplente_12m
```

Se existir `id_operacao`, usar como identificador da operação.

Se não existir `id_operacao`, criar a partir do índice ou de `id_cliente`, documentando que no case cada cliente aparece uma vez na base de concessão.

---

## 4. Colunas opcionais úteis

Estas colunas são úteis, mas não obrigatórias:

```text
data_concessao
safra_concessao
idade_concessao
cat_escolaridade
cod_agencia
valor_maximo_sugerido
valor_aprovado
decisao_politica
classe_restritivo
redutor_restritivo
redutor_relacionamento
parcela_maxima
```

Se existirem, podem ser usadas para diagnóstico, comparação com política inicial e tabelas explicativas.

---

## 5. Papéis das variáveis

| Variável                  | Papel               | Pode entrar na regra? | Observação                              |
| ------------------------- | ------------------- | --------------------- | --------------------------------------- |
| `pd_score`                | risco               | sim                   | rating interno criado pelo modelo       |
| `faixa_risco`             | risco               | sim                   | discretização da PD                     |
| `valor_renda`             | capacidade          | sim                   | base do limite de parcela               |
| `valor_parcela`           | operação/capacidade | sim                   | comparação com renda                    |
| `valor_emprestado`        | operação/exposição  | sim                   | valor solicitado/concedido histórico    |
| `valor_taxa`              | operação            | sim                   | usada no cálculo de valor presente      |
| `valor_prazo`             | operação            | sim                   | usada no cálculo de valor presente      |
| `valor_restritivos`       | restritivo          | sim                   | proxy de pressão financeira             |
| `restritivos_sobre_renda` | restritivo          | sim                   | redutor de limite                       |
| `comprometimento_renda`   | capacidade          | sim                   | diagnóstico e regra                     |
| `tempo_conta_anos`        | relacionamento      | sim                   | redutor/bônus controlado                |
| `flag_cliente_ativo`      | relacionamento      | sim                   | cliente ativo/inativo                   |
| `idade_concessao`         | perfil              | usar com cautela      | mais adequado para modelo/interpretação |
| `cat_escolaridade`        | perfil              | usar com cautela      | atenção a governança/fairness           |
| `cod_agencia`             | monitoramento       | não recomendado       | risco de regra operacional enviesada    |
| `target_inadimplente_12m` | avaliação           | não                   | usar apenas para backtest               |
| `flag_inadimplente`       | avaliação futura    | não                   | potencial leakage                       |

---

## 6. Validações obrigatórias no notebook

Antes de simular cenários, executar validações:

### 6.1 Presença de colunas

Verificar se todas as colunas obrigatórias existem.

Se faltarem colunas, interromper com erro claro:

```text
Colunas obrigatórias ausentes: [...]
```

### 6.2 Tipos

Verificar se variáveis numéricas estão como numéricas:

```text
pd_score
valor_renda
valor_emprestado
valor_parcela
valor_taxa
valor_prazo
valor_restritivos
restritivos_sobre_renda
comprometimento_renda
tempo_conta_anos
target_inadimplente_12m
```

### 6.3 Nulos

Calcular nulos por coluna obrigatória.

Regra recomendada:

* `pd_score` nulo: não pode simular;
* `valor_renda` nulo ou zero: limite deve ser zero;
* `valor_taxa` nula: tratar com taxa técnica mínima;
* `valor_prazo` nulo ou zero: tratar com prazo mínimo 1;
* `target_inadimplente_12m` nulo: não usar na avaliação.

### 6.4 Faixa de score

Validar:

```text
0 <= pd_score <= 1
```

Se houver valores fora, interromper ou corrigir com alerta explícito.

### 6.5 Faixas de risco

Validar se `faixa_risco` contém apenas:

```text
A - Baixo risco
B - Médio-baixo risco
C - Médio risco
D - Alto risco
E - Muito alto risco
```

Se houver faixas diferentes, listar categorias encontradas.

---

## 7. Derivações auxiliares permitidas

O notebook 06 pode criar:

```text
classe_restritivo_cenario
classe_tempo_conta_cenario
pct_max_parcela_renda_cenario
redutor_restritivo_cenario
redutor_relacionamento_cenario
redutor_tempo_conta_cenario
parcela_maxima_cenario
valor_maximo_sugerido_cenario
valor_aprovado_cenario
decisao_cenario
cenario
```

Essas variáveis devem ser específicas do cenário e não devem sobrescrever variáveis originais sem necessidade.

---

## 8. Regras para restritivos

Criar classificação padronizada:

```text
sem_restritivo: valor nulo, zero ou menor que zero
ate_2pct:       até 2% da renda
ate_5pct:       acima de 2% até 5% da renda
ate_10pct:      acima de 5% até 10% da renda
acima_10pct:    acima de 10% da renda
```

Essa classificação deve alimentar redutores de limite.

---

## 9. Regras para tempo de relacionamento

Criar classificação padronizada:

```text
curto: tempo_conta_anos < 1
medio: 1 <= tempo_conta_anos < 3
longo: tempo_conta_anos >= 3
```

Uso recomendado:

* relacionamento curto: redutor leve ou moderado;
* relacionamento médio: neutro;
* relacionamento longo: neutro ou redutor menos severo.

Evitar aumentar agressivamente limite apenas por tempo de conta.

---

## 10. Tratamento de cliente ativo

`flag_cliente_ativo` deve ser interpretada como:

```text
1 = cliente ativo
0 = cliente inativo
```

Regra recomendada:

* cliente ativo: redutor 1.00;
* cliente inativo: redutor menor que 1.00.

O valor exato depende do cenário.

---

## 11. Fórmula padrão de limite

A política deve calcular:

```text
parcela_maxima =
    valor_renda
    × pct_max_parcela_renda_cenario
    × redutor_restritivo_cenario
    × redutor_relacionamento_cenario
    × redutor_tempo_conta_cenario
```

Depois:

```text
valor_maximo_sugerido =
    parcela_maxima × fator_valor_presente
```

Onde:

```text
fator_valor_presente =
    (1 - (1 + valor_taxa)^(-valor_prazo)) / valor_taxa
```

---

## 12. Tratamentos técnicos da fórmula

Aplicar tratamentos robustos:

```text
valor_renda <= 0 → parcela máxima = 0
valor_taxa <= 0 → substituir por 0.0001
valor_prazo <= 0 → substituir por 1
valor_maximo_sugerido < 0 → truncar em 0
valor_aprovado não pode ser maior que valor_emprestado
```

---

## 13. Decisões padronizadas

Usar exatamente estas categorias:

```text
Aprovar valor solicitado
Aprovar valor reduzido
Análise manual
Recusar
```

Não criar nomes alternativos.

Isso evita problemas na comparação dos cenários.

---

## 14. Indicadores obrigatórios de cenário

Para cada cenário, calcular:

```text
qtd_operacoes
taxa_historica_inadimplencia
taxa_aprovacao_automatica
taxa_analise_manual
taxa_recusa
inadimplencia_aprovados
pd_media_aprovados
valor_original_total
valor_aprovado_total
pct_exposicao_aprovada
reducao_exposicao
valor_medio_aprovado
```

---

## 15. Indicadores por decisão

Para cada cenário e decisão, calcular:

```text
qtd_operacoes
participacao_operacoes
bad_rate_observado
pd_media
valor_original_total
valor_aprovado_total
ticket_medio_original
ticket_medio_aprovado
```

---

## 16. Indicadores por faixa de risco

Para cada cenário e faixa de risco, calcular:

```text
qtd_operacoes
bad_rate_observado
pd_media
taxa_aprovacao
taxa_analise_manual
taxa_recusa
valor_original_total
valor_aprovado_total
pct_exposicao_aprovada
```

---

## 17. Critérios de consistência esperados

A simulação deve produzir resultados intuitivos:

1. a faixa E deve ter maior restrição que a faixa A;
2. o cenário expansivo deve aprovar mais que o conservador;
3. o cenário conservador deve ter menor inadimplência dos aprovados;
4. a exposição aprovada deve crescer do conservador para o expansivo;
5. a inadimplência dos aprovados não deve superar a taxa histórica sem justificativa;
6. análise manual deve concentrar risco intermediário;
7. recusa deve concentrar risco alto ou muito alto.

Se esses pontos não ocorrerem, investigar regra ou dados.

---

## 18. Saídas de auditoria

Salvar tabelas que permitam auditar a política:

```text
politica_contrato_dados_cenarios.csv
politica_parametros_cenarios.csv
politica_resumo_cenarios.csv
politica_resumo_decisoes_cenarios.csv
politica_resumo_faixas_cenarios.csv
politica_score_decisao_cenarios.csv
politica_final_recomendada.csv
```

---

## 19. Resumo executivo do contrato

O notebook 06 deve usar a base já preparada com `pd_score`, não deve retreinar modelo e não deve reconstruir target.

Seu papel é simular políticas alternativas com base em risco, capacidade de pagamento, restritivos e relacionamento.

O target de inadimplência 12m deve ser usado apenas para avaliar o desempenho histórico das decisões simuladas.
