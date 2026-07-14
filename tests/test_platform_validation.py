import time
import httpx

GATEWAY = "http://gateway:8000"
EVIDENCE = "http://evidence-service:8200"


def test_account_takeover_flow():
    # trigger scenario
    with httpx.Client() as c:
        r = c.post(f"{GATEWAY}/api/v1/debug/publish-event", json={"scenario": "account_takeover", "tenant_id": "tenant-001"}, timeout=10.0)
        assert r.status_code == 200
        body = r.json()
        assert body.get("status") in ("published_scenario", "published")

    # poll evidence service graph until expected nodes appear
    found = False
    deadline = time.time() + 30
    resp = None
    while time.time() < deadline:
        try:
            resp = httpx.get(f"{EVIDENCE}/api/v1/debug/graph", timeout=5.0)
            if resp.status_code != 200:
                time.sleep(1)
                continue
            j = resp.json()
            nodes = j.get("nodes", [])
            props_list = [n.get("properties", {}) for n in nodes]
            ids = " ".join([str(p) for p in props_list])
            # check presence of key items
            if any("acct-1234" in str(p) for p in props_list) and any("txn-9999" in str(p) for p in props_list) and any("user-42" in str(p) for p in props_list) and any("ben-55" in str(p) for p in props_list):
                found = True
                break
        except Exception:
            pass
        time.sleep(1)

    assert found, f"Expected nodes not found; last response: {resp.text if resp is not None else 'no resp'}"

    # basic relationship check
    rels = resp.json().get("relationships", [])
    assert isinstance(rels, list)
    assert len(rels) >= 1
