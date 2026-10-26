"""
Parse DATABASE_URL manually (brackets cause URL parsing issues)
"""

database_url = "postgresql://postgres:[Nancy1000M@#$1]@db.qzfynpuvbybqgmbaccu.supabase.co:5432/postgres"

print("DATABASE_URL Analysis:")
print(f"  Protocol: postgresql")
print(f"  Username: postgres")
print(f"  Hostname: db.qzfynpuvbybqgmbaccu.supabase.co")
print(f"  Port: 5432")
print(f"  Database: postgres")
print(f"  Password: REDACTED (contains special characters: [ ], @, #, $)")

# Password contains: [Nancy1000M@#$1]
# Special chars: [ ] @ # $
# These need URL encoding

import urllib.parse

password = "[Nancy1000M@#$1]"
encoded_password = urllib.parse.quote(password, safe='')

print(f"\nURL-encoded password: {encoded_password}")

safe_url = f"postgresql://postgres:{encoded_password}@db.qzfynpuvbybqgmbaccu.supabase.co:5432/postgres"
print(f"\nSafe DATABASE_URL:")
print(f"  {safe_url}")
