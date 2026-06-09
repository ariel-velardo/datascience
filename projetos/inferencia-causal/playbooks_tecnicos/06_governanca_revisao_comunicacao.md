06_playbook_governanca_revisao_comunicacao# Playbook de Governança, Revisão Crítica e Comunicação Técnica

## 1. Objetivo

Este playbook define padrões para revisar, comunicar e governar projetos de Ciência de Dados, Machine Learning e Inferência Causal.

Ele deve ser usado para garantir que análises, modelos e políticas sejam:

- tecnicamente defensáveis;
- causalmente honestos;
- interpretáveis;
- auditáveis;
- úteis para decisão;
- comunicados com clareza.

---

## 2. Princípio de responsabilidade técnica

A ferramenta, biblioteca ou agente de código pode apoiar implementação e revisão, mas a responsabilidade técnica permanece com o cientista de dados.

Decisões críticas não devem ser delegadas sem revisão:

- formulação do problema;
- definição do treatment;
- definição do outcome;
- seleção de features;
- desenho da ABT;
- assumptions causais;
- escolha do estimador;
- métrica de avaliação;
- regra de decisão;
- interpretação de resultado.

---

## 3. Revisão crítica obrigatória

Todo projeto deve passar por revisão nos seguintes eixos:

### Formulação

- A pergunta está clara?
- A decisão está clara?
- O outcome está alinhado ao objetivo?
- O estimando está explícito?

### Dados

- Os dados representam a população-alvo?
- Há missing relevante?
- Há viés de seleção?
- Há mudanças temporais?

### Temporalidade

- Features são anteriores à decisão?
- Targets são posteriores?
- Existe label delay?
- Existe censura?

### Causalidade

- Existe grupo controle?
- O tratamento foi randomizado?
- Há confundidores?
- Há overlap?
- As assumptions foram documentadas?

### Modelo

- O modelo é adequado ao problema?
- Existe baseline?
- A métrica é compatível?
- Há overfitting?
- Há estabilidade temporal?

### Decisão

- A saída é acionável?
- O custo foi considerado?
- Restrições foram respeitadas?
- Há fallback?
- A decisão é auditável?

### Produção

- Existe contrato de dados?
- Existe monitoramento?
- Existe versionamento?
- Existe rollback?
- Existe responsável?

---

## 4. Linguagem de comunicação

Evitar afirmações fortes quando as assumptions não sustentam causalidade.

Evitar:

- “o modelo provou que...”
- “a campanha causou...”
- “a variável X gera...”
- “garantimos impacto...”

Preferir:

- “a estimativa sugere...”
- “sob as assumptions definidas...”
- “observamos associação...”
- “o efeito estimado foi...”
- “há evidência compatível com...”
- “a limitação principal é...”

---

## 5. Comunicação para público técnico

Incluir:

- definição do problema;
- dados usados;
- unidade de análise;
- treatment;
- control;
- outcome;
- janela temporal;
- estimador;
- assumptions;
- validações;
- métricas;
- limitações;
- próximos passos.

---

## 6. Comunicação para negócio

Incluir:

- decisão apoiada;
- público elegível;
- ação recomendada;
- impacto esperado;
- custo esperado;
- risco;
- limitações;
- como testar;
- como monitorar;
- próximo ciclo de decisão.

---

## 7. Comunicação de incerteza

Todo resultado causal deve explicitar:

- intervalo de confiança ou incerteza prática;
- tamanho amostral;
- estabilidade por segmento;
- sensibilidade a assumptions;
- limitações de identificação;
- risco de confundimento residual.

---

## 8. Checklist antes de apresentar resultado

1. A pergunta de negócio está clara?
2. A decisão está clara?
3. O tratamento está definido?
4. O controle está definido?
5. O outcome está definido?
6. A janela temporal está definida?
7. Features e targets respeitam temporalidade?
8. As assumptions foram listadas?
9. O estimador foi justificado?
10. A métrica é adequada?
11. O resultado é acionável?
12. O custo foi considerado?
13. As limitações foram explicitadas?
14. O próximo passo está claro?

---

## 9. Classificação de severidade de problemas

### Crítico

Impede uso do resultado.

Exemplos:

- leakage;
- target mal definido;
- ausência de controle;
- chave duplicada na ABT;
- tratamento confundido com outcome;
- custo ignorado em decisão financeira.

### Alto

Resultado pode ser usado apenas como exploração.

Exemplos:

- overlap ruim;
- viés de seleção relevante;
- falta de validação temporal;
- métrica desalinhada;
- segmentos instáveis.

### Médio

Não bloqueia, mas exige ressalva.

Exemplos:

- missing moderado;
- baixa interpretabilidade;
- ausência de teste de sensibilidade;
- pouca documentação.

### Baixo

Melhoria de manutenção ou clareza.

Exemplos:

- nomes pouco claros;
- repetição de código;
- gráficos pouco informativos;
- organização de notebook.

---

## 10. Padrão de conclusão

Toda entrega deve terminar com:

- o que foi feito;
- o que foi validado;
- qual risco foi mitigado;
- o que ainda não está provado;
- qual decisão pode ser tomada;
- qual decisão ainda não deve ser tomada;
- próximo passo recomendado.