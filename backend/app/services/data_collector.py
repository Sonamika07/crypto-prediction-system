import time
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert

from backend.app.database import SessionLocal
from backend.app.models.market_data import MarketData
from backend.app.services.historical_data_service import (
    fetch_historical_klines
)
from backend.app.services.prediction_service import (
    get_latest_prediction
)


SYMBOL = "BTCUSDT"
INTERVAL = "1h"

# Check every 5 minutes.
# Binance data itself is hourly.
CHECK_INTERVAL = 300


def collect_latest_closed_candle():

    db = SessionLocal()

    try:

        # Get latest 2 hourly candles.
        # The second-last candle is the latest CLOSED candle.
        klines = fetch_historical_klines(
            symbol=SYMBOL,
            interval=INTERVAL,
            limit=2
        )

        if len(klines) < 2:

            print(
                "Not enough candle data received."
            )

            return


        candle = klines[-2]


        market_data = {
            "symbol": SYMBOL,

            "timestamp": datetime.fromtimestamp(
                candle[0] / 1000,
                tz=timezone.utc
            ),

            "open_price": candle[1],
            "high_price": candle[2],
            "low_price": candle[3],
            "close_price": candle[4],
            "volume": candle[5]
        }


        # Insert candle only if it does not already exist.
        statement = insert(
            MarketData
        ).values(
            market_data
        )


        statement = statement.on_conflict_do_nothing(
            constraint="unique_market_symbol_timestamp"
        )


        result = db.execute(
            statement
        )

        db.commit()


        if result.rowcount == 1:

            print()
            print(
                "NEW CLOSED BTCUSDT CANDLE SAVED"
            )

            print(
                "Timestamp:",
                market_data["timestamp"]
            )

            print(
                "Close price:",
                market_data["close_price"]
            )


            # Generate prediction for the new candle.
            try:

                prediction = get_latest_prediction()

                print()
                print(
                    "NEW PREDICTION"
                )

                print(
                    prediction
                )

            except Exception as prediction_error:

                print(
                    "Prediction error:",
                    prediction_error
                )


        else:

            print(
                "Candle already exists. "
                "No new prediction required."
            )


    except Exception as error:

        db.rollback()

        print(
            "Data collection error:",
            error
        )


    finally:

        db.close()


def collect_data():

    print("=" * 60)
    print("BTCUSDT AUTOMATIC DATA COLLECTOR")
    print("=" * 60)

    print(
        f"Checking every {CHECK_INTERVAL // 60} minutes..."
    )


    while True:

        collect_latest_closed_candle()

        print()
        print(
            f"Waiting {CHECK_INTERVAL // 60} minutes "
            "for next check..."
        )

        time.sleep(
            CHECK_INTERVAL
        )


if __name__ == "__main__":

    collect_data()