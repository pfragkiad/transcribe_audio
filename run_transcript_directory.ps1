# Run without arguments: .\run_transcript_directory.ps1
# Edit all settings here. There are no command-line parameters.
# $InputDirectory = $PSScriptRoot    # Example: 'D:\lessons'
$InputDirectory = 'D:\ch\Pimsleur Conversational Mandarin Chinese'
$Extension = 'mp3'                # mp3 or .mp3 (case-insensitive)
$Mode = 'mixed'                   # mixed or chinese
$Pinyin = $true                   # $true: inline Pinyin; $false: original text
$Format = 'txt'                   # txt or srt
$Device = 'auto'                  # auto, cuda, or cpu
$Model = 'large-v3'
$OutputDir = Join-Path $PSScriptRoot 'output'
$TargetDirectory = ''            # Optional: absolute path, or relative to $InputDirectory
$ListOnly = $false                # $true: list matching files without processing

# Examples: copy the desired settings above.
# Directory: $InputDirectory = 'D:\lessons'
# Extension: $Extension = 'mp3'
# Mixed without Pinyin:   $Mode = 'mixed';   $Pinyin = $false
# Mixed with Pinyin:      $Mode = 'mixed';   $Pinyin = $true
# Chinese without Pinyin: $Mode = 'chinese'; $Pinyin = $false
# Chinese with Pinyin:    $Mode = 'chinese'; $Pinyin = $true
# TXT output: $Format = 'txt'
# SRT output: $Format = 'srt'
# Preview matching files: $ListOnly = $true
# Move results elsewhere: $TargetDirectory = 'D:\results'
# Move into the input directory's results folder: $TargetDirectory = 'results'
# Keep results in output/: $TargetDirectory = ''
# Files directly inside the directory are processed in filename order.
# Output: output/<input name>.<format>, with no internal directories.
# If script execution is disabled:
# powershell -ExecutionPolicy Bypass -File .\run_transcript_directory.ps1

$ErrorActionPreference = 'Stop'
if (-not $InputDirectory) { $InputDirectory = $PSScriptRoot }
if (-not $OutputDir) { $OutputDir = Join-Path $PSScriptRoot 'output' }
if (-not (Test-Path -LiteralPath $InputDirectory -PathType Container)) {
    throw "Input directory not found: $InputDirectory"
}
$Extension = $Extension.Trim().TrimStart('.')
if ($Extension -notmatch '^[a-zA-Z0-9]+$') {
    throw 'Specify one extension, for example mp3 or .mp3 (without wildcards).'
}
$files = @(Get-ChildItem -LiteralPath $InputDirectory -File |
    Where-Object { $_.Extension -ieq ".$Extension" } |
    Sort-Object Name)
if ($files.Count -eq 0) {
    Write-Output "No .$Extension files found in $InputDirectory."
    return
}
if ($ListOnly) {
    $files | ForEach-Object { Write-Output $_.FullName }
    return
}

$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw 'Project Python was not found. Create .venv and install requirements.txt first.'
}
$scriptPath = Join-Path $PSScriptRoot 'transcript.py'
$finalDirectory = $OutputDir
if (-not [string]::IsNullOrWhiteSpace($TargetDirectory)) {
    $targetBasePath = $TargetDirectory
    if (-not [System.IO.Path]::IsPathRooted($TargetDirectory)) {
        $targetBasePath = Join-Path $InputDirectory $TargetDirectory
    }
    $finalDirectory = [System.IO.Path]::GetFullPath($targetBasePath)
    New-Item -ItemType Directory -Path $finalDirectory -Force | Out-Null
}
$failures = @()
for ($index = 0; $index -lt $files.Count; $index++) {
    $file = $files[$index]
    Write-Output "[$($index + 1)/$($files.Count)] $($file.Name)"
    $pythonArguments = @(
        '-u', $scriptPath, $file.FullName,
        '--mode', $Mode, '--format', $Format,
        '--device', $Device, '--model', $Model,
        '--output-dir', $OutputDir
    )
    if ($Pinyin) { $pythonArguments += '--pinyin' }
    & $pythonPath @pythonArguments
    if ($LASTEXITCODE -ne 0) {
        $failures += $file.Name
        Write-Warning "Failed: $($file.Name) (exit code $LASTEXITCODE). Continuing."
        continue
    }
    if (-not [string]::IsNullOrWhiteSpace($TargetDirectory)) {
        $sourcePath = [System.IO.Path]::GetFullPath((Join-Path $OutputDir ($file.BaseName + '.' + $Format)))
        $targetPath = Join-Path $finalDirectory ($file.BaseName + '.' + $Format)
        if (-not $sourcePath.Equals($targetPath, [System.StringComparison]::OrdinalIgnoreCase)) {
            try {
                Move-Item -LiteralPath $sourcePath -Destination $targetPath -Force
                Write-Output "Moved to: $targetPath"
            }
            catch {
                $failures += $file.Name
                Write-Warning "Could not move $($file.Name): $_. Result remains in $OutputDir."
            }
        }
    }
}
Write-Output "Completed $($files.Count - $failures.Count)/$($files.Count) files. Output: $finalDirectory"
if ($failures.Count -gt 0) {
    throw "Transcription failed for: $($failures -join ', ')"
}
