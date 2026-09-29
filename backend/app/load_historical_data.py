from backend.app.database import SessionLocal
from backend.app.services.historical_data_service import (
    save_historical_klines
)


def main():

    db = SessionLocal()

    try:

        print("=" * 60)
        print("HISTORICAL BTCUSDT DATA LOADER")
        print("=" * 60)

        saved_count = save_historical_klines(
            db=db,
            symbol="BTCUSDT",
            interval="1h",
            total_candles=5000
        )

        print()
        print("=" * 60)
        print("DATA LOADING COMPLETED")
        print("=" * 60)

        print(
            f"New candles saved: {saved_count}"
        )

    except Exception as e:

        db.rollback()

        print()
        print("ERROR:")
        print(e)

    finally:

        db.close()


if __name__ == "__main__":
    main()