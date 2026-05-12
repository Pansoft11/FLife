# FLIFE Lite Build Instructions

## Windows Toolchain

Run:

```powershell
npm run doctor:windows
```

Required:

- Node.js and npm.
- Rust MSVC toolchain.
- Visual Studio Build Tools with Desktop development with C++.
- Windows 10/11 SDK.

## Build Frontend

```powershell
npm run build:report
```

The bundle report is written to `build/bundle-report.json`.

## Build Installer

```powershell
npm run release:windows
```

Expected output:

```txt
build/release/
src-tauri/target/release/
src-tauri/target/release/bundle/nsis/
```

## Code Signing

Set signing secrets through environment variables only. Do not commit certificates or private keys.

```powershell
$env:FLIFE_CODESIGN_THUMBPRINT="..."
$env:FLIFE_CODESIGN_TIMESTAMP="http://timestamp.digicert.com"
```
