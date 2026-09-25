$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '..\.venv\Scripts\python.exe'
& $python -m ruff check .
& $python -m ruff format --check .
& $python -m pytest
& $python scripts\verify_release.py
Push-Location (Join-Path $PSScriptRoot '..\frontend')
try {
    npm test
    npm run build
}
finally {
    Pop-Location
}
