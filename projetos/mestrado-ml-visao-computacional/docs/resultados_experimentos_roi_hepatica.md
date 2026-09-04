# Resultados dos experimentos exploratorios com ROI hepatica

## 1. Objetivo

Esta etapa comparou o baseline CNN 2D com imagem inteira contra versoes que usam uma regiao hepatica aproximada.

O objetivo foi investigar se o modelo parece depender de sinal visual plausivel na regiao do figado ou se pode estar explorando atalhos fora dessa regiao, como bordas, fundo preto, ruido, artefatos JPEG, musculatura ou outras areas nao hepaticas.

O estudo permanece exploratorio e nao validado clinicamente.

## 2. Abordagens comparadas

Foram comparadas tres abordagens:

1. `full_image`
   - Usa a imagem inteira.
   - Equivale ao baseline CNN 2D atual.

2. `roi_crop_aproximada`
   - Usa um recorte fixo e ajustavel de uma regiao hepatica aproximada.
   - A ROI e heuristica, exploratoria e nao clinica.

3. `roi_mask_heuristica`
   - Usa uma mascara geometrica simples para reduzir fundo e regioes fora da ROI aproximada.
   - A mascara e heuristica, exploratoria e nao clinica.

Todos os experimentos preservaram a separacao por `inferred_group_id`. Nao houve divisao aleatoria por slice.

## 3. Metricas finais no teste

| Abordagem | Nivel | N | Balanced accuracy | Sensibilidade | Especificidade | ROC-AUC | Average precision | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full_image` | slice | 560 | 0.8155 | 0.8233 | 0.8077 | 0.9227 | 0.9451 | 0.8316 | 0.8233 | 0.8275 |
| `full_image` | group | 35 | 0.8080 | 0.7826 | 0.8333 | 0.9203 | 0.9624 | 0.9000 | 0.7826 | 0.8372 |
| `roi_crop_aproximada` | slice | 560 | 0.8674 | 0.8233 | 0.9115 | 0.9541 | 0.9653 | 0.9148 | 0.8233 | 0.8667 |
| `roi_crop_aproximada` | group | 35 | 0.8496 | 0.7826 | 0.9167 | 0.9529 | 0.9765 | 0.9474 | 0.7826 | 0.8571 |
| `roi_mask_heuristica` | slice | 560 | 0.8505 | 0.8933 | 0.8077 | 0.9517 | 0.9594 | 0.8428 | 0.8933 | 0.8673 |
| `roi_mask_heuristica` | group | 35 | 0.8098 | 0.8696 | 0.7500 | 0.9529 | 0.9754 | 0.8696 | 0.8696 | 0.8696 |

## 4. Metricas finais na validacao

| Abordagem | Nivel | N | Balanced accuracy | Sensibilidade | Especificidade | ROC-AUC | Average precision | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full_image` | slice | 538 | 0.8343 | 0.8014 | 0.8672 | 0.9431 | 0.9507 | 0.8692 | 0.8014 | 0.8339 |
| `full_image` | group | 33 | 0.8182 | 0.8182 | 0.8182 | 0.9339 | 0.9666 | 0.9000 | 0.8182 | 0.8571 |
| `roi_crop_aproximada` | slice | 538 | 0.8166 | 0.7270 | 0.9063 | 0.9485 | 0.9476 | 0.8952 | 0.7270 | 0.8023 |
| `roi_crop_aproximada` | group | 33 | 0.8182 | 0.7273 | 0.9091 | 0.9587 | 0.9748 | 0.9412 | 0.7273 | 0.8205 |
| `roi_mask_heuristica` | slice | 538 | 0.8790 | 0.8830 | 0.8750 | 0.9423 | 0.9421 | 0.8861 | 0.8830 | 0.8845 |
| `roi_mask_heuristica` | group | 33 | 0.8864 | 0.8636 | 0.9091 | 0.9504 | 0.9713 | 0.9500 | 0.8636 | 0.9048 |

## 5. Interpretacao inicial

No teste em nivel de grupo, `roi_crop_aproximada` apresentou a maior balanced accuracy:

- `full_image`: 0.8080
- `roi_crop_aproximada`: 0.8496
- `roi_mask_heuristica`: 0.8098

No teste em nivel de slice, `roi_crop_aproximada` tambem apresentou a maior balanced accuracy:

- `full_image`: 0.8155
- `roi_crop_aproximada`: 0.8674
- `roi_mask_heuristica`: 0.8505

A abordagem `roi_mask_heuristica` apresentou maior sensibilidade no teste por grupo:

- `full_image`: 0.7826
- `roi_crop_aproximada`: 0.7826
- `roi_mask_heuristica`: 0.8696

No entanto, `roi_mask_heuristica` tambem reduziu a especificidade no teste por grupo:

- `full_image`: 0.8333
- `roi_crop_aproximada`: 0.9167
- `roi_mask_heuristica`: 0.7500

Isso sugere que a mascara heuristica aumentou a deteccao da classe positiva, mas tambem produziu mais falsos positivos.

A abordagem `roi_crop_aproximada` apresentou o melhor equilibrio geral no teste por grupo, mas essa leitura deve ser feita com cautela, pois a ROI nao e uma segmentacao anatomica validada.

## 6. Limitacoes metodologicas

As principais limitacoes sao:

- as imagens estao em JPEG;
- nao ha DICOM;
- nao ha NIfTI;
- nao ha valores HU confiaveis;
- nao ha metadados clinicos;
- nao ha informacao de scanner, protocolo ou fase;
- nao ha segmentacao hepatica validada;
- a ROI e uma aproximacao geometrica;
- a mascara e heuristica;
- o `inferred_group_id` e um agrupamento tecnico, nao uma identificacao clinica validada;
- nao ha validacao externa;
- o estudo tem carater exploratorio.

Esses resultados nao provam causalmente que o modelo usa apenas sinal hepatico.

## 7. Conclusao exploratoria

Os resultados indicam que restringir a imagem a uma regiao hepatica aproximada pode manter ou melhorar algumas metricas em relacao ao baseline com imagem inteira.

Em particular, `roi_crop_aproximada` melhorou a balanced accuracy no teste por slice e por grupo. Isso sugere que vale aprofundar a investigacao com uma etapa futura baseada em segmentacao hepatica validada.

Ainda assim, a conclusao e apenas exploratoria. A ROI usada nesta etapa e heuristica, nao clinica e nao substitui uma mascara hepatica validada por especialista ou por um pipeline de segmentacao supervisionada adequadamente avaliado.

Este estudo nao e validado clinicamente e nao deve ser interpretado como ferramenta diagnostica.
