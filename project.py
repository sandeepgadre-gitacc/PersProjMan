from flask import Flask, render_template, request, redirect, session, url_for
from flask import flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required
from dal import get_dashboard_data, get_project_progress, get_chart_data, get_duetasks
from dal import insertupdate_project, removeproject, getproject, gettasksforproject, gettask, insertupdate_task, removetask, adduser, getuserdata, get_chart_summary


# Initiate app
app = Flask(__name__)

# Configure session
import os
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-me")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_USE_SIGNER"] = True   # signs the session-id cookie
Session(app)

@app.route("/")
def index():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def registeruser():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        email = request.form.get("email")

        # Validate input
        if not username or not password or not email or not confirm :
            flash("All fields are required", "warning")
            return redirect(request.url)

        if password != confirm:
            flash("Passwords do not match", "warning")
            return redirect(request.url)

        # Hash password
        hashedPW = generate_password_hash(password)

        # Insert user into DB
        try:
            adduser(username, hashedPW, email)
        except RuntimeError:
            flash("Username or email already exists", "danger")
            return redirect("/register")

        # Registration successful - goto Login
        return redirect("/login")

    # If GET Method
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please provide username and password", "warning")
            return redirect("/login")

        # Query user
        rows = getuserdata(username)

        if len(rows) != 1 or not check_password_hash(rows[0]["pwdhash"], password):
            flash("Invalid username or password", "danger")
            return redirect("/login")


        # Remember which user has logged in
        session["userid"] = rows[0]["userid"]
        session["username"] = username

        return redirect("/dashboard")
    else:
        #IF not POST
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    userid = session["userid"]
    uname = session["username"]

    user_projects, total_projects,completed_tasks, pending_tasks = get_dashboard_data(userid)
    duesoon_tasks, overdue_tasks = get_duetasks(userid)
    project_progress = get_project_progress(userid)

    # Get data for Chart
    statcount = get_chart_summary(userid)

    return render_template("dashboard.html",
                           projects=user_projects,
                           totalprojects=total_projects,
                           completedtasks=completed_tasks,
                           pendingtasks=pending_tasks,
                           duesoon=duesoon_tasks,
                           overdue=overdue_tasks,
                           projectprogress = project_progress,
                           statcount=statcount
                           )


@app.route("/createproject/<string:operate>/<int:projectid>", methods=["GET", "POST"])
@login_required
def createproject(operate, projectid):

    if request.method == "POST":

        name = request.form.get("name")
        startdate = request.form.get("startdate")
        duedate = request.form.get("duedate")

        if not name:
            flash("Project name is required", "warning")
            return redirect(request.url)

        if operate == "update":
            insertupdate_project(False, session["userid"], name, startdate, duedate, projectid)
        else:
            insertupdate_project(True, session["userid"], name, startdate, duedate,0)

        return redirect("/dashboard")
    else:
        if operate == 'new':
            project={}
            return render_template("project.html", operate="new", project=project, tasks={})
        else:
            return redirect(url_for("project", operate=operate, projectid=projectid))


@app.route("/deleteproject/<int:projectid>", methods=["POST"])
@login_required
def deleteproject(projectid):

    if not projectid:
        return "Project id required", 400

    # Ensure project belongs to user
    project = getproject(projectid, session["userid"])

    if not project:
        return "Unauthorized - project does not belong to user", 403

    removeproject(projectid,session["userid"])

    return redirect("/dashboard")



@app.route("/project/<string:operate>/<int:projectid>", methods=["GET", "POST"])
@login_required
def project(operate, projectid):

    if not projectid:
        return "Project id required", 400

    project = getproject(projectid, session["userid"])

    if not project:
        return "Project not found", 404

    # Get tasks for this project
    tasks = gettasksforproject(projectid, session["userid"])
    return render_template("project.html", operate=operate, project=project[0], tasks=tasks)


@app.route("/createupdatetask/<int:projectid>/<string:operate>/<int:taskid>/<string:projoperate>", methods=["GET", "POST"])
@login_required
def createupdatetask(projectid, operate, taskid, projoperate):

    # Ensure project belongs to user
    project = getproject(projectid, session["userid"])

    if not project:
        return "Unauthorized - project does not belong to user", 403

    if request.method == "POST":
        if operate in ["new", "update"]:
            title = request.form.get("title")
            taskdesc = request.form.get("taskdesc")
            taskpriority = request.form.get("taskpriority")
            taskstatus = request.form.get("taskstatus")
            duedate = request.form.get("duedate")
            if not title:
                flash("Task title is required", "warning")
                return redirect(request.url)
        else:

            tasks = gettask(taskid, projectid)
            if not tasks:
                return "Task not found", 404
            task = tasks[0]
            title = task["title"]
            taskdesc = task["taskdesc"]
            taskpriority = task["taskpriority"]
            taskstatus = task["taskstatus"]
            duedate = task["duedate"]

        if operate == "new":
            insertupdate_task(True, 0, projectid, title, taskdesc,taskpriority, taskstatus, duedate)
        elif operate == "update":
            insertupdate_task(False, taskid, projectid, title, taskdesc,taskpriority, taskstatus, duedate)

        if operate == "view":
            return render_template("task.html", operate="view", task = task, projectid=projectid, projoperate=projoperate)
        else:
            return redirect(url_for("project", operate=projoperate, projectid=projectid))

    else: #POST is FALSE
        if operate in ["view", "update"]:
            # Fetch the task details
            task_data = gettask(taskid, projectid)
            if not task_data:
                return "Task not found", 404

            # Show the task page
            return render_template("task.html", operate=operate, projectid=projectid, task=task_data[0], projoperate=projoperate)

        # Handle 'new' task mode
        return render_template("task.html", operate="new", projectid=projectid, task={}, projoperate=projoperate)


@app.route("/deletetask/<int:projectid>/<int:taskid>", methods=["POST"])
@login_required
def deletetask(projectid, taskid):

    project = getproject(projectid, session["userid"])
    if not project:
        return "Unauthorized - project does not belong to user", 403

    removetask(taskid, projectid)

    return redirect(f"/project/view/{projectid}")


@app.context_processor
def fillsummary():
    if "userid" in session:
        user_projects, total_projects, completed_tasks, pending_tasks = get_dashboard_data(session["userid"])

        return dict(
            totalprojects=total_projects,
            completedtasks=completed_tasks,
            pendingtasks=pending_tasks
        )

    return dict(
        totalprojects=0,
        completedtasks=0,
        pendingtasks=0
    )


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


#+++++=====+++++=====+++++#
def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()

