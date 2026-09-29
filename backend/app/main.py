import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text

from backend.app.services.prediction_service import (
    get_latest_prediction
)


# ==================================================
# ENVIRONMENT CONFIGURATION
# ==================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set in .env"
    )


# ==================================================
# DATABASE CONNECTION
# ==================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="Crypto Prediction API",
    description=(
        "Real-time BTCUSDT market prediction API"
    ),
    version="1.0.0"
)


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message":
            "Crypto Prediction API is running"
    }


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ==================================================
# LATEST PREDICTION
# ==================================================

@app.get("/prediction")
def prediction():

    return get_latest_prediction()


# ==================================================
# MARKET DATA
# ==================================================

@app.get("/market-data")
def market_data(
    limit: int = 100
):

    # Safety limit

    if limit < 1:

        limit = 1

    if limit > 1000:

        limit = 1000


    query = text(
        """
        SELECT
            timestamp,
            open_price,
            high_price,
            low_price,
            close_price,
            volume
        FROM market_data
        WHERE symbol = 'BTCUSDT'
        ORDER BY timestamp DESC
        LIMIT :limit
        """
    )


    with engine.connect() as connection:

        rows = connection.execute(
            query,
            {
                "limit": limit
            }
        ).mappings().all()


    return list(
        reversed(rows)
    )


# ==================================================
# PREDICTION HISTORY
# ==================================================

@app.get("/prediction-history")
def prediction_history(
    limit: int = 50
):

    # Safety limit

    if limit < 1:

        limit = 1

    if limit > 500:

        limit = 500


    query = text(
        """
        SELECT
            timestamp,
            symbol,
            prediction,
            confidence
        FROM predictions
        ORDER BY timestamp DESC
        LIMIT :limit
        """
    )


    with engine.connect() as connection:

        rows = connection.execute(
            query,
            {
                "limit": limit
            }
        ).mappings().all()


    return list(rows)


# ==================================================
# MODEL METRICS
# ==================================================

@app.get("/model-metrics")
def model_metrics():

    """
    Returns historical ML validation metrics.

    These values describe the current model
    evaluation results and are NOT live
    trading performance or profit guarantees.
    """

    metrics = {

        "model":
            "Random Forest",

        "symbol":
            "BTCUSDT",

        "test_accuracy":
            0.5105,

        "test_accuracy_percent":
            51.05,

        "walk_forward_average":
            0.5250,

        "walk_forward_average_percent":
            52.50,

        "highest_walk_forward_fold":
            0.5620,

        "highest_walk_forward_fold_percent":
            56.20,

        "lowest_walk_forward_fold":
            0.5000,

        "lowest_walk_forward_fold_percent":
            50.00,

        "walk_forward_folds":
            4,

        "evaluation_type":
            "Historical validation",

        "note":
            (
                "Historical validation metrics only. "
                "They do not guarantee future performance "
                "or trading profit."
            )
    }


    return metrics