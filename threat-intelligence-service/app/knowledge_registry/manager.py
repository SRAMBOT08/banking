from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from app.core.logger import get_logger
from app.knowledge_registry.inmemory import InMemoryKnowledgeRegistry
from app.knowledge_registry.models import AttackPattern, KnowledgeStatistics
from app.knowledge_registry.providers import ProviderManager
from app.knowledge_registry.validator import validate_registry

logger = get_logger("registry_manager")


class RegistryValidationError(RuntimeError):
    def __init__(self, findings: List[Dict[str, Any]]):
        self.findings = findings
        super().__init__("critical knowledge registry validation errors: " + ", ".join(f["code"] for f in findings))


class RegistryManager:
    """Stable, typed public boundary for all Threat Intelligence knowledge."""

    def __init__(self, patterns_dir: str, cache_ttl: int = 300, registry_version: str = "1",
                 provider_manager: Optional[ProviderManager] = None):
        self.patterns_dir = patterns_dir
        self.cache_ttl = cache_ttl
        self.registry_version = registry_version
        self._backend = InMemoryKnowledgeRegistry(patterns_dir)
        self._providers = provider_manager or ProviderManager()
        self._cache: Dict[str, Any] = {}
        self._cache_created: Dict[str, float] = {}
        self._hits = 0
        self._misses = 0
        self._validation_status = "not_loaded"
        self._validation_findings: List[Dict[str, Any]] = []
        self._load_time = 0.0
        self._reload_time = 0.0

    @property
    def provider_manager(self) -> ProviderManager:
        return self._providers

    def load(self) -> None:
        started = time.perf_counter()
        self._backend.load()
        self._sync_providers()
        findings = self.validate_registry()["findings"]
        critical = [finding for finding in findings if finding["severity"] == "critical"]
        if critical:
            self._validation_status = "invalid"
            raise RegistryValidationError(critical)
        self._validation_status = "valid"
        self._warm_cache()
        self._load_time = time.perf_counter() - started
        logger.info("registry_loaded", extra={"registry_version": self.registry_version, "load_duration": self._load_time})

    def reload_registry(self) -> None:
        started = time.perf_counter()
        self.invalidate_cache()
        self._backend.reload()
        self._sync_providers()
        findings = self.validate_registry()["findings"]
        critical = [finding for finding in findings if finding["severity"] == "critical"]
        if critical:
            self._validation_status = "invalid"
            raise RegistryValidationError(critical)
        self._validation_status = "valid"
        self._warm_cache()
        self._reload_time = time.perf_counter() - started
        logger.info("registry_reloaded", extra={"registry_version": self.registry_version, "load_duration": self._reload_time})

    reload = reload_registry

    def _sync_providers(self) -> None:
        self._providers.replace("attack_patterns", self._backend.list_all_patterns())
        self._providers.replace("indicators", self._backend.list_indicators())
        self._providers.replace("mitre", self._backend.list_mitre())
        self._providers.replace("fraud", self._backend.list_fraud_patterns())
        self._providers.replace("recommendations", self._backend.list_recommendations())
        self._providers.replace("confidence", self._backend.list_confidence_models())
        self._providers.replace("relationships", self._backend.get_relationships())

    def validate_registry(self) -> Dict[str, Any]:
        self._validation_findings = validate_registry(self._backend.raw_patterns)
        return {
            "valid": not any(f["severity"] == "critical" for f in self._validation_findings),
            "findings": list(self._validation_findings),
            "errors": list(self._validation_findings),
        }

    def _warm_cache(self) -> None:
        self._cache["patterns"] = tuple(self._providers.list("attack_patterns"))
        self._cache_created["patterns"] = time.time()

    def invalidate_cache(self) -> None:
        self._cache.clear()
        self._cache_created.clear()

    def _patterns(self) -> List[AttackPattern]:
        created = self._cache_created.get("patterns")
        if created is not None and time.time() - created <= self.cache_ttl:
            self._hits += 1
            return list(self._cache["patterns"])
        self._misses += 1
        patterns = self._providers.list("attack_patterns")
        self._cache["patterns"] = tuple(patterns)
        self._cache_created["patterns"] = time.time()
        return patterns

    @staticmethod
    def _version_key(version: str) -> tuple:
        return tuple(int(part) if part.isdigit() else part.casefold() for part in str(version).replace("-", ".").split("."))

    def get_attack_pattern(self, name: str, version: Optional[str] = None) -> Optional[AttackPattern]:
        patterns = [p for p in self._patterns() if p.name == name]
        if version is not None:
            return next((p for p in patterns if p.version == str(version)), None)
        return max(patterns, key=lambda p: self._version_key(p.version), default=None)

    def get_latest_pattern(self, name: str) -> Optional[AttackPattern]:
        return self.get_attack_pattern(name)

    def list_attack_patterns(self) -> List[AttackPattern]:
        return sorted(self._patterns(), key=lambda p: (p.name, self._version_key(p.version)))

    def list_patterns(self) -> Dict[str, Dict[str, AttackPattern]]:
        result: Dict[str, Dict[str, AttackPattern]] = {}
        for pattern in self.list_attack_patterns():
            result.setdefault(pattern.name, {})[pattern.version] = pattern
        return result

    def search_attack_patterns(self, query: str) -> List[AttackPattern]:
        return sorted(self._providers.search("attack_patterns", query), key=lambda p: (p.name, self._version_key(p.version)))

    def get_indicator(self, indicator_id: str):
        return self._providers.get("indicators", indicator_id)

    def list_indicators(self):
        return self._providers.list("indicators")

    def search_indicators(self, query: str):
        return self._providers.search("indicators", query)

    def get_mitre(self, identifier: str):
        return self._providers.get("mitre", identifier, "id")

    def search_mitre(self, query: str):
        return self._providers.search("mitre", query)

    def get_fraud_pattern(self, identifier: str):
        return self._providers.get("fraud", identifier)

    def search_fraud_patterns(self, query: str):
        return self._providers.search("fraud", query)

    def get_confidence_model(self, pattern_name: str):
        pattern = self.get_latest_pattern(pattern_name)
        return pattern.confidence_model if pattern else None

    def get_recommendation(self, recommendation_id: str):
        return self._providers.get("recommendations", recommendation_id)

    def get_related_patterns(self, name: str) -> List[AttackPattern]:
        pattern = self.get_latest_pattern(name)
        related = set(pattern.related_patterns if pattern else [])
        if pattern and pattern.metadata:
            related.update(pattern.metadata.related_patterns)
        return [candidate for candidate in self.list_attack_patterns() if candidate.name in related]

    def get_pattern_dependencies(self, name: str) -> List[AttackPattern]:
        pattern = self.get_latest_pattern(name)
        dependencies = set(pattern.dependencies if pattern else [])
        if pattern and pattern.metadata:
            dependencies.update(pattern.metadata.dependencies)
        return [candidate for candidate in self.list_attack_patterns() if candidate.name in dependencies]

    def search_knowledge(self, query: str):
        return self.search_attack_patterns(query) + self.search_indicators(query) + self.search_fraud_patterns(query)

    def list_knowledge(self):
        return {"patterns": self.list_attack_patterns(), "indicators": self.list_indicators(), "fraud": self.search_fraud_patterns("")}

    def get_registry_statistics(self) -> KnowledgeStatistics:
        total = self._hits + self._misses
        patterns = self.list_attack_patterns()
        return KnowledgeStatistics(
            pattern_count=len(patterns), indicator_count=len(self.list_indicators()),
            mitre_count=len(self._providers.list("mitre")), fraud_count=len(self._providers.list("fraud")),
            recommendation_count=len(self._providers.list("recommendations")),
            confidence_model_count=len(self._providers.list("confidence")),
            relationship_count=len(self._providers.list("relationships")), registry_version=self.registry_version,
            validation_status=self._validation_status, cache_hit_rate=self._hits / max(1, total),
            cache_miss_rate=self._misses / max(1, total), registry_load_time=self._load_time,
            registry_reload_time=self._reload_time, knowledge_size=sum(len(self._providers.list(domain)) for domain in self._providers.providers),
            provider_count=self._providers.count(),
        )

    get_stats = get_registry_statistics
