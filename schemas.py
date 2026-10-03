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
