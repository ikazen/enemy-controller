from datetime import datetime, timezone

from fastapi import APIRouter

from app.panels import HealthState, HealthStatus, Metric, Panel, register


async def _fetch_airflow(_role: str) -> HealthStatus:
    return HealthStatus(
        name="Airflow",
        state=HealthState.OK,
        latency_ms=42.1,
        detail=None,
        checked_at=datetime.now(timezone.utc),
    )


async def _fetch_grafana(_role: str) -> HealthStatus:
    return HealthStatus(
        name="Grafana",
        state=HealthState.OK,
        latency_ms=18.3,
        detail=None,
        checked_at=datetime.now(timezone.utc),
    )


async def _fetch_minio(_role: str) -> HealthStatus:
    return HealthStatus(
        name="MinIO",
        state=HealthState.DOWN,
        latency_ms=None,
        detail="connection refused",
        checked_at=datetime.now(timezone.utc),
    )


async def _fetch_reflexion_daemon(_role: str) -> HealthStatus:
    return HealthStatus(
        name="reflexion-daemon",
        state=HealthState.OK,
        latency_ms=7.5,
        detail=None,
        checked_at=datetime.now(timezone.utc),
    )


async def _fetch_summary(_role: str) -> list[Metric]:
    return [
        Metric(label="Services", value="4/5", hint="1 down"),
        Metric(label="Uptime", value="99.2%"),
        Metric(label="DAGs running", value="3"),
    ]


class InfraService:
    key = "infra"
    title = "Infra"

    def __init__(self) -> None:
        self._panels = [
            Panel(
                id="infra-airflow",
                title="Airflow",
                fetch=_fetch_airflow,
                template="partials/panel_health.html",
                refresh_seconds=15,
            ),
            Panel(
                id="infra-grafana",
                title="Grafana",
                fetch=_fetch_grafana,
                template="partials/panel_health.html",
                refresh_seconds=15,
            ),
            Panel(
                id="infra-minio",
                title="MinIO",
                fetch=_fetch_minio,
                template="partials/panel_health.html",
                refresh_seconds=15,
            ),
            Panel(
                id="infra-reflexion-daemon",
                title="reflexion-daemon",
                fetch=_fetch_reflexion_daemon,
                template="partials/panel_health.html",
                refresh_seconds=15,
            ),
            Panel(
                id="infra-summary",
                title="Summary",
                fetch=_fetch_summary,
                template="partials/panel_metrics.html",
                refresh_seconds=30,
            ),
        ]
        for p in self._panels:
            register(p)

    def panels(self) -> list[Panel]:
        return self._panels

    def router(self) -> APIRouter:
        return APIRouter()
