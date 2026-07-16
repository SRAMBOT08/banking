from __future__ import annotations
from typing import Any
from ..models import CaseFileDocument, ReportType


class ContextBuilder:
    FIELDS = {
        ReportType.EXECUTIVE: ('metadata', 'executive_summary', 'decision', 'confidence', 'execution', 'recommendations'),
        ReportType.TECHNICAL: ('metadata', 'technical_summary', 'timeline', 'evidence', 'threat', 'graph', 'confidence'),
        ReportType.SOC: ('metadata', 'timeline', 'evidence', 'threat', 'graph', 'decision', 'recommendations'),
        ReportType.ROOT_CAUSE: ('metadata', 'timeline', 'evidence', 'threat', 'graph', 'historical', 'decision'),
        ReportType.TIMELINE: ('metadata', 'timeline', 'evidence'),
        ReportType.MITRE: ('metadata', 'threat', 'evidence', 'references'),
        ReportType.FRAUD: ('metadata', 'threat', 'evidence', 'historical', 'decision'),
        ReportType.BUSINESS_IMPACT: ('metadata', 'executive_summary', 'decision', 'execution', 'recommendations'),
        ReportType.RECOMMENDATIONS: ('metadata', 'recommendations', 'decision', 'execution', 'evidence'),
        ReportType.COMPLIANCE: ('metadata', 'audit', 'references', 'decision', 'evidence'),
    }

    def build(self, case_file: CaseFileDocument, report_type: ReportType) -> dict[str, Any]:
        context = {field: getattr(case_file, field) for field in self.FIELDS[report_type]}
        if 'metadata' in context:
            context['metadata'] = {**context['metadata'], 'case_id': str(case_file.case_id)}
        return context
