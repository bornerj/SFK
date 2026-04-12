param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$Target,

    [Parameter(Mandatory = $false)]
    [switch]$Yes,

    [Parameter(Mandatory = $false)]
    [switch]$DryRun,

    [Parameter(Mandatory = $false)]
    [switch]$Interactive
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile   = Join-Path $ScriptDir "update-project.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] $Message"
    [System.IO.File]::AppendAllText($LogFile, $line + [System.Environment]::NewLine, [System.Text.Encoding]::UTF8)
    Write-Host $Message
}

# Start log entry
[System.IO.File]::AppendAllText($LogFile, [System.Environment]::NewLine + "--- SFK Update Project Session Start: " + (Get-Date) + " ---" + [System.Environment]::NewLine, [System.Text.Encoding]::UTF8)

# --- Interactive wizard if no target given ---
function Ask-MissingValues {
    Write-Host ""
    Write-Host "=== SFK - Update Project Wizard ==="
    Write-Host ""

    if ([string]::IsNullOrWhiteSpace($script:Target)) {
        while ([string]::IsNullOrWhiteSpace($script:Target)) {
            $script:Target = (Read-Host "Path to the existing project to update").Trim()
        }
    }
}

if ($Interactive -or [string]::IsNullOrWhiteSpace($Target)) {
    Ask-MissingValues
}

$Updater = Join-Path $ScriptDir "tools\sfk_updater.py"

if (-not (Test-Path $Updater)) {
    Write-Log "ERROR: Updater engine not found at '$Updater'."
    exit 1
}

$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    $PythonCmd = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $PythonCmd) {
    Write-Log "ERROR: Python was not found in PATH. Install Python 3 and try again."
    exit 1
}

Write-Log "Updating project: $Target"
if ($DryRun) { Write-Log "Mode: dry-run (no files will be written)" }

$PyArgs = @($Updater, $Target)
if ($Yes)    { $PyArgs += "--yes"     }
if ($DryRun) { $PyArgs += "--dry-run" }

Write-Log "Running updater..."

$output = & $PythonCmd.Source @PyArgs 2>&1
$ExitCode = $LASTEXITCODE

foreach ($line in $output) {
    $lineStr = $line.ToString()
    Write-Host $lineStr
    [System.IO.File]::AppendAllText($LogFile, $lineStr + [System.Environment]::NewLine, [System.Text.Encoding]::UTF8)
}

if ($ExitCode -ne 0) {
    Write-Log "ERROR: Update failed with exit code $ExitCode. Check $LogFile for details."
    exit $ExitCode
}

Write-Log "Update complete!"