# Auto YouTube Pipeline — Windows Launcher
# Run this to start the always-on scheduler, or use individual commands below.
$ErrorActionPreference = "Continue"
$venvPath = "$PSScriptRoot\.venv"
$scriptsDir = "$PSScriptRoot\scripts"
$outputDir = "$PSScriptRoot\output"

# Activate venv or create one
if (!(Test-Path "$venvPath\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    & python -m venv $venvPath
    & "$venvPath\Scripts\pip.exe" install -q -r "$PSScriptRoot\requirements.txt"
}
& "$venvPath\Scripts\python.exe" "$scriptsDir\pipeline.py" @args
