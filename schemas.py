from datetime import date

from pydantic import BaseModel, ConfigDict


class VehicleCreate(BaseModel):
    make: str
    model: str
    year: int
    plate: str
    odometer_km: int = 0


class VehicleOut(VehicleCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ServiceRecordCreate(BaseModel):
    service_date: date
    odometer_km: int
    service_type: str
    cost: float = 0
    notes: str | None = None


class ServiceRecordOut(ServiceRecordCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vehicle_id: int


class FuelEntryCreate(BaseModel):
    fuel_date: date
    odometer_km: int
    liters: float
    total_cost: float


class FuelEntryOut(FuelEntryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vehicle_id: int


class FuelStats(BaseModel):
    entries_count: int
    total_km: int
    avg_consumption_l_per_100km: float | None
    total_cost: float
    cost_per_km: float | None


class ReminderCreate(BaseModel):
    title: str
    due_date: date | None = None
    due_odometer_km: int | None = None


class ReminderOut(ReminderCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vehicle_id: int
    days_left: int | None = None
    km_left: int | None = None
    status: str = "ok"


class UrgentReminderOut(ReminderOut):
    vehicle_label: str
