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
