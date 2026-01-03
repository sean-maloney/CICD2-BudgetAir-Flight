from typing import Annotated, Optional, List
from annotated_types import Ge, Le
from pydantic import BaseModel, EmailStr, ConfigDict, StringConstraints, Field
from enum import Enum
 
FlightNameStr = Annotated[str, StringConstraints(min_length=1, max_length=100)]
FlightIdStr = Annotated[str, StringConstraints(pattern=r"^F\d{7}$")]
FlightOriginStr = Annotated[str, StringConstraints(min_length=1, max_length=32)]
FlightDestinationStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]
FlightDepartureTimeStr = Annotated[str, StringConstraints(min_length=5, max_length=5)]
FlightArrivalTimeStr = Annotated[str, StringConstraints(min_length=5, max_length=5)] #23:10
FlightDepartureDateStr = Annotated[str, StringConstraints(min_length=10, max_length=10)]
FlightArrivalDate = Annotated[str, StringConstraints(min_length=10, max_length=10)] #12/11/2025
FlightPriceStr = Annotated[str, StringConstraints(min_length=1, max_length=100)]
FlightSeatsInt = Annotated[int, Ge(0), Le(1000)]
CompanyNameStr = Annotated[str, StringConstraints(min_length=1, max_length=100)]
CompanyAirlineCodeStr = Annotated[str, StringConstraints(min_length=1, max_length=3)]
CompanyCountryStr = Annotated[str, StringConstraints(min_length=2, max_length=100)]
CompanyEmailStr = EmailStr
CompanyPhoneStr = Annotated[str, StringConstraints(min_length=5, max_length=20)]
 
class FlightCreate(BaseModel):
    name: FlightNameStr
    flight_id: FlightIdStr
    origin: FlightOriginStr
    destination: FlightDestinationStr
    departure_time: FlightDepartureTimeStr
    arrival_time: FlightArrivalTimeStr
    departure_date: FlightDepartureDateStr
    arrival_date: FlightArrivalDate
    price: FlightPriceStr
    business_seats: FlightSeatsInt = Field(default=0, description="Number of business class seats")
    economy_seats: FlightSeatsInt = Field(default=0, description="Number of economy class seats")
    company_id: int
 
class FlightUpdate(BaseModel):
    name: FlightNameStr
    flight_id: FlightIdStr
    origin: FlightOriginStr
    destination: FlightDestinationStr
    departure_time: FlightDepartureTimeStr
    arrival_time: FlightArrivalTimeStr
    departure_date: FlightDepartureDateStr
    arrival_date: FlightArrivalDate
    price: FlightPriceStr
    business_seats: FlightSeatsInt = Field(default=0, description="Number of business class seats")
    economy_seats: FlightSeatsInt = Field(default=0, description="Number of economy class seats")
    company_id: int

class FlightPatch(BaseModel):
    name: Optional[FlightNameStr] = None
    flight_id: Optional[FlightIdStr] = None
    origin: Optional[FlightOriginStr] = None
    destination: Optional[FlightDestinationStr] = None
    departure_time: Optional[FlightDepartureTimeStr] = None
    arrival_time: Optional[FlightArrivalTimeStr] = None
    departure_date: Optional[FlightDepartureDateStr] = None
    arrival_date: Optional[FlightArrivalDate] = None
    price: Optional[FlightPriceStr] = None
    business_seats: Optional[FlightSeatsInt] = None
    economy_seats: Optional[FlightSeatsInt] = None
    company_id: Optional[int] = None
 
class FlightRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: FlightNameStr
    flight_id: FlightIdStr
    origin: FlightOriginStr
    destination: FlightDestinationStr
    departure_time: FlightDepartureTimeStr
    arrival_time: FlightArrivalTimeStr
    departure_date: FlightDepartureDateStr
    arrival_date: FlightArrivalDate
    price: FlightPriceStr
    business_seats: int
    economy_seats: int
    company_id: int


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    company_id: int
    code: CompanyAirlineCodeStr
    name: CompanyNameStr
    country: CompanyCountryStr
    email: CompanyEmailStr
    phone: CompanyPhoneStr
 
class FlightReadWithCompany(FlightRead):
    company: Optional[CompanyRead] = None
 
class CompanyCreate(BaseModel):
    code: CompanyAirlineCodeStr         
    name: CompanyNameStr        
    country: CompanyCountryStr
    email: CompanyEmailStr
    phone: CompanyPhoneStr

class FlightCreateForCompany(BaseModel):
    name: FlightNameStr
    flight_id: FlightIdStr
    origin: FlightOriginStr
    destination: FlightDestinationStr
    departure_time: FlightDepartureTimeStr
    arrival_time: FlightArrivalTimeStr
    departure_date: FlightDepartureDateStr
    arrival_date: FlightArrivalDate
    price: FlightPriceStr
    business_seats: FlightSeatsInt = Field(default=0, description="Number of business class seats")
    economy_seats: FlightSeatsInt = Field(default=0, description="Number of economy class seats")
 
class CompanyUpdate(BaseModel):
    code: Optional[CompanyAirlineCodeStr] = None
    name: Optional[CompanyNameStr] = None
    country: Optional[CompanyCountryStr] = None
    email: Optional[CompanyEmailStr] = None
    phone: Optional[CompanyPhoneStr] = None
 
class FlightReadCompany(CompanyRead):
    flights: Optional[FlightRead] = Field(default_factory=list) 

class BookingStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

BookingUserIdStr = Annotated[str, StringConstraints(min_length=1, max_length=100)]
BookingFlightIdStr = Annotated[str, StringConstraints(min_length=1, max_length=8)]
BookingStatusStr = Annotated[str, StringConstraints(min_length=1, max_length=20)]

class BookingCreate(BaseModel):
    user_id: BookingUserIdStr
    flight_id: BookingFlightIdStr
    flight_name: FlightNameStr
    origin: FlightOriginStr
    destination: FlightDestinationStr
    departure_time: FlightDepartureTimeStr
    arrival_time: FlightArrivalTimeStr
    departure_date: FlightDepartureDateStr
    arrival_date: FlightArrivalDate
    price: FlightPriceStr
    company_id: int
    status: BookingStatus = Field(default=BookingStatus.PENDING)
    payment_id: Optional[str] = None
    paid_at: Optional[str] = None

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    payment_id: Optional[str] = None
    paid_at: Optional[str] = None

class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: str
    flight_id: str
    flight_name: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    departure_date: str
    arrival_date: str
    price: str
    company_id: int
    status: str
    payment_id: Optional[str] = None
    paid_at: Optional[str] = None
    created_at: str
    updated_at: str
