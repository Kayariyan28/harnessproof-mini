"""Deterministic API orchestration / explicit provider allowlist; NEVER auto-switch to billed routes."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoint:
    alias: str
    model: str
    free_verified: bool = False


class ProviderRouter:
    """Dispatch to caller-supplied transport; no credentials, secret logging or paid fallback."""
    def __init__(self, endpoints, max_requests=10):
        if not (1 <= max_requests <= 100):
            raise ValueError('Bound calls to 1-100')
        self.endpoints={e.alias:e for e in endpoints}
        self.max_requests=max_requests
        self.calls=0

    def call(self, alias, messages, transport):
        endpoint=self.endpoints.get(alias)
        if endpoint is None:
            raise ValueError('Unknown provider alias')
        if not endpoint.free_verified:
            raise PermissionError('Provider not verified free; explicit configuration required')
        if self.calls >= self.max_requests:
            raise RuntimeError('API quota cap reached')
        self.calls+=1
        return transport(endpoint,messages)
