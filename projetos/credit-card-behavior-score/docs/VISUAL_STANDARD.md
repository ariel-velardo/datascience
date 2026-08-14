# Padrão Visual do Projeto

## Objetivo

Manter consistência visual entre:

- análise exploratória;
- notebook técnico;
- gráficos executivos;
- apresentação final.

## Biblioteca

Plotly será a biblioteca principal de visualização.

## Paleta

| Papel | Cor |
|---|---|
| Principal | #54B69B |
| Secundária | #A7DCDA |
| Lima | #DDE461 |
| Amarelo | #F4E13D |
| Verde | #009840 |
| Destaque | #F850D8 |
| Preto | #111111 |
| Cinza escuro | #4B5563 |
| Cinza | #9CA3AF |
| Cinza claro | #E5E7EB |
| Fundo | #FFFFFF |

## Uso das Cores

### Principal

Usar como cor padrão da análise.

### Secundária

Usar para séries secundárias, comparação ou benchmark.

### Amarelo

Reservar para informações que mereçam destaque.

### Magenta

Reservar principalmente para:

- alertas;
- deteriorações;
- anomalias;
- pontos que exijam atenção.

### Cinza

Utilizar para contexto, referência ou elementos de menor prioridade visual.

## Títulos

Durante a exploração, títulos podem ser descritivos.

Exemplo:

Taxa do evento por safra

Nos gráficos executivos, sempre que os dados permitirem, os títulos devem comunicar o principal insight.

Exemplo:

Taxa do evento permanece estável nas safras mais recentes

Nunca antecipar uma conclusão no título antes de confirmá-la nos dados.

## Eixos

Os eixos devem:

- possuir unidade clara;
- utilizar percentual quando pertinente;
- evitar excesso de casas decimais;
- evitar abreviações ambíguas.

## Legendas

Evitar legendas quando a informação puder ser identificada diretamente.

Quando necessárias, priorizar orientação horizontal acima do gráfico.

## Grid

Utilizar apenas grids discretos quando ajudarem a leitura.

Evitar excesso de linhas.

## Interatividade

Durante a análise, utilizar quando agregar valor:

- hover;
- zoom;
- seleção;
- tooltips.

Evitar interatividade puramente decorativa.

## Exportação

### HTML

Utilizado para:

- exploração;
- revisão;
- preservação da interatividade.

### PNG

Utilizado para:

- apresentação executiva;
- documentos estáticos;
- materiais finais.

## Dimensões

### Análise

1000 x 550

### Apresentação

Aproximadamente:

1200 x 675

## Tipos de Gráficos Preferenciais

### Evolução temporal

Linha com marcadores.

### Comparação de categorias

Barras horizontais ou verticais.

### Composição temporal de múltiplas variáveis

Heatmap.

### Distribuição

Histograma, boxplot ou ECDF conforme a pergunta analítica.

### Comparação de modelos

Barras ou dumbbell.

### Score versus risco

Linha ou barras ordenadas por faixa.

### Estabilidade

Linhas temporais e heatmaps.

## Evitar

- gráficos 3D;
- pizzas quando barras comunicarem melhor;
- excesso de cores;
- excesso de rótulos;
- gráficos redundantes;
- visualizações sem pergunta analítica;
- elementos puramente decorativos.

## Princípio Geral

Cada gráfico deve existir porque ajuda a responder uma pergunta.

A sequência deve ser:

pergunta -> análise -> visualização -> interpretação.
