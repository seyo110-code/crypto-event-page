"""전략 단위 테스트. 실행: trading-bot 디렉터리에서 `pytest tests`."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "user_data" / "strategies"))

from supertrend_strategy import (  # noqa: E402
    SupertrendBasic,
    SupertrendFiltered,
    SupertrendFull,
    supertrend,
)


def make_ohlcv(n: int = 600, seed: int = 0) -> pd.DataFrame:
    """상승 추세 -> 횡보 -> 하락 추세 구간을 가진 합성 1h 데이터."""
    rng = np.random.default_rng(seed)
    drift = np.concatenate([np.full(n // 3, 0.002), np.zeros(n // 3), np.full(n - 2 * (n // 3), -0.002)])
    rets = drift + rng.normal(0, 0.006, n)
    close = 100 * np.exp(np.cumsum(rets))
    open_ = np.concatenate([[close[0]], close[:-1]])
    spread = np.abs(rng.normal(0, 0.004, n)) * close
    high = np.maximum(open_, close) + spread
    low = np.minimum(open_, close) - spread
    return pd.DataFrame(
        {
            "date": pd.date_range("2025-01-01", periods=n, freq="1h", tz="UTC"),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": rng.uniform(100, 1000, n),
        }
    )


def test_supertrend_line_is_on_correct_side():
    df = make_ohlcv()
    line, direction = supertrend(df, 10, 3.0)
    warm = direction != 0
    assert warm.sum() > 500
    up = warm & (direction == 1)
    down = warm & (direction == -1)
    assert (df.loc[up, "close"] >= line[up]).all()
    assert (df.loc[down, "close"] <= line[down]).all()


def test_supertrend_follows_regimes():
    df = make_ohlcv()
    _, direction = supertrend(df, 10, 3.0)
    assert (direction.iloc[50:200] == 1).mean() > 0.8
    assert (direction.iloc[450:] == -1).mean() > 0.8


def test_long_band_only_ratchets_up_within_trend():
    df = make_ohlcv()
    line, direction = supertrend(df, 10, 3.0)
    same_up = (direction == 1) & (direction.shift(1) == 1)
    assert (line[same_up] >= line.shift(1)[same_up] - 1e-12).all()
    same_down = (direction == -1) & (direction.shift(1) == -1)
    assert (line[same_down] <= line.shift(1)[same_down] + 1e-12).all()


def run_signals(cls, htf_dir: int | None = None) -> pd.DataFrame:
    strat = cls({"candle_type_def": "futures"})
    df = make_ohlcv()
    df = strat.populate_indicators(df, {"pair": "TEST/USDT:USDT"})
    df["st_dir_4h"] = df["st_dir"] if htf_dir is None else htf_dir
    df = strat.populate_entry_trend(df, {"pair": "TEST/USDT:USDT"})
    df = strat.populate_exit_trend(df, {"pair": "TEST/USDT:USDT"})
    return df


def test_basic_enters_on_every_flip():
    df = run_signals(SupertrendBasic)
    flips_up = ((df["st_dir"] == 1) & (df["st_dir"].shift(1) == -1)).sum()
    assert df["enter_long"].fillna(0).sum() == flips_up
    assert df["exit_long"].fillna(0).sum() > 0
    # 진입 봉에서 같은 방향 청산 신호가 동시에 나지 않아야 한다
    assert not ((df["enter_long"] == 1) & (df["exit_long"] == 1)).any()


def test_at_most_one_entry_per_trend_leg():
    df = run_signals(SupertrendFiltered)
    segment = (df["st_dir"] != df["st_dir"].shift(1)).cumsum()
    entries = df["enter_long"].fillna(0) + df["enter_short"].fillna(0)
    assert entries.groupby(segment).sum().max() <= 1


def test_htf_filter_blocks_counter_trend_entries():
    df = run_signals(SupertrendFiltered, htf_dir=-1)
    assert df["enter_long"].fillna(0).sum() == 0
    assert df["enter_short"].fillna(0).sum() > 0


def test_filtered_takes_fewer_trades_than_basic():
    basic = run_signals(SupertrendBasic)
    filt = run_signals(SupertrendFiltered)
    n_basic = basic["enter_long"].fillna(0).sum() + basic["enter_short"].fillna(0).sum()
    n_filt = filt["enter_long"].fillna(0).sum() + filt["enter_short"].fillna(0).sum()
    assert n_filt <= n_basic


def test_full_strategy_flags():
    assert SupertrendFull.use_custom_stoploss
    assert SupertrendFull.position_adjustment_enable
    assert not SupertrendBasic.use_supertrend_stop
