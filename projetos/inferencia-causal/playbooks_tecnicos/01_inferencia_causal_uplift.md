# Playbook de Inferência Causal, Uplift Modeling e Personalização

## 1. Princípio central

Projetos causais não buscam apenas prever o que vai acontecer. Eles buscam responder o que aconteceria sob uma intervenção.

Um modelo preditivo estima associação:

P(Y | X)

Um modelo causal busca estimar efeito de intervenção:

E[Y | do(T=1)] - E[Y | do(T=0)]

Em projetos aplicados, isso significa distinguir:

- quem tem maior propensão ao outcome;
- quem muda de comportamento por causa da intervenção;
- quem não é impactado;
- quem pode ser impactado negativamente;
- qual ação gera valor líquido positivo.

---

## 2. Formulação causal

A formulação básica de uplift/CATE é:

τ(X) = E[Y | X, T=1] - E[Y | X, T=0]

Onde:

- X: características pré-tratamento;
- T: tratamento/intervenção;
- Y: outcome observado após a intervenção;
- τ(X): efeito médio condicional do tratamento para um perfil X.

O estimando pode variar conforme o objetivo:

- ATE: efeito médio na população;
- ATT: efeito médio entre tratados;
- CATE: efeito médio condicional;
- LATE: efeito local para compliers;
- efeito por segmento;
- efeito por tratamento em problemas multi-treatment.

---

## 3. Diferença entre propensão e uplift

### Propensão

Pergunta:

“Quem tem maior probabilidade de converter, comprar, atrasar, churnar ou responder?”

Uso adequado:

- priorização;
- ranking comercial;
- alerta operacional;
- predição de risco;
- segmentação.

Limitação:

Propensão não mede impacto causal.

Um cliente com alta propensão pode realizar o outcome mesmo sem intervenção.

---

### Uplift

Pergunta:

“Quem muda de comportamento por causa da intervenção?”

Uso adequado:

- campanhas;
- cupons;
- descontos;
- cashback;
- tratamento médico;
- intervenção educacional;
- cobrança;
- renegociação;
- política operacional.

Limitação:

Exige grupo controle, identificação causal defensável ou assumptions explícitas.

---

## 4. Quadrantes comportamentais

### Persuadíveis

τ(X) > 0

A intervenção aumenta a probabilidade do outcome desejado.

Ação:

- priorizar;
- testar intensidade de incentivo;
- considerar custo e ROI.

---

### Sure Things

τ(X) ≈ 0 e alta probabilidade orgânica de outcome.

Ação:

- evitar incentivo custoso;
- reduzir canibalização;
- usar comunicação sem benefício financeiro.

---

### Lost Causes

τ(X) ≈ 0 e baixa probabilidade de outcome.

Ação:

- evitar gasto;
- testar outras estratégias;
- nutrir ou resegmentar.

---

### Sleeping Dogs

τ(X) < 0

A intervenção reduz o outcome desejado ou gera efeito adverso.

Ação:

- bloquear;
- reduzir contato;
- investigar causa do efeito negativo.

---

## 5. Domínios de aplicação

Este playbook se aplica a qualquer domínio com intervenção:

- CRM e marketing;
- descontos, cupons e cashback;
- churn e retenção;
- crédito e cobrança;
- pricing;
- saúde;
- educação;
- fraude;
- produto digital;
- operações;
- logística;
- políticas públicas.

---

## 6. Perguntas obrigatórias antes de modelar

1. Qual decisão será tomada?
2. Qual é a intervenção?
3. Qual é o grupo controle?
4. O tratamento foi randomizado?
5. Qual é o outcome?
6. Qual é a janela do outcome?
7. Quais variáveis são pré-tratamento?
8. Quais variáveis são pós-tratamento?
9. Há confundidores observáveis?
10. Há confundidores não observáveis prováveis?
11. Há overlap entre tratados e controles?
12. Há interferência entre unidades?
13. Há censura, atrito ou atraso de rótulo?
14. Qual estimando será reportado?
15. Como o efeito vira decisão?

---

## 7. Riscos comuns

- confundir correlação com causalidade;
- usar propensão como se fosse uplift;
- usar variável pós-tratamento como feature;
- usar target leakage;
- usar split aleatório em problema temporal;
- ignorar viés de seleção;
- ignorar falta de overlap;
- não reportar assumptions;
- não transformar efeito em decisão;
- não considerar custo da intervenção.