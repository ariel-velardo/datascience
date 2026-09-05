# Auditoria de Viabilidade Causal — COVID-19 e desistência no ensino superior

**Projeto:** Big Data Analytics da trajetória no ensino superior brasileiro
**Base:** `data/processed/trajetorias_2015_2020.parquet` — coortes de ingresso 2015–2020, 1.403.065 linhas
**Data:** 2026-09-04
**Status:** auditoria de identificação. **Nenhum modelo causal foi implementado. Nenhuma estimativa causal é reportada. Nenhum commit foi feito.**

Documento irmão: [auditoria_multicoorte.md](auditoria_multicoorte.md) — aquisição, auditoria por coorte e construção do painel.
Antecedente: [auditoria_metodologica.md](auditoria_metodologica.md) — auditoria estrutural da coorte 2015.
**Reavaliação posterior:** [gate_pre_tendencias.md](gate_pre_tendencias.md) — execução do gate C3 com tratamento predeterminado (ver §21).

---

> ## ⚠ NOTA DE VERSÃO — leia antes de usar este documento
>
> **O corpo deste documento (§1–§20) é a auditoria de 2026-09-04 e está preservado como foi escrito**, inclusive nos pontos em que a reavaliação posterior o corrigiu. Nada foi reescrito retroativamente.
>
> Em **§21** está a **reavaliação com tratamento predeterminado (pré-COVID)**, executada depois, com os Censos da Educação Superior 2015–2019. Ela fecha a ressalva registrada em §11.6 e §18/C1, e altera a classificação de dois gates.
>
> **Onde §21 contradiz §1–§20, vale §21.** Os pontos afetados estão marcados no texto com `↪ ver §21`.

---

Convenção:

- **[FATO]** — verificado programaticamente nesta auditoria, com a contagem exata reportada.
- **[DICIONÁRIO]** — transcrito da documentação oficial do Inep.
- **[HIPÓTESE]** — interpretação minha, ainda não comprovada.

**Aviso de linguagem.** Todos os números descritivos deste documento são **associações e diferenças de composição**. Nenhum deve ser lido como efeito. Os termos "efeito", "impacto" e "causa" aparecem aqui apenas na descrição de estimandos hipotéticos e de suas condições de identificação.

---

## 1. Pergunta causal

> **Qual foi o impacto diferencial do choque pandêmico de COVID-19 sobre a desistência anual em cursos de graduação que dependiam de ensino presencial antes de 2020, comparativamente a cursos que já operavam na modalidade a distância antes de 2020?**

Três precisões deliberadas em relação à formulação inicial do projeto:

1. **"choque pandêmico"**, não "a pandemia" — o tratamento é a interrupção do ensino presencial e o conjunto de perturbações simultâneas de 2020, não o vírus.
2. **"que dependiam de ensino presencial antes de 2020"** — a modalidade precisa ser **predeterminada**. Modalidade medida depois do choque é desfecho, não tratamento.
3. **"impacto diferencial ... comparativamente a"** — o desenho nunca poderá estimar o efeito total da pandemia sobre a evasão, porque não existe grupo não exposto. Ver §13.

---

## 2. Estimando

Notação: `c` = curso, `k` = coorte de ingresso, `t` = ano-calendário, `τ = t − k` = idade da trajetória, `g(c) ∈ {P, E}` = modalidade predeterminada (presencial / EAD).
`Y_{c,k,t}` = risco anual de desistência.

O estimando defensável é um **ATT diferencial em diferenças**:

```
θ_τ = E[ Y^{covid} − Y^{sem covid} | g = P, τ ]  −  E[ Y^{covid} − Y^{sem covid} | g = E, τ ]
```

Em português: *o quanto o risco anual de desistência dos cursos presencialmente dependentes mudou com o choque de 2020, além do quanto mudou o risco dos cursos que já eram a distância, na mesma idade de trajetória.*

**O que este estimando NÃO é:**

| Não é | Por quê |
|---|---|
| "Efeito da pandemia sobre a evasão no Brasil" | O grupo de comparação também foi tratado (§13). |
| "Efeito do EAD sobre a evasão" | O contraste EAD × presencial em nível é confundido por composição de alunos, invisível nesta base ([auditoria_metodologica.md](auditoria_metodologica.md) §10.1). |
| "Efeito sobre estudantes" | A unidade é o curso. Qualquer leitura individual é falácia ecológica. |
| "Efeito sobre a evasão do sistema" | A base mede desistência **do curso**; transferência interna conta como desistência. |

O estimando é indexado por τ porque o risco de desistência varia fortemente com a idade da trajetória — **[FATO]** o hazard agregado é 15,4% em τ=0, 21,7% em τ=1, 18,1% em τ=2, e a população em risco cai de 100% para 30,9% em τ=4. Um estimando não indexado por τ não teria significado.

---

## 3. Dados necessários

| Bloco | Situação | Papel |
|---|---|---|
| Indicadores de Trajetória, coortes 2015–2020 | ✅ **em disco, auditado** | desfecho e estrutura do painel |
| Modalidade **predeterminada** por curso (pré-2020) | ❌ **ausente** | tratamento — ver §6 e §15 |
| Categoria administrativa / organização acadêmica pré-2020 | ❌ ausente | estratificação e overlap |
| Seletividade, turno, financiamento, demografia de ingresso | ❌ ausente | robustez e comparabilidade |
| Severidade local da pandemia (municipal) | ❌ ausente | desenho alternativo (§8.5) |

**O bloco ausente crítico é o tratamento.** É a razão pela qual o veredito de §19 não é positivo hoje.

---

## 4. Unidade observacional

**Unidade primária:** `curso × coorte × ano de referência` — a linha do painel. 1.403.065 observações.

**Unidade de tratamento:** `curso` (`CO_CURSO`). A modalidade é atributo do curso, não da observação.

**Unidade de agrupamento para inferência:** `IES` (`CO_IES`). Ver §16.

**Trajetória:** o par `(coorte, curso)`. **[FATO]** 190.488 trajetórias; 43.861 cursos distintos; 2.798 IES.

Um mesmo `CO_CURSO` aparece em até seis coortes: **[FATO]** 21.338 cursos nas seis, 5.758 em uma só. Isso é uma vantagem — permite efeitos fixos de curso que sobrevivem a mudanças de coorte — e um risco: o painel de cursos é desbalanceado, e a entrada/saída de cursos é endógena (§12.3).

---

## 5. Outcome recomendado (Etapa 3)

### 5.1 A população em risco, derivada da identidade contábil

A base não publica a população em risco. Ela foi **derivada** da identidade contábil e **verificada**, não arbitrada:

```
EM_RISCO_INICIO(t) = QT_PERMANENCIA(t−1)          (em τ=0: QT_INGRESSANTE)

QT_PERMANENCIA(t) = EM_RISCO_INICIO(t) − QT_DESISTENCIA(t)
                    − QT_CONCLUINTE(t) − QT_FALECIDO(t)
```

**[FATO]** A segunda igualdade fecha em **1.403.065 / 1.403.065 linhas (100,000%)**, em aritmética inteira.

```
hazard(t) = 100 × QT_DESISTENCIA(t) / (EM_RISCO_INICIO(t) − QT_FALECIDO(t))
```

O desconto de falecidos no denominador reproduz a convenção do próprio Inep, que trata falecidos como censura — **[FATO]** as cinco taxas publicadas batem com denominador "vivo" em 100% das linhas nas seis coortes, e com denominador bruto em apenas ~97%.

### 5.2 Comparação dos quatro candidatos

| Candidato | Denominador | Comportamento em τ | Adequação a DiD |
|---|---|---|---|
| **`TDA`** (acumulada) | coorte inteira | monotônico crescente por construção | **Inadequado** |
| **`QT_DESISTENCIA`** (contagem) | — | escala com o porte do curso | Inadequado como desfecho; útil como peso |
| **`TADA`** (anual publicada) | **coorte inteira** | decai mecanicamente | **Inadequado** |
| **`hazard` condicional** | **população ainda em risco** | aproximadamente estável | **Recomendado** |

**`TDA` — confirmada a suspeita.** Como acumulada, `TDA(t) ≥ TDA(t−1)` sempre — **[FATO]** 0 violações em todo o painel. O valor pós-2020 contém aritmeticamente todo o valor pré-2020. **[FATO]** `corr(TDA(τ=1), TDA(τ=4))` = 0,729 · 0,733 · 0,742 · 0,733 · 0,744 · 0,707 nas coortes 2015…2020. Um DiD sobre `TDA` estimaria um degrau numa série que não pode descer, e o coeficiente pós-choque herdaria mecanicamente a diferença pré-choque de nível. **A expectativa registrada no enunciado da tarefa está correta e agora está verificada.**

**`TADA` — inadequada, e por um motivo mais sutil e mais grave do que o de `TDA`.** O denominador de `TADA` é a coorte inteira, não quem ainda está em risco. Logo `TADA` cai mecanicamente à medida que o estoque se esvazia:

**[FATO]** médias ponderadas, todas as coortes agregadas:

| τ | `TADA` | `hazard` | % da coorte ainda em risco |
|---|---|---|---|
| 0 | 15,408 | 15,408 | 100,00 |
| 1 | 18,216 | 21,747 | 83,77 |
| 2 | 11,326 | 18,147 | 62,41 |
| 3 | 7,377 | 16,067 | 45,92 |
| 4 | 4,762 | 15,392 | 30,93 |
| 5 | 2,899 | 16,368 | 17,71 |
| 7 | 1,359 | 25,791 | 5,27 |
| 9 | 0,527 | 29,128 | 1,81 |

`TADA` cai 29× entre τ=0 e τ=9; o risco condicional **sobe**. `TADA` mede sobretudo o esvaziamento do estoque, não o comportamento.

Isso é fatal para um DiD entre modalidades porque **os dois grupos esvaziam o estoque em ritmos diferentes** — o EAD muito mais rápido. O resultado é uma inversão de sinal:

**[FATO]** Em **21 das 45 células `(τ, ano)` do painel, o sinal da diferença presencial − EAD é oposto entre `TADA` e `hazard`.** Exemplo (τ=4, ano 2019, coorte 2015):

| Métrica | Presencial | EAD | Diferença |
|---|---|---|---|
| `TADA` | 6,008 | 4,704 | **+1,304** (EAD "desiste menos") |
| `hazard` | 15,331 | 22,963 | **−7,632** (EAD desiste muito mais) |

A leitura por `TADA` é um artefato: em τ=4 o EAD já perdeu tanta gente que suas desistências, divididas pela coorte original, parecem pequenas. **Um DiD sobre `TADA` pode produzir um coeficiente com o sinal errado por construção.**

### 5.3 Recomendação

