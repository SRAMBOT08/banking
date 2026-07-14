from __future__ import annotations
from app.services.ai_service import AIInvestigationService
from app.services.snapshot_client import InvestigationSnapshotClient
from app.reports.generator import ReportGenerator


class SnapshotPipeline:
    """Consumes snapshot metadata, retrieves the immutable snapshot, and reasons over it."""
    def __init__(self, client: InvestigationSnapshotClient, service: AIInvestigationService, publisher):
        self.client = client
        self.service = service
        self.publisher = publisher

    async def handle(self, event: dict) -> None:
        snapshot = await self.client.get(str(event["investigation_id"]), int(event["snapshot_version"]))
        response = await self.service.reason(snapshot, "incident_summary")
        if self.publisher:
            context = self.service.context(snapshot)
            report = ReportGenerator().generate(context, "executive", "json")
            self.publisher.publish(self.service.settings.reasoned_topic, response.model_dump(mode="json"), response.snapshot_id)
            self.publisher.publish(self.service.settings.report_topic, report.model_dump(mode="json"), response.snapshot_id)
            self.publisher.publish(self.service.settings.metrics_topic, self.service.metrics.snapshot(), response.snapshot_id)
