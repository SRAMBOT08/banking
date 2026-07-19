"""PostgreSQL implementation of InvestigationRepository."""
from __future__ import annotations
from typing import List, Optional
import asyncpg
from app.models.investigation import (
    Investigation, InvestigationState, InvestigationPriority, TimelineEvent,
    Hypothesis, InvestigationConfidence, ConfidenceHistory, InvestigationMetadata,
    InvestigationEvidence, EvidenceSummary, MissingEvidence, InvestigationRecommendation
)
from app.repositories.base import InvestigationRepository


class PostgresInvestigationRepository(InvestigationRepository):
    """PostgreSQL implementation of InvestigationRepository."""

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def save(self, investigation: Investigation) -> Investigation:
        """Persist or update an investigation atomically."""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Upsert investigation
                await conn.execute("""
                    INSERT INTO investigations (
                        investigation_id, tenant_id, state, priority,
                        confidence_score, confidence_factors,
                        explanation, next_action, related_entities,
                        missing_evidence, investigation_plan,
                        confidence_history, metadata,
                        state_history, actions,
                        created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                    ON CONFLICT (investigation_id) DO UPDATE SET
                        state = EXCLUDED.state,
                        priority = EXCLUDED.priority,
                        confidence_score = EXCLUDED.confidence_score,
                        confidence_factors = EXCLUDED.confidence_factors,
                        explanation = EXCLUDED.explanation,
                        next_action = EXCLUDED.next_action,
                        related_entities = EXCLUDED.related_entities,
                        missing_evidence = EXCLUDED.missing_evidence,
                        investigation_plan = EXCLUDED.investigation_plan,
                        confidence_history = EXCLUDED.confidence_history,
                        metadata = EXCLUDED.metadata,
                        state_history = EXCLUDED.state_history,
                        actions = EXCLUDED.actions,
                        updated_at = EXCLUDED.updated_at
                """,
                    investigation.investigation_id,
                    investigation.metadata.tenant_id,
                    investigation.state.value,
                    investigation.priority.value,
                    investigation.confidence.score,
                    investigation.confidence.factors,
                    investigation.explanation,
                    investigation.next_action,
                    investigation.related_entities,
                    [me.model_dump() for me in investigation.missing_evidence],
                    [rec.model_dump() for rec in investigation.investigation_plan],
                    [{"timestamp": ch.timestamp, "score": ch.score, "reason": ch.reason} for ch in investigation.confidence_history],
                    investigation.metadata.model_dump(),
                    investigation.state_history,
                    investigation.actions,
                    investigation.metadata.created_at,
                    investigation.metadata.updated_at,
                )

                # Save timeline events (replace all)
                await conn.execute("DELETE FROM timeline_events WHERE investigation_id = $1", investigation.investigation_id)
                for event in investigation.timeline.events:
                    await conn.execute("""
                        INSERT INTO timeline_events (event_id, investigation_id, timestamp, event_type, description, evidence_refs, source)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, event.event_id, investigation.investigation_id, event.timestamp, event.event_type,
                        event.description, event.evidence_refs, event.source)

                # Save hypotheses (replace all)
                await conn.execute("DELETE FROM hypotheses WHERE investigation_id = $1", investigation.investigation_id)
                for h in investigation.hypotheses:
                    await conn.execute("""
                        INSERT INTO hypotheses (
                            hypothesis_id, investigation_id, pattern_name, pattern_version, confidence,
                            candidate_ids, matched_indicators, missing_indicators, mitre_mapping, fraud_mapping,
                            explanation, status
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    """, h.hypothesis_id, investigation.investigation_id, h.pattern_name, h.pattern_version,
                        h.confidence, h.candidate_ids, h.matched_indicators, h.missing_indicators,
                        h.mitre_mapping, h.fraud_mapping, h.explanation, h.status)

                # Save missing evidence (replace all)
                await conn.execute("DELETE FROM missing_evidence WHERE investigation_id = $1", investigation.investigation_id)
                for me in investigation.missing_evidence:
                    await conn.execute("""
                        INSERT INTO missing_evidence (investigation_id, evidence_type, reason, priority, blocked)
                        VALUES ($1, $2, $3, $4, $5)
                    """, investigation.investigation_id, me.evidence_type, me.reason, me.priority.value, me.blocked)

                # Save confidence history (replace all)
                await conn.execute("DELETE FROM confidence_history WHERE investigation_id = $1", investigation.investigation_id)
                for ch in investigation.confidence_history:
                    await conn.execute("""
                        INSERT INTO confidence_history (investigation_id, timestamp, score, reason)
                        VALUES ($1, $2, $3, $4)
                    """, investigation.investigation_id, ch.timestamp, ch.score, ch.reason)

                # Save recommendations (deprecated)
                await conn.execute("DELETE FROM recommendations WHERE investigation_id = $1", investigation.investigation_id)
                for rec in investigation.investigation_plan:
                    await conn.execute("""
                        INSERT INTO recommendations (recommendation_id, investigation_id, title, required_evidence, priority, source_pattern, status)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, rec.recommendation_id, investigation.investigation_id, rec.title,
                        rec.required_evidence, rec.priority, rec.source_pattern, "pending")

                # Save evidence (deprecated)
                await conn.execute("DELETE FROM evidence WHERE investigation_id = $1", investigation.investigation_id)
                for ev in investigation.evidence:
                    await conn.execute("""
                        INSERT INTO evidence (evidence_id, investigation_id, evidence_type, timestamp, confidence, properties, source)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, ev.evidence_id, investigation.investigation_id, ev.evidence_type,
                        ev.timestamp, ev.confidence, ev.properties, ev.source)

                # Save state history
                await conn.execute("DELETE FROM state_transitions WHERE investigation_id = $1", investigation.investigation_id)
                for sh in investigation.state_history:
                    await conn.execute("""
                        INSERT INTO state_transitions (investigation_id, from_state, to_state, timestamp, metadata)
                        VALUES ($1, $2, $3, $4, $5)
                    """, investigation.investigation_id, sh["from"], sh["to"], sh["timestamp"], sh.get("metadata", {}))

        return investigation

    async def get(self, investigation_id: str) -> Optional[Investigation]:
        """Retrieve an investigation by ID."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM investigations WHERE investigation_id = $1", investigation_id)
            if not row:
                return None
            return await self._build_investigation(conn, row)

    async def list_all(self) -> List[Investigation]:
        """List all investigations, ordered by ID."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM investigations ORDER BY investigation_id")
            return [await self._build_investigation(conn, row) for row in rows]

    async def find_by_correlation(self, correlation_id: str) -> List[Investigation]:
        """Find investigations containing a correlation ID."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM investigations 
                WHERE metadata->'correlation_ids' @> $1::jsonb
                ORDER BY investigation_id
            """, f'["{correlation_id}"]')
            return [await self._build_investigation(conn, row) for row in rows]

    async def find_by_tenant(self, tenant_id: str, limit: int = 100, offset: int = 0) -> List[Investigation]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM investigations WHERE tenant_id = $1 ORDER BY investigation_id LIMIT $2 OFFSET $3",
                tenant_id, limit, offset
            )
            return [await self._build_investigation(conn, row) for row in rows]

    async def delete(self, investigation_id: str) -> bool:
        async with self._pool.acquire() as conn:
            result = await conn.execute("DELETE FROM investigations WHERE investigation_id = $1", investigation_id)
            return result == "DELETE 1"

    async def _build_investigation(self, conn: asyncpg.Connection, row: asyncpg.Record) -> Investigation:
        """Build Investigation object from database row."""
        investigation_id = row["investigation_id"]

        # Get timeline events
        timeline_rows = await conn.fetch(
            "SELECT * FROM timeline_events WHERE investigation_id = $1 ORDER BY timestamp",
            investigation_id
        )
        timeline_events = [
            TimelineEvent(
                event_id=r["event_id"],
                timestamp=r["timestamp"],
                event_type=r["event_type"],
                description=r["description"],
                evidence_refs=r["evidence_refs"] or [],
                source=r["source"]
            ) for r in timeline_rows
        ]

        # Get hypotheses
        hyp_rows = await conn.fetch(
            "SELECT * FROM hypotheses WHERE investigation_id = $1",
            investigation_id
        )
        hypotheses = [
            Hypothesis(
                hypothesis_id=r["hypothesis_id"],
                pattern_name=r["pattern_name"],
                pattern_version=r["pattern_version"],
                confidence=r["confidence"],
                candidate_ids=r["candidate_ids"] or [],
                matched_indicators=r["matched_indicators"] or [],
                missing_indicators=r["missing_indicators"] or [],
                mitre_mapping=r["mitre_mapping"],
                fraud_mapping=r["fraud_mapping"],
                explanation=r["explanation"] or {},
                status=r["status"]
            ) for r in hyp_rows
        ]

        # Get missing evidence
        me_rows = await conn.fetch(
            "SELECT * FROM missing_evidence WHERE investigation_id = $1",
            investigation_id
        )
        missing_evidence = [
            MissingEvidence(
                evidence_type=r["evidence_type"],
                reason=r["reason"],
                priority=InvestigationPriority(r["priority"]),
                blocked=r["blocked"]
            ) for r in me_rows
        ]

        # Get confidence history
        ch_rows = await conn.fetch(
            "SELECT * FROM confidence_history WHERE investigation_id = $1 ORDER BY timestamp",
            investigation_id
        )
        confidence_history = [
            ConfidenceHistory(timestamp=r["timestamp"], score=r["score"], reason=r["reason"])
            for r in ch_rows
        ]

        # Get recommendations (deprecated)
        rec_rows = await conn.fetch(
            "SELECT * FROM recommendations WHERE investigation_id = $1",
            investigation_id
        )
        recommendations = [
            InvestigationRecommendation(
                recommendation_id=r["recommendation_id"],
                title=r["title"],
                required_evidence=r["required_evidence"] or [],
                priority=r["priority"],
                source_pattern=r["source_pattern"]
            ) for r in rec_rows
        ]

        # Get evidence (deprecated)
        ev_rows = await conn.fetch(
            "SELECT * FROM evidence WHERE investigation_id = $1",
            investigation_id
        )
        evidence = [
            InvestigationEvidence(
                evidence_id=r["evidence_id"],
                evidence_type=r["evidence_type"],
                timestamp=r["timestamp"],
                confidence=r["confidence"],
                properties=r["properties"] or {},
                source=r["source"]
            ) for r in ev_rows
        ]

        # Get state history
        sh_rows = await conn.fetch(
            "SELECT * FROM state_transitions WHERE investigation_id = $1 ORDER BY timestamp",
            investigation_id
        )
        state_history = [
            {"from": r["from_state"], "to": r["to_state"], "timestamp": r["timestamp"], "metadata": r["metadata"] or {}}
            for r in sh_rows
        ]

        # Build confidence object
        confidence = InvestigationConfidence(
            score=row["confidence_score"],
            factors=row["confidence_factors"] or {}
        )

        metadata = InvestigationMetadata(
            tenant_id=row["tenant_id"],
            correlation_ids=row["metadata"].get("correlation_ids", []),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            source=row["metadata"].get("source", "investigation-service"),
            schema_version=row["metadata"].get("schema_version", "1.0")
        )

        # Evidence summary
        evidence_summary = EvidenceSummary(
            total=len(ev_rows),
            by_type={},
            average_confidence=0,
            evidence_ids=[e.evidence_id for e in ev_rows]
        )
        if ev_rows:
            for e in ev_rows:
                evidence_summary.by_type[e["evidence_type"]] = evidence_summary.by_type.get(e["evidence_type"], 0) + 1
            evidence_summary.average_confidence = sum(e["confidence"] for e in ev_rows) // len(ev_rows)

        return Investigation(
            investigation_id=investigation_id,
            state=InvestigationState(row["state"]),
            priority=InvestigationPriority(row["priority"]),
            confidence=confidence,
            timeline=timeline_events,
            hypotheses=hypotheses,
            missing_evidence=missing_evidence,
            investigation_plan=recommendations,
            next_action=row["next_action"] or "Collect evidence",
            explanation=row["explanation"],
            confidence_history=confidence_history,
            metadata=metadata,
            state_history=state_history,
            evidence=evidence,
            evidence_summary=evidence_summary,
        )