| Papel | Outcome |
|---|---|
| **Principal** | `hazard(t) = 100 × QT_DESISTENCIA(t) / (EM_RISCO_INICIO(t) − QT_FALECIDO(t))` |
| Transformação | Considerar `log(hazard)` ou complementar log-log; o desfecho é uma proporção |
| Ponderação | Por `EM_RISCO_INICIO` (a rigor, o denominador do próprio hazard) |
| Robustez | `TADA` — reportar **explicitamente como artefato de denominador**, para exibir a inversão de sinal |
| Nunca | `TDA` como desfecho de DiD |

**Limitação operacional do hazard [FATO]:** o hazard é indefinido onde a população em risco se exaure. Isso ocorre em 0,00% das linhas em τ=0, 1,05% em τ=1, 2,93% em τ=2, 6,43% em τ=3, 12,49% em τ=4, e 20,6%–64,8% em τ=5..9. **Isso limita o desenho principal a τ ≤ 4** — e τ ≤ 4 é também o intervalo com suporte pré-2020 (§11). As duas restrições coincidem, o que é conveniente, mas a ausência de τ ≥ 5 precisa ser declarada: o desenho não fala sobre desistência tardia.

---

## 6. Tratamento recomendado (Etapa 4)

### 6.1 O achado decisivo: o tratamento não existe na base atual

> `↪ ver §21` — confirmado que o tratamento não está na base de trajetória, **mas** a reavaliação mostrou que `TP_MODALIDADE_ENSINO` nunca muda dentro de um `CO_CURSO`: o snapshot de 2024 não estava errado sobre modalidade. O ganho real dos Censos foi na estratificação, não no tratamento.

**[FATO] Os seis arquivos de trajetória carregam o MESMO snapshot de 2024.**

Todos os seis são publicados com ano final de análise 2024, e o dicionário declara que as covariáveis são registradas "no último ano de análise" **[DICIONÁRIO]**. A verificação empírica confirma: dos **38.103 cursos que aparecem em duas ou mais coortes**, o número em que a modalidade diverge entre arquivos é

| Atributo | Cursos com valor divergente entre coortes |
|---|---|
| `TP_MODALIDADE_ENSINO` | **0** |
| `TP_CATEGORIA_ADMINISTRATIVA` | **0** |
| `TP_ORGANIZACAO_ACADEMICA` | **0** |
| `CO_IES` | **0** |

Zero divergências em 38.103 cursos. **Não é que os arquivos concordem: é que são o mesmo retrato.** Consequência direta:

> **Nenhuma das três alternativas de tratamento (A, B ou C) pode ser construída a partir dos arquivos de trajetória.** A modalidade disponível é de 2024 — quatro anos **depois** do choque. Usá-la é medir o tratamento depois do desfecho.

Isso reproduz, em escala multi-coorte, o achado de [auditoria_metodologica.md](auditoria_metodologica.md) §4.5, e o agrava: antes era um problema de uma coorte; agora é uma propriedade de todo o painel.

### 6.2 Avaliação das três alternativas

| | Definição | Depende de | Avaliação |
|---|---|---|---|
| **A** | Modalidade no ano de ingresso da coorte `k` | Censo de cada ano 2015…2019 | Predeterminada em relação ao ingresso e ao choque, para `k ≤ 2019`. **Mas a variável muda de data entre coortes** — para a coorte 2015 é medida em 2015, para a 2019 em 2019. Se a modalidade de um curso mudou nesse intervalo, coortes diferentes recebem rótulos diferentes para o mesmo curso, e o "tratamento" passa a variar por um motivo alheio ao choque. Para `k = 2020`, é medida **durante** o choque: inutilizável. |
| **B** | Modalidade observada em **2019**, fixa para todas as coortes | Censo 2019 | **Recomendada.** Uma única data, comum a todas as coortes, imediatamente anterior ao choque. O tratamento não deriva entre coortes. Requer que o curso exista no Censo 2019 — exclui cursos criados em 2020, o que é desejável (§14). Para a coorte 2015 a variável é medida 4 anos após o ingresso, o que é irrelevante: o que precisa ser pré-choque é o tratamento, não o momento do ingresso. |
| **C** | Restringir a cursos com modalidade **estável** em 2015–2019 | Censos 2015–2019 | **Recomendada como restrição de população, não como definição de tratamento.** Remove os cursos que migraram de modalidade no período pré-choque, para os quais o rótulo é ambíguo e cuja migração é plausivelmente endógena ao próprio desempenho. |

### 6.3 Recomendação

> **Tratamento = `TP_MODALIDADE_ENSINO` no Censo de 2019 (definição B), aplicado à população restrita a cursos com modalidade estável em 2015–2019 (restrição C), com a definição A como análise de sensibilidade.**

Justificativa metodológica: o estimando de §2 é sobre **exposição ao choque**. A variável de exposição deve, portanto, ser datada imediatamente **antes** do choque e ser a **mesma** para todas as coortes — caso contrário, variação no rótulo do tratamento se confunde com variação temporal. B satisfaz as duas condições; A satisfaz a primeira mas não a segunda; C limpa os casos ambíguos.

Consequência operacional: **isto exige os Censos históricos.** Ver §15. Enquanto eles não forem incorporados, **o GATE C1 está em FALHA e nenhuma estimativa deve ser produzida.**

### 6.4 A "presencialidade" é binária demais

**[HIPÓTESE, e uma limitação de primeira ordem]** `TP_MODALIDADE_ENSINO ∈ {1, 2}` classifica a oferta administrativa, não o grau real de dependência de atividade presencial. Um curso presencial de Medicina e um de Administração noturno têm exposições ao fechamento físico completamente distintas, e recebem o mesmo rótulo. Simetricamente, "EAD" abrange desenhos com e sem encontros presenciais obrigatórios. Isso é uma violação de **consistência** do SUTVA (§13) e limita a interpretação do estimando mesmo se tudo o mais funcionasse.

---

## 7. População principal

A população deve ser escolhida por comparabilidade, não por N.

**População principal proposta:**

1. Cursos com modalidade **estável e observada** em 2015–2019 (restrição C);
2. dentro de **IES que ofertavam as duas modalidades** em todo o período pré-choque;
3. dentro de **áreas CINE com suporte nas duas modalidades** em todas as coortes pré-2020;
4. coortes de ingresso **2015–2019** (a de 2020 fica fora do desenho principal — §14);
5. τ ≤ 4 (limite do suporte pré-2020 e da definição do hazard);
6. cursos com `EM_RISCO_INICIO ≥ 20` no ano observado, como sensibilidade.

**[FATO] Dimensão dessa população, apurada com o snapshot atual** (portanto uma aproximação superior, já que a restrição C ainda não pôde ser aplicada):

| Critério | Coorte 2015 | Coorte 2019 |
|---|---|---|
| IES que ofertam ambas as modalidades | 142 | 337 |
| IES que ofertam ambas em **todas** as coortes 2015–2019 | 107 | 107 |
| Cursos nessas IES | 6.661 | 8.048 |
| — presenciais | 5.670 | 5.826 |
| — EAD | 991 | 2.222 |
| Ingressantes | 1.354.974 | 1.983.635 |
| Estratos `IES × CO_CINE_ROTULO` com ambas as modalidades | 598 | 1.706 |

**107 IES** — 4,5% das 2.401 IES do país — é a base de comparação honesta. Ela cobre 1,35–1,98 milhão de ingressantes, ou seja, N não é o problema. **Validade externa é**: as conclusões valeriam para as instituições que operam as duas modalidades simultaneamente, que são grandes, majoritariamente privadas e não representativas do sistema.

**Áreas CINE a excluir do desenho principal [FATO]:** área 05 (Ciências naturais, matemática e estatística) tem **1 curso EAD** na coorte 2015 e 29 na de 2019; área 08 (Agricultura) tem **2** e 21. Não há comparação possível nessas áreas nas coortes iniciais. Áreas com suporte razoável nas seis coortes: **04** (mín. 473 cursos EAD), **01** (387), **06** (75), **07** (75), **10** (39), **09** (32).

**Categoria administrativa [FATO]:** a categoria 3 (pública municipal) tem **zero** ingressantes EAD na coorte 2019. Federais e estaduais têm 16.699 e 16.031 ingressantes EAD contra 346.262 e 158.385 presenciais — razões de 1:21 e 1:10. Na prática, a comparação entre modalidades **só existe dentro do setor privado**, e sobretudo na categoria 4 (privada com fins lucrativos), que concentra **85,26%** dos ingressantes EAD da coorte 2019.

---

## 8. DiD candidato (Etapa 5, desenhos 1 a 4)

### 8.1 Desenho 1 — DiD com múltiplas coortes

| Item | Especificação |
|---|---|
| **Unidade observacional** | `curso × coorte × ano`, restrita a τ ≤ 4 |
| **Tratamento** | `Presencial_c` = 1 se modalidade em 2019 = presencial (§6.3) |
| **Grupo de comparação** | Cursos EAD em 2019, na mesma IES e área CINE |
| **Período pré** | anos-calendário 2015–2019 |
| **Período pós** | anos-calendário 2020–2024 |
| **Outcome** | `hazard(t)` (§5.3) |
| **Efeitos fixos** | curso (`α_c`); idade de trajetória **por grupo** (`γ_τ^{g}`); ano-calendário (`λ_t`) |
| **Controles** | nenhum contemporâneo (seriam pós-tratamento). Apenas predeterminados, e preferencialmente como estratificação |
| **Clustering** | `CO_IES`, com wild cluster bootstrap (§16) |
| **Estimando** | `θ` de §2, agregado em τ |
| **Ponderação** | `EM_RISCO_INICIO` |

```
hazard_{c,k,t} = α_c + γ_τ^{g(c)} + λ_t + β · Presencial_c · Post_t + ε_{c,k,t}
```

**Pressupostos, em ordem de fragilidade:**

1. **Tendências paralelas condicionais** — na ausência do choque, o gap presencial−EAD do hazard, dentro de idade de trajetória, teria seguido a mesma trajetória. **Testável apenas na sua parte não linear** (§10). → **falha empiricamente** (§11).
2. **Tratamento predeterminado** — falha hoje (§6.1), recuperável via Censo.
3. **Composição estável dos braços** — falha (§12.3).
4. **Ausência de tendência linear diferencial no perfil por idade** — não testável (§10.4).
5. SUTVA — violada em vários canais (§13).

**Nota sobre estimadores.** Como o tratamento é uma característica fixa do curso e o choque é comum a todos em 2020, este é um DiD de **timing único**. Os problemas de ponderação negativa de Goodman-Bacon e os estimadores de Callaway–Sant'Anna / Sun–Abraham, próprios de adoção escalonada, **não se aplicam aqui**. O problema deste desenho não é o estimador: é a identificação.

### 8.2 Desenho 2 — Event study em torno de 2020

