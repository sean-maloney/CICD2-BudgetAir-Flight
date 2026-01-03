from contextlib import asynccontextmanager
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from .database import engine, SessionLocal
from .models import Base, FlightDB, CompanyDB, BookingDB
from .schemas import (
    FlightCreate,
    FlightUpdate,
    FlightPatch,
    FlightRead,
    FlightReadWithCompany,
    FlightCreateForCompany,
    CompanyCreate,
    CompanyRead,
    CompanyUpdate,
    BookingCreate,
    BookingUpdate,
    BookingRead,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def commit_or_rollback(db: Session, error_msg: str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=error_msg)


@app.get("/health")
def health():
    return {"status": "ok"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


@app.post(
    "/api/companies", response_model=CompanyRead, status_code=status.HTTP_201_CREATED
)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = CompanyDB(**company.model_dump())
    db.add(db_company)
    commit_or_rollback(db, "Company Already Exists!")
    db.refresh(db_company)
    return db_company


@app.get("/api/companies", response_model=list[CompanyRead])
def list_courses(db: Session = Depends(get_db)):
    stmt = select(CompanyDB).order_by(CompanyDB.company_id)
    return db.execute(stmt).scalars().all()


@app.get("/api/companies/{company_id}", response_model=CompanyRead)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(CompanyDB, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="company not found")
    return company


@app.put("/api/companies/{company_id}", response_model=CompanyRead)
def update_company(
    company_id: int, updated: CompanyCreate, db: Session = Depends(get_db)
):
    company = db.get(CompanyDB, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="company not found")

    company.code = updated.code
    company.name = updated.name
    company.country = updated.country
    company.email = updated.email
    company.phone = updated.phone

    try:
        db.commit()
        db.refresh(company)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Company already exists!")

    return company


@app.patch("/api/companies/{company_id}", response_model=CompanyRead)
def patch_company(
    company_id: int, updated: CompanyUpdate, db: Session = Depends(get_db)
):
    company = db.get(CompanyDB, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="company not found")

    changes = updated.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in changes.items():
        setattr(company, field, value)

    commit_or_rollback(db, "Company update failed")
    db.refresh(company)
    return company


@app.delete("/api/companies/{company_id}", status_code=204)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(CompanyDB, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()
    return Response(status_code=204)


@app.post("/api/flights", response_model=FlightRead, status_code=201)
def create_flight(flight: FlightCreate, db: Session = Depends(get_db)):
    db_flight = FlightDB(**flight.model_dump())
    db.add(db_flight)
    commit_or_rollback(db, "Flight already exists")
    db.refresh(db_flight)
    return db_flight


@app.get("/api/flights", response_model=list[FlightRead])
def list_flights(db: Session = Depends(get_db)):
    stmt = select(FlightDB).order_by(FlightDB.id)
    return db.execute(stmt).scalars().all()


@app.get("/api/flights/search", response_model=list[FlightRead])
def search_flights(
    origin: str = None, destination: str = None, db: Session = Depends(get_db)
):
    stmt = select(FlightDB)

    if origin:
        stmt = stmt.where(FlightDB.origin.ilike(f"%{origin}%"))
    if destination:
        stmt = stmt.where(FlightDB.destination.ilike(f"%{destination}%"))

    stmt = stmt.order_by(FlightDB.id)
    return db.execute(stmt).scalars().all()


@app.get("/api/flights/{flight_id}", response_model=FlightReadWithCompany)
def get_flight(flight_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(FlightDB)
        .where(FlightDB.id == flight_id)
        .options(selectinload(FlightDB.company))
    )
    flight = db.execute(stmt).scalar_one_or_none()

    if not flight:
        raise HTTPException(status_code=404, detail="flight not found")

    return flight


@app.patch("/api/flights/{flight_id}", response_model=FlightRead)
def patch_flight(flight_id: int, updated: FlightPatch, db: Session = Depends(get_db)):
    flight = db.get(FlightDB, flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    changes = updated.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in changes.items():
        setattr(flight, field, value)

    commit_or_rollback(db, "Flight update failed")
    db.refresh(flight)
    return flight


@app.put("/api/flights/{flight_id}", response_model=FlightRead)
def update_flight(flight_id: int, updated: FlightUpdate, db: Session = Depends(get_db)):
    flight = db.get(FlightDB, flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    flight.name = updated.name
    flight.flight_id = updated.flight_id
    flight.origin = updated.origin
    flight.destination = updated.destination
    flight.departure_time = updated.departure_time
    flight.arrival_time = updated.arrival_time
    flight.departure_date = updated.departure_date
    flight.arrival_date = updated.arrival_date
    flight.price = updated.price
    flight.business_seats = updated.business_seats
    flight.economy_seats = updated.economy_seats
    flight.company_id = updated.company_id

    try:
        db.commit()
        db.refresh(flight)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Flight already exists")

    return flight


@app.delete("/api/flights/{flight_id}", status_code=204)
def delete_flight(flight_id: int, db: Session = Depends(get_db)):
    flight = db.get(FlightDB, flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    db.delete(flight)
    db.commit()
    return Response(status_code=204)


@app.post(
    "/api/companies/{company_id}/flights", response_model=FlightRead, status_code=201
)
def create_flight_for_company(
    company_id: int, flight: FlightCreateForCompany, db: Session = Depends(get_db)
):
    company = db.get(CompanyDB, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    data = flight.model_dump()
    data["company_id"] = company_id

    db_flight = FlightDB(**data)
    db.add(db_flight)
    commit_or_rollback(db, "Flight Creation Failed!")
    db.refresh(db_flight)

    return db_flight


@app.get("/api/companies/{company_id}/flights", response_model=list[FlightRead])
def list_flights_for_company(company_id: int, db: Session = Depends(get_db)):
    stmt = select(FlightDB).where(FlightDB.company_id == company_id)
    flights = db.execute(stmt).scalars().all()

    if not flights:
        if not db.get(CompanyDB, company_id):
            raise HTTPException(status_code=404, detail="Company not found")

    return flights


@app.post(
    "/api/bookings", response_model=BookingRead, status_code=status.HTTP_201_CREATED
)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    booking_data = booking.model_dump()
    db_booking = BookingDB(**booking_data)
    db.add(db_booking)
    commit_or_rollback(db, "Booking creation failed")
    db.refresh(db_booking)
    # Convert datetime to string for response
    booking_dict = {
        "id": db_booking.id,
        "user_id": db_booking.user_id,
        "flight_id": db_booking.flight_id,
        "flight_name": db_booking.flight_name,
        "origin": db_booking.origin,
        "destination": db_booking.destination,
        "departure_time": db_booking.departure_time,
        "arrival_time": db_booking.arrival_time,
        "departure_date": db_booking.departure_date,
        "arrival_date": db_booking.arrival_date,
        "price": db_booking.price,
        "company_id": db_booking.company_id,
        "status": db_booking.status,
        "payment_id": db_booking.payment_id,
        "paid_at": db_booking.paid_at,
        "created_at": db_booking.created_at.isoformat()
        if db_booking.created_at
        else "",
        "updated_at": db_booking.updated_at.isoformat()
        if db_booking.updated_at
        else "",
    }
    return booking_dict


@app.get("/api/bookings", response_model=list[BookingRead])
def list_bookings(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    stmt = select(BookingDB)
    if user_id:
        stmt = stmt.where(BookingDB.user_id == user_id)
    stmt = stmt.order_by(BookingDB.id)
    bookings = db.execute(stmt).scalars().all()

    return [
        {
            "id": b.id,
            "user_id": b.user_id,
            "flight_id": b.flight_id,
            "flight_name": b.flight_name,
            "origin": b.origin,
            "destination": b.destination,
            "departure_time": b.departure_time,
            "arrival_time": b.arrival_time,
            "departure_date": b.departure_date,
            "arrival_date": b.arrival_date,
            "price": b.price,
            "company_id": b.company_id,
            "status": b.status,
            "payment_id": b.payment_id,
            "paid_at": b.paid_at,
            "created_at": b.created_at.isoformat() if b.created_at else "",
            "updated_at": b.updated_at.isoformat() if b.updated_at else "",
        }
        for b in bookings
    ]


@app.get("/api/bookings/{booking_id}", response_model=BookingRead)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.get(BookingDB, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "flight_id": booking.flight_id,
        "flight_name": booking.flight_name,
        "origin": booking.origin,
        "destination": booking.destination,
        "departure_time": booking.departure_time,
        "arrival_time": booking.arrival_time,
        "departure_date": booking.departure_date,
        "arrival_date": booking.arrival_date,
        "price": booking.price,
        "company_id": booking.company_id,
        "status": booking.status,
        "payment_id": booking.payment_id,
        "paid_at": booking.paid_at,
        "created_at": booking.created_at.isoformat() if booking.created_at else "",
        "updated_at": booking.updated_at.isoformat() if booking.updated_at else "",
    }


@app.put("/api/bookings/{booking_id}", response_model=BookingRead)
def update_booking(
    booking_id: int, updated: BookingUpdate, db: Session = Depends(get_db)
):
    booking = db.get(BookingDB, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    changes = updated.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in changes.items():
        setattr(booking, field, value.value if hasattr(value, "value") else value)

    commit_or_rollback(db, "Booking update failed")
    db.refresh(booking)
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "flight_id": booking.flight_id,
        "flight_name": booking.flight_name,
        "origin": booking.origin,
        "destination": booking.destination,
        "departure_time": booking.departure_time,
        "arrival_time": booking.arrival_time,
        "departure_date": booking.departure_date,
        "arrival_date": booking.arrival_date,
        "price": booking.price,
        "company_id": booking.company_id,
        "status": booking.status,
        "payment_id": booking.payment_id,
        "paid_at": booking.paid_at,
        "created_at": booking.created_at.isoformat() if booking.created_at else "",
        "updated_at": booking.updated_at.isoformat() if booking.updated_at else "",
    }


@app.delete("/api/bookings/{booking_id}", status_code=204)
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.get(BookingDB, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    db.delete(booking)
    db.commit()
    return Response(status_code=204)


@app.get("/api/users/{user_id}/bookings", response_model=list[BookingRead])
def get_user_bookings(user_id: str, db: Session = Depends(get_db)):
    stmt = select(BookingDB).where(BookingDB.user_id == user_id).order_by(BookingDB.id)
    bookings = db.execute(stmt).scalars().all()
    return [
        {
            "id": b.id,
            "user_id": b.user_id,
            "flight_id": b.flight_id,
            "flight_name": b.flight_name,
            "origin": b.origin,
            "destination": b.destination,
            "departure_time": b.departure_time,
            "arrival_time": b.arrival_time,
            "departure_date": b.departure_date,
            "arrival_date": b.arrival_date,
            "price": b.price,
            "company_id": b.company_id,
            "status": b.status,
            "payment_id": b.payment_id,
            "paid_at": b.paid_at,
            "created_at": b.created_at.isoformat() if b.created_at else "",
            "updated_at": b.updated_at.isoformat() if b.updated_at else "",
        }
        for b in bookings
    ]
