from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func

from backend.app.database import Base


class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    symbol = Column(
        String(20),
        nullable=False
    )

    timestamp = Column(
        DateTime(timezone=True),
        nullable=False
    )

    prediction = Column(
        String(10),
        nullable=False
    )

    confidence = Column(
        Numeric(10, 6),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )