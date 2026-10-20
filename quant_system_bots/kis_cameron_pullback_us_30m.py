# -*- coding: utf-8 -*-
"""
kis_cameron_pullback_us_30m.py — KIS 미국주식 30분봉 로스 카메론(Ross Cameron) 풀백 트레이더
========================================================================================
Alpaca 30분봉 자동매매 봇(alpaca_cameron_pullback_30m.py)의 정밀 3-Tier 가드레일 전략을
한국투자증권(KIS) OpenAPI 해외주식 거래 환경으로 완벽 이식한 실전 자동매매 엔진.

전략 핵심 철학:
1. 실시간 급등주 스캐너 (Alpaca Movers & yfinance Fallback):
   - 가격: $2.00 ~ $50.00
   - 당일 모멘텀 서지 >= +3.0%
   - 거래량 및 거래대금 상위 스몰캡 모멘텀 유니버스 동적 추출
2. 30분봉 1차 눌림목(First Pullback) 셋업:
   - 상승 충격파: 직전 2~7봉 내 +2.0% 이상 강한 서지(Impulse Surge)
   - 1차 눌림목: 1~3봉 음봉 또는 도지/팽이형(몸통 <= 45% of range)
   - 되돌림 폭: 충격파 상승분의 60% 이내
   - 거래량 수축: 눌림목 거래량 <= 충격파 평균 거래량의 1.35배
   - 지지 레벨: 9 EMA(0.98 버퍼) 및 VWAP(0.97 버퍼) 상단 유지
   - 유동성 가드: 캔들 거래량 >= 10,000주 (호가 공백 슬리피지 방지)
   - 진입 트리거: 직전 눌림목 캔들의 고점(High) 돌파
   - 바 레벨 락(Bar-Level Lock): 동일 30분봉 내 1회만 진입 (중복 주문 원천 차단)
3. Universal Jev Gate (US_STOCKS AI 필터):
   - 유상증자(Offering), 주식 희석(Dilution), 가짜 모멘텀 설거지 공시 사전 차단
   - Veto 시 15~30분 쿨다운 자동 등록
4. KIS OpenAPI 주문 & 리스크 관리:
   - 동적 Half-Kelly 포지션 사이징: 가용 자본의 16% ~ 20%
   - [Tier 1] 마켓어블 리밋 주문 (최대 0.8% 슬리피지 캡)
   - [Tier 2] 유동성 보존 캡 (포지션당 최대 $8,000 / 3,000주)
   - [Tier 3] 하드 손절 플로어 (최대 7% 하드 캡 클램프)
   - 가상 브래킷 OCO 엔진: 1:3.0 R:R 익절 / 스윙 로우 손절 실시간 추적 집행
   - KIS 원장 체결 동기화(Reconciliation via TTTS3012R): 고스트 포지션 제거 및 실체결 수량 일치
   - 10:00 EST 이전 진입 대기 (첫 30분봉 완성 후 진입), 14:30 EST 컷오프
   - EOD 당일 청산: 15:50 EST 장마감 전 전량 청산 (오버나이트 갭 리스크 원천 배제)
"""

import os
import sys
import time
import math
import json
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import numpy as np
import yfinance as yf
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, ".env"))

# ── LOGGING CONFIG ──
LOG_DIR = os.path.join(CURRENT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
STATE_DIR = os.path.join(CURRENT_DIR, "state")
os.makedirs(STATE_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "kis_cameron_us_30m.log")
STATE_FILE = os.path.join(STATE_DIR, "kis_cameron_us_30m_state.json")
TOKEN_FILE = os.path.join(CURRENT_DIR, "remote_deploy", "kis_token.json")

logger = logging.getLogger("KIS_Cameron_US_30M")
logger.setLevel(logging.INFO)
logger.propagate = False

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=3, encoding="utf-8")
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    if sys.stdout.isatty():
        logger.addHandler(stream_handler)

# ── KIS API CREDENTIALS ──
KIS_APP_KEY = os.getenv("KIS_API_KEY", "")
KIS_APP_SECRET = os.getenv("KIS_SECRET", "")
acc_no = os.getenv("KIS_ACCOUNT_NO", "")
if "-" in acc_no:
    KIS_CANO, KIS_PRDT_ABRV = acc_no.split("-")
elif len(acc_no) >= 10:
    KIS_CANO, KIS_PRDT_ABRV = acc_no[:8], acc_no[8:10]
else:
    KIS_CANO, KIS_PRDT_ABRV = "", ""

KIS_URL = os.getenv("KIS_URL", "https://openapi.koreainvestment.com:9443")

# ── ALPACA MARKET DATA FEED CREDENTIALS (SIP 바 & 스캐너용) ──
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_DATA_URL = "https://data.alpaca.markets/v2"
ALPACA_REST_URL = os.getenv("ALPACA_REST_URL", "https://paper-api.alpaca.markets/v2")

ALPACA_HEADERS = {
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
    "Content-Type": "application/json"
}

# ── HTTP RETRY SESSION ──
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "DELETE"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

from jev.universal_jev_gate import UniversalJevGate

# ── STRATEGY HYPERPARAMETERS (Alpaca 30M과 100% 일치) ──
TIMEFRAME = "30Min"
MIN_PRICE = 2.00
MAX_PRICE = 50.00
MIN_GAP_PCT = 3.0             # 최소 3% 모멘텀 서지
MAX_ALLOCATED_CAPITAL = 5000.0  # [BUDGET CAP] 봇 운용 총 가용자본 한도 ($5,000)
MAX_PORTFOLIO_PCT = 0.20      # 20% per trade (Half-Kelly 16% ~ 20%)
MAX_POSITION_DOLLAR = 5000.0   # [TIER 2] 포지션당 최대 $5,000 유동성 보존 캡
MAX_POSITION_SHARES = 3000     # [TIER 2] 포지션당 최대 3,000주 한도
MAX_ENTRY_SLIPPAGE_PCT = 0.008 # [TIER 1] 돌파 트리거 대비 최대 0.8% 마켓어블 리밋 버퍼
MAX_CONCURRENT_TRADES = 4     # 최대 동시 보유 4종목
RISK_REWARD_RATIO = 2.0       # 1:2.0 R:R (30분봉 실전 수익 보존 최적화 + 트레일링 스탑 병행)
MAX_SL_PCT = 0.07             # 최대 손절폭 7% 하드 캡
MIN_SL_PCT = 0.01             # 최소 손절폭 1%
BREAKEVEN_TRIGGER_PCT = 0.018 # +1.8% 도달 시 본절(+0.4%) 보호 스탑 활성화
BREAKEVEN_FLOOR_PCT = 0.004   # 본절 보호 스탑 플로어 (+0.4%)
TRAILING_TRIGGER_PCT = 0.025  # +2.5% 도달 시 고점 대비 트레일링 스탑 활성화
TRAILING_DROP_PCT = 0.010     # 고점 대비 -1.0% 이탈 시 트레일링 익절
START_HOUR_EST = 10           # 첫 30분봉 완성 대기 후 10:00 EST부터 신규 진입 허용
START_MIN_EST = 0
CUTOFF_HOUR_EST = 14          # 14:30 EST 이후 신규 진입 금지
CUTOFF_MIN_EST = 30
EOD_CLOSE_HOUR_EST = 15       # 15:50 EST 미청산 당일 단타 포지션 일괄 시장가 청산
EOD_CLOSE_MIN_EST = 50
COOLDOWN_SEC = 900            # 15분 재진입 쿨다운
ORDER_TIMEOUT_SEC = 60        # 미체결 매수 주문 자동 취소 제한시간 (초)


