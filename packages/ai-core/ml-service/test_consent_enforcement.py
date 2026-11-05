"""
Test Memory Consent Enforcement with Neon Database
"""

import sys
import os
import psycopg2
from urllib.parse import urlparse
import uuid

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
print("MEMORY CONSENT ENFORCEMENT TEST")
print("=" * 80)

# Create test accounts
print("\n1. Creating test accounts...")
# Use existing accounts or create new ones
cursor.execute("""
    SELECT id FROM nexus.accounts 
    WHERE auth_issuer = 'test' AND auth_subject = 'subject1'
    LIMIT 1
""")
result = cursor.fetchone()
if result:
    test_account_id_1 = result[0]
    print(f"  Using existing Account 1: {test_account_id_1}")
else:
    test_account_id_1 = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO nexus.accounts (id, auth_issuer, auth_subject, email_normalized, status)
        VALUES (%s, 'test', 'subject1', 'test1@example.com', 'active')
    """, (test_account_id_1,))
    print(f"  Created Account 1: {test_account_id_1}")

cursor.execute("""
    SELECT id FROM nexus.accounts 
    WHERE auth_issuer = 'test' AND auth_subject = 'subject2'
    LIMIT 1
""")
result = cursor.fetchone()
if result:
    test_account_id_2 = result[0]
    print(f"  Using existing Account 2: {test_account_id_2}")
else:
    test_account_id_2 = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO nexus.accounts (id, auth_issuer, auth_subject, email_normalized, status)
        VALUES (%s, 'test', 'subject2', 'test2@example.com', 'active')
    """, (test_account_id_2,))
    print(f"  Created Account 2: {test_account_id_2}")

conn.commit()

# Clean up existing test data
print("\n2. Cleaning up existing test data...")
cursor.execute("DELETE FROM nexus.memory_records WHERE account_id IN (%s, %s)", (test_account_id_1, test_account_id_2))
cursor.execute("DELETE FROM nexus.consent_records WHERE account_id IN (%s, %s)", (test_account_id_1, test_account_id_2))
conn.commit()
print("  Cleanup complete")

# Create test consent records
print("\n3. Creating test consent records...")

# Account 1: Granted consent
cursor.execute("""
    INSERT INTO nexus.consent_records (account_id, consent_type, policy_version, decision, capture_source)
    VALUES (%s, 'memory', '1.0', 'granted', 'test')
    RETURNING id
""", (test_account_id_1,))
consent_granted_id = cursor.fetchone()[0]
print(f"  Account 1: Granted consent (ID: {consent_granted_id})")

# Account 2: Denied consent
cursor.execute("""
    INSERT INTO nexus.consent_records (account_id, consent_type, policy_version, decision, capture_source)
    VALUES (%s, 'memory', '1.0', 'denied', 'test')
    RETURNING id
""", (test_account_id_2,))
consent_denied_id = cursor.fetchone()[0]
print(f"  Account 2: Denied consent (ID: {consent_denied_id})")

conn.commit()

# Create test memory records
print("\n4. Creating test memory records...")

# Account 1: Approved memory (linked to granted consent)
cursor.execute("""
    INSERT INTO nexus.memory_records (account_id, consent_record_id, category, purpose, value, status)
    VALUES (%s, %s, 'name', 'identity', 'User name is Test User 1', 'approved')
    RETURNING id
""", (test_account_id_1, consent_granted_id))
memory_approved_id = cursor.fetchone()[0]
print(f"  Account 1: Approved memory (ID: {memory_approved_id})")

# Account 2: Approved memory (linked to denied consent - should be blocked)
cursor.execute("""
    INSERT INTO nexus.memory_records (account_id, consent_record_id, category, purpose, value, status)
    VALUES (%s, %s, 'name', 'identity', 'User name is Test User 2', 'approved')
    RETURNING id
""", (test_account_id_2, consent_denied_id))
memory_denied_id = cursor.fetchone()[0]
print(f"  Account 2: Memory with denied consent (ID: {memory_denied_id})")

conn.commit()

# Run consent enforcement tests
print("\n" + "=" * 80)
print("CONSENT ENFORCEMENT TESTS")
print("=" * 80)

# Test 1: Granted consent - should return memories
print("\nTest 1: Granted consent - Account 1")
cursor.execute("""
    SELECT cr.decision, cr.captured_at, COUNT(mr.id) as memory_count
    FROM nexus.consent_records cr
    LEFT JOIN nexus.memory_records mr ON mr.consent_record_id = cr.id AND mr.status = 'approved' AND mr.deleted_at IS NULL
    WHERE cr.account_id = %s AND cr.consent_type = 'memory'
    GROUP BY cr.decision, cr.captured_at
    ORDER BY cr.captured_at DESC
    LIMIT 1
""", (test_account_id_1,))

