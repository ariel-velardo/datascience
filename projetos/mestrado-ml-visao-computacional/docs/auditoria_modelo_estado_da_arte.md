# Auditoria técnica do modelo e aproximação a um estado da arte realista

> **Aviso importante:** este documento é uma auditoria técnica de um estudo exploratório e **não validado clinicamente**. Nenhum achado ou recomendação aqui deve ser lido como validação, refutação ou orientação diagnóstica. O objetivo é técnico e metodológico: apontar riscos, inconsistências e oportunidades de melhoria no pipeline de visão computacional.

## 0. Contexto, escopo e limites desta auditoria

Esta auditoria cobre o repositório inteiro: `README.md`, `docs/`, `configs/`, `scripts/`, `src/liverct/`, os 9 notebooks (`01` a `09`) e os artefatos gerados em `data/interim/` e `reports/`.

O que foi feito para produzir este documento:

- leitura integral do código em `src/liverct/` e `scripts/`;
- leitura das saídas já executadas e salvas dos 9 notebooks (sem reexecução);
- leitura de todos os `docs/*.md` existentes;
- inspeção direta dos artefatos gerados (`data/interim/*.csv`, `data/interim/*.json`, `reports/tables/*.csv`, `reports/tables/*.json`);
- inspeção visual de uma amostra de figuras já geradas em `reports/figures/` (Grad-CAM, exemplos de ROI, curvas);
- verificação computacional pontual e independente das alegações mais críticas (ver seção 2.2) usando um script novo, leve e re-executável: [`scripts/verify_group_split_integrity.py`](../scripts/verify_group_split_integrity.py).

O que **não** foi feito, para deixar claro o alcance real desta auditoria:

- nenhum notebook foi reexecutado;
- nenhum modelo foi retreinado;
- nenhum experimento novo foi rodado (as propostas da seção 8 e do documento [`plano_experimentos_proximos_passos.md`](plano_experimentos_proximos_passos.md) são recomendações, não resultados);
- a leitura visual de Grad-CAM cobriu apenas 3 casos, de forma qualitativa (ver seção 5.3 e seção 10);
- nenhum dado bruto, imagem médica, checkpoint ou notebook principal (`01`–`09`) foi alterado.

Todos os números citados neste documento vêm de arquivos já gerados no repositório (`data/interim/`, `reports/tables/`, `reports/tables/*.json`) ou da execução do script de verificação citado acima. Nenhuma métrica foi inventada ou estimada.

Os achados estão catalogados com um ID estável (`REPO-XX`, `DAT-XX`, `MET-XX`, `CNN-XX`, `GRC-XX`, `ROI-XX`, `MIL-XX`) em [`reports/tables/auditoria_achados_modelo.csv`](../reports/tables/auditoria_achados_modelo.csv), referenciado ao longo deste texto. Nenhum achado foi classificado como severidade **crítica** — decisão editorial explícita: a única categoria de problema que justificaria essa severidade seria vazamento de dados entre splits, e a seção 2.2 mostra que isso foi verificado como ausente, de forma redundante e reproduzível. O teto de severidade usado é **alta**.

Toda recomendação deste documento é rotulada como um destes 6 tipos: `correção necessária`, `melhoria metodológica`, `experimento futuro`, `dependente de novos dados`, `dependente de segmentação` ou `dependente de DICOM/NIfTI`.

---

## 1. Mapa do repositório e consistência

### 1.1. Dependência entre notebooks

```
01_metodologia_dataset_e_splits.ipynb        (index + split; gera data/interim/*.csv)
        │
        ▼
02_auditoria_qualidade_imagens.ipynb          (audita as imagens indexadas em 01)
        │
        ▼
03_eda_visual_e_tecnica.ipynb                 (EDA sobre index + split + auditoria)
        │
        ▼
04_baseline_estatistico_controle.ipynb        (baseline estatístico sobre o split de 01)
        │
        ▼
05_baseline_cnn_2d.ipynb                      (CNN sobre o split de 01; compara com 04)
        │
        ▼
06_analise_visual_erros.ipynb                 (casos de erro do modelo de 05)
        │
        ▼
07_gradcam_interpretabilidade.ipynb           (Grad-CAM sobre os casos de 06, modelo de 05)

08_experimentos_roi_hepatica.ipynb  ──┐        (ambos dependem só do split de 01;
09_mil_por_grupo.ipynb              ──┘         não dependem um do outro)
```

Os notebooks `01`–`07` formam uma cadeia sequencial estrita. `08` e `09` são ramos independentes que só dependem do split produzido em `01` (via `data/interim/split_slices.csv`) — confirmado em código (ver seção 2.2) e não um do outro.

### 1.2. Documentação vs. código executado — achados

**[`REPO-01`, severidade alta]** `notebooks/08_experimentos_roi_hepatica.ipynb` define `PROJECT_ROOT = Path.cwd()` sem nenhum fallback para o diretório pai. A saída já executada e salva no notebook mostra literalmente:

```
Split nao encontrado: C:\GitHub\mestrado_ml_visao_computacional\notebooks\data\interim\split_slices.csv
Tabela de comparacao ainda nao encontrada.
Diretorio ainda nao encontrado: ...\notebooks\reports\figures\roi_examples
```

Ou seja, o kernel procurou os dados dentro de `notebooks/data/...` em vez de `data/...`. `notebooks/09_mil_por_grupo.ipynb` já resolve exatamente esse problema com um fallback de 2 linhas:

```python
PROJECT_ROOT = Path.cwd()
if not (PROJECT_ROOT / "src").exists() and (PROJECT_ROOT.parent / "src").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
```

e suas saídas mostram corretamente 3.557 slices / 225 grupos e a tabela de comparação real. Os dados subjacentes de `08` **estão corretos** — `reports/tables/roi_experiment_comparison.csv` existe e tem números coerentes (ver seção 6) — só a apresentação dentro do notebook está quebrada. **[correção necessária, não aplicada nesta etapa]**: aplicar o mesmo fallback do notebook `09` ao notebook `08` e reexecutá-lo. Por instrução do projeto, notebooks principais (`01`–`09`) não devem ser alterados sem aprovação explícita; esta seção documenta o diagnóstico exato e a correção exata para essa aprovação.

