from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Mapping, Protocol


class ConfidenceStrategy(Protocol):
    def aggregate(self, scores: Mapping[str, float], weights: Mapping[str, float]) -> float: ...


class WeightedAverage:
    def aggregate(self, scores: Mapping[str, float], weights: Mapping[str, float]) -> float:
        total = sum(max(0.0, float(weights.get(name, 0.0))) for name in scores)
        return sum(max(0.0, min(1.0, float(score))) * max(0.0, float(weights.get(name, 0.0))) for name, score in scores.items()) / total if total else 0.0


@dataclass
class ConfidenceManager:
    weights: Dict[str, float] = field(default_factory=lambda: {"knowledge": 1.0, "pattern": 1.0, "graph": 1.0, "history": 1.0, "policy": 1.0, "ml": 0.0, "threat_feed": 0.0})
    strategy: ConfidenceStrategy = field(default_factory=WeightedAverage)

    def aggregate(self, scores: Mapping[str, float]) -> float:
        normalized = self._normalize(scores)
        return self.strategy.aggregate(normalized, self.weights)

    def breakdown(self, scores: Mapping[str, float]) -> Dict[str, float]:
        normalized = self._normalize(scores)
        normalized["final"] = self.aggregate(normalized)
        return normalized

    def aggregate_result(self, scores: Mapping[str, float]) -> Dict[str, object]:
        breakdown = self.breakdown(scores)
        return {"overall_confidence": breakdown["final"], "confidence_breakdown": breakdown, "confidence_explanation": self.explain(breakdown)}

    @staticmethod
    def explain(breakdown: Mapping[str, float]) -> str:
        contributors = sorted(((name, value) for name, value in breakdown.items() if name != "final"), key=lambda item: item[1], reverse=True)
        return "Confidence is the configured weighted aggregation of " + ", ".join(f"{name}={value:.2f}" for name, value in contributors) + "."

    def _normalize(self, scores: Mapping[str, float]) -> Dict[str, float]:
        aliases = {"knowledge_score": "knowledge", "pattern_match": "pattern", "pattern_match_score": "pattern", "historical": "history", "historical_score": "history", "graph_score": "graph", "policy_score": "policy", "future_ml": "ml", "future_ml_score": "ml", "threat_feed_score": "threat_feed"}
        return {aliases.get(name, name): max(0.0, min(1.0, float(value))) for name, value in scores.items()}
