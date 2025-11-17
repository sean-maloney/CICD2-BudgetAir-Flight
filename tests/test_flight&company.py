import pytest

#payloads
def company_payload(code="RYR",name="Ryanair",country="Ireland",email="info@ryanair.com",phone="01234567"):
    return{"code": code, "name": name, "country": country, "email": email, "phone": phone}

def flight_payload(company_id: int, name="Dublin-London", flight_id="F1234567", origin="DUB", destination="LHR", departure_time="10:30",arrival_time="12:00",departure_date="20-11-2025",arrival_date="20-11-2025",price="€1234567",):
    return{"name": name, "flight_id": flight_id, "origin": origin, "destination": destination, "departure_time": departure_time, "arrival_time": arrival_time, "departure_date": departure_date, "arrival_date": arrival_date, "price": price, "company_id": company_id}

#                                              company tests
def test_create_company_ok(client):
    r = client.post("/api/companies", json=company_payload())
    assert r.status_code == 201
    data = r.json()
    assert data["company_id"] == 1
    assert data["name"] == "Ryanair"
    assert data["code"] == "RYR"

def test_get_company_ok(client):
    r_create = client.post("/api/companies", json=company_payload(name = "Air 2"))
    assert r_create.status_code == 201
    cid = r_create.json()["company_id"]
    
    r = client.get(f"/api/companies/{cid}")
    assert r.status_code == 200
    data = r.json()
    assert data["company_id"] == cid
    assert data["name"] == "Air 2"

