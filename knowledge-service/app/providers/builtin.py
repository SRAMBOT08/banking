from __future__ import annotations
from app.query.models import (
    AttackPattern, DetectionRule, FraudPattern, KnowledgeRecommendation, KnowledgeReference,
    KnowledgeRelationship, KnowledgeSource, KnowledgeTag, KnowledgeVersion, MITRETactic,
    MITRETechnique, Playbook, SecurityControl, ThreatIndicator, QuantumThreatPattern,
)


class BuiltinEnterpriseProvider:
    """Deterministic initial provider; future providers implement the same contract."""
    name = "enterprise-security"

    def items(self):
        source = KnowledgeSource(provider=self.name, name="SentinelIQ Enterprise Registry")
        version = [KnowledgeVersion(version="1.0", status="historical"), KnowledgeVersion(version="1.1", status="current")]
        return [
            AttackPattern(id="pattern.account_takeover", name="Account Takeover Pattern", description="Enterprise pattern for suspicious account access.", provider="detection-knowledge", indicators=["multiple_new_devices", "impossible_travel"], techniques=["T1078"], tags=[KnowledgeTag(name="pattern"), KnowledgeTag(name="account_takeover")], related_ids=["fraud.account_takeover", "pb.account_takeover"]),
            MITRETactic(id="TA0001", name="Initial Access", tactic_id="TA0001", description="Techniques used to gain an initial foothold.", provider="mitre", source=source, techniques=["T1078"], tags=[KnowledgeTag(name="mitre"), KnowledgeTag(name="access")]),
            MITRETechnique(id="T1078", name="Valid Accounts", technique_id="T1078", description="Adversaries use valid accounts to gain access and evade controls.", provider="mitre", source=source, tactics=["TA0001"], platforms=["Cloud", "Windows"], tags=[KnowledgeTag(name="mitre"), KnowledgeTag(name="account_takeover")], versions=version, related_ids=["fraud.account_takeover", "det.account_takeover"]),
            FraudPattern(id="fraud.account_takeover", name="Account Takeover", description="Suspicious authentication and account access sequence.", provider="fraud-knowledge", risk_score=85, indicators=["multiple_new_devices", "impossible_travel", "credential_stuffing"], controls=["AC-2"], tags=[KnowledgeTag(name="fraud"), KnowledgeTag(name="account_takeover")], related_ids=["T1078", "pb.account_takeover"]),
            DetectionRule(id="det.account_takeover", name="Account Takeover Detection", description="Detects correlated authentication anomalies.", provider="detection-rules", rule_type="correlation", expression="impossible_travel AND new_device AND credential_stuffing", severity="high", techniques=["T1078"], tags=[KnowledgeTag(name="detection"), KnowledgeTag(name="account_takeover")]),
            SecurityControl(id="AC-2", name="Account Management", description="Manage account lifecycle and privileged access.", provider="security-controls", control_family="Access Control", objective="Ensure accounts are authorized, reviewed, and revoked.", policy_refs=["POLICY-IAM-001"], tags=[KnowledgeTag(name="control"), KnowledgeTag(name="iam")]),
            Playbook(id="pb.account_takeover", name="Account Takeover Response", description="Contain and investigate suspected account takeover.", provider="security-playbooks", steps=["Revoke active sessions", "Require step-up authentication", "Review recent changes", "Notify account owner"], trigger_rules=["det.account_takeover"], required_controls=["AC-2"], tags=[KnowledgeTag(name="playbook"), KnowledgeTag(name="account_takeover")]),
            ThreatIndicator(id="indicator.suspicious_ip", name="Suspicious Authentication Source", description="An IP associated with repeated anomalous authentication.", provider="threat-metadata", indicator_type="ipv4", pattern="198.51.100.0/24", confidence=75, source_name="SentinelIQ threat metadata", tags=[KnowledgeTag(name="threat_intelligence")]),
            QuantumThreatPattern(id="quantum.harvest_now", name="Harvest Now Decrypt Later", description="Long-lived encrypted data exposed to future quantum decryption.", provider="quantum-security", quantum_risk="high", migration_actions=["Inventory cryptography", "Prioritize crypto-agility", "Adopt post-quantum standards"], tags=[KnowledgeTag(name="quantum")]),
        ]

    def recommendations(self):
        return [
            KnowledgeRecommendation(id="rec.step_up_auth", name="Require Step-Up Authentication", description="Require phishing-resistant authentication after anomalous access.", priority=90, actions=["Challenge with phishing-resistant MFA", "Record elevated assurance"]),
            KnowledgeRecommendation(id="rec.revoke_sessions", name="Revoke Active Sessions", description="Invalidate active sessions when takeover indicators are confirmed.", priority=95, actions=["Revoke sessions", "Rotate credentials"]),
        ]

    def relationships(self):
        return [
            KnowledgeRelationship(id="rel.technique.tactic", source_id="T1078", target_id="TA0001", relationship_type="technique_to_tactic", description="Valid Accounts belongs to Initial Access."),
            KnowledgeRelationship(id="rel.fraud.technique", source_id="fraud.account_takeover", target_id="T1078", relationship_type="pattern_to_technique"),
            KnowledgeRelationship(id="rel.pattern.recommendation", source_id="fraud.account_takeover", target_id="rec.step_up_auth", relationship_type="pattern_to_recommendation"),
            KnowledgeRelationship(id="rel.playbook.rule", source_id="pb.account_takeover", target_id="det.account_takeover", relationship_type="playbook_to_detection"),
            KnowledgeRelationship(id="rel.threat.control", source_id="indicator.suspicious_ip", target_id="AC-2", relationship_type="threat_to_control"),
        ]