Ver §11. É o desenho preferido, porque expõe o padrão pré-choque em vez de escondê-lo num único coeficiente.

### 8.3 Desenho 3 — Triple difference

Um DDD só ajuda se a terceira dimensão for plausivelmente exógena ao choque **e** modificar a exposição de forma conhecida. Avaliação dos candidatos disponíveis:

| Terceira dimensão | Avaliação |
|---|---|
| Área CINE com alta dependência de atividade prática (saúde, engenharias, laboratórios) × áreas sem | **O mais defensável.** A intensidade de uso de espaço físico é predeterminada e conhecida. Reduz a dependência da comparação EAD, porque o contraste passa a ser *entre cursos presenciais*. **Mas [FATO]** as áreas 05 e 08 têm suporte EAD quase nulo, então o braço EAD do DDD fica indefinido justamente nas áreas mais "práticas". Viável apenas em versão restrita, comparando áreas 09 (saúde, 270 cursos EAD em 2019) e 07 (engenharias, 348) contra 04 (negócios, 1.645). |
| Categoria administrativa (pública × privada) | **Desaconselhado.** **[FATO]** o EAD público é residual — 16.699 ingressantes federais contra 1.396.740 privados com fins lucrativos na coorte 2019. O DDD não teria suporte no braço público. |
| Região / severidade local | **Impossível neste corte.** **[FATO]** 100% dos cursos EAD têm geografia nula, por construção da base. |
| Organização acadêmica | Endógena ao desempenho institucional (status de universidade é conquistado). Condicionar nela pode induzir viés de colisor. |

**Veredito:** o DDD por intensidade prática da área é o único candidato defensável, e ele **não resolve** nenhum dos gates que falham. Deve entrar como heterogeneidade dentro do desenho principal, não como estratégia de identificação alternativa.

### 8.4 Desenho 4 — Comparação estratificada / pareada (robustez)

**Exato dentro de `IES × CO_CINE_ROTULO`** — o estrato mais fino com suporte real. **[FATO]** 598 estratos na coorte 2015, 1.706 na de 2019.

Isto absorve o confundimento institucional e de rótulo de curso, que é a maior parte do confundimento **observável**. Não absorve a composição socioeconômica dos alunos, que é o confundidor dominante e permanece invisível.

**Propensity score / IPW: desaconselho ativamente.** **[FATO]** com 4 a 6 IES concentrando metade dos ingressantes EAD e áreas inteiras sem suporte, os pesos explodem, e o resultado teria aparência de rigor sem substância. Se o overlap for tratado, que seja por **restrição explícita de população** (§7), que é honesta e auditável, não por reponderação.

### 8.5 Desenho 5 — alternativa que não usa o EAD como comparação (não solicitado, mas recomendado)

Vale registrar, porque muda a avaliação de viabilidade do projeto como um todo:

> **Dose-resposta dentro do universo presencial:** unidade `curso presencial × coorte × ano`; tratamento contínuo = severidade local da pandemia (mortalidade por COVID, ou rigor/duração do fechamento de atividades presenciais) no município ou UF do curso; efeitos fixos de curso, de τ, e de ano; comparação entre municípios mais e menos atingidos.

Vantagens: dispensa o grupo EAD e portanto todos os problemas de overlap, concentração e recomposição (§12); tem variação contínua e muitas unidades; o tratamento é predeterminado em relação ao curso. Custo: **[FATO]** exclui integralmente o EAD (sem geografia), exige dados externos de severidade, e a severidade local não é exógena (correlaciona com densidade urbana, renda e estrutura produtiva) — exigiria seu próprio conjunto de gates.

**Não desenvolvo este desenho aqui**, porque está fora do escopo pedido. Registro-o porque, se os gates de §18 falharem como a evidência atual sugere, ele é a via mais promissora para preservar uma pergunta causal neste projeto.

---

## 9. Event study candidato

**Especificação — versão estratificada por idade de trajetória (recomendada):**

Para cada τ ∈ {0, 1, 2} separadamente:

```
hazard_{c,k,k+τ} = α_{IES(c) × área(c)} + Σ_{j ≠ j₀} δ_j · Presencial_c · 1[k = j]
                   + η_k + ε
```

onde `k` indexa a coorte (equivalentemente, o ano-calendário, já que dentro de τ fixo `t = k + τ`), `η_k` são efeitos de coorte comuns aos dois grupos, e `j₀` é a coorte de referência (a última pré-choque).

Os `δ_j` com `k + τ < 2020` são os **leads** — devem ser estatisticamente e economicamente nulos. Os `δ_j` com `k + τ ≥ 2020` são os **lags** — o efeito.

**Especificação alternativa — versão em painel:**

```
hazard_{c,k,t} = α_c + γ_τ^{g(c)} + λ_t + Σ_{j ≠ 2019} δ_j · Presencial_c · 1[t = j] + ε
```

Reporta uma trajetória em ano-calendário. É mais legível, mas mistura idades de trajetória diferentes em cada ano, e sofre da indeterminação linear de §10.4 de forma mais severa. **Recomendo a versão estratificada como principal e esta como ilustração visual.**

**Convenções obrigatórias:**

- ano-base: **2019** (último ano integralmente pré-choque);
- reportar os `δ_j` com IC de wild cluster bootstrap por IES;
- reportar quantos cursos e quantas IES contribuem para **cada** `δ_j`;
- eixo rotulado como **ano-calendário e τ simultaneamente**, nunca só "ano".

---

## 10. O problema age-period-cohort (Etapa 6)

Esta é a seção central da auditoria.

### 10.1 As três colinearidades exatas

**[FATO]** No painel construído, `NU_ANO_REFERENCIA = NU_ANO_INGRESSO + IDADE_TRAJETORIA` vale em 1.403.065 de 1.403.065 linhas. Daí decorrem três colinearidades **exatas, estruturais e não amostrais**:

| # | Onde | Colinearidade |
|---|---|---|
| **1** | Globalmente | `t ≡ k + τ`. Efeitos fixos de coorte, de idade e de ano-calendário **não podem ser incluídos simultaneamente**: o conjunto tem deficiência de posto exatamente 1. |
| **2** | Dentro de uma trajetória `(c, k)` | `τ` e `t` avançam 1 a 1. Com efeito fixo de trajetória, incluir `γ_τ` **e** `λ_t` deixa uma direção linear inidentificada. |
| **3** | Dentro de um estrato de τ fixo | `k ≡ t − τ`. **Coorte e ano-calendário são a mesma variável.** Efeitos de coorte e efeitos de período não podem ser separados dentro de τ. |

A colinearidade #3 é a mais consequente e a menos óbvia, e ela define o que o desenho realmente faz.

### 10.2 O que a estrutura do painel permite ver

**[FATO]** Em 2020, a exposição por coorte é:

| Coorte | τ em 2020 | Ano do curso |
|---|---|---|
| 2015 | 5 | 6º |
| 2016 | 4 | 5º |
| 2017 | 3 | 4º |
| 2018 | 2 | 3º |
| 2019 | 1 | 2º |
| 2020 | 0 | 1º |

Cada coorte encontra o choque numa idade de trajetória diferente. Isso é simultaneamente o **recurso** que separa período de idade — porque a mesma idade τ é vivida por coortes distintas em anos distintos — e a **armadilha**, porque dentro de cada τ a coorte é redundante com o ano.

### 10.3 Como distinguir os três mecanismos — e o que fica indistinguível

| Mecanismo | Como é isolado | Fica identificado? |
|---|---|---|
| **Amadurecimento natural da coorte** (idade da trajetória) | Efeitos fixos de τ, estimados com as coortes pré-2020 | **Sim**, na sua parte não linear |
| **Diferenças estruturais entre coortes** (composição de ingresso, tamanho, seleção) | Efeitos fixos de coorte `η_k`, ou efeitos fixos de curso quando o curso aparece em várias coortes | **Sim**, se comuns aos dois grupos |
| **Tendências de calendário** (mercado de trabalho, política, expansão do EAD) | Efeitos fixos de ano `λ_t`, comuns aos dois grupos | **Sim**, se comuns aos dois grupos |
| **Choque COVID (o objeto)** | Interação `Presencial × Post`, ou o conjunto de `δ_j` | **Sim, mas apenas até uma tendência linear** — ver §10.4 |

### 10.4 A colinearidade estrutural que resta — e o que ela custa

Este é o ponto que precisa ser dito com precisão, porque ele é o gate.

A indeterminação APC é **exclusivamente linear**: pode-se somar `δ·t` aos efeitos de período, subtrair `δ·τ` dos efeitos de idade e somar `δ·k` aos efeitos de coorte sem alterar nenhum valor ajustado. Segue-se:

**(a) Boa notícia.** `Post_t = 1[t ≥ 2020]` é uma função **não linear** de `t`. Um degrau não pertence ao espaço nulo da indeterminação APC. Portanto **o DiD não é automaticamente destruído pelo problema APC**. Esta é a resposta à pergunta central da tarefa, e ela é positiva.

**(b) Má notícia, e é decisiva.** A conclusão em (a) só vale se as componentes lineares específicas de grupo forem restringidas. Concretamente:

> Se o modelo permitir simultaneamente **perfis de idade específicos por grupo** (`γ_τ^P`, `γ_τ^E`), **efeitos de coorte específicos por grupo** (`η_k^P`, `η_k^E`) e **efeitos de período específicos por grupo** (`λ_t^P`, `λ_t^E`), então **toda a trajetória do event study é inidentificada até uma tendência linear específica de grupo** — e uma tendência linear específica de grupo é exatamente o que a hipótese de tendências paralelas proíbe.

Ou seja: das três dimensões, **no máximo duas podem ser específicas de grupo**. É preciso escolher, e a escolha é uma hipótese substantiva, não uma decisão técnica:

| Restrição imposta | Custo |
|---|---|
| Perfil de idade **comum** aos dois grupos | Contrafactual. **[FATO]** o perfil de hazard por τ difere em forma entre modalidades — em τ=4/2019 o hazard presencial é 15,3 e o EAD 23,0; em τ=1 os níveis são 17,1 e 22,7. Impor perfil comum atribui essa diferença de forma ao choque. **Inaceitável.** |
| Efeitos de coorte **comuns** aos dois grupos | **A escolha recomendada**, e ainda assim forte: assume que a recomposição do braço EAD entre as coortes 2015 e 2019 não alterou seu risco de desistência. **[FATO] 75,6% dos cursos EAD da coorte 2019 não estavam no braço EAD da coorte 2015.** A hipótese é implausível. |
| Efeitos de período comuns | Sem sentido: é o objeto de interesse. |

### 10.5 Especificação proposta

Explicitando a escolha de (b):

