#!/usr/bin/env python3
"""
DHAN API Diagnostic Script
Tests various endpoints to identify the issue
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_file = Path(__file__).parent / ".env"
load_dotenv(env_file)

DHAN_API_KEY = os.getenv("DHAN_API_KEY", "")
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "")

print("=" * 70)
print(" DHAN API DIAGNOSTICS ".center(70))
print("=" * 70)

if not DHAN_API_KEY or not DHAN_CLIENT_ID:
    print("\n❌ ERROR: Missing credentials in .env file")
    print(f"   DHAN_API_KEY: {'Set' if DHAN_API_KEY else 'NOT SET'}")
    print(f"   DHAN_CLIENT_ID: {'Set' if DHAN_CLIENT_ID else 'NOT SET'}")
    exit(1)

print(f"\n[OK] API Key: {DHAN_API_KEY[:30]}...")
print(f"[OK] Client ID: {DHAN_CLIENT_ID}")

BASE_URL = "https://api.dhan.co"

headers = {
    "Authorization": f"Bearer {DHAN_API_KEY}",
    "Content-Type": "application/json"
}

# Test different endpoints
endpoints = [
    ("GET", "/v2/user/account", {}, "User Account Info"),
    ("GET", "/v1/user/account", {}, "User Account Info (v1)"),
    ("GET", "/v2/quotes", {"securityId": "1", "mode": "LTP"}, "Quote (v2)"),
    ("GET", "/v1/quotes", {"securityId": "1", "mode": "LTP"}, "Quote (v1)"),
    ("POST", "/v2/user/account", {}, "User Account (POST)"),
]

print("\n" + "=" * 70)
print("Testing Endpoints:")
print("=" * 70)

for method, endpoint, params, description in endpoints:
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n[{method}] {description}")
    print(f"    URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=10,
                verify=False
            )
        else:
            response = requests.post(
                url,
                headers=headers,
                json=params,
                timeout=10,
                verify=False
            )
        
        print(f"    Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"    [SUCCESS]")
            try:
                data = response.json()
                print(f"    Response: {json.dumps(data, indent=6)[:200]}...")
            except:
                print(f"    Response: {response.text[:200]}")
        elif response.status_code in [400, 401, 403]:
            print(f"    [AUTH ERROR]")
            try:
                data = response.json()
                print(f"    Error: {data}")
            except:
                print(f"    Response: {response.text}")
        elif response.status_code == 404:
            print(f"    [NOT FOUND - Endpoint may not exist]")
        else:
            print(f"    [OTHER ERROR]")
            print(f"    Response: {response.text[:200]}")
    
    except Exception as e:
        print(f"    [EXCEPTION] {str(e)}")

print("\n" + "=" * 70)
print("DIAGNOSTIC SUMMARY:")
print("=" * 70)
print("""
If all endpoints return 404:
  → API Key may be invalid or expired
  → Check DHAN_API_KEY in .env file
  → Get a new API key from DHAN Dashboard

If some endpoints work:
  → The API structure may be different than expected
  → Check DHAN API documentation
  → Update endpoint URLs in src/provider.py

Next Steps:
  1. Check your DHAN Dashboard for valid API key
  2. Verify API key hasn't expired
  3. Contact DHAN support if credentials are correct but endpoints fail
""")
print("=" * 70)
