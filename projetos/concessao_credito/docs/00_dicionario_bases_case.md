# Dicionário das bases do case de concessão de crédito

## 1. Objetivo

Este documento descreve as bases usadas no projeto de política de concessão de crédito.

Ele deve ser usado como referência para qualquer IA ou pessoa que vá trabalhar no projeto, evitando interpretações erradas sobre o produto, o público, as variáveis disponíveis e as limitações dos dados.

---

## 2. Base `concessao.csv`

### 2.1 Descrição

A base `concessao.csv` contém o histórico de empréstimos concedidos pelo banco fictício.

Cada linha representa uma operação concedida a um cliente.

A base contém dados disponíveis no momento em que o cliente pediu o empréstimo, incluindo:

* dados cadastrais;
* dados de relacionamento com o banco;
* dados financeiros;
* dados da operação de crédito concedida.

Essa base é a principal base de entrada para modelagem e política.

---

## 2.2 Dimensão

Inspeção inicial:

```text
linhas: 30.000
colunas: 13
clientes únicos: 30.000
duplicadas: 0
```

Cada `id_cliente` aparece uma única vez na base de concessão.

---

## 2.3 Janela temporal

```text
data mínima de concessão: 2019-08-20
data máxima de concessão: 2022-08-18
quantidade aproximada de meses de concessão: 37
```

Essa janela é importante porque a modelagem e a validação devem respeitar a ordem temporal.

Em crédito, o ideal é avaliar o modelo em safras futuras, evitando um split aleatório que misture passado e futuro.

---

## 2.4 Colunas da base `concessao.csv`

| Coluna                | Tipo esperado      | Descrição                                | Uso no projeto                             |
| --------------------- | ------------------ | ---------------------------------------- | ------------------------------------------ |
| `id_cliente`          | inteiro            | Identificador único do cliente           | Chave de ligação com inadimplência         |
| `data_concessao`      | data               | Data em que o empréstimo foi concedido   | Safra, target 12m, split temporal          |
| `valor_emprestado`    | numérico           | Valor do empréstimo concedido            | Exposição e comparação com limite sugerido |
| `valor_parcela`       | numérico           | Valor mensal da parcela                  | Capacidade de pagamento                    |
| `valor_taxa`          | numérico           | Taxa mensal da operação                  | Cálculo do valor presente do limite        |
| `valor_prazo`         | inteiro            | Prazo em meses                           | Cálculo do valor máximo sugerido           |
| `valor_renda`         | numérico           | Renda mensal do cliente                  | Capacidade de pagamento                    |
| `valor_restritivos`   | numérico           | Dívidas em órgãos de proteção ao crédito | Restritivo financeiro                      |
| `cat_escolaridade`    | categórico         | Escolaridade do cliente                  | Perfil cadastral; usar com cautela         |
| `flag_cliente_ativo`  | inteiro/binário    | 0 = não ativo, 1 = ativo                 | Relacionamento com o banco                 |
| `cod_agencia`         | inteiro/categórico | Agência vinculada ao cliente             | Monitoramento; evitar regra direta         |
| `data_nascimento`     | data               | Data de nascimento                       | Idade na concessão                         |
| `data_abertura_conta` | data               | Data de abertura da conta corrente       | Tempo de relacionamento                    |

---

## 2.5 Qualidade inicial dos dados

Achados principais:

```text
nulos em cat_escolaridade: 414
demais colunas sem nulos
duplicadas: 0
```

A variável `cat_escolaridade` tinha uma categoria duplicada por espaço no final:

```text
Fundamental Incompleto
Fundamental Incompleto 
```

A correção esperada é usar:

```python
df["cat_escolaridade"] = df["cat_escolaridade"].str.strip()
```

---

## 2.6 Distribuições relevantes da base `concessao`

Principais estatísticas observadas:

### Valor emprestado

```text
mediana: aproximadamente R$ 9,2 mil
média: aproximadamente R$ 13,1 mil
p95: aproximadamente R$ 37,7 mil
máximo: aproximadamente R$ 190,8 mil
```

### Valor da parcela

```text
mediana: aproximadamente R$ 1,36 mil
média: aproximadamente R$ 1,81 mil
p95: aproximadamente R$ 4,74 mil
```

### Renda

```text
mínimo: R$ 1.200
mediana: aproximadamente R$ 2,98 mil
média: aproximadamente R$ 3,61 mil
p95: aproximadamente R$ 8,09 mil
```

### Prazo

```text
mínimo: 3 meses
mediana: 9 meses
máximo: 15 meses
```

### Taxa mensal

```text
mediana: aproximadamente 4,0% ao mês
faixa aproximada: 1,87% a 6,05% ao mês
```

### Comprometimento de renda derivado

```text
comprometimento = valor_parcela / valor_renda
mediana: aproximadamente 50%
máximo observado: 90%
```

Essa variável é central para a política, pois ajuda a limitar a parcela máxima aceitável.

### Restritivos sobre renda derivado

```text
restritivos_sobre_renda = valor_restritivos / valor_renda
mediana: aproximadamente 0,6%
p75: aproximadamente 2,7%
p95: aproximadamente 9,4%
```

Essa variável deve ser usada como redutor de limite.

---

## 2.7 Variáveis derivadas esperadas

A partir da base `concessao`, os notebooks anteriores criaram ou devem criar:

| Variável derivada         | Fórmula/conceito                                         | Uso                     |
| ------------------------- | -------------------------------------------------------- | ----------------------- |
| `idade_concessao`         | diferença entre `data_concessao` e `data_nascimento`     | Perfil e risco          |
| `tempo_conta_anos`        | diferença entre `data_concessao` e `data_abertura_conta` | Relacionamento          |
| `comprometimento_renda`   | `valor_parcela / valor_renda`                            | Capacidade de pagamento |
| `restritivos_sobre_renda` | `valor_restritivos / valor_renda`                        | Pressão financeira      |
| `safra_concessao`         | mês/ano da concessão                                     | Análise temporal        |
| `data_ref_12m`            | fim do mês 12 meses após concessão                       | Construção do target    |

