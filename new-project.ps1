param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$Target,

    [Parameter(Mandatory = $false)]
    [string]$ProjectName,

    [Parameter(Mandatory = $false)]
    [switch]$Force,

    [Parameter(Mandatory = $false)]
    [switch]$InitGit,

    [Parameter(Mandatory = $false)]
    [switch]$KeepExamples,

    [Parameter(Mandatory = $false)]
    [switch]$Interactive
)

$ErrorActionPreference = "Stop"

function Read-YesNo {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Prompt,
        [Parameter(Mandatory = $false)]
        [bool]$Default = $false
    )

    $suffix = if ($Default) { "[Y/n]" } else { "[y/N]" }

    while ($true) {
        $answer = (Read-Host "$Prompt $suffix").Trim().ToLowerInvariant()
        if ([string]::IsNullOrWhiteSpace($answer)) {
            return $Default
        }

        switch ($answer) {
            "y" { return $true }
            "yes" { return $true }
            "s" { return $true }
            "sim" { return $true }
            "n" { return $false }
            "no" { return $false }
            "nao" { return $false }
        }

        Write-Host "Resposta invalida. Use y/n."
    }
}

function Ask-MissingValues {
    Write-Host ""
    Write-Host "=== SFK — New Project Wizard ==="
    Write-Host ""

    if ([string]::IsNullOrWhiteSpace($script:Target)) {
        while ([string]::IsNullOrWhiteSpace($script:Target)) {
            $script:Target = (Read-Host "Pasta destino do novo projeto").Trim()
        }
    }

    if ([string]::IsNullOrWhiteSpace($script:ProjectName)) {
        $defaultProjectName = Split-Path -Leaf $script:Target
        $inputProjectName = (Read-Host "Nome do projeto [$defaultProjectName]").Trim()
        if ([string]::IsNullOrWhiteSpace($inputProjectName)) {
            $script:ProjectName = $defaultProjectName
        } else {
            $script:ProjectName = $inputProjectName
        }
    }

    if (-not $PSBoundParameters.ContainsKey("InitGit")) {
        $script:InitGit = Read-YesNo "Inicializar git automaticamente?" $false
    }

    if (-not $PSBoundParameters.ContainsKey("KeepExamples")) {
        $script:KeepExamples = Read-YesNo "Manter arquivos *_EXAMPLE.md?" $false
    }

    if (-not $PSBoundParameters.ContainsKey("Force")) {
        $targetPath = [System.IO.Path]::GetFullPath($script:Target)
        $hasContent = (Test-Path $targetPath) -and (Get-ChildItem $targetPath -Force -ErrorAction SilentlyContinue | Select-Object -First 1)
        if ($hasContent) {
            $script:Force = Read-YesNo "Destino nao vazio. Permitir escrita com --force?" $false
        } else {
            $script:Force = $false
        }
    }
}

if ($Interactive -or [string]::IsNullOrWhiteSpace($Target)) {
    Ask-MissingValues
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Scaffolder = Join-Path $ScriptDir "tools\jb_kit_turbo.py"

if (-not (Test-Path $Scaffolder)) {
    throw "Scaffolder not found at '$Scaffolder'."
}

$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    $PythonCmd = Get-Command py -ErrorAction SilentlyContinue
}

if (-not $PythonCmd) {
    throw "Python was not found in PATH. Install Python 3 and try again."
}

$Args = @($Scaffolder, $Target)

if ($ProjectName) {
    $Args += @("--project-name", $ProjectName)
}
if ($Force) {
    $Args += "--force"
}
if ($InitGit) {
    $Args += "--init-git"
}
if ($KeepExamples) {
    $Args += "--keep-examples"
}

& $PythonCmd.Source @Args
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
    exit $ExitCode
}
