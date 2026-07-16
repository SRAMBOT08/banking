from __future__ import annotations
from datetime import datetime, timedelta, timezone
from random import Random
from typing import Iterable
from uuid import UUID, uuid5, NAMESPACE_URL
from .generators import EnterpriseGenerators
from .models import EventType, ScenarioName, Severity, SimulationEvent
from .scenario_library import SCENARIO_LIBRARY, ScenarioDefinition


class TimelineEngine:
    def expand(self, definition: ScenarioDefinition, start: datetime) -> list[tuple[datetime, object]]:
        return [(start + timedelta(minutes=step.offset_minutes), step) for step in definition.steps]


class NoiseGenerator:
    def __init__(self, rng: Random): self.rng = rng
    def generate(self, start: datetime, count: int, identity: dict, network: dict) -> list[dict]:
        actions = [('normal_login', EventType.AUTHENTICATION), ('routine_dns', EventType.NETWORK), ('card_purchase', EventType.TRANSACTION), ('vpn_keepalive', EventType.NETWORK), ('employee_activity', EventType.CLOUD)]
        return [{'timestamp': start + timedelta(minutes=self.rng.randrange(0, max(count * 3, 1))), 'action': action, 'event_type': event_type, 'severity': Severity.INFO, 'payload': {'legitimate': True}} for action, event_type in (actions[self.rng.randrange(len(actions))] for _ in range(count))]


class AttackMutator:
    def __init__(self, rng: Random): self.rng = rng
    def mutate(self, payload: dict, scenario: ScenarioName) -> dict:
        result = dict(payload)
        if scenario in {ScenarioName.LARGE_BANKING_TRANSFER, ScenarioName.ACCOUNT_TAKEOVER} and 'amount' in result:
            result['amount'] = round(float(result['amount']) * (0.85 + self.rng.random() * 0.3), 2)
        result['simulation_variant'] = self.rng.randrange(1, 10000)
        return result


class EventGenerator:
    def __init__(self, rng: Random):
        self.rng = rng
        self.entities = EnterpriseGenerators(rng)
        self.timeline = TimelineEngine()
        self.noise = NoiseGenerator(rng)
        self.mutator = AttackMutator(rng)

    def generate(self, scenario: ScenarioName, tenant_id: str, start: datetime, seed: int, noise_ratio: float = .7, simulation_id: UUID | None = None) -> list[SimulationEvent]:
        definition = SCENARIO_LIBRARY[scenario]
        simulation_id = simulation_id or uuid5(NAMESPACE_URL, f'sentineliq:simulation:{tenant_id}:{scenario.value}:{seed}')
        correlation_id = uuid5(simulation_id, f'correlation:{scenario.value}')
        identity = self.entities.identity(seed % 8)
        device = self.entities.device(seed % 8)
        location = self.entities.location(seed % 4)
        network = self.entities.network(seed % 8)
        candidates: list[tuple[datetime, EventType, Severity, str, dict]] = []
        for timestamp, step in self.timeline.expand(definition, start):
            payload = self.mutator.mutate(step.payload, scenario)
            payload.update({'action': step.action, 'attack': True, 'attack_tags': definition.attack_tags})
            candidates.append((timestamp, step.event_type, step.severity, step.action, payload))
        noise_count = round(len(candidates) * noise_ratio * 2)
        for item in self.noise.generate(start, noise_count, identity, network):
            candidates.append((item['timestamp'], item['event_type'], item['severity'], item['action'], item['payload']))
        candidates.sort(key=lambda item: (item[0], item[3]))
        events = []
        for sequence, (timestamp, event_type, severity, action, payload) in enumerate(candidates, 1):
            entity = {'user': identity, 'device': device, 'location': location, 'network': network, 'account': self.entities.account(seed % 8)}
            event_id = uuid5(simulation_id, f'{scenario.value}:{sequence}:{timestamp.isoformat()}:{action}')
            normalized_timestamp = timestamp.astimezone(timezone.utc)
            events.append(SimulationEvent(event_id=event_id, timestamp=normalized_timestamp, ingestion_timestamp=normalized_timestamp, event_type=event_type, correlation_id=correlation_id, investigation_id=simulation_id, tenant_id=tenant_id, source_id=f'sim-{simulation_id}', severity=severity, scenario=scenario, sequence=sequence, entity=entity, payload=payload, metadata={'simulation_id': str(simulation_id), 'seed': seed, 'scenario_description': definition.description, 'timeline_position': sequence, 'deterministic_replay_key': f'{simulation_id}:{sequence}'}))
        return events


class ScenarioEngine:
    def __init__(self, generator: EventGenerator | None = None): self.generator = generator or EventGenerator(Random())
    def run(self, scenarios: Iterable[ScenarioName], tenant_id: str, start: datetime | None = None, seed: int = 1, noise_ratio: float = .7, simulation_id: UUID | None = None) -> list[SimulationEvent]:
        start = (start or datetime.now(timezone.utc)).astimezone(timezone.utc)
        generator = EventGenerator(Random(seed))
        result = []
        for index, scenario in enumerate(scenarios):
            result.extend(generator.generate(scenario, tenant_id, start + timedelta(minutes=index * 2), seed + index, noise_ratio, simulation_id))
        return sorted(result, key=lambda event: (event.timestamp, event.sequence, event.event_id.hex))


class ScenarioComposer:
    """Compose independently executable scenarios into one correlated run."""
    def __init__(self, engine: ScenarioEngine | None = None): self.engine = engine or ScenarioEngine()
    def compose(self, scenarios: Iterable[ScenarioName], tenant_id: str = 'demo-bank', seed: int = 1, start: datetime | None = None, noise_ratio: float = .7) -> list[SimulationEvent]:
        return self.engine.run(scenarios, tenant_id, start, seed, noise_ratio)
