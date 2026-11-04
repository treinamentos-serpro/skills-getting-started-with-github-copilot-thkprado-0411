import copy
import json

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities database after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def unregister_credentials(monkeypatch):
    accounts = {
        "michael": {
            "password": "michael-password",
            "email": "michael@mergington.edu",
        },
        "other": {
            "password": "other-password",
            "email": "other@mergington.edu",
        },
        "unregistered": {
            "password": "unregistered-password",
            "email": "notregistered@mergington.edu",
        },
        "staff": {
            "password": "staff-password",
            "role": "staff",
        },
    }
    monkeypatch.setenv("UNREGISTER_CREDENTIALS", json.dumps(accounts))
    return {
        username: (username, account["password"])
        for username, account in accounts.items()
    }
