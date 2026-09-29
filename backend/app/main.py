from fastapi import FastAPI

from backend.app.services.prediction_service import get_latest_prediction


app = FastAPI(
    title="Crypto Prediction API",
    description="Real-time BTCUSDT market prediction API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Crypto Prediction API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/prediction")
def prediction():
    return get_latest_prediction()