```
hazard_{c,k,t} = α_c                    # efeito fixo de curso
               + γ_τ^{g(c)}             # perfil de idade ESPECÍFICO por modalidade
               + λ_t                    # ano-calendário, COMUM
               + η_k                    # coorte, COMUM
               + Σ_{j≠2019} δ_j · Presencial_c · 1[t=j]
               + ε
```

com a normalização de que `γ_τ^P − γ_τ^E` não tem componente linear em τ.

**Essa normalização é o pressuposto de identificação, e ela não é testável.** Precisa aparecer no texto do relatório final, nesses termos, ao lado de qualquer coeficiente.

**Sobre efeitos fixos de IES:** `α_c` (curso) subsume `α_{IES}`. Efeitos fixos de IES sozinhos são insuficientes — **[FATO]** o ICC intra-IES é 0,36–0,50 (§Multi-coorte 5.5), ou seja metade a dois terços da variância é intra-IES. Use efeito fixo de curso; a IES entra como nível de clusterização (§16).

### 10.6 Existe um problema de identificação insolúvel?

**Sim, um, e ele é declarado aqui sem atenuação:**

> **A componente linear da diferença entre os perfis de desistência-por-idade dos cursos presenciais e dos cursos EAD não é separável da componente linear do efeito diferencial do choque.** Nenhum arranjo de efeitos fixos, nenhuma restrição de população e nenhum estimador resolve isso, porque a origem é a identidade `t = k + τ`, que é aritmética.

O que **é** testável é a parte não linear: se o gap presencial−EAD pula em 2020 e volta ao normal depois, isso não pode ser explicado por tendência linear. É por isso que o event study de §9, e não o DiD de coeficiente único, é o desenho a executar — e é por isso que a próxima seção é decisiva.

---

## 11. Pré-tendências (Etapa 7)

### 11.1 Quantos anos pré-2020 conseguimos observar

**[FATO]** Por idade de trajetória:

| τ | Coortes com observação **pré**-2020 | Coortes pós | Anos pré cobertos | Leads testáveis |
|---|---|---|---|---|
| 0 | 5 (2015–2019) | 1 (2020) | 2015–2019 | **4** |
| 1 | 4 (2015–2018) | 2 (2019–2020) | 2016–2019 | **3** |
| 2 | 3 (2015–2017) | 3 (2018–2020) | 2017–2019 | **2** |
| 3 | 2 (2015–2016) | 4 | 2018–2019 | 1 |
| 4 | 1 (2015) | 5 | 2019 | **0** |
| ≥5 | **0** | todas | — | **0** |

**Consequências:**

- **Não existe nenhum período pré-2020 para τ ≥ 5.** Metade do intervalo de idades do painel não tem contrafactual.
- Em **τ = 4 o teste de pré-tendências é impossível**: há uma única coorte pré-choque, logo zero leads.
- O teste só tem substância em **τ ∈ {0, 1, 2}**, com 4, 3 e 2 leads.
- Cada lead é contribuído por **uma única coorte**. Não há replicação: um lead é uma coorte.

### 11.2 O teste, executado

O gap `hazard(presencial) − hazard(EAD)`, ponderado por população em risco, por idade de trajetória e ano. **Este é o objeto que o DiD supõe estável no pré-choque.**

**[FATO] τ = 0 (ano de ingresso):**

| Ano | Coorte | Período | Presencial | EAD | **Gap** |
|---|---|---|---|---|---|
| 2015 | 2015 | PRÉ | 11,913 | 16,300 | **−4,387** |
| 2016 | 2016 | PRÉ | 13,372 | 23,364 | **−9,992** |
| 2017 | 2017 | PRÉ | 13,092 | 18,267 | **−5,175** |
| 2018 | 2018 | PRÉ | 12,908 | 21,315 | **−8,407** |
| 2019 | 2019 | PRÉ | 14,929 | 17,897 | **−2,968** |
| 2020 | 2020 | PÓS | 14,983 | 16,182 | −1,199 |

Amplitude do gap no pré-choque: **7,02 p.p.** Desvio-padrão: **2,92 p.p.**
Variação 2019 → 2020: **+1,77 p.p.** — ou seja, **o "efeito" é 0,6 desvio-padrão da própria oscilação pré-choque.**

**[FATO] τ = 1:**

| Ano | Coorte | Período | Presencial | EAD | **Gap** |
|---|---|---|---|---|---|
| 2016 | 2015 | PRÉ | 17,145 | 22,746 | **−5,601** |
| 2017 | 2016 | PRÉ | 17,358 | 25,565 | **−8,207** |
| 2018 | 2017 | PRÉ | 18,197 | 29,730 | **−11,533** |
| 2019 | 2018 | PRÉ | 18,702 | 29,507 | **−10,805** |
| 2020 | 2019 | PÓS | 18,417 | 28,467 | −10,050 |
| 2021 | 2020 | PÓS | 18,051 | 29,796 | −11,745 |

Amplitude pré: **5,93 p.p.** · dp **2,70 p.p.** · variação 2019→2020: **+0,76 p.p.**

**[FATO] τ = 2:**

| Ano | Coorte | Período | Presencial | EAD | **Gap** |
|---|---|---|---|---|---|
| 2017 | 2015 | PRÉ | 15,561 | 19,365 | **−3,804** |
| 2018 | 2016 | PRÉ | 16,568 | 22,737 | **−6,169** |
| 2019 | 2017 | PRÉ | 16,895 | 18,901 | **−2,006** |
| 2020 | 2018 | PÓS | 16,244 | 18,259 | −2,015 |
| 2021 | 2019 | PÓS | 14,908 | 20,022 | −5,114 |
| 2022 | 2020 | PÓS | 18,804 | 27,381 | −8,577 |

Amplitude pré: **4,16 p.p.** · dp **2,09 p.p.** · variação 2019→2020: **−0,01 p.p.**

### 11.3 A população restrita não resolve

Restringindo às **104 IES que ofertam ambas as modalidades em todas as seis coortes** — a comparação mais defensável disponível — **[FATO]** as pré-tendências **pioram**:

| τ | Amplitude do gap pré (geral) | Amplitude do gap pré (restrito) | dp restrito |
|---|---|---|---|
| 0 | 7,02 | **8,38** | 3,37 |
| 1 | 5,93 | **7,00** | 3,00 |
| 2 | 4,16 | 3,73 | 1,87 |
| 3 | 4,46 | 2,42 | 1,71 |

E o sinal do gap chega a inverter no grupo restrito — em τ=2, ano 2019, o gap é **+0,355** (presencial desistindo mais que EAD), contra **−3,379** no ano anterior. Uma oscilação de 3,7 p.p. entre dois anos consecutivos do período pré-choque.

### 11.4 Suporte comparável entre idades e dominância institucional

- **Suporte entre idades:** desigual e assimétrico. τ=0 tem 5 pontos pré; τ=4 tem 1; τ≥5 tem 0. Qualquer agregação em τ pondera implicitamente os leads de forma arbitrária. **Recomendação: nunca agregar em τ sem reportar τ por τ.**
- **Dominância institucional:** severa. **[FATO]** 4 a 6 IES concentram 50% dos ingressantes EAD em qualquer coorte; 12 a 20 concentram 80%. O braço de comparação inteiro é, na prática, uma dúzia de grupos educacionais. Uma mudança de política interna de **uma** dessas instituições move o gap agregado mais do que a pandemia plausivelmente moveria. **[HIPÓTESE]** É essa a explicação mais provável da oscilação de 7 p.p. observada no pré-choque.
- **Teste obrigatório antes de qualquer estimativa:** recalcular a série do gap excluindo, uma por vez, cada uma das 10 maiores IES EAD (*leave-one-institution-out*). Se a série pré-choque mudar materialmente, o braço de comparação não é um grupo, é um punhado de firmas.

### 11.5 Critérios objetivos para o teste

Sejam `δ_j` os coeficientes de lead do event study de §9, `σ_pré` o desvio-padrão dos gaps pré-choque, e `|θ̂|` a magnitude do efeito estimado.

| Veredito | Critérios (todos precisam valer) |
|---|---|
| **PASSA** | (i) `\|δ_j\| < 1,0` p.p. para todo lead; (ii) teste conjunto dos leads com `p > 0,10`; (iii) `σ_pré < \|θ̂\| / 3`; (iv) nenhum lead muda de sinal; (v) o resultado sobrevive ao *leave-one-institution-out* das 10 maiores IES EAD; (vi) ≥ 3 leads disponíveis. |
| **ALERTA** | (i) `\|δ_j\| < 2,0` p.p. para todo lead; (ii) `0,01 ≤ p ≤ 0,10`; (iii) `\|θ̂\|/3 ≤ σ_pré < \|θ̂\|`; (iv) ≥ 2 leads. → Estimar, mas **reportar como associação com interpretação causal explicitamente suspensa**, e apresentar o event study antes de qualquer número resumo. |
| **FALHA** | Qualquer lead com `\|δ_j\| ≥ 2,0` p.p.; **ou** `p < 0,01`; **ou** `σ_pré ≥ \|θ̂\|`; **ou** algum lead com sinal invertido; **ou** menos de 2 leads; **ou** sensibilidade ao *leave-one-institution-out*. |

### 11.6 Veredito das pré-tendências, com os dados atuais

> `↪ ver §21` — o teste foi refeito com tratamento predeterminado e com estimação formal (event study, wild cluster bootstrap). A ressalva registrada ao final desta subseção está **fechada**.

> ### **FALHA**, em τ=0, τ=1 e τ=2, por múltiplos critérios simultâneos.

| Critério | τ=0 | τ=1 | τ=2 |
|---|---|---|---|
| Algum lead ≥ 2,0 p.p. de oscilação | **sim** (7,0) | **sim** (5,9) | **sim** (4,2) |
| `σ_pré` vs. mudança 2019→2020 | 2,92 vs 1,77 → `σ_pré > \|θ̂\|` | 2,70 vs 0,76 → `σ_pré > \|θ̂\|` | 2,09 vs 0,01 → `σ_pré ≫ \|θ̂\|` |
| Sinal estável no pré | não | não | não (inverte no restrito) |

**A oscilação pré-choque do gap é maior do que a mudança observada em 2020, em todas as idades de trajetória testáveis.** Não há um degrau em 2020 que se destaque do ruído do período pré-choque.

**Ressalva honesta, e ela importa.** Este teste foi executado com a modalidade **do snapshot de 2024**, porque o tratamento predeterminado ainda não existe (§6.1). Parte da oscilação pode ser artefato de rotular como "EAD" cursos que só se tornaram EAD depois de 2019. **O teste precisa ser refeito com o tratamento de §6.3 antes de o GATE C3 ser encerrado.** Não considero provável que o resultado mude de sinal — a oscilação é grande demais e o braço EAD é concentrado demais — mas o teste atual não é definitivo, e apresentá-lo como definitivo seria tão incorreto quanto ignorá-lo.

