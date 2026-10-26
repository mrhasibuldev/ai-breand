"""
Phase 1B-E: Comprehensive Supabase Connectivity Diagnostic
Tests DNS, HTTP/API, and Supabase JS client connectivity
"""

import os
import socket
import urllib.parse
import subprocess
import json

print("=" * 70)
print("COMPREHENSIVE SUPABASE CONNECTIVITY DIAGNOSTIC")
print("=" * 70)

# Phase 1A: Check environment configuration
print("\n" + "=" * 70)
print("PHASE 1A: ENVIRONMENT CONFIGURATION")
print("=" * 70)

env_path = r"C:\Users\Nusaiba\Desktop\Ai Breand\.env"
supabase_url = None
supabase_anon_key = None
database_url = None

if os.path.exists(env_path):
    print(f"[PASS] .env file exists")
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('NEXT_PUBLIC_SUPABASE_URL='):
                supabase_url = line.split('=', 1)[1]
                print(f"[PASS] NEXT_PUBLIC_SUPABASE_URL found (length: {len(supabase_url)})")
            elif line.startswith('NEXT_PUBLIC_SUPABASE_ANON_KEY='):
                supabase_anon_key = line.split('=', 1)[1]
                print(f"[PASS] NEXT_PUBLIC_SUPABASE_ANON_KEY found (length: {len(supabase_anon_key)})")
            elif line.startswith('DATABASE_URL='):
                database_url = line.split('=', 1)[1]
                print(f"[PASS] DATABASE_URL found (length: {len(database_url)})")
else:
    print(f"[FAIL] .env file NOT found")

if not supabase_url:
    print("[FAIL] NEXT_PUBLIC_SUPABASE_URL NOT SET")
    print("   Supabase JS client cannot be initialized")
if not supabase_anon_key:
    print("[FAIL] NEXT_PUBLIC_SUPABASE_ANON_KEY NOT SET")
    print("   Supabase JS client cannot be initialized")

# Extract hostname from DATABASE_URL
db_hostname = None
if database_url:
    try:
        # Parse manually to avoid special character issues
        parts = database_url.split('@')
        if len(parts) > 1:
            host_part = parts[1].split('/')[0]
            db_hostname = host_part.split(':')[0]
            print(f"[INFO] DATABASE_HOSTNAME: {db_hostname}")
    except Exception as e:
        print(f"[ERROR] Could not parse DATABASE_URL: {e}")

# Phase 1B: DNS Resolution Tests
print("\n" + "=" * 70)
print("PHASE 1B: DNS RESOLUTION TESTS")
print("=" * 70)

test_hosts = []
if db_hostname:
    test_hosts.append(("DATABASE_HOSTNAME", db_hostname))
if supabase_url:
    # Extract hostname from Supabase URL
    try:
        from urllib.parse import urlparse
        parsed = urlparse(supabase_url)
        if parsed.hostname:
            test_hosts.append(("SUPABASE_API_HOSTNAME", parsed.hostname))
    except:
        pass

# Add test for known Supabase pattern
test_hosts.append(("SUPABASE_STANDARD", "qzfynpuvbybqgqmbaccu.supabase.co"))

dns_results = {}
for name, hostname in test_hosts:
    print(f"\nTesting: {name} ({hostname})")
    try:
        ip = socket.gethostbyname(hostname)
        print(f"  [PASS] DNS Resolution: {ip}")
        dns_results[name] = {"status": "PASS", "ip": ip}
    except socket.gaierror as e:
        print(f"  [FAIL] DNS Resolution: {e}")
        dns_results[name] = {"status": "FAIL", "error": str(e)}

# Phase 1C: TCP Connection Tests
print("\n" + "=" * 70)
print("PHASE 1C: TCP CONNECTION TESTS")
print("=" * 70)

