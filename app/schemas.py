from typing import Annotated, Optional, List
from annotated_types import Ge, Le
from pydantic import BaseModel, EmailStr, ConfigDict, StringConstraints, Field
 
# ---------- Reusable type aliases ----------
FlightNameStr = Annotated[str, StringConstraints(min_length=1, max_length=100)]
FlightIdStr = Annotated[str, StringConstraints(pattern=r"^F\d{7}$")]
FlightOriginStr = Annotated[str, StringConstraints(min_length=1, max_length=32)]
FlightDestinationStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]
FlightDepartureTimeStr = Annotated[str, StringConstraints(min_length=5, max_length=5)]
FlightArrivalTimeStr = Annotated[str, StringConstraints(min_length=5, max_length=5)] #23:10
FlightDepartureDateStr = Annotated[str, StringConstraints(min_length=10, max_length=10)]
FlightArrivalDate = Annotated[str, StringConstraints(min_length=10, max_length=10)] #12/11/2025
FlightPriceStr = Annotated[str, StringConstraints(pattern=r"^€\d{7}$")]
CompanyNameStr = Annotated[str, StringConstraints(min_length=1, max_length=100)]
CompanyAirlineCodeStr = Annotated[str, StringConstraints(min_length=1, max_length=3)]
CompanyCountryStr = Annotated[str, StringConstraints(min_length=2, max_length=100)]
CompanyEmailStr = EmailStr
CompanyPhoneStr = Annotated[str, StringConstraints(min_length=5, max_length=20)]
 
# ---------- Flight ----------
class FlightCreate(BaseModel):
    name: FlightNameStr
    flight_id: FlightIdStr
    origin: FlightOriginStr
    destination: FlightDestinationStr
    departure_time: FlightDepartureTimeStr
    arrival_time: FlightArrivalTimeStr
    depature_date: FlightDepartureDateStr
    arrival_date: FlightArrivalDate
    price: FlightPriceStr
 
class FlightUpdate(BaseModel):
    name: FlightNameStr
    flight_id: FlightIdStr
    origin: FlightOriginStr
    destination: FlightDestinationStr
    departure_time: FlightDepartureTimeStr
    arrival_time: FlightArrivalTimeStr
    depature_date: FlightDepartureDateStr
    arrival_date: FlightArrivalDate
    price: FlightPriceStr
 
class FlightRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: FlightNameStr
    flight_id: FlightIdStr
    origin: FlightOriginStr
    destination: FlightDestinationStr
    departure_time: FlightDepartureTimeStr
    arrival_time: FlightArrivalTimeStr
    depature_date: FlightDepartureDateStr
    arrival_date: FlightArrivalDate
    price: FlightPriceStr


# ---------- Company ----------
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
 
class CompanyUpdate(BaseModel):
    code: Optional[CompanyAirlineCodeStr] = None
    name: Optional[CompanyNameStr] = None
    country: Optional[CompanyCountryStr] = None
    email: Optional[CompanyEmailStr] = None
    phone: Optional[CompanyPhoneStr] = None
 
class FlightReadCompany(CompanyRead):
    flights: Optional[FlightRead] = Field(default_factory=list) 
 
