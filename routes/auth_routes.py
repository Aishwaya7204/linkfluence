from functools import wraps
import sqlite3

from flask import (Blueprint, flash, redirect, render_template, session,
                   url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db
from flask import request

auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            flash("Please log in to access your campaign workspace.", "error")
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id") is not None:
        return redirect(url_for("brand_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not email or "@" not in email or len(email) > 254:
            flash("Enter a valid email address.", "error")
        elif len(password) < 8:
            flash("Use a password with at least 8 characters.", "error")
        elif password != confirm:
            flash("The passwords do not match.", "error")
        else:
            try:
                with get_db() as db:
                    cursor = db.execute(
                        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                        (email, generate_password_hash(password)),
                    )
                    user_id = cursor.lastrowid
                    # Existing demo campaigns from a pre-login database belong
                    # to the first account created after upgrading.
                    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1:
                        db.execute("UPDATE campaigns SET user_id = ? WHERE user_id IS NULL",
                                   (user_id,))
            except sqlite3.IntegrityError:
                flash("An account with that email may already exist.", "error")
            else:
                session.clear()
                session["user_id"] = user_id
                session["user_email"] = email
                flash("Your account is ready.", "success")
                return redirect(url_for("brand_dashboard"))

    return render_template("auth.html", mode="register")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id") is not None:
        return redirect(url_for("brand_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Email or password is incorrect.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            session["user_email"] = user["email"]
            flash("Welcome back.", "success")
            return redirect(url_for("brand_dashboard"))

    return render_template("auth.html", mode="login")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))
