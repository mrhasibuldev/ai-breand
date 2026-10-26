"""
Run migration with proper URL encoding
"""

import urllib.parse
import subprocess
import os

# Original password
password = "[Nancy1000M@#$1]"
url_encoded_password = urllib.parse.quote(password, safe='')

# Build DATABASE_URL
database_url = f"postgresql://postgres:{url_encoded_password}@db.qzfynpuvbybqgqmbaccu.supabase.co:5432/postgres"

print(f"DATABASE_URL: {database_url}")

# Set environment variable
os.environ['DATABASE_URL'] = database_url

# Run migration
os.chdir(r"C:\Users\Nusaiba\Desktop\Ai Breand\packages\database-core")
result = subprocess.run(["node", "run-migrations.js"], capture_output=True, text=True)

print(result.stdout)
print(result.stderr)
