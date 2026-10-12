from flask import Blueprint, render_template, request
from database.db import get_db

creator_bp = Blueprint("creators", __name__)

@creator_bp.route("/creators")
def creators():
    niche = request.args.get("niche", "").strip()
    platform = request.args.get("platform", "").strip()
    search = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    sort = request.args.get("sort", "engagement")
    try:
        min_followers = max(0, int(request.args.get("min_followers", "0") or 0))
        max_followers = max(0, int(request.args.get("max_followers", "0") or 0))
        min_engagement = max(0, float(request.args.get("min_engagement", "0") or 0))
        max_rate = max(0, float(request.args.get("max_rate", "0") or 0))
    except ValueError:
        min_followers, max_followers, min_engagement, max_rate = 0, 0, 0, 0

    sql = "SELECT * FROM creators WHERE 1=1"
    params = []
    if niche:
        sql += " AND niche = ?"
        params.append(niche)
    if platform:
        sql += " AND platform = ?"
        params.append(platform)
    if search:
        sql += " AND (name LIKE ? OR handle LIKE ? OR bio LIKE ?)"
        params.extend([f"%{search}%"] * 3)
    if location:
        sql += " AND location = ?"
        params.append(location)
    if min_followers:
        sql += " AND followers >= ?"
        params.append(min_followers)
    if max_followers:
        sql += " AND followers <= ?"
        params.append(max_followers)
    if min_engagement:
        sql += " AND engagement >= ?"
        params.append(min_engagement)
    if max_rate:
        sql += " AND rate <= ?"
        params.append(max_rate)
    sort_columns = {"engagement": "engagement DESC", "followers": "followers DESC",
                    "rate": "rate ASC", "name": "name COLLATE NOCASE ASC"}
    sql += " ORDER BY " + sort_columns.get(sort, sort_columns["engagement"])

    with get_db() as db:
        profiles = db.execute(sql, params).fetchall()
        niches = [r["niche"] for r in db.execute(
            "SELECT DISTINCT niche FROM creators ORDER BY niche"
        ).fetchall()]
        platforms = [r["platform"] for r in db.execute(
            "SELECT DISTINCT platform FROM creators ORDER BY platform"
        ).fetchall()]
        locations = [r["location"] for r in db.execute(
            "SELECT DISTINCT location FROM creators ORDER BY location"
        ).fetchall()]

    return render_template("creators.html", creators=profiles, niches=niches,
                           platforms=platforms, selected_niche=niche,
                           selected_platform=platform, q=search,
                           selected_location=location, locations=locations,
                           selected_sort=sort, min_followers=min_followers,
                           max_followers=max_followers,
                           min_engagement=min_engagement, max_rate=max_rate)

@creator_bp.route("/creator/<int:creator_id>")
def creator_profile(creator_id):
    with get_db() as db:
        creator = db.execute(
            "SELECT * FROM creators WHERE id = ?", (creator_id,)
        ).fetchone()
    if creator is None:
        return render_template("results.html", title="Creator not found",
                               message="This creator profile was not found.",
                               matches=[]), 404
    return render_template("creator_profile.html", creator=creator)
