class QueryError(RuntimeError):
    pass


class QueryNotFoundError(QueryError):
    pass


class QueryValidationError(QueryError):
    pass
