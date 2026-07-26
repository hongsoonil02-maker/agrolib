# 🌐 Enterprise Projects Overview (Projects_Overview.md)

> 본 문서는 안그래 군단이 관리하고 개발/운용하는 전사 12개 프로젝트의 사양, 역할 및 연결 링크 모음입니다. (Vault: Agrolib)

---

## 📈 1. Quant Trading & Automation Systems

### 🤖 Bot A: KIS Korea Stock Trading Bot
- **파일명/경로**: `bot_a_kr_stock.py` (`c:\Users\master\quant_system\bot_a_kr_stock.py`)
- **대상 시장**: 한국주식 (코스피/코스닥) via KIS (한국투자증권 API)
- **주요 기능**: 모닝 스캐너, 장중 실시간 신호 매매, 수수료/슬리피지 엔진 연동

### 🤖 Bot B: NASDAQ US Stock Trading Bot
- **파일명/경로**: `bot_b_nasdaq.py` (`c:\Users\master\quant_system\bot_b_nasdaq.py`)
- **대상 시장**: 미국주식 (나스닥 주요 종목 NVDA, TSLA, AAPL, QQQ 등)
- **주요 기능**: Keltner Squeeze, RVOL Sweep, 실시간 미국 시세 파이프라인

### 🤖 Bot C: OKX Crypto Swap Trading Bot
- **파일명/경로**: `bot_c_okx_swap.py` (`c:\Users\master\quant_system\bot_c_okx_swap.py`)
- **대상 시장**: OKX 크립토 무기한 선물 (Perpetual Swap)
- **주요 기능**: 레버리지 매매, Kelly Sizing 자금 관리, 실시간 리스크 헤징

### 🤖 Bot D: Upbit Crypto Spot Trading Bot
- **파일명/경로**: `bot_d_upbit.py` (`c:\Users\master\quant_system\bot_d_upbit.py`)
- **대상 시장**: Upbit 원화(KRW) 마켓 크립토 현물
- **주요 기능**: 변동성 돌파, 이동평균 모멘텀, 자동 잔고 밸런싱

### ⚙️ Quant Central Core Engine (`quant_system`)
- **경로**: `c:\Users\master\quant_system\`
- **주요 기능**: 몬테카를로 검증, Kelly Engine, 백테스트 엔진(`backtest_final.py`), Alpha Sniper Orchestrator

---

## 💻 2. SaaS & Platform Solutions

### 🌐 100-Bagger SaaS Frontend (`100_bagger_saas`)
- **경로**: `c:\Users\master\quant_system\100_bagger_saas\` (및 `c:\Users\master\100_bagger_saas\`)
- **스택**: Next.js / React / TypeScript / Tailwind CSS
- **주요 기능**: 100-Bagger 사용자 대시보드, 퀀트 분석 차트, 구독 및 포트폴리오 관리 UI

### ⚙️ 100-Bagger SaaS Backend (`100_bagger_backend`)
- **경로**: `c:\Users\master\quant_system\100_bagger_backend\` (및 `c:\Users\master\100_bagger_backend\`)
- **스택**: Python / FastAPI / PostgreSQL / Redis
- **주요 기능**: 퀀트 시그널 API, 사용자 인증, 데이터베이스 조회 및 알림 서비스

---

## 🌿 3. Bio & Veterinary Product Landings

### 📄 Rotagal Landing Page (`rotagal-landing`)
- **경로**: `c:\Users\master\rotagal-landing\`
- **설명**: 로타갈(Rotagal) 송아지 설사 예방/치료제 공식 브랜딩 & Landing Page

### 📄 Vetacol Landing Page (`vetacol-landing`)
- **경로**: `c:\Users\master\vetacol-landing\`
- **설명**: 베타콜(Vetacol) 동물용 항균/치료제 브랜딩 & Landing Page

### 📄 Monsmecta Landing Page (`monsmecta-landing`)
- **경로**: `c:\Users\master\monsmecta-landing\`
- **설명**: 몬스멕타(Monsmecta) 소화기 치료제 공식 랜딩페이지

### 📄 Parvogel Landing Page (`parvogel_landing`)
- **경로**: `c:\Users\master\parvogel_landing\`
- **설명**: 파보겔(Parvogel) 파보바이러스 백신/치료제 공식 랜딩페이지

---

## 🚜 4. Smart Livestock System

### 🐄 Smart Livestock Redesign (`smart_livestock_redesign`)
- **경로**: `c:\Users\master\smart_livestock_redesign\`
- **설명**: 스마트 축산 관리 솔루션 모듈 및 UI/UX 리디자인 프로젝트
