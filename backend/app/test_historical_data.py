from backend.app.database import SessionLocal
from backend.app.services.historical_data_service import save_historical_klines


def main():
    db = SessionLocal()

    try:
        count = save_historical_klines(
            db=db,
            symbol="BTCUSDT",
            interval="1h",
            limit=500
        )

        print("HISTORICAL DATA SAVED SUCCESSFULLY")
        print("Rows inserted:", count)

    finally:
        db.close()


if __name__ == "__main__":
    main()
    