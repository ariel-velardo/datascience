# Playbook de Design de Sistemas de ML Causal em Produção

## 1. Objetivo

Este playbook define padrões de projeto para transformar análises causais e modelos de ML em sistemas confiáveis, testáveis, monitoráveis e acionáveis.

Ele se aplica a projetos de:

- predição;
- inferência causal;
- uplift modeling;
- experimentação;
- otimização de decisão;
- scoring em lote;
- scoring online;
- políticas operacionais.

---

## 2. Separação de camadas

Um sistema de ML causal deve separar:

1. Camada de dados.
2. Camada de features.
3. Camada de modelagem.
4. Camada causal.
5. Camada de decisão.
6. Camada de monitoramento.
7. Camada de comunicação.

---

## 3. Pipeline de ingestão

Responsável por:

- ler fontes brutas;
- validar existência;
- validar schema;
- padronizar tipos;
- registrar volumes;
- preservar dados originais;
- sinalizar erros.

Não deve:

- criar target;
- aplicar regra causal complexa;
- filtrar dados sem rastreabilidade.

---

## 4. Pipeline de normalização

Responsável por:

- padronizar chaves;
- parsear campos aninhados;
- normalizar datas;
- tratar outliers mascarados;
- preservar granularidade original;
- criar views limpas.

---

## 5. Feature pipeline

Responsável por:

- calcular features pré-tratamento;
- respeitar janelas temporais;
- criar agregações históricas;
- gerar variáveis reutilizáveis;
- evitar target leakage;
- manter lógica compatível entre treino e scoring.

Regra:

Toda feature deve ser reproduzível no momento real da decisão.

---

## 6. Training pipeline

Responsável por:

- receber ABT validada;
- aplicar split temporal;
- treinar baseline;
- treinar modelo principal;
- avaliar métricas;
- registrar artefatos;
- documentar assumptions.

---

## 7. Causal pipeline

Responsável por:

- definir tratamento;
- definir controle;
- definir outcome;
- definir estimando;
- checar assumptions;
- estimar efeito;
- avaliar heterogeneidade;
- reportar limitações.

---

## 8. Scoring pipeline

Responsável por:

- aplicar modelo em população elegível;
- gerar score;
- gerar ranking;
- registrar versão do modelo;
- gerar logs de decisão;
- não recalcular features com lógica diferente da usada no treino.

---

## 9. Decision pipeline

Responsável por:

- converter score/efeito em ação;
- aplicar elegibilidade;
- aplicar restrições;
- calcular custo;
- calcular valor esperado;
- aplicar orçamento;
- gerar decisão final;
- gerar motivo da decisão.

---

## 10. Monitoring pipeline

Responsável por monitorar:

- volume de dados;
- schema;
- missing;
- drift de features;
- drift de tratamento;
- drift de outcome;
- distribuição de scores;
- estabilidade do efeito;
- performance de negócio;
- aderência operacional;
- custo;
- ROI;
- fairness, quando aplicável.

---

## 11. Contratos de dados

Cada tabela importante deve ter contrato:

- nome;
- descrição;
- granularidade;
- chave primária;
- colunas obrigatórias;
- tipos;
- regra de nulos;
- regra temporal;
- cardinalidade;
- validações bloqueantes;
- validações de alerta;
- responsável;
- frequência de atualização.

---

## 12. Padrão de funções

Preferir funções pequenas e com responsabilidade única:

- load_raw_data;
- validate_raw_schema;
- parse_events;
- normalize_entities;
- build_decision_panel;
- build_pre_treatment_features;
- build_post_treatment_targets;
- build_abt;
- validate_abt;
- train_baseline;
- estimate_effect;
- evaluate_effect;
- simulate_policy;
- validate_policy.

Cada função deve ter:

- entrada clara;
- saída clara;
- validação mínima;
- nome que revele intenção;
- ausência de efeitos colaterais desnecessários.

---

## 13. Notebook como narrativa

O notebook deve conter:

- contexto;
- definição do problema;
- decisões metodológicas;
- chamadas principais;
- validações;
- tabelas de resumo;
- gráficos;
- interpretação;
- limitações.

O notebook não deve virar depósito de lógica complexa.

Mover para funções/módulos:

- parsing repetitivo;
- queries longas;
- validações reutilizáveis;
- cálculo de métricas;
- simulações financeiras;
- regras de decisão.

---

## 14. Validação em camadas

### Dados brutos

- arquivos existem;
- volume não zero;
- schema esperado.

### Dados limpos

- tipos corretos;
- chaves válidas;
- eventos válidos;
- sem perda indevida de linhas.

### ABT

- chave única;
- tratamento e controle presentes;
- features pré-tratamento;
- targets pós-tratamento;
- sem variáveis proibidas.

### Modelo

- split adequado;
- baseline;
- métrica compatível;
- estabilidade;
- limitações.

### Política

- orçamento respeitado;
- custo não negativo;
- no máximo uma ação por unidade;
- decisão auditável.

---

## 15. Versionamento

Versionar:

- dados;
- ABT;
- features;
- modelo;
- estimador;
- política;
- thresholds;
- regras de elegibilidade;
- métricas.

Toda recomendação deve ser reproduzível.

---

## 16. Batch scoring versus online scoring

### Batch

Adequado quando:

- decisão é periódica;
- latência baixa não é necessária;
- features são majoritariamente históricas;
- operação consome listas.

### Online

Adequado quando:

- decisão acontece em tempo real;
- contexto muda rapidamente;
- há necessidade de personalização imediata;
- latência é requisito crítico.

---

## 17. Rollback

Todo sistema decisional deve prever:

- rollback de modelo;
- rollback de política;
- fallback por regra;
- bloqueio de campanha;
- interrupção por métrica de risco;
- auditoria de decisões passadas.

---

## 18. Critério de produção

Um projeto só deve ser considerado pronto para produção quando tiver:

- dados validados;
- ABT reproduzível;
- modelo ou estimador documentado;
- métrica compatível com decisão;
- política auditável;
- monitoramento mínimo;
- plano de rollback;
- limitações explícitas.