**[`REPO-05`, severidade alta]** Dos 10 scripts em `scripts/` que importam `liverct` diretamente, **6 não adicionam `src/` ao `sys.path`** antes do import: `build_dataset_index.py`, `build_splits.py`, `audit_images.py`, `run_visual_eda.py`, `run_statistical_baseline.py` e `run_gradcam.py`. Os outros 4 (`train_baseline_cnn.py`, `evaluate_baseline_cnn.py`, `run_roi_experiments.py`, `run_mil_experiment.py`) já fazem isso corretamente:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
```

Verificado empiricamente nesta auditoria: o pacote `liverct` **não está instalado** (nem sequer no `.venv` do projeto — `python -c "import liverct"` falha com `ModuleNotFoundError`, e não há nenhum `.pth`, `pyproject.toml`, `setup.py` ou instalação editável no repositório). Isso significa que os comandos listados em `docs/mapa_notebooks_do_projeto.md` sob "Comandos úteis" — `python scripts/build_dataset_index.py`, `python scripts/build_splits.py`, `python scripts/audit_images.py`, `python scripts/run_visual_eda.py`, `python scripts/run_statistical_baseline.py` — **falham com `ModuleNotFoundError: No module named 'liverct'`** se executados exatamente como documentado, a partir de um clone novo do repositório. **[correção necessária]**: adicionar o mesmo bloco de 3 linhas usado nos outros 4 scripts ao topo dos 6 scripts afetados.

**[`REPO-02`, severidade média]** `configs/config.local.yaml` declara uma seção `splits:` (60/20/20) e uma seção `preprocessing:` (224×224, `normalize: true`) que **nunca são lidas por nenhum código**: o split real usado em todo o projeto é 70/15/15 fixo em `src/liverct/data/split_dataset.py`, e o pré-processamento real é 256×256 com apenas divisão por 255 (`src/liverct/models/cnn_dataset.py`). Além disso, `configs/config.example.yaml` — citado por `scripts/build_dataset_index.py` como o template a copiar — **tem 0 bytes**. **[correção necessária]**: preencher `config.example.yaml` com os parâmetros de fato usados (ou remover as seções mortas de `config.local.yaml` e documentar que split/preprocessing são fixos no código).

**[`REPO-03`, severidade alta]** `tests/` contém apenas um `__init__.py` vazio. Não há nenhum teste automatizado para as invariantes mais críticas do projeto (integridade de split por grupo, consistência de bag/label do MIL). **[melhoria metodológica]**, detalhada na seção 9 e no plano de experimentos.

**[`REPO-04`, severidade média]** `requirements.txt` lista 14 pacotes sem nenhuma versão fixada. Versões efetivamente instaladas hoje (checadas via `.venv/Lib/site-packages`): `torch 2.12.1`, `torchvision 0.27.1`, `numpy 2.4.6`, `pandas 3.0.3`, `scikit-learn 1.9.0`, `opencv-python 4.13.0.92`, `pillow 12.2.0`, `xgboost 3.2.0`, `matplotlib 3.11.0`, `pyyaml 6.0.3`, `tqdm 4.68.3`. **[melhoria metodológica]**: fixar essas versões.

Fora esses pontos, a documentação (README, `docs/01`–`docs/07`, `docs/mapa_notebooks_do_projeto.md`) foi cruzada com os números reais em `data/interim/` e `reports/tables/` e **bate exatamente** — nenhuma divergência numérica foi encontrada entre o que os docs afirmam e o que os artefatos gerados mostram.

---

## 2. Auditoria de dados e splits

### 2.1. Indexação e construção do `inferred_group_id`

`src/liverct/data/index_dataset.py::parse_filename` constrói o `inferred_group_id` dividindo o nome do arquivo (sem extensão) pelo caractere `-`: os 3 primeiros tokens formam o `inferred_group_id`, o 4º token é o `slice_id` (ex.: `1-img-00004-00080.jpg` → grupo `1-img-00004`, slice `80`).

Verificado computacionalmente sobre os 3.557 arquivos indexados: **100% têm exatamente 4 tokens** — o parsing é limpo nos dados atuais, e `build_dataset_index.py` roda uma validação adicional (`validate_group_label_consistency`) que levanta `RuntimeError` caso algum grupo apareça associado a mais de uma classe (0 conflitos encontrados).

**[`DAT-01`, severidade média]**: se um nome de arquivo tiver menos de 4 tokens, o código cai silenciosamente para um "grupo singleton" (o `inferred_group_id` vira o nome do arquivo inteiro), sem log nem exceção. Hoje esse caminho nunca é exercitado, mas não há teste de regressão que trave esse comportamento caso o formato de nomes mude em um lote futuro do dataset. **[melhoria metodológica]**: adicionar aviso/log e um teste de regressão (ver seção 9, achado `REPO-03`).

### 2.2. Verificação de vazamento de grupo entre splits

Esta é a regra metodológica mais importante do projeto (`AGENTS.local.md`: *"Nunca fazer split por imagem/slice. Fazer split por `inferred_group_id`"*). Foi verificada nesta auditoria de forma independente, redundante e reproduzível.

O split é feito em `src/liverct/data/split_dataset.py::split_groups`, com unidade = **grupo** (nunca slice), estratificado por classe (`groupby("class_name")` antes de particionar), com `seed=42` fixo e proporções `70% / 15% / 15%`. A expansão de grupo para slice (`expand_splits_to_slices`) é um simples mapeamento — nenhum slice recebe um split próprio.

Executando `python scripts/verify_group_split_integrity.py` (script criado nesta auditoria, que reaproveita as mesmas funções de validação já usadas em produção por `train_cnn.py`, `roi_experiments.py` e `mil_dataset.py`) sobre `data/interim/split_slices.csv`, o resultado real obtido foi:

```
=== VERIFICACAO DE INTEGRIDADE DO SPLIT POR GRUPO ===
Total de slices: 3557
Total de grupos (inferred_group_id): 225

Grupos por split e classe:
  - test  | Healthy             : 12 grupos
  - test  | Hepatic_Steatosis   : 23 grupos
  - train | Healthy             : 53 grupos
  - train | Hepatic_Steatosis   : 104 grupos
  - val   | Healthy             : 11 grupos
  - val   | Hepatic_Steatosis   : 22 grupos

