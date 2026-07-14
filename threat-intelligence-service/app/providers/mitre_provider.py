from __future__ import annotations
from typing import Dict


class MITREProvider:
    def __init__(self):
        # static small mapping for MVP
        self.map = {
            'account_takeover': {'technique': 'T1110', 'tactic': 'Initial Access'},
        }

    def get_mapping(self, pattern_name: str) -> Dict:
        return self.map.get(pattern_name, {})
