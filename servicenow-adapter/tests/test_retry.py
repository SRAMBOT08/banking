import pytest

from app.models import RetryPolicy
from app.retry.engine import RetryEngine, RetryState


@pytest.mark.asyncio
async def test_retry_engine_exponential_backoff_path():
    engine = RetryEngine(RetryPolicy(max_retries=2, base_delay_ms=10, max_delay_ms=10))
    state = RetryState(attempt=0)
    assert engine.should_retry(500, None, state)
    await engine.backoff(state)
    state.attempt = 1
    assert engine.should_retry(429, None, state)
    await engine.backoff(state)
    state.attempt = 2
    assert not engine.should_retry(500, None, state)
