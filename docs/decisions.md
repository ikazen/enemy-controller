# Decisions (ADR)

living document. 과거 결정은 언제든 뒤집을 수 있다.

## ADR-001 — 권한 분리는 Tailscale 헤더 존재 여부로

**결정**: 공개=리버스 프록시 경유, admin=`tailscale serve` 경유. `tailscale serve` 가 주입하는 `Tailscale-User-Login` 헤더가 있으면 admin.

**대안**: (a) OAuth/세션 로그인 — 자랑용 공개 서비스에 과함. (b) admin 전용 별도 앱 — panel 코드 중복. (c) 소스 IP 기반 — Docker+host Tailscale 에서 컨테이너가 보는 IP 가 호스트/브리지라 신뢰 불가.

**불변식**: 앱은 loopback 만 바인드 / 공개 프록시는 inbound `Tailscale-*` strip / role 은 서버 도출, mutating 엔드포인트마다 재검증 / `X-Forwarded-*` 로 role 판정 금지.

**위협 모델**: 외부에서 admin 스푸핑 → 헤더 strip + loopback 바인드로 차단. SSRF → 업스트림 타깃은 정적 config 에서만, 사용자 입력 아님. 시크릿 유출 → 공개 panel 에 시크릿/내부 식별자 노출 금지, 값은 `.env` 에만. DoS → 명시적 범위 밖이나 timeout/요청 크기 제한/보안 헤더는 건다.

## ADR-002 — 자체 DB 없음, 실시간 pull + TTL 캐시

**결정**: 모니터링 데이터는 백엔드 API 를 실시간 호출. 저장 안 함. 폭주 방지로 업스트림 응답을 TTL(5~15s) 캐시.

**이유**: 데이터 소유권은 각 백엔드에 있다. controller 는 뷰일 뿐. DB 운영/마이그레이션/일관성 부담 제거. 접속자 10명/일이라 캐시면 충분.

**트레이드오프**: 히스토리/추세 그래프는 불가 (백엔드가 제공하면 표시만). 필요해지면 그때 재고.

## ADR-003 — panel + ServiceModule 레지스트리로 확장

**결정**: panel = frozen dataclass + fetch 콜러블. service = ServiceModule Protocol. 새 서비스 = 모듈 파일 + 레지스트리 등록.

**이유**: "서비스 계속 추가" 가 1순위 요구. 추상화는 2회(reflexion-rondo, lck-pics) 반복 확인됨 → Protocol 도입 정당. (YAGNI 통과)

## ADR-004 — SSR + HTMX (SPA 아님)

**결정**: 서버에서 HTML fragment 렌더, HTMX 폴링으로 갱신. JS 프레임워크 없음.

**이유**: 패널 = 주기 갱신되는 작은 HTML 조각. SPA 빌드/상태관리 오버헤드 불필요. FastAPI 한 프로세스로 끝.

## ADR-005 — 공개는 읽기 전용, 제어는 admin + 서버 게이트

**결정**: public role 은 mutating 엔드포인트에 도달 불가. 제어 버튼은 admin 일 때만 렌더하되, 엔드포인트 자체가 role 의존성으로 재검증하고 감사 로그를 남긴다.

**이유**: 버튼 숨김은 UX, 보안 아님. 권한 검사는 서버 단일 지점.

## ADR-006 — Docker(loopback) + host Tailscale + 기존 리버스 프록시

**결정**: 컨테이너는 `127.0.0.1:<port>` 에만 published. 공개는 호스트의 기존 리버스 프록시(`<your-domain>`, airflow/grafana 와 동일 패턴)가 프록시. admin 은 host `tailscale serve`.

**이유**: 도메인/프록시/TLS 인프라가 이미 있다. 컨테이너에 tailscale sidecar 넣는 것보다 단순. 컨테이너→tailnet 백엔드 호출 경로는 runbook 에서 처리.
