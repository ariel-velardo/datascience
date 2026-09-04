# Visão Computacional Aplicada à Tomografia Hepática

**Estudo exploratório para classificação de esteatose hepática em imagens de tomografia computadorizada**

Projeto desenvolvido para a disciplina **MAQ-020 — Aprendizado de Máquina**, no contexto do trabalho **Imagens Médicas Agêntico**.

> **Aviso importante:** este estudo é exploratório e **não validado clinicamente**.  
> Os resultados não devem ser interpretados como diagnóstico automático, ferramenta clínica ou recomendação médica.

---

## Integrantes

- Ariel Velardo
- Alexandre Suehara
- André de Moricz
- Fernando Maciel
- Celso Pochini
- Walkiria Hueb

---

## Objetivo do trabalho

O objetivo deste projeto é avaliar se imagens de tomografia hepática contêm sinal computacional inicial capaz de diferenciar exames classificados como:

- `Healthy`
- `Hepatic Steatosis`

A proposta não é desenvolver um sistema diagnóstico, mas investigar, de forma exploratória, se há evidência computacional inicial e comportamento visual plausível para justificar novos experimentos.

### Pergunta central

> Existe evidência computacional inicial e comportamento visual plausível para justificar novos experimentos com classificação de esteatose hepática em imagens de tomografia?

---

## Objetivos técnicos

O projeto foi estruturado para construir um pipeline reprodutível envolvendo:

- indexação do dataset;
- auditoria de qualidade das imagens;
- análise exploratória;
- construção de splits por grupo;
- prevenção de vazamento de dados;
- baseline estatístico;
- baseline CNN 2D;
- avaliação por slice e por grupo;
- análise visual de erros;
- interpretabilidade com Grad-CAM;
- experimentos com ROI hepática aproximada;
- experimento com Multiple Instance Learning;
- bootstrap por grupo;
- análise de calibração;
- seleção de checkpoint por métrica de grupo;
- testes automatizados;
- documentação metodológica e auditoria técnica.

---

## Dados disponíveis

O dataset utilizado contém imagens JPEG de tomografia hepática organizadas em duas classes:

- `Healthy`
- `Hepatic_Steatosis`

Cada arquivo representa um **slice**, isto é, um corte individual de tomografia.

Como vários slices podem pertencer ao mesmo exame, foi criado o identificador:

```text
inferred_group_id
```

Esse identificador agrupa slices associados ao mesmo exame inferido.

### Resumo do conjunto atual

| Informação | Quantidade |
|---|---:|
| Total de slices | 3.557 |
| Total de grupos/exames inferidos | 225 |
| Grupos de treino | 157 |
| Grupos de validação | 33 |
| Grupos de teste | 35 |

### Distribuição por split

| Split | Healthy | Hepatic Steatosis | Total de grupos |
|---|---:|---:|---:|
| Treino | 53 | 104 | 157 |
| Validação | 11 | 22 | 33 |
| Teste | 12 | 23 | 35 |

---

## Divisão dos dados e prevenção de vazamento

A divisão entre treino, validação e teste foi feita por `inferred_group_id`, e não por slice individual.

Isso garante que slices pertencentes ao mesmo exame não sejam distribuídos entre conjuntos diferentes.

O script:

```text
scripts/verify_group_split_integrity.py
```

reutiliza as funções de validação do projeto e confirmou:

```text
train-val leakage:  0
train-test leakage: 0
val-test leakage:   0
```

Portanto, nenhum `inferred_group_id` aparece em mais de um split.

Esse cuidado reduz o risco de vazamento de dados e evita uma avaliação artificialmente otimista.

---

## Estrutura do repositório

| Pasta | Descrição |
|---|---|
| `configs/` | Arquivos de configuração do projeto. |
| `data/` | Dados locais e artefatos intermediários não versionados. |
| `docs/` | Documentação técnica, metodológica e auditorias. |
| `models/` | Checkpoints e modelos locais não versionados. |
| `notebooks/` | Notebooks numerados do projeto. |
| `reports/figures/` | Figuras e visualizações geradas. |
| `reports/tables/` | Métricas, predições e tabelas de resultados. |
| `scripts/` | Scripts executáveis do pipeline. |
| `src/liverct/` | Código-fonte modular do projeto. |
| `tests/` | Testes automatizados. |

