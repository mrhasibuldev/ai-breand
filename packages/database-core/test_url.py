"""
Parse DATABASE_URL safely without exposing password
"""

import urllib.parse

database_url = "postgresql://postgres:[Nancy1000M@#$1]@db.qzfynpuvbybqgqmbaccu.supabase.co:5432/postgres"

try:
    parsed = urllib.parse.urlparse(database_url)
    
    print("DATABASE_URL Analysis:")
    print(f"  Protocol: {parsed.scheme}")
    print(f"  Username: {parsed.username}")
    print(f"  Hostname: {parsed.hostname}")
    print(f"  Port: {parsed.port}")
    print(f"  Database: {parsed.path.lstrip('/')}")
    print(f"  Password: REDACTED (length: {len(parsed.password)})")
    
    # Check if password contains special characters
    password = parsed.password
    special_chars = ['@', ':', '/', '?', '#', '&', '%']
    has_special = any(char in password for char in special_chars)
    print(f"  Password contains special chars: {has_special}")
    
    # Try URL-encoding
    encoded_password = urllib.parse.quote(password, safe='')
    print(f"  Encoded password length: {len(encoded_password)}")
    
    # Rebuild URL with encoded password
    safe_url = f"{parsed.scheme}://{parsed.username}:{encoded_password}@{parsed.hostname}:{parsed.port}{parsed.path}"
    print(f"\nSafe URL (password encoded):")
    print(f"  {safe_url}")
    
except Exception as e:
    print(f"Error parsing URL: {e}")
