# FLIFE Lite Setup Guide

## Prerequisites

- Node.js 20 or newer
- Python 3.10 or newer
- Rust stable with Cargo for Tauri packaging
- Microsoft WebView2 Runtime on Windows

## Install

```powershell
cd flife-lite
npm install
python -m venv .venv
.\.venv\Scripts\python -m pip install -r python_engine\requirements.txt
```

## Run Frontend Preview

```powershell
npm run dev
```

## Run Licensing Server

```powershell
$env:PYTHONPATH="src"
$env:FLIFE_LICENSE_SECRET="replace-with-a-long-random-secret"
python -m uvicorn licensing.server.main:app --host 127.0.0.1 --port 8088
```

Development seed key:

```txt
FLIFE-TRIAL-DEV-2026
```

## Run Native Desktop

After installing Rust:

```powershell
npm run tauri:dev
```

## Package Installer

```powershell
npm run tauri:build
```

The NSIS installer is generated under `src-tauri\target\release\bundle\nsis`.
