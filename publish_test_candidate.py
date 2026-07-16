#!/usr/bin/env python3
"""Publish test candidate directly to investigation.candidates.v1"""
import json
from confluent_kafka import Producer
import time

try:
    print("Connecting to Kafka at kafka:9092...")
    producer = Producer({"bootstrap.servers": "kafka:9092"})
    print("✓ Connected to Kafka!")
    
    candidate = {
        "candidate_id": "phase1-test-001",
        "tenant_id": "tenant-001",
        "pattern_name": "Account Takeover",
        "pattern_version": "1.0.0",
        "confidence": 0.85,
        "explanation": {
            "matched_nodes": 3,
            "total_nodes": 4,
            "confidence_factors": {
                "authentication_anomaly": 0.9,
                "device_change": 0.8,
                "geo_anomaly": 0.75
            }
        },
        "evidence_refs": [
            {"evidence_id": "evt-001", "type": "authentication_event"},
            {"evidence_id": "evt-002", "type": "device_change"},
            {"evidence_id": "evt-003", "type": "geo_anomaly"}
        ]
    }
    
    print(f"\nPublishing test candidate...")
    print(f"  Pattern: {candidate['pattern_name']}")
    print(f"  Confidence: {candidate['confidence']}")
    
    producer.produce(
        'investigation.candidates.v1',
        value=json.dumps(candidate).encode('utf-8'),
        key=candidate['candidate_id'].encode('utf-8')
    )
    producer.poll(0)
    producer.flush(5)
    
    print(f"✓ Published successfully to investigation.candidates.v1!")
    print("\nCandidate should now trigger Phase 1 workflow in investigation-service...")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
