# Experimento MIL por grupo

## 1. Objetivo

Este experimento implementa uma abordagem de Multiple Instance Learning, ou MIL, para classificar grupos de slices de tomografia hepática.

No projeto, cada imagem JPEG representa um slice. Vários slices pertencem ao mesmo agrupamento técnico, identificado por `inferred_group_id`. No MIL, cada `inferred_group_id` passa a ser tratado como uma bag de slices, e o modelo produz uma predição única por grupo.

O objetivo é comparar a abordagem atual baseada em CNN por slice com uma formulação que aprende diretamente no nível de grupo/exame inferido.

## 2. Por que MIL faz sentido neste projeto

A classificação por slice é simples, mas a unidade metodológica mais importante do projeto é o grupo inferido. Isso acontece porque slices do mesmo grupo são correlacionados e não devem ser separados entre treino, validação e teste.

O MIL é uma formulação natural para esse cenário:

1. cada grupo vira uma bag;
2. cada slice é uma instância dentro da bag;
3. o rótulo é definido no nível da bag;
4. o modelo aprende a agregar informação dos slices para uma predição por grupo.

Essa abordagem reduz a distância entre a forma de treinamento e a forma de avaliação por grupo.

## 3. Arquivos implementados

Arquivos principais:

```text
src/liverct/models/mil_dataset.py
src/liverct/models/mil_model.py
src/liverct/models/mil_experiment.py
scripts/run_mil_experiment.py
notebooks/09_mil_por_grupo.ipynb
docs/experimento_mil_por_grupo.md
```

## 4. Abordagens comparadas

O script permite comparar três estratégias simples de pooling:

1. `mean_pooling`: média dos embeddings dos slices da bag.
2. `max_pooling`: máximo dos embeddings dos slices da bag.
3. `attention_pooling`: atenção simples aprendida sobre os embeddings dos slices.

Todas as abordagens usam um encoder CNN pequeno para transformar cada slice em embedding. Depois, o pooling gera uma representação única da bag, usada para a classificação binária.

## 5. Entradas

Entrada principal:

```text
data/interim/split_slices.csv
```

Esse arquivo é derivado localmente e não deve ser versionado. Ele precisa conter:

- `file_path`;
- `label`;
- `split`;
- `inferred_group_id`;
- `class_name`;
- `filename`;
- `slice_id`, quando disponível.

O script valida que cada `inferred_group_id` aparece em apenas um split.

## 6. Saídas previstas

Saídas pequenas em `reports/`:

```text
reports/tables/mil_experiment_metrics.csv
reports/tables/mil_group_predictions.csv
reports/tables/mil_training_history.csv
reports/figures/mil_confusion_matrix.png
```

Checkpoints são salvos localmente em:

```text
models/checkpoints/mil_experiments/
```

Os checkpoints não devem ser versionados.

## 7. Métricas

As métricas são calculadas no nível de grupo:

- balanced accuracy;
- sensitivity;
- specificity;
- ROC-AUC;
- average precision;
- precision;
- recall;
- F1;
- matriz de confusão.

A classe positiva é:

```text
Hepatic_Steatosis
```

## 8. Como executar

Execução completa com os três poolings:

```bash
python scripts/run_mil_experiment.py --epochs 10 --batch-size 1
```

Execução leve registrada nesta etapa, útil em CPU:

```bash
python scripts/run_mil_experiment.py --epochs 3 --image-size 128 --max-slices-per-bag 12 --batch-size 1 --patience 2
```

Smoke test sem salvar tabelas/figuras:

```bash
python scripts/run_mil_experiment.py --epochs 1 --image-size 64 --max-slices-per-bag 4 --max-groups-per-split 4 --pooling mean_pooling attention_pooling --no-save
```

## 9. Resultados da execução registrada

Foi executada uma versão leve do experimento em CPU, com:

- `epochs = 3`;
- `image_size = 128`;
- `max_slices_per_bag = 12`;
- `batch_size = 1`;
- `patience = 2`;
- `seed = 42`;
- poolings: `mean_pooling`, `max_pooling` e `attention_pooling`.

Essa execução é real e reproduzível, mas não deve ser interpretada como busca exaustiva de hiperparâmetros.

### 9.1. Métricas no teste por grupo

| Modelo | N grupos | Balanced accuracy | Sensibilidade | Especificidade | ROC-AUC | Average precision | Precision | Recall | F1 | TN | FP | FN | TP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `mil_mean_pooling` | 35 | 0.6087 | 0.2174 | 1.0000 | 0.6304 | 0.8018 | 1.0000 | 0.2174 | 0.3571 | 12 | 0 | 18 | 5 |
| `mil_max_pooling` | 35 | 0.5054 | 0.2609 | 0.7500 | 0.4710 | 0.6786 | 0.6667 | 0.2609 | 0.3750 | 9 | 3 | 17 | 6 |
| `mil_attention_pooling` | 35 | 0.5181 | 0.8696 | 0.1667 | 0.6630 | 0.8615 | 0.6667 | 0.8696 | 0.7547 | 2 | 10 | 3 | 20 |

### 9.2. Leitura inicial

Nesta configuração curta, `mean_pooling` foi mais específico, mas perdeu muitos casos positivos. `attention_pooling` foi mais sensível, mas produziu mais falsos positivos. `max_pooling` ficou próximo do acaso em balanced accuracy no teste.

Esses resultados indicam que o MIL está operacional, mas ainda precisa de experimentos adicionais antes de qualquer afirmação forte. A comparação deve considerar que a CNN full image e os experimentos ROI foram treinados com outra configuração.

## 10. Interpretação esperada

O MIL deve ser comparado contra:

- CNN 2D com imagem inteira e agregação média das probabilidades por grupo;
- experimentos com ROI hepática aproximada, se as tabelas estiverem disponíveis;
- baseline estatístico de controle, quando útil para contextualização.

Um resultado melhor em MIL pode indicar que a agregação aprendida por grupo é útil. Um resultado pior pode indicar que a formulação é mais difícil, que o dataset é pequeno no nível de grupo, ou que a configuração de treino precisa ser ajustada.

Em qualquer caso, o estudo permanece exploratório.

## 11. Limitações

As principais limitações continuam sendo:

- imagens em JPEG;
- ausência de DICOM;
- ausência de NIfTI;
- ausência de valores HU confiáveis;
- ausência de metadados clínicos;
- ausência de segmentação hepática validada;
- `inferred_group_id` é um agrupamento técnico, não uma identificação clínica validada;
- amostra pequena no nível de grupo;
- ausência de validação externa.

O experimento MIL não valida o modelo para uso clínico e não deve ser apresentado como diagnóstico autônomo.
