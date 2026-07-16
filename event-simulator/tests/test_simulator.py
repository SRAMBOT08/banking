from datetime import datetime, timezone
from random import Random

from app.engine import EventGenerator, ScenarioEngine
from app.models import EventType, ScenarioName
from app.publisher import InMemoryPublisher
from app.scheduler import SimulationScheduler


START = datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc)


def test_every_scenario_is_independently_executable():
    generator = EventGenerator(Random(42))
    for scenario in ScenarioName:
        events = generator.generate(scenario, 'bank', START, 42, noise_ratio=0)
        assert events, scenario
        assert any(event.scenario == scenario for event in events)
        assert all(event.timestamp.tzinfo is not None for event in events)
        assert all(event.correlation_id for event in events)


def test_replay_is_deterministic():
    first = ScenarioEngine().run([ScenarioName.ACCOUNT_TAKEOVER], 'bank', START, 99, 0)
    second = ScenarioEngine().run([ScenarioName.ACCOUNT_TAKEOVER], 'bank', START, 99, 0)
    assert [event.model_dump(mode='json') for event in first] == [event.model_dump(mode='json') for event in second]


def test_noise_is_interleaved_with_attack_telemetry():
    events = ScenarioEngine().run([ScenarioName.LARGE_BANKING_TRANSFER], 'bank', START, 5, .8)
    assert any(event.payload.get('attack') for event in events)
    assert any(event.payload.get('legitimate') for event in events)
    assert events == sorted(events, key=lambda event: (event.timestamp, event.sequence, event.event_id.hex))


def test_composes_multiple_concurrent_scenarios():
    events = ScenarioEngine().run([ScenarioName.PHISHING_CAMPAIGN, ScenarioName.TOR_LOGIN], 'bank', START, 3, 0)
    assert {event.scenario for event in events} == {ScenarioName.PHISHING_CAMPAIGN, ScenarioName.TOR_LOGIN}


def test_scheduler_publishes_independent_run():
    publisher = InMemoryPublisher()
    scheduler = SimulationScheduler(publisher)
    # Exercise the engine synchronously to avoid making the unit test depend on a running loop.
    events = scheduler.engine.run([ScenarioName.NEW_DEVICE_LOGIN], 'bank', START, 7, 0)
    for event in events: publisher.publish(event)
    assert len(publisher.events) == 3
    assert publisher.events[0].event_type in {EventType.AUTHENTICATION, EventType.ASSET}
