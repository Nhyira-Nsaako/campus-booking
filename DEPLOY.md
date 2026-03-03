# Deployment Guide — Campus Facility Booking System v2

## Prerequisites
- Git installed (`git --version`)
- A [GitHub](https://github.com) account
- A [Render](https://render.com) account (free, no credit card required)
- Python 3.8+ installed locally

---

## Step 1 — Test Locally First

```bash
# Navigate into the project
cd campus-booking

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
# → http://localhost:5000
```

**Demo credentials:**
| Email | Password | Role |
|-------|----------|------|
| kwame.mensah@ug.edu.gh | student123 | Student |
| ama.asante@ug.edu.gh | staff123 | Staff |
| kofi.boateng@ug.edu.gh | admin123 | Admin |

---

## Step 2 — Push to GitHub

### 2a. Create a new GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Name it `campus-booking` (or anything you like)
3. Set to **Public** or **Private**
4. **Do NOT** initialise with a README (we'll push our own)
5. Click **Create repository**

### 2b. Initialise Git and push

Open your terminal inside the `campus-booking/` folder:

```bash
# Initialise a git repository
git init

# Stage all files
git add .

# Create first commit
git commit -m "feat: initial commit — campus booking system with auth"

# Add GitHub as the remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/campus-booking.git

# Push to main branch
git branch -M main
git push -u origin main
```

> **Tip:** If Git asks for credentials, use your GitHub username and a
> [Personal Access Token](https://github.com/settings/tokens) (not your password).

---

## Step 3 — Deploy on Render (Free)

### 3a. Connect your repo

1. Go to [render.com](https://render.com) and sign in
2. Click **New → Web Service**
3. Click **Connect a repository** and authorise GitHub
4. Select your `campus-booking` repository
5. Click **Connect**

### 3b. Configure the service

Render will auto-detect the `render.yaml`. Verify these settings:

| Setting | Value |
|---------|-------|
| **Name** | campus-booking |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | Free |

Click **Create Web Service**.

### 3c. Wait for deployment

Render will build and deploy your app (usually 2–4 minutes).
Your app will be live at: `https://campus-booking.onrender.com`

### 3d. First visit — DB initialisation

On the first request, the SQLite database is auto-created with seed data.
Visit `https://your-app.onrender.com/api/health` to verify the server is running.

---

## ⚠️ Important: SQLite on Render Free Tier

Render's free tier uses an **ephemeral filesystem** — the SQLite `.db` file
is deleted on each redeploy or restart. This means:
- Seed data is re-created on each restart ✅
- Any new users/bookings you created are lost on restart ❌

**For persistent data:** Add a free PostgreSQL database on Render and update
`config/database.py` to use `psycopg2` with the `DATABASE_URL` environment variable.

---

## Step 4 — Environment Variables (Optional)

To set the database path or any secrets, add env vars in Render:

1. Go to your service → **Environment**
2. Add key: `DATABASE_PATH`, value: `/tmp/campus_booking.db`

---

## Future Updates — Push & Redeploy

After making code changes:

```bash
git add .
git commit -m "fix: describe your change here"
git push origin main
```

Render auto-deploys every time you push to `main`. ✅

---

## Why NOT Vercel?

Vercel is a **serverless/static** platform. It **does not support**:
- Long-running Python WSGI servers (gunicorn/Flask)
- Persistent file writes (SQLite)
- Traditional Flask routing

Use **Render** or **Railway** instead — both are free and designed for full-stack Python apps.

