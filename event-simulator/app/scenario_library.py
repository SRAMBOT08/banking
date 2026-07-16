from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from .models import EventType, ScenarioName, Severity


@dataclass(frozen=True)
class ScenarioStep:
    offset_minutes: int
    event_type: EventType
    action: str
    severity: Severity
    payload: dict[str, Any]


@dataclass(frozen=True)
class ScenarioDefinition:
    name: ScenarioName
    description: str
    steps: tuple[ScenarioStep, ...]
    attack_tags: tuple[str, ...]


def _steps(*items: tuple[int, EventType, str, Severity, dict[str, Any]]) -> tuple[ScenarioStep, ...]:
    return tuple(ScenarioStep(*item) for item in items)


def build_library() -> dict[ScenarioName, ScenarioDefinition]:
    auth_fail = _steps((0, EventType.AUTHENTICATION, 'login_failure', Severity.LOW, {'reason': 'invalid_password'}), (1, EventType.AUTHENTICATION, 'login_failure', Severity.LOW, {'reason': 'invalid_password'}), (2, EventType.AUTHENTICATION, 'login_failure', Severity.MEDIUM, {'reason': 'invalid_password'}), (3, EventType.AUTHENTICATION, 'login_success', Severity.HIGH, {'risk_signal': 'credential_velocity'}))
    library: dict[ScenarioName, ScenarioDefinition] = {}
    def add(name, description, steps, *tags): library[name] = ScenarioDefinition(name, description, steps, tags)
    add(ScenarioName.CREDENTIAL_STUFFING, 'Reused credentials tested across customer accounts.', auth_fail, 'credential_access', 'automation')
    add(ScenarioName.PASSWORD_SPRAY, 'One password tested against many enterprise identities.', _steps((0, EventType.AUTHENTICATION, 'distributed_login_failures', Severity.MEDIUM, {'target_count': 12}), (4, EventType.AUTHENTICATION, 'successful_login', Severity.HIGH, {'password_reuse': True}), (7, EventType.IDENTITY, 'session_created', Severity.HIGH, {})), 'credential_access', 'spray')
    add(ScenarioName.ACCOUNT_TAKEOVER, 'Compromised account followed by device and transfer anomalies.', _steps((0, EventType.AUTHENTICATION, 'login_failure', Severity.LOW, {}), (2, EventType.AUTHENTICATION, 'login_success', Severity.HIGH, {'mfa': 'push_accepted'}), (5, EventType.ASSET, 'new_device_observed', Severity.HIGH, {}), (8, EventType.TRANSACTION, 'beneficiary_added', Severity.HIGH, {}), (10, EventType.TRANSACTION, 'large_transfer', Severity.CRITICAL, {'amount': 48750})), 'account_takeover', 'fraud')
    add(ScenarioName.IMPOSSIBLE_TRAVEL, 'Successful logins from geographically impossible locations.', _steps((0, EventType.AUTHENTICATION, 'login_success', Severity.INFO, {'location': 'New York'}), (8, EventType.AUTHENTICATION, 'login_success', Severity.HIGH, {'location': 'Singapore', 'distance_km': 15300, 'impossible_travel': True})), 'identity', 'geovelocity')
    add(ScenarioName.NEW_DEVICE_LOGIN, 'Known user authenticates from an unmanaged device.', _steps((0, EventType.AUTHENTICATION, 'login_success', Severity.MEDIUM, {}), (1, EventType.ASSET, 'new_device_registered', Severity.HIGH, {'managed': False}), (3, EventType.AUTHENTICATION, 'mfa_challenge', Severity.MEDIUM, {})), 'identity', 'device')
    add(ScenarioName.PRIVILEGE_ESCALATION, 'User obtains elevated privileges outside their normal role.', _steps((0, EventType.CLOUD, 'role_assumption', Severity.MEDIUM, {'role': 'analyst'}), (3, EventType.IDENTITY, 'privilege_granted', Severity.HIGH, {'role': 'global-admin'}), (6, EventType.CLOUD, 'sensitive_resource_access', Severity.CRITICAL, {})), 'privilege_escalation', 'identity')
    add(ScenarioName.PHISHING_CAMPAIGN, 'Malicious campaign sends a credential-harvesting link.', _steps((0, EventType.EMAIL, 'campaign_delivered', Severity.MEDIUM, {'recipient_count': 28}), (4, EventType.EMAIL, 'malicious_link_clicked', Severity.HIGH, {'domain_reputation': 'new'}), (7, EventType.AUTHENTICATION, 'login_success', Severity.HIGH, {'source': 'phishing_landing_page'})), 'initial_access', 'phishing')
    add(ScenarioName.BUSINESS_EMAIL_COMPROMISE, 'Mailbox takeover followed by payment instruction manipulation.', _steps((0, EventType.AUTHENTICATION, 'mailbox_login', Severity.HIGH, {}), (5, EventType.EMAIL, 'forwarding_rule_created', Severity.HIGH, {'external_target': True}), (12, EventType.EMAIL, 'payment_instruction_sent', Severity.CRITICAL, {'vendor_change': True})), 'initial_access', 'fraud')
    add(ScenarioName.SUSPICIOUS_POWERSHELL, 'Encoded PowerShell executes on a managed endpoint.', _steps((0, EventType.ENDPOINT, 'powershell_started', Severity.MEDIUM, {'encoded': True}), (2, EventType.ENDPOINT, 'credential_dump_attempt', Severity.HIGH, {}), (5, EventType.NETWORK, 'command_and_control_beacon', Severity.HIGH, {})), 'execution', 'endpoint')
    add(ScenarioName.MALWARE_EXECUTION, 'Malicious executable launches and establishes persistence.', _steps((0, EventType.ENDPOINT, 'file_written', Severity.MEDIUM, {'extension': '.exe'}), (2, EventType.ENDPOINT, 'malware_executed', Severity.HIGH, {}), (6, EventType.ENDPOINT, 'persistence_created', Severity.CRITICAL, {})), 'execution', 'malware')
    add(ScenarioName.SUSPICIOUS_DNS, 'Endpoint resolves algorithmically generated malicious domains.', _steps((0, EventType.NETWORK, 'dns_query', Severity.LOW, {'domain_class': 'newly_registered'}), (2, EventType.NETWORK, 'dns_query_burst', Severity.HIGH, {'query_count': 240}), (5, EventType.NETWORK, 'c2_resolution', Severity.HIGH, {})), 'command_and_control', 'dns')
    add(ScenarioName.TOR_LOGIN, 'Account authenticates through a TOR exit node.', _steps((0, EventType.AUTHENTICATION, 'login_success', Severity.HIGH, {'network': 'tor_exit'}), (2, EventType.NETWORK, 'tor_exit_observed', Severity.HIGH, {}), (5, EventType.TRANSACTION, 'sensitive_action', Severity.CRITICAL, {})), 'defense_evasion', 'anonymization')
    add(ScenarioName.VPN_ABUSE, 'Valid VPN access is used outside expected patterns.', _steps((0, EventType.AUTHENTICATION, 'vpn_login', Severity.MEDIUM, {'country': 'unknown'}), (15, EventType.CLOUD, 'internal_resource_sweep', Severity.HIGH, {}), (20, EventType.NETWORK, 'vpn_session_extended', Severity.HIGH, {'duration_minutes': 480})), 'initial_access', 'persistence')
    add(ScenarioName.DATA_EXFILTRATION, 'Sensitive records are staged and transferred externally.', _steps((0, EventType.CLOUD, 'sensitive_query', Severity.MEDIUM, {'records': 1200}), (6, EventType.ENDPOINT, 'archive_created', Severity.HIGH, {'format': '7z'}), (12, EventType.NETWORK, 'large_outbound_transfer', Severity.CRITICAL, {'bytes': 7800000000})), 'exfiltration', 'data')
    add(ScenarioName.LARGE_BANKING_TRANSFER, 'Unusual high-value transfer follows an authentication anomaly.', _steps((0, EventType.AUTHENTICATION, 'login_success', Severity.MEDIUM, {}), (3, EventType.TRANSACTION, 'beneficiary_added', Severity.HIGH, {}), (6, EventType.TRANSACTION, 'large_transfer', Severity.CRITICAL, {'amount': 250000}), (9, EventType.TRANSACTION, 'transfer_reversed', Severity.HIGH, {})), 'impact', 'fraud')
    add(ScenarioName.MONEY_MULE, 'Multiple accounts receive and rapidly distribute funds.', _steps((0, EventType.TRANSACTION, 'incoming_transfer', Severity.MEDIUM, {'amount': 18000}), (8, EventType.TRANSACTION, 'rapid_outbound_transfers', Severity.HIGH, {'recipient_count': 9}), (14, EventType.FRAUD, 'mule_pattern_detected', Severity.CRITICAL, {})), 'fraud', 'impact')
    add(ScenarioName.INSIDER_THREAT, 'Privileged employee accesses and stages unusual data.', _steps((0, EventType.CLOUD, 'unusual_data_access', Severity.MEDIUM, {'records': 3000}), (30, EventType.ENDPOINT, 'removable_media_mount', Severity.HIGH, {}), (45, EventType.NETWORK, 'external_upload', Severity.CRITICAL, {})), 'insider', 'exfiltration')
    add(ScenarioName.RANSOMWARE, 'Endpoint compromise spreads and encrypts shared resources.', _steps((0, EventType.ENDPOINT, 'malware_executed', Severity.HIGH, {}), (5, EventType.NETWORK, 'lateral_movement', Severity.HIGH, {'host_count': 14}), (18, EventType.ENDPOINT, 'mass_encryption', Severity.CRITICAL, {'file_count': 85000}), (25, EventType.CLOUD, 'backup_deletion_attempt', Severity.CRITICAL, {})), 'impact', 'ransomware')
    add(ScenarioName.HARVEST_NOW_DECRYPT_LATER, 'Long-term collection targets encrypted banking communications.', _steps((0, EventType.NETWORK, 'encrypted_traffic_collected', Severity.MEDIUM, {'protocol': 'tls'}), (60, EventType.CLOUD, 'cryptographic_metadata_collected', Severity.HIGH, {}), (120, EventType.THREAT, 'quantum_sensitive_asset_identified', Severity.HIGH, {})), 'collection', 'cryptography')
    add(ScenarioName.QUANTUM_READINESS_FAILURES, 'Legacy cryptography remains on a high-value service.', _steps((0, EventType.ASSET, 'legacy_cipher_detected', Severity.MEDIUM, {'cipher': 'rsa-1024'}), (20, EventType.CLOUD, 'unprotected_key_inventory', Severity.HIGH, {}), (40, EventType.THREAT, 'quantum_readiness_gap', Severity.CRITICAL, {})), 'vulnerability', 'cryptography')
    return library

SCENARIO_LIBRARY = build_library()
