# Auditoria Metodológica e Estrutural

**Projeto:** Evasão/desistência no ensino superior brasileiro (Big Data Analytics)
**Base principal:** `data/raw/trajetoria/2015_2024/indicadores_trajetoria_educacao_superior_2015_2024.xlsx`
**Dicionário oficial:** `data/raw/trajetoria/2015_2024/Dicionário_acompanhamento_trajetória.docx`
**Data da auditoria:** 2026-09-04
**Status:** auditoria apenas. Nenhum dado bruto foi modificado, nenhum arquivo apagado, nenhum modelo implementado, nenhum commit realizado.

Convenção usada em todo o documento:

- **[FATO]** — verificado programaticamente nesta auditoria, com a contagem exata reportada.
- **[DICIONÁRIO]** — transcrito do dicionário oficial do Inep.
- **[HIPÓTESE]** — interpretação minha, ainda não comprovada pelos dados.

---

## 1. Auditoria factual dos dados

### 1.1 Estrutura física do arquivo

| Item | Valor |
|---|---|
| Planilha | `INDICADORES_TRAJETORIA` (única) |
| `ws.max_row` reportado pelo Excel | 281.440 |
| Linhas 1–8 | preâmbulo institucional (MEC/Inep, título, rótulos longos) |
| Linha 9 | cabeçalho técnico (31 colunas) |
| Linhas 10–281.440 | 281.431 linhas |
| Linhas de dados reais | **281.430** |
| Linhas não-dados no rodapé | **1** — `Fonte: Censo da Educação Superior/Inep.` |

**[FATO]** O rodapé existe e precisa ser removido em qualquer ingestão. Um `read_excel(skiprows=8)` ingênuo produz uma linha espúria e força as colunas numéricas para `object`.

**[FATO]** A linha 5 do preâmbulo declara textualmente o escopo do arquivo:

> "Indicadores de Trajetória dos Alunos nos Cursos de Graduação da Educação Superior 2024 **(coorte 2015)**"

### 1.2 Achado central da auditoria

**[FATO] A base contém uma única coorte de ingresso.**

```
SELECT count(DISTINCT NU_ANO_INGRESSO)  ->  1
NU_ANO_INGRESSO = 2015 em 281.430/281.430 linhas
NU_ANO_REFERENCIA ∈ {2015, ..., 2024}   (10 valores)
```

Este é o fato mais consequente de toda a auditoria, e ele **contradiz a premissa implícita do desenho preditivo proposto na Terceira Tarefa**. Não existe variação entre coortes. O painel é:

**28.143 cursos × 10 anos de referência = 281.430 linhas.**

Não é um painel multi-coorte. É o acompanhamento longitudinal de **uma** coorte (ingressantes de 2015) ao longo de 10 anos.

### 1.3 Dimensões

| Dimensão | Contagem [FATO] |
|---|---|
| Linhas de dados | 281.430 |
| Trajetórias distintas (cursos) | 28.143 |
| IES distintas | 2.158 |
| Coortes de ingresso | 1 (2015) |
| Anos de referência | 10 (2015–2024) |
| Ingressantes totais na coorte | 3.027.277 |
| Áreas gerais CINE | 10 |

### 1.4 Tipagem — armadilha detectada

**[FATO]** `CO_CINE_AREA_GERAL` e `CO_CINE_ROTULO` são **texto**, não número. `CO_CINE_AREA_GERAL` usa códigos com zero à esquerda (`"01"`, `"06"`, `"10"`). Uma tipagem para inteiro destrói silenciosamente os 281.430 valores — foi exatamente o que aconteceu na primeira tentativa desta auditoria, e só foi detectado por contagem de conversões falhas. O dicionário do Censo 2024 confirma: `CO_CINE_AREA_GERAL` é `Char(2)`.

---

## 2. Unidade observacional e chave

### 2.1 Unidade observacional (pergunta 1)

**[FATO]** A unidade observacional é:

> **curso de graduação × ano de referência**, dentro da coorte fixa de ingressantes de 2015.

Cada linha é uma **contagem agregada de alunos**, não um aluno. Não há microdado de aluno aqui. Toda a análise é ecológica — conclusões valem sobre cursos, não sobre estudantes (ver §13, risco R1).

### 2.2 Chave mínima (pergunta 2)

Testei as chaves candidatas. **[FATO]**:

| Chave candidata | Combinações distintas | Única? |
|---|---|---|
| `CO_IES, CO_CURSO, NU_ANO_INGRESSO, NU_ANO_REFERENCIA` | 281.430 | sim |
| `CO_CURSO, NU_ANO_INGRESSO, NU_ANO_REFERENCIA` | 281.430 | sim |
| **`CO_CURSO, NU_ANO_REFERENCIA`** | **281.430** | **sim** |

**A chave mínima real é `(CO_CURSO, NU_ANO_REFERENCIA)`.**

A chave que você propôs funciona, mas é redundante:

- `NU_ANO_INGRESSO` é constante (=2015) — carrega zero informação;
- `CO_IES` é funcionalmente determinado por `CO_CURSO` — **[FATO]** há 28.143 `CO_CURSO` distintos e 28.143 trajetórias, e nenhum `CO_CURSO` aparece com mais de um `CO_IES`.

**Identificador de trajetória: `CO_CURSO`, sozinho. 28.143 trajetórias.**

### 2.3 Trajetórias (perguntas 3, 4, 5, 6)

**[FATO]**

| Pergunta | Resposta |
|---|---|
| 3. Quantas trajetórias distintas? | **28.143** |
| 4. Observações anuais por trajetória? | **exatamente 10, para todas** |
| 5. Existem trajetórias incompletas? | **Não. Zero.** |
| 6. Distribuição do nº de anos acompanhados? | Degenerada: 100,00% das trajetórias têm n=10 |

O painel é **perfeitamente balanceado**. Isso é incomum e é uma vantagem operacional real: nenhuma imputação, nenhum painel desbalanceado, nenhuma decisão sobre atrito.

**Nuance importante [FATO]:** `NU_PRAZO_ACOMPANHAMENTO` varia de 2 a 10 anos e `NU_ANO_MAXIMO_ACOMPANHAMENTO` varia de 2016 a 2024, **mas todas as trajetórias mesmo assim têm 10 linhas**:

| `NU_PRAZO_ACOMPANHAMENTO` | Ano máximo | Nº de cursos |
|---|---|---|
| 2 | 2016 | 25 |
| 3 | 2017 | 76 |
| 4 | 2018 | 2.687 |
| 5 | 2019 | 952 |
| 6 | 2020 | 1.902 |
| 7 | 2021 | 475 |
| 8 | 2022 | 12.404 |
| 9 | 2023 | 832 |
| 10 | 2024 | 8.790 |

E — ponto que eu esperava que fosse diferente — **os dados não congelam após o prazo máximo**. Depois de `NU_ANO_MAXIMO_ACOMPANHAMENTO` ainda são registrados **54.540 desistências e 22.773 conclusões** em 56.287 linhas. O Inep continua rastreando o vínculo além do prazo formal de acompanhamento.

**Consequência prática:** `TDA` em 2024 é bem definido e comparável para todas as 28.143 trajetórias. Você **não** precisa truncar em `NU_ANO_MAXIMO_ACOMPANHAMENTO`. Mas `NU_PRAZO_ACOMPANHAMENTO` **deve** entrar como covariável: um curso de prazo 4 e um de prazo 10 estão em pontos completamente diferentes do próprio ciclo quando observados aos 10 anos.

---

## 3. Qualidade e consistência

### 3.1 Duplicidades (pergunta 7)

**[FATO] Nenhuma.**

- Grupos por `(CO_CURSO, NU_ANO_REFERENCIA)` com contagem > 1: **0**. Todos os 281.430 grupos têm exatamente 1 linha.
- Linhas integralmente idênticas: **0**.

### 3.2 Valores ausentes (pergunta 8)

**[FATO]** Apenas 3 colunas têm nulos, e são **estruturais, não erro**:

| Coluna | Nulos | Explicação |
|---|---|---|
| `CO_REGIAO` | 11.180 | todos EAD |
| `CO_UF` | 11.180 | todos EAD |
| `CO_MUNICIPIO` | 11.180 | todos EAD |

11.180 = 1.118 cursos EAD × 10 anos. **100% dos nulos geográficos são EAD, e 100% dos cursos EAD têm geografia nula.** O dicionário do Censo 2024 confirma a regra: *"Dados de Cursos a distância não calculados para esta dimensão geográfica."*

**As outras 28 colunas: zero nulos.**

**Implicação de desenho:** qualquer análise regional exclui automaticamente 24% dos ingressantes da coorte (os 729.419 do EAD). Isso não é opcional — é imposto pela base. Toda tabela regional precisa carregar a nota "presencial apenas".

### 3.3 Valores impossíveis (pergunta 9)

**[FATO] Nenhum valor impossível.**

| Teste | Violações |
|---|---|
| `QT_INGRESSANTE` < 0 | 0 |
| `QT_INGRESSANTE` = 0 | 0 |
| `QT_PERMANENCIA/CONCLUINTE/DESISTENCIA/FALECIDO` < 0 | 0 |
| `TAP`, `TCA`, `TDA`, `TCAN`, `TADA` fora de [0, 100] | 0 (todas as cinco) |

**[FATO]** `min(QT_INGRESSANTE) = 4`. A distribuição na cauda inferior é lisa (4→249 cursos, 5→230, 6→189, 7→187, 8→186, 9→180...), sem pico artificial de empilhamento.

**[HIPÓTESE]** O Inep aplica um corte de publicação em ≥4 ingressantes. Não encontrei essa regra declarada no dicionário. Trate como corte observado, não documentado.

Distribuição de `QT_INGRESSANTE` (nível curso): mín 4 | p25 34 | mediana 57 | p75 102 | p95 287 | máx 25.001 | média 107,6.

### 3.4 Relações entre as quantidades (pergunta 10)

Aqui está o resultado mais forte da auditoria.

**[FATO] `QT_INGRESSANTE` é constante dentro da trajetória** — 0 dos 28.143 cursos têm mais de um valor. É o tamanho fixo da coorte.

**[FATO] A identidade contábil correta é a versão acumulada, e ela fecha exatamente:**

```
QT_PERMANENCIA(t)
  + Σ_{s≤t} QT_CONCLUINTE(s)
  + Σ_{s≤t} QT_DESISTENCIA(s)
  + Σ_{s≤t} QT_FALECIDO(s)
  = QT_INGRESSANTE
```

→ satisfeita em **281.430 / 281.430 linhas (100,000%)**, resíduo mínimo 0, resíduo máximo 0. Exata em aritmética inteira, sem tolerância.

A versão **anual ingênua** (sem acumular) fecha em apenas 35.789 / 281.430 linhas (12,7%) — ou seja, **falharia** como regra de validação, e é a formulação que o enunciado da pergunta 10 sugere.

Isso estabelece a semântica das quantidades, que os nomes sozinhos não revelam:

