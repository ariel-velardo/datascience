# Auditoria de viabilidade causal — reformulação do Fies (2018)

**Projeto:** Impacto de choques de política sobre a desistência no ensino superior
**Data:** 2026-09-05
**Escopo:** **AUDITORIA DE VIABILIDADE.** Nenhum modelo causal final foi implementado. Nenhuma estimativa de efeito é reportada. Nenhum arquivo novo foi baixado. Nenhum commit foi feito.
**Antecedente:** a linha causal COVID × presencial/EAD foi **encerrada** — ver [auditoria_causal_covid.md](auditoria_causal_covid.md) §21 e [gate_pre_tendencias.md](gate_pre_tendencias.md). Este documento abre um candidato **novo e independente**.

Convenção: **[FATO]** verificado programaticamente nos dados em disco · **[FONTE]** documento oficial citado · **[HIPÓTESE]** interpretação.

---

## 1. Pergunta

> **Após a reformulação do Fies, cursos privados que anteriormente dependiam mais do financiamento estudantil apresentaram mudança diferencial na desistência em relação a cursos menos expostos?**

Esta auditoria **não** pressupõe que a pergunta esteja identificada. O objetivo declarado é **tentar derrubá-la**. As seções 2 a 16 são tentativas de falseamento; a §17 consolida os gates e a §18 dá o veredito.

---

## 2. Choque institucional

### 2.1 O que mudou em 2018

**[FONTE]** A **Lei nº 13.530, de 7 de dezembro de 2017** (publicada no DOU em **8/12/2017**, vigência na data da publicação) reformulou o Fies. Dispositivos relevantes:

| Item | Conteúdo |
|---|---|
| **Aplicação** | As novas regras valem para contratos firmados **a partir do primeiro semestre de 2018**. Contratos até 2017.2 mantêm as condições originais, com migração **voluntária**. |
| **Juros** | Taxa de juros **real igual a zero** para os novos contratos, na forma definida pelo CMN. |
| **Amortização** | Pagamento por **percentual da renda** (máximo de 20% da renda bruta), com desconto em folha; fim da carência de 18 meses do regime anterior. |
| **FG-Fies** | Criação do **Fundo Garantidor do Fies**, de natureza privada, com participação da União em até **R$ 3 bilhões**. |
| **Contrapartida das IES** | **Adesão obrigatória** ao FG-Fies para novos financiamentos, com aportes sobre os encargos educacionais: **13% no ano 1** e **entre 10% e 25% nos anos 2 a 5, conforme evasão e inadimplência da própria instituição**. |
| **Novas modalidades** | Fies-Trabalhador, Fies-Empresa e o Programa de Financiamento Estudantil com recursos de fundos constitucionais (FNO, FNE, FCO) e de desenvolvimento (FDA, FDCO, FDNE). |
| **EAD** | **Nenhuma menção específica** à educação a distância no texto da lei. |
| **ProUni** | Uma única referência: o valor dos encargos que superar a bolsa **parcial** do ProUni pode ser financiado. Nenhuma alteração substantiva no ProUni. |

### 2.2 O ponto que derruba o corte ingênuo em 2018

**[FONTE]** O Fies atingiu **733 mil novos financiamentos em 2014** e caiu para **menos de 300 mil contratos anuais no triênio 2015–2017**, após as restrições impostas pelo MEC no fim de 2014. O gasto do programa havia saltado de R$ 1,1 bilhão (2010) para R$ 13,7 bilhões (2014).

**[FONTE]** A restrição foi a **Portaria Normativa MEC nº 21, de 26 de dezembro de 2014**, que passou a exigir, entre outros critérios, **média mínima de 450 pontos no Enem e nota diferente de zero na redação**, alterando as condições **antes do prazo de solicitação para 2015.1**.

> **[FATO] Portanto, 2018 NÃO é o primeiro período tratado.** O choque dominante sobre o Fies é de **dezembro de 2014**, com efeito a partir da coorte de 2015 — e é **maior** que o de 2018 (queda de ~60% no fluxo de novos contratos, contra a contração incremental de 2018).

Isto é confirmado nos nossos próprios dados. **[FATO]** Share agregado de ingressantes com Fies, cursos **privados presenciais**:

| Ano do Censo | Ingressantes | **% com Fies** | % com ProUni |
|---|---|---|---|
| 2015 | 1.723.604 | **15,98** | 8,34 |
| 2016 | 1.638.293 | **10,76** | 8,57 |
| 2017 | 1.650.614 | **9,06** | 7,98 |
| 2018 | 1.554.594 | **4,76** | 8,18 |
| 2019 | 1.514.506 | **4,39** | 7,70 |

Há **duas quedas grandes**, não uma: 2015→2016 (−33%) e 2017→2018 (−47%). O período que o desenho trataria como "pré-reforma" (2015–2017) é ele próprio um período de contração acelerada da política.

### 2.3 Houve antecipação em 2017? Houve transição gradual?

**[FATO] Sim para as duas perguntas, e é isso que compromete o desenho.** Medindo a exposição de cada curso em 2015 e acompanhando o share efetivo:

| Quartil de exposição em 2015 | 2015 | 2016 | 2017 | 2018 | 2019 |
|---|---|---|---|---|---|
| Q1 (baixo) | 0,000 | 0,037 | 0,040 | 0,021 | 0,026 |
| Q2 | 0,047 | 0,069 | 0,068 | 0,033 | 0,027 |
| Q3 | 0,142 | 0,116 | 0,097 | 0,050 | 0,043 |
| **Q4 (alto)** | **0,365** | **0,220** | **0,174** | **0,106** | **0,097** |

