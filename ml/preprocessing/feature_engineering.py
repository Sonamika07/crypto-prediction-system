import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df = df.sort_values("timestamp")

    df["return_1h"] = df["close_price"].pct_change()

    df["ma_5"] = df["close_price"].rolling(5).mean()

    df["ma_10"] = df["close_price"].rolling(10).mean()

    df["volatility_5"] = (
        df["close_price"]
        .pct_change()
        .rolling(5)
        .std()
    )

    df["volume_change"] = df["volume"].pct_change()

    df["target"] = (
        df["close_price"].shift(-1) > df["close_price"]
    ).astype(int)

    df = df.dropna()

    return df