| Variável | Natureza [FATO] |
|---|---|
| `QT_INGRESSANTE` | constante da coorte |
| `QT_PERMANENCIA` | **estoque** — alunos com vínculo ativo *no* ano t |
| `QT_CONCLUINTE` | **fluxo anual** — concluíram *naquele* ano |
| `QT_DESISTENCIA` | **fluxo anual** — desistiram *naquele* ano |
| `QT_FALECIDO` | **fluxo anual** |

Confirmação independente por monotonicidade **[FATO]**: `QT_PERMANENCIA` nunca sobe (0 violações em 253.287 transições), enquanto `QT_CONCLUINTE` cai 76.422 vezes e `QT_DESISTENCIA` cai 106.608 vezes — comportamento de fluxo, não de acumulado.

**Falecidos [FATO]:** 1.386 no total, em 1.123 linhas. Numericamente irrelevantes (0,046% da coorte), mas metodologicamente decisivos — ver §4.2.

---

## 4. Os indicadores segundo o dicionário oficial (pergunta 11)

### 4.1 O que o dicionário diz [DICIONÁRIO]

Transcrição literal das posições 27–31 do `Dicionário_acompanhamento_trajetória.docx`:

| Var | Nome oficial | Descrição oficial da categoria |
|---|---|---|
| `TAP` | Taxa de Permanência | "Percentual de ingressantes que estão com vínculo ativo no curso no ano de referência" |
| `TCA` | Taxa de Conclusão Acumulada | "Percentual de ingressantes que concluíram o curso **até** o ano de referência" |
| `TDA` | Taxa de Desistência Acumulada | "Percentual de ingressantes que desistiram do curso **até** o ano de referência" |
| `TCAN` | Taxa de Conclusão Anual | "Percentual de ingressantes que concluíram o curso **no** ano de referência" |
| `TADA` | Taxa de Desistência Anual | "Percentual de ingressantes que desistiram do curso **no** ano de referência" |

E as quantidades correspondentes [DICIONÁRIO]:

| Var | Descrição oficial |
|---|---|
| `QT_INGRESSANTE` | "Número de ingressantes do curso no ano de ingresso da coorte." |
| `QT_PERMANENCIA` | "Número de estudantes que permaneceram no curso de graduação no ano de referência da análise" |
| `QT_CONCLUINTE` | "Número de estudantes que concluíram o curso de graduação no ano de referência da análise" |
| `QT_DESISTENCIA` | "Número de estudantes que desistiram do curso de graduação no ano de referência da análise" |
| `QT_FALECIDO` | "Número de estudantes que faleceram no ano de referência da análise" |

O dicionário **não** publica as fórmulas — em particular, **não diz qual é o denominador**. Recuperei-as empiricamente.

### 4.2 Fórmulas exatas recuperadas dos dados

**[FATO]** Testei cada indicador contra duas hipóteses de denominador — bruto (`QT_INGRESSANTE`) e líquido de falecidos (`QT_INGRESSANTE − Σfalecidos`). Resultado, com tolerância 0,005 p.p.:

| Indicador | Acertos com denominador **líquido** | Acertos com denominador **bruto** |
|---|---|---|
| `TAP` | **281.430 / 281.430** | 276.489 |
| `TCA` | **281.430 / 281.430** | 274.745 |
| `TDA` | **281.430 / 281.430** | 273.898 |
| `TCAN` | **281.430 / 281.430** | 278.030 |
| `TADA` | **281.430 / 281.430** | 277.652 |

**O denominador é `QT_INGRESSANTE − Σ_{s≤t} QT_FALECIDO(s)`, em 100% dos casos, para os cinco indicadores.**

Fórmulas confirmadas:

```
D(t) = QT_INGRESSANTE − Σ_{s≤t} QT_FALECIDO(s)      (denominador "vivo" acumulado)

TAP(t)  = 100 × QT_PERMANENCIA(t)           / D(t)
TCA(t)  = 100 × Σ_{s≤t} QT_CONCLUINTE(s)    / D(t)
TDA(t)  = 100 × Σ_{s≤t} QT_DESISTENCIA(s)   / D(t)
TCAN(t) = 100 × QT_CONCLUINTE(t)            / D(t)
TADA(t) = 100 × QT_DESISTENCIA(t)           / D(t)
```

**Interpretação substantiva:** o Inep trata falecidos como **censura**, removendo-os da população de risco. As taxas são condicionais a estar vivo. Essa é a escolha correta, e é o que torna exata a identidade da seção seguinte.

### 4.3 A identidade TAP + TCA + TDA (pergunta 12)

**[FATO] Não é "aproximadamente 100%". É exatamente 100,00 em 281.430 de 281.430 linhas (100,000%).**

Testei separadamente nos dois regimes, porque a pergunta era especificamente sobre o tratamento de falecidos:

| Grupo | n | mín | máx | média |
|---|---|---|---|---|
| Sem falecidos acumulados | 273.831 | 100,00 | 100,00 | 100,0000 |
| **Com falecidos acumulados** | **7.599** | **100,00** | **100,00** | **100,0000** |

A identidade **não se degrada** na presença de falecidos — precisamente porque eles saem do denominador. Se o denominador fosse bruto, a soma cairia abaixo de 100 nas 7.599 linhas afetadas. A escolha de denominador do Inep é o que faz a identidade fechar.

`TAP + TCA + TDA = 100` é, portanto, uma **restrição estrutural exata**, não uma regularidade empírica.

**Consequência para modelagem (crítica):** os três indicadores vivem num **simplex de 2 graus de liberdade**. Modelar `TDA` usando `TAP` e `TCA` do mesmo ano como preditores é colinearidade perfeita: `TDA = 100 − TAP − TCA`. Um modelo linear fica singular; uma árvore vai "prever" o alvo com R² ≈ 1 e parecer excelente. **Isto é vazamento algébrico, e é a armadilha mais fácil de cair neste dataset.**

### 4.4 Acumuladas vs. anuais (pergunta 13)

**[FATO] Sim, confirmado — mas com uma sutileza.**

Teste de monotonicidade em 253.287 transições ano-a-ano:

| Teste | Violações |
|---|---|
| `TCA(t) < TCA(t−1)` (acumulada deveria não decrescer) | **0** |
| `TDA(t) < TDA(t−1)` (acumulada deveria não decrescer) | **0** |
| `TAP(t) > TAP(t−1)` (permanência deveria não crescer) | **0** |

`TCA` e `TDA` são inequivocamente acumuladas; `TAP` é um estoque monotonicamente decrescente. E `TCAN`/`TADA` batem exatamente contra o fluxo anual dividido por `D(t)` (281.430/281.430, §4.2) — são inequivocamente anuais.

**A sutileza [FATO]:** `TCA(t) ≠ Σ_{s≤t} TCAN(s)` em geral. A soma das anuais bate com a acumulada em apenas 279.743/281.430 (`TCA`) e 276.237/281.430 (`TDA`), com tolerância 0,02 p.p.

**Por quê:** o denominador `D(t)` muda ao longo do tempo quando há falecidos, então as taxas anuais têm bases diferentes e **não são aditivas**. Reconstruir `TDA` somando `TADA` introduz erro em ~1,8% das linhas. **Use `TDA` diretamente; nunca reconstrua por soma de `TADA`.**

### 4.5 Estabilidade das características (pergunta 14)

**[FATO] Todas as covariáveis são 100% constantes dentro da trajetória.** Testei 14 colunas — `NO_IES`, `TP_CATEGORIA_ADMINISTRATIVA`, `TP_ORGANIZACAO_ACADEMICA`, `NO_CURSO`, `CO_REGIAO`, `CO_UF`, `CO_MUNICIPIO`, `TP_GRAU_ACADEMICO`, `TP_MODALIDADE_ENSINO`, `CO_CINE_ROTULO`, `CO_CINE_AREA_GERAL`, `CO_IES`, `NU_PRAZO_INTEGRALIZACAO`, `NU_PRAZO_ACOMPANHAMENTO`. Em todas: **0 cursos com mais de um valor**.

**Mas isso não significa que as características foram estáveis na realidade.** É um artefato de construção, e o dicionário é explícito. Cada uma dessas variáveis é descrita como sendo **"no último ano de análise"** [DICIONÁRIO]:

> `CO_IES`: "Código único de identificação da instituição de educação superior em que o curso está localizado **no último ano de análise**."
>
> `TP_CATEGORIA_ADMINISTRATIVA`: "Código da categoria Administrativa da IES **no último ano de análise**."
>
> `TP_MODALIDADE_ENSINO`: "Código da modalidade de ensino do curso **no último ano de análise**."

Ou seja: **todos os atributos são um retrato de 2024, retro-aplicado aos 10 anos da trajetória.**

**[FATO] Confirmei isso empiricamente contra o Censo 2024.** Cruzando os 28.143 cursos com `MICRODADOS_CADASTRO_CURSOS_2024.CSV`, 22.864 casam (81,24%), e nesses:

| Atributo | Concordância trajetória × Censo 2024 |
|---|---|
| `TP_MODALIDADE_ENSINO` | 22.864 / 22.864 (**100%**) |
| `TP_CATEGORIA_ADMINISTRATIVA` | 22.864 / 22.864 (**100%**) |
| `TP_GRAU_ACADEMICO` | 22.864 / 22.864 (**100%**) |

Concordância perfeita, sem uma única discordância. Está provado: **as covariáveis da base de trajetória são o snapshot de 2024**.

**Esta é uma ameaça de validade de primeira ordem, e é o segundo achado mais importante desta auditoria.** Um curso que era municipal em 2015 e virou privado em 2020 aparece como privado durante toda a trajetória — inclusive nos anos em que era público. Uma IES que virou universidade em 2019 aparece como universidade em 2015. **As covariáveis são medidas DEPOIS do desfecho.** Isso reaparece em §9 (vazamento) e §10 (causalidade), onde é fatal.

---

## 5. O que podemos responder

Com esta base, sozinha, e de forma **defensável**:

1. **Qual foi o destino final da coorte 2015 ao fim de 10 anos**, no total e por qualquer recorte disponível — com decomposição exata em permanência / conclusão / desistência, e a identidade fechando em 100%.
2. **Qual o formato temporal da evasão** — em que ano da trajetória a desistência ocorre. Perfil de hazard com 10 pontos por curso.
3. **Onde a desistência se concentra** — modalidade, categoria administrativa, organização acadêmica, grau, área CINE, UF, município, IES, e interações.
4. **Quanta heterogeneidade é institucional vs. de curso** (já medido: ICC ≈ 0,65 — §8).
5. **Se existem perfis distintos de trajetória** — evasão precoce vs. tardia vs. crônica, via clustering de curvas.
6. **Quão previsível é o desfecho final a partir dos anos iniciais** — com as ressalvas severas de §9.
7. **Associações ajustadas** entre atributos do curso e evasão — explicitamente rotuladas como associação.

---

## 6. O que NÃO podemos responder

Esta seção é tão importante quanto a anterior. Cada item abaixo é uma pergunta que **parece** respondível com esta base e **não é**.

1. **Nada sobre alunos individuais.** Os dados são agregados por curso. Qualquer afirmação sobre "o perfil do aluno que evade" é **falácia ecológica**. Não há sexo, idade, renda, cor/raça, nota de ingresso, situação de trabalho.

2. **Nada sobre tendência temporal da evasão no Brasil.** **[FATO]** Há uma única coorte. É impossível dizer "a evasão aumentou/diminuiu". Não existe coorte 2016 para comparar. Variação em `NU_ANO_REFERENCIA` é **idade da coorte**, não **tempo histórico**. Confundir os dois seria o erro mais grave possível neste projeto — e é um erro fácil de cometer, porque o eixo se chama "ano".

3. **Nada sobre o efeito causal de qualquer atributo.** Ver §10. Não há aleatorização, não há descontinuidade, não há período pré-tratamento, e as covariáveis são pós-desfecho.

4. **Distinção entre evasão do curso e evasão do sistema.** O aluno que troca de curso conta como desistência aqui. Não sabemos se saiu do ensino superior ou apenas migrou. Isso **superestima** a evasão real do sistema, e superestima **diferencialmente** onde a transferência interna é comum (IES grandes, EAD) — o que contamina justamente a comparação entre modalidades. O microdado 2024 tem `QT_SIT_TRANSFERIDO`, mas em nível de curso-ano e não rastreável ao indivíduo; não resolve.

5. **Efeito da pandemia.** A coorte 2015 estava em τ=5 em 2020. Sem outras coortes, não há como separar "efeito COVID" de "efeito de estar no 5º ano de curso". Perfeitamente confundido.

6. **Validação preditiva fora da amostra no tempo.** Não existe coorte futura para validar. Ver §9.

7. **Análise regional para EAD.** **[FATO]** 11.180 linhas sem geografia, por construção.

8. **Nada sobre cursos com menos de 4 ingressantes, cursos criados após 2015, ou cursos extintos antes de 2024** (§7.D).

---

## 7. Melhor pergunta principal

### A. Pergunta principal (recomendada)

> **Como a desistência se distribui e se acumula ao longo de dez anos na coorte de ingressantes de 2015 da graduação brasileira, quais dimensões institucionais e de área concentram o risco, e em que medida o desfecho de dez anos já é discernível a partir dos anos iniciais da trajetória?**

Por que esta e não outra:

- É **descritiva-preditiva**, não causal — honesta quanto ao que os dados sustentam.
- Cobre os sete pilares de Big Data Analytics exigidos, sem forçar nenhum.
- Não usa "efeito" nem "impacto".
- "Em que medida... já é discernível" é deliberado: transforma o exercício preditivo numa **pergunta de mensuração de antecipabilidade**, que é respondível, em vez de numa promessa de forecasting, que não é (§9).

### B. Perguntas secundárias

**Descritivas / estruturais**

1. Qual o destino final da coorte 2015 aos 10 anos, e como se decompõe em permanência/conclusão/desistência?
2. Onde a desistência se concentra: modalidade, categoria administrativa, organização acadêmica, grau, área CINE, região?
3. Quanto da variação do desfecho é *entre instituições* e quanto é *entre cursos da mesma instituição*?
4. Quanto da diferença bruta entre modalidades sobrevive ao ajuste por IES e área?

**Longitudinais**

5. Qual o perfil temporal do hazard de desistência ao longo de τ = 0..9? Onde está o pico?
6. O perfil temporal difere em **forma** entre grupos, ou apenas em **nível**?
7. Existem tipologias distintas de curva de trajetória? Quantas, e quem as habita?
8. Como `NU_PRAZO_INTEGRALIZACAO` reorganiza o calendário da evasão?

**Preditivas**

9. Observando apenas τ ≤ 2, quão bem se antecipa o desfecho em τ=9 — e quanto disso é ganho informacional real vs. aninhamento algébrico?
10. Entre os alunos ainda ativos em τ=2, o que prediz a desistência **subsequente**?
11. Um modelo treinado num conjunto de IES generaliza para IES nunca vistas?

### C. Unidade analítica

Duas, deliberadamente:

- **Descritiva e longitudinal:** `curso × ano` (281.430 obs) — o painel completo.
- **Preditiva:** `curso` (28.143 obs) — uma linha por trajetória, painel pivotado para formato largo. Modelar em formato longo seria pseudo-replicação por fator 10.

### D. População

**População-alvo:** ingressantes de 2015 em cursos de graduação brasileiros presentes no Censo da Educação Superior, em cursos que ainda existiam em 2024 e tinham ≥ 4 ingressantes em 2015.

Esta definição contém **duas seleções que precisam ser declaradas explicitamente no relatório final**:

- **[FATO]** Corte inferior de 4 ingressantes (§3.3).
- **[HIPÓTESE, fortemente sugerida pela evidência]** **Seleção por sobrevivência do curso.** Como a identificação é feita "no último ano de análise", um curso extinto entre 2015 e 2024 plausivelmente não entra na base. Isso é **seleção pelo desfecho**: cursos fechados provavelmente tinham evasão alta. **A evasão medida aqui é, portanto, provavelmente subestimada.** Não consigo quantificar o viés sem o Censo 2015 (§12). Declare como limitação.

### E. Outcomes

| Papel | Outcome | Justificativa |
|---|---|---|
| **Primário** | `TDA` em `NU_ANO_REFERENCIA = 2024` | Desistência acumulada aos 10 anos. Definido para 100% dos cursos. Contínuo em [0,100]. |
| Secundário | `TCA(2024)` | Conclusão — o espelho. **Não** modelar junto com `TDA` e `TAP` (simplex, §4.3). |
| Longitudinal | `TADA(τ)`, τ=0..9 | Hazard anual. |
| Preditivo (recomendado) | `TDA(9) − TDA(2)` e `[TDA(9) − TDA(2)] / TAP(2)` | Desistência **tardia** e taxa **condicional** entre sobreviventes. São os alvos que evitam o aninhamento — ver §9.3. |
| Classificação | `1[TDA(2024) ≥ 75]` | **[FATO]** p80 ≈ 75,8; 6.140 cursos (21,8%) ≥ 75. Corte redondo, prevalência sadia. |

### F. Principais dimensões analíticas

`TP_MODALIDADE_ENSINO` · `TP_CATEGORIA_ADMINISTRATIVA` (e o agrupamento público/privado) · `TP_ORGANIZACAO_ACADEMICA` · `TP_GRAU_ACADEMICO` · `CO_CINE_AREA_GERAL` (10 áreas) · `CO_CINE_ROTULO` (granular) · `CO_REGIAO` / `CO_UF` / `CO_MUNICIPIO` (presencial) · `NU_PRAZO_INTEGRALIZACAO` · `QT_INGRESSANTE` (porte) · `CO_IES` (efeito institucional) · `τ` (tempo de trajetória).

---

## 8. Descriptive Analytics recomendado

Os números abaixo **já foram calculados** nesta auditoria e podem servir de espinha dorsal do relatório final. Todos são **[FATO]**.

### 8.1 O retrato de 10 anos

Coorte 2015, situação em 2024 (28.143 cursos, 3.027.277 ingressantes):

| Indicador | Média simples entre cursos | Ponderada por ingressantes |
|---|---|---|
| `TDA` (desistência acumulada) | **58,58%** | **≈ 60,5%** |
| `TCA` (conclusão acumulada) | 40,17% | — |
| `TAP` (ainda ativos) | 1,25% | 1,00% |

Distribuição de `TDA(2024)` entre cursos: mín 0 | p10 30,95 | p25 45,21 | **mediana 59,60** | p75 72,73 | p90 84,03 | máx 100 | dp 20,69.

**Manchete defensável:** aproximadamente **três em cada cinco** ingressantes de 2015 haviam desistido do curso em que entraram, dez anos depois. (Com a ressalva de §6.4: é desistência **do curso**, não necessariamente do sistema.)

Casos extremos: 135 cursos com `TDA` = 0; 997 cursos com `TDA` = 100 — estes últimos são pequenos (mediana de 11 ingressantes), o que é ruído amostral, não catástrofe institucional. **Trate as taxas de cursos pequenos com desconfiança explícita** (§13, R4).

### 8.2 Onde a desistência se concentra

**Por área CINE** (ponderada por ingressantes) — o recorte com maior amplitude:

| Área CINE | Cursos | Ingressantes | `TDA` pond. |
|---|---|---|---|
| 06 Computação e TIC | 1.797 | 141.426 | **70,57** |
| 07 Engenharia, produção e construção | 4.558 | 450.925 | 65,83 |
| 05 Ciências naturais, matemática e estatística | 780 | 42.091 | 62,55 |
| 04 Negócios, administração e direito | 7.146 | 1.037.961 | 61,42 |
| 10 Serviços | 680 | 66.534 | 59,16 |
| 02 Artes e humanidades | 1.212 | 72.203 | 58,60 |
| 01 Educação | 5.581 | 562.752 | 58,05 |
| 03 Ciências sociais, comunicação e informação | 1.481 | 140.780 | 58,05 |
| 09 Saúde e bem-estar | 4.087 | 444.958 | 54,97 |
| 08 Agricultura, silvicultura, pesca e veterinária | 821 | 67.647 | **51,97** |

Amplitude ≈ 18,6 p.p. — **a dimensão mais informativa da base**.

**Por modalidade:**

| Modalidade | Cursos | Ingressantes | `TDA` pond. | `TCA` médio |
|---|---|---|---|---|
| Presencial | 27.025 | 2.297.858 | 58,93 | 40,60 |
| EAD | 1.118 | 729.419 | **65,28** | 29,80 |

Note a assimetria estrutural: **EAD é 4,0% dos cursos mas 24,1% dos ingressantes.** Porte médio 652 ingressantes (EAD) vs. 85 (presencial). Isso obriga a reportar médias ponderadas e não ponderadas lado a lado — elas contam histórias diferentes (`TDA` médio simples do EAD é 69,59; ponderado, 65,28).

**Por categoria administrativa:**

| Categoria | Cursos | Ingressantes | `TDA` pond. |
|---|---|---|---|
| 1 Pública Federal | 5.486 | 337.805 | 54,63 |
| 2 Pública Estadual | 2.692 | 168.626 | 50,83 |
| 3 Pública Municipal | 228 | 13.271 | 51,67 |
| **4 Privada com fins lucrativos** | **11.167** | **1.721.739** | **64,45** |
| 5 Privada sem fins lucrativos | 8.244 | 764.602 | 56,61 |
| 7 Especial | 326 | 21.234 | 50,38 |

O contraste privado-com-fins-lucrativos (64,45) vs. pública estadual (50,83) é de ~13,6 p.p. e cobre 57% dos ingressantes na categoria 4.

**Por grau acadêmico:** Tecnológico 63,00 > Bacharelado 60,47 > Licenciatura 58,01.

