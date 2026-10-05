from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    make: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int]
    plate: Mapped[str] = mapped_column(String(20), unique=True)
    odometer_km: Mapped[int] = mapped_column(default=0)

    service_records: Mapped[list["ServiceRecord"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan"
    )


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    service_date: Mapped[date]
    odometer_km: Mapped[int]
    service_type: Mapped[str] = mapped_column(String(50))
    cost: Mapped[float] = mapped_column(default=0)
    notes: Mapped[str | None] = mapped_column(String(500), default=None)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="service_records")