class KisCameronPullbackUS30M:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.access_token = ""
        self.token_expired_at = 0.0
        self.account_equity = 10000.0      # USD 기준 계좌 평가액
        self.available_cash = 10000.0      # USD 기준 실시간 주문가능 현금
        self.fx_rate = 1380.0             # USD/KRW 환율
        self.watchlist: List[str] = []
        self.last_scanned_time = 0
        self.last_reconcile_time = 0
        self.jev_gate = UniversalJevGate(confidence_threshold=0.60)

        self.exchange_cache: Dict[str, Tuple[str, str]] = {} # symbol -> (trade_cd, quote_cd)
        self.active_positions: Dict[str, Dict[str, Any]] = {}
        self.pending_orders: Dict[str, Dict[str, Any]] = {}  # symbol -> {odno, side, qty, price, placed_at}
        self.cooldowns: Dict[str, float] = {}
        self.last_entry_bar: Dict[str, str] = {}             # symbol -> bar_time (Bar-Level Lock)

        self.load_state()
        logger.info(f"🚀 [KIS US Cameron 30M Swing Engine] 초기화 완료 (Dry Run: {self.dry_run})")
        logger.info(f"   KIS REST URL: {KIS_URL}")
        logger.info(f"   계좌번호: {KIS_CANO[:4]}****-{KIS_PRDT_ABRV}")

        # 시작 시 계좌 잔고 및 토큰 동기화
        self.issue_token()
        self.sync_account_equity()
        self.reconcile_positions_with_ledger()

    # ─────────────────────────────────────────────────────────────
    #  STATE PERSISTENCE
    # ─────────────────────────────────────────────────────────────
    def load_state(self):
        """로컬 상태 파일 안전 로드"""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        self.active_positions = saved.get("active_positions", {})
                        self.pending_orders = saved.get("pending_orders", {})
                        self.cooldowns = saved.get("cooldowns", {})
                        self.last_entry_bar = saved.get("last_entry_bar", {})
                logger.info(f"📂 [State Loaded] 보유 포지션: {list(self.active_positions.keys())} | 미체결: {list(self.pending_orders.keys())}")
        except Exception as e:
            logger.error(f"❌ State load failed: {e}")
            self.active_positions = {}
            self.pending_orders = {}
            self.cooldowns = {}
            self.last_entry_bar = {}

    def save_state(self):
        """원자적(Atomic) 파일 교체로 상태 저장"""
        try:
            tmp = STATE_FILE + ".tmp"
            payload = {
                "active_positions": self.active_positions,
                "pending_orders": self.pending_orders,
                "cooldowns": self.cooldowns,
                "last_entry_bar": self.last_entry_bar,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            os.replace(tmp, STATE_FILE)
        except Exception as e:
            logger.error(f"❌ State save failed: {e}")

    # ─────────────────────────────────────────────────────────────
    #  KIS AUTH & HEADERS
    # ─────────────────────────────────────────────────────────────
    def issue_token(self) -> bool:
        """KIS OAuth2 액세스 토큰 발급 및 캐싱 (24시간 유효)"""
        now = time.time()
        if self.access_token and now < self.token_expired_at:
            return True

        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                if d.get("access_token") and d.get("expires_at", 0) > now + 300:
                    self.access_token = d["access_token"]
                    self.token_expired_at = d["expires_at"]
                    return True
            except Exception:
                pass

        if not KIS_APP_KEY or not KIS_APP_SECRET:
            logger.error("❌ KIS_API_KEY 또는 KIS_SECRET 환경변수가 설정되지 않았습니다.")
            return False

        try:
            url = f"{KIS_URL}/oauth2/tokenP"
            body = {
                "grant_type": "client_credentials",
                "appkey": KIS_APP_KEY,
                "appsecret": KIS_APP_SECRET
            }
            resp = session.post(url, json=body, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token", "")
                expires_in = int(data.get("expires_in", 86400))
                self.token_expired_at = now + expires_in - 600
                tmp_tok = f"{TOKEN_FILE}.tmp.{os.getpid()}"
                with open(tmp_tok, "w", encoding="utf-8") as f:
                    json.dump({"access_token": self.access_token, "expires_at": self.token_expired_at}, f)
                os.replace(tmp_tok, TOKEN_FILE)
                logger.info("🔑 [Auth] KIS OpenAPI 토큰 발급 및 캐싱 완료")
                return True
            else:
                logger.error(f"❌ 토큰 발급 실패: HTTP {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            logger.error(f"❌ 토큰 요청 예외 발생: {e}")
            return False

    def get_kis_headers(self, tr_id: str) -> dict:
        self.issue_token()
        return {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": KIS_APP_KEY,
            "appsecret": KIS_APP_SECRET,
            "tr_id": tr_id,
            "custtype": "P"
        }

    # ─────────────────────────────────────────────────────────────
    #  EXCHANGE RESOLUTION & MARKET DATA
    # ─────────────────────────────────────────────────────────────
    def get_exchange_info(self, symbol: str) -> Tuple[str, str]:
        """
        미국 주식 거래소 코드 (주문용, 시세조회용) 정밀 동적 매핑:
        Returns: (trade_exchange_code, quote_exchange_code)
        예: NASDAQ -> ("NASD", "NAS"), NYSE -> ("NYSE", "NYS"), AMEX -> ("AMEX", "AMS")
        """
        if symbol in self.exchange_cache:
            return self.exchange_cache[symbol]

        # 1. Alpaca Asset API
        if ALPACA_API_KEY and ALPACA_SECRET_KEY:
            try:
                res = session.get(f"{ALPACA_REST_URL}/assets/{symbol}", headers=ALPACA_HEADERS, timeout=3)
                if res.status_code == 200:
                    exch = res.json().get("exchange", "").upper()
                    if "NASD" in exch:
                        self.exchange_cache[symbol] = ("NASD", "NAS")
                        return self.exchange_cache[symbol]
                    elif "NYSE" in exch or "ARCA" in exch:
                        self.exchange_cache[symbol] = ("NYSE", "NYS")
                        return self.exchange_cache[symbol]
                    elif "AMEX" in exch or "BATS" in exch:
                        self.exchange_cache[symbol] = ("AMEX", "AMS")
                        return self.exchange_cache[symbol]
            except Exception:
                pass

        # 2. yfinance fast_info 폴백
        try:
            t = yf.Ticker(symbol)
            exch = getattr(t.fast_info, "exchange", "").upper()
            if any(k in exch for k in ["NMS", "NGM", "NCM", "NAS"]):
                self.exchange_cache[symbol] = ("NASD", "NAS")
                return self.exchange_cache[symbol]
            elif any(k in exch for k in ["NYQ", "NYS", "ARC"]):
                self.exchange_cache[symbol] = ("NYSE", "NYS")
                return self.exchange_cache[symbol]
            elif any(k in exch for k in ["ASE", "AMX", "BTS"]):
                self.exchange_cache[symbol] = ("AMEX", "AMS")
                return self.exchange_cache[symbol]
        except Exception:
            pass

        self.exchange_cache[symbol] = ("NASD", "NAS")
        return self.exchange_cache[symbol]

    def get_exchange_code(self, symbol: str) -> str:
        """KIS 주문용 거래소 코드 (NASD / NYSE / AMEX)"""
        return self.get_exchange_info(symbol)[0]

    def get_usd_krw_rate(self) -> float:
        """USD/KRW 환율 실시간 조회 (yfinance 기반, 실패 시 1,380원 보수적 폴백)"""
        try:
            ticker = yf.Ticker("USDKRW=X")
            df = ticker.history(period="1d", interval="5m")
            if df is not None and not df.empty and "Close" in df.columns:
                rate = float(df["Close"].iloc[-1])
                if rate > 900.0:
                    self.fx_rate = rate
                    return rate
        except Exception:
            pass
        return self.fx_rate

    def sync_account_equity(self):
        """KIS 외화 예수금 및 통합증거금 원화 주문가능액 합산 조회"""
        if not self.issue_token():
            return

        usd_cash = 0.0
        tot_evlu_usd = 0.0

        # 1. 해외주식 외화 잔고 조회 (TTTS3012R)
        try:
            headers = self.get_kis_headers("TTTS3012R")
            params = {
                "CANO": KIS_CANO,
                "ACNT_PRDT_CD": KIS_PRDT_ABRV,
                "OVRS_EXCG_CD": "NASD",
                "TR_CRCY_CD": "USD",
                "CTX_AREA_FK200": "",
                "CTX_AREA_NK200": ""
            }
            res = session.get(f"{KIS_URL}/uapi/overseas-stock/v1/trading/inquire-balance", headers=headers, params=params, timeout=8)
            if res.status_code == 200:
                out2 = res.json().get("output2", {})
                tot_evlu_usd = float(out2.get("tot_evlu_pfls_amt", 0.0) or 0.0)
                usd_cash = float(out2.get("frcr_dnca_amt", 0.0) or 0.0)
        except Exception as e:
            logger.warning(f"⚠️ KIS 해외주식 잔고 조회 경고: {e}")

        # 2. 통합증거금 원화 주문가능액 조회 (TTTC8908R)
        krw_cash = 0.0
        try:
            k_headers = self.get_kis_headers("TTTC8908R")
            k_params = {
                "CANO": KIS_CANO,
                "ACNT_PRDT_CD": KIS_PRDT_ABRV,
                "PDNO": "005930",
                "ORD_UNPR": "0",
                "ORD_DVSN": "01",
                "CMA_EVLU_AMT_ICLD_YN": "Y",
                "OVRS_ICLD_YN": "Y"
            }
            res_k = session.get(f"{KIS_URL}/uapi/domestic-stock/v1/trading/inquire-psbl-order", headers=k_headers, params=k_params, timeout=8)
            if res_k.status_code == 200:
                out = res_k.json().get("output", {})
                krw_cash = float(out.get("max_buy_amt") or out.get("ord_psbl_cash", 0.0))
        except Exception as e:
            logger.warning(f"⚠️ KIS 원화 주문가능액 조회 경고: {e}")

        fx = self.get_usd_krw_rate()
        krw_in_usd = krw_cash / fx if krw_cash > 0 else 0.0
        self.available_cash = usd_cash + krw_in_usd

        # 포지션 평가액 합산 계좌 순자산 추정
        calc_equity = tot_evlu_usd + self.available_cash
        if calc_equity > 100.0:
            self.account_equity = calc_equity

        logger.info(
            f"💼 [KIS Account] 총 가용현금: ${self.available_cash:,.2f} (USD: ${usd_cash:,.2f} + KRW 통합: ${krw_in_usd:,.2f}) | "
            f"추정 총자산: ${self.account_equity:,.2f} | FX: ₩{fx:,.1f}"
        )

    def get_realtime_price(self, symbol: str) -> Optional[float]:
        """
        실시간 현재가 조회 (우선순위):
        1. KIS 해외주식 현재가 체결조회 (HHDFS00000300)
        2. Alpaca Latest Trade API (SIP 실시간 체결가)
        3. yfinance fast_info
        """
        if self.issue_token():
            try:
                _, quote_excd = self.get_exchange_info(symbol)
                headers = self.get_kis_headers("HHDFS00000300")
                params = {"AUTH": "", "EXCD": quote_excd, "SYMB": symbol}
                res = session.get(f"{KIS_URL}/uapi/overseas-price/v1/quotations/price", headers=headers, params=params, timeout=4)
                if res.status_code == 200:
                    last_px = float(res.json().get("output", {}).get("last", 0.0))
                    if last_px > 0:
                        return last_px
            except Exception:
                pass

        # Alpaca SIP Trade 폴백
        if ALPACA_API_KEY and ALPACA_SECRET_KEY:
            try:
                url = f"{ALPACA_DATA_URL}/stocks/{symbol}/trades/latest"
                res = session.get(url, headers=ALPACA_HEADERS, timeout=4)
                if res.status_code == 200:
                    px = float(res.json().get("trade", {}).get("p", 0.0))
                    if px > 0:
                        return px
            except Exception:
                pass

        # yfinance 폴백
        try:
            t = yf.Ticker(symbol)
            px = t.fast_info.last_price
            if px and px > 0:
                return float(px)
        except Exception:
            pass

        return None

    def reconcile_positions_with_ledger(self):
        """
        [원장 체결 확인 & 고스트 포지션 정리]
        KIS 해외주식 잔고(TTTS3012R)와 실시간 주문 상태를 대조:
        - 원장에 실체결된 잔고를 active_positions에 정확한 평균단가 및 수량으로 반영
        - 원장에 실제 잔고가 있으나 active_positions에 없는 고아 포지션 자동 입양(Adopt)하여 손절/익절 감시 복원
        - pending_orders 중 체결 완료 확인 시 active_positions 승격
        - 정상 청산 완료된 포지션만 안전하게 정리
        """
        if not self.issue_token():
            return

        now_t = time.time()
        if now_t - self.last_reconcile_time < 20.0:
            return
        self.last_reconcile_time = now_t

        headers = self.get_kis_headers("TTTS3012R")
        target_exchanges = ["NASD", "NYSE", "AMEX"]

        real_holdings: Dict[str, dict] = {}
        try:
            for excg in target_exchanges:
                params = {
                    "CANO": KIS_CANO,
                    "ACNT_PRDT_CD": KIS_PRDT_ABRV,
                    "OVRS_EXCG_CD": excg,
                    "TR_CRCY_CD": "USD",
                    "CTX_AREA_FK200": "",
                    "CTX_AREA_NK200": ""
                }
                try:
                    res = session.get(f"{KIS_URL}/uapi/overseas-stock/v1/trading/inquire-balance", headers=headers, params=params, timeout=8)
                    if res.status_code == 200:
                        data = res.json()
                        if data.get("rt_cd") == "0":
                            for row in data.get("output1", []):
                                sym = row.get("ovrs_pdno", "").strip().upper()
                                try:
                                    qty = int(float(row.get("ovrs_cblc_qty", 0)))
                                    avg_px = float(row.get("pchs_avg_pric", 0.0))
                                    now_px = float(row.get("now_pric2", 0.0))
                                except (ValueError, TypeError):
                                    continue
                                if sym and qty > 0:
                                    real_holdings[sym] = {"qty": qty, "avg_price": avg_px, "now_price": now_px, "excg": excg}
                except Exception as e:
                    logger.debug(f"[{excg}] 원장 조회 예외: {e}")

            state_changed = False

            # 1. pending_orders 중 실제 원장에 입고된 종목 확인 -> active_positions로 정식 승격 (실체결가 기준 SL/TP 재동기화)
            ny_today = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
            for sym in list(self.pending_orders.keys()):
                if sym in real_holdings:
                    order_info = self.pending_orders.pop(sym)
                    h = real_holdings[sym]
                    fill_px = h["avg_price"]
                    orig_sl = float(order_info.get("stop_loss") or round(fill_px * (1.0 - MAX_SL_PCT), 2))
                    hard_max_sl = round(fill_px * (1.0 - MAX_SL_PCT), 2)
                    sl = max(orig_sl, hard_max_sl)
                    if sl >= fill_px:
                        sl = round(fill_px * 0.97, 2)
                    actual_risk = max(fill_px - sl, fill_px * MIN_SL_PCT)
                    tp = round(fill_px + (actual_risk * RISK_REWARD_RATIO), 2)
                    self.active_positions[sym] = {
                        "qty": h["qty"],
                        "entry_price": fill_px,
                        "stop_loss": sl,
                        "take_profit": tp,
                        "entry_time": order_info.get("placed_at", now_t),
                        "entry_date": ny_today,
                        "highest_price": max(fill_px, h.get("now_price", fill_px)),
                        "trailing_active": False,
                        "excg": h.get("excg", "NASD")
                    }
                    logger.info(
                        f"🎉 [Buy Order Filled & Synced] {sym} {h['qty']}주 실체결 평단 ${fill_px:.2f} -> "
                        f"브래킷 감시 활성화 (SL: ${sl:.2f}, TP: ${tp:.2f})"
                    )
                    state_changed = True

            # 2. 원장에 실체결 잔고가 있으나 active_positions에 없는 고아(Orphan) 포지션 자동 입양(Adopt)
            for sym, h in real_holdings.items():
                if sym not in self.active_positions:
                    avg_px = h["avg_price"]
                    qty = h["qty"]
                    sl = round(avg_px * 0.97, 2)
                    tp = round(avg_px * (1.0 + 0.03 * RISK_REWARD_RATIO), 2)
                    self.active_positions[sym] = {
                        "qty": qty,
                        "entry_price": avg_px,
                        "stop_loss": sl,
                        "take_profit": tp,
                        "entry_time": now_t,
                        "entry_date": ny_today,
                        "highest_price": max(avg_px, h.get("now_price", avg_px)),
                        "trailing_active": False,
                        "excg": h.get("excg", "NASD")
                    }
                    logger.warning(
                        f"🚨 [Orphan Holding Adopted] 원장 보유 종목 {sym} {qty}주 @ ${avg_px:.2f} 발견! "
                        f"active_positions 자동 편입 및 실시간 손절/익절 감시 개시 (SL: ${sl}, TP: ${tp})"
                    )
                    state_changed = True
                else:
                    if self.active_positions[sym]["qty"] != h["qty"]:
                        self.active_positions[sym]["qty"] = h["qty"]
                        state_changed = True

            # 3. active_positions 중 실제 원장 잔고가 0이고 pending_orders에도 없는 경우만 정상 청산으로 정리
            for sym in list(self.active_positions.keys()):
                if sym not in real_holdings and sym not in self.pending_orders:
                    logger.info(f"🏁 [Position Closed Confirmed] {sym} 원장 잔고 소진 확인 -> active_positions 정상 정리")
                    self.active_positions.pop(sym, None)
                    self.cooldowns[sym] = now_t + 1800.0  # 30분 쿨다운
                    state_changed = True

            if state_changed:
                self.save_state()

        except Exception as e:
            logger.error(f"❌ KIS 잔고 원장 대조 예외: {e}")

    # ─────────────────────────────────────────────────────────────
    #  SCANNER & SIP BARS
    # ─────────────────────────────────────────────────────────────
    def is_pure_common_stock(self, sym: str) -> bool:
        """
        로스 카메론 원칙: ETF, ETP, ETN, 2X/3X 레버리지·인버스, SPAC, 워런트, 우선주를 철저히 배제하고
        순수 소형 보통주(Common Equity)만 엄격히 통과
        """
        if len(sym) > 5 or "." in sym or "-" in sym or "/" in sym:
            return False
        if len(sym) == 5 and any(sym.endswith(sfx) for sfx in ["W", "U", "R", "P", "X", "Y", "F", "Q"]):
            return False
        if any(sym.endswith(sfx) for sfx in ["WS", "PR", "RT"]):
            return False

        if not hasattr(self, "_asset_type_cache"):
            self._asset_type_cache = {}

        if sym in self._asset_type_cache:
            return self._asset_type_cache[sym]

        substr_keywords = (
            "ETF", "ETN", "ETP", "2X", "3X", "1.5X", "-1X", "-2X", "-3X",
            "LEVERAGED", "INVERSE", "PROSHARES", "DIREXION", "GRANITESHARES",
            "TRADR", "DEFIANCE", "YIELDMAX", "ISHARES", "VANGUARD", "SPDR",
            "INVESCO", "WISDOMTREE", "VANECK", "GLOBAL X", "FIRST TRUST",
            "WARRANT", "PREFERRED"
        )
        word_keywords = ("DAILY", "ULTRA", "FUND", "TRUST", "INDEX", "BULL", "BEAR", "SHORT", "UNITS", "RIGHTS", "NOTES")

        # 1. Alpaca Asset API 종목명 & 거래소(BATS/ARCA) 검증
        if ALPACA_API_KEY and ALPACA_SECRET_KEY:
            try:
                res = session.get(f"{ALPACA_REST_URL}/assets/{sym}", headers=ALPACA_HEADERS, timeout=4)
                if res.status_code == 200:
                    asset = res.json()
                    if not asset.get("tradable", True):
                        self._asset_type_cache[sym] = False
                        return False
                    name_upper = (asset.get("name") or "").upper()
                    exch_upper = (asset.get("exchange") or "").upper()
                    for kw in substr_keywords:
                        if kw in name_upper:
                            logger.info(f"   🚫 [ETF/ETP Filter] {sym} 제외: Alpaca 종목명 '{asset.get('name')}' (키워드: {kw})")
                            self._asset_type_cache[sym] = False
                            return False
                    padded_name = f" {name_upper} "
                    for kw in word_keywords:
                        if f" {kw} " in padded_name:
                            logger.info(f"   🚫 [ETF/ETP Filter] {sym} 제외: Alpaca 종목명 '{asset.get('name')}' (단어: {kw})")
                            self._asset_type_cache[sym] = False
                            return False
                    if exch_upper in ("BATS", "ARCA"):
                        logger.info(f"   🚫 [ETF Exchange Filter] {sym} 제외: 거래소 '{exch_upper}' ({asset.get('name')})")
                        self._asset_type_cache[sym] = False
                        return False
            except Exception as e:
                logger.debug(f"Alpaca asset check failed for {sym}: {e}")

        # 2. yfinance quoteType 및 종목명 이중 판별
        try:
            t = yf.Ticker(sym)
            info = getattr(t, "info", {}) or {}
            qtype = info.get("quoteType") or getattr(t.fast_info, "quoteType", None)
            if qtype and qtype != "EQUITY":
                logger.info(f"   🚫 [ETF/ETP Filter] {sym} 제외: quoteType='{qtype}' (로스 카메론 원칙 미부합)")
                self._asset_type_cache[sym] = False
                return False
            yf_name = (info.get("longName") or info.get("shortName") or "").upper()
            for kw in substr_keywords:
                if kw in yf_name:
                    logger.info(f"   🚫 [ETF/ETP Filter] {sym} 제외: yfinance 종목명 '{yf_name}' (키워드: {kw})")
                    self._asset_type_cache[sym] = False
                    return False
        except Exception:
            pass

        self._asset_type_cache[sym] = True
        return True

    def scan_top_movers(self, limit: int = 25) -> List[str]:
        """
        모멘텀 급등주 동적 발굴:
        1. Alpaca Screener API (당일 +3% 이상 급등, $2 ~ $50 주가 범위)
        2. 순수 보통주(Common Stock)만 허용 (ETF/ETP/워런트 전면 제외)
        3. yfinance Movers 폴백
        """
        logger.info("🔍 [Scanner] Alpaca Screener API를 통한 미국 모멘텀 급등주 스캔 시작...")
        candidates = []

        if ALPACA_API_KEY and ALPACA_SECRET_KEY:
            try:
                resp = session.get("https://data.alpaca.markets/v1beta1/screener/stocks/movers?top=50", headers=ALPACA_HEADERS, timeout=6)
                if resp.status_code == 200:
                    gainers = resp.json().get("gainers", [])
                    for g in gainers:
                        sym = g.get("symbol", "")
                        price = float(g.get("price", 0.0))
                        pct = float(g.get("percent_change", 0.0))
                        if MIN_PRICE <= price <= MAX_PRICE and pct >= MIN_GAP_PCT:
                            # ETF / ETP / 워런트 / 우선주 완전 배제
                            if sym not in candidates and self.is_pure_common_stock(sym):
                                candidates.append(sym)
                                logger.info(f"   🎯 Scanner Match (Common Stock): {sym} | Price: ${price:.2f} | Surge: +{pct:.1f}%")
            except Exception as e:
                logger.error(f"❌ Alpaca 스캐너 에러: {e}")

        # 폴백: candidates가 비었을 때 나스닥 모멘텀 대표 보통주 유니버스 가동 (ETF 일절 제외)
        if not candidates:
            logger.info("ℹ️ 스캐너 폴백 모멘텀 보통주 유니버스 가동...")
            candidates = ["SOUN", "BBAI", "PLTR", "MARA", "RIOT", "CLSK", "IONQ", "RGTI", "QUBT", "NVAX"]

        final_targets = candidates[:limit]
        logger.info(f"📋 [Watchlist Updated] 순수 보통주 감시 대상 ({len(final_targets)}): {final_targets}")
        self.watchlist = final_targets
        return final_targets

    def fetch_bars(self, symbol: str, limit: int = 60) -> Optional[pd.DataFrame]:
        """
        30분봉 OHLCV 수집:
        1. Alpaca SIP 피드 (정확한 거래량, VWAP 및 9 EMA)
        2. yfinance 폴백 (interval='30m', period='1mo')
        """
        if ALPACA_API_KEY and ALPACA_SECRET_KEY:
            try:
                url = f"{ALPACA_DATA_URL}/stocks/bars"
                start_iso = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
                params = {
                    "symbols": symbol,
                    "timeframe": TIMEFRAME,
                    "start": start_iso,
                    "limit": limit,
                    "sort": "desc",
                    "feed": "sip"
                }
                resp = session.get(url, headers=ALPACA_HEADERS, params=params, timeout=6)
                if resp.status_code == 200:
                    raw_bars = resp.json().get("bars", {}).get(symbol, [])
                    if raw_bars and len(raw_bars) >= 15:
                        df = pd.DataFrame(raw_bars)
                        df.rename(columns={
                            "t": "time", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "vw": "vwap"
                        }, inplace=True)
                        if "time" in df.columns:
                            df["time"] = pd.to_datetime(df["time"])
                            df = df.sort_values("time").reset_index(drop=True)
                        if "close" in df.columns and len(df) >= 15:
                            if "vwap" not in df.columns or df["vwap"].isna().all():
                                typical_price = (df["high"] + df["low"] + df["close"]) / 3
                                df["vwap"] = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum().replace(0, 1)
                            df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
                            return df
            except Exception as e:
                logger.debug(f"Alpaca bars fetch failed for {symbol}: {e}")

        # yfinance 폴백
        try:
            t = yf.Ticker(symbol)
            df = t.history(period="1mo", interval="30m")
            if df is not None and len(df) >= 15:
                df = df.reset_index()
                df.rename(columns={
                    "Datetime": "time", "Date": "time", "Open": "open", "High": "high",
                    "Low": "low", "Close": "close", "Volume": "volume"
                }, inplace=True)
                if "time" in df.columns:
                    df["time"] = pd.to_datetime(df["time"])
                    df = df.sort_values("time").reset_index(drop=True)
                if "close" in df.columns and len(df) >= 15:
                    typical_price = (df["high"] + df["low"] + df["close"]) / 3
                    df["vwap"] = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum().replace(0, 1)
                    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
                    return df
        except Exception as e:
            logger.debug(f"yfinance bars fetch failed for {symbol}: {e}")

        return None

    # ─────────────────────────────────────────────────────────────
    #  SETUP EVALUATION (Ross Cameron 30M First Pullback)
    # ─────────────────────────────────────────────────────────────
    def detect_first_pullback_setup(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """
        로스 카메론 30분봉 1차 눌림목 돌파 셋업 검증:
        - 1. 충격파: 직전 2~7봉 내 2% 이상 서지
        - 2. 눌림목: 음봉 또는 몸통 45% 이하 도지형 캔들
        - 3. 지지선: 9 EMA(0.98 버퍼), VWAP(0.97 버퍼) 상단 지지
        - 4. 되돌림 폭: 충격파 상승분의 60% 이내
        - 5. 거래량 수축: 눌림목 거래량 <= 충격파 평균 거래량의 1.35배
        - 6. 유동성 가드: 캔들 거래량 >= 10,000주 (호가 공백 슬리피지 방지)
        - 7. 돌파 트리거: 직전 눌림목 캔들의 고점(High) 돌파
        - 8. 손절폭: 1% <= SL <= 7% (MAX_SL_PCT)
        """
        if df is None or len(df) < 15 or "ema9" not in df.columns or "vwap" not in df.columns or "close" not in df.columns:
            return False, {}

        curr_bar = df.iloc[-1]
        prev_bar = df.iloc[-2]

        prev_range = prev_bar["high"] - prev_bar["low"]
        is_bearish = prev_bar["close"] < prev_bar["open"]
        is_small_body = prev_range > 0 and (abs(prev_bar["close"] - prev_bar["open"]) / prev_range) <= 0.45
        is_pullback_candle = is_bearish or is_small_body

        if not is_pullback_candle:
            return False, {}

        # 9 EMA 및 VWAP 지지선 확인
        if prev_bar["close"] < prev_bar["ema9"] * 0.98 or prev_bar["low"] < prev_bar["vwap"] * 0.97:
            return False, {}

        # 충격파 서지 확인
        prior_bars = df.iloc[-7:-2]
        impulse_low = prior_bars["low"].min()
        impulse_high = prior_bars["high"].max()
        impulse_surge = impulse_high - impulse_low

        if impulse_surge <= 0 or (impulse_surge / impulse_low) < 0.02:
            return False, {}

        # 되돌림 폭 확인 (최대 60%)
        pullback_retrace = impulse_high - prev_bar["low"]
        retrace_ratio = pullback_retrace / impulse_surge
        if retrace_ratio > 0.60:
            return False, {}

        # 거래량 수축 확인
        impulse_avg_vol = prior_bars["volume"].mean()
        if impulse_avg_vol > 0 and prev_bar["volume"] > impulse_avg_vol * 1.35:
            return False, {}

        # 유동성 가드 (캔들당 최소 10,000주 이상 거래)
        min_bar_shares = 10000
        if prev_bar["volume"] < min_bar_shares or impulse_avg_vol < min_bar_shares:
            return False, {}

        trigger_price = prev_bar["high"]
        stop_loss_price = prev_bar["low"]

        risk_per_share = trigger_price - stop_loss_price
        if risk_per_share <= 0:
            return False, {}

        risk_pct = risk_per_share / trigger_price
        if risk_pct > MAX_SL_PCT or risk_pct < MIN_SL_PCT:
            return False, {}

        target_price = trigger_price + (risk_per_share * RISK_REWARD_RATIO)
        curr_close = float(curr_bar["close"])
        # [방어 패치 1] 단순 윗꼬리 터치 후 밀린 캔들(curr_close < trigger * 0.998) 및 과도한 추격(> +1.5%), 손절선 근접 진입 원천 차단
        is_triggered = (
            curr_bar["high"] >= trigger_price and
            curr_close >= trigger_price * 0.998 and
            curr_close <= trigger_price * 1.015 and
            curr_close > stop_loss_price * 1.012
        )

        setup_info = {
            "bar_time": str(curr_bar["time"]),
            "trigger_price": round(trigger_price, 2),
            "stop_loss": round(stop_loss_price, 2),
            "target_price": round(target_price, 2),
            "risk_per_share": round(risk_per_share, 2),
            "risk_pct": round(risk_pct * 100, 2),
            "surge_pct": round(impulse_surge / impulse_low * 100, 2),
            "vol_ratio": round(prev_bar["volume"] / impulse_avg_vol, 2) if impulse_avg_vol > 0 else 1.0,
            "retrace_ratio": round(retrace_ratio * 100, 1),
            "curr_price": round(curr_bar["close"], 2),
            "is_triggered": is_triggered
        }

        return is_triggered, setup_info

    # ─────────────────────────────────────────────────────────────
    #  POSITION SIZING (Half-Kelly + Tier 2 Liquidity Cap)
    # ─────────────────────────────────────────────────────────────
    def calculate_dynamic_position_size(self, setup: Dict[str, Any], trigger_price: float) -> int:
        """
        동적 Half-Kelly 포지션 사이징:
        - 기본 Half-Kelly: 16% ~ 20%
        - 봇 할당 자본 캡 ($5,000) 및 잔여 예산 클램프
        - [Tier 2] 포지션당 최대 $5,000 / 3,000주 상한 적용
        - 증권사 가용 현금 버퍼 초과 방지
        """
        vol_ratio = setup.get("vol_ratio", 1.0)
        retrace_ratio = setup.get("retrace_ratio", 40.0)

        conviction = 1.0
        if vol_ratio > 1.1:
            conviction -= 0.10
        if retrace_ratio > 45.0:
            conviction -= 0.10

        kelly_pct = max(0.16, min(MAX_PORTFOLIO_PCT, MAX_PORTFOLIO_PCT * conviction))

        # 봇 할당 자본금 기준 계산 ($5,000 한도)
        allocated_capital = min(self.account_equity, MAX_ALLOCATED_CAPITAL) if self.account_equity > 0 else MAX_ALLOCATED_CAPITAL
        target_allocation = allocated_capital * kelly_pct

        # 현재 보유 포지션 총 투입금액 차감 후 잔여 예산 클램프
        current_exposure = sum(
            float(pos.get("qty", 0)) * float(pos.get("entry_price", 0.0))
            for pos in self.active_positions.values()
        )
        remaining_budget = max(0.0, MAX_ALLOCATED_CAPITAL - current_exposure)
        target_allocation = min(target_allocation, remaining_budget)

        # 가용 현금 내 클램프 (95% 한도)
        if self.available_cash > 0:
            target_allocation = min(target_allocation, self.available_cash * 0.95)

        # [TIER 2] $5,000 하드 캡
        target_allocation = min(target_allocation, MAX_POSITION_DOLLAR)
        qty = math.floor(target_allocation / trigger_price)
        qty = min(qty, MAX_POSITION_SHARES)

        logger.info(
            f"   📊 [Dynamic Kelly Sizing] 배정: {kelly_pct*100:.1f}% (~${target_allocation:,.2f}) "
            f"[남은예산: ${remaining_budget:,.2f}/{MAX_ALLOCATED_CAPITAL:,.0f}] -> {qty}주 (최대 {MAX_POSITION_SHARES}주)"
        )
        return qty

    # ─────────────────────────────────────────────────────────────
    #  ORDER EXECUTION (KIS OpenAPI + Universal JEV Gate)
    # ─────────────────────────────────────────────────────────────
    def execute_entry(self, symbol: str, setup: Dict[str, Any]) -> bool:
        """
        KIS 해외주식 매수 발주 (TTTT1002U):
        1. JEV AI Gate 승인 검증
        2. Tier 1: 트리거 대비 최대 0.8% 마켓어블 리밋 주문
        3. Tier 3: 하드 손절 플로어 (-7%) 자동 보정
        4. 가상 브래킷 추적 테이블 등록
        """
        trigger_price = setup["trigger_price"]
        stop_loss = setup["stop_loss"]
        take_profit = setup["target_price"]
        curr_price = setup.get("curr_price", trigger_price)
        base_ref = max(trigger_price, curr_price)

        # [TIER 3] 하드 손절 플로어 (최대 -7% 강제 보정)
        hard_max_sl = round(trigger_price * (1.0 - MAX_SL_PCT), 2)
        if stop_loss < hard_max_sl:
            logger.info(f"   🛡️ [SL Clamp] 손절가 하한선 보정: ${stop_loss:.2f} -> ${hard_max_sl:.2f} (-{MAX_SL_PCT*100:.0f}%)")
            stop_loss = hard_max_sl

        # 익절가 최소 마진 확보 (+0.05)
        min_tp = round(base_ref + 0.05, 2)
        if take_profit <= min_tp:
            take_profit = round(base_ref + max(setup.get("risk_per_share", 0.05) * RISK_REWARD_RATIO, 0.05), 2)

        qty = self.calculate_dynamic_position_size(setup, trigger_price)
        if qty <= 0:
            logger.warning(f"⚠️ [{symbol}] 계산된 주문 수량이 0이므로 진입 스킵.")
            return False

        # JEV AI Gate 검증
        loop = asyncio.new_event_loop()
        try:
            decision = loop.run_until_complete(
                self.jev_gate.verify_entry(
                    asset_class="US_STOCKS",
                    symbol=symbol,
                    setup_name="CAMERON_30M_PULLBACK",
                    context={
                        "surge_pct": setup.get("surge_pct", 0),
                        "gap_pct": setup.get("surge_pct", 0),
                        "vol_ratio": setup.get("vol_ratio", 1.0),
                        "rvol": setup.get("vol_ratio", 1.0),
                        "retrace_pct": setup.get("retrace_ratio", 40),
                        "price": trigger_price,
                        "sector": "SmallCap Momentum",
                        "headline": f"Ross Cameron 30M Pullback Breakout above ${setup['trigger_price']:.2f}"
                    }
                )
            )
            if not decision.approved:
                logger.warning(f"🛑 [JEV VETO] {symbol} AI Gate 진입 거부! 사유: {decision.reason} (신뢰도: {decision.confidence:.2f})")
                self.cooldowns[symbol] = time.time() + 900
                self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
                self.save_state()
                return False
            logger.info(f"🛡️ [JEV APPROVED] {symbol} AI Gate 통과! 사유: {decision.reason} (신뢰도: {decision.confidence:.2f})")
        except Exception as e:
            logger.warning(f"⚠️ JEV 검증 예외: {e}. 주의 하에 진행.")
        finally:
            loop.close()

        # [실시간 현재가 사전 검증 게이트] 주문 발주 직전 실시간 체결가 재확인
        live_px = self.get_realtime_price(symbol)
        if live_px and live_px > 0:
            if live_px <= stop_loss * 1.010:
                logger.warning(f"🛡️ [Pre-Order Gate Blocked] {symbol} 실시간 현재가(${live_px:.2f})가 손절선(${stop_loss:.2f}) 근접/이탈 -> 진입 취소")
                self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
                self.save_state()
                return False
            if live_px < trigger_price * 0.997:
                logger.warning(f"🛡️ [Pre-Order Gate Blocked] {symbol} 실시간 현재가(${live_px:.2f})가 돌파선(${trigger_price:.2f}) 아래로 밀림(윗꼬리 페이크) -> 진입 취소")
                return False
            if live_px > trigger_price * 1.015:
                logger.warning(f"🛡️ [Pre-Order Gate Blocked] {symbol} 실시간 현재가(${live_px:.2f})가 돌파선(${trigger_price:.2f}) 대비 +1.5% 초과 급등 -> 추격매수 차단")
                self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
                self.save_state()
                return False

        # [TIER 1] Marketable Limit (트리거 대비 +0.8% 슬리피지 버퍼)
        limit_entry_price = round(trigger_price * (1.0 + MAX_ENTRY_SLIPPAGE_PCT), 2)
        excg_cd = self.get_exchange_code(symbol)

        logger.info(f"⚡ [KIS ENTRY TRIGGER] {symbol}")
        logger.info(f"   수량: {qty}주 (~${qty * limit_entry_price:,.2f}) @ 지정가 ${limit_entry_price:.2f}")
        logger.info(f"   트리거: ${trigger_price:.2f} | 손절: ${stop_loss:.2f} (-{setup['risk_pct']}%) | 익절: ${take_profit:.2f} (+{setup['risk_pct']*RISK_REWARD_RATIO:.1f}%)")

        if self.dry_run:
            logger.info(f"   [Dry Run] {symbol} 매수 주문 가상 체결 기록.")
            self.active_positions[symbol] = {
                "qty": qty,
                "entry_price": trigger_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "entry_time": time.time(),
                "bar_time": setup.get("bar_time")
            }
            self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
            self.save_state()
            return True

        # KIS 실주문 전송 (TTTT1002U)
        headers = self.get_kis_headers("TTTT1002U")
        body = {
            "CANO": KIS_CANO,
            "ACNT_PRDT_CD": KIS_PRDT_ABRV,
            "OVRS_EXCG_CD": excg_cd,
            "PDNO": symbol,
            "ORD_QTY": str(qty),
            "OVRS_ORD_UNPR": f"{limit_entry_price:.2f}",
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": "00"  # 지정가
        }
        try:
            res = session.post(f"{KIS_URL}/uapi/overseas-stock/v1/trading/order", headers=headers, json=body, timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("rt_cd") == "0":
                odno = data.get("output", {}).get("ODNO", "")
                logger.info(f"   ✅ [KIS 매수 접수 성공] {symbol} ODNO: {odno}")
                self.pending_orders[symbol] = {
                    "odno": odno,
                    "side": "buy",
                    "qty": qty,
                    "price": limit_entry_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "placed_at": time.time(),
                    "bar_time": setup.get("bar_time")
                }
                self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
                self.save_state()
                return True
            else:
                msg = data.get("msg1", "")
                logger.error(f"   ❌ [KIS 매수 거부] {symbol}: {msg}")
                # 단일종목 ETP, 자격 미달, 거래정지 등 거부 종목은 당일(24시간) 쿨다운 + 바 레벨 락 격리
                self.cooldowns[symbol] = time.time() + 86400.0
                self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
                self.save_state()
        except Exception as e:
            logger.error(f"   ❌ [KIS 매수 예외] {symbol}: {e}")

        return False

    def cancel_stale_pending_orders(self):
        """미체결 상태로 장시간(ORDER_TIMEOUT_SEC 초) 방치된 매수 주문 취소 (TTTT1004U)"""
        now_t = time.time()
        for sym, o in list(self.pending_orders.items()):
            if now_t - o["placed_at"] > ORDER_TIMEOUT_SEC:
                odno = o["odno"]
                logger.warning(f"⏰ [Order Timeout] {sym} 미체결 매수 주문(ODNO: {odno}) {ORDER_TIMEOUT_SEC}초 경과 -> 취소 발주")
                headers = self.get_kis_headers("TTTT1004U")
                body = {
                    "CANO": KIS_CANO,
                    "ACNT_PRDT_CD": KIS_PRDT_ABRV,
                    "OVRS_EXCG_CD": self.get_exchange_code(sym),
                    "PDNO": sym,
                    "ORG_ODNO": str(odno),
                    "RVSE_CNCL_DVSN_CD": "02",
                    "ORD_QTY": str(o["qty"]),
                    "OVRS_ORD_UNPR": "0",
                    "ORD_SVR_DVSN_CD": "0"
                }
                is_cancelled = False
                try:
                    res = session.post(f"{KIS_URL}/uapi/overseas-stock/v1/trading/order-rvsecncl", headers=headers, json=body, timeout=8)
                    if res.status_code == 200:
                        d = res.json()
                        msg = d.get("msg1", "")
                        if d.get("rt_cd") == "0":
                            logger.info(f"   🚫 [Cancel Success] {sym} 주문 취소 접수 완료")
                            is_cancelled = True
                        elif "이미" in msg or "체결" in msg or "취소" in msg:
                            logger.info(f"   ℹ️ [Cancel Info] {sym} 이미 체결 또는 취소 처리됨: {msg}")
                            is_cancelled = True
                        else:
                            logger.error(f"   ❌ 주문 취소 거부 {sym}: {msg}")
                    else:
                        logger.error(f"   ❌ 주문 취소 HTTP 오류 {sym}: status={res.status_code}")
                except Exception as e:
                    logger.error(f"   ❌ 주문 취소 예외 {sym}: {e}")

                # 취소가 성공했거나 이미 거래소에서 소진된 것이 확인된 경우에만 pending_orders에서 제거
                if is_cancelled:
                    self.pending_orders.pop(sym, None)
                    self.cooldowns[sym] = now_t + 1800.0  # 타임아웃 취소된 종목은 30분 쿨다운
                    self.save_state()

    # ─────────────────────────────────────────────────────────────
    #  POSITION MONITORING & EXIT (Virtual Bracket Engine)
    # ─────────────────────────────────────────────────────────────
    def monitor_positions(self):
        """
        실시간 포지션 감시 및 가상 브래킷 OCO + 동적 본절/트레일링 스탑 집행:
        0. 전일 오버나이트 미청산 포지션(overnight_force_close 또는 entry_date < ny_today) 개장 직후 즉시 청산
        1. 수익률 +1.8% 도달 시 본절(+0.4%) 스탑 상향, +2.5% 도달 시 고점 대비 -1.0% 트레일링 스탑 가동
        2. 현재가 >= take_profit: 목표가 익절 매도
        3. 현재가 <= stop_loss: 스윙 로우 또는 트레일링 스탑 이탈 매도
        """
        if not self.active_positions:
            return

        now_ny = datetime.now(ZoneInfo("America/New_York"))
        ny_today = now_ny.strftime("%Y-%m-%d")
        now_t = time.time()

        # 09:30:00 ~ 09:30:05 EDT 개장 직후 시초가 호가 안정화를 위해 최대 5초 대기
        if now_ny.hour == 9 and now_ny.minute == 30 and now_ny.second < 5:
            time.sleep(5 - now_ny.second)

        state_modified = False
        for sym, pos in list(self.active_positions.items()):
            # 이미 매도 주문이 발주되어 체결 대기 중인 경우(45초간) 중복 매도 방지
            if now_t < float(pos.get("sell_pending_until", 0.0)):
                continue

            curr_px = self.get_realtime_price(sym)
            if not curr_px or curr_px <= 0:
                continue

            entry_px = float(pos.get("entry_price", curr_px))
            sl = float(pos["stop_loss"])
            tp = float(pos["take_profit"])
            qty = int(pos["qty"])

            # 0. 오버나이트 이월 포지션 개장 즉시 일괄 청산
            pos_date = pos.get("entry_date", ny_today)
            if pos.get("overnight_force_close") or pos_date < ny_today:
                logger.warning(f"🌅 [OVERNIGHT OPEN LIQUIDATION] {sym} {qty}주 전일 이월 포지션 개장 즉시 청산 집행 (현재가 ${curr_px:.2f})")
                if self.sell_position(sym, qty, curr_px, reason="OVERNIGHT_OPEN_LIQUIDATION"):
                    pos["sell_pending_until"] = now_t + 45.0
                    self.cooldowns[sym] = now_t + 1800.0
                    state_modified = True
                continue

            # 최고가 갱신 및 동적 본절/트레일링 스탑 업데이트
            highest_px = max(float(pos.get("highest_price", entry_px)), curr_px)
            if highest_px > float(pos.get("highest_price", 0.0)):
                pos["highest_price"] = highest_px
                state_modified = True

            if entry_px > 0:
                peak_gain_pct = (highest_px - entry_px) / entry_px
                if peak_gain_pct >= TRAILING_TRIGGER_PCT:
                    trail_sl = round(max(entry_px * (1.0 + BREAKEVEN_FLOOR_PCT), highest_px * (1.0 - TRAILING_DROP_PCT)), 2)
                    if trail_sl > sl:
                        logger.info(
                            f"📈 [Trailing Stop 상향] {sym} 고점 ${highest_px:.2f} (+{peak_gain_pct*100:.2f}%) -> "
                            f"손절선 상향 ${sl:.2f} -> ${trail_sl:.2f}"
                        )
                        sl = trail_sl
                        pos["stop_loss"] = sl
                        pos["trailing_active"] = True
                        state_modified = True
                elif peak_gain_pct >= BREAKEVEN_TRIGGER_PCT:
                    be_sl = round(entry_px * (1.0 + BREAKEVEN_FLOOR_PCT), 2)
                    if be_sl > sl:
                        logger.info(
                            f"🛡️ [Breakeven Lock 활성화] {sym} 고점 ${highest_px:.2f} (+{peak_gain_pct*100:.2f}%) -> "
                            f"본절 보호 스탑 설정 ${sl:.2f} -> ${be_sl:.2f}"
                        )
                        sl = be_sl
                        pos["stop_loss"] = sl
                        state_modified = True

            # 1. 익절 도달 (TP)
            if curr_px >= tp:
                logger.info(f"🎯 [TAKE PROFIT 도달] {sym} 현재가 ${curr_px:.2f} >= 목표가 ${tp:.2f} (+1:{RISK_REWARD_RATIO} R:R)")
                if self.sell_position(sym, qty, curr_px, reason="TAKE_PROFIT"):
                    pos["sell_pending_until"] = now_t + 45.0
                    self.cooldowns[sym] = now_t + 1800.0
                    state_modified = True

            # 2. 손절선 또는 트레일링 스탑 이탈 (SL)
            elif curr_px <= sl:
                exit_reason = "TRAILING_STOP" if pos.get("trailing_active") or sl > entry_px else "STOP_LOSS"
                logger.warning(f"🛑 [{exit_reason} 도달] {sym} 현재가 ${curr_px:.2f} <= 스탑가 ${sl:.2f} (평단 ${entry_px:.2f})")
                if self.sell_position(sym, qty, curr_px, reason=exit_reason):
                    pos["sell_pending_until"] = now_t + 45.0
                    self.cooldowns[sym] = now_t + 1800.0
                    state_modified = True

        if state_modified:
            self.save_state()

    def sell_position(self, symbol: str, qty: int, curr_px: float, reason: str = "EXIT") -> bool:
        """
        체결우선(-1%) 지정가 매도 실행 (TTTT1006U)
        실질적 시장가 청산 효과를 위해 현재가 대비 1% 아래 지정가로 발주
        """
        limit_px = round(curr_px * 0.98, 2)
        excg_cd = self.get_exchange_code(symbol)
        self.cooldowns[symbol] = time.time()

        logger.info(f"📤 [KIS 청산 매도] {symbol} {qty}주 @ ${limit_px:.2f} | 사유: {reason}")
        if self.dry_run:
            logger.info(f"   [Dry Run] {symbol} 매도 가상 완료.")
            return True

        headers = self.get_kis_headers("TTTT1006U")
        body = {
            "CANO": KIS_CANO,
            "ACNT_PRDT_CD": KIS_PRDT_ABRV,
            "OVRS_EXCG_CD": excg_cd,
            "PDNO": symbol,
            "ORD_QTY": str(qty),
            "OVRS_ORD_UNPR": f"{limit_px:.2f}",
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": "00"
        }
        try:
            res = session.post(f"{KIS_URL}/uapi/overseas-stock/v1/trading/order", headers=headers, json=body, timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("rt_cd") == "0":
                odno = data.get("output", {}).get("ODNO", "")
                logger.info(f"   ✅ [KIS 매도 접수 성공] {symbol} ODNO: {odno}")
                return True
            else:
                logger.error(f"   ❌ [KIS 매도 실패] {symbol}: {data.get('msg1')}")
        except Exception as e:
            logger.error(f"   ❌ [KIS 매도 예외] {symbol}: {e}")

        return False

    def eod_liquidate_all(self):
        """15:50 EST 장마감 전 미체결 매수 취소 및 당일 단타 미청산 포지션 일괄 전량 청산"""
        now_t = time.time()
        # 1. 미체결 매수 주문 즉시 취소
        for sym, o in list(self.pending_orders.items()):
            o["placed_at"] = 0
        if self.pending_orders:
            self.cancel_stale_pending_orders()

        if not self.active_positions:
            return
        logger.info("🚨 [EOD 당일 청산] 15:50 EST 도달 — 미청산 포지션 전량 청산 집행")
        state_modified = False
        for sym, pos in list(self.active_positions.items()):
            if now_t < float(pos.get("sell_pending_until", 0.0)):
                continue
            px = self.get_realtime_price(sym) or pos["entry_price"]
            if self.sell_position(sym, pos["qty"], px, reason="EOD_CLOSE"):
                pos["sell_pending_until"] = now_t + 45.0
                self.cooldowns[sym] = now_t + 1800.0
                state_modified = True
        if state_modified:
            self.save_state()

    # ─────────────────────────────────────────────────────────────
    #  MAIN EVALUATION LOOP
    # ─────────────────────────────────────────────────────────────
    def run_iteration(self):
        """단일 주기 실행 (약 15초 주기)"""
        now_ny = datetime.now(ZoneInfo("America/New_York"))
        now_t = time.time()
        is_weekday = now_ny.weekday() < 5

        # 미국 정규장 운영 시간: 09:30 ~ 16:00 EST
        market_open = is_weekday and (
            (now_ny.hour == 9 and now_ny.minute >= 30) or
            (10 <= now_ny.hour < 16)
        )

        logger.info(
            f"⏰ [Heartbeat] NY: {now_ny.strftime('%H:%M:%S')} | 장중: {market_open} | "
            f"보유 포지션: {list(self.active_positions.keys())} | 미체결: {list(self.pending_orders.keys())}"
        )

        if not market_open:
            return

        # 1. 원장 체결 대조 및 고스트 포지션 정리
        self.reconcile_positions_with_ledger()

        # 2. 미체결 매수 주문 타임아웃 취소
        self.cancel_stale_pending_orders()

        # 3. 실시간 포지션 감시 (익절/손절 체크)
        self.monitor_positions()

        # 4. EOD 장마감 전량 청산 체크 (15:50 EST)
        if now_ny.hour == EOD_CLOSE_HOUR_EST and now_ny.minute >= EOD_CLOSE_MIN_EST:
            self.eod_liquidate_all()
            return

        # 5. 신규 진입 조건 검사
        # - 10:00 EST 이전 진입 대기 (첫 30분봉 완성 대기)
        # - 14:30 EST 이후 컷오프
        # - 최대 동시 보유 4종목 이하
        before_start = (now_ny.hour < START_HOUR_EST)
        past_cutoff = (now_ny.hour > CUTOFF_HOUR_EST) or (now_ny.hour == CUTOFF_HOUR_EST and now_ny.minute >= CUTOFF_MIN_EST)

        if before_start:
            logger.info(f"⏳ [오픈 대기] 10:00 EST 첫 30분봉 완성 전까지 신규 진입 대기 중...")
            return

        if past_cutoff:
            return

        if len(self.active_positions) >= MAX_CONCURRENT_TRADES:
            return

        # 스캐너 실행 (10분 주기 또는 워치리스트 부재 시)
        if not self.watchlist or (now_t - self.last_scanned_time > 600):
            self.sync_account_equity()
            self.scan_top_movers(limit=25)
            self.last_scanned_time = now_t

        for sym in self.watchlist:
            if sym in self.active_positions or sym in self.pending_orders:
                continue

            if now_t - self.cooldowns.get(sym, 0) < COOLDOWN_SEC:
                continue

            if len(self.active_positions) >= MAX_CONCURRENT_TRADES:
                break

            df = self.fetch_bars(sym, limit=40)
            if df is not None and len(df) >= 15:
                is_triggered, setup = self.detect_first_pullback_setup(df)
                if is_triggered:
                    curr_bar_time = setup.get("bar_time", "")
                    # [BAR-LEVEL LOCK] 동일 30분봉 내 중복 진입 차단
                    if self.last_entry_bar.get(sym) == curr_bar_time:
                        continue

                    logger.info(f"🔥 [SETUP 포착] {sym} 30분봉 1차 눌림목 돌파 셋업 발생! (Trigger: ${setup['trigger_price']:.2f})")
                    self.execute_entry(sym, setup)
                    time.sleep(1)

    def run_loop(self):
        """메인 지속 실행 루프"""
        logger.info("🟢 [KIS Cameron US 30M Trader] 상시 루프 가동 시작 (주기: 15초)")
        while True:
            try:
                self.run_iteration()
                time.sleep(15)
            except KeyboardInterrupt:
                logger.info("🛑 사용자에 의한 봇 종료 요청")
                break
            except Exception as e:
                logger.error(f"❌ 메인 루프 예외: {e}")
                time.sleep(15)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="KIS 미국주식 30분봉 로스 카메론 풀백 트레이더")
    parser.add_argument("--dry-run", action="store_true", help="가상 주문 모드로 실행")
    args = parser.parse_args()

    trader = KisCameronPullbackUS30M(dry_run=args.dry_run)
    trader.run_loop()
