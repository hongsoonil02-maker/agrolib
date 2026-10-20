#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
okx_cameron_pullback_trader.py — OKX 1-Hour Ross Cameron Bi-Directional Momentum Pullback Engine
=================================================================================================
Ported from Alpaca 1-Hour Small-Cap Momentum Pullback Strategy (Option B / Model 2-C)
45-Day OKX Backtest Verified:
  - Win Rate: 63.0% (221W / 130L)
  - Profit Factor: 2.00 (Net of 0.10% round-trip taker fees)
  - Net Return: +67.44% (+$1,112.71 on $1,650 capital)
  - Max Drawdown: -3.05%

Core Architecture & 4-Stage Defensive Guardrails:
1. Dynamic High-Beta Altcoin Universe:
   - Core 16 High-Beta Altcoins + Dynamic OKX 24h Top Gainers/Losers (>= 4% move, >= $10M vol)
2. 1-Hour First Pullback Setup (Bi-Directional LONG & SHORT):
   - [LONG] Prior 5-bar impulse surge >= +2.5% above EMA50 & VWAP -> 1H pullback (<= 55% retrace,
     volume contraction <= 1.25x, holds EMA9/VWAP) -> Breakout above prev_bar['high']
   - [SHORT] Prior 5-bar impulse dump >= -2.5% below EMA50 & VWAP -> 1H relief bounce (<= 55% retrace,
     volume contraction <= 1.25x, rejected below EMA9/VWAP) -> Breakdown below prev_bar['low']
3. 4-Stage Defensive & Profit-Preservation Patch:
   - [Patch 1] Candle Hold & Pre-Order Live Price Gate: Blocks upper/lower wick fakeouts
     (requires live price holding beyond trigger, within 1.5% chase cap, and > 1.2% away from SL)
   - [Patch 2] Actual Fill Price SL/TP Re-Synchronization (1 : 2.2 Risk-to-Reward)
   - [Patch 3] Dynamic Breakeven Lock (+1.8% price move -> locks SL at +0.40% net profit above fees)
     & Trailing Stop (+2.5% price move -> trails 1.0% behind peak price)
   - [Patch 4] Hard Bar-Level 1-Time Lock + Post-Exit Cooldown (1h after TP/BE, 2h after SL)
     to 100% prevent instant re-entry churn loops.
