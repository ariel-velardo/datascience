# Mapa dos notebooks do projeto

Este arquivo resume a funcao de cada notebook numerado do projeto. Os notebooks foram organizados para contar a historia metodologica do estudo: primeiro a base dos dados, depois auditoria, EDA, baseline estatistico, CNN, analise de erros, interpretabilidade e experimentos com ROI.

O projeto continua sendo exploratorio e nao validado clinicamente. Nenhum notebook deve ser interpretado como ferramenta diagnostica autonoma.

## Sequencia recomendada

| Notebook | Funcao |
|---|---|
| `01_metodologia_dataset_e_splits.ipynb` | Explica o dataset, as classes `Healthy` e `Hepatic_Steatosis`, o conceito de slice, o agrupamento por `inferred_group_id` e a validacao do split por grupo para reduzir risco de leakage. |
| `02_auditoria_qualidade_imagens.ipynb` | Documenta a auditoria tecnica das imagens JPEG, incluindo formatos, dimensoes, legibilidade, duplicatas exatas, canais/modos de imagem e limitacoes por ausencia de DICOM, NIfTI, HU confiavel e metadados clinicos. |
| `03_eda_visual_e_tecnica.ipynb` | Realiza EDA visual e tecnica, com distribuicoes por classe, grupos, slices por grupo, estatisticas simples de intensidade e reaproveitamento de figuras/tabelas em `reports/`. |
| `04_baseline_estatistico_controle.ipynb` | Documenta o baseline estatistico de controle com features simples de intensidade, mantendo split por `inferred_group_id` e avaliacao por slice e por grupo. |
| `05_baseline_cnn_2d.ipynb` | Apresenta o primeiro baseline CNN 2D, compara resultados com o baseline estatistico e registra metricas por slice e por grupo. |
| `06_analise_visual_erros.ipynb` | Organiza casos de falso positivo, falso negativo, verdadeiro positivo e verdadeiro negativo do baseline CNN para inspecao qualitativa. |
| `07_gradcam_interpretabilidade.ipynb` | Aplica Grad-CAM aos casos selecionados para investigar se a CNN olha para regioes visualmente plausiveis ou possiveis atalhos tecnicos. |
| `08_experimentos_roi_hepatica.ipynb` | Compara o uso da imagem inteira com recorte de ROI hepatica aproximada e mascara heuristica, mantendo o carater exploratorio e nao clinico. |
| `09_mil_por_grupo.ipynb` | Organiza o experimento de Multiple Instance Learning, no qual cada `inferred_group_id` e tratado como uma bag de slices e avaliado diretamente no nivel de grupo. |

## Separacao metodologica

- Notebooks `01`, `02` e `03`: analise descritiva e validacao tecnica dos dados.
- Notebook `04`: baseline preditivo simples de controle.
- Notebooks `05`, `08` e `09`: experimentos preditivos com CNN, ROI aproximada e MIL por grupo.
- Notebooks `06` e `07`: analise qualitativa de erros e interpretabilidade.
- Nenhum notebook executa inferencia causal; quando houver conclusoes, elas devem ser tratadas como exploratorias.

## Comandos uteis

Para abrir os notebooks:

```bash
jupyter notebook notebooks/
```

Para gerar artefatos derivados usados pelos notebooks iniciais:

```bash
python scripts/build_dataset_index.py
python scripts/build_splits.py
python scripts/audit_images.py
python scripts/run_visual_eda.py
python scripts/run_statistical_baseline.py
python scripts/run_mil_experiment.py --epochs 3 --image-size 128 --max-slices-per-bag 12 --patience 2
```

Os comandos acima dependem do dataset local configurado em `configs/config.local.yaml`. Dados brutos, imagens, checkpoints e modelos treinados nao devem ser versionados.

## Apendice experimental MIL por grupo

O notebook `09_mil_por_grupo.ipynb` deve ser lido como etapa adicional e experimental. Ele modela cada `inferred_group_id` como uma bag de slices e compara `mean_pooling`, `max_pooling` e `attention_pooling`.

No teste por grupo, `mil_mean_pooling` teve balanced accuracy 0.6087, sensibilidade 0.2174, especificidade 1.0000, ROC-AUC 0.6304 e F1 0.3571. `mil_max_pooling` teve balanced accuracy 0.5054, sensibilidade 0.2609, especificidade 0.7500, ROC-AUC 0.4710 e F1 0.3750. `mil_attention_pooling` teve balanced accuracy 0.5181, sensibilidade 0.8696, especificidade 0.1667, ROC-AUC 0.6630 e F1 0.7547.

A leitura metodologica e que o MIL atual ainda precisa de ajuste: `mean_pooling` ficou conservador, `max_pooling` foi fraco e `attention_pooling` aumentou sensibilidade ao custo de muitos falsos positivos. Assim, o MIL ainda nao substitui a linha principal. A melhor abordagem principal ate agora permanece a CNN com ROI crop aproximada, enquanto o MIL fica documentado como caminho futuro.

Todos os resultados continuam exploratorios e nao validam uso clinico.
