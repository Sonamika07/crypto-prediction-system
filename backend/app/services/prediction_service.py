import os

import joblib
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

MODEL_PATH = "ml/models/btc_direction_model.joblib"

model = joblib.load(MODEL_PATH)


def get_latest_prediction():

    query = """
    SELECT
        timestamp,
        close_price,
        volume
    FROM market_data
    WHERE symbol = 'BTCUSDT'
    ORDER BY timestamp DESC
    LIMIT 20
    """

    df = pd.read_sql(query, engine)

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

    df = df.dropna()

    features = [
        "return_1h",
        "ma_5",
        "ma_10",
        "volatility_5",
        "volume_change"
    ]

    latest = df[features].iloc[-1:]

    prediction = model.predict(latest)[0]

    probability = model.predict_proba(latest)[0]

    direction = "UP" if prediction == 1 else "DOWN"

    confidence = float(max(probability))

    return {
        "symbol": "BTCUSDT",
        "prediction": direction,
        "confidence": round(confidence, 4),
        "timestamp": df["timestamp"].iloc[-1].isoformat()
    }