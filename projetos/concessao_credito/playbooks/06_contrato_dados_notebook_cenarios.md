# Playbook — Contrato de dados v2 do notebook 06

## 1. Objetivo

Este playbook define o contrato de dados mínimo para o notebook:

```text
notebooks/06_cenarios_politica_recomendacao.ipynb
```

A nova versão do notebook 06 deve simular uma política de concessão baseada em:

```text
rating interno
+ renda
+ multiplicador de renda
+ teto por rating
+ capacidade de pagamento
+ fatores de ajuste de limite
+ impacto financeiro
```

O objetivo deste contrato é evitar:

* uso de variáveis erradas;
* uso de target como regra de decisão;
* reconstrução desnecessária de etapas anteriores;
* criação de variáveis inexistentes;
* uso de premissas não suportadas pela base.

---

## 2. Base principal esperada

O notebook 06 deve ler preferencialmente:

```text
data/processed/base_politica_validacao_com_score.parquet
```

Essa base é a saída do notebook 05 e contém a safra de validação enriquecida com:

* score de PD;
* rating/faixa de risco;
* variáveis financeiras;
* variáveis de operação;
* variáveis de relacionamento;
* variáveis de restritivos;
* target de inadimplência apenas para backtest.

Se essa base não existir, o notebook pode procurar base equivalente em:

```text
data/processed/
```

Mas deve interromper se não encontrar uma base com score de PD já calculado.

O notebook 06 não deve retreinar modelo nem recriar target.

---

## 3. Colunas obrigatórias

A base de entrada deve conter:

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

Se `id_operacao` existir, usar como identificador da operação.

Se `id_operacao` não existir, criar a partir do índice ou de `id_cliente`, documentando que no case cada cliente aparece uma única vez na base de concessão.

---

## 4. Colunas opcionais úteis

Estas colunas podem ser usadas para diagnóstico, se existirem:

