class CaseBuilderError(RuntimeError):
    """Base case builder error."""


class ContextValidationError(CaseBuilderError):
    """The supplied investigation context cannot become a case."""


class CaseNotFoundError(CaseBuilderError):
    """The requested case or version does not exist."""


class ImmutableVersionError(CaseBuilderError):
    """An existing case version cannot be overwritten."""
