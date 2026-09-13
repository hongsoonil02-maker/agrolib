#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
okx_major_strategy.py — OKX Major Crypto Auto Trading Engine
- Trades Top 10 Major Cryptocurrencies
- Supertrend + StochRSI logic (inherited from BaseStrategyBrain)
- 1h timeframe, leverage controlled by OKX_LEVERAGE env var
"""
import asyncio
import sys
import os
from strategy_common import BaseStrategyBrain


class OKXMajorStrategyBrain(BaseStrategyBrain):
    STRATEGY_NAME = "OKX_Major_Strategy"
    LOG_FILE = "okx_major_strategy.log"
    LOGGER_NAME = "OKX_Major_Strategy"
    STRATEGY_LEVERAGE = int(os.getenv("OKX_MAJOR_LEVERAGE", "10"))
    
    # [포트폴리오 & 리스크 튜닝 - alv*** 벤치마킹]
    PORTFOLIO_WEIGHT = 0.25      # 자본 분산 배분 (실질 레버리지 2.5배 이하로 엄격 통제)
    # [Fix] 마진 -8%/-6% 고정 스탑 제거: 실거래(08-30~09-03) 메이저 19건 0승 -161 USDT.
    # 스탑은 BaseStrategyBrain의 ATR 스탑(OKX_ATR_STOP_K)이 담당하고, HARD_STOP은 env(OKX_HARD_STOP_LOSS, 기본 -30%)
    # 최후 방어선만 유지. (서브클래스에서 -8%로 두면 ATR 스탑(예: 2%×5x = -10%)보다 먼저 발동해 ATR 스탑이 무력화됨)
    HARD_STOP_LOSS_PCT = float(os.getenv("OKX_HARD_STOP_LOSS", "-0.30"))

    # [alv*** 빅스윙 트레일링] 샹들리에 ATR 트레일링으로 대세 추세 홀딩
    # K / 가동 임계는 env(OKX_ATR_TRAIL_K / OKX_ATR_TRAIL_ARM_PNL)로 통일 (기존 하드코딩 0.20은 3x에서 사실상 미도달)
    ATR_TRAILING_ENABLED = True


    # [수익성 개선] 메이저 1h 복원: 실거래 15m에서 19건 0승(-161 USDT).
    # 메이저 코인은 추세 주기가 길어 1h가 자연스럽고, ATR 스탑 거리도 넓어져 노이즈 손절 해소.
    TIMEFRAME = "1h"
    TIMEFRAME_MINUTES = 60
    CHOP_ADX_BLOCK_THRESHOLD = 20.0  # ADX < 20 횡보장 휩쏘 진입 차단

    MAJOR_COINS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'LINK', 'DOT', 'BNB', 'TRX']

    # [Fix] 트레일링청산 플립 기본 비활성: 15m 미확정 신호 + 1h 재진입과 결합해 ADA/BNB 4회/5일 왕복 유발.
    # 확정 캔들 신호 전환 후 데이터로 재검증되면 OKX_FLIP_ON_TRAILING_CLOSE=true로 재활성.
    FLIP_ON_TRAILING_CLOSE = os.getenv("OKX_FLIP_ON_TRAILING_CLOSE", "false").lower() == "true"

    def _symbol_matches(self, symbol: str, ticker_data: dict, markets: dict) -> bool:
        if symbol not in markets or not markets[symbol].get('swap'):
            return False
        if 'USDT' not in symbol:
            return False
        base_coin = symbol.split('-')[0].split('/')[0]
        if base_coin not in self.MAJOR_COINS:
            return False
        return True


if __name__ == "__main__":
    brain = OKXMajorStrategyBrain()
    try:
        asyncio.run(brain.run_all())
    except KeyboardInterrupt:
        brain.logger.info("🛑 프로그램 종료")