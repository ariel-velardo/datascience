# Auditoria Multi-Coorte — Indicadores de Trajetória 2015–2020

**Projeto:** Impacto da COVID-19 sobre a desistência no ensino superior
**Escopo:** aquisição, auditoria e consolidação das coortes de ingresso 2015–2020
**Data:** 2026-09-04
**Status:** auditoria e ingestão. Nenhum XLSX original foi modificado. Nenhum modelo causal implementado. Nenhum commit realizado.

Convenção:

- **[FATO]** — verificado programaticamente nesta auditoria, com a contagem exata reportada.
- **[DICIONÁRIO]** — transcrito da documentação oficial do Inep.
- **[HIPÓTESE]** — interpretação ainda não comprovada.

Documento irmão: [auditoria_causal_covid.md](auditoria_causal_covid.md) — a avaliação de viabilidade causal que se apoia nestes dados.

---

## 1. Confirmação das fontes (Etapa 1)

A página oficial é
`https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/indicadores-de-trajetoria-da-educacao-superior`.
Os links de download não aparecem no HTML da página: as abas são carregadas por AJAX. Os endereços foram recuperados dos atributos `data-url` das abas e, dentro do conteúdo de cada aba, do link para `download.inep.gov.br`.

**[FATO] As seis coortes existem, todas com acompanhamento encerrando em 2024:**

| Coorte | URL oficial | ZIP | `Last-Modified` | XLSX extraído | MD5 confere |
|---|---|---|---|---|---|
| 2015 | `https://download.inep.gov.br/informacoes_estatisticas/indicadores_educacionais/indicadores_trajetoria_es_2015_2024.zip` | 78,5 MB | 2025-08-22 | 42,81 MB | ✅ |
| 2016 | `.../indicadores_trajetoria_es_2016_2024.zip` | 75,2 MB | 2025-08-22 | 40,62 MB | ✅ |
| 2017 | `.../indicadores_trajetoria_es_2017_2024.zip` | 71,8 MB | 2025-08-22 | 38,67 MB | ✅ |
| 2018 | `.../indicadores_trajetoria_es_2018_2024.zip` | 67,8 MB | 2025-08-22 | 36,24 MB | ✅ |
| 2019 | `.../indicadores_trajetoria_es_2019_2024.zip` | 62,0 MB | 2025-08-22 | 32,87 MB | ✅ |
| 2020 | `.../indicadores_trajetoria_es_2020_2024.zip` | 53,1 MB | 2025-08-22 | 27,74 MB | ✅ |

Formato: ZIP contendo `XLSX` + `ODS` (mesma tabela) + `Dicionário_acompanhamento_trajetória.docx` + `md5_*.txt`.
Período de acompanhamento: da coorte `k` até 2024, ou seja **`2024 − k + 1` anos de referência**.

**Metodologia oficial:** `https://download.inep.gov.br/informacoes_estatisticas/indicadores_educacionais/2017/metodologia_indicadores_trajetoria_curso.pdf`

**Coortes mais antigas também existem** (não baixadas), sob outro padrão de nome — relevantes para o plano de dados de §11 do documento causal:

| Aba | Arquivo | ZIP | Publicação |
|---|---|---|---|
| 2010–2019 | `Indicadores_Educacionais_Indicadores_Fluxo_Educacao_Superior_2010_2019.zip` | 55,6 MB | 2020-10-07 |
| 2011–2020 | `Indicadores_Fluxo_ES_2011_2020.zip` | 56,7 MB | 2023-03-16 |
| 2012–2021 | `Indicadores_Fluxo_ES_2012_2021.zip` | 58,8 MB | 2023-03-16 |
| 2013–2022 | `indicadores_fluxo_es_2013-2022.zip` | 74,4 MB | 2023-09-11 |
| 2014–2023 | `indicadores_fluxo_es_2014-2023.zip` | 76,5 MB | 2024-09-18 |

---

## 2. Política de economia de disco aplicada

Executada pelo script [src/baixa_trajetorias.py](../src/baixa_trajetorias.py):

