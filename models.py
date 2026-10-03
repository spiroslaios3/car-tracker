from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    make: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int]
    plate: Mapped[str] = mapped_column(String(20), unique=True)
    odometer_km: Mapped[int] = mapped_column(default=0)
