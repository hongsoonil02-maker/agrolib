#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_fj_comparison_backtest.py — 현재 봇 vs FJ Investment 카피봇 비교 백테스트

5가지 전략을 동일 데이터(90일, 15m)에서 시뮬레이션:
  A. 현재 봇 (개선 전): DCA 8회, 10x, 15 포지션, Time Stop 없음
  B. 현재 봇 (개선 후): DCA 0, 3x, 5 포지션, Time Stop 48h
  C. FJ 스타일 (추세추종): 정찰병→불타기, 칼손절 5%, 3x
  D. FJ리스크 + 현재지표: 현재 봇의 지표 + FJ 리스크관리
  E. 최적 하이브리드: D + Time Stop + ADX 필터
"""
import asyncio
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import ccxt.async_support as ccxt_async

INITIAL_EQUITY = 3250.0
FEE_RATE = 0.0005

SYMBOLS = [
    "BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT",
    "BNB/USDT:USDT", "XRP/USDT:USDT", "ADA/USDT:USDT",
    "DOGE/USDT:USDT", "HYPE/USDT:USDT", "LINK/USDT:USDT",
    "AVAX/USDT:USDT", "ENA/USDT:USDT", "PEPE/USDT:USDT",
    "WIF/USDT:USDT", "SUI/USDT:USDT", "ZEC/USDT:USDT",
]


def calc_supertrend(df, period=10, multiplier=3.0):
    hl2 = (df['h'] + df['l']) / 2
    h, l, c = df['h'], df['l'], df['c']
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False).mean()
    fu = hl2 + multiplier * atr
    fl = hl2 - multiplier * atr
    sd = pd.Series(1, index=df.index, dtype='int')
    for i in range(period, len(df)):
        if c.iloc[i] > fu.iloc[i - 1]:
            sd.iloc[i] = 1
        elif c.iloc[i] < fl.iloc[i - 1]:
            sd.iloc[i] = -1
        else:
            sd.iloc[i] = sd.iloc[i - 1]
            if sd.iloc[i] == 1 and fl.iloc[i] < fl.iloc[i - 1]:
                fl.iloc[i] = fl.iloc[i - 1]
            if sd.iloc[i] == -1 and fu.iloc[i] > fu.iloc[i - 1]:
                fu.iloc[i] = fu.iloc[i - 1]
    return sd, atr


def calc_stoch_k(series, period=14, smooth=3):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    stoch = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    return stoch.rolling(smooth).mean() * 100


def calc_adx(df, period=14):
    h, l, c = df['h'], df['l'], df['c']
    up, down = h.diff(), -l.diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / period, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1.0 / period, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1.0 / period, adjust=False).mean() / atr
    denom = (plus_di + minus_di).where((plus_di + minus_di) != 0)
    dx = 100 * (plus_di - minus_di).abs() / denom
    return dx.ewm(alpha=1.0 / period, adjust=False).mean().fillna(0.0)


async def fetch_all(ex, sym, tf, since_ms):
    out = []
    since = since_ms
    for _ in range(50):
        try:
            batch = await ex.fetch_ohlcv(sym, tf, since=since, limit=300)
        except Exception:
            break
        if not batch:
            break
        out.extend(batch)
        if len(batch) < 300:
            break
        since = batch[-1][0] + 1
        await asyncio.sleep(0.05)
    df = pd.DataFrame(out, columns=['t', 'o', 'h', 'l', 'c', 'v']).drop_duplicates('t')
    return df.sort_values('t').reset_index(drop=True)


class Strategy:
    def __init__(self, name, leverage, max_pos, max_dca, hard_stop_pct,
                 soft_stop_pct, time_stop_hours, pyramiding,
                 pyramid_trigger_pct, pyramid_ratio,
                 entry_threshold, short_allowed, adx_filter, adx_min,
                 trailing_arm_pct, trailing_k):
        self.name = name
        self.leverage = leverage
        self.max_pos = max_pos
        self.max_dca = max_dca
        self.hard_stop_pct = hard_stop_pct
        self.soft_stop_pct = soft_stop_pct
        self.time_stop_hours = time_stop_hours
        self.pyramiding = pyramiding
        self.pyramid_trigger_pct = pyramid_trigger_pct
        self.pyramid_ratio = pyramid_ratio
        self.entry_threshold = entry_threshold
        self.short_allowed = short_allowed
        self.adx_filter = adx_filter
        self.adx_min = adx_min
        self.trailing_arm_pct = trailing_arm_pct
        self.trailing_k = trailing_k


def simulate(data, btc_df, strat):
    cash = INITIAL_EQUITY
    peak_equity = INITIAL_EQUITY
    max_dd = 0.0
    positions = {}
    trades = []

    all_ts = sorted(set().union(*[set(df['t']) for df in data.values()]))
    warmup = 100

    for idx, t in enumerate(all_ts):
        if idx < warmup:
            continue

        btc_adx = 25.0
        if strat.adx_filter and btc_df is not None:
            brows = btc_df.index[btc_df['t'] == t]
            if len(brows) > 0:
                btc_adx = float(btc_df['adx'].iloc[brows[0]])

        for sym, df in data.items():
            rows = df.index[df['t'] == t]
            if len(rows) == 0:
                continue
            i = rows[0]
            if i < 2:
                continue
            curr, prev = df.iloc[i], df.iloc[i - 1]
            px = float(curr['c'])
            atr_val = float(curr['atr']) if 'atr' in curr.index else 0.0

            plist = positions.get(sym, [])
            remaining = []
            for p in plist:
                p['last_px'] = px
                pnl_pct = (px - p['entry']) / p['entry'] * strat.leverage * p['dir']
                p['extreme'] = max(p.get('extreme', 0), pnl_pct)
                best = p['extreme']
                hours_held = (t - p['entry_t']) / (3600 * 1000)
                exit_now = False

                if pnl_pct <= strat.hard_stop_pct:
                    exit_now = True
                elif strat.soft_stop_pct != 0 and pnl_pct <= strat.soft_stop_pct:
                    exit_now = True
                elif strat.trailing_k > 0 and best >= strat.trailing_arm_pct:
                    if p['dir'] == 1:
                        highest = max(p.get('highest', p['entry']), float(curr['h']))
                        p['highest'] = highest
                        trail_line = highest - strat.trailing_k * (p.get('entry_atr', atr_val) or atr_val)
                        if px < trail_line:
                            exit_now = True
                    else:
                        lowest = min(p.get('lowest', p['entry']), float(curr['l']))
                        p['lowest'] = lowest
                        trail_line = lowest + strat.trailing_k * (p.get('entry_atr', atr_val) or atr_val)
                        if px > trail_line:
                            exit_now = True
                if not exit_now:
                    if best >= 0.50 and pnl_pct <= best * 0.6:
                        exit_now = True
                    elif best >= 0.20 and pnl_pct <= 0.05:
                        exit_now = True
                if not exit_now and strat.time_stop_hours > 0:
                    if hours_held >= strat.time_stop_hours and pnl_pct <= 0.02:
                        exit_now = True
                if not exit_now and pnl_pct >= 0.80:
                    exit_now = True

                if exit_now:
                    gross = p['margin'] * pnl_pct
                    fee = p['margin'] * strat.leverage * FEE_RATE * 2
                    net = gross - fee
                    cash += p['margin'] + net
                    trades.append({'pnl': net, 'margin': p['margin']})
                else:
                    remaining.append(p)
            positions[sym] = remaining

            if strat.pyramiding and remaining:
                for p in remaining:
                    pnl_pct = (px - p['entry']) / p['entry'] * strat.leverage * p['dir']
                    if pnl_pct >= strat.pyramid_trigger_pct and not p.get('pyramided'):
                        pyr_margin = p['margin'] * strat.pyramid_ratio
                        if pyr_margin >= 30 and pyr_margin <= cash * 0.5:
                            fee = pyr_margin * strat.leverage * FEE_RATE
                            cash -= pyr_margin + fee
                            remaining.append({
                                'entry': px, 'margin': pyr_margin, 'dir': p['dir'],
                                'extreme': 0.0, 'last_px': px, 'entry_t': t,
                                'entry_atr': atr_val, 'pyramided': True,
                            })
                            p['pyramided'] = True
                            break

            if remaining:
                continue
            if strat.adx_filter and btc_adx < strat.adx_min:
                continue
            active_syms = set(s for s, pl in positions.items() if pl)
            if len(active_syms) >= strat.max_pos:
                continue

            long_score = 0
            ema50 = float(curr.get('ema50', 0))
            if px > ema50 > 0: long_score += 50
            if prev['st_dir'] == -1 and curr['st_dir'] == 1: long_score += 40
            if curr['st_dir'] == 1 and prev['stoch_k'] < 20 and curr['stoch_k'] >= 20: long_score += 30
            if curr['st_dir'] == 1 and prev['st_dir'] == 1: long_score += 20
            if 20 < curr['stoch_k'] < 80: long_score += 20

            short_score = 0
            if strat.short_allowed:
                if px < ema50 and ema50 > 0: short_score += 50
                if prev['st_dir'] == 1 and curr['st_dir'] == -1: short_score += 40
                if curr['st_dir'] == -1 and prev['stoch_k'] > 80 and curr['stoch_k'] <= 80: short_score += 30
                if curr['st_dir'] == -1 and prev['st_dir'] == -1: short_score += 20
                if 20 < curr['stoch_k'] < 80: short_score += 20

            entry_dir = 0
            if long_score >= strat.entry_threshold: entry_dir = 1
            elif short_score >= strat.entry_threshold + 20 and strat.short_allowed: entry_dir = -1
            if entry_dir == 0: continue

            equity = cash
            for s, pl in positions.items():
                for p in pl:
                    pnl = (p['last_px'] - p['entry']) / p['entry'] * strat.leverage * p['dir']
                    equity += p['margin'] * (1 + pnl)
            margin = (equity / strat.max_pos) * 0.5
            if margin < 30 or margin > cash * 0.95: continue

            fee = margin * strat.leverage * FEE_RATE
            cash -= margin + fee
            positions[sym] = [{'entry': px, 'margin': margin, 'dir': entry_dir,
                               'extreme': 0.0, 'last_px': px, 'entry_t': t, 'entry_atr': atr_val}]

        equity = cash
        for s, pl in positions.items():
            for p in pl:
                pnl = (p['last_px'] - p['entry']) / p['entry'] * strat.leverage * p['dir']
                equity += p['margin'] * (1 + pnl)
        if equity > peak_equity: peak_equity = equity
        dd = (equity - peak_equity) / peak_equity
        if dd < max_dd: max_dd = dd

    equity = cash
    for s, pl in positions.items():
        for p in pl:
            pnl = (p['last_px'] - p['entry']) / p['entry'] * strat.leverage * p['dir']
            net = p['margin'] * pnl - p['margin'] * strat.leverage * FEE_RATE * 2
            equity += p['margin'] + net
            trades.append({'pnl': net, 'margin': p['margin']})

    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    wr = len(wins) / len(trades) * 100 if trades else 0
    aw = np.mean([t['pnl'] for t in wins]) if wins else 0
    al = abs(np.mean([t['pnl'] for t in losses])) if losses else 1
    roi = (equity - INITIAL_EQUITY) / INITIAL_EQUITY * 100
    return {'equity': equity, 'roi_pct': roi, 'mdd_pct': max_dd * 100,
            'trades': len(trades), 'win_rate': wr, 'pl_ratio': aw / al if al else 0,
            'avg_win': aw, 'avg_loss': -(abs(np.mean([t['pnl'] for t in losses])) if losses else 0)}


async def main():
    ex = ccxt_async.okx({"enableRateLimit": True, "options": {"defaultType": "swap"}})
    since = int(datetime(2026, 6, 15, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
    try:
        print("=" * 100)
        print("📊 현재 봇 vs FJ Investment 카피봇 비교 백테스트")
        print(f"   기간: 2026-06-15 ~ 현재 (~90일) | 시드: ${INITIAL_EQUITY:,.0f} | 심볼: {len(SYMBOLS)}개")
        print("=" * 100)
        print("\n🔄 데이터 수집 중...")
        data = {}
        for sym in SYMBOLS:
            try:
                df = await fetch_all(ex, sym, "15m", since)
                if len(df) >= 200:
                    df['st_dir'], df['atr'] = calc_supertrend(df)
                    df['stoch_k'] = calc_stoch_k(df['c'])
                    df['ema50'] = df['c'].ewm(span=50, adjust=False).mean()
                    df['adx'] = calc_adx(df)
                    df = df.dropna().reset_index(drop=True)
                    data[sym] = df
                    print(f"  ✅ {sym}: {len(df)} candles")
            except Exception as e:
                print(f"  ❌ {sym}: {e}")
        print(f"\n📦 {len(data)}개 심볼 수집 완료\n")
        btc_df = data.get("BTC/USDT:USDT")

        strategies = [
            Strategy("A. 개선 전 (기존 봇)", 10, 15, 8, -0.30, -0.12, 0, False, 0.4, 0.35, 70, True, False, 15, 0.20, 2.5),
            Strategy("B. 개선 후 (현재 봇)", 3, 5, 0, -0.20, -0.12, 48, False, 0.4, 0.35, 70, True, True, 15, 0.06, 3.0),
            Strategy("C. FJ 스타일 (추세추종)", 3, 5, 0, -0.05, 0, 72, True, 0.15, 0.50, 90, False, True, 20, 0.06, 2.0),
            Strategy("D. FJ리스크+현재지표", 3, 5, 0, -0.05, 0, 48, True, 0.20, 0.50, 70, True, True, 15, 0.06, 2.5),
            Strategy("E. 최적 하이브리드", 3, 5, 0, -0.08, 0, 48, True, 0.15, 0.50, 80, True, True, 18, 0.06, 2.5),
        ]

        print("=" * 115)
        print(f"{'전략':30s} {'최종자산':>10s} {'수익률':>8s} {'MDD':>8s} {'거래수':>6s} {'승률':>7s} {'손익비':>7s} {'평균수익':>10s} {'평균손실':>10s}")
        print("-" * 115)
        results = []
        for strat in strategies:
            r = simulate(data, btc_df, strat)
            results.append((strat.name, r))
            print(f"  {strat.name:28s} ${r['equity']:>8,.0f} {r['roi_pct']:>+7.1f}% {r['mdd_pct']:>+7.1f}% {r['trades']:>5d} {r['win_rate']:>6.1f}% {r['pl_ratio']:>6.2f}x ${r['avg_win']:>+8.1f} ${r['avg_loss']:>+8.1f}")
        print("=" * 115)

        print("\n📋 전략 파라미터 비교")
        print("-" * 95)
        print(f"{'전략':30s} {'레버':>4s} {'포지션':>6s} {'DCA':>4s} {'손절':>6s} {'시간손절':>8s} {'불타기':>6s} {'진입점수':>8s} {'ADX':>4s}")
        print("-" * 95)
        for strat in strategies:
            print(f"  {strat.name:28s} {strat.leverage:>3d}x {strat.max_pos:>5d} {strat.max_dca:>3d} {strat.hard_stop_pct*100:>+5.0f}% {'OFF' if strat.time_stop_hours == 0 else f'{strat.time_stop_hours:.0f}h':>7s} {'ON' if strat.pyramiding else 'OFF':>5s} {strat.entry_threshold:>7d} {'ON' if strat.adx_filter else 'OFF':>3s}")

        print("\n" + "=" * 80)
        best = max(results, key=lambda x: x[1]['roi_pct'] / max(abs(x[1]['mdd_pct']), 1))
        print(f"🏆 최적 리스크 대비 수익 전략: {best[0]}")
        print(f"   수익률: {best[1]['roi_pct']:+.1f}% | MDD: {best[1]['mdd_pct']:+.1f}% | 승률: {best[1]['win_rate']:.1f}% | 손익비: {best[1]['pl_ratio']:.2f}x")
        print("=" * 80)
    finally:
        await ex.close()

if __name__ == "__main__":
    asyncio.run(main())