```
download ZIP → conferir MD5 → extrair → manter XLSX + dicionário + md5.txt
            → apagar ODS (duplicata exata do XLSX) → apagar ZIP
```

**[FATO] Balanço de disco:**

| | Volume |
|---|---|
| Se tudo fosse mantido (ZIP + XLSX + ODS, 5 coortes novas) | ~ 493 MB |
| Efetivamente em disco após a política (5 coortes novas) | **169 MB** |
| Economia | **~ 66%** |
| `data/raw/` total, incluindo a coorte 2015 pré-existente | **210 MB** |
| Camada analítica `trajetorias_2015_2020.parquet` | **25,6 MB** |
| Pico transitório de disco (1 ZIP por vez) | ≤ 79 MB |

**Arquivos apagados, e por quê:**

| Arquivo | Volume | Justificativa |
|---|---|---|
| `indicadores_trajetoria_educacao_superior_{2016..2020}_2024.ods` | 160,7 MB | Duplicata exata do XLSX correspondente — mesmo conteúdo em outro formato de planilha. O MD5 de cada ODS está registrado no `md5_*.txt` mantido em disco, e ambos são redownloadáveis do portal do Inep. |
| `indicadores_trajetoria_es_{2016..2020}_2024.zip` | 330,7 MB | Container. O conteúdo útil já foi extraído e verificado por MD5. |

Nenhum arquivo pré-existente foi apagado ou modificado. O XLSX da coorte 2015, já presente antes desta sessão, teve o MD5 reconferido (`7d3de477baea4c6ee30f91413da20d69`) e bate com o publicado.

**Nota técnica.** O host `download.inep.gov.br` não envia o certificado intermediário da cadeia TLS. `requests`/OpenSSL falha com `CERTIFICATE_VERIFY_FAILED`; o `curl` do Windows resolve o intermediário via AIA e valida normalmente. O script usa `curl` como transporte, **com verificação TLS ativa** (sem `-k`), e reconfere a integridade contra o MD5 publicado pelo próprio Inep.

---

## 3. Auditoria por coorte (Etapa 2)

Cada XLSX foi auditado **isoladamente, antes de qualquer concatenação**, por
[src/constroi_painel_multicoorte.py](../src/constroi_painel_multicoorte.py).
As métricas completas ficam em `data/processed/auditoria_multicoorte.json`.

### 3.1 Tabela-resumo por coorte

**[FATO]**

| Coorte | Linhas de dados | Cursos | IES | Ingressantes | Anos de ref. | Obs./curso | `QT_ING` mín |
|---|---|---|---|---|---|---|---|
| 2015 | 281.430 | 28.143 | 2.158 | 3.027.277 | 2015–2024 | 10 | 4 |
| 2016 | 263.178 | 29.242 | 2.185 | 3.061.457 | 2016–2024 | 9 | 4 |
| 2017 | 247.200 | 30.900 | 2.274 | 3.316.684 | 2017–2024 | 8 | 4 |
| 2018 | 230.209 | 32.887 | 2.340 | 3.522.615 | 2018–2024 | 7 | 4 |
| 2019 | 206.808 | 34.468 | 2.401 | 3.707.897 | 2019–2024 | 6 | 4 |
| 2020 | 174.240 | 34.848 | 2.339 | 3.859.448 | 2020–2024 | 5 | 4 |
| **Total** | **1.403.065** | — | — | — | — | — | — |

### 3.2 Verificações de qualidade — todas as seis coortes

**[FATO]** Todos os testes abaixo passam **identicamente** nas seis coortes:

