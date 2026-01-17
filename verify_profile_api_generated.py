import requests
import random
import string

BASE_URL = "http://127.0.0.1:8000/api/v1"

def get_random_string(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def verify_service_provider_profile():
    # 1. Signup Service Provider
    email = f"sp_{get_random_string()}@example.com"
    password = "password123"
    name = f"SP {get_random_string()}"
    
    print(f"Signing up Service Provider: {email}")
    signup_data = {
        "email": email,
        "pass": password,
        "name": name
    }
    response = requests.post(f"{BASE_URL}/auth/signup/service-provider", json=signup_data)
    if response.status_code != 200:
        print(f"Signup failed: {response.status_code} {response.text}")
        return
    print("Signup successful")

    # 2. Login
    login_data = {
        "email": email,
        "pass": password
    }
    print("Logging in...")
    response = requests.post(f"{BASE_URL}/auth/login/service-provider", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} {response.text}")
        return
    token = response.json()["access_token"]
    print("Login successful, token received")

    # 3. Create Profile
    headers = {"Authorization": f"Bearer {token}"}
    profile_data = {
        "profile_photo": "http://example.com/photo.jpg",
        "full_name": name,
        "location_country": "India",
        "location_city": "Bangalore",
        "language": "English, Hindi",
        "experience": "5 Years",
        "project_completed": 10,
        "bio": "Expert in Python"
    }
    print("Creating Profile...")
    response = requests.post(f"{BASE_URL}/service-provider/profile", json=profile_data, headers=headers)
    if response.status_code != 200:
        print(f"Create Profile failed: {response.status_code} {response.text}")
        return
    
    print("Profile Created Successfully:")
    print(response.json())

    # 4. Update Profile
    update_data = {
        "experience": "6 Years",
        "project_completed": 11
    }
    print("Updating Profile...")
    response = requests.post(f"{BASE_URL}/service-provider/profile", json=update_data, headers=headers)
    if response.status_code != 200:
        print(f"Update Profile failed: {response.status_code} {response.text}")
        return
    
    print("Profile Updated Successfully:")
    print(response.json())

if __name__ == "__main__":
    verify_service_provider_profile()
