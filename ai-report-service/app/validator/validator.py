from __future__ import annotations
from ..models import CaseFileDocument


class ReportValidationError(ValueError): pass


class ReportValidator:
    REQUIRED = ('Purpose', 'Findings', 'Evidence', 'Outcome', 'Limitations', 'Traceability')
    def validate(self, text: str, case_file: CaseFileDocument) -> str:
        missing = [heading for heading in self.REQUIRED if f'## {heading}' not in text and f'# {heading}' not in text]
        if missing: raise ReportValidationError(f'missing mandatory sections: {missing}')
        case_id = str(case_file.case_id)
        if case_id not in text: raise ReportValidationError('report is not traceable to the CaseFile')
        if 'investigationcontext' in text.lower(): raise ReportValidationError('report references forbidden InvestigationContext')
        return text
