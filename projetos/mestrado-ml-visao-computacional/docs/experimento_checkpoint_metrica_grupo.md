# Experimento: seleção de checkpoint por métrica de grupo (baseline CNN)

> **Aviso importante:** este documento descreve um experimento exploratório sobre um estudo **não validado clinicamente**. Nenhum número aqui deve ser lido como validação, refutação ou orientação diagnóstica. Todos os valores citados vêm de arquivos gerados nesta rodada (`reports/tables/baseline_cnn_group_metric_*`, `reports/tables/bootstrap_group_metrics.csv`, `reports/tables/baseline_cnn_checkpoint_metric_comparison.csv`) ou dos artefatos já existentes do baseline antigo (`reports/tables/baseline_cnn_*`). Nenhum resultado foi inventado.

## 1. Hipótese

O pipeline original (`src/liverct/models/train_cnn.py`) seleciona o checkpoint do baseline CNN exclusivamente pela menor `val_loss`. Isso foi apontado como achado `MET-01` na auditoria técnica (`docs/auditoria_modelo_estado_da_arte.md`, seção 4.2), reforçado pelo achado `CNN-02`: a curva de `val_loss` do treino original é visivelmente ruidosa (pico de 0,8658 na época 6, mínimo de 0,2850 na época 11, novo pico de 0,61+ nas épocas 12–15). Como a avaliação principal do projeto é sempre feita por `inferred_group_id` (nunca por slice isolado), a hipótese testada aqui — formalizada como experimento 5 em `reports/tables/plano_experimentos_priorizado.csv` — é que selecionar o checkpoint por uma métrica de grupo (balanced accuracy) produz um modelo mais alinhado com o que o projeto realmente reporta e compara, sem precisar mudar arquitetura, dados ou hiperparâmetros.

Critério de sucesso definido a priori (mesmo documento): balanced accuracy de grupo no teste igual ou superior a 0,8080 (valor do baseline antigo), sem sensibilidade de grupo abaixo de 0,7826 (valor do baseline antigo).

## 2. O que foi mantido constante

- Arquitetura: `SimpleCNN2D` (23.585 parâmetros treináveis), sem nenhuma alteração de camadas.
- Split: `data/interim/split_slices.csv`, o mesmo split por `inferred_group_id` já validado (70/15/15, seed=42) — não recriado, não modificado.
- Seed: 42.
- Hiperparâmetros: `image_size=256, batch_size=32, epochs≤20, learning_rate=1e-3, weight_decay=1e-4, dropout=0.25, patience=5`.
- Threshold de decisão: fixo em 0,5 (sem nenhum tuning de threshold nesta rodada).
- Pré-processamento: idêntico (escala de cinza, resize condicional, divisão por 255).
- Nenhum aumento de dados (augmentation) foi adicionado.
- Nenhum outro modelo foi retreinado nesta rodada (os 3 braços de ROI, o MIL e qualquer backbone pré-treinado permanecem exatamente como estavam).

A única variável metodológica alterada foi o critério de seleção do checkpoint.

## 3. O que mudou

`src/liverct/models/train_cnn.py` ganhou um campo configurável `checkpoint_metric` em `CNNTrainingConfig` (default `"val_loss"`, preservando o comportamento antigo byte a byte para qualquer chamada que não passe o novo argumento) e um novo valor `"val_group_balanced_accuracy"`.

A cada época, além de `val_loss` (como antes), o pipeline agora sempre calcula as métricas de grupo na validação (`val_group_balanced_accuracy`, `val_group_f1`, `val_group_sensitivity`, `val_group_specificity`, `val_group_roc_auc`, `val_group_average_precision`), reaproveitando sem modificação `aggregate_probabilities_by_group` e `compute_binary_classification_metrics` já existentes. Isso é feito independentemente do critério de seleção escolhido, para que o histórico de treino fique sempre completo e comparável.

## 4. Regra de seleção

Nova função pura `select_best_checkpoint(candidate, current_best, checkpoint_metric)`:

- `checkpoint_metric="val_loss"` (default, compatível com o comportamento legado): menor `val_loss` vence.
- `checkpoint_metric="val_group_balanced_accuracy"` (usado nesta rodada):
  1. maior `val_group_balanced_accuracy` vence;
  2. empate → maior `val_group_f1` vence;
  3. empate → menor `val_loss` vence;
  4. empate total → mantém o checkpoint já salvo (não há troca).

O teste de teste (`test`) nunca participa da seleção — isso já era estruturalmente verdadeiro no código (`run_cnn_training` nunca carrega o split `test`) e passou a ser coberto por um teste de regressão automatizado (`tests/test_checkpoint_selection.py`), que espiona todas as chamadas de `select_split` durante um treino de ponta a ponta e confirma que `"test"` nunca é solicitado, em nenhum dos dois modos.

## 5. Arquivos alterados/criados

