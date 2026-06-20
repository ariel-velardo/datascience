# Instruções para IA — Geração v2 do notebook 06

## 1. Papel da IA

Atue como cientista de dados sênior especializado em:

* risco de crédito;
* política de concessão;
* modelagem de PD;
* score/rating;
* definição de limite;
* simulação de impacto financeiro;
* governança de modelos;
* explicabilidade aplicada a crédito.

A tarefa é refazer o notebook 06 para corrigir a camada de política.

A versão anterior se apoiava demais em score, percentual de parcela/renda e redutores. A nova versão deve implementar uma política de concessão baseada em **limite por rating, renda, teto e impacto financeiro**.

---

## 2. Escopo da tarefa

Refazer:

```text
notebooks/06_cenarios_politica_recomendacao.ipynb
```

O notebook deve comparar cenários de apetite de risco e recomendar uma política inicial de concessão baseada em:

```text
rating interno
+ multiplicador de renda
+ teto por rating
+ capacidade de pagamento
+ fatores de ajuste de limite
+ decisão
+ impacto financeiro
```

---

## 3. Arquivos que podem ser criados ou alterados

Pode alterar:

```text
notebooks/06_cenarios_politica_recomendacao.ipynb
```

Pode criar ou sobrescrever saídas do notebook 06:

```text
data/processed/base_simulacao_cenarios_politica.parquet

outputs/tables/politica_publico_faixa_renda_rating.csv
outputs/tables/politica_publico_rating_tempo_relacionamento.csv
outputs/tables/politica_publico_rating_pd_bad_rate.csv
outputs/tables/politica_publico_rating_exposicao.csv
outputs/tables/politica_publico_rating_restritivos.csv
outputs/tables/politica_parametros_limite_cenarios.csv
outputs/tables/politica_impacto_financeiro_cenarios.csv
outputs/tables/politica_impacto_por_rating.csv
outputs/tables/politica_impacto_por_decisao.csv
outputs/tables/politica_score_gerencial_cenarios.csv
outputs/tables/politica_final_recomendada_limites.csv

outputs/figures/06_publico_distribuicao_rating.html
outputs/figures/06_publico_bad_rate_rating.html
outputs/figures/06_publico_renda_rating.html
outputs/figures/06_impacto_exposicao_cenarios.html
outputs/figures/06_impacto_por_rating.html
outputs/figures/06_tradeoff_aprovacao_inadimplencia.html
outputs/figures/06_valor_solicitado_vs_aprovado.html
```

Pode atualizar, se necessário:

```text
docs/06_contexto_politica_credito.md
playbooks/06_metodologia_cenarios_politica.md
playbooks/06_contrato_dados_notebook_cenarios.md
playbooks/06_instrucoes_ia_geracao_notebook.md
```

---

## 4. Arquivos que não devem ser alterados

Não alterar:

```text
data/raw/*
notebooks/00_validacao_ambiente.ipynb
notebooks/01_diagnostico_bases.ipynb
notebooks/02_target_inadimplencia_12m.ipynb
notebooks/03_eda_credito.ipynb
notebooks/04_modelagem_pd.ipynb
notebooks/05_politica_concessao_credito.ipynb
outputs/models/*
```

Se precisar reaproveitar lógica, ler os notebooks anteriores e copiar apenas o necessário para o notebook 06.

---

## 5. Contexto obrigatório

A política é para concessão de empréstimo bancário parcelado.

A base sugere pessoa física com relacionamento bancário.

Não tratar como:

* política PJ;
* abertura de conta;
* financiamento com garantia conhecida;
* política de cartão;
* política completa de perda esperada;
* política com bureau externo completo.

Não criar variáveis inexistentes, como:

* faturamento;
* CNAE;
* ramo de atividade;
* porte PJ;
* garantia;
* colateral;
* LGD;
* EAD formal;
* score externo completo.

A base não possui propostas recusadas. Reconhecer essa limitação.

---

## 6. Fluxo já realizado no projeto

O projeto já executou:

```text
00 — validação de ambiente
01 — diagnóstico das bases
02 — construção do target de inadimplência 12m
03 — análise exploratória
04 — modelagem de PD
05 — política inicial e interpretação do modelo
```

