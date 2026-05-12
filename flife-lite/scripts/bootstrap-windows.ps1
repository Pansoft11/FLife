$ErrorActionPreference = "Continue"

function Test-CommandVersion($Name, $VersionArg = "--version") {
  $command = Get-Command $Name -ErrorAction SilentlyContinue
  if (-not $command) {
    Write-Host "[MISSING] $Name" -ForegroundColor Yellow
    return $false
  }
  Write-Host "[OK] $Name -> $($command.Source)"
  try { & $Name $VersionArg } catch { Write-Host "Version check failed: $($_.Exception.Message)" -ForegroundColor Yellow }
  return $true
}

function Add-PathIfExists($PathValue) {
  if ((Test-Path $PathValue) -and ($env:PATH -notlike "*$PathValue*")) {
    $env:PATH = "$PathValue;$env:PATH"
    Write-Host "[PATH] Added $PathValue"
  }
}

Write-Host "FLIFE Lite Windows bootstrap"
Write-Host "============================"

Add-PathIfExists "$env:USERPROFILE\.cargo\bin"
Add-PathIfExists "C:\Program Files\nodejs"
Add-PathIfExists "$env:LOCALAPPDATA\Programs\Python\Python311"
Add-PathIfExists "$env:LOCALAPPDATA\Programs\Python\Python312"

$ok = $true
$ok = (Test-CommandVersion "git") -and $ok
$ok = (Test-CommandVersion "node") -and $ok
$ok = (Test-CommandVersion "npm") -and $ok
$ok = (Test-CommandVersion "python") -and $ok
$ok = (Test-CommandVersion "rustc") -and $ok
$ok = (Test-CommandVersion "cargo") -and $ok

$vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vswhere) {
  $vs = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 Microsoft.VisualStudio.Component.Windows10SDK.19041 -property installationPath
  if ($vs) {
    Write-Host "[OK] Visual Studio Build Tools -> $vs"
  } else {
    Write-Host "[MISSING] Visual Studio Build Tools with MSVC + Windows SDK components" -ForegroundColor Yellow
    $ok = $false
  }
} else {
  Write-Host "[MISSING] vswhere / Visual Studio Installer" -ForegroundColor Yellow
  $ok = $false
}

$cl = Get-Command "cl.exe" -ErrorAction SilentlyContinue
if ($cl) {
  Write-Host "[OK] MSVC linker/compiler visible -> $($cl.Source)"
} else {
  Write-Host "[MISSING] cl.exe is not visible. Use 'Developer PowerShell for VS' or run vcvars64.bat." -ForegroundColor Yellow
  $ok = $false
}

$sdk = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin" -ErrorAction SilentlyContinue
if ($sdk) {
  Write-Host "[OK] Windows SDK detected"
} else {
  Write-Host "[MISSING] Windows SDK" -ForegroundColor Yellow
  $ok = $false
}

if (-not $ok) {
  Write-Host ""
  Write-Host "Install URLs:"
  Write-Host "- Rust: https://rustup.rs/"
  Write-Host "- Visual Studio Build Tools: https://aka.ms/vs/17/release/vs_BuildTools.exe"
  Write-Host "- Node.js LTS: https://nodejs.org/en/download"
  Write-Host "- Python: https://www.python.org/downloads/windows/"
  Write-Host "- Git: https://git-scm.com/download/win"
  Write-Host ""
  Write-Host "Visual Studio workload/components:"
  Write-Host "- Desktop development with C++"
  Write-Host "- MSVC v143"
  Write-Host "- Windows 10/11 SDK"
  Write-Host "- C++ CMake tools for Windows"
  Write-Host ""
  Write-Host "After installing, restart VS Code and run: npm run bootstrap:windows"
  exit 1
}

npm run doctor:windows
