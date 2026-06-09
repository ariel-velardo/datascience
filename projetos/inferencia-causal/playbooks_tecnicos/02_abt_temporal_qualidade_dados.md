# Playbook de ABT Temporal e Qualidade de Dados

## 1. Objetivo

Este playbook define padrões para construção de Analytical Base Tables em projetos preditivos e causais.

Em projetos de inferência causal, a ABT não é apenas uma tabela de modelagem. Ela é o contrato que define:

- unidade de análise;
- momento de decisão;
- tratamento;
- controle;
- features válidas;
- outcome;
- janela temporal;
- risco de leakage.

---

## 2. Regra principal

Toda ABT causal deve separar claramente:

- passado: features;
- presente: decisão/tratamento;
- futuro: outcome.

Se uma informação não estaria disponível no momento da decisão, ela não pode ser usada como feature.

---

## 3. Granularidade

A granularidade deve refletir a decisão real.

Exemplos:

- cliente × campanha × momento;
- contrato × renegociação × data;
- paciente × tratamento × data;
- aluno × intervenção × semana;
- usuário × feature rollout × sessão;
- loja × preço × período;
- transação × regra antifraude × instante.

A chave primária deve ser compatível com essa granularidade.

---

## 4. Componentes obrigatórios

Toda ABT causal deve conter:

### Identificação

- entity_id;
- treatment_id, quando aplicável;
- decision_time;
- observation_window;
- outcome_window;
- chave primária da linha.

### Tratamento

- treatment_flag;
- treatment_type;
- treatment_intensity;
- treatment_cost, quando aplicável;
- eligibility_flag;
- assignment_mechanism, quando conhecido.

### Features pré-tratamento

- histórico comportamental;
- recência;
- frequência;
- valor acumulado;
- tendências anteriores;
- atributos cadastrais;
- exposição anterior;
- contexto disponível antes da decisão.

### Outcome pós-tratamento

- outcome binário;
- outcome contínuo;
- receita/valor;
- churn;
- default;
- retenção;
- engajamento;
- evento adverso;
- tempo até evento.

### Flags de qualidade

- missing crítico;
- outlier mascarado;
- ausência de histórico;
- janela incompleta;
- elegibilidade;
- censura;
- atraso de rótulo.

---

## 5. Variáveis proibidas

Não podem entrar como features:

- variáveis geradas após o tratamento;
- resposta à campanha;
- conclusão da oferta;
- conversão futura;
- receita futura;
- status posterior ao outcome;
- variáveis calculadas usando janela posterior;
- flags de target;
- informações disponíveis apenas para tratados;
- identificadores que codificam diretamente o outcome.

---

## 6. Janelas temporais

Definir explicitamente:

- janela de observação histórica;
- momento de decisão;
- janela de tratamento;
- janela de outcome;
- período de maturação do rótulo;
- período de exclusão, quando necessário.

Exemplo:

- observar comportamento nos 90 dias anteriores;
- definir tratamento no dia D;
- medir conversão até D+7;
- aguardar D+14 para evitar label delay.

---

## 7. Validações obrigatórias

### Dados brutos

- arquivos existem;
- volume maior que zero;
- schema esperado;
- tipos coerentes;
- ausência de colunas críticas nulas.

### Chaves

- chave primária não duplicada;
- ids de entidades válidos;
- ids de tratamento válidos;
- joins sem perdas inesperadas.

### Temporalidade

- features com timestamp anterior ao decision_time;
- outcomes com timestamp posterior ao decision_time;
- sem agregações olhando para o futuro;
- sem normalização usando informação fora do treino.

### Tratamento e controle

- ambos presentes;
- tamanhos amostrais suficientes;
- distribuição por período;
- elegibilidade clara;
- controle compatível com a população tratada.

### Qualidade

- missing rate;
- outliers;
- cardinalidade;
- drift temporal;
- valores impossíveis;
- duplicidade;
- inconsistência de eventos.

---

## 8. ABT para produção

A ABT de treino e a ABT de scoring devem compartilhar a mesma lógica de features.

Diferença:

- treino tem outcome;
- scoring não tem outcome;
- scoring usa apenas features disponíveis no momento da decisão;
- scoring deve respeitar elegibilidade operacional.

Toda feature usada no treino precisa ser reproduzível no scoring.