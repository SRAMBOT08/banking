from __future__ import annotations
import json
from ..context_builder import ContextBuilder
from ..models import CaseFileDocument, ReportType
from ..templates.manager import PromptTemplateManager


class PromptBuilder:
    def __init__(self, context_builder=None, templates=None):
        self.context_builder = context_builder or ContextBuilder()
        self.templates = templates or PromptTemplateManager()

    def build(self, case_file: CaseFileDocument, report_type: ReportType) -> str:
        context = self.context_builder.build(case_file, report_type)
        return self.templates.template(report_type) + '\nCASEFILE_CONTEXT_JSON:\n' + json.dumps(context, default=str, sort_keys=True, separators=(',', ':'))
