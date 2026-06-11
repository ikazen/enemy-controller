# Runbook — 배포 & 운영

## 토폴로지

```
                      ┌─────────────────────────── host ───────────────────────────┐
Internet ─TLS─▶ 리버스 프록시 ─▶ 127.0.0.1:<port> ◀─ tailscale serve ◀─ tailnet device
 (<your-domain>)  (Tailscale-* strip)      │                  (Tailscale-User-Login 주입)
                                    enemy-controller 컨테이너
                                            │ httpx (tailnet 내부)
                                            ▼
                              reflexion-rondo / lck-pics / airflow / grafana / minio
```

## 배포 (Docker + host Tailscale)

1. 컨테이너는 호스트 **loopback 에만** published: `ports: ["127.0.0.1:<port>:8000"]`. 절대 `0.0.0.0` 금지.
2. 공개: 기존 리버스 프록시(airflow/grafana 와 동일)가 `<your-domain>` → `127.0.0.1:<port>` 프록시. **inbound `Tailscale-*` 헤더 strip 설정 필수** (ADR-001 불변식).
   - Caddy 예: `header_down -Tailscale-*` 가 아니라 inbound 제거 → `request_header -Tailscale-User-Login` 등으로 들어오는 값 삭제.
3. admin: 호스트에서 `tailscale serve https / http://127.0.0.1:<port>`. tailnet 접속 시 identity 헤더 주입됨.

## 컨테이너 → tailnet 백엔드 호출

컨테이너가 tailnet 백엔드(`*.ts.net`, tailnet CGNAT 대역)에 닿아야 한다. 택 1:

- `network_mode: host` — 가장 단순. 호스트 tailscale 라우팅 그대로 사용.
- 또는 컨테이너에 tailnet CGNAT 대역 라우트를 호스트 경유로 추가.

MagicDNS 이름을 쓰려면 컨테이너 resolver 가 tailscale DNS 를 봐야 한다 — 안 되면 `.env` 에 tailnet IP 직접 기입.

## 배포 위치 확인

```bash
docker inspect <container> | grep -i sha   # 이미지 태그(git SHA) → 떠있는 커밋 확인
```

## 운영 체크

- 헬스: `GET /healthz` (controller 자체 헬스, 업스트림 무관하게 200).
- 한 백엔드가 죽으면 해당 panel 만 degraded, 나머지 정상이어야 한다 (timeout 동작 확인).
- 로그: admin 제어 호출(queue insert/cancel)은 `Tailscale-User-Login` 값과 함께 감사 로그.

## 보안 운영 점검 (주기적)

- [ ] 컨테이너가 공개 IP 에 직접 바인드돼 있지 않다 (`ss -tlnp` 로 loopback 확인).
- [ ] 공개 프록시가 `Tailscale-*` 를 strip 한다 (`curl -H "Tailscale-User-Login: x" https://<your-domain>/` → 여전히 public).
- [ ] prod 에서 `DEV_FORCE_ADMIN` 류 개발 플래그 비활성.
- [ ] `/docs`, `/redoc` 는 prod 에서 비활성 또는 admin 전용.
- [ ] 공개 panel 응답에 내부 식별자(도메인/IP/tailnet/경로) 노출 없음.
