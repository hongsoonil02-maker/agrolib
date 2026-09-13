# 100 Bagger Backend 작업 아카이브 — 2026-09-14

- **작업일자**: 2026-07-19 ~ 2026-09-14 (최근 수정 2026-09-14 07:50)
- **대상 폴더 2곳**:
  1. `C:\Users\master\quant_system\100_bagger_backend` (81 files, 레거시/운영 엔진) — `quant_system` 모노레포 일부
  2. `C:\Users\master\Projects\us-stock-100x-backend` (OptB SaaS 백엔드) — GitHub `hongsoonil02-maker/us-stock-100x-backend`
  3. 관련 worktrees: `C:\Users\master\.trae\worktrees\100_bagger_backend`, `quant_system.worktrees/*`
- **GitHub 리포지토리**:
  - `hongsoonil02-maker/us-stock-100x-backend` (public, 2 commits, FastAPI)
  - `hongsoonil02-maker/quant_system` (private, 100+ commits, `quant_system/100_bagger_backend` 포함)
- **옵시디언 볼트**: `C:\Users\master\agrolib` (`.obsidian`, 동일 GitHub `agrolib` Wiki 이중 보관)

---

## 1. 폴더 A — `quant_system\100_bagger_backend` (운영 엔진, 81 files)

- **역할**: 미국/한국/인도/대만/베트남/인도네시아/멕시코 7개 시장 100배거 스캐너 운영 파이프라인
- **파일 수**: 81, **최근 수정**: `quant_engine_v4.py` / `quant_engine_base.py` (2026-09-14 07:50)
- **주요 파일 (최근 LastWriteTime 순)**:
  - `quant_engine_v4.py` (7157B), `quant_engine_base.py` (32014B) — 베이스 Template Method + v4 구현
  - `kis_portfolio_sync.py` (12076B), `rescore_database_100baggers.py` (7498B), `virtual_portfolio.py` (17925B)
  - `fear_greed_index.py` (13360B), `ai_analyzer_kr.py` (16498B), `backfill_roe_5yr.py` (6309B)
  - 전체 파이썬 목록: `ai_analyzer_kr.py`, `alert_notifier.py`, `alpha_extraction.py`, `backfill_kr_sector.py`, `central_error_logger.py`, `check_kr_supabase.py`, `data_integrity_checker.py`, `diagnose_db.py`, `extract_fundamentals.py`, `extract_hidden_champions.py`, `hermes_full_scanner.py`, `hermes_local_orchestrator.py`, `pipeline_watchdog.py`, `quant_engine_base/kr/v4/emerging.py`, `scan_100bagger.py`, `sync_i18n.py`, `test_fdr_markets.py`, `update_kr_names.py` 등
- **로그/상태**: `engine_daily_ai.log` (51KB), `engine_daily_sync.log` (40KB), `engine_weekly_report.log` (11KB), `global_error_log.json` (10KB), `failed_ledger.json` (3KB), `last_success_timestamp.json`

### `quant_engine_base.py` 핵심 (발췌)
```python
# Shared base, Template Method — 서브클래스가 훅 override
MAX_RETRIES=5, MIN_ROE=20.0, MIN_ROIC=15.0, MIN_REVENUE_GROWTH=0.15
import yfinance, supabase, concurrent.futures
# MAX_RETRIES/INITIAL_BACKOFF/BACKOFF_MULTIPLIER로 7시장 수집 안정화
```

### `quant_system` 모노레포 최근 커밋 (100_bagger 관련)
- `496dcf60 fix: prevent stale screener results — checkpoint TTL, always-cleanup, recency gates` (최신)
- `1e7da916 feat: upgrade James scoring engine with authentic 100-bagger multi-factor model and rescore database`
- `7cb7ad97 feat: wire roe_5yr backfill into weekly pipeline with pagination`
- `2660d3f5 feat: upgrade institutional price gates (US: .00-.00, KR: 1000-2000000 KRW)`
- `quant_system` 원격: `origin https://github.com/hongsoonil02-maker/quant_system.git`

---

## 2. 폴더 B — `Projects\us-stock-100x-backend` (OptB 신형 SaaS 엔진)

