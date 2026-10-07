"""Appointment tests."""

from datetime import datetime, timedelta, timezone


def test_create_appointment(client, auth_headers):
    start = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    end = (datetime.now(timezone.utc) + timedelta(days=1, hours=1)).isoformat()

    response = client.post("/api/appointments", json={
        "title": "Roof Inspection",
        "customer_name": "Test Customer",
        "start_time": start,
        "end_time": end,
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Roof Inspection"
    assert data["status"] == "scheduled"


def test_list_appointments(client, auth_headers):
    response = client.get("/api/appointments", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_appointment(client, auth_headers):
    start = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    create_resp = client.post("/api/appointments", json={
        "title": "Test Appt", "start_time": start,
    }, headers=auth_headers)
    appt_id = create_resp.json()["id"]

    response = client.put(f"/api/appointments/{appt_id}", json={
        "status": "confirmed",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


def test_cancel_appointment(client, auth_headers):
    start = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    create_resp = client.post("/api/appointments", json={
        "title": "Cancel Me", "start_time": start,
    }, headers=auth_headers)
    appt_id = create_resp.json()["id"]

    response = client.delete(f"/api/appointments/{appt_id}", headers=auth_headers)
    assert response.status_code == 204
