import numpy as np
import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df = df.sort_values("timestamp")

    close = df["close_price"]

    # Price return
    df["return_1h"] = close.pct_change()

    # Moving averages
    df["ma_5"] = close.rolling(5).mean()

    df["ma_10"] = close.rolling(10).mean()

    # Exponential moving average
    df["ema_10"] = close.ewm(
        span=10,
        adjust=False
    ).mean()

    # Volatility
    df["volatility_5"] = (
        close.pct_change()
        .rolling(5)
        .std()
    )

    # Volume change
    df["volume_change"] = (
        df["volume"].pct_change()
    )

    # Momentum
    df["momentum_5"] = (
        close - close.shift(5)
    )

    # High-low range
    df["price_range"] = (
        df["high_price"] - df["low_price"]
    )

    # RSI
    delta = close.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["rsi"] = 100 - (
        100 / (1 + rs)
    )

    # MACD
    ema_12 = close.ewm(
        span=12,
        adjust=False
    ).mean()

    ema_26 = close.ewm(
        span=26,
        adjust=False
    ).mean()

    df["macd"] = ema_12 - ema_26

    # Bollinger Bands
    rolling_mean = close.rolling(20).mean()

    rolling_std = close.rolling(20).std()

    df["bb_upper"] = (
        rolling_mean + 2 * rolling_std
    )

    df["bb_lower"] = (
        rolling_mean - 2 * rolling_std
    )

    # Target
    df["target"] = (
        close.shift(-1) > close
    ).astype(int)

    # Clean invalid values
    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    df = df.dropna()

    return df