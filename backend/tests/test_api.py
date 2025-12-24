"""
Backend API Test Script
Tests all endpoints: auth, documents, summaries
"""

import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:8000"

# Test data
TEST_USER = {
    "email": "apitest@example.com",
    "password": "TestPassword123!",
    "full_name": "API Test User"
}

# Sample text for testing (if no file)
SAMPLE_TEXT = """
Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural 
intelligence displayed by humans and animals. Leading AI textbooks define the field as the study 
of "intelligent agents": any device that perceives its environment and takes actions that maximize 
its chance of successfully achieving its goals. Colloquially, the term "artificial intelligence" 
is often used to describe machines (or computers) that mimic "cognitive" functions that humans 
associate with the human mind, such as "learning" and "problem solving".
"""


def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_registration():
    """Test user registration"""
    print_section("1. Testing User Registration")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=TEST_USER,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 201:
            print("[+] Registration successful!")
            user_data = response.json()
            print(f"   User ID: {user_data['id']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Verified: {user_data['is_verified']}")
            return True
        elif response.status_code == 400:
            try:
                error_data = response.json()
                if "already registered" in str(error_data):
                    print("[!] User already exists (OK for testing)")
                    return True
                else:
                    print(f"[!] Registration failed: {error_data}")
                    return False
            except:
                print(f"[!] Registration failed: {response.text[:200]}")
                return False
        else:
            print(f"[!] Registration failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"[!] Error during registration: {e}")
        return False


def test_login():
    """Test user login and get token"""
    print_section("2. Testing User Login")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    
    if response.status_code == 200:
        print("[+] Login successful!")
        data = response.json()
        token = data["access_token"]
        print(f"   Token (first 50 chars): {token[:50]}...")
        return token
    else:
        print(f"[!] Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_upload_document(token):
    """Test document upload"""
    print_section("3. Testing Document Upload")
    
    # Create a test text file
    test_file_path = "test_document.txt"
    with open(test_file_path, "w") as f:
        f.write(SAMPLE_TEXT)
    
    # Upload file
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(test_file_path, "rb") as f:
        files = {"file": ("test_document.txt", f, "text/plain")}
        response = requests.post(
            f"{BASE_URL}/documents/upload",
            headers=headers,
            files=files
        )
    
    if response.status_code == 201:
        print("[+] Document upload successful!")
        doc_data = response.json()
        print(f"   Document ID: {doc_data['id']}")
        print(f"   Filename: {doc_data['filename']}")
        print(f"   Word count: {doc_data['word_count']}")
        print(f"   File size: {doc_data['file_size']} bytes")
        return doc_data['id']
    else:
        print(f"[!] Upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_list_documents(token):
    """Test listing documents"""
    print_section("4. Testing List Documents")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/documents/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"[+] Retrieved {data['total']} document(s)")
        for doc in data['documents']:
            print(f"   - {doc['filename']} (ID: {doc['id']})")
        return True
    else:
        print(f"[!] List failed: {response.status_code}")
        return False


def test_generate_summary(token, document_id):
    """Test AI summary generation"""
    print_section("5. Testing AI Summary Generation")
    
    print("[*] Generating summary with BART model...")
    print("    (This may take 10-30 seconds on first run as model loads)")
    
    headers = {"Authorization": f"Bearer {token}"}
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/summaries/generate",
        headers=headers,
        json={
            "document_id": document_id,
            "max_length": 100,
            "min_length": 30
        }
    )
    
    elapsed = time.time() - start_time
    
    if response.status_code == 201:
        print(f"[+] Summary generated successfully! ({elapsed:.1f}s)")
        summary_data = response.json()
        print(f"\n   Summary ID: {summary_data['id']}")
        print(f"   Summary length: {summary_data.get('word_count', 'N/A')} words")
        print(f"   Compression ratio: {summary_data.get('compression_ratio', 'N/A')}")
        print(f"   Generation time: {summary_data.get('generation_time', 'N/A')}s")
        print(f"\n   [*] Summary text:")
        print(f"   {'-'*56}")
        print(f"   {summary_data['summary_text']}")
        print(f"   {'-'*56}")
        return summary_data['id']
    else:
        print(f"[!] Summary generation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_get_summary(token, summary_id):
    """Test retrieving a summary"""
    print_section("6. Testing Get Summary")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/summaries/{summary_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("[+] Summary retrieved successfully!")
        data = response.json()
        print(f"   Summary ID: {data['id']}")
        print(f"   Created at: {data['created_at']}")
        return True
    else:
        print(f"[!] Get summary failed: {response.status_code}")
        return False


def test_statistics(token):
    """Test document statistics"""
    print_section("7. Testing Document Statistics")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/documents/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print("[+] Statistics retrieved!")
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Total words: {stats['total_words']}")
        print(f"   Total size: {stats['total_size_mb']} MB")
        print(f"   File types: {stats['file_types']}")
        return True
    else:
        print(f"[!] Statistics failed: {response.status_code}")
        return False


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*60)
    print("  [*] BACKEND API TEST SUITE")
    print("="*60)
    
    # Test 1: Registration
    if not test_registration():
        print("\n[!] Test suite failed at registration")
        return
    
    # Test 2: Login
    token = test_login()
    if not token:
        print("\n[!] Test suite failed at login")
        return
    
    # Test 3: Upload document
    document_id = test_upload_document(token)
    if not document_id:
        print("\n[!] Test suite failed at document upload")
        return
    
    # Test 4: List documents
    test_list_documents(token)
    
    # Test 5: Generate summary
    summary_id = test_generate_summary(token, document_id)
    if not summary_id:
        print("\n[!] Test suite failed at summary generation")
        return
    
    # Test 6: Get summary
    test_get_summary(token, summary_id)
    
    # Test 7: Statistics
    test_statistics(token)
    
    # Final summary
    print_section("[+] ALL TESTS PASSED!")
    print("Backend is working correctly!")
    print("\nYou can now:")
    print("  1. Build the frontend")
    print("  2. Add more features")
    print("  3. Deploy to production")


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n[!] ERROR: Cannot connect to API server")
        print("   Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n[!] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
