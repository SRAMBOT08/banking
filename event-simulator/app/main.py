from __future__ import annotations
from uuid import UUID
from fastapi import FastAPI, HTTPException
from .config import settings
from .models import ScenarioName, SimulationRequest, SimulationStatus
from .publisher import publisher_from_settings
from .scenario_library import SCENARIO_LIBRARY
from .scheduler import SimulationScheduler

publisher = publisher_from_settings()
scheduler = SimulationScheduler(publisher)
app = FastAPI(title='SentinelIQ Enterprise Event Simulator', version='1.0.0')


@app.get('/health')
async def health() -> dict:
    return {'status': 'ok', 'service': settings.service_name, 'transport': settings.transport, 'topic': settings.event_topic}


@app.get('/scenarios')
async def scenarios() -> list[dict]:
    return [{'name': name.value, 'description': definition.description, 'attack_tags': definition.attack_tags, 'steps': len(definition.steps)} for name, definition in SCENARIO_LIBRARY.items()]


@app.post('/simulations', response_model=SimulationStatus, status_code=202)
async def start_simulation(request: SimulationRequest) -> SimulationStatus:
    unknown = [scenario for scenario in request.scenarios if scenario not in SCENARIO_LIBRARY]
    if unknown: raise HTTPException(400, f'Unsupported scenarios: {unknown}')
    return scheduler.start(request)


@app.get('/simulations/{simulation_id}', response_model=SimulationStatus)
async def simulation_status(simulation_id: UUID) -> SimulationStatus:
    result = scheduler.status(simulation_id)
    if result is None: raise HTTPException(404, 'Simulation not found')
    return result


@app.get('/simulations/{simulation_id}/events')
async def simulation_events(simulation_id: UUID) -> list[dict]:
    if scheduler.status(simulation_id) is None: raise HTTPException(404, 'Simulation not found')
    return [event.model_dump(mode='json') for event in scheduler.events(simulation_id)]


@app.post('/simulations/{simulation_id}/stop', response_model=SimulationStatus)
async def stop_simulation(simulation_id: UUID) -> SimulationStatus:
    if scheduler.status(simulation_id) is None: raise HTTPException(404, 'Simulation not found')
    await scheduler.stop(simulation_id)
    return scheduler.status(simulation_id)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=settings.api_port)
