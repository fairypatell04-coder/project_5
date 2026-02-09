# app/tests/test_background.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_trigger_email():
    res = client.post("/send-email", json={"email": "test@example.com"})
    assert res.status_code == 200
    assert res.json()["status"] == "Email scheduled"