> **[FATO] No quartil mais exposto, 71,5% de toda a queda de 2015→2019 já havia ocorrido até 2017** — isto é, **antes** da reforma. A Lei 13.530/2017 responde por menos de um terço da contração observada.

Além disso, a tabela mostra **forte reversão à média**: o Q1 sai de 0,000 e *sobe* para 0,037–0,040; o Q4 cai de 0,365 para 0,174 **antes de qualquer reforma**. Uma exposição definida por quartis de um único ano gera pré-tendência mecânica por construção.

### 2.4 Cronologia

| Data | Ato | Conteúdo | Efeito sobre coortes |
|---|---|---|---|
| **26/12/2014** | **Portaria Normativa MEC nº 21/2014** | Enem ≥ 450 + redação ≠ 0; restrição de vagas e de aditamentos | **Coorte 2015 em diante** — choque dominante |
| 2015–2017 | Contingenciamento orçamentário e novas portarias normativas | Fluxo anual cai de 733 mil (2014) para < 300 mil | Coortes 2015–2017 |
| **25/05/2017** | **Decreto nº 9.057/2017** | Desregulamenta o EAD: polos criados pela própria IES; credenciamento EAD **sem** exigência de oferta presencial prévia | **Coorte 2017 em diante** — ver §15 |
| 06/09/2017 | MP nº 785/2017 | Antecipa o desenho do "Novo Fies"; convertida na Lei 13.530 | Antecipação de expectativas em 2017.2 |
| **07/12/2017** | **Lei nº 13.530/2017** (DOU 08/12/2017) | Novo Fies: juro real zero, pagamento por renda, FG-Fies, adesão obrigatória com aporte indexado à **evasão** da IES | **Coorte 2018 em diante** |
| 2020 | Pandemia de COVID-19 | Choque geral sobre trajetórias | **Ano-calendário ≥ 2020** — trunca horizontes |

