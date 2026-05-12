# Session Recovery

Autosave snapshots are stored under `%LOCALAPPDATA%/FLIFE/recovery/`.

The recovery layer is intentionally file-based for offline-first desktop use:

- `autosave-current.json` tracks the latest open project state.
- Timestamped snapshots retain the last known good project payload.
- Corrupted `.flifeproj` archives are quarantined before restore attempts.

Future implementation hooks:

- Snapshot before solver execution.
- Snapshot after import mapping changes.
- Restore prompt on next startup after abnormal shutdown.
