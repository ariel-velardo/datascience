# Experimentos com ROI hepatica aproximada e papel futuro do nnU-Net

## 1. Por que o experimento com ROI e o proximo passo viavel

O baseline CNN 2D atual classifica imagens JPEG completas em duas classes:

- `Healthy`;
- `Hepatic_Steatosis`.

Esse baseline respeita a regra metodologica principal do projeto: treino, validacao e teste sao separados por `inferred_group_id`, nunca por slice aleatorio.

O proximo passo viavel e comparar a imagem inteira com transformacoes simples que restringem parcialmente a area visual usada pela CNN. Isso permite investigar se parte do desempenho depende de sinal plausivel na regiao hepatica ou de atalhos visuais fora dessa regiao.

Este experimento e exploratorio. A ROI aproximada nao e segmentacao hepatica validada, nao e mascara clinica e nao deve ser usada para inferencia diagnostica.

## 2. O que o experimento testa em relacao ao baseline com imagem inteira

As abordagens propostas sao:

1. `full_image`: usa a imagem inteira, equivalente ao baseline visual atual.
2. `roi_crop_aproximada`: aplica um recorte fixo e configuravel em torno de uma regiao hepatica aproximada.
3. `roi_mask_heuristica`: aplica uma mascara geometrica simples para reduzir fundo e regioes fora da ROI aproximada.

A comparacao testa se a performance muda quando o modelo ve menos bordas, fundo preto, musculatura, artefatos JPEG ou outras regioes fora da area esperada do figado.

Possiveis leituras:

- desempenho parecido entre `full_image` e ROI pode indicar que ha sinal util dentro da regiao aproximada;
- queda forte com ROI pode sugerir que o baseline usa informacao fora da ROI, mas isso nao prova atalho;
- melhora com ROI pode indicar reducao de ruido visual, mas ainda exige validacao;
- resultados instaveis podem refletir amostra pequena, JPEG, hiperparametros ou fragilidade da propria heuristica.

Separacao metodologica:

- analise descritiva: verificar exemplos visuais, distribuicao de slices/grupos e integridade do split;
- analise preditiva: treinar e comparar CNNs com diferentes transformacoes de entrada;
- analise causal: nao e realizada nesta etapa, pois nao ha desenho causal, randomizacao, mascara validada ou controle clinico suficiente.

## 3. Limitacoes de usar JPEG sem segmentacao hepatica validada

As imagens disponiveis estao em JPEG. Isso traz limitacoes importantes:

- nao ha valores HU confiaveis;
- ha compressao com perda;
- nao ha metadados DICOM sobre scanner, protocolo, fase ou janela;
- nao ha volume 3D estruturado;
- nao ha mascara hepatica de referencia;
- a orientacao e o enquadramento podem variar;
- o `inferred_group_id` e um agrupamento tecnico, nao uma identificacao clinica validada.

Por isso, a ROI aproximada deve ser tratada como uma intervencao tecnica para teste de sensibilidade do pipeline, nao como localizacao anatomica confiavel.

Tambem nao se deve converter JPEG para simular DICOM ou NIfTI. Essa conversao nao recupera informacao perdida nem cria metadados clinicos reais.

## 4. Por que nnU-Net e relevante para segmentacao medica

O nnU-Net e relevante porque foi desenhado para segmentacao supervisionada de imagens medicas. Ele automatiza varias decisoes de pre-processamento, configuracao de rede, treinamento e inferencia para tarefas de segmentacao, especialmente em dados volumetricos como CT e MRI.

Em um cenario adequado, o nnU-Net poderia ser usado para segmentar o figado e gerar mascaras anatomicamente mais plausiveis do que uma ROI fixa ou mascara geometrica.

## 5. Por que nnU-Net nao substitui diretamente a CNN de classificacao

O problema atual do projeto e classificacao binaria:

- entrada: imagem JPEG de CT hepatica;
- saida: `Healthy` ou `Hepatic_Steatosis`.

O nnU-Net resolve outra tarefa principal: segmentacao supervisionada pixel/voxel a pixel/voxel. Ele nao substitui diretamente a CNN classificadora porque sua saida esperada e uma mascara, nao uma classe diagnostica.

Um pipeline futuro poderia usar segmentacao como etapa anterior a classificacao, por exemplo:

- segmentar o figado;
- recortar ou mascarar a regiao hepatica;
- treinar uma CNN classificadora usando apenas essa regiao;
- comparar com a imagem inteira.

Mesmo nesse caso, a classificacao de esteatose continuaria precisando de avaliacao propria.

## 6. Dados necessarios para testar nnU-Net corretamente

Para testar nnU-Net de forma metodologicamente correta seriam necessarios:

- dados medicos em formato adequado, preferencialmente DICOM, NIfTI ou outro formato sem perda;
- volumes ou imagens com geometria preservada;
- mascaras hepaticas de referencia produzidas ou validadas por especialista;
- separacao de treino, validacao e teste por paciente, exame ou grupo clinicamente consistente;
- protocolo claro de avaliacao da segmentacao, como Dice, IoU, sensibilidade de mascara e analise visual;
- documentacao da origem dos dados e dos criterios de anotacao.

Nao e adequado inventar mascara clinica a partir de JPEG, nem converter JPEG para simular um formato medico sem perda.

## 7. Comparacao futura recomendada

Uma comparacao futura mais forte poderia seguir esta sequencia:

1. `full_image`: CNN com imagem inteira.
2. `roi_crop_aproximada`: CNN com recorte heuristico aproximado.
3. `roi_mask_heuristica`: CNN com mascara geometrica simples, se a heuristica se mostrar estavel.
4. `figado_segmentado_mascara_validada`: CNN treinada com mascara hepatica validada por referencia.
5. `pipeline_nnunet`: segmentacao supervisionada do figado com nnU-Net, seguida de classificacao binaria com um classificador separado.

Todas as comparacoes devem manter a regra de split por grupo e avaliar metricas por slice e por grupo. O teste deve permanecer isolado ate a etapa final de avaliacao.

## 8. Execucao implementada nesta etapa

Arquivos principais:

    src/liverct/features/roi_transforms.py
    src/liverct/models/roi_experiments.py
    scripts/run_roi_experiments.py
    notebooks/08_experimentos_roi_hepatica.ipynb

Saidas previstas:

    reports/tables/roi_experiment_comparison.csv
    reports/figures/roi_examples/

O script cria automaticamente os diretorios de saida. Checkpoints ficam em:

    models/checkpoints/roi_experiments/

Esses checkpoints sao artefatos derivados e nao devem ser versionados.

Em ambiente CPU, a execucao pode ser retomada sem repetir abordagens ja finalizadas:

    python scripts/run_roi_experiments.py --resume-existing

## 9. Grad-CAM para ROI

O projeto ja possui uma implementacao de Grad-CAM para `SimpleCNN2D`.

Nesta etapa, a geracao automatica de `reports/figures/gradcam_roi/` nao foi incluida como saida obrigatoria porque uma comparacao correta exigiria selecionar casos comparaveis para cada abordagem e garantir que o Grad-CAM seja calculado sobre a mesma transformacao usada no treinamento de cada modelo.

Isso pode ser feito em etapa posterior reaproveitando `src/liverct/explainability/gradcam.py`, mas sem misturar checkpoints, transformacoes e casos selecionados de forma ad hoc.
