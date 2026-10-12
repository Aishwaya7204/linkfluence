# LinkFluence

LinkFluence is a Flask-based hackathon prototype for discovering content creators and matching them to brand campaign briefs.

## Features
- Creator directory with search and filters
- Creator profile pages
- Campaign brief creation
- Creator matching based on niche, platform, budget, follower target, and engagement
- Match score explanations showing the contribution of each matching factor
- Creator filters for location, audience size, engagement, and rate, with sorting
- Campaign-specific creator shortlists and side-by-side comparison
- Brand dashboard
- SQLite persistence
- Responsive HTML/CSS interface

## Tech stack
- Python and Flask
- SQLite
- HTML and Jinja templates
- CSS

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in the project folder.
3. Create and activate a virtual environment:

   Windows:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python app.py
   ```
6. Open `http://127.0.0.1:5000` in your browser.

The SQLite database is created automatically at `instance/linkfluence.db`; sample creators are inserted on first run. Existing databases are upgraded with the shortlist table automatically when the app starts.

## Demo flow
1. Create an account or log in.
2. Open **Discover Creators** and try the location, follower, engagement, and rate filters.
3. Create a campaign brief, for example Food + Instagram, budget ₹10,000, target 30,000 followers.
4. Expand **Why this match?** on a result to see the score components.
5. Save a couple of creators, open the shortlist, and compare at least two.
6. Open the dashboard to revisit campaign matches and saved shortlists.

Accounts use Werkzeug password hashing. Campaign pages and saved lists require login. This prototype does not yet include email verification, password reset, or third-party sign-in.

All creator profiles and figures are sample data. The ranking is a transparent heuristic, not a trained AI model or a guarantee of campaign performance.

## Deployment
### Deploy a public demo with Render
1. Push this project to GitHub, with `app.py` and `requirements.txt` at the repository root (or note the subfolder containing them).
2. In Render, choose **New > Web Service** and connect the repository.
3. Set the Root Directory to the folder containing `app.py` if it is not the repository root.
4. Set Build Command to `pip install -r requirements.txt` and Start Command to `gunicorn app:app`.
5. Add a strong random `SECRET_KEY` and set `SESSION_COOKIE_SECURE=true` in Render, then create the service and wait for the deploy to finish.
6. Open the generated `onrender.com` URL and test a creator page such as `/creator/5`.
7. Submit that public URL as the **Demo URL** in ByteXL. Keep the GitHub URL in the GitHub URL field.

The local SQLite database is suitable for a demo but is not persistent on a free Render service; saved campaigns can reset after a restart or redeploy. Free services may also take about a minute to wake after a period without traffic. Use a persistent database if the demo needs durable data.

## Current limitations
- Matching is a rule-based heuristic, not a trained AI model.
- Creator profiles and metrics are demo data, not verified.
- No authentication, payments, messaging, or live social-platform integrations.
- External profile images and Google Fonts need internet access.

## Folder structure
See the project folders for templates, routes, database, models, services, and docs.