O notebook 06 deve começar da base com score exportada pelo notebook 05.

Não recomeçar o case.

---

## 7. Entrada principal

Ler:

```text
data/processed/base_politica_validacao_com_score.parquet
```

Se não existir, procurar base equivalente em:

```text
data/processed/
```

Mas interromper se não houver `pd_score`.

Colunas obrigatórias:

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

Se `id_operacao` não existir, criar.

---

## 8. Regras de segurança

A IA deve garantir:

* não retreinar modelo;
* não recriar target;
* não usar `target_inadimplente_12m` como variável de decisão;
* usar target apenas para avaliação/backtest;
* não alterar notebooks 00 a 05;
* não alterar dados brutos;
* não usar `cod_agencia` como regra de concessão;
* não usar decisões da política antiga como insumo da nova decisão;
* não criar teto infinito;
* não deixar valor aprovado maior que valor solicitado.

---

## 9. Estrutura obrigatória do notebook

Criar o notebook com a estrutura:

```markdown
# 06 — Política de concessão baseada em limite e impacto financeiro

## 1. Contexto e correção metodológica
## 2. Setup e leitura da base com score
## 3. Contrato de dados e validações iniciais
## 4. Caracterização do público da política
## 5. Validação do rating interno
## 6. Definição dos parâmetros de limite
## 7. Funções da política de limite
## 8. Simulação dos cenários
## 9. Impacto financeiro da política
## 10. Comparação dos cenários e recomendação
## 11. Política final recomendada
## 12. Limitações, governança e próximos passos
## 13. Checklist de saídas
```

---

## 10. Contexto e correção metodológica

Na primeira seção, explicar:

* o modelo de PD não é a política;
* o score é usado como rating interno;
* a política deve definir limite;
* clientes de melhor rating podem ter maior alavancagem;
* clientes de pior rating devem ter teto menor, mesa ou recusa;
* a decisão deve depender de valor solicitado versus limite calculado;
* o impacto financeiro deve ser explicitado.

Evitar defender a política antiga como final.

---

## 11. Caracterização obrigatória do público

Criar e salvar tabelas:

### 11.1 Faixa de renda vs rating

```text
outputs/tables/politica_publico_faixa_renda_rating.csv
```

Tabela:

```text
faixa_renda
faixa_risco
qtd_clientes
```

### 11.2 Rating vs tempo de relacionamento

```text
outputs/tables/politica_publico_rating_tempo_relacionamento.csv
```

Tabela:

```text
faixa_risco
classe_tempo_relacionamento
qtd_clientes
```

### 11.3 Rating vs PD e bad rate

```text
outputs/tables/politica_publico_rating_pd_bad_rate.csv
```

Tabela:

```text
faixa_risco
qtd_clientes
pd_min
pd_media
pd_max
bad_rate_observado
```

### 11.4 Rating vs exposição

```text
outputs/tables/politica_publico_rating_exposicao.csv
```

Tabela:

```text
faixa_risco
qtd_clientes
renda_media
valor_solicitado_medio
valor_solicitado_total
parcela_media
comprometimento_medio
restritivos_media
restritivos_sobre_renda_media
```

### 11.5 Rating vs restritivos

```text
outputs/tables/politica_publico_rating_restritivos.csv
```

Tabela:

```text
faixa_risco
classe_restritivo
qtd_clientes
```

---

## 12. Faixas auxiliares

Implementar:

```python
classificar_faixa_renda
classificar_tempo_relacionamento
classificar_restritivo_sobre_renda
```

Faixas sugeridas de renda:

```text
Até R$ 2 mil
R$ 2 mil a R$ 5 mil
R$ 5 mil a R$ 10 mil
R$ 10 mil a R$ 20 mil
Acima de R$ 20 mil
```

Tempo de relacionamento:

```text
curto: tempo_conta_anos < 1
medio: 1 <= tempo_conta_anos < 3
longo: tempo_conta_anos >= 3
```

Restritivos:

```text
sem_restritivo
ate_2pct
ate_5pct
ate_10pct
acima_10pct
```

---

## 13. Validação do rating interno

Mostrar por rating:

