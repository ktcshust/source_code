# aiobreaker / pybreaker wrappers + decorators
# app/circuit_breaker.py
from aiobreaker import CircuitBreakerListener, CircuitBreaker
import pybreaker
import asyncio
from typing import Callable, Any
from app.logging import log

# async circuit breaker for async calls (aiobreaker)
class _LogCBListener(CircuitBreakerListener):
    async def state_change(self, cb, old_state, new_state):
        log.info("circuit_state_change", circuit=cb.name, from_state=str(old_state), to_state=str(new_state))

def async_circuitbreaker(name: str, fail_max: int = 5, reset_timeout: int = 60):
    cb = CircuitBreaker(fail_max=fail_max, reset_timeout=reset_timeout, name=name, listeners=[_LogCBListener()])
    return cb

# sync breaker (pybreaker) example
def sync_circuitbreaker(name: str, fail_max: int = 5, reset_timeout: int = 60):
    return pybreaker.CircuitBreaker(fail_max=fail_max, reset_timeout=reset_timeout)

# usage example:
# cb = async_circuitbreaker("openai")
# @cb
# async def call_openai(...):
#     ...

