from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Measurement(Base):
    """Machine process measurement stored in PostgreSQL."""

    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    machine_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    rpm: Mapped[float] = mapped_column(Float, nullable=False)
    tool_wear: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )