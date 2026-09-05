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

## 8.5 Resultados do event study — leads pré-2020

**[FATO]** Fonte: `data/processed/gate_pre_tendencias.json` — 33 especificações, todas com wild cluster bootstrap **B = 9.999** concluído (seed 20260904). Coeficientes em pontos percentuais de hazard, com erro-padrão CR1 clusterizado por `CO_IES_2019` entre parênteses.

> **Leitura:** `δ_j` é o desvio, na coorte `j`, do gap presencial−EAD em relação ao gap da coorte de referência. Sob tendências paralelas, **todos** os `δ_j` deveriam ser ≈ 0.

### τ = 0 (ref. = coorte 2019, 4 leads)

| Spec | δ 2015 | δ 2016 | δ 2017 | δ 2018 | max\|δ\| | dp(δ) |
|---|---|---|---|---|---|---|
| **S1** sem estrato | −1,162 (5,03) | **−6,698** (2,67) | −1,867 (1,68) | **−5,216** (1,88) | **6,698** | 2,651 |
| **S2** IES | **+4,758** (2,28) | **+2,424** (2,12) | +1,694 (1,17) | +0,349 (1,05) | **4,758** | 1,847 |
| **S3** IES × área *(principal)* | **+4,539** (2,44) | +1,904 (2,43) | +1,723 (1,27) | −0,064 (1,07) | **4,539** | 1,896 |
| **S4** IES × rótulo | **+4,257** (2,25) | **+2,207** (2,47) | +1,878 (1,47) | −0,549 (1,24) | **4,257** | 1,970 |
| **S5** categoria × área | **−3,889** (4,58) | **−7,058** (2,68) | **−3,263** (1,80) | **−6,299** (1,83) | **7,058** | 1,836 |
| S3 **não ponderado** | **+4,258** (1,50) | **+2,520** (1,50) | **+2,937** (0,98) | +1,736 (1,06) | **4,258** | 1,055 |

### τ = 1 (ref. = coorte 2018, 3 leads)

| Spec | δ 2015 | δ 2016 | δ 2017 | max\|δ\| | dp(δ) |
|---|---|---|---|---|---|
| **S1** sem estrato | **+5,151** (3,40) | **+2,612** (2,97) | −0,886 (2,19) | **5,151** | 3,031 |
| **S2** IES | **+2,231** (1,74) | +1,592 (1,71) | +0,313 (1,06) | **2,231** | 0,977 |
| **S3** IES × área *(principal)* | +1,746 (2,03) | +1,037 (1,79) | +0,121 (1,06) | **1,746** | 0,815 |
| **S4** IES × rótulo | +1,420 (2,60) | +0,855 (2,60) | +0,376 (1,34) | **1,420** | 0,523 |
| **S5** categoria × área | **+3,988** (2,91) | +1,487 (2,55) | −1,184 (1,95) | **3,988** | 2,586 |
| S3 **não ponderado** | +1,619 (1,51) | +1,174 (1,29) | +1,477 (1,33) | **1,620** | 0,227 |

### τ = 2 (ref. = coorte 2017, 2 leads)

| Spec | δ 2015 | δ 2016 | max\|δ\| | dp(δ) |
|---|---|---|---|---|
| **S1** sem estrato | −1,882 (1,48) | **−4,335** (2,43) | **4,335** | 1,735 |
| **S2** IES | −0,483 (1,51) | **−2,985** (1,73) | **2,985** | 1,769 |
| **S3** IES × área *(principal)* | −1,391 (1,48) | **−3,288** (1,81) | **3,288** | 1,342 |
| **S4** IES × rótulo | −1,960 (1,72) | **−2,852** (1,52) | **2,852** | 0,630 |
| **S5** categoria × área | −1,907 (1,44) | **−3,025** (2,27) | **3,025** | 0,790 |
| S3 **não ponderado** | −1,058 (1,35) | −0,330 (1,34) | **1,058** | 0,515 |

Em negrito, `|δ| ≥ 2,0` p.p. — o limiar de FALHA de §11.5. **[FATO]** 20 dos 45 leads estimados nas especificações ponderadas excedem esse limiar.

**Amostra de estimação da especificação principal S3 [FATO]:**

| τ | Linhas | Cursos (pres. / EAD) | IES | Estratos × coorte | N efetivo IES EAD |
|---|---|---|---|---|---|
| 0 | 33.625 | 7.841 / 2.793 | 320 | 2.629 | **12,2** |
| 1 | 25.653 | 7.671 / 2.718 | 314 | 1.957 | **13,2** |
| 2 | 17.002 | 6.279 / 1.819 | 236 | 1.252 | **12,2** |