```text
qtd_clientes
pd_min
pd_media
pd_max
bad_rate_observado
valor_solicitado_total
```

A narrativa deve explicar que:

* os intervalos de PD vêm da construção anterior do rating;
* a validade do rating é observada pela monotonicidade de PD e bad rate;
* rating melhor deve ter menor bad rate;
* rating pior deve concentrar maior inadimplência.

---

## 14. Parâmetros dos cenários

Criar três cenários:

```text
Conservador
Base/Equilibrado
Expansivo controlado
```

Cada cenário deve parametrizar por rating:

```text
multiplicador_renda
teto_rating
pct_max_comprometimento
elegivel_aprovacao_automatica
elegivel_aprovacao_reduzida
tratamento_rating
valor_minimo_operacional
```

Também deve parametrizar:

```text
fator_restritivo
fator_cliente_ativo
fator_tempo_relacionamento
```

Salvar:

```text
outputs/tables/politica_parametros_limite_cenarios.csv
```

---

## 15. Calibração de tetos

Os tetos devem ser defensáveis.

Usar preferencialmente percentis históricos de `valor_emprestado` por rating.

Exemplo de regra aceitável:

```text
Conservador:
teto por rating baseado em percentis menores da distribuição histórica.

Base/Equilibrado:
teto por rating baseado em percentis intermediários.

Expansivo controlado:
teto por rating baseado em percentis mais altos, mas ainda finitos.
```

Documentar a regra no notebook.

Nunca usar teto infinito.

---

## 16. Funções obrigatórias

Implementar funções reutilizáveis:

```python
classificar_faixa_renda
classificar_tempo_relacionamento
classificar_restritivo_sobre_renda
calcular_valor_presente_parcelas
calcular_limite_cliente
simular_politica_limite
resumir_impacto_cenario
resumir_impacto_por_rating
resumir_impacto_por_decisao
validar_consistencia_politica
```

As funções devem receber parâmetros explícitos e evitar dependência desnecessária de variáveis globais.

---

## 17. Fórmula da política

Para cada cliente e cenário:

### 17.1 Limite por multiplicador

```text
limite_multiplicador =
    valor_renda × multiplicador_renda
```

### 17.2 Limite por capacidade

```text
parcela_maxima =
    valor_renda × pct_max_comprometimento
```

```text
limite_capacidade =
    parcela_maxima × ((1 - (1 + valor_taxa)^(-valor_prazo)) / valor_taxa)
```

### 17.3 Limite bruto

```text
limite_bruto =
    min(limite_multiplicador, limite_capacidade, teto_rating)
```

### 17.4 Limite final

```text
limite_final =
    limite_bruto
    × fator_restritivo
    × fator_cliente_ativo
    × fator_tempo_relacionamento
```

Tratamentos:

```text
valor_renda <= 0 → limite zero
valor_taxa <= 0 → usar 0.0001
valor_prazo <= 0 → usar 1
limite_final < 0 → truncar em zero
```

---

## 18. Decisões obrigatórias

Usar exatamente:

```text
Aprovar valor solicitado
Aprovar valor reduzido
Análise manual
Recusar
```

### 18.1 Aprovar valor solicitado

Condição:

```text
rating elegível para automático
valor_emprestado <= limite_final
renda válida
sem restritivo impeditivo
sem regra de mesa
```

Valor aprovado:

```text
valor_aprovado = valor_emprestado
```

### 18.2 Aprovar valor reduzido

Condição:

```text
rating elegível
valor_emprestado > limite_final
limite_final >= valor_minimo_operacional
sem regra de recusa
sem obrigatoriedade de mesa
```

Valor aprovado:

```text
valor_aprovado = limite_final
```

### 18.3 Análise manual

Aplicar para:

```text
rating D, conforme cenário
restritivo relevante
cliente inativo com risco intermediário
proposta muito acima do limite
caso próximo ao teto
```

Valor aprovado automático:

```text
valor_aprovado = 0
```

### 18.4 Recusar

Aplicar para:

```text
rating E
renda inválida
limite final abaixo do mínimo operacional
restritivo severo conforme cenário
```

Valor aprovado automático:

```text
valor_aprovado = 0
```

---

