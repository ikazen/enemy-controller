from enum import StrEnum

from fastapi import Request

from .config import settings


class Role(StrEnum):
    PUBLIC = "public"
    ADMIN = "admin"


def get_role(request: Request) -> Role:
    # prod 에서는 DEV_FORCE_ADMIN 무시
    if settings.app_env == "dev" and settings.dev_force_admin:
        return Role.ADMIN
    # Tailscale-User-Login 헤더 존재 여부만으로 판정 (값 비교 안 함)
    # X-Forwarded-* 는 스푸핑 가능하므로 절대 사용하지 않는다 (ADR-001)
    if request.headers.get("Tailscale-User-Login"):
        return Role.ADMIN
    return Role.PUBLIC
