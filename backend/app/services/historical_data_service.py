from datetime import datetime, timezone
from decimal import Decimal

import requests
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.app.models.market_data import MarketData


BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"


def fetch_historical_klines(
    symbol="BTCUSDT",
    interval="1h",
    limit=1000,
    start_time=None,
    end_time=None
):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    if start_time is not None:
        params["startTime"] = start_time

    if end_time is not None:
        params["endTime"] = end_time

    response = requests.get(
        BINANCE_KLINES_URL,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


def save_historical_klines(
    db: Session,
    symbol="BTCUSDT",
    interval="1h",
    total_candles=5000
):
    saved_count = 0
    requested_count = 0

    end_time = int(datetime.now(timezone.utc).timestamp() * 1000)

    while requested_count < total_candles:

        remaining = total_candles - requested_count

        batch_size = min(1000, remaining)

        print(
            f"Fetching {batch_size} candles..."
        )

        klines = fetch_historical_klines(
            symbol=symbol,
            interval=interval,
            limit=batch_size,
            end_time=end_time
        )

        if not klines:
            print("No more historical data received.")
            break

        print(
            f"Received {len(klines)} candles."
        )

        for candle in klines:

            open_time = datetime.fromtimestamp(
                candle[0] / 1000,
                tz=timezone.utc
            )

            market_data = {
                "symbol": symbol,
                "timestamp": open_time,
                "open_price": Decimal(candle[1]),
                "high_price": Decimal(candle[2]),
                "low_price": Decimal(candle[3]),
                "close_price": Decimal(candle[4]),
                "volume": Decimal(candle[5])
            }

            statement = insert(MarketData).values(
                market_data
            )

            statement = statement.on_conflict_do_nothing(
                constraint="unique_market_symbol_timestamp"
            )

            result = db.execute(statement)

            if result.rowcount == 1:
                saved_count += 1

        db.commit()

        requested_count += len(klines)

        print(
            f"Progress: {requested_count}/{total_candles} candles processed."
        )

        oldest_timestamp = klines[0][0]

        end_time = oldest_timestamp - 1

        if len(klines) < batch_size:
            print("No more historical candles available.")
            break

    return saved_count