**Por organização acadêmica:** IF 64,64 > Centro Universitário 62,27 > Faculdade 59,10 ≈ Universidade 59,67.

**Por região (presencial apenas):**

| Região | Cursos | `TDA` pond. |
|---|---|---|
| 1 Norte | 1.922 | 59,48 |
| 2 Nordeste | 5.117 | 58,90 |
| 3 Sudeste | 12.200 | 59,00 |
| 4 Sul | 5.272 | 58,06 |
| 5 Centro-Oeste | 2.514 | 59,63 |

**Achado negativo importante:** amplitude de **1,6 p.p.** entre regiões. **A geografia macro quase não importa.** Isso é um resultado publicável e contraintuitivo — a desigualdade da evasão brasileira é **setorial e institucional, não regional**. Reporte-o como achado, não o esconda por ser "nulo".

### 8.3 Entregáveis descritivos recomendados

1. Funil da coorte 2015→2024 (waterfall dos 3.027.277 ingressantes).
2. Ranking de `TDA` por área CINE, com IC bootstrap e ponderação explícita.
3. Painel de barras pareadas ponderada vs. não ponderada, para tornar visível o efeito do porte.
4. Distribuição de `TDA(2024)` entre cursos (histograma + densidade), estratificada por modalidade.
5. Heatmap área CINE × categoria administrativa.
6. Mapa coroplético por UF (presencial), com a nota de que a amplitude é pequena — o mapa deve **desmentir** a expectativa, e a escala de cor precisa ser honesta quanto a isso.
7. Decomposição de variância entre-IES vs. intra-IES (§8.4).
8. Curva de Lorenz / concentração: qual fração dos cursos concentra qual fração das desistências.

### 8.4 Estrutura de agrupamento — usar isto no desenho preditivo

**[FATO]** 2.158 IES, mediana de 5 cursos por IES, média 13,0, máximo 898.

**[FATO] Proxy de ICC (variância entre-IES / variância total) do `TDA(2024)` = 0,6476**, calculado sobre as 1.780 IES com ≥2 cursos (variância total 428,0; variância entre-IES 277,2).

**Aproximadamente 65% da variação do desfecho é institucional, não do curso.** Este único número tem três consequências:

- justifica modelos multinível / efeitos aleatórios por IES;
- **exige** `GroupKFold` por `CO_IES` na validação (§9.7);
- sugere que a pergunta "qual curso evade" é, em boa medida, a pergunta "qual instituição".

---

## 9. Análise longitudinal e Predictive Analytics recomendados

### 9.1 O perfil temporal (análise longitudinal)

**[FATO]** Evolução agregada da coorte 2015 (médias entre cursos, e ponderadas):

| τ | Ano | `TAP` pond. | `TDA` médio | `TADA` pond. | `TCAN` pond. | Hazard condicional |
|---|---|---|---|---|---|---|
| 0 | 2015 | 86,40 | 12,71 | 12,97 | 0,62 | 12,97 |
| 1 | 2016 | 68,08 | 27,92 | **15,94** | 2,38 | 18,45 |
| 2 | 2017 | 51,85 | 38,55 | 11,16 | 5,07 | 16,39 |
| 3 | 2018 | 34,67 | 46,08 | 8,01 | 9,16 | 15,45 |
| 4 | 2019 | 18,23 | 51,68 | 5,69 | **10,75** | 16,42 |
| 5 | 2020 | 9,10 | 54,36 | 2,67 | 6,46 | 14,64 |
| 6 | 2021 | 5,30 | 55,83 | 1,54 | 2,26 | 16,94 |
| 7 | 2022 | 3,17 | 57,02 | 1,11 | 1,02 | 20,87 |
| 8 | 2023 | 1,81 | 58,00 | 0,83 | 0,53 | 26,32 |
| 9 | 2024 | 1,00 | 58,58 | 0,53 | 0,28 | 29,13 |

**Achados longitudinais [FATO]:**

- **A evasão é brutalmente precoce.** τ=0 e τ=1 concentram **28,9 p.p. dos ~60 p.p. totais** — quase metade de toda a evasão de dez anos ocorre nos **dois primeiros anos**. Qualquer política derivada deste projeto aponta para o primeiro ano.
- O hazard **bruto** desaba monotonicamente (12,97 → 0,53), mas o hazard **condicional** (desistências sobre a população ainda em risco) é aproximadamente **plano em ~15–18% e depois sobe** para 29% em τ=9. Ou seja: quem permanece muito além do prazo tem risco crescente, não decrescente. Essa distinção entre hazard bruto e condicional é exatamente o tipo de nuance que separa uma análise longitudinal séria de uma série de gráficos de linha.
- Conclusão tem pico em τ=4 (`TCAN` 10,75), coerente com bacharelados de 4–5 anos.

**Métodos recomendados:**

1. Curvas tipo Kaplan-Meier construídas do agregado (não é sobrevivência individual — chame de "curvas de estado da coorte", não de KM, para não sugerir microdado).
2. Decomposição do hazard condicional por grupo, testando **forma** e não só nível.
3. **Clustering de trajetórias** (k-means / k-medoids sobre os vetores `TADA(0..9)` normalizados, ou GMM). Este é o entregável longitudinal mais forte: gera uma tipologia empírica ("evasão precoce aguda", "sangramento crônico", "retenção com conclusão tardia") e depois caracteriza quem habita cada cluster. Alto valor para a disciplina, baixo risco metodológico.
4. Modelo misto de crescimento com intercepto aleatório por IES — usa diretamente o ICC de 0,65.

### 9.2 O desenho que você propôs: avaliação honesta

Desenho proposto: **informações até τ+2 → `TDA` no fim do acompanhamento** (`X_2015:2017 → TDA_2024`).

**Veredito: é implementável, e a mecânica anti-vazamento entre anos é correta e necessária. Mas o desenho, como enunciado, tem três problemas — um deles fatal para a interpretação usual — e precisa ser reformulado.**

#### Problema 1 — FATAL PARA A INTERPRETAÇÃO: o alvo está aninhado no preditor

`TDA` é acumulada e **[FATO]** monotonicamente não-decrescente (0 violações em 253.287 transições). Logo:

```
TDA(9) ≥ TDA(2)   sempre, por construção
```

**[FATO]** `TDA(2)` já representa em média **64,2%** do valor de `TDA(9)` (médias: 38,55 vs. 58,58).

**[FATO]** `corr(TDA(2), TDA(9)) = 0,744`.

Esse R² ≈ 0,55 **não é poder preditivo**. É, em sua maior parte, a tautologia de que uma soma parcial correlaciona com a soma total que a contém. Um R² de 0,55 apresentado como "conseguimos prever a evasão futura" seria enganoso, e um avaliador atento detectaria imediatamente.

E o efeito piora se você atrasar o cutoff: **[FATO]** `corr(TDA(3), TDA(9)) = 0,842`. Quanto mais tarde o corte, mais "preditivo" o modelo parece — e menos útil ele é. **Um cutoff mais tardio deve ser lido como um resultado pior, não melhor.**

Correlações brutas com `TDA(9)` **[FATO]**: `TDA(0)` 0,451 · `TDA(1)` 0,636 · `TDA(2)` 0,744 · `TDA(3)` 0,842 · `TAP(2)` −0,441 · `TCA(2)` −0,282.

#### Problema 2 — FATAL PARA A VALIDAÇÃO TEMPORAL: existe uma única coorte

**[FATO]** `NU_ANO_INGRESSO` tem um único valor. Portanto:

- não existe coorte 2016 para testar um modelo treinado na coorte 2015;
- **não existe cutoff temporal real** no sentido de backtesting;
- não é possível qualquer split temporal fora da amostra.

O que o desenho realmente faz é: usar informação inicial da **mesma** coorte para prever o desfecho final da **mesma** coorte. A generalização testável não é "para o futuro", é **"para cursos e instituições não vistos"**.

**Isto precisa ser dito explicitamente no relatório final.** Chamar isso de "previsão do futuro" seria uma deturpação. Chame de **antecipação precoce dentro de coorte, validada por generalização institucional.**

#### Problema 3 — as features não são contemporâneas ao cutoff

**[FATO]** (§4.5) todas as covariáveis são o snapshot de **2024**. Um modelo que usa `TP_CATEGORIA_ADMINISTRATIVA` para prever com corte em 2017 está usando informação de 2024 — **posterior ao desfecho**. É vazamento temporal genuíno, embora provavelmente pequeno para atributos estáveis.

**Mitigação:** classifique as features por estabilidade plausível e reporte separadamente.

- Baixo risco (quase imutáveis): `CO_CINE_AREA_GERAL`, `CO_CINE_ROTULO`, `TP_GRAU_ACADEMICO`, `NU_PRAZO_INTEGRALIZACAO`.
- Risco moderado: `TP_MODALIDADE_ENSINO`, `CO_UF`, `CO_MUNICIPIO`.
- **Risco alto (podem ter mudado como consequência do próprio desempenho):** `TP_CATEGORIA_ADMINISTRATIVA`, `TP_ORGANIZACAO_ACADEMICA`, `CO_IES`.

Rode o modelo com e sem o grupo de alto risco e reporte a diferença. Se for pequena, você neutralizou a objeção; se for grande, você achou um resultado interessante.

### 9.3 Reformulação recomendada do alvo

Substitua o alvo único por **três**, reportados juntos. É o que transforma o problema de tautológico em científico.

| Alvo | Definição | Por que |
|---|---|---|
| **T1** (referência) | `TDA(9)` | Comparabilidade com a literatura. Reportar sabendo do aninhamento. |
| **T2 (principal)** | `TDA(9) − TDA(2)` | **Desistência tardia.** Remove o componente aninhado. **[FATO]** média 20,03, dp 15,10, mediana 17,30, p25 9,23, p75 27,69. E `corr(TDA(2), T2) = −0,401` — **negativa**, ou seja, T2 **não** é trivialmente predito por `TDA(2)`. Alvo genuíno. |
| **T3 (mais interpretável)** | `[TDA(9) − TDA(2)] / TAP(2)` | **Taxa condicional de desistência entre os ainda ativos em τ=2.** **[FATO]** definida para 26.915 cursos (95,6%); média 41,33%, mediana 37,72%; `corr(TDA(2), T3) = 0,171` — quase ortogonal ao passado. **Este é o alvo cientificamente mais defensável de toda a base.** |

Interpretação de T3, que é a frase de efeito do projeto: *dos alunos que ainda estavam matriculados ao fim do segundo ano, cerca de 41% ainda viriam a desistir.*

**Alvo de classificação:** `1[TDA(9) ≥ 75]` — **[FATO]** 6.140 cursos, 21,8% de prevalência.

### 9.4 Unidade de modelagem

**Uma linha por `CO_CURSO`** — 28.143 observações. Painel pivotado para largo. Modelar em formato longo (281.430 linhas) seria pseudo-replicação: dez linhas do mesmo curso não são dez observações independentes.

