import os

import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from ml.preprocessing.feature_engineering import create_features


# --------------------------------------------------
# ENVIRONMENT CONFIGURATION
# --------------------------------------------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set in .env"
    )


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# --------------------------------------------------
# MODEL CONFIGURATION
# --------------------------------------------------

MODEL_PATH = "ml/models/btc_direction_model.joblib"

model = joblib.load(
    MODEL_PATH
)


# --------------------------------------------------
# FEATURES
# --------------------------------------------------

FEATURES = [
    "return_1h",
    "ma_5",
    "ma_10",
    "ema_10",
    "volatility_5",
    "volume_change",
    "momentum_5",
    "price_range",
    "rsi",
    "macd",
    "bb_upper",
    "bb_lower"
]


# --------------------------------------------------
# ALERT CONFIGURATION
# --------------------------------------------------

ALERT_CONFIDENCE_THRESHOLD = 0.60


# --------------------------------------------------
# GET LATEST PREDICTION
# --------------------------------------------------

def get_latest_prediction():

    query = """
    SELECT
        timestamp,
        open_price,
        high_price,
        low_price,
        close_price,
        volume
    FROM market_data
    WHERE symbol = 'BTCUSDT'
      AND volume > 0
    ORDER BY timestamp ASC
    """

    df = pd.read_sql(
        query,
        engine
    )


    # ----------------------------------------------
    # CHECK DATA
    # ----------------------------------------------

    if len(df) < 30:

        raise ValueError(
            "Not enough market data for prediction."
        )


    # ----------------------------------------------
    # FEATURE ENGINEERING
    # ----------------------------------------------

    df = create_features(df)


    if df.empty:

        raise ValueError(
            "No valid feature data available for prediction."
        )


    # ----------------------------------------------
    # CHECK FEATURES
    # ----------------------------------------------

    missing_features = [
        feature
        for feature in FEATURES
        if feature not in df.columns
    ]


    if missing_features:

        raise ValueError(
            f"Missing features: {missing_features}"
        )


    # ----------------------------------------------
    # LATEST ROW
    # ----------------------------------------------

    latest = df[
        FEATURES
    ].iloc[-1:].copy()


    latest = latest.replace(
        [np.inf, -np.inf],
        np.nan
    )


    if latest.isnull().any().any():

        raise ValueError(
            "Latest market features contain invalid values."
        )


    # ----------------------------------------------
    # MODEL PREDICTION
    # ----------------------------------------------

    prediction_value = model.predict(
        latest
    )[0]


    probabilities = model.predict_proba(
        latest
    )[0]


    # ----------------------------------------------
    # DIRECTION
    # ----------------------------------------------

    direction = (
        "UP"
        if prediction_value == 1
        else "DOWN"
    )


    # ----------------------------------------------
    # CONFIDENCE
    # ----------------------------------------------

    confidence = float(
        max(probabilities)
    )


    # ----------------------------------------------
    # TIMESTAMP
    # ----------------------------------------------

    prediction_timestamp = (
        df["timestamp"].iloc[-1]
    )


    # ----------------------------------------------
    # ALERT LOGIC
    # ----------------------------------------------

    if confidence >= ALERT_CONFIDENCE_THRESHOLD:

        alert = True

        alert_message = (
            f"High-confidence {direction} "
            f"prediction detected."
        )

    else:

        alert = False

        alert_message = (
            "Prediction confidence is below "
            "the alert threshold."
        )


    # ----------------------------------------------
    # CHECK EXISTING PREDICTION
    # ----------------------------------------------

    check_query = text(
        """
        SELECT
            symbol,
            timestamp,
            prediction,
            confidence
        FROM predictions
        WHERE symbol = :symbol
          AND timestamp = :timestamp
        ORDER BY id DESC
        LIMIT 1
        """
    )


    with engine.connect() as connection:

        existing_prediction = connection.execute(
            check_query,
            {
                "symbol": "BTCUSDT",
                "timestamp": prediction_timestamp
            }
        ).mappings().first()


    # ----------------------------------------------
    # EXISTING PREDICTION
    # ----------------------------------------------

    if existing_prediction:

        existing_confidence = float(
            existing_prediction["confidence"]
        )


        existing_direction = (
            existing_prediction["prediction"]
        )


        if (
            existing_confidence
            >= ALERT_CONFIDENCE_THRESHOLD
        ):

            existing_alert = True

            existing_alert_message = (
                f"High-confidence "
                f"{existing_direction} "
                f"prediction detected."
            )

        else:

            existing_alert = False

            existing_alert_message = (
                "Prediction confidence is below "
                "the alert threshold."
            )


        return {

            "symbol":
                existing_prediction["symbol"],

            "prediction":
                existing_direction,

            "confidence":
                existing_confidence,

            "timestamp":
                existing_prediction[
                    "timestamp"
                ].isoformat(),

            "alert":
                existing_alert,

            "alert_message":
                existing_alert_message,

            "threshold":
                ALERT_CONFIDENCE_THRESHOLD,

            "status":
                "existing"
        }


    # ----------------------------------------------
    # INSERT NEW PREDICTION
    # ----------------------------------------------

    insert_query = text(
        """
        INSERT INTO predictions
        (
            symbol,
            timestamp,
            prediction,
            confidence
        )
        VALUES
        (
            :symbol,
            :timestamp,
            :prediction,
            :confidence
        )
        """
    )


    with engine.begin() as connection:

        connection.execute(
            insert_query,
            {
                "symbol":
                    "BTCUSDT",

                "timestamp":
                    prediction_timestamp,

                "prediction":
                    direction,

                "confidence":
                    confidence
            }
        )


    # ----------------------------------------------
    # RETURN RESULT
    # ----------------------------------------------

    return {

        "symbol":
            "BTCUSDT",

        "prediction":
            direction,

        "confidence":
            round(confidence, 4),

        "timestamp":
            prediction_timestamp.isoformat(),

        "alert":
            alert,

        "alert_message":
            alert_message,

        "threshold":
            ALERT_CONFIDENCE_THRESHOLD,

        "status":
            "new"
    }