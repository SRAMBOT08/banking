from __future__ import annotations


class GuardrailError(ValueError): pass


class Guardrails:
    def __init__(self, max_prompt_chars: int = 60000): self.max_prompt_chars = max_prompt_chars
    def validate_prompt(self, prompt: str) -> None:
        if not prompt.strip(): raise GuardrailError('prompt context is empty')
        if len(prompt) > self.max_prompt_chars: raise GuardrailError('prompt exceeds maximum size')
        lowered = prompt.lower()
        if 'casefile_context_json:' not in lowered: raise GuardrailError('CaseFile context is missing')
        injection_markers = ('ignore previous instructions', 'reveal system prompt', 'jailbreak', 'act as a different')
        if any(marker in lowered for marker in injection_markers): raise GuardrailError('prompt injection marker detected')
