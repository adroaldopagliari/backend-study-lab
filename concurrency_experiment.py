#!/usr/bin/env python3
"""Deterministic discrete-event simulation; not a real system benchmark."""
import argparse
import heapq
import json
import math
import platform
from pathlib import Path


def simulate(workers, jobs=2000, capacity=8, penalty_ms=2.0, limit=None):
    if min(workers, jobs, capacity) < 1 or penalty_ms < 0 or (limit is not None and limit < 1):
        raise ValueError('Counts must be positive and penalty nonnegative')
    slots = min(workers, limit or workers, jobs)
    events, service_times = [], []
    launched = completed = 0
    now = 0.0

    def launch(at):
        nonlocal launched
        active = len(events) + 1
        # An explicit hypothesis: dependency contention increases service time.
        duration = 100.0 + penalty_ms * max(0, active - capacity) ** 2
        service_times.append(duration)
        heapq.heappush(events, (at + duration, launched))
        launched += 1

    for _ in range(slots):
        launch(now)
    while events:
        now, _ = heapq.heappop(events)
        completed += 1
        if launched < jobs:
            launch(now)
    ordered = sorted(service_times)
    return dict(workers=workers, inflight_limit=limit, completed=completed,
                simulated_seconds=round(now / 1000, 3),
                useful_jobs_per_second=round(completed * 1000 / now, 3),
                p95_service_ms=round(ordered[math.ceil(.95 * jobs) - 1], 3))


def experiment():
    return {
        'kind': 'synthetic discrete-event simulation',
        'model_version': 1,
        'runtime': platform.python_version(),
        'parameters': {'jobs': 2000, 'base_service_ms': 100, 'dependency_capacity': 8,
                       'contention_penalty_ms': 2, 'arrivals': 'entire batch at time zero'},
        'service_time_rule': '100 + 2 * max(0, active_jobs_at_start - 8)^2 milliseconds',
        'limitations': ['Contention is assumed, not discovered.',
                       'Service time is fixed at job start; later concurrency changes do not alter it.',
                       'No real threads, database, network, retries, CPU or cloud costs are measured.',
                       'p95 service time excludes waiting in the batch queue.'],
        'contention': [simulate(w) for w in (1, 4, 8, 16, 32)],
        'no_contention_control': [simulate(w, penalty_ms=0) for w in (1, 4, 8, 16, 32)],
        'bounded_control': simulate(32, limit=8),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(experiment(), indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result)
    else:
        print(result, end='')
