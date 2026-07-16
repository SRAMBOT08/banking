from __future__ import annotations
import html
import json
from ..models import CaseFileDocument, ReportFile, ReportFormat, ReportType


class ReportFormatter:
    def format(self, text: str, case_file: CaseFileDocument, report_type: ReportType, output_format: ReportFormat, model: str, source_hash: str, created_by: str) -> ReportFile:
        title = f'{report_type.value.replace("_", " ").title()} — {case_file.metadata.get("title", case_file.case_id)}'
        structured = {'title': title, 'case_id': str(case_file.case_id), 'case_version': case_file.version.get('version'), 'body': text}
        content = text
        if output_format == ReportFormat.HTML: content = f'<article><h1>{html.escape(title)}</h1><div>{html.escape(text).replace(chr(10), "<br>")}</div></article>'
        elif output_format == ReportFormat.JSON: content = json.dumps(structured, sort_keys=True)
        elif output_format == ReportFormat.PDF_READY: content = f'%PDF-READY\nTITLE: {title}\n\n{text}'
        return ReportFile(case_id=case_file.case_id, case_version=int(case_file.version.get('version', 0)), report_type=report_type, output_format=output_format, title=title, content=content, structured_content=structured, model=model, created_by=created_by, source_hash=source_hash, provenance=tuple(item for item in case_file.audit.get('provenance', ())))
