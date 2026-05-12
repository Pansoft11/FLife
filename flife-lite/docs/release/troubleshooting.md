# Troubleshooting

## Build Toolchain Missing

Run:

```powershell
npm run bootstrap:windows
```

Install Rust via rustup and Visual Studio Build Tools with Desktop development with C++.

## License Server Unavailable

Check `FLIFE_LICENSE_SERVER` and verify `/license-status`.

## Crash Recovery

Crash logs are stored in `%LOCALAPPDATA%/FLIFE/crash-dumps/`.
