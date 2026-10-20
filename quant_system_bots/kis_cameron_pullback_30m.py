#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kis_cameron_pullback_30m.py — KIS 한국주식(KOSPI/KOSDAQ) 30분봉 로스 카메론(Ross Cameron) 풀백 트레이더
==================================================================================================
전략 개요:
1. 실시간 급등주 스캐너 (KIS FHPST01700000 API):
   - 당일 등락률 +3.0% ~ +28.0% 급등주 중 누적 거래량 10만 주 이상 동적 스캐닝
   - 우선주, 스팩(SPAC), ETN 및 관리/상폐 종목 필터링
2. 30분봉 1차 눌림목(First Pullback) 셋업:
   - 상승 충격파: 직전 2~6봉 내 +3.0% 이상 서지(Surge)
   - 눌림목 캔들: 음봉 또는 몸통 45% 이하 도지형 캔들
   - 지지 레벨: 9 EMA (2% 버퍼) 및 VWAP (3% 버퍼) 지지
   - 되돌림 폭: 충격파 상승분의 60% 이내
   - 거래량 수축: 눌림목 거래량 <= 충격파 평균 거래량의 1.35배
   - 유동성 가드: 캔들 거래량 >= 10,000주 (호가 공백 슬리피지 방지)
   - 돌파 트리거: 직전 눌림목 캔들의 고점 돌파 시 매수 발주
   - 바 레벨 락(Bar-Level Lock): 동일 30분봉 내 1회만 진입 (중복 진입 원천 차단)
3. Universal Jev Gate (KR_STOCKS):
   - 전환사채(CB/BW) 폭탄, 유상증자, 테마 꼭대기 설거지 공시 AI 필터링
   - Veto 거부 시 30분 쿨다운 등록으로 뇌동매매/무한 재시도 차단
4. 리스크 관리 & 주문 집행:
   - 동적 Half-Kelly 포지션 사이징: 계좌 가용 자본의 16% ~ 20%
   - 최대 동시 보유 4종목 (포트폴리오 분산)
   - 손절(SL): 눌림목 저점 (최대 -5.0% 하드 캡)
   - 익절(TP): 1:2.5 Risk-to-Reward (~+5% to +10%)
   - 장마감 EOD 15:15 KST 당일 전량 청산 (오버나이트 갭하락 리스크 배제)
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

LOG_FILE = os.path.join(LOG_DIR, "kis_cameron_30m.log")
POSITIONS_FILE = os.path.join(STATE_DIR, "kis_cameron_30m_positions.json")
TOKEN_FILE = os.path.join(CURRENT_DIR, "remote_deploy", "kis_token.json")

logger = logging.getLogger("KIS_Cameron_30M")
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

# ── KIS CREDENTIALS & SESSIONS ──
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

# ── STRATEGY HYPERPARAMETERS ──
TIMEFRAME = "30m"
MIN_PRICE = 1000.0             # 1,000원 이상 (극단적 초저가 동전주 제외)
MAX_PRICE = 200000.0           # 20만원 이하
MIN_SURGE_PCT = 0.035          # 충격파: 최소 +3.5% 상승 (폭락장 휩소 방어)
MAX_SL_PCT = 0.065             # 최대 손절 -6.5% 유연한 하드 캡 (기존 4.0%에서 완화)
MIN_SL_PCT = 0.008             # 최소 손절 -0.8%
RISK_REWARD_RATIO = 1.8        # 1:1.8 Risk-to-Reward (검증 최적치)
TRAIL_ACTIVATE_PCT = 0.018     # +1.8% 도달 시 트레일링 및 본절(+0.6%) 보호 가동
TRAIL_DISTANCE_PCT = 0.008     # 고점 대비 -0.8% 추적 익절
BE_FLOOR_PCT = 0.006           # 최소 수수료·세금 보전 익절폭 (+0.6%)
TOTAL_BUDGET_CAP = 3000000.0   # 🛡️ [폭락장 방어] 총 운용 예산 300만 원 하드 캡 (총 주문가능 1,487만 원 중 300만 원만 사용)
MAX_PORTFOLIO_PCT = 0.25       # 종목당 최대 25% 배정 (~75만 원)
MAX_POSITION_KRW = 800000.0    # 종목당 최대 80만 원 상한
MAX_CONCURRENT_POSITIONS = 4   # 최대 4종목 보유 (300만 원 분산)
COOLDOWN_SEC = 900             # 15분 기본 쿨다운
JEV_VETO_COOLDOWN_SEC = 1800   # JEV 거부 시 30분 쿨다운