### 9.5 Cutoff temporal e features permitidas

**Cutoff: τ ≤ 2 (anos de referência 2015, 2016, 2017).** Justificativa: é onde está a informação (28,9 dos ~60 p.p. de evasão já ocorreram), e é cedo o bastante para ter valor prático de intervenção. Reporte também τ ≤ 1 como cenário mais rigoroso, e τ ≤ 3 apenas para demonstrar a inflação artificial do R² (§9.2, problema 1).

**Features permitidas (todas com `NU_ANO_REFERENCIA ≤ 2017`):**

*Dinâmicas (do painel, τ = 0,1,2):*
- `TADA(0)`, `TADA(1)`, `TADA(2)` — hazard anual
- `TCAN(0..2)`
- `TDA(2)`, `TAP(2)`, `TCA(2)` — **escolher no máximo dois dos três** (simplex, §4.3)
- Deltas e forma: `TADA(1) − TADA(0)`, `TADA(2) − TADA(1)`, inclinação ajustada, curvatura
- Contagens absolutas `QT_DESISTENCIA(0..2)` (informação de precisão que a taxa perde)

*Estáticas:*
- `QT_INGRESSANTE` (e `log`) — porte
- `CO_CINE_AREA_GERAL`, `CO_CINE_ROTULO` (target-encoded **dentro do fold**)
- `TP_GRAU_ACADEMICO`, `TP_MODALIDADE_ENSINO`, `NU_PRAZO_INTEGRALIZACAO`, `NU_PRAZO_ACOMPANHAMENTO`
- `TP_CATEGORIA_ADMINISTRATIVA`, `TP_ORGANIZACAO_ACADEMICA` — **marcadas como risco alto** (§9.2, problema 3)
- `CO_REGIAO` / `CO_UF` com categoria explícita "EAD/sem geografia" (**nunca** imputar)

**Features PROIBIDAS — lista de bloqueio explícita:**

| Proibido | Motivo |
|---|---|
| Qualquer coluna com `NU_ANO_REFERENCIA` > 2017 | vazamento temporal direto |
| `TAP`, `TCA`, `TDA` de τ ≥ 3 | idem |
| `TAP(2)` **e** `TCA(2)` **e** `TDA(2)` juntos | colinearidade perfeita (§4.3) |
| `NU_ANO_MAXIMO_ACOMPANHAMENTO` bruto | redundante com `NU_PRAZO_ACOMPANHAMENTO` (`NU_ANO_INGRESSO` é constante) |
| `NO_CURSO`, `NO_IES` como texto livre | identificadores; alta cardinalidade, memorização |
| Qualquer variável do Censo 2024 | medida **após** o desfecho (§12) |
| Estatísticas de encoding computadas na base completa | vazamento por pré-processamento |

### 9.6 Baseline (obrigatório — é o que dá sentido às métricas)

Reporte, em escada:

1. **B0 — média global.** R² = 0 por construção.
2. **B1 — média por área CINE.** Só as 10 áreas.
3. **B2 — regressão linear apenas com `TDA(2)`.** **Este é o baseline crítico**, porque é ele que quantifica a tautologia. Para o alvo T1 ele já entrega R² ≈ 0,55 sem nenhum aprendizado.
4. **B3 — média por IES** (com regularização; usa o ICC de 0,65).
5. **B4 — regressão linear com todas as features permitidas.**

**Um modelo complexo só se justifica pelo ganho sobre B2 e B3, nunca sobre B0.** Reportar "R² = 0,60!" contra B0 quando B2 já entrega 0,55 seria desonesto. Reporte sempre o **delta**.

### 9.7 Estratégia de validação — o ponto mais importante

Você pediu atenção especial ao vazamento entre anos da mesma trajetória. **Esse problema está resolvido por construção** ao usar uma linha por curso (§9.4) — nenhuma trajetória se divide entre treino e teste, porque a trajetória inteira **é** a linha.

**Mas existe um vazamento maior e menos óbvio, e ele é o risco real deste projeto: o vazamento entre cursos da mesma IES.**

**[FATO]** ICC ≈ 0,65 — dois terços da variância do desfecho são institucionais. Uma IES com 898 cursos teria, sob `KFold` aleatório, ~718 cursos no treino e ~180 no teste. O modelo aprende "esta é a IES 1491, que evade 70%" e o reproduz no teste. A performance seria inflada e não generalizaria para nenhuma instituição nova.

**Regra:**

> **`GroupKFold` (ou `StratifiedGroupKFold`) com `groups = CO_IES`. 5 folds. Nenhuma IES aparece em treino e teste simultaneamente.**

Protocolo completo:

1. **Split externo:** `GroupShuffleSplit` por `CO_IES`, 20% das IES retidas como holdout, tocado **uma única vez** no final.
2. **Split interno:** `StratifiedGroupKFold` (5 folds, grupos = `CO_IES`, estratificado por quintil do alvo) para seleção de hiperparâmetros.
3. **Todo** pré-processamento (imputação, escala, target encoding de CINE, encoding de IES) **dentro** do `Pipeline`, ajustado apenas no fold de treino.
4. **Reporte os dois esquemas lado a lado** — `KFold` aleatório e `GroupKFold` por IES. A diferença entre eles **é um resultado do projeto**: ela mensura empiricamente quanto do desempenho aparente é memorização institucional. Essa comparação vale mais que qualquer modelo isolado.
5. Ponderação por `QT_INGRESSANTE` ou exclusão de cursos com < 20 ingressantes como **análise de sensibilidade**, não como escolha principal.

### 9.8 Modelos

Escada de complexidade, cada degrau justificado pelo anterior:

1. **OLS / GLM** com as features permitidas — interpretável, referência.
2. **Regressão beta** ou GLM binomial com `logit` — o alvo é uma proporção em [0,100] com massa nos extremos (135 cursos em 0; 997 em 100). OLS é tecnicamente mal-especificado, e demonstrar consciência disso é um ponto metodológico a favor.
3. **Modelo misto** com intercepto aleatório por `CO_IES` — usa diretamente o ICC de 0,65. **Provavelmente o modelo mais adequado ao problema**, e o mais alinhado com a estrutura real dos dados.
4. **Random Forest** — não-linearidades e interações.
5. **Gradient Boosting** (LightGBM/XGBoost) — provável melhor desempenho bruto; suporte nativo a categóricas de alta cardinalidade.
6. **Interpretação:** SHAP sobre o melhor modelo, **sempre com linguagem associativa** ("está associado a", nunca "causa"). Comparar a ordenação SHAP com os coeficientes do modelo misto — concordância reforça, discordância é achado.

Não recomendo redes neurais: 28.143 linhas tabulares, sem ganho esperado sobre boosting, e custo interpretativo alto.

### 9.9 Métricas

**Regressão (T1, T2, T3):** MAE (unidade natural: pontos percentuais), RMSE, R², e **ΔR² sobre B2** — a métrica que realmente importa. Spearman entre predito e observado. Análise de resíduos por área CINE, por porte e por modalidade, para detectar subgrupos onde o modelo falha.

**Classificação (`TDA ≥ 75`):** ROC-AUC, **PR-AUC** (prevalência 21,8% — PR-AUC é a métrica honesta), Brier score, curva de calibração, e **precision@k** (`k` = 500 e 1.000 cursos) — a métrica operacional: *se o MEC pudesse examinar 500 cursos, quantos seriam de fato de alto risco?*

**Reporte tudo com intervalos entre folds**, não como número único.

### 9.10 Prevenção de vazamento — checklist executável

- [ ] Uma linha por `CO_CURSO`; nenhuma trajetória dividida entre treino e teste.
- [ ] Nenhuma coluna com `NU_ANO_REFERENCIA` > cutoff — verificado por asserção automática no código, não por inspeção visual.
- [ ] `GroupKFold` por `CO_IES`; asserção de interseção vazia de IES entre folds.
- [ ] No máximo dois de {`TAP(2)`, `TCA(2)`, `TDA(2)`} (simplex exato).
- [ ] Todo encoding/imputação dentro do `Pipeline`.
- [ ] Target encoding de CINE/IES ajustado apenas no fold de treino.
- [ ] Nenhuma variável do Censo 2024 nas features.
- [ ] Holdout externo tocado uma única vez.
- [ ] Alvos T2/T3 reportados junto com T1, com o aninhamento explicado no texto.
- [ ] `KFold` aleatório vs. `GroupKFold` reportados lado a lado.

---

## 10. Viabilidade de inferência causal

Avaliação honesta, tratamento por tratamento.

### 10.1 Treatment A — Modalidade: presencial vs. EAD

| Critério | Avaliação |
|---|---|
| **Treatment** | `TP_MODALIDADE_ENSINO` ∈ {1, 2} |
| **Outcome** | `TDA(2024)` |
| **Temporalidade** | **VIOLADA.** **[FATO]** A modalidade é registrada "no último ano de análise" (2024) — nove anos **depois** do início da exposição. Um curso que era presencial em 2015 e migrou para EAD aparece como EAD desde 2015. O tratamento é medido após o desfecho. Isso, sozinho, já impede identificação. |
| **Confundidores** | **Catastróficos e não observados.** Perfil socioeconômico, idade, situação de trabalho, seletividade do ingresso, preparo prévio — **nenhum** está na base. Alunos EAD são sistematicamente mais velhos, mais trabalhadores e de menor renda. Esse é *o* confundidor, e ele é integralmente invisível aqui. |
| **Overlap / positividade** | **VIOLADO em regiões grandes do suporte.** **[FATO]** Por área CINE, cursos EAD: área 05 → **1 curso**; área 08 → **2**; área 03 → **12**; área 02 → **22**; área 09 → **32**. Não há comparabilidade nessas áreas. Por região, o overlap é **nulo por construção** — EAD não tem geografia (§3.2). |
| **Selection bias** | **Extremo. [FATO]** Só 146 das 2.158 IES ofertam EAD. **Os 10 maiores ofertantes concentram 74,82% de todos os ingressantes EAD.** 83,18% dos ingressantes EAD estão em IES privadas com fins lucrativos. O "tratamento" é essencialmente *"estudar em um de ~10 grandes grupos educacionais privados"*, não *"estudar a distância"*. |
| **Confundimento não observado** | Decisivo. Sem covariáveis de aluno, qualquer estimativa é confundida por composição. |
| **SUTVA** | **Violado.** A expansão do EAD alterou o próprio pool de comparação presencial (equilíbrio geral): alunos que teriam ido ao presencial foram para o EAD, mudando a composição de **ambos** os braços. Além disso, "EAD" não é um tratamento único — abrange desenhos pedagógicos radicalmente distintos (violação de consistência). |
| **Identificação** | **NÃO IDENTIFICADO.** |

**Veredito A: não existe estimativa causal defensável do efeito da modalidade nesta base.** A diferença bruta de 6,4 p.p. (65,28 vs. 58,93) é uma **diferença descritiva de composição**, e não deve ser apresentada de outra forma.