---

## 3. Base `inadimplencia.csv`

### 3.1 Descrição

A base `inadimplencia.csv` contém o acompanhamento mensal de inadimplência dos clientes após a concessão do empréstimo.

Cada linha representa o status de inadimplência de um cliente em uma data de referência mensal.

---

## 3.2 Dimensão

Inspeção inicial:

```text
linhas: 257.960
colunas: 3
clientes únicos: 28.700
duplicadas: 0
```

A base não contém todos os 30.000 clientes da concessão.

Foram identificados:

```text
clientes da concessão com acompanhamento: 28.700
clientes só em concessão: 1.300
clientes só em inadimplência: 0
```

Os 1.300 clientes sem acompanhamento parecem estar concentrados em safras recentes, especialmente perto do fim da janela de extração.

---

## 3.3 Janela temporal

```text
data mínima de referência: 2019-09-30
data máxima de referência: 2022-07-31
quantidade aproximada de meses de referência: 35
```

Essa janela limita quais concessões possuem informação suficiente para avaliar inadimplência 12 meses depois.

---

## 3.4 Colunas da base `inadimplencia.csv`

| Coluna              | Tipo esperado   | Descrição                           | Uso no projeto                     |
| ------------------- | --------------- | ----------------------------------- | ---------------------------------- |
| `id_cliente`        | inteiro         | Identificador do cliente            | Chave com concessão                |
| `data_referencia`   | data            | Mês de referência do acompanhamento | Construção da janela pós-concessão |
| `flag_inadimplente` | inteiro/binário | 0 = adimplente, 1 = inadimplente    | Target e backtest                  |

---

## 3.5 Cuidados com a base de inadimplência

A base de inadimplência não deve ser usada como feature de modelagem ou política, porque ela contém informações posteriores à concessão.

Ela deve ser usada apenas para:

1. construção do target;
2. avaliação histórica do modelo;
3. backtest da política.

Usar inadimplência futura como variável explicativa causaria vazamento de informação.

---

## 4. Relação entre as bases

A ligação entre as bases é feita por:

```text
id_cliente
```

A unidade de análise da política é a operação de empréstimo concedida.

Como cada cliente aparece uma única vez na base `concessao`, neste case `id_cliente` funciona também como chave da operação histórica.

Em produção, seria melhor ter um `id_operacao` próprio, mas no projeto foi criada uma identificação operacional quando necessário.

---

## 5. Construção do target de inadimplência 12m

O enunciado sugere usar como indicador de mau pagador o fato de o cliente estar inadimplente 12 meses após a concessão.

A lógica adotada no projeto foi:

1. calcular a data 12 meses após a concessão;
2. ajustar para o fim do mês, já que a inadimplência é mensal;
3. verificar se havia janela de acompanhamento suficiente;
4. criar `target_inadimplente_12m`;
5. separar operações sem janela completa para scoring futuro.

Resultado documentado:

```text
base original: 30.000 operações
operações com janela completa de 12 meses: 19.558
operações sem janela suficiente: 10.442
taxa de inadimplência 12m: aproximadamente 12,3%
```

---

## 6. Bases processadas geradas

Os notebooks anteriores geraram bases intermediárias e processadas.

Principais bases esperadas:

```text
data/interim/concessao_diagnostico.parquet
data/interim/inadimplencia_diagnostico.parquet

data/processed/base_concessao_com_target_12m.parquet
data/processed/base_modelagem_12m.parquet
data/processed/base_scoring_sem_janela_12m.parquet
data/processed/base_politica_validacao_com_score.parquet
```

A base que deve alimentar o notebook 06 é:

```text
data/processed/base_politica_validacao_com_score.parquet
```

Ela deve conter o score de PD, faixas de risco e variáveis necessárias para simular política.

---

## 7. Interpretação de negócio das bases

A base disponível é compatível com uma política de concessão de empréstimo para pessoa física com relacionamento bancário.

A base não é compatível com política PJ, pois não contém:

* faturamento;
* CNAE;
* ramo de atividade;
* porte;
* balanço;
* fluxo de caixa empresarial.

A base não é compatível com uma política completa de garantias, pois não contém:

* garantia;
* colateral;
* recuperação;
* LGD;
* EAD regulatório.

A base também não contém propostas recusadas. Portanto, a política será simulada sobre clientes que receberam crédito historicamente.

---

## 8. Uso correto das bases no notebook 06

No notebook 06, usar:

### Como entrada

```text
base_politica_validacao_com_score.parquet
```

### Como variáveis de decisão

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
* `flag_cliente_ativo`.

### Como variável de avaliação

* `target_inadimplente_12m`.

### Nunca usar como variável de decisão

* `flag_inadimplente` posterior;
* `target_inadimplente_12m`;
* qualquer informação após a concessão;
* decisão simulada de outro cenário.

---

## 9. Resumo executivo das bases

O projeto parte de uma base histórica de empréstimos concedidos e de uma base mensal de inadimplência posterior à concessão.

A partir dessas bases, foi criado um target de inadimplência em 12 meses e treinado um modelo de PD.

O score gerado pelo modelo será usado como rating interno de risco. A política de crédito será construída combinando esse rating com renda, comprometimento, restritivos, relacionamento e condições da operação.

A política final deve ser apresentada como uma política inicial simulada, sujeita a validação da área de crédito e monitoramento em produção.
