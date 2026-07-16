from __future__ import annotations
import hashlib
import json
from .models import CaseFileDocument, ReportFile, ReportRequest
from .formatter import ReportFormatter
from .guardrails import Guardrails
from .prompt_builder import PromptBuilder
from .providers import ModelProvider
from .repository import ReportRepository
from .validator import ReportValidator


class ReportService:
    def __init__(self, repository: ReportRepository, provider: ModelProvider, prompt_builder=None, guardrails=None, validator=None, formatter=None):
        self.repository, self.provider = repository, provider
        self.prompt_builder, self.guardrails = prompt_builder or PromptBuilder(), guardrails or Guardrails()
        self.validator, self.formatter = validator or ReportValidator(), formatter or ReportFormatter()

    async def generate(self, request: ReportRequest) -> ReportFile:
        case_file = CaseFileDocument.model_validate(request.case_file)
        prompt = self.prompt_builder.build(case_file, request.report_type)
        self.guardrails.validate_prompt(prompt)
        response = await self.provider.generate(prompt)
        text = self.validator.validate(response.text, case_file)
        source_hash = hashlib.sha256(json.dumps(request.case_file, default=str, sort_keys=True).encode()).hexdigest()
        report = self.formatter.format(text, case_file, request.report_type, request.output_format, response.model, source_hash, request.created_by)
        return self.repository.create(report)
