# Playbook — Metodologia v2 para política de concessão baseada em limite

## 1. Objetivo

Este playbook orienta a reconstrução do notebook `06_cenarios_politica_recomendacao.ipynb`.

A versão anterior da política usava principalmente:

```text
PD / rating
+ percentual máximo de parcela/renda
+ redutores
+ decisão automática/manual/recusa
```

Essa abordagem é útil como primeira simulação, mas não é suficiente como política de concessão de crédito, porque não explicita de forma clara:

* qual público será alavancado;
* quanto limite será concedido;
* qual teto será aplicado por rating;
* qual o impacto financeiro da política;
* quanto de exposição será liberado em cada grupo de risco;
* como impedir concessões muito altas apenas porque a PD é aceitável.

A nova abordagem deve tratar a política como uma **política de limite por rating**, combinando:

```text
rating interno
+ renda
+ multiplicador de renda
+ teto máximo por rating
+ capacidade de pagamento
+ fatores de ajuste de limite
+ decisão de concessão
+ impacto financeiro
```

O objetivo final do notebook 06 é propor uma política inicial, baseada em evidência histórica, que responda:

* para quais clientes o crédito pode ser oferecido;
* qual valor máximo pode ser concedido;
* qual impacto financeiro a política gera;
* qual risco esperado/observado dos clientes aprovados;
* quais clientes devem ir para análise manual;
* quais clientes devem ser recusados.

---

## 2. Enquadramento do problema

O case trata de uma política de concessão para produto de empréstimo bancário parcelado.

A base sugere cliente pessoa física com relacionamento bancário, pois contém:

* renda mensal;
* data de nascimento;
* escolaridade;
* data de abertura de conta;
* tempo de relacionamento;
* indicador de cliente ativo;
* restritivos financeiros;
* dados da operação concedida.

A política **não deve** ser tratada como:

* política PJ;
* abertura de conta;
* financiamento com garantia conhecida;
* política completa de perda esperada com LGD/EAD;
* política baseada em bureau externo completo;
* política com histórico de propostas recusadas.

A base não informa garantia, colateral, LGD, EAD formal ou propostas recusadas. Portanto, a política deve reconhecer essas limitações explicitamente.

---

## 3. Papel do score de PD

O `pd_score` não é a política.

Ele é uma camada de mensuração de risco, criada no notebook 04 e aplicada no notebook 05.

O papel correto do `pd_score` é:

```text
pd_score → rating interno → insumo da política
```

A política deve usar o rating para definir:

* elegibilidade;
* multiplicador de renda;
* teto de limite;
* necessidade de análise manual;
* recusa;
* intensidade dos ajustes por restritivos e relacionamento.

O target de inadimplência em 12 meses (`target_inadimplente_12m`) deve ser usado apenas para backtest, nunca como variável de decisão.

---

## 4. Entrada principal

O notebook 06 deve partir da base:

```text
data/processed/base_politica_validacao_com_score.parquet
```

Essa base vem do notebook 05 e deve conter a safra de validação enriquecida com:

* score de PD;
* faixa de risco/rating;
* variáveis financeiras;
* variáveis de relacionamento;
* variáveis de restritivos;
* target apenas para avaliação histórica.

Se o arquivo não existir, verificar se há base equivalente em:

```text
data/processed/
```

Mas o notebook 06 não deve recriar target nem retreinar modelo.

---

## 5. O que não pode ser alterado

Não alterar:

```text
data/raw/*
notebooks/00_validacao_ambiente.ipynb
notebooks/01_diagnostico_bases.ipynb
notebooks/02_target_inadimplencia_12m.ipynb
notebooks/03_eda_credito.ipynb
notebooks/04_modelagem_pd.ipynb
notebooks/05_politica_concessao_credito.ipynb
```

O notebook 06 pode ser refeito, pois é a camada de política e recomendação.

---

## 6. Caracterização obrigatória do público

Antes de propor política, o notebook deve mostrar quem é o público.

Criar tabelas executivas com:

### 6.1 Faixa de renda vs rating

Tabela:

```text
faixa_renda × faixa_risco
recheio: quantidade de clientes
```

Objetivo:

* mostrar concentração dos clientes por renda e risco;
* evidenciar se há público de baixa PD com renda relevante;
* apoiar a definição de multiplicadores e tetos.

### 6.2 Rating vs tempo de relacionamento

Tabela:

```text
faixa_risco × classe_tempo_relacionamento
recheio: quantidade de clientes
```

Objetivo:

* mostrar se os melhores ratings também têm relacionamento mais longo;
* sustentar a política de alavancagem para clientes com histórico.

### 6.3 Rating vs PD e bad rate

