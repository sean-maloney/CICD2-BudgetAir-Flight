from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from typing import Optional, List
 
 
class Base(DeclarativeBase):
    pass
 
 #user database model
class FlightDB(Base):
    __tablename__ = "flights"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    flight_id: Mapped[str] = mapped_column(String(8), nullable=False)
    origin: Mapped[str] = mapped_column(String(32), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    departure_time: Mapped[str] = mapped_column(String(5), nullable=False)
    arrival_time: Mapped[str] = mapped_column(String(5), nullable=False)
    departure_date: Mapped[str] = mapped_column(String(10), nullable=False)
    arrival_date: Mapped[str] = mapped_column(String(10), nullable=False)
    price: Mapped[str] = mapped_column(String(10), nullable=False)
    business_seats: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    economy_seats: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False)
    company: Mapped["CompanyDB"] = relationship(back_populates="flights")

class CompanyDB(Base):
    __tablename__ = "companies"
    company_id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(3), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    flights: Mapped[List["FlightDB"]] = relationship(back_populates="company",cascade="all, delete-orphan")
    