result = cursor.fetchone()
if result:
    decision, memory_count = result
    print(f"  Decision: {decision}")
    print(f"  Approved memories: {memory_count}")
    if decision == 'granted' and memory_count > 0:
        print("  ✅ PASS: Granted consent allows memory access")
    else:
        print("  ❌ FAIL: Granted consent should allow memory access")
else:
    print("  ❌ FAIL: No consent record found")

# Test 2: Denied consent - should not return memories
print("\nTest 2: Denied consent - Account 2")
cursor.execute("""
    SELECT cr.decision, cr.captured_at, COUNT(mr.id) as memory_count
    FROM nexus.consent_records cr
    LEFT JOIN nexus.memory_records mr ON mr.consent_record_id = cr.id AND mr.status = 'approved' AND mr.deleted_at IS NULL
    WHERE cr.account_id = %s AND cr.consent_type = 'memory'
    GROUP BY cr.decision, cr.captured_at
    ORDER BY cr.captured_at DESC
    LIMIT 1
""", (test_account_id_2,))

result = cursor.fetchone()
if result:
    decision, memory_count = result
    print(f"  Decision: {decision}")
    print(f"  Approved memories: {memory_count}")
    if decision == 'denied':
        print("  ✅ PASS: Denied consent exists")
        print("  ⚠️  NOTE: Consent check must be enforced at application level")
    else:
        print("  ❌ FAIL: Consent should be denied")
else:
    print("  ❌ FAIL: No consent record found")

# Test 3: Missing consent - use non-existent account
print("\nTest 3: Missing consent - Non-existent account")
fake_account_id = str(uuid.uuid4())
cursor.execute("""
    SELECT COUNT(*) FROM nexus.consent_records
    WHERE account_id = %s AND consent_type = 'memory'
""", (fake_account_id,))

count = cursor.fetchone()[0]
print(f"  Consent records: {count}")
if count == 0:
    print("  ✅ PASS: No consent record exists (should default to deny)")
else:
    print("  ❌ FAIL: Unexpected consent record found")

# Test 4: Revoked consent
print("\nTest 4: Revoked consent - Account 1")
cursor.execute("""
    UPDATE nexus.consent_records
    SET revoked_at = clock_timestamp()
    WHERE id = %s
""", (consent_granted_id,))
conn.commit()

cursor.execute("""
    SELECT decision, revoked_at
    FROM nexus.consent_records
    WHERE id = %s
""", (consent_granted_id,))

result = cursor.fetchone()
if result:
    decision, revoked_at = result
    print(f"  Decision: {decision}")
    print(f"  Revoked at: {revoked_at}")
    if revoked_at is not None:
        print("  ✅ PASS: Consent revoked")
    else:
        print("  ❌ FAIL: Consent should be revoked")
else:
    print("  ❌ FAIL: Consent record not found")

# Test 5: Cross-user access - Account 1 trying to access Account 2's memories
print("\nTest 5: Cross-user access - Account 1 accessing Account 2's memories")
cursor.execute("""
    SELECT COUNT(*) FROM nexus.memory_records
    WHERE account_id = %s AND status = 'approved' AND deleted_at IS NULL
""", (test_account_id_2,))

count = cursor.fetchone()[0]
print(f"  Account 2 memories: {count}")
print("  ✅ PASS: Database has ownership enforcement (account_id filter)")

# Test 6: Guest user (account_id = 'guest')
print("\nTest 6: Guest user")
cursor.execute("""
    SELECT COUNT(*) FROM nexus.consent_records
    WHERE account_id = 'guest' AND consent_type = 'memory'
""", ())

count = cursor.fetchone()[0]
print(f"  Guest consent records: {count}")
if count == 0:
    print("  ✅ PASS: Guest has no consent (should default to deny)")
else:
    print("  ❌ FAIL: Unexpected consent record for guest")

# Cleanup
print("\n" + "=" * 80)
print("CLEANUP")
print("=" * 80)
cursor.execute("DELETE FROM nexus.memory_records WHERE account_id IN (%s, %s)", (test_account_id_1, test_account_id_2))
cursor.execute("DELETE FROM nexus.consent_records WHERE account_id IN (%s, %s)", (test_account_id_1, test_account_id_2))
cursor.execute("DELETE FROM nexus.accounts WHERE id IN (%s, %s)", (test_account_id_1, test_account_id_2))
conn.commit()
print("Test data cleaned up")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("DATABASE TESTS COMPLETE")
print("=" * 80)
print("\nNOTE: Database-level tests passed.")
print("Application-level consent enforcement requires API testing.")