**O que é defensável:** **[FATO]** existem **598 estratos IES × `CO_CINE_ROTULO`** contendo simultaneamente cursos presenciais e EAD (1.385 presenciais, 612 EAD — 55% de todos os cursos EAD), e 341 estratos no nível IES × área geral. Uma comparação **dentro da mesma instituição e do mesmo rótulo de curso** remove o confundimento institucional e de área — que é a maior parte do confundimento *observável*.

Isto é valioso e recomendo fazer. **Mas rotule-o corretamente:** *associação ajustada dentro de instituição e área*, com validade externa restrita às 142 IES que ofertam ambas as modalidades. **Não é um efeito causal**, porque o confundimento de composição de alunos permanece inteiramente intacto. Apresentá-lo como "efeito do EAD" seria o erro que esta seção existe para prevenir.

### 10.2 Treatment B — Categoria administrativa (pública vs. privada)

| Critério | Avaliação |
|---|---|
| **Temporalidade** | **VIOLADA.** Mesmo problema: categoria de 2024 (§4.5). E aqui é pior — mudanças de categoria administrativa (aquisições, fusões, mudança de mantenedora) são **plausivelmente consequência** de desempenho institucional. É uma variável pós-tratamento. Condicionar nela pode **induzir** viés de colisor, não apenas deixar de removê-lo. |
| **Confundidores** | Seletividade do ingresso é o confundidor dominante — federais e estaduais selecionam via vestibular/ENEM competitivo. **Ausente da base.** A diferença observada é largamente diferença de preparo prévio dos alunos. |
| **Overlap** | Melhor que modalidade (todas as categorias presentes em todas as áreas e regiões), mas o suporte é desbalanceado (228 cursos municipais vs. 11.167 privados com fins lucrativos). |
| **Selection bias** | Auto-seleção total de alunos entre setores, por nota e por renda. |
| **SUTVA** | Violado: expansão do setor privado (ProUni, FIES) alterou a composição de ambos os setores ao longo do período. |
| **Identificação** | **NÃO IDENTIFICADO.** |

**Veredito B: não identificado.** A diferença de ~13,6 p.p. entre privada com fins lucrativos (64,45) e pública estadual (50,83) é real e importante como **descrição**, e vale reportar. Mas atribuí-la ao caráter público/privado da instituição é injustificado.

### 10.3 Treatment C — Outras características

- **Organização acadêmica** (universidade vs. faculdade): mesmos problemas, e o status de universidade é conquistado por desempenho — pós-tratamento por excelência. **Não identificado.**
- **Grau acadêmico** e **área CINE**: não são tratamentos em nenhum sentido útil. São escolhas do aluno; o "efeito" da área é indistinguível de quem escolhe a área. **Não identificado.**
- **Prazo de integralização**: mais interessante — é uma característica estrutural do curso, menos sujeita à auto-seleção. Mas é determinado por diretrizes curriculares nacionais **por área**, então está quase perfeitamente confundido com área. **Não identificado.**

### 10.4 Por que nenhum desenho quase-experimental salva a análise

Verifiquei sistematicamente cada estratégia padrão:

| Desenho | Por que falha aqui |
|---|---|
| **DiD** | Exige períodos pré e pós-tratamento. **[FATO]** O tratamento é fixo dentro da trajetória (§4.5) e há uma única coorte. Não há "antes". **Impossível.** |
| **Event study** | Idem — nenhuma variação temporal no tratamento. **Impossível.** |
| **RDD** | Requer uma regra de atribuição com limiar. Nenhuma variável da base é uma running variable com corte de política. **Impossível.** |
| **IV** | Requer instrumento correlacionado ao tratamento e excluído do desfecho. Nenhum candidato na base — todas as 31 colunas são atributos do curso ou desfechos. **Impossível.** |
| **Efeitos fixos de IES** | **Parcialmente viável** (598 estratos, §10.1) — absorve confundimento institucional. Mas **não** absorve composição de alunos, que é o confundidor dominante. Reduz o viés; não identifica. |
| **PSM / IPW** | Propensity score sobre as covariáveis disponíveis não fecha a porta dos não observados. Com overlap violado (§10.1), pesos explodem. Daria uma falsa aparência de rigor — **desaconselho ativamente**. |

### 10.5 Conclusão sobre inferência causal

> **Declaração explícita, conforme solicitado: esta base NÃO permite inferência causal defensável para nenhum dos tratamentos considerados.**

As razões são estruturais e não contornáveis por técnica estatística:

1. **Uma única coorte** → nenhuma variação temporal em tratamento.
2. **Tratamentos medidos em 2024** → posteriores ao desfecho; alguns são pós-tratamento/colisores.
3. **Zero covariáveis de aluno** → o confundidor dominante (composição) é integralmente invisível.
4. **Dados agregados** → falácia ecológica em qualquer interpretação individual.
5. **Overlap violado** para o tratamento mais interessante.
6. **SUTVA violada** por equilíbrio geral no mercado de ensino superior.

**Recomendação para a extensão metodológica (Opção 1):** não adotar inferência causal como extensão. O produto honesto seria um capítulo demonstrando **por que** a identificação falha — o que tem valor pedagógico real, mas não é uma análise causal, e não entrega o que a extensão promete. Se você quiser preservar algo desse esforço, inclua-o como uma seção curta de "Limitações causais" dentro do projeto principal, ancorada nos números de §10.1 (74,82% de concentração, 1 curso EAD na área 05, 598 estratos). Isso fortalece o projeto sem prometer o que os dados não sustentam.

---

## 11. Viabilidade de Quantum Machine Learning

### 11.1 Existe uma pergunta científica real?

**Sim — desde que seja formulada com precisão e modéstia.**

A pergunta **inválida** (e a mais comum na literatura de QML aplicada): *"QML supera ML clássico na previsão de evasão?"* — a resposta é conhecida (não), o experimento não seria informativo, e a comparação seria artificial.

A pergunta **válida**:

> **Em um problema tabular real, de baixa dimensionalidade, com classes fortemente sobrepostas e estrutura de agrupamento hierárquica, um kernel quântico (fidelidade de estados) induz uma geometria de similaridade materialmente diferente de um kernel RBF clássico ajustado — e essa diferença se traduz em alguma diferença de desempenho, sob orçamento computacional e protocolo de validação idênticos?**

Isto é uma pergunta de **caracterização de kernel**, não de vantagem quântica. É respondível, o resultado é informativo em qualquer direção (inclusive nulo), e é honesta.

Formulação alternativa, ainda mais defensável: **um estudo de correspondência de kernels** — medir a discrepância entre a matriz de Gram quântica e a RBF (alinhamento kernel-alvo, KTA), e verificar se a diferença de desempenho é explicada pela diferença de alinhamento. Isso produz um resultado interpretável **mesmo quando o desempenho é idêntico**, que é o desfecho mais provável.

### 11.2 Como gerar a amostra

Quantum kernels são O(n²) em avaliações de circuito. 28.143 amostras seriam ~400 milhões de avaliações — inviável. Subamostragem é obrigatória, e **é aí que a comparação normalmente se torna artificial**. Protocolo para evitar isso:

1. **Tarefa:** classificação binária `1[TDA(2024) ≥ 75]`. **[FATO]** prevalência 21,8%.
2. **Amostra:** **1.000–2.000 cursos**, por **amostragem estratificada agrupada**: sorteie **IES** (não cursos), preservando a estrutura de agrupamento, estratificando por categoria administrativa e área CINE. Sortear cursos diretamente quebraria a estrutura de dependência e produziria um problema mais fácil que o real.
3. **Balanceamento:** manter a prevalência natural de 21,8%. Balancear artificialmente para 50/50 é uma das formas mais comuns de tornar a comparação artificial.
4. **Validação:** o **mesmo** `GroupKFold` por `CO_IES` de §9.7. Sem exceção para o experimento quântico.
5. **Repetir com 10 sementes** de subamostragem e reportar a distribuição. Com n ≈ 1.000 e diferenças de AUC da ordem de 0,01–0,02, **uma única partição não distingue sinal de ruído** — e esse é o erro que mata a maioria desses experimentos.

### 11.3 Como reduzir a dimensionalidade

Alvo: **4 a 8 features** (4–8 qubits, simulável em notebook).

Recomendo **seleção**, não PCA, e a razão importa: features selecionadas mantêm significado substantivo, então uma diferença de kernel pode ser interpretada; componentes principais não permitem interpretação alguma.

Conjunto sugerido (6 features, todas do cutoff τ ≤ 2, respeitando §9.5):

1. `TADA(0)` — hazard do 1º ano
2. `TADA(1)` — hazard do 2º ano
3. `TADA(2) − TADA(1)` — aceleração
4. `TAP(2)` — sobrevivência em τ=2
5. `log(QT_INGRESSANTE)` — porte
6. `TP_MODALIDADE_ENSINO` — binária

Padronize e reescale para [0, π] (encoding de ângulo). **O escalador deve ser ajustado dentro do fold.** Reporte também uma variante com PCA(6) como robustez.

### 11.4 Como evitar uma comparação artificial

Este é o ponto onde a maioria dos estudos de QML aplicado falha. Regras não negociáveis:

| Regra | Razão |
|---|---|
| **Orçamento de tuning idêntico** | Se o RBF recebe busca em grade sobre (C, γ) com 50 configurações, o quantum kernel recebe 50 configurações sobre suas próprias (profundidade, entanglement, escala de encoding, C). Comparar um RBF tunado com um quantum kernel default — ou o inverso — é o viés mais comum da área. |
| **Mesma amostra, mesmos folds, mesmas seeds** | Sem exceções. |
| **Mesmo pré-processamento** | Ambos recebem exatamente a mesma matriz de features. |
| **Baselines clássicos além do RBF** | Kernel linear, SVM polinomial, LightGBM, regressão logística. Se um kernel **linear** iguala ambos, a conclusão é que o problema é aproximadamente linearmente separável nessas 6 dimensões, e a comparação de kernels é vazia — **isto é um resultado, e precisa ser verificado antes de qualquer outra coisa.** |
| **Testes estatísticos** | Teste de Wilcoxon pareado entre folds e sementes; ICs bootstrap. Nunca comparar dois números isolados. |
| **Pré-registrar a hipótese** | Escreva a hipótese e o critério de decisão **antes** de rodar. Impede reinterpretação post hoc de um resultado nulo. |
| **Simulador sem ruído como principal** | Hardware real ou modelos de ruído introduzem uma variável confundidora não interpretável. Ruído como sensibilidade opcional, jamais como experimento principal. |

### 11.5 Objetivo do experimento

**Objetivo declarado:** avaliar se a métrica de similaridade induzida por um feature map quântico difere mensuravelmente de um RBF clássico, em uma representação reduzida de um problema real de evasão, sob protocolo idêntico — e caracterizar a diferença via alinhamento kernel-alvo, não apenas via acurácia.

**O que NÃO é objetivo:** demonstrar vantagem quântica; melhorar a previsão de evasão; justificar computação quântica para política educacional.

**Desfecho esperado [HIPÓTESE]:** desempenho estatisticamente indistinguível. **Isto é um resultado válido e publicável**, e o enquadramento acima o torna informativo em vez de decepcionante.

### 11.6 Limitações a declarar

1. Simulação clássica de 4–8 qubits — não demonstra nada sobre hardware real nem sobre escalabilidade.
2. n ≈ 1.000–2.000 por restrição computacional, não por desenho estatístico.
3. Redução a 6 features descarta a maior parte da informação disponível; o classificador quântico opera num problema deliberadamente empobrecido.
4. Um resultado nulo não generaliza para outros feature maps, outros datasets ou outras tarefas.
5. Nenhuma vantagem quântica é reivindicada, testada ou implicada.
6. O experimento não melhora nenhuma conclusão substantiva sobre evasão — é estritamente metodológico.

### 11.7 Recomendação sobre QML

**Recomendo fazer — como apêndice estritamente delimitado, e recomendo QML em vez de inferência causal.**

Justificativa comparativa direta:

| | Opção 1 — Inferência causal | Opção 2 — QML |
|---|---|---|
| Viabilidade | **Nula** — identificação impossível (§10.5) | Alta — escopo controlado |
| Risco de descaracterizar o projeto | Alto (redesenho completo) | Baixo (apêndice de ~10% do esforço) |
| Risco de conclusão inválida | **Muito alto** — tentação de rotular associação como efeito | Baixo, com o protocolo de §11.4 |
| Aderência a Big Data Analytics | Tangencial | Complementar (métodos de kernel) |
| Alinhamento com sua pesquisa de mestrado | Nenhum | **Direto** |

**Condições inegociáveis:**

- Máximo **10–15%** do esforço e da extensão do relatório.
- Seção intitulada "Experimento metodológico complementar", **após** todas as conclusões substantivas.
- Nenhuma conclusão sobre evasão depende dela.
- As limitações de §11.6 aparecem **junto** dos resultados, não em nota de rodapé.
- Se o cronograma apertar, **esta é a primeira coisa a cortar** — e o projeto principal permanece completo sem ela.

---

## 12. Necessidade dos dados de 2024

### 12.1 O que foi inspecionado

Conforme instruído, **não** li os 432 MB integralmente. Inspecionei: cabeçalho, dicionário oficial (`ANEXO I`), e agregações via DuckDB com projeção de colunas.

**[FATO]** Inventário de `data/raw/2024/`:

| Arquivo | Tamanho |
|---|---|
| `MICRODADOS_CADASTRO_CURSOS_2024.CSV` | **432 MB** |
| `MICRODADOS_ED_SUP_IES_2024.CSV` | 977 KB |
| `Anexos/ANEXO I - Dicionário de Dados/dicionário_dados_educação_superior.xlsx` | 54 KB |
| `Anexos/ANEXO II - ...` (4 PDFs de questionários) | ~1,9 MB |
| `leia-me/` (2 PDFs) | ~934 KB |
| `md5_microdados_ed_superior_2024.txt` | 139 B |

**[FATO] Nota técnica:** o CSV é **latin-1**, não UTF-8, e delimitado por `;`. Leitura como UTF-8 falha.

### 12.2 Por que o arquivo é tão grande — e por que isso importa

**[FATO]** 720.349 linhas de dados para apenas **46.150 cursos distintos**. A causa é `TP_DIMENSAO` [DICIONÁRIO]: *"Tipo de dimensão geográfica dos cursos presenciais e a distância"*.

| `TP_DIMENSAO` | Significado | Linhas | Cursos distintos |
|---|---|---|---|
| 1 | Presencial ofertado no Brasil | 34.824 | 34.824 |
| **2** | **EAD ofertado no Brasil (replicado por município de oferta)** | **673.756** | **11.255** |
| 3 | EAD com dimensão só nível Brasil | 11.319 | 11.319 |
| 4 | EAD ofertado por IES brasileiras no exterior | 450 | 450 |

**93,5% do arquivo é redundância geográfica de cursos EAD.** Para um join em nível de curso, apenas `TP_DIMENSAO ∈ {1, 3}` é necessário — **46.143 linhas**.

### 12.3 Existem features relevantes ausentes na base de trajetória?

**[FATO] Sim, muitas, e são substantivas.** Cruzei os 28.143 cursos da trajetória contra o Censo 2024 (`TP_DIMENSAO ∈ {1,3}`): **22.864 casam (81,24%)**, e nesses a cobertura das novas variáveis é **100%** (22.864/22.864 não-nulos em todas as testadas).

Famílias de variáveis **ausentes** da base de trajetória:

| Família | Exemplos | Relevância |
|---|---|---|
| **Seletividade** | `QT_VG_TOTAL`, `QT_INSCRITO_TOTAL` (razão candidato/vaga) | **Altíssima** — é o melhor proxy disponível para o confundidor dominante de §10 |
| **Composição demográfica** | `QT_ING_FEM`, `QT_ING_0_17..60_MAIS`, `QT_ING_PRETA/PARDA/INDIGENA` | Alta — mitiga parcialmente a falácia ecológica |
| **Financiamento** | `QT_ING_FIES`, `QT_ING_PROUNII/PROUNIP`, `IN_GRATUITO` | Alta — determinante conhecido de evasão |
| **Ação afirmativa** | `QT_ING_RESERVA_VAGA`, `QT_ING_RVPPI`, `QT_ING_PROCESCPUBLICA` | Alta |
| **Turno** | `QT_ING_DIURNO`, `QT_ING_NOTURNO` | **Alta** — noturno é preditor clássico e **não existe** na trajetória |
| **Situação de vínculo** | `QT_SIT_TRANCADA`, `QT_SIT_DESVINCULADO`, `QT_SIT_TRANSFERIDO` | Alta — `TRANSFERIDO` toca diretamente a limitação de §6.4 |
| **Apoio institucional** | `QT_APOIO_SOCIAL`, `QT_ATIV_EXTRACURRICULAR`, `QT_MOB_ACADEMICA` | Média |
| **Granularidade CINE** | `CO_CINE_AREA_ESPECIFICA`, `CO_CINE_AREA_DETALHADA` | Média |
| **Contexto institucional** (arquivo IES) | `QT_DOC_EX_DOUT`, `QT_DOC_EX_INT_DE`, `QT_TEC_TOTAL`, `NO_MESORREGIAO_IES` | Média-alta — qualificação e regime docente |

### 12.4 A objeção decisiva

**Todas essas variáveis são medidas em 2024. A coorte ingressou em 2015.**

`QT_ING_FIES` no Censo 2024 descreve os ingressantes **de 2024**, não os de 2015. Usá-la para prever a evasão da coorte 2015 é:

- **anacronismo** — a variável é posterior ao desfecho;
- **erro de unidade** — descreve uma coorte diferente de alunos;
- e, em §9.5, está na **lista de bloqueio** por essas razões.

**O arquivo que resolveria isso — `MICRODADOS_CADASTRO_CURSOS_2015.CSV` — não está no disco.** Ele é o que permitiria caracterizar a coorte 2015 na entrada (seletividade, turno, financiamento, demografia **em 2015**) e seria uma adição genuinamente transformadora ao projeto: features contemporâneas ao cutoff, sem vazamento temporal.

**Recomendação de aquisição:** baixe o Censo 2015 (cadastro de cursos) do portal do Inep. Após o mesmo filtro `TP_DIMENSAO ∈ {1,3}` e projeção de colunas, ele ocupará **poucos MB**. Custo de disco desprezível, ganho metodológico alto. **É a maior alavanca disponível para melhorar o projeto.**

### 12.5 Usos legítimos dos dados de 2024

Mesmo com a objeção acima, o arquivo tem três usos válidos:

1. **Validação de metadados** — já realizada nesta auditoria: concordância 100% em modalidade, categoria e grau (§4.5), o que **prova** a natureza pós-hoc das covariáveis. Este achado sozinho justifica ter mantido o arquivo até aqui.
2. **Quantificar a seleção por sobrevivência** — **[FATO]** 5.279 cursos da trajetória (18,76%) **não** aparecem no Censo 2024. Isso mede diretamente a extinção de cursos, e permite testar se cursos extintos tinham `TDA` mais alta em τ=2 — uma análise de sensibilidade direta para a hipótese de §7.D.
3. **Contexto institucional plausivelmente estável** — mesorregião, qualificação docente. Como *robustez*, nunca no modelo principal.

### 12.6 Recomendação

> ### **MANTER TEMPORARIAMENTE** — e reduzir imediatamente.

**Justificativa:** o arquivo tem valor real (§12.5), mas 432 MB são **500× maiores** do que o necessário para extrair esse valor.

**Ação recomendada (ainda não executada — requer sua autorização):**

1. Gerar `data/interim/censo2024_cursos_slim.parquet` com `TP_DIMENSAO ∈ {1,3}` e ~34 colunas relevantes.
   **[FATO] Já testei essa extração nesta auditoria: 46.143 linhas, 0,84 MB em Parquet+ZSTD.** Redução de **432 MB → 0,84 MB (99,8%)**, sem perda de nenhuma informação em nível de curso.
2. Verificar o MD5 contra `md5_microdados_ed_superior_2024.txt` e registrar o hash no repositório para reprodutibilidade.
3. **Após** os passos 1–2 confirmados, o CSV de 432 MB **pode ser apagado** — é redownloadable do portal do Inep e o `.gitignore` já exclui `data/raw/`.

**Manter definitivamente (custo trivial, valor alto):** `MICRODADOS_ED_SUP_IES_2024.CSV` (977 KB), o dicionário `ANEXO I` (54 KB), o `md5`, e o `leia-me/`. O dicionário é documentação essencial.

**Sobre `Anexos/ANEXO II`** (4 PDFs de questionários, ~1,9 MB): baixo valor para este projeto — são instrumentos de coleta. **PODE APAGAR** se o espaço apertar, mas 1,9 MB não justifica o risco.

**Nenhum arquivo foi apagado nesta auditoria.**

---

## 13. Principais riscos metodológicos

Ordenados por severidade.

