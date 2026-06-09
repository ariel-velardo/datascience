param(
    [switch]$Execute,
    [switch]$ArchiveRootVenv
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$DryRun = -not $Execute.IsPresent

$Projetos = Join-Path $Root "projetos"
$Starbucks = Join-Path $Projetos "starbucks-customer-rewards-program-dataset"
$Causal = Join-Path $Projetos "inferencia-causal"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "### $Message" -ForegroundColor Cyan
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

function Move-Safe {
    param(
        [string]$SourceRelative,
        [string]$DestinationDir,
        [string]$NewName = ""
    )

    $Source = Join-Path $Root $SourceRelative

    if (-not (Test-Path -LiteralPath $Source)) {
        Write-Host "[IGNORADO] NÃ£o encontrado: $SourceRelative"
        return
    }

    Ensure-Dir $DestinationDir

    if ($NewName -ne "") {
        $FileName = $NewName
    }
    else {
        $FileName = Split-Path $Source -Leaf
    }

    $Destination = Join-Path $DestinationDir $FileName

    if (Test-Path -LiteralPath $Destination) {
        throw "Destino jÃ¡ existe: $Destination. Resolva antes de executar para evitar sobrescrita."
    }

    if ($DryRun) {
        Write-Host "[PREVIEW] Moveria: $Source -> $Destination"
    }
    else {
        Move-Item -LiteralPath $Source -Destination $Destination
        Write-Host "[OK] Movido: $SourceRelative -> $Destination"
    }
}

function Write-FileIfMissing {
    param(
        [string]$Path,
        [string]$Content
    )

    if (Test-Path -LiteralPath $Path) {
        Write-Host "[IGNORADO] Arquivo jÃ¡ existe: $Path"
        return
    }

    if ($DryRun) {
        Write-Host "[PREVIEW] Criaria arquivo: $Path"
    }
    else {
        Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
        Write-Host "[OK] Arquivo criado: $Path"
    }
}

function Create-VenvIfMissing {
    param([string]$ProjectPath)

    $VenvPath = Join-Path $ProjectPath ".venv"

    if (Test-Path -LiteralPath $VenvPath) {
        Write-Host "[OK] .venv jÃ¡ existe: $VenvPath"
        return
    }

    if ($DryRun) {
        Write-Host "[PREVIEW] Criaria ambiente virtual em: $VenvPath"
    }
    else {
        Write-Host "[EXECUTANDO] Criando .venv em: $VenvPath"
        python -m venv $VenvPath
        Write-Host "[OK] .venv criada: $VenvPath"
    }
}

function Archive-RootVenvIfRequested {
    $RootVenv = Join-Path $Root ".venv"
    $ArchivedVenv = Join-Path $Root ".venv_workspace_antiga"

    if (-not (Test-Path -LiteralPath $RootVenv)) {
        Write-Host "[OK] NÃ£o existe .venv na raiz para arquivar."
        return
    }

    if (-not $ArchiveRootVenv.IsPresent) {
        Write-Host "[AVISO] Existe uma .venv na raiz. Ela serÃ¡ mantida."
        Write-Host "        Depois, se quiser arquivar automaticamente, rode com: -ArchiveRootVenv"
        return
    }

    if (Test-Path -LiteralPath $ArchivedVenv) {
        throw "JÃ¡ existe $ArchivedVenv. NÃ£o vou sobrescrever."
    }

    if ($DryRun) {
        Write-Host "[PREVIEW] Renomearia .venv da raiz para: .venv_workspace_antiga"
    }
    else {
        Rename-Item -LiteralPath $RootVenv -NewName ".venv_workspace_antiga"
        Write-Host "[OK] .venv da raiz arquivada como: .venv_workspace_antiga"
    }
}

Write-Host ""
Write-Host "Raiz detectada: $Root" -ForegroundColor Yellow

if (-not (Test-Path -LiteralPath (Join-Path $Root "AGENTS.md"))) {
    Write-Host ""
    Write-Host "[AVISO] NÃ£o encontrei AGENTS.md na raiz atual."
    Write-Host "Confirme se vocÃª estÃ¡ realmente dentro da pasta DATASCIENCE antes de executar."
}

if ($DryRun) {
    Write-Host ""
    Write-Host "Modo atual: PREVIEW. Nenhum arquivo serÃ¡ alterado." -ForegroundColor Yellow
    Write-Host "Para executar de verdade, rode:"
    Write-Host ".\reorganizar_datascience_com_venv.ps1 -Execute"
}
else {
    Write-Host ""
    Write-Host "Modo atual: EXECUÃ‡ÃƒO REAL." -ForegroundColor Green
}

Write-Step "Criando estrutura principal"

Ensure-Dir $Projetos
Ensure-Dir $Starbucks
Ensure-Dir $Causal

Write-Step "Criando subpastas do projeto Starbucks"

Ensure-Dir (Join-Path $Starbucks "notebooks")

Write-Step "Criando subpastas do projeto InferÃªncia Causal"

Ensure-Dir (Join-Path $Causal "estudos")
Ensure-Dir (Join-Path $Causal "notebooks")
Ensure-Dir (Join-Path $Causal "projetos")
Ensure-Dir (Join-Path $Causal "referencias")

Write-Step "Movendo arquivos e pastas atuais para os projetos corretos"

Move-Safe "app" $Starbucks
Move-Safe "backend" $Starbucks
Move-Safe "data" $Starbucks
Move-Safe "simulacao_elasticidade_uplift.ipynb" (Join-Path $Starbucks "notebooks")
Move-Safe "playbooks_tecnicos" $Causal

if (Test-Path -LiteralPath (Join-Path $Root "README.md")) {
    Move-Safe "README.md" $Starbucks
}

Write-Step "Criando READMEs e requirements.txt"

$RootReadme = @"
# Datascience

Workspace pessoal para projetos de CiÃªncia de Dados, Machine Learning, InferÃªncia Causal, CRM Analytics, CrÃ©dito, Forecasting, ExperimentaÃ§Ã£o e PortfÃ³lio.

## Estrutura

- `projetos/starbucks-customer-rewards-program-dataset/`: projeto prÃ¡tico de treino com o dataset Starbucks Customer Rewards Program.
- `projetos/inferencia-causal/`: estudos, playbooks, notebooks e projetos de inferÃªncia causal.

## Regra geral

A raiz deve conter apenas arquivos gerais do workspace.

Cada projeto deve ficar dentro da pasta `projetos/` e ter seu prÃ³prio ambiente virtual `.venv`.
"@

$StarbucksReadme = @"
# Starbucks Customer Rewards Program Dataset

Projeto de treino para praticar anÃ¡lise de dados, CRM Analytics, elasticidade, uplift modeling, inferÃªncia causal e otimizaÃ§Ã£o de decisÃ£o usando o dataset Starbucks Customer Rewards Program.

## Estrutura

- `app/`: aplicaÃ§Ã£o ou interface do projeto.
- `backend/`: APIs, serviÃ§os auxiliares ou lÃ³gica de backend.
- `data/`: bases de dados.
- `notebooks/`: anÃ¡lises exploratÃ³rias, modelagem e simulaÃ§Ãµes.
- `.venv/`: ambiente virtual isolado do projeto.
- `requirements.txt`: dependÃªncias do projeto.
"@

$CausalReadme = @"
# InferÃªncia Causal

Pasta destinada a estudos, playbooks, notebooks e projetos relacionados a inferÃªncia causal.

## Estrutura

- `playbooks_tecnicos/`: materiais conceituais e guias de estudo.
- `estudos/`: anotaÃ§Ãµes, resumos e fichamentos.
- `notebooks/`: experimentos, simulaÃ§Ãµes e provas de conceito.
- `projetos/`: aplicaÃ§Ãµes prÃ¡ticas completas.
- `referencias/`: artigos, livros, links e materiais de apoio.
- `.venv/`: ambiente virtual isolado para estudos e experimentos.
- `requirements.txt`: dependÃªncias usadas nos estudos.
"@

$GitIgnore = @"
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd

# Virtual environments
.venv/
venv/
env/

# Jupyter
.ipynb_checkpoints/

# Dados sensÃ­veis ou grandes
*.csv
*.xlsx
*.parquet
*.db
*.sqlite

# Sistema
.DS_Store
Thumbs.db

# VS Code
.vscode/
"@

Write-FileIfMissing (Join-Path $Root "README.md") $RootReadme
Write-FileIfMissing (Join-Path $Starbucks "README.md") $StarbucksReadme
Write-FileIfMissing (Join-Path $Causal "README.md") $CausalReadme
Write-FileIfMissing (Join-Path $Starbucks "requirements.txt") ""
Write-FileIfMissing (Join-Path $Causal "requirements.txt") ""
Write-FileIfMissing (Join-Path $Root ".gitignore") $GitIgnore

Write-Step "Criando uma .venv para cada projeto"

Create-VenvIfMissing $Starbucks
Create-VenvIfMissing $Causal

Write-Step "Tratando .venv antiga da raiz"

Archive-RootVenvIfRequested

Write-Host ""
Write-Host "Processo finalizado." -ForegroundColor Green

if ($DryRun) {
    Write-Host ""
    Write-Host "Nada foi alterado. Para aplicar de verdade, rode:"
    Write-Host ".\reorganizar_datascience_com_venv.ps1 -Execute"
}
else {
    Write-Host ""
    Write-Host "ReorganizaÃ§Ã£o aplicada com sucesso."
    Write-Host ""
    Write-Host "Para verificar a estrutura:"
    Write-Host "tree /F .\projetos"
}
