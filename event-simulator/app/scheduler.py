from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from threading import Lock
from uuid import UUID, uuid4
from .engine import ScenarioEngine
from .models import SimulationRequest, SimulationStatus
from .publisher import EventPublisher


class SimulationScheduler:
    def __init__(self, publisher: EventPublisher, engine: ScenarioEngine | None = None):
        self.publisher, self.engine = publisher, engine or ScenarioEngine()
        self._statuses: dict[UUID, SimulationStatus] = {}
        self._events: dict[UUID, list] = {}
        self._tasks: dict[UUID, asyncio.Task] = {}
        self._lock = Lock()

    def start(self, request: SimulationRequest) -> SimulationStatus:
        simulation_id = uuid4()
        status = SimulationStatus(simulation_id=simulation_id, status='running', scenarios=request.scenarios, seed=request.seed, started_at=datetime.now(timezone.utc))
        with self._lock: self._statuses[simulation_id] = status
        task = asyncio.create_task(self._run(simulation_id, request))
        self._tasks[simulation_id] = task
        return status

    async def _run(self, simulation_id: UUID, request: SimulationRequest) -> None:
        try:
            events = self.engine.run(request.scenarios, request.tenant_id, request.start_time, request.seed, request.noise_ratio, simulation_id)
            self._events[simulation_id] = events
            interval = 1 / request.event_rate_per_second if request.event_rate_per_second else 0
            deadline = asyncio.get_running_loop().time() + request.duration_seconds if request.duration_seconds else None
            for event in events:
                if simulation_id not in self._tasks: return
                self.publisher.publish(event)
                status = self._statuses[simulation_id]
                status.generated_events += 1; status.published_events += 1
                if interval: await asyncio.sleep(interval)
                if deadline and asyncio.get_running_loop().time() >= deadline: break
            self.publisher.flush()
            self._statuses[simulation_id].status = 'completed'
            self._statuses[simulation_id].stopped_at = datetime.now(timezone.utc)
        except asyncio.CancelledError:
            self._statuses[simulation_id].status = 'stopped'
            self._statuses[simulation_id].stopped_at = datetime.now(timezone.utc)
        except Exception as exc:
            self._statuses[simulation_id].status = 'failed'; self._statuses[simulation_id].error = str(exc)

    def status(self, simulation_id: UUID) -> SimulationStatus | None: return self._statuses.get(simulation_id)
    def events(self, simulation_id: UUID) -> list: return self._events.get(simulation_id, [])
    async def stop(self, simulation_id: UUID) -> bool:
        task = self._tasks.get(simulation_id)
        if not task: return False
        task.cancel(); await asyncio.gather(task, return_exceptions=True); self._tasks.pop(simulation_id, None); return True
