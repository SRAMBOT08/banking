from ..models import ReportType


class PromptTemplateManager:
    def template(self, report_type: ReportType) -> str:
        return (f'Write a {report_type.value.replace("_", " ")} for the supplied CaseFile. '
                'Use only supplied facts. Mark unavailable information as Not available. '
                'Do not investigate, infer, classify, calculate confidence, or invent entities. '
                'Include the headings: Purpose, Findings, Evidence, Outcome, Limitations, Traceability.')