| Verificação | Resultado |
|---|---|
| Planilhas por arquivo | 1 (`INDICADORES_TRAJETORIA`) |
| Linha do cabeçalho técnico | 9 |
| Nº de colunas | **31**, com nomes idênticos e na mesma ordem |
| Linha de rodapé | exatamente 1 (`Fonte: Censo da Educação Superior/Inep.`) — removida na ingestão |
| Preâmbulo linha 5 declara a coorte | sim, e bate com o nome do arquivo nas 6 |
| Chave `(CO_CURSO, NU_ANO_REFERENCIA)` única | **sim, nas 6** |
| Linhas integralmente duplicadas | **0, nas 6** |
| Painel balanceado (todo curso com o mesmo nº de anos) | **sim, nas 6** |
| `QT_INGRESSANTE` constante dentro da trajetória | **sim, nas 6** |
| `QT_INGRESSANTE ≤ 0` | 0 |
| Quantidades negativas | 0 |
| Taxas fora de [0, 100] | 0 |
| Colunas com nulos | apenas `CO_REGIAO`, `CO_UF`, `CO_MUNICIPIO` |
| 100% dos nulos geográficos são EAD **e** 100% dos EAD têm geografia nula | **sim, nas 6** |
| Identidade contábil acumulada | **100,000%, resíduo máximo 0, nas 6** |
| `TAP + TCA + TDA = 100` | **100,000% (desvio máx. 1,0 × 10⁻⁸), nas 6** |
| Monotonicidade `TDA` (não decrescente) | 0 violações |
| Monotonicidade `TAP` (não crescente) | 0 violações |
| Fórmulas com denominador "vivo" | **100% de acerto para TAP, TCA, TDA, TCAN, TADA, nas 6** |
| Covariáveis constantes dentro da trajetória | **0 cursos variantes, em todas as 7 testadas, nas 6** |

Nulos geográficos por coorte **[FATO]**: 11.180 · 11.619 · 15.168 · 19.390 · 23.664 · 26.230 linhas — crescendo com a expansão do EAD.

### 3.3 Identidade contábil e fórmulas — confirmadas em escala

A identidade recuperada na auditoria anterior sobre a coorte 2015 **vale sem exceção nas seis coortes**:

```
D(t) = QT_INGRESSANTE − Σ_{s≤t} QT_FALECIDO(s)      (denominador "vivo")

QT_PERMANENCIA(t) + Σ_{s≤t}(CONCLUINTE + DESISTENCIA + FALECIDO) = QT_INGRESSANTE

TAP(t)  = 100 × QT_PERMANENCIA(t)         / D(t)
TCA(t)  = 100 × Σ_{s≤t} QT_CONCLUINTE(s)  / D(t)
TDA(t)  = 100 × Σ_{s≤t} QT_DESISTENCIA(s) / D(t)
TCAN(t) = 100 × QT_CONCLUINTE(t)          / D(t)
TADA(t) = 100 × QT_DESISTENCIA(t)         / D(t)
```

O denominador **bruto** (sem descontar falecidos) falha: para `TDA` acerta apenas 273.898/281.430 na coorte 2015 e 171.473/174.240 na coorte 2020.

### 3.4 Diferenças de schema entre coortes

**[FATO] Nenhuma.** As 31 colunas são idênticas em nome e ordem nas seis coortes. A concatenação só foi executada após uma asserção automática de igualdade dos schemas (`assert len(set(colunas)) == 1`).

A única diferença de conteúdo detectada é cosmética: no preâmbulo, a coorte 2015 rotula a última taxa como `TDAN` e as demais como `TADA`; o **cabeçalho técnico da linha 9 é `TADA` nas seis**.

---

## 4. Camada analítica construída

**Arquivo:** `data/processed/trajetorias_2015_2020.parquet` — 25,56 MB, compressão ZSTD.

**[FATO] Dimensões:**

| Item | Valor |
|---|---|
| Linhas | 1.403.065 |
| Trajetórias `(coorte, curso)` | 190.488 |
| Cursos distintos | 43.861 |
| IES distintas | 2.798 |
| Anos de referência | 2015–2024 |
| Idade de trajetória (τ) | 0–9 |

**Proveniência registrada por linha:** `NU_ANO_INGRESSO` (a coorte), `ARQUIVO_ORIGEM` (nome do XLSX publicado) e `MD5_ORIGEM` (hash do XLSX). Qualquer linha do painel é rastreável até o arquivo oficial de origem.

