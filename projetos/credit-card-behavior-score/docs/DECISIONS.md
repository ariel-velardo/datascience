# Registro de Decisões

Este documento registra decisões metodológicas e de engenharia do projeto.

Nenhum agente de IA deverá alterar silenciosamente decisões registradas aqui.

---

## D001 — Nome neutro do projeto

Decisão:

Utilizar:

credit-card-behavior-score

Evitar nomes de empresas em:

- caminho do projeto;
- módulos Python;
- notebooks;
- README público;
- commits.

Motivo:

Manter o projeto genérico, reutilizável e adequado para portfólio profissional.

Status:

Aceito.

---

## D002 — Enquadramento como Behavior Score

Decisão:

Tratar o problema como score comportamental de risco de crédito para clientes já existentes de cartão.

Status:

Aceito.

---

## D003 — Semântica da variável alvo

Decisão:

Não inventar o significado de Ever30Mob6 enquanto não existir documentação que confirme sua definição.

Utilizar preferencialmente:

"evento adverso"

ou

"evento de risco".

Status:

Aceito.

---

## D004 — Validação temporal

Decisão:

Utilizar separação cronológica entre:

treino;

validação;

teste fora do tempo — OOT.

Não utilizar divisão aleatória como desenho principal.

As safras exatas serão definidas depois da auditoria dos dados.

Status:

Aceito.

---

## D005 — Identificadores

Decisão:

Não utilizar como variáveis preditivas:

- index;
- id.

A safra será utilizada principalmente para controle temporal e estabilidade.

Status:

Aceito.

---

## D006 — Estratégia de modelos

Decisão inicial:

1. Regressão Logística como benchmark;
2. CatBoost como challenger não linear.

Outros modelos exigirão justificativa analítica.

Status:

Aceito.

---

## D007 — Desbalanceamento

Decisão:

Não aplicar automaticamente:

- SMOTE;
- undersampling;
- oversampling.

Primeiro avaliar o desbalanceamento e o comportamento dos modelos na distribuição natural da população.

Status:

Aceito.

---

## D008 — Seleção de variáveis

Decisão:

Não remover ou selecionar variáveis utilizando apenas uma métrica.

Considerar conjuntamente:

- sinal preditivo;
- redundância;
- estabilidade;
- risco de vazamento;
- interpretabilidade.

Status:

Aceito.

---

## D009 — Direção do score

Decisão:

Escala:

0 a 1000.

Score maior significa menor risco estimado.

Status:

Aceito.

---

## D010 — Versionamento dos dados

Decisão:

Bases raw, interim e processed não serão versionadas no Git.

Status:

Aceito.

---

## D011 — Ativos de marca

Decisão:

Imagens e logos utilizados como referência visual permanecerão locais.

O código público utilizará apenas uma identidade visual genérica baseada em uma paleta definida no projeto.

Status:

Aceito.

---

## D012 — Consistência visual

Decisão:

Utilizar um único módulo reutilizável de visualização.

Gráficos do notebook final e da apresentação deverão compartilhar:

- tipografia;
- cores;
- padrões de títulos;
- padrões de exportação.

Status:

Aceito.

---

## D013 — Notebook final

Decisão:

Durante o desenvolvimento poderão existir múltiplos notebooks.

Artefato técnico final:

notebooks/credit_card_behavior_score.ipynb

O notebook deverá ser autocontido e estar completamente executado.

Status:

Aceito.

---

## D014 — Governança de IA Generativa

Decisão:

Ferramentas de IA poderão apoiar:

- implementação;
- revisão;
- documentação;
- testes;
- comunicação.

A validação humana continuará obrigatória para decisões metodológicas e conclusões.

Status:

Aceito.

---

## D015 — Idioma do projeto

Decisão:

Documentação, análises, interpretações, títulos dos gráficos, nomes de variáveis internas e funções desenvolvidas neste projeto deverão ser preferencialmente escritos em português.

Exceções:

- nomes originais das colunas da base;
- nomes oficiais de bibliotecas;
- nomes oficiais de algoritmos ou métricas quando a tradução prejudicar clareza;
- nomes estruturais já estabelecidos no repositório.

Status:

Aceito.

---

## D016 — Biblioteca de visualização

Decisão:

Utilizar Plotly como biblioteca principal de visualização do projeto.

Os notebooks deverão priorizar gráficos interativos e os mesmos objetos gráficos poderão ser exportados para formatos estáticos para utilização na apresentação executiva.

Matplotlib e Seaborn não serão utilizados como padrão.

Motivos:

- interatividade durante a exploração;
- qualidade visual adequada para comunicação executiva;
- reutilização entre notebook e apresentação;
- padronização visual centralizada;
- redução da necessidade de reconstruir gráficos posteriormente.

A confiabilidade das análises continuará dependendo da metodologia, dos dados e das métricas, e não da biblioteca de visualização.

Status:

Aceito.
