from datetime import datetime, timezone

from fastapi import APIRouter

from app.panels import Metric, Panel, register


async def _fetch_best_scores(_role: str) -> list[dict]:
    return [
        {
            "id": "titanic",
            "name": "Titanic Survival",
            "best_score": 0.8231,
            "submissions": 12,
            "last_submission_at": "2026-06-01",
        },
        {
            "id": "house-prices",
            "name": "House Prices",
            "best_score": 0.9412,
            "submissions": 7,
            "last_submission_at": "2026-05-15",
        },
    ]


async def _fetch_cycles(_role: str) -> dict:
    return {
        "training_runs": 47,
        "cycle": 3,
        "metrics": [
            Metric(label="Best Score", value="0.8231"),
            Metric(label="Avg Score", value="0.7904"),
            Metric(label="Cycle", value="3"),
        ],
    }


async def _fetch_submissions(_role: str) -> list[dict]:
    return [
        {"competition": "Titanic Survival", "last_submission_at": "2026-06-01 15:30 UTC"},
        {"competition": "House Prices", "last_submission_at": "2026-05-15 09:00 UTC"},
    ]


async def _fetch_queue(_role: str) -> dict:
    return {
        "running": 1,
        "pending": 2,
        "items": [
            {
                "id": "q-001",
                "competition_id": "titanic",
                "status": "running",
                "enqueued_at": datetime(2026, 6, 13, 10, 0, tzinfo=timezone.utc),
            },
            {
                "id": "q-002",
                "competition_id": "house-prices",
                "status": "pending",
                "enqueued_at": datetime(2026, 6, 13, 10, 5, tzinfo=timezone.utc),
            },
        ],
    }


async def _fetch_queue_control(_role: str) -> dict:
    return {}


class ReflexionRondoService:
    key = "reflexion-rondo"
    title = "reflexion-rondo"

    def __init__(self) -> None:
        self._panels = [
            Panel(
                id="rondo-best-scores",
                title="Best Scores",
                fetch=_fetch_best_scores,
                template="partials/panel_scores.html",
                refresh_seconds=60,
                grid_w=6, grid_h=4,
            ),
            Panel(
                id="rondo-cycles",
                title="Training Cycles",
                fetch=_fetch_cycles,
                template="partials/panel_metrics.html",
                refresh_seconds=30,
                grid_w=3, grid_h=3,
            ),
            Panel(
                id="rondo-submissions",
                title="Last Submissions",
                fetch=_fetch_submissions,
                template="partials/panel_submissions.html",
                refresh_seconds=60,
                grid_w=3, grid_h=3,
            ),
            Panel(
                id="rondo-queue",
                title="Queue",
                fetch=_fetch_queue,
                template="partials/panel_queue.html",
                refresh_seconds=10,
                grid_w=4, grid_h=3,
            ),
            Panel(
                id="rondo-queue-control",
                title="Queue Control",
                fetch=_fetch_queue_control,
                template="partials/panel_queue_control.html",
                refresh_seconds=0,
                public=False,
                grid_w=4, grid_h=2,
            ),
        ]
        for p in self._panels:
            register(p)

    def panels(self) -> list[Panel]:
        return self._panels

    def router(self) -> APIRouter:
        return APIRouter()