Tabela:

```text
faixa_risco
qtd_clientes
pd_min
pd_media
pd_max
bad_rate_observado
```

Objetivo:

* mostrar que o rating ordena risco;
* justificar os intervalos de PD;
* provar monotonicidade entre rating e inadimplência observada.

### 6.4 Rating vs exposição e capacidade

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

Objetivo:

* explicar quanto a carteira movimenta em cada rating;
* mostrar onde existe oportunidade de alavancagem;
* mostrar onde existe necessidade de restrição.

### 6.5 Rating vs restritivos

Tabela:

```text
faixa_risco × classe_restritivo
recheio: quantidade de clientes
```

Objetivo:

* identificar concentração de restritivos por rating;
* apoiar fatores de ajuste de limite.

---

## 7. Faixas auxiliares

### 7.1 Faixa de renda

Criar faixas de renda interpretáveis.

Sugestão:

```text
Até R$ 2 mil
R$ 2 mil a R$ 5 mil
R$ 5 mil a R$ 10 mil
R$ 10 mil a R$ 20 mil
Acima de R$ 20 mil
```

Se a distribuição da base exigir, ajustar por percentis, documentando a decisão.

### 7.2 Classe de tempo de relacionamento

Criar:

```text
curto: tempo_conta_anos < 1
medio: 1 <= tempo_conta_anos < 3
longo: tempo_conta_anos >= 3
```

### 7.3 Classe de restritivo

Criar:

```text
sem_restritivo: restritivos_sobre_renda <= 0 ou nulo
ate_2pct:       0 < restritivos_sobre_renda <= 0.02
ate_5pct:       0.02 < restritivos_sobre_renda <= 0.05
ate_10pct:      0.05 < restritivos_sobre_renda <= 0.10
acima_10pct:    restritivos_sobre_renda > 0.10
```

---

## 8. Estrutura da política de limite

A política deve calcular o limite do cliente em etapas.

### 8.1 Limite por multiplicador de renda

```text
limite_multiplicador =
    valor_renda × multiplicador_rating
```

O multiplicador deve ser maior para ratings melhores e menor para ratings piores.

Exemplo conceitual:

```text
Rating A: renda × 4,0
Rating B: renda × 3,0
Rating C: renda × 2,0
Rating D: renda × 1,0 ou mesa
Rating E: recusa
```

Os valores finais devem ser calibrados com a base.

### 8.2 Limite por capacidade de pagamento

Calcular parcela máxima:

```text
parcela_maxima =
    valor_renda × pct_max_comprometimento_rating
```

Converter para valor presente usando taxa e prazo da operação:

```text
limite_capacidade =
    parcela_maxima × ((1 - (1 + taxa)^(-prazo)) / taxa)
```

Tratamentos técnicos:

```text
valor_renda <= 0 → limite zero
valor_taxa <= 0 → usar taxa técnica mínima, como 0.0001
valor_prazo <= 0 → usar prazo mínimo 1
limite negativo → truncar em zero
```

### 8.3 Teto por rating

A política precisa de teto.

O teto evita situações absurdas, como aprovar valores muito altos apenas porque a PD está dentro de uma faixa aceitável.

O teto deve ser calculado ou calibrado a partir da própria base.

Sugestões defensáveis:

* usar percentis históricos de `valor_emprestado` por rating;
* usar percentis globais de exposição;
* definir teto crescente por rating, sempre documentando a regra.

Exemplo conceitual:

```text
Rating A: teto maior
Rating B: teto intermediário
Rating C: teto menor
Rating D: teto muito reduzido ou mesa
Rating E: sem limite automático
```

Não usar teto infinito.

### 8.4 Limite bruto

```text
limite_bruto =
    mínimo entre:
    - limite_multiplicador
    - limite_capacidade
    - teto_rating
```

### 8.5 Fatores de ajuste de limite

Substituir a linguagem de “redutores” por:

```text
fatores de ajuste de limite
```

Ajustes possíveis:

```text
limite_final =
    limite_bruto
    × fator_restritivo
    × fator_cliente_ativo
    × fator_tempo_relacionamento
```

Esses fatores devem ser menores ou iguais a 1, salvo decisão explícita e muito bem documentada.

Não criar bônus agressivo apenas por tempo de conta.

---

## 9. Decisão da política

Usar exatamente as categorias:

```text
Aprovar valor solicitado
Aprovar valor reduzido
Análise manual
Recusar
```

### 9.1 Aprovar valor solicitado

Condição conceitual:

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

### 9.2 Aprovar valor reduzido

Condição conceitual:

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

### 9.3 Análise manual

Usar para:

* rating D, conforme cenário;
* restritivo relevante;
* cliente inativo com risco intermediário;
* proposta muito acima do limite calculado;
* caso próximo ao teto;
* situações nas quais a base não permite decisão automática segura.

Valor aprovado automático:

```text
valor_aprovado = 0
```

### 9.4 Recusar

Usar para:

* rating E;
* renda inválida;
* limite final abaixo do mínimo operacional;
* restritivo severo conforme cenário;
* risco extremo.

Valor aprovado automático:

```text
valor_aprovado = 0
```

---

## 10. Cenários de apetite de risco

Os cenários devem ser tratados como simulações de apetite de risco, não como três políticas finais.

### 10.1 Conservador

Objetivo:

* proteger carteira;
* reduzir risco dos aprovados;
* priorizar rating A e B;
* restringir rating C;
* enviar D para análise manual;
* recusar E.

Características:

```text
multiplicadores menores
tetos menores
comprometimento máximo menor
fatores de ajuste mais severos
mais análise manual
menor exposição aprovada
```

### 10.2 Base / Equilibrado

Objetivo:

* equilibrar aprovação, exposição e risco;
* alavancar bons clientes;
* preservar controle em risco médio;
* deixar risco alto para mesa.

Características:

```text
multiplicadores intermediários
tetos intermediários
comprometimento máximo moderado
fatores de ajuste moderados
```

### 10.3 Expansivo controlado

Objetivo:

* testar maior alavancagem nos melhores ratings;
* ampliar exposição em A e B;
* aceitar algum aumento de risco em C;
* manter D controlado e E recusado.

Características:

```text
multiplicadores maiores para A/B
tetos maiores para A/B
comprometimento máximo maior
fatores de ajuste menos severos
sem eliminar governança de restritivos
```

Mesmo no cenário expansivo, deve existir teto.

---

## 11. Métricas obrigatórias por cenário

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

Aprovação automática total deve somar:

```text
Aprovar valor solicitado + Aprovar valor reduzido
```

---

## 12. Métricas obrigatórias por rating

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

Essa tabela será essencial para responder:

* quanto dinheiro é liberado para rating A;
* quanto dinheiro é liberado para rating B;
* quanto risco está sendo aceito;
* onde a política restringe.

---

## 13. Métricas obrigatórias por decisão

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

## 14. Gráficos recomendados

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

Os gráficos devem seguir o padrão visual do projeto.

---

## 15. Saídas esperadas

Salvar:

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
```

---

## 16. Critério de recomendação

A recomendação não deve ser escolhida previamente.

Criar score gerencial como apoio de decisão, considerando:

* controle de inadimplência dos aprovados;
* aprovação automática;
* exposição aprovada;
* eficiência operacional;
* concentração de risco por rating;
* volume em análise manual.

Sugestão de pesos iniciais:

```text
controle de inadimplência: 40%
aprovação automática: 25%
exposição aprovada: 25%
eficiência operacional: 10%
```

O score gerencial é apenas apoio. A escolha final deve ser justificada em texto.

Não recomendar automaticamente o cenário expansivo apenas porque aprova mais.

---

## 17. Política final proposta

Após escolher o cenário recomendado, gerar tabela com:

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

Essa tabela será a principal saída gerencial.

---

## 18. Limitações obrigatórias

Registrar no notebook:

* base contém apenas operações concedidas;
* ausência de propostas recusadas;
* ausência de garantia ou colateral;
* ausência de LGD;
* ausência de EAD formal;
* ausência de score externo completo;
* ausência de histórico anterior detalhado de atraso;
* simulação histórica não é política definitiva de produção;
* parâmetros precisam ser validados com a área de política de crédito;
* variáveis como idade e escolaridade exigem governança/fairness;
* monitoramento por safra é obrigatório.

---

## 19. Monitoramento recomendado

Sugerir monitoramento periódico de:

* taxa de aprovação;
* taxa de aprovação reduzida;
* taxa de análise manual;
* taxa de recusa;
* valor aprovado;
* exposição aprovada por rating;
* bad rate por safra;
* bad rate por rating;
* PD média dos aprovados;
* AUC;
* KS;
* PSI do score;
* PSI das principais variáveis;
* concentração de decisão por grupos;
* perda observada, se LGD/EAD forem disponibilizados.

---

## 20. Frase de fechamento esperada

A política recomendada deve ser apresentada como uma política inicial baseada em evidência histórica.

A conclusão deve deixar claro:

```text
O score de PD é uma camada de mensuração de risco.
A política de concessão combina rating, renda, teto de limite, capacidade de pagamento, restritivos e relacionamento.
A recomendação final deve ser validada com a área de política de crédito antes de qualquer uso produtivo.
```