| # | Risco | Severidade | Evidência | Mitigação |
|---|---|---|---|---|
| **R1** | **Falácia ecológica** — dados de curso interpretados como sobre alunos | **Crítica** | Unidade = curso × ano (§2.1) | Linguagem disciplinada em todo o texto: "cursos com maior desistência", nunca "alunos que desistem". Revisar cada afirmação do relatório final. |
| **R2** | **Coorte única lida como série temporal** — "a evasão cresceu entre 2015 e 2024" | **Crítica** | **[FATO]** 1 coorte (§1.2) | Renomear o eixo para τ (ano da trajetória). Declarar na introdução e nas legendas. É o erro mais fácil de cometer e o mais fatal. |
| **R3** | **Vazamento algébrico** — `TAP+TCA+TDA=100` | **Crítica** | **[FATO]** exato em 281.430/281.430 (§4.3) | No máximo 2 dos 3 no modelo. Asserção automática. |
| **R4** | **Vazamento por agrupamento institucional** | **Crítica** | **[FATO]** ICC ≈ 0,65 (§8.4) | `GroupKFold` por `CO_IES`. Reportar contra `KFold` aleatório como resultado. |
| **R5** | **Aninhamento mecânico no alvo** — `TDA(9) ⊇ TDA(2)` | **Alta** | **[FATO]** 64,2% já acumulado em τ=2; `r`=0,744 (§9.2) | Alvos T2/T3 (§9.3). Baseline B2 obrigatório. Reportar Δ, nunca R² absoluto. |
| **R6** | **Covariáveis pós-desfecho** (snapshot 2024) | **Alta** | **[FATO]** concordância 100% com Censo 2024 (§4.5) | Estratificar features por risco. Rodar com e sem as de alto risco. |
| **R7** | **Seleção por sobrevivência do curso** | **Alta** | **[HIPÓTESE]**; **[FATO]** 18,76% dos cursos ausentes em 2024 (§12.5) | Declarar como limitação. Testar via §12.5.2. Evasão real provavelmente **maior** que a medida. |
| **R8** | **Deriva causal na linguagem** | **Alta** | §10 | Proibir "efeito", "impacto", "causa", "leva a". Revisão terminológica final dedicada. |
| **R9** | **Ruído em cursos pequenos** | **Média** | **[FATO]** 1.221 cursos (4,3%) com <10 ingressantes; `TDA`=100 tem mediana de 11 ingressantes (§8.1) | Ponderar por `QT_INGRESSANTE`; sensibilidade com corte em 20; nunca ranquear cursos pequenos sem IC. |
| **R10** | **Média ponderada vs. simples** | **Média** | **[FATO]** EAD: 4,0% dos cursos, 24,1% dos ingressantes (§8.2) | Reportar ambas, sempre, lado a lado. |
| **R11** | **EAD sem geografia contamina análise regional** | **Média** | **[FATO]** 11.180 nulos estruturais (§3.2) | Categoria explícita "EAD/sem geografia". **Nunca imputar.** Nota em toda tabela regional. |
| **R12** | **Tipagem de códigos CINE** | **Média** | **[FATO]** `Char(2)` com zero à esquerda (§1.4) | Forçar `str` na ingestão; teste automatizado. |
| **R13** | **Confusão evasão de curso × de sistema** | **Média** | §6.4 | Declarar na definição do desfecho. |
| **R14** | **Rodapé do XLSX** | **Baixa** | **[FATO]** 1 linha (§1.1) | Filtro na ingestão + asserção de 281.430 linhas. |
| **R15** | **QML descaracterizar o projeto** | **Baixa** | §11.7 | Teto de 10–15%; apêndice; primeira coisa a cortar. |

---

## 14. Roadmap recomendado

Sequência em 8 etapas. Nenhuma foi executada — a auditoria é a etapa 0.

**Etapa 0 — Auditoria** ✅ concluída (este documento)

**Etapa 1 — Ingestão reprodutível**
`src/ingest_trajetoria.py`: XLSX → `data/interim/trajetoria_2015.parquet`. Cabeçalho na linha 9, remover o rodapé, forçar `str` nos códigos CINE. Asserções: 281.430 linhas · 28.143 `CO_CURSO` · chave `(CO_CURSO, NU_ANO_REFERENCIA)` única · nulos apenas nas 3 colunas geográficas.
**[FATO]** A conversão leva ~115 s via `openpyxl` em `read_only`, e o Parquet resultante tem **3,3 MB** (vs. 41 MB do XLSX). Converta uma vez; nunca releia o XLSX.

**Etapa 2 — Camada de qualidade**
`src/qualidade.py`: reimplementar as 14 verificações desta auditoria como testes automatizados — identidade contábil, `TAP+TCA+TDA=100`, monotonicidade, as cinco fórmulas de taxa, unicidade da chave, faixas. Todas devem passar. É a evidência do pilar "qualidade de dados".

**Etapa 3 — Construção das tabelas analíticas**
`traj_longo` (281.430 × curso-ano, com τ e acumulados) e `traj_largo` (28.143 × curso, pivotado, com T1/T2/T3). Fronteira de cutoff codificada explicitamente.

**Etapa 4 — Descriptive Analytics e visualização** (§8)
Os oito entregáveis de §8.3. Sempre ponderada + simples. **Cada gráfico com o τ correto no eixo, nunca "ano".**

**Etapa 5 — Análise longitudinal** (§9.1)
Curvas de estado, hazard bruto vs. condicional, clustering de trajetórias, modelo misto com intercepto aleatório por IES.

**Etapa 6 — Predictive Analytics** (§9.3–§9.10)
Escada B0→B4, depois RF e boosting. Alvos T1/T2/T3 + classificação. `GroupKFold` por IES vs. `KFold` aleatório lado a lado. SHAP com linguagem associativa. Checklist de §9.10 executado.

**Etapa 7 — Interpretação e limitações**
Síntese; seção de limitações ancorada em §6, §10.5 e §13; revisão terminológica final contra R8.

**Etapa 8 — Apêndice QML** (§11) — *opcional, apenas se houver folga de cronograma*

**Trilha paralela — Dados:**
(a) extrair o slim Parquet de 2024 e reduzir o CSV de 432 MB (§12.6);
(b) **baixar o Censo 2015 de cursos** — maior ganho marginal disponível (§12.4).

---

## 15. Recomendação final

### O que os dados são

Um painel **perfeitamente balanceado, sem duplicatas, sem valores impossíveis, e internamente consistente até a última casa decimal** — a identidade contábil e a identidade `TAP+TCA+TDA=100` fecham em **281.430 de 281.430 linhas**, e as cinco fórmulas de taxa foram recuperadas com acerto de 100%. Qualidade de dados excepcional. **[FATO]**

### O que os dados não são

**Não são um painel multi-coorte.** **[FATO]** Há **uma única coorte** (ingresso 2015), acompanhada por 10 anos. Este fato reescreve três das seis tarefas propostas:

- **Não há tendência histórica a estudar** — apenas o envelhecimento de uma coorte;
- **Não há validação preditiva temporal possível** — apenas generalização para instituições não vistas;
- **Não há inferência causal identificável** — sem variação temporal no tratamento, sem período pré, sem covariáveis de aluno.

### Recomendações, em ordem de importância

1. **Adote a pergunta principal de §7.A** e reformule o desenho preditivo como **antecipação precoce dentro de coorte com validação por generalização institucional** — não como forecasting temporal.

2. **Adote os alvos T2 e T3** (§9.3) ao lado de T1. **[FATO]** `TDA(2)` já contém 64,2% de `TDA(9)`; sem T2/T3 o exercício preditivo é largamente tautológico. T3 — *"dos que ainda estavam matriculados no fim do 2º ano, ~41% ainda viriam a desistir"* — é o resultado mais defensável e mais comunicável da base inteira.

3. **`GroupKFold` por `CO_IES`, sem exceção**, e reporte-o contra `KFold` aleatório. **[FATO]** ICC ≈ 0,65. Essa comparação é, ela própria, um resultado do projeto.

4. **Não faça inferência causal.** §10 é uma avaliação honesta e a resposta é negativa para todos os tratamentos considerados. A diferença EAD-presencial é composicional: **[FATO]** 74,82% dos ingressantes EAD estão em 10 grupos, 83,18% em privadas com fins lucrativos, e há **1 curso EAD** na área CINE 05. O que é defensável é a comparação **dentro de IES × rótulo CINE** (598 estratos), rotulada como **associação ajustada**.

5. **Para a extensão metodológica, escolha QML (Opção 2), não inferência causal (Opção 1).** Não por preferência, mas porque a Opção 1 **não é executável** com estes dados, e a Opção 2 é executável, delimitável em 10–15% do esforço, e alinhada à sua pesquisa. Formule-a como caracterização de kernel, não como busca de vantagem quântica, e siga o protocolo anti-artificialidade de §11.4. Se o cronograma apertar, corte-a — o projeto principal fica completo sem ela.

6. **Dados de 2024: MANTER TEMPORARIAMENTE.** Extraia o slim Parquet (**[FATO]** 432 MB → **0,84 MB**, testado nesta auditoria), verifique o MD5, e só então apague o CSV. E **baixe o Censo 2015 de cursos** — é a maior alavanca isolada disponível para melhorar este projeto, porque forneceria features contemporâneas ao cutoff em vez de anacrônicas.

7. **Discipline a linguagem.** Riscos R1, R2 e R8 são os que arruinariam o trabalho, e nenhum deles é técnico — são de redação. Reserve uma revisão final dedicada exclusivamente a caçar "efeito", "impacto", "causa", "a evasão aumentou" e afirmações sobre alunos.

### Veredito

**O projeto é viável, aderente a Big Data Analytics em todos os sete pilares exigidos, e assenta sobre dados de qualidade excepcional.** As restrições reais são de **inferência**, não de dados: coorte única, unidade agregada, covariáveis pós-hoc. Reconhecidas explicitamente e incorporadas ao desenho, elas não enfraquecem o trabalho — **tratá-las com rigor é o que o distingue.**

---

## Anexo — Arquivos criados nesta auditoria

**Nenhum arquivo do projeto foi modificado ou apagado. Nenhum commit foi feito. Nenhum modelo foi implementado.**

**Único arquivo criado no projeto:**

- `docs/auditoria_metodologica.md` (este documento)

**Arquivos temporários, todos fora do projeto**, em
`C:\Users\ariel\AppData\Local\Temp\claude\c--GitHub-datascience-projetos-big-data-evasao-ensino-superior\6821a647-f694-4d6f-a7fa-010e5bb7b699\scratchpad\`:

| Arquivo | Finalidade |
|---|---|
| `read_docx.py` | extração do texto do dicionário oficial (.docx via zipfile) |
| `xlsx_to_parquet.py` | conversão streaming XLSX → Parquet |
| `trajetoria.parquet` (3,3 MB) | cópia de trabalho da base |
| `convert.log` | log da conversão |
| `dic2024.py`, `dic2024b.py`, `dic_full.py`, `dic_cursos.txt` | dicionário do Censo 2024 |
| `cursos2024.py` | perfil de `TP_DIMENSAO` do CSV de 432 MB |
| `audit1.py` … `audit8.py` | as 14 verificações desta auditoria |
| `join2024.py` | teste de cobertura do join com o Censo 2024 |
| `censo2024_cursos_slim_TESTE.parquet` (0,84 MB) | **prova de conceito** da redução de §12.6 — descartável |

Podem ser apagados a qualquer momento. Recomendo promover `xlsx_to_parquet.py` e os scripts de auditoria a `src/` (etapas 1 e 2 do roadmap), já que constituem a evidência reprodutível dos pilares de aquisição e qualidade de dados.
