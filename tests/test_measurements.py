from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def sample_payload() -> dict:
    return {
        "machine_id": "MACHINE-001",
        "temperature": 72.5,
        "rpm": 1450,
        "tool_wear": 12.7,
        "timestamp": "2026-06-02T09:30:00Z",
    }


def test_create_and_get_measurement() -> None:
    create_response = client.post("/measurements", json=sample_payload())

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"] == 1
    assert created["machine_id"] == "MACHINE-001"

    get_response = client.get("/measurements/1")

    assert get_response.status_code == 200
    assert get_response.json()["temperature"] == 72.5


def test_list_measurements() -> None:
    client.post("/measurements", json=sample_payload())

    response = client.get("/measurements")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


def test_rejects_invalid_measurement_payload() -> None:
    payload = sample_payload()
    payload["temperature"] = 999

    response = client.post("/measurements", json=payload)

    assert response.status_code == 422
    assert response.json()["error"] == "Validation error"


def test_delete_measurement() -> None:
    client.post("/measurements", json=sample_payload())

    delete_response = client.delete("/measurements/1")
    get_response = client.get("/measurements/1")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_analysis_summary() -> None:
    client.post("/measurements", json=sample_payload())
    client.post(
        "/measurements",
        json={
            "machine_id": "MACHINE-002",
            "temperature": 82.5,
            "rpm": 1550,
            "tool_wear": 18.7,
            "timestamp": "2026-06-02T09:35:00Z",
        },
    )

    response = client.get("/analysis/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["temperature"]["min"] == 72.5
    assert summary["temperature"]["max"] == 82.5
    assert summary["rpm"]["average"] == 1500