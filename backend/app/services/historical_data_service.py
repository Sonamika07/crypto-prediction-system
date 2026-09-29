from datetime import datetime, timezone
from decimal import Decimal

import requests
from sqlalchemy.orm import Session

from backend.app.models.market_data import MarketData


BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"


def fetch_historical_klines(
    symbol: str = "BTCUSDT",
    interval: str = "1h",
    limit: int = 500
):
    response = requests.get(
        BINANCE_KLINES_URL,
        params={
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        },
        timeout=15
    )

    response.raise_for_status()

    return response.json()


def save_historical_klines(
    db: Session,
    symbol: str = "BTCUSDT",
    interval: str = "1h",
    limit: int = 500
):
    klines = fetch_historical_klines(
        symbol=symbol,
        interval=interval,
        limit=limit
    )

    saved_count = 0

    for candle in klines:
        open_time = datetime.fromtimestamp(
            candle[0] / 1000,
            tz=timezone.utc
        )

        market_data = MarketData(
            symbol=symbol,
            timestamp=open_time,
            open_price=Decimal(candle[1]),
            high_price=Decimal(candle[2]),
            low_price=Decimal(candle[3]),
            close_price=Decimal(candle[4]),
            volume=Decimal(candle[5])
        )

        db.add(market_data)
        saved_count += 1

    db.commit()

    return saved_count