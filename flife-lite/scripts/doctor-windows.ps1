$ErrorActionPreference = "Continue"

function Test-Command($Name) {
  $command = Get-Command $Name -ErrorAction SilentlyContinue
  if ($command) {
    Write-Host "[OK] $Name -> $($command.Source)"
    & $Name --version
    return $true
  }
  Write-Host "[MISSING] $Name is not on PATH" -ForegroundColor Yellow
  return $false
}

$ok = $true
$ok = (Test-Command "node") -and $ok
$ok = (Test-Command "npm") -and $ok
$ok = (Test-Command "rustc") -and $ok
$ok = (Test-Command "cargo") -and $ok

$cl = Get-Command "cl.exe" -ErrorAction SilentlyContinue
if ($cl) {
  Write-Host "[OK] MSVC compiler -> $($cl.Source)"
} else {
  Write-Host "[MISSING] MSVC compiler cl.exe is not on PATH" -ForegroundColor Yellow
  $ok = $false
}

$windowsKits = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin" -ErrorAction SilentlyContinue
if ($windowsKits) {
  Write-Host "[OK] Windows 10/11 SDK detected"
} else {
  Write-Host "[MISSING] Windows SDK was not detected" -ForegroundColor Yellow
  $ok = $false
}

if (-not $ok) {
  Write-Host ""
  Write-Host "Remediation:"
  Write-Host "1. Install Rust from https://rustup.rs and choose the MSVC toolchain."
  Write-Host "2. Install Visual Studio Build Tools with 'Desktop development with C++'."
  Write-Host "3. Include MSVC v143, Windows 10/11 SDK, and C++ CMake tools."
  Write-Host "4. Restart VS Code or open a Developer PowerShell and rerun npm run doctor:windows."
  exit 1
}

Write-Host "[READY] Windows build toolchain is ready."
