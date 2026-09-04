# Instruções para IA — Geração do notebook 06

## 1. Papel da IA

Atue como cientista de dados sênior especializado em:

* risco de crédito;
* concessão de crédito;
* política de crédito;
* modelagem de PD;
* score/rating;
* simulação de cenários;
* explicabilidade;
* governança de modelos.

Você deve implementar a próxima etapa do projeto de forma segura, sem alterar o que já foi feito.

---

## 2. Escopo da tarefa

Criar o notebook:

```text
notebooks/06_cenarios_politica_recomendacao.ipynb
```

Também respeitar os documentos:

```text
docs/06_contexto_politica_credito.md
playbooks/06_metodologia_cenarios_politica.md
```

O notebook deve comparar cenários de política de crédito e recomendar uma política final com base no trade-off entre inadimplência, aprovação e exposição financeira.

---

## 3. Arquivos que podem ser criados

Você pode criar:

```text
notebooks/06_cenarios_politica_recomendacao.ipynb
outputs/tables/*.csv
outputs/figures/*.html
data/processed/base_simulacao_cenarios_politica.parquet
```

Você pode criar ou atualizar somente se necessário:

```text
docs/06_contexto_politica_credito.md
playbooks/06_metodologia_cenarios_politica.md
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
```

Se precisar reaproveitar código desses notebooks, leia e copie a lógica para o notebook 06, sem modificar os arquivos anteriores.

---

## 5. Contexto obrigatório

A política é para concessão de empréstimo bancário parcelado.

A base sugere cliente pessoa física/correntista ou com relacionamento bancário.

Não tratar como política PJ.

Não criar variáveis de PJ, como:

* faturamento;
* CNAE;
* ramo de atividade;
* porte;
* setor econômico;
* balanço;
* fluxo de caixa empresarial.

Não tratar como abertura de conta.

Não assumir existência de garantia.

A base não possui score externo. O score interno foi criado por modelagem e aparece como `pd_score`.

---

## 6. Fluxo já realizado no projeto

O projeto seguiu esta sequência:

```text
00 — validação de ambiente
01 — diagnóstico das bases
02 — criação do target de inadimplência 12m
03 — análise exploratória
04 — modelagem de PD
05 — política inicial e interpretação do modelo
06 — cenários de política e recomendação final
```

O notebook 06 deve começar de onde o notebook 05 parou.

---

## 7. Entrada principal

Ler a base:

```text
data/processed/base_politica_validacao_com_score.parquet
```

Se não existir, procurar base equivalente em `data/processed`.

Validar as colunas obrigatórias:

```text
id_operacao
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

Se alguma coluna obrigatória estiver ausente, interromper com erro claro listando as colunas faltantes.

---

## 8. Padrão visual

Reutilizar o padrão visual dos notebooks anteriores.

Se existirem funções como:

```python
aplicar_layout
salvar_figura
```

reutilizar.

Se não existirem no notebook 06, criar versões compatíveis.

Usar Plotly.

Não usar Seaborn.

Usar verde como cor principal do projeto quando houver necessidade de especificar cor.

Os gráficos devem ter:

* título executivo;
* subtítulo;
* eixo nomeado;
* margem suficiente para não cortar rótulos;
* salvamento em HTML.

---

## 9. Estrutura obrigatória do notebook

Criar o notebook com esta estrutura:

```markdown
# 06 — Cenários de política e recomendação final

## 1. Contexto de negócio e premissas da política
## 2. Setup e leitura da base com score
## 3. Contrato de dados e validações iniciais
## 4. Diagnóstico da política inicial
## 5. Variáveis disponíveis e limitações da política
## 6. Definição dos cenários de política
## 7. Funções de simulação da política
## 8. Simulação dos cenários
## 9. Comparação executiva dos cenários
## 10. Escolha do cenário recomendado
## 11. Política final proposta
## 12. Limitações, riscos e próximos passos
## 13. Conclusão do notebook
```

---

## 10. Cenários obrigatórios

Criar pelo menos três cenários:

1. Conservador;
2. Equilibrado;
3. Expansivo.

Cada cenário deve parametrizar:

* percentual máximo de parcela/renda por faixa de risco;
* redutores por restritivos;
* redutor por cliente inativo;
* redutor por tempo de relacionamento;
* tratamento da faixa D;
* tratamento da faixa E;
* valor mínimo operacional para aprovação reduzida.

---

## 11. Funções obrigatórias

Implementar funções reutilizáveis:

```python
classificar_restritivo_sobre_renda
classificar_tempo_relacionamento
calcular_valor_presente_parcelas
simular_cenario_politica
calcular_resumo_cenario
resumir_decisoes_por_cenario
resumir_faixas_por_cenario
```

As funções devem receber parâmetros explícitos e evitar dependência desnecessária de variáveis globais.

---

## 12. Fórmula da política

Usar a fórmula:

```text
parcela_maxima =
    valor_renda
    × pct_max_parcela_renda
    × redutor_restritivo
    × redutor_cliente_ativo
    × redutor_tempo_conta
