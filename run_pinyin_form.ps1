# Start the desktop form: .\run_pinyin_form.ps1
$ErrorActionPreference = 'Stop'

$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\pythonw.exe'
$formPath = Join-Path $PSScriptRoot 'pinyin_form.pyw'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw 'Project Python was not found. Create .venv and install requirements.txt first.'
}

Start-Process -FilePath $pythonPath -ArgumentList ('"{0}"' -f $formPath) -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
