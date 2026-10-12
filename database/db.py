import os
import sqlite3
from flask import current_app

def get_db():
    db_path = current_app.config["DATABASE_PATH"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS creators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                handle TEXT NOT NULL UNIQUE,
                niche TEXT NOT NULL,
                platform TEXT NOT NULL,
                followers INTEGER NOT NULL,
                engagement REAL NOT NULL,
                rate REAL NOT NULL,
                location TEXT NOT NULL,
                bio TEXT NOT NULL,
                image_url TEXT
            );
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_name TEXT NOT NULL,
                title TEXT NOT NULL,
                niche TEXT NOT NULL,
                platform TEXT NOT NULL,
                budget REAL NOT NULL,
                target_followers INTEGER NOT NULL,
                description TEXT NOT NULL,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS campaign_matches (
                campaign_id INTEGER NOT NULL,
                creator_id INTEGER NOT NULL,
                score REAL NOT NULL,
                PRIMARY KEY (campaign_id, creator_id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
                FOREIGN KEY (creator_id) REFERENCES creators(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS campaign_shortlist (
                campaign_id INTEGER NOT NULL,
                creator_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (campaign_id, creator_id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
                FOREIGN KEY (creator_id) REFERENCES creators(id) ON DELETE CASCADE
            );
        """)
        # Upgrade databases created by older project versions.
        campaign_columns = {row["name"] for row in db.execute(
            "PRAGMA table_info(campaigns)").fetchall()}
        if "user_id" not in campaign_columns:
            db.execute("ALTER TABLE campaigns ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL")
        if db.execute("SELECT COUNT(*) FROM creators").fetchone()[0] == 0:
            rows = [
                ("Ananya Sharma", "@ananya.creates", "Fashion", "Instagram", 45000, 5.8, 7000, "Hyderabad", "Fashion and everyday lifestyle creator.", "https://images.unsplash.com/photo-1534528741775-53994a69daeb"),
                ("Rahul Verma", "@rahul.tech", "Technology", "YouTube", 80000, 6.2, 15000, "Bengaluru", "Technology reviews, apps, and gadgets.", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e"),
                ("Meera Reddy", "@meera.food", "Food", "Instagram", 32000, 7.1, 5000, "Hyderabad", "Food discoveries, recipes, and restaurant reviews.", "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"),
                ("Arjun Kumar", "@arjun.fitness", "Fitness", "YouTube", 65000, 4.9, 12000, "Chennai", "Fitness routines, wellness, and healthy habits.", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d"),
                ("Priya Das", "@priya.lifestyle", "Lifestyle", "Instagram", 55000, 6.5, 9000, "Hyderabad", "Lifestyle, travel, beauty, and daily inspiration.", "https://images.unsplash.com/photo-1531123897727-8f129e1688ce"),
                ("Kiran Rao", "@kiran.gaming", "Gaming", "YouTube", 40000, 5.4, 8000, "Pune", "Gaming videos, streams, and game reviews.", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d")
            ]
            db.executemany("""
                INSERT INTO creators
                (name, handle, niche, platform, followers, engagement, rate, location, bio, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