- **GitHub**: `hongsoonil02-maker/us-stock-100x-backend` (public, 2026-07-19 생성)
- **버전**: `58a53d9` (최신, 2026-07-19), 초기 `957a90f Initial commit: ORCA instructions`
- **스택**: FastAPI + Python 3.11 + httpx/yfinance/alpha-vantage + pandas/polars + SQLAlchemy (Postgres/SQLite)
- **구조**:
```
src/
  main.py                         # FastAPI app, /health, /api/v1/scoring
  api/screener_routes.py
  engine/bagger_scoring_engine.py  # MultiFactorBaggerScoringEngine
ORCA_AGENT_INSTRUCTIONS.md (2541B)
requirements.txt (158B)
.aider.conf.yml (369B)
```
- **README** 핵심:
  > 미국 기업의 시총/매출성장/ROE/FCF/내부자매수/밸류괴리+SEC 공시로 `100배 장주식 발굴 스코어링 로직` 계산. `GET /api/v1/screen`, `GET /api/v1/stock/{ticker}`

### `bagger_scoring_engine.py` 핵심 (OptB Copilot & Hermes, 0-100점)
```python
class MultiFactorBaggerScoringEngine: # CAN SLIM 30 + Rule of 40 25 + Insider 20 + RVOL 25
  weights = {can_slim:0.30, rule_of_40:0.25, insider_buying:0.20, rvol_momentum:0.25}
  def compute_rule_of_40(revenue_growth_pct + fcf_margin_pct): >=60→25, >=40→20, >=25→12
  def compute_can_slim(eps_growth_yoy, sales_growth_qtr, roe): eps>=40→12, sales>=35→10, roe>=25→8 (cap 30)
  def determine_signal(total): >=90 STRONG BUY, >=83 BUY
  # 7개 시장 지원, gateway=http://localhost:20128 (omniroute)
```

### `src/main.py` (발췌)
```python
app = FastAPI(title="US Stock 100-Bagger Backend (OptB)")
app.include_router(router, prefix="/api/v1/scoring")
@app.get("/health") → {"status":"HEALTHY","team":"OptB (Copilot & Hermes)"}
```

- **원격**: `origin https://github.com/hongsoonil02-maker/us-stock-100x-backend.git`

---

## 3. 두 백엔드 비교

| 구분 | `quant_system\100_bagger_backend` | `Projects\us-stock-100x-backend` |
|------|-----------------------------------|----------------------------------|
| 성격 | 운영 파이프라인 (레거시+현행, 7시장, Supabase, yfinance, 수십 개 스크립트) | SaaS API 서버 (신형, FastAPI, 단일 스코어링 엔진, 7시장) |
| 파일 수 | 81 py + 로그/세팅 | 3 py + 설정 |
| 스코어링 | `quant_engine_base` Template Method, MIN_ROE 20 등 하드 게이트 | `MultiFactorBaggerScoringEngine` 4팩터 100점, 가중 평균 |
| 배포 | `quant_system` 모노레포 내 직접 실행 (auto_quant.sh, engine_watcher.sh) | `vite` 없음, `uvicorn src.main:app --reload` |

---

## 4. 보관 정보

- **원본 유지**: 두 폴더 모두 원위치 보존 (`quant_system\100_bagger_backend` 81 files + 로그, `Projects\us-stock-100x-backend` 전체 `src/`)
- **Git 상태**:
  - `quant_system` — `496dcf60` 최신, `origin/main` 추적, `100_bagger_backend`는 모노레포 일부로 별도 원격 없음
  - `us-stock-100x-backend` — `58a53d9` 최신, `origin/main` clean, `git log --oneline -2` 확인
- **본 문서**: 옵시디언 볼트 `agrolib/Wiki/2026-09-14_100_Bagger_Backend_작업_아카이브.md` 및 GitHub `agrolib` Wiki 이중 커밋 (다음 push)
- **연계 문서**: `2026-09-14_SnJ_Animal_Hospital_개선_작업.md`, `2026-09-14_Vet_Animal_Hospital_작업_아카이브.md` 동일 Wiki에 병행 — 세 문서는 VetLink/SnJ/100Bagger 생태계 아카이브 세트

---

*아카이브 생성일 2026-09-14, 파일 트리 및 `git log` 스냅샷 기준. 추가 엔진 개선 시 본 문서 갱신 필요.*
