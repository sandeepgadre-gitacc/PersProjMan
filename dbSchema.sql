PRAGMA foreign_keys = ON;

CREATE TABLE users (
    userid INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    useremail TEXT NOT NULL UNIQUE,
    pwdhash TEXT NOT NULL
);

CREATE TABLE projects (
    projectid INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER NOT NULL,
    projectname TEXT NOT NULL,
    startdate DATE,
    duedate DATE,
    FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE
);

CREATE TABLE tasks (
    taskid INTEGER PRIMARY KEY AUTOINCREMENT,
    projectid INTEGER NOT NULL,
    title TEXT NOT NULL,
    taskdesc TEXT,
    taskpriority TEXT CHECK(taskpriority IN ('Low','Medium','High')) NOT NULL DEFAULT 'Medium',
    taskstatus TEXT CHECK(taskstatus IN ('Todo','InProgress','Done')) NOT NULL DEFAULT 'Todo',
    duedate DATE,
    FOREIGN KEY (projectid) REFERENCES projects(projectid) ON DELETE CASCADE
);
