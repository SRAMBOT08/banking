import json
from pathlib import Path

from app.events import BaseEvent
from app.pipeline.extractor import extract
from app.pipeline.resolver import resolve_entities, canonical_id
from app.pipeline.relationship_builder import build_relationships
from app.repo.inmemory import InMemoryGraphRepo
from app.pipeline.graph_engine import GraphEngine


DATA_FILE = Path(__file__).parents[2] / "tests" / "integration_data" / "scenario_simple_transactions.json"
EXPECTED_FILE = Path(__file__).parents[2] / "tests" / "expected_graphs" / "scenario_simple_transactions_expected.json"


def load_events(path):
    with open(path, "r", encoding="utf-8") as fh:
        arr = json.load(fh)
    events = [BaseEvent.model_validate(e) for e in arr]
    return events


def compare_graph(repo: InMemoryGraphRepo, expected: dict):
    missing_nodes = []
    for node in expected.get("nodes", []):
        if node["canonical_id"] not in repo.nodes:
            missing_nodes.append(node)
    missing_rels = []
    for rel in expected.get("relationships", []):
        if not any(r for r in repo.relationships if r["from"] == rel["from"] and r["to"] == rel["to"] and r["type"] == rel["type"]):
            missing_rels.append(rel)
    return {"missing_nodes": missing_nodes, "missing_relationships": missing_rels}


def test_integration_simple_transactions(tmp_path):
    events = load_events(DATA_FILE)
    repo = InMemoryGraphRepo()
    engine = GraphEngine(repo)

    for ev in events:
        extracted = extract(ev)
        resolved = resolve_entities(extracted)
        rels = build_relationships(resolved)
        engine.apply(resolved, rels)

    expected_raw = json.loads(open(EXPECTED_FILE).read())
    # regenerate expected canonical ids deterministically using resolver.canonical_id
    expected = {"nodes": [], "relationships": expected_raw.get("relationships", [])}
    for n in expected_raw.get("nodes", []):
        # labels expected like ["USER"] -> entity type 'user'
        label = n.get("labels", [None])[0]
        etype = label.lower() if label else ""
        props = n.get("properties", {})
        cid = canonical_id(etype, props)
        expected["nodes"].append({"canonical_id": cid, "labels": n.get("labels", []), "properties": props})

    report = compare_graph(repo, expected)

    # write report
    out = tmp_path / "report.json"
    out.write_text(json.dumps(report, indent=2))

    assert not report["missing_nodes"] and not report["missing_relationships"], f"Integration mismatch: {report}"

*** End Patch
