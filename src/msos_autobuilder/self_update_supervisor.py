"""Repository-local supervisor contract used by staged Windows handoff probes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

MANAGED_TASK_NAMES: tuple[str, ...] = (
    "PPE Headless Stack",
    "PPE VM Watchdog",
    "PPE VM Hygiene",
    "PPE Network Watchdog",
    "PPE Desktop Mirror Sync",
)


@dataclass(frozen=True)
class ManagedTaskState:
    name: str
    state: str


@dataclass(frozen=True)
class TaskStateValidation:
    task_count: int
    ready_count: int
    states: tuple[ManagedTaskState, ...]


class PowerShellTaskController:
    """Validate staged PowerShell task state snapshots without mutating the host."""

    def __init__(self, states: Mapping[str, str] | None = None) -> None:
        self._states = dict(states or {})

    def states_for_task_names(self, task_names: tuple[str, ...] = MANAGED_TASK_NAMES) -> tuple[ManagedTaskState, ...]:
        return tuple(ManagedTaskState(name=name, state=self._states.get(name, "Unknown")) for name in task_names)

    def validate_states(self, task_names: tuple[str, ...] = MANAGED_TASK_NAMES) -> TaskStateValidation:
        states = self.states_for_task_names(task_names)
        ready_count = sum(1 for task in states if task.state == "Ready")
        return TaskStateValidation(task_count=len(states), ready_count=ready_count, states=states)

