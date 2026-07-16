class AggregationError(RuntimeError):
    """Base error for deterministic intelligence aggregation."""


class AggregationValidationError(AggregationError):
    """Raised when a unified context fails validation."""