---

## Notebooks do projeto

| Notebook | Descrição |
|---|---|
| `01_metodologia_dataset_e_splits.ipynb` | Documenta o dataset, o conceito de slice/grupo, o `inferred_group_id` e o split por grupo. |
| `02_auditoria_qualidade_imagens.ipynb` | Audita formatos, dimensões, legibilidade, duplicatas e limitações das imagens JPEG. |
| `03_eda_visual_e_tecnica.ipynb` | Apresenta a EDA visual e técnica, com distribuições por classe, grupo, split e intensidade de pixels. |
| `04_baseline_estatistico_controle.ipynb` | Documenta o baseline estatístico de controle anterior à CNN. |
| `05_baseline_cnn_2d.ipynb` | Registra o primeiro baseline CNN 2D e suas métricas por slice e por grupo. |
| `06_analise_visual_erros.ipynb` | Organiza falsos positivos, falsos negativos, verdadeiros positivos e verdadeiros negativos para inspeção visual. |
| `07_gradcam_interpretabilidade.ipynb` | Apresenta mapas Grad-CAM para investigar quais regiões influenciaram as decisões da CNN. |
| `08_experimentos_roi_hepatica.ipynb` | Compara imagem inteira, ROI hepática aproximada e máscara heurística. |
| `09_mil_por_grupo.ipynb` | Implementa e documenta um experimento de Multiple Instance Learning por `inferred_group_id`. |

Veja também:

```text
docs/mapa_notebooks_do_projeto.md
```

---

## Metodologia geral

O pipeline principal segue as etapas:

```text
Imagens JPEG
    ↓
Indexação
    ↓
Auditoria e EDA
    ↓
Split por inferred_group_id
    ↓
Baseline estatístico
    ↓
CNN 2D supervisionada
    ↓
Avaliação por slice e por grupo
    ↓
Análise de erros
    ↓
Grad-CAM
    ↓
Experimentos com ROI hepática
    ↓
MIL por grupo
    ↓
Bootstrap, calibração e auditoria
```

A avaliação principal é realizada no nível de grupo, pois esse nível se aproxima mais da unidade de exame disponível no dataset.

---

## Baseline estatístico

Foi construído um baseline estatístico utilizando características simples de intensidade das imagens.

O objetivo desse modelo não é competir com arquiteturas profundas, mas fornecer um controle simples e interpretável para comparação.

A auditoria mostrou que, no nível de grupo, a regressão logística apresentou sensibilidade e F1 competitivos em relação à CNN.

Isso reforça a importância de não avaliar os modelos apenas por uma única métrica.

---

## Baseline CNN 2D

O primeiro modelo de visão computacional utiliza uma CNN 2D supervisionada com:

- três blocos convolucionais;
- Batch Normalization;
- ReLU;
- Max Pooling;
- Adaptive Average Pooling;
- Dropout;
- saída binária com `BCEWithLogitsLoss`.

As imagens são convertidas para escala de cinza e normalizadas para o intervalo `[0, 1]`.

### Resultado principal no teste por grupo

| Métrica | Resultado |
|---|---:|
| Balanced Accuracy | 0,8080 |
| Sensibilidade | 0,7826 |
| Especificidade | 0,8333 |
| ROC-AUC | 0,9203 |
| F1 | 0,8372 |

Matriz de confusão no teste por grupo:

|  | Predito Healthy | Predito Steatosis |
|---|---:|---:|
| Real Healthy | 10 | 2 |
| Real Steatosis | 5 | 18 |

Esses resultados são promissores como experimento inicial, mas devem ser interpretados considerando o número reduzido de grupos de teste.

---

## Análise de erros

Foram organizados exemplos de:

- verdadeiro positivo;
- verdadeiro negativo;
- falso positivo;
- falso negativo.

