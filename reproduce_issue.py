import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_flow():
    email = "test_sp_debug@example.com"
    password = "password123"
    
    # 1. Signup (ignore error if exists)
    signup_data = {
        "email": email,
        "pass": password,  # Use 'pass' alias
        "name": "Test SP"
        # "type": "service provider" # Let it default to avoid weird literal errors
    }

    try:
        r = requests.post(f"{BASE_URL}/auth/signup/service-provider", json=signup_data)
        if r.status_code == 200:
            print("Signup successful")
        elif r.status_code == 400 and "already exists" in r.text:
            print("User already exists, proceeding to login")
        else:
            print(f"Signup failed: {r.status_code} {r.text}")
            return
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Is it running on port 8000?")
        return

    # 2. Login
    login_data = {
        "username": email, # OAuth2PasswordRequestForm uses username
        "password": password
    }
    # Note: The schema in auth.py uses ClientLogin/ServiceProviderLogin which expects 'email' and 'pass' (alias)
    # But OAuth2PasswordBearer usually expects standard form data 'username' & 'password'.
    # Let's check auth.py again.
    # auth.py: login_service_provider takes ServiceProviderLogin (json body)
    # ServiceProviderLogin: email: EmailStr, password: str = Field(..., alias="pass")
    
    # WAIT! Standard OAuth2PasswordBearer expects a FORM POST to tokenUrl.
    # But the implementation in auth.py `login_service_provider` uses `login_in: ServiceProviderLogin` which implies JSON body.
    # However, `deps.py` defines `oauth2_scheme = OAuth2PasswordBearer(tokenUrl=...)`.
    # OAuth2PasswordBearer client (like Swagger UI) sends Form Data.
    # If the endpoint `login_service_provider` expects JSON, Swagger UI might fail if it sends Form Data.
    # BUT, let's verify what `ServiceProviderLogin` expects.
    
    # If I use `requests.post(..., json=...)` it sends JSON.
    # Let's try sending JSON first as defined in schemas.
    
    login_json = {
        "email": email,
        "pass": password 
    }
    r = requests.post(f"{BASE_URL}/auth/login/service-provider", json=login_json)
    if r.status_code != 200:
        print(f"Login failed: {r.status_code} {r.text}")
        return
    
    token = r.json().get("access_token")
    if not token:
        print("No token in response")
        return
    print(f"Got token: {token[:10]}...")

    # 3. Call Portfolio Endpoint
    headers = {"Authorization": f"Bearer {token}"}
    portfolio_data = {
        "title": "Debug Project",
        "project_url": "http://example.com"
    }
    r = requests.post(f"{BASE_URL}/service-provider/portfolio", json=portfolio_data, headers=headers)
    
    if r.status_code == 200:
        print("✅ Portfolio create successful!")
        print(r.json())
    else:
        print(f"❌ Portfolio create failed: {r.status_code} {r.text}")

if __name__ == "__main__":
    test_flow()
