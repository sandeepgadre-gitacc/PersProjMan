from functools import wraps
from flask import redirect, session
from datetime import datetime, timezone

# Decorator to require a login
def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get("userid") is None:
            return redirect("/login")
        return func(*args, **kwargs)
    return decorated_function



def get_utcdate(date_str):
    # date_str = "2026-07-05"
    if not date_str:
        return None

    local_dt = datetime.fromisoformat(date_str)
    # treat as UTC
    utc_dt = local_dt.replace(tzinfo=timezone.utc)
    # "YYYY-MM-DD"
    return utc_dt.date().isoformat()

