from datetime import datetime, timezone
from decimal import Decimal

import requests
from sqlalchemy.orm import Session

from backend.app.models.market_data import MarketData


BINANCE_PRICE_URL = "https://api.binance.com/api/v3/ticker/price"


def fetch_current_price(symbol: str = "BTCUSDT") -> Decimal:
    response = requests.get(
        BINANCE_PRICE_URL,
        params={"symbol": symbol},
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return Decimal(data["price"])


def save_current_price(db: Session, symbol: str = "BTCUSDT"):
    price = fetch_current_price(symbol)

    market_data = MarketData(
        symbol=symbol,
        timestamp=datetime.now(timezone.utc),
        open_price=price,
        high_price=price,
        low_price=price,
        close_price=price,
        volume=Decimal("0")
    )

    db.add(market_data)
    db.commit()
    db.refresh(market_data)

    return market_data
