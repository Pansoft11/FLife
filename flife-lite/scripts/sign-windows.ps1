param(
  [Parameter(Mandatory=$true)]
  [string]$Path
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $Path)) {
  throw "File to sign does not exist: $Path"
}

if (-not $env:FLIFE_CODESIGN_THUMBPRINT) {
  Write-Host "FLIFE_CODESIGN_THUMBPRINT not set; leaving artifact unsigned for local/dev build: $Path"
  exit 0
}

$timestamp = $env:FLIFE_CODESIGN_TIMESTAMP
if (-not $timestamp) {
  $timestamp = "http://timestamp.digicert.com"
}

Set-AuthenticodeSignature `
  -FilePath $Path `
  -Certificate (Get-ChildItem Cert:\CurrentUser\My\$env:FLIFE_CODESIGN_THUMBPRINT) `
  -TimestampServer $timestamp `
  -HashAlgorithm SHA256 | Format-List
