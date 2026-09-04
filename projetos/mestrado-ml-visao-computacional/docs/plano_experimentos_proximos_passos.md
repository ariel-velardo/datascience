# Plano de próximos experimentos

> **Aviso importante:** este documento propõe experimentos futuros para um estudo exploratório e **não validado clinicamente**. Nenhuma hipótese aqui é um resultado; nenhum critério de sucesso deve ser lido como meta clínica. Todos os números citados como referência vêm de artefatos já gerados no repositório (`reports/tables/`) — nenhum é inventado.

## 1. Contexto e propósito deste documento

Este documento é o companheiro narrativo de [`reports/tables/plano_experimentos_priorizado.csv`](../reports/tables/plano_experimentos_priorizado.csv). A tabela é a fonte de verdade estruturada (uma linha por experimento, com hipótese, mudança necessária, métrica principal, risco, critério de sucesso e arquivos afetados); este documento expande o raciocínio por trás da priorização e o sequenciamento recomendado.

Os experimentos aqui derivam diretamente dos achados catalogados em [`reports/tables/auditoria_achados_modelo.csv`](../reports/tables/auditoria_achados_modelo.csv) e discutidos em [`auditoria_modelo_estado_da_arte.md`](auditoria_modelo_estado_da_arte.md). Cada experimento referencia o(s) ID(s) de achado que o motivam (ver seção 6).

Nem todo achado da auditoria virou um experimento aqui: achados de correção pontual sem hipótese testável (ex. `REPO-04`, fixar versões em `requirements.txt`; `MET-05`, consolidar duas funções de agregação duplicadas) ficam só na tabela de achados — não geram uma linha de experimento, porque não há nada a "testar", apenas a corrigir.

## 2. Critérios de priorização

A ordem da tabela reflete esforço e impacto sob duas premissas explícitas do projeto:

- **Dataset pequeno**: 157 grupos de treino, 33 de validação, 35 de teste. Isso favorece experimentos que reaproveitam predições/artefatos já salvos (bootstrap, calibração, quantificação de Grad-CAM) sobre experimentos que exigem novo treino.
- **Sem cluster GPU**: o ambiente é CPU-only (nenhuma dependência de CUDA foi encontrada em uso ativo). Isso penaliza fortemente experimentos de retreino demorado, especialmente o MIL (`batch_size=1`, um bag por vez).

Por isso, os experimentos 1–4 do plano (bootstrap, calibração, correção do notebook 08, testes automatizados) são todos de esforço baixo e não exigem nenhum retreino — são o caminho mais rápido para fortalecer o rigor do que já existe. Os experimentos 5–8 exigem retreino, mas de um modelo pequeno (a CNN tem ~23,6 mil parâmetros); o experimento 8 (MIL) é o mais caro e o de menor prioridade relativa, coerente com seu status de apêndice experimental no projeto.

## 3. Experimentos priorizados

A tabela completa está em `reports/tables/plano_experimentos_priorizado.csv`; abaixo, um resumo narrativo na mesma ordem.

**1. Bootstrap por grupo (IC 95%) sobre métricas já existentes.** Nenhuma das comparações já reportadas no projeto (CNN vs. baseline estatístico, os 3 braços de ROI, as 3 variantes de MIL) vem hoje com intervalo de confiança. Com 33–35 grupos por split, diferenças de poucos centésimos de balanced accuracy podem ser ruído. Este experimento não treina nada novo: reamostra com reposição os grupos já presentes em `reports/tables/*_group_predictions.csv` e recalcula a métrica a cada reamostra.

**2. Calibração de probabilidade.** O projeto não tem nenhum código de calibração (achado `MET-03`). Como as probabilidades de grupo já são usadas para ordenar casos (análise de erro, seleção de casos para Grad-CAM), vale saber se elas são bem calibradas antes de confiar nelas para qualquer uso além do threshold binário.

**3. Corrigir `PROJECT_ROOT` do notebook 08 — especificado, não aplicado nesta etapa.** É a correção de menor esforço de todo o plano: o diagnóstico é exato (achado `REPO-01`) e a correção já existe, testada, no notebook 09. Está listada aqui como um experimento formal (não uma edição direta) porque o projeto exige aprovação explícita antes de alterar notebooks principais.

**4. Testes automatizados para invariantes de segurança.** A auditoria confirmou que a lógica de split por grupo e de bag do MIL está correta hoje, mas sem nenhuma proteção automática contra regressão (achado `REPO-03`). É barato e de alto valor: dataframes sintéticos pequenos bastam para exercitar os casos de borda relevantes.

**5. Critério de checkpoint por métrica balanceada em vez de `val_loss`.** A curva de `val_loss` do baseline CNN é visivelmente ruidosa (achado `CNN-02`); selecionar o checkpoint por uma métrica mais alinhada ao que o projeto realmente reporta (balanced accuracy/F1 de grupo) é uma mudança pequena de código com potencial de melhorar a métrica que importa, sem mudar a arquitetura.

