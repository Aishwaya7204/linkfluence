import math
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import get_db
from services.matching_service import match_creators
from routes.auth_routes import login_required

campaign_bp = Blueprint("campaigns", __name__)

@campaign_bp.route("/create-brief", methods=["GET", "POST"])
@login_required
def create_brief():
    if request.method == "POST":
        brand_name = request.form.get("brand_name", "").strip()
        title = request.form.get("title", "").strip()
        niche = request.form.get("niche", "").strip()
        platform = request.form.get("platform", "").strip()
        description = request.form.get("description", "").strip()

        try:
            budget = float(request.form.get("budget", "0"))
            target_followers = int(request.form.get("target_followers", "0"))
        except ValueError:
            flash("Enter a valid budget and follower target.", "error")
            return redirect(url_for("campaigns.create_brief"))

        if not all([brand_name, title, niche, platform, description]):
            flash("Please complete all fields.", "error")
            return redirect(url_for("campaigns.create_brief"))
        if not math.isfinite(budget) or budget <= 0 or target_followers < 0:
            flash("Budget must be positive and followers cannot be negative.", "error")
            return redirect(url_for("campaigns.create_brief"))

        with get_db() as db:
            cursor = db.execute("""
                INSERT INTO campaigns
                (brand_name, title, niche, platform, budget,
                 target_followers, description, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (brand_name, title, niche, platform, budget,
                  target_followers, description, session["user_id"]))
            campaign_id = cursor.lastrowid
            db.commit()

        matches = match_creators(campaign_id)
        return render_template("results.html", title="Your creator matches",
                               message=f"Found {len(matches)} potential creators for {title}.",
                               matches=matches, campaign_id=campaign_id,
                               shortlisted_ids=set())

    return render_template("create_brief.html")

@campaign_bp.route("/campaign/<int:campaign_id>/matches")
@login_required
def campaign_matches(campaign_id):
    with get_db() as db:
        campaign = db.execute(
            "SELECT * FROM campaigns WHERE id = ? AND (user_id = ? OR user_id IS NULL)",
            (campaign_id, session["user_id"])
        ).fetchone()
        shortlisted_ids = {row["creator_id"] for row in db.execute(
            "SELECT creator_id FROM campaign_shortlist WHERE campaign_id = ?",
            (campaign_id,)).fetchall()}
    if campaign is None:
        return render_template("results.html", title="Campaign not found",
                               message="This campaign does not exist.", matches=[]), 404
    matches = match_creators(campaign_id)
    return render_template("results.html", title="Creator matches",
                           message=f"Matches for {campaign['title']}.",
                           matches=matches, campaign_id=campaign_id,
                           shortlisted_ids=shortlisted_ids)

@campaign_bp.route("/campaign/<int:campaign_id>/shortlist", methods=["GET", "POST"])
@login_required
def campaign_shortlist(campaign_id):
    if request.method == "POST":
        creator_id = request.form.get("creator_id", type=int)
        action = request.form.get("action", "save")
        with get_db() as db:
            exists = db.execute("SELECT id FROM campaigns WHERE id = ? AND (user_id = ? OR user_id IS NULL)",
                                (campaign_id, session["user_id"])).fetchone()
            creator = db.execute("SELECT id FROM creators WHERE id = ?",
                                 (creator_id,)).fetchone() if creator_id else None
            if not exists or not creator:
                return "Campaign or creator not found", 404
            if action == "remove":
                db.execute("DELETE FROM campaign_shortlist WHERE campaign_id = ? AND creator_id = ?",
                           (campaign_id, creator_id))
                flash("Creator removed from shortlist.", "success")
            else:
                db.execute("INSERT OR IGNORE INTO campaign_shortlist (campaign_id, creator_id) VALUES (?, ?)",
                           (campaign_id, creator_id))
                flash("Creator saved to this campaign shortlist.", "success")
        return redirect(url_for("campaigns.campaign_matches", campaign_id=campaign_id))

    with get_db() as db:
        campaign = db.execute("SELECT * FROM campaigns WHERE id = ? AND (user_id = ? OR user_id IS NULL)",
                              (campaign_id, session["user_id"])).fetchone()
        if campaign is None:
            return "Campaign not found", 404
        creators = db.execute("""
            SELECT c.*, s.created_at FROM campaign_shortlist s
            JOIN creators c ON c.id = s.creator_id
            WHERE s.campaign_id = ? ORDER BY c.name COLLATE NOCASE
        """, (campaign_id,)).fetchall()
    return render_template("shortlist.html", campaign=campaign, creators=creators)

@campaign_bp.route("/campaign/<int:campaign_id>/compare")
@login_required
def compare_creators(campaign_id):
    selected = request.args.getlist("creator_id", type=int)
    with get_db() as db:
        campaign = db.execute("SELECT * FROM campaigns WHERE id = ? AND (user_id = ? OR user_id IS NULL)",
                              (campaign_id, session["user_id"])).fetchone()
        if campaign is None:
            return "Campaign not found", 404
        saved = db.execute("""
            SELECT c.* FROM campaign_shortlist s JOIN creators c ON c.id = s.creator_id
            WHERE s.campaign_id = ? ORDER BY c.name COLLATE NOCASE
        """, (campaign_id,)).fetchall()
        if selected:
            selected = list(dict.fromkeys(selected))[:4]
            placeholders = ",".join("?" for _ in selected)
            creators = db.execute(f"""
                SELECT c.* FROM campaign_shortlist s JOIN creators c ON c.id = s.creator_id
                WHERE s.campaign_id = ? AND c.id IN ({placeholders})
                ORDER BY c.name COLLATE NOCASE
            """, [campaign_id, *selected]).fetchall()
        else:
            creators = []
    return render_template("compare.html", campaign=campaign,
                           saved=saved, creators=creators)
