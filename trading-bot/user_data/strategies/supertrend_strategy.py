"""
Supertrend 기반 Freqtrade 전략 모음.

세 가지 변형을 한 번에 백테스트해서 개선 효과를 비교할 수 있게 구성했다.

    freqtrade backtesting --strategy-list SupertrendBasic SupertrendFiltered SupertrendFull

- SupertrendBasic    : 슈퍼트렌드 방향 전환 시 진입, 반대 전환 시 청산 (가장 단순한 봇)
- SupertrendFiltered : + ADX 추세 강도 필터 + 상위 타임프레임(4h) 방향 필터
- SupertrendFull     : + 슈퍼트렌드 선 추적 손절 + 1차 부분 익절/본전 손절
                       + 손실 한도 기반 포지션 크기 + 연속 손실 보호장치

모든 판단은 "마감된 봉" 기준이다 (Freqtrade 기본 동작).
"""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd
import talib.abstract as ta
from pandas import DataFrame

from freqtrade.persistence import Order, Trade
from freqtrade.strategy import IStrategy, informative, stoploss_from_absolute


def supertrend(
    dataframe: DataFrame, period: int = 10, multiplier: float = 3.0
) -> tuple[pd.Series, pd.Series]:
    """슈퍼트렌드 선과 방향(1=상승, -1=하락)을 계산한다.

    ATR은 Wilder 방식(TA-Lib ATR)을 사용한다. TradingView 기본 Supertrend와 같은 정의.
    """
    high = dataframe["high"].to_numpy(dtype=float)
    low = dataframe["low"].to_numpy(dtype=float)
    close = dataframe["close"].to_numpy(dtype=float)
    atr = ta.ATR(dataframe, timeperiod=period).to_numpy(dtype=float)

    hl2 = (high + low) / 2.0
    basic_upper = hl2 + multiplier * atr
    basic_lower = hl2 - multiplier * atr

    n = len(close)
    upper = np.full(n, np.nan)
    lower = np.full(n, np.nan)
    line = np.full(n, np.nan)
    direction = np.zeros(n, dtype=int)

    start = int(np.argmax(~np.isnan(atr))) if np.any(~np.isnan(atr)) else n
    for i in range(start, n):
        if i == start:
            upper[i] = basic_upper[i]
            lower[i] = basic_lower[i]
            direction[i] = 1
        else:
            # 밴드는 추세 방향으로만 조여진다 (직전 종가가 밴드를 뚫었으면 리셋).
            upper[i] = (
                basic_upper[i]
                if basic_upper[i] < upper[i - 1] or close[i - 1] > upper[i - 1]
                else upper[i - 1]
            )
            lower[i] = (
                basic_lower[i]
                if basic_lower[i] > lower[i - 1] or close[i - 1] < lower[i - 1]
                else lower[i - 1]
            )
            if direction[i - 1] == 1:
                direction[i] = -1 if close[i] < lower[i] else 1
            else:
                direction[i] = 1 if close[i] > upper[i] else -1
        line[i] = lower[i] if direction[i] == 1 else upper[i]

    return (
        pd.Series(line, index=dataframe.index),
        pd.Series(direction, index=dataframe.index),
    )


