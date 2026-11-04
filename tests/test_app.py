from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

from src.app import activities


def signup_url(activity_name):
    return f"/activities/{quote(activity_name)}/signup"


def participants_url(activity_name):
    return f"/activities/{quote(activity_name)}/participants"


def test_root_redirects_to_static_index(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_names = set(activities.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == expected_names
    for details in data.values():
        assert {"description", "schedule", "max_participants", "participants"} <= details.keys()


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"

    # Act
    response = client.post(signup_url(activity_name), params={"email": "a@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(email) == 1


def test_signup_full_activity_returns_400(client):
    # Arrange
    activity_name = "Basketball Team"
    activity = activities[activity_name]
    activity["participants"] = [
        f"student{i}@mergington.edu" for i in range(activity["max_participants"])
    ]
    email = "latecomer@mergington.edu"

    # Act
    response = client.post(signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
    assert email not in activity["participants"]


def test_concurrent_signups_do_not_exceed_capacity(client):
    # Arrange
    activity_name = "Basketball Team"
    activity = activities[activity_name]
    activity["participants"] = [
        f"student{i}@mergington.edu" for i in range(activity["max_participants"] - 1)
    ]
    emails = ["first@mergington.edu", "second@mergington.edu"]

    # Act
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(
                lambda email: client.post(signup_url(activity_name), params={"email": email}),
                emails,
            )
        )

    # Assert
    assert sorted(response.status_code for response in responses) == [200, 400]
    assert len(activity["participants"]) == activity["max_participants"]


def test_concurrent_signups_do_not_add_duplicate_participants(client):
    # Arrange
    activity_name = "Art Club"
    email = "newstudent@mergington.edu"

    # Act
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(
                lambda _: client.post(signup_url(activity_name), params={"email": email}),
                range(2),
            )
        )

    # Assert
    assert sorted(response.status_code for response in responses) == [200, 400]
    assert activities[activity_name]["participants"].count(email) == 1


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(participants_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_concurrent_unregistrations_return_not_found_after_first_removal(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(
                lambda _: client.delete(
                    participants_url(activity_name), params={"email": email}
                ),
                range(2),
            )
        )

    # Assert
    assert sorted(response.status_code for response in responses) == [200, 404]
    assert email not in activities[activity_name]["participants"]


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"

    # Act
    response = client.delete(participants_url(activity_name), params={"email": "a@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(participants_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
