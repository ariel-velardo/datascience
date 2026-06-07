# AGENTS.md

## 1. Escopo

Estas instruções valem para todo o repositório.

Este projeto envolve Ciência de Dados, Machine Learning, Inferência Causal, CRM Analytics, experimentação, uplift modeling, otimização de decisão e construção de pipelines analíticos orientados a produção.

Trabalhe de forma incremental. Prefira mudanças pequenas, seguras e fáceis de revisar.

---

## 2. Regras Operacionais

- Não instale pacotes sem pedido explícito.
- Não crie pastas sem pedido explícito.
- Não apague arquivos.
- Não altere arquivos fora do escopo solicitado.
- Antes de editar arquivos, apresente um plano curto.
- Depois de editar arquivos, liste o que foi alterado e explique como validar.
- Não gere código com placeholders.
- Não deixe código incompleto.
- Prefira código claro, modular, testável e reutilizável.
- Prefira validações explícitas em vez de apenas inspeção visual.
- Mantenha notebooks legíveis e com narrativa analítica.
- Mova lógica reutilizável para funções apenas quando isso melhorar clareza ou reuso.

---

## 3. Stack Padrão

Use DuckDB como motor analítico principal para:

- leitura de arquivos locais;
- parsing de JSON;
- transformações SQL;
- joins;
- agregações;
- janelas temporais;
- validações de dados;
- construção de ABTs.

Use Pandas principalmente para:

- materializar resultados finais;
- inspeção leve;
- visualização;
- preparação para modelagem;
- integração com bibliotecas de ML.

Evite fazer joins relacionais pesados e agregações grandes em Pandas quando DuckDB for mais apropriado.

---

## 4. Estrutura do Projeto

Pastas relevantes podem incluir:

- `data/`: dados brutos ou locais.
- `notebooks/`: notebooks exploratórios e narrativos.
- `playbooks_tecnicos/`: guias metodológicos e técnicos.
- `src/`: código reutilizável, caso exista.
- `tests/`: validações e testes, caso exista.

Não presuma que uma pasta existe. Inspecione antes.

---

## 5. Índice dos Playbooks

Use apenas o playbook necessário para a tarefa atual. Não leia todos os playbooks sem necessidade.

- `00_contexto_operacional_projeto.md`: regras operacionais e disciplina de trabalho.
- `01_playbook_inferencia_causal_uplift.md`: inferência causal, uplift, CATE e efeitos de tratamento.
- `02_playbook_abt_temporal_qualidade_dados.md`: desenho de ABT, consistência temporal e qualidade de dados.
- `03_playbook_estimadores_validacao_causal.md`: estimadores, assumptions, validação e overlap.
- `04_playbook_otimizacao_roi_politica_decisao.md`: ROI, restrições, política de decisão e otimização.
- `05_playbook_design_sistema_ml_causal_producao.md`: design de produção, pipelines, contratos e monitoramento.
- `06_playbook_governanca_revisao_comunicacao.md`: revisão crítica, governança, comunicação e limitações.

---

## 6. Regras de Inferência Causal

Não confunda predição com causalidade.

Para qualquer problema causal ou com intervenção, defina explicitamente:

- decisão de negócio ou decisão operacional;
- unidade de análise;
- tratamento/intervenção;
- grupo controle/comparação;
- momento de decisão;
- outcome;
- janela do outcome;
- features pré-tratamento;
- variáveis pós-tratamento que devem ser excluídas;
- assumptions;
- limitações.

Features devem estar disponíveis antes do momento de decisão.

Targets devem ser medidos depois do momento de decisão.

Não use variáveis pós-tratamento como features.

Não apresente modelo de propensão como se fosse uplift causal.

Caso não exista grupo controle ou estratégia de identificação defensável, deixe claro que o resultado é preditivo ou associativo, não causal.

---

## 7. Regras de ABT

Em projetos causais, a ABT deve documentar:

- chave primária;
- granularidade;
- ID da entidade;
- ID do tratamento, quando aplicável;
- flag de tratamento;
- momento de decisão;
- janela de features;
- janela de outcome;
- colunas de target;
- colunas proibidas por leakage;
- flags de qualidade.

A ABT deve ser validada para:

- dados não vazios;
- schema esperado;
- unicidade da chave;
- presença de tratamento e controle;
- ausência de nulos críticos;
- ausência de timestamps impossíveis;
- ausência de feature leakage;
- ausência de target leakage.

---

## 8. Regras de Modelagem

Comece com um baseline simples e defensável antes de modelos complexos.

Para problemas preditivos, use métricas preditivas adequadas.

Para problemas causais ou de uplift, prefira métricas como:

- uplift por decil;
- Qini/AUUC, quando aplicável;
- ganho incremental;
- comparação entre tratamento e controle;
- heterogeneidade de efeito;
- valor de negócio;
- ROI.

Não use acurácia, F1 ou ROC-AUC como métrica principal para qualidade de uplift ou decisão causal.

---

## 9. Regras de Decisão

Score de modelo não é entrega final.

Quando o projeto envolver decisão, gere uma política acionável sempre que possível.

Uma política deve considerar:

- efeito esperado;
- valor esperado;
- custo esperado;
- valor líquido esperado;
- ROI;
- elegibilidade;
- capacidade;
- orçamento;
- risco;
- fallback.

Não recomende tratar automaticamente toda unidade com score positivo.

Para incentivos, descontos, cupons, cashback, pricing, retenção ou ações operacionais, considere custo e risco de canibalização.

---

## 10. Regras de Design de Produção

Separe conceitualmente a lógica em:

1. ingestão;
2. normalização;
3. construção de features;
4. construção da ABT;
5. modelagem ou estimação de efeito;
6. avaliação;
7. política de decisão;
8. monitoramento.

Prefira contratos explícitos para tabelas e saídas importantes.

Toda saída importante deve conter:

- nome do artefato;
- granularidade;
- chave;
- validação;
- limitação conhecida;
- próximo passo.

---

## 11. Regras de Revisão

Antes de considerar uma tarefa concluída, verifique:

- A mudança ficou dentro do escopo?
- As assumptions de dados estão explícitas?
- As regras temporais foram respeitadas?
- Existe leakage?
- A métrica está alinhada à decisão?
- As limitações foram declaradas?
- A saída é acionável?
- Existe validação?

Classifique problemas como:

- crítico: invalida o resultado;
- alto: resultado apenas exploratório;
- médio: usar com ressalvas;
- baixo: melhoria de manutenção ou clareza.

---

## 12. Formato de Resposta

Para tarefas de planejamento:

1. plano curto;
2. riscos;
3. arquivos provavelmente afetados;
4. plano de validação.

Para tarefas de implementação:

1. plano curto antes da edição;
2. mudança mínima e dentro do escopo;
3. arquivos alterados;
4. instruções de validação;
5. limitações restantes.

Para tarefas de revisão:

1. achados por severidade;
2. evidência;
3. correção recomendada;
4. indicação se é bloqueador ou não.