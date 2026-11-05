"""
Check if Neon database contains production data
"""

import sys
import os
import psycopg2
from urllib.parse import urlparse

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Read DATABASE_URL
env_path = r"C:\Users\Nusaiba\Desktop\Ai Breand\.env"
with open(env_path, 'r') as f:
    for line in f:
        if line.startswith('DATABASE_URL='):
            database_url = line.strip().split('=', 1)[1]
            break

# Parse connection string
parsed = urlparse(database_url)

conn = psycopg2.connect(
    host=parsed.hostname,
    port=parsed.port,
    database=parsed.path[1:],
    user=parsed.username,
    password=parsed.password,
    sslmode='require'
)

cursor = conn.cursor()

print("=" * 80)
print("DATABASE PRODUCTION DATA CHECK")
print("=" * 80)

# Check accounts
cursor.execute("SELECT COUNT(*) FROM nexus.accounts")
account_count = cursor.fetchone()[0]
print(f"\nAccounts: {account_count}")

if account_count > 0:
    print("  ⚠️  WARNING: Database contains accounts")
    cursor.execute("SELECT auth_issuer, email_normalized FROM nexus.accounts LIMIT 5")
    for row in cursor.fetchall():
        print(f"    {row[0]} / {row[1]}")
else:
    print("  ✅ No accounts found (safe for test data)")

# Check consent records
cursor.execute("SELECT COUNT(*) FROM nexus.consent_records")
consent_count = cursor.fetchone()[0]
print(f"\nConsent records: {consent_count}")

if consent_count > 0:
    print("  ⚠️  WARNING: Database contains consent records")
else:
    print("  ✅ No consent records found (safe for test data)")

# Check memory records
cursor.execute("SELECT COUNT(*) FROM nexus.memory_records")
memory_count = cursor.fetchone()[0]
print(f"\nMemory records: {memory_count}")

if memory_count > 0:
    print("  ⚠️  WARNING: Database contains memory records")
else:
    print("  ✅ No memory records found (safe for test data)")

# Check if there are any records from the previous test attempt
cursor.execute("SELECT COUNT(*) FROM nexus.accounts WHERE auth_issuer = 'test'")
test_account_count = cursor.fetchone()[0]
print(f"\nTest accounts (auth_issuer='test'): {test_account_count}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

if account_count == 0 and consent_count == 0 and memory_count == 0:
    print("✅ Database is empty - SAFE to create test records")
elif test_account_count > 0 and consent_count == 0 and memory_count == 0:
    print("✅ Only test accounts exist - SAFE to continue with test records")
elif account_count > 0 or consent_count > 0 or memory_count > 0:
    print("❌ Database contains real user data - DO NOT create test records")
    print("   RECOMMENDATION: Use a dedicated test database")

cursor.close()
conn.close()