### 8.5.1 A instabilidade que mais pesa: o sinal do lead depende da especificação

**[FATO]** Em τ = 0, os leads são **negativos e grandes** sem estrato (S1: −6,698) e **positivos e grandes** dentro da mesma IES e da mesma área CINE (S3: +4,539). A escolha do estrato **inverte o sinal da pré-tendência**, com magnitude comparável nos dois sentidos.

**[FATO]** Na especificação principal S3, o sinal também **inverte entre idades de trajetória**: +4,539 (τ=0) · +1,746 (τ=1) · −3,288 (τ=2).

**[HIPÓTESE]** É o que se espera quando não existe tendência diferencial subjacente estável, e sim **recomposição**: o gap agregado é dominado por quais IES e quais áreas entram na comparação em cada coorte — consistente com §7.2 (renovação de 61,6% do braço EAD na coorte 2020) e com a dominância de uma dúzia de grupos educacionais (§11.4 da auditoria).

Um pré-teste cujo **sinal** depende do estrato e da idade não sustenta a hipótese de tendências paralelas em nenhuma das duas direções.

---

## 8.6 Teste conjunto dos leads — wild cluster bootstrap

**[FATO]** H₀: todos os `δ_j` de lead são nulos. Estatística de Wald com VCV CR1; p-valor por **wild cluster bootstrap Rademacher com o nulo imposto (WCB-R), B = 9.999**, reamostragem por `CO_IES_2019`.

| Spec | τ=0 — Wald / p | τ=1 — Wald / p | τ=2 — Wald / p |
|---|---|---|---|
| **S1** sem estrato | 19,21 / **0,0362** | 5,52 / 0,4556 | 5,01 / 0,1886 |
| **S2** IES | 10,52 / 0,2268 | 1,86 / 0,7809 | 3,33 / 0,3508 |
| **S3** IES × área *(principal)* | 13,54 / 0,1419 | 1,07 / 0,9147 | 4,83 / 0,1983 |
| **S4** IES × rótulo | 10,78 / 0,2153 | 0,62 / 0,9742 | 5,86 / 0,1539 |
| **S5** categoria × área | 15,64 / **0,0499** | 5,03 / 0,4635 | 3,43 / 0,3045 |
| S3 **não ponderado** | 11,92 / **0,0254** | 1,51 / 0,6908 | 0,62 / 0,7460 |

**[FATO]** Incluir a coorte pós-2020 na regressão (`inclui_pos_2020 = true`) não altera os leads e move o p-valor conjunto, no máximo, na terceira casa decimal (ex.: S2/τ=0: 0,2268 → 0,2261). Os leads são robustos à janela.

**Nenhum p conjunto cai abaixo de 0,01.** Três caem na faixa 0,01–0,10 — e são exatamente as três especificações com os **maiores** leads (S1 e S5 em τ=0, e a versão não ponderada). Os p altos concentram-se em τ=1 e τ=2, onde há apenas **3 e 2 leads**.

### 8.6.1 Escopo exato da inferência bootstrap — declarado

**[FATO]** O WCB-R de B = 9.999 foi aplicado ao **teste conjunto**. Os erros-padrão e IC95 individuais dos leads são **CR1 analíticos**, não bootstrap.

Isso importa, e por isso está declarado: **[FATO]** o número efetivo de IES do braço EAD na amostra de estimação de S3 é **12,2 · 13,2 · 12,2** — muito abaixo do limiar de 20 do GATE C6. Com esse número de clusters, o CR1 analítico é **anticonservador**: os IC95 individuais são, se algo, **estreitos demais**. O veredito desta seção não depende disso, porque se apoia em magnitude e não em significância — mas **nenhuma leitura de significância individual a 5% deve ser feita a partir das tabelas de §8.5**.

---

## 8.7 Magnitude dos leads versus a quebra de 2020

Comparação exigida pelo critério (iii) de §11.5. A "quebra de 2020" é o coeficiente da coorte cujo **ano-calendário é 2020** (τ=0 → coorte 2020; τ=1 → coorte 2019; τ=2 → coorte 2018). **Ela é reportada exclusivamente como referência de magnitude, e não é uma estimativa de efeito causal.**

