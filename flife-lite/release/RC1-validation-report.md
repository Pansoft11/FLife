# FLIFE Lite RC1 Validation Report

Generated: 2026-05-12T10:55:24.882Z

| Check | Status | Path |
| --- | --- | --- |
| Installer artifact | PENDING | `release/installer/FLIFE-Lite-Setup.exe` |
| Portable ZIP | PENDING | `release/portable/FLIFE-Lite-Portable.zip` |
| Checksums | PENDING | `release/checksums/SHA256SUMS.txt` |
| Release manifest | PENDING | `release/manifests/release-manifest.json` |
| Bundle report | PENDING | `release/reports/bundle-report.json` |

Manual validation checklist:

- Installer launches and installs to selected directory.
- Desktop and Start menu shortcuts are created.
- Portable ZIP launches from a writable folder or USB drive.
- Activation succeeds against licensing server.
- Offline mode remains valid through grace period.
- Report generation creates HTML and DOCX-ready output.
- Recovery snapshots are written after workspace changes.
- Updater manifest parses and signature placeholder is replaced for production.
- Crash dumps are written to `%LOCALAPPDATA%/FLIFE/crash-dumps/`.