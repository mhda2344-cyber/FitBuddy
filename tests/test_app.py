import os

os.environ["DEMO_MODE"] = "true"


from fastapi.testclient import TestClient

from app.main import app

from app.database import init_db


init_db()

client = TestClient(app)


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_generate_workout():

    response = client.post(

        "/generate-workout",

        data={
            "username": "Test User",

            "user_id": "TEST001",

            "age": "21",

            "weight": "65",

            "goal": "muscle gain",

            "intensity": "medium",
        },
    )

    assert response.status_code == 200

    assert "7-Day Workout Plan" in response.text


def test_feedback():

    response = client.post(

        "/submit-feedback",

        data={
            "user_id": "TEST001",

            "feedback":
                "Add more cardio and one rest day.",
        },
    )

    assert response.status_code == 200

    assert "Updated" in response.text