# Concessao de Credito

Projeto de modelagem de risco de credito para apoiar uma politica de concessao
de emprestimos em um banco ficticio.

## Objetivo

Sugerir uma regra de concessao de credito que defina:

1. Quais clientes podem receber o produto de emprestimo;
2. Qual valor maximo pode ser concedido para cada cliente;
3. Como equilibrar risco de inadimplencia, capacidade de pagamento e retorno.

## Problema de negocio

O projeto simula o desafio de uma instituicao financeira que precisa transformar
historico de emprestimos e comportamento de inadimplencia em uma politica objetiva
de concessao de credito.

A solucao proposta combina:

* estimativa de probabilidade de inadimplencia em 12 meses;
* analise de capacidade de pagamento;
* segmentacao de risco;
* definicao de valor maximo recomendado por cliente.

## Bases

As bases devem ser mantidas localmente em `data/raw/`:

* `concessao.csv`
* `inadimplencia.csv`

Os arquivos de dados nao sao versionados no Git.

## Estrutura

* `notebooks/`: analises exploratorias, modelagem e relatorio final.
* `src/`: funcoes reutilizaveis do projeto.
* `outputs/`: tabelas, graficos e modelos gerados.
* `reports/`: materiais finais de apresentacao e relatorio.
* `docs/`: premissas, decisoes tecnicas e politica proposta.
* `references/`: referencias bibliograficas e notas de apoio, sem dados sensiveis.

## Como reproduzir

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
jupyter notebook
```

Rodar os notebooks na ordem:

1. `00_validacao_ambiente.ipynb`
2. `01_diagnostico_bases.ipynb`
3. `02_target_inadimplencia_12m.ipynb`
4. `03_eda_credito.ipynb`
5. `04_modelagem_pd.ipynb`
6. `05_politica_concessao.ipynb`
7. `99_relatorio_final.ipynb`

## Saidas esperadas

Ao final, o projeto deve gerar:

* diagnostico das bases;
* definicao do target de inadimplencia em 12 meses;
* comparacao entre modelos de credit scoring;
* regra proposta de aprovacao, recusa e valor maximo;
* graficos e tabelas de apoio;
* relatorio tecnico e apresentacao gerencial.
