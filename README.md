# India Entry Project - Backend

This is the backend for the India Entry Project, built with **FastAPI**.
It provides a robust authentication system supporting Email/Password, Google, and Microsoft login flows for two types of users: **Clients** and **Service Providers**.

## Features implemented

### 1. User Management
- **Two User Types**:
    - **Client**: Typical end-users.
    - **Service Provider**: Users offering services.
- **Native Authentication**:
    - Sign Up & Login endpoints for both user types.
    - JWT (JSON Web Token) based session management.
    - Password hashing using Bcrypt.

### 2. OAuth Integration
- **Google Authentication**:
    - "Sign in with Google" flow.
    - Automatic user creation (with random password) if the email doesn't exist.
- **Microsoft Authentication**:
    - "Sign in with Microsoft" flow (Single Tenant / Organization).
    - Automatic user creation if the email doesn't exist.
    - Validates tokens against Azure AD v2.0 endpoint.

### 3. Testing Interface
- **Static Test UI**: A simple HTML page (`static/google_login.html`) is served to test OAuth flows locally without a full frontend.

## Project Structure

```
app/
├── api/v1/endpoints/  # API Routers
│   ├── auth.py        # Login/Signup logic (Native + OAuth)
├── core/
│   ├── config.py      # App configuration (Settings)
│   ├── security.py    # JWT & Password utilities
├── models/            # SQLAlchemy Database Models
├── schemas/           # Pydantic Schemas (Request/Response)
main.py                # Application entry point
static/                # Static files (Test UI)
```

## Setup & Running

### 1. Prerequisites
- Python 3.9+
- MySQL Database

### 2. Environment Variables
Create a `.env` file in the root directory:

```env
PROJECT_NAME="India Entry Project"
SECRET_KEY="your_secret_key"
ACCESS_TOKEN_EXPIRE_MINUTES=60
MYSQL_SERVER="localhost"
MYSQL_USER="root"
MYSQL_PASSWORD="your_password"
MYSQL_DB="Main"

# OAuth Credentials
GOOGLE_CLIENT_ID="your-google-client-id"
MICROSOFT_CLIENT_ID="your-microsoft-client-id"
MICROSOFT_TENANT_ID="your-microsoft-tenant-id"
```

### 3. Installation

```bash
pip install -r requirements.txt
```

### 4. Running the Server

```bash
uvicorn app.main:app --reload
```
The server will start at `http://localhost:8000`.

### 5. Testing OAuth

Navigate to:
> **http://localhost:8000/static/google_login.html**

1.  Select **Client** or **Service Provider**.
2.  Click **Sign in with Google** or **Sign in with Microsoft**.
3.  Upon success, an **Access Token** will be displayed.

## Configuration Notes for OAuth

- **Google Cloud Console**:
    - **Authorized JavaScript origins**: `http://localhost:8000` and `http://127.0.0.1:8000`
- **Azure Portal**:
    - **Platform**: Single-page application (SPA).
    - **Redirect URI**: `http://localhost:8000/static/google_login.html`
    - **Manifest**: Set `"requestedAccessTokenVersion": 2`.