| τ | Spec | max\|δ_lead\| | quebra 2020 (EP) | **razão lead / quebra** |
|---|---|---|---|---|
| 0 | S1 | 6,698 | +1,220 (0,98) | **5,49×** |
| 0 | S2 | 4,758 | +4,815 (1,07) | 0,99× |
| 0 | **S3** *(principal)* | **4,539** | **+5,159 (1,13)** | **0,88×** |
| 0 | S4 | 4,257 | +5,917 (1,01) | 0,72× |
| 0 | S5 | 7,058 | +2,132 (1,12) | **3,31×** |
| 1 | S1 | 5,151 | +0,778 (1,11) | **6,62×** |
| 1 | S2 | 2,231 | +1,591 (1,15) | **1,40×** |
| 1 | **S3** *(principal)* | **1,746** | **+1,540 (0,97)** | **1,13×** |
| 1 | S4 | 1,420 | +1,467 (1,13) | 0,97× |
| 1 | S5 | 3,988 | +1,477 (1,09) | **2,70×** |
| 2 | S1 | 4,335 | +0,016 (1,69) | **274×** |
| 2 | S2 | 2,985 | −0,656 (1,50) | **4,55×** |
| 2 | **S3** *(principal)* | **3,288** | **−0,176 (1,26)** | **18,7×** |
| 2 | S4 | 2,852 | +0,438 (1,34) | **6,51×** |
| 2 | S5 | 3,025 | +1,573 (1,59) | **1,92×** |

**[FATO] Em 11 das 15 combinações τ × especificação, o maior lead pré-2020 supera a quebra de 2020.** Na especificação principal S3, a razão é 0,88× (τ=0), 1,13× (τ=1) e 18,7× (τ=2).

**[FATO]** Critério (iii) de §11.5 — `σ_pré` versus `|θ̂|` — com `σ_pré = dp(δ_lead)` e `|θ̂|` = quebra de 2020, na especificação principal S3:

| τ | dp(δ) | quebra 2020 | `\|θ̂\|/3` | Faixa do critério |
|---|---|---|---|---|
| 0 | 1,896 | 5,159 | 1,720 | `\|θ̂\|/3 ≤ σ < \|θ̂\|` → **ALERTA** |
| 1 | 0,815 | 1,540 | 0,513 | `\|θ̂\|/3 ≤ σ < \|θ̂\|` → **ALERTA** |
| 2 | 1,342 | 0,176 | 0,059 | `σ ≫ \|θ̂\|` (7,6×) → **FALHA** |

Somente τ = 0 apresenta uma quebra de 2020 que se destaca da oscilação pré-choque — e, mesmo ali, apenas sob estratificação *within*-IES, e por margem estreita. Em τ = 2 **não há quebra**: o coeficiente de 2020 é −0,176 p.p., indistinguível de zero, contra leads de até 3,288 p.p.

---

## 8.8 O que os p-valores altos **não** dizem

A maioria dos p conjuntos é alta (0,14 a 0,97). **Isso não é evidência de tendências paralelas.** É o que a baixa potência produz quando o braço de comparação tem ~12 IES efetivas.

**[FATO]** Na especificação principal S3, τ = 0, o lead de 2015 vale **+4,539 p.p., com IC95 = [−0,243 ; +9,320]**. Esse intervalo:

- **inclui zero** — daí o p alto; e
- **inclui +9,320 p.p., ou seja, 1,8 vez a própria quebra de 2020 (+5,159 p.p.).**

O teste não distingue "ausência de pré-tendência" de "pré-tendência com o dobro do tamanho do efeito que se pretende medir". Um teste com esse intervalo **não tem poder para validar coisa alguma**: ele é não informativo, não aprovador.

O mesmo vale nas demais idades **[FATO]**:

| τ | Lead | δ | IC95 | Quebra 2020 | O IC comporta pré-tendência de até |
|---|---|---|---|---|---|
| 0 | 2015 | +4,539 | [−0,243 ; +9,320] | +5,159 | **1,8×** a quebra |
| 1 | 2015 | +1,746 | [−2,240 ; +5,733] | +1,540 | **3,7×** a quebra |
| 2 | 2016 | −3,288 | [−6,828 ; +0,251] | −0,176 | **39×** a quebra |

> **Regra aplicada aqui:** o GATE C3 é julgado por **magnitude substantiva e incerteza**, não por p-valor. Aceitar H₀ num teste sem potência é confundir *ausência de evidência* com *evidência de ausência*. As pré-tendências estimadas são **grandes em relação à quebra de 2020**, e a incerteza em torno delas é **larga o bastante para acomodar pré-tendências ainda maiores**. As duas leituras apontam na mesma direção, e nenhuma delas é favorável.

