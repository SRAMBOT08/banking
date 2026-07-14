from app.knowledge_registry.manager import RegistryManager


def test_registry_manager_load(tmp_path):
    # create a temp patterns dir with a sample yaml
    pdir = tmp_path / "patterns"
    pdir.mkdir()
    f = pdir / "sample.yaml"
    f.write_text("""
name: sample_attack
version: 1.0
nodes: []
edges: []
""")

    rm = RegistryManager(str(pdir))
    rm.load()
    stats = rm.get_stats()
    assert stats['pattern_count'] == 1
    p = rm.get_attack_pattern('sample_attack')
    assert p is not None