**Fontes:** [Lei 13.530/2017 — Planalto](https://www.planalto.gov.br/ccivil_03/_Ato2015-2018/2017/Lei/L13530.htm) · [Lei 13.530/2017 — texto original, Câmara](https://www2.camara.leg.br/legin/fed/lei/2017/lei-13530-7-dezembro-2017-785887-publicacaooriginal-154436-pl.html) · [Sanção da lei — Senado Notícias](https://www12.senado.leg.br/noticias/materias/2017/12/08/lei-que-reformula-o-fies-e-sancionada-com-vetos-nesta-sexta-feira) · [Portaria Normativa MEC nº 21/2014 (compilada)](https://sisfiesportal.mec.gov.br/arquivos/portaria_normativa_21_26122014_compilada_050115.pdf) · [Portaria Normativa nº 21/2014 — FNDE](https://www.fnde.gov.br/index.php/acesso-a-informacao/institucional/legislacao/item/6188-portaria-normativa-n%C2%BA21,-de-26-de-dezembro-2014) · [Decreto nº 9.057/2017 — Planalto](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/decreto/d9057.htm) · [Decreto nº 9.057/2017 — Imprensa Nacional](https://www.in.gov.br/materia/-/asset_publisher/Kujrw0TZC2Mb/content/id/20238603/do1-2017-05-26-decreto-n-9-057-de-25-de-maio-de-2017-20238503) · [MEC — atualização da regulamentação de EaD](https://portal.mec.gov.br/busca-geral/212-noticias/educacao-superior-1690610854/50451-mec-atualiza-regulamentacao-de-ead-e-amplia-a-oferta-de-cursos) · [IPEA Radar 58 — "A reestruturação do Fies"](https://www.ipea.gov.br/portal/images/stories/PDFs/radar/181219_radar_58_art6.pdf) · [MEC — perguntas frequentes Fies](https://www.gov.br/mec/pt-br/acesso-a-informacao/perguntas-frequentes/fundo-de-financiamento-estudantil-fies)

---

## 3. Cronologia — leitura para o desenho

Três consequências diretas:

1. **A janela pré-tratamento não existe em estado limpo.** Toda coorte observável (2015+) já está sob o regime restritivo pós-PN 21/2014.
2. **Há dois choques adicionais colados ao de 2018**: o Decreto do EAD (maio/2017) e a COVID (2020).
3. **O aporte ao FG-Fies é função da evasão da própria IES.** Isso cria retroalimentação direta entre tratamento e desfecho: instituições mais expostas passam, a partir de 2018, a ter **incentivo financeiro explícito** para reduzir a evasão medida. Ver §15.3.

---

## 4. Dados disponíveis — nada novo foi baixado

**[FATO]** Inventário verificado antes de qualquer construção:

| Arquivo | Conteúdo | Serve para |
|---|---|---|
| `data/processed/trajetorias_2015_2020.parquet` | 1.403.065 linhas · coortes 2015–2020 · `CUM_DESISTENCIA`, `QT_INGRESSANTE`, `IDADE_TRAJETORIA` | **outcome** |
| `data/processed/modalidade_pre_covid_2015_2019.parquet` | 183.226 curso-anos · **já contém `QT_ING`, `QT_ING_FIES`, `QT_ING_PROUNII`, `QT_ING_PROUNIP`** | **exposição** |
| `data/interim/censo_cursos_slim_{2015..2019}.parquet` | Censos slim, 43 colunas | conferência |

> **[FATO] A auditoria completa foi feita com os arquivos já em disco. Nenhum download foi necessário, e nenhum foi feito.** A tabela de exposição do Fies já existia dentro do painel construído para a auditoria do COVID.

### 4.1 Uma limitação estrutural do Censo slim

**[FATO]** No Censo slim (filtro `TP_DIMENSAO ∈ {1,3}`), **toda linha de EAD tem `QT_ING` nulo** — nos cinco anos, sem exceção:

| Ano | Linhas dim. 1 (presencial) | `QT_ING` nulo | Linhas dim. 3 (EAD) | `QT_ING` nulo |
|---|---|---|---|---|
| 2015 | 32.397 | 0 | 1.476 | **1.476 (100%)** |
| 2019 | 36.178 | 0 | 4.531 | **4.531 (100%)** |

Os ingressantes de EAD estão nas linhas de **dimensão 2** (replicadas por município de oferta), descartadas na extração slim. **Consequência: `share_fies` só é computável para cursos presenciais.** Isso não é um defeito para este desenho — o Fies do período é essencialmente presencial — mas define a população antes de qualquer escolha metodológica.

---

## 5. Unidade observacional

**Escolha: `curso × coorte de ingresso`, com o desfecho medido em horizonte fixo τ.**

Isto responde diretamente ao problema **age-period-cohort** que derrubou o desenho COVID (§10 da auditoria anterior). Ao fixar τ, **todas as coortes comparadas estão exatamente na mesma idade de trajetória**, e a variação restante é entre coortes — que é a dimensão do tratamento. Não há confusão entre amadurecimento da coorte e tempo de calendário.

Tabela construída: `data/processed/painel_fies_curso_coorte.parquet` (**[FATO]** 442.416 linhas · 22.276 cursos), por [src/constroi_painel_fies.py](../src/constroi_painel_fies.py). Os arquivos preexistentes não foram alterados.

---

## 6. Outcome

**Construído a partir das contagens, não de `TDA`:**

```
desist_acum(τ) = 100 × CUM_DESISTENCIA / (QT_INGRESSANTE − CUM_FALECIDO)
```

`TDA` foi descartada pela mesma razão registrada na auditoria metodológica: é uma taxa já normalizada pelo Inep, cuja definição mistura horizontes. A construção acima é explícita e comparável entre coortes na mesma idade τ.

### 6.1 Qual horizonte τ é utilizável — e a restrição que a COVID impõe

Como `ano_calendário = coorte + τ`, e a COVID contamina `ano_calendário ≥ 2020`:

| τ | Coortes pré-reforma limpas | Coortes **pós-reforma** limpas | Leads | Utilizável? |
|---|---|---|---|---|
| **0** | 2015, 2016, 2017 | **2018, 2019** | 2 | **sim** |
| **1** | 2015, 2016, 2017 | **2018** | 2 | **sim** |
| 2 | 2015, 2016, 2017 | **nenhuma** | 2 | **não** |
| 3 | 2015, 2016 | **nenhuma** | 1 | **não** |

> **[FATO] Para τ ≥ 2 não existe nenhuma coorte pós-reforma livre de COVID.** A coorte 2018 atinge τ=2 no ano-calendário 2020.

Isso elimina os horizontes substantivamente mais interessantes. A desistência acumulada até τ=3 — a que melhor caracteriza abandono definitivo — é **inobservável** para qualquer coorte tratada sem contaminação pela pandemia.

**Horizonte recomendado: τ = 1** (desistência acumulada até o fim do segundo ano). Justificativa: (a) τ=0 mede apenas o ano de ingresso e é mecanicamente estreito; (b) τ=1 preserva uma coorte pós-reforma limpa (2018); (c) τ≥2 não preserva nenhuma. **[FATO]** Cobertura em τ=1, painel fechado nas 4 coortes: **15.246 cursos**, 60.984 linhas.

---

## 7. Construção de `share_fies`

```
share_fies = QT_ING_FIES / QT_ING     (somente quando QT_ING > 0)
```

**[DICIONÁRIO]** `QT_ING_FIES` = número de ingressantes do ano que têm financiamento do Fies. Unidade: pessoas. Denominador natural: `QT_ING`, ingressantes do mesmo curso no mesmo ano. É medida de **fluxo de ingressantes**, não de estoque de matriculados — compatível com a unidade curso × coorte.

### 7.1 Auditoria da variável

**[FATO]**

| Verificação | Resultado |
|---|---|
| `QT_ING_FIES > QT_ING` (impossível) | **0 linhas**, nos 5 anos |
| `share_fies > 1` | **0 linhas** |
| `QT_ING_FIES` nulo | exatamente as linhas de EAD (§4.1) |
| `QT_ING == 0` (denominador inválido), privado presencial | 10,4% a 12,9% dos curso-anos |
| `QT_ING_FIES == 0` em categorias 1 e 2 (federal/estadual) | **0 ingressantes com Fies em todos os anos** — como esperado |

**[FATO]** Distribuição de `share_fies`, privado presencial, cursos com `QT_ING > 0`:

| Ano | n | média | p50 | p75 | p90 | p99 | **% em zero** |
|---|---|---|---|---|---|---|---|
| 2015 | 18.982 | 0,133 | 0,076 | 0,202 | 0,351 | 0,711 | **28,6** |
| 2016 | 19.897 | 0,106 | 0,055 | 0,150 | 0,290 | 0,652 | **30,9** |
| 2017 | 20.936 | 0,093 | 0,041 | 0,124 | 0,254 | 0,661 | **33,6** |
| 2018 | 22.214 | 0,052 | 0,000 | 0,056 | 0,154 | 0,517 | **50,5** |
| 2019 | 22.716 | 0,049 | 0,000 | 0,039 | 0,140 | 0,639 | **58,8** |

A variável é **limpa**: limitada a [0,1], sem valores impossíveis, sem inconsistência com o denominador.

### 7.2 Em que nível o Fies é utilizável?

**[FATO]** Correlação de `share_fies` do mesmo curso entre anos:

| | 2015 | 2016 | 2017 | 2018 | 2019 |
|---|---|---|---|---|---|
| 2015 | 1,000 | 0,530 | 0,398 | 0,373 | 0,271 |
| 2016 | 0,530 | 1,000 | 0,561 | 0,498 | 0,431 |
| 2017 | 0,398 | 0,561 | 1,000 | 0,550 | 0,441 |

A correlação ano a ano no **nível do curso é apenas moderada (0,40–0,56)**. `share_fies` de um único ano é uma medida ruidosa da exposição estrutural do curso.

| Nível | Utilizável? | Observação |
|---|---|---|
| **A. Curso** | **Sim, mas só como média plurianual** | Ano único é ruidoso e gera lead mecânico (§11.2) |
| **B. IES** | **Sim** | Mais estável; custo: perde variação intra-IES, que é a mais defensável |
| **C. IES × área CINE** | **Sim — melhor compromisso** | Estável e preserva comparação dentro da instituição |
| D. Curso-ano | **Não** | É o próprio tratamento se movendo; não é exposição predeterminada |

---

## 8. Exposição predeterminada

Comparação das candidatas (**[FATO]**):

| Definição | Correlação com `exp_2015` | Problema |
|---|---|---|
| **A.** `share_fies` 2015 | — | **Gera lead mecânico decisivo** (§11.2): t = −5,2 (τ=0) e −5,8 (τ=1) |
| **B.** média 2015–2016 | alta | Já incorpora a contração de 2016 |
| **C.** média 2015–2017 | 0,817 (Pearson) · 0,839 (Spearman) | **Menos ruidosa**, mas medida *durante* a rampa do tratamento |
| **D.** nível IES (2015–17) | — | Estável; intervalos de confiança muito largos (§11.2) |
| **E.** nível IES × área (2015–17) | — | Construída na tabela; não testada isoladamente nesta auditoria |

**Recomendação: contínua, média 2015–2017, no nível curso (com variante IES × área para robustez).** Tratamento **contínuo** é preferível a quartis, e por uma razão empírica e não estética: **[FATO]** a discretização em quartis introduz reversão à média severa — o Q1 sai de `share = 0,000` em 2015 e sobe para 0,037 em 2016 sem nenhuma mudança de política (§2.3).

> **Ressalva que não se resolve com os dados atuais:** nenhuma dessas definições é predeterminada em relação ao **choque dominante**, que é o de dezembro de 2014. O Censo mais antigo em disco é o de 2015, já posterior à Portaria Normativa 21/2014. Uma exposição genuinamente pré-choque exigiria os Censos de **2013–2014**. Ver §19.

---

## 9. População

**Recomendada: cursos presenciais de IES privadas (`TP_CATEGORIA_ADMINISTRATIVA ∈ {4,5}`), com painel fechado nas coortes usadas.**

**[FATO]** Justificativa quantitativa — Fies por categoria administrativa (share agregado, %):

| Categoria | 2015 | 2016 | 2017 | 2018 | 2019 | Cursos com Fies > 0 (2017) |
|---|---|---|---|---|---|---|
| 1 — pública federal | **0,00** | 0,00 | 0,00 | 0,00 | 0,00 | **0** |
| 2 — pública estadual | **0,00** | 0,00 | 0,00 | 0,00 | 0,00 | **0** |
| 3 — pública municipal | 2,83 | 1,75 | 2,66 | 1,03 | 0,62 | 118 |
| **4 — privada com fins lucrativos** | **19,73** | 12,09 | 9,71 | 4,88 | 4,54 | **7.164** |
| **5 — privada sem fins lucrativos** | **12,09** | 9,20 | 8,31 | 4,56 | 4,11 | **6.748** |
| 7 — especial | 9,84 | 6,07 | 2,85 | 1,43 | 1,32 | 27 |

As públicas federais e estaduais têm **exatamente zero** ingressantes com Fies — não são contrafactual, são população fora do universo da política. Excluí-las não é maximizar comparabilidade em detrimento de N: é definir corretamente o universo.

| Restrição | Decisão | Motivo |
|---|---|---|
| Somente privadas (4, 5) | **Sim** | Únicas com Fies |
| Excluir públicas | **Sim** | Exposição estruturalmente nula |
| Somente presencial | **Sim, forçado** | `QT_ING` nulo em EAD (§4.1) |
| Painel fechado de cursos | **Sim** | §13 |
| Cursos com `QT_ING = 0` | **Excluir** | Denominador inválido (10–13%) |
| Categorias 3 e 7 | **Excluir** | 145 cursos com Fies; ruído |

---

## 10. Desenho candidato

```
Y_{c,k} = α_c + λ_k + Σ_{j ≠ ref} δ_j · ExposiçãoFies^pré_c · 1[k = j] + ε_{c,k}
```

- `c` = curso · `k` = coorte de ingresso · `Y` = desistência acumulada até τ **fixo**
- `α_c` = efeito fixo de curso · `λ_k` = efeito fixo de coorte
- Exposição **contínua**, medida no pré (2015–2017), **invariante no tempo**
- Ponderação por população em risco · **cluster por `CO_IES`**

**Estimando, em português:** *a mudança diferencial na desistência acumulada até o horizonte τ, entre a coorte `j` e a coorte de referência, associada a um aumento de 1 ponto na proporção de ingressantes financiados pelo Fies antes da reforma, dentro do mesmo curso.*

Como a exposição é uma proporção em [0,1], um coeficiente δ é o efeito de ir de **0% a 100%** de financiamento — magnitude não observada na prática. **Toda leitura substantiva abaixo é convertida para o contraste interquartílico realista Q4−Q1 ≈ 0,27.**

**O que esta especificação NÃO resolve, e é preciso dizer:** ela testa uma quebra em 2018 **supondo** que 2015–2017 seja um período de tratamento constante. A §2.3 mostra que não é. O termo `POS_REFORMA` mede o **último terço** de uma contração contínua, não um degrau.

---

## 11. Pré-tendências

### 11.1 Leitura descritiva

**[FATO]** Desistência acumulada (%), ponderada, por quartil de exposição (média 2015–2017) × coorte:

**τ = 1** (coortes 2015–2018, painel fechado, 15.246 cursos)

| Quartil | 2015 | 2016 | 2017 | **2018 (pós)** |
|---|---|---|---|---|
| Q1 (exp. 0,010) | 28,226 | 27,008 | 28,579 | 29,729 |
| Q2 (0,057) | 28,129 | 29,991 | 30,603 | 31,068 |
| Q3 (0,122) | 28,065 | 31,806 | 32,288 | 33,205 |
| Q4 (0,279) | 27,054 | 29,949 | 30,117 | 30,896 |
| **Gap Q4 − Q1** | **−1,173** | **+2,941** | **+1,538** | **+1,167** |

**τ = 0** (coortes 2015–2019, 14.171 cursos)

| **Gap Q4 − Q1** | 2015 | 2016 | 2017 | **2018** | **2019** |
|---|---|---|---|---|---|
| | **−0,424** | **+1,964** | **+1,937** | **+1,601** | **+3,678** |

Dois problemas visíveis a olho nu:

1. **O salto ocorre em 2015→2016** (+4,1 p.p. em τ=1; +2,4 p.p. em τ=0) — **dois anos antes da reforma**.
2. **No ano da reforma o gap ENCOLHE**, não cresce: 1,538 → 1,167 (τ=1) e 1,937 → 1,601 (τ=0).

E um terceiro, menos visível: **a relação não é monotônica na exposição.** O Q3 tem desistência mais alta que o Q4 em todas as coortes. Não há dose-resposta.

### 11.2 Regressão de leads (efeito fixo de curso + de coorte, cluster por IES)

**[FATO]** Referência = coorte 2017 (última pré-reforma). Coeficientes em p.p. por unidade de exposição.

| τ | Exposição | Lead 2015 | Lead 2016 | Pós 2018 | Pós 2019 | Clusters |
|---|---|---|---|---|---|---|
| 0 | média 15–17 | −3,693 (3,82) | −2,858 (2,05) | **+0,853** (2,13) | +4,847 (3,39) | 1.628 |
| 0 | **2015 apenas** | **−17,249 (3,33) · t = −5,18** | −1,418 (1,43) | −2,707 (1,52) | +9,839 (2,39) | 1.606 |
| 0 | IES 15–17 | −1,518 (5,48) | −2,394 (2,82) | +2,366 (2,92) | +6,974 (5,09) | 1.628 |
| 1 | média 15–17 | −5,684 (3,92) | +1,788 (2,51) | **+1,712** (2,45) | — | 1.688 |
| 1 | **2015 apenas** | **−18,857 (3,27) · t = −5,77** | +0,537 (1,78) | −1,379 (1,72) | — | 1.664 |
| 1 | IES 15–17 | −1,737 (5,49) | +3,480 (3,58) | +2,959 (3,19) | — | 1.688 |

### 11.3 Teste conjunto dos leads — wild cluster bootstrap

**[FATO]** H₀: todos os leads nulos. Rademacher, nulo imposto, cluster por `CO_IES`, **B = 999**:

| τ | Exposição | Wald | **p** |
|---|---|---|---|
| 0 | média 15–17 | 2,079 | 0,3860 |
| 0 | **2015 apenas** | 28,374 | **0,0010** |
| 1 | média 15–17 | 3,661 | 0,2040 |
| 1 | **2015 apenas** | 36,216 | **0,0010** |

### 11.4 Magnitude substantiva — a leitura que decide

Aplicando a regra estabelecida no projeto (**não** ler p > 0,05 como paralelismo), convertendo para o contraste interquartílico realista **Q4 − Q1 = 0,269**:

| τ | Maior lead pré-2018 | **em p.p. (Q4−Q1)** | Coeficiente de 2018 | **em p.p. (Q4−Q1)** | **Razão lead/pós** |
|---|---|---|---|---|---|
| 0 | −3,693 | **−0,99** | +0,853 | **+0,23** | **4,3×** |
| 1 | −5,684 | **−1,53** | +1,712 | **+0,46** | **3,3×** |

> **O movimento pré-reforma é 3 a 4 vezes maior que o movimento no ano da reforma — e tem sinal oposto.**

Os p-valores altos da exposição plurianual (0,20 e 0,39) **não** indicam paralelismo: os IC95 dos leads são largos o bastante para acomodar pré-tendências muito maiores que a quebra. Em τ=1, o IC do lead de 2015 é **[−13,36; +1,99]**, cujo extremo inferior é **7,8 vezes** o coeficiente de 2018. E quando a exposição é medida com precisão suficiente para ter poder — a especificação de 2015 — o teste conjunto **rejeita o paralelismo a p = 0,001**.

Há apenas **2 leads disponíveis** em qualquer horizonte utilizável, o que impede por construção qualquer veredito de PASSA sob os critérios do projeto (que exigem ≥ 3).

---

## 12. Overlap

**[FATO]**

| Métrica | Resultado | Comparação com o desenho EAD (encerrado) |
|---|---|---|
| Cursos privados presenciais no painel | 29.582 | — |
| IES distintas | 2.591 | — |
| Cursos com exposição estritamente positiva (2017) | 66,4% | — |
| Massa em zero (2017) | 33,6% | grupo de comparação natural, bem povoado |
| Suporte na faixa intermediária | p50 = 0,041 · p75 = 0,124 · p90 = 0,254 | contínuo, sem buracos |

O suporte comum é **genuinamente bom**: a exposição é contínua, com massa em toda a distribuição e um grupo de exposição zero grande e bem definido. **O problema de suporte que inviabilizou o braço EAD não reaparece.**

Ressalva: a **não-monotonicidade** documentada em §11.1 (Q3 > Q4 na desistência) indica que a exposição não ordena o desfecho de forma limpa — não é um problema de overlap, mas contamina a interpretação de dose-resposta.

---

## 13. Composição

**[FATO]** Cursos privados presenciais, tomando 2015 como base:

| Ano | Cursos | Novos vs. 2015 | % novos | Sobreviventes de 2015 |
|---|---|---|---|---|
| 2016 | 22.678 | 1.689 | 7,4% | 96,4% |
| 2017 | 23.363 | 3.457 | 14,8% | 91,4% |
| **2018** | 24.792 | 5.630 | **22,7%** | 88,0% |
| 2019 | 25.740 | 7.408 | **28,8%** | 84,2% |

**[FATO]** Mudança de atributo entre 2015 e 2019, entre os 18.332 cursos presentes nos dois anos:

| Atributo | Mudaram | % |
|---|---|---|
| `CO_CINE_AREA_GERAL` | 0 | 0,0 |
| `CO_IES` | 152 | 0,8 |
| **`TP_CATEGORIA_ADMINISTRATIVA`** | **1.923** | **10,5** |
| **`TP_ORGANIZACAO_ACADEMICA`** | **2.469** | **13,5** |

**[FATO]** E — o achado que mais preocupa — o porte cai **diferencialmente por exposição**. Ingressantes presenciais médios por IES, variação 2017→2019:

| Quartil de exposição ao Fies | Variação 2017→2019 |
|---|---|
| Q1 | −3,8% |
| Q2 | −5,4% |
| Q3 | −6,1% |
| **Q4** | **−9,3%** |

A renovação de 22,7% em 2018 fica na faixa de ALERTA (15–35%) — bem melhor que os 75–81% do braço EAD. Mas o encolhimento diferencial significa que **a composição dos ingressantes muda mais nos cursos tratados**, o que é seleção correlacionada ao tratamento: quem ainda se matricula num curso que perdeu o Fies não é quem se matriculava antes.

---

## 14. Clustering

**[FATO]** Na amostra de estimação (τ=1, painel fechado, 4 coortes):

| Métrica | Valor | Limiar do projeto |
|---|---|---|
| IES distintas (clusters) | **1.688** | — |
| N efetivo de IES (Kish, ponderado por população em risco) | **103,6** | ≥ 40 → PASSA |
| N efetivo ponderado por ingressantes com Fies | **132,4** | — |
| N efetivo no quartil mais fraco (Q2) | **44,7** | ≥ 40 |
| Concentração: top-1 IES no total de Fies | 2,2%–6,0% | ≤ 20% |
| IES que concentram 50% do Fies | **75 a 105** | — |

> **Comparação direta com o desenho encerrado: o braço EAD tinha 12 a 16 IES efetivas e 4 a 6 IES concentrando 50% dos ingressantes. Aqui são 104–132 IES efetivas e 75–105 IES concentrando 50% do Fies.**

**Este é o gate em que o desenho do Fies é estruturalmente superior, e por uma ordem de magnitude.** A inferência tem poder real, o wild cluster bootstrap é confiável, e nenhuma instituição isolada move o resultado.

---

## 15. Políticas simultâneas e confundimento

### 15.1 ProUni — não confunde

**[FATO]** O share de ingressantes com ProUni é **estável** durante todo o período: 8,34% (2015) · 8,57% · 7,98% · 8,18% · 7,70% (2019). Não houve choque contemporâneo no ProUni.

**[FATO]** A correlação entre exposição ao Fies e ao ProUni no nível da IES é **0,242 (Pearson) / 0,453 (Spearman)** — suficientemente distinta para servir de **placebo** (§16).

### 15.2 A desregulamentação do EAD — confunde, e seriamente

**[FONTE]** O **Decreto nº 9.057, de 25/05/2017** permitiu que as IES criassem polos de EAD por conta própria e que se credenciassem em EAD **sem** oferta presencial prévia — seis meses antes da Lei do Novo Fies.

**[FATO]** O efeito nos nossos dados é enorme. Cursos EAD por IES privada, média:

| Quartil de exposição ao Fies | 2015 | 2017 | 2019 | Crescimento 2017→2019 |
|---|---|---|---|---|
| Q1 | 0,18 | 0,30 | 0,78 | +160% |
| Q2 | 0,59 | 0,80 | 2,40 | +200% |
| Q3 | 0,86 | 1,48 | 3,11 | +110% |
| Q4 | 0,59 | 0,92 | 2,23 | +142% |

**Por que isto é fatal e não apenas incômodo:** o canal do EAD e o canal do Fies operam sobre **a mesma margem** — a acessibilidade financeira do ensino privado. Um estudante que perde o Fies e migra para um curso EAD mais barato aparece nos nossos dados como **desistência do curso presencial**. A expansão do EAD é grande em todos os quartis, o que impede tratá-la como choque comum absorvido pelo efeito fixo de coorte: ela é grande **e** temporalmente colada à reforma.

### 15.3 O FG-Fies retroalimenta o desfecho

**[FONTE]** A Lei 13.530/2017 condiciona o aporte da IES ao FG-Fies a percentuais de **10% a 25%** dos encargos educacionais nos anos 2 a 5, **em função da evasão e da inadimplência da própria instituição**.

**[HIPÓTESE, com base direta no texto legal]** Isto cria, a partir de 2018, incentivo financeiro explícito para que as IES mais expostas ao Fies **reduzam a evasão medida** — por retenção genuína ou por gestão do registro administrativo. O desfecho passa a ser, em parte, um objeto que o tratado tem interesse em mover. Qualquer β estimado mistura efeito comportamental do estudante com resposta institucional ao próprio desenho da política.

### 15.4 COVID

Trunca os horizontes conforme §6.1. Não é confundimento no sentido clássico — é perda de janela observacional.

---

## 16. Placebos propostos

**Não executados nesta auditoria**, por decisão explícita: gates estruturais falharam (§17), e testes caros não devem ser rodados antes disso.

| Placebo | Construção | O que derrubaria |
|---|---|---|
| **P1 — falso corte em 2016** | `POS = 1[k ≥ 2016]`, usando só 2015–2017 | Se der "efeito", a quebra não é de 2018 |
| **P2 — falso corte em 2017** | `POS = 1[k ≥ 2017]`, só coortes pré | Idem, e testa antecipação |
| **P3 — outcome placebo** | conclusão acumulada em τ fixo (`conclui_acum`, já na tabela) | Efeito no que a política não deveria mover |
| **P4 — exposição ao ProUni** | mesma regressão com `prouni_pre` | ProUni não sofreu reforma em 2018 (§15.1); efeito ⇒ artefato |
| **P5 — leave-one-IES-out** | excluir cada um dos 10 maiores grupos | Dependência de um punhado de firmas |
| **P6 — públicas como falso tratado** | atribuir exposição sintética a cat. 1 e 2 | Exposição real é zero; efeito ⇒ tendência espúria |

**[FATO]** P1 e P2 já têm resposta parcial e desfavorável: a §11.1 mostra que o salto do gap Q4−Q1 ocorre em **2015→2016**, exatamente onde P1 procuraria.

---

## 17. Gates F1–F8

| Gate | Critério | Situação | Evidência decisiva |
|---|---|---|---|
| **F1** — choque/política bem definido | Data e conteúdo precisos; o corte é o primeiro período tratado | 🟡 **ALERTA** | Lei 13.530/2017 é precisa e datada, **mas 2018 não é o primeiro período tratado**: o choque dominante é a PN 21/2014 (733 mil → < 300 mil contratos), e **71,5% da contração no quartil mais exposto ocorreu até 2017** |
| **F2** — exposição predeterminada mensurável | Medida antes do choque, estável, sem contaminação | 🟡 **ALERTA** | `share_fies` é limpa (0 valores impossíveis) e mensurável, mas: ano único gera lead mecânico (t = −5,8); a média 15–17 é medida **durante** a rampa; **não existe Censo pré-2015 em disco** |
| **F3** — overlap | Suporte comum em toda a distribuição | 🟢 **PASSA** | Exposição contínua, 66% dos cursos com exposição > 0, massa em zero de 34% bem povoada, sem buracos de suporte |
| **F4** — pré-tendências | Leads pequenos vs. quebra; teste conjunto; ≥ 3 leads | 🔴 **FALHA** | Leads **3,3× a 4,3×** o coeficiente de 2018, **com sinal oposto**; salto do gap em **2015→2016**; exposição de 2015 rejeita paralelismo a **p = 0,001**; apenas **2 leads** disponíveis |
| **F5** — estabilidade de composição | ≤ 15% novos (PASSA), 15–35% (ALERTA) | 🟡 **ALERTA** | 22,7% de cursos novos em 2018; categoria administrativa muda em 10,5% e organização em 13,5%; **porte cai −9,3% no Q4 contra −3,8% no Q1** |
| **F6** — número efetivo de clusters | ≥ 40 IES efetivas em cada braço | 🟢 **PASSA** | **1.688 clusters**, N efetivo **103,6–132,4**, pior quartil 44,7, top-1 IES ≤ 6% |
| **F7** — ausência de política simultânea fatal | Quebra atribuível à reforma | 🔴 **FALHA** | **Decreto 9.057/2017** (EAD) seis meses antes, mesmo canal de acessibilidade, cursos EAD por IES **+110% a +200%** entre 2017 e 2019; **FG-Fies indexa aporte à evasão da própria IES**, retroalimentando o desfecho |
| **F8** — sensibilidade | Sinal e magnitude preservados nos placebos | ⚪ **NÃO AVALIADO** | Depende de estimativas que não devem existir enquanto F4 e F7 falham (§16) |

---

## 18. Veredito

> # **CAUSAL NÃO IDENTIFICADO**
>
> — para o desenho **"reforma de 2018 × exposição pré ao Fies"**, tal como especificado.

**Dois gates estruturais falham, e por razões independentes:**

1. **F4 (pré-tendências).** O movimento diferencial na desistência entre cursos mais e menos expostos ocorre **em 2015→2016**, dois anos antes da reforma, e é **3 a 4 vezes maior** que o movimento observado em 2018 — que, além de menor, tem **sinal oposto**. Não há degrau em 2018 que se destaque do que já vinha acontecendo.

2. **F7 (política simultânea).** O Decreto 9.057/2017 desregulamentou o EAD seis meses antes da reforma, atuando sobre **a mesma margem de acessibilidade financeira e sobre a mesma população**; a migração presencial → EAD é registrada como desistência no nosso desfecho. Somado a isso, o FG-Fies **indexa o aporte da instituição à sua própria evasão**, tornando o desfecho um objeto que o tratado tem incentivo direto para mover.

**A causa raiz de F4, e ela é diagnosticável:** o desenho trata 2018 como o início do tratamento, quando o tratamento começou em **dezembro de 2014**. O período "pré" de 2015–2017 é, ele próprio, período tratado — em que **71,5% da contração do Fies já se realizou**. Não é um problema de estimador nem de especificação: é o corte temporal estar no lugar errado.

### 18.1 O que este veredito NÃO significa

- **Não significa que o Fies seja um candidato ruim.** Ao contrário: nos dois gates que mataram o desenho COVID de forma irrecuperável — **overlap (F3) e número efetivo de clusters (F6)** — o Fies **passa com folga**. São 104–132 IES efetivas contra 12–16 do EAD; nenhuma instituição isolada domina. A unidade curso × coorte com horizonte fixo **resolve** o problema age-period-cohort de §10 da auditoria anterior.
- **Não significa irrecuperável.** Diferente do C6 do desenho COVID — que era uma propriedade do mercado brasileiro de EAD e não do desenho — as falhas aqui são **de recorte temporal**, e recorte temporal é escolha nossa.
- **Não autoriza estimar nada.** A regra de §19 da auditoria anterior se aplica por analogia: enquanto F4 estiver em falha, nenhum coeficiente de efeito deve ser reportado, nem como preliminar.

### 18.2 O candidato que os dados de fato sugerem

O choque de **dezembro de 2014** é melhor que o de 2018 em quase todas as dimensões auditadas:

| Dimensão | Choque de 2018 | **Choque de 2014/2015** |
|---|---|---|
| Magnitude | contração incremental (~29% do total) | **queda de 733 mil → < 300 mil contratos (~60%)** |
| Nitidez | lei de dezembro, aplicação semestral, migração voluntária | **portaria de 26/12/2014, regra dura (Enem ≥ 450), aplicação imediata em 2015.1** |
| Política simultânea | Decreto do EAD a 6 meses; FG-Fies retroalimenta evasão | **nenhuma equivalente identificada nesta auditoria** |
| Horizonte livre de COVID | τ ≤ 1 apenas | **τ até 4 para a coorte 2015** |
| Coortes pós disponíveis | 1 a 2 | **5 (2015–2019)** |
| Exposição predeterminada | indisponível (Censo começa em 2015) | exigiria Censos 2013–2014 |

**[HIPÓTESE]** É plausível que a pergunta correta seja *"a restrição de acesso ao Fies em 2015 alterou diferencialmente a desistência em cursos mais dependentes do financiamento?"* — e que ela seja identificável onde a de 2018 não é.

---

## 19. Próximo passo mínimo

> ### Adquirir os Censos da Educação Superior **2013 e 2014** (cadastro de cursos, camada slim) e os indicadores de trajetória das coortes **2013 e 2014**, e refazer **exclusivamente** o teste de pré-tendências — agora com o corte em 2015.

**Necessidade demonstrada, não presumida.** Esta auditoria foi feita inteiramente com os arquivos já em disco, e o que ela estabeleceu é exatamente o que falta:

1. **[FATO]** Não existe nenhum Censo anterior a 2015 no projeto — logo **nenhuma exposição ao Fies predeterminada em relação ao choque dominante** pode ser construída hoje.
2. **[FATO]** Com exposição medida em 2015 (já pós-choque), o teste conjunto de leads rejeita paralelismo a **p = 0,001** — o sintoma esperado de exposição medida durante o tratamento.
3. **[FATO]** Com apenas 2 leads disponíveis, nenhum veredito de PASSA é atingível por construção. Coortes 2013–2014 elevariam os leads para 4.

**Escopo e custo:**

- **Censos 2013 e 2014:** ~20–25 MB de ZIP, mesma política de disco já validada em [src/baixa_censos_pre_covid.py](../src/baixa_censos_pre_covid.py) — download → conferir MD5 → extrair só o cadastro de cursos → filtrar `TP_DIMENSAO ∈ {1,3}` → Parquet slim → **apagar CSV e ZIP**. Residual ≈ 2 MB.
- **Verificação prévia obrigatória:** confirmar que `QT_ING_FIES` existe e tem a mesma definição em 2013–2014, e que a taxonomia **CINE** está harmonizada retroativamente (foi confirmada para 2015 em §3.1 do relatório do gate anterior; 2013–2014 usam OCDE e podem exigir conversão).
- **Trajetórias 2013 e 2014:** confirmar disponibilidade na série do Inep antes de baixar.

**O que NÃO fazer neste passo:** não estimar DiD, não estimar efeito, não implementar dose-resposta. **Apenas os leads, e o julgamento dos gates F1–F4 com o corte em 2015.**

**Critério de continuação:** se as pré-tendências passarem com o corte em 2015, o desenho passa a **CAUSAL VIÁVEL COM RESTRIÇÕES** — com F7 ainda exigindo tratamento explícito do Decreto do EAD para as coortes de 2017 em diante, e com F5 declarado em alerta permanente. Se falharem também ali, **encerrar a linha do Fies** e consolidar o trabalho descritivo.

---

## Anexo — o que esta auditoria fez e não fez

**[FATO] Não fez:** nenhum download · nenhum modelo causal final · nenhuma estimativa de efeito · nenhum commit · nenhuma alteração em arquivo preexistente.

**Criado:**

| Arquivo | Papel |
|---|---|
| [src/constroi_painel_fies.py](../src/constroi_painel_fies.py) | tabela analítica curso × coorte com horizonte fixo |
| `data/processed/painel_fies_curso_coorte.parquet` | 442.416 linhas · 22.276 cursos · 7,5 MB |
| `docs/auditoria_causal_fies.md` | este documento |

Os coeficientes pós-2018 exibidos na §11.2 são **referência de magnitude para o julgamento do gate F4**, rotulados como tal, e **não são estimativas de efeito causal**.
