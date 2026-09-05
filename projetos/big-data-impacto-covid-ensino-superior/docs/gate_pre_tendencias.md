# GATE C3 — Teste de pré-tendências com tratamento predeterminado

**Projeto:** Impacto da COVID-19 sobre a desistência no ensino superior
**Data:** 2026-09-04
**Escopo:** execução do **único** gate causal mínimo definido em [auditoria_causal_covid.md](auditoria_causal_covid.md) §20.
**Status:** **Nenhum DiD final foi estimado. Nenhum matching foi feito. Nenhuma estimativa de efeito causal é reportada.**

Convenção: **[FATO]** verificado programaticamente · **[DICIONÁRIO]** documentação oficial · **[HIPÓTESE]** interpretação.

---

## 1. O que este documento resolve

A auditoria anterior classificou o GATE C3 (tendências paralelas) como **FALHA**, mas registrou uma ressalva explícita: o teste havia usado a modalidade do **snapshot de 2024**, e portanto não era conclusivo. Este documento fecha essa ressalva, construindo o tratamento a partir dos Censos da Educação Superior **2015–2019** e refazendo o teste.

---

## 2. Aquisição dos Censos 2015–2019

**Fonte oficial única:** `https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_{ano}.zip`

**[FATO]** Todos os cinco arquivos baixados, com **MD5 conferido contra o `md5_microdados_ed_superior_{ano}.txt` publicado dentro do próprio ZIP** — cinco de cinco conferem.

| Ano | ZIP | CSV de cursos (descomprimido) | Colunas | Linhas CSV | Parquet slim | MD5 |
|---|---|---|---|---|---|---|
| 2015 | 8,40 MB | 47,33 MB | 200 | 81.156 | 0,887 MB | ✅ |
| 2016 | 9,10 MB | 53,90 MB | 200 | 92.866 | 0,905 MB | ✅ |
| 2017 | 10,67 MB | 68,93 MB | 200 | 119.798 | 0,926 MB | ✅ |
| 2018 | 13,22 MB | 104,04 MB | 200 | 182.892 | 0,964 MB | ✅ |
| 2019 | 16,91 MB | 142,94 MB | 200 | 253.139 | 1,004 MB | ✅ |
| **Total** | **58,3 MB** | **417,1 MB** | — | 729.851 | **4,69 MB** | — |

**Política de disco executada** ([src/baixa_censos_pre_covid.py](../src/baixa_censos_pre_covid.py)), um ano por vez:

```
download ZIP → conferir MD5 publicado → extrair SOMENTE o cadastro de cursos
  → documentar schema → filtrar TP_DIMENSAO ∈ {1,3} → projetar 44 colunas
  → gravar Parquet slim → APAGAR o CSV e o ZIP
```

**[FATO]** Pico transitório de disco: 159,9 MB (ano de 2019). Residual permanente: **4,69 MB**. Redução de 417,1 MB → 4,69 MB (**98,9%**). Nenhum CSV ou ZIP de Censo permanece em disco.

Nenhum ano ≥ 2020 foi baixado. O script contém a asserção `assert ano <= 2019`.

---

## 3. Schema por ano e validação de `CO_CURSO` como chave

Schemas documentados **antes** de qualquer processamento, em `data/interim/censo_schema_{ano}.json`.

### 3.1 Schemas

**[FATO]** Os cinco anos têm **200 colunas, com nomes e ordem idênticos**. Nenhuma das 44 colunas pedidas está ausente em nenhum ano. A taxonomia **CINE** já está presente em 2015 — o Inep a harmonizou retroativamente, de modo que **não** é necessário converter de OCDE para CINE.

Codificação `latin-1`, delimitador `;`. Códigos CINE vêm com aspas duplicadas em alguns anos (`"""0721E01"""`) e são normalizados como texto, preservando o zero à esquerda.

### 3.2 `TP_DIMENSAO` e a explosão de linhas

**[DICIONÁRIO]** `TP_DIMENSAO`: 1 = presencial no Brasil · 2 = EAD replicado por município de oferta · 3 = EAD com dimensão apenas Brasil · 4 = EAD no exterior.

**[FATO]**

| Ano | dim 1 | dim 2 (replicação) | dim 3 | dim 4 | Após filtro {1,3} |
|---|---|---|---|---|---|
| 2015 | 32.397 | 47.283 | 1.476 | — | **33.873** |
| 2016 | 33.031 | 58.171 | 1.664 | — | **34.695** |
| 2017 | 33.581 | 84.085 | 2.112 | 20 | **35.693** |
| 2018 | 35.076 | 144.549 | 3.180 | 87 | **38.256** |
| 2019 | 36.178 | 212.197 | 4.531 | 233 | **40.709** |

