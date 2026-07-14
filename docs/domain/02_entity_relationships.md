# 02 — Entity Relationships

This document lists relationships between domain entities. Relationship verbs are deliberate to make flows readable.

Relationships Catalogue

- User OWNS Investigation
- User ASSIGNED_TO Ticket
- User USES Device
- User INITIATES Transaction
- Customer OWNS Account
- Account CONTAINS Transaction
- Transaction SENT_TO Beneficiary
- Transaction RELATED_TO Alert
- Device ASSOCIATED_WITH IP
- IP MATCHES Threat Indicator
- Threat Indicator MAPPED_TO Attack Pattern
- Alert TRIGGERS Investigation
- Investigation CONTAINS Evidence
- Evidence LINKS_TO Account/Transaction/Device/IP/Asset
- Evidence SUPPORTED_BY Threat Indicator
- Attack Pattern MAPPED_TO Threat Indicator
- Policy TRIGGERS Alert
- Investigation PRODUCES Recommendation
- Recommendation TRIGGERS Ticket
- Ticket REPRESENTS Case
- Case CONTAINS Investigation(s)
- Risk ATTACHED_TO Account/Customer/Asset

Relationship Cardinality and Notes
- A Customer MAY own multiple Accounts (1 → many).
- An Investigation MAY contain multiple Evidence nodes (1 → many).
- An Alert MAY trigger multiple Investigations in some workflows; ownership defined in Investigation Service.
- Topic-level coupling: Each relationship that crosses service boundaries must be implemented via events and not direct DB access.

Guiding Principle: single ownership for each entity and graph; references (IDs) used across services.
