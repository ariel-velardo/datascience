# Contexto Operacional do Projeto

## 1. Objetivo

Este playbook define regras operacionais para desenvolvimento de projetos de Ciência de Dados, Machine Learning e Inferência Causal em ambiente local ou produtivo.

Ele deve ser usado para manter consistência, segurança e rastreabilidade em qualquer projeto que envolva:

- ingestão de dados;
- construção de bases analíticas;
- modelagem preditiva;
- inferência causal;
- avaliação de impacto;
- otimização de decisão;
- geração de artefatos para negócio ou produção.

---

## 2. Princípios de trabalho

Todo desenvolvimento deve seguir estes princípios:

1. Trabalhar de forma incremental.
2. Evitar alterações grandes sem validação intermediária.
3. Preservar rastreabilidade de decisões técnicas.
4. Separar exploração, modelagem e produção.
5. Evitar dependências desnecessárias.
6. Documentar assumptions, limitações e riscos.
7. Validar dados antes de modelar.
8. Validar modelo antes de recomendar ação.
9. Diferenciar resultado preditivo de evidência causal.
10. Gerar saídas interpretáveis e acionáveis.

---

## 3. Regras de ambiente

- Não instalar pacotes sem necessidade explícita.
- Não alterar estrutura de pastas sem justificativa.
- Não apagar arquivos sem confirmação.
- Não modificar arquivos fora do escopo da tarefa.
- Não usar código incompleto ou placeholders.
- Preferir código modular, testável e reutilizável.
- Manter nomes claros para tabelas, funções, variáveis e artefatos.
- Sempre incluir validações mínimas nas etapas críticas.

---

## 4. Stack analítica recomendada

### DuckDB

Usar DuckDB para:

- leitura de arquivos locais;
- parsing de JSON/Parquet/CSV;
- joins relacionais;
- agregações;
- janelas temporais;
- validações SQL;
- construção de ABTs;
- materialização de tabelas intermediárias.

### Pandas

Usar Pandas para:

- inspeção leve;
- materialização de resultado final;
- pequenas análises exploratórias;
- visualizações;
- preparação para modelagem;
- integração com bibliotecas de ML.

### Pydantic ou validações manuais

Usar para:

- contratos de schema;
- validação de tipos;
- validação de parâmetros;
- proteção contra entradas inválidas.

---

## 5. Critério geral de aceite

Toda etapa deve terminar com:

- artefato gerado;
- validação executada;
- risco mitigado;
- limitação explícita;
- próximo passo recomendado.

Exemplo:

“ABT criada com chave única, tratamento e controle presentes, features pré-tratamento e targets pós-tratamento. Risco mitigado: vazamento temporal. Limitação: possível confundimento residual. Próximo passo: diagnóstico de overlap e balanceamento.”