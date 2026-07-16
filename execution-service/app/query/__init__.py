from ..repository import CaseExecutionRepository


class ExecutionQueryService:
    def __init__(self, repository: CaseExecutionRepository): self.repository = repository
    def get(self, execution_id): return self.repository.get(execution_id)
    def status(self, execution_id): return self.repository.get(execution_id).status
    def history(self, filters=None): return self.repository.search(filters or {})
    def audit(self, execution_id=None): return self.repository.audit(execution_id)
    def statistics(self): return self.repository.statistics()

__all__ = ['ExecutionQueryService']
