from __future__ import annotations
from typing import Dict, Any, Optional, List
from app.core.logger import get_logger
from app.pattern_loader.loader import load_yaml_patterns
from app.knowledge_registry.validator import compute_checksum
from app.knowledge_registry.models import (
    AttackPattern, ThreatIndicator, MitreTechnique, MitreTactic,
    FraudPattern, ConfidenceModel, Recommendation, PatternRelationship,
)

logger = get_logger("kr_inmemory")


class InMemoryKnowledgeRegistry:
    def __init__(self, patterns_dir: str):
        self.patterns_dir = patterns_dir
        self._patterns: Dict[str, Dict[str, AttackPattern]] = {}
        self._indicators: Dict[str, ThreatIndicator] = {}
        self._mitre: Dict[str, Any] = {}
        self._fraud: Dict[str, FraudPattern] = {}
        self._recommendations: Dict[str, Recommendation] = {}
        self._confidence: Dict[str, ConfidenceModel] = {}
        self._relationships: List[PatternRelationship] = []
        self._checksums: Dict[str, str] = {}
        self.raw_patterns: Dict[str, Dict[str, Any]] = {}

    def load(self):
        self._patterns.clear()
        self._indicators.clear()
        self._mitre.clear()
        self._fraud.clear()
        self._recommendations.clear()
        self._confidence.clear()
        self._relationships.clear()
        self._checksums.clear()
        patterns = load_yaml_patterns(self.patterns_dir)
        self.raw_patterns = patterns
        # store patterns keyed by name -> version mapping
        for name, p in patterns.items():
            pname = p.get('name') or name
            version = str(p.get('version') or '0')
            typed = AttackPattern(
                name=pname,
                version=version,
                nodes=p.get("nodes", []),
                edges=p.get("edges", []),
                metadata=p.get("metadata"),
                confidence_model=p.get("confidence_model"),
                recommendations=p.get("recommendations", p.get("recommendation", [])) or [],
                mitre=p.get("mitre"),
                fraud=p.get("fraud"),
                related_patterns=p.get("related_patterns", []),
                dependencies=p.get("dependencies", []),
                weights=p.get("weights", {}),
            )
            self._patterns.setdefault(pname, {})[version] = typed
            if typed.confidence_model:
                self._confidence[pname] = typed.confidence_model
            if typed.mitre:
                identifier = typed.mitre.get("technique") or typed.mitre.get("id")
                if identifier:
                    self._mitre[str(identifier)] = MitreTechnique(
                        id=str(identifier), name=str(typed.mitre.get("name") or identifier),
                        tactic=typed.mitre.get("tactic"), references=typed.mitre.get("references", []),
                    )
            if typed.fraud:
                identifier = typed.fraud.get("id") or typed.fraud.get("name")
                if identifier:
                    self._fraud[str(identifier)] = FraudPattern.model_validate({"id": identifier, **typed.fraud})
            for rec in typed.recommendations:
                if rec.id:
                    self._recommendations[rec.id] = rec
            for edge in typed.edges:
                if edge.get("from") and edge.get("to") and edge.get("type"):
                    self._relationships.append(PatternRelationship(source=edge["from"], target=edge["to"], relationship=edge["type"]))
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

    def list_all_patterns(self) -> List[AttackPattern]:
        return [pattern for versions in self._patterns.values() for pattern in versions.values()]

    def get_indicator(self, indicator_id: str) -> Optional[Dict[str, Any]]:
        return self._indicators.get(indicator_id)

    def list_indicators(self) -> List[Dict[str, Any]]:
        return list(self._indicators.values())

    def get_mitre(self, identifier: str):
        return self._mitre.get(identifier)

    def list_mitre(self):
        return list(self._mitre.values())

    def search(self, query: str) -> List[Any]:
        q = query.lower()
        results = []
        for name, versions in self._patterns.items():
            for pattern in versions.values():
                haystack = pattern.model_dump_json().lower()
                if q in haystack:
                    results.append(pattern)
        return results

    def get_fraud_pattern(self, identifier: str):
        return self._fraud.get(identifier)

    def list_fraud_patterns(self):
        return list(self._fraud.values())

    def get_confidence_model(self, pattern_name: str):
        return self._confidence.get(pattern_name)

    def get_recommendation(self, recommendation_id: str):
        return self._recommendations.get(recommendation_id)

    def get_relationships(self):
        return list(self._relationships)

    def list_recommendations(self):
        return list(self._recommendations.values())

    def list_confidence_models(self):
        return list(self._confidence.values())
