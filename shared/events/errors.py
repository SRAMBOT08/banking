class EventValidationError(Exception):
    """Raised when an event fails validation."""


class SchemaVersionError(EventValidationError):
    """Raised when event schema version is unsupported or invalid."""


class SerializationError(EventValidationError):
    """Raised when serialization/deserialization fails."""


class DuplicateEventRegistrationError(EventValidationError):
    """Raised when an event is registered twice."""


class UnknownEventError(EventValidationError):
    """Raised when event type/version is not registered."""
