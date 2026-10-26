"""
Phase 1: DATABASE_URL Diagnostic (Windows-compatible version)
Check environment loading and database connectivity
"""

import os
import urllib.parse
import socket
import ssl

# Parse DATABASE_URL
database_url = "postgresql://postgres:%5BNancy1000M@40%23%241%5D@db.qzfynpuvbybqgqmbaccu.supabase.co:5432/postgres"

print("=" * 60)
print("DATABASE_URL DIAGNOSTIC")
print("=" * 60)

# Parse URL components
try:
    password = "[Nancy1000M@#$1]"
    encoded_password = urllib.parse.quote(password, safe='')
    
    print("\nURL Components:")
    print(f"  Protocol: postgresql")
    print(f"  Username: postgres")
    print(f"  Password: REDACTED (length: {len(password)})")
    print(f"  Hostname: db.qzfynpuvbybqgqmbaccu.supabase.co")
    print(f"  Port: 5432")
    print(f"  Database: postgres")
    print(f"  Encoded password: {encoded_password}")
    
    # Rebuild safe URL
    safe_url = f"postgresql://postgres:{encoded_password}@db.qzfynpuvbybqgqmbaccu.supabase.co:5432/postgres"
    print(f"\nSafe URL (for connection):")
    print(f"  {safe_url}")
    
except Exception as e:
    print(f"Error parsing URL: {e}")

# DNS Resolution
print("\n" + "=" * 60)
print("DNS RESOLUTION TEST")
print("=" * 60)

hostname = "db.qzfynpuvbybqgqmbaccu.supabase.co"
port = 5432

try:
    ip_address = socket.gethostbyname(hostname)
    print(f"[PASS] DNS Resolution SUCCESS")
    print(f"  Hostname: {hostname}")
    print(f"  IP Address: {ip_address}")
except socket.gaierror as e:
    print(f"[FAIL] DNS Resolution FAILED")
    print(f"  Error: {e}")
    print(f"  Cause: Hostname cannot be resolved")
    print(f"  Impact: Cannot connect to database")
    print(f"\nROOT CAUSE IDENTIFIED:")
    print(f"  The Supabase hostname cannot be resolved from this machine.")
    print(f"  This is a NETWORK/DNS issue, not a password issue.")
    print(f"\nPossible causes:")
    print(f"  1. DNS server configuration")
    print(f"  2. Network firewall blocking")
    print(f"  3. VPN/proxy interference")
    print(f"  4. ISP restrictions")
    print(f"  5. Local network configuration")
    exit(1)

# TCP Connection Test
print("\n" + "=" * 60)
print("TCP CONNECTION TEST")
print("=" * 60)

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((hostname, port))
    
    if result == 0:
        print(f"[PASS] TCP Connection SUCCESS")
        print(f"  Host: {hostname}:{port}")
        print(f"  PostgreSQL is reachable")
    else:
        print(f"[FAIL] TCP Connection FAILED")
        print(f"  Error code: {result}")
        print(f"  Cause: Cannot establish TCP connection")
    
    sock.close()
except Exception as e:
    print(f"[FAIL] TCP Connection FAILED")
    print(f"  Error: {e}")

# SSL/TLS Test
print("\n" + "=" * 60)
print("SSL/TLS TEST")
print("=" * 60)

try:
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(f"[PASS] SSL/TLS SUCCESS")
            print(f"  SSL Version: {ssock.version()}")
            print(f"  Certificate verified")
except Exception as e:
    print(f"[FAIL] SSL/TLS FAILED")
    print(f"  Error: {e}")

# PostgreSQL Connection Test
print("\n" + "=" * 60)
print("POSTGRESQL CONNECTION TEST")
print("=" * 60)

try:
    import psycopg2
    
    conn = psycopg2.connect(safe_url)
    cursor = conn.cursor()
    
    print(f"[PASS] PostgreSQL Connection SUCCESS")
    print(f"  Connected to: {hostname}:{port}")
    print(f"  Database: postgres")
    
    # Test query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"  PostgreSQL Version: {version[0][:50]}...")
    
    # Check nexus schema
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'nexus'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    print(f"\n  Nexus Schema Tables ({len(tables)}):")
    for table in tables:
        print(f"    - {table[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"[FAIL] PostgreSQL Connection FAILED")
    print(f"  Error: {e}")
    print(f"  Type: {type(e).__name__}")

print("\n" + "=" * 60)
print("ENVIRONMENT FILE CHECK")
print("=" * 60)

env_path = r"C:\Users\Nusaiba\Desktop\Ai Breand\.env"
if os.path.exists(env_path):
    print(f"[PASS] .env file exists: {env_path}")
    with open(env_path, 'r') as f:
        content = f.read()
        if 'DATABASE_URL' in content:
            print(f"[PASS] DATABASE_URL found in .env")
            # Count length but don't show password
            for line in content.split('\n'):
                if line.startswith('DATABASE_URL='):
                    print(f"  Length: {len(line)} characters")
        else:
            print(f"[FAIL] DATABASE_URL NOT found in .env")
else:
    print(f"[FAIL] .env file NOT found: {env_path}")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
