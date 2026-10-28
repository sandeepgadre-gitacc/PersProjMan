# Smart Personal Project Tracker

## Video Demo

**Demo URL:** *(Add your CS50 demo video link here before submission.)*

------------------------------------------------------------------------

# Description

Smart Personal Project Tracker is a web application developed as my
**CS50 Python Final Project**. The application helps individual users
organize personal projects, manage tasks, monitor progress, and
visualize project status through an interactive dashboard.

Unlike a full-featured enterprise project management system, this
application focuses on simplicity. A user can register, log in securely,
create multiple projects, add tasks to each project, assign priorities
and due dates, update task status, and monitor overall progress from a
centralized dashboard.

The application is built using **Python**, **Flask**, **SQLite**,
**Bootstrap 5**, **Jinja2**, and **Chart.js**.

------------------------------------------------------------------------

# Features

-   Secure user registration and login
-   Password hashing using Werkzeug
-   Session-based authentication
-   Create, edit and delete projects
-   Create, edit and delete tasks
-   Task priorities
-   Due date management
-   Task status (Todo, In Progress, Done)
-   Dashboard with project statistics
-   Progress bars
-   Charts for task visualization
-   Complete user data isolation

------------------------------------------------------------------------

# Technology Stack

## Backend

-   Python
-   Flask
-   SQLite

## Frontend

-   HTML5
-   Bootstrap 5.3.2
-   Jinja2 Templates
-   Chart.js

------------------------------------------------------------------------

# Project Structure

``` text
project.py          Main Flask application
dal.py              Data Access Layer
helpers.py          Authentication helper functions
dbSchema.sql        Database schema
ppt.db              SQLite database
templates/          HTML templates
test_project.py     Unit tests
```

------------------------------------------------------------------------

# Application Design

The application follows a layered architecture.

**Presentation Layer**

Flask routes receive requests and render Jinja templates.

**Business Logic**

Application logic validates user input, controls navigation, and
coordinates database operations.

**Data Access Layer**

Database operations are separated into `dal.py`. Instead of embedding
SQL queries throughout the Flask routes, all database interactions are
centralized in one module. This improves readability, simplifies
maintenance, and makes future enhancements easier.

**Database**

SQLite stores users, projects, and tasks.

------------------------------------------------------------------------

# Frontend Design

The application uses **template inheritance**.

`layout.html` serves as the base template for every page. It includes:

-   Bootstrap 5.3.2 from the official CDN
-   Navigation layout
-   Shared page structure
-   Jinja template blocks
-   Embedded custom CSS for the application's layout

Rather than maintaining a separate stylesheet, custom styling is defined
within `layout.html`. The CSS creates a consistent interface using a
header, sidebar, and main work area while Bootstrap provides responsive
components such as buttons, cards, forms, tables, alerts, and progress
bars.

------------------------------------------------------------------------

# Database Design

The application stores information in three logical entities:

-   Users
-   Projects
-   Tasks

Relationships:

-   One user can own many projects.
-   One project can contain many tasks.
-   Users can access only their own projects and tasks.

------------------------------------------------------------------------

# Dashboard

The dashboard provides a quick overview of project activity by
displaying:

-   Total projects
-   Total tasks
-   Completed tasks
-   Overdue tasks
-   Progress bars
-   Graphical summaries using Chart.js

This allows users to understand project health without opening every
project individually.

------------------------------------------------------------------------

# Security

The application includes several security features:

-   Password hashing using Werkzeug
-   Flask sessions
-   Login protection for authenticated pages
-   User-specific database queries to prevent unauthorized access

------------------------------------------------------------------------

# Testing

Automated tests are included in `test_project.py` to verify important
functionality.

------------------------------------------------------------------------

# Design Decisions

Several design decisions influenced the final implementation:

-   Separating SQL into `dal.py` rather than embedding SQL in Flask
    routes.
-   Using template inheritance with `layout.html` to eliminate
    duplicated HTML.
-   Choosing Bootstrap instead of writing a complete custom CSS
    framework.
-   Using Chart.js to provide a more visual dashboard.

These decisions improved maintainability, readability, and the overall
user experience.

------------------------------------------------------------------------

# Future Enhancements

Possible future improvements include:

-   Email reminders
-   Calendar integration
-   File attachments
-   Team collaboration
-   Search and filtering
-   Dark mode
-   Mobile-friendly enhancements

------------------------------------------------------------------------

# Running the Project

Install the required Python packages and start the Flask application.

``` bash
flask run
```

Open the local server in your browser and register a new account.

------------------------------------------------------------------------

# Author

**Sandeep Gadre**

Developed as the **CS50 Python Final Project**.
