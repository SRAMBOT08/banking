from __future__ import annotations
from app.pattern_loader.loader import load_yaml_patterns, validate_patterns
from app.core.logger import get_logger

logger = get_logger("kr_loader")


def load_all_patterns(dirpath: str):
    patterns = load_yaml_patterns(dirpath)
    errors = validate_patterns(patterns)
    if errors:
        logger.error("pattern_validation_errors", extra={"errors": errors})
        raise RuntimeError("Pattern validation failed: " + ", ".join(errors))
    logger.info("patterns_loaded", extra={"count": len(patterns)})
    return patterns
