from app.knowledge_registry.manager import RegistryManager, RegistryValidationError
from app.knowledge_registry.providers import ProviderManager, AttackPatternProvider
from app.knowledge_registry.validator import validate_registry
from app.knowledge_registry.models import AttackPattern


def write_pattern(directory, name, version, **extra):
    import yaml
    payload = {"name": name, "version": version, "nodes": [], "edges": [], **extra}
    (directory / f"{name}-{version}.yaml").write_text(yaml.safe_dump(payload), encoding="utf-8")


def test_version_resolution_cache_and_reload(tmp_path):
    write_pattern(tmp_path, "sample", "1.2")
    write_pattern(tmp_path, "sample", "1.10")
    registry = RegistryManager(str(tmp_path), cache_ttl=300)
    registry.load()
    assert registry.get_latest_pattern("sample").version == "1.10"
    registry.list_attack_patterns()
    assert registry.get_registry_statistics().cache_hit_rate > 0
    registry.reload_registry()
    assert registry.get_latest_pattern("sample").version == "1.10"


def test_provider_manager_is_static_and_typed():
    pattern = AttackPattern(name="sample", version="1")
    providers = ProviderManager({"attack_patterns": AttackPatternProvider([pattern])})
    assert providers.get("attack_patterns", "sample", "name") is pattern
    assert providers.search("attack_patterns", "sample") == [pattern]


def test_validation_detects_relationship_and_cycles():
    findings = validate_registry({
        "a": {"name": "a", "version": "1", "nodes": [], "edges": [{"from": "x", "to": "y"}], "dependencies": ["b"]},
        "b": {"name": "b", "version": "1", "nodes": [], "edges": [], "dependencies": ["a"]},
    })
    codes = {finding["code"] for finding in findings}
    assert "orphan_relationship" in codes
    assert "cyclic_dependency_graph" in codes


def test_startup_rejects_critical_validation(tmp_path):
    write_pattern(tmp_path, "bad", "1", severity="catastrophic")
    registry = RegistryManager(str(tmp_path))
    try:
        registry.load()
    except RegistryValidationError as exc:
        assert any(finding["code"] == "invalid_severity" for finding in exc.findings)
    else:
        raise AssertionError("critical registry validation did not fail startup")
