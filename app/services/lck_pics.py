from datetime import datetime, timezone

from fastapi import APIRouter

from app.panels import HealthState, HealthStatus, Panel, register


async def _fetch_health(_role: str) -> HealthStatus:
    return HealthStatus(
        name="lck-pics",
        state=HealthState.UNKNOWN,
        latency_ms=None,
        detail="service not yet deployed",
        checked_at=datetime.now(timezone.utc),
    )


class LckPicsService:
    key = "lck-pics"
    title = "lck-pics"

    def __init__(self) -> None:
        self._panels = [
            Panel(
                id="lck-pics-health",
                title="lck-pics",
                fetch=_fetch_health,
                template="partials/panel_health.html",
                refresh_seconds=30,
            ),
        ]
        for p in self._panels:
            register(p)

    def panels(self) -> list[Panel]:
        return self._panels

    def router(self) -> APIRouter:
        return APIRouter()
