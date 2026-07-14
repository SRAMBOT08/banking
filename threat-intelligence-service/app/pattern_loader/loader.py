from __future__ import annotations
import os
import yaml
from typing import Dict, Any, List
from app.core.logger import get_logger
from app.config.settings import settings

logger = get_logger("pattern_loader")


def load_yaml_patterns(dirpath: str = None) -> Dict[str, Dict]:
    dirpath = dirpath or settings.patterns_dir
    patterns = {}
    if not os.path.isdir(dirpath):
        logger.warning("patterns_dir_missing", extra={"dir": dirpath})
        return patterns
    for fn in sorted(os.listdir(dirpath)):
        if not fn.endswith('.yaml') and not fn.endswith('.yml'):
            continue
        path = os.path.join(dirpath, fn)
        with open(path, 'r', encoding='utf-8') as fh:
            doc = yaml.safe_load(fh)
            name = doc.get('name') or os.path.splitext(fn)[0]
            patterns[name] = doc
            logger.info("pattern_loaded", extra={"pattern": name, "file": fn})
    return patterns


def validate_patterns(patterns: Dict[str, Dict]) -> List[str]:
    errors = []
    for name, p in patterns.items():
        for field in settings.required_pattern_fields:
            if field not in p:
                errors.append(f"pattern {name} missing field {field}")
    return errors
