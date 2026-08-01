"""Tests for The 511 manifest consistency."""

from __future__ import annotations

import json
from pathlib import Path

from custom_components.the511.const import DOMAIN, NAME

MANIFEST_PATH = Path("custom_components/the511/manifest.json")


def test_manifest_fields():
    """The manifest must declare the integration correctly."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["domain"] == DOMAIN
    assert manifest["name"] == NAME
    assert manifest["config_flow"] is True
    assert manifest["integration_type"] == "service"
    assert manifest["iot_class"] == "cloud_polling"


def test_manifest_codeowners():
    """Codeowners should reference a real GitHub handle."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["codeowners"]
    for owner in manifest["codeowners"]:
        assert owner.startswith("@")
