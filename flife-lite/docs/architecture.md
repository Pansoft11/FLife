# FLIFE Lite Architecture

FLIFE Lite is split into four layers:

1. React + TypeScript workbench UI in `src/frontend`.
2. Tauri command bridge in `src-tauri`.
3. Python fatigue engine wrapper in `python_engine/flife_lite_engine`.
4. FastAPI licensing service in `src/licensing/server`.
5. Release engineering scripts in `scripts`.
6. Future extension layers under `src/backend` for recovery, telemetry, FEA importers, and AI hooks.

The existing open-source `FLife/` package remains the fatigue solver source of truth. The desktop product calls it through a stable Python request/response API so future solvers, FEA importers, batch execution, and cloud execution can be added without rewriting the UI.

## Runtime Flow

```txt
React UI -> Tauri command -> Python CLI -> FLife solver -> JSON result -> React charts
```

The app also has browser fallback data so UI development can continue before a native Tauri build is available.

## Licensing Flow

```txt
React activation page -> Tauri command -> local encrypted store -> FastAPI /activate
```

The server returns a signed license token. The local client stores only the token payload encrypted under `%LOCALAPPDATA%/FLIFE`. Machine fingerprinting is hashed before it leaves the device.

## Production Notes

- Replace the development `FLIFE_LICENSE_SECRET`.
- Ship a bundled Python runtime or compile the engine with PyInstaller for a fully standalone installer.
- Add a signed updater endpoint before enabling Tauri updater.
- Move SQLite to PostgreSQL for enterprise/floating licenses.
- Use `.flifeproj` archives for reproducible projects.
- Keep FEA vendor adapters isolated behind importer contracts.