A análise de erros permite investigar se o modelo pode estar utilizando:

- bordas da imagem;
- fundo preto;
- costelas;
- musculatura;
- artefatos JPEG;
- estruturas fora da região hepática.

Essa análise motivou os experimentos posteriores com ROI e Grad-CAM.

---

## Interpretabilidade com Grad-CAM

O Grad-CAM foi utilizado para investigar as regiões da imagem que mais influenciaram as decisões da CNN.

Foram geradas visualizações com:

1. imagem original;
2. mapa de ativação;
3. sobreposição do mapa sobre a imagem.

> O Grad-CAM não valida diagnóstico e não demonstra causalidade.  
> Ele apenas mostra quais regiões influenciaram a decisão computacional do modelo.

A inspeção visual encontrou casos com ativação sobre a região hepática, mas também exemplos com ativação sobre costelas, bordas corporais e regiões externas ao fígado.

Esse resultado reforça o risco de **shortcut learning**, no qual o modelo pode aprender padrões técnicos em vez de sinais anatômicos relevantes.

---

## Experimentos com ROI hepática

Foram comparadas três abordagens:

- imagem inteira;
- recorte de ROI hepática aproximada;
- máscara heurística da região hepática.

### Resultados no teste por grupo

| Modelo | Balanced Accuracy | Sensibilidade | Especificidade | ROC-AUC | F1 |
|---|---:|---:|---:|---:|---:|
| Imagem inteira | 0,8080 | 0,7826 | 0,8333 | 0,9203 | 0,8372 |
| ROI crop aproximada | 0,8496 | 0,7826 | 0,9167 | 0,9529 | 0,8571 |
| ROI mask heurística | 0,8098 | 0,8696 | 0,7500 | 0,9529 | 0,8696 |

A ROI crop apresentou a maior balanced accuracy pontual.

Entretanto, a diferença equivale a apenas um ou dois grupos corretamente classificados a mais, considerando o pequeno conjunto de teste.

---

## Bootstrap por grupo e incerteza

Para avaliar a estabilidade das métricas, foi implementado bootstrap no nível de grupo, com intervalo de confiança de 95%.

Exemplo dos intervalos de balanced accuracy:

| Modelo | Estimativa pontual | IC 95% aproximado |
|---|---:|---:|
| Imagem inteira | 0,808 | 0,664 – 0,938 |
| ROI crop aproximada | 0,850 | 0,725 – 0,958 |
| ROI mask heurística | 0,810 | 0,659 – 0,939 |

Os intervalos apresentam ampla sobreposição.

Portanto, embora a ROI crop tenha a maior estimativa pontual, não há evidência suficiente para afirmar que sua vantagem seja estatisticamente robusta com os 35 grupos de teste disponíveis.

O resultado correto é:

> A ROI crop é uma direção promissora, mas sua superioridade ainda não foi demonstrada de forma estatisticamente estável.

---

## Calibração das probabilidades

Foi implementada uma análise de calibração contendo:

- Brier score;
- reliability tables;
- reliability curves;
- comparação entre probabilidades previstas e frequências observadas.

Os artefatos estão disponíveis em:

```text
reports/tables/calibration_group_metrics.csv
reports/figures/calibration/
```

A calibração mostrou que os modelos MIL apresentam probabilidades muito concentradas próximas de 0,5, comportamento compatível com subtreinamento.

---

## Apêndice experimental: MIL por grupo

O notebook `09_mil_por_grupo.ipynb` testa **Multiple Instance Learning** no nível de `inferred_group_id`.

Nesse experimento, cada grupo é tratado como uma *bag* de slices, e o modelo aprende uma única predição por grupo.

Foram testadas três estratégias:

- `mean_pooling`;
- `max_pooling`;
- `attention_pooling`.

### Resultados no teste por grupo

| Modelo | Balanced Accuracy | Sensibilidade | Especificidade | ROC-AUC | F1 |
|---|---:|---:|---:|---:|---:|
| `mil_mean_pooling` | 0,6087 | 0,2174 | 1,0000 | 0,6304 | 0,3571 |
| `mil_max_pooling` | 0,5054 | 0,2609 | 0,7500 | 0,4710 | 0,3750 |
| `mil_attention_pooling` | 0,5181 | 0,8696 | 0,1667 | 0,6630 | 0,7547 |