A dimensão 2 é replicação geográfica pura e chega a 83,8% do arquivo em 2019. Removê-la é obrigatório e não perde nenhum curso.

### 3.3 `CO_CURSO` serve como chave de ligação?

**[FATO] Sim.**

| Verificação | Resultado |
|---|---|
| `CO_CURSO` único após o filtro `TP_DIMENSAO ∈ {1,3}` | **sim, nos 5 anos** (linhas = cursos distintos) |
| `CO_CURSO` determina `CO_IES` dentro de cada ano | **sim, nos 5 anos** |
| Chave `(CO_CURSO, NU_ANO_CENSO)` única na tabela longitudinal | **sim** — 183.226 linhas, 46.098 cursos |
| Cobertura do painel de trajetórias (43.861 cursos) pelo **Censo 2019** | **39.289 (89,58%)** |
| Cobertura pelo **Censo 2015** | 29.252 (66,69%) |
| Cobertura por **qualquer** Censo 2015–2019 | **40.837 (93,11%)** |
| `CO_IES` concorda entre painel e Censo 2019, nos casados | 98,06% |
| `CO_IES` concorda entre painel e Censo 2015, nos casados | 97,61% |

A discordância de ~2% em `CO_IES` é esperada e informativa: o painel de trajetórias carrega a IES **de 2024**, e houve fusões/incorporações. Por isso a estratificação passa a usar `CO_IES_2019`, do Censo, e não a do painel.

---

## 4. Tabela longitudinal pré-COVID

**Arquivo:** `data/processed/modalidade_pre_covid_2015_2019.parquet` — 1,87 MB.

**[FATO]** 183.226 linhas · 46.098 cursos · 2.901 IES · anos 2015–2019 · chave `(CO_CURSO, NU_ANO_CENSO)` única.

Colunas: `CO_CURSO`, `CO_IES`, `NU_ANO_CENSO`, `TP_MODALIDADE_ENSINO`, `TP_CATEGORIA_ADMINISTRATIVA`, `TP_ORGANIZACAO_ACADEMICA`, `TP_GRAU_ACADEMICO`, `CO_CINE_ROTULO`, `CO_CINE_AREA_GERAL`, `CO_REGIAO`, `CO_UF`, `QT_ING`, `QT_VG_TOTAL`, `QT_INSCRITO_TOTAL`, `QT_ING_NOTURNO`, `QT_ING_FIES`, `QT_ING_PROUNII`, `QT_ING_PROUNIP`.

Nenhuma informação de 2020 ou posterior entra na definição do tratamento.

---

## 5. Auditoria de estabilidade da modalidade — o achado central

### 5.1 Classificação

**[FATO]** Entre os 46.098 cursos da tabela longitudinal:

| Classe | Cursos | Definição |
|---|---|---|
| **presencial estável** | **33.795** | modalidade 1 em todos os anos observados, ≥ 2 anos, presente em 2019 |
| **EAD estável** | **3.128** | modalidade 2 em todos os anos observados, ≥ 2 anos, presente em 2019 |
| **mudou de modalidade** | **0** | — |
| sem informação suficiente | 9.175 | observado em 1 só ano, ou ausente em 2019 |

Distribuição de anos observados **[FATO]**: 1 ano → 5.368 cursos · 2 → 5.104 · 3 → 3.628 · 4 → 3.224 · **5 → 28.774**.

### 5.2 Zero mudanças de modalidade — e o que isso significa

> **[FATO] Nenhum dos 40.730 cursos observados em dois ou mais anos entre 2015 e 2019 mudou de `TP_MODALIDADE_ENSINO`. Zero.**

E, comparando com o painel de trajetórias: **[FATO]** dos 39.289 cursos casados, a modalidade do snapshot de 2024 e a de 2019 concordam em **39.289 (100,000%)** — a tabela cruzada não tem nenhuma célula fora da diagonal.

**[HIPÓTESE, com evidência de apoio forte]** `TP_MODALIDADE_ENSINO` é um atributo **imutável** do identificador `CO_CURSO`. Quando uma IES passa a ofertar a distância um curso que ofertava presencialmente, o Inep registra um **curso novo, com novo código**, e não uma mudança de modalidade no código existente.

Evidência **[FATO]**: dos 3.209 cursos EAD novos em 2019 (ausentes do Censo 2015), **1.439 (44,8%)** pertencem a uma IES que já tinha, em 2015, um curso **presencial** com o mesmo `CO_CINE_ROTULO`. A migração institucional para EAD existe e é grande — mas aparece como entrada de cursos novos, nunca como troca de modalidade.

