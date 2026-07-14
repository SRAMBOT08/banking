from __future__ import annotations
import os
import yaml
from typing import Dict, Any


def load_patterns(dirpath: str) -> Dict[str, Any]:
    patterns = {}
    if not os.path.isdir(dirpath):
        return patterns
    for fn in os.listdir(dirpath):
        if not fn.endswith('.yaml') and not fn.endswith('.yml'):
            continue
        path = os.path.join(dirpath, fn)
        with open(path, 'r', encoding='utf-8') as fh:
            doc = yaml.safe_load(fh)
            name = doc.get('name') or os.path.splitext(fn)[0]
            patterns[name] = doc
    return patterns
