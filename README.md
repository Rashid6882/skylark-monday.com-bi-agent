# Monday.com Business Intelligence Agent

An AI-powered Business Intelligence (BI) Agent built to connect with Monday.com boards (Work Orders and Deals data) to answer founder-level queries, manage dirty/messy real-world datasets gracefully, and prepare executive leadership updates.

---

## 🚀 Dual-Mode Architecture

To ensure maximum versatility and easy evaluation, the application is designed to run in two distinct modes:

### 1. Mock Local Mode (Default)
* **How it works:** When the backend server starts, it automatically preloads and normalizes data from the local Excel spreadsheets included in this repository:
  * [`Deal funnel Data.xlsx`](file:///c:/Users/rashi/OneDrive/Desktop/Skylark_drone/Deal%20funnel%20Data.xlsx) — Contains active sales opportunities, values, and stages.
  * [`Work_Order_Tracker Data.xlsx`](file:///c:/Users/rashi/OneDrive/Desktop/Skylark_drone/Work_Order_Tracker%20Data.xlsx) — Contains project status, billed values, collected amounts, and receivables.
* **Why it's useful:** You can test all features (the chatbot, KPIs, and executive report generation) immediately offline without needing a Monday.com account or API tokens.

### 2. Live Monday.com API Mode
* **How it works:** Inputting your Monday.com developer token and board IDs in the sidebar of the web application and clicking **Save & Connect** switches the application to Live Mode.
* **API Details:** 
  * Queries Monday.com's official GraphQL v2 API (`https://api.monday.com/v2`) using API version `2023-10`.
  * Automatically fetches live items, parses columns dynamically, maps the schema, and overrides the preloaded local data with real-time board records.
* **Fallback Strategy:** If the connection parameters are invalid or the board fetch fails, the agent falls back to the local Excel datasets to ensure uninterrupted operation.

---

## 🛠️ Technical Stack & Architecture

- **Backend:** Python 3.11, FastAPI (Fast REST API framework), Pandas & NumPy (data cleaning, normalization, and business intelligence logic).
- **Frontend:** HTML5, CSS3, Vanilla JavaScript. Features a responsive glassmorphic dashboard styled using the Outfits font family.
- **Data Resilience Engine:** Automatic standardizations for:
  * Inconsistent sector names (e.g., matching "energy", "Energy sector", "solar").
  * Currency formats, missing values, and null counts.
  * Mismatched dates or empty operational stages.

---

## 📁 Project Structure

```text
Skylark_drone/
├── backend/
│   ├── ai_agent.py          # Chatbot logic, heuristics, and query parsing
│   ├── data_normalizer.py   # Cleans and standardizes raw Excel/API datasets
│   ├── main.py              # FastAPI application server and routes
│   └── monday_client.py     # Monday.com GraphQL API client
├── Deal funnel Data.xlsx    # Sales pipeline local mock data
├── Work_Order_Tracker Data.xlsx # Work order tracker local mock data
├── index.html               # Responsive Frontend dashboard
├── DECISION_LOG.md          # Architectural decisions & assumptions
└── README.md                # Project documentation (this file)
```

---

## ⚙️ Installation & Local Setup

### 1. Prerequisites
Make sure you have [Python 3.11+](https://www.python.org/downloads/) installed.

### 2. Backend Setup
1. Open your terminal in the workspace directory:
   ```bash
   cd Skylark_drone
   ```
2. Install the required dependencies:
   ```bash
   pip install fastapi uvicorn openpyxl pandas requests
   ```
3. Launch the FastAPI server:
   ```bash
   python -m uvicorn backend.main:app --port 8000
   ```
   *You should see output indicating that the server is running on `http://127.0.0.1:8000`.*

### 3. Frontend Setup
* Simply double-click [`index.html`](file:///c:/Users/rashi/OneDrive/Desktop/Skylark_drone/index.html) (or drag it into your browser) to run the dashboard. It will automatically connect to your backend at `http://127.0.0.1:8000`.

---

## 🔌 Connecting to Live Monday.com

To synchronize your real Monday.com boards:

1. **Get your API Token**:
   * Click on your **Profile Picture (Avatar)** in the bottom-left of Monday.com.
   * Go to **Developer** (or **Administration > API**).
   * Copy the **Personal API Token**.
2. **Get your Board IDs**:
   * Open your Deals and Work Orders boards on Monday.com.
   * The **Board ID** is the string of numbers at the very end of your browser's URL (e.g., `https://workspace.monday.com/boards/123456789`).
3. **Connect**:
   * Enter your API Token and Board IDs in the sidebar of the dashboard UI.
   * Click **Save & Connect**. The BI Agent will test the connection and fetch live board items.

---

## 📦 Pushing to GitHub

Follow these steps to upload the repository to GitHub:

1. **Initialize Git Repository**:
   ```bash
   git init
   ```
2. **Create a `.gitignore`** to avoid uploading system cache, virtual environments, or temporary files:
   Create a file named `.gitignore` with the following content:
   ```text
   __pycache__/
   *.pyc
   .env
   .vscode/
   .idea/
   ```
3. **Commit Your Files**:
   ```bash
   git add .
   git commit -m "Initial commit: Monday.com BI Agent with Dual-Mode configuration"
   ```
4. **Push to GitHub**:
   * Go to [GitHub](https://github.com) and create a new repository (e.g., `monday-bi-agent`). Do not add a README, license, or gitignore.
   * Copy the remote repository URL and run:
     ```bash
     git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
     git branch -M main
     git push -u origin main
     ```

---

## 🌐 Deployment Guide

To make the application publicly accessible:

### 1. Backend Deployment (e.g., Render, Railway, or Fly.io)
You can deploy the FastAPI backend to services like Render or Railway:
* **Build Command**: `pip install -r requirements.txt` (generate this file by running `pip freeze > requirements.txt` before deploying)
* **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
* **Note**: In [`backend/main.py`](file:///c:/Users/rashi/OneDrive/Desktop/Skylark_drone/backend/main.py), CORS is already configured with `allow_origins=["*"]`, enabling your frontend to safely make API requests.

### 2. Frontend Deployment (e.g., GitHub Pages, Netlify, or Vercel)
You can deploy the frontend [`index.html`](file:///c:/Users/rashi/OneDrive/Desktop/Skylark_drone/index.html) static file:
* **For GitHub Pages**: Just enable GitHub Pages in your repository settings under the `main` branch.
* **Update API URL**: After deploying the backend, open your deployed [`index.html`](file:///c:/Users/rashi/OneDrive/Desktop/Skylark_drone/index.html) and update `API_HOST` to your deployed backend URL:
  ```javascript
  const API_HOST = "https://your-deployed-backend.onrender.com";
  ```
