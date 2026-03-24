$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

# Resolve a usable Python launcher
$pythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py -3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} else {
    throw "No Python launcher found. Install Python and add it to PATH."
}

Write-Host ("Using Python launcher: " + $pythonCmd)

# Create venv if missing
if (-not (Test-Path ".venv")) {
    Write-Host "[1/5] Creating virtual environment..."
    Invoke-Expression "$pythonCmd -m venv .venv"
} else {
    Write-Host "[1/5] .venv already exists, skip create."
}

# Validate venv python exists
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual env python not found at: $venvPython. venv creation likely failed."
}

Write-Host "[2/5] Upgrading pip..."
& $venvPython -m pip install --upgrade pip

if (-not (Test-Path "requirements.txt")) {
    throw "requirements.txt not found"
}

Write-Host "[3/5] Installing dependencies..."
& $venvPython -m pip install -r "requirements.txt"

if ((-not (Test-Path ".env")) -and (Test-Path ".env.example")) {
    Write-Host "[4/5] .env missing, copying from .env.example"
    Copy-Item ".env.example" ".env"
} else {
    Write-Host "[4/5] .env exists or .env.example missing, skip copy."
}

Write-Host "[5/5] Starting FastAPI on http://127.0.0.1:8000"
& $venvPython -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
