from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Car tracker is running"}


@app.post("/vehicles", response_model=schemas.VehicleOut, status_code=201)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = models.Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A vehicle with this plate already exists",
        )
    db.refresh(db_vehicle)
    return db_vehicle


@app.get("/vehicles", response_model=list[schemas.VehicleOut])
def list_vehicles(db: Session = Depends(get_db)):
    return db.scalars(select(models.Vehicle)).all()


@app.get("/vehicles/{vehicle_id}", response_model=schemas.VehicleOut)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.get(models.Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@app.put("/vehicles/{vehicle_id}", response_model=schemas.VehicleOut)
def update_vehicle(
    vehicle_id: int,
    data: schemas.VehicleCreate,
    db: Session = Depends(get_db),
):
    vehicle = db.get(models.Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    for field, value in data.model_dump().items():
        setattr(vehicle, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A vehicle with this plate already exists",
        )
    db.refresh(vehicle)
    return vehicle


@app.delete("/vehicles/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.get(models.Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(vehicle)
    db.commit()


@app.post(
    "/vehicles/{vehicle_id}/services",
    response_model=schemas.ServiceRecordOut,
    status_code=201,
)
def add_service(
    vehicle_id: int,
    record: schemas.ServiceRecordCreate,
    db: Session = Depends(get_db),
):
    vehicle = db.get(models.Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db_record = models.ServiceRecord(vehicle_id=vehicle_id, **record.model_dump())
    db.add(db_record)
    if record.odometer_km > vehicle.odometer_km:
        vehicle.odometer_km = record.odometer_km
    db.commit()
    db.refresh(db_record)
    return db_record


@app.get(
    "/vehicles/{vehicle_id}/services",
    response_model=list[schemas.ServiceRecordOut],
)
def list_services(vehicle_id: int, db: Session = Depends(get_db)):
    if db.get(models.Vehicle, vehicle_id) is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    stmt = (
        select(models.ServiceRecord)
        .where(models.ServiceRecord.vehicle_id == vehicle_id)
        .order_by(models.ServiceRecord.service_date.desc())
    )
    return db.scalars(stmt).all()


@app.post(
    "/vehicles/{vehicle_id}/fuel",
    response_model=schemas.FuelEntryOut,
    status_code=201,
)
def add_fuel(
    vehicle_id: int,
    entry: schemas.FuelEntryCreate,
    db: Session = Depends(get_db),
):
    vehicle = db.get(models.Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db_entry = models.FuelEntry(vehicle_id=vehicle_id, **entry.model_dump())
    db.add(db_entry)
    if entry.odometer_km > vehicle.odometer_km:
        vehicle.odometer_km = entry.odometer_km
    db.commit()
    db.refresh(db_entry)
    return db_entry


@app.get(
    "/vehicles/{vehicle_id}/fuel",
    response_model=list[schemas.FuelEntryOut],
)
def list_fuel(vehicle_id: int, db: Session = Depends(get_db)):
    if db.get(models.Vehicle, vehicle_id) is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    stmt = (
        select(models.FuelEntry)
        .where(models.FuelEntry.vehicle_id == vehicle_id)
        .order_by(models.FuelEntry.odometer_km.desc())
    )
    return db.scalars(stmt).all()


@app.get(
    "/vehicles/{vehicle_id}/fuel/stats",
    response_model=schemas.FuelStats,
)
def fuel_stats(vehicle_id: int, db: Session = Depends(get_db)):
    if db.get(models.Vehicle, vehicle_id) is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    stmt = (
        select(models.FuelEntry)
        .where(models.FuelEntry.vehicle_id == vehicle_id)
        .order_by(models.FuelEntry.odometer_km)
    )
    entries = db.scalars(stmt).all()
    total_cost = sum(e.total_cost for e in entries)

    total_km = 0
    if len(entries) >= 2:
        total_km = entries[-1].odometer_km - entries[0].odometer_km
    if total_km <= 0:
        return schemas.FuelStats(
            entries_count=len(entries),
            total_km=0,
            avg_consumption_l_per_100km=None,
            total_cost=total_cost,
            cost_per_km=None,
        )

    liters_used = sum(e.liters for e in entries[1:])
    cost_used = sum(e.total_cost for e in entries[1:])
    return schemas.FuelStats(
        entries_count=len(entries),
        total_km=total_km,
        avg_consumption_l_per_100km=round(liters_used / total_km * 100, 2),
        total_cost=total_cost,
        cost_per_km=round(cost_used / total_km, 3),
    )


from fastapi.staticfiles import StaticFiles

app.mount("/app", StaticFiles(directory="static", html=True), name="static")


@app.delete("/services/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    record = db.get(models.ServiceRecord, service_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(record)
    db.commit()
