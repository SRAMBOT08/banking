# SentinelIQ
## AI-Powered Evidence Intelligence & Decision Platform for Banking Security

**Product Requirements Document & Technical Specification**

**Version:** 1.0 (MVP Freeze)  
**Date:** 2025  
**Status:** Ready for Implementation

---

# Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Product Vision & Strategy](#product-vision--strategy)
4. [Core Architecture](#core-architecture)
5. [Detailed System Layers](#detailed-system-layers)
6. [Feature Specifications](#feature-specifications)
7. [User Stories & Use Cases](#user-stories--use-cases)
8. [MVP Scope](#mvp-scope)
9. [Technical Requirements](#technical-requirements)
10. [Success Metrics & KPIs](#success-metrics--kpis)
11. [Glossary & Definitions](#glossary--definitions)
12. [Appendices](#appendices)

---

# EXECUTIVE SUMMARY

## What is SentinelIQ?

SentinelIQ is an **Evidence Intelligence & Decision Platform** that transforms fragmented cybersecurity telemetry and banking transactions into explainable, evidence-backed investigations.

Positioned between enterprise detection systems (SIEM, EDR, fraud engines) and operational workflows (ticketing, notification, escalation), SentinelIQ enables security analysts to investigate incidents faster, understand root causes more thoroughly, and make confident decisions with complete transparency.

## The Core Problem

Banks operate multiple security systems that generate thousands of independent alerts daily:

* SIEM detects suspicious login patterns
* EDR detects malware
* Fraud Engine flags high-value transactions
* Threat Intelligence matches IPs against threat feeds
* IAM logs privilege escalation

**But these systems work in isolation.**

SOC analysts manually switch between tools, correlate events, piece together timelines, and guess at what actually happened. This is time-consuming, error-prone, and leaves evidence trails incomplete.

**SentinelIQ solves this by:**
1. Correlating events across all systems into a unified Evidence Graph
2. Automatically generating investigation hypotheses
3. Evaluating evidence for/against each hypothesis
4. Providing explainable confidence scores
5. Recommending evidence-backed actions
6. Simulating outcomes before decisions are made
7. Learning from completed cases for future investigations

## Why This Matters

| Traditional Approach | SentinelIQ Approach |
|---|---|
| Analyst sees 15 alerts | Analyst sees 1 investigation with 15 pieces of evidence |
| "Risk Score: 87%" | "Account Takeover: 78% | Legitimate: 22% because..." |
| Manual correlation | Automated, evidence-backed correlation |
| No transparency | Every conclusion traces back to evidence |
| No learning | Each case enriches future investigations |

## Market Position

```
Detection Systems (SIEM, EDR, Fraud Engine, PAM, etc.)
           ↓
SentinelIQ: Evidence Intelligence Layer ← NEW
           ↓
Execution Systems (ServiceNow, Slack, Teams, etc.)
```

**SentinelIQ is not:**
- A detection tool (SIEM replacements exist)
- A ticketing system (ServiceNow exists)
- A general-purpose AI platform (ChatGPT exists)

**SentinelIQ is:**
- An investigation orchestrator
- An evidence correlation engine
- An explainable decision support system
- A learning platform for security operations

---

# PROBLEM STATEMENT

## Banking Security Landscape

Modern banks face an expanding threat surface:

* **Cybersecurity threats**: Account takeover, insider threats, credential stuffing, ransomware
* **Financial fraud**: Money mules, unauthorized transfers, beneficiary fraud
* **Quantum risks**: Harvest-Now-Decrypt-Later attacks on long-term sensitive data
* **Operational complexity**: Multiple disconnected security systems

## Current State

Banks have invested in point solutions:

| System | Purpose | Output |
|---|---|---|
| SIEM (e.g., Splunk) | Centralized logging & correlation | Alerts on anomalous events |
| EDR (e.g., CrowdStrike) | Endpoint security monitoring | Malware detection alerts |
| IAM (e.g., Okta) | Identity & access management | Privilege/access anomaly alerts |
| Fraud Detection | Transactional analysis | Transaction risk scores |
| PAM (e.g., BeyondTrust) | Privileged access monitoring | Access violation alerts |
| Threat Intelligence | External threat feeds | IP/domain/hash reputation |
| Core Banking | Transaction ledger | Transaction records |

**Each system works independently.**

## The Gap

When an actual attack occurs:

```
Time 0:00 - SIEM: "Suspicious login from India"
Time 0:05 - EDR: "Malware detected on device"
Time 0:10 - Fraud Engine: "High-value transfer flagged"
Time 0:15 - Threat Intelligence: "IP matches known botnet"
Time 0:20 - Core Banking: "Beneficiary account in Russia"
```

**What happened?**
- Is this coordinated? Or coincidence?
- How confident are we it's an attack?
- What's the most likely attack vector?
- What evidence contradicts this?
- What else do we need to know?
- What should we do?

**SOC Analyst must answer these manually, spending 15-45 minutes per incident.**

## Problem Statement Requirements

SentinelIQ must:

1. **Correlate cybersecurity telemetry with transactional behaviour** - connect security events to financial impact
2. **Detect cyber threats proactively** - identify threats before they reach their final stage
3. **Identify fraud patterns** - recognize multi-stage fraud sequences
4. **Detect quantum-related attack indicators** - monitor for HNDL and cryptographic vulnerabilities
5. **Reduce false positives** - provide evidence-based confidence instead of raw alerts
6. **Provide explainable AI-driven threat intelligence** - every conclusion must be traceable to evidence

---

# PRODUCT VISION & STRATEGY

## One-Line Vision

**SentinelIQ transforms fragmented cybersecurity telemetry and banking transactions into evidence-backed investigations, helping SOC analysts make faster, explainable, and confident security decisions while seamlessly integrating with enterprise operational workflows.**

## Core Philosophy

SentinelIQ answers **nine critical questions** that most security tools ignore:

| Question | Addressed By |
|----------|--------------|
| What happened? | Evidence Intelligence Engine |
| How are events connected? | Evidence Graph & Relationship Registry |
| What attack is most likely? | Hypothesis Library & Investigation Engine |
| What evidence supports this? | Evidence Intelligence Engine |
| What evidence contradicts this? | Multi-hypothesis Reasoning |
| What evidence is still missing? | Investigation Engine |
| How confident are we? | Confidence Engine |
| What should we do? | Decision Intelligence & Action Recommendations |
| What happens if we choose each action? | Decision Outcome Simulator |

## Strategic Pillars

### 1. Evidence-First Architecture
Every conclusion, relationship, and confidence score is built on traceable evidence. This is the core intellectual property.

### 2. Explainability by Design
No black boxes. Analysts can understand why SentinelIQ reached its conclusions.

### 3. Graceful Degradation
Missing data sources reduce confidence but don't break investigations.

### 4. Enterprise Integration
Seamless connection to existing ticketing, notification, and workflow systems.

### 5. Continuous Learning
Each completed investigation becomes organizational knowledge for future cases.

## Product Differentiation

| Dimension | Competitors | SentinelIQ |
|-----------|---|---|
| **Core Focus** | Detection (more alerts) | Investigation (fewer, better alerts) |
| **Decision Making** | Risk scores | Evidence-backed hypotheses |
| **Transparency** | Black-box ML | Traceable reasoning |
| **Scope** | Single domain (cyber or fraud) | Cross-domain correlation |
| **Architecture** | Custom integrations | Evidence graph model scales |
| **Learning** | Batch retraining | Real-time case memory |

---

# CORE ARCHITECTURE

## System Overview Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   Enterprise Security Stack                      │
│                                                                   │
│  SIEM  │ EDR │ IAM │ Fraud Engine │ PAM │ Threat Intel │ Banking │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: Event Ingestion                      │
│           Receives events from all enterprise systems            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 2: Unified Event Model                        │
│          Normalizes all events to canonical schema               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         LAYER 3: Evidence Intelligence Engine                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Entity Extraction → Entity Resolution → Enrichment       │   │
│  │ ↓                                                         │   │
│  │ Relationship Registry → Relationship Builder → Evidence  │   │
│  │                                                  Graph    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           LAYER 4: Investigation Engine                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Hypothesis Library → Hypothesis Generation              │   │
│  │ ↓                                                         │   │
│  │ Investigation Engine → Confidence Calculation            │   │
│  │ ↓                                                         │   │
│  │ Multi-Hypothesis Reasoning & Missing Evidence Detection  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│             LAYER 5: Decision Intelligence                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Action Recommendations → Decision Policy Engine          │   │
│  │ ↓                                                         │   │
│  │ Decision Outcome Simulator → Impact Analysis             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [Analyst Approval Gate]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│        LAYER 6: Enterprise Execution Layer                       │
│    Ticketing │ Notification │ Workflow │ Escalation             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         LAYER 7: Investigation Memory                            │
│    Stores evidence graphs, outcomes, and lessons learned        │
└─────────────────────────────────────────────────────────────────┘
```

## Architectural Principles

### 1. Pipeline Architecture
Each layer has a single responsibility and passes structured output to the next layer.

### 2. Evidence-Centric Design
Every relationship, entity, and conclusion includes:
- Supporting evidence
- Confidence score
- Source reliability
- Timestamp
- Context

### 3. Graceful Degradation
Missing data sources reduce confidence but don't block investigations:

```
Threat Intelligence unavailable?
  ↓
  Confidence: 95% → 83%
  ↓
  Recommendation: "Additional confirmation needed (TI unavailable)"
  ↓
  Investigation continues
```

### 4. Extensibility via Registry
New event types and relationships are added declaratively, not by code changes.

### 5. Deterministic + AI Hybrid
- **Hypothesis generation**: Deterministic (rule-based attack patterns)
- **Hypothesis evaluation**: AI-driven (reasoning over evidence)
- **Decision making**: Policy-driven with human approval

This balance provides explainability without sacrificing sophistication.

---

# DETAILED SYSTEM LAYERS

## Layer 1: Event Ingestion

**Responsibility**: Receive events from all enterprise systems.

### Inputs

From production enterprise systems:
- SIEM (Splunk, ELK, etc.)
- EDR (CrowdStrike, Cortex, etc.)
- IAM (Okta, Azure AD, etc.)
- Fraud Engine (proprietary or vendor)
- PAM (BeyondTrust, Delinea, etc.)
- Threat Intelligence (external feeds)
- Core Banking System (transaction ledger)

For MVP: **Enterprise Threat Simulator** generates realistic event streams.

### Outputs

Raw events with metadata:
```json
{
  "source_system": "SIEM",
  "event_type": "LOGIN",
  "timestamp": "2025-01-15T14:23:45Z",
  "raw_event": {...},
  "ingestion_time": "2025-01-15T14:23:47Z",
  "source_reliability": 0.95
}
```

### Key Features

- **Multi-source ingestion**: REST API, webhooks, polling, streaming
- **Timestamp normalization**: All events converted to UTC
- **Source tracking**: Every event knows its origin
- **Rate limiting**: Prevents system overload
- **Deduplication**: Filters obvious duplicates

---

## Layer 2: Unified Event Model

**Responsibility**: Normalize heterogeneous event formats into a canonical schema.

### Input

Raw events from Layer 1.

### Transformation

```
Splunk Login Alert
{
  "user": "alice@bank.com",
  "src_ip": "192.168.1.1",
  "login_time": "2025-01-15 14:23:45"
}
        ↓
    [Normalization]
        ↓
Unified Event
{
  "event_type": "LOGIN",
  "entities": {
    "user": "alice@bank.com",
    "ip": "192.168.1.1"
  },
  "timestamp": "2025-01-15T14:23:45Z",
  "source_system": "SIEM",
  "source_reliability": 0.95
}
```

### Canonical Event Schema

```json
{
  "event_id": "string (UUID)",
  "event_type": "enum (LOGIN, TRANSACTION, ALERT, ...)",
  "entities": {
    "primary_entity": "string",
    "related_entities": ["string"]
  },
  "attributes": {
    "key": "value"
  },
  "timestamp": "ISO8601",
  "source_system": "string",
  "source_reliability": "float (0-1)",
  "raw_event": "object",
  "processing_metadata": {
    "ingestion_time": "ISO8601",
    "normalization_time": "ISO8601"
  }
}
```

### Supported Event Types

- **Authentication**: LOGIN, LOGOUT, MFA_CHALLENGE, PRIVILEGE_ESCALATION
- **Transactions**: TRANSFER, BENEFICIARY_ADD, WITHDRAWAL, DEPOSIT
- **Security**: MALWARE_DETECTED, SUSPICIOUS_ACTIVITY, THREAT_MATCH, ACCESS_DENIED
- **Device**: DEVICE_ENROLLMENT, DEVICE_COMPROMISE, OS_UPDATE, PATCH_STATUS
- **Network**: VPN_CONNECT, VPN_DISCONNECT, NETWORK_ANOMALY, IP_REPUTATION
- **Quantum**: CRYPTOGRAPHIC_ASSET_IDENTIFIED, QUANTUM_EXPOSURE_DETECTED

---

## Layer 3: Evidence Intelligence Engine

**Responsibility**: Transform normalized events into investigation-ready evidence.

This is the **intellectual core** of SentinelIQ.

### Architecture

```
Unified Event
     ↓
┌─────────────────────────────────────┐
│ Entity Extraction                   │
│ (User, Device, IP, Transaction...)  │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ Entity Resolution                   │
│ (Same person? Same device?)         │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ Evidence Quality Engine             │
│ (Reliability scoring)               │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ Context Enrichment                  │
│ (TI, baselines, health, quantum...) │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ Relationship Builder                │
│ (Edges between entities)            │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ Evidence Graph                      │
│ (Trusted knowledge base)            │
└─────────────────────────────────────┘
```

### 3.1 Entity Extraction

**Input**: Normalized events  
**Output**: Structured entities with type and attributes

**Extracted Entity Types**:

| Entity Type | Examples | Attributes |
|---|---|---|
| **Customer** | alice@bank.com, Customer-ID-123 | name, email, phone, risk_level |
| **Employee** | Employee-239 | name, department, role, access_level |
| **Device** | device-uuid | os, health_status, is_managed, last_seen |
| **Session** | session-uuid | start_time, end_time, auth_method, mfa_used |
| **Account** | bank account | account_type, balance, velocity_profile |
| **Transaction** | transaction-id | amount, currency, source, destination, timestamp |
| **Beneficiary** | beneficiary-id | name, account, country, risk_score |
| **IP Address** | 192.168.1.1 | country, threat_reputation, is_vpn, is_proxy |
| **Threat Indicator** | hash, domain, ip | type, reputation_score, observed_campaigns |
| **Cryptographic Asset** | key-id, certificate-id | algorithm, key_length, exposure_level |

**Example**:
```json
Input Event:
{
  "event_type": "LOGIN",
  "entities": {"user": "alice@bank.com", "ip": "203.15.4.99"},
  "attributes": {"device_id": "abc123", "mfa": true}
}

Extracted Entities:
[
  {
    "id": "customer-alice-001",
    "type": "CUSTOMER",
    "value": "alice@bank.com",
    "attributes": {"domain": "bank.com"}
  },
  {
    "id": "device-abc123",
    "type": "DEVICE",
    "value": "abc123",
    "attributes": {"os": "Windows", "health": "healthy"}
  },
  {
    "id": "ip-203.15.4.99",
    "type": "IP_ADDRESS",
    "value": "203.15.4.99",
    "attributes": {"country": "India", "threat_reputation": "clean"}
  }
]
```

### 3.2 Entity Resolution

**Input**: Extracted entities  
**Output**: De-duplicated entity references

**Problem**: The same real-world entity appears in different systems with different identifiers.

```
Customer Alice:
  SIEM calls her: alice@bank.com
  Core Banking calls her: CustomerID-123
  IAM calls her: Employee-239
  Fraud System calls her: AccountHolderID-X1A
```

**Solution**: Entity resolution merges these into one canonical entity.

**Resolution Strategy**:

1. **Deterministic matching** (high confidence):
   - Email address exact match
   - Employee ID exact match
   - Customer ID exact match

2. **Heuristic matching** (medium confidence):
   - Name + date-of-birth match
   - Phone number match
   - Device fingerprint match

3. **Manual resolution** (when ambiguous):
   - Flagged for analyst review
   - Investigation proceeds with both possibilities

**Example**:
```
Input entities:
  - alice@bank.com
  - CustomerID-123
  - Employee-239

Entity Resolution Output:
  entity_group_id: "entity-alice-merged-001"
  canonical_identifier: "alice@bank.com"
  aliases: ["CustomerID-123", "Employee-239"]
  resolution_confidence: 0.98
  resolution_method: "email_and_id_match"
```

### 3.3 Evidence Quality Engine

**Input**: Raw events  
**Output**: Reliability scores for each event

**Scoring Factors**:

| Factor | Scoring |
|--------|---------|
| **Source Reliability** | SIEM=0.95, EDR=0.93, Manual Alert=0.60 |
| **Data Completeness** | All fields present=1.0, Missing optional=0.85 |
| **Timestamp Consistency** | Logical order=1.0, Out of order=0.70 |
| **Duplicate Detection** | First occurrence=1.0, Known duplicate=0.30 |
| **Telemetry Staleness** | <5 min old=1.0, >1 hour old=0.70 |

**Calculation**:
```
reliability_score = 
  (source_reliability * 0.4) +
  (data_completeness * 0.3) +
  (timestamp_consistency * 0.2) +
  (duplicate_factor * 0.1)
```

**Output**:
```json
{
  "event_id": "event-001",
  "reliability_score": 0.89,
  "reliability_components": {
    "source": 0.95,
    "completeness": 0.85,
    "timestamp": 1.0,
    "duplicate": 1.0
  },
  "quality_issues": []
}
```

### 3.4 Context Enrichment

**Input**: Entities with reliability scores  
**Output**: Enriched entities with external intelligence

**Enrichment Sources**:

| Source | Data | Example |
|--------|------|---------|
| **Threat Intelligence** | IP/domain reputation, campaigns | "203.15.4.99: known botnet" |
| **Device Health** | OS, patches, antivirus status | "Windows 11 + latest patches" |
| **Behavioral Baseline** | User's normal patterns | "Alice typically logs in 9-5 from India" |
| **Geo-location** | IP geolocation | "203.15.4.99 located in Russia" |
| **Quantum Exposure** | Crypto algorithm inventory | "Device uses legacy RSA-1024" |
| **Historical Activity** | Previous transactions/logins | "Alice's avg transfer: ₹50k" |
| **Risk Scoring** | Entity risk level | "Device: 0.3 | User: 0.2" |

**Example**:
```
Before Enrichment:
{
  "type": "IP_ADDRESS",
  "value": "203.15.4.99"
}

After Enrichment:
{
  "type": "IP_ADDRESS",
  "value": "203.15.4.99",
  "enrichment": {
    "country": "Russia",
    "threat_feeds": [
      {"feed": "ABUSE_CH", "threat_type": "botnet", "confidence": 0.92}
    ],
    "historical_context": {
      "alice_login_history": "never from Russia",
      "login_baseline": "India only, 9-5 IST"
    },
    "quantum_context": "N/A"
  }
}
```

### 3.5 Relationship Registry

**Responsibility**: Define valid relationships between entities declaratively.

Instead of hardcoding graph logic in Python, relationships are defined in a registry.

**Benefits**:
- Adding new event types doesn't require code changes
- Relationships are auditable
- Easy to extend for quantum risk or new threat types

**Registry Format**:

```json
{
  "relationship_id": "LOGIN",
  "source_entity_type": "USER",
  "target_entity_type": "DEVICE",
  "description": "User logged in from device",
  "relationship_type": "LOGGED_IN_FROM",
  "supporting_event_types": ["LOGIN"],
  "evidence_required": true,
  "bidirectional": false,
  "time_window": "5m",
  "confidence_factors": {
    "mfa_present": 0.15,
    "device_known": 0.20,
    "location_expected": 0.25,
    "time_expected": 0.20,
    "threat_intel_match": -0.30
  }
}
```

**Pre-defined Relationships**:

| From | To | Relationship | Evidence Source |
|---|---|---|---|
| USER | DEVICE | LOGGED_IN_FROM | LOGIN event |
| DEVICE | IP_ADDRESS | USES_IP | Network telemetry |
| USER | TRANSACTION | INITIATED_TRANSACTION | Transaction log |
| TRANSACTION | BENEFICIARY | SENT_TO_BENEFICIARY | Transaction details |
| IP_ADDRESS | THREAT_INDICATOR | MATCHES_THREAT | Threat Intel |
| DEVICE | CRYPTOGRAPHIC_ASSET | CONTAINS_KEY | Inventory system |
| CRYPTOGRAPHIC_ASSET | QUANTUM_EXPOSURE | HAS_EXPOSURE | Crypto analysis |
| USER | USER | SIMILAR_BEHAVIOR_TO | Anomaly detection |

### 3.6 Relationship Builder

**Input**: Enriched entities + Relationship Registry  
**Output**: Evidence graph edges with confidence scores

**Process**:

1. For each pair of entities, check the Registry
2. If a valid relationship exists, evaluate supporting evidence
3. Calculate relationship confidence
4. Create edge with evidence references

**Example**:

```
Event: Alice logs in from device ABC using IP 203.15.4.99

Relationships to build:
  USER (alice) ---LOGGED_IN_FROM---> DEVICE (abc)
  DEVICE (abc) ---USES_IP---> IP_ADDRESS (203.15.4.99)
  IP_ADDRESS (203.15.4.99) ---MATCHES_THREAT---> THREAT (botnet_xyz)

Confidence Calculation for MATCHES_THREAT:
  threat_feed_agreement: 0.92
  historical_prevalence: 0.85
  temporal_recency: 0.75
  ---
  relationship_confidence = 0.84
```

**Output**:
```json
{
  "edge_id": "edge-001",
  "source_entity_id": "ip-203.15.4.99",
  "target_entity_id": "threat-botnet-xyz",
  "relationship_type": "MATCHES_THREAT",
  "confidence": 0.84,
  "confidence_breakdown": {
    "threat_feed_agreement": 0.92,
    "historical_prevalence": 0.85,
    "temporal_recency": 0.75
  },
  "supporting_evidence": [
    "event-001 (threat intel feed match)",
    "historical record (IP seen in botnet 3 times)"
  ],
  "created_time": "2025-01-15T14:25:00Z"
}
```

### 3.7 Evidence Graph

**Responsibility**: Store and query the unified knowledge base.

The Evidence Graph is the **source of truth** for all investigations.

**Structure**:

```
Nodes (Entities)
├── Customer (alice@bank.com)
├── Device (abc123)
├── IP (203.15.4.99)
├── Transaction (txn-001)
├── Beneficiary (receiver-xyz)
├── Threat Indicator (botnet)
└── Cryptographic Asset (key-rsa-1024)

Edges (Relationships)
├── alice --LOGGED_IN_FROM--> device (confidence: 0.99)
├── device --USES_IP--> 203.15.4.99 (confidence: 0.98)
├── 203.15.4.99 --MATCHES_THREAT--> botnet (confidence: 0.84)
├── alice --INITIATED_TRANSACTION--> txn-001 (confidence: 0.95)
├── txn-001 --SENT_TO_BENEFICIARY--> receiver (confidence: 0.99)
└── device --CONTAINS_KEY--> key-rsa-1024 (confidence: 0.92)
    └── HAS_EXPOSURE--> quantum-risk (confidence: 0.88)

Metadata
├── Timestamps (when each relationship was established)
├── Evidence references (which events support each edge)
├── Reliability scores (confidence in each connection)
├── Context (enrichment data)
└── Change history (audit trail)
```

**Storage Requirements**:

- Graph database (Neo4j, Amazon Neptune, etc.)
- Full-text search on entity properties
- Time-window queries
- Relationship path traversal
- Bulk ingestion support

**Query Examples**:

```cypher
# Find all entities related to Alice in the last 24 hours
MATCH (alice:User {id: "alice@bank.com"})
-[r:*1..5]-(related)
WHERE r.timestamp > datetime() - duration("P1D")
RETURN alice, related, r

# Find threat indicators connected to this transaction
MATCH (txn:Transaction {id: "txn-001"})
-[:INVOLVES*1..3]-(threat:Threat)
RETURN threat, path

# Find quantum exposure on devices used by this customer
MATCH (customer:Customer {id: "alice"})
-[:OWNS]-(device:Device)
-[:CONTAINS_KEY]-(key:CryptoAsset)
-[:HAS_EXPOSURE]-(quantum:QuantumRisk)
RETURN device, key, quantum
```

---



# Attack Knowledge Graph

[CONTENT PLACEHOLDER]

## Layer 4: Investigation Engine

**Responsibility**: Evaluate evidence against hypotheses, estimate confidence, identify missing evidence.

This layer implements the **investigation methodology** that experienced analysts use.

### Investigation Loop

```
Evidence Graph
     ↓
┌──────────────────────────────┐
│ Hypothesis Generation        │
│ (from Hypothesis Library)    │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│ For Each Hypothesis:         │
│ - Gather supporting evidence │
│ - Gather contradicting evid. │
│ - Identify missing evidence  │
│ - Calculate confidence       │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│ Multi-Hypothesis Reasoning   │
│ (don't force one answer)     │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│ Confidence >= 70%?           │
│ - Yes: Proceed to Decision   │
│ - No: Gather more evidence   │
└──────────────────────────────┘
```

### 4.1 Hypothesis Library

Pre-defined investigation templates based on known attack/fraud patterns.

**Hypothesis Template Structure**:

```json
{
  "hypothesis_id": "ACCOUNT_TAKEOVER",
  "name": "Account Takeover",
  "description": "Unauthorized access to customer account leading to fraud",
  "attack_stages": [
    "Compromised Credentials",
    "Unauthorized Login",
    "Malicious Activity",
    "Financial Harm"
  ],
  "required_evidence_graph_patterns": [
    {
      "pattern": "USER -[LOGIN]-> NEW_DEVICE",
      "indicates": "unusual access"
    },
    {
      "pattern": "IP -[MATCHES_THREAT]-> BOTNET",
      "indicates": "malicious source"
    },
    {
      "pattern": "USER -[INITIATED_TRANSACTION]-> LARGE_AMOUNT",
      "indicates": "financial harm"
    }
  ],
  "supporting_indicators": [
    "New device never seen before",
    "IP matches threat feed",
    "Login outside normal hours",
    "Login from unexpected geo",
    "Immediate high-value transaction",
    "Beneficiary in high-risk country",
    "MFA bypassed or not required",
    "Device has quantum-exposed keys"
  ],
  "contradicting_indicators": [
    "Customer confirms login",
    "IP is known/trusted VPN",
    "Transaction matches normal pattern",
    "Device is recognized as owned",
    "MFA successfully verified"
  ],
  "missing_evidence_checklist": [
    "Device health status",
    "EDR logs from device",
    "Customer notification status",
    "Beneficiary account info",
    "Previous transaction history"
  ],
  "confidence_scoring": {
    "new_device": 0.25,
    "threat_matched_ip": 0.20,
    "unusual_location": 0.15,
    "large_amount": 0.20,
    "rapid_escalation": 0.15,
    "malware_detected": 0.30,
    "customer_denial": -0.40
  },
  "recommended_actions": [
    "Hold Transaction",
    "Force MFA Re-authentication",
    "Notify Customer",
    "Escalate to Investigation Team",
    "Temporary Account Lock"
  ]
}
```

**Pre-defined Hypotheses for MVP**:

1. **Account Takeover**: Compromised credentials → unauthorized access → fraud
2. **Credential Stuffing**: Bulk login attempts → successful breach → activity
3. **Insider Threat**: Privileged access abuse → data exfiltration → harm
4. **Money Mule**: Compromised account → transfers to mule beneficiary → downstream cash-out
5. **Ransomware**: Malware infection → encryption → extortion demand
6. **Privilege Abuse**: Legitimate user exceeds authority → unauthorized activity
7. **Quantum Exposure**: Legacy crypto detected → HNDL risk identified

### 4.2 Investigation Engine

**Input**: Evidence Graph + Hypothesis Library  
**Output**: Investigation object with confidence, supporting/contradicting evidence

**Algorithm**:

```python
investigation = {
  "investigation_id": "inv-001",
  "hypotheses": []
}

for hypothesis in hypothesis_library:
  hypothesis_result = {
    "hypothesis_id": hypothesis.id,
    "name": hypothesis.name,
    "confidence": 0.0,
    "supporting_evidence": [],
    "contradicting_evidence": [],
    "missing_evidence": []
  }
  
  # Search graph for supporting patterns
  for pattern in hypothesis.required_evidence_graph_patterns:
    matches = graph.search(pattern)
    for match in matches:
      hypothesis_result.supporting_evidence.append({
        "pattern": pattern,
        "evidence": match,
        "strength": calculate_strength(match)
      })
  
  # Search graph for contradicting evidence
  for indicator in hypothesis.contradicting_indicators:
    contradictions = graph.find_contradictions(indicator)
    hypothesis_result.contradicting_evidence.extend(contradictions)
  
  # Identify missing evidence
  hypothesis_result.missing_evidence = identify_gaps(hypothesis, hypothesis_result)
  
  # Calculate confidence
  hypothesis_result.confidence = calculate_confidence(
    supporting_evidence,
    contradicting_evidence,
    missing_evidence,
    hypothesis.confidence_scoring
  )
  
  investigation.hypotheses.append(hypothesis_result)

return investigation
```

### 4.3 Confidence Calculation

**Input**: Supporting evidence, contradicting evidence, missing evidence, reliability scores  
**Output**: Confidence score (0-100%)

**Formula**:

```
base_score = sum(supporting_evidence_weights)

contradiction_penalty = sum(contradicting_evidence_weights)

missing_evidence_penalty = count(missing_evidence) * 0.05

confidence = 
  min(100,
    (base_score - contradiction_penalty - missing_evidence_penalty) *
    average_evidence_reliability
  )
```

**Example for Account Takeover**:

```
Supporting Evidence:
  + New device login: +25 (weight: 0.25, reliability: 1.0)
  + Threat-matched IP: +20 (weight: 0.20, reliability: 0.84)
  + Large amount transfer: +20 (weight: 0.20, reliability: 0.99)
  + Location outside baseline: +15 (weight: 0.15, reliability: 0.95)
  ────────────────────────────
  Subtotal: 80 points

Contradicting Evidence:
  - Customer confirmed login: -40 (weight: 0.40, reliability: 1.0)
  ────────────────────────────
  Penalty: -40 points

Missing Evidence:
  ? Device health status
  ? EDR logs
  ? Beneficiary verification
  ────────────────────────────
  Penalty: -15 points (3 missing * 0.05)

Base Confidence = 80 - 40 - 15 = 25

Average Evidence Reliability = 0.96

Final Confidence = 25 * 0.96 = 24%
```

**Confidence Tiers**:

```
95-100%  │ Near-Certain Attack (Immediate Action Recommended)
85-94%   │ Very High Confidence (Investigation + Quick Response)
70-84%   │ High Confidence (Gather More Evidence or Investigate)
50-69%   │ Medium Confidence (Monitoring / Low-Priority Investigation)
<50%     │ Low Confidence (No Action, Retain for Correlation)
```

### 4.4 Multi-Hypothesis Reasoning

**Principle**: Don't force a single answer when multiple hypotheses are viable.

**Example**:

```
Scenario: Alice logs in from new device in Russia at 2 AM

Hypothesis A: Account Takeover
  Confidence: 42%
  Evidence: New device, unexpected location, unusual time, threat-matched IP
  Contradicts: Customer available for contact, device could be owned

Hypothesis B: Legitimate Business Travel
  Confidence: 38%
  Evidence: Alice travels frequently for work, amount within limits
  Contradicts: 2 AM timestamp, no advance notice in system

Hypothesis C: Credential Stuffing Failure (Account Safe)
  Confidence: 20%
  Evidence: MFA prevented access, transaction blocked by rules
  Contradicts: Device recognized, IP already seen in other accounts

Result:
  [
    {hypothesis: "Account Takeover", confidence: 42%, action: "investigate"},
    {hypothesis: "Legitimate Travel", confidence: 38%, action: "verify"},
    {hypothesis: "Blocked Attack", confidence: 20%, action: "monitor"}
  ]
```

### 4.5 Missing Evidence Detection

**Responsibility**: Identify what data would increase confidence.

**Algorithm**:

```
For current investigation:
  1. List all supporting evidence present
  2. For each hypothesis, list "ideal evidence"
  3. Compare present vs. ideal
  4. Rank missing evidence by impact
  5. Recommend data sources to query
```

**Example Output**:

```
Account Takeover Investigation (Current Confidence: 42%)

Recommended Evidence Sources (Would increase confidence):

Priority 1 (High Impact):
  □ Device Health Report from EDR
    → Confidence delta: +25% if compromised, -15% if healthy
  □ Customer Verification Call
    → Confidence delta: +35% if customer denies, -40% if confirms
  □ Beneficiary Account History
    → Confidence delta: +20% if high-risk profile
    
Priority 2 (Medium Impact):
  □ Previous Transaction History for Alice
    → Confidence delta: +10% if anomalous, -5% if normal
  □ Device Ownership Verification
    → Confidence delta: +10% if device unknown, -15% if owned

Priority 3 (Low Impact):
  □ VPN/Proxy Status of IP
    → Confidence delta: +5% if confirmed malicious
```

---

## Layer 5: Decision Intelligence

**Responsibility**: Convert investigation results into explainable, evidence-backed operational recommendations.

### 5.1 Action Recommendations

**Input**: Investigation object (confidence scores + hypotheses)  
**Output**: Ranked list of recommended actions with explanations

**Recommendation Engine**:

```
For each hypothesis with confidence >= 50%:
  1. Look up recommended_actions in hypothesis template
  2. Filter actions based on confidence tier
  3. Rank by impact and feasibility
  4. Explain recommendation with evidence
```

**Confidence-Based Action Mapping**:

| Confidence | Recommended Actions | Rationale |
|---|---|---|
| >95% | Immediate hold, force MFA, notify customer | Attack highly likely |
| 85-95% | Hold + investigation, notify customer | Strong evidence of threat |
| 70-85% | Gather more evidence, light monitoring | Need confirmation |
| 50-70% | Continue monitoring, no hold | Inconclusive |
| <50% | Retain for future correlation | Insufficient evidence |

**Example Output**:

```json
{
  "investigation_id": "inv-001",
  "primary_hypothesis": {
    "id": "ACCOUNT_TAKEOVER",
    "confidence": 78,
    "confidence_tier": "high"
  },
  "recommended_actions": [
    {
      "action_id": "HOLD_TRANSACTION",
      "action": "Hold Transaction Pending Verification",
      "priority": "HIGH",
      "confidence_support": 78,
      "explanation": "Account Takeover hypothesis at 78% confidence based on: new device (high confidence), threat-matched IP (medium confidence), unusual location/time (medium confidence)",
      "evidence_summary": [
        "Device: New, never seen before for this customer",
        "IP: 203.15.4.99 matches known botnet in threat intelligence",
        "Location: Russia (customer normally in India)",
        "Time: 2:00 AM (customer normally active 9-5 IST)"
      ],
      "impact": {
        "fraud_prevention": "High (if account takeover, this stops fraud)",
        "customer_impact": "Medium (customer inconvenience, but recoverable)",
        "false_positive_risk": "22% (if legitimate travel, customer delayed)"
      }
    },
    {
      "action_id": "FORCE_MFA",
      "action": "Force MFA Re-authentication",
      "priority": "HIGH",
      "confidence_support": 78,
      "explanation": "MFA may not have been required for this login. Forcing re-authentication can verify if customer is legitimate.",
      "impact": {
        "fraud_prevention": "Medium (delays attacker, proves customer identity)",
        "customer_impact": "Low (customer can quickly verify)",
        "false_positive_risk": "10%"
      }
    },
    {
      "action_id": "NOTIFY_CUSTOMER",
      "action": "Notify Customer of Suspicious Activity",
      "priority": "MEDIUM",
      "confidence_support": 78,
      "explanation": "Customer should be aware of attempted access from Russia. If legitimate travel, customer confirms. If not, customer denies (improves confidence).",
      "impact": {
        "fraud_prevention": "High (customer can confirm or deny)",
        "customer_impact": "Low (customer appreciates security awareness)",
        "false_positive_risk": "5%"
      }
    }
  ],
  "decision_outcome_simulation": {...}
}
```

### 5.2 Decision Policy Engine

**Responsibility**: Apply consistent, auditable decision rules based on confidence.

**Decision Policy**:

```json
{
  "policy_version": "1.0",
  "effective_date": "2025-01-15",
  
  "confidence_bands": [
    {
      "min_confidence": 95,
      "max_confidence": 100,
      "decision": "IMMEDIATE_HOLD",
      "rule": "Confidence >= 95%: Recommend immediate transaction hold",
      "analyst_override": "REQUIRED",
      "notifications": ["customer", "escalation_team"],
      "sla_minutes": 5
    },
    {
      "min_confidence": 85,
      "max_confidence": 94,
      "decision": "INVESTIGATE_HOLD",
      "rule": "Confidence 85-94%: Hold transaction pending investigation",
      "analyst_override": "ALLOWED",
      "notifications": ["investigation_queue"],
      "sla_minutes": 15
    },
    {
      "min_confidence": 70,
      "max_confidence": 84,
      "decision": "GATHER_EVIDENCE",
      "rule": "Confidence 70-84%: Request additional evidence",
      "analyst_override": "ALLOWED",
      "notifications": ["investigation_queue"],
      "sla_minutes": 30
    },
    {
      "min_confidence": 50,
      "max_confidence": 69,
      "decision": "MONITOR",
      "rule": "Confidence 50-69%: Continue monitoring",
      "analyst_override": "ALLOWED",
      "notifications": [],
      "sla_minutes": 120
    },
    {
      "min_confidence": 0,
      "max_confidence": 49,
      "decision": "NO_ACTION",
      "rule": "Confidence < 50%: Retain for future correlation",
      "analyst_override": "ALLOWED",
      "notifications": [],
      "sla_minutes": 0
    }
  ],
  
  "policy_exceptions": [
    {
      "condition": "hypothesis=RANSOMWARE AND confidence >= 50%",
      "override_decision": "IMMEDIATE_ESCALATION",
      "reason": "Ransomware requires immediate response regardless of confidence"
    },
    {
      "condition": "transaction_amount > 1000000 AND confidence >= 70%",
      "override_decision": "HOLD_PENDING_APPROVAL",
      "reason": "High-value transactions require escalation"
    }
  ]
}
```

### 5.3 Decision Outcome Simulator

**Responsibility**: Predict impact of each recommended action before it's executed.

**Input**: Investigation + Recommended Actions  
**Output**: Predicted outcomes and impact analysis

**For MVP: Evidence-Based Outcome Prediction**

Instead of counterfactual reasoning (which requires complex modeling), use historical outcomes.

```python
def simulate_outcome(action, investigation):
  """
  Predict outcome based on similar historical cases
  """
  # Find similar past cases
  similar_cases = investigation_memory.find_similar(
    investigation.evidence_graph,
    investigation.hypothesis,
    top_k=20
  )
  
  # Filter cases where this action was taken
  cases_with_action = [
    case for case in similar_cases 
    if action in case.actions_taken
  ]
  
  # Calculate outcomes
  outcomes = {
    "fraud_prevented": sum(case.prevented_fraud for case in cases_with_action) / len(cases_with_action),
    "false_positive_rate": sum(case.was_false_positive for case in cases_with_action) / len(cases_with_action),
    "customer_satisfaction": avg(case.customer_satisfaction for case in cases_with_action),
    "operational_cost": avg(case.cost for case in cases_with_action),
    "similar_cases": len(cases_with_action)
  }
  
  return outcomes
```

**Example Output**:

```json
{
  "investigation_id": "inv-001",
  "simulation_results": [
    {
      "action": "HOLD_TRANSACTION",
      "outcomes": {
        "fraud_prevention": "92% (168 of 183 similar cases prevented fraud)",
        "false_positive_rate": "8% (15 of 183 were legitimate transactions)",
        "customer_satisfaction": 3.2/5 ("Delayed legitimate transaction"),
        "operational_cost": "Low",
        "recommendation": "✅ RECOMMENDED"
      },
      "similar_cases_analyzed": 183,
      "case_similarity": 0.94
    },
    {
      "action": "FORCE_MFA",
      "outcomes": {
        "fraud_prevention": "72% (prevented if attacker couldn't complete MFA)",
        "false_positive_rate": "2% (minimal impact on legitimate users)",
        "customer_satisfaction": 4.1/5 ("Quick verification, appreciated security"),
        "operational_cost": "Very Low",
        "recommendation": "✅ RECOMMENDED"
      },
      "similar_cases_analyzed": 156,
      "case_similarity": 0.91
    },
    {
      "action": "FREEZE_ACCOUNT",
      "outcomes": {
        "fraud_prevention": "100% (prevents all further activity)",
        "false_positive_rate": "25% (severe customer impact)",
        "customer_satisfaction": 1.8/5 ("Account locked, customer very upset"),
        "operational_cost": "High (escalation calls, manual review)",
        "recommendation": "❌ NOT RECOMMENDED (use only if customer unreachable)"
      },
      "similar_cases_analyzed": 47,
      "case_similarity": 0.89
    }
  ]
}
```

---

## Layer 6: Enterprise Execution Layer

**Responsibility**: Operationalize approved decisions through enterprise systems.

After analyst approves a decision, SentinelIQ creates tickets, sends notifications, and triggers workflows.

### Supported Connectors

**Ticketing Systems**:
- ServiceNow (primary)
- Jira
- Freshservice

**Notification Channels**:
- Microsoft Teams
- Slack
- Email
- PagerDuty

**Workflow Orchestration**:
- Zapier
- IFTTT
- Custom webhooks

### Execution Flow

```
Analyst Approval
     ↓
┌─────────────────────────────────┐
│ Ticket Creation                 │
│ - Title: "Account Takeover..."  │
│ - Description: Investigation    │
│ - Priority: Based on confidence │
│ - Owner: Investigation team     │
└─────────────────────────────────┘
     ↓
┌─────────────────────────────────┐
│ Notification Dispatch           │
│ - Microsoft Teams alert         │
│ - Escalation PagerDuty page     │
│ - Customer notification email   │
└─────────────────────────────────┘
     ↓
┌─────────────────────────────────┐
│ Workflow Trigger               │
│ - Hold transaction in core     │
│ - Freeze account if needed     │
│ - Log audit trail              │
└─────────────────────────────────┘
     ↓
Execution Complete (Tracked & Logged)
```

---

## Layer 7: Investigation Memory

**Responsibility**: Store and learn from completed investigations.

### Stored Investigation Record

```json
{
  "investigation_id": "inv-001",
  "timestamp": "2025-01-15T14:30:00Z",
  "customer_id": "alice@bank.com",
  
  "evidence_graph": {
    "nodes": [...],
    "edges": [...]
  },
  
  "investigation_timeline": [
    {
      "step": 1,
      "timestamp": "2025-01-15T14:23:45Z",
      "event": "Login from Russia",
      "system": "SIEM"
    },
    {
      "step": 2,
      "timestamp": "2025-01-15T14:24:30Z",
      "event": "Transaction initiated",
      "system": "Core Banking"
    }
  ],
  
  "hypotheses_evaluated": [
    {
      "hypothesis_id": "ACCOUNT_TAKEOVER",
      "final_confidence": 78
    },
    {
      "hypothesis_id": "LEGITIMATE_TRAVEL",
      "final_confidence": 22
    }
  ],
  
  "actions_recommended": [
    "HOLD_TRANSACTION",
    "FORCE_MFA",
    "NOTIFY_CUSTOMER"
  ],
  
  "analyst_decision": {
    "action_approved": "HOLD_TRANSACTION",
    "reasoning": "High confidence + historical outcome (92% fraud prevention)",
    "analyst_id": "analyst-bob-123",
    "timestamp": "2025-01-15T14:32:00Z"
  },
  
  "final_outcome": {
    "was_fraud": true,
    "fraud_amount_prevented": 500000,
    "customer_impact": "minimal",
    "lessons_learned": "New IP + new device + beneficiary abroad = strong ATO indicator"
  },
  
  "feedback": {
    "analyst_rating": 5,
    "false_positive": false,
    "suggestions": "Consider adding device geolocation to enrichment"
  }
}
```

### Learning Mechanism

**Similar Case Retrieval**:

When a new investigation starts, find similar past cases using:

1. **Graph Similarity**: Compare evidence graph structure
   - Same entities involved?
   - Same relationships?
   - Similar event sequences?

2. **Context Similarity**: Compare case context
   - Same customer/device profile?
   - Same threat indicators?
   - Similar amounts/timing?

3. **Outcome Relevance**: Weight by outcome certainty
   - Cases with confident outcomes > cases with uncertain outcomes

**Example**:

```
New Investigation: ACCOUNT_TAKEOVER (78% confidence)

Similar Past Cases:
  1. inv-456: ATO from same threat IP, same customer profile
     Similarity: 0.94 | Outcome: fraud confirmed | Preventing bias: ✓
     
  2. inv-789: ATO with new device + malware detection
     Similarity: 0.87 | Outcome: fraud confirmed | Preventing bias: ✓
     
  3. inv-234: Login from same region, legitimate travel
     Similarity: 0.71 | Outcome: false positive | Preventing bias: ✓
     
Lessons from Past Cases:
  "In 92 similar cases, holding prevented fraud 92% of the time"
  "In 15 cases with customer denial, 86% turned out legitimate"
```

---

# FEATURE SPECIFICATIONS

## Core Features

### Feature 1: Evidence Graph Visualization

**User Story**: As a SOC analyst, I want to see how events are connected so I understand the complete incident picture.

**Specification**:

- Interactive graph visualization showing entities and relationships
- Filter by entity type, relationship type, confidence level
- Timeline view showing event sequences
- Search across all entities and relationships
- Drill-down into supporting evidence for each relationship

**Technical Details**:
- Graph rendering: D3.js or similar
- Real-time updates as new events arrive
- Performance target: <2s render time for 500 nodes

### Feature 2: Multi-Hypothesis Investigation

**User Story**: As a SOC analyst, I want to see all possible explanations for an incident, not just one score, so I can make better decisions.

**Specification**:

- Display multiple hypotheses with individual confidence scores
- Show supporting evidence for each hypothesis
- Show contradicting evidence
- Highlight evidence gaps
- Allow analyst to dismiss hypotheses or add evidence

### Feature 3: Confidence Transparency

**User Story**: As a SOC analyst, I want to understand how confident SentinelIQ is and why, so I can decide whether to act.

**Specification**:

- Confidence score breakdown showing each factor's contribution
- Explanation of why each piece of evidence increased/decreased confidence
- Quality metrics for supporting evidence (reliability, recency, source)
- Clear indication of missing evidence and its impact

### Feature 4: Decision Outcome Simulator

**User Story**: As a SOC analyst, I want to know what will happen if I approve an action before I approve it.

**Specification**:

- Compare outcomes across recommended actions
- Show historical outcomes from similar cases
- Highlight false positive rate for each action
- Show customer impact metrics
- Display operational cost/effort

### Feature 5: Investigation Memory Search

**User Story**: As a SOC analyst, I want to find similar past investigations to learn from them.

**Specification**:

- Search by evidence pattern, hypothesis, or outcome
- Filter by date range, confidence level, fraud status
- Compare current case side-by-side with similar past cases
- Review analyst notes and lessons learned
- See how often similar cases turned out to be fraud

### Feature 6: Enterprise Ticket Integration

**User Story**: As a SOC analyst, I want to create a ticket and notify teams in one click.

**Specification**:

- One-click ticket creation in ServiceNow/Jira
- Auto-populated with investigation summary, confidence, evidence
- Select from pre-configured notification templates
- Route to correct team based on incident type
- Track ticket status in SentinelIQ

### Feature 7: Attack Studio (Demo Environment)

**User Story**: As a judge/demo participant, I want to create a custom attack scenario to test SentinelIQ.

**Specification**:

- Visual workflow builder for creating attack scenarios
- Pre-built building blocks (login, transfer, malware, etc.)
- Randomize timing and parameters
- Generate realistic event stream
- Run investigation in real-time and watch results

### Feature 8: Quantum Risk Integration

**User Story**: As a banker concerned about quantum threats, I want to see which transactions involve quantum-exposed cryptography.

**Specification**:

- Detect legacy cryptographic algorithms in use
- Identify long-term sensitive data at risk
- Calculate HNDL exposure for each transaction
- Integrate quantum risk into investigation confidence
- Recommend cryptographic asset remediation

---

# USER STORIES & USE CASES

## Use Case 1: Account Takeover Detection

**Scenario**: Customer's account is compromised via credential stuffing.

**Timeline**:
```
14:23 - SIEM: Login from Russia (unusual)
14:24 - Fraud Engine: High-value transfer (unusual)
14:25 - Threat Intel: IP matches botnet (malicious)
14:26 - EDR: Malware detected on device (compromised)
```

**Without SentinelIQ**:
- Analyst manually reviews 4 alerts
- Spends 20 minutes correlating events
- Manually creates ServiceNow ticket
- Result: Fraud goes through while analyst investigates

**With SentinelIQ**:
```
14:26 - SentinelIQ Investigation Created
  ├─ Evidence Graph auto-built
  ├─ Hypotheses generated: Account Takeover (78%), Legitimate Travel (22%)
  ├─ Recommended: Hold Transaction (92% effective historically)
  ├─ Decision Outcome: "Hold prevents fraud 92% of the time"
  └─ Analyst approves in 2 minutes

14:27 - Ticket created, teams notified, transaction held
14:28 - Customer called, confirms not legitimate
Result: Fraud prevented, case closed in 2 minutes
```

## Use Case 2: Insider Threat Detection

**Scenario**: Employee with access to financial systems attempts to transfer customer funds.

**Timeline**:
```
08:15 - IAM: Privilege escalation (unusual for this role)
08:16 - Core Banking: Large transfer initiated (off-hours)
08:17 - PAM: Access to sensitive account (flagged)
08:18 - Fraud Engine: Beneficiary in high-risk country
```

**Investigation**:
```
SentinelIQ Analysis:
  Hypotheses:
    ├─ Insider Threat: 85% confidence
    │  └─ Employee has access, initiating large transfer, unusual time
    ├─ System Error: 10% confidence
    │  └─ Could be automated process
    └─ Legitimate Business: 5% confidence
       └─ No valid business reason identified

Recommended Actions:
  ✅ Escalate to Security Team (HIGH)
  ✅ Freeze Account (HIGH)
  ✅ Revoke Access (HIGH)

Outcome Simulation:
  "In 47 similar insider threat cases, escalation + access revocation prevented fraud 100% of the time"

Analyst Decision: APPROVED
  → Ticket escalated to CISO
  → Access revoked immediately
  → Investigation team notified
```

## Use Case 3: Quantum Risk Monitoring

**Scenario**: Bank wants to monitor quantum-exposed cryptographic assets.

**Investigation Setup**:
```
SentinelIQ monitoring:
  
Daily Scan:
  ├─ Identify all cryptographic assets in use (RSA-1024, ECC, AES)
  ├─ Flag legacy algorithms (RSA-1024, RSA-2048)
  ├─ Calculate quantum exposure for each
  └─ Identify long-term sensitive data at risk

When Transaction Detected:
  Device contains RSA-1024?
    ├─ Yes → Quantum Risk: HIGH (HNDL exposure)
    │       └─ Add confidence penalty to transaction trust
    └─ No → Quantum Risk: NONE

Recommendation:
  "Transaction involves device with quantum-exposed crypto.
   Consider requiring additional authentication for high-value transfers."
```

## Use Case 4: Fraud Pattern Recognition

**Scenario**: Money mule scheme detected through transaction pattern analysis.

**Pattern**:
```
1. Stolen credentials → Account compromised
2. New beneficiary added → Mule account
3. Immediate transfer → To mule account
4. Rapid secondary transfer → Out of system

Timeline: 15 minutes (impossibly fast for legitimate user)
```

**SentinelIQ Detection**:
```
Investigation Memory matching:
  "This pattern matches 14 previous money mule schemes"
  "In 14 cases, the final withdrawal happened within 2 hours"
  "Fraud was prevented in 13 of 14 cases"

Confidence: 89% (Money Mule Attack)

Recommended Actions:
  ✅ Hold primary transfer (92% fraud prevention)
  ✅ Flag secondary beneficiary (new & suspicious)
  ✅ Alert customer (mule accounts often hacked)
  ✅ Coordinate with law enforcement (criminal activity)

Analyst Decision: APPROVED → Fraud prevented
```

---

# MVP SCOPE

## What We're Building (MVP)

### Layer 1: Event Ingestion ✅
- Enterprise Threat Simulator (generates realistic events)
- REST API for event ingestion
- Event validation & schema checking

### Layer 2: Unified Event Model ✅
- Event normalization engine
- Canonical event schema
- Support for 10+ event types

### Layer 3: Evidence Intelligence Engine ✅
- Entity extraction (8 entity types)
- Entity resolution (deterministic + heuristic)
- Evidence quality scoring
- Context enrichment (mock data for MVP)
- Relationship registry (10 core relationships)
- Relationship builder
- Neo4j graph storage & querying

### Layer 4: Investigation Engine ✅
- Hypothesis library (5 hypotheses)
- Investigation evaluation algorithm
- Confidence calculation engine
- Multi-hypothesis reasoning
- Missing evidence detection

### Layer 5: Decision Intelligence ✅
- Action recommendations (5 core actions)
- Decision policy engine (5 confidence bands)
- Decision outcome simulator (historical-based)

### Layer 6: Enterprise Execution Layer ✅
- Ticket creation (ServiceNow connector)
- Notifications (Teams, Slack, Email)
- Webhook execution

### Layer 7: Investigation Memory ✅
- Basic case storage & retrieval
- Graph similarity search
- Lesson learned capture

### Enterprise Threat Simulator ✅
- Scenario library (5 scenarios)
- Attack studio (visual workflow builder)
- Event generation engine

## What We're NOT Building (MVP)

### Post-MVP Features
- Production EDR/SIEM connectors (use simulator instead)
- Advanced ML/LLM integration (use deterministic reasoning)
- Real-time streaming from enterprise systems
- Advanced SIEM integration (Splunk, ELK APIs)
- Mobile app
- Advanced analytics dashboards
- Threat hunting features
- Compliance reporting

### Deferred to Production
- Batch processing of historical data
- Machine learning models
- Advanced counterfactual reasoning
- Distributed graph processing
- Machine-learned confidence scoring
- Custom hypothesis builder for users

---

# TECHNICAL REQUIREMENTS

## Architecture Requirements

### Technology Stack

**Backend**:
- Language: Python 3.10+
- Framework: FastAPI
- Database: Neo4j (graph), PostgreSQL (case storage)
- Message Queue: Redis (optional for scaling)

**Frontend**:
- Framework: React 18+
- Visualization: D3.js or Cytoscape.js (graph viz)
- State Management: Redux or Zustand
- Styling: Tailwind CSS

**Infrastructure**:
- Containerization: Docker
- Orchestration: Kubernetes (optional for MVP)
- CI/CD: GitHub Actions or similar

### Data Requirements

**Event Volume (MVP)**:
- Ingest: 1,000-10,000 events/hour
- Storage: 1-7 days retention (10-100 GB)
- Graph: 10,000-100,000 nodes

**Latency Targets**:
- Event ingestion → Evidence graph: <5 seconds
- Hypothesis evaluation: <10 seconds
- Confidence calculation: <5 seconds
- Investigation creation: <20 seconds total

### Security Requirements

**Authentication & Authorization**:
- OAuth 2.0 for user authentication
- Role-based access control (RBAC):
  - SOC Analyst (read investigations, approve actions)
  - Investigation Manager (create investigations, configure policies)
  - Admin (system configuration, user management)

**Data Protection**:
- TLS 1.2+ for all network communication
- Encryption at rest for sensitive data
- PII handling per banking regulations
- Audit logging of all analyst actions

**Compliance**:
- GDPR compliance (data retention, deletion)
- PCI DSS compliance (payment card data)
- SOC 2 Type II readiness (logging, monitoring)

### Integration Requirements

**Enterprise System Connectors**:

| System | Purpose | MVP Status |
|--------|---------|------------|
| ServiceNow | Ticketing | Simulator |
| Microsoft Teams | Notifications | Simulator |
| Slack | Notifications | Simulator |
| Core Banking API | Transactions | Simulator |
| Threat Intelligence API | TI enrichment | Mock data |
| EDR API | Device security | Mock data |

For MVP, all external systems use simulated data. Production connectors follow.

---

# SUCCESS METRICS & KPIs

## Product Success Metrics

### Operational Efficiency
| Metric | Target | Measurement |
|--------|--------|-------------|
| Investigation Time | <5 minutes avg | Time from event to decision |
| Alert Reduction | 70% fewer alerts | Compared to manual correlation |
| Analyst Productivity | 5x more investigations/day | Cases handled per analyst |
| Time to Decision | <10 minutes | From alert to approved action |

### Quality & Accuracy
| Metric | Target | Measurement |
|--------|--------|-------------|
| Fraud Prevention Rate | 90%+ | Percentage of detected fraud prevented |
| False Positive Rate | <10% | Percentage of false alerts |
| Confidence Accuracy | 85%+ | Confidence score matches actual outcome |
| Evidence Completeness | 95%+ | Investigations capture all relevant events |

### User Adoption
| Metric | Target | Measurement |
|--------|--------|-------------|
| Analyst Satisfaction | 4.0+/5.0 | NPS score for investigation quality |
| Feature Usage | 80%+ | % analysts using all major features |
| Recommendation Approval Rate | 75%+ | % of recommended actions approved |

### Business Impact
| Metric | Target | Measurement |
|--------|--------|-------------|
| Fraud Loss Prevented | $500K+ per month | Financial impact of blocked fraud |
| Customer Impact | <2% | False positives affecting customers |
| Investigation Accuracy | 95%+ | Correct hypothesis identified |

---

# GLOSSARY & DEFINITIONS

| Term | Definition |
|------|-----------|
| **Analyst** | SOC professional who reviews investigations and approves actions |
| **Attack Pattern** | Sequence of events indicating a specific type of attack (e.g., Account Takeover) |
| **Beneficiary** | Recipient of a financial transfer |
| **Confidence Score** | Percentage indicating likelihood that a hypothesis is correct (0-100%) |
| **Contradiction** | Evidence that reduces confidence in a hypothesis |
| **Decision Policy** | Rules mapping confidence levels to recommended actions |
| **Entity** | Real-world object in investigation (User, Device, IP, Transaction, etc.) |
| **Entity Resolution** | Process of matching entities across systems to identify duplicates |
| **Evidence** | Event or data point supporting/contradicting a hypothesis |
| **Evidence Graph** | Directed graph showing entities and their relationships with supporting evidence |
| **Graceful Degradation** | System continues operating with reduced confidence when data sources unavailable |
| **Hypothesis** | Possible explanation for observed events (e.g., "Account Takeover") |
| **Investigation** | Complete analysis of an incident with hypotheses, evidence, and recommendations |
| **Multi-Hypothesis Reasoning** | Evaluating multiple possible explanations instead of forcing one answer |
| **Normalization** | Converting vendor-specific event formats to canonical schema |
| **Relationship** | Connection between two entities (e.g., "User logged in from Device") |
| **Relationship Registry** | Declarative configuration of valid relationships between entity types |
| **Reliability Score** | Confidence in the accuracy of an event or data point (0-1) |
| **SOC** | Security Operations Center (team of security analysts) |
| **Supporting Evidence** | Event/data that increases confidence in a hypothesis |
| **Threat Indicator** | Malicious IP, domain, file hash, etc. |

---

# APPENDICES

## Appendix A: Hypothesis Templates (MVP)

### Template 1: Account Takeover

```json
{
  "id": "ACCOUNT_TAKEOVER",
  "name": "Account Takeover",
  "description": "Attacker gains unauthorized access to customer account via compromised credentials",
  "required_patterns": [
    "USER -[LOGIN]-> NEW_DEVICE",
    "IP -[MATCHES_THREAT]-> THREAT"
  ],
  "supporting_indicators": [
    "New device never seen before",
    "Login from unusual geography",
    "Login outside normal hours",
    "IP matches threat feed",
    "Immediate high-value transaction",
    "Beneficiary in high-risk country",
    "MFA bypassed or not required",
    "Device malware detected"
  ],
  "contradicting_indicators": [
    "Customer confirms login",
    "IP is known/trusted",
    "Device owned by customer",
    "MFA successfully verified",
    "Transaction matches normal pattern"
  ],
  "missing_evidence_checklist": [
    "Device health status",
    "EDR logs",
    "Customer verification",
    "Beneficiary background",
    "Previous transaction history"
  ],
  "confidence_factors": {
    "new_device": 0.25,
    "threat_ip": 0.20,
    "unusual_location": 0.15,
    "large_amount": 0.20,
    "rapid_escalation": 0.15,
    "malware": 0.30,
    "customer_denial": -0.40
  },
  "recommended_actions": [
    "HOLD_TRANSACTION",
    "FORCE_MFA",
    "NOTIFY_CUSTOMER",
    "ESCALATE_INVESTIGATION"
  ]
}
```

### Template 2: Credential Stuffing

```json
{
  "id": "CREDENTIAL_STUFFING",
  "name": "Credential Stuffing Attack",
  "description": "Attacker uses leaked credentials to attempt bulk logins",
  "required_patterns": [
    "MULTIPLE_USERS -[LOGIN_FAILED]-> SAME_SYSTEM",
    "IP -[MATCHES_THREAT]-> THREAT"
  ],
  "supporting_indicators": [
    "Many failed login attempts from single IP",
    "Attempts across multiple user accounts",
    "IP matches threat feed",
    "Failed attempts within minutes",
    "Unusual login times"
  ],
  "contradicting_indicators": [
    "Attacks from known testing IP",
    "Controlled test environment"
  ],
  "missing_evidence_checklist": [
    "IP geolocation",
    "User account status",
    "Password change history",
    "MFA enforcement status"
  ],
  "confidence_factors": {
    "multiple_users": 0.30,
    "threat_ip": 0.25,
    "failed_logins": 0.20,
    "rapid_attempts": 0.25
  },
  "recommended_actions": [
    "BLOCK_IP",
    "FORCE_PASSWORD_RESET",
    "REQUIRE_MFA",
    "NOTIFY_CUSTOMERS"
  ]
}
```

### Template 3: Insider Threat

```json
{
  "id": "INSIDER_THREAT",
  "name": "Insider Threat",
  "description": "Employee abuses access to initiate fraud",
  "required_patterns": [
    "EMPLOYEE -[ACCESS]-> SENSITIVE_DATA",
    "EMPLOYEE -[INITIATED_TRANSACTION]-> LARGE_AMOUNT"
  ],
  "supporting_indicators": [
    "Privilege escalation",
    "Access outside normal duties",
    "Unusual transaction amounts",
    "Beneficiary in high-risk region",
    "Off-hours access",
    "Data exfiltration detected"
  ],
  "contradicting_indicators": [
    "Valid business reason documented",
    "Approval from management",
    "Normal working hours"
  ],
  "missing_evidence_checklist": [
    "Employee background check",
    "Access justification",
    "Transaction approval trail",
    "Device security status"
  ],
  "confidence_factors": {
    "privilege_escalation": 0.30,
    "data_access": 0.25,
    "large_transaction": 0.25,
    "off_hours": 0.20
  },
  "recommended_actions": [
    "ESCALATE_TO_CISO",
    "FREEZE_ACCOUNT",
    "REVOKE_ACCESS",
    "LEGAL_NOTIFICATION"
  ]
}
```

### Template 4: Money Mule

```json
{
  "id": "MONEY_MULE",
  "name": "Money Mule Fraud",
  "description": "Multi-stage fraud: compromise account → add mule beneficiary → transfer money → cash out",
  "required_patterns": [
    "USER -[LOGIN]-> NEW_DEVICE",
    "USER -[ADD_BENEFICIARY]-> NEW_ACCOUNT",
    "USER -[TRANSFER]-> NEW_ACCOUNT -[TRANSFER]-> EXTERNAL"
  ],
  "supporting_indicators": [
    "Account compromise indicators",
    "New beneficiary added quickly",
    "Immediate transfer after beneficiary add",
    "High-value transfer amount",
    "Beneficiary account in different country",
    "Beneficiary never contacted before",
    "Secondary transfer happens quickly"
  ],
  "contradicting_indicators": [
    "Customer pre-approved beneficiary",
    "Beneficiary is known contact"
  ],
  "missing_evidence_checklist": [
    "Beneficiary verification",
    "Customer communication",
    "Mule account history",
    "Cash-out detection"
  ],
  "confidence_factors": {
    "new_beneficiary": 0.30,
    "fast_cascade": 0.25,
    "high_amount": 0.20,
    "unusual_country": 0.25
  },
  "recommended_actions": [
    "HOLD_ALL_TRANSFERS",
    "BLOCK_BENEFICIARY",
    "NOTIFY_CUSTOMER",
    "ESCALATE_LAW_ENFORCEMENT"
  ]
}
```

### Template 5: Ransomware

```json
{
  "id": "RANSOMWARE",
  "name": "Ransomware Attack",
  "description": "Malware infection leading to data encryption and extortion",
  "required_patterns": [
    "DEVICE -[MALWARE_DETECTED]-> TRUE",
    "DEVICE -[FILE_ENCRYPTION]-> DETECTED"
  ],
  "supporting_indicators": [
    "Malware detected on device",
    "File encryption activity",
    "Ransom note found",
    "Privilege escalation to admin",
    "Lateral movement detected",
    "Large file transfers"
  ],
  "contradicting_indicators": [
    "Malware vendor false positive",
    "Legitimate encryption software"
  ],
  "missing_evidence_checklist": [
    "EDR forensics",
    "File system analysis",
    "Network traffic logs",
    "Admin access logs"
  ],
  "confidence_factors": {
    "malware_detected": 0.40,
    "file_encryption": 0.35,
    "lateral_movement": 0.25
  },
  "recommended_actions": [
    "ISOLATE_DEVICE_IMMEDIATELY",
    "ESCALATE_TO_CISO_EMERGENCY",
    "ACTIVATE_INCIDENT_RESPONSE",
    "NOTIFY_AUTHORITIES"
  ]
}
```

## Appendix B: Decision Policy Examples

### Policy: Account Takeover at Various Confidence Levels

```
Confidence 95%: Account Takeover (RECOMMENDED IMMEDIATE HOLD)
  ├─ Action: Hold Transaction
  ├─ Analyst Override: REQUIRED for approval
  ├─ Notifications: Escalation Team, Customer
  ├─ SLA: 5 minutes
  └─ Decision: "Overwhelming evidence of account compromise"

Confidence 78%: Account Takeover (INVESTIGATE & RECOMMEND HOLD)
  ├─ Action: Hold Transaction
  ├─ Analyst Override: ALLOWED
  ├─ Notifications: Investigation Queue
  ├─ SLA: 15 minutes
  └─ Decision: "Strong evidence + some contradictions"

Confidence 65%: Account Takeover (GATHER MORE EVIDENCE)
  ├─ Action: Request Additional Data
  ├─ Analyst Override: ALLOWED
  ├─ Notifications: Investigation Queue
  ├─ SLA: 30 minutes
  └─ Decision: "Need more context before deciding"

Confidence 40%: Account Takeover (CONTINUE MONITORING)
  ├─ Action: No Immediate Action
  ├─ Analyst Override: ALLOWED
  ├─ Notifications: None (logged for correlation)
  ├─ SLA: N/A
  └─ Decision: "Insufficient evidence to act"
```

## Appendix C: Sample Investigation Object

```json
{
  "investigation_id": "inv-2025-001-alice-aTO",
  "timestamp_created": "2025-01-15T14:26:00Z",
  "customer_id": "alice@bank.com",
  "triggered_by_event": "event-SIEM-login-001",
  
  "evidence_graph": {
    "nodes": [
      {"id": "user-alice", "type": "USER", "value": "alice@bank.com"},
      {"id": "device-abc123", "type": "DEVICE", "value": "abc123", "health": "unknown"},
      {"id": "ip-203.15.4.99", "type": "IP", "value": "203.15.4.99", "country": "Russia"},
      {"id": "txn-x1", "type": "TRANSACTION", "value": "txn-x1", "amount": 500000},
      {"id": "benef-xyz", "type": "BENEFICIARY", "value": "receiver@bank-ru"},
      {"id": "threat-botnet", "type": "THREAT", "value": "botnet-xyz"}
    ],
    "edges": [
      {
        "id": "edge-1",
        "source": "user-alice",
        "target": "device-abc123",
        "type": "LOGGED_IN_FROM",
        "confidence": 0.99,
        "evidence": ["event-SIEM-login-001"]
      },
      {
        "id": "edge-2",
        "source": "device-abc123",
        "target": "ip-203.15.4.99",
        "type": "USES_IP",
        "confidence": 0.98,
        "evidence": ["event-network-trace-001"]
      },
      {
        "id": "edge-3",
        "source": "ip-203.15.4.99",
        "target": "threat-botnet",
        "type": "MATCHES_THREAT",
        "confidence": 0.84,
        "evidence": ["threat-feed-abuse-ch-001"]
      },
      {
        "id": "edge-4",
        "source": "user-alice",
        "target": "txn-x1",
        "type": "INITIATED_TRANSACTION",
        "confidence": 0.95,
        "evidence": ["event-banking-txn-001"]
      },
      {
        "id": "edge-5",
        "source": "txn-x1",
        "target": "benef-xyz",
        "type": "SENT_TO_BENEFICIARY",
        "confidence": 0.99,
        "evidence": ["event-banking-txn-001"]
      }
    ]
  },
  
  "hypotheses_evaluated": [
    {
      "hypothesis_id": "ACCOUNT_TAKEOVER",
      "name": "Account Takeover",
      "confidence": 78,
      "confidence_tier": "high",
      "supporting_evidence": [
        {
          "indicator": "New device never seen before",
          "weight": 0.25,
          "supporting_event": "device-abc123 first login",
          "evidence_reliability": 0.99
        },
        {
          "indicator": "IP matches threat feed (botnet)",
          "weight": 0.20,
          "supporting_event": "threat-feed-abuse-ch-001",
          "evidence_reliability": 0.84
        },
        {
          "indicator": "Login from Russia (unusual)",
          "weight": 0.15,
          "supporting_event": "IP geolocation",
          "evidence_reliability": 0.95
        },
        {
          "indicator": "Large amount transfer (₹500K)",
          "weight": 0.20,
          "supporting_event": "txn-x1",
          "evidence_reliability": 0.99
        },
        {
          "indicator": "Login at 2 AM (off-hours)",
          "weight": 0.15,
          "supporting_event": "timestamp 2025-01-15T14:26",
          "evidence_reliability": 1.00
        }
      ],
      "contradicting_evidence": [
        {
          "indicator": "Device has valid TLS cert",
          "weight": -0.05,
          "evidence_reliability": 0.75
        }
      ],
      "missing_evidence": [
        "Device health status (EDR)",
        "Customer verification call",
        "Beneficiary account history",
        "Previous transaction patterns for alice"
      ],
      "missing_evidence_impact": -0.15
    },
    {
      "hypothesis_id": "LEGITIMATE_TRAVEL",
      "name": "Legitimate Business Travel",
      "confidence": 22,
      "confidence_tier": "low",
      "supporting_evidence": [
        {
          "indicator": "Alice travels internationally for work",
          "weight": 0.20,
          "evidence_reliability": 0.70
        }
      ],
      "contradicting_evidence": [
        {
          "indicator": "No advance notification in system",
          "weight": -0.30,
          "evidence_reliability": 0.95
        },
        {
          "indicator": "Beneficiary account in Russia (business reason?)",
          "weight": -0.15,
          "evidence_reliability": 0.75
        },
        {
          "indicator": "Transfer amount unusually large",
          "weight": -0.15,
          "evidence_reliability": 0.85
        }
      ]
    }
  ],
  
  "recommended_actions": [
    {
      "action_id": "HOLD_TRANSACTION",
      "name": "Hold Transaction",
      "priority": "HIGH",
      "confidence_support": 78,
      "explanation": "Account Takeover hypothesis at 78% confidence. Holding prevents fraud in 92% of similar cases.",
      "impact_simulation": {
        "fraud_prevention_rate": 0.92,
        "false_positive_rate": 0.08,
        "customer_satisfaction": 3.2,
        "similar_historical_cases": 183
      }
    },
    {
      "action_id": "FORCE_MFA",
      "name": "Force MFA Re-authentication",
      "priority": "HIGH",
      "confidence_support": 78,
      "explanation": "Verify customer identity via MFA. If customer confirms, reduces account takeover confidence. If fails, confirms compromise.",
      "impact_simulation": {
        "fraud_prevention_rate": 0.72,
        "false_positive_rate": 0.02,
        "customer_satisfaction": 4.1,
        "similar_historical_cases": 156
      }
    },
    {
      "action_id": "NOTIFY_CUSTOMER",
      "name": "Notify Customer",
      "priority": "MEDIUM",
      "confidence_support": 78,
      "explanation": "Alert customer to suspicious activity. Customer response clarifies legitimacy.",
      "impact_simulation": {
        "fraud_prevention_rate": 0.88,
        "false_positive_rate": 0.05,
        "customer_satisfaction": 4.3,
        "similar_historical_cases": 176
      }
    }
  ],
  
  "decision_policy_applied": "HIGH_CONFIDENCE",
  "suggested_decision": "HOLD_TRANSACTION",
  "analyst_decision": {
    "action_approved": "HOLD_TRANSACTION",
    "reasoning": "78% confidence + 92% historical fraud prevention rate = justified hold",
    "approved_by": "analyst-bob-123",
    "timestamp_approved": "2025-01-15T14:28:00Z"
  },
  
  "execution_status": "COMPLETED",
  "ticket_created": "SNOW-INC-0123456",
  "notifications_sent": ["teams-security-channel", "customer-email", "pagerduty-escalation"],
  "transaction_status": "HELD",
  
  "resolution": {
    "timestamp_resolved": "2025-01-15T14:45:00Z",
    "final_outcome": "FRAUD_CONFIRMED",
    "fraud_details": {
      "confirmed_by": "Customer denied login",
      "fraud_amount": 500000,
      "recovered_amount": 500000,
      "lessons_learned": "New IP + new device + beneficiary abroad = 99% confidence ATO"
    },
    "analyst_satisfaction": 5,
    "feedback": "Perfect investigation. SentinelIQ saved customer ₹5L"
  }
}
```

---

# END OF DOCUMENT

**Document Version**: 1.0 (MVP Freeze)  
**Last Updated**: 2025-01-15  
**Status**: Ready for Implementation  
**Approved By**: Product Leadership  

For questions or clarifications, contact the SentinelIQ product team.