---

## 12. Overlap e concentração (Etapa 8)

### 12.1 Contagens

**[FATO]** por coorte:

| Coorte | IES presencial | IES EAD | IES com **ambas** | Cursos pres. | Cursos EAD | % ingr. EAD |
|---|---|---|---|---|---|---|
| 2015 | 2.154 | 146 | 142 | 27.025 | 1.118 | 24,09 |
| 2016 | 2.181 | 157 | 153 | 27.951 | 1.291 | 28,28 |
| 2017 | 2.269 | 245 | 240 | 29.004 | 1.896 | 33,24 |
| 2018 | 2.333 | 298 | 291 | 30.117 | 2.770 | 40,02 |
| 2019 | 2.391 | 347 | 337 | 30.524 | 3.944 | 44,18 |
| 2020 | 2.312 | 409 | 382 | 29.602 | 5.246 | 52,84 |

Apenas **6,1% a 17,5%** das IES ofertam EAD. Quase todas as que ofertam EAD também ofertam presencial — o que é a boa notícia: o overlap dentro de IES existe.

### 12.2 Concentração

**[FATO]**

| Coorte | IES para 50% dos ingr. EAD | IES para 80% | Top-5 (%) | Top-10 (%) | Top-20 (%) |
|---|---|---|---|---|---|
| 2015 | **4** | 14 | 57,41 | 74,82 | 87,12 |
| 2016 | 4 | 12 | 61,12 | 76,51 | 88,12 |
| 2017 | 5 | 17 | 54,69 | 70,82 | 82,87 |
| 2018 | 5 | 17 | 52,74 | 69,25 | 82,30 |
| 2019 | **6** | 20 | 49,13 | 67,49 | 80,24 |
| 2020 | 5 | 20 | 50,14 | 68,60 | 80,67 |

**Número efetivo de clusters (IES) por braço** — medida de Kish `(Σw)²/Σw²` **[FATO]**:

| Coorte | Braço | IES nominais | **N efetivo (ponderado por ingressantes)** | N efetivo (por cursos) |
|---|---|---|---|---|
| 2015 | Presencial | 2.154 | 185,2 | 359,9 |
| 2015 | **EAD** | 146 | **11,7** | 63,7 |
| 2019 | Presencial | 2.391 | 180,4 | 428,0 |
| 2019 | **EAD** | 347 | **16,0** | 117,7 |
| 2020 | **EAD** | 409 | **15,8** | 135,8 |

> **O braço de comparação tem um número efetivo de instituições entre 12 e 16.** Este número, e não o de 347 IES ou 1,6 milhão de ingressantes, é o que governa a incerteza real da estimativa. Ver §16.

### 12.3 Estabilidade de composição

**[FATO]** Renovação dos braços, tomando a coorte 2015 como base:

| Coorte | EAD: % cursos novos | EAD: % ingressantes em cursos novos | Presencial: % cursos novos | Presencial: % ingr. novos |
|---|---|---|---|---|
| 2016 | 22,7 | 5,1 | 9,1 | 5,0 |
| 2017 | 45,6 | 17,8 | 14,8 | 10,3 |
| 2018 | 64,5 | 26,6 | 21,0 | 15,3 |
| 2019 | **75,6** | **35,1** | 25,2 | 20,1 |
| 2020 | **81,5** | **43,5** | 27,3 | 22,2 |

E os atributos médios do braço EAD mudam junto **[FATO]**:

| Coorte | Porte médio EAD | Porte médio presencial | % ingr. EAD em privada c/ fins lucrativos | % ingr. EAD em centro universitário |
|---|---|---|---|---|
| 2015 | 652,4 | 85,0 | 83,18 | 30,05 |
| 2019 | 415,3 | 67,8 | 85,26 | 37,09 |
| 2020 | 388,7 | 61,5 | 87,92 | 38,03 |

**Este é o achado mais problemático desta seção.** O braço de comparação não é o mesmo objeto ao longo do tempo: três quartos dos seus cursos são novos em 2019, e seu porte médio caiu 36%. Um DiD que compara "EAD em 2019" com "EAD em 2016" está comparando dois conjuntos amplamente distintos de cursos. **[FATO]** O braço presencial também se renova, mas a um terço da velocidade.

**Mitigação parcial:** restringir ao painel de cursos presentes nas seis coortes — **[FATO]** 21.338 cursos, dos quais **apenas 901 EAD**. Isso estabiliza a composição ao custo de reduzir o braço EAD a 901 cursos, majoritariamente de instituições antigas e grandes. Troca de um viés por outro; a comparabilidade melhora, a validade externa piora ainda mais.

### 12.4 Overlap por área CINE

**[FATO]** cursos EAD por área geral:

| Área CINE | 2015 | 2017 | 2019 | 2020 | Presencial 2019 |
|---|---|---|---|---|---|
| 01 Educação | 387 | 648 | 897 | 1.170 | 5.054 |
| 02 Artes e humanidades | 22 | 41 | 154 | 226 | 1.286 |
| 03 Ciências sociais, comunicação | 12 | 20 | 71 | 131 | 1.805 |
| 04 Negócios, administração, direito | 473 | 771 | 1.645 | 2.060 | 7.247 |
| **05 Ciências naturais, matemática** | **1** | **1** | 29 | 54 | 783 |
| 06 Computação e TIC | 75 | 111 | 319 | 464 | 1.805 |
| 07 Engenharia, produção, construção | 75 | 144 | 348 | 455 | 5.086 |
| **08 Agricultura, veterinária** | **2** | **6** | 21 | 22 | 1.121 |
| 09 Saúde e bem-estar | 32 | 79 | 270 | 396 | 5.566 |
| 10 Serviços | 39 | 75 | 190 | 268 | 771 |

**Áreas 05 e 08 não têm suporte utilizável** nas coortes iniciais e devem ser excluídas do desenho principal. **Áreas 02 e 03 são marginais** antes de 2017.

Nota importante: o crescimento do número de cursos EAD por área **não é boa notícia para o desenho** — ele significa que o suporte aparece exatamente no período pós-choque, isto é, o overlap melhora justamente onde não faz falta e é pior justamente no período pré-choque, onde as tendências paralelas precisam ser testadas.

### 12.5 Categoria administrativa e organização acadêmica

**[FATO]** coorte 2019, ingressantes:

| Categoria administrativa | Presencial | EAD | Razão |
|---|---|---|---|
| 1 Pública federal | 346.262 | 16.699 | 20,7 : 1 |
| 2 Pública estadual | 158.385 | 16.031 | 9,9 : 1 |
| 3 Pública municipal | 9.393 | **0** | sem overlap |
| 4 Privada c/ fins lucrativos | 1.017.314 | **1.396.740** | 0,73 : 1 |
| 5 Privada s/ fins lucrativos | 524.144 | 207.143 | 2,5 : 1 |
| 7 Especial | 14.280 | 1.506 | 9,5 : 1 |

**[FATO]** organização acadêmica, coorte 2019 (cursos): universidades 12.490 pres. / 1.705 EAD · centros universitários 8.020 / 1.931 · faculdades 8.457 / 287 · IF 1.504 / 19 · CEFET 53 / 2.

**Conclusão de overlap:** o suporte comum existe essencialmente em **um setor** (privado), **duas organizações acadêmicas** (universidade e centro universitário) e **cinco a seis áreas CINE**. Fora disso, a comparação não é ruim — ela é inexistente.

### 12.6 Uma população restrita oferece comparação mais defensável?

**Sim, e é a recomendação de §7.** Mas com duas ressalvas que precisam constar do relatório final:

1. **A restrição não resolve as pré-tendências** — **[FATO]** elas pioram no grupo restrito em τ=0 e τ=1 (§11.3).
2. **A restrição não resolve a concentração** — as 107 IES que qualificam incluem justamente os grandes grupos que dominam o EAD. Restringir a população **aumenta** a dominância dessas instituições, não a reduz.

Registro explicitamente, conforme instruído: **não maximizar N às custas de comparabilidade.** A recomendação vai na direção oposta — usar as 107 IES em vez das 2.401 — e ainda assim os gates falham.

---

## 13. SUTVA e contaminação (Etapa 9)

### 13.1 O EAD não é um grupo de controle

A pandemia atingiu os dois braços. Cursos EAD sofreram a mesma crise econômica, a mesma mortalidade, a mesma disrupção familiar e as mesmas mudanças de política de financiamento estudantil. O que os cursos EAD **não** sofreram, ou sofreram menos, foi a interrupção da atividade presencial.

**Consequência formal:** o estimando de §2 é uma **diferença de efeitos**, não um efeito. Se o choque aumentou a desistência em ambos os grupos em magnitudes semelhantes, `θ ≈ 0` — e isso **não** significa que a pandemia não afetou a evasão. Significa que ela afetou os dois grupos de forma parecida.

> **Frase obrigatória no relatório final:** *"Este desenho não estima o efeito da pandemia sobre a evasão. Estima, na melhor das hipóteses, a diferença entre o efeito sobre cursos presenciais e o efeito sobre cursos que já eram a distância. Um resultado nulo é compatível com um efeito grande e comum aos dois grupos."*

### 13.2 Canais de contaminação, avaliados

| Canal | Mecanismo | Direção esperada em `θ` | Gravidade |
|---|---|---|---|
| **Ensino remoto emergencial** | Cursos presenciais adotaram ensino remoto em 2020–2021. O "tratamento" não é "perder o ensino"; é "receber ensino remoto improvisado". | Ambígua — atenua ou amplifica | **Crítica.** Redefine o próprio tratamento. |
| **Migração de alunos entre modalidades** | Alunos que teriam ido ao presencial foram ao EAD. **[FATO]** ingressantes presenciais caem 12,1% de 2019 para 2020 enquanto os EAD sobem 24,5%. | Viés de composição em **ambos** os braços | **Crítica.** Violação direta de SUTVA por equilíbrio geral. |
| **Reclassificação de cursos** | Cursos presenciais reclassificados como EAD/híbridos após 2020 mudam de braço. | Contamina o tratamento | **Crítica** se o tratamento for de 2024 (§6.1); **resolvida** pela definição B de §6.3. |
| **Transferência interna contada como desistência** | Aluno que migra de curso dentro da IES conta como desistente. Grandes grupos EAD facilitam migração. | Superestima desistência, diferencialmente no EAD | Alta |
| **Políticas simultâneas** | Alterações em FIES/ProUni, prorrogações de matrícula, flexibilização regulatória do MEC — todas em 2020, e nenhuma neutra entre modalidades | Confunde-se integralmente com o choque | **Alta e irremediável.** Não há como separar COVID de política educacional de 2020. |
| **Crise econômica** | Renda e emprego caem em 2020; efeito sobre evasão de cursos pagos é direto | Confunde-se com o choque | Alta |
| **Mortalidade e saúde** | **[FATO]** falecidos são censurados corretamente pelo denominador da base, então o efeito mecânico está tratado. Efeitos indiretos (luto, doença, cuidado familiar) não. | Aumenta desistência em ambos | Média |
| **Seleção de ingresso** | Quem escolhe entrar em 2020 é diferente de quem entrou em 2019 | Ver §14 | **Crítica para a coorte 2020** |

