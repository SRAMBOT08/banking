from app.patterns.loader import load_patterns
from app.engine.matcher import match_pattern
from app.engine.scorer import score_match

def make_evidence_graph():
    return {
        "nodes": [
            {"properties": {"device_id": "device-900", "user_id": "user-42"}},
            {"properties": {"beneficiary_id": "ben-55"}},
            {"properties": {"transaction_id": "txn-9999", "account_id": "acct-1234"}},
        ],
        "relationships": []
    }


def test_account_takeover_pattern():
    patterns = load_patterns('patterns')
    pat = patterns.get('account_takeover')
    eg = make_evidence_graph()
    matched, missing = match_pattern(pat, eg)
    score, breakdown = score_match(pat, matched, missing)
    assert 'device_id' in matched
    assert 'beneficiary_id' in matched
    assert 'transaction_id' in matched
    assert score >= 90 or score >= 60  # ensure scoring produced positive score
