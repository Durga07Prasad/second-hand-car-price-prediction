# 🚀 CarValueAI — Deployment Guide

Complete instructions for deploying the Second-Hand Car Price Prediction platform
(FastAPI backend + React frontend) using Docker, Render, or Railway.

---

## 📁 Project Structure (Deployment-Relevant)

```
CarPricePrediction/
├── backend/
│   ├── Dockerfile            # Python 3.11 + FastAPI
│   ├── .dockerignore
│   ├── render.yaml           # Render blueprint (Docker web service)
│   ├── requirements.txt
│   └── app_models/           # ML artifacts (~2.8MB total)
├── frontend/
│   ├── Dockerfile            # Multi-stage: Node build → Nginx serve
│   ├── .dockerignore
│   ├── nginx.conf            # SPA fallback + gzip
│   └── render.yaml           # Render blueprint (static site)
├── docker-compose.yml        # Local dev: both services
├── railway.json              # Railway config (backend)
└── DEPLOYMENT.md             # ← You are here
```

---

## 1️⃣ Local Docker Build & Test

### Prerequisites
- Docker Desktop installed and running
- Ports 8000 and 5173 available

### Build & Start

```bash
docker-compose up --build
```

**WAIT** for both containers to report ready in the logs:
- Backend: `INFO: Uvicorn running on http://0.0.0.0:8000`
- Frontend: `nginx ... start worker processes`

### Test Backend

```bash
# Health check — must return {"status":"healthy","model_loaded":true,...}
curl http://localhost:8000/health

# Swagger UI — open in browser
open http://localhost:8000/docs
```

### Test Frontend

Open **http://localhost:5173** in your browser and manually verify:

- [ ] **Home page** loads with hero section and animated stats
- [ ] **Predict page**: Submit a test car → prediction price + SHAP chart appear
- [ ] **Dashboard/Analytics page** loads with feature importance chart
- [ ] **History page** shows the test prediction you just made
- [ ] **Feedback** submission works (if feedback UI exists)

### Troubleshooting

> **Frontend can't reach the backend?**
>
> `VITE_API_URL` is baked into the JS bundle at **build time**. Since the frontend
> runs in your **browser** (not container-to-container), it needs to reach the
> backend via `http://localhost:8000` — which works because Docker exposes port 8000
> on the host. This is already configured in `docker-compose.yml`.
>
> If you change the backend port, rebuild the frontend:
> ```bash
> docker-compose build --no-cache frontend
> ```

### ⛔ DO NOT proceed to cloud deployment until ALL checks above pass.

---

## 2️⃣ Render — Backend Deployment

### Steps

1. **Push code to GitHub** (if not done already)
   ```bash
   git add -A
   git commit -m "Add Docker + deployment config"
   git push origin main
   ```

2. **Create a New Web Service** on [Render Dashboard](https://dashboard.render.com)
   - Connect your GitHub repo
   - **Root Directory**: `backend`
   - **Environment**: Docker (auto-detected from Dockerfile)
   - **Plan**: Free
   - **Health Check Path**: `/health`

3. **Wait for deploy** to complete (first build takes 3-5 minutes)

4. **Note the URL** — e.g., `https://car-price-api.onrender.com`

5. **Test the live backend:**
   ```bash
   curl https://car-price-api.onrender.com/health
   # → {"status":"healthy","model_loaded":true,...}
   ```
   Also visit `https://car-price-api.onrender.com/docs` for Swagger UI.

### (Optional, Recommended) Add PostgreSQL

SQLite resets on every Render redeploy (ephemeral filesystem). For persistent data:

1. Go to Render Dashboard → **New** → **PostgreSQL** → Free plan
2. Copy the **Internal Database URL**
3. In your backend service → **Environment** → set:
   ```
   DATABASE_URL = <paste the PostgreSQL connection string>
   ```
4. Redeploy — the backend auto-switches to PostgreSQL, no code changes needed.

---

## 3️⃣ Render — Frontend Deployment

### Steps

1. **Create a New Static Site** on [Render Dashboard](https://dashboard.render.com)
   - Connect your GitHub repo
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

2. **Set Environment Variable** (build-time):
   ```
   VITE_API_URL = https://car-price-api.onrender.com
   ```
   > Render's static site builder runs in a Node environment, so Vite picks up
   > `VITE_API_URL` automatically during `npm run build` — no Docker ARG needed.

3. **Wait for deploy** to complete

4. **Note the frontend URL** — e.g., `https://car-price-frontend.onrender.com`

5. **Test the live frontend** — run through the full flow:
   - Predict → see price + SHAP chart
   - History → see the prediction just made
   - Analytics → charts render
   - Feedback → submit successfully

---

## 4️⃣ Railway Alternative

### Backend

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy (uses railway.json config automatically)
railway up

# Set environment variables
railway variables set DATABASE_URL="sqlite:////app/data/car_predictions.db"
```

### Frontend (via Railway)

```bash
# In the frontend/ directory
cd frontend
railway init
railway up

# Set build-time env var
railway variables set VITE_API_URL="https://your-backend.up.railway.app"
```

---

## ✅ Final Verification Checklist

**All items must pass before considering deployment done:**

- [ ] Backend `/health` returns `{"status":"healthy","model_loaded":true}` on live URL
- [ ] Backend `/docs` (Swagger UI) is accessible publicly
- [ ] Frontend loads on live URL without errors
- [ ] Predict flow works end-to-end on **LIVE deployment** (not localhost)
- [ ] SHAP explanation chart renders correctly on live deployment
- [ ] History page shows predictions made via the live frontend
- [ ] Mobile responsive check on live URL (resize browser to 375px width)
- [ ] **Note**: Free tier cold-start delay is ~30-60s on the first request after idle

---

## 📝 Important Notes

### VITE_API_URL is a Build-Time Variable
Vite inlines `import.meta.env.VITE_API_URL` into the JavaScript bundle during
`npm run build`. Changing a runtime environment variable will **NOT** update the
frontend. You must **rebuild** the frontend image/site with the new URL.

### Model Artifacts
All `.pkl` and `.json` files in `app_models/` are committed to Git (~2.8MB total).
This is intentional for simplicity. If artifacts grow beyond 50MB, consider
Git LFS or external storage (S3, GCS).

### SQLite Limitations in Production
- Render/Railway use ephemeral filesystems — SQLite data is lost on redeploy
- For demos, this is acceptable
- For production, add a managed PostgreSQL database (free tier available on Render)