Slices por split e classe:
  - test  | Healthy             : 260 slices
  - test  | Hepatic_Steatosis   : 300 slices
  - train | Healthy             : 1095 slices
  - train | Hepatic_Steatosis   : 1364 slices
  - val   | Healthy             : 256 slices
  - val   | Hepatic_Steatosis   : 282 slices

Leakage entre splits (grupos presentes em mais de um split):
  - train-val:  0
  - train-test: 0
  - val-test:   0

=== VEREDITO ===
PASS: nenhum inferred_group_id aparece em mais de um split.
```

Isso confirma, de forma independente do `split_summary.json` já existente e do texto do notebook `01`: **nenhum `inferred_group_id` aparece em mais de um split.** Esse resultado pode ser reproduzido a qualquer momento rodando o script.

Resumo (grupos / slices por split e classe):

| Split | Grupos Healthy | Grupos Steatosis | Grupos total | Slices Healthy | Slices Steatosis | Slices total |
|---|---:|---:|---:|---:|---:|---:|
| Train | 53 | 104 | 157 | 1.095 | 1.364 | 2.459 |
| Val | 11 | 22 | 33 | 256 | 282 | 538 |
| Test | 12 | 23 | 35 | 260 | 300 | 560 |
| **Total** | **76** | **149** | **225** | **1.611** | **1.946** | **3.557** |

A estratificação por classe no nível de grupo funciona como esperado: a proporção Healthy/Steatosis por grupo fica estável entre 33,3% e 34,3% em todos os splits (33,76% train, 33,33% val, 34,29% test) — a estratificação é feita corretamente na unidade de grupo, não de slice.

### 2.3. Duplicatas

`src/liverct/data/audit_images.py::find_exact_duplicates` usa hash MD5 do arquivo inteiro, aplicado globalmente (não só dentro de uma classe/split) — ou seja, capturaria uma duplicata mesmo que estivesse em splits ou classes diferentes. Resultado: `data/interim/duplicate_hashes.csv` tem 0 linhas; recomputado de forma independente nesta auditoria a partir de `image_quality_audit.csv` (3.557 hashes únicos para 3.557 arquivos) — confirma 0 duplicatas exatas.

**[`DAT-04`, severidade baixa]**: apenas duplicatas byte-idênticas (MD5) são checadas; quase-duplicatas (o mesmo slice salvo/recomprimido sob outro nome) não são verificadas — já reconhecido como limitação futura em `docs/01_metodologia_dataset_e_splits.md`. **[experimento futuro]**: hash perceptual complementar (seção 9/plano de experimentos).

### 2.4. Ausência de vazamento por estatística de normalização

Não existe, em nenhum ponto do pipeline, uma estatística global (média/desvio-padrão) calculada sobre o dataset inteiro e reutilizada na modelagem — as imagens são só divididas por 255 (`cnn_dataset.py`), sem subtração de média. O único ponto onde uma estatística é de fato ajustada é o `StandardScaler` do baseline estatístico (`src/liverct/models/statistical_baseline.py`), e ele é ajustado **apenas no split de treino** (`train_df = df[df["split"] == "train"]` antes de `.fit()`), depois aplicado em val/test — sem vazamento.

### 2.5. Separação slice vs. grupo nas métricas

Confirmado nos três pipelines de modelagem (CNN baseline, ROI, MIL): todos calculam e salvam métricas **separadamente** em nível de slice e em nível de grupo (ex.: `baseline_cnn_test_slice_predictions.csv` vs. `baseline_cnn_test_group_predictions.csv`), com a agregação de grupo feita por média das probabilidades de slice (`src/liverct/evaluation/group_aggregation.py`, ver seção 3.2). A seleção de modelo (early stopping/checkpoint) em todos os pipelines usa o split de validação corretamente carregado por grupo.

### 2.6. Riscos de atalho visual nos dados

**[`DAT-02`, severidade alta]**: o tamanho médio do arquivo JPEG é sistematicamente maior para `Hepatic_Steatosis` do que para `Healthy`, em **todos** os splits (`image_quality_summary.json`): geral 41.793,72 vs. 38.595,21 bytes; train 41.583,57 vs. 38.471,48; val 42.584,21 vs. 37.689,98; test 42.006,12 vs. 40.007,59. Há também, na inspeção visual das miniaturas em `reports/figures/eda_samples_by_class.png`, um artefato recorrente de borda brilhante (compatível com mesa de tomógrafo) em posição aproximadamente fixa. Todas as 3.557 imagens têm `min_intensity = 0` e `max_intensity = 255` (letterboxing preto nos cantos + saturação de branco), um padrão uniforme entre classes — não é, por si só, um vetor de vazamento, mas o tamanho de arquivo correlacionado à classe é um sinal técnico não anatômico, e um vetor plausível de atalho visual para a CNN (ver também achado `GRC-01`, seção 5.3). **[experimento futuro]**: quantificar a correlação entre esses sinais técnicos e a predição do modelo.

**[`DAT-03`, severidade baixa]**: a checagem de canal/modo de imagem no notebook `02` só tem evidência executada e persistida para as primeiras 20 linhas de `image_quality_audit.csv` — como a tabela está ordenada por split/classe/grupo, essas 20 linhas cobrem um único `inferred_group_id`, uma única classe (`Healthy`) e um único split (`test`). A conclusão (todas as imagens são RGB de 3 canais, redundantes sobre conteúdo em escala de cinza) está correta — uma reamostragem estratificada independente feita nesta auditoria (90 imagens, 15 por combinação classe×split) confirmou 100% RGB em todos os casos — mas a evidência **persistida no notebook** não é representativa por si só. **[melhoria metodológica]**: trocar `.head(20)` por amostra estratificada.

---

## 3. Auditoria de métricas e avaliação

### 3.1. Inventário de métricas

`src/liverct/evaluation/classification_metrics.py::compute_binary_classification_metrics` calcula: accuracy, balanced accuracy, precision, sensibilidade (recall), especificidade, F1, matriz de confusão (tn/fp/fn/tp), ROC-AUC e average precision (com guarda para NaN quando só uma classe está presente). Essas métricas cobrem razoavelmente bem o desbalanceamento de classe do projeto (balanced accuracy, sensibilidade/especificidade e AUC/AP são todas robustas a desbalanceamento, ao contrário de accuracy pura).

### 3.2. Agregação por grupo

`src/liverct/evaluation/group_aggregation.py::aggregate_probabilities_by_group` agrega por **média das probabilidades de slice**, aplicando o threshold sobre essa média — usado por CNN, ROI e MIL. **[`MET-05`, severidade baixa]**: `src/liverct/models/statistical_baseline.py` reimplementa a mesma lógica de forma independente (`aggregate_predictions_by_group`), com um schema de coluna ligeiramente diferente — uma violação DRY que pode causar inconsistência silenciosa se a regra de agregação for corrigida em um lugar e esquecida no outro. **[melhoria metodológica]**: consolidar em uma única função.

### 3.3. Threshold fixo em 0,5

**[`MET-04`, severidade média]**: o threshold de decisão é 0,5 em todo o pipeline. Em `classification_metrics.py` é ao menos um parâmetro com esse valor como default; em `statistical_baseline.py` é um literal `0.5` direto no código, sem parametrização alguma. Nenhuma análise de sensibilidade/especificidade em função do threshold foi feita. **[experimento futuro]**: gerar essa curva sobre as probabilidades já salvas (não exige retreino).

### 3.4. Ausência total de calibração, bootstrap e intervalo de confiança

**[`MET-03`, severidade alta]**: uma busca (`grep`) por `bootstrap`, `confidence_interval`, `calibrat`, `brier` e `temperature` em todo `src/` e `scripts/` não encontrou **nenhuma ocorrência**. Todas as métricas reportadas no projeto (accuracy, balanced accuracy, F1, ROC-AUC, AP) são pontuais. Com apenas 33 grupos de validação e 35 de teste, diferenças pequenas entre modelos — como as vistas entre os 3 braços de ROI (seção 6) — não podem hoje ser diferenciadas de ruído amostral.

**Proposta concreta [experimento futuro], sem exigir retreino** (detalhada no plano de experimentos):

- **Bootstrap por grupo**: reamostragem com reposição dos grupos de teste/validação, recalculando a métrica de interesse a cada reamostra, para produzir um IC 95% — aplicável diretamente sobre os arquivos `*_group_predictions.csv` já salvos.
- **Calibração**: reliability curve (probabilidade prevista vs. frequência observada, por bins) e Brier score sobre as probabilidades de grupo já salvas; temperature scaling (1 parâmetro, ajustado na validação) como correção pós-hoc, se a curva indicar necessidade.

### 3.5. `pos_weight` e desbalanceamento: slice vs. grupo

**[`MET-02`, severidade média]**: `src/liverct/models/train_cnn.py::compute_pos_weight` calcula o peso de classe a partir da razão **slice-level** do treino (1.364 positivos / 1.095 negativos ≈ 1,25:1). O desbalanceamento real no **nível de grupo** — a unidade de avaliação mais relevante do projeto — é mais severo (104/53 ≈ 1,96:1). O peso efetivamente aplicado no treino é, portanto, mais brando do que o desbalanceamento visto na avaliação por grupo.

### 3.6. Conclusões escritas vs. números — checagem nominal de 3 alegações

**Alegação 1 — "a CNN supera o baseline estatístico" (implícita em `docs/05`).** Verificação: no nível de **grupo/teste** (a unidade que mais importa no projeto), comparando `reports/tables/baseline_cnn_vs_statistical_baseline_test.csv`:

| Nível | ΔBalanced Acc. | ΔSensibilidade | ΔEspecificidade | ΔF1 | ΔROC-AUC | ΔAP |
|---|---:|---:|---:|---:|---:|---:|
| Slice | +0,0815 | +0,0400 | +0,1231 | +0,0657 | +0,0678 | +0,0683 |
| Grupo | +0,0181 | **−0,1304** | +0,1666 | **−0,0378** | +0,0870 | +0,0567 |

**[`MET-06`, severidade alta]**: no nível de grupo, a CNN vence em especificidade, ROC-AUC e AP, mas **perde para a regressão logística (4 features de intensidade)** em sensibilidade (−0,1304) e F1 (−0,0378). Isso já está honestamente reportado em `docs/04_baseline_estatistico_controle.md`, mas merece destaque proporcional: sensibilidade (não deixar de identificar um caso de esteatose) é o eixo mais relevante em uma leitura cautelosa, e é exatamente onde o baseline mais simples vence, no nível que conta.

**Alegação 2 — "`roi_crop_aproximada` é a linha principal mais promissora" (`README.md`, `docs/resultados_experimentos_roi_hepatica.md`).** Verificação detalhada na seção 6.3: direcionalmente correta (maior balanced accuracy de grupo no teste), mas numericamente frágil (35 grupos de teste, sem teste de significância, toda a vantagem de especificidade equivale a 1–2 grupos). Achado `ROI-02`.

**Alegação 3 — enquadramento do MIL como "ainda não superou a CNN... linha experimental futura" (`README.md`, `docs/experimento_mil_por_grupo.md`).** Verificação: já está adequadamente cauteloso e não superestima o resultado — a auditoria (seção 7) mostra que a causa raiz é ainda mais específica do que o texto atual sugere (subtreinamento severo e mensurável, não apenas "precisa de ajuste").

Nenhuma linguagem clinicamente conclusiva foi encontrada em `docs/04`–`docs/07` ou nas células de markdown dos notebooks `04`–`07` — o texto é consistentemente cauteloso (ex.: *"o mapa Grad-CAM não prova causalidade"*, *"não é possível afirmar validade clínica apenas com esses mapas"*). Este é um achado positivo genuíno da auditoria.

---

## 4. Auditoria da CNN 2D

### 4.1. Arquitetura e pré-processamento

`src/liverct/models/simple_cnn.py::SimpleCNN2D`: 3 blocos convolucionais (1→16→32→64 canais, `Conv2d 3×3` + `BatchNorm` + `ReLU` + `MaxPool 2×2` cada), `AdaptiveAvgPool2d`, `Dropout(0,25)`, `Linear(64, 1)` — saída de um único logit (sigmoid aplicado na inferência), treinado com `BCEWithLogitsLoss`. Aproximadamente 23,6 mil parâmetros treináveis — uma arquitetura deliberadamente pequena e simples, coerente com o objetivo exploratório e o tamanho do dataset (157 grupos de treino).

Pré-processamento: conversão para escala de cinza, resize condicional para 256×256 (nunca dispara na prática, pois todas as imagens já têm esse tamanho) com `resample=Image.BILINEAR` explícito, normalização por divisão simples por 255 (sem subtração de média/desvio-padrão).

### 4.2. Configuração de treino

`Adam(lr=1e-3, weight_decay=1e-4)`, `batch_size=32`, `epochs=20` com early stopping (`patience=5`), `dropout=0,25`, `seed=42`. Sementes cobertas por `set_global_seed()`: `random`, `numpy`, `torch` (CPU e CUDA) e `cudnn.deterministic=True`, chamada **antes** da construção dos dataloaders e do modelo — ordem correta para reprodutibilidade. O treino real parou na época 16 (melhor época = 11, `val_loss=0,2850`).

**[`MET-01`, severidade alta]**: a seleção do checkpoint usa exclusivamente `val_loss` (`improved = val_loss < best_val_loss`), não balanced accuracy, F1 ou ROC-AUC — as métricas efetivamente usadas para reportar e comparar os experimentos. **[melhoria metodológica]**: mudar o critério de seleção para uma métrica balanceada de grupo.

### 4.3. Aumento de dados — ausente

**[`CNN-01`, severidade alta]**: nenhum aumento de dados é aplicado, nem no treino nem na validação. O parâmetro `image_transform` existe na assinatura de `LiverCTSliceDataset`/`build_dataloader`, mas `run_cnn_training` nunca o passa. Uma busca por padrões de flip/rotação/augmentation em `src/` não encontrou nenhuma ocorrência. Com apenas 157 grupos de treino, esse é um regularizador barato e já parcialmente cabeado na arquitetura, mas sem uso. **[experimento futuro]**: flips horizontais leves + pequenas rotações, só no `train_loader`.

### 4.4. Overfitting/underfitting — leitura da curva

A partir de `reports/tables/baseline_cnn_training_history.csv`: a perda de treino cai de forma razoavelmente monotônica (0,506 → ~0,28–0,31). A perda de validação é **muito volátil**, não a assinatura clássica de overfitting (val subindo enquanto train desce de forma estável): pico de 0,8658 na época 6, mínimo de 0,2850 na época 11 (checkpoint salvo), novo pico de 0,6136+ nas épocas 12–15, terminando em 0,3520 na época 16. **[`CNN-02`, severidade média]**: esse padrão é mais consistente com ruído amostral do val set pequeno (33 grupos / 538 slices) do que com overfitting clássico — a época "melhor" pode refletir parcialmente esse ruído.

### 4.5. Risco de atalho visual

A CNN opera sobre a imagem inteira, incluindo os artefatos técnicos descritos no achado `DAT-02` (tamanho de arquivo correlacionado à classe, letterboxing, borda de mesa) e sem nenhuma restrição de campo visual à região hepática nesta etapa (isso só é testado nos experimentos de ROI, seção 6). A evidência visual de Grad-CAM (seção 5.3, achado `GRC-01`) mostra casos concretos de ativação fora do fígado, reforçando esse risco.

### 4.6. Propostas realistas de melhoria

Ordenadas por esforço/impacto (detalhadas no plano de experimentos):

1. **[experimento futuro]** Critério de checkpoint por balanced accuracy/F1 de grupo em vez de `val_loss` (achado `MET-01`).
2. **[experimento futuro]** Aumento de dados leve (flip/rotação pequena) (achado `CNN-01`).
3. **[melhoria metodológica]** Recalcular `pos_weight` na razão de grupo, não de slice (achado `MET-02`).
4. **[experimento futuro]** Bootstrap por grupo e calibração sobre as saídas já existentes (achado `MET-03`), antes de decidir se vale a pena investir em mudanças mais caras de arquitetura.

---

## 5. Auditoria de Grad-CAM e interpretabilidade

### 5.1. Implementação

`src/liverct/explainability/gradcam.py` usa `find_last_conv2d_layer()` para localizar automaticamente a última camada `Conv2d` — para `SimpleCNN2D`, resolve para `features.8` (resolução espacial 32×32, antes do pooling final), confirmado em todas as 66 linhas de `reports/tables/gradcam_cases.csv`. A matemática é o Grad-CAM padrão: pesos = média global das gradientes por canal, mapa = ReLU da soma ponderada das ativações, normalizado para [0, 1]. O modelo é colocado em modo `.eval()` antes da inferência — tratamento correto de BatchNorm/Dropout.

### 5.2. Alinhamento com a imagem original

O redimensionamento do heatmap (de 32×32 para o tamanho da imagem original) é feito em `scripts/run_gradcam.py::resize_heatmap_to_image`, com `resample=Image.BILINEAR` e ordem width/height corretamente compatível com a convenção do Pillow — um ponto onde erros de alinhamento são comuns, e aqui está correto.

**[`GRC-02`, severidade média]**: `run_gradcam.py::load_image_as_tensor` reimplementa o carregamento de imagem de forma independente de `cnn_dataset.py`, chamando `image.resize((256, 256))` **sem** especificar `resample` (o que faz o Pillow usar BICUBIC por padrão), enquanto o pipeline de treino/avaliação usa BILINEAR explícito. Hoje isso é inofensivo, porque 100% das imagens já são 256×256 e o resize nunca dispara em nenhum dos dois caminhos — mas é uma divergência latente: se imagens de outro tamanho forem adicionadas no futuro, o Grad-CAM passaria a explicar um pré-processamento sutilmente diferente do que o modelo realmente viu. **[melhoria metodológica]**: reaproveitar a função de `cnn_dataset.py`.

### 5.3. Evidência visual real — o que os mapas mostram

Inspeção direta de 3 casos em `reports/figures/gradcam/`:

- **Falso negativo** (`207-img-00043`, p≈0,062): ativação concentrada quase inteiramente na borda de costela/parede corporal — nenhuma ativação relevante sobre o fígado.
- **Falso positivo** (`114-img-00064`, p≈0,863): ativação espalhada em bordas de costela, mais um hotspot forte e concentrado **fora do contorno do corpo** (compatível com um artefato externo, como um cabo) — um padrão clássico de atalho visual.
- **Verdadeiro positivo** (`190-img-00028`, p≈0,993): mostra ativação substancial sobre a região hepática, junto com ativação em borda de costela.

**[`GRC-01`, severidade alta]**: esta é evidência concreta (não hipotética) de que o modelo pode estar usando, em pelo menos alguns casos, sinal fora do fígado — coerente com o achado `DAT-02`. É importante frisar que essa leitura é **qualitativa** e cobre apenas 3 casos entre 66 disponíveis; não substitui uma quantificação sistemática.

### 5.4. Sanity checks propostos (nenhum executado nesta auditoria)

Todos **[experimento futuro]**, aplicáveis sobre os 66 casos já selecionados em `reports/tables/gradcam_cases.csv`, sem necessidade de retreino:

1. **Grad-CAM com pesos aleatorizados**: gerar mapas usando a mesma arquitetura `SimpleCNN2D` com pesos aleatórios (sem treino) e comparar visualmente/quantitativamente com os mapas do modelo treinado — a expectativa é que o mapa aleatório não tenha coerência espacial nem relação com o conteúdo anatômico.
2. **Quantificação da ativação dentro/fora da ROI hepática aproximada**: usando a mesma `RoiBoxFractions` já definida em `src/liverct/features/roi_transforms.py` (seção 6), calcular a fração de energia do heatmap que cai dentro da caixa, separando por TP/TN/FP/FN.
3. **Comparação com a ROI hepática**: complementar ao item 2, sobrepor visualmente o heatmap e a caixa/máscara de ROI para os mesmos 66 casos.
4. **Análise separada por TP/TN/FP/FN**: agregar a métrica do item 2 por tipo de desfecho, não só olhar casos individuais.
5. **Proposta de "plausibilidade anatômica" mais objetiva**: em vez de uma leitura qualitativa caso a caso, usar a fração de energia dentro da ROI aproximada (item 2) como uma métrica numérica proxy — reconhecidamente aproximada, já que a própria ROI é uma heurística geométrica (achado `ROI-01`), não uma segmentação validada. Um valor mais alto é consistente com maior plausibilidade anatômica, mas não a prova.

---

## 6. Auditoria de ROI hepática

Este documento audita a ROI hepática do ponto de vista de corretude e justiça metodológica; para a descrição completa do experimento e discussão de resultados, ver `docs/resultados_experimentos_roi_hepatica.md` e `docs/experimentos_roi_e_nnunet.md` (não duplicados aqui).

### 6.1. Como a ROI e a máscara são construídas

`src/liverct/features/roi_transforms.py::RoiBoxFractions` define uma caixa **geométrica fixa**, em frações da imagem (`center_x=0,44, center_y=0,53, width=0,68, height=0,70`), igual para toda imagem, calculada apenas a partir das dimensões da imagem — **não** a partir de intensidade de pixel, contorno ou qualquer conteúdo. Isso é importante: como a caixa não depende do conteúdo da imagem, ela **não pode** criar um vetor de vazamento correlacionado à classe (a preocupação original desta auditoria). O braço "crop" encolhe a imagem para essa caixa; o braço "máscara heurística" desenha a mesma caixa como elipse sobre uma tela do **tamanho original**, preenchendo o resto de preto.

**[`ROI-01`, severidade alta]**: como consequência dessa diferença de implementação, crop e máscara não isolam apenas "quanta informação foi removida" — também variam em enquadramento/zoom (crop = zoomed-in na caixa; máscara = zoomed-out, com contexto ao redor preenchido de preto). Esse é um fator de confusão metodológico entre os dois braços que não está nomeado nos documentos atuais. **[melhoria metodológica]**: nomear explicitamente essa diferença em `docs/resultados_experimentos_roi_hepatica.md`; para um ablation futuro mais limpo, considerar uma variante que combine máscara + recorte da bounding box.

### 6.2. A comparação de 3 braços é justa?

Confirmado: `roi_experiments.py` usa a mesma arquitetura (`SimpleCNN2D`), carrega o split de `data/interim/split_slices.csv` uma única vez e aplica os 3 tratamentos sobre o mesmo split, com hiperparâmetros idênticos (`image_size=256, batch_size=32, epochs=20, learning_rate=0,001, weight_decay=0,0001, dropout=0,25, patience=5, seed=42`, confirmado via os `config` embutidos nos 3 checkpoints salvos). A única diferença real entre os 3 treinos é o número de épocas efetivamente treinadas antes do early stopping (16 / 10 / 14) — consequência legítima do critério de parada, não um viés injetado. Como checagem de consistência interna, `baseline_cnn` (treinado separadamente) e `roi_full_image` (o braço "imagem inteira" deste experimento) reproduzem os mesmos números a 6 casas decimais.

### 6.3. Números reais e a leitura "mais promissora"

| Modelo | Balanced Acc. (grupo, teste) | Sensibilidade | Especificidade | ROC-AUC | F1 |
|---|---:|---:|---:|---:|---:|
| `full_image` | 0,8080 | 0,7826 | 0,8333 | 0,9203 | 0,8372 |
| `roi_crop_aproximada` | **0,8496** | 0,7826 | 0,9167 | 0,9529 | 0,8571 |
| `roi_mask_heuristica` | 0,8098 | 0,8696 | 0,7500 | 0,9529 | 0,8696 |

**[`ROI-02`, severidade média]**: `roi_crop_aproximada` tem, de fato, a melhor balanced accuracy de grupo no teste — a afirmação do README/docs de que essa é a linha "mais promissora" é direcionalmente correta. Mas: com apenas 35 grupos de teste (12 Healthy), sem teste de significância e com seed única, toda a vantagem de especificidade equivale a uma diferença de 1–2 grupos (10 TN/2 FP para `full_image` vs. 11 TN/1 FP para `roi_crop`); a sensibilidade do crop é **igual** à da imagem inteira (0,7826) e **pior** que a da máscara (0,8696). Os documentos atuais já trazem essa ressalva ("essa leitura deve ser feita com cautela"), mas vale reforçá-la com intervalo de confiança (achado `MET-03`) antes de tratá-la como conclusão estável.

### 6.4. Leitura visual

Inspeção de 3 exemplos em `reports/figures/roi_examples/`: a caixa/máscara plausivelmente centra sobre a estrutura hepática (consistente com convenção radiológica), mas de forma crua — inclui costela, coluna e tecido não hepático, e em pelo menos um exemplo mais cranial a borda da caixa quase corta uma estrutura adjacente (provável vaso). Consistente com a própria descrição do projeto como heurística, não clínica.

### 6.5. Propostas de melhoria

1. **[melhoria metodológica]** Documentar explicitamente o confundidor de zoom entre crop e máscara (achado `ROI-01`).
2. **[experimento futuro]** Bootstrap por grupo sobre os 3 braços, para saber se a diferença de 0,8496 vs. 0,8080/0,8098 é estatisticamente distinguível de ruído.
3. **[experimento futuro]** Quantificar a fração de energia do Grad-CAM dentro da ROI aproximada (achado `GRC-01`/proposta da seção 5.4).
4. **[dependente de segmentação]** Comparar contra uma segmentação hepática real (nnU-Net ou equivalente) em vez da caixa heurística.
5. **[dependente de DICOM/NIfTI]** Uso futuro de dados DICOM/NIfTI para uma ROI baseada em coordenadas físicas reais, não em frações de uma imagem JPEG já recortada por terceiros.

---

## 7. Auditoria de MIL por grupo

Este documento audita a lógica e os resultados do MIL do ponto de vista de corretude; para descrição completa do experimento, ver `docs/experimento_mil_por_grupo.md` (não duplicado aqui).

### 7.1. Construção das bags — verificado correto

`src/liverct/models/mil_dataset.py` agrupa por `inferred_group_id` e levanta `ValueError` explicitamente se um grupo tiver mais de um valor de `label` ou mais de um valor de `split` — ou seja, é estruturalmente impossível uma bag misturar slices de grupos diferentes ou de splits diferentes. O rótulo da bag vem diretamente desse valor único. Este é um achado **positivo**: a preocupação central do pedido de auditoria ("todos os slices de uma bag pertencem ao mesmo grupo") está corretamente garantida em código, não apenas por convenção.

A seleção de slices por bag (`select_slices_for_bag`) é **determinística** (amostragem igualmente espaçada via `np.linspace`, sem aleatoriedade), usada da mesma forma no treino e na avaliação — ou seja, não há inconsistência entre o que é visto no treino e o que é avaliado no teste.

### 7.2. Pooling — verificado correto

Mean pooling e max pooling operam corretamente sobre a dimensão de slice. O attention pooling calcula pesos por slice e normaliza com `softmax` sobre a dimensão correta (slice, não batch nem feature). Não há padding em nenhum ponto do pipeline — bags de tamanho variável são processadas uma a uma (`collate_mil_bags` documenta explicitamente "collate variable-length bags without padding") — portanto o modo de falha "padding vazando na atenção/pooling" não pode ocorrer estruturalmente neste código.

### 7.3. Orçamento de treino real — a causa raiz dos resultados fracos

**[`MIL-01`, severidade alta]**: confirmado em `reports/tables/mil_experiment_summary.json` (consistente com o `config` embutido nos 3 checkpoints): `epochs=3, image_size=128, batch_size=1, patience=2`. O `best_epochs` registrado foi **1** (mean_pooling), **2** (max_pooling) e **1** (attention_pooling) — ou seja, o "melhor" checkpoint de 2 das 3 variantes veio logo da primeira época. O backbone (`SliceFeatureEncoder`) é treinado do zero, sem pesos pré-treinados.

Uma hipótese alternativa — "os resultados fracos refletem colapso por desbalanceamento de classe (predizer sempre a classe majoritária)" — foi testada nesta auditoria e **refutada**: a classe majoritária é `Hepatic_Steatosis` (positiva), mas o `mean_pooling` colapsa na direção **oposta** (especificidade 1,0, sensibilidade 0,2174 — prevendo majoritariamente a classe negativa/minoritária). A evidência real: as probabilidades previstas ficam concentradas perto de 0,5 em todas as variantes e splits (desvio-padrão ≈0,03), e os pesos de atenção do `attention_pooling` são aproximadamente uniformes (≈1/n_slices para praticamente toda bag de teste) — um padrão consistente com **subtreinamento severo**, não com uma regra aprendida (correta ou degenerada).

Conclusão desta auditoria: a formulação do MIL (bags, labels, pooling) está correta; os resultados fracos são explicados, de forma concreta e mensurável, pelo orçamento de treino, não por um defeito de desenho.

### 7.4. Amostragem de slices por bag

**[`MIL-02`, severidade média]**: `max_slices_per_bag=12` é aplicado de forma determinística tanto no treino quanto na **avaliação final**. Bags Healthy de teste têm, em média, 21,67 slices disponíveis — ou seja, cerca de 45% da evidência disponível é descartada mesmo na avaliação, não só no treino. Como o pipeline já processa bags de tamanho variável sem padding (seção 7.2), aumentar esse limite (ao menos na avaliação) é tecnicamente simples.

### 7.5. Comparação com a CNN — é justa?

Confirmado: `mil_experiment.py` carrega o mesmo `data/interim/split_slices.csv` usado por `train_cnn.py` e `roi_experiments.py` (mesma função `load_group_safe_split`, que reaproveita `load_split_slices`/`validate_group_split_integrity` de `cnn_dataset.py`), e os totais batem exatamente (35 grupos / 560 slices de teste, 33/538 de validação) com os das outras duas linhas. A comparação usa o mesmo conjunto de teste em todos os casos.

### 7.6. Propostas de melhoria

Todas **[experimento futuro]**, detalhadas no plano de experimentos:

1. Retreinar com orçamento realista (mais épocas, `patience` maior) — prioridade mais alta, dado que a causa raiz (seção 7.3) está bem identificada.
2. Avaliar um backbone 2D pré-treinado (torchvision, já disponível no ambiente) em vez do encoder treinado do zero.
3. Testar `max_slices_per_bag` maior, ao menos na avaliação.
4. Balanceamento de bags (class weight ou sampler no nível de bag, não só `pos_weight` na loss).
5. Regularização adicional (dropout maior, weight decay) se um orçamento maior reintroduzir overfitting.
6. Reforçar/validar formalmente que a seleção de checkpoint continua no nível de bag/grupo após qualquer mudança (já confirmado correto na versão atual).
7. Análise de atenção por slice: uma vez que o modelo esteja de fato treinado (não subtreinado), inspecionar quais slices recebem mais peso de atenção por grupo, como uma forma adicional de interpretabilidade.

---

## 8. Rumo a um estado da arte realista

Esta seção separa explicitamente o que é possível **agora**, com o dataset JPEG atual, do que depende de dados ou anotações que o projeto não possui hoje. Nenhum resultado é prometido — apenas um plano técnico.

### 8.1. Possível agora, com JPEG, sem novos dados

| Direção | Viabilidade hoje | Observação |
|---|---|---|
| Backbone 2D pré-treinado (ImageNet) via `torchvision` | Alta — `torchvision 0.27.1` já instalado | Transfer learning simples: trocar `SimpleCNN2D` por um backbone leve pré-treinado (ex. ResNet18/EfficientNet pequeno) com fine-tuning; risco de overfitting maior em 157 grupos exige regularização cuidadosa |
| Self-supervised / transfer learning | Alta | Mesmo backbone acima; pré-treino supervisionado em ImageNet já é uma forma de transfer learning disponível sem dado novo |
| Radiomics como baseline complementar | Alta — `scikit-learn`/`opencv-python` já instalados | Estender `statistical_baseline.py` com features de textura (GLCM, LBP) via `opencv`/`scikit-image` (não instalado, mas leve de adicionar), mantendo a mesma estrutura de split/avaliação já validada |
| Bootstrap por grupo / IC 95% | Alta | Seção 3.4 — puro pós-processamento sobre predições já salvas |
| Calibração (reliability curve, Brier, temperature scaling) | Alta | Seção 3.4 — idem |
| Explicabilidade quantitativa (Grad-CAM × ROI) | Alta | Seção 5.4 — reaproveita código e casos já existentes |
| Análise de robustez por grupo/exame | Alta | Junto ao bootstrap por grupo — verificar se o desempenho é estável entre subconjuntos de grupos |
| Comparação com baseline estatístico | Já existe | `statistical_baseline.py` já compara CNN vs. regressão logística vs. dummy; pode ser estendida a ROI e MIL da mesma forma |
| Comparação com baseline clínico simples | Parcial | O projeto não tem regra clínica simples (ex. um limiar de intensidade médio) documentada como baseline; seria barato adicionar como mais uma linha de `statistical_baseline.py` |
| MONAI / TorchIO | Baixa sem novo dado | As bibliotecas em si podem ser instaladas (não estão hoje), mas seu valor real é para dados volumétricos (DICOM/NIfTI) — sobre JPEG 2D isolado, o ganho é limitado |

### 8.2. Depende de dado novo, segmentação ou DICOM/NIfTI

| Direção | Depende de | Observação |
|---|---|---|
| Modelos 2.5D/3D | `dependente de DICOM/NIfTI` | Exige volume completo reconstruído (ordem espacial real entre slices, espaçamento entre cortes) — o dataset atual é uma coleção de JPEGs 2D sem garantia de volume contíguo |
| Segmentação hepática (U-Net/nnU-Net) | `dependente de segmentação` | Exige máscaras anotadas (ao menos um subconjunto) para treinar/validar; hoje não há nenhuma anotação de segmentação no projeto |
| DICOM/NIfTI + valores HU reais | `dependente de DICOM/NIfTI` | O dataset atual é derivado de JPEG sem metadado de aquisição (`AGENTS.local.md` confirma explicitamente a ausência de HU, voxel spacing, scanner/protocolo) |
| Radiomics calibrado em HU | `dependente de DICOM/NIfTI` | Radiomics sobre JPEG (8.1) é possível, mas não é comparável a radiomics calibrado em unidades Hounsfield reais |
| Validação externa | `dependente de novos dados` | Exige um segundo dataset rotulado, de fonte/scanner diferente |
| MONAI/TorchIO com ganho real | `dependente de DICOM/NIfTI` | Seu valor pleno (transforms 3D, I/O médico nativo) só se realiza com dado volumétrico |

O plano de experimentos priorizado (documento companheiro, seção correspondente) detalha por onde começar dentro do que já é viável hoje.

---

## 9. Síntese e tabela de achados

Todos os achados desta auditoria estão catalogados em [`reports/tables/auditoria_achados_modelo.csv`](../reports/tables/auditoria_achados_modelo.csv), com ID, severidade, arquivo afetado, descrição, risco técnico, recomendação rotulada, esforço e impacto estimados.

Contagem por severidade (23 achados, nenhum crítico):

| Severidade | Quantidade |
|---|---:|
| Alta | 11 |
| Média | 9 |
| Baixa | 3 |

Contagem por área:

| Prefixo | Área | Quantidade |
|---|---|---:|
| `REPO` | Repositório e reprodutibilidade | 5 |
| `DAT` | Dados e splits | 4 |
| `MET` | Métricas e avaliação | 6 |
| `CNN` | CNN 2D | 2 |
| `GRC` | Grad-CAM | 2 |
| `ROI` | ROI hepática | 2 |
| `MIL` | MIL por grupo | 2 |

Os 5 achados de severidade alta com maior relevância imediata, um por área com achados de severidade alta: `REPO-01` (notebook 08 quebrado), `REPO-05` (scripts sem `sys.path`, achado novo desta auditoria), `MET-03` (ausência total de calibração/IC), `CNN-01` (sem aumento de dados), `GRC-01`/`ROI-01`/`MIL-01` (achados centrais de cada linha experimental).

---

## 10. Limitações desta auditoria

- Nenhum notebook foi reexecutado; a leitura de "documentação bate com código executado" se apoiou nas saídas já salvas nos `.ipynb` e nos artefatos em `data/interim/`/`reports/`.
- A leitura visual de Grad-CAM (seção 5.3) cobriu 3 casos de 66 disponíveis — é ilustrativa, não uma análise sistemática. A proposta da seção 5.4 é exatamente para tornar essa leitura sistemática.
- Os achados sobre artefatos visuais (letterboxing, borda de mesa, seção 2.6) vêm de inspeção visual de miniaturas agregadas e estatística simples (min/max/tamanho de arquivo), não de uma análise formal de shortcut-learning (ex. um modelo treinado só sobre bordas para medir separabilidade).
- Nenhum modelo foi retreinado; achados sobre causa raiz (ex. subtreinamento do MIL, seção 7.3) são inferências fundamentadas em configuração e estatísticas de saída já registradas, não em um experimento controlado novo.
- Esta auditoria não avalia questões de licenciamento, privacidade ou proveniência do dataset Kaggle de origem — fora do escopo solicitado.
