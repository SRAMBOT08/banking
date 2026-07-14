from app.knowledge_registry.manager import RegistryManager
from app.engine.matcher import match_pattern_graph


def make_sample_evidence():
    return {
        "nodes": [
            {"properties": {"device_id": "device-900", "user_id": "user-42"}},
            {"properties": {"beneficiary_id": "ben-55"}},
            {"properties": {"transaction_id": "txn-9999", "account_id": "acct-1234"}},
        ],
        "relationships": []
    }


def test_load_and_match():
    registry = RegistryManager('patterns')
    registry.load()
    eg = make_sample_evidence()
    matched, missing, edges = match_pattern_graph(registry, 'account_takeover', eg)
    assert 'device_id' in matched
    assert 'beneficiary_id' in matched
    assert 'transaction_id' in matched
    assert missing == []
    assert ('device', 'transaction') in edges
