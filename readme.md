# CivicReporter — AI-Powered Municipal Issue Reporting

CivicReporter is a full-stack web application that lets citizens report public infrastructure issues (potholes, garbage dumps) by submitting a photo. Two specialized AI models automatically analyze the image, and the report flows through a structured review pipeline involving Municipal Officials and Inspection Officers.

> **Note:** A running MySQL server and an active internet connection are required for the AI inference to work.

---

## Table of Contents

- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)
- [User Roles](#user-roles)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)

---

## About the Project

Traditional municipal fault reporting is slow and opaque. CivicReporter replaces paper forms and phone calls with a transparent, AI-assisted pipeline:

1. A **citizen** uploads a photo of an issue along with their location.
2. Two hosted **Roboflow AI models** automatically detect potholes and/or garbage in the image.
3. A **Municipal Official** reviews the report, marks it in-progress, and flags it for verification when resolved.
4. An **Inspection Officer** does a final on-site check and either approves or rejects the resolution.
5. Citizens can see live status updates and leave a review once the issue is resolved.

---

## Key Features

- **Three-role system** — Citizen, Municipal Official, and Inspection Officer, each with their own dashboard and permissions.
- **Dual AI detection** — Two independent Roboflow models run in parallel to detect potholes and garbage from a single uploaded image.
- **Interactive map** — A public-facing map shows the live location and status of all reported issues.
- **Full lifecycle tracking** — Every status change is recorded in a JSON timeline on the report (submitted → in-progress → pending verification → resolved/rejected).
- **Advanced filtering** — Officials can filter the report queue by issue type, zone, and status.
- **Citizen reviews** — After a report is resolved, the submitting citizen can rate the resolution.
- **Auto-generated API docs** — FastAPI provides Swagger UI and ReDoc out of the box.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.9+, FastAPI, Uvicorn |
| Database | MySQL, SQLAlchemy (PyMySQL driver) |
| Auth & Security | Passlib (bcrypt), python-jose (JWT) |
| AI Inference | Roboflow hosted API |
| Image Processing | Pillow, OpenCV |
| Frontend | HTML5, Tailwind CSS, Vanilla JavaScript |

---

## Project Structure

```
CivicReporter/
├── backend/
│   ├── main.py          # FastAPI app, all routes
│   ├── models.py        # SQLAlchemy ORM models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── database.py      # DB connection and session setup
│   ├── security.py      # Password hashing and JWT logic
│   ├── inference.py     # Roboflow AI model initialization and image analysis
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── index.html       # Public-facing dashboard / map
│   ├── register.html    # Account creation
│   ├── login.html       # Login page
│   └── dashboard.html   # Role-specific dashboard (citizen / official / officer)
└── uploads/             # Uploaded images are stored here at runtime
```

---

## Setup and Installation

### Prerequisites

- Python 3.9 or newer
- A running MySQL server (MySQL Workbench is recommended for local setup)

### Step 1: Unzip and enter the project

```sh
unzip CivicReporter.zip
cd CivicReporter
```

### Step 2: Create the MySQL database

Open MySQL Workbench (or any MySQL client) and run:

```sql
CREATE DATABASE civicreporter;
```

### Step 3: Configure the database connection

Open `backend/database.py` and update the credentials at the top of the file:

```python
DB_USER     = "root"
DB_PASSWORD = "your_actual_password"   # ← change this
DB_HOST     = "127.0.0.1"
DB_NAME     = "civicreporter"
```

### Step 4: Set a secure JWT secret key

Open `backend/security.py` and replace the placeholder `SECRET_KEY` with a real random key. You can generate one by running:

```sh
openssl rand -hex 32
```

Then paste the output as the value of `SECRET_KEY` in `security.py`.

### Step 5: Create and activate a virtual environment

**macOS / Linux:**
```sh
cd backend
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```sh
cd backend
python -m venv venv
.\venv\Scripts\activate
```

### Step 6: Install dependencies

```sh
pip install -r requirements.txt
```

---

## Running the Application

### Start the backend server

From the **root `CivicReporter/` folder** (not inside `backend/`):

```sh
# Activate the virtual environment first if it isn't already active
source backend/venv/bin/activate          # macOS/Linux
# .\backend\venv\Scripts\activate         # Windows

uvicorn backend.main:app --reload
```

The API is now running at `http://127.0.0.1:8000`.

On first run, SQLAlchemy will automatically create all required database tables.

### Open the frontend

Navigate to the `frontend/` folder and open the HTML files directly in your browser:

1. Open `register.html` — create accounts for each role you want to test.
2. Open `login.html` — log in with your credentials.
3. You will be redirected to `dashboard.html`, which adapts its UI based on your user role.
4. Open `index.html` for the public-facing map (no login required).

---

## User Roles

| Role | `user_type` value | What they can do |
|---|---|---|
| Citizen | `citizen` | Submit reports, view own reports, leave reviews on resolved issues |
| Municipal Official | `municipal_official` | View all reports, filter by zone/type/status, mark reports in-progress or pending verification |
| Inspection Officer | `inspection_officer` | Approve or reject reports that are pending verification |

Set the `user_type` field when registering. The dashboard UI will change automatically based on the logged-in user's role.

---

## API Documentation

FastAPI auto-generates interactive API docs while the server is running:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

Key endpoints:

| Method | Path | Description |
|---|---|---|
| `POST` | `/register` | Register a new user |
| `POST` | `/token` | Log in and receive a JWT |
| `GET` | `/users/me` | Get the current user's profile |
| `GET` | `/api/public-dashboard` | Public analytics + recent reports (no auth) |
| `POST` | `/api/report` | Submit a new report with an image |
| `GET` | `/api/reports/my-reports` | Get the current citizen's reports |
| `GET` | `/api/reports` | Get all reports (officials only, supports filters) |
| `PATCH` | `/api/reports/{id}/status` | Update report status (officials only) |
| `POST` | `/api/reports/{id}/verify` | Approve or reject a resolution (inspection officers only) |
| `POST` | `/api/reports/{id}/review` | Submit a citizen review (resolved reports only) |
| `GET` | `/api/mcd-performance` | MCD performance analytics (supervisor access) |

---

## Environment Variables

The following values are currently hardcoded and should be moved to environment variables before deploying to production:

| File | Variable | Description |
|---|---|---|
| `database.py` | `DB_PASSWORD` | MySQL password |
| `security.py` | `SECRET_KEY` | JWT signing secret — must be a long random string |
| `inference.py` | `POTHOLE_API_KEY`, `GARBAGE_API_KEY` | Roboflow API keys |
