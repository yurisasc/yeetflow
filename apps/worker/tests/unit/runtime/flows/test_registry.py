from uuid import NAMESPACE_URL, uuid5

import yaml

from app.runtime.flows.registry import FlowRegistry


def test_manifest_without_id_generates_deterministic_uuid(tmp_path):
    flows_dir = tmp_path / "flows"
    manifest_dir = flows_dir / "sample-flow"
    manifest_dir.mkdir(parents=True)

    manifest_data = {
        "name": "Sample Flow",
        "key": "sample-flow",
        "description": "Flow without explicit id",
        "config": {"steps": []},
    }
    (manifest_dir / "manifest.yaml").write_text(
        yaml.safe_dump(manifest_data), encoding="utf-8"
    )

    registry = FlowRegistry(flows_dir)

    manifest = registry.get_manifest_by_key("sample-flow")
    assert manifest is not None

    expected_id = str(uuid5(NAMESPACE_URL, "sample-flow"))
    assert manifest.id == expected_id
