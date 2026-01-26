# Product Requirement Document (PRD): Web Reader MVP

**Version:** 1.0
**Date:** 2023-10-27
**Status:** Approved for Development
**Architect:** Gemini (AI Thought Partner)

---

## 1. Executive Summary
The **Web Reader App** is a desktop-first web application designed to improve content consumption efficiency. It allows users to input any article URL, converts the web content into a distraction-free "Reader View," and provides high-quality, synchronized audio playback using Google Cloud's WaveNet Text-to-Speech engine. The MVP targets a small user base (≤ 100 users) with a focus on low latency and high-fidelity "Karaoke-style" text synchronization.

---

## 2. Objectives & Scope

### 2.1 Goals
* **Accessibility:** Transform visual web content into auditory experiences instantly.
* **Focus:** Remove visual clutter (ads, popups) via a dedicated Reader Mode.
* **Precision:** Allow users to select specific text to read, rather than forcing them to listen from the top.
* **Economy:** Utilize Google Cloud Free Tier and low-cost WaveNet models to maintain minimal operating costs.

### 2.2 Scope (MVP)
* **Platform:** Desktop Web Browsers (Chrome, Firefox, Safari, Edge).
* **User Base:** ≤ 100 Concurrent Users.
* **Authentication:** None (Open Access for MVP, architecture ready for future Auth integration).
* **Data Persistence:** Ephemeral (Audio is streamed, not saved long-term).

---

## 3. Functional Requirements

### 3.1 Content Input
* **FR-01:** System must accept a text block input directly from the user (Copy/Paste).
* **FR-02:** [Removed - URL fetching no longer needed]
* **FR-03:** [Removed - HTML parsing no longer needed]
* **FR-04:** Content must be rendered in the frontend as clean, readable text.

### 3.2 Audio Synthesis (WaveNet)
* **FR-05:** System must use **Google Cloud Text-to-Speech (WaveNet)** models.
* **FR-06:** Users must be able to select a "Voice Persona" (e.g., Male/Female variants).
* **FR-07:** The synthesis request must include `enableTimepoints` to retrieve word-level timestamp data.

### 3.3 Playback & Interaction
* **FR-08 (Select-to-Read):** Users must be able to highlight a paragraph and trigger playback for just that selection.
* **FR-09 (Karaoke Sync):** As audio plays, the corresponding word in the text must be visually highlighted in real-time.
* **FR-10 (Controls):** Standard audio controls (Play, Pause, Seek/Scrub) must be available.
* **FR-11 (Latency):** Audio playback should begin within < 2 seconds of the user request.

---

## 4. System Architecture

### 4.1 High-Level Diagram
[Client Browser (React)] <--> [Google Cloud Run (Python FastAPI)] <--> [Google Cloud TTS API]

### 4.2 Technology Stack
| Component | Technology | Reasoning |
| :--- | :--- | :--- |
| **Frontend** | **React.js** (or Vue.js) | Component-based structure ideal for managing complex UI states (highlighting/audio sync). |
| **Hosting** | **Firebase Hosting** | Fast global CDN, free SSL, easy integration with Google Cloud services. |
| **Backend** | **Python 3.9+ (FastAPI)** | High performance, native async support for handling concurrent requests, excellent library ecosystem for HTML parsing. |
| **Compute** | **Google Cloud Run** | Serverless container platform. Scales to zero (costs $0 when idle). |
| **AI Engine** | **Cloud TTS (WaveNet)** | Industry-standard quality, low latency, cost-effective compared to Chirp/Studio voices. |

---

## 5. Technical Specifications

### 5.1 Backend API (Python / FastAPI)

The backend will expose two primary REST endpoints.

#### Endpoint A: [Removed]
* Endpoint `/api/v1/extract` is deprecated/removed in favor of client-side text input.

#### Endpoint B: `/api/v1/synthesize`
* **Method:** `POST`
* **Input:**
    ```json
    {
      "text": "The text selected by the user...",
      "voice_id": "en-US-Wavenet-D"
    }
    ```
* **Process:**
    1.  Instantiate `texttospeech.TextToSpeechClient`.
    2.  Construct `SynthesisInput`.
    3.  Configure `VoiceSelectionParams` (Hardcoded to WaveNet).
    4.  Enable `TimepointType.SSML_MARK` or strictly rely on `enable_time_pointing`.
* **Output:**
    ```json
    {
      "audio_base64": "UklGRi...",
      "timepoints": [
        { "mark_name": "word_1", "time_seconds": 0.5 },
        { "mark_name": "word_2", "time_seconds": 0.9 }
      ]
    }
    ```

### 5.2 Frontend Logic (Synchronization)

* **State Management:**
    * `audioSrc`: The Base64 blob converted to a playable URL.
    * `wordTimings`: The array of timepoints from the API.
    * `currentWordIndex`: Tracks which word is currently active.
* **Sync Loop:**
    * Use `requestAnimationFrame` or the `<audio>` element's `timeupdate` event (firing every ~250ms).
    * Compare `audio.currentTime` against `wordTimings`.
    * Apply a CSS class (e.g., `.highlight { background-color: yellow; }`) to the matching word `<span>`.

---

## 6. Security & Compliance

### 6.1 CORS (Cross-Origin Resource Sharing)
* The Cloud Run backend must have CORS configured to **only allow requests from the Firebase Hosting domain**. This prevents unauthorized websites from using your backend as a free API.

### 6.2 Data Privacy
* **No Logging:** The backend should explicitly *not* log the text content sent by users to avoid storing sensitive reading habits.
* **Ephemeral:** Audio files are returned directly to the client and discarded from server memory immediately.

---

## 7. Cost Analysis (Estimates for 100 Users)

| Service | Free Tier Limit | Estimated MVP Usage | Estimated Cost |
| :--- | :--- | :--- | :--- |
| **Cloud Run** | 2M requests/mo | ~50,000 requests | **$0.00** |
| **Cloud Build** | 120 mins/day | ~10 mins/deploy | **$0.00** |
| **TTS (WaveNet)** | 1M chars/mo | ~2M chars (Heavy use) | **~$16.00** |
| **Firebase Hosting** | 10GB transfer | ~1GB | **$0.00** |
| **Total Monthly** | | | **~$16.00** |

---

## 8. Deployment Strategy

### 8.1 Prerequisites
1.  GCP Project Created.
2.  APIs Enabled: `Cloud Run`, `Text-to-Speech`, `Artifact Registry`.
3.  Service Account created with `Cloud Run Invoker` and `TTS User` roles.

### 8.2 Backend Deployment (Dockerfile)
```dockerfile
# Python 3.9 Slim Image
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]