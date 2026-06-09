04_playbook_otimizacao_roi_politica_decisao# Playbook de Otimização, ROI e Política de Decisão

## 1. Objetivo

Este playbook orienta a transformação de estimativas preditivas ou causais em decisões operacionais.

A saída de um projeto aplicado não deve ser apenas um score. Deve ser uma política de decisão:

- quem tratar;
- qual ação aplicar;
- quando aplicar;
- qual custo esperado;
- qual benefício esperado;
- qual restrição respeitar;
- qual risco aceitar;
- qual fallback usar.

---

## 2. Separar efeito de decisão

A estimativa causal responde:

“Qual é o efeito esperado da intervenção?”

A política de decisão responde:

“O que fazer com esse efeito, considerando custo, restrição e risco?”

Nunca assumir que todo efeito positivo implica ação.

---

## 3. Valor incremental esperado

Para cada unidade i e tratamento k:

valor_incremental = efeito_incremental × valor_do_outcome

Quando houver custo:

valor_liquido = valor_incremental - custo_esperado

Quando houver margem:

valor_liquido = efeito_incremental × margem_esperada - custo_esperado

---

## 4. Custo esperado

O custo da ação pode depender de:

- valor nominal do incentivo;
- probabilidade de resgate;
- canal;
- custo operacional;
- custo de atendimento;
- custo de risco;
- custo de oportunidade;
- restrição de capacidade.

Exemplo:

custo_esperado = valor_cupom × probabilidade_resgate

---

## 5. ROI incremental

ROI = valor_liquido_incremental / custo_esperado

Cuidados:

- custo zero exige tratamento separado;
- ROI alto com baixo volume pode ser irrelevante;
- valor líquido negativo deve bloquear ação;
- ROI deve ser interpretado junto com impacto absoluto.

---

## 6. Restrições de decisão

Possíveis restrições:

- orçamento total;
- orçamento por campanha;
- capacidade operacional;
- limite por canal;
- frequência máxima de contato;
- elegibilidade;
- risco regulatório;
- fairness;
- estoque;
- margem mínima;
- limite por cliente;
- limite por região.

---

## 7. Problema de alocação

Quando há múltiplos tratamentos, a decisão pode ser formulada como otimização:

Maximizar:

Σ valor_liquido_ik × x_ik

Sujeito a:

Σ custo_ik × x_ik ≤ orçamento

E:

Σ x_ik ≤ 1 para cada unidade i

Onde:

- x_ik = 1 se a unidade i recebe o tratamento k;
- x_ik = 0 caso contrário.

---

## 8. Heurísticas aceitáveis

Quando não houver tempo ou solver disponível:

- ordenar por valor líquido esperado;
- ordenar por ROI com restrição de valor mínimo;
- aplicar greedy por budget;
- aplicar regras de elegibilidade;
- bloquear efeitos negativos;
- priorizar maior efeito líquido;
- desempatar por risco ou valor absoluto.

Heurísticas devem ser explicitadas como aproximações.

---

## 9. Segmentos de decisão

### Tratar

Condição:

- efeito positivo;
- valor líquido positivo;
- elegível;
- dentro do orçamento.

### Não tratar

Condição:

- efeito nulo;
- valor líquido negativo;
- custo não justificado;
- sem elegibilidade.

### Bloquear

Condição:

- efeito negativo;
- risco operacional;
- canibalização;
- restrição regulatória.

### Testar

Condição:

- incerteza alta;
- segmento novo;
- baixo volume;
- potencial estratégico.

### Fallback

Condição:

- dados insuficientes;
- score instável;
- ausência de overlap;
- política não aplicável.

---

## 10. Cenários

Simular cenários:

- 5% do budget;
- 10% do budget;
- 20% do budget;
- 30% do budget;
- sem restrição;
- restrição por canal;
- restrição por região;
- restrição por risco.

Para cada cenário:

- número de unidades acionadas;
- custo total;
- valor incremental;
- valor líquido;
- ROI;
- cobertura;
- segmentos bloqueados.

---

## 11. Saída operacional

A tabela final deve conter:

- entity_id;
- treatment_candidate;
- score;
- expected_effect;
- expected_value;
- expected_cost;
- expected_net_value;
- roi;
- decision;
- reason;
- policy_version;
- model_version;
- generated_at.

Toda decisão deve ser auditável.