```text
id_operacao
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

Observações:

* `idade_concessao` e `cat_escolaridade` podem aparecer em diagnóstico e interpretação, mas exigem cautela de governança.
* `cod_agencia` não deve ser usado como regra de concessão; pode ser usado apenas para monitoramento.
* `valor_maximo_sugerido`, `valor_aprovado` e `decisao_politica`, se existirem, pertencem à política anterior e podem ser usadas apenas como referência histórica, não como insumo da nova decisão.

---

## 5. Papéis das variáveis

| Variável                  | Papel               | Pode entrar na regra? | Observação                           |
| ------------------------- | ------------------- | --------------------- | ------------------------------------ |
| `id_cliente`              | identificador       | não                   | Chave do cliente                     |
| `id_operacao`             | identificador       | não                   | Criar se não existir                 |
| `pd_score`                | risco               | sim                   | Score interno de PD                  |
| `faixa_risco`             | rating              | sim                   | Rating interno derivado do score     |
| `valor_renda`             | capacidade/limite   | sim                   | Base para multiplicador e capacidade |
| `valor_emprestado`        | valor solicitado    | sim                   | Proxy do valor solicitado histórico  |
| `valor_parcela`           | operação/capacidade | sim                   | Diagnóstico e comparação             |
| `valor_taxa`              | operação            | sim                   | Usada no valor presente              |
| `valor_prazo`             | operação            | sim                   | Usada no valor presente              |
| `valor_restritivos`       | restritivo          | sim                   | Proxy de pressão financeira          |
| `restritivos_sobre_renda` | restritivo          | sim                   | Fator de ajuste de limite            |
| `comprometimento_renda`   | capacidade          | sim                   | Diagnóstico e regra auxiliar         |
| `tempo_conta_anos`        | relacionamento      | sim                   | Fator de ajuste de limite            |
| `flag_cliente_ativo`      | relacionamento      | sim                   | Cliente ativo/inativo                |
| `idade_concessao`         | perfil/governança   | evitar regra direta   | Usar com cautela                     |
| `cat_escolaridade`        | perfil/governança   | evitar regra direta   | Usar com cautela                     |
| `cod_agencia`             | monitoramento       | não recomendado       | Não usar como política de concessão  |
| `target_inadimplente_12m` | avaliação/backtest  | não                   | Nunca usar na decisão                |
| `flag_inadimplente`       | avaliação futura    | não                   | Potencial leakage                    |

---

## 6. Validações obrigatórias

Antes de simular cenários, validar:

### 6.1 Presença de colunas

Verificar se todas as colunas obrigatórias existem.

Se faltarem colunas, interromper com erro claro:

```text
Colunas obrigatórias ausentes: [...]
```

### 6.2 Tipos numéricos

Validar ou converter para numérico:

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

Calcular percentual de nulos nas colunas obrigatórias.

Regras:

```text
pd_score nulo → não pode simular
faixa_risco nulo → não pode simular
valor_renda nulo ou <= 0 → limite deve ser zero
valor_taxa nula ou <= 0 → usar taxa técnica mínima
valor_prazo nulo ou <= 0 → usar prazo mínimo 1
target_inadimplente_12m nulo → não usar na avaliação
```

### 6.4 Faixa do score

Validar:

```text
0 <= pd_score <= 1
```

Se houver valores fora do intervalo, interromper ou corrigir com alerta explícito.

### 6.5 Faixas de risco esperadas

Validar se `faixa_risco` contém apenas categorias compatíveis com:

```text
A - Baixo risco
B - Médio-baixo risco
C - Médio risco
D - Alto risco
E - Muito alto risco
```

Se houver categorias diferentes, listar as categorias encontradas e padronizar se possível.

---

## 7. Variáveis derivadas permitidas

O notebook 06 pode criar:

```text
id_operacao
faixa_renda
classe_restritivo_cenario
classe_tempo_relacionamento
multiplicador_renda_cenario
teto_rating_cenario
pct_max_comprometimento_cenario
fator_restritivo_cenario
fator_cliente_ativo_cenario
fator_tempo_relacionamento_cenario
parcela_maxima_cenario
limite_multiplicador_cenario
limite_capacidade_cenario
limite_bruto_cenario
limite_final_cenario
valor_aprovado_cenario
decisao_cenario
cenario
```

Essas variáveis devem ser específicas do cenário e não devem sobrescrever variáveis originais.

---

## 8. Variáveis que não podem ser usadas na decisão

Não usar como entrada de decisão:

```text
target_inadimplente_12m
flag_inadimplente
inadimplência posterior
decisões simuladas anteriores
bad rate observado
qualquer variável criada após a concessão
```

Essas variáveis podem ser usadas somente para avaliação histórica/backtest.

---

## 9. Faixa de renda

Criar `faixa_renda` para caracterização do público.

Sugestão inicial:

```text
Até R$ 2 mil
R$ 2 mil a R$ 5 mil
R$ 5 mil a R$ 10 mil
R$ 10 mil a R$ 20 mil
Acima de R$ 20 mil
```

Se a distribuição da base exigir outro corte, documentar.

---

## 10. Classe de restritivo

Criar classificação padronizada:

```text
sem_restritivo: valor nulo, zero ou menor que zero
ate_2pct:       até 2% da renda
ate_5pct:       acima de 2% até 5% da renda
ate_10pct:      acima de 5% até 10% da renda
acima_10pct:    acima de 10% da renda
```

Essa classe deve alimentar fatores de ajuste de limite.

---

## 11. Classe de relacionamento

Criar classificação padronizada:

```text
curto: tempo_conta_anos < 1
medio: 1 <= tempo_conta_anos < 3
longo: tempo_conta_anos >= 3
```

Essa classe deve alimentar fatores de ajuste de limite.

Evitar bônus agressivo por tempo de conta. Relacionamento deve ser usado como fator de prudência, não como substituto do risco.

---

## 12. Parâmetros obrigatórios por cenário

Cada cenário deve conter:

```text
cenario
faixa_risco
multiplicador_renda
teto_rating
pct_max_comprometimento
elegivel_aprovacao_automatica
elegivel_aprovacao_reduzida
tratamento_rating
valor_minimo_operacional
```

Além disso, cada cenário deve ter tabelas de fatores:

```text
fatores por classe_restritivo
fatores por flag_cliente_ativo
fatores por classe_tempo_relacionamento
```

---

## 13. Cálculo do limite

### 13.1 Limite por multiplicador

```text
limite_multiplicador =
    valor_renda × multiplicador_renda
```

### 13.2 Limite por capacidade

```text
parcela_maxima =
    valor_renda × pct_max_comprometimento
```

```text
limite_capacidade =
    parcela_maxima × ((1 - (1 + valor_taxa)^(-valor_prazo)) / valor_taxa)
```

Tratamentos:

```text
valor_taxa <= 0 → substituir por 0.0001
valor_prazo <= 0 → substituir por 1
valor_renda <= 0 → limite zero
```

### 13.3 Limite bruto

```text
limite_bruto =
    min(limite_multiplicador, limite_capacidade, teto_rating)
```

### 13.4 Limite final

```text
limite_final =
    limite_bruto
    × fator_restritivo
    × fator_cliente_ativo
    × fator_tempo_relacionamento
