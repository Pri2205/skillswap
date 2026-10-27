import os
import re
import secrets

from dotenv import load_dotenv
from flask import (Flask, abort, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()          # .env file se secrets padhta hai (local par)

import db              # load_dotenv ke BAAD import karna

app = Flask(__name__, static_folder="Static")
app.secret_key = os.environ.get("SECRET_KEY", "")
if not app.secret_key:
    raise RuntimeError("SECRET_KEY set nahi hai (.env file check karo)")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("RENDER") == "true",   # Render par https
)

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_RE = re.compile(r"^[6-9]\d{9}$")
SIGNUP_POINTS = 500


# ---------- chhote helpers ----------
@app.context_processor
def inject_globals():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return {
        "csrf_token": session["csrf_token"],
        "current_user": session.get("user_name"),
    }


def check_csrf():
    sent = request.form.get("csrf_token", "")
    if not sent or not secrets.compare_digest(sent, session.get("csrf_token", "")):
        abort(400)


def make_referral_code():
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"      # confusing letters nahi
    return "SS" + "".join(secrets.choice(letters) for _ in range(6))


def log_in(user):
    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["csrf_token"] = secrets.token_hex(16)


# ---------- database ready karo ----------
try:
    db.init_db()
except db.DBError as exc:
    print(f"[DB] Table setup nahi hua: {exc}")


# ---------- pages ----------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", form={}, notice="")

    check_csrf()
    form = request.form
    name = " ".join(form.get("name", "").split())
    email = form.get("email", "").strip().lower()
    phone = form.get("phone", "").strip()
    password = form.get("password", "")
    confirm = form.get("confirm", "")
    referral = form.get("referral", "").strip().upper()

    error = None
    if len(name) < 2:
        error = "Please enter your full name."
    elif not EMAIL_RE.match(email):
        error = "Please enter a valid email address."
    elif not PHONE_RE.match(phone):
        error = "Phone number must be 10 digits and start with 6, 7, 8 or 9."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."
    elif password != confirm:
        error = "Passwords do not match."

    referrer_id = None
    if not error and referral:
        try:
            referrer = db.one("SELECT id FROM users WHERE referral_code = ?", [referral])
        except db.DBError:
            referrer = None
        if referrer:
            referrer_id = referrer["id"]
        else:
            error = "That referral code is not valid. Leave it empty if you don't have one."

    if error:
        return render_template("register.html", form=form, notice=error), 400

    password_hash = generate_password_hash(password)
    try:
        for _ in range(5):                      # referral code takra jaye to dobara
            try:
                result = db.execute(
                    "INSERT INTO users (name, email, phone, password_hash, skillpoints, "
                    "referral_code, referred_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [name, email, phone, password_hash, SIGNUP_POINTS,
                     make_referral_code(), referrer_id],
                )
                break
            except db.UniqueError as exc:
                if exc.column == "email":
                    return render_template(
                        "register.html", form=form,
                        notice="An account with this email already exists. Try signing in."), 409
                if exc.column == "phone":
                    return render_template(
                        "register.html", form=form,
                        notice="An account with this phone number already exists. Try signing in."), 409
                # referral_code takraya -> loop dobara chalega
        else:
            raise db.DBError("referral code nahi ban paya")
    except db.DBError as exc:
        print(f"[DB] register failed: {exc}")
        return render_template(
            "register.html", form=form,
            notice="Something went wrong on our side. Please try again in a minute."), 500

    log_in({"id": result["last_id"], "name": name})
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", form={}, notice="")

    check_csrf()
    identifier = request.form.get("identifier", "").strip()
    password = request.form.get("password", "")

    try:
        if "@" in identifier:
            user = db.one("SELECT * FROM users WHERE email = ?", [identifier.lower()])
        else:
            user = db.one("SELECT * FROM users WHERE phone = ?", [identifier])
    except db.DBError as exc:
        print(f"[DB] login failed: {exc}")
        return render_template(
            "login.html", form=request.form,
            notice="Something went wrong on our side. Please try again in a minute."), 500

    if not user or not check_password_hash(user["password_hash"], password):
        return render_template(
            "login.html", form=request.form,
            notice="Incorrect email / phone or password."), 401

    log_in(user)
    return redirect(url_for("home"))


@app.route("/logout", methods=["POST"])
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)