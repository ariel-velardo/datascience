# Uso de Inteligência Artificial Generativa

## Objetivo

Ferramentas de Inteligência Artificial Generativa são utilizadas como apoio de produtividade, implementação e revisão durante o desenvolvimento do projeto.

Essas ferramentas não substituem validação metodológica nem julgamento analítico.

---

## Ferramentas

Ferramentas que poderão ser utilizadas:

- ChatGPT;
- OpenAI Codex;
- Claude Code;
- Gemini.

---

## Possíveis Usos

A IA poderá auxiliar em:

- estruturação do projeto;
- geração de código;
- refatoração;
- geração de testes;
- documentação;
- sugestões de visualização;
- revisão de código;
- depuração;
- estruturação da apresentação;
- revisão crítica das análises.

---

## Decisões Sob Controle Humano

As seguintes decisões exigem validação humana:

- formulação do problema de negócio;
- interpretação da variável alvo;
- desenho temporal das amostras;
- avaliação de vazamento;
- tratamento de valores especiais;
- seleção de variáveis;
- escolha do modelo;
- aceitação de hiperparâmetros;
- interpretação das métricas;
- transformação em score;
- definição das faixas de risco;
- conclusões de estabilidade;
- recomendações de negócio.

---

## Controles de Validação

Resultados produzidos ou sugeridos por IA deverão ser verificados utilizando:

- dados originais;
- código executado;
- resultados estatísticos;
- documentação do projeto;
- testes de reprodutibilidade.

Nenhum resultado numérico deverá ser incluído na entrega final apenas porque foi produzido ou sugerido por uma ferramenta de IA.

---

## Cuidados com os Dados

A base contém variáveis anonimizadas.

As ferramentas de IA não devem atribuir significados de negócio que não estejam documentados.

Informações desconhecidas deverão permanecer explicitamente como desconhecidas.

---

## Rastreabilidade

Contribuições relevantes deverão ser registradas abaixo.

| Data | Ferramenta | Atividade | Validação humana |
|---|---|---|---|
| 2026-08-14 | ChatGPT | Estruturação inicial do projeto e planejamento metodológico | Revisado |
| 2026-08-14 | OpenAI Codex | Implementação, execução e validação da Etapa 1 — auditoria dos dados | Sujeito à revisão humana |
| 2026-08-14 | OpenAI Codex | Implementação, execução e validação temporal, triagem de leakage e proposta de split Treino/Validação/OOT | Sujeito à revisão humana |
| 2026-08-14 | OpenAI Codex | Revisão corretiva da auditoria e do diagnóstico temporal, auditoria do PSI, comparação de splits e atualização do gate metodológico | Sujeito à revisão humana |
| 2026-08-15 | OpenAI Codex | Construção, execução e validação do notebook técnico final até a comparação entre Regressão Logística e CatBoost | Validação humana pendente para decisões de features, champion, interpretações e decisões de negócio |
| 2026-08-16 | OpenAI Codex | Último gate de desenvolvimento: tuning controlado, robustez de features, calibração, explicabilidade e configuração candidata à avaliação OOT | Validação humana pendente |
| 2026-08-16 | OpenAI Codex | Fechamento humano do candidato pré-OOT com 13 features, `var12_estado`, configuração congelada e registro reprodutível de versões | Validação humana aplicada às decisões; abertura do OOT ainda pendente |
| 2026-08-16 | Claude Code | Revisão independente + implementação das correções pré-OOT | Validação humana pendente |
| 2026-08-16 | OpenAI Codex | Avaliação final OOT do candidato congelado, com protocolo definido antes da primeira predição OOT nesta execução, métricas, incerteza, estabilidade, calibração, lift, PSI e SHAP | Validação humana pendente |
| 2026-08-16 | OpenAI Codex | Correção da narrativa OOT, alinhamento das features finais, migração de `var12_estado` e implementação testável da fórmula log-odds/PDO do Behavior Score | Modelo e OOT preservados; Base Score, PDO e Base Odds pendentes de decisão humana |
| A definir | Gemini | A definir | A definir |
