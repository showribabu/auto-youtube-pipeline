# Auto YouTube Pipeline — Windows Launcher
$ErrorActionPreference = "Continue"
$venvPython = "$PSScriptRoot\.venv\Scripts\python.exe"
$scriptsDir = "$PSScriptRoot\scripts"

if (Test-Path $venvPython) {
    $pythonExe = $venvPython
} else {
    $pythonExe = (Get-Command python).Source
}

Write-Host "Running Auto YouTube Pipeline with: $pythonExe"
& "$pythonExe" "$scriptsDir\pipeline.py" @args