def test_get_company_not_found(client):
    r = client.get("/api/companies/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "company not found"

def test_update_compnay_ok(client):
    r_create = client.post("/api/companies", json=company_payload(name="OldCo"))
    assert r_create.status_code == 201
    cid = r_create.json()["company_id"]

    r = client.put(f"/api/companies/{cid}", json=company_payload(code="EZY",name="NewCo",country="UK",email="new@co.com",phone="41234567",),)
    assert r.status_code == 200
    data=r.json()
    assert data["company_id"] == cid
    assert data["code"] == "EZY"
    assert data["name"] == "NewCo"
    assert data["country"] == "UK"
    assert data["email"] == "new@co.com"
    assert data["phone"] == "41234567"

def test_patch_company_ok(client):
    r_create = client.post("/api/companies", json=company_payload(name="PatchMe"))
    assert r_create.status_code == 201
    cid = r_create.json()["company_id"]

    r = client.patch(f"/api/companies/{cid}", json=company_payload(name="PatchedCo",phone="49999999",),)
    assert r.status_code == 200
    data=r.json()
    assert data["company_id"] == cid
    assert data["name"] == "PatchedCo"
    assert data["phone"] == "49999999"

    assert data["code"] == "RYR"
    assert data["country"] == "Ireland"
    assert data["email"] == "info@ryanair.com"


def test_delete_company_then_404(client):
    r_create = client.post("/api/companies", json=company_payload(name="DeleteMe"))
    assert r_create.status_code==201
    cid=r_create.json()["company_id"]

    r1 = client.delete(f"/api/companies/{cid}")
    assert r1.status_code == 204

    r2 = client.get(f"/api/companies/{cid}")
    assert r2.status_code == 404


#                            Flights


def test_create_flight_ok(client):
    c = client.post("/api/companies", json=company_payload(name="FlightCo"))
    assert c.status_code == 201
    company_id = c.json()["company_id"]


    r = client.post("/api/flights", json=flight_payload(company_id))
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Dublin-London"
    assert data["flight_id"] == "F1234567"
    assert data["company_id"] == company_id

def test_get_flight_ok(client):
    c = client.post("/api/companies", json=company_payload(name = "FlightCo2"))
    assert c.status_code == 201
    company_id = c.json()["company_id"]
    
    f = client.post(f"/api/flights/", json=flight_payload(company_id, name="Route 2"))
    assert f.status_code == 201
    fid = f.json()["id"]

    r = client.get(f"/api/flights/{fid}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == fid
    assert data["name"] == "Route 2"
    assert data["company_id"] == company_id

def test_get_flight_not_found(client):
    r = client.get("/api/flights/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "flight not found"

def test_update_company_ok(client):
    c = client.post("/api/companies", json=company_payload(name="UpdatedCo"))
    assert c.status_code == 201
    company_id = c.json()["company_id"]

    f_create = client.post("/api/flights", json=flight_payload(company_id, name="OldFlight"))
    assert f_create.status_code == 201
    fid = f_create.json()["id"]

    r = client.put(f"/api/flights/{fid}", json=flight_payload(company_id=company_id, name="NewFlight",flight_id="F0000002",origin="DUB",destination="CDG",departure_time="15:00",arrival_time="18:00",departure_date="21-11-2025",arrival_date="21-11-2025",price="€2222222",),)
    
    assert r.status_code == 200
    data=r.json()
    assert data["id"] == fid
    assert data["name"] == "NewFlight"
    assert data["flight_id"] == "F0000002"
    assert data["destination"] == "CDG"
    assert data["price"] == "€2222222"
    assert data["company_id"] == company_id



def test_patch_flight_ok(client):
    c = client.post("/api/companies", json=company_payload(name="PatchFlightCo"))
    assert c.status_code == 201
    company_id = c.json()["company_id"]

    f_create = client.post("/api/flights", json=flight_payload(company_id, name="PatchMeFlight",destination="AMS"),)
    assert f_create.status_code == 201
    fid = f_create.json()["id"]

    r = client.patch(f"/api/flights/{fid}", json={"name": "PatchedFlight", "price": "€9999999"},)
    assert r.status_code == 200
    data=r.json()

    assert data["id"] == fid
    assert data["name"] == "PatchedFlight"
    assert data["price"] == "€9999999"

    assert data["destination"] == "AMS"
    assert data["company_id"] == company_id

def test_delete_company_then_404(client):
    c = client.post("/api/companies", json=company_payload(name="DeleteFlightCo"))
    assert c.status_code == 201
    company_id = c.json()["company_id"]

    f_create = client.post("/api/flights", json=flight_payload(company_id, name="DeleteMeFlight"))
    assert f_create.status_code == 201
    fid = f_create.json()["id"]

    r1 = client.delete(f"/api/flights/{fid}")
    assert r1.status_code == 204

    r2 = client.get(f"/api/flights/{fid}")
    assert r2.status_code == 404

# ========== NESTED: flights under company_id ========== #

def test_create_flights_for_company_and_list(client):
    c = client.post("/api/companies", json=company_payload(name="NestedCo"))
    assert c.status_code == 201
    company_id = c.json()["company_id"]

    # create two flights via nested endpoint
    r1 = client.post(
        f"/api/companies/{company_id}/flights",
        json={
            "name": "NestedFlight1",
            "flight_id": "F0000101",
            "origin": "DUB",
            "destination": "LHR",
            "departure_time": "08:00",
            "arrival_time": "09:00",
            "departure_date": "2025-11-22",
            "arrival_date": "2025-11-22",
            "price": "€3333333",
        },
    )
    assert r1.status_code == 201

    r2 = client.post(
        f"/api/companies/{company_id}/flights",
        json={
            "name": "NestedFlight2",
            "flight_id": "F0000102",
            "origin": "DUB",
            "destination": "CDG",
            "departure_time": "10:00",
            "arrival_time": "13:00",
            "departure_date": "2025-11-22",
            "arrival_date": "2025-11-22",
            "price": "€4444444",
        },
    )
    assert r2.status_code == 201

    # list flights for that company
    r_list = client.get(f"/api/companies/{company_id}/flights")
    assert r_list.status_code == 200
    flights = r_list.json()
    assert len(flights) == 2
    names = {f["name"] for f in flights}
    assert "NestedFlight1" in names
    assert "NestedFlight2" in names
    for f in flights:
        assert f["company_id"] == company_id
