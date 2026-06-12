import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.panels import get_panel
from app.security import Role, get_role
from app.services import SERVICES

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent.parent / "templates")


@router.get("/")
async def index(request: Request, role: Role = Depends(get_role)):
    active = next(s for s in SERVICES if s.key == "infra")
    return templates.TemplateResponse(
        request,
        "index.html",
        {"services": SERVICES, "active": active, "service": active, "role": role},
    )


@router.get("/services/{key}")
async def service_grid(key: str, request: Request, role: Role = Depends(get_role)):
    service = next((s for s in SERVICES if s.key == key), None)
    if service is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request,
        "partials/grid.html",
        {"service": service, "role": role},
    )


@router.get("/panels/{panel_id}")
async def panel_render(panel_id: str, request: Request, role: Role = Depends(get_role)):
    panel = get_panel(panel_id)
    if panel is None:
        raise HTTPException(status_code=404)
    if not panel.public and role == Role.PUBLIC:
        return HTMLResponse("")
    data = await panel.fetch(role)
    return templates.TemplateResponse(
        request,
        panel.template,
        {"panel": panel, "data": data, "role": role},
    )


@router.post("/services/{key}/queue")
async def queue_insert(key: str, request: Request, role: Role = Depends(get_role)):
    if role != Role.ADMIN:
        raise HTTPException(status_code=403)
    logger.info("audit: queue insert requested by %s", request.headers.get("Tailscale-User-Login", "dev"))
    return HTMLResponse(
        '<div class="alert alert-info text-sm">insert queued (not yet implemented)</div>'
    )


@router.post("/services/{key}/queue/{item_id}/cancel")
async def queue_cancel(key: str, item_id: str, request: Request, role: Role = Depends(get_role)):
    if role != Role.ADMIN:
        raise HTTPException(status_code=403)
    logger.info(
        "audit: queue cancel %s requested by %s",
        item_id,
        request.headers.get("Tailscale-User-Login", "dev"),
    )
    return HTMLResponse(
        '<div class="alert alert-warning text-sm">cancel sent (not yet implemented)</div>'
    )