### Interpretação

O `mean_pooling` apresentou comportamento conservador, com especificidade alta e sensibilidade baixa.

O `max_pooling` apresentou desempenho próximo do acaso nesta configuração.

O `attention_pooling` alcançou alta sensibilidade, mas com especificidade muito baixa.

A auditoria identificou que o experimento MIL foi treinado com orçamento muito limitado:

- apenas três épocas máximas;
- early stopping entre uma e duas épocas;
- encoder treinado do zero;
- máximo de 12 slices por grupo.

Portanto, os resultados atuais não indicam necessariamente uma limitação da formulação MIL, mas um modelo severamente subtreinado.

O MIL permanece como linha experimental futura.

---

## Seleção de checkpoint por métrica de grupo

O pipeline original selecionava o melhor checkpoint exclusivamente pela menor `val_loss`.

Foi implementado um novo critério configurável baseado em:

1. maior balanced accuracy de validação por grupo;
2. maior F1 de validação por grupo em caso de empate;
3. menor `val_loss` como segundo desempate.

O conjunto de teste não participa da seleção do checkpoint.

### Resultado do experimento

Na validação por grupo:

| Métrica | Checkpoint por `val_loss` | Checkpoint por métrica de grupo |
|---|---:|---:|
| Balanced Accuracy | 0,8182 | 0,9091 |
| Sensibilidade | 0,8182 | 0,8182 |
| Especificidade | 0,8182 | 1,0000 |

No conjunto de teste, porém, os dois checkpoints produziram a mesma matriz de confusão:

```text
TN = 10
FP = 2
FN = 5
TP = 18
```

Assim:

- a seleção por métrica de grupo melhorou os resultados de validação;
- não houve ganho de classificação no conjunto de teste;
- ROC-AUC e Average Precision apresentaram pequena redução;
- os intervalos de confiança continuaram amplamente sobrepostos.

A conclusão correta é:

> O novo critério melhora o alinhamento metodológico entre seleção de checkpoint e avaliação por grupo, mas não demonstrou ganho de generalização no teste atual.

---

## Testes automatizados

O projeto possui testes automatizados para validar:

- integridade dos splits por grupo;
- ausência de vazamento entre treino, validação e teste;
- consistência das bags MIL;
- impossibilidade de misturar labels dentro de uma bag;
- impossibilidade de misturar splits dentro de uma bag;
- regra de seleção de checkpoint;
- desempate por F1 e `val_loss`;
- garantia de que o conjunto de teste não participa da seleção.

Para executar:

```bash
python -m unittest discover -s tests -t . -p "test_*.py"
```

---

## Auditoria técnica

Foi realizada uma auditoria completa do pipeline, cobrindo:

- estrutura do repositório;
- consistência entre documentação e código;
- splits e risco de vazamento;
- métricas;
- CNN;
- Grad-CAM;
- ROI hepática;
- MIL;
- calibração;
- incerteza;
- reprodutibilidade;
- próximos experimentos.

Documentos principais:

```text
docs/auditoria_modelo_estado_da_arte.md
docs/plano_experimentos_proximos_passos.md
reports/tables/auditoria_achados_modelo.csv
reports/tables/plano_experimentos_priorizado.csv
```

A auditoria catalogou 23 achados:

| Severidade | Quantidade |
|---|---:|
| Alta | 11 |
| Média | 9 |
| Baixa | 3 |
| Crítica | 0 |

Nenhum problema crítico de vazamento foi encontrado.

Os principais riscos identificados são metodológicos:

- ausência de validação externa;
- tamanho reduzido do conjunto de teste;
- risco de atalhos visuais;
- ausência de segmentação hepática validada;
- limitações do JPEG;
- ausência de DICOM/NIfTI e valores HU;
- MIL subtreinado;
- incerteza elevada das métricas.

---

## Como executar o projeto

