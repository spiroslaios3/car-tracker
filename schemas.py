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
