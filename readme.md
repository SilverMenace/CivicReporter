# CivicReporter: AI-Powered Municipal Issue Reporting 🚀

CivicReporter is a full-stack web application for reporting and managing public infrastructure issues. It uses pre-configured AI models to autonomously detect problems like potholes and garbage in user-submitted images.

**Important Note for Grader:** This project is configured to run with a MySQL database. Please follow the setup instructions carefully. An internet connection is also required for the AI analysis to function.

---

## 📖 Table of Contents

- [About The Project](#-about-the-project)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Setup and Installation](#-setup-and-installation)
- [How to Run the Application](#-how-to-run-the-application)
- [API Documentation](#-api-documentation)

---

## 📖 About The Project

This project addresses the inefficiencies in traditional municipal fault reporting. It provides a direct, secure, and transparent pipeline between citizens and their local government. By leveraging AI to automate the initial analysis, the platform reduces processing time and helps prioritize critical repairs.



---

## ✨ Key Features

* **Three User Roles**: Secure portals for Citizens, Municipal Officials, and Inspection Officers.
* **AI Detection Engine**: Connects to two specialized AI models to detect potholes and garbage.
* **Interactive Dashboards**: All user roles have access to analytics and a live, interactive map showing the location and status of all reported issues.
* **Advanced Filtering**: Officials can filter reports by issue type, zone, and status.
* **Complete Reporting Lifecycle**: Full workflow from citizen submission, to municipal action, to final verification by an inspection officer.

---

## 🛠️ Technology Stack

* **Backend**:
    * Python 3.9+
    * FastAPI & Uvicorn
    * **MySQL Database**
    * SQLAlchemy (with PyMySQL driver)
    * Pydantic
    * Passlib & python-jose (for security)
    * Roboflow (for AI model inference API)
* **Frontend**:
    * HTML5
    * Tailwind CSS
    * JavaScript

---

## 🚀 Setup and Installation

This guide explains how to set up the project on a local machine.

### Prerequisites

* Python 3.9 or newer.
* A running MySQL server and a management tool like MySQL Workbench.

### Step 1: Unzip the Project

Unzip the `CivicReporter.zip` file. This will create the project folder containing all necessary files.

### Step 2: Create the MySQL Database

1.  Open **MySQL Workbench** and connect to your local MySQL server.
2.  Open a new query tab and run the following command to create the database:
    ```sql
    CREATE DATABASE civicreporter;
    ```

### Step 3: Configure the Database Password

1.  Navigate to the `backend/` folder and open the file `database.py`.
2.  On line 13, change the value of the `DB_PASSWORD` variable from `"your_password"` to your actual MySQL root password. Save the file.

### Step 4: Install Dependencies

1.  **Open a terminal** and navigate into the `backend` directory of the project:
    ```sh
    cd path/to/your/CivicReporter/backend
    ```
2.  **Create and Activate a Virtual Environment**:
    * On **macOS/Linux**:
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```
    * On **Windows**:
        ```sh
        python -m venv venv
        .\venv\Scripts\activate
        ```
3.  **Install All Required Packages**:
    ```sh
    pip install -r requirements.txt
    ```

---

## ▶️ How to Run the Application

1.  **Start the Backend Server**:
    * From the **root `CivicReporter/` folder**, run the following commands:
        ```sh
        source backend/venv/bin/activate
        uvicorn backend.main:app
        ```
    * The backend is now running at `http://127.0.0.1:8000`.

2.  **Access the Frontend**:
    * Navigate to the `frontend/` folder in your file explorer.
    * Open `register.html` in your web browser to create accounts.
    * Then, open `login.html` to log in.

---

## 🔌 API Documentation

This project uses FastAPI, which automatically generates interactive API documentation. Once the backend server is running, you can access the following URLs in your browser:

* **Swagger UI**: `http://127.0.0.1:8000/docs`
* **ReDoc**: `http://127.0.0.1:8000/redoc`