### 5.3 As duas consequências, e elas vão em direções opostas

**Consequência 1 — a ressalva da auditoria anterior está fechada, e no sentido desfavorável.**

O teste de pré-tendências anterior **não estava contaminado** por reclassificação pós-2020. Não havia nada a corrigir na variável de tratamento. A falha de pré-tendências documentada antes não era artefato: era o dado.

**Consequência 2 — a restrição C ("modalidade estável") é vazia, mas a exclusão por cobertura não é.**

Não há cursos "instáveis" a remover. O que a restrição faz de fato é **excluir os cursos ausentes dos Censos pré-2020** — isto é, os criados a partir de 2020. E isso importa: **[FATO]** o braço EAD do painel cai de 5.246 para 2.530 cursos na coorte 2020, porque 2.716 cursos EAD dessa coorte só existem a partir de 2020.

### 5.4 As demais covariáveis, ao contrário, **mudam**

**[FATO]** Entre os 40.730 cursos com ≥ 2 anos observados:

| Covariável | Cursos que mudaram entre 2015 e 2019 | % |
|---|---|---|
| `TP_MODALIDADE_ENSINO` | **0** | 0,0 |
| `CO_CINE_AREA_GERAL` | **0** | 0,0 |
| `TP_GRAU_ACADEMICO` | 16 | 0,04 |
| `CO_IES` | 249 | 0,6 |
| **`TP_CATEGORIA_ADMINISTRATIVA`** | **2.993** | **7,3** |
| **`TP_ORGANIZACAO_ACADEMICA`** | **3.245** | **8,0** |

Ou seja: o snapshot de 2024 **estava certo sobre modalidade e área, e errado sobre categoria administrativa e organização acadêmica em 7–8% dos cursos.** O ganho real desta aquisição não foi o tratamento — foi a **estratificação**, que agora usa valores genuinamente pré-choque. Todas as especificações abaixo usam `CATEGORIA_2019`, `ORGANIZACAO_2019`, `CINE_AREA_2019` e `CO_IES_2019`.

---

## 6. Painel causal integrado

**Arquivo:** `data/processed/painel_causal_pre_covid.parquet` — 29,12 MB.

**[FATO]** O original `trajetorias_2015_2020.parquet` foi **preservado, sem escrita** (MD5 `84092e0cf73bc0eda9b34120fa348e31`). O novo painel é um `LEFT JOIN` do original com o tratamento, mantendo as 1.403.065 linhas e todas as colunas originais, e acrescentando `MODALIDADE_2019`, `MODALIDADE_PRIMEIRO_ANO`, `CLASSE_TRATAMENTO`, `TRATAMENTO_ESTAVEL`, `N_ANOS_CENSO_PRE`, `CO_IES_2019`, `CATEGORIA_2019`, `ORGANIZACAO_2019`, `GRAU_2019`, `CINE_ROTULO_2019`, `CINE_AREA_2019`, `QT_ING_2019`, `QT_VG_2019`, `QT_INSC_2019`.

**[FATO]** Classificação dos 43.861 cursos do painel:

| Classe | Cursos |
|---|---|
| presencial estável | **32.651** |
| EAD estável | **3.047** |
| sem informação suficiente (1 só ano de Censo) | 5.139 |
| ausente dos Censos pré-COVID (criado em 2020+) | 3.024 |
| **cobertura do tratamento** | **40.837 (93,11%)** |

A população do teste é a de **35.698 cursos com tratamento pré-COVID estável** — 1.147.326 linhas do painel.

---

## 7. Overlap sob o tratamento predeterminado

### 7.1 Composição por coorte

**[FATO]** Somente cursos com tratamento pré-COVID estável:

| Coorte | Cursos pres. | Cursos EAD | Ingr. pres. | Ingr. EAD | % ingr. EAD | IES EAD | IES com ambas |
|---|---|---|---|---|---|---|---|
| 2015 | 25.913 | 1.093 | 2.265.536 | 727.729 | 24,31 | 144 | 139 |
| 2016 | 27.240 | 1.279 | 2.177.310 | 865.401 | 28,44 | 156 | 151 |
| 2017 | 28.489 | 1.865 | 2.201.260 | 1.098.711 | 33,29 | 240 | 234 |
| 2018 | 29.685 | 2.676 | 2.102.702 | 1.398.195 | 39,94 | 287 | 280 |
| 2019 | 28.214 | 2.590 | 1.955.171 | 1.491.823 | 43,28 | 270 | 261 |
| 2020 | 26.198 | 2.530 | 1.645.859 | 1.675.262 | 50,44 | 273 | 258 |