## 19. Simulação dos cenários

Simular todos os cenários.

Salvar base consolidada:

```text
data/processed/base_simulacao_cenarios_politica.parquet
```

A base final deve conter:

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

## 20. Impacto financeiro

Gerar:

```text
outputs/tables/politica_impacto_financeiro_cenarios.csv
outputs/tables/politica_impacto_por_rating.csv
outputs/tables/politica_impacto_por_decisao.csv
```

Métricas mínimas:

```text
qtd_clientes
valor_solicitado_total
valor_aprovado_total
pct_exposicao_aprovada
limite_medio
valor_aprovado_medio
pd_media_aprovados
bad_rate_observado_aprovados
taxa_aprovacao_valor_solicitado
taxa_aprovacao_reduzida
taxa_aprovacao_automatica_total
taxa_analise_manual
taxa_recusa
exposicao_por_rating
```

---

## 21. Gráficos obrigatórios

Gerar e salvar:

```text
outputs/figures/06_publico_distribuicao_rating.html
outputs/figures/06_publico_bad_rate_rating.html
outputs/figures/06_publico_renda_rating.html
outputs/figures/06_impacto_exposicao_cenarios.html
outputs/figures/06_impacto_por_rating.html
outputs/figures/06_tradeoff_aprovacao_inadimplencia.html
outputs/figures/06_valor_solicitado_vs_aprovado.html
```

Usar Plotly.

Não usar Seaborn.

Seguir o padrão visual do projeto.

---

## 22. Escolha da recomendação

Não assumir previamente que o cenário expansivo é melhor.

Criar score gerencial como apoio, considerando:

```text
controle de inadimplência
aprovação automática
exposição aprovada
eficiência operacional
concentração de risco
```

Sugestão de pesos:

```text
controle de inadimplência: 40%
aprovação automática: 25%
exposição aprovada: 25%
eficiência operacional: 10%
```

Explicar que o score gerencial é apoio de decisão, não verdade absoluta.

A recomendação final deve ser justificada em texto.

---

## 23. Política final recomendada

Gerar:

```text
outputs/tables/politica_final_recomendada_limites.csv
```

A tabela deve conter:

```text
cenario_recomendado
faixa_risco
intervalo_pd
bad_rate_observado
multiplicador_renda
teto_rating
pct_max_comprometimento
tratamento_restritivos
tratamento_cliente_inativo
tratamento_tempo_relacionamento
acao_principal
regra_limite
observacao_negocio
```

Essa é a principal tabela gerencial da nova política.

---

## 24. Checklist de qualidade

Antes de finalizar, verificar:

```text
[ ] notebooks 00 a 05 não foram alterados
[ ] data/raw não foi alterado
[ ] modelo não foi retreinado
[ ] target não foi recriado
[ ] target não entra na decisão
[ ] rating A tem maior multiplicador/teto que B/C/D
[ ] rating E é recusado
[ ] rating D não recebe aprovação automática irrestrita
[ ] valor aprovado nunca supera valor solicitado
[ ] análise manual tem valor aprovado automático zero
[ ] recusa tem valor aprovado automático zero
[ ] não há teto infinito
[ ] tabelas de público foram geradas
[ ] tabelas de impacto financeiro foram geradas
[ ] política final por limite foi gerada
```

---

## 25. Limitações obrigatórias

Registrar no notebook:

* base contém apenas operações concedidas;
* ausência de propostas recusadas;
* ausência de garantia;
* ausência de LGD;
* ausência de EAD formal;
* ausência de score externo completo;
* ausência de histórico anterior detalhado de atraso;
* simulação histórica não é política definitiva de produção;
* parâmetros precisam de validação com política de crédito;
* variáveis como idade e escolaridade exigem governança;
* monitoramento por safra é obrigatório.

---

## 26. Fechamento esperado

A conclusão deve dizer, em essência:

```text
A política recomendada é uma política inicial de limite baseada em evidência histórica.
O score de PD foi usado como rating interno, mas a decisão de concessão combina rating, renda, teto de limite, capacidade de pagamento, restritivos e relacionamento.
A recomendação deve ser validada com a área de política de crédito antes de uso produtivo.
```
