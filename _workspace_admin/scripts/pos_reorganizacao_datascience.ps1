param(
    [switch]$Execute
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$DryRun = -not $Execute.IsPresent

$Projetos = Join-Path $Root "projetos"
$Starbucks = Join-Path $Projetos "starbucks-customer-rewards-program-dataset"
$Causal = Join-Path $Projetos "inferencia-causal"

$RootVenv = Join-Path $Root ".venv"
$ArchivedRootVenv = Join-Path $Root ".venv_workspace_antiga"

$RootAgents = Join-Path $Root "AGENTS.md"
$RootGitignore = Join-Path $Root ".gitignore"

$CausalPlaybooks = Join-Path $Causal "playbooks_tecnicos"
$StarbucksPlaybooks = Join-Path $Starbucks "playbooks_tecnicos"

function Write-Step {
    param([string]$Message)

    Write-Host ""
    Write-Host "### $Message" -ForegroundColor Cyan
}

function Require-Path {
    param(
        [string]$Path,
        [string]$Description
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "NÃ£o encontrei $Description em: $Path"
    }
}

function Ensure-Dir {
    param([string]$Path)

    if (Test-Path -LiteralPath $Path) {
        Write-Host "[OK] Pasta jÃ¡ existe: $Path"
        return
    }

    if ($DryRun) {
        Write-Host "[PREVIEW] Criaria pasta: $Path"
    }
    else {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "[OK] Pasta criada: $Path"
    }
}

function Add-Gitignore-Line {
    param([string]$Line)

    if (-not (Test-Path -LiteralPath $RootGitignore)) {
        if ($DryRun) {
            Write-Host "[PREVIEW] Criaria .gitignore"
            return
        }
        else {
            New-Item -ItemType File -Path $RootGitignore -Force | Out-Null
        }
    }

    $Content = Get-Content -LiteralPath $RootGitignore -Raw -ErrorAction SilentlyContinue

    if ($Content -match [regex]::Escape($Line)) {
        Write-Host "[OK] .gitignore jÃ¡ contÃ©m: $Line"
        return
    }

    if ($DryRun) {
        Write-Host "[PREVIEW] Adicionaria ao .gitignore: $Line"
    }
    else {
        Add-Content -LiteralPath $RootGitignore -Value $Line -Encoding UTF8
        Write-Host "[OK] Adicionado ao .gitignore: $Line"
    }
}

function Archive-RootVenv {
    if (-not (Test-Path -LiteralPath $RootVenv)) {
        Write-Host "[OK] NÃ£o existe .venv na raiz."
        return
    }

    if (Test-Path -LiteralPath $ArchivedRootVenv) {
        Write-Host "[AVISO] JÃ¡ existe .venv_workspace_antiga. A .venv atual da raiz serÃ¡ mantida."
        return
    }

    if ($DryRun) {
        Write-Host "[PREVIEW] Renomearia .venv da raiz para .venv_workspace_antiga"
    }
    else {
        Rename-Item -LiteralPath $RootVenv -NewName ".venv_workspace_antiga"
        Write-Host "[OK] .venv da raiz arquivada como .venv_workspace_antiga"
    }
}

function Write-Agents {
    $AgentsContent = @'
# AGENTS.md

## 1. Escopo do Workspace

Estas instruÃ§Ãµes valem para todo o workspace `datascience`.

Este workspace contÃ©m mÃºltiplos projetos independentes de CiÃªncia de Dados, Machine Learning, InferÃªncia Causal, CRM Analytics, ExperimentaÃ§Ã£o, Uplift Modeling, OtimizaÃ§Ã£o de DecisÃ£o, CrÃ©dito, Forecasting e construÃ§Ã£o de pipelines analÃ­ticos orientados a produÃ§Ã£o.

Cada projeto deve ficar dentro de:

- `projetos/<nome-do-projeto>/`

Exemplos atuais:

- `projetos/starbucks-customer-rewards-program-dataset/`
- `projetos/inferencia-causal/`

A raiz do workspace deve conter apenas arquivos gerais, como:

- `AGENTS.md`
- `README.md`
- `.gitignore`
- scripts administrativos do workspace

NÃ£o trate a raiz `datascience/` como se fosse um Ãºnico projeto.

---

## 2. Regra de Escopo ObrigatÃ³rio

Antes de modificar qualquer arquivo, identifique explicitamente o escopo da tarefa.

Para qualquer tarefa de implementaÃ§Ã£o, revisÃ£o ou refatoraÃ§Ã£o, apresente antes:

1. projeto alvo;
2. arquivos que pretende ler;
3. arquivos que pretende modificar;
4. arquivos ou pastas que nÃ£o serÃ£o alterados;
5. plano curto de validaÃ§Ã£o.

Nunca altere arquivos fora da pasta ou dos arquivos mencionados pelo usuÃ¡rio.

Se o usuÃ¡rio pedir para trabalhar em um projeto especÃ­fico, modifique apenas arquivos dentro da pasta desse projeto.

Ao trabalhar em um projeto, trate a pasta desse projeto como a raiz lÃ³gica da tarefa.

Exemplo:

- Se o projeto alvo for `projetos/starbucks-customer-rewards-program-dataset/`, nÃ£o altere `projetos/inferencia-causal/` sem autorizaÃ§Ã£o explÃ­cita.
- Se o projeto alvo for `projetos/inferencia-causal/`, nÃ£o altere `projetos/starbucks-customer-rewards-program-dataset/` sem autorizaÃ§Ã£o explÃ­cita.

NÃ£o altere automaticamente:

- `.venv/`
- `.venv_workspace_antiga/`
- dados brutos;
- arquivos grandes;
- outros projetos nÃ£o citados;
- `AGENTS.md`;
- `.gitignore`;
- `README.md` da raiz.

NÃ£o crie, mova, renomeie ou delete arquivos sem pedido explÃ­cito.

---

## 3. Regras Operacionais

Trabalhe de forma incremental.

Prefira mudanÃ§as pequenas, seguras e fÃ¡ceis de revisar.

NÃ£o instale pacotes sem pedido explÃ­cito.

NÃ£o crie pastas sem pedido explÃ­cito.

NÃ£o apague arquivos.

NÃ£o altere arquivos fora do escopo solicitado.

Antes de editar arquivos, apresente um plano curto.

Depois de editar arquivos, liste o que foi alterado e explique como validar.

NÃ£o gere cÃ³digo com placeholders.

NÃ£o deixe cÃ³digo incompleto.

Prefira cÃ³digo claro, modular, testÃ¡vel e reutilizÃ¡vel.

Prefira validaÃ§Ãµes explÃ­citas em vez de apenas inspeÃ§Ã£o visual.

Mantenha notebooks legÃ­veis e com narrativa analÃ­tica.

Mova lÃ³gica reutilizÃ¡vel para funÃ§Ãµes apenas quando isso melhorar clareza ou reuso.

---

## 4. Ambientes Virtuais

Cada projeto deve ter seu prÃ³prio ambiente virtual `.venv`.

Exemplo:

- `projetos/starbucks-customer-rewards-program-dataset/.venv/`
- `projetos/inferencia-causal/.venv/`

NÃ£o use a `.venv` da raiz para desenvolvimento de projetos.

NÃ£o edite, mova ou apague ambientes virtuais sem pedido explÃ­cito.

Ao orientar execuÃ§Ã£o de cÃ³digo, sempre indique qual `.venv` deve ser ativada.

---

## 5. Stack PadrÃ£o

Use DuckDB como motor analÃ­tico principal para:

- leitura de arquivos locais;
- parsing de JSON;
- transformaÃ§Ãµes SQL;
- joins;
- agregaÃ§Ãµes;
- janelas temporais;
- validaÃ§Ãµes de dados;
- construÃ§Ã£o de ABTs.

Use Pandas principalmente para:

- materializar resultados finais;
- inspeÃ§Ã£o leve;
- visualizaÃ§Ã£o;
- preparaÃ§Ã£o para modelagem;
- integraÃ§Ã£o com bibliotecas de ML.

Evite fazer joins relacionais pesados e agregaÃ§Ãµes grandes em Pandas quando DuckDB for mais apropriado.

---

## 6. Estrutura Esperada dos Projetos

Pastas relevantes podem incluir:

- `data/`: dados brutos, tratados ou locais.
- `notebooks/`: notebooks exploratÃ³rios e narrativos.
- `playbooks_tecnicos/`: guias metodolÃ³gicos e tÃ©cnicos.
- `src/`: cÃ³digo reutilizÃ¡vel, caso exista.
- `tests/`: validaÃ§Ãµes e testes, caso exista.
- `reports/`: saÃ­das analÃ­ticas, grÃ¡ficos, tabelas e materiais executivos.
- `app/`: aplicaÃ§Ã£o, interface ou dashboard.
- `backend/`: APIs, serviÃ§os auxiliares ou lÃ³gica de backend.

NÃ£o presuma que uma pasta existe. Inspecione antes.

---

## 7. Uso dos Playbooks TÃ©cnicos

Use apenas o playbook necessÃ¡rio para a tarefa atual.

NÃ£o leia todos os playbooks sem necessidade.

Os playbooks principais de inferÃªncia causal ficam em:

- `projetos/inferencia-causal/playbooks_tecnicos/`

O projeto Starbucks tambÃ©m pode ter uma cÃ³pia local em:

- `projetos/starbucks-customer-rewards-program-dataset/playbooks_tecnicos/`

Ãndice dos playbooks:

- `00_contexto_operacional_projeto.md`: regras operacionais e disciplina de trabalho.
- `01_inferencia_causal_uplift.md`: inferÃªncia causal, uplift, CATE e efeitos de tratamento.
- `02_abt_temporal_qualidade_dados.md`: desenho de ABT, consistÃªncia temporal e qualidade de dados.
- `03_estimadores_validacao_causal.md`: estimadores, assumptions, validaÃ§Ã£o e overlap.
- `04_otimizacao_roi_politica_decisao.md`: ROI, restriÃ§Ãµes, polÃ­tica de decisÃ£o e otimizaÃ§Ã£o.
- `05_design_sistema_ml_causal_producao.md`: design de produÃ§Ã£o, pipelines, contratos e monitoramento.
- `06_governanca_revisao_comunicacao.md`: revisÃ£o crÃ­tica, governanÃ§a, comunicaÃ§Ã£o e limitaÃ§Ãµes.

Se o nome real do arquivo for diferente, use o arquivo existente e nÃ£o renomeie sem pedido explÃ­cito.

---

## 8. Quando Aplicar Regras de InferÃªncia Causal

As regras de inferÃªncia causal devem ser aplicadas quando a tarefa envolver:

- tratamento;
- intervenÃ§Ã£o;
- campanha;
- cupom;
- desconto;
- incentivo;
- polÃ­tica de decisÃ£o;
- experimento;
- teste A/B;
- uplift;
- CATE;
- impacto incremental;
- ROI incremental;
- personalizaÃ§Ã£o de aÃ§Ã£o;
- avaliaÃ§Ã£o de efeito.

Quando o problema for apenas preditivo, exploratÃ³rio ou descritivo, nÃ£o force uma interpretaÃ§Ã£o causal.

NÃ£o confunda prediÃ§Ã£o com causalidade.

Para qualquer problema causal ou com intervenÃ§Ã£o, defina explicitamente:

- decisÃ£o de negÃ³cio ou decisÃ£o operacional;
- unidade de anÃ¡lise;
- tratamento/intervenÃ§Ã£o;
- grupo controle/comparaÃ§Ã£o;
- momento de decisÃ£o;
- outcome;
- janela do outcome;
- features prÃ©-tratamento;
- variÃ¡veis pÃ³s-tratamento que devem ser excluÃ­das;
- assumptions;
- limitaÃ§Ãµes.

Features devem estar disponÃ­veis antes do momento de decisÃ£o.

Targets devem ser medidos depois do momento de decisÃ£o.

NÃ£o use variÃ¡veis pÃ³s-tratamento como features.

NÃ£o apresente modelo de propensÃ£o como se fosse uplift causal.

Caso nÃ£o exista grupo controle ou estratÃ©gia de identificaÃ§Ã£o defensÃ¡vel, deixe claro que o resultado Ã© preditivo ou associativo, nÃ£o causal.

---

## 9. Regras de ABT

Em projetos causais, a ABT deve documentar:

- chave primÃ¡ria;
- granularidade;
- ID da entidade;
- ID do tratamento, quando aplicÃ¡vel;
- flag de tratamento;
- momento de decisÃ£o;
- janela de features;
- janela de outcome;
- colunas de target;
- colunas proibidas por leakage;
- flags de qualidade.

A ABT deve ser validada para:

- dados nÃ£o vazios;
- schema esperado;
- unicidade da chave;
- presenÃ§a de tratamento e controle;
- ausÃªncia de nulos crÃ­ticos;
- ausÃªncia de timestamps impossÃ­veis;
- ausÃªncia de feature leakage;
- ausÃªncia de target leakage.

---

## 10. Regras de Modelagem

Comece com um baseline simples e defensÃ¡vel antes de modelos complexos.

Para problemas preditivos, use mÃ©tricas preditivas adequadas.

Para problemas causais ou de uplift, prefira mÃ©tricas como:

- uplift por decil;
- Qini/AUUC, quando aplicÃ¡vel;
- ganho incremental;
- comparaÃ§Ã£o entre tratamento e controle;
- heterogeneidade de efeito;
- valor de negÃ³cio;
- ROI.

NÃ£o use acurÃ¡cia, F1 ou ROC-AUC como mÃ©trica principal para qualidade de uplift ou decisÃ£o causal.

---

## 11. Regras de DecisÃ£o

Score de modelo nÃ£o Ã© entrega final.

Quando o projeto envolver decisÃ£o, gere uma polÃ­tica acionÃ¡vel sempre que possÃ­vel.

Uma polÃ­tica deve considerar:

- efeito esperado;
- valor esperado;
- custo esperado;
- valor lÃ­quido esperado;
- ROI;
- elegibilidade;
- capacidade;
- orÃ§amento;
- risco;
- fallback.

NÃ£o recomende tratar automaticamente toda unidade com score positivo.

Para incentivos, descontos, cupons, cashback, pricing, retenÃ§Ã£o ou aÃ§Ãµes operacionais, considere custo e risco de canibalizaÃ§Ã£o.

---

## 12. Regras de Design de ProduÃ§Ã£o

Separe conceitualmente a lÃ³gica em:

1. ingestÃ£o;
2. normalizaÃ§Ã£o;
3. construÃ§Ã£o de features;
4. construÃ§Ã£o da ABT;
5. modelagem ou estimaÃ§Ã£o de efeito;
6. avaliaÃ§Ã£o;
7. polÃ­tica de decisÃ£o;
8. monitoramento.

Prefira contratos explÃ­citos para tabelas e saÃ­das importantes.

Toda saÃ­da importante deve conter:

- nome do artefato;
- granularidade;
- chave;
- validaÃ§Ã£o;
- limitaÃ§Ã£o conhecida;
- prÃ³ximo passo.

---

## 13. Regras de RevisÃ£o

Antes de considerar uma tarefa concluÃ­da, verifique:

- A mudanÃ§a ficou dentro do escopo?
- As assumptions de dados estÃ£o explÃ­citas?
- As regras temporais foram respeitadas?
- Existe leakage?
- A mÃ©trica estÃ¡ alinhada Ã  decisÃ£o?
- As limitaÃ§Ãµes foram declaradas?
- A saÃ­da Ã© acionÃ¡vel?
- Existe validaÃ§Ã£o?

Classifique problemas como:

- crÃ­tico: invalida o resultado;
- alto: resultado apenas exploratÃ³rio;
- mÃ©dio: usar com ressalvas;
- baixo: melhoria de manutenÃ§Ã£o ou clareza.

---

## 14. Formato de Resposta

Para tarefas de planejamento:

1. plano curto;
2. riscos;
3. arquivos provavelmente afetados;
4. plano de validaÃ§Ã£o.

Para tarefas de implementaÃ§Ã£o:

1. plano curto antes da ediÃ§Ã£o;
2. mudanÃ§a mÃ­nima e dentro do escopo;
3. arquivos alterados;
4. instruÃ§Ãµes de validaÃ§Ã£o;
5. limitaÃ§Ãµes restantes.

Para tarefas de revisÃ£o:

1. achados por severidade;
2. evidÃªncia;
3. correÃ§Ã£o recomendada;
4. indicaÃ§Ã£o se Ã© bloqueador ou nÃ£o.
'@

    if (-not (Test-Path -LiteralPath $RootAgents)) {
        if ($DryRun) {
            Write-Host "[PREVIEW] Criaria AGENTS.md na raiz"
        }
        else {
            Set-Content -LiteralPath $RootAgents -Value $AgentsContent -Encoding UTF8
            Write-Host "[OK] AGENTS.md criado na raiz"
        }
        return
    }

    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $BackupPath = Join-Path $Root "AGENTS.backup_$Timestamp.md"

    if ($DryRun) {
        Write-Host "[PREVIEW] Criaria backup do AGENTS atual em: $BackupPath"
        Write-Host "[PREVIEW] Substituiria o conteÃºdo de AGENTS.md pela nova versÃ£o"
    }
    else {
        Copy-Item -LiteralPath $RootAgents -Destination $BackupPath
        Set-Content -LiteralPath $RootAgents -Value $AgentsContent -Encoding UTF8
        Write-Host "[OK] Backup criado: $BackupPath"
        Write-Host "[OK] AGENTS.md atualizado"
    }
}

function Sync-Starbucks-Playbooks {
    Require-Path $CausalPlaybooks "playbooks tÃ©cnicos de inferÃªncia causal"

    Ensure-Dir $StarbucksPlaybooks

    $MarkdownFiles = Get-ChildItem -LiteralPath $CausalPlaybooks -Filter "*.md" -File

    if ($MarkdownFiles.Count -eq 0) {
        Write-Host "[AVISO] Nenhum arquivo .md encontrado em: $CausalPlaybooks"
        return
    }

    foreach ($File in $MarkdownFiles) {
        $Destination = Join-Path $StarbucksPlaybooks $File.Name

        if ($DryRun) {
            Write-Host "[PREVIEW] Copiaria playbook: $($File.FullName) -> $Destination"
        }
        else {
            Copy-Item -LiteralPath $File.FullName -Destination $Destination -Force
            Write-Host "[OK] Playbook copiado/atualizado: $($File.Name)"
        }
    }
}

Write-Host ""
Write-Host "Raiz detectada: $Root" -ForegroundColor Yellow

Require-Path $Projetos "pasta projetos"
Require-Path $Starbucks "projeto Starbucks"
Require-Path $Causal "projeto InferÃªncia Causal"

if ($DryRun) {
    Write-Host ""
    Write-Host "Modo atual: PREVIEW. Nada serÃ¡ alterado." -ForegroundColor Yellow
    Write-Host "Para executar de verdade, rode:"
    Write-Host ".\pos_reorganizacao_datascience.ps1 -Execute"
}
else {
    Write-Host ""
    Write-Host "Modo atual: EXECUÃ‡ÃƒO REAL." -ForegroundColor Green
}

Write-Step "Atualizando .gitignore"

Add-Gitignore-Line ""
Add-Gitignore-Line "# Ambientes virtuais"
Add-Gitignore-Line ".venv/"
Add-Gitignore-Line ".venv*/"
Add-Gitignore-Line "**/.venv/"
Add-Gitignore-Line ".venv_workspace_antiga/"

Write-Step "Arquivando .venv antiga da raiz"
Write-Host "[AVISO] Arquivamento da .venv da raiz pulado temporariamente. Ela será mantida, mas ignorada pelo .gitignore."
Write-Step "Atualizando AGENTS.md da raiz"

Write-Agents

Write-Step "Copiando playbooks tÃ©cnicos para o projeto Starbucks"

Sync-Starbucks-Playbooks

Write-Host ""
Write-Host "Processo finalizado." -ForegroundColor Green

if ($DryRun) {
    Write-Host ""
    Write-Host "Nada foi alterado. Para aplicar, rode:"
    Write-Host ".\pos_reorganizacao_datascience.ps1 -Execute"
}
else {
    Write-Host ""
    Write-Host "Valide com:"
    Write-Host "tree /F .\projetos\starbucks-customer-rewards-program-dataset"
    Write-Host "tree /F .\projetos\inferencia-causal"
}


