from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SLOSnapshot:
    goal_completion_rate: float = 0.0
    validated_result_rate: float = 0.0
    unsupported_claim_rate: float = 0.0
    recovery_success_rate: float = 0.0
    human_escalation_rate: float = 0.0
    duplicate_side_effect_rate: float = 0.0
    mean_cost_per_success: float = 0.0
    p50_latency: float = 0.0
    p95_latency: float = 0.0
    p99_latency: float = 0.0
    checkpoint_recovery_seconds: float = 0.0
    queue_delay: float = 0.0
    replan_frequency: float = 0.0
    validator_disagreement: float = 0.0
    security_violation_rate: float = 0.0
    memory_contamination_rate: float = 0.0


@dataclass
class SLOTracker:
    successes: int = 0
    attempts: int = 0
    latencies: list[float] = field(default_factory=list)

    def record(self, *, ok: bool, latency: float) -> None:
        self.attempts += 1
        if ok:
            self.successes += 1
        self.latencies.append(latency)

    def snapshot(self) -> SLOSnapshot:
        lat = sorted(self.latencies) or [0.0]
        def pct(p: float) -> float:
            return lat[min(len(lat) - 1, int(p * (len(lat) - 1)))]

        return SLOSnapshot(
            goal_completion_rate=self.successes / self.attempts if self.attempts else 0.0,
            p50_latency=pct(0.50),
            p95_latency=pct(0.95),
            p99_latency=pct(0.99),
        )
