# Contexto de negócio da política de concessão de crédito

## 1. Objetivo do documento

Este documento consolida o contexto de negócio que deve orientar a construção do notebook `06_cenarios_politica_recomendacao.ipynb`.

A finalidade é garantir que a política de crédito seja construída de forma coerente com o produto, o público, as variáveis disponíveis e as limitações do case.

O foco não é apenas criar uma regra estatística, mas transformar o score de risco em uma política de concessão defensável, capaz de responder:

* quais clientes podem receber crédito;
* qual valor máximo pode ser concedido;
* quais clientes devem ir para análise manual;
* quais clientes devem ser recusados;
* qual o trade-off entre inadimplência, aprovação e exposição financeira.

---

## 2. Enquadramento do produto

O case trata de uma política de concessão para um produto de empréstimo.

A base não traz uma descrição comercial detalhada do produto, mas as variáveis disponíveis indicam que se trata de uma operação de crédito parcelado, com:

* valor emprestado;
* valor da parcela;
* prazo;
* taxa;
* renda;
* dados cadastrais do cliente;
* restritivos financeiros;
* histórico posterior de inadimplência.

Portanto, a política deve ser tratada como uma política de concessão de empréstimo bancário parcelado.

---

## 3. Público da política

A base sugere um público de pessoa física com relacionamento bancário.

Essa leitura vem das variáveis disponíveis:

* data de nascimento;
* idade na concessão;
* escolaridade;
* renda;
* data de abertura de conta;
* tempo de conta;
* indicador de cliente ativo;
* restritivos financeiros.

Não há variáveis típicas de pessoa jurídica, como:

* faturamento da empresa;
* CNPJ;
* CNAE;
* ramo de atividade;
* segmento econômico;
* porte da empresa;
* sócios;
* balanço;
* DRE;
* fluxo de caixa empresarial.

Logo, a política não deve ser construída como política PJ.

---

## 4. O que esta política não é

Esta política não deve ser interpretada como:

1. política de abertura de conta;
2. política cadastral pura;
3. política PJ;
4. política de financiamento com garantia explicitamente conhecida;
5. política completa de perda esperada com PD, LGD e EAD formais;
6. política baseada em bureau completo;
7. política baseada em histórico transacional detalhado.

A política é uma política de concessão de empréstimo para cliente com relacionamento bancário, usando os dados disponíveis no momento da proposta.

---

## 5. Garantia e colateral

A base não contém variável explícita de garantia, colateral, avalista, bem financiado, alienação fiduciária ou recuperação esperada.

Por isso, não devemos afirmar que o produto é necessariamente sem garantia.

A formulação correta é:

> A base não informa garantia. Portanto, a política foi construída sem considerar mitigadores formais de perda, usando risco estimado, capacidade de pagamento, restritivos e relacionamento como principais critérios de decisão.

Na prática, isso justifica uma política mais conservadora, especialmente para faixas de maior risco.

---

## 6. Score, rating e PD

A base original não continha um score pronto de crédito.

O score foi construído no projeto por modelagem supervisionada.

O fluxo foi:

1. cruzamento da base de concessão com a base de inadimplência;
2. criação do target de inadimplência em 12 meses;
3. treinamento de modelos de PD;
4. escolha do modelo candidato;
5. aplicação do modelo na safra de validação;
6. criação da variável `pd_score`.

O `pd_score` representa a probabilidade estimada de inadimplência em até 12 meses após a concessão.

No notebook de política, esse score passa a funcionar como um rating interno de risco.

---

## 7. Diferença entre modelo e política

O modelo responde:

> Qual é a probabilidade estimada de inadimplência desta proposta?

A política responde:

> O que a instituição deve fazer com essa proposta dado o risco estimado, a capacidade de pagamento, os restritivos e o relacionamento do cliente?

Portanto, o modelo não é a política.

A política usa o modelo como uma camada objetiva de mensuração de risco.

---

## 8. Variáveis disponíveis para política

As principais variáveis disponíveis são:

### Risco estimado

* `pd_score`
* `faixa_risco`

### Capacidade de pagamento

* `valor_renda`
* `valor_parcela`
* `comprometimento_renda`

### Restritivos financeiros

* `valor_restritivos`
* `restritivos_sobre_renda`

### Relacionamento

* `flag_cliente_ativo`
* `tempo_conta_anos`
* `data_abertura_conta`

### Características da operação

* `valor_emprestado`
* `valor_taxa`
* `valor_prazo`

### Perfil cadastral

* `idade_concessao`
* `cat_escolaridade`

### Avaliação histórica

* `target_inadimplente_12m`

A variável `target_inadimplente_12m` deve ser usada apenas para backtest e avaliação da política. Ela não pode ser usada como variável de decisão.

---

## 9. Variáveis típicas de política que não estão disponíveis

Algumas variáveis comuns em políticas reais não aparecem na base.

### Para pessoa jurídica

* faturamento;
* ramo de atividade;
* CNAE;
* porte;
* fluxo de caixa;
* balanço;
* sócios;
* tempo de constituição da empresa.

### Para pessoa física

* score externo de bureau;
* histórico detalhado de atrasos anteriores;
* quantidade de contratos ativos;
* saldo em conta;
* uso de cartão;
* comprometimento total no sistema financeiro;
* segmento bancário formal;
* estabilidade profissional;
* patrimônio.

### Para a operação

