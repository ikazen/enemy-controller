# Architecture

## 목표와 제약

- 접속자 하루 10명 이하. 성능보다 **단순함 + 외부 공격 방어 + 확장 용이성**.
- 별도 DB 없음. 모든 데이터는 백엔드 서비스 API 를 실시간 호출.
- 서비스는 계속 늘어난다 → "모듈 하나 추가 = 탭 하나 추가" 가 되어야 한다.

## 권한 분리 (보안의 핵심)

공개 서비스인데 tailnet 접속이면 admin 이다. 이 분리는 **요청 헤더 존재 여부**로만 결정한다.

```
공개  : Internet → DNS <your-domain> → 리버스 프록시(TLS) → 127.0.0.1:<port> (컨테이너)
admin : tailnet device → host `tailscale serve` → 127.0.0.1:<port> (컨테이너)
```

- `tailscale serve` 는 프록시한 요청에 `Tailscale-User-Login` 헤더를 주입한다.
- 공개 리버스 프록시는 들어오는 `Tailscale-*` 헤더를 **전부 제거**한다.
- 앱은 loopback/컨테이너 내부에만 바인드. 공개 인터넷에 직접 노출되지 않는다.

→ 따라서 `Tailscale-User-Login` 헤더가 있으면 admin, 없으면 public.
(tailnet 접속 = 모두 admin 정책이므로 헤더 *값* 은 비교하지 않고, 표시/감사 로그용으로만 보관한다.)

### 절대 불변식 (깨지면 권한 우회 가능)

1. 앱은 절대 `0.0.0.0` 공개 바인드 금지 — 공개 인입은 오직 리버스 프록시 경유.
2. 공개 리버스 프록시는 inbound `Tailscale-*` 헤더를 strip 해야 한다.
3. role 은 서버에서만 도출. UI 의 버튼 숨김은 장식일 뿐, **모든 변경(mutating) 엔드포인트는 role 의존성으로 재검증**.
4. role 판정에 `X-Forwarded-For` / `X-Real-IP` 사용 금지 (스푸핑 가능).

자세한 위협 모델은 [decisions.md](decisions.md) ADR-001 참조.

## 데이터 흐름

```
브라우저 ─HTMX poll─▶ /panels/{id} ─▶ panel.fetch(role)
                                          └─▶ cache(TTL) ─miss─▶ httpx → 백엔드 API (tailnet 내부)
                                          ▼
                                       partial 렌더 → HTML fragment 반환
```

- 백엔드는 모두 tailnet 내부에 있고, 컨테이너가 tailnet 으로 호출한다 (runbook 의 네트워킹 참조).
- 업스트림 호출에는 timeout 을 건다. 실패 시 panel 은 "unavailable" 상태로 렌더 — 한 서비스가 죽어도 대시보드는 산다.
- TTL 캐시로 여러 패널/사용자의 폴링이 백엔드를 두드리지 않게 한다 (TTL 5~15s).

## panel / service 레지스트리 (확장 지점)

두 개념만 안다:

- **Panel** = HTML fragment 하나를 만드는 단위. frozen dataclass + fetch 콜러블.
- **ServiceModule** = 탭 하나 + 그 탭의 panel 들 + admin 제어 라우트. Protocol.

```python
@dataclass(frozen=True, slots=True)
class Panel:
    id: str
    title: str
    fetch: Callable[[Role], Awaitable[Any]]  # 데이터 (캐시/업스트림 경유)
    template: str                            # partial 경로
    refresh_seconds: int = 10
    public: bool = True                      # False면 admin 전용

class ServiceModule(Protocol):
    key: str          # "reflexion-rondo"
    title: str
    def panels(self) -> list[Panel]: ...
    def router(self) -> APIRouter: ...       # admin-gated 제어 엔드포인트
```

- 새 서비스 추가 = `app/services/<name>.py` 작성 후 `services/__init__.py:SERVICES` 에 등록. 끝.
- 메인 대시보드 = `infra` 모듈의 헬스 panel 들. 각 서비스 탭 = 해당 모듈의 panel grid.
- 제어 라우트는 admin role 의존성으로 보호하고, 모든 호출을 감사 로그에 남긴다.

panel 데이터 contract 와 reflexion-rondo 의 구체 panel 은 [spec.md](spec.md).

## 디렉터리 레이아웃

```
app/
  main.py            # FastAPI 앱, 라우터/정적파일 마운트
  config.py          # pydantic-settings: 백엔드 URL, 토큰, owner login, 캐시 TTL
  security.py        # Role 도출 의존성 (Tailscale 헤더 → public/admin)
  http_client.py     # 공유 httpx.AsyncClient + timeout
  cache.py           # async TTL 캐시
  panels.py          # Panel dataclass, 레지스트리, 렌더 헬퍼
  services/
    __init__.py      # SERVICES: list[ServiceModule]
    infra.py         # airflow/grafana/minio/reflexion 데몬 헬스 panel
    reflexion_rondo.py
    lck_pics.py
  web/routes.py      # /, /services/{key}, /panels/{id}, 제어 라우트
  templates/         # base.html, index.html, partials/
  static/            # 빌드된 tailwind+daisyui css
tests/
```

## 렌더링 (HTMX)

- `/` : shell + 탭 네비 + panel placeholder grid.
- placeholder: `<div hx-get="/panels/{id}" hx-trigger="load, every {n}s" hx-swap="innerHTML">`.
- `/services/{key}` : 해당 서비스 panel grid (탭 전환도 HTMX).
- admin 액션 버튼: `hx-post="/services/{key}/..."` → 서버에서 role 재검증.
- 디자인(panel 비주얼/그리드)은 추후 확정 — DaisyUI `card` 를 panel 단위로 쓰는 정도만 가정.
