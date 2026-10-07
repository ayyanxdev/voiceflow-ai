"""Lead CRUD tests."""


def test_create_lead(client, auth_headers, test_business):
    response = client.post("/api/leads", json={
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+15551234567",
        "email": "john@test.com",
        "source": "inbound_call",
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["qualification_score"] >= 0


def test_list_leads(client, auth_headers):
    response = client.get("/api/leads", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_lead(client, auth_headers):
    # Create first
    create_resp = client.post("/api/leads", json={
        "first_name": "Jane", "last_name": "Smith"
    }, headers=auth_headers)
    lead_id = create_resp.json()["id"]

    response = client.get(f"/api/leads/{lead_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Jane"


def test_update_lead(client, auth_headers):
    create_resp = client.post("/api/leads", json={
        "first_name": "Test", "last_name": "User",
        "phone": "+15559999999",
        "email": "test@test.com",
        "company": "Test Corp",
        "notes": "Very interested in service and wants to schedule appointment",
    }, headers=auth_headers)
    lead_id = create_resp.json()["id"]

    response = client.put(f"/api/leads/{lead_id}", json={
        "status": "qualified",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "qualified"
    # Score should be recalculated: 30 (contact) + 20 (complete) + 10 (company) + 30 (appt notes) + 20 (qualified) = 110 -> clamped to 100 -> hot
    assert response.json()["temperature"] == "hot"


def test_delete_lead(client, auth_headers):
    create_resp = client.post("/api/leads", json={
        "first_name": "Delete", "last_name": "Me"
    }, headers=auth_headers)
    lead_id = create_resp.json()["id"]

    response = client.delete(f"/api/leads/{lead_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify deleted
    get_resp = client.get(f"/api/leads/{lead_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_lead_not_found(client, auth_headers):
    response = client.get("/api/leads/99999", headers=auth_headers)
    assert response.status_code == 404
