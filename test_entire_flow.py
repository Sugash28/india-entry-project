import requests
import os
import time

BASE_URL = "http://localhost:8000/api/v1"
TS = int(time.time())
CLIENT_EMAIL = f"client_{TS}@example.com"
SP_EMAIL = f"sp_{TS}@example.com"
PASSWORD = "password123"

def test_flow():
    print("--- 1. Signup & Login ---")
    # Signup Client
    r = requests.post(f"{BASE_URL}/auth/signup/client", json={
        "email": CLIENT_EMAIL, "password": PASSWORD, "name": "Test Client"
    })
    if r.status_code != 200:
        print(f"FAILED Signup Client: {r.status_code} {r.text}")
        return
    print(f"Signup Client: {r.status_code}")
    
    # Login Client
    r = requests.post(f"{BASE_URL}/auth/login/client", json={"email": CLIENT_EMAIL, "password": PASSWORD})
    client_token = r.json()["access_token"]
    client_headers = {"Authorization": f"Bearer {client_token}"}
    print("Logged in as Client")

    # Signup SP
    # IMPORTANT: SP uses 'pass' instead of 'password' in JSON
    r = requests.post(f"{BASE_URL}/auth/signup/service-provider", json={
        "email": SP_EMAIL, "pass": PASSWORD, "name": "Test Provider"
    })
    if r.status_code != 200:
        print(f"FAILED Signup SP: {r.status_code} {r.text}")
        return
    print(f"Signup SP: {r.status_code}")
    
    # Login SP
    r = requests.post(f"{BASE_URL}/auth/login/service-provider", json={"email": SP_EMAIL, "pass": PASSWORD})
    sp_token = r.json()["access_token"]
    sp_headers = {"Authorization": f"Bearer {sp_token}"}
    print("Logged in as SP")

    print("\n--- 2. Project Creation & Bidding ---")
    # Create Project
    r = requests.post(f"{BASE_URL}/client/projects/", headers=client_headers, json={
        "title": "E2E Test Project", "description": "Testing the whole flow", "budget_range": "100-200", "currency": "USD"
    })
    project = r.json()
    project_id = project["id"]
    print(f"Project Created ID: {project_id}")

    # SP Bids
    r = requests.post(f"{BASE_URL}/service-provider/projects/{project_id}/bid", headers=sp_headers, json={
        "bid_amount": 150, "currency": "USD", "cover_letter": "I can do this!"
    })
    bid = r.json()
    bid_id = bid["id"]
    print(f"Bid Submitted ID: {bid_id}")

    # Client Accepts Bid
    r = requests.put(f"{BASE_URL}/client/projects/{project_id}/bids/{bid_id}/accept", headers=client_headers)
    print(f"Bid Accepted: {r.status_code} | Project Status: {r.json().get('status', 'unknown')}")

    print("\n--- 3. Contract Signing ---")
    # Create dummy signature photo
    with open("dummy_sig.png", "wb") as f:
        f.write(b"fake image data")

    # Client Signs Contract
    files = {'signature_photo': ('sig.png', open('dummy_sig.png', 'rb'), 'image/png')}
    data = {'project_id': project_id, 'bid_id': bid_id, 'terms_and_conditions': 'Be excellent to each other.'}
    r = requests.post(f"{BASE_URL}/client/contracts/", headers=client_headers, data=data, files=files)
    contract = r.json()
    contract_id = contract["id"]
    print(f"Client Signed Contract. ID: {contract_id}")

    # SP Counter-signs
    files = {'signature_photo': ('sig_sp.png', open('dummy_sig.png', 'rb'), 'image/png')}
    r = requests.post(f"{BASE_URL}/client/contracts/{contract_id}/sign/service-provider", headers=sp_headers, files=files)
    print(f"SP Signed Contract: {r.status_code} | Status: {r.json().get('status')}")

    print("\n--- 4. Work Submission & Funds ---")
    # Check project status
    r = requests.get(f"{BASE_URL}/client/projects/{project_id}", headers=client_headers)
    print(f"Project Status (after signatures): {r.json()['status']}")

    # Create dummy PDF
    with open("dummy_work.pdf", "wb") as f:
        f.write(b"%PDF-1.4 dummy data")

    # SP Submits Work
    files = {'work_pdf': ('work.pdf', open('dummy_work.pdf', 'rb'), 'application/pdf')}
    data = {'github_link': 'https://github.com/test/repo'}
    r = requests.post(f"{BASE_URL}/client/projects/{project_id}/submit-work", headers=sp_headers, data=data, files=files)
    print(f"Work Submitted: {r.status_code} | Status: {r.json().get('status')}")

    # Client Releases Funds
    r = requests.put(f"{BASE_URL}/client/projects/{project_id}/release-funds", headers=client_headers)
    final_project = r.json()
    print(f"Funds Released: {r.status_code} | Final Status: {final_project['status']} | Escrow: {final_project['escrow_funded']}")

    # Cleanup
    os.remove("dummy_sig.png")
    os.remove("dummy_work.pdf")

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"Test crashed: {e}")