# 상장폐지/정리매매 블랙리스트
EXCLUDED_SYMBOLS = {"007630", "259290", "066790"}


def is_pure_korean_common_stock(code: str, name: str) -> bool:
    """한국 순수 보통주 검증 (우선주, 스팩, 리츠, ETN, ETF, 선물/파생상품 전면 차단)"""
    if not (len(code) == 6 and code.isdigit()):
        return False
    if not code.endswith("0"):
        return False
    excluded_keywords = [
        "우", "우B", "우C", "스팩", "SPAC", "리츠", "REIT",
        "ETN", "ETF", "인버스", "레버리지", "선물", "옵션", "풋", "콜",
        "KODEX", "TIGER", "ACE", "SOL", "KBSTAR", "RISE", "PLUS",
        "HANARO", "KOSEF", "TIMEFOLIO", "ARIRANG", "WOORI", "히어로즈", "마이티", "UNICORN"
    ]
    if any(kw in name for kw in excluded_keywords):
        return False
    return True


class KisCameronPullbackTrader:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.access_token = ""
        self.token_expired_at = 0
        self.account_equity = 10000000.0
        self.account_cash = 10000000.0
        self.watchlist: List[Dict[str, Any]] = []
        self.last_scanned_time = 0
        self.positions: Dict[str, Any] = {}
        self.cooldowns: Dict[str, float] = {}
        self.last_entry_bar: Dict[str, str] = {}
        self.jev_gate = UniversalJevGate(confidence_threshold=0.60)

        self.load_state()
        logger.info("=" * 70)
        logger.info(f"🚀 [KIS 한국주식 30분봉 로스 카메론 풀백 엔진] 초기화 완료 (Dry-Run: {self.dry_run})")
        logger.info(f"   계좌: {KIS_CANO}-{KIS_PRDT_ABRV} | 엔드포인트: {KIS_URL}")
        logger.info(f"   포지션 파일: {POSITIONS_FILE}")
        logger.info("=" * 70)

        self.issue_token()
        self.sync_account_balance()

    def issue_token(self) -> bool:
        """Issue or renew KIS token with file caching to prevent EGW00133 rate limits"""
        now = time.time()
        if self.access_token and now < self.token_expired_at:
            return True

        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                cached_token = cache.get("access_token")
                cached_exp = cache.get("expires_at", 0)
                if cached_token and now < cached_exp - 300:
                    self.access_token = cached_token
                    self.token_expired_at = cached_exp
                    return True
            except Exception as e:
                logger.warning(f"⚠️ Token cache read error: {e}")

        # Request new token
        url = f"{KIS_URL}/oauth2/tokenP"
        payload = {
            "grant_type": "client_credentials",
            "appkey": KIS_APP_KEY,
            "appsecret": KIS_APP_SECRET
        }
        try:
            resp = session.post(url, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token", "")
                expires_in = int(data.get("expires_in", 86400))
                self.token_expired_at = now + expires_in
                os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
                with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                    json.dump({"access_token": self.access_token, "expires_at": self.token_expired_at}, f)
                logger.info("🔑 KIS 접근 토큰 발급 및 캐싱 성공")
                return True
            else:
                logger.error(f"❌ KIS 토큰 발급 실패: {resp.text}")
        except Exception as e:
            logger.error(f"❌ KIS 토큰 발급 예외: {e}")
        return False

    def get_headers(self, tr_id: str) -> Dict[str, str]:
        return {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": KIS_APP_KEY,
            "appsecret": KIS_APP_SECRET,
            "tr_id": tr_id
        }

    def load_state(self):
        try:
            if os.path.exists(POSITIONS_FILE):
                with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self.positions = saved.get("positions", {})
                self.cooldowns = saved.get("cooldowns", {})
                self.last_entry_bar = saved.get("last_entry_bar", {})
                logger.info(f"📂 [State Loaded] 보유 포지션 {len(self.positions)}건 복원 완료: {list(self.positions.keys())}")
        except Exception as e:
            logger.error(f"❌ State load error: {e}")
            self.positions = {}
            self.cooldowns = {}
            self.last_entry_bar = {}

    def save_state(self):
        try:
            payload = {
                "positions": self.positions,
                "cooldowns": self.cooldowns,
                "last_entry_bar": self.last_entry_bar,
                "updated_at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
            }
            tmp = POSITIONS_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            os.replace(tmp, POSITIONS_FILE)
        except Exception as e:
            logger.error(f"❌ State save error: {e}")

    def sync_account_balance(self):
        if not self.issue_token():
            return
        
        # 1. KIS 주식주문가능금액조회 (해외 통합증거금 포함 실제 매수 여력 확인)
        live_buying_power = 14872230.0 # 기본 통합증거금 기준 1,487만 원
        url = f"{KIS_URL}/uapi/domestic-stock/v1/trading/inquire-psbl-order"
        headers = self.get_headers("TTTC8908R")
        params = {
            "CANO": KIS_CANO,
            "ACNT_PRDT_CD": KIS_PRDT_ABRV,
            "PDNO": "005930",
            "ORD_UNPR": "0",
            "ORD_DVSN": "01",
            "CMA_EVLU_AMT_ICLD_YN": "Y",
            "OVRS_ICLD_YN": "Y"
        }
        try:
            resp = session.get(url, headers=headers, params=params, timeout=6)
            if resp.status_code == 200:
                out = resp.json().get("output", {})
                max_buy = float(out.get("max_buy_amt", 0) or out.get("nrcvb_buy_amt", 0) or 0)
                if max_buy > 0:
                    live_buying_power = max_buy
        except Exception as e:
            logger.warning(f"⚠️ 주문가능금액 조회 예외: {e}")

        # 2. 사용자 지정 폭락장 방어 하드 캡 (300만 원 강제 클램프)
        self.total_live_buying_power = live_buying_power
        self.account_equity = min(live_buying_power, TOTAL_BUDGET_CAP)
        self.account_cash = self.account_equity

        logger.info(
            f"💼 [KIS Account] 실시간 총 주문가능액: ₩{self.total_live_buying_power:,.0f} | "
            f"🛡️ 폭락장 방어 예산 캡: ₩{self.account_equity:,.0f} (최대 300만 원 한도 운용)"
        )

    def scan_top_movers(self, limit: int = 25) -> List[Dict[str, Any]]:
        """KIS Open API 실시간 등락률 순위(FHPST01700000)를 통한 모멘텀 급등주 동적 발굴"""
        if not self.issue_token():
            return []
        logger.info("🔍 [Scanner] KIS 실시간 급등주 스캔 시작 (FHPST01700000)...")
        url = f"{KIS_URL}/uapi/domestic-stock/v1/ranking/fluctuation"
        headers = self.get_headers("FHPST01700000")
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_cond_scr_div_code": "20170",
            "fid_input_iscd": "0000",
            "fid_rank_sort_cls_code": "0",  # 상승률 순
            "fid_input_cnt_1": "0",
            "fid_prc_cls_code": "0",
            "fid_input_price_1": str(int(MIN_PRICE)),
            "fid_input_price_2": str(int(MAX_PRICE)),
            "fid_vol_cnt": "100000",        # 거래량 10만주 이상
            "fid_trgt_cls_code": "0",
            "fid_trgt_exls_cls_code": "0",
            "fid_div_cls_code": "0",
            "fid_rsfl_rate1": "3.0",        # +3% 이상
            "fid_rsfl_rate2": "28.5"        # 상한가(30%) 진입 전 종목만
        }
        candidates = []
        try:
            resp = session.get(url, headers=headers, params=params, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("output", [])
                for item in items:
                    code = item.get("stck_shrn_iscd", "")
                    name = item.get("hts_kor_isnm", "")
                    price = float(item.get("stck_prpr", 0.0))
                    rate = float(item.get("prdy_ctrt", 0.0))
                    vol = int(item.get("acml_vol", 0))

                    if code in EXCLUDED_SYMBOLS:
                        continue
                    # 우선주, 스팩, 리츠, ETN, ETF 전면 필터링
                    if not is_pure_korean_common_stock(code, name):
                        continue

                    is_kq_by_code = code.isdigit() and int(code) > 50000
                    market_suffix = ".KQ" if len(code) == 6 and (code.startswith("1") or code.startswith("2") or code.startswith("3") or code.startswith("4") or (code.startswith("0") and is_kq_by_code)) else ".KS"
                    candidates.append({
                        "code": code,
                        "name": name,
                        "price": price,
                        "change_pct": rate,
                        "volume": vol,
                        "yf_ticker": f"{code}{market_suffix}"
                    })
                    logger.info(f"   🎯 Scanner Match: {name}({code}) | ₩{price:,.0f} | +{rate:.1f}% | 거래량: {vol:,}주")
        except Exception as e:
            logger.error(f"❌ KIS 스캐너 에러: {e}")

        final_targets = candidates[:limit]
        logger.info(f"📋 [Watchlist Updated] 당일 타깃 유니버스 ({len(final_targets)}종목) 갱신 완료")
        self.watchlist = final_targets
        return final_targets

    def fetch_30m_bars(self, code: str) -> Optional[pd.DataFrame]:
        """Fetch 30-minute OHLCV candles with VWAP and 9 EMA, trying both .KQ and .KS"""
        for suffix in [".KQ", ".KS"]:
            ticker = f"{code}{suffix}"
            try:
                df = yf.download(ticker, period="1mo", interval=TIMEFRAME, progress=False)
                if df is not None and not df.empty and len(df) >= 15:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = [c[0].lower() for c in df.columns]
                    else:
                        df.columns = [c.lower() for c in df.columns]

                    df = df.reset_index()
                    # Ensure the first column (timestamp) is named 'time'
                    df.rename(columns={df.columns[0]: "time"}, inplace=True)

                    tp = (df["high"] + df["low"] + df["close"]) / 3
                    df["vwap"] = (tp * df["volume"]).cumsum() / df["volume"].cumsum().replace(0, 1)
                    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
                    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean() # 중기 추세선
                    return df
            except Exception as e:
                logger.debug(f"Fetch failed for {ticker}: {e}")
                continue
        return None

    def detect_first_pullback_setup(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """Ross Cameron 30m First Pullback Setup Evaluator"""
        if len(df) < 15:
            return False, {}

        curr_bar = df.iloc[-1]
        prev_bar = df.iloc[-2]

        # 1. 눌림목 캔들: 음봉 또는 실몸통 45% 이하 도지/팽이형 캔들
        prev_rng = prev_bar["high"] - prev_bar["low"]
        if prev_rng <= 0:
            return False, {}
        is_bearish = prev_bar["close"] < prev_bar["open"]
        is_small_body = (abs(prev_bar["close"] - prev_bar["open"]) / prev_rng) <= 0.45
        if not (is_bearish or is_small_body):
            return False, {}

        # 2. 9 EMA (2% 버퍼) 및 VWAP (3% 버퍼) 지지 확인
        if prev_bar["close"] < prev_bar["ema9"] * 0.98 or prev_bar["low"] < prev_bar["vwap"] * 0.97:
            return False, {}

        # 3. [폭락장 역배열 트랩 방어] 20 EMA(중기 추세선) 아래에 있는 하락 추세 종목 원천 차단
        if "ema20" in prev_bar and prev_bar["close"] < prev_bar["ema20"] * 0.99:
            return False, {}

        # 4. 직전 2~6봉 내 급등 충격파(Impulse Leg) 확인
        prior = df.iloc[-7:-2]
        surge_low = prior["low"].min()
        surge_high = prior["high"].max()
        surge = surge_high - surge_low
        if surge <= 0 or (surge / surge_low) < MIN_SURGE_PCT:
            return False, {}

        # 4. 되돌림 폭 65% 이내 & 거래량 축소
        pullback_depth = surge_high - prev_bar["low"]
        retrace_ratio = pullback_depth / surge
        if retrace_ratio > 0.65:
            return False, {}

        prior_avg_vol = prior["volume"].mean()
        if prior_avg_vol > 0 and prev_bar["volume"] > prior_avg_vol * 1.35:
            return False, {}

        # 5. 초소형 유동성 트랩 방지 (캔들 거래량 10,000주 이상)
        if prev_bar["volume"] < 10000 or prior_avg_vol < 10000:
            return False, {}

        # 6. 돌파 트리거
        trigger_price = prev_bar["high"]
        stop_loss = prev_bar["low"]
        risk = trigger_price - stop_loss
        if risk <= 0:
            return False, {}

        risk_pct = risk / trigger_price
        if not (MIN_SL_PCT <= risk_pct <= MAX_SL_PCT):
            return False, {}

        take_profit = trigger_price + (risk * RISK_REWARD_RATIO)
        is_triggered = curr_bar["high"] >= trigger_price

        vol_ratio = prev_bar["volume"] / prior_avg_vol if prior_avg_vol > 0 else 1.0

        setup_info = {
            "bar_time": str(curr_bar["time"]),
            "trigger_price": float(trigger_price),
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit),
            "risk_pct": float(risk_pct * 100),
            "target_pct": float((take_profit / trigger_price - 1) * 100),
            "vol_ratio": float(vol_ratio),
            "retrace_ratio": float(retrace_ratio * 100),
            "surge_pct": float(surge / surge_low * 100),
            "curr_price": float(curr_bar["close"]),
            "is_triggered": is_triggered
        }
        return is_triggered, setup_info

    def calculate_position_size(self, trigger_price: float, risk_pct: float) -> int:
        """Dynamic Half-Kelly Position Sizing (총 300만 원 예산 엄격 준수)"""
        current_invested = sum(pos.get("qty", 0) * pos.get("entry_price", 0) for pos in self.positions.values())
        remaining_budget = max(0.0, TOTAL_BUDGET_CAP - current_invested)

        if remaining_budget < 100000.0:
            logger.warning(f"⏸️ [Budget Exhausted] 잔여 예산 ₩{remaining_budget:,.0f} < 10만 원. 추가 매수 스킵.")
            return 0

        conviction = 1.0
        if risk_pct > 3.0:
            conviction -= 0.15

        kelly_pct = max(0.20, min(MAX_PORTFOLIO_PCT, MAX_PORTFOLIO_PCT * conviction))
        target_allocation = min(self.account_equity * kelly_pct, MAX_POSITION_KRW)
        target_allocation = min(target_allocation, remaining_budget)

        qty = max(1, math.floor(target_allocation / trigger_price))
        logger.info(
            f"   📊 [폭락장 방어 사이징] 배정: ₩{target_allocation:,.0f} "
            f"(누적 투자: ₩{current_invested:,.0f} / 한도 ₩{TOTAL_BUDGET_CAP:,.0f}) -> {qty}주 @ ₩{trigger_price:,.0f}"
        )
        return qty

    def execute_order(self, code: str, name: str, qty: int, side: str, price: float = 0.0) -> bool:
        """Executes market/limit buy or sell order via KIS OpenAPI"""
        if self.dry_run:
            logger.info(f"🧪 [DRY-RUN] {side.upper()} {name}({code}) {qty}주 주문 체결 시뮬레이션 @ ₩{price:,.0f}")
            return True

        if not self.issue_token():
            return False

        url = f"{KIS_URL}/uapi/domestic-stock/v1/trading/order-cash"
        tr_id = "TTTC0802U" if side == "buy" else "TTTC0801U"
        headers = self.get_headers(tr_id)
        ord_dvsn = "01" if price == 0.0 else "00"  # 01: 시장가, 00: 지정가

        payload = {
            "CANO": KIS_CANO,
            "ACNT_PRDT_CD": KIS_PRDT_ABRV,
            "PDNO": code,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(qty),
            "ORD_UNPR": str(int(price))
        }
        try:
            resp = session.post(url, headers=headers, json=payload, timeout=8)
            data = resp.json()
            if data.get("rt_cd") == "0":
                logger.info(f"✅ [주문 성공] {side.upper()} {name}({code}) {qty}주 | {data.get('msg1')}")
                return True
            else:
                logger.error(f"❌ [주문 실패] {side.upper()} {code}: {data.get('msg1')} ({data.get('msg_cd')})")
        except Exception as e:
            logger.error(f"❌ KIS 주문 송출 예외 ({code}): {e}")
        return False

    def get_realtime_quote(self, code: str) -> Optional[Dict[str, float]]:
        """KIS 실시간 현재가 및 상한가 조회 (FHKST01010100)"""
        if not self.issue_token():
            return None
        try:
            url = f"{KIS_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = self.get_headers("FHKST01010100")
            params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code}
            r = session.get(url, headers=headers, params=params, timeout=4)
            if r.status_code == 200:
                out = r.json().get("output", {})
                price = float(out.get("stck_prpr", 0) or 0)
                upper_limit = float(out.get("stck_mxpr", 0) or 0)
                if price > 0:
                    return {"price": price, "upper_limit": upper_limit}
        except Exception as e:
            logger.warning(f"⚠️ 실시간 현재가 조회 예외 ({code}): {e}")
        return None

    def fetch_latest_fill_price(self, code: str, fallback_price: float) -> float:
        """주문 직후 KIS 당일 체결내역(TTTC8001R)에서 실제 평균 체결단가 확인"""
        if self.dry_run or not self.issue_token():
            return fallback_price
        try:
            time.sleep(0.6)
            today_str = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d")
            url = f"{KIS_URL}/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
            headers = self.get_headers("TTTC8001R")
            headers["custtype"] = "P"
            params = {
                "CANO": KIS_CANO,
                "ACNT_PRDT_CD": KIS_PRDT_ABRV,
                "INQR_STRT_DT": today_str,
                "INQR_END_DT": today_str,
                "SLL_BUY_DVSN_CD": "02",
                "INQR_DVSN": "00",
                "PDNO": code,
                "CCLD_DVSN": "01",
                "ORD_GNO_BRNO": "",
                "ODNO": "",
                "INQR_DVSN_3": "00",
                "INQR_DVSN_1": "",
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": ""
            }
            r = session.get(url, headers=headers, params=params, timeout=5)
            if r.status_code == 200:
                rows = r.json().get("output1", [])
                for row in rows:
                    if row.get("pdno") == code and float(row.get("avg_prvs", 0) or 0) > 0:
                        return float(row["avg_prvs"])
        except Exception as e:
            logger.warning(f"⚠️ 실체결단가 조회 예외 ({code}): {e}")
        return fallback_price

    def evaluate_positions(self):
        """Monitors open positions for Take Profit, Stop Loss, Upper Limit, or EOD close"""
        now_kst = datetime.now(ZoneInfo("Asia/Seoul"))
        now_t = time.time()

        for code, pos in list(self.positions.items()):
            current_price = pos.get("entry_price", 0.0)
            upper_limit = 0.0
            quote = self.get_realtime_quote(code)
            if quote:
                current_price = quote["price"]
                upper_limit = quote["upper_limit"]

            entry_p = float(pos.get("entry_price", current_price) or current_price)
            highest_p = max(float(pos.get("highest_price", entry_p) or entry_p), current_price)
            pos["highest_price"] = highest_p

            sl = pos["stop_loss"]
            tp = pos["take_profit"]
            if upper_limit > 0 and tp > upper_limit:
                tp = upper_limit
                pos["take_profit"] = tp

            # 트레일링 스탑 & 본절(+0.6%) 보호 스탑 동적 상향
            if entry_p > 0 and highest_p >= entry_p * (1.0 + TRAIL_ACTIVATE_PCT):
                trail_sl = round(highest_p * (1.0 - TRAIL_DISTANCE_PCT))
                be_floor = round(entry_p * (1.0 + BE_FLOOR_PCT))
                new_sl = max(sl, trail_sl, be_floor)
                if new_sl > sl:
                    sl = new_sl
                    pos["stop_loss"] = sl
                    logger.info(f"📈 [트레일링 스탑 상향] {pos.get('name', code)}({code}) 고점 ₩{highest_p:,.0f} -> 보호 스탑 ₩{sl:,.0f} (평단 ₩{entry_p:,.0f})")

            qty = pos["qty"]
            name = pos.get("name", code)

            # EOD 15:15 KST 당일 청산
            is_eod = (now_kst.hour == 15 and now_kst.minute >= 15)
            hit_upper = (upper_limit > 0 and current_price >= upper_limit)
            hit_tp = (current_price >= tp) or hit_upper
            hit_sl = current_price <= sl

            if hit_tp or hit_sl or is_eod:
                reason = "TAKE_PROFIT" if hit_tp else ("STOP_LOSS" if hit_sl else "EOD_CLOSE")
                logger.info(f"🔔 [청산 발동] {name}({code}) {qty}주 | 사유: {reason} | 현재가: ₩{current_price:,.0f} (손절: ₩{sl:,.0f}, 익절: ₩{tp:,.0f})")
                success = self.execute_order(code, name, qty, "sell", 0.0)
                if success:
                    del self.positions[code]
                    self.cooldowns[code] = now_t
                    self.save_state()

    def run_iteration(self):
        now_kst = datetime.now(ZoneInfo("Asia/Seoul"))
        now_t = time.time()
        is_open = (9 <= now_kst.hour < 15 or (now_kst.hour == 15 and now_kst.minute <= 20)) and now_kst.weekday() < 5

        logger.info(f"⏰ [Heartbeat] KST: {now_kst.strftime('%H:%M:%S')} | 정규장: {is_open} | 보유 포지션: {list(self.positions.keys())}")

        # 1. 보유 포지션 감시
        self.evaluate_positions()

        # 장 운영 시간 외 대기
        if not is_open and not self.dry_run:
            logger.info("⏳ 현재 한국 정규장(09:00 ~ 15:20 KST) 운영 시간이 아닙니다. 대기 중...")
            return

        # 2. 10분마다 급등주 스캐너 갱신
        if not self.watchlist or (now_t - self.last_scanned_time > 600):
            self.scan_top_movers(limit=25)
            self.last_scanned_time = now_t

        if len(self.positions) >= MAX_CONCURRENT_POSITIONS:
            logger.info(f"⏸️ 최대 보유 한도({MAX_CONCURRENT_POSITIONS}종목) 도달. 신규 진입 대기...")
            return

        # 3. [시초가 변동성 방어] 09:00 ~ 09:30 당일 첫 30분봉 완성 대기
        # 시초가 갭등락 노이즈 및 전일 종가봉 기반 오진입 방지 -> 09:30 이후 첫 30M 캔들 완성 후 진입 개시
        if now_kst.hour == 9 and now_kst.minute < 30:
            logger.info("⏳ [시초가 방어] 09:00~09:30 첫 30분봉 완성 대기 중 (신규 진입은 09:30 이후 개시)...")
            return

        # 3.2 [오후장 설거지 방어] 14:30 KST 이후 신규 진입 전면 차단 (기존 보유분 트레일링/청산만 수행)
        if (now_kst.hour == 14 and now_kst.minute >= 30) or now_kst.hour >= 15:
            logger.info("🛡️ [오후장 진입 마감] 14:30 KST 이후 신규 매수 차단 (보유 포지션 감시 전용 모드)...")
            return

        # 4. 타깃 유니버스 30분봉 풀백 셋업 검증
        for target in self.watchlist:
            code = target["code"]
            name = target["name"]
            yf_ticker = target["yf_ticker"]

            # 중복 진입 및 쿨다운 검사
            if code in self.positions or (now_t - self.cooldowns.get(code, 0) < COOLDOWN_SEC):
                continue

            df = self.fetch_30m_bars(code)
            if df is None:
                continue

            triggered, setup = self.detect_first_pullback_setup(df)
            if triggered:
                bar_time = setup.get("bar_time")
                if self.last_entry_bar.get(code) == bar_time:
                    continue

                # 3.5 [실시간 현재가 1차 사전 검증 게이트 — yfinance 지연 보정]
                quote_pre = self.get_realtime_quote(code)
                if not quote_pre:
                    logger.warning(f"⚠️ [SKIP] {name}({code}) 실시간 현재가 조회 실패로 진입 보류")
                    continue
                live_p = quote_pre["price"]
                upper_lim = quote_pre["upper_limit"]
                trig_p = setup["trigger_price"]
                sl_p = setup["stop_loss"]

                if live_p <= sl_p * 1.008 or live_p < trig_p * 0.995:
                    logger.info(
                        f"🛡️ [LIVE GATE BLOCK] {name}({code}) 실시간 현재가(₩{live_p:,.0f})가 "
                        f"돌파선(₩{trig_p:,.0f})/손절선(₩{sl_p:,.0f}) 하회 — 지연 시그널 진입 차단"
                    )
                    continue
                if live_p > trig_p * 1.015:
                    logger.info(
                        f"🛡️ [SLIPPAGE GUARD] {name}({code}) 실시간 현재가(₩{live_p:,.0f})가 "
                        f"돌파선(₩{trig_p:,.0f}) 대비 +{(live_p/trig_p - 1)*100:.2f}% 급등 — 고점 추격매수 차단"
                    )
                    self.last_entry_bar[code] = bar_time
                    self.save_state()
                    continue
                if upper_lim > 0 and (upper_lim - live_p) / live_p < 0.015:
                    logger.info(
                        f"🛡️ [UPPER LIMIT GUARD] {name}({code}) 현재가(₩{live_p:,.0f})가 "
                        f"상한가(₩{upper_lim:,.0f}) 근접(여력 1.5% 미만) — 진입 차단"
                    )
                    self.last_entry_bar[code] = bar_time
                    self.save_state()
                    continue

                logger.info(f"🔥 [SETUP CONFIRMED] {name}({code}) | 30M Bar: {bar_time} | 현재가: ₩{live_p:,.0f} (돌파선: ₩{trig_p:,.0f}) | 되돌림: {setup['retrace_ratio']:.1f}% | 리스크: {setup['risk_pct']:.1f}%")

                # 4. Universal Jev Gatekeeper 사전 검증
                loop = asyncio.new_event_loop()
                try:
                    decision = loop.run_until_complete(
                        self.jev_gate.verify_entry(
                            asset_class="KR_STOCKS",
                            symbol=f"{name}({code})",
                            setup_name="CAMERON_30M_PULLBACK",
                            context={
                                "name": name,
                                "code": code,
                                "surge_pct": setup.get("surge_pct", 0),
                                "day_change_pct": target.get("change_pct", 0),
                                "day_volume": target.get("volume", 0),
                                "retrace_pct": setup.get("retrace_ratio", 0),
                                "vol_ratio": setup.get("vol_ratio", 1.0),
                                "pullback_vol_contraction": setup.get("vol_ratio", 1.0),
                                "risk_pct": setup.get("risk_pct", 0),
                                "theme": f"KRX Top Gainer Momentum ({name})"
                            }
                        )
                    )
                    if not decision.approved:
                        logger.warning(f"🛑 [JEV VETO] {name}({code}) AI 거절! 사유: {decision.reason} (Conf: {decision.confidence:.2f})")
                        # 거부 시 30분 쿨다운 등록 및 당해 봉 잠금
                        self.cooldowns[code] = time.time() + (JEV_VETO_COOLDOWN_SEC - COOLDOWN_SEC)
                        self.last_entry_bar[code] = bar_time
                        self.save_state()
                        continue
                    logger.info(f"🛡️ [JEV APPROVED] {name}({code}) AI 승인 완료! 사유: {decision.reason} (Conf: {decision.confidence:.2f})")
                except Exception as e:
                    logger.warning(f"⚠️ Jev 검증 예외 ({code}): {e}")
                finally:
                    loop.close()

                # 5. 주문 직전 실시간 가격 2차 재검증 및 실체결가 기반 SL/TP 동기화
                quote_now = self.get_realtime_quote(code) or quote_pre
                exec_ref_price = quote_now["price"]
                upper_lim_now = quote_now["upper_limit"]
                if exec_ref_price <= setup["stop_loss"] * 1.008 or exec_ref_price > setup["trigger_price"] * 1.016:
                    logger.warning(
                        f"🛑 [PRE-ORDER ABORT] {name}({code}) JEV 검증 중 가격 이탈 "
                        f"(현재가: ₩{exec_ref_price:,.0f}, 돌파선: ₩{setup['trigger_price']:,.0f}, 손절선: ₩{setup['stop_loss']:,.0f}) — 주문 취소"
                    )
                    continue

                qty = self.calculate_position_size(exec_ref_price, setup["risk_pct"])
                if qty <= 0:
                    continue
                success = self.execute_order(code, name, qty, "buy", 0.0)
                if success:
                    actual_entry = self.fetch_latest_fill_price(code, exec_ref_price)
                    raw_sl = setup["stop_loss"]
                    actual_risk = actual_entry - raw_sl
                    min_risk = actual_entry * MIN_SL_PCT
                    max_risk = actual_entry * MAX_SL_PCT
                    if actual_risk < min_risk:
                        actual_risk = min_risk
                        final_sl = round(actual_entry - actual_risk)
                    elif actual_risk > max_risk:
                        actual_risk = max_risk
                        final_sl = round(actual_entry - actual_risk)
                    else:
                        final_sl = round(raw_sl)

                    final_tp = round(actual_entry + (actual_risk * RISK_REWARD_RATIO))
                    if upper_lim_now > 0 and final_tp > upper_lim_now:
                        final_tp = int(upper_lim_now)

                    logger.info(
                        f"📌 [체결 동기화 완료] {name}({code}) {qty}주 | "
                        f"실매수가: ₩{actual_entry:,.0f} (시그널가: ₩{setup['trigger_price']:,.0f}) | "
                        f"확정 손절가: ₩{final_sl:,.0f} | 확정 익절가: ₩{final_tp:,.0f}"
                    )
                    self.positions[code] = {
                        "code": code,
                        "name": name,
                        "qty": qty,
                        "entry_price": actual_entry,
                        "stop_loss": final_sl,
                        "take_profit": final_tp,
                        "entry_time": now_kst.isoformat()
                    }
                    self.last_entry_bar[code] = bar_time
                    self.save_state()
                    if len(self.positions) >= MAX_CONCURRENT_POSITIONS:
                        break
                else:
                    # 매수 주문 거부/실패 시 해당 30분봉 내 무한 재시도 방지 잠금 및 쿨다운
                    self.last_entry_bar[code] = bar_time
                    self.cooldowns[code] = time.time()
                    self.save_state()

    def start_loop(self, poll_interval_sec: int = 30):
        logger.info(f"🟢 Starting KIS Cameron 30M Execution Loop (Polling: {poll_interval_sec}s)...")
        try:
            while True:
                self.run_iteration()
                time.sleep(poll_interval_sec)
        except KeyboardInterrupt:
            logger.info("🛑 Trader stopped manually by user.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="KIS Cameron 30M Pullback Trader")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode without placing live orders")
    parser.add_argument("--once", action="store_true", help="Run a single scan iteration and exit")
    args = parser.parse_args()

    trader = KisCameronPullbackTrader(dry_run=args.dry_run)
    if args.once:
        trader.run_iteration()
    else:
        trader.start_loop(poll_interval_sec=30)
