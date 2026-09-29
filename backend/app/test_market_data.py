from backend.app.database import SessionLocal
from backend.app.services.market_data_service import save_current_price


def main():
    db = SessionLocal()

    try:
        data = save_current_price(db, "BTCUSDT")

        print("MARKET DATA SAVED SUCCESSFULLY")
        print("ID:", data.id)
        print("Symbol:", data.symbol)
        print("Price:", data.close_price)
        print("Timestamp:", data.timestamp)

    finally:
        db.close()


if __name__ == "__main__":
    main()
