# -*- coding: utf-8 -*-
"""
alpaca_cameron_pullback_trader.py — Ross Cameron Small-Cap Momentum Pullback Strategy
Designed for Alpaca Live/Paper Trading ($100k Account, 1-Hour Timeframe Optimized)

Strategy Core Philosophy (Ross Cameron 1-Hour First Pullback):
1. Pre-Market / Market Open Scanner:
   - Price: $2.00 ~ $50.00
   - Momentum Surge >= 3%
   - Consolidated SIP Market Feed with true volume & VWAP
2. Entry Setup (1-Hour Candle Pattern):
   - Clear morning surge (Impulse Wave: at least 2 strong bullish bars, >=2% surge)
   - First Pullback: 1~3 bearish candles
   - Pullback retracement <= 50% of the impulse leg
   - Pullback volume significantly lower than impulse volume (< 1.1x avg volume)
   - Price remains above VWAP and 9 EMA
   - Entry Trigger: Current bar breaks above the High of the previous pullback candle
   - Hard Bar-Level Lock: 1-Time entry per candle to eliminate duplicate order loops
3. Risk & Order Management:
   - Dynamic Half-Kelly Position Sizing: 16% ~ 20% of account equity per trade
   - Max 5 concurrent positions, with 80% Gross Account Exposure ceiling (0% margin safe)
   - Native Alpaca Bracket Order:
       * Stop-Loss: Swing Low (Low of the pullback candle) -> Market Stop (<= 5% SL)
       * Take-Profit: 1:3.0 Risk-to-Reward -> Limit Order
   - Hard Cutoff: No new entries after 14:30 EST
   - EOD Market Close: 15:50 ~ 15:59 EST
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
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, ".env"))

# ── LOGGING CONFIG ──
LOG_FILE = os.path.join(CURRENT_DIR, "alpaca_cameron_trader.log")
STATE_FILE = os.path.join(CURRENT_DIR, "state", "alpaca_cameron_1h_state.json")
ORDER_TAG = "cam1h"
logger = logging.getLogger("AlpacaCameronTrader")
logger.setLevel(logging.INFO)
logger.propagate = False

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=2, encoding="utf-8")
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    if sys.stdout.isatty():
        logger.addHandler(stream_handler)

# ── CREDENTIALS & SESSIONS ──
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    sys.exit("❌ ALPACA_API_KEY / ALPACA_SECRET_KEY missing in quant_system/.env")
ALPACA_REST_URL = os.getenv("ALPACA_REST_URL", "https://paper-api.alpaca.markets/v2")
ALPACA_DATA_URL = "https://data.alpaca.markets/v2"

HEADERS = {
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
    "Content-Type": "application/json"
}

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

# ── STRATEGY HYPERPARAMETERS (1-Hour Swing Holy Grail Spec) ──
TIMEFRAME = "1Hour"          # 1-Hour Timeframe (Noise & Whipsaw completely eliminated)
MIN_PRICE = 2.00
MAX_PRICE = 50.00
MIN_GAP_PCT = 3.0           # Minimum 3% momentum surge on 1H
INSTANCE_EQUITY_SHARE = 0.50 # 50% of account equity allocated to 1H instance ($47.8k / $95.6k)
MAX_PORTFOLIO_PCT = 0.20    # 20% of allocated instance equity per trade (~10% of total account)
MAX_POSITION_DOLLAR = 8000.0 # [TIER 2] Hard $8,000 cap per position to preserve book liquidity
MAX_POSITION_SHARES = 3000   # [TIER 2] Hard 3,000 share cap per position
MAX_ENTRY_SLIPPAGE_PCT = 0.008 # [TIER 1] Max 0.8% marketable limit buffer above trigger
MAX_CONCURRENT_TRADES = 4   # Max 4 concurrent positions for this instance
MAX_INSTANCE_EXPOSURE_PCT = 0.80  # Max 80% of instance equity (~40% of total account equity)
GLOBAL_ACCOUNT_EXPOSURE_PCT = 0.85 # Safety brake for entire account
RISK_REWARD_RATIO = 2.2     # 1:2.2 R:R + Active Breakeven/Trailing Profit Guard
MAX_SL_PCT = 0.07           # Max 7% stop loss distance (Relaxed from 5% to accommodate 1H candle range)
MIN_SL_PCT = 0.01           # Min 1% stop loss distance
START_HOUR_EST = 10         # Allow entries starting 10:00 EST (30 mins after market open)
START_MIN_EST = 0
CUTOFF_HOUR_EST = 15        # Allow entries until 3:00 PM EST
CUTOFF_MIN_EST = 0
COOLDOWN_SEC = 900          # 15-minute re-entry cooldown
ENTRY_GRACE_SEC = 90        # 90-second execution grace period


class AlpacaCameronPullbackTrader:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.account_equity = 100000.0
        self.watchlist: List[str] = []
        self.last_scanned_time = 0
        self.jev_gate = UniversalJevGate(confidence_threshold=0.60)
        self.own_entries: Dict[str, float] = {}
        self.cooldowns: Dict[str, float] = {}
        self.last_entry_bar: Dict[str, str] = {}  # symbol -> bar_time (Bar-Level Lock)
        self.peak_plpc: Dict[str, float] = {}     # symbol -> max unrealized_plpc for trailing stop
        
        self.load_state()
        logger.info(f"🚀 [Ross Cameron 1H Swing Engine + JEV Gate] Initializing... Dry Run: {self.dry_run}")
        logger.info(f"   REST Endpoint: {ALPACA_REST_URL}")
        
        # Startup reconciliation with live Alpaca state to prevent orphan positions
        self.sync_startup_state()

    def load_state(self):
        """Loads state with backward compatibility for legacy format"""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        if "own_entries" in saved:
                            self.own_entries = saved.get("own_entries", {})
                            self.cooldowns = saved.get("cooldowns", {})
                            self.last_entry_bar = saved.get("last_entry_bar", {})
                            self.peak_plpc = saved.get("peak_plpc", {})
                        else:
                            # Legacy flat dict format
                            self.own_entries = saved
                            self.cooldowns = {}
                            self.last_entry_bar = {}
        except Exception as e:
            logger.error(f"❌ Error loading state from {STATE_FILE}: {e}")
            self.own_entries = {}
            self.cooldowns = {}
            self.last_entry_bar = {}

    def save_state(self):
        """Persists full state safely with atomic replace"""
        try:
            tmp = STATE_FILE + ".tmp"
            payload = {
                "own_entries": self.own_entries,
                "cooldowns": self.cooldowns,
                "last_entry_bar": self.last_entry_bar,
                "peak_plpc": self.peak_plpc,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            os.replace(tmp, STATE_FILE)
        except Exception as e:
            logger.error(f"❌ State save failed: {e}")

    def sync_startup_state(self):
        """Reconciles internal state with live Alpaca orders and positions on startup"""
        try:
            orders = self.get_open_orders()
            positions = self.get_open_positions()
            now_t = time.time()

            if orders is not None:
                for o in orders:
                    cid = o.get("client_order_id", "")
                    sym = o.get("symbol", "")
                    if cid.startswith(f"{ORDER_TAG}-") and sym:
                        if sym not in self.own_entries:
                            self.own_entries[sym] = now_t
                            logger.info(f"🔄 [Startup Sync] Recovered pending order {cid} for {sym}")

            if positions is not None:
                for p in positions:
                    sym = p.get("symbol", "")
                    if sym in self.own_entries:
                        logger.info(f"🔄 [Startup Sync] Confirmed active position for {sym} ({p.get('qty')} shares)")
            
            self.save_state()
        except Exception as e:
            logger.error(f"❌ Error during startup sync: {e}")

    def get_open_orders(self) -> Optional[List[Dict[str, Any]]]:
        """Fetches active pending orders from Alpaca. Returns None on network/API failure."""
        try:
            resp = session.get(f"{ALPACA_REST_URL}/orders?status=open", headers=HEADERS, timeout=6)
            if resp.status_code == 200:
                return resp.json()
            logger.error(f"❌ Open orders API error ({resp.status_code}): {resp.text}")
        except Exception as e:
            logger.error(f"❌ Exception fetching open orders: {e}")
        return None

    def get_open_positions(self) -> Optional[List[Dict[str, Any]]]:
        """Fetches active positions from Alpaca. Returns None on network/API failure."""
        try:
            resp = session.get(f"{ALPACA_REST_URL}/positions", headers=HEADERS, timeout=6)
            if resp.status_code == 200:
                return resp.json()
            logger.error(f"❌ Open positions API error ({resp.status_code}): {resp.text}")
        except Exception as e:
            logger.error(f"❌ Exception fetching open positions: {e}")
        return None

    def get_account_summary(self) -> Optional[Dict[str, Any]]:
        """Fetches equity and buying power from Alpaca. Returns None on failure."""
        try:
            resp = session.get(f"{ALPACA_REST_URL}/account", headers=HEADERS, timeout=6)
            if resp.status_code == 200:
                acc = resp.json()
                self.account_equity = float(acc.get("equity", 100000.0))
                return {
                    "equity": self.account_equity,
                    "buying_power": float(acc.get("buying_power", 0.0)),
                    "status": acc.get("status")
                }
            logger.error(f"❌ Account API error ({resp.status_code}): {resp.text}")
        except Exception as e:
            logger.error(f"❌ Exception fetching account summary: {e}")
        return None

    def get_market_clock(self) -> Dict[str, Any]:
        """Checks if US market is open"""
        try:
            resp = session.get(f"{ALPACA_REST_URL}/clock", headers=HEADERS, timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.error(f"❌ Failed to get market clock: {e}")
        return {"is_open": False}

    def calculate_dynamic_position_size(self, setup: Dict[str, Any], trigger_price: float, buying_power: Optional[float] = None) -> int:
        """
        Dynamic Half-Kelly Position Sizing:
        - Baseline: p=0.74 (1H win rate), b=3.0 (R:R) -> Half-Kelly: 16% ~ 20%
        - Evaluated against 50% instance allocated equity ($47.8k / $95.6k)
        - Clamped to available instance budget and available buying power
        """
        vol_ratio = setup.get("vol_ratio", 1.0)
        retrace_ratio = setup.get("retrace_ratio", 40.0)

        conviction = 1.0
        if vol_ratio > 1.1:
            conviction -= 0.10
        if retrace_ratio > 45.0:
            conviction -= 0.10

        kelly_pct = max(0.16, min(MAX_PORTFOLIO_PCT, MAX_PORTFOLIO_PCT * conviction))
        instance_equity = self.account_equity * INSTANCE_EQUITY_SHARE
        target_allocation = instance_equity * kelly_pct

        # Instance budget clamp (Max 80% of 50% allocated equity = 40% of total account)
        positions = self.get_open_positions() or []
        instance_market_val = sum(abs(float(p.get("market_value", 0.0))) for p in positions if p.get("symbol") in self.own_entries)
        max_instance_budget = instance_equity * MAX_INSTANCE_EXPOSURE_PCT
        remaining_instance_budget = max(0.0, max_instance_budget - instance_market_val)
        target_allocation = min(target_allocation, remaining_instance_budget)

        if buying_power is not None and buying_power > 0:
            target_allocation = min(target_allocation, buying_power * 0.95)

        # [TIER 2: LIQUIDITY PRESERVATION CAP] Max $8,000 / Max 3,000 shares to prevent market impact
        target_allocation = min(target_allocation, MAX_POSITION_DOLLAR)
        qty = math.floor(target_allocation / trigger_price)
        qty = min(qty, MAX_POSITION_SHARES)
        logger.info(f"   📊 [Dynamic Kelly Sizing] Target: {kelly_pct*100:.1f}% (Capped ~${target_allocation:,.2f}) -> {qty} shares (Max: {MAX_POSITION_SHARES})")
        return qty

    def is_pure_common_stock(self, sym: str) -> bool:
        """
        Ross Cameron strict rule: Exclude ETF, ETP, ETN, 2X/3X Leveraged/Inverse, SPAC, Warrants, and Preferred shares.
        Trade only pure common small-cap equities.
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

        # 1. Alpaca Asset API Metadata & Exchange Check (Blocks BATS/ARCA ETFs like APLX, AXTX)
        try:
            res = session.get(f"{ALPACA_REST_URL}/assets/{sym}", headers=HEADERS, timeout=4)
            if res.status_code == 200:
                asset = res.json()
                if not asset.get("tradable", True):
                    self._asset_type_cache[sym] = False
                    return False
                name_upper = (asset.get("name") or "").upper()
                exch_upper = (asset.get("exchange") or "").upper()
                for kw in substr_keywords:
                    if kw in name_upper:
                        logger.info(f"   🚫 [ETF/ETP Filter] Excluded {sym}: '{asset.get('name')}' (keyword='{kw}')")
                        self._asset_type_cache[sym] = False
                        return False
                padded_name = f" {name_upper} "
                for kw in word_keywords:
                    if f" {kw} " in padded_name:
                        logger.info(f"   🚫 [ETF/ETP Filter] Excluded {sym}: '{asset.get('name')}' (word='{kw}')")
                        self._asset_type_cache[sym] = False
                        return False
                if exch_upper in ("BATS", "ARCA"):
                    logger.info(f"   🚫 [ETF Exchange Filter] Excluded {sym}: exchange='{exch_upper}' ({asset.get('name')})")
                    self._asset_type_cache[sym] = False
                    return False
        except Exception as e:
            logger.debug(f"Alpaca asset check failed for {sym}: {e}")

        # 2. Secondary yfinance quoteType & name check
        try:
            import yfinance as yf
            t = yf.Ticker(sym)
            info = getattr(t, "info", {}) or {}
            qtype = info.get("quoteType") or getattr(t.fast_info, "quoteType", None)
            if qtype and qtype != "EQUITY":
                logger.info(f"   🚫 [ETF/ETP Filter] Excluded {sym} (quoteType='{qtype}')")
                self._asset_type_cache[sym] = False
                return False
            yf_name = (info.get("longName") or info.get("shortName") or "").upper()
            for kw in substr_keywords:
                if kw in yf_name:
                    logger.info(f"   🚫 [ETF/ETP Filter] Excluded {sym}: yfinance name '{yf_name}'")
                    self._asset_type_cache[sym] = False
                    return False
        except Exception:
            pass

        self._asset_type_cache[sym] = True
        return True

    def scan_top_movers(self, limit: int = 25) -> List[str]:
        """
        Scans for Ross Cameron momentum runners:
        - $2.00 <= Price <= $50.00
        - Percent Change >= 3%
        - Pure Common Stocks Only (Excludes ETF, ETP, ETN)
        """
        logger.info("🔍 [Scanner] Scanning top gainers from Alpaca Screener API (Common Stocks Only)...")
        candidates = []
        try:
            resp = session.get("https://data.alpaca.markets/v1beta1/screener/stocks/movers?top=50", headers=HEADERS, timeout=6)
            if resp.status_code == 200:
                gainers = resp.json().get("gainers", [])
                for g in gainers:
                    sym = g.get("symbol", "")
                    price = float(g.get("price", 0.0))
                    pct = float(g.get("percent_change", 0.0))
                    if MIN_PRICE <= price <= MAX_PRICE and pct >= MIN_GAP_PCT:
                        if sym not in candidates and self.is_pure_common_stock(sym):
                            candidates.append(sym)
                            logger.info(f"   🎯 Scanner Match (Common Stock): {sym} | Price: ${price:.2f} | Change: +{pct:.1f}%")
        except Exception as e:
            logger.error(f"❌ Error during scanner: {e}")

        final_targets = candidates[:limit]
        logger.info(f"📋 [Watchlist Updated] Target Common Equities ({len(final_targets)}): {final_targets}")
        self.watchlist = final_targets
        return final_targets

    def fetch_bars(self, symbol: str, limit: int = 60) -> Optional[pd.DataFrame]:
        """
        Fetches consolidated SIP bars for accurate volume, VWAP, and EMA9.
        Using feed='sip' guarantees full consolidated US exchange volume.
        """
        try:
            url = f"{ALPACA_DATA_URL}/stocks/bars"
            start_iso = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
            params = {
                "symbols": symbol,
                "timeframe": TIMEFRAME,
                "start": start_iso,
                "limit": 100,
                "sort": "desc",
                "feed": "sip"  # Full US market consolidated feed (replaces 1% IEX)
            }
            resp = session.get(url, headers=HEADERS, params=params, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                raw_bars = data.get("bars", {}).get(symbol, [])
                if not raw_bars or len(raw_bars) < 15:
                    return None

                raw_bars.reverse()
                df = pd.DataFrame(raw_bars)
                df.rename(columns={
                    "t": "time", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "vw": "vwap"
                }, inplace=True)
                
                if "vwap" not in df.columns or df["vwap"].isna().all():
                    typical_price = (df["high"] + df["low"] + df["close"]) / 3
                    df["vwap"] = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum().replace(0, 1)

                df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
                return df
            else:
                logger.error(f"❌ Failed to fetch bars for {symbol} ({resp.status_code}): {resp.text}")
        except Exception as e:
            logger.error(f"❌ Error fetching bars for {symbol}: {e}")
        return None

    # Backward compatibility alias
    fetch_1min_bars = fetch_bars

    def detect_first_pullback_setup(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluates Ross Cameron First Pullback Setup:
        - 1. Impulse Wave: Lookback 3~8 bars for a strong rally (higher highs, >=2% surge).
        - 2. Pullback: 1~3 consecutive bearish candles (red bars) immediately preceding.
        - 3. Retracement: <= 50% of the impulse leg.
        - 4. Volume Drying Up: Pullback average volume < Impulse average volume * 1.1.
        - 5. Trend Support: Pullback low above VWAP and close above/touching 9 EMA.
        - 6. Trigger: Current bar price crosses above the High of the pullback candle.
        - 7. Bar Timestamp: Exported for 1-time execution lock.
        """
        if df is None or len(df) < 15 or "ema9" not in df.columns or "vwap" not in df.columns or "close" not in df.columns:
            return False, {}

        curr_bar = df.iloc[-1]
        prev_bar = df.iloc[-2]
        
        # Pullback candle: Bearish red bar OR small-body consolidation/doji (body <= 45% of range)
        prev_range = prev_bar["high"] - prev_bar["low"]
        is_bearish = prev_bar["close"] < prev_bar["open"]
        is_small_body = prev_range > 0 and (abs(prev_bar["close"] - prev_bar["open"]) / prev_range) <= 0.45
        is_pullback = is_bearish or is_small_body
        if not is_pullback:
            return False, {}

        # Check support above 9 EMA (0.98 buffer) & VWAP (0.97 buffer)
        if prev_bar["close"] < prev_bar["ema9"] * 0.98 or prev_bar["low"] < prev_bar["vwap"] * 0.97:
            return False, {}

        # Scan for impulse leg prior to pullback (2~6 bars before)
        prior_bars = df.iloc[-7:-2]
        impulse_low = prior_bars["low"].min()
        impulse_high = prior_bars["high"].max()
        impulse_surge = impulse_high - impulse_low

        if impulse_surge <= 0 or (impulse_surge / impulse_low) < 0.02:
            return False, {}  # Less than 2% surge is not an impulse wave

        # Retracement check: pullback must not erase more than 65% of surge (1H candle amplitude)
        pullback_retrace = impulse_high - prev_bar["low"]
        retrace_ratio = pullback_retrace / impulse_surge
        if retrace_ratio > 0.65:
            return False, {}  # Retraced more than 65%

        # Volume contraction: Pullback volume < average impulse volume * 1.35
        impulse_avg_vol = prior_bars["volume"].mean()
        if impulse_avg_vol > 0 and prev_bar["volume"] > impulse_avg_vol * 1.35:
            return False, {}  # Heavy selling volume on pullback

        # Liquidity Check: Ensure minimum 5,000 shares per 1H bar
        min_bar_shares = 5000
        if prev_bar["volume"] < min_bar_shares or impulse_avg_vol < min_bar_shares:
            return False, {}

        # Breakout Trigger: Current price breaks above the high of the pullback candle
        trigger_price = prev_bar["high"]
        stop_loss_price = prev_bar["low"]
        
        # Risk check
        risk_per_share = trigger_price - stop_loss_price
        if risk_per_share <= 0:
            return False, {}

        risk_pct = risk_per_share / trigger_price
        if risk_pct > MAX_SL_PCT or risk_pct < MIN_SL_PCT:
            return False, {}  # Risk outside 1% ~ 7% buffer

        target_price = trigger_price + (risk_per_share * RISK_REWARD_RATIO)

        # Trigger condition: current high >= trigger_price
        curr_close = float(curr_bar["close"])
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

    def execute_bracket_order(self, symbol: str, setup: Dict[str, Any], buying_power: Optional[float] = None) -> bool:
        """
        Executes an Alpaca Native Bracket Order:
        - Market/Marketable Limit Buy
        - Auto Take-Profit Limit
        - Auto Stop-Loss Market
        """
        trigger_price = setup["trigger_price"]
        stop_loss = setup["stop_loss"]
        take_profit = setup["target_price"]
        curr_price = setup.get("curr_price", trigger_price)
        base_ref = max(trigger_price, curr_price)

        # [TIER 3: HARD STOP-LOSS FLOOR ALIGNMENT] Stop loss must NEVER exceed MAX_SL_PCT from trigger
        hard_max_sl = round(trigger_price * (1.0 - MAX_SL_PCT), 2)
        if stop_loss < hard_max_sl:
            logger.info(f"   🛡️ [SL Clamp] Tightening stop loss from ${stop_loss:.2f} to hard ceiling ${hard_max_sl:.2f} (-{MAX_SL_PCT*100:.0f}%)")
            stop_loss = hard_max_sl

        min_tp = round(base_ref + 0.05, 2)
        if take_profit <= min_tp:
            take_profit = round(base_ref + max(setup.get("risk_per_share", 0.05) * RISK_REWARD_RATIO, 0.05), 2)

        qty = self.calculate_dynamic_position_size(setup, trigger_price, buying_power=buying_power)
        if qty <= 0:
            logger.warning(f"⚠️ [Order Skipped] Calculated quantity for {symbol} is 0.")
            return False

        # [PRE-ORDER LIVE SIP PRICE GATE] Verify real-time trade price before submitting bracket order
        try:
            rt_res = session.get(f"{ALPACA_DATA_URL}/stocks/{symbol}/trades/latest", headers=HEADERS, timeout=4)
            if rt_res.status_code == 200:
                live_px = float(rt_res.json().get("trade", {}).get("p", 0.0))
                if live_px > 0:
                    if live_px <= stop_loss * 1.010:
                        logger.warning(f"🛡️ [Pre-Order Gate Blocked] {symbol} live price (${live_px:.2f}) too close to stop (${stop_loss:.2f})")
                        self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
                        self.save_state()
                        return False
                    if live_px < trigger_price * 0.997:
                        logger.warning(f"🛡️ [Pre-Order Gate Blocked] {symbol} live price (${live_px:.2f}) fell below trigger (${trigger_price:.2f})")
                        return False
                    if live_px > trigger_price * 1.015:
                        logger.warning(f"🛡️ [Pre-Order Gate Blocked] {symbol} live price (${live_px:.2f}) chased > +1.5% above trigger (${trigger_price:.2f})")
                        self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
                        self.save_state()
                        return False
        except Exception:
            pass

        # [TIER 1: MARKETABLE LIMIT ORDER WITH SLIPPAGE CAP] Max 0.8% above breakout trigger
        limit_entry_price = round(trigger_price * (1.0 + MAX_ENTRY_SLIPPAGE_PCT), 2)

        order_payload = {
            "symbol": symbol,
            "qty": qty,
            "side": "buy",
            "type": "limit",
            "limit_price": str(limit_entry_price),
            "time_in_force": "day",
            "order_class": "bracket",
            "client_order_id": f"{ORDER_TAG}-{symbol}-{int(time.time())}",
            "take_profit": {
                "limit_price": str(take_profit)
            },
            "stop_loss": {
                "stop_price": str(stop_loss)
            }
        }

        # Jev Pre-Trade Verification (aligned with US_STOCKS prompt)
        loop = asyncio.new_event_loop()
        try:
            decision = loop.run_until_complete(
                self.jev_gate.verify_entry(
                    asset_class="US_STOCKS",
                    symbol=symbol,
                    setup_name="CAMERON_1H_PULLBACK",
                    context={
                        "surge_pct": setup.get("surge_pct", 0),
                        "gap_pct": setup.get("surge_pct", 0),
                        "vol_ratio": setup.get("vol_ratio", 1.0),
                        "rvol": setup.get("vol_ratio", 1.0),
                        "retrace_pct": setup.get("retrace_ratio", 40),
                        "price": trigger_price,
                        "sector": "SmallCap Momentum",
                        "headline": f"Ross Cameron {TIMEFRAME} Pullback Breakout above ${setup['trigger_price']:.2f}"
                    }
                )
            )
            if not decision.approved:
                logger.warning(f"🛑 [JEV VETO] {symbol} Order blocked by AI Gate! Reason: {decision.reason} (Conf: {decision.confidence:.2f})")
                self.cooldowns[symbol] = time.time() + 900  # 30-min total cooldown (15m base + 15m extra)
                self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
                self.save_state()
                return False
            logger.info(f"🛡️ [JEV APPROVED] {symbol} Entry validated by AI Gate! Reason: {decision.reason} (Conf: {decision.confidence:.2f})")
        except Exception as e:
            logger.warning(f"⚠️ Jev verification error: {e}. Proceeding with caution.")
        finally:
            loop.close()

        logger.info(f"⚡ [BRACKET ORDER TRIGGERED] {symbol}")
        logger.info(f"   Quantity: {qty} shares (~${qty * trigger_price:,.2f})")
        logger.info(f"   Trigger: ${trigger_price:.2f} | Stop: ${stop_loss:.2f} (-{setup['risk_pct']}%) | Target: ${take_profit:.2f} (+{setup['risk_pct']*RISK_REWARD_RATIO:.1f}%)")

        if self.dry_run:
            logger.info("   [Dry Run Mode] Bracket order logged without transmission.")
            self.own_entries[symbol] = time.time()
            self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
            self.save_state()
            return True

        try:
            resp = session.post(f"{ALPACA_REST_URL}/orders", headers=HEADERS, json=order_payload, timeout=8)
            if resp.status_code in [200, 201]:
                order_res = resp.json()
                logger.info(f"   ✅ [Order Accepted] Order ID: {order_res.get('id')} | Status: {order_res.get('status')}")
                self.own_entries[symbol] = time.time()
                self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
                self.save_state()
                return True
            else:
                logger.error(f"   ❌ [Order Failed] Status: {resp.status_code} | Msg: {resp.text}")
                self.last_entry_bar[symbol] = setup.get("bar_time", str(time.time()))
                self.cooldowns[symbol] = time.time()
                self.save_state()
        except Exception as e:
            logger.error(f"   ❌ Exception sending bracket order for {symbol}: {e}")

        return False

    def close_position(self, symbol: str) -> bool:
        """Closes position at market after explicitly cancelling open bracket legs to prevent held-share 403 errors"""
        try:
            logger.info(f"🚨 [Position Close] Closing position & cancelling bracket orders for {symbol}...")
            # 1. Explicitly cancel any open orders for this symbol first
            try:
                open_ords = self.get_open_orders() or []
                cancelled_any = False
                for o in open_ords:
                    if o.get("symbol") == symbol and o.get("id"):
                        session.delete(f"{ALPACA_REST_URL}/orders/{o['id']}", headers=HEADERS, timeout=5)
                        cancelled_any = True
                if cancelled_any:
                    time.sleep(0.4)
            except Exception:
                pass

            # 2. Liquidate position with cancel_orders=true (with retry if bracket leg release is slightly delayed)
            for attempt in range(2):
                resp = session.delete(f"{ALPACA_REST_URL}/positions/{symbol}?cancel_orders=true", headers=HEADERS, timeout=8)
                if resp.status_code in [200, 204]:
                    logger.info(f"   ✅ [Position Liquidated] {symbol} Market Close Success")
                    return True
                elif resp.status_code == 404:
                    logger.info(f"   ℹ️ [Position Already Closed] {symbol} not found in open positions (404)")
                    return True
                else:
                    logger.warning(f"   ⚠️ [Position Close Attempt {attempt+1}] {symbol} Status: {resp.status_code} | Msg: {resp.text}")
                    time.sleep(0.6)
        except Exception as e:
            logger.error(f"   ❌ Exception closing position for {symbol}: {e}")
        return False

    def run_iteration(self):
        """Single evaluation cycle with strict error & duplicate protection"""
        # 1. Fetch live account, positions, and orders
        acc = self.get_account_summary()
        open_positions = self.get_open_positions()
        open_orders = self.get_open_orders()

        # [CRITICAL GUARD] If API fails or times out, DO NOT touch state or entries!
        if acc is None or open_positions is None or open_orders is None:
            logger.warning("⚠️ [API Network/Timeout Guard] Failed to fetch account/positions/orders. Skipping iteration to protect state integrity.")
            return

        pos_symbols = {p["symbol"] for p in open_positions}
        pending_symbols = {o["symbol"] for o in open_orders}

        clock = self.get_market_clock()
        is_open = clock.get("is_open", False)

        now_est = datetime.now(ZoneInfo("America/New_York"))
        now_t = time.time()
        
        logger.info(f"⏰ [Heartbeat] EST: {now_est.strftime('%H:%M:%S')} | Market Open: {is_open} | Open Positions: {list(pos_symbols)} | Pending Orders: {list(pending_symbols)} | Equity: ${acc['equity']:,.2f}")

        # Scan for movers if watchlist empty or every 10 minutes
        if not self.watchlist or (now_t - self.last_scanned_time > 600):
            self.scan_top_movers(limit=25)
            self.last_scanned_time = now_t

        # Stale entry cleanup (only when API calls succeeded)
        stale = []
        for s, entry_t in list(self.own_entries.items()):
            if s not in pos_symbols and s not in pending_symbols:
                if now_t - entry_t > ENTRY_GRACE_SEC:
                    stale.append(s)

        for s in stale:
            logger.info(f"📤 [Position Closed] {s} 브래킷 청산 확인 — 추적 해제 및 {COOLDOWN_SEC//60}분 쿨다운 등록")
            del self.own_entries[s]
            self.peak_plpc.pop(s, None)
            self.cooldowns[s] = now_t
        if stale:
            self.save_state()

        own_positions = [s for s in self.own_entries if s in pos_symbols]

        # [TIER 4: ACTIVE 15-SEC EMERGENCY CIRCUIT BREAKER]
        # Inspects live unrealized PnL every cycle to prevent slippage disaster
        for p in open_positions:
            sym = p.get("symbol", "")
            if sym in self.own_entries:
                try:
                    unrealized_plpc = float(p.get("unrealized_plpc", 0.0))
                    hard_cutoff_loss = -(MAX_SL_PCT + 0.005) # -5.5% for 1H
                    peak = max(float(self.peak_plpc.get(sym, 0.0)), unrealized_plpc)
                    if peak > float(self.peak_plpc.get(sym, 0.0)):
                        self.peak_plpc[sym] = peak
                        self.save_state()

                    # [DYNAMIC TRAILING & BREAKEVEN GUARD]
                    if peak >= 0.025 and unrealized_plpc <= max(0.004, peak - 0.010):
                        logger.info(
                            f"📈 [TRAILING PROFIT LOCK] {sym} Peak: +{peak*100:.2f}% -> Current: +{unrealized_plpc*100:.2f}% "
                            f"(retraced -1.0% from peak). Closing position to lock profit!"
                        )
                        if self.close_position(sym):
                            self.own_entries.pop(sym, None)
                            self.peak_plpc.pop(sym, None)
                            self.cooldowns[sym] = now_t
                            self.save_state()
                        continue
                    elif peak >= 0.018 and unrealized_plpc <= 0.003:
                        logger.info(
                            f"🛡️ [BREAKEVEN PROFIT LOCK] {sym} Peak: +{peak*100:.2f}% -> Current: +{unrealized_plpc*100:.2f}% "
                            f"(fell to +0.30% breakeven floor). Closing position to prevent loss!"
                        )
                        if self.close_position(sym):
                            self.own_entries.pop(sym, None)
                            self.peak_plpc.pop(sym, None)
                            self.cooldowns[sym] = now_t
                            self.save_state()
                        continue

                    if unrealized_plpc <= hard_cutoff_loss:
                        logger.warning(
                            f"🚨 [EMERGENCY CIRCUIT BREAKER TRIGGERED] {sym} Live Loss: {unrealized_plpc*100:.2f}% "
                            f"breached hard floor {hard_cutoff_loss*100:.1f}%. Immediate market liquidation executed!"
                        )
                        if self.close_position(sym):
                            self.own_entries.pop(sym, None)
                            self.peak_plpc.pop(sym, None)
                            self.cooldowns[sym] = now_t
                            self.save_state()
                except Exception as e:
                    logger.error(f"❌ Error checking circuit breaker for {sym}: {e}")

        # Stale Pending Entry Order Cancellation (Cancel unfulfilled limit entry orders after 120s)
        for o in open_orders:
            cid = o.get("client_order_id", "")
            if cid.startswith(f"{ORDER_TAG}-") and o.get("side") == "buy" and o.get("status") in ["new", "accepted"]:
                submitted_at_str = o.get("submitted_at")
                if submitted_at_str:
                    try:
                        sub_dt = datetime.fromisoformat(submitted_at_str.replace("Z", "+00:00"))
                        if (datetime.now(timezone.utc) - sub_dt).total_seconds() > 120:
                            oid = o.get("id")
                            session.delete(f"{ALPACA_REST_URL}/orders/{oid}", headers=HEADERS, timeout=5)
                            logger.info(f"⏱️ [Entry Timeout] Cancelled unfilled entry order {cid} (>120s stale)")
                    except Exception:
                        pass

        # EOD Market Close: 15:50 ~ 15:59 EST 당일 보유분 일괄 종가 청산 및 대기 주문 취소
        if now_est.hour == 15 and now_est.minute >= 50:
            # 1. 미체결 대기 주문 취소
            for o in open_orders:
                cid = o.get("client_order_id", "")
                if cid.startswith(f"{ORDER_TAG}-"):
                    oid = o.get("id")
                    try:
                        session.delete(f"{ALPACA_REST_URL}/orders/{oid}", headers=HEADERS, timeout=5)
                        logger.info(f"🔔 [EOD Window] Cancelled pending entry order {cid}")
                    except Exception:
                        pass
            # 2. 보유 포지션 전량 청산
            if own_positions:
                logger.info(f"🔔 [EOD Window] 15:50 EST 도달 - 당사 보유 종목 {own_positions} 일괄 종가 청산 진행")
                for s in list(own_positions):
                    if self.close_position(s):
                        self.own_entries.pop(s, None)
                        self.cooldowns[s] = now_t
                self.save_state()
            return

        # Regular market hours check
        if not is_open:
            return

        # Start time check (Wait for first completed regular session 1H candle: 10:30 EST)
        if now_est.hour < START_HOUR_EST or (now_est.hour == START_HOUR_EST and now_est.minute < START_MIN_EST):
            logger.info(f"⏳ [Opening Candle Wait] Current time {now_est.strftime('%H:%M')} EST < Start time {START_HOUR_EST}:{START_MIN_EST:02d} EST. Waiting for first completed {TIMEFRAME} candle.")
            return

        # Cutoff time check (14:30 EST)
        if now_est.hour > CUTOFF_HOUR_EST or (now_est.hour == CUTOFF_HOUR_EST and now_est.minute >= CUTOFF_MIN_EST):
            logger.info(f"⏳ Past cutoff time ({CUTOFF_HOUR_EST}:{CUTOFF_MIN_EST:02d} EST). No new small-cap entries permitted.")
            return

        # [GLOBAL ACCOUNT RISK GUARD] 85% maximum total portfolio exposure (Margin Protection)
        total_market_val = sum(abs(float(p.get("market_value", 0.0))) for p in open_positions)
        equity = float(acc["equity"])
        global_exposure = total_market_val / equity if equity > 0 else 1.0
        if global_exposure >= GLOBAL_ACCOUNT_EXPOSURE_PCT:
            logger.info(f"⏸️ [Global Risk Guard] Total account exposure ({global_exposure*100:.1f}%) >= {GLOBAL_ACCOUNT_EXPOSURE_PCT*100:.0f}%. Margin protection active.")
            return

        # [INSTANCE EXPOSURE CEILING GUARD] 50% allocated capital ceiling ($47.8k / $95.6k)
        instance_equity = equity * INSTANCE_EQUITY_SHARE
        instance_positions = [p for p in open_positions if p.get("symbol") in self.own_entries]
        instance_market_val = sum(abs(float(p.get("market_value", 0.0))) for p in instance_positions)
        instance_exposure = instance_market_val / instance_equity if instance_equity > 0 else 1.0
        if instance_exposure >= MAX_INSTANCE_EXPOSURE_PCT:
            logger.info(f"⏸️ [Instance Risk Guard] {ORDER_TAG} exposure (${instance_market_val:,.2f} / ${instance_equity:,.2f} = {instance_exposure*100:.1f}%) >= {MAX_INSTANCE_EXPOSURE_PCT*100:.0f}%. Budget exhausted.")
            return

        # Instance position count check
        own_pending_symbols = {o["symbol"] for o in open_orders if o.get("client_order_id", "").startswith(f"{ORDER_TAG}-")}
        total_active_entries = set(own_positions).union({s for s in self.own_entries if s in own_pending_symbols})
        if len(total_active_entries) >= MAX_CONCURRENT_TRADES:
            logger.info(f"⏸️ Max concurrent positions ({len(total_active_entries)}/{MAX_CONCURRENT_TRADES}) reached. Monitoring exits...")
            return

        # Scan watchlist for First Pullback Setups (cross-instance collision proof)
        for symbol in self.watchlist:
            # 1. 계좌 전체(1H or 30M 병렬 인스턴스 포함)에서 이미 진입/보유 중인 종목 스킵
            # 2. 계좌 전체의 미체결 대기 주문 중인 종목 스킵
            # 3. 최근 청산 또는 JEV Veto 후 쿨다운 기간 내 종목 스킵
            if (symbol in pos_symbols or 
                symbol in pending_symbols or 
                (now_t - self.cooldowns.get(symbol, 0) < COOLDOWN_SEC)):
                continue

            df = self.fetch_bars(symbol, limit=40)
            if df is None:
                continue

            triggered, setup = self.detect_first_pullback_setup(df)
            if triggered:
                # [BAR-LEVEL 1-TIME LOCK GUARD] 동일 캔들 내 재진입 원천 차단
                bar_time = setup.get("bar_time")
                if self.last_entry_bar.get(symbol) == bar_time:
                    logger.info(f"⏸️ [Bar Lock] {symbol} already triggered in current {TIMEFRAME} bar ({bar_time}). Skipping duplicate.")
                    continue

                logger.info(f"🔥 [SETUP CONFIRMED] {symbol} | Bar: {bar_time} | Retrace: {setup['retrace_ratio']}% | Risk: {setup['risk_pct']}%")
                success = self.execute_bracket_order(symbol, setup, buying_power=acc.get("buying_power"))
                if success:
                    break

    def start_loop(self, poll_interval_sec: int = 15):
        """Continuous execution loop with dynamic sleep"""
        logger.info("🟢 Starting Alpaca Cameron Trader Execution Loop...")
        try:
            while True:
                self.run_iteration()
                # 장마감 시간대에는 60초 대기하여 로그 낭비 방지, 장중에는 15초 폴링
                clock = self.get_market_clock()
                sleep_sec = poll_interval_sec if clock.get("is_open", False) else 60
                time.sleep(sleep_sec)
        except KeyboardInterrupt:
            logger.info("🛑 Trader stopped manually by user.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Alpaca Ross Cameron Pullback Trader (1H)")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode without placing live orders")
    parser.add_argument("--once", action="store_true", help="Run a single scan iteration and exit")
    args = parser.parse_args()

    trader = AlpacaCameronPullbackTrader(dry_run=args.dry_run)
    if args.once:
        trader.run_iteration()
    else:
        trader.start_loop(poll_interval_sec=15)
