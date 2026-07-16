from __future__ import annotations


class OrchestrationError(Exception):
    """Base error raised by the investigation orchestration boundary."""


class RecoverableError(OrchestrationError):
    """Failure that can be recovered from a checkpoint."""


class RetryableError(RecoverableError):
    """Transient failure eligible for retry policy."""


class OrchestrationTimeout(RetryableError):
    """Node or workflow exceeded its configured execution timeout."""


class FatalError(OrchestrationError):
    """Failure that must stop the workflow and propagate to the caller."""


class WorkflowCancelled(OrchestrationError):
    """Graceful cancellation requested by the workflow owner."""
