# Protocolo Pré-Análise

## 1. Finalidade

Este documento registra o estado metodológico do projeto antes da
estimação de qualquer efeito pós-tratamento.

Seu objetivo é separar claramente:

1. decisões já congeladas na fase exploratória;
2. especificações candidatas vindas da exploração;
3. decisões ainda abertas que precisam de fundamentação acadêmica ex ante.

Nenhuma escolha metodológica deve ser alterada posteriormente apenas
porque produz resultados mais favoráveis.

---

# 2. Pergunta de pesquisa atual

Pergunta candidata:

> Qual foi o efeito da chegada de novos campi da Rede Federal de Educação
> Profissional, Científica e Tecnológica, associados à Expansão Fase II,
> sobre a atividade econômica dos municípios brasileiros?

A redação final ainda poderá ser refinada após a revisão de literatura
e a reconstrução institucional.

Mudanças futuras na formulação da pergunta não podem ser motivadas pela
observação dos efeitos estimados.

---

# 3. Status do projeto

FASE_EXPLORATORIA = ENCERRADA

VIABILIDADE_CAUSAL = PROMISSORA_COM_RESSALVAS

EFEITO_CAUSAL_ESTIMADO = NAO

FASE_ATUAL = DESENVOLVIMENTO_ACADEMICO

---

# 4. Decisões já congeladas

## 4.1 Política

Expansão da Rede Federal de Educação Profissional, Científica e
Tecnológica, com foco na chamada Expansão Fase II.

## 4.2 Unidade de análise

Município-ano.

## 4.3 Definição conceitual do tratamento

Primeira presença federal de EPT observada no município associada à
Expansão Fase II.

## 4.4 Interpretação do timing

O ano de tratamento deve ser interpretado como:

"proxy anual de primeira presença operacional observada no Censo Escolar".

Ele não deve ser denominado automaticamente:

- ano de criação;
- ano de autorização;
- ano de inauguração.

## 4.5 Horizonte econômico principal explorado

2007–2019.

O encerramento em 2019 evita incorporar diretamente o choque da
pandemia de COVID-19 ao desenho principal.

## 4.6 Tratamento escalonado

Os municípios recebem tratamento em anos distintos.

Um modelo TWFE ingênuo não será utilizado como estimador causal
principal.

## 4.7 Validade externa

O suporte comum observado na exploração foi limitado.

Portanto, qualquer estimando futuro deve explicitar a diferença entre:

- população de interesse;
- população tratada observada;
- população tratada com suporte comum;
- população efetivamente utilizada na estimação.

Não será feita generalização automática para toda a Expansão Fase II.

---

# 5. Resultados exploratórios que funcionam como diagnóstico

Estes resultados orientam o desenvolvimento, mas não constituem ainda
a especificação causal final.

## 5.1 Municípios Fase II

Municípios únicos identificados: 144.

## 5.2 Tratados principais inicialmente considerados

2010 = 37

2011 = 65

2012 = 14

2013 = 3

Total = 119.

## 5.3 Common support

119 tratados inicialmente considerados.

53 tratados permaneceram no suporte comum exploratório.

## 5.4 Matching exploratório

Melhor configuração exploratória encontrada:

- nearest-neighbor;
- K = 1;
- com reposição;
- exact matching por UF;
- somente variáveis pré-tratamento.

Resultados aproximados:

- 53 tratados matched;
- 51 controles únicos;
- ESS dos controles ≈ 49,3;
- mediana |SMD| ≈ 0,0225;
- máximo |SMD| ≈ 0,2248.

GATE_MATCHING = ALERTA.

## 5.5 Amostra core exploratória

Coorte 2010 = 17 tratados.

Coorte 2011 = 30 tratados.

Total = 47 pares.

As coortes 2012 e 2013 foram consideradas pequenas e permanecem como
candidatas a análises de sensibilidade.

## 5.6 Pré-tendências

Janela exploratória balanceada:

k = -3, -2, -1.

Os resultados foram considerados promissores, mas não comprovam
tendências paralelas.

## 5.7 Placebos

Foram encontrados sinais pré-tratamento em algumas combinações de
coorte e outcome.

Esses sinais permanecem como alerta para:

- antecipação;
- erro de timing;
- seleção dinâmica;
- choques locais prévios;
- instabilidade amostral.

GATE_ESTATISTICO_FINAL = PROMISSOR_COM_ALERTAS.

---

# 6. Itens ainda NÃO congelados

Os seguintes elementos precisam ser definidos academicamente antes da
estimação final:

## 6.1 Outcome primário

Candidatos atuais:

- pessoal ocupado assalariado;
- pessoal ocupado total;
- número de unidades locais;
- salário médio mensal.

A escolha do outcome primário deve ser baseada em:

- pergunta substantiva;
- mecanismo econômico;
- literatura;
- qualidade da mensuração;
- interpretação causal.

Não será escolhido o outcome que apresentar o maior efeito estimado.

## 6.2 Outcomes secundários

Serão definidos depois da escolha do outcome primário.

## 6.3 Estimando

