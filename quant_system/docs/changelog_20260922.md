# OKX 자동매매 시스템 변경 이력
## 2026-09-22 (v2.4.0 - Critical Bug Fix & JEV Supreme)

### 변경 사항

#### 1. JEV Supreme 아키텍처 적용
- `strategy_common.py`: JEV AI가 1번 판단권자로 설정
- BTC EMA50/200 매크로 필터, ADX chop 게이트 100% 해제 (JEV 활성 시)
- `vol_cond = True` 강제 (JEV가 실시간 호가 수급으로 판단)
- `.env`: `JEV_CONFIDENCE_THRESHOLD` 0.65 → 0.55, `JEV_TIMEOUT_MS` 1500ms

#### 2. Breakeven Stop 레버리지 곱수 버그 수정 (P0)
- **문제**: `pnl_pct_long`에 레버리지(20x)가 곱해진 ROE를 Breakeven 임계값(0.005)과 비교
  - 20x 레버리지에서 가격 0.025% 하락에도 Breakeven Stop 발동
  - 09-20 BNB -0.4% 하락 → ROE -8% → 즉시 "본전 보호" 청산 (실제로는 큰 손실)
- **수정**: `spot_pnl_pct` (레버리지 제외 가격 비율) 분리, Breakeven은 `spot_pnl_pct <= -0.005`로 비교
  - 롱/숏 양쪽 동일 적용

#### 3. ATR Stop 배수 확대
- `ATR_STOP_K`: 2.5 → 3.5
- BTC 30분봉 ATR 기준 스탑 거리: ~1.3% → ~1.8%
- 1시간 내 정상 변동에 걸리는 노이즈 손절 방지

#### 4. Health Circuit Breaker 리셋
- `tripped = false`, `cooldown_until = 0`
- `health_last_trip_ts = NOW` (이전 손실 거래 평가 대상 제외)

#### 5. 파일 정리
- `__pycache__/` 삭제, stale PID 삭제
- 로그 파일 최근 2000줄로 트리밍
- 일회성 테스트 스크립트 → `_archive/` 이동

### 수정 파일
- `strategy_common.py` (핵심 전략 로직)
- `.env` (JEV 파라미터)
- `state/circuit_breaker_*.json` (CB 상태)