**6. Aumento de dados leve na CNN 2D.** O hook para `image_transform` já existe no código e nunca é usado (achado `CNN-01`). Flips horizontais e rotações pequenas são baratos de testar e diretamente relevantes para reduzir dependência de padrões de posição fixos, dado o tamanho pequeno do conjunto de treino.

**7. Fração do Grad-CAM dentro da ROI + sanity check de pesos aleatorizados.** A auditoria já encontrou evidência visual qualitativa de ativação fora do fígado em alguns casos (achado `GRC-01`). Este experimento sistematiza essa observação sobre os 66 casos já selecionados, sem precisar retreinar nada.

**8. Retreinar MIL com orçamento realista + backbone pré-treinado.** A causa raiz do desempenho fraco do MIL já está identificada com precisão (achado `MIL-01`: 1–2 épocas efetivas de treino). Este é o experimento mais caro do plano — treino CPU-only com `batch_size=1` é lento — e por isso vem por último, apesar de a hipótese ser a mais bem fundamentada de todas.

Três linhas adicionais na tabela ficam explicitamente **bloqueadas** por dependência de recursos que o projeto não tem hoje, mantidas para que o roadmap seja honesto sobre o que falta, não para serem executadas em seguida: segmentação hepática real (`dependente de segmentação`), re-basear em valores HU via DICOM/NIfTI (`dependente de DICOM/NIfTI`) e validação externa (`dependente de novos dados`).

## 4. Sequenciamento recomendado

1. **Rigor estatístico primeiro (experimentos 1–2).** Calcular IC e calibração antes de decidir qualquer retreino, porque o resultado pode mudar o que "sucesso" significa para os experimentos seguintes — por exemplo, se o IC mostrar que a diferença entre `roi_crop_aproximada` e `full_image` (achado `ROI-02`) não é distinguível de ruído, isso muda a prioridade de investir mais tempo ajustando a ROI.
2. **Correções de baixo risco em paralelo (experimentos 3–4).** A especificação da correção do notebook 08 e a criação de testes automatizados não dependem de nenhum resultado dos experimentos 1–2 e podem ser feitas a qualquer momento.
3. **Mudanças na CNN antes do retreino do MIL (experimentos 5–6 antes do 8).** O MIL reutiliza a mesma lógica de split e de agregação por grupo que a CNN; faz sentido estabilizar o critério de seleção de checkpoint e testar aumento de dados na CNN primeiro, para não gastar o orçamento de retreino do MIL (o mais caro) antes de decisões que podem mudar a linha de base de comparação.
4. **Grad-CAM quantitativo (experimento 7) pode rodar a qualquer momento** depois do experimento 1, já que também é só pós-processamento sobre artefatos existentes.
5. **MIL por último (experimento 8)**, precisamente porque é o mais caro e o resultado dos experimentos 1–2 pode mudar como seus resultados devem ser interpretados (ex. um IC amplo em cima de só 35 grupos de teste limita quanto uma melhora no MIL pode ser considerada "real").

## 5. Como não superestimar resultados de experimentos futuros

- Todo critério de sucesso na tabela é definido **relativo a um número já existente e citado** (ex. "balanced accuracy de grupo igual ou superior a 0,8080"), nunca como um alvo absoluto inventado (ex. nunca "atingir 90% de acurácia").
- Nenhum resultado de nenhum experimento futuro deste plano deve ser usado para validar uso clínico, diagnóstico automático ou qualquer decisão sobre pacientes reais — o projeto continua sendo, em qualquer cenário, um estudo exploratório sobre um único dataset público, sem validação externa.
- Uma melhora de métrica em um experimento futuro, isoladamente, não é evidência forte sem o intervalo de confiança do experimento 1 — a ordem de execução da seção 4 existe justamente para evitar essa armadilha.
- Ao reportar qualquer resultado novo, manter a mesma separação já praticada no projeto entre nível de slice e nível de grupo, e preferir sempre o nível de grupo como métrica principal de decisão.

## 6. Referências cruzadas

| Achado(s) da auditoria | Experimento correspondente | Seção do doc de auditoria |
|---|---|---|
| `MET-03` | 1. Bootstrap por grupo | 3.4 |
| `MET-03` | 2. Calibração de probabilidade | 3.4 |
| `REPO-01` | 3. Corrigir `PROJECT_ROOT` do notebook 08 | 1.2 |
| `REPO-03` | 4. Testes automatizados | 1.2, 9 |
| `MET-01`, `CNN-02` | 5. Critério de checkpoint balanceado | 3.6, 4.2, 4.4 |
| `CNN-01`, `DAT-02` | 6. Aumento de dados leve | 4.3, 4.5 |
| `GRC-01`, `GRC-02`, `ROI-01` | 7. Fração do Grad-CAM dentro da ROI | 5.3, 5.4 |
| `MIL-01`, `MIL-02` | 8. Retreinar MIL | 7.3, 7.4, 7.6 |
| — | Segmentação hepática real (bloqueado) | 6.5, 8.2 |
| — | DICOM/NIfTI + HU (bloqueado) | 8.2 |
| — | Validação externa (bloqueado) | 8.2 |