Ainda deve ser definido formalmente.

Exemplos de perguntas que precisam ser respondidas:

- ATT de qual população?
- efeito médio sobre municípios tratados com suporte comum?
- efeito agregado por coorte?
- efeito dinâmico por event time?
- qual horizonte pós-tratamento é substantivamente relevante?

## 6.4 População causal principal

Ainda deve ser formalizada a relação entre:

- 144 municípios Fase II;
- 119 tratados 2010–2013;
- 53 tratados com suporte comum;
- 47 tratados das coortes 2010–2011.

A amostra de 47 pares não será automaticamente transformada em
população causal principal apenas porque apresentou diagnóstico
exploratório favorável.

## 6.5 Grupo de comparação

O pool conservador de aproximadamente 4.958 municípios permanece como
referência exploratória.

Ainda deve ser definido formalmente:

- never-treated;
- not-yet-treated;
- combinação admissível;
- regras adicionais de exclusão.

## 6.6 Estimador principal

Candidatos:

- Callaway–Sant'Anna;
- Sun–Abraham;
- outro estimador moderno para staggered adoption.

A decisão precisa ser fundamentada antes da análise final.

## 6.7 Antecipação

Ainda será definido se:

- antecipação = 0;
- antecipação = 1 ano;
- outra janela possui justificativa institucional.

## 6.8 Spillovers

Precisamos avaliar:

- proximidade geográfica;
- deslocamento de estudantes e trabalhadores;
- efeitos sobre municípios vizinhos;
- possível exclusão de controles próximos.

Distâncias como 30 km ou 50 km serão consideradas apenas se houver
fundamentação substantiva.

## 6.9 Inferência

Ainda devem ser definidos:

- nível de clusterização;
- procedimento de inferência;
- eventuais ajustes para número reduzido de clusters/coortes.

---

# 7. Casos de timing que exigem tratamento explícito

## Sobral/CE

- pertence à Fase II;
- há evidência externa de entrada/criação em 2008;
- inauguração oficial em 2009;
- não deve ser usado como controle;
- pode permanecer fora do timing principal uniforme pelo Censo;
- pode entrar em sensibilidade com timing externo.

## Campinas/SP

- pertence à Fase II;
- início de atividades do IFSP em 2013;
- não pode ser controle;
- pode entrar em análise de sensibilidade com timing externo 2013.

Nenhum desses casos deve ser corrigido silenciosamente na
especificação principal.

---

# 8. Mecanismos econômicos

Um campus da Rede Federal pode afetar o município por diferentes canais:

1. contratação direta de professores, técnicos e outros trabalhadores;
2. consumo local de servidores e estudantes;
3. demanda por serviços;
4. formação de capital humano;
5. atração de empresas;
6. criação de novos estabelecimentos;
7. mudanças salariais;
8. efeitos sobre composição setorial;
9. deslocamentos de atividade entre municípios.

O aumento de emprego público diretamente associado ao campus é um
efeito econômico real da política.

Entretanto, análises futuras poderão separar:

- efeito direto da presença do campus;
- efeitos indiretos sobre atividade econômica privada.

---

# 9. Fontes principais candidatas

## Política e tratamento

- MEC;
- relação histórica de campi dos Institutos Federais;
- Censo Escolar.

## Atividade econômica

IBGE / Cadastro Central de Empresas — CEMPRE.

Período exploratório principal:

2007–2019.

## Possíveis complementos

- população municipal IBGE;
- CEMPRE por setor;
- RAIS, apenas se necessária;
- documentos institucionais dos Institutos Federais.

---

# 10. Ordem obrigatória antes da estimação

A próxima sequência do projeto será:

1. revisão de literatura;
2. reconstrução histórica e institucional da Expansão Fase II;
3. formulação do DAG;
4. refinamento da pergunta de pesquisa;
5. definição da população de interesse;
6. definição da população identificável;
7. definição formal do estimando;
8. definição do outcome primário;
9. definição dos outcomes secundários;
10. formalização do tratamento e timing;
11. definição da hipótese de antecipação;
12. definição da política de spillovers;
13. definição do grupo de comparação;
14. escolha do estimador principal;
15. definição da estratégia de inferência;
16. validação externa do timing;
17. reconstrução do pipeline;
18. análise descritiva;
19. estimação causal.

Não executar a etapa 19 antes da conclusão documental das etapas
anteriores.

---

# 11. Regra contra specification searching

Após o início da análise pós-tratamento, mudanças metodológicas só
serão aceitas se:

1. forem motivadas por erro identificado;
2. tiverem justificativa substantiva independente do resultado;
3. forem documentadas;
4. a especificação originalmente definida também permanecer reportada,
   sempre que tecnicamente possível.

---

# 12. Próxima atividade

A próxima atividade substantiva é a revisão de literatura e a
reconstrução institucional da Expansão Fase II.

Essas etapas devem fornecer evidência para decidir:

- mecanismo causal;
- seleção dos municípios;
- timing;
- antecipação;
- spillovers;
- outcomes;
- estimando;
- estratégia de identificação.