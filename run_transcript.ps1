# Run without arguments: .\run_transcript.ps1
# Edit these settings to select exactly one UTF-8 output file.
$InputFile = Join-Path $PSScriptRoot 'CD1 Lesson 1.mp3'
$Mode = 'mixed'     # mixed or chinese
$Pinyin = $true     # $true: Chinese word(pinyin); $false: original text
$Format = 'txt'     # txt or srt
$Device = 'auto'    # auto, cuda, or cpu
$Model = 'large-v3'
$OutputDir = Join-Path $PSScriptRoot 'output'

# Examples: copy one pair of settings above.
# Mixed without Pinyin:   $Mode = 'mixed';   $Pinyin = $false
# Mixed with Pinyin:      $Mode = 'mixed';   $Pinyin = $true
# Chinese without Pinyin: $Mode = 'chinese'; $Pinyin = $false
# Chinese with Pinyin:    $Mode = 'chinese'; $Pinyin = $true
# TXT output: $Format = 'txt'
# SRT output: $Format = 'srt'
# CPU: $Device = 'cpu'
# CUDA: $Device = 'cuda'
# Python equivalents (use .venv\Scripts\python.exe):
# python transcript.py "CD1 Lesson 1.mp3" --mode mixed
# python transcript.py "CD1 Lesson 1.mp3" --mode mixed --pinyin
# python transcript.py "CD1 Lesson 1.mp3" --mode chinese
# python transcript.py "CD1 Lesson 1.mp3" --mode chinese --pinyin
# python transcript.py "CD1 Lesson 1.mp3" --mode mixed --pinyin --format srt
# python transcript.py "CD1 Lesson 1.mp3" --mode chinese --pinyin --format srt
# Output: output/<input name>.<format> (regardless of mode or Pinyin).
# If script execution is disabled:
# powershell -ExecutionPolicy Bypass -File .\run_transcript.ps1

$ErrorActionPreference = 'Stop'

$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw 'Project Python was not found. Create .venv and install requirements.txt first.'
}
if (-not (Test-Path -LiteralPath $InputFile -PathType Leaf)) {
    throw "Input file not found: $InputFile"
}

$scriptPath = Join-Path $PSScriptRoot 'transcript.py'
$pythonArguments = @(
    $scriptPath, $InputFile,
    '--mode', $Mode,
    '--format', $Format,
    '--device', $Device,
    '--model', $Model,
    '--output-dir', $OutputDir
)
if ($Pinyin) {
    $pythonArguments += '--pinyin'
}

& $pythonPath @pythonArguments
if ($LASTEXITCODE -ne 0) {
    throw "Transcription failed with exit code $LASTEXITCODE."
}
