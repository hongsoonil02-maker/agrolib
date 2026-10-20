# 2026-10-20 GCP Coinbot Server (`136.111.207.137`) — 5대 자동매매 봇 카메론 풀백 아키텍처 통합, 백테스트 검증 및 서버 대청소 보고서

## 1. 작업 요약 (Executive Summary)
- **작업 일시**: 2026-10-20 (KST)
- **대상 서버**: GCP `coinbot` (`hongsoonil02@136.111.207.137`, `/home/hongsoonil02/quant_system`)
- **핵심 달성 사항**:
  1. **KIS 한국주식 30분봉 봇 (`kis_cameron_pullback_30m.py`)**: 10/20 실전 10건 매매 복기(`-₩131,423`) 후 4대 방어·수익보존 패치 적용 및 백테스트 검증(`-₩131,423 → +₩18,452`, `PF 0.25 → 2.41`).
  2. **KIS 미국주식 30분봉 봇 (`kis_cameron_pullback_us_30m.py`) & Alpaca 미국주식 30M/1H 봇 (`alpaca_cameron_pullback_30m.py`, `alpaca_cameron_pullback_trader.py`)**:
     - 개장 시 중복 매도를 유발하는 `kis_liquidate_at_open.service` 비활성화 및 메인 봇 내 `09:30:05 EDT` 오버나이트 자동 청산(`AIBZ`, `EVAX`) 일원화.
     - 2X/3X 레버리지·인버스 ETF(`APLX`, `AXTX`, `AXTU` 등 `BATS`/`ARCA` 상장 ETP) 2중 필터링 차단.
     - `TARGET_RR` 미정의 `NameError` 수정, 실체결가 기준 SL/TP 재계산, 캔들 종가 돌파 유지 + 실시간 체결가 검증 게이트, 동적 본절(`+1.8% → +0.3%~+0.4%`) 및 트레일링 스탑(`+2.5% → -1.0%`) 이식.
     - 30일 Alpaca SIP 분봉 백테스트 결과: 승률 `37.9% → 61.1%`, 손익비 `1.15 → 2.10`, 순수익 `+$620.94 → +$1,168.73` (`+88.2%` 증가).
  3. **공통 AI 필터 (`jev/universal_jev_gate.py`)**:
     - `aiohttp.ClientSession` 이벤트 루프 재사용으로 인해 발생하던 `RuntimeError: Event loop is closed` 및 SSL 소켓 파일 디스크립터 누수(`Errno 9`)를 호출별 컨텍스트 매니저 방식으로 근본 해결.
  4. **OKX 코인 선물 봇 전면 교체 (`okx_johnbread_grid_swing.py` 폐기 → `okx_cameron_pullback_trader.py` 옵션 B 이식)**:
     - 어제(10/19) 하루 94회 이벤트·수수료 누수 및 `-$234.35` 손실을 유발한 존빵 4H 역추세 그리드의 5대 결함(손절 직후 0.002초 재진입 루프, 급등 코인 숏/폭락 코인 롱 역추세 물타기, 40x 본절 수수료 손실 등) 규명 및 폐기.
     - **옵션 B (카메론 1시간봉 양방향 LONG+SHORT 알트코인 풀백 + 4대 방어·트레일링 패치)** 이식 완료 (45일 백테스트: 351회 거래, **승률 `63.0%`, PF `2.00`, MDD `-3.05%`, 순수익 `+$1,112.71` / `+67.44%`**).
  5. **서버 대청소 (Ghost / Zombie / Old / Cache 정리)**:
     - 백업 파일(`*.bak_*`), 구버전 봇 스크립트 및 테스트/백테스트 스크립트 90여 개, 구버전 `systemd` 유닛 30여 개, 유령 타이머(`okx_tori_executor.timer`), `state/bt_cache`, `__pycache__`, `/tmp` 임시 파일 전량 삭제.

---

## 2. 현재 가동 중인 5대 프로덕션 자동매매 봇 (`systemd --user`)

| # | 서비스명 (`systemd --user`) | 실행 스크립트 | 대상 시장 / 타임프레임 | 핵심 리스크 & 익절/손절 파라미터 |
|---|---|---|---|---|
| 1 | `kis_cameron_30m.service` | `kis_cameron_pullback_30m.py` | KIS 국내주식 (30분봉) | `09:30~14:30 KST` 진입, `15:15` EOD 청산, `1:1.8 R:R`, `+1.8%` 도달 시 `+0.6%` 본절 & `-0.8%` 트레일링 |
| 2 | `kis_cameron_30m_trader.service` | `kis_cameron_pullback_us_30m.py` | KIS 미국주식 실전 (30분봉) | `10:00~14:30 EST` 진입, `15:50` EOD 청산, `1:2.0 R:R`, `+1.8%` 본절(`+0.4%`), `+2.5%` 트레일링(`-1.0%`) |
| 3 | `alpaca_cameron_30m_trader.service` | `alpaca_cameron_pullback_30m.py` | Alpaca 미국주식 (30분봉) | 계좌 50% 배분, `1:2.0 R:R` 브래킷 + 15초 주기 본절(`+1.8%→+0.3%`) & 트레일링(`+2.5%→-1.0%`) |
| 4 | `alpaca_cameron_trader.service` | `alpaca_cameron_pullback_trader.py` | Alpaca 미국주식 (1시간봉) | 계좌 50% 배분, `1:2.2 R:R` 브래킷 + 15초 주기 본절(`+1.8%→+0.3%`) & 트레일링(`+2.5%→-1.0%`) |
| 5 | `okx_cameron_trader.service` | `okx_cameron_pullback_trader.py` | OKX 선물 (1시간봉 양방향) | 16개 고베타 알트 + 동적 급등락 스캐너, `5x Cross`, `1:2.2 R:R`, `+1.8%` 본절(`+0.4%`), `+2.5%` 트레일링(`-1.0%`) |

---

## 3. 정돈된 서버 디렉토리 구조 (`/home/hongsoonil02/quant_system`)
```text
/home/hongsoonil02/quant_system/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── kis_cameron_pullback_30m.py          # [1] KIS 한국주식 30M
├── kis_cameron_pullback_us_30m.py       # [2] KIS 미국주식 30M
├── alpaca_cameron_pullback_30m.py       # [3] Alpaca 미국주식 30M
├── alpaca_cameron_pullback_trader.py    # [4] Alpaca 미국주식 1H
├── okx_cameron_pullback_trader.py       # [5] OKX 코인선물 1H (양방향 Option B)
├── jev/
│   └── universal_jev_gate.py            # 5대 봇 공통 AI Gatekeeper (세션 누수 패치 완료)
├── remote_deploy/
│   └── kis_token.json                   # KIS OAuth 공유 토큰 캐시
├── state/
│   ├── kis_cameron_30m_positions.json
│   ├── kis_cameron_us_30m_state.json
│   ├── alpaca_cameron_30m_state.json
│   ├── alpaca_cameron_1h_state.json
│   └── okx_cameron_1h_state.json
└── logs/
    ├── kis_cameron_30m.log
    └── kis_cameron_us_30m.log
```