### 13.3 Consistência (a outra metade do SUTVA)

"Presencial" não é um tratamento único. **[HIPÓTESE]** A intensidade da exposição varia por área, turno, porte da cidade e capacidade tecnológica da instituição — nada disso está na base. Estimar um `θ` único é estimar uma média sobre versões heterogêneas de um tratamento que não é bem definido. Ver §6.4.

---

## 14. Coorte 2020 (Etapa 10)

### 14.1 O problema

A coorte 2020 **escolheu ingressar durante o choque**. O tratamento e a seleção de entrada são simultâneos, e por isso a coorte 2020 não informa sobre o efeito do choque sobre trajetórias já iniciadas.

**[FATO] A magnitude da seleção de entrada é grande e é assimétrica entre os braços:**

| | Coorte 2019 | Coorte 2020 | Variação |
|---|---|---|---|
| Ingressantes presenciais | 2.069.778 | 1.820.226 | **−12,06%** |
| Ingressantes EAD | 1.638.119 | 2.039.222 | **+24,49%** |
| Total | 3.707.897 | 3.859.448 | +4,09% |
| Cursos presenciais | 30.524 | 29.602 | **−3,02%** (primeira queda da série) |
| Cursos EAD | 3.944 | 5.246 | +33,01% |

O braço presencial da coorte 2020 perdeu **um em cada oito** ingressantes em relação à coorte anterior, e esses alunos em boa parte apareceram do outro lado. **Os dois braços foram recompostos, em direções opostas, exatamente no ano do tratamento.** Isso é seleção de entrada em estado puro.

**[FATO]** Coerentemente, o hazard de τ=0 se comporta de modo suspeito: presencial 14,929 (2019) → 14,983 (2020), praticamente estável; EAD 17,897 → 16,182, **caindo**. Ler essa queda do EAD como "efeito protetor do EAD" seria inverter causa e composição: o EAD absorveu alunos que teriam ido ao presencial.

### 14.2 Decisão

| Uso | Recomendação |
|---|---|
| Desenho causal principal | **EXCLUIR.** A coorte 2020 não deve entrar no DiD nem no event study principais. |
| Análise descritiva | **INCLUIR**, com destaque. É a evidência mais forte e mais comunicável do documento — a recomposição de entrada de 2020 é um resultado por si só, e é honestamente descritivo. |
| Teste de heterogeneidade | **NÃO.** Heterogeneidade pressupõe que o efeito esteja identificado no grupo; aqui não está. |
| **Uso recomendado adicional** | **Como falsificação de seleção.** Se o desenho principal (coortes 2015–2019) produzir um efeito e a coorte 2020 produzir um efeito de sinal oposto, isso é diagnóstico de que a variação está sendo dirigida por composição de entrada, não por comportamento de permanência. |

**Adicionalmente:** a coorte **2019** também merece cautela. Ela ingressou em 2019 (pré-choque, portanto sem seleção de entrada contaminada) mas viveu τ=1 em 2020 — o primeiro ano, que é onde se concentra o risco. É a coorte **mais informativa** do desenho e deve ser reportada separadamente.

---

## 15. Censos históricos necessários (Etapa 11)

**Nenhum arquivo desta seção foi baixado.** Esta é a especificação de aquisição.

### 15.1 Achado que muda o custo do plano

O receio de "microdados gigantes" **não se aplica aos anos que precisamos**. Inspecionei os diretórios centrais dos ZIP remotos por HTTP Range (alguns KB por arquivo, sem baixar o conteúdo):

**[FATO]**

| Ano | ZIP | `MICRODADOS_CADASTRO_CURSOS_{ano}.CSV` descomprimido | `..._IES_{ano}.CSV` |
|---|---|---|---|
| 2014 | 8,5 MB | 42,97 MB | 0,89 MB |
| **2015** | **8,4 MB** | **47,33 MB** | 0,90 MB |
| **2016** | **9,1 MB** | **53,90 MB** | 0,92 MB |
| **2017** | **10,7 MB** | **68,93 MB** | 0,93 MB |
| **2018** | **13,2 MB** | **104,04 MB** | 0,96 MB |
| **2019** | **16,9 MB** | **142,94 MB** | 0,99 MB |
| 2020 | 22,3 MB | 199,99 MB | 0,94 MB |
| 2021 | 26,6 MB | 257,90 MB | 1,08 MB |
| 2024 | 456,8 MB | ~432 MB | 0,98 MB |

O Censo 2024 (o que a auditoria anterior tinha em disco) é o **outlier absoluto**, ~27× maior que o de 2015. **Os Censos 2015–2019 somam 58,3 MB em ZIP.** Não são arquivos grandes.

URL: `https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_{ano}.zip`

### 15.2 Compatibilidade de schema — confirmada

**[FATO]** Li apenas o cabeçalho dos CSV de 2015 e 2019, por HTTP Range:

- ambos têm **exatamente 200 colunas**, com nomes e ordem **idênticos**;
- ambos já trazem a taxonomia **CINE** (`CO_CINE_ROTULO`, `CO_CINE_AREA_GERAL`, `CO_CINE_AREA_ESPECIFICA`, `CO_CINE_AREA_DETALHADA`) — o Inep harmonizou retroativamente, então **não** será preciso converter de OCDE para CINE;
- `TP_MODALIDADE_ENSINO`, `TP_DIMENSAO`, `CO_CURSO`, `CO_IES`, `TP_CATEGORIA_ADMINISTRATIVA`, `TP_ORGANIZACAO_ACADEMICA`, `TP_GRAU_ACADEMICO` estão presentes nos dois;
- codificação **latin-1**, delimitador `;` — igual ao de 2024.

Isso elimina o principal risco técnico do plano.

### 15.3 O que baixar, e por quê

| Ano | Necessário para | Prioridade |
|---|---|---|
| **2019** | **Definir o tratamento** (`TP_MODALIDADE_ENSINO` em 2019 — definição B de §6.3). Sem este arquivo o GATE C1 não pode ser fechado. | **Crítica** |
| **2015, 2016, 2017, 2018** | Testar a **estabilidade** da modalidade 2015–2019 (restrição C) e construir a definição A como sensibilidade. Também fornecem covariáveis predeterminadas contemporâneas a cada coorte. | **Alta** |
| 2014 | Estender a janela de estabilidade um ano para trás. | Baixa |
| 2020 | **Não baixar para o desenho principal.** Só serviria para medir reclassificação pós-choque, que é desfecho. Se baixado, exclusivamente para diagnóstico de contaminação. | Opcional |
| 2021–2024 | Não necessário. | Não |

### 15.4 Colunas a extrair

Chave: **`CO_CURSO`** (verificado nesta auditoria como identificador estável e funcionalmente determinante de `CO_IES`). Filtro obrigatório: **`TP_DIMENSAO ∈ {1, 3}`** — remove a replicação por município de oferta dos cursos EAD, que na edição 2024 respondia por 93,5% das linhas.

| Bloco | Colunas | Papel |
|---|---|---|
| **Chave e tratamento** | `NU_ANO_CENSO`, `CO_IES`, `CO_CURSO`, `TP_DIMENSAO`, **`TP_MODALIDADE_ENSINO`** | tratamento predeterminado |
| **Estratificação** | `TP_CATEGORIA_ADMINISTRATIVA`, `TP_ORGANIZACAO_ACADEMICA`, `TP_REDE`, `TP_GRAU_ACADEMICO`, `TP_NIVEL_ACADEMICO`, `IN_GRATUITO` | população e overlap |
| **Área e geografia** | `CO_CINE_ROTULO`, `CO_CINE_AREA_GERAL`, `CO_CINE_AREA_ESPECIFICA`, `CO_REGIAO`, `CO_UF`, `CO_MUNICIPIO`, `IN_CAPITAL` | estratos e desenho alternativo (§8.5) |
| **Seletividade** | `QT_VG_TOTAL`, `QT_INSCRITO_TOTAL`, `QT_ING` | melhor proxy disponível do confundidor dominante |
| **Turno** | `QT_ING_DIURNO`, `QT_ING_NOTURNO`, `QT_VG_TOTAL_NOTURNO` | preditor clássico, ausente da trajetória |
| **Financiamento** | `QT_ING_FIES`, `QT_ING_PROUNII`, `QT_ING_PROUNIP`, `QT_ING_RESERVA_VAGA` | política simultânea (§13.2) |
| **Demografia de ingresso** | `QT_ING_FEM`, `QT_ING_18_24`, `QT_ING_25_29`, `QT_ING_30_34`, `QT_ING_35_39`, `QT_ING_40_49`, `QT_ING_50_59`, `QT_ING_60_MAIS`, `QT_ING_PRETA`, `QT_ING_PARDA`, `QT_ING_INDIGENA`, `QT_ING_PROCESCPUBLICA` | mitigação parcial da falácia ecológica |
| **Vínculo** | `QT_SIT_TRANCADA`, `QT_SIT_DESVINCULADO`, `QT_SIT_TRANSFERIDO` | quantifica a confusão evasão-de-curso × de-sistema |

~45 colunas de 200.

**Regra inegociável:** essas variáveis só podem ser usadas **do ano `≤` ao ano de referência da observação**. Covariáveis de 2019 são pré-tratamento para o choque de 2020, mas **não** são pré-ingresso para a coorte 2015. Elas servem para (a) definir o tratamento, (b) estratificar, (c) robustez. **Nunca** como controles contemporâneos ao desfecho.

### 15.5 Extração slim e economia de disco

Procedimento por ano:

```
baixar ZIP (8–17 MB)
  → conferir MD5 contra md5_microdados_ed_superior_{ano}.txt do próprio ZIP
  → extrair somente dados/MICRODADOS_CADASTRO_CURSOS_{ano}.CSV e .../IES_{ano}.CSV
  → filtrar TP_DIMENSAO ∈ {1,3}, projetar as ~45 colunas
  → gravar data/interim/censo_cursos_slim_{ano}.parquet (ZSTD)
  → APAGAR o CSV e o ZIP
  → manter o dicionário ANEXO I de um único ano (54 KB)
```

**[FATO], por analogia com a extração já testada na auditoria anterior:** o Censo 2024, com 432 MB de CSV, produziu 46.143 linhas e **0,84 MB** de Parquet. Os anos 2015–2019 têm CSV entre 6× e 3× menores, então:

| | Estimativa |
|---|---|
| Pico transitório de disco (um ano por vez) | **≤ 160 MB** (ZIP 17 MB + CSV 143 MB) |
| Residual permanente, 5 anos slim | **≈ 4–5 MB** |
| Residual permanente, arquivos IES (5 anos) | ≈ 1 MB |

**Sim, a extração slim com apagamento imediato do bruto é viável e recomendada**, e o custo permanente é desprezível.

### 15.6 Alternativa considerada e descartada

Os arquivos de trajetória de coortes antigas trazem snapshots **anteriores** a 2024: o arquivo 2010–2019 (55,6 MB, publicado em 2020-10-07) carregaria covariáveis do último ano de análise **2019** — genuinamente pré-pandemia, e sem depender de Censo.

**Descartado**, por cobertura: esse arquivo contém apenas cursos com coorte de ingresso em 2010 e sobrevivência até 2019. **[FATO]** 81,5% dos cursos EAD da coorte 2020 e 75,6% dos da coorte 2019 sequer existiam como cursos EAD em 2015 — a cobertura para o braço que mais importa seria péssima. O Censo 2019 é mais barato (16,9 MB) e cobre todos os cursos ativos.

---

## 16. Estratégia de inferência e clusterização

| Item | Decisão |
|---|---|
| **Nível de clusterização** | `CO_IES`. O tratamento é constante dentro de IES para a grande maioria dos cursos, e o ICC é 0,36–0,50. |
| **Método** | **Wild cluster bootstrap** com pesos de Rademacher, imposto sob a hipótese nula, ≥ 9.999 réplicas. Erros-padrão CR1 assintóticos **não são válidos aqui**. |
| **Motivo** | **[FATO]** o número efetivo de clusters do braço EAD, ponderado por ingressantes, é **11,7 (coorte 2015) a 16,0 (coorte 2019)**. A assintótica de cluster-robust exige dezenas a centenas de clusters por braço. |
| **Alternativa a reportar em paralelo** | **Inferência de aleatorização / permutação** sobre o rótulo de modalidade dentro de estratos `IES × área`, e um teste de placebo por reatribuição do ano do choque (§17). |
| **Nunca** | Erros-padrão robustos a heterocedasticidade sem cluster; clusterização em nível de curso; qualquer inferência que trate as 1,4 milhão de linhas como observações independentes. |
| **Pseudo-replicação** | Cada trajetória contribui até 10 linhas. O erro-padrão precisa refletir 190.488 trajetórias, não 1.403.065 linhas — e, na prática, ~12–16 instituições efetivas do lado EAD. |
| **Ponderação** | Por `EM_RISCO_INICIO`. Reportar também a versão não ponderada: **[FATO]** as duas contam histórias diferentes, porque o porte médio EAD é 6 a 7 vezes o presencial. |

**Consequência prática, e ela é dura:** com 12 a 16 clusters efetivos num braço, o poder estatístico para detectar um efeito de 1–2 p.p. é baixo, e os intervalos de confiança honestos serão largos o bastante para incluir zero e o dobro do efeito plausível. **Isso precisa ser reconhecido antes de estimar, não depois.**

---

## 17. Robustez e falsificações

Cada item abaixo é um teste que **pode derrubar** o resultado. Devem ser pré-registrados antes de qualquer estimativa.

| # | Teste | O que detecta | Critério de reprovação |
|---|---|---|---|
| **F1** | **Placebo temporal:** reatribuir o choque a 2018 e a 2019, truncando a amostra em 2019 | Se um "efeito" aparece num ano sem choque, o desenho está capturando tendência | Qualquer coeficiente placebo com magnitude ≥ 50% do estimado |
| **F2** | **Leave-one-institution-out** das 10 maiores IES EAD, uma por vez | Dominância institucional (§12.2) | Coeficiente muda de sinal ou varia > 50% ao remover **uma** IES |
| **F3** | **Desfecho placebo:** hazard de **conclusão** em vez de desistência | Se o "efeito" aparece em todo desfecho, é composição, não comportamento | Efeito de magnitude comparável no placebo |
| **F4** | **Sensibilidade ao outcome:** repetir com `TADA` e com `TDA` | Demonstra a fragilidade documentada em §5.2 | (é diagnóstico, não reprovação) — **[FATO]** espera-se inversão de sinal em 21 de 45 células |
| **F5** | **Sensibilidade à definição de tratamento:** B vs A vs C (§6.2) | Se as três divergem, o tratamento não é bem definido | Divergência qualitativa entre as definições |
| **F6** | **Painel fechado de cursos** (presentes nas 6 coortes) vs. painel aberto | Composição (§12.3) | Divergência qualitativa |
| **F7** | **Exclusão da coorte 2020**, e depois exclusão da 2019 | Seleção de entrada (§14) | Resultado depende de uma única coorte |
| **F8** | **Corte de porte:** `EM_RISCO_INICIO ≥ 20`, ≥ 50 | Ruído de cursos pequenos | Resultado só aparece nos cursos pequenos |
| **F9** | **Restrição a `IES × CO_CINE_ROTULO` com ambas as modalidades** | Confundimento institucional e de área | Resultado desaparece sob o estrato fino |
| **F10** | **Heterogeneidade por τ**, reportada sempre separadamente | Agregação em τ mascarando sinais opostos | Sinais opostos entre τ=0, 1 e 2 |
| **F11** | **Ponderada vs. não ponderada** | Dominância de cursos grandes | Divergência qualitativa |
| **F12** | **Reversão em 2022–2024** | Um choque transitório deve reverter; um efeito permanente é suspeito de ser tendência | Efeito monotonicamente crescente até 2024 |

---

## 18. Gates de decisão (Etapa 12)

Situação apurada **com os dados hoje em disco**. Onde o gate depende de dado ainda não adquirido, isso está dito.

### GATE C1 — Tratamento predeterminado  `↪ ver §21` (reclassificado)

| | |
|---|---|
| **Critério PASSA** | Modalidade medida em ano ≤ 2019, disponível para ≥ 90% dos cursos da população, e estável em 2015–2019 para ≥ 95% deles. |
| **ALERTA** | Cobertura 75–90%, ou 5–15% de cursos instáveis (tratáveis pela restrição C). |
| **FALHA** | Modalidade só disponível em ano ≥ 2020, ou cobertura < 75%. |
| **Situação** | **FALHA.** **[FATO]** todos os seis arquivos de trajetória carregam o snapshot de 2024; 0 de 38.103 cursos apresentam modalidade divergente entre coortes. |
| **Se falhar** | **Bloqueia toda a análise causal.** Nenhuma estimativa deve ser produzida enquanto C1 estiver em falha. |
| **Recuperável?** | **Sim, e de forma barata** — Censo 2019 (16,9 MB) + 2015–2018 (41,4 MB). Ver §15. Este é o próximo passo. |

### GATE C2 — Overlap

| | |
|---|---|
| **PASSA** | Em cada estrato `área CINE × categoria administrativa` usado, ambos os braços têm ≥ 30 cursos e ≥ 5 IES, em **todas** as coortes pré-2020; e nenhuma IES isolada responde por > 20% dos ingressantes de um braço. |
| **ALERTA** | Suporte satisfeito em ≥ 60% dos estratos; ou uma IES responde por 20–35% de um braço. |
| **FALHA** | Suporte em < 60% dos estratos; ou uma IES responde por > 35% de um braço. |
| **Situação** | **FALHA.** **[FATO]** áreas 05 e 08 têm 1 e 2 cursos EAD na coorte 2015; a categoria 3 tem zero EAD; **4 a 6 IES concentram 50% dos ingressantes EAD**; o número efetivo de IES do braço EAD é 11,7–16,0. |
| **Se falhar** | Restringir a população (§7) e **reavaliar**. Se ainda falhar, o estimando deve ser redefinido para a população restrita — e a validade externa declarada como limitada a ela. |
| **Recuperável?** | **Parcialmente.** A restrição a 107 IES melhora comparabilidade mas **agrava** a concentração. |

### GATE C3 — Tendências paralelas  `↪ ver §21` (reclassificado)

| | |
|---|---|
| **Critérios** | Os de §11.5. |
| **Situação** | **FALHA**, em τ=0, 1 e 2, por múltiplos critérios simultâneos. **[FATO]** amplitude do gap pré-choque de 7,02 / 5,93 / 4,16 p.p. contra mudanças 2019→2020 de +1,77 / +0,76 / −0,01 p.p. `σ_pré` excede `\|θ̂\|` em todas as três idades. |
| **Se falhar** | **Nenhuma alegação causal.** O projeto passa a reportar as séries como **descritivas**, e a falha de pré-tendências como **resultado metodológico** — que é um resultado legítimo e comunicável. |
| **Recuperável?** | **Incerto.** O teste precisa ser **refeito** com o tratamento predeterminado de C1. **[HIPÓTESE]** não espero reversão, dada a magnitude da oscilação e a concentração do braço EAD, mas o teste atual não é conclusivo e não deve ser apresentado como se fosse. |

### GATE C4 — Estabilidade de composição

| | |
|---|---|
| **PASSA** | ≤ 15% dos cursos de cada braço são novos entre a primeira e a última coorte pré-choque; porte médio varia ≤ 20%. |
| **ALERTA** | 15–35% de cursos novos, ou porte médio variando 20–35%. |
| **FALHA** | > 35% de cursos novos, ou porte médio variando > 35%. |
| **Situação** | **FALHA.** **[FATO]** 75,6% dos cursos EAD da coorte 2019 são novos em relação à de 2015; 35,1% dos ingressantes EAD estão em cursos novos; o porte médio EAD cai de 652 para 415 (−36,3%). O braço presencial fica em ALERTA (25,2% de cursos novos, porte −20,2%). |
| **Se falhar** | Restringir ao painel fechado de cursos. **[FATO]** isso reduz o braço EAD a 901 cursos e muda o estimando: passa a valer para cursos EAD estabelecidos até 2015, não para o EAD brasileiro. |
| **Recuperável?** | Parcialmente, ao custo de validade externa. |

### GATE C5 — Age / cohort / calendar-time

| | |
|---|---|
| **PASSA** | Especificação declara explicitamente qual das três dimensões é restrita a ser comum entre grupos; a restrição é justificada substantivamente; e resultados são reportados **por τ**, nunca só agregados. |
| **ALERTA** | Especificação declarada mas com restrição frágil (ex.: efeitos de coorte comuns num contexto de forte recomposição). |
| **FALHA** | Modelo inclui simultaneamente efeitos específicos de grupo em idade, coorte e período; ou reporta um coeficiente único agregado em τ sem a decomposição; ou trata `NU_ANO_REFERENCIA` como "tempo" sem τ. |
| **Situação** | **ALERTA.** A estrutura é compreendida e a especificação de §10.5 é implementável. Mas a restrição necessária — **efeitos de coorte comuns aos dois braços** — é diretamente contrariada pela evidência de C4. |
| **Se falhar** | Reformular ou abandonar. |
| **Nota permanente** | A indeterminação **linear** de §10.6 nunca é resolvida. Ela deve constar do relatório final como limitação declarada, independentemente dos demais gates. |

