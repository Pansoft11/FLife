from pathlib import Path

from flife_lite_engine.material_library import search_materials, seed_material_library
from flife_lite_engine.project import create_project_archive, read_project_manifest
from flife_lite_engine.reporting import render_report_html, write_report_bundle
from licensing.local_license.offline import create_offline_request
from licensing.server.state import SubscriptionState, derive_subscription_state


ARTIFACT_DIR = Path("flife-lite/build/test-artifacts")


def test_project_archive_roundtrip():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    project = create_project_archive(
        ARTIFACT_DIR / "bracket.flifeproj",
        {"solver": "Dirlik", "material": "Steel", "settings": {"safety_factor": 1.2}},
    )

    manifest = read_project_manifest(project)

    assert manifest["version"] == "1.0"
    assert manifest["schema_version"] == "1.1"
    assert manifest["solver"] == "Dirlik"
    assert manifest["created_by"] == "FLIFE Lite"


def test_report_and_material_library():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    html = render_report_html({"project": "Bracket", "material": "SAE 4140", "life_seconds": 1200})
    outputs = write_report_bundle(ARTIFACT_DIR / "reports", {"project": "Bracket", "method": "Dirlik"})
    library = seed_material_library(ARTIFACT_DIR / "materials.json")

    assert "Engineering Conclusions" in html
    assert Path(outputs["html"]).exists()
    assert search_materials(library, query="4140")


def test_subscription_state_derivation():
    assert derive_subscription_state(
        active=True,
        revoked=True,
        expires_at="2999-01-01T00:00:00+00:00",
    ) == SubscriptionState.REVOKED


def test_offline_activation_request_file():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    request_file = create_offline_request(ARTIFACT_DIR / "activation", "user@example.com", "FLIFE-TEST-KEY")

    assert request_file.suffix == ".flreq"
    assert request_file.exists()
