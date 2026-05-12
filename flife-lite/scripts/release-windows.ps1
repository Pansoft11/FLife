$ErrorActionPreference = "Stop"

$releaseRoot = "release"
$installerDir = Join-Path $releaseRoot "installer"
$portableDir = Join-Path $releaseRoot "portable"
$checksumsDir = Join-Path $releaseRoot "checksums"
$manifestsDir = Join-Path $releaseRoot "manifests"
$reportsDir = Join-Path $releaseRoot "reports"

function Ensure-Dir($PathValue) {
  New-Item -ItemType Directory -Force -Path $PathValue | Out-Null
}

function Write-Manifest($Status, $Message) {
  $manifest = [ordered]@{
    product = "FLIFE Lite"
    version = (Get-Content package.json | ConvertFrom-Json).version
    channel = "RC1"
    status = $Status
    message = $Message
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    artifacts = @{}
  }
  Get-ChildItem $releaseRoot -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    $rel = Resolve-Path -Relative $_.FullName
    $manifest.artifacts[$rel] = @{
      bytes = $_.Length
      sha256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    }
  }
  $manifest | ConvertTo-Json -Depth 8 | Out-File (Join-Path $manifestsDir "release-manifest.json") -Encoding utf8
}

if (Test-Path $releaseRoot) { Remove-Item -LiteralPath $releaseRoot -Recurse -Force }
Ensure-Dir $installerDir
Ensure-Dir $portableDir
Ensure-Dir $checksumsDir
Ensure-Dir $manifestsDir
Ensure-Dir $reportsDir
Ensure-Dir "build"

npm run bootstrap:windows
npm ci
npm run lint
npm run typecheck
$env:PYTHONPATH = "python_engine;src;.."
python -m pytest tests -q -p no:cacheprovider
python -c "from licensing.server.database import SCHEMA; from licensing.server.main import app; print(app.title); assert 'licenses' in SCHEMA"
npm run build:report

Copy-Item build\bundle-report.json (Join-Path $reportsDir "bundle-report.json") -Force

npm run tauri:build

$releaseExe = Get-ChildItem src-tauri\target\release -Filter "*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
$installerExe = Get-ChildItem src-tauri\target\release\bundle -Recurse -Filter "*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1

if ($releaseExe) {
  Copy-Item $releaseExe.FullName (Join-Path $portableDir "FLIFE-Lite.exe") -Force
}
if ($installerExe) {
  Copy-Item $installerExe.FullName (Join-Path $installerDir "FLIFE-Lite-Setup.exe") -Force
}

Copy-Item dist (Join-Path $portableDir "dist") -Recurse -Force
Copy-Item python_engine (Join-Path $portableDir "python_engine") -Recurse -Force
Copy-Item src\licensing (Join-Path $portableDir "licensing") -Recurse -Force
Copy-Item update-manifest.json (Join-Path $manifestsDir "update-manifest.json") -Force
Copy-Item docs\release-notes.md (Join-Path $releaseRoot "release-notes.md") -Force

Compress-Archive -Path (Join-Path $portableDir "*") -DestinationPath (Join-Path $portableDir "FLIFE-Lite-Portable.zip") -Force

Get-ChildItem $releaseRoot -Recurse -File | ForEach-Object {
  "{0}  {1}" -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash, (Resolve-Path -Relative $_.FullName)
} | Out-File (Join-Path $checksumsDir "SHA256SUMS.txt") -Encoding ascii

Write-Manifest "complete" "RC1 release artifacts generated."

node scripts/validate-release.mjs
Write-Host "RC1 release artifacts generated under $releaseRoot"