class SupertrendBasic(IStrategy):
    """기준선: 슈퍼트렌드 전환 진입 / 반대 전환 청산."""

    INTERFACE_VERSION = 3

    timeframe = "1h"
    can_short = True
    process_only_new_candles = True
    startup_candle_count = 200

    # ROI 익절은 쓰지 않고 신호/손절로만 청산한다.
    minimal_roi = {"0": 100}
    # 비상용 하드 손절 (레버리지 반영된 계좌 기준 손실률).
    stoploss = -0.15
    trailing_stop = False

    # ---- 전략 설정값 (하위 클래스에서 켜고 끈다) ----
    st_period = 10
    st_multiplier = 3.0
    entry_window = 6  # 전환 후 몇 봉 안에서만 진입을 허용할지 (늦은 추격 진입 방지)

    use_adx_filter = False
    adx_period = 14
    adx_threshold = 20

    use_htf_filter = False  # 4h 슈퍼트렌드 방향과 같을 때만 진입

    use_supertrend_stop = False  # 슈퍼트렌드 선을 추적 손절선으로 사용
    use_partial_tp = False  # 1R 도달 시 절반 익절 후 본전 손절
    partial_tp_r = 1.0
    partial_tp_fraction = 0.5

    use_risk_sizing = False  # 1회 손절 시 잔고의 risk_per_trade 만큼만 잃도록 크기 계산
    risk_per_trade = 0.01

    leverage_value = 2.0

    # ------------------------------------------------------------------
    # 지표
    # ------------------------------------------------------------------
    @informative("4h")
    def populate_indicators_4h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        _, dataframe["st_dir"] = supertrend(dataframe, self.st_period, self.st_multiplier)
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["st_line"], dataframe["st_dir"] = supertrend(
            dataframe, self.st_period, self.st_multiplier
        )
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=self.adx_period)
        return dataframe

    # ------------------------------------------------------------------
    # 진입 / 청산 신호
    # ------------------------------------------------------------------
    def _filters(self, dataframe: DataFrame, side: int) -> pd.Series:
        ok = pd.Series(True, index=dataframe.index)
        if self.use_adx_filter:
            ok &= dataframe["adx"] > self.adx_threshold
        if self.use_htf_filter:
            ok &= dataframe["st_dir_4h"] == side
        return ok

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        st_dir = dataframe["st_dir"]
        # 추세 구간 번호와 구간 시작 후 경과 봉 수
        segment = (st_dir != st_dir.shift(1)).cumsum()
        bars_since_flip = dataframe.groupby(segment).cumcount()
        # 실제 "전환"으로 시작된 구간만 인정 (지표 워밍업 직후 첫 구간 제외)
        first_dir = st_dir.groupby(segment).transform("first")
        prev_dir = st_dir.shift(1).groupby(segment).transform("first")
        real_flip = (prev_dir == -first_dir) & (first_dir != 0)

        for side, col in ((1, "enter_long"), (-1, "enter_short")):
            cond = (
                real_flip
                & (st_dir == side)
                & (bars_since_flip < self.entry_window)
                & self._filters(dataframe, side)
            )
            # 추세 구간당 첫 번째로 조건이 성립한 봉에서만 진입한다.
            # (전환 봉에서 필터가 막혔더라도 entry_window 안에 풀리면 그때 진입)
            first_in_segment = cond.astype(int).groupby(segment).cumsum() == 1
            dataframe.loc[cond & first_in_segment, [col, "enter_tag"]] = (
                1,
                "st_long" if side == 1 else "st_short",
            )
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        flip_down = (dataframe["st_dir"] == -1) & (dataframe["st_dir"].shift(1) == 1)
        flip_up = (dataframe["st_dir"] == 1) & (dataframe["st_dir"].shift(1) == -1)
        dataframe.loc[flip_down, "exit_long"] = 1
        dataframe.loc[flip_up, "exit_short"] = 1
        return dataframe

    # ------------------------------------------------------------------
    # 공통 헬퍼
    # ------------------------------------------------------------------
    def _last_candle(self, pair: str) -> pd.Series | None:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe is None or dataframe.empty:
            return None
        return dataframe.iloc[-1]

    def leverage(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        return min(self.leverage_value, max_leverage)


class SupertrendFiltered(SupertrendBasic):
    """횡보장 휩쏘 감소용 필터 추가."""

    use_adx_filter = True
    use_htf_filter = True


class SupertrendFull(SupertrendFiltered):
    """필터 + 청산 개선 + 리스크 관리."""

    use_supertrend_stop = True
    use_partial_tp = True
    use_risk_sizing = True

    use_custom_stoploss = True
    position_adjustment_enable = True
    max_entry_position_adjustment = 0  # 물타기/불타기 없음, 부분 청산만 사용

    @property
    def protections(self):
        return [
            # 손절 직후 같은 종목 재진입 대기
            {"method": "CooldownPeriod", "stop_duration_candles": 2},
            # 24시간 안에 손절 3번이면 해당 종목 12시간 쉬기
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 24,
                "trade_limit": 3,
                "stop_duration_candles": 12,
                "only_per_pair": True,
            },
            # 최근 48시간 낙폭이 15%를 넘으면 전체 24시간 정지
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 48,
                "trade_limit": 5,
                "stop_duration_candles": 24,
                "max_allowed_drawdown": 0.15,
            },
        ]

    # 진입 체결 시 최초 손절선(=슈퍼트렌드 선)을 기록 -> R 단위 계산에 사용
    def order_filled(
        self, pair: str, trade: Trade, order: Order, current_time: datetime, **kwargs
    ) -> None:
        if order.ft_order_side == trade.entry_side and trade.nr_of_successful_entries == 1:
            candle = self._last_candle(pair)
            if candle is not None and not np.isnan(candle["st_line"]):
                trade.set_custom_data("init_stop", float(candle["st_line"]))

    def custom_stake_amount(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        if not self.use_risk_sizing:
            return proposed_stake
        candle = self._last_candle(pair)
        if candle is None or np.isnan(candle["st_line"]) or current_rate <= 0:
            return proposed_stake
        stop_pct = abs(current_rate - candle["st_line"]) / current_rate
        if stop_pct < 0.002:  # 손절폭이 비정상적으로 좁으면 크기를 키우지 않는다
            return proposed_stake
        balance = self.wallets.get_total_stake_amount()
        notional = balance * self.risk_per_trade / stop_pct
        stake = notional / leverage
        stake = min(stake, max_stake)
        if min_stake is not None and stake < min_stake:
            return 0  # 최소 주문 금액 미만이면 진입 생략
        return stake

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs,
    ) -> float | None:
        if not self.use_supertrend_stop:
            return None
        candle = self._last_candle(pair)
        if candle is None or np.isnan(candle["st_line"]):
            return None
        side = -1 if trade.is_short else 1
        if candle["st_dir"] != side:
            return None  # 방향이 뒤집혔으면 exit 신호가 처리한다
        stop = float(candle["st_line"])
        if self.use_partial_tp and trade.nr_of_successful_exits >= 1:
            # 1차 익절 후에는 최소 본전에 손절
            stop = max(stop, trade.open_rate) if side == 1 else min(stop, trade.open_rate)
        return stoploss_from_absolute(
            stop, current_rate, is_short=trade.is_short, leverage=trade.leverage
        )

    def adjust_trade_position(
        self,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        min_stake: float | None,
        max_stake: float,
        current_entry_rate: float,
        current_exit_rate: float,
        current_entry_profit: float,
        current_exit_profit: float,
        **kwargs,
    ) -> float | None | tuple[float | None, str | None]:
        if not self.use_partial_tp or trade.has_open_orders:
            return None
        if trade.nr_of_successful_exits >= 1:
            return None
        init_stop = trade.get_custom_data("init_stop")
        if init_stop is None:
            return None
        risk = abs(trade.open_rate - init_stop)
        if risk <= 0:
            return None
        if trade.is_short:
            hit = current_exit_rate <= trade.open_rate - self.partial_tp_r * risk
        else:
            hit = current_exit_rate >= trade.open_rate + self.partial_tp_r * risk
        if not hit:
            return None
        amount = trade.stake_amount * self.partial_tp_fraction
        if min_stake is not None and (
            amount < min_stake or trade.stake_amount - amount < min_stake
        ):
            return None
        return -amount, "tp1"