tcp_results = {}
for name, hostname in test_hosts:
    port = 443 if "API" in name else 5432
    print(f"\nTesting: {name} ({hostname}:{port})")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((hostname, port))
        if result == 0:
            print(f"  [PASS] TCP Connection successful")
            tcp_results[name] = {"status": "PASS"}
        else:
            print(f"  [FAIL] TCP Connection failed (code: {result})")
            tcp_results[name] = {"status": "FAIL", "code": result}
        sock.close()
    except Exception as e:
        print(f"  [FAIL] TCP Connection error: {e}")
        tcp_results[name] = {"status": "FAIL", "error": str(e)}

# Phase 1D: Test Supabase HTTP/API Connectivity
print("\n" + "=" * 70)
print("PHASE 1D: SUPABASE HTTP/API CONNECTIVITY")
print("=" * 70)

http_results = {}
if supabase_url:
    print(f"\nTesting: Supabase API Endpoint")
    print(f"  URL: {supabase_url}")
    
    try:
        import urllib.request
        import ssl
        
        # Create SSL context that doesn't verify (for testing only)
        context = ssl._create_unverified_context()
        
        # Try to fetch a simple endpoint
        test_url = f"{supabase_url}/auth/v1/user"
        print(f"  Testing: {test_url}")
        
        request = urllib.request.Request(test_url)
        request.add_header('apikey', supabase_anon_key if supabase_anon_key else '')
        
        try:
            response = urllib.request.urlopen(request, timeout=10, context=context)
            status = response.getcode()
            print(f"  [PASS] HTTP Connection successful (status: {status})")
            http_results["supabase_api"] = {"status": "PASS", "http_status": status}
        except urllib.error.HTTPError as e:
            # 401/403 is expected without auth - connection works
            if e.code in [401, 403]:
                print(f"  [PASS] HTTP Connection works (auth required - expected)")
                http_results["supabase_api"] = {"status": "PASS", "http_status": e.code}
            else:
                print(f"  [FAIL] HTTP Error: {e.code}")
                http_results["supabase_api"] = {"status": "FAIL", "error": str(e)}
        except urllib.error.URLError as e:
            print(f"  [FAIL] URL Error: {e.reason}")
            http_results["supabase_api"] = {"status": "FAIL", "error": str(e.reason)}
            
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        http_results["supabase_api"] = {"status": "FAIL", "error": str(e)}
else:
    print("[SKIP] Supabase URL not configured")

# Phase 1E: Summary
print("\n" + "=" * 70)
print("PHASE 1E: DIAGNOSTIC SUMMARY")
print("=" * 70)

print("\nEnvironment Variables:")
print(f"  NEXT_PUBLIC_SUPABASE_URL: {'SET' if supabase_url else 'NOT SET'}")
print(f"  NEXT_PUBLIC_SUPABASE_ANON_KEY: {'SET' if supabase_anon_key else 'NOT SET'}")
print(f"  DATABASE_URL: {'SET' if database_url else 'NOT SET'}")

print("\nDNS Resolution:")
for name, result in dns_results.items():
    print(f"  {name}: {result['status']}")

print("\nTCP Connection:")
for name, result in tcp_results.items():
    print(f"  {name}: {result['status']}")

print("\nHTTP/API:")
if http_results:
    for name, result in http_results.items():
        print(f"  {name}: {result['status']}")
else:
    print("  [NOT TESTED]")

# Phase 1F: Architecture Decision
print("\n" + "=" * 70)
print("PHASE 1F: ARCHITECTURE DECISION")
print("=" * 70)

state_a = any(r.get("status") == "PASS" for name, r in tcp_results.items() if "DATABASE" in name)
state_b = http_results.get("supabase_api", {}).get("status") == "PASS"
state_c = not state_a and not state_b

if state_a:
    print("STATE A: Direct PostgreSQL connectivity works")
    print("  Recommendation: Can use PostgreSQL directly")
elif state_b:
    print("STATE B: Supabase API connectivity works")
    print("  Recommendation: Use Supabase JS client/API")
    print("  Note: Direct PostgreSQL blocked but API available")
elif state_c:
    print("STATE C: Both direct PostgreSQL and Supabase API blocked")
    print("  Recommendation: Fix network connectivity before proceeding")
else:
    print("UNKNOWN STATE: Could not determine connectivity")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
