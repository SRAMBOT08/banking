# ADR-004: PostgreSQL

Context
- Relational store required for users, investigations, audit logs, and policies.

Decision
- Use PostgreSQL for relational data. Use Alembic for migrations in Phase 2.

Consequences
- Must establish schema ownership and migration practices in Phase 2.