**Colunas derivadas acrescentadas** (as 31 originais são preservadas sem alteração):

| Coluna | Definição |
|---|---|
| `IDADE_TRAJETORIA` (τ) | `NU_ANO_REFERENCIA − NU_ANO_INGRESSO` |
| `CUM_CONCLUINTE`, `CUM_DESISTENCIA`, `CUM_FALECIDO` | somas acumuladas dentro de `(coorte, curso)` |
| `EM_RISCO_INICIO` | `QT_PERMANENCIA(t−1)`; em τ=0, `QT_INGRESSANTE` |
| `HAZARD_DESISTENCIA` | `100 × QT_DESISTENCIA(t) / (EM_RISCO_INICIO(t) − QT_FALECIDO(t))` |

**[FATO] Validação de `EM_RISCO_INICIO`:** a identidade de fluxo

```
QT_PERMANENCIA(t) = EM_RISCO_INICIO(t) − QT_DESISTENCIA(t) − QT_CONCLUINTE(t) − QT_FALECIDO(t)
```

fecha em **1.403.065 / 1.403.065 linhas (100,000%)**. A população em risco não foi arbitrada: foi derivada da identidade contábil da própria base e verificada exaustivamente.

**Tipagem.** `CO_CINE_AREA_GERAL` e `CO_CINE_ROTULO` são forçados a texto (códigos com zero à esquerda, `Char(2)`/`Char(7)` no dicionário). `CO_REGIAO`/`CO_UF`/`CO_MUNICIPIO` são `Int64` anulável — os nulos do EAD são estruturais e **nunca** devem ser imputados.

---

## 5. Achados estruturais do painel consolidado

### 5.1 O painel é um triângulo, não um retângulo

**[FATO]** Estrutura `(coorte × ano de referência) → τ`:

| Coorte \ Ano | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2015 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| 2016 | | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| 2017 | | | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| 2018 | | | | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| 2019 | | | | | 0 | 1 | 2 | 3 | 4 | 5 |
| 2020 | | | | | | 0 | 1 | 2 | 3 | 4 |

Todas as coortes terminam em 2024 (truncamento à direita). Consequências:

- **cada célula `(coorte, ano)` tem um único τ**, e `ano = coorte + τ` é uma identidade exata — este é o problema age-period-cohort, e ele é estrutural, não amostral;
- só τ ≤ 4 tem observações **anteriores** a 2020;
- τ = 0..4 têm as seis coortes (190.488 trajetórias cada); τ = 5..9 perdem uma coorte por ano.

### 5.2 Expansão e recomposição do EAD

**[FATO]**

| Coorte | Cursos pres. | Cursos EAD | Ingr. pres. | Ingr. EAD | % ingr. EAD | IES pres. | IES EAD |
|---|---|---|---|---|---|---|---|
| 2015 | 27.025 | 1.118 | 2.297.858 | 729.419 | 24,09 | 2.154 | 146 |
| 2016 | 27.951 | 1.291 | 2.195.829 | 865.628 | 28,28 | 2.181 | 157 |
| 2017 | 29.004 | 1.896 | 2.214.184 | 1.102.500 | 33,24 | 2.269 | 245 |
| 2018 | 30.117 | 2.770 | 2.112.867 | 1.409.748 | 40,02 | 2.333 | 298 |
| 2019 | 30.524 | 3.944 | 2.069.778 | 1.638.119 | 44,18 | 2.391 | 347 |
| 2020 | 29.602 | 5.246 | 1.820.226 | 2.039.222 | **52,84** | 2.312 | 409 |

Em cinco anos o EAD passa de **um quarto a mais da metade** dos ingressantes. O número de cursos EAD quadruplica (×4,69) e o porte médio cai de 652 para 389 ingressantes.

### 5.3 Renovação dos braços de comparação

**[FATO]** Percentual de cursos da coorte `k` que **não** estavam na coorte 2015 na mesma modalidade:

| Coorte | EAD: % cursos novos | EAD: % ingressantes em cursos novos | Presencial: % cursos novos | Presencial: % ingr. novos |
|---|---|---|---|---|
| 2016 | 22,7 | 5,1 | 9,1 | 5,0 |
| 2017 | 45,6 | 17,8 | 14,8 | 10,3 |
| 2018 | 64,5 | 26,6 | 21,0 | 15,3 |
| 2019 | 75,6 | 35,1 | 25,2 | 20,1 |
| 2020 | **81,5** | **43,5** | 27,3 | 22,2 |

O braço EAD se renova **três vezes mais rápido** que o presencial. Esta é a ameaça número um a qualquer desenho que compare os dois grupos ao longo das coortes.

### 5.4 Concentração institucional do EAD

**[FATO]**

| Coorte | IES para 50% dos ingr. EAD | IES para 80% | IES EAD (total) | Top-10 (%) |
|---|---|---|---|---|
| 2015 | **4** | 14 | 146 | 74,82 |
| 2016 | 4 | 12 | 157 | 76,51 |
| 2017 | 5 | 17 | 245 | 70,82 |
| 2018 | 5 | 17 | 298 | 69,25 |
| 2019 | **6** | 20 | 347 | 67,49 |
| 2020 | 5 | 20 | 409 | 68,60 |

A concentração cai um pouco, mas permanece extrema: **quatro a seis instituições concentram metade de todos os ingressantes EAD do Brasil** em qualquer coorte.

### 5.5 Dependência intra-IES

**[FATO]** ICC do hazard de desistência em τ=1, por ANOVA de uma via com grupos = `CO_IES` (IES com ≥ 2 cursos):

| Coorte | Cursos | IES | ICC |
|---|---|---|---|
| 2015 | 27.519 | 1.775 | 0,3597 |
| 2016 | 28.570 | 1.812 | 0,3772 |
| 2017 | 30.229 | 1.885 | 0,4156 |
| 2018 | 32.116 | 1.942 | 0,4327 |
| 2019 | 33.645 | 1.982 | **0,5046** |
| 2020 | 34.036 | 1.888 | 0,4604 |

*Correção metodológica em relação à auditoria anterior:* o ICC ≈ 0,65 reportado em `auditoria_metodologica.md` §8.4 foi calculado como razão simples entre a variância das médias por IES e a variância total. Esse estimador é **enviesado para cima** quando muitas IES têm poucos cursos, porque o ruído amostral das médias entra na variância "entre". O estimador de ANOVA acima é o correto. A conclusão substantiva não muda — a dependência intra-IES é grande e **cresce ao longo das coortes** — mas a magnitude é de ~0,36–0,50, não 0,65.

---

## 6. Comandos e arquivos desta etapa

**Criados no projeto:**

| Arquivo | Papel |
|---|---|
| `src/baixa_trajetorias.py` | download + verificação MD5 + extração + política de retenção |
| `src/constroi_painel_multicoorte.py` | ingestão auditada e construção do Parquet |
| `data/processed/trajetorias_2015_2020.parquet` | camada analítica (25,56 MB) |
| `data/processed/auditoria_multicoorte.json` | métricas completas por coorte |
| `docs/auditoria_multicoorte.md` | este documento |
| `docs/auditoria_causal_covid.md` | avaliação de viabilidade causal |
| `data/raw/trajetoria/{2016..2020}_2024/` | XLSX + dicionário + md5 de cada coorte |

**Comandos executados:**

```bash
python src/baixa_trajetorias.py 2016 2017 2018 2019 2020
python src/constroi_painel_multicoorte.py
```

Ambos são idempotentes: o download pula coortes que já têm XLSX em disco.

**Nada foi commitado.** `data/` e `*.parquet` já estavam no `.gitignore`; apenas os dois scripts em `src/` e os dois documentos em `docs/` aparecem como não rastreados.

Scripts de diagnóstico exploratório permaneceram fora do projeto, no scratchpad da sessão (`diag_causal.py`, `diag_causal2.py`, `diag_causal3.py`, `listar_zip_remoto.py`, `cabecalho_csv_remoto.py`, `audit_headers.py`).