- `src/liverct/models/train_cnn.py` — `checkpoint_metric`/`artifact_prefix` em `CNNTrainingConfig`, `select_best_checkpoint`, `compute_val_group_metrics`, `save_checkpoint` e `run_cnn_training` atualizados.
- `scripts/train_baseline_cnn.py` — novos argumentos `--checkpoint-metric`, `--checkpoint-name`, `--artifact-prefix`.
- `scripts/evaluate_baseline_cnn.py` — novo argumento `--artifact-prefix`, `--checkpoint` agora deriva do prefixo quando omitido.
- `scripts/compare_checkpoint_metrics.py` (novo) — monta a comparação antigo × novo usando predições de grupo já salvas e o IC já calculado por `scripts/run_bootstrap_ci.py`.
- `tests/test_checkpoint_selection.py` (novo) — testes unitários da regra de seleção/desempate e teste de integração com dados sintéticos.
- Artefatos novos, sem sobrescrever nada do baseline antigo: `models/checkpoints/baseline_cnn_group_metric_best.pt`, `reports/tables/baseline_cnn_group_metric_*` (training_history, val_slice_predictions, val_group_predictions, validation_metrics, training_summary, test_slice_predictions, test_group_predictions, test_metrics, vs_statistical_baseline_test), `reports/tables/baseline_cnn_checkpoint_metric_comparison.csv`, e 3 novas linhas em `reports/tables/bootstrap_group_metrics.csv` (`model_label="baseline_cnn"` split `val`, e `model_label="baseline_cnn_group_metric"` splits `val`/`test`).

## 6. Execução real

Treino em CPU (`torch.cuda.is_available() == False`), ~2.459 slices de treino / 538 de validação. O treino novo parou por early stopping na época 12 (melhor época = 7), levando aproximadamente 13 minutos de execução real. Para comparação, o baseline antigo (critério `val_loss`) havia parado na época 16 (melhor época = 11, `val_loss=0,28499`).

Checkpoint novo (`baseline_cnn_group_metric_best.pt`): melhor época = 7, `val_loss=0,30472`, `val_group_balanced_accuracy=0,90909`, `val_group_f1=0,9`.

## 7. Resultados

### 7.1. Validação (33 grupos) — split usado para a própria seleção

| Métrica | Antigo (`val_loss`) | Novo (`val_group_balanced_accuracy`) | Delta |
|---|---:|---:|---:|
| Balanced accuracy | 0,8182 | 0,9091 | +0,0909 |
| Sensibilidade | 0,8182 | 0,8182 | 0,0000 |
| Especificidade | 0,8182 | 1,0000 | +0,1818 |
| F1 | 0,8571 | 0,9000 | +0,0429 |
| ROC-AUC | 0,9339 | 0,9463 | +0,0124 |
| Average precision | 0,9666 | 0,9771 | +0,0105 |
| Matriz de confusão (tn/fp/fn/tp) | 9/2/4/18 | 11/0/4/18 | tn+2, fp−2 |

Na validação, o novo checkpoint eliminou os 2 falsos positivos do antigo (11 healthy corretos em vez de 9), sem alterar a sensibilidade (mesmos 18 verdadeiros positivos, mesmos 4 falsos negativos).

### 7.2. Teste (35 grupos) — split nunca usado para seleção

| Métrica | Antigo (`val_loss`) | Novo (`val_group_balanced_accuracy`) | Delta |
|---|---:|---:|---:|
| Balanced accuracy | 0,8080 | 0,8080 | 0,0000 |
| Sensibilidade | 0,7826 | 0,7826 | 0,0000 |
| Especificidade | 0,8333 | 0,8333 | 0,0000 |
| F1 | 0,8372 | 0,8372 | 0,0000 |
| ROC-AUC | 0,9203 | 0,9167 | −0,0036 |
| Average precision | 0,9624 | 0,9621 | −0,0003 |
| Matriz de confusão (tn/fp/fn/tp) | 10/2/5/18 | 10/2/5/18 | sem mudança |

No teste, a matriz de confusão do novo checkpoint é **idêntica**, valor a valor, à do checkpoint antigo — mesmas 18 verdadeiras esteatoses, mesmos 2 falsos positivos, mesmos 5 falsos negativos, mesmos 10 healthy corretos. As únicas diferenças são pequenas variações negativas em ROC-AUC (−0,0036) e average precision (−0,0003), métricas sensíveis à ordenação contínua das probabilidades, não ao ponto de corte 0,5.

## 8. Intervalos de confiança (bootstrap por grupo, 95%, `n_bootstrap=2000`)

Fonte: `reports/tables/bootstrap_group_metrics.csv`.

