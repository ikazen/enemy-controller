# Setup — 로컬 개발

## 요구사항

- Python 3.12+ (uv 권장)
- Node (Tailwind/DaisyUI 빌드용) 또는 Tailwind standalone CLI

## 의존성

```bash
uv sync           # 또는 uv venv && uv pip install -e .
```

런타임: `fastapi`, `uvicorn[standard]`, `httpx`, `jinja2`, `pydantic-settings`.
개발: `pytest`, `pytest-asyncio`, `ruff`, `respx`(httpx mock).

## 환경변수

`.env.example` 복사 후 채운다. 실제 도메인/토큰은 repo 에 절대 커밋하지 않는다.

```bash
cp .env.example .env
```

주요 키: 백엔드 base URL 들, per-service 토큰(있으면), `OWNER_LOGIN`(감사 표시용), 캐시 TTL.

## CSS 빌드 (Tailwind + DaisyUI)

```bash
# 개발: watch
npx tailwindcss -i app/static/src.css -o app/static/app.css --watch
```

`tailwind.config.js` 에 DaisyUI 플러그인 등록, content 에 `app/templates/**/*.html` 포함. 디자인 토큰/테마는 추후 확정.

## 실행

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- 기본은 **public** role 로 보인다 (`Tailscale-User-Login` 헤더 없음).
- admin 화면을 로컬에서 보려면 헤더를 흉내낸다 (개발 한정):

```bash
curl -H "Tailscale-User-Login: dev@local" http://127.0.0.1:8000/
```

또는 `DEV_FORCE_ADMIN=true` 같은 **개발 전용** 플래그를 두되, prod 빌드에서는 반드시 비활성. (security.py 에서 prod 일 때 무시)

## 테스트

```bash
pytest
```

- 업스트림은 `respx` 로 mock. 실제 백엔드 호출 금지.
- role 분기(public/admin), 업스트림 실패 시 panel degraded 렌더를 우선 커버.
