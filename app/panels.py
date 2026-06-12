from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from fastapi import APIRouter


class HealthState(StrEnum):
    OK = "ok"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class HealthStatus:
    name: str
    state: HealthState
    latency_ms: float | None
    detail: str | None
    checked_at: datetime


@dataclass(frozen=True, slots=True)
class Metric:
    label: str
    value: str
    hint: str | None = None


@dataclass(frozen=True, slots=True)
class Panel:
    id: str
    title: str
    fetch: Callable[[str], Awaitable[Any]]
    template: str
    refresh_seconds: int = 10
    public: bool = True


class ServiceModule(Protocol):
    key: str
    title: str

    def panels(self) -> list[Panel]: ...
    def router(self) -> "APIRouter": ...


_registry: dict[str, Panel] = {}


def register(panel: Panel) -> None:
    _registry[panel.id] = panel


def get_panel(panel_id: str) -> Panel | None:
    return _registry.get(panel_id)
