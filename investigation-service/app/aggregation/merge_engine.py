from __future__ import annotations

from typing import Any, Iterable
from .models import MergeStatistics


class DeterministicMergeEngine:
    """Merge service facts by canonical IDs while retaining source attribution."""

    def merge(self, sections: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, list[dict[str, Any]]], MergeStatistics]:
        merged: dict[str, list[dict[str, Any]]] = {}
        duplicates: dict[str, int] = {}
        inputs = {key: len(value) for key, value in sections.items()}
        for section, items in sections.items():
            unique: dict[str, dict[str, Any]] = {}
            duplicate_count = 0
            for item in items:
                identifier = str(item.get("id") or item.get("name") or repr(sorted(item.items())))
                if identifier in unique:
                    duplicate_count += 1
                    existing = unique[identifier]
                    sources = set(existing.get("sources", [])) | set(item.get("sources", [])) | {str(item.get("source", "unknown"))}
                    existing["sources"] = sorted(sources)
                    for key, value in item.items():
                        if key not in existing or existing[key] in (None, "", [], {}):
                            existing[key] = value
                else:
                    copy = dict(item)
                    copy["sources"] = sorted(set(copy.get("sources", [])) | {str(copy.get("source", "unknown"))})
                    unique[identifier] = copy
            merged[section] = list(unique.values())
            duplicates[section] = duplicate_count
        return merged, MergeStatistics(input_counts=inputs, output_counts={key: len(value) for key, value in merged.items()}, duplicates_removed=duplicates)
