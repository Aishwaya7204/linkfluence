from database.db import get_db

def _score(creator, campaign):
    """Return a transparent heuristic score and its component breakdown."""
    niche = 35 if creator["niche"].lower() == campaign["niche"].lower() else 8
    platform = 25 if creator["platform"].lower() == campaign["platform"].lower() else 0
    budget = (20 if creator["rate"] <= campaign["budget"] else
              max(0, 20 * campaign["budget"] / creator["rate"]))
    if campaign["target_followers"] <= 0:
        audience = 15
    else:
        ratio = creator["followers"] / campaign["target_followers"]
        audience = 15 if 0.75 <= ratio <= 1.5 else (8 if ratio >= 0.5 else 3)
    engagement = min(5, max(0, creator["engagement"] * 0.7))
    breakdown = [
        {"label": "Niche fit", "score": round(niche, 1), "max": 35},
        {"label": "Platform fit", "score": round(platform, 1), "max": 25},
        {"label": "Budget fit", "score": round(budget, 1), "max": 20},
        {"label": "Audience fit", "score": round(audience, 1), "max": 15},
        {"label": "Engagement bonus", "score": round(engagement, 1), "max": 5},
    ]
    total = min(100, sum(part["score"] for part in breakdown))
    return round(total, 1), breakdown

def match_creators(campaign_id):
    with get_db() as db:
        campaign = db.execute(
            "SELECT * FROM campaigns WHERE id = ?", (campaign_id,)
        ).fetchone()
        if campaign is None:
            return []

        creators = db.execute("SELECT * FROM creators").fetchall()
        ranked = []
        for creator in creators:
            score, breakdown = _score(creator, campaign)
            ranked.append({"creator": creator, "score": score,
                           "breakdown": breakdown})

        ranked.sort(key=lambda item: item["score"], reverse=True)
        db.execute("DELETE FROM campaign_matches WHERE campaign_id = ?",
                   (campaign_id,))
        db.executemany("""
            INSERT INTO campaign_matches (campaign_id, creator_id, score)
            VALUES (?, ?, ?)
        """, [(campaign_id, item["creator"]["id"], item["score"])
              for item in ranked])
        db.commit()
        return ranked
