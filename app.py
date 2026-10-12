import hmac
import os
import secrets
from flask import Flask, abort, render_template, request, session
from config import Config
from database.db import init_db
from routes.creator_routes import creator_bp
from routes.campaign_routes import campaign_bp
from routes.auth_routes import auth_bp, login_required


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true",
    )

    # Database helpers use Flask's current_app, so initialization
    # must run inside an application context.
    with app.app_context():
        init_db()

    @app.before_request
    def protect_post_requests():
        if request.method == "POST":
            expected = session.get("_csrf_token", "")
            submitted = request.form.get("csrf_token", "")
            if not expected or not hmac.compare_digest(expected, submitted):
                abort(400, description="Invalid or missing form security token. Refresh the page and try again.")

    @app.context_processor
    def inject_csrf_helper():
        def csrf_token():
            if "_csrf_token" not in session:
                session["_csrf_token"] = secrets.token_urlsafe(32)
            return session["_csrf_token"]
        return {"csrf_token": csrf_token}

    app.register_blueprint(creator_bp)
    app.register_blueprint(campaign_bp)
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        from database.db import get_db

        with get_db() as db:
            creators = db.execute(
                "SELECT * FROM creators ORDER BY engagement DESC LIMIT 3"
            ).fetchall()

        return render_template("index.html", creators=creators)

    @app.route("/brand-dashboard")
    @login_required
    def brand_dashboard():
        from database.db import get_db

        with get_db() as db:
            campaigns = db.execute(
                "SELECT campaigns.*, (SELECT COUNT(*) FROM campaign_shortlist s "
                "WHERE s.campaign_id = campaigns.id) AS shortlist_count "
                "FROM campaigns WHERE user_id = ? OR user_id IS NULL ORDER BY id DESC",
                (session["user_id"],)
            ).fetchall()
            stats = {
                "creators": db.execute(
                    "SELECT COUNT(*) FROM creators"
                ).fetchone()[0],
                "campaigns": db.execute(
                "SELECT COUNT(*) FROM campaigns WHERE user_id = ? OR user_id IS NULL",
                (session["user_id"],)
                ).fetchone()[0],
                "matches": db.execute(
                "SELECT COUNT(*) FROM campaign_matches m JOIN campaigns c ON c.id = m.campaign_id "
                "WHERE c.user_id = ? OR c.user_id IS NULL",
                (session["user_id"],)
                ).fetchone()[0],
            }

        return render_template(
            "brand_dashboard.html", campaigns=campaigns, stats=stats
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            render_template(
                "results.html",
                title="Page not found",
                message="The page you requested does not exist.",
                matches=[],
            ),
            404,
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
