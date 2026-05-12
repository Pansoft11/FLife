from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_VERSION = "1.1"


def create_project_archive(output_path: str | Path, metadata: dict[str, Any], files: list[str | Path] | None = None) -> Path:
    path = Path(output_path)
    if path.suffix != ".flifeproj":
        path = path.with_suffix(".flifeproj")
    path.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "version": "1.0",
        "schema_version": PROJECT_VERSION,
        "project_id": metadata.get("project_id", ""),
        "solver": metadata.get("solver", "Dirlik"),
        "solver_version": metadata.get("solver_version", "FLife 2.1.0"),
        "material": metadata.get("material", "Steel"),
        "created_by": "FLIFE Lite",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "dependencies": metadata.get("dependencies", []),
        "metadata": metadata,
    }

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
        archive.writestr("settings/settings.json", json.dumps(metadata.get("settings", {}), indent=2))
        archive.writestr("reports/.keep", "")
        archive.writestr("reports/cache/.keep", "")
        archive.writestr("results/.keep", "")
        archive.writestr("input/.keep", "")
        archive.writestr("thumbnail/thumbnail.json", json.dumps(metadata.get("thumbnail", {"type": "placeholder"}), indent=2))
        for file_path in files or []:
            source = Path(file_path)
            if source.exists() and source.is_file():
                archive.write(source, f"input/{source.name}")
    return path


def read_project_manifest(project_path: str | Path) -> dict[str, Any]:
    with zipfile.ZipFile(project_path, "r") as archive:
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        return migrate_manifest(manifest)


def migrate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if "schema_version" not in manifest:
        manifest["schema_version"] = "1.1"
    manifest.setdefault("project_id", "")
    manifest.setdefault("solver_version", "unknown")
    manifest.setdefault("updated_at", manifest.get("created_at", ""))
    manifest.setdefault("dependencies", [])
    return manifest
