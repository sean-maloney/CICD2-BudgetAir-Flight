from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from .database import engine, SessionLocal
from .models import Base, FlightDB, CompanyDB
from .schemas import (FlightCreate, FlightUpdate, FlightPatch, FlightRead, FlightReadWithCompany, FlightCreateForCompany, CompanyCreate, CompanyRead, CompanyUpdate)

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
 
  #checks health returns if ok
@app.get("/health")
def health():
  return {"status": "ok"}
 
# CORS (add this block)
app.add_middleware(
CORSMiddleware,
    allow_origins=["*"], # dev-friendly; tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)
 
#Replacing @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    #Shutdown
    #Optionally close pools, flush queses, etc
    #SessionLocal.close_all()
 
#company create
@app.post("/api/companies",response_model= CompanyRead,status_code=status.HTTP_201_CREATED)
def create_company(company: CompanyCreate, db:Session = Depends(get_db)):
   db_company = CompanyDB(**company.model_dump())
   db.add(db_company)
   commit_or_rollback(db, "Company Already Exists!")
   db.refresh(db_company)
   return db_company

#get companies
@app.get("/api/companies", response_model=list[CompanyRead])
def list_courses(db: Session = Depends(get_db)):
  stmt = select(CompanyDB).order_by(CompanyDB.company_id)
  return db.execute(stmt).scalars().all()

@app.get("/api/companies/{company_id}", response_model=CompanyRead)
def get_company(company_id: int, db:Session=Depends(get_db)):
   company = db.get(CompanyDB, company_id)
   if not company:
      raise HTTPException(status_code=404, detail="company not found")
   return company
 
#update
@app.put("/api/companies/{company_id}", response_model=CompanyRead)
def update_company(company_id: int, updated:CompanyCreate, db:Session = Depends(get_db)):
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

#patch
@app.patch("/api/companies/{company_id}", response_model=CompanyRead)
def patch_company(company_id: int, updated: CompanyUpdate, db:Session = Depends(get_db)):
  company = db.get(CompanyDB, company_id)
  if not company:
    raise HTTPException(status_code=404, detail="company not found")
  
  changes = updated.model_dump(exclude_unset=True, exclude_none=True)
  for field, value in changes.items():
    setattr(company, field, value)

  commit_or_rollback(db, "Company update failed")
  db.refresh(company)
  return company

#company delete
@app.delete("/api/companies/{company_id}", status_code=204)
def delete_company(company_id: int, db:Session=Depends(get_db)):
  company = db.get(CompanyDB, company_id)
  if not company:
    raise HTTPException(status_code=404, detail="Company not found")
  db.delete(company)
  db.commit()
  return Response(status_code=204)


#----------------------FLIGHTS----------------------------

#create flight
@app.post("/api/flights", response_model=FlightRead, status_code=201)
def create_flight(flight: FlightCreate, db:Session = Depends(get_db)):
  db_flight = FlightDB(**flight.model_dump())
  db.add(db_flight)
  commit_or_rollback(db, "Flight already exists")
  db.refresh(db_flight)
  return db_flight

#list flights
@app.get("/api/flights", response_model=list[FlightRead])
def list_flights(db:Session = Depends(get_db)):
  stmt = (
    select(FlightDB)
    .order_by(FlightDB.id)
  )
  return db.execute(stmt).scalars().all()

@app.get("/api/flights/search", response_model=list[FlightRead])
def search_flights(origin: str = None, destination: str = None, db: Session = Depends(get_db)):
  stmt = select(FlightDB)
  
  if origin:
    stmt = stmt.where(FlightDB.origin.ilike(f"%{origin}%"))
  if destination:
    stmt = stmt.where(FlightDB.destination.ilike(f"%{destination}%"))
  
  stmt = stmt.order_by(FlightDB.id)
  return db.execute(stmt).scalars().all()

#get flight with company
@app.get("/api/flights/{flight_id}",response_model=FlightReadWithCompany)
def get_flight(flight_id: int, db:Session=Depends(get_db)):
  stmt = (
    select(FlightDB)
    .where(FlightDB.id == flight_id)
    .options(selectinload(FlightDB.company))
  )
  flight = db.execute(stmt).scalar_one_or_none()

  if not flight:
    raise HTTPException(status_code=404, detail="flight not found")
  
  return flight


#patch flight
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

#update flight
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

#delete flight
@app.delete("/api/flights/{flight_id}", status_code=204)
def delete_flight(flight_id : int, db:Session = Depends(get_db)):
  flight = db.get(FlightDB, flight_id)
  if not flight:
    raise HTTPException(status_code=404, detail="Flight not found")
  db.delete(flight)
  db.commit()
  return Response(status_code=204)

#Nested: Create flight for a company
@app.post("/api/companies/{company_id}/flights", response_model=FlightRead, status_code=201)
def create_flight_for_company(company_id: int, flight: FlightCreateForCompany, db: Session = Depends(get_db)):
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