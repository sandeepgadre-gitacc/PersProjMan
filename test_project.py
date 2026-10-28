import pytest
from unittest.mock import patch
from werkzeug.security import generate_password_hash
from project import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        with app.app_context():
            yield client

@patch("project.getuserdata")
def test_login(mok_getuserdata,client):
    ## test_login_success(client)

    mok_getuserdata.return_value = [{
        "userid": 1,
        "username": "sandeep",
        "pwdhash": generate_password_hash("mypassword")
    }]

    response = client.post("/login", data={"username": "sandeep", "password": "mypassword"})

    # Should redirect to dashboard
    assert response.status_code == 302
    assert "/dashboard" in response.location

    # Check session values
    with client.session_transaction() as seshn:
        assert seshn["userid"] == 1
        assert seshn["username"] == "sandeep"

@patch("project.get_dashboard_data")
@patch("project.get_duetasks")
@patch("project.get_project_progress")
@patch("project.get_chart_summary")
def test_dashboard(mok_summary, mok_progress, mok_duetasks, mok_dashboard, client):

    # Mock DAL return values
    mok_dashboard.return_value = ([], 0, 0, 0)
    mok_duetasks.return_value = ([], [])
    mok_progress.return_value = []
    mok_summary.return_value = {}

    # Simulate logged-in user
    with client.session_transaction() as seshn:
        seshn["userid"] = 1
        seshn["username"] = "sandeep"

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"dashboard" in response.data.lower()