### 7.2 O overlap melhorou?

**Modestamente, e apenas na dimensão de composição.**

| Métrica | Antes (snapshot 2024, todos os cursos) | Depois (tratamento pré-COVID estável) |
|---|---|---|
| Cursos EAD, coorte 2019 | 3.944 | **2.590** |
| Cursos EAD, coorte 2020 | 5.246 | **2.530** |
| % cursos EAD novos desde 2015, coorte 2019 | 75,6% | **62,9%** |
| % cursos EAD novos desde 2015, coorte 2020 | 81,5% | **61,6%** |
| % ingressantes EAD em cursos novos, coorte 2020 | 43,5% | **31,2%** |
| N efetivo de IES do braço EAD, coorte 2019 | 16,0 | **14,6** |
| IES que concentram 50% dos ingressantes EAD | 4–6 | **4–5** |

**[FATO]** A renovação do braço EAD cai de 81,5% para 61,6% na coorte 2020 — melhora real, porque os cursos criados durante o choque saem da amostra. Mas **continua acima de 35%**, o limiar de falha do GATE C4.

**A concentração não melhorou — piorou marginalmente.** **[FATO]** número efetivo de IES (Kish, ponderado por ingressantes):

| Coorte | Presencial estável | **EAD estável** |
|---|---|---|
| 2015 | 183,5 | **11,6** |
| 2017 | 192,0 | **12,9** |
| 2019 | 173,7 | **14,6** |
| 2020 | 142,8 | **13,4** |

Excluir cursos criados em 2020 remove sobretudo cursos de instituições menores, o que **aumenta** o peso relativo dos grandes grupos. O GATE C6 permanece em falha.

### 7.3 Suporte por área CINE

**[FATO]** Cursos EAD estáveis por área geral:

| Área CINE | 2015 | 2017 | 2019 | Presencial 2019 |
|---|---|---|---|---|
| 01 Educação | 377 | 632 | 641 | 4.799 |
| 02 Artes e humanidades | 20 | 38 | 86 | 1.218 |
| 03 Ciências sociais, comunicação | 12 | 20 | 40 | 1.633 |
| 04 Negócios, administração, direito | 463 | 758 | 1.153 | 6.582 |
| **05 Ciências naturais, matemática** | **1** | **1** | **11** | 759 |
| 06 Computação e TIC | 75 | 109 | 178 | 1.753 |
| 07 Engenharia, produção, construção | 72 | 146 | 220 | 4.708 |
| **08 Agricultura, veterinária** | **4** | **10** | **19** | 1.036 |
| 09 Saúde e bem-estar | 31 | 77 | 139 | 5.029 |
| 10 Serviços | 38 | 74 | 103 | 697 |

Áreas 05 e 08 continuam sem suporte utilizável. Áreas 02 e 03 são marginais antes de 2017.

---

## 8. O teste de pré-tendências

### 8.1 Especificação

Conforme [auditoria_causal_covid.md](auditoria_causal_covid.md) §9, versão **estratificada por idade de trajetória** — a única que não confunde amadurecimento da coorte com tempo de calendário.

Para cada τ ∈ {0, 1, 2}, com a coorte `k` indexando também o ano-calendário (`t = k + τ`):

```
hazard_{c,k} = α_{estrato(c) × k} + Σ_{j ≠ ref} δ_j · Presencial_c · 1[k = j] + ε_{c,k}
```

| Item | Escolha |
|---|---|
| **Outcome** | `hazard = 100 × QT_DESISTENCIA / (EM_RISCO_INICIO − QT_FALECIDO)`. **Nunca `TDA` nem `TADA`.** |
| **Tratamento** | `Presencial` = 1 para presencial estável pré-COVID, 0 para EAD estável pré-COVID |
| **Controle de idade/coorte** | τ fixo por regressão (elimina o efeito de idade); efeito fixo `estrato × coorte` (elimina efeitos de coorte comuns) |
| **Identificação** | absorver `estrato × coorte` faz com que **só estratos com as duas modalidades naquela coorte** contribuam — a comparação é automaticamente *within* |
| **Ponderação** | população em risco (`EM_RISCO_INICIO − QT_FALECIDO`); versão não ponderada reportada |
| **Cluster** | `CO_IES_2019` |
| **Inferência** | **wild cluster bootstrap** (Rademacher, nulo imposto), B = 9.999 |
| **Ano-base** | última coorte integralmente pré-choque para cada τ |

**Leads disponíveis [FATO]:**

| τ | Coortes pré-2020 | Referência | Leads |
|---|---|---|---|
| 0 | 2015, 2016, 2017, 2018, 2019 | 2019 | **4** |
| 1 | 2015, 2016, 2017, 2018 | 2018 | **3** |
| 2 | 2015, 2016, 2017 | 2017 | **2** |
| 3 | 2015, 2016 | 2016 | 1 (insuficiente) |
| 4 | 2015 | — | **0** |
| ≥5 | nenhuma | — | **0** |

### 8.2 Parametrização — nota metodológica

A regressão inclui o **efeito principal `Presencial`** além das interações `Presencial × coorte`. Sem ele, os coeficientes mediriam o **nível** do gap em cada coorte, com o gap do ano-base forçado a zero, e não o desvio em relação ao ano-base — que é o que um event study reporta. Com o efeito principal incluído:

```
δ_j = (gap presencial−EAD na coorte j) − (gap na coorte de referência)
```

**[FATO]** Verificação: na especificação S1 sem estrato, τ=0, `δ_2015 = −1,162`, que é exatamente `−4,535 − (−3,373)` dos gaps brutos de §8.3. A parametrização está correta.

### 8.3 Especificações de estrato

| Sigla | Estrato (sempre × coorte) | Papel |
|---|---|---|
| **S1** | nenhum | gap bruto |
| **S2** | `CO_IES_2019` | IES com ambas as modalidades |
| **S3** | `CO_IES_2019 × CINE_AREA_2019` | **principal** — mesma IES e mesma área CINE |
| **S4** | `CO_IES_2019 × CINE_ROTULO_2019` | mesmo rótulo de curso, o estrato mais fino |
| **S5** | `CATEGORIA_2019 × CINE_AREA_2019` | mesma categoria administrativa e área |

### 8.4 Gap bruto, para leitura direta

**[FATO]** Hazard ponderado, somente tratamento pré-COVID estável:

**τ = 0**

| Ano | Coorte | Período | Presencial | EAD | Gap |
|---|---|---|---|---|---|
| 2015 | 2015 | PRÉ | 11,758 | 16,293 | **−4,535** |
| 2016 | 2016 | PRÉ | 13,294 | 23,365 | **−10,071** |
| 2017 | 2017 | PRÉ | 13,077 | 18,318 | **−5,241** |
| 2018 | 2018 | PRÉ | 12,899 | 21,488 | **−8,589** |
| 2019 | 2019 | PRÉ | 14,964 | 18,337 | **−3,373** |
| 2020 | 2020 | PÓS | 14,890 | 17,042 | −2,152 |

Amplitude pré: **6,698 p.p.** · dp: **2,839 p.p.** · variação 2019→2020: **+1,221 p.p.**

**τ = 1**

| Ano | Coorte | Período | Presencial | EAD | Gap |
|---|---|---|---|---|---|
| 2016 | 2015 | PRÉ | 16,894 | 22,692 | **−5,798** |
| 2017 | 2016 | PRÉ | 17,229 | 25,565 | **−8,336** |
| 2018 | 2017 | PRÉ | 18,005 | 29,839 | **−11,834** |
| 2019 | 2018 | PRÉ | 18,622 | 29,570 | **−10,948** |
| 2020 | 2019 | PÓS | 18,264 | 28,434 | −10,170 |
| 2021 | 2020 | PÓS | 17,665 | 29,989 | −12,324 |

Amplitude pré: **6,036 p.p.** · dp: **2,727 p.p.** · variação 2019→2020: **+0,778 p.p.**

**τ = 2**

| Ano | Coorte | Período | Presencial | EAD | Gap |
|---|---|---|---|---|---|
| 2017 | 2015 | PRÉ | 15,447 | 19,353 | **−3,906** |
| 2018 | 2016 | PRÉ | 16,375 | 22,734 | **−6,359** |
| 2019 | 2017 | PRÉ | 16,769 | 18,794 | **−2,025** |
| 2020 | 2018 | PÓS | 16,262 | 18,271 | −2,009 |
| 2021 | 2019 | PÓS | 14,739 | 19,979 | −5,240 |
| 2022 | 2020 | PÓS | 18,654 | 26,950 | −8,296 |

Amplitude pré: **4,334 p.p.** · dp: **2,173 p.p.** · variação 2019→2020: **+0,016 p.p.**

> **Em todas as três idades de trajetória, a oscilação do gap dentro do período pré-choque é maior — em τ=2, muito maior — do que a mudança observada em 2020.** As séries com tratamento predeterminado são praticamente idênticas às da auditoria anterior, o que era esperado depois de §5.2.

<!-- RESULTADOS_REGRESSAO -->

---
