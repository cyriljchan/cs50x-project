import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, valid_date, error_page
from datetime import date, timedelta
from pandas import date_range
import random
from os import path


# Configure application
app = Flask(__name__)

# Connect to vertapp.db
ROOT = path.dirname(path.realpath(__file__))
db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
db.row_factory = sqlite3.Row

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show VetApp Frontpage"""

    # Query session user information
    db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pets WHERE client_id=?", (session["user_id"],))
    pets = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> to dicts

    if session["user_type"] == "client":
        cursor.execute("""SELECT schedules.*, pets.name, pets.species FROM schedules
                    LEFT JOIN pets ON pets.id == schedules.pet_id
                    WHERE pets.client_id=? AND schedules.date>=CURRENT_DATE
                    ORDER BY schedules.date, schedules.time""",
                    (session["user_id"],))
    else:
        cursor.execute("""SELECT schedules.*, pets.name, pets.species,
                       users.firstname, users.lastname FROM schedules
                       LEFT JOIN pets ON pets.id == schedules.pet_id
                       LEFT JOIN users on users.id == pets.client_id
                       WHERE schedules.dvm_id=? AND schedules.date>=CURRENT_DATE
                       ORDER BY schedules.date, schedules.time""",
                       (session["user_id"],))

    schedules = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> to dicts
    db.close()

    # Load the frontpage
    return render_template("index.html", pets=pets, schedules=schedules)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure fields are filled properly
        if not username:
            return error_page("must provide username", 403)
        if not password:
            return error_page("must provide password", 403)

        # Verify user login/password
        db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        rows = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> to dicts
        db.close()
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return error_page("invalid username and/or password", 403)

        # Save user as session
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        session["user_type"] = rows[0]["type"]
        flash("Logged in!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("User has logged out")
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register User"""

    types = ["dvm", "client"]

    # Submit user registration
    if request.method == "POST":
        type = request.form.get("type")
        license = request.form.get("license")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        contact = request.form.get("contact")

        # Ensure fields are filled correctly
        if not type or type not in types:
            return error_page("invalid user type")
        if type == "dvm" and not license:
            return error_page("invalid license number")
        if not username:
            return error_page("invalid username")
        if not password:
            return error_page("invalid password")
        if not confirmation or password != confirmation:
            return error_page("password not match")
        if not firstname:
            return error_page("must type first name")
        if not lastname:
            return error_page("must type last name")
        if not email:
            return error_page("must type email")
        if not contact:
            return error_page("must type contact")

        # Ensure username is not in use
        db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        rows = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> to dicts
        db.close()
        if rows:
            return error_page("username in use")

        else:
            with sqlite3.connect(path.join(ROOT, "vetapp.db")) as db:
                cursor = db.cursor()
                cursor.execute("""INSERT INTO users (type, license, username, hash, firstname, lastname, email, contact)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (type, license, username, generate_password_hash(password),
                               firstname, lastname, email, contact))
                db.commit()
            flash("Registered!")
            return redirect("/")

    # Load the register page
    return render_template("register.html", types=types)


@app.route("/profile")
@login_required
def profile():
    """Show Session User Profile"""

    # Query session user information
    db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
    rows = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> to dicts
    db.close()

    # Load profile page
    return render_template("profile.html", user=rows[0])


@app.route("/modify_profile", methods=["GET", "POST"])
@login_required
def modify_profile():
    """Edit user information"""

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        contact = request.form.get("contact")

        # Ensure fields are filled correctly
        if not username:
            return error_page("invalid username")
        if not email:
            return error_page("invalid email")
        if not contact:
            return error_page("invalid contact")

        # Update user information
        with sqlite3.connect(path.join(ROOT, "vetapp.db")) as db:
            cursor = db.cursor()
            cursor.execute("""UPDATE users SET username=?, email=?, contact=?
                           WHERE id=?""", (username, email, contact, session["user_id"],))

        # Redirect to profile page
        flash("Update successful!")
        return redirect("/profile")

    else:
        # Query session user information
        db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
        rows = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> into dicts
        db.close()

        # Load modify profile page
        return render_template("modify_profile.html", user=rows[0])


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change Password"""

    if request.method == "POST":
        password = request.form.get("password")
        new_password = request.form.get("new_password")
        new_confirmation = request.form.get("new_confirmation")

        # Ensure forms are filled correctly
        db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("SELECT hash FROM users WHERE id=?", (session["user_id"],))
        rows = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> to dicts
        db.close()

        if not check_password_hash(rows[0]["hash"], password):
            return error_page("invalid password")
        if not new_password:
            return error_page("invalid new password")
        if not new_confirmation or new_password != new_confirmation:
            return error_page("new password not match")

        # Change password
        with sqlite3.connect(path.join(ROOT, "vetapp.db")) as db:
            cursor = db.cursor()
            cursor.execute("UPDATE users SET hash=? WHERE id=?",
                           (generate_password_hash(new_password), session["user_id"],))

        # Redirect to profile
        flash("Password changed successfully!")
        return redirect("/profile")

    # Load Change Password page
    else:
        return render_template("change_password.html")


@app.route("/pets")
@login_required
def pets():
    """Session User Pets"""

    # Query user pet information
    db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pets WHERE client_id=?", (session["user_id"],))
    rows = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> to dicts
    db.close()

    # Load pets page
    return render_template("pets.html", pets=rows)


@app.route("/add_pet", methods=["GET", "POST"])
@login_required
def add_pet():
    """Add pet to the pets table"""

    # Submit pet information
    if request.method == "POST":
        name = request.form.get("name")
        birthdate = request.form.get("birthdate")
        species = request.form.get("species")
        breed = request.form.get("breed")
        pattern = request.form.get("pattern")

        if not name:
            return error_page("invalid name")
        if not birthdate or not valid_date(birthdate):
            return error_page("invalid birthdate")
        if not species:
            return error_page("invalid species")
        if not breed:
            return error_page("invalid breed")
        if not pattern:
            return error_page("invalid color, markings, patterns")

        # INSERT into pets table
        with sqlite3.connect(path.join(ROOT, "vetapp.db")) as db:
            cursor = db.cursor()
            cursor.execute("""INSERT INTO pets (client_id, name, birthdate, species, breed, pattern)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                           (session["user_id"], name, birthdate, species, breed, pattern))
            db.commit()

        # Redirect to pets page
        flash(f"{name} has been added!")
        return redirect("/pets")

    # Load add pets page
    else:
        return render_template("add_pet.html")


@app.route("/modify_pet", methods=["POST"])
@login_required
def modify_pet():
    """Modify pet data"""

    id = request.form.get("id")
    db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pets WHERE client_id=? and id=?",
                    (session["user_id"], id,))
    rows = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> to dicts
    db.close()

    # Load edit pets page
    return render_template("modify_pet.html", pet=rows[0])


@app.route("/rm_pet", methods=["POST"])
@login_required
def rm_pet():
    """Remove pet from the pets table"""

    # DELETE from pets
    id = request.form.get("id")
    with sqlite3.connect(path.join(ROOT, "vetapp.db")) as db:
        cursor = db.cursor()
        cursor.execute("""DELETE FROM pets WHERE client_id == ? AND id == ?""",
                       (session["user_id"], id))
        db.commit()

    flash("Remove success!")
    return redirect("/pets")


@app.route("/edit_pet", methods=["POST"])
@login_required
def edit_pet():
    """Edit pet information"""

    # Submit updated pet information
    id = request.form.get("id")
    name = request.form.get("name")
    birthdate = request.form.get("birthdate")
    species = request.form.get("species")
    breed = request.form.get("breed")
    pattern = request.form.get("pattern")

    if not name:
        return error_page("invalid name")
    if not birthdate or not valid_date(birthdate):
        return error_page("invalid birthdate")
    if not species:
        return error_page("invalid species")
    if not breed:
        return error_page("invalid breed")
    if not pattern:
        return error_page("invalid color, markings, patterns")

    # UPDATE pets table
    with sqlite3.connect(path.join(ROOT, "vetapp.db")) as db:
        cursor = db.cursor()
        cursor.execute("""UPDATE pets SET name=?, birthdate=?, species=?, breed=?, pattern=?
                    WHERE client_id == ? AND id == ?""",
                    (name, birthdate, species, breed, pattern, session["user_id"], id))
        db.commit()

    # Redirect to pets page
    flash("Update success!")
    return redirect("/pets")


@app.route("/vaccines", methods=["POST"])
@login_required
def vaccines():
    """Show Pet Vaccine Records"""

    id = request.form.get("id")

    # Query vaccine records for pet
    db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("""SELECT name FROM pets WHERE id=?""", (id,))
    pets = [dict(row) for row in cursor.fetchall()]

    cursor.execute("""SELECT vaccines.*, pets.name,
                   users.firstname, users.lastname FROM vaccines
                   LEFT JOIN pets ON pets.id=vaccines.pet_id
                   LEFT JOIN users ON users.id=vaccines.dvm_id
                   WHERE vaccines.pet_id=?""", (id,))
    vaccines = [dict(row) for row in cursor.fetchall()]

    return render_template("vaccines.html", pets=pets[0], vaccines=vaccines)


@app.route("/clients")
@login_required
def clients():
    """Show Client Records"""

    # Query All Existing Clients and Pets
    db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM users WHERE type='client'""")
    clients = [dict(row) for row in cursor.fetchall()]  # Change <sql.Rows obj> to dicts

    cursor.execute("""SELECT * FROM pets""")
    pets = [dict(row) for row in cursor.fetchall()]  # Change <sql.Rows obj> to dicts
    db.close()

    return render_template("clients.html", clients=clients, pets=pets)



@app.route("/schedules")
@login_required
def schedules():
    """Show Session User Schedule"""

    # Query schedules
    db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    if session["user_type"] == "client":
        cursor.execute("""SELECT schedules.*, pets.name AS pet_name,
                    users.lastname AS dvm_name FROM schedules
                    LEFT JOIN pets ON pets.id == schedules.pet_id
                    LEFT JOIN users ON users.id == schedules.dvm_id
                    WHERE pets.client_id=?
                    ORDER BY schedules.date DESC, schedules.time""", (session["user_id"],))
    else:
        cursor.execute("""SELECT schedules.*, pets.name AS pet_name,
                    users.lastname AS dvm_name FROM schedules
                    LEFT JOIN pets ON pets.id == schedules.pet_id
                    LEFT JOIN users ON users.id == schedules.dvm_id
                    WHERE schedules.dvm_id=?
                    ORDER BY schedules.date, schedules.time""", (session["user_id"],))

    schedules = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> to dicts
    db.close()

    return render_template("schedules.html", schedules=schedules)

@app.route("/add_schedule", methods=["GET", "POST"])
@login_required
def add_schedule():
    """Add Schedule"""

    # Submit schedule information
    if request.method == "POST":
        day = request.form.get("date")
        time = request.form.get("time")
        pet_id = request.form.get("pet_id")
        purpose = request.form.get("purpose")

        if not day:
            return error_page("invalid date")
        if not time:
            return error_page("invalid time")
        if not pet_id:
            return error_page("invalid pet_name")
        if not purpose:
            return error_page("invalid purpose")

        # RANDOM DVM ID
        db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE type='dvm'")
        dvm_ids = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> to dicts
        dvm_id = random.choice(dvm_ids)['id']

        # INSERT into schedules table
        with sqlite3.connect(path.join(ROOT, "vetapp.db")) as db:
            cursor = db.cursor()
            cursor.execute("""INSERT INTO schedules (dvm_id, pet_id, date, time, purpose)
                           VALUES (?, ?, ?, ?, ?)""",
                           (dvm_id, pet_id, day, time, purpose))
            db.commit()

        # Redirect to pets page
        flash("Schedule has been added!")
        return redirect("/schedules")

    else:

        # Query pet names
        db = sqlite3.connect(path.join(ROOT, "vetapp.db"))
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("SELECT id, name FROM pets WHERE client_id=?", (session["user_id"],))
        pets = [dict(row) for row in cursor.fetchall()] # Change <sql.Rows obj> to dicts

        # Query scheduled datetimes
        cursor = db.cursor()
        cursor.execute("SELECT date, time FROM schedules WHERE date >= CURRENT_DATE")

        # Create {date:[time]} dict from query
        scheduled = {}
        for row in cursor.fetchall():
            if row["date"] not in scheduled:
                scheduled[row["date"]] = [row["time"]]
            else:
                scheduled[row["date"]].append(row["time"])
        db.close()

        # Create {date:[time]} dict from datetime
        days = [(date.today() + timedelta(days=add)).strftime("%Y-%m-%d") for add in range(7)]
        times = [t.strftime("%H:%M:%S") for t in date_range("9:00", "18:00", freq="30min").time]
        timeslots = {day:times[:] for day in days}

        # Filter out scheduled dates
        for day in scheduled:
            timeslots[day] = [time for time in timeslots[day] if time not in scheduled[day]]

        # Load add schedule page
        return render_template("add_schedule.html", pets=pets, timeslots=timeslots)

# DB CREATION
# CREATE TABLE users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#     type TEXT NOT NULL,
#     license TEXT NULL,
#     username TEXT NOT NULL,
#     hash TEXT NOT NULL,
#     firstname TEXT NOT NULL,
#     lastname TEXT NOT NULL,
#     email TEXT NOT NULL,
#     contact TEXT NOT NULL
# );

# CREATE TABLE pets (
#     id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#     client_id INTEGER NOT NULL,
#     name TEXT NOT NULL,
#     birthdate TEXT NULL,
#     species TEXT NOT NULL,
#     breed TEXT NOT NULL,
#     pattern TEXT NOT NULL
# );

# CREATE TABLE schedules (
#     id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#     dvm_id INTEGER NOT NULL,
#     pet_id INTEGER NOT NULL,
#     date TEXT NOT NULL,
#     time TEXT NOT NULL,
#     complaint TEXT NOT NULL
# );

# CREATE TABLE vaccines (
#     id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#     pet_id INTEGER NOT NULL,
#     dvm_id INTEGER NOT NULL,
#     vaccine TEXT NOT NULL,
#     date TEXT NOT NULL
# );