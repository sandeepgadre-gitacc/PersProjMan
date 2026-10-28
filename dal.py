from cs50 import SQL
from helpers import get_utcdate

# Connect to database
db = SQL("sqlite:///ppt.db")


def get_dashboard_data(userid):
    """Fetches all projects and all tasks for a specific user."""

    # Query 1: Get all projects
    projects = db.execute(
        "SELECT * FROM projects WHERE userid = ? ORDER BY duedate DESC", (userid))


    total_projects = len(projects)

    completed_tasks = db.execute(
        "SELECT COUNT(tasks.taskid) as count FROM tasks JOIN projects ON tasks.projectid=projects.projectid WHERE projects.userid = ? AND tasks.taskstatus = 'Done'",
        (userid))[0]["count"]

    pending_tasks = db.execute(
        "SELECT COUNT(tasks.taskid) as count FROM tasks JOIN projects ON tasks.projectid=projects.projectid WHERE projects.userid = ? AND tasks.taskstatus != 'Done'",
        (userid) )[0]["count"]

    # Return as a tuple
    return projects, total_projects, completed_tasks, pending_tasks


def get_duetasks(userid):
    duesoon_tasks = db.execute(
        """
        SELECT tasks.* FROM tasks JOIN projects ON tasks.projectid=projects.projectid WHERE projects.userid = ?
        AND tasks.taskstatus != 'Done'
        AND tasks.duedate BETWEEN DATE('now', '+1 day') AND DATE('now', '+3 day')
        ORDER BY tasks.duedate
        """ , (userid)
    )
    overdue_tasks = db.execute(
        """
        SELECT tasks.* FROM tasks JOIN projects ON tasks.projectid=projects.projectid WHERE projects.userid = ?
        AND tasks.taskstatus != 'Done'
        AND tasks.duedate <= DATE('now')
        ORDER BY tasks.duedate DESC
        """ , (userid)
    )

    # Return as a tuple
    return duesoon_tasks, overdue_tasks


def get_project_progress(userid):

    progress = db.execute("""
        SELECT
        projects.projectid,
        projects.projectname,
        COUNT(tasks.taskid) AS progtotal_tasks,
        SUM(CASE WHEN tasks.taskstatus = 'Done' THEN 1 ELSE 0 END) AS progcompleted_tasks
        FROM projects LEFT JOIN tasks ON projects.projectid = tasks.projectid
        WHERE projects.userid = ? GROUP BY projects.projectid
        """, userid)

    return progress


def get_chart_data(userid):

    chartdata = db.execute("""SELECT tasks.taskstatus, COUNT(*) as count FROM tasks JOIN projects
                          ON tasks.projectid=projects.projectid
                          WHERE projects.userid = ? GROUP BY taskstatus""", userid)

    return chartdata

def get_chart_summary(userid):

    data = get_chart_data(userid)

    result = {"todo": 0, "inprog": 0, "done": 0}

    for row in data:
        if row["taskstatus"] == "Todo":
            result["todo"] = row["count"]
        elif row["taskstatus"] == "InProgress":
            result["inprog"] = row["count"]
        elif row["taskstatus"] == "Done":
            result["done"] = row["count"]

    return result


def insertupdate_project(isinsert, userid, projectname, startdt, duedt, projectid):
    if isinsert:
        db.execute(
                "INSERT INTO projects (userid, projectname, startdate, duedate) VALUES (?, ?, ?, ?)",
                userid,
                projectname,
                get_utcdate(startdt),
                get_utcdate(duedt)
                )
    else:
        db.execute(
                "UPDATE projects SET projectname=?, startdate=?, duedate=? WHERE projectid=?",
                projectname,
                get_utcdate(startdt),
                get_utcdate(duedt),
                projectid
                )


def removeproject(projectid, userid):

    db.execute(
            "DELETE FROM tasks where projectid = ? ", projectid
    )
    db.execute(
            "DELETE FROM projects where projectid = ? AND userid = ?", projectid, userid
     )



def getproject(projectid, userid):
    return db.execute(
        "SELECT * FROM projects where projectid = ? AND userid = ?", projectid, userid
    )


def gettasksforproject(projectid, userid):
    return db.execute(
        "SELECT tasks.* FROM tasks JOIN projects ON tasks.projectid = projects.projectid WHERE tasks.projectid = ? AND projects.userid = ?", projectid, userid
    )


def gettask(taskid, projectid):
    return db.execute("SELECT tasks.* FROM tasks tasks WHERE taskid=? AND projectid = ? ", taskid,projectid)


def insertupdate_task(isinsert, taskid, projectid, title, taskdesc, taskpriority, taskstatus, duedate):

    if isinsert:
        db.execute(
                """INSERT INTO tasks
                (projectid, title, taskdesc,taskpriority, taskstatus, duedate)
                VALUES (?, ?, ?, ?, ?, ?)""",projectid, title, taskdesc,taskpriority, taskstatus, get_utcdate(duedate))
    else:
        db.execute(
                """UPDATE tasks SET title = ?, taskdesc = ?,
                taskpriority = ?, taskstatus = ?, duedate = ?
                WHERE taskid = ?""", title, taskdesc,taskpriority, taskstatus, get_utcdate(duedate), taskid)


def removetask(taskid, projectid):

    db.execute("DELETE FROM tasks WHERE taskid = ? AND projectid = ?", taskid, projectid)


def adduser(username, hashedPW, email):

    db.execute("INSERT INTO users (username, pwdhash, useremail) VALUES (?, ?, ?)", username, hashedPW, email)


def getuserdata(username):

    return db.execute("SELECT * FROM users WHERE username = ?", username)