```

Converter em valor máximo sugerido:

```text
valor_maximo_sugerido =
    parcela_maxima × ((1 - (1 + taxa)^(-prazo)) / taxa)
```

Depois definir:

```text
valor_aprovado =
    min(valor_emprestado, valor_maximo_sugerido)
```

Se a decisão for recusa ou análise manual, o valor aprovado automático deve ser zero.

---

## 13. Decisões obrigatórias

Usar exatamente estas decisões:

```text
Aprovar valor solicitado
Aprovar valor reduzido
Análise manual
Recusar
```

Evitar criar nomes alternativos para não bagunçar o resumo.

---

## 14. Métricas obrigatórias

Para cada cenário, calcular:

* quantidade de operações;
* taxa histórica de inadimplência;
* taxa aprovação automática;
* taxa análise manual;
* taxa recusa;
* inadimplência dos aprovados;
* PD média dos aprovados;
* valor original total;
* valor aprovado total;
* percentual de exposição aprovada;
* redução de exposição;
* valor médio aprovado.

---

## 15. Gráficos obrigatórios

Gerar e salvar:

1. trade-off aprovação versus inadimplência dos aprovados;
2. taxa de aprovação, análise manual e recusa por cenário;
3. inadimplência dos aprovados por cenário;
4. exposição aprovada por cenário;
5. decisões por faixa de risco;
6. valor original versus valor aprovado.

---

## 16. Escolha da política recomendada

Criar uma tabela de score gerencial.

Sugestão de pesos:

```text
40% controle de inadimplência
30% preservação da aprovação
20% preservação da exposição
10% eficiência operacional
```

A escolha deve ser baseada nos resultados.

Não assumir previamente que o cenário equilibrado é o melhor.

Se o cenário recomendado não for o equilibrado, explicar por quê.

---

## 17. Política final

Gerar uma tabela final com:

* cenário recomendado;
* faixa de risco;
* intervalo de PD;
* ação principal;
* percentual máximo de parcela/renda;
* tratamento de restritivos;
* tratamento de cliente inativo;
* tratamento de tempo de conta;
* regra de limite;
* observação de negócio.

---

## 18. Limitações obrigatórias

Registrar:

* base apenas com operações concedidas;
* ausência de propostas recusadas;
* ausência de garantia;
* ausência de LGD;
* ausência de EAD formal;
* ausência de score externo;
* ausência de histórico anterior detalhado de atraso;
* necessidade de validação com política de crédito;
* necessidade de monitoramento de safra;
* necessidade de governança para variáveis como idade e escolaridade.

---

## 19. Saídas esperadas

Salvar:

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

## 20. Qualidade esperada

O notebook deve ser explicável para três públicos:

1. cientista de dados;
2. pessoa de política de crédito;
3. avaliador executivo do case.

A narrativa deve deixar claro:

* o score foi criado por modelagem;
* a política usa o score como rating interno;
* a decisão não é binária;
* o valor máximo é definido por capacidade de pagamento;
* restritivos e relacionamento ajustam o limite;
* o cenário recomendado depende do apetite de risco;
* as limitações são reconhecidas.

---

## 21. Antes de implementar

Antes de criar o notebook, faça um breve diagnóstico textual:

* quais arquivos serão lidos;
* quais funções serão reaproveitadas;
* quais outputs serão criados;
* quais cuidados serão tomados para não alterar notebooks anteriores.

Depois implemente.
