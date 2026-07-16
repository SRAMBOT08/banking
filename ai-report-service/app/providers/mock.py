from __future__ import annotations
import json
from .base import ModelProvider, ProviderResponse


class DeterministicNIMProvider(ModelProvider):
    @property
    def model_name(self) -> str: return 'nim-deterministic'
    async def generate(self, prompt: str) -> ProviderResponse:
        payload = json.loads(prompt.split('CASEFILE_CONTEXT_JSON:', 1)[1])
        metadata = payload.get('metadata', {})
        case_id = metadata.get('case_id', 'Not available')
        title = metadata.get('title', 'Investigation report')
        evidence = payload.get('evidence', {}).get('items', [])
        return ProviderResponse(model=self.model_name, text=(
            f'# {title}\n\n## Purpose\nHuman-readable report for CaseFile `{case_id}`.\n\n'
            f'## Findings\nThe CaseFile contains {len(evidence)} supplied evidence record(s).\n\n'
            '## Evidence\nOnly evidence supplied by the CaseFile is described; no additional conclusions were generated.\n\n'
            '## Outcome\nSee the supplied decision and execution sections.\n\n'
            '## Limitations\nInformation not present in the CaseFile is Not available.\n\n'
            f'## Traceability\nCaseFile `{case_id}`.'
        ))
