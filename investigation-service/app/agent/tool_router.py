from __future__ import annotations
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any, Dict, Optional
from .tools import interfaces

logger = logging.getLogger(__name__)


class ToolResolutionError(LookupError):
    pass


class ToolExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolPolicy:
    timeout_seconds: Optional[float] = None
    max_retries: int = 0


class ToolRouter:
    """Holds concrete tool instances and dispatches calls. DI boundary for the Agent."""

    def __init__(self, tools: Optional[Dict[str, interfaces.Tool]] = None, policies: Optional[Dict[str, ToolPolicy]] = None):
        self._tools: Dict[str, Dict[str, interfaces.Tool]] = {}
        self._policies = policies or {}
        self.execution_history: list[Dict[str, Any]] = []
        for name, tool in (tools or {}).items():
            self.register(name, tool)

    def register(self, name: str, tool: interfaces.Tool, version: str = "1") -> None:
        if name in self._tools and version in self._tools[name]:
            raise ValueError(f"Tool already registered: {name}@{version}")
        self._tools.setdefault(name, {})[version] = tool

    def unregister(self, name: str, version: str = "1") -> None:
        if name not in self._tools or version not in self._tools[name]:
            raise ToolResolutionError(f"Tool is not registered: {name}@{version}")
        del self._tools[name][version]
        if not self._tools[name]:
            del self._tools[name]

    def get(self, name: str, version: Optional[str] = None) -> interfaces.Tool:
        versions = self._tools.get(name)
        if not versions:
            raise ToolResolutionError(f"Tool is not registered: {name}")
        selected = version or sorted(versions)[-1]
        if selected not in versions:
            raise ToolResolutionError(f"Tool version is not registered: {name}@{selected}")
        return versions[selected]

    def invoke(self, name: str, *args: Any, version: Optional[str] = None, **kwargs: Any) -> Any:
        started = datetime.now(timezone.utc)
        tool = self.get(name, version)
        policy = self._policies.get(name, ToolPolicy())
        logger.info({"event": "tool_invoked", "tool": name, "version": version or "latest", "timestamp": started.isoformat()})
        last_error: Optional[Exception] = None
        for attempt in range(policy.max_retries + 1):
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(tool.execute, *args, **kwargs)
            try:
                result = future.result(timeout=policy.timeout_seconds)
                duration = (datetime.now(timezone.utc) - started).total_seconds() * 1000
                record = {"tool": name, "version": version or "latest", "attempt": attempt + 1, "duration_ms": duration, "status": "completed"}
                self.execution_history.append(record)
                logger.info({"event": "tool_completed", **record})
                executor.shutdown(wait=True)
                return result
            except FutureTimeout as exc:
                last_error = ToolExecutionError(f"Tool timed out: {name}")
            except Exception as exc:
                last_error = exc
            finally:
                if last_error is not None:
                    future.cancel()
                    executor.shutdown(wait=False, cancel_futures=True)
            self.execution_history.append({"tool": name, "attempt": attempt + 1, "status": "retrying", "error": str(last_error)})
            logger.warning({"event": "tool_retry", "tool": name, "attempt": attempt + 1, "error": str(last_error)})
        logger.error("tool_failed", extra={"tool": name})
        raise ToolExecutionError(f"Tool execution failed: {name}") from last_error

    def discover(self, prefix: Optional[str] = None) -> list[str]:
        names = sorted(self._tools)
        return [name for name in names if prefix is None or name.startswith(prefix)]