---

## 8.9 Aplicação dos critérios de §11.5

Especificação principal S3 (IES × área CINE), por idade de trajetória:

| Critério (§11.5) | τ = 0 | τ = 1 | τ = 2 |
|---|---|---|---|
| (i) `\|δ_j\| < 1,0` (PASSA) / `< 2,0` (ALERTA) | **+4,539** → 🔴 **FALHA** | 1,746 → 🟡 ALERTA | **−3,288** → 🔴 **FALHA** |
| (ii) p conjunto | 0,1419 (> 0,10) | 0,9147 (> 0,10) | 0,1983 (> 0,10) |
| (iii) `σ_pré` vs `\|θ̂\|` | 1,896 vs 5,159 → 🟡 ALERTA | 0,815 vs 1,540 → 🟡 ALERTA | 1,342 vs 0,176 → 🔴 **FALHA** |
| (iv) nenhum lead muda de sinal | **inverte** (+4,539 … −0,064) → 🔴 **FALHA** | ok (todos +) | ok (todos −) |
| (v) sobrevive ao *leave-one-institution-out* | ⚪ **NÃO EXECUTADO** | ⚪ **NÃO EXECUTADO** | ⚪ **NÃO EXECUTADO** |
| (vi) ≥ 3 leads (PASSA) / ≥ 2 (ALERTA) | 4 → ok | 3 → ok | 2 → só ALERTA |
| **Veredito por idade** | 🔴 **FALHA** | 🟡 **ALERTA** | 🔴 **FALHA** |

Fora da especificação principal o quadro é **pior**, não melhor: **[FATO]** em τ = 0, S1 e S5 têm leads de 6,698 e 7,058 p.p., com p conjunto de 0,0362 e 0,0499; a versão não ponderada tem p = 0,0254 com quatro leads acima de 1,7 p.p.

### Veredito do GATE C3

> # 🔴 **FALHA**

**Motivos determinantes — cada um suficiente isoladamente:**

1. **[FATO]** Leads de **+4,539 p.p. (τ=0)** e **−3,288 p.p. (τ=2)** na especificação principal, contra o limiar de FALHA de 2,0 p.p. de §11.5. Ao todo, **20 dos 45 leads** das especificações ponderadas excedem esse limiar.
2. **[FATO]** Em τ = 2, a oscilação pré-choque (dp 1,342) é **7,6 vezes** a quebra de 2020 (0,176 p.p.). Não há degrau a explicar.
3. **[FATO]** O **sinal** da pré-tendência inverte com o estrato (τ=0: −6,698 em S1 contra +4,539 em S3) e com a idade de trajetória (S3: +4,539 → +1,746 → −3,288). Critério (iv) violado.
4. **[FATO]** O critério (v) — *leave-one-institution-out* das 10 maiores IES EAD (teste F2 de §17) — **não foi executado**. PASSA é, por construção, inatingível sem ele.
5. Os p-valores altos **não sustentam** veredito favorável: os IC95 dos leads comportam pré-tendências de **1,8× a 39×** a quebra de 2020 (§8.8).

**A ressalva de §11.6 da auditoria está fechada.** O teste foi refeito com tratamento **predeterminado** (Censos 2015–2019; modalidade verificada como imutável em §5.2), com estratificação genuinamente pré-choque, com event study formal e com wild cluster bootstrap de 9.999 réplicas. **O resultado não se reverteu** — como antecipado em §11.6, a oscilação era grande demais e o braço EAD, concentrado demais.

O que a nova evidência **acrescenta** ao veredito anterior é qualitativo, e agrava: sabe-se agora que a pré-tendência **não tem sinal estável**. Antes havia uma pré-tendência grande; agora sabe-se que ela é grande **e não é uma tendência** — é recomposição.

---

## 9. Veredito e recomendação

### 9.1 Situação dos gates após esta execução