### GATE C6 — Dependência intra-IES

| | |
|---|---|
| **PASSA** | ≥ 40 IES efetivas em **cada** braço, e inferência por wild cluster bootstrap. |
| **ALERTA** | 20–40 IES efetivas no braço menor. |
| **FALHA** | < 20 IES efetivas no braço menor. |
| **Situação** | **FALHA.** **[FATO]** número efetivo (Kish, ponderado por ingressantes) do braço EAD: 11,7 (2015) · 13,0 (2017) · 16,0 (2019) · 15,8 (2020). |
| **Se falhar** | Inferência exclusivamente por wild cluster bootstrap **e** por permutação; intervalos de confiança reportados sem exceção; **nenhuma leitura de significância a 5% sem os dois métodos concordarem**. Reconhecer que o poder é baixo. |
| **Recuperável?** | **Não.** É uma propriedade do mercado de EAD brasileiro, não do desenho. |

### GATE C7 — Sensibilidade

| | |
|---|---|
| **PASSA** | Sinal e ordem de magnitude preservados em **todos** os testes F1–F12 de §17. |
| **ALERTA** | Sinal preservado, magnitude varia até 50%, em ≥ 10 dos 12 testes. |
| **FALHA** | Sinal inverte em qualquer teste; ou resultado desaparece em F2 (uma IES), F6 (painel fechado) ou F9 (estrato fino); ou F1 (placebo) produz efeito. |
| **Situação** | **NÃO AVALIADO** — depende de estimativas, que não devem existir enquanto C1 estiver em falha. |
| **Se falhar** | Nenhuma alegação causal. |

### 18.1 Painel de gates

> `↪ ver §21.7` para o painel atualizado após a reavaliação.

| Gate | Situação | Recuperável? | Custo da recuperação |
|---|---|---|---|
| **C1** Tratamento predeterminado | 🔴 **FALHA** | **Sim** | 58 MB de download; ~1 dia de trabalho |
| **C2** Overlap | 🔴 **FALHA** | Parcial | Restrição de população; perda de validade externa |
| **C3** Tendências paralelas | 🔴 **FALHA** | **Incerto** | Reteste obrigatório após C1 |
| **C4** Estabilidade de composição | 🔴 **FALHA** | Parcial | Painel fechado; braço EAD cai a 901 cursos |
| **C5** Age/period/cohort | 🟡 **ALERTA** | Sim, com hipótese declarada | Indeterminação linear permanece |
| **C6** Dependência intra-IES | 🔴 **FALHA** | **Não** | — |
| **C7** Sensibilidade | ⚪ não avaliado | — | — |

---

## 19. Veredito atual  `↪ ver §21.8` para o veredito atualizado

> # **CAUSAL NÃO IDENTIFICADO**

**Quatro gates fundamentais em falha (C1, C2, C3, C4), um em alerta (C5) e um irrecuperável (C6).**

O gate que decide é o **C6**, e ele merece ser dito com clareza porque é o único que nenhum trabalho adicional resolve:

> **[FATO] O braço de comparação tem entre 12 e 16 instituições efetivas.** A pergunta "qual foi o impacto diferencial da COVID sobre cursos presenciais versus EAD" é, operacionalmente, a pergunta "como cerca de uma dúzia de grandes grupos educacionais privados se comportaram em 2020 comparados a todo o resto do sistema". Isso não é um problema de estimador, de amostra ou de especificação. É a estrutura do mercado brasileiro de EAD.

Os demais gates reforçam:

- **C1** é recuperável e barato, e **deve** ser recuperado — mas resolver C1 não resolve C3, C4 nem C6.
- **C3** falha por larga margem: **[FATO]** a oscilação pré-choque do gap (7,0 p.p. em τ=0) é **quatro vezes** a mudança observada em 2020 (+1,8 p.p.). Não existe degrau distinguível do ruído.
- **C4** falha porque o grupo de comparação foi reconstruído durante o período de estudo: **[FATO]** 75,6% dos cursos EAD da coorte 2019 não existiam como tais na de 2015.
- **C5** deixa uma indeterminação linear permanente, declarada em §10.6.

**O que este veredito NÃO significa:**

- Não significa que a pandemia não afetou a evasão. Significa que **este desenho, com estes dados, não consegue medir isso.**
- Não significa que o painel multi-coorte foi inútil. Ele produziu resultados descritivos e longitudinais de primeira qualidade — a expansão do EAD de 24% para 53% dos ingressantes, a recomposição de entrada de 2020 (−12,1% presencial / +24,5% EAD), o perfil de hazard condicional por idade de trajetória. **A construção da base valeu, e ela sustenta um trabalho forte — descritivo e longitudinal, não causal.**
- Não significa que o veredito seja final. Ele é **condicional aos dados hoje disponíveis**, e o §20 define exatamente o que o mudaria.

**Condição para revisão do veredito:** resolver C1 (Censos 2015–2019) e **refazer o teste de pré-tendências de §11 com o tratamento predeterminado**. Se — contra a expectativa registrada em §11.6 — as pré-tendências passarem no grupo restrito de §7, o veredito passa a **CAUSAL VIÁVEL COM RESTRIÇÕES SEVERAS**, com C6 permanentemente em falha, inferência exclusivamente por bootstrap/permutação, e validade externa limitada às ~107 IES que ofertam ambas as modalidades.

**Regra que este documento estabelece:** enquanto C1 ou C3 estiverem em falha, **nenhuma estimativa de DiD ou event study deve ser reportada**, nem mesmo como "resultado preliminar". Um coeficiente publicado é lido como causal independentemente das ressalvas que o acompanhem.

---

## 20. Próximo passo mínimo  `↪ EXECUTADO — ver §21`

**Um único passo, delimitado, e ele decide o projeto:**

> ### Baixar os Censos da Educação Superior 2015–2019 (cadastro de cursos), extrair a camada slim, construir o tratamento predeterminado, e refazer exclusivamente o teste de pré-tendências de §11.

Escopo exato:

1. **Baixar** `microdados_censo_da_educacao_superior_{2015..2019}.zip` — **[FATO]** 58,3 MB somados. Conferir MD5 contra o `md5_*.txt` de cada ZIP.
2. **Extrair slim**: `TP_DIMENSAO ∈ {1,3}`, ~45 colunas de §15.4 → `data/interim/censo_cursos_slim_{ano}.parquet`. **Apagar CSV e ZIP imediatamente.** Residual ≈ 5 MB.
3. **Construir** `TRATAMENTO_2019` (definição B) e `MODALIDADE_ESTAVEL_2015_2019` (restrição C). Reportar a taxa de cobertura do join com os 43.861 cursos do painel, e quantos cursos mudaram de modalidade no pré-choque.
4. **Refazer a tabela de §11.2** com o tratamento predeterminado, para τ ∈ {0, 1, 2}, na população principal de §7, com wild cluster bootstrap por IES e o teste *leave-one-institution-out* de F2.
5. **Aplicar os critérios de §11.5** e registrar PASSA / ALERTA / FALHA.

**O que NÃO fazer neste passo:** não estimar DiD, não estimar event study de lags, não reportar nenhum coeficiente de efeito. **Apenas os leads.** O teste de pré-tendências precisa ser executado e julgado *antes* de qualquer estimativa existir, porque uma vez que um número de efeito exista, ele será citado.

**Critério de continuação:**

| Resultado do passo 5 | Ação |
|---|---|
| **PASSA** | Prosseguir para o event study completo, com C6 permanentemente declarado em falha. |
| **ALERTA** | Prosseguir apenas com o event study, sem coeficiente resumo, e com a interpretação causal explicitamente suspensa. |
| **FALHA** (esperado) | **Encerrar a linha causal.** Reorientar para: (a) o trabalho descritivo e longitudinal multi-coorte, que os dados sustentam plenamente; (b) o desenho alternativo de §8.5, se houver apetite por dados externos de severidade local; (c) um capítulo metodológico sobre **por que a identificação falha**, ancorado nos números deste documento — que tem valor didático real e é honesto. |

**Custo do passo:** ~58 MB de download transitório, ~5 MB permanentes, e o tempo de um script. **É barato o bastante para não haver razão de não fazê-lo, e decisivo o bastante para não haver razão de fazer qualquer outra coisa antes.**

---

## Anexo — O que foi feito nesta auditoria

**Nenhum dado bruto foi modificado. Nenhum Censo histórico foi baixado. Nenhum modelo causal foi implementado. Nenhum commit foi feito. O README não foi alterado.**

**Criado no projeto:**

| Arquivo | Papel |
|---|---|
| `src/baixa_trajetorias.py` | aquisição das coortes 2016–2020, com política de retenção |
| `src/constroi_painel_multicoorte.py` | ingestão auditada e Parquet multi-coorte |
| `data/processed/trajetorias_2015_2020.parquet` | 25,56 MB |
| `data/processed/auditoria_multicoorte.json` | métricas de auditoria por coorte |
| `docs/auditoria_multicoorte.md` | aquisição e auditoria |
| `docs/auditoria_causal_covid.md` | este documento |
| `data/raw/trajetoria/{2016..2020}_2024/` | XLSX + dicionário + md5 |

**Apagado, e por quê:** 5 arquivos `.ods` (160,7 MB — duplicata exata do XLSX correspondente, com MD5 registrado no `md5_*.txt` mantido em disco) e 5 arquivos `.zip` (330,7 MB — containers já extraídos e verificados). Detalhamento em [auditoria_multicoorte.md](auditoria_multicoorte.md) §2.

**Comandos:**

```bash
python src/baixa_trajetorias.py 2016 2017 2018 2019 2020
python src/constroi_painel_multicoorte.py
```

**Fora do projeto** (scratchpad da sessão, descartáveis): `audit_headers.py`, `diag_causal.py`, `diag_causal2.py`, `diag_causal3.py`, `listar_zip_remoto.py` (leitura de diretório central de ZIP remoto por HTTP Range), `cabecalho_csv_remoto.py` (leitura de cabeçalho de CSV dentro de ZIP remoto, sem baixar o arquivo).

**Correção registrada:** o ICC intra-IES de 0,65 reportado em [auditoria_metodologica.md](auditoria_metodologica.md) §8.4 usava um estimador enviesado para cima. Por ANOVA de uma via, o valor correto é 0,36–0,50 conforme a coorte. A conclusão substantiva — dependência intra-IES grande, exigindo clusterização e `GroupKFold` por IES — não muda.
