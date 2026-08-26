# 🔧 OKX 자동매매 봇 개선 구현 계획

> 거래내역 분석 보고서 기반 7개 개선사항 차례대로 구현

---

## 개선 #1 — Ghost 프로세스 종료 🔴 긴급

**문제**: `bot_c_okx_swap.py 8003` (레거시 포트)이 CPU 71% 점유 중  
**조치**: 해당 PID `kill` 처리  
**영향**: 즉시 리소스 해방, 기존 8013 포트 봇에 영향 없음

---

## 개선 #2 — 숏 진입 비대칭 임계값 강화 🔴 긴급

**문제**: 숏 PF=0.95 (적자). 현재 숏 임계값 = 롱 +20 (예: 메이저 롱 80, 숏 100)  
**조치**: 숏 비대칭을 **+20 → +30**으로 강화 (예: 메이저 롱 80, 숏 **110**)  
**근거**: 14일간 숏 승률 32.1% vs 롱 74.4%. 숏은 구조적 불리 → 더 강한 신호에서만 진입

#### [MODIFY] [`strategy_common.py`](file:///home/hongsoonil02/quant_system/strategy_common.py)
- L853: `ENTRY_THRESHOLD_SHORT = ENTRY_THRESHOLD_LONG + 20` → `+ 30`

---

## 개선 #3 — 서킷 브레이커 강화 🔴 긴급

**문제**: Max DD 58.9%. 현재 서킷 브레이커 -6%에서 발동하지만, DD가 여전히 과대  
**조치**: 서킷 브레이커 임계값 **-6% → -4%**로 조기 발동 + 회복 기준도 비례 조정

#### [MODIFY] [`.env`](file:///home/hongsoonil02/quant_system/.env)
- `OKX_CIRCUIT_BREAKER_ROE=-6` → `-4`

---

## 개선 #4 — 스윕(강제청산) 조건 완화 🟡 개선

**문제**: 전체 거래의 21.8%(724건)가 스윕 청산 → 전략적 청산이 아닌 시간초과 기계적 청산
**조치**: 스윕 판정 기준을 **24h/5% → 36h/3%**로 변경  
- 보유 시간 임계값: 24h → **36h** (수익 거래 평균 보유가 28h이므로 여유 확보)
- 정체 판정 변동률: 5% → **3%** (더 작은 변동만 정체로 간주)

#### [MODIFY] [`master_bot_orchestrator.py`](file:///home/hongsoonil02/quant_system/master_bot_orchestrator.py)
- L595: `86400000` (24h) → `129600000` (36h)
- L598: `0.05` → `0.03`

---

## 개선 #5 — 손실 심볼 블랙리스트 추가 🟡 개선

**문제**: GPS(-64.7%), SNXX(-38.3%), POL(-21.6%) 반복 손실  
**조치**: Venture 전략의 BLACKLIST에 `GPS`, `SNXX`, `POL` 추가

#### [MODIFY] [`okx_venture_strategy.py`](file:///home/hongsoonil02/quant_system/okx_venture_strategy.py)
- L23: BLACKLIST에 `'GPS', 'SNXX', 'POL'` 추가

---

## 개선 #6 — Chop Filter 배포 바닥 상향 🟡 개선

**문제**: W34 거래 급감(1,208→48건). `CHOP_FLOOR=0.15`에서 사이즈가 너무 작아 최소 마진($100) 미달 → 사실상 차단  
**조치**: `CHOP_FLOOR` **0.15 → 0.25** (저변동 장에서도 최소 25% 사이즈 보장)

#### [MODIFY] [`.env`](file:///home/hongsoonil02/quant_system/.env)
- `OKX_CHOP_FLOOR=0.15` → `0.25`

---

## 개선 #7 — DCA 최대 횟수 축소 🟡 개선

**문제**: DCA 609건이 수익성에 기여하는지 불확실. 기존 4회 물타기는 역추세 시 손실 누적  
**조치**: DCA 최대 **4회 → 3회**로 축소 (한 단계 더 보수적으로)

#### [MODIFY] [`.env`](file:///home/hongsoonil02/quant_system/.env)
- `OKX_MAX_DCA_ENTRIES=4` → `3`

---

## 검증 계획

### 자동 검증
- 변경 후 각 봇 프로세스 `systemctl --user restart` 수행
- 로그에서 새 파라미터 적용 확인 (`grep` 검증)

### 수동 모니터링
- 변경 후 24h 동안 거래 활동 추이 관찰
- 특히 W35 거래 건수가 W33/W34 사이(적절한 수준)로 회복되는지 확인

> [!WARNING]
> 모든 변경은 **실시간 운영 중인 프로덕션 봇**에 적용됩니다. 서비스 재시작이 필요합니다.
