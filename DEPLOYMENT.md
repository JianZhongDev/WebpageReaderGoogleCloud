# Deployment Guide - Google Cloud Platform

This guide outlines the steps to deploy your Web Reader app to Google Cloud for the **lowest cost** (paying only for usage, with generous free tiers).

## Recommended Architecture
*   **Backend**: **Google Cloud Run** (Serverless containers).
    *   *Why*: Scales to zero when not in use. You don't pay for idle time.
*   **Frontend**: **Firebase Hosting** (Static hosting).
    *   *Why*: Free tier is generous, performs better (CDN), and avoids container cold-starts for the UI.

## Prerequisites
1.  [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed (`gcloud`).
2.  [Node.js](https://nodejs.org/) installed (for building the frontend).
3.  A Google Cloud Project with billing enabled.

---

## 🚀 Automated Deployment (Recommended)

We have provided shell scripts to automate the entire process.

### Step 1: Deploy Backend
1.  Run the backend deployment script:
    ```bash
    ./deploy_backend.sh
    ```
2.  It will ask you to log in if needed and set up the Cloud Run service.
3.  **Copy the Backend URL** displayed at the end of the script output.

### Step 2: Deploy Frontend
1.  Run the frontend deployment script with the URL you just copied:
    ```bash
    ./deploy_frontend.sh "YOUR_BACKEND_URL"
    ```
    *(Example: `./deploy_frontend.sh "https://web-reader-backend-xyz.a.run.app"`)*

2.  The script will build the frontend and deploy it to Firebase Hosting.

---

## Manual Deployment Guide

## Step 1: Deploy Backend (Cloud Run)

1.  **Enable APIs**:
    ```bash
    gcloud services enable run.googleapis.com texttospeech.googleapis.com artifactregistry.googleapis.com
    ```

2.  **Authenticate & Set Project**:
    ```bash
    gcloud auth login
    gcloud config set project YOUR_PROJECT_ID
    ```

3.  **Build & Deploy**:
    Run this from the `Docker/backend` directory:
    ```bash
    cd Docker/backend
    gcloud run deploy web-reader-backend --source . --region us-central1 --allow-unauthenticated --set-env-vars ALLOWED_ORIGINS="*"
    ```
    *Note*: We use `ALLOWED_ORIGINS="*"` to allow any frontend to access the API. For stricter security, you can set this to your specific Firebase URL once deployed.

4.  **View URL**:
    The command will output a URL (e.g., `https://web-reader-backend-xyz-uc.a.run.app`). **Copy this URL.**

5.  **Grant Permissions (Critical)**:
    The Cloud Run service uses the "Default Compute Service Account". You must ensure this account has permission to use Text-to-Speech.
    *   Go to IAM in Google Cloud Console.
    *   Find the `Compute Engine default service account`.
    *   Add Role: `Cloud Text-to-Speech API User`.

    > **Note**: You do NOT need `credentials.json` in Cloud Run. The code validates `GOOGLE_APPLICATION_CREDENTIALS` or falls back to the environment's identity automatically.

---

## Step 2: Deploy Frontend (Firebase Hosting)

1.  **Install Firebase Tools**:
    ```bash
    npm install -g firebase-tools
    ```

2.  **Initialize Firebase**:
    Navigate to `Docker/frontend`:
    ```bash
    cd ../frontend
    firebase login
    firebase init
    ```
    *   Select **Hosting**.
    *   Select **Use an existing project** (choose your GCP project).
    *   What do you want to use as your public directory? `dist`
    *   Configure as a single-page app? **Yes**
    *   Set up automatic builds and deploys with GitHub? **No** (for now).

3.  **Build the Frontend**:
    Replace `YOUR_BACKEND_URL` with the Cloud Run URL from Step 1.
    ```bash
    # Linux/Mac
    export VITE_API_URL=https://web-reader-backend-xyz-uc.a.run.app
    npm install
    npm run build
    ```

4.  **Deploy**:
    ```bash
    firebase deploy
    ```

5.  **Done!**
    Firebase will give you a public URL (e.g., `https://your-project.web.app`). Open it and test the app!

---

## Cost Analysis
*   **Cloud Run**: Free tier includes 2 million requests/month and significant CPU/RAM time. For on-demand usage, it will likely be **$0.00**.
*   **Firebase Hosting**: Free tier includes 10GB storage/transfer. Likely **$0.00**.
*   **Text-to-Speech API**: Free tier includes 1 million characters (Standard) or 100k characters (WaveNet) per month. After that, WaveNet is ~$16 per 1 million characters. This is the main potential cost driver if usage is heavy.

## Alternative: Pure Docker (All Cloud Run)
If you prefer not to use Firebase and want to stick to Docker containers for everything:
1.  You would need to update the Frontend Dockerfile to handle a production build (using Nginx).
2.  Deploy the frontend container to Cloud Run similarly to the backend.
3.  **Downside**: Slightly higher cost (container startup time) and latency compared to Firebase.
