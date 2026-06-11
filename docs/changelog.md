# Changelog

## Unreleased

- 초기 설계 문서 작성: architecture, spec(업스트림 contract 제안), decisions(ADR-001~006), setup, runbook.
- 스택 확정: FastAPI + Jinja2 + HTMX + Tailwind + DaisyUI, httpx, pydantic-settings.
- 권한 분리 모델 확정: 공개=리버스 프록시 / admin=`tailscale serve` 헤더, tailnet 접속이면 admin.
