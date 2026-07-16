from collections import Counter


class Metrics:
    def __init__(self):
        self.requests = Counter()
        self.failures = Counter()
        self.latencies = []

    def record_request(self, service: str):
        self.requests[service] += 1

    def record_failure(self, service: str):
        self.failures[service] += 1

    def record_latency(self, latency_ms: float):
        self.latencies.append(latency_ms)
