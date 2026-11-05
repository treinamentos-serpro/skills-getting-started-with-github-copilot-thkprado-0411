"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import json
import secrets
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from threading import Lock

unregister_security = HTTPBasic()

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice basketball skills and compete in school games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": []
    },
    "Soccer Club": {
        "description": "Develop soccer skills and play friendly matches",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 22,
        "participants": []
    },
    "Art Club": {
        "description": "Explore drawing, painting, and other visual arts",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Act, write, and produce performances for the school community",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Science Club": {
        "description": "Explore scientific ideas through experiments and projects",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 16,
        "participants": []
    },
    "Debate Club": {
        "description": "Build research, public speaking, and critical thinking skills",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 16,
        "participants": []
    }
}

activity_lock = Lock()


def get_unregister_account(
    credentials: HTTPBasicCredentials = Depends(unregister_security),
):
    try:
        accounts = json.loads(os.environ.get("UNREGISTER_CREDENTIALS", "{}"))
    except json.JSONDecodeError:
        accounts = {}

    if not isinstance(accounts, dict):
        accounts = {}

    authenticated_account = None
    for username, account in accounts.items():
        if not isinstance(username, str) or not isinstance(account, dict):
            continue
        password = account.get("password")
        if not isinstance(password, str) or not password:
            continue
        username_matches = secrets.compare_digest(
            credentials.username.encode("utf-8"), username.encode("utf-8")
        )
        password_matches = secrets.compare_digest(
            credentials.password.encode("utf-8"), password.encode("utf-8")
        )
        if username_matches and password_matches:
            authenticated_account = account

    if authenticated_account is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return authenticated_account


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    with activity_lock:
        # Validate activity exists
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Get the specific activity
        activity = activities[activity_name]

        # Validate student is not already signed up
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student already signed up for this activity")

        # Validate activity is not full
        if len(activity["participants"]) >= activity["max_participants"]:
            raise HTTPException(status_code=400, detail="Activity is full")

        # Add student
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/participants")
def unregister_from_activity(
    activity_name: str,
    email: str,
    account: dict = Depends(get_unregister_account),
):
    """Unregister a student from an activity"""
    with activity_lock:
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")

        if account.get("role") != "staff" and account.get("email") != email:
            raise HTTPException(
                status_code=403,
                detail="You can only unregister your own account",
            )

        activity = activities[activity_name]

        if email not in activity["participants"]:
            raise HTTPException(
                status_code=404,
                detail="Student is not signed up for this activity",
            )

        activity["participants"].remove(email)
        return {"message": f"Unregistered {email} from {activity_name}"}
