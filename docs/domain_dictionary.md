# Domain Dictionary

Defines core business entities used across the platform.

- User: human operator or system account. Properties: id, username, roles. Relationships: owns Investigations, Accounts (operator role).
- Customer: bank customer. Properties: customer_id, name, KYC_status. Relationships: owns Accounts, Beneficiaries.
- Account: bank account. Properties: account_id, account_type, balance, currency. Relationships: Customer owns Account; Transactions reference Account.
- Transaction: financial transaction. Properties: transaction_id, amount, timestamp, from_account, to_account, status.
- Beneficiary: recipient linked to an Account.
- Device: endpoint device. Properties: device_id, device_type, last_seen, owner.
- IP: IP address entity. Properties: ip_address, asn, geo.
- Threat Indicator: IOC such as hash, domain, URL, reputation score.
- Incident: security incident record. Properties: incident_id, severity, status.
- Investigation: orchestration object for triage and investigation.
- Evidence: individual piece of evidence tied to events and graph nodes.
- Asset: logical or physical asset tracked by the platform.
- Policy: detection or response policy definitions.
- Risk: derived risk score or indicator.

Each entry contains Meaning, Properties, Relationships, and Used By in Phase 2 documentation.