| Split | Modelo | Balanced accuracy (IC 95%) | Sensibilidade (IC 95%) | Especificidade (IC 95%) |
|---|---|---|---|---|
| Val | Antigo | 0,8182 [0,6591; 0,9401] | 0,8182 [0,6364; 0,9565] | 0,8182 [0,5455; 1,0000] |
| Val | Novo | 0,9091 [0,8182; 0,9783] | 0,8182 [0,6364; 0,9565] | 1,0000 [1,0000; 1,0000] |
| Teste | Antigo | 0,8080 [0,6643; 0,9375] | 0,7826 [0,6087; 0,9500] | 0,8333 [0,5830; 1,0000] |
| Teste | Novo | 0,8080 [0,6603; 0,9375] | 0,7826 [0,6000; 0,9500] | 0,8333 [0,5830; 1,0000] |

Na validação, os intervalos de balanced accuracy dos dois checkpoints se sobrepõem largamente (o IC do antigo vai até 0,9401, e o IC do novo começa em 0,8182 — exatamente no ponto estimado do antigo). Com apenas 33 grupos de validação, essa sobreposição impede afirmar que a melhora observada na validação é estatisticamente distinguível de ruído amostral, apesar de ser exatamente a métrica que o novo critério foi desenhado para otimizar.

No teste, os dois modelos têm point estimates idênticos e ICs quase idênticos (a pequena diferença no limite inferior de sensibilidade, 0,6087 vs 0,6000, reflete apenas a reamostragem com seed compartilhada sobre dados idênticos de entrada).

Nenhum bootstrap pareado foi calculado sobre o delta em si (isso exigiria um método estatístico novo, fora do escopo desta rodada) — a tabela `baseline_cnn_checkpoint_metric_comparison.csv` deixa essas colunas de IC do delta como `NaN` de propósito, para não sugerir um teste de significância que não foi feito.

## 9. Discussão: trade-off sensibilidade/especificidade

Não houve nenhum trade-off nesta rodada: em nenhum dos dois splits a sensibilidade caiu. Na validação, a melhora de balanced accuracy veio inteiramente de uma melhora de especificidade (2 falsos positivos a menos), sem custo de sensibilidade. No teste, nenhuma métrica baseada em limiar mudou. Isso é consistente com o achado `MET-06` da auditoria (a CNN, na configuração antiga, já perdia para o baseline estatístico em sensibilidade/F1 de grupo no teste) — essa rodada não alterou esse quadro nem para melhor nem para pior no teste.

## 10. Limitações

- Poucos grupos por split (33 validação, 35 teste) — diferenças de 1–2 grupos mudam as métricas visivelmente, e os ICs bootstrap são consequentemente largos.
- Execução com seed única (42); não há replicação com sementes diferentes para separar variação de treino de sinal real.
- Nenhum teste de significância formal (ex. bootstrap pareado) foi calculado sobre o delta entre os dois checkpoints — apenas a sobreposição qualitativa dos ICs de cada modelo foi usada como sinal.
- Threshold fixo em 0,5 nesta rodada — não foi testado se um threshold diferente mudaria a leitura sensibilidade/especificidade para qualquer um dos dois checkpoints.
- O resultado de teste idêntico entre os dois checkpoints é específico desta seed e deste split; não deve ser generalizado como "a escolha do critério de checkpoint não importa" — apenas que, nesta configuração específica, a época selecionada por cada critério (7 vs. 11) levou às mesmas decisões de classificação no teste, com uma leve perda de ranking contínuo (ROC-AUC/AP).

## 11. Conclusão cautelosa

A mudança de critério de seleção de checkpoint (de `val_loss` para `val_group_balanced_accuracy`, com desempate por F1 de grupo e depois por `val_loss`) produziu, nesta rodada, uma melhora visível na própria métrica de validação usada para selecionar o checkpoint (balanced accuracy de grupo: 0,8182 → 0,9091, com eliminação de 2 falsos positivos), sem custo de sensibilidade. Essa melhora, no entanto, tem um intervalo de confiança que se sobrepõe amplamente ao do checkpoint antigo, dado o número pequeno de grupos de validação — não pode ser tratada como uma melhora estatisticamente robusta a partir de uma única rodada com seed única.

No teste — o split que de fato importa para avaliar generalização, e que nunca participou da seleção — as duas versões do modelo produziram exatamente as mesmas decisões de classificação a 0,5 de limiar (mesma matriz de confusão, mesma balanced accuracy, sensibilidade, especificidade e F1), com uma variação muito pequena e na direção negativa em ROC-AUC e average precision.

Portanto: o critério de seleção por métrica de grupo é uma mudança metodologicamente mais coerente com a forma como o projeto relata seus resultados (por grupo, não por `val_loss` agregado), e atende ao critério de sucesso definido a priori (balanced accuracy de teste ≥ 0,8080 e sensibilidade de teste ≥ 0,7826 — ambos exatamente iguais ao valor de referência). Mas, nesta rodada específica, essa mudança não produziu uma melhora mensurável de generalização no teste — apenas manteve o desempenho já observado. Não há evidência, nesta rodada, para afirmar que o novo critério de checkpoint produz um modelo "melhor" no sentido de generalização; há evidência de que ele é pelo menos equivalente no teste e potencialmente mais estável na validação, uma leitura que exigiria réplicas com outras seeds para ser confirmada.
