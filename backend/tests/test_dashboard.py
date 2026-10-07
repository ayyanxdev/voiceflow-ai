"""Dashboard tests."""


def test_get_dashboard(client, auth_headers):
    response = client.get("/api/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data
    assert "charts" in data
    assert "recent_activity" in data
    assert "recent_calls" in data
    assert "hot_leads" in data
    assert "upcoming_appointments" in data


def test_dashboard_overview_empty(client, auth_headers):
    response = client.get("/api/dashboard", headers=auth_headers)
    assert response.status_code == 200
    overview = response.json()["overview"]
    assert overview["total_calls"] == 0
    assert overview["total_leads"] == 0


def test_dashboard_includes_retell_booked_appointment(client, auth_headers):
    booking = client.post("/api/webhooks/retell/book-appointment", json={
        "customer_name": "Taylor Reed",
        "customer_phone": "+15550000456",
        "start_time": "2027-06-18T10:30:00",
        "title": "Roof Inspection",
    })
    assert booking.status_code == 200, booking.text

    response = client.get("/api/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["overview"]["appointments_booked"] == 1
    assert any(
        appointment["id"] == booking.json()["appointment_id"]
        for appointment in data["upcoming_appointments"]
    )