# ---------------------------
# 1. login_required test
# ---------------------------
def test_createproject_requires_login(client):
    response = client.get("/createproject/new/0", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.location


# ---------------------------
# 2. GET new project
# ---------------------------
def test_createproject_get_new(client):
    # Simulate logged-in user
    with client.session_transaction() as sess:
        sess["userid"] = 1
        sess["username"] = "sandeep"

    response = client.get("/createproject/new/0")

    assert response.status_code == 200
    assert b"project" in response.data.lower()   # template loads


# ---------------------------
# 3. GET update → redirect to /project
# ---------------------------
def test_createproject_get_update_redirect(client):
    with client.session_transaction() as sess:
        sess["userid"] = 1
        sess["username"] = "sandeep"

    response = client.get("/createproject/update/5", follow_redirects=False)

    assert response.status_code == 302
    assert "/project/update/5" in response.location


# ---------------------------
# 4. POST new project
# ---------------------------
@patch("project.insertupdate_project")
def test_createproject_post_new(mok_insert, client):
    with client.session_transaction() as sess:
        sess["userid"] = 1
        sess["username"] = "sandeep"

    response = client.post(
        "/createproject/new/0",
        data={"name": "My Project", "startdate": "2024-01-01", "duedate": "2024-02-01"},
        follow_redirects=False
    )

    # insertupdate_project(True, userid, name, startdate, duedate, 0)
    mok_insert.assert_called_once()

    assert response.status_code == 302
    assert "/dashboard" in response.location


# ---------------------------
# 5. POST update project
# ---------------------------
@patch("project.insertupdate_project")
def test_createproject_post_update(mok_insert, client):
    with client.session_transaction() as sess:
        sess["userid"] = 1
        sess["username"] = "sandeep"

    response = client.post(
        "/createproject/update/10",
        data={"name": "Updated Project", "startdate": "2024-01-01", "duedate": "2024-03-01"},
        follow_redirects=False
    )

    mok_insert.assert_called_once()

    assert response.status_code == 302
    assert "/dashboard" in response.location


# ---------------------------------------------------------
# 1. login_required
# ---------------------------------------------------------
def test_createupdatetask_requires_login(client):
    response = client.get("/createupdatetask/1/new/0/view", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.location


# ---------------------------------------------------------
# 2. GET new task
# ---------------------------------------------------------
@patch("project.getproject")
def test_createupdatetask_get_new_logged_in(mok_getproject, client):
    mok_getproject.return_value = [{
        "projectid": 1,
        "userid": 1,
        "projectname": "Test Project",
        "startdate": "2024-01-01",
        "duedate": "2024-12-31"
    }]

    with client.session_transaction() as sess:
        sess["userid"] = 1
        sess["username"] = "sandeep"

    response = client.get("/createupdatetask/1/new/0/view")

    assert response.status_code == 200
    assert b"task" in response.data.lower()


# ---------------------------------------------------------
# 3. GET update task
# ---------------------------------------------------------
@patch("project.getproject")
@patch("project.gettask")
def test_createupdatetask_get_update(mok_gettask, mok_getproject, client):
    mok_getproject.return_value = [{
        "projectid": 1,
        "userid": 1,
        "projectname": "Test Project",
        "startdate": "2024-01-01",
        "duedate": "2024-12-31"
    }]
    # gettask() returns a LIST of rows in the real DAL — the route does task_data[0],
    # so the mock must match that shape or you'll get a KeyError instead of a real assertion.
    mok_gettask.return_value = [{
        "taskid": 2,
        "title": "Existing Task",
        "taskdesc": "Some description",
        "taskstatus": "Todo",
        "taskpriority": "High",
        "duedate": "2024-01-01"
    }]

    with client.session_transaction() as sess:
        sess["userid"] = 1
        sess["username"] = "sandeep"

    response = client.get("/createupdatetask/1/update/2/view")

    assert response.status_code == 200
    assert b"existing task" in response.data.lower()


# ---------------------------------------------------------
# 4. POST new task
# ---------------------------------------------------------
@patch("project.getproject")
@patch("project.insertupdate_task")
def test_createupdatetask_post_new(mok_insert, mok_getproject, client):
    mok_getproject.return_value = [{
        "projectid": 1,
        "userid": 1,
        "projectname": "Test Project",
        "startdate": "2024-01-01",
        "duedate": "2024-12-31"
    }]

    with client.session_transaction() as sess:
        sess["userid"] = 1
        sess["username"] = "sandeep"

    response = client.post(
        "/createupdatetask/1/new/0/update",
        data={
            "title": "New Task",
            "taskstatus": "Open",
            "taskpriority": "Medium",
            "duedate": "2024-02-01"
        },
        follow_redirects=False
    )

    mok_insert.assert_called_once()

    assert response.status_code == 302
    assert "/project/update/1" in response.location


# ---------------------------------------------------------
# 5. POST update task
# ---------------------------------------------------------
@patch("project.getproject")
@patch("project.insertupdate_task")
def test_createupdatetask_post_update(mok_insert, mok_getproject, client):
    mok_getproject.return_value = [{
        "projectid": 1,
        "userid": 1,
        "projectname": "Test Project",
        "startdate": "2024-01-01",
        "duedate": "2024-12-31"
    }]

    with client.session_transaction() as sess:
        sess["userid"] = 1
        sess["username"] = "sandeep"

    response = client.post(
        "/createupdatetask/1/update/10/update",
        data={
            "title": "Updated Task",
            "taskstatus": "Done",
            "taskpriority": "Low",
            "duedate": "2024-03-01"
        },
        follow_redirects=False
    )

    mok_insert.assert_called_once()

    assert response.status_code == 302
    assert "/project/update/1" in response.location


# ---------------------------------------------------------
# 6. POST missing fields → validation failure
# ---------------------------------------------------------
@patch("project.getproject")
def test_createupdatetask_post_missing_fields(mok_getproject, client):
    mok_getproject.return_value = [{
        "projectid": 1,
        "userid": 1,
        "projectname": "Test Project",
        "startdate": "2024-01-01",
        "duedate": "2024-12-31"
    }]

    with client.session_transaction() as sess:
        sess["userid"] = 1
        sess["username"] = "sandeep"

    response = client.post(
        "/createupdatetask/1/new/0/view",
        data={"title": "", "taskstatus": "", "taskpriority": "", "duedate": ""},
        follow_redirects=True
    )

    # Matches the actual flash message in project.py's createupdatetask route
    assert b"Task title is required" in response.data
