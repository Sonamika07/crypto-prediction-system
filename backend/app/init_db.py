from backend.app.database import Base, engine
from backend.app.models.market_data import MarketData

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
