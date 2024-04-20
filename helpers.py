from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime


def error_page(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("error.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# Checks date syntax
def valid_date(datestring):
    try:
        datetime.strptime(datestring, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# SQLITE3 HELPERS
# class SQL():
#     def __init__(self, database):
#         self.database = database

#     def SQL(database):

#     def execute(self, query, args=(), one=False):
#         cur = self.execute(query, args)
#         rv = cur.fetchall()
#         cur.close()
#         return (rv[0] if rv else None) if one else rv

