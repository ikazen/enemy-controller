# Spec — 업스트림 contract & panel 정의

백엔드 API 는 아직 미설계다. 여기 적힌 contract 는 controller 가 **소비하고 싶은 모양의 제안**이다. 실제 백엔드를 만들 때 이 모양에 맞추거나, 맞추기 어려우면 connector 에서 변환한다.

## 공통 원칙

- 모든 백엔드는 tailnet 내부에 노출. controller 가 내부 호출.
- 자체 서비스는 표준 헬스 엔드포인트를 노출한다:
  - `GET /health` → `{ "status": "ok"|"degraded"|"down", "version": str, "checks": [{"name": str, "status": str}] }`
- 제3자 서비스는 native 엔드포인트를 그대로 쓰고 connector 가 `HealthStatus` 로 정규화한다:
  - Airflow `GET /health`, Grafana `GET /api/health`, MinIO `GET /minio/health/live`.
- 인증이 필요하면 per-service 토큰을 `.env` 에서 읽어 헤더로 붙인다. (tailnet 내부라 대부분 토큰 없이 가능)

## controller view model (frozen dataclass)

```python
class HealthState(StrEnum):
    OK = "ok"; DEGRADED = "degraded"; DOWN = "down"; UNKNOWN = "unknown"

@dataclass(frozen=True, slots=True)
class HealthStatus:
    name: str
    state: HealthState
    latency_ms: float | None
    detail: str | None
    checked_at: datetime

@dataclass(frozen=True, slots=True)
class Metric:
    label: str
    value: str           # 포맷된 값 (단위 포함)
    hint: str | None = None
```

- 업스트림 호출 실패/timeout → `HealthState.UNKNOWN` 또는 `DOWN`, panel 은 degraded UI.

## 메인 대시보드 (infra 모듈)

panel 들 (모두 public):

| panel id | 내용 | 소스 |
|---|---|---|
| `infra-airflow` | Airflow 스케줄러/DAG 상태 | Airflow `/health` |
| `infra-grafana` | Grafana up | Grafana `/api/health` |
| `infra-minio` | MinIO live/ready | MinIO health |
| `infra-reflexion-daemon` | reflexion 데몬 상태 | 자체 `/health` |
| `infra-summary` | 위 헬스 롤업 + 보여주고 싶은 커스텀 지표 | 집계 |

## reflexion-rondo (제안 contract)

읽기 (public):

- `GET /api/competitions` → `[{ "id": str, "name": str, "best_score": float, "submissions": int, "last_submission_at": datetime }]`
- `GET /api/competitions/{id}/cycles` → `{ "training_runs": int, "cycle": int, "metrics": [{label, value}] }`
- `GET /api/queue` → `{ "running": int, "pending": int, "items": [{ "id": str, "competition_id": str, "status": str, "enqueued_at": datetime }] }`

제어 (admin 전용, controller 의 `/services/reflexion-rondo/...` → 백엔드로 프록시):

- `POST /api/queue` body `{ "competition_id": str, "params": {...} }` → `201 { "id": str }`
- `POST /api/queue/{id}/cancel` → `200`

panel:

| panel id | 내용 | public |
|---|---|---|
| `rondo-best-scores` | 대회별 베스트 스코어 테이블 | yes |
| `rondo-cycles` | 학습 횟수 / cycle 지표 | yes |
| `rondo-submissions` | 최근 제출 날짜 | yes |
| `rondo-queue` | 큐 상태 (running/pending) | yes |
| `rondo-queue-control` | insert / cancel 버튼 | **admin only** |

## lck-pics

contract 미정. infra 헬스 panel 만 우선 두고, 지표/제어는 서비스가 구체화되면 추가.

## 새 서비스 추가 체크리스트

1. 백엔드에 `GET /health` (+ 필요한 읽기/제어 엔드포인트) 노출.
2. `app/services/<name>.py` 에 `ServiceModule` 구현 — panels() + (제어 있으면) router().
3. `.env` 에 `<NAME>_BASE_URL` (+ 필요시 토큰) 추가, `config.py` 반영.
4. `services/__init__.py:SERVICES` 에 등록.
