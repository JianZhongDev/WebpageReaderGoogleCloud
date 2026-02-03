# Project Deployment Status
**Last Updated:** $(date)

## 🟢 Deployment Status: Success
The Webpage Reader application has been successfully deployed to Google Cloud Platform.

### 🔗 Live URLs
- **Frontend (Web App):** [https://webreadergcd.web.app](https://webreadergcd.web.app)
- **Backend (API):** [https://web-reader-backend-992294632301.us-west2.run.app](https://web-reader-backend-992294632301.us-west2.run.app)

---

## ⚙️ Global Configurations
- **Google Cloud Project ID:** `webreadergcd`
- **Region:** `us-west2` (Backend & Artifact Registry)
- **Frontend Hosting:** Firebase Hosting
- **Backend Hosting:** Cloud Run (Serverless)

---

## 📂 Local Project Configurations

### Automation Scripts
Reference these scripts for future updates.
- **Backend**: `./deploy_backend.sh`
  - *Actions*: Checks gcloud, enables APIs (run, tts, build), builds container in `us-west2` Artifact Registry, deploys to Cloud Run.
- **Frontend**: `./deploy_frontend.sh <BACKEND_URL>`
  - *Actions*: Installs dependencies, detects GCP project, builds Vite app with `VITE_API_URL`, deploys to Firebase.

### Key Configuration Files
- `Docker/frontend/firebase.json`: Configures Firebase Hosting for Vite (SPA rewrites).
- `Docker/backend/main.py`: FastAPI backend application.
- `Docker/frontend/vite.config.js`: Frontend build configuration.

---

## 📝 Deployment Operations Log
1.  **Dependencies Installed**: `gcloud` SDK, `node` (v25), `firebase-tools`.
2.  **Backend Setup**:
    - Enabled `run.googleapis.com`, `texttospeech.googleapis.com`, `artifactregistry.googleapis.com`, `cloudbuild.googleapis.com`.
    - Created Artifact Registry repo `backend-repo` in `us-west2`.
    - Deployed container image to Cloud Run.
3.  **Frontend Setup**:
    - Initialized Firebase Project `webreadergcd`.
    - Linked local directory to Firebase Hosting.
    - Built production assets with backend connection.
4.  **Issues Resolved**:
    - Fixed `cloudbuild` API missing error.
    - Fixed interactive prompts by explicit region targeting (`us-west2`).
    - Fixed missing `firebase.json` by creating a default configuration.
    - Resolved project initialization conflict by verifying `firebase projects:list`.

---

## 🚀 How to Redeploy

### Backend (Python)
If you modify `Docker/backend/`:
```bash
./deploy_backend.sh
# Note the URL output if it changes (unlikely for updates).
```

### Frontend (React)
If you modify `Docker/frontend/`:
```bash
# Re-run with your backend URL
./deploy_frontend.sh "https://web-reader-backend-992294632301.us-west2.run.app"
```