* garantia;
* colateral;
* LGD;
* EAD regulatório;
* receita esperada líquida;
* custo de funding;
* spread líquido;
* recuperação pós-default.

Essas ausências precisam ser documentadas como limitações e não devem ser preenchidas por suposição.

---

## 10. Lógica de política recomendada

A política deve ter duas camadas principais.

### Camada 1 — risco

Usar `pd_score` para classificar a proposta em faixas de risco:

* A - Baixo risco;
* B - Médio-baixo risco;
* C - Médio risco;
* D - Alto risco;
* E - Muito alto risco.

Essa faixa define o apetite inicial de concessão.

### Camada 2 — capacidade de pagamento

Calcular uma parcela máxima aceitável:

```text
parcela_maxima =
    renda
    × percentual_maximo_parcela_renda_por_faixa
    × redutor_restritivo
    × redutor_relacionamento
    × redutor_tempo_conta
```

Depois, converter a parcela máxima em valor máximo sugerido usando taxa e prazo.

---

## 11. Decisões possíveis

A política deve classificar cada proposta em uma das seguintes decisões:

1. Aprovar valor solicitado;
2. Aprovar valor reduzido;
3. Análise manual;
4. Recusar.

Essa estrutura é mais realista do que uma regra binária simples de aprovação ou recusa.

A faixa intermediária de análise manual é importante porque permite tratar casos que não devem ser aprovados automaticamente, mas também não precisam ser recusados de forma automática.

---

## 12. Papel da análise manual

A análise manual deve concentrar propostas com risco elevado ou incerteza relevante, especialmente quando:

* a PD é alta, mas não extrema;
* existem restritivos relevantes;
* o cliente está inativo;
* o tempo de relacionamento é baixo;
* o valor solicitado é alto em relação à renda;
* a proposta fica próxima dos limites de aprovação.

A análise manual funciona como uma camada de governança e exceção.

---

## 13. Cenários de apetite de risco

A política final não deve ser apresentada como uma regra única sem comparação.

Devem ser simulados pelo menos três cenários:

### Conservador

Prioriza redução de inadimplência e proteção da exposição.

Características:

* menor percentual máximo de parcela/renda;
* redutores mais fortes;
* alto risco direcionado para análise manual;
* muito alto risco recusado;
* menor exposição aprovada.

### Equilibrado

Busca equilíbrio entre aprovação, inadimplência e exposição.

Características:

* percentuais intermediários de parcela/renda;
* redutores moderados;
* preserva aprovação em baixo e médio risco;
* mantém análise manual para alto risco;
* tende a ser o cenário recomendado se mantiver inadimplência controlada.

### Expansivo

Prioriza crescimento de concessão.

Características:

* maior percentual máximo de parcela/renda;
* redutores mais leves;
* pode aprovar parte de alto risco com limite reduzido;
* mantém recusa para risco extremo;
* aceita maior inadimplência esperada.

---

## 14. Métricas para escolher a política

A escolha do cenário recomendado deve considerar:

* taxa de aprovação automática;
* taxa de análise manual;
* taxa de recusa;
* inadimplência observada dos aprovados;
* PD média dos aprovados;
* exposição original;
* exposição aprovada;
* redução de exposição;
* valor médio aprovado;
* inadimplência por decisão;
* distribuição das decisões por faixa de risco.

Não se deve escolher apenas o cenário com menor inadimplência, pois isso pode gerar uma política excessivamente restritiva.

Também não se deve escolher apenas o cenário com maior aprovação, pois isso pode elevar demais o risco.

A política recomendada deve equilibrar risco, volume e eficiência operacional.

---

## 15. Limitações metodológicas

A simulação deve explicitar estas limitações:

1. a base contém apenas operações historicamente concedidas;
2. não há propostas recusadas;
3. não há garantia ou recuperação;
4. não há LGD ou EAD formal;
5. não há histórico anterior detalhado de atraso;
6. não há score externo de bureau;
7. não há dados transacionais completos;
8. idade e escolaridade exigem atenção de governança e fairness;
9. a política foi validada em backtest histórico, não em experimento real;
10. a política precisaria ser calibrada com apetite de risco da instituição.

---

## 16. Perguntas para validação com área de política de crédito

Antes de levar a política para produção, validar com especialistas:

1. O produto é com ou sem garantia?
2. Existe valor mínimo operacional para concessão?
3. Existe teto regulatório ou interno de comprometimento de renda?
4. Qual é o apetite de risco máximo aceitável?
5. Qual bad rate esperado para carteira aprovada?
6. A instituição prefere reduzir perda ou preservar volume?
7. A análise manual tem capacidade operacional para absorver casos intermediários?
8. Existe política específica para cliente inativo?
9. Restritivos devem gerar recusa automática ou apenas redução de limite?
10. Quais variáveis não disponíveis seriam obrigatórias em produção?
11. A idade e a escolaridade podem ser usadas diretamente ou apenas em análise técnica?
12. Como monitorar a política ao longo do tempo?

---

## 17. Frase executiva da política

A política proposta usa o score interno de PD como rating de risco e combina essa informação com capacidade de pagamento, restritivos financeiros e relacionamento com o banco para definir aprovação, aprovação com valor reduzido, análise manual ou recusa.

Como a base não informa garantias, recuperação ou propostas recusadas, a recomendação deve ser tratada como uma política inicial simulada, sujeita à validação da área de crédito e calibração conforme o apetite de risco da instituição.
