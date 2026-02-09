# app/tests/test_rate_limit.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_rate_limit():
    for _ in range(5):
        res = client.get("/data/1")
        assert res.status_code == 200
    # 6th request should be limited
    res = client.get("/data/1")
    assert res.status_code == 429  # Too Many Requests
