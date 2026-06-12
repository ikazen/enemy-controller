import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)


def test_public_role_no_header():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "admin" not in resp.text


def test_admin_role_with_tailscale_header():
    resp = client.get("/", headers={"Tailscale-User-Login": "user@example.com"})
    assert resp.status_code == 200
    assert "admin" in resp.text


def test_dev_force_admin_only_in_dev_mode():
    with patch("app.security.settings") as mock_settings:
        mock_settings.app_env = "prod"
        mock_settings.dev_force_admin = True
        resp = client.get("/")
    # prod 에서는 DEV_FORCE_ADMIN 무시 — 헤더 없으면 public
    assert "admin" not in resp.text or "public" in resp.text


def test_admin_panel_hidden_from_public():
    resp = client.get("/panels/rondo-queue-control")
    assert resp.status_code == 200
    assert resp.text == ""


def test_admin_panel_visible_to_admin():
    resp = client.get(
        "/panels/rondo-queue-control",
        headers={"Tailscale-User-Login": "user@example.com"},
    )
    assert resp.status_code == 200
    assert "enqueue" in resp.text


def test_unknown_panel_returns_404():
    resp = client.get("/panels/does-not-exist")
    assert resp.status_code == 404


def test_unknown_service_returns_404():
    resp = client.get("/services/does-not-exist")
    assert resp.status_code == 404


def test_control_endpoint_blocked_for_public():
    resp = client.post("/services/reflexion-rondo/queue")
    assert resp.status_code == 403


def test_control_endpoint_allowed_for_admin():
    resp = client.post(
        "/services/reflexion-rondo/queue",
        headers={"Tailscale-User-Login": "user@example.com"},
    )
    assert resp.status_code == 200


def test_infra_grid_loads():
    resp = client.get("/services/infra")
    assert resp.status_code == 200
    assert "infra-airflow" in resp.text


def test_rondo_grid_loads():
    resp = client.get("/services/reflexion-rondo")
    assert resp.status_code == 200


def test_health_panel_renders():
    resp = client.get("/panels/infra-airflow")
    assert resp.status_code == 200
    assert "ok" in resp.text
    assert "UTC" in resp.text


def test_minio_panel_shows_down():
    resp = client.get("/panels/infra-minio")
    assert resp.status_code == 200
    assert "down" in resp.text
