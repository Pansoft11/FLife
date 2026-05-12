# FEA Import Foundation

This directory is reserved for plugin-style result importers.

Planned adapters:

- ANSYS result import.
- Abaqus ODB-derived stress history import.
- Nastran OP2/PCH import.

Importer contract:

```txt
discover(file) -> metadata
extract_stress(file, selection) -> tensor/time-history payload
normalize_units(payload) -> MPa-based solver input
```

The goal is to keep vendor-specific parsing isolated from the FLIFE solver API.