### 1. Criar e ativar o ambiente

No Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configurar o dataset

Crie:

```text
configs/config.local.yaml
```

com o caminho local do dataset.

Dados brutos não devem ser enviados ao GitHub.

### 3. Gerar os índices e splits

```bash
python scripts/build_dataset_index.py
python scripts/build_splits.py
python scripts/verify_group_split_integrity.py
```

### 4. Executar auditoria e EDA

```bash
python scripts/audit_images.py
python scripts/run_visual_eda.py
python scripts/run_statistical_baseline.py
```

### 5. Executar os testes

```bash
python -m unittest discover -s tests -t . -p "test_*.py"
```

### 6. Abrir os notebooks

```bash
jupyter notebook notebooks/
```

---

## Observação sobre dados e arquivos não versionados

Não devem ser adicionados ao GitHub:

```text
data/
models/
.venv/
.git/
__pycache__/
.ipynb_checkpoints/
checkpoints .pt
imagens médicas originais
metadados sensíveis
```

O repositório deve conter apenas:

- código;
- notebooks;
- documentação;
- tabelas de resultados não sensíveis;
- figuras derivadas;
- testes automatizados.

---

## Limitações

As principais limitações atuais são:

- uso de imagens JPEG com compressão;
- ausência de DICOM ou NIfTI;
- ausência de valores HU confiáveis;
- ausência de espaçamento entre slices;
- ausência de metadados clínicos;
- ausência de segmentação hepática validada;
- ROI aproximada e geométrica;
- conjunto de teste com apenas 35 grupos;
- ausência de validação externa;
- ausência de comparação entre diferentes scanners ou instituições;
- ausência de protocolo clínico de uso.

Essas limitações impedem qualquer interpretação clínica forte.

---

## Próximos passos

Os principais próximos passos de pesquisa são:

1. quantificar a fração de Grad-CAM dentro da ROI hepática;
2. executar sanity checks com pesos randomizados;
3. testar aumento de dados leve;
4. recalcular o peso de classe no nível de grupo;
5. avaliar backbone 2D pré-treinado;
6. retreinar MIL com mais épocas e backbone mais forte;
7. avaliar mais slices por bag;
8. incluir features de textura e radiomics;
9. obter segmentação hepática real;
10. testar U-Net ou nnU-Net;
11. utilizar dados DICOM/NIfTI e valores HU;
12. realizar validação externa.

Os passos envolvendo segmentação, modelos 3D, nnU-Net e HU dependem de novos dados ou anotações que não estão disponíveis no dataset atual.

---

## Status atual

O projeto possui uma esteira técnica reprodutível contendo:

- split seguro por grupo;
- auditoria dos dados;
- EDA;
- baseline estatístico;
- CNN 2D;
- avaliação por slice e grupo;
- análise de erros;
- Grad-CAM;
- experimentos com ROI;
- MIL;
- bootstrap;
- calibração;
- seleção de checkpoint por métrica de grupo;
- testes automatizados;
- auditoria técnica;
- documentação dos próximos passos.

Como entrega da disciplina, o trabalho está tecnicamente concluído.

Novos experimentos devem ser tratados como evolução de pesquisa, e não como correções obrigatórias desta versão.

---

## Conclusão

Os experimentos indicam que há sinal computacional inicial nas imagens de tomografia hepática.

Entretanto:

- o conjunto de teste é pequeno;
- os intervalos de confiança são amplos;
- há evidência de ativação fora da região hepática;
- a ROI crop não apresentou superioridade estatisticamente robusta;
- a seleção de checkpoint por métrica de grupo não gerou melhora no teste;
- o experimento MIL está subtreinado;
- não há validação externa ou clínica.

Portanto, os resultados devem ser interpretados como evidência exploratória inicial.

A próxima evolução do projeto deve priorizar:

- melhor localização anatômica;
- segmentação hepática;
- dados em formato médico adequado;
- análise quantitativa da interpretabilidade;
- maior robustez estatística;
- validação externa.

Este trabalho permanece **exploratório** e **não validado clinicamente**.