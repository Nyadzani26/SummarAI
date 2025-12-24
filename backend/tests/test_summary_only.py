"""Quick test for summarization endpoint"""
import requests

BASE_URL = "http://localhost:8000"

# Login first
print("[*] Logging in...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "apitest@example.com",
        "password": "TestPassword123!"
    }
)

if login_response.status_code != 200:
    print(f"[!] Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"[+] Login successful!")

# Get documents
print("\n[*] Getting documents...")
docs_response = requests.get(
    f"{BASE_URL}/documents/",
    headers={"Authorization": f"Bearer {token}"}
)

if docs_response.status_code != 200:
    print(f"[!] Failed to get documents: {docs_response.status_code}")
    exit(1)

documents = docs_response.json()["documents"]
if not documents:
    print("[!] No documents found. Upload a document first!")
    exit(1)

document_id = documents[0]["id"]
print(f"[+] Found document ID: {document_id}")

# Generate summary
print(f"\n[*] Generating summary for document {document_id}...")
summary_response = requests.post(
    f"{BASE_URL}/summaries/generate",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "document_id": document_id,
        "max_length": 100,
        "min_length": 30
    }
)

print(f"\n[*] Response status: {summary_response.status_code}")
print(f"[*] Response body:")
print(summary_response.text)

if summary_response.status_code == 201:
    summary = summary_response.json()
    print(f"\n[+] SUCCESS! Summary generated:")
    print(f"    {summary['summary_text']}")
else:
    print(f"\n[!] FAILED! Status: {summary_response.status_code}")