| Gate | Antes | **Depois** | Observação |
|---|---|---|---|
| **C1** Tratamento predeterminado | 🔴 FALHA | 🟢 **PASSA** | **[FATO]** cobertura 93,11% (≥ 90%); 0 cursos com modalidade instável em 2015–2019 (≥ 95%) |
| **C2** Overlap | 🔴 FALHA | 🔴 **FALHA** | áreas CINE 05 e 08 sem suporte; 4–5 IES concentram 50% dos ingressantes EAD |
| **C3** Tendências paralelas | 🔴 FALHA *(não conclusivo)* | 🔴 **FALHA** *(conclusivo)* | §8.9 |
| **C4** Estabilidade de composição | 🔴 FALHA | 🔴 **FALHA** | renovação do braço EAD cai de 81,5% para 61,6% — segue acima de 35% |
| **C5** Age/period/cohort | 🟡 ALERTA | 🟡 **ALERTA** | indeterminação linear permanente (§10.6 da auditoria) |
| **C6** Dependência intra-IES | 🔴 FALHA | 🔴 **FALHA** | **[FATO]** N efetivo de IES EAD na amostra S3: **12,2 · 13,2 · 12,2** |
| **C7** Sensibilidade | ⚪ não avaliado | ⚪ **não avaliado** | depende de estimativas que não devem existir |

**C1 foi recuperado — e recuperá-lo não salvou o desenho.** Era exatamente o teste que valia a pena fazer: barato, decisivo, e agora respondido.

### 9.2 Recomendação

> ## **ENCERRAR a linha causal COVID × presencial/EAD.**

Aplicando a tabela de critério de continuação de §20 da auditoria: **resultado do passo 5 = FALHA → "Encerrar a linha causal."**

Não é um gate marginal. **[FATO]** Três gates fundamentais permanecem em falha (C2, C3, C4), e um deles — **C6** — é **irrecuperável por construção**: o braço de comparação tem ~12 instituições efetivas. Nenhum estimador, amostra ou especificação altera a estrutura do mercado brasileiro de EAD.

**Nenhum DiD deve ser estimado.** A regra de §19 da auditoria permanece vinculante: enquanto C3 estiver em falha, nenhuma estimativa de efeito deve ser reportada, nem mesmo como preliminar.

**Reorientação recomendada, em ordem de retorno sobre esforço:**

1. **Trabalho descritivo e longitudinal multi-coorte** — plenamente sustentado pelos dados já em disco: a expansão do EAD de 24,3% para 50,4% dos ingressantes (2015 → 2020), a recomposição da entrada de 2020, o perfil de hazard condicional por idade de trajetória, a renovação do parque EAD.
2. **Capítulo metodológico sobre por que a identificação falha**, ancorado nos números deste documento. **[FATO]** O achado de §5.2 — a modalidade é atributo imutável de `CO_CURSO`, e a migração para EAD aparece como **cursos novos**, sendo que 44,8% dos cursos EAD novos de 2019 pertencem a uma IES que já tinha um presencial com o mesmo rótulo CINE em 2015 — é um resultado substantivo e publicável por si só, e explica **mecanicamente** por que o desenho DiD não pode funcionar aqui.
3. **Desenho alternativo de §8.5 da auditoria** (variação de severidade local), apenas se houver apetite por dados externos — sabendo que ele não reaproveita o braço EAD como comparação.

### 9.3 O que este documento **não** fez

**[FATO]** Nenhum DiD estimado · nenhum event study de *lags* · nenhum matching · nenhuma estimativa de efeito causal · nenhum dado bruto modificado · nenhum Censo de ano ≥ 2020 baixado · nenhum commit.

O único coeficiente pós-2020 reportado é a **quebra de 2020**, exigida pelo critério (iii) de §11.5 como referência de magnitude, e rotulada como tal em todas as tabelas e no próprio JSON: `"papel": "QUEBRA/pos (referencia de magnitude, NAO e efeito)"`.

### 9.4 Pendência declarada

O *leave-one-institution-out* das 10 maiores IES EAD (critério (v) de §11.5; teste F2 de §17) **não foi executado**. Ele não é necessário para o veredito de FALHA — já determinado pelos critérios (i), (iii) e (iv) — e só poderia agravá-lo. Fica registrado como **não executado**, para que ninguém o leia como aprovado.

---

## 10. Reprodução

```bash
python src/baixa_censos_pre_covid.py        # Censos 2015-2019, slim, MD5 conferido
python src/constroi_tratamento_pre_covid.py # tratamento predeterminado + painel causal
python src/gate_pre_tendencias.py           # event study dos leads + WCB B=9.999
```

**[FATO]** Saída do último passo: `data/processed/gate_pre_tendencias.json` — 33 especificações (3 τ × 5 estratos × 2 janelas, mais 3 não ponderadas), todas com `"B": 9999`. Seed fixa `20260904`; o wild bootstrap é determinístico dado o seed, de modo que as tabelas acima são reproduzíveis sem nova execução.
