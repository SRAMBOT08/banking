from __future__ import annotations
from typing import Dict, Any, Optional, List
from app.core.logger import get_logger
from app.pattern_loader.loader import load_yaml_patterns
from app.knowledge_registry.validator import validate_patterns_basic, compute_checksum, validate_pattern_references
from app.knowledge_registry.models import AttackPattern, ConfidenceModel, Recommendation, PatternMetadata

logger = get_logger("kr_inmemory")


class InMemoryKnowledgeRegistry:
    def __init__(self, patterns_dir: str):
        self.patterns_dir = patterns_dir
        self._patterns: Dict[str, Dict[str, Any]] = {}
        self._indicators: Dict[str, Dict[str, Any]] = {}
        self._checksums: Dict[str, str] = {}

    def load(self):
        patterns = load_yaml_patterns(self.patterns_dir)
        errors = validate_patterns_basic(patterns)
        errors += validate_pattern_references(patterns)
        if errors:
            logger.error("pattern_validation_errors", extra={"errors": errors})
            raise RuntimeError("pattern validation failed: " + ",".join(errors))
        # store patterns keyed by name -> version mapping
        for name, p in patterns.items():
            pname = p.get('name') or name
            version = str(p.get('version') or '0')
            # convert to typed model
            try:
                metadata = PatternMetadata(**p.get('metadata', {})) if p.get('metadata') else None
            except Exception:
                metadata = None
            conf = None
            try:
                if p.get('confidence_model'):
                    conf = ConfidenceModel(**p.get('confidence_model'))
            except Exception:
                conf = None
            recs = []
            try:
                for r in p.get('recommendations', []) or p.get('recommendation', []) or []:
                    recs.append(Recommendation(**r) if isinstance(r, dict) else r)
            except Exception:
                recs = []

            ap = AttackPattern(
                name=pname,
                version=version,
                nodes=p.get('nodes', []),
                edges=p.get('edges', []),
                metadata=metadata,
                confidence_model=conf,
                recommendations=recs,
                mitre=p.get('mitre'),
                fraud=p.get('fraud'),
            )

            self._patterns.setdefault(pname, {})[version] = ap
            self._checksums[f"{pname}:{version}"] = compute_checksum(p)
        logger.info("registry_loaded", extra={"pattern_count": sum(len(v) for v in self._patterns.values())})

    def reload(self):
        self._patterns.clear()
        self._checksums.clear()
        self.load()

    def get_attack_pattern(self, name: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        versions = self._patterns.get(name)
        if not versions:
            return None
        if version:
            return versions.get(version)
        # return latest (max by version string)
        latest = sorted(versions.keys())[-1]
        return versions.get(latest)

    def list_patterns(self) -> Dict[str, Dict[str, Any]]:
        return self._patterns

    def get_indicator(self, indicator_id: str) -> Optional[Dict[str, Any]]:
        return self._indicators.get(indicator_id)

    def list_indicators(self) -> List[Dict[str, Any]]:
        return list(self._indicators.values())
