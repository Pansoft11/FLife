# FLIFE Lite Release Notes

## 0.1.0 Production Hardening Preview

- Added Windows build doctor and release automation scripts.
- Hardened Tauri release profile for smaller binaries.
- Added NSIS license screen and installer hook placeholders.
- Split Plotly charts into lazy-loaded results module.
- Added `.flifeproj` compressed project archive support.
- Added HTML/DOCX-ready report generation foundation.
- Added material library seed/search utilities.
- Added solver job manager for process isolation, timeouts, cancellation, and progress status.
- Added subscription state primitives for trial, active, expired, suspended, revoked, and offline grace states.
- Added update manifest placeholder and code-signing-ready release path.

Native Windows artifacts require Rust/Cargo and MSVC Build Tools on the packaging machine.
