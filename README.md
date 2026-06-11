# enemy-controller

내 프로젝트들을 한 화면에서 모니터링하고, tailnet 안에서는 직접 제어하는 대시보드.

- **공개 화면**: `<your-domain>` 으로 누구나 접근. 인프라/서비스 헬스, 지표를 읽기 전용으로 노출 (자랑 + 상태 확인용).
- **Admin 화면**: tailnet 으로 접속하면 동일 앱이 제어 기능까지 노출 (queue insert/cancel 등).
- 별도 DB 없이 각 백엔드 서비스 API 를 실시간 호출해서 보여준다.
- 새 서비스는 모듈 하나 추가로 탭이 늘어나는 구조 (현재 reflexion-rondo, lck-pics).

## 기술 스택

FastAPI + Jinja2 + HTMX + Tailwind CSS + DaisyUI. 업스트림 호출은 httpx(async). 설정은 pydantic-settings.

## 문서

- [architecture.md](docs/architecture.md) — 구조, 권한 분리, panel/service 레지스트리, 디렉터리 레이아웃
- [spec.md](docs/spec.md) — 업스트림 API contract(제안), panel 정의, view model
- [decisions.md](docs/decisions.md) — 핵심 설계 결정(ADR)
- [setup.md](docs/setup.md) — 로컬 개발 환경
- [runbook.md](docs/runbook.md) — 배포(Docker + host Tailscale), 운영
- [changelog.md](docs/changelog.md)

## 빠른 시작

[setup.md](docs/setup.md) 참조. 실제 도메인/토큰 등 민감 값은 repo 에 두지 않고 `.env` (참고: [.env.example](.env.example)) 에만 둔다.