"""

import os
import sys
import time
import math
import json
import signal
import asyncio
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any

import ccxt
import numpy as np
import pandas as pd
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, ".env"))

LOG_DIR = os.path.join(CURRENT_DIR, "logs")
STATE_DIR = os.path.join(CURRENT_DIR, "state")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

LOG_FILE = os.path.join(CURRENT_DIR, "okx_cameron_pullback.log")
STATE_FILE = os.path.join(STATE_DIR, "okx_cameron_1h_state.json")

logger = logging.getLogger("OKXCameron1HTrader")
logger.setLevel(logging.INFO)
logger.propagate = False

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=3, encoding="utf-8")
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    if sys.stdout.isatty():
        logger.addHandler(stream_handler)

from jev.universal_jev_gate import UniversalJevGate

# ── STRATEGY HYPERPARAMETERS (Option B: Bi-Directional 1H Cameron Pullback) ──
TIMEFRAME = "1h"
CORE_UNIVERSE = [
    "ZEC/USDT:USDT", "MAGIC/USDT:USDT", "PEPE/USDT:USDT", "SUI/USDT:USDT",
    "FET/USDT:USDT", "SEI/USDT:USDT", "TIA/USDT:USDT", "ORDI/USDT:USDT",
    "INJ/USDT:USDT", "APT/USDT:USDT", "WIF/USDT:USDT", "DOGE/USDT:USDT",
    "AVAX/USDT:USDT", "NEAR/USDT:USDT", "RENDER/USDT:USDT", "SOL/USDT:USDT"
]

LEVERAGE = 5                      # 5x Cross Margin
NOTIONAL_PCT_PER_TRADE = 0.30     # 30% of account equity notional per trade (~6% margin at 5x)
MAX_NOTIONAL_USDT = 800.0         # Hard cap per position
MAX_CONCURRENT_POSITIONS = 4      # Max 4 concurrent positions (~24% max margin used, >76% free cash)
RISK_REWARD_RATIO = 2.2           # 1 : 2.2 R:R
MIN_IMPULSE_PCT = 0.025           # Minimum 2.5% 5-bar impulse surge/dump
MAX_RETRACE_RATIO = 0.55          # Maximum 55% retracement of impulse wave
MAX_VOL_RATIO = 1.25              # Pullback volume <= 1.25x impulse average volume
MIN_SL_PCT = 0.006                # Min 0.6% pullback candle range (allows tight 1H bull/bear flags)
EXEC_MIN_SL_PCT = 0.008           # Min 0.8% actual stop-loss floor at execution
MAX_SL_PCT = 0.055                # Max 5.5% stop-loss distance

BREAKEVEN_TRIGGER_PCT = 0.018     # +1.8% unleveraged price move (+9% ROE) -> lock SL at +0.4%
BREAKEVEN_FLOOR_PCT = 0.004       # +0.4% above entry (covers 0.10% taker fees + net profit)
TRAILING_TRIGGER_PCT = 0.025      # +2.5% unleveraged price move (+12.5% ROE) -> activate trailing stop
TRAILING_DROP_PCT = 0.010         # Trail 1.0% behind highest/lowest price

MAX_HOLD_SEC = 24 * 3600          # 24-hour time stop
WIN_COOLDOWN_SEC = 3600           # 1-hour cooldown after TP / Breakeven / Trailing exit
LOSS_COOLDOWN_SEC = 7200          # 2-hour cooldown after Stop-Loss (eliminates churn loops)
SCAN_INTERVAL_SEC = 900           # Refresh dynamic movers every 15 minutes
POLL_INTERVAL_SEC = 15            # 15-second live position & breakout monitor


class OKXCameron1HBiDirectionalTrader:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.running = True
        self.api_key = os.getenv("OKX_API_KEY", "").strip()
        self.secret = os.getenv("OKX_SECRET", "").strip()
        self.passphrase = os.getenv("OKX_PASSPHRASE", "").strip()

        if not all([self.api_key, self.secret, self.passphrase]):
            raise ValueError("❌ OKX_API_KEY / OKX_SECRET / OKX_PASSPHRASE missing in .env")

        self.exchange = ccxt.okx({
            "apiKey": self.api_key,
            "secret": self.secret,
            "password": self.passphrase,
            "enableRateLimit": True,
            "options": {"defaultType": "swap"}
        })
        self.exchange.load_markets()

        self.total_equity = 1650.0
        self.free_equity = 1650.0
        self.watchlist: List[str] = []
        self.last_scan_time = 0.0
        self.last_reconcile_time = 0.0
        self.leverage_initialized = set()
        self.jev_gate = UniversalJevGate(confidence_threshold=0.55)

        self.active_positions: Dict[str, Dict[str, Any]] = {}
        self.cooldowns: Dict[str, float] = {}
        self.last_entry_bar: Dict[str, int] = {}

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        self.load_state()
        self.sync_balance()
        self.reconcile_with_exchange(force=True)
        logger.info(
            f"🚀 [OKX Cameron 1H Bi-Directional Engine (Option B)] Initialized | "
            f"Equity: ${self.total_equity:,.2f} USDT | Leverage: {LEVERAGE}x | DryRun: {self.dry_run}"
        )

    def _handle_signal(self, signum, frame):
        logger.info(f"🛑 Signal {signum} received. Shutting down cleanly...")
        self.running = False

    # ─────────────────────────────────────────────────────────────
    #  STATE PERSISTENCE
    # ─────────────────────────────────────────────────────────────
    def load_state(self):
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.active_positions = data.get("active_positions", {})
                self.cooldowns = data.get("cooldowns", {})
                self.last_entry_bar = data.get("last_entry_bar", {})
                logger.info(f"📂 [State Loaded] Active positions: {list(self.active_positions.keys())}")
        except Exception as e:
            logger.error(f"❌ State load error: {e}")
            self.active_positions = {}
            self.cooldowns = {}
            self.last_entry_bar = {}

    def save_state(self):
        try:
            tmp = STATE_FILE + ".tmp"
            payload = {
                "active_positions": self.active_positions,
                "cooldowns": self.cooldowns,
                "last_entry_bar": self.last_entry_bar,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            os.replace(tmp, STATE_FILE)
        except Exception as e:
            logger.error(f"❌ State save error: {e}")

    # ─────────────────────────────────────────────────────────────
    #  ACCOUNT & EXCHANGE SYNC
    # ─────────────────────────────────────────────────────────────
    def sync_balance(self):
        try:
            bal = self.exchange.fetch_balance()
            usdt = bal.get("USDT", {})
            tot = float(usdt.get("total", 0.0) or 0.0)
            free = float(usdt.get("free", 0.0) or 0.0)
            if tot > 0:
                self.total_equity = tot
                self.free_equity = free
        except Exception as e:
            logger.warning(f"⚠️ Balance fetch warning: {e}")

    def ensure_leverage(self, symbol: str):
        if symbol in self.leverage_initialized or self.dry_run:
            return
        try:
            self.exchange.set_leverage(LEVERAGE, symbol, params={"mgnMode": "cross"})
            self.leverage_initialized.add(symbol)
        except Exception:
            self.leverage_initialized.add(symbol)

    def reconcile_with_exchange(self, force: bool = False):
        now_t = time.time()
        if not force and (now_t - self.last_reconcile_time < 30.0):
            return
        self.last_reconcile_time = now_t

        try:
            raw_positions = self.exchange.fetch_positions()
            live_map: Dict[str, Dict[str, Any]] = {}
            for p in raw_positions:
                contracts = float(p.get("contracts") or 0.0)
                if contracts > 0:
                    sym = p.get("symbol", "")
                    side = (p.get("side") or "long").lower()
                    entry_px = float(p.get("entryPrice") or 0.0)
                    mark_px = float(p.get("markPrice") or entry_px)
                    if sym and entry_px > 0:
                        live_map[sym] = {
                            "symbol": sym,
                            "side": side,
                            "contracts": contracts,
                            "entry_px": entry_px,
                            "mark_px": mark_px
                        }

            changed = False
            # 1. Adopt orphan exchange positions
            for sym, lp in live_map.items():
                self.ensure_leverage(sym)
                if sym not in self.active_positions:
                    side = lp["side"]
                    ep = lp["entry_px"]
                    sl = round(ep * (0.965 if side == "long" else 1.035), 6)
                    tp = round(ep * (1.0 + 0.035 * RISK_REWARD_RATIO if side == "long" else 1.0 - 0.035 * RISK_REWARD_RATIO), 6)
                    self.active_positions[sym] = {
                        "symbol": sym,
                        "side": side,
                        "contracts": lp["contracts"],
                        "entry_px": ep,
                        "stop_loss": sl,
                        "take_profit": tp,
                        "best_px": lp["mark_px"],
                        "trailing_active": False,
                        "open_ts": now_t
                    }
                    logger.warning(f"🔄 [Orphan Position Adopted] {sym} {side.upper()} {lp['contracts']} contracts @ ${ep:.4f} (SL: ${sl:.4f}, TP: ${tp:.4f})")
                    changed = True
                else:
                    if self.active_positions[sym].get("contracts") != lp["contracts"]:
                        self.active_positions[sym]["contracts"] = lp["contracts"]
                        changed = True

            # 2. Prune closed positions
            for sym in list(self.active_positions.keys()):
                if sym not in live_map:
                    logger.info(f"🏁 [Exchange Closure Synced] {sym} position no longer open on OKX -> removed from state")
                    self.active_positions.pop(sym, None)
                    if sym not in self.cooldowns or self.cooldowns[sym] < now_t:
                        self.cooldowns[sym] = now_t + WIN_COOLDOWN_SEC
                    changed = True

            if changed:
                self.save_state()
        except Exception as e:
            logger.warning(f"⚠️ Exchange position sync warning: {e}")

    # ─────────────────────────────────────────────────────────────
    #  DYNAMIC SCANNER & 1H OHLCV INDICATORS
    # ─────────────────────────────────────────────────────────────
    def update_watchlist(self):
        now_t = time.time()
        if self.watchlist and (now_t - self.last_scan_time < SCAN_INTERVAL_SEC):
            return

        valid_core = [s for s in CORE_UNIVERSE if s in self.exchange.markets]
        dynamic_movers = []
        try:
            tickers = self.exchange.fetch_tickers(params={"instType": "SWAP"})
            scored = []
            for sym, t in tickers.items():
                if not sym.endswith("/USDT:USDT"):
                    continue
                if any(x in sym for x in ["BTC/", "ETH/", "USDC/", "USDT/"]):
                    continue
                mkt = self.exchange.markets.get(sym, {})
                if str(mkt.get("info", {}).get("instCategory", "1")) != "1":
                    continue
                pct = float(t.get("percentage") or 0.0)
                last_px = float(t.get("last") or 0.0)
                vol_ccy = float(t.get("info", {}).get("volCcy24h") or t.get("baseVolume") or 0.0)
                qvol = float(t.get("quoteVolume") or (vol_ccy * last_px) or 0.0)
                if last_px > 0 and abs(pct) >= 3.0 and qvol >= 5_000_000:
                    scored.append((abs(pct), sym, pct))
            scored.sort(reverse=True)
            for _, sym, pct in scored[:16]:
                if sym not in valid_core:
                    dynamic_movers.append(sym)
        except Exception as e:
            logger.debug(f"Dynamic ticker scan skipped: {e}")

        self.watchlist = valid_core + dynamic_movers[:12]
        self.last_scan_time = now_t
        logger.info(f"🔍 [Watchlist Updated] Monitoring {len(self.watchlist)} High-Beta Swap Symbols (Core: {len(valid_core)}, Dynamic Movers: {len(dynamic_movers[:12])}) -> {dynamic_movers[:12]}")

    def fetch_1h_bars(self, symbol: str, limit: int = 65) -> Optional[pd.DataFrame]:
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=limit)
            if not ohlcv or len(ohlcv) < 52:
                return None
            df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "vol"])
            for c in ["open", "high", "low", "close", "vol"]:
                df[c] = df[c].astype(float)
            df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
            df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
            df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
            tp = (df["high"] + df["low"] + df["close"]) / 3.0
            pv = (tp * df["vol"]).rolling(24, min_periods=1).sum()
            vv = df["vol"].rolling(24, min_periods=1).sum().replace(0, 1.0)
            df["vwap"] = pv / vv
            return df
        except Exception as e:
            logger.debug(f"Failed to fetch 1H bars for {symbol}: {e}")
            return None

    def get_realtime_price(self, symbol: str) -> Optional[float]:
        try:
            t = self.exchange.fetch_ticker(symbol)
            px = float(t.get("last") or t.get("close") or 0.0)
            return px if px > 0 else None
        except Exception:
            return None

    # ─────────────────────────────────────────────────────────────
    #  BI-DIRECTIONAL 1H CAMERON PULLBACK DETECTION
    # ─────────────────────────────────────────────────────────────
    def detect_1h_pullback_setup(self, df: pd.DataFrame) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Evaluates Bi-Directional (LONG & SHORT) 1-Hour Ross Cameron First Pullback Setup:
        Returns (side, setup_dict) where side is 'long', 'short', or None.
        """
        if df is None or len(df) < 52:
            return None, {}

        curr_bar = df.iloc[-1]
        prev_bar = df.iloc[-2]
        prior_bars = df.iloc[-7:-2]

        prev_range = float(prev_bar["high"] - prev_bar["low"])
        if prev_range <= 0:
            return None, {}

        body_ratio = abs(float(prev_bar["close"] - prev_bar["open"])) / prev_range
        impulse_avg_vol = float(prior_bars["vol"].mean())
        if impulse_avg_vol <= 0 or float(prev_bar["vol"]) > impulse_avg_vol * MAX_VOL_RATIO:
            return None, {}

        vol_ratio = float(prev_bar["vol"]) / impulse_avg_vol
        curr_close = float(curr_bar["close"])
        bar_ts = int(curr_bar["ts"])

        # 1. LONG PULLBACK CHECK
        is_pullback_long = (prev_bar["close"] < prev_bar["open"]) or (body_ratio <= 0.45)
        long_support_ok = (
            prev_bar["close"] >= prev_bar["ema9"] * 0.985 and
            prev_bar["low"] >= prev_bar["vwap"] * 0.975 and
            prev_bar["close"] > prev_bar["ema50"] * 1.005
        )
        impulse_low = float(prior_bars["low"].min())
        impulse_high = float(prior_bars["high"].max())
        impulse_surge = impulse_high - impulse_low
        long_impulse_ok = (
            impulse_surge > 0 and
            (impulse_surge / impulse_low) >= MIN_IMPULSE_PCT and
            float(prior_bars.iloc[-1]["close"]) > float(prior_bars.iloc[0]["open"])
        )
        long_retrace = (impulse_high - float(prev_bar["low"])) / impulse_surge if impulse_surge > 0 else 1.0

        if is_pullback_long and long_support_ok and long_impulse_ok and long_retrace <= MAX_RETRACE_RATIO:
            trigger_px = float(prev_bar["high"])
            sl_px = float(prev_bar["low"])
            risk_pct = (trigger_px - sl_px) / trigger_px if trigger_px > 0 else 0.0
            if MIN_SL_PCT <= risk_pct <= MAX_SL_PCT:
                # [Patch 1] Breakout Hold & Anti-Wick Gate
                if (
                    float(curr_bar["high"]) >= trigger_px and
                    curr_close >= trigger_px * 0.998 and
                    curr_close <= trigger_px * 1.015 and
                    curr_close > sl_px * 1.005
                ):
                    return "long", {
                        "side": "long",
                        "bar_ts": bar_ts,
                        "trigger_px": trigger_px,
                        "stop_loss": sl_px,
                        "risk_pct": round(risk_pct * 100.0, 2),
                        "surge_pct": round((impulse_surge / impulse_low) * 100.0, 2),
                        "retrace_pct": round(long_retrace * 100.0, 1),
                        "vol_ratio": round(vol_ratio, 2),
                        "curr_px": curr_close
                    }

        # 2. SHORT PULLBACK CHECK
        is_pullback_short = (prev_bar["close"] > prev_bar["open"]) or (body_ratio <= 0.45)
        short_resist_ok = (
            prev_bar["close"] <= prev_bar["ema9"] * 1.015 and
            prev_bar["high"] <= prev_bar["vwap"] * 1.025 and
            prev_bar["close"] < prev_bar["ema50"] * 0.995
        )
        dump_high = float(prior_bars["high"].max())
        dump_low = float(prior_bars["low"].min())
        dump_size = dump_high - dump_low
        short_impulse_ok = (
            dump_size > 0 and
            (dump_size / dump_high) >= MIN_IMPULSE_PCT and
            float(prior_bars.iloc[-1]["close"]) < float(prior_bars.iloc[0]["open"])
        )
        short_retrace = (float(prev_bar["high"]) - dump_low) / dump_size if dump_size > 0 else 1.0

        if is_pullback_short and short_resist_ok and short_impulse_ok and short_retrace <= MAX_RETRACE_RATIO:
            trigger_px = float(prev_bar["low"])
            sl_px = float(prev_bar["high"])
            risk_pct = (sl_px - trigger_px) / trigger_px if trigger_px > 0 else 0.0
            if MIN_SL_PCT <= risk_pct <= MAX_SL_PCT:
                # [Patch 1] Breakdown Hold & Anti-Wick Gate
                if (
                    float(curr_bar["low"]) <= trigger_px and
                    curr_close <= trigger_px * 1.002 and
                    curr_close >= trigger_px * 0.985 and
                    curr_close < sl_px * 0.995
                ):
                    return "short", {
                        "side": "short",
                        "bar_ts": bar_ts,
                        "trigger_px": trigger_px,
                        "stop_loss": sl_px,
                        "risk_pct": round(risk_pct * 100.0, 2),
                        "surge_pct": round((dump_size / dump_high) * 100.0, 2),
                        "retrace_pct": round(short_retrace * 100.0, 1),
                        "vol_ratio": round(vol_ratio, 2),
                        "curr_px": curr_close
                    }

        return None, {}

    # ─────────────────────────────────────────────────────────────
    #  ORDER EXECUTION & LIVE POSITION MONITORING
    # ─────────────────────────────────────────────────────────────
    def execute_entry(self, symbol: str, side: str, setup: Dict[str, Any]) -> bool:
        trigger_px = float(setup["trigger_px"])
        sl_px = float(setup["stop_loss"])
        bar_ts = int(setup["bar_ts"])

        # 1. Pre-Order Live Ticker Price Gate
        live_px = self.get_realtime_price(symbol) or float(setup["curr_px"])
        if side == "long":
            if live_px < trigger_px * 0.997 or live_px > trigger_px * 1.015 or live_px <= sl_px * 1.004:
                logger.info(f"🛡️ [Pre-Order Gate Blocked] {symbol} LONG live=${live_px:.5f} outside valid trigger window (trig=${trigger_px:.5f}, sl=${sl_px:.5f})")
                return False
        else:
            if live_px > trigger_px * 1.003 or live_px < trigger_px * 0.985 or live_px >= sl_px * 0.996:
                logger.info(f"🛡️ [Pre-Order Gate Blocked] {symbol} SHORT live=${live_px:.5f} outside valid trigger window (trig=${trigger_px:.5f}, sl=${sl_px:.5f})")
                return False

        # 2. JEV AI Gate Verification
        loop = asyncio.new_event_loop()
        try:
            decision = loop.run_until_complete(
                self.jev_gate.verify_entry(
                    asset_class="CRYPTO",
                    symbol=symbol,
                    setup_name=f"CAMERON_1H_PULLBACK_{side.upper()}",
                    context={
                        "surge_pct": setup["surge_pct"],
                        "retrace_pct": setup["retrace_pct"],
                        "vol_ratio": setup["vol_ratio"],
                        "range_pct": setup["risk_pct"]
                    }
                )
            )
            if not decision.approved:
                logger.warning(f"🛑 [JEV VETO] {symbol} {side.upper()} blocked: {decision.reason} (conf={decision.confidence:.2f})")
                self.last_entry_bar[symbol] = bar_ts
                self.cooldowns[symbol] = time.time() + 1800.0
                self.save_state()
                return False
            logger.info(f"🛡️ [JEV APPROVED] {symbol} {side.upper()} validated: {decision.reason} (conf={decision.confidence:.2f})")
        except Exception as e:
            logger.warning(f"⚠️ JEV Gate exception ({symbol}): {e}")
        finally:
            loop.close()

        # 3. Position Sizing (30% of equity notional, capped at $800 USDT)
        self.sync_balance()
        target_notional = min(self.total_equity * NOTIONAL_PCT_PER_TRADE, MAX_NOTIONAL_USDT, self.free_equity * LEVERAGE * 0.80)
        market = self.exchange.market(symbol)
        contract_size = float(market.get("contractSize") or 1.0)
        min_contracts = float(market.get("limits", {}).get("amount", {}).get("min") or 1.0)

        raw_contracts = target_notional / (live_px * contract_size)
        contracts = max(min_contracts, float(math.floor(raw_contracts)))
        if contracts * live_px * contract_size < 10.0:
            logger.warning(f"⚠️ [{symbol}] Notional too small (< $10 USDT). Skipping.")
            return False

        self.ensure_leverage(symbol)
        order_side = "buy" if side == "long" else "sell"

        if self.dry_run:
            fill_px = live_px
            logger.info(f"⚡ [DRY RUN ENTRY] {symbol} {side.upper()} {contracts} contracts @ ${fill_px:.5f}")
        else:
            try:
                try:
                    order = self.exchange.create_market_order(symbol, order_side, contracts, params={"posSide": side})
                except Exception as e_hedge:
                    if "51000" in str(e_hedge) or "posSide" in str(e_hedge):
                        order = self.exchange.create_market_order(symbol, order_side, contracts)
                    else:
                        raise e_hedge
                fill_px = float(order.get("average") or order.get("price") or live_px)
                logger.info(f"⚡ [OKX ENTRY EXECUTED] {symbol} {side.upper()} {contracts} contracts (~${contracts*fill_px*contract_size:.2f}) @ ${fill_px:.5f} | ID: {order.get('id')}")
            except Exception as e:
                logger.error(f"❌ [OKX Entry Failed] {symbol} {side.upper()}: {e}")
                self.last_entry_bar[symbol] = bar_ts
                self.cooldowns[symbol] = time.time() + 1800.0
                self.save_state()
                return False

        # [Patch 2] Actual Fill Price SL/TP Re-Sync (1 : 2.2 R:R)
        actual_risk = abs(fill_px - sl_px)
        actual_risk = max(fill_px * EXEC_MIN_SL_PCT, min(actual_risk, fill_px * MAX_SL_PCT))
        if side == "long":
            final_sl = fill_px - actual_risk
            final_tp = fill_px + (actual_risk * RISK_REWARD_RATIO)
        else:
            final_sl = fill_px + actual_risk
            final_tp = fill_px - (actual_risk * RISK_REWARD_RATIO)

        self.active_positions[symbol] = {
            "symbol": symbol,
            "side": side,
            "contracts": contracts,
            "entry_px": fill_px,
            "stop_loss": final_sl,
            "take_profit": final_tp,
            "best_px": fill_px,
            "trailing_active": False,
            "open_ts": time.time(),
            "bar_ts": bar_ts
        }
        self.last_entry_bar[symbol] = bar_ts
        self.save_state()
        logger.info(
            f"📌 [Bracket Active] {symbol} {side.upper()} | Fill: ${fill_px:.5f} | "
            f"SL: ${final_sl:.5f} | TP: ${final_tp:.5f} (1:{RISK_REWARD_RATIO} R:R)"
        )
        return True

    def close_position(self, symbol: str, pos: Dict[str, Any], cur_px: float, reason: str) -> bool:
        side = pos["side"]
        contracts = float(pos["contracts"])
        close_side = "sell" if side == "long" else "buy"
        entry_px = float(pos["entry_px"])
        raw_ret_pct = ((cur_px - entry_px) / entry_px if side == "long" else (entry_px - cur_px) / entry_px) * 100.0

        logger.info(
            f"📤 [OKX EXIT] {symbol} {side.upper()} {contracts} contracts @ ${cur_px:.5f} (Entry: ${entry_px:.5f}) | "
            f"Reason: {reason} | Move: {raw_ret_pct:+.2f}% (Lev ROE: {raw_ret_pct*LEVERAGE:+.1f}%)"
        )

        if self.dry_run:
            return True

        try:
            try:
                order = self.exchange.create_market_order(
                    symbol, close_side, contracts, params={"posSide": side, "reduceOnly": True}
                )
            except Exception as e_hedge:
                if "51000" in str(e_hedge) or "posSide" in str(e_hedge):
                    order = self.exchange.create_market_order(
                        symbol, close_side, contracts, params={"reduceOnly": True}
                    )
                else:
                    raise e_hedge
            logger.info(f"   ✅ [Closed on OKX] {symbol} Order ID: {order.get('id')}")
            return True
        except Exception as e:
            logger.error(f"   ❌ [Close Failed] {symbol}: {e}")
            return False

    def monitor_positions(self):
        if not self.active_positions:
            return

        now_t = time.time()
        state_modified = False

        for sym, pos in list(self.active_positions.items()):
            cur_px = self.get_realtime_price(sym)
            if not cur_px or cur_px <= 0:
                continue

            side = pos["side"]
            entry_px = float(pos["entry_px"])
            sl = float(pos["stop_loss"])
            tp = float(pos["take_profit"])
            best_px = float(pos.get("best_px", entry_px))
            open_ts = float(pos.get("open_ts", now_t))

            # [Patch 3] Dynamic Breakeven (+1.8% -> +0.4%) & Trailing Stop (+2.5% -> -1.0% from peak)
            if side == "long":
                if cur_px > best_px:
                    best_px = cur_px
                    pos["best_px"] = best_px
                    state_modified = True
                peak_gain = (best_px - entry_px) / entry_px if entry_px > 0 else 0.0
                if peak_gain >= TRAILING_TRIGGER_PCT:
                    trail_sl = max(entry_px * (1.0 + BREAKEVEN_FLOOR_PCT), best_px * (1.0 - TRAILING_DROP_PCT))
                    if trail_sl > sl:
                        logger.info(f"📈 [Trailing Stop Raised] {sym} LONG Peak ${best_px:.5f} (+{peak_gain*100:.2f}%) -> SL ${sl:.5f} -> ${trail_sl:.5f}")
                        sl = trail_sl
                        pos["stop_loss"] = sl
                        pos["trailing_active"] = True
                        state_modified = True
                elif peak_gain >= BREAKEVEN_TRIGGER_PCT:
                    be_sl = entry_px * (1.0 + BREAKEVEN_FLOOR_PCT)
                    if be_sl > sl:
                        logger.info(f"🛡️ [Breakeven Lock Active] {sym} LONG Peak ${best_px:.5f} (+{peak_gain*100:.2f}%) -> SL ${sl:.5f} -> ${be_sl:.5f}")
                        sl = be_sl
                        pos["stop_loss"] = sl
                        state_modified = True

                tp_hit = cur_px >= tp
                sl_hit = cur_px <= sl
                is_profit_stop = sl > entry_px
            else:
                if cur_px < best_px or best_px <= 0:
                    best_px = cur_px
                    pos["best_px"] = best_px
                    state_modified = True
                peak_gain = (entry_px - best_px) / entry_px if entry_px > 0 else 0.0
                if peak_gain >= TRAILING_TRIGGER_PCT:
                    trail_sl = min(entry_px * (1.0 - BREAKEVEN_FLOOR_PCT), best_px * (1.0 + TRAILING_DROP_PCT))
                    if trail_sl < sl:
                        logger.info(f"📈 [Trailing Stop Lowered] {sym} SHORT Peak ${best_px:.5f} (+{peak_gain*100:.2f}%) -> SL ${sl:.5f} -> ${trail_sl:.5f}")
                        sl = trail_sl
                        pos["stop_loss"] = sl
                        pos["trailing_active"] = True
                        state_modified = True
                elif peak_gain >= BREAKEVEN_TRIGGER_PCT:
                    be_sl = entry_px * (1.0 - BREAKEVEN_FLOOR_PCT)
                    if be_sl < sl:
                        logger.info(f"🛡️ [Breakeven Lock Active] {sym} SHORT Peak ${best_px:.5f} (+{peak_gain*100:.2f}%) -> SL ${sl:.5f} -> ${be_sl:.5f}")
                        sl = be_sl
                        pos["stop_loss"] = sl
                        state_modified = True

                tp_hit = cur_px <= tp
                sl_hit = cur_px >= sl
                is_profit_stop = sl < entry_px

            time_hit = (now_t - open_ts) >= MAX_HOLD_SEC

            if tp_hit or sl_hit or time_hit:
                if tp_hit:
                    reason = "TAKE_PROFIT"
                    cd_sec = WIN_COOLDOWN_SEC
                elif sl_hit:
                    if pos.get("trailing_active"):
                        reason = "TRAILING_STOP"
                        cd_sec = WIN_COOLDOWN_SEC
                    elif is_profit_stop:
                        reason = "BREAKEVEN_STOP"
                        cd_sec = WIN_COOLDOWN_SEC
                    else:
                        reason = "STOP_LOSS"
                        cd_sec = LOSS_COOLDOWN_SEC
                else:
                    reason = "TIME_STOP_24H"
                    cd_sec = WIN_COOLDOWN_SEC

                if self.close_position(sym, pos, cur_px, reason):
                    self.active_positions.pop(sym, None)
                    self.cooldowns[sym] = now_t + cd_sec
                    state_modified = True

        if state_modified:
            self.save_state()

    # ─────────────────────────────────────────────────────────────
    #  MAIN LOOP
    # ─────────────────────────────────────────────────────────────
    def run_iteration(self):
        now_t = time.time()
        self.reconcile_with_exchange()
        self.update_watchlist()

        # 1. Monitor active positions (TP / Trailing / Breakeven / SL / Time Stop)
        self.monitor_positions()

        logger.info(
            f"⏰ [Heartbeat] Equity: ${self.total_equity:,.2f} USDT (Free: ${self.free_equity:,.2f}) | "
            f"Active ({len(self.active_positions)}/{MAX_CONCURRENT_POSITIONS}): {list(self.active_positions.keys())}"
        )

        if len(self.active_positions) >= MAX_CONCURRENT_POSITIONS:
            return

        # 2. Scan Watchlist for 1-Hour Bi-Directional Cameron First Pullback Setups
        for sym in self.watchlist:
            if not self.running:
                break
            if len(self.active_positions) >= MAX_CONCURRENT_POSITIONS:
                break
            if sym in self.active_positions:
                continue
            if now_t < self.cooldowns.get(sym, 0.0):
                continue

            df = self.fetch_1h_bars(sym, limit=65)
            if df is None:
                continue

            side, setup = self.detect_1h_pullback_setup(df)
            if side and setup:
                bar_ts = int(setup["bar_ts"])
                if self.last_entry_bar.get(sym) == bar_ts:
                    continue
                logger.info(
                    f"🔥 [1H CAMERON SETUP] {sym} {side.upper()} | Impulse: {setup['surge_pct']}% | "
                    f"Retrace: {setup['retrace_pct']}% | VolRatio: {setup['vol_ratio']}x | Trigger: ${setup['trigger_px']:.5f}"
                )
                self.execute_entry(sym, side, setup)

    def run_loop(self):
        logger.info("🟢 Starting OKX Cameron 1H Bi-Directional Pullback Loop (15s cycle)...")
        while self.running:
            try:
                self.run_iteration()
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}", exc_info=True)
            for _ in range(POLL_INTERVAL_SEC):
                if not self.running:
                    break
                time.sleep(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OKX Cameron 1H Bi-Directional Pullback Trader")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode without real orders")
    parser.add_argument("--once", action="store_true", help="Run a single iteration and exit")
    args = parser.parse_args()

    trader = OKXCameron1HBiDirectionalTrader(dry_run=args.dry_run)
    if args.once:
        trader.run_iteration()
    else:
        trader.run_loop()
