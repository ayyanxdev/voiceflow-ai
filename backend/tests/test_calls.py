"""Call tests."""


def test_create_call(client, auth_headers):
    response = client.post("/api/calls", json={
        "direction": "inbound",
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["direction"] == "inbound"
    assert data["status"] == "initiated"


def test_list_calls(client, auth_headers):
    response = client.get("/api/calls", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_call(client, auth_headers):
    create_resp = client.post("/api/calls", json={
        "direction": "outbound",
    }, headers=auth_headers)
    call_id = create_resp.json()["id"]

    response = client.get(f"/api/calls/{call_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["direction"] == "outbound"


def test_update_call(client, auth_headers):
    create_resp = client.post("/api/calls", json={
        "direction": "inbound",
    }, headers=auth_headers)
    call_id = create_resp.json()["id"]

    response = client.put(f"/api/calls/{call_id}", json={
        "status": "completed",
        "outcome": "qualified",
        "transcript": "Test transcript",
        "duration_seconds": 120,
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["outcome"] == "qualified"