```

Tratamentos:

```text
limite_final < 0 → truncar em zero
limite_final nulo → zero
```

---

## 14. Valor aprovado

O valor aprovado automático não pode ser maior que o valor solicitado histórico.

Usar:

```text
valor_aprovado =
    min(valor_emprestado, limite_final)
```

Mas somente para decisões:

```text
Aprovar valor solicitado
Aprovar valor reduzido
```

Para:

```text
Análise manual
Recusar
```

usar:

```text
valor_aprovado = 0
```

---

## 15. Categorias de decisão

Usar exatamente:

```text
Aprovar valor solicitado
Aprovar valor reduzido
Análise manual
Recusar
```

Não criar nomes alternativos.

---

## 16. Indicadores obrigatórios de cenário

Para cada cenário, calcular:

```text
qtd_clientes
taxa_historica_inadimplencia
taxa_aprovacao_valor_solicitado
taxa_aprovacao_reduzida
taxa_aprovacao_automatica_total
taxa_analise_manual
taxa_recusa
pd_media_aprovados
bad_rate_observado_aprovados
valor_solicitado_total
valor_aprovado_total
pct_exposicao_aprovada
reducao_exposicao
limite_medio
valor_aprovado_medio
```

---

## 17. Indicadores por rating

Para cada cenário e rating, calcular:

```text
cenario
faixa_risco
qtd_clientes
pd_media
bad_rate_observado
renda_media
valor_solicitado_total
valor_aprovado_total
pct_exposicao_aprovada
limite_medio
valor_aprovado_medio
taxa_aprovacao_automatica
taxa_analise_manual
taxa_recusa
```

---

## 18. Indicadores por decisão

Para cada cenário e decisão, calcular:

```text
cenario
decisao
qtd_clientes
participacao_clientes
pd_media
bad_rate_observado
valor_solicitado_total
valor_aprovado_total
valor_solicitado_medio
valor_aprovado_medio
```

---

## 19. Tabelas de público obrigatórias

Salvar:

```text
outputs/tables/politica_publico_faixa_renda_rating.csv
outputs/tables/politica_publico_rating_tempo_relacionamento.csv
outputs/tables/politica_publico_rating_pd_bad_rate.csv
outputs/tables/politica_publico_rating_exposicao.csv
outputs/tables/politica_publico_rating_restritivos.csv
```

---

## 20. Tabelas de política obrigatórias

Salvar:

```text
outputs/tables/politica_parametros_limite_cenarios.csv
outputs/tables/politica_impacto_financeiro_cenarios.csv
outputs/tables/politica_impacto_por_rating.csv
outputs/tables/politica_impacto_por_decisao.csv
outputs/tables/politica_score_gerencial_cenarios.csv
outputs/tables/politica_final_recomendada_limites.csv
```

---

## 21. Base final simulada

Salvar:

```text
data/processed/base_simulacao_cenarios_politica.parquet
```

Essa base deve conter, para cada cliente e cenário:

```text
cenario
id_cliente
id_operacao
pd_score
faixa_risco
valor_renda
valor_emprestado
valor_taxa
valor_prazo
classe_restritivo_cenario
classe_tempo_relacionamento
multiplicador_renda_cenario
teto_rating_cenario
pct_max_comprometimento_cenario
limite_multiplicador_cenario
limite_capacidade_cenario
limite_bruto_cenario
limite_final_cenario
decisao_cenario
valor_aprovado_cenario
target_inadimplente_12m
```

---

## 22. Consistência esperada

A simulação deve produzir resultados intuitivos:

1. rating A deve ter maior multiplicador/teto que B, C e D;
2. rating E deve ser o mais restrito;
3. valor aprovado nunca deve superar valor solicitado;
4. análise manual e recusa devem ter valor aprovado automático zero;
5. cenário expansivo deve aprovar mais exposição que o conservador;
6. cenário conservador deve ter menor risco médio dos aprovados;
7. rating D não deve receber aprovação automática irrestrita;
8. rating E não deve receber limite automático;
9. não deve existir teto infinito;
10. target não deve entrar na decisão.

Se essas regras não forem atendidas, investigar antes de recomendar a política.

---

## 23. Resumo executivo do contrato

O notebook 06 deve usar a base já preparada com `pd_score`.

Ele não deve retreinar modelo, recriar target ou usar inadimplência posterior como decisão.

A política deve ser simulada como uma política de limite, combinando:

```text
rating
+ renda
+ multiplicador
+ teto
+ capacidade
+ restritivos
+ relacionamento
```

A avaliação histórica deve usar o target apenas para backtest.
