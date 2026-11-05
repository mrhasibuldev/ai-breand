"""
Test Neon database connection and verify consent_records schema
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

# Read DATABASE_URL from .env
env_path = r"C:\Users\Nusaiba\Desktop\Ai Breand\.env"

with open(env_path, 'r') as f:
    for line in f:
        if line.startswith('DATABASE_URL='):
            database_url = line.strip().split('=', 1)[1]
            break

print("Testing database connection...")
print(f"Database URL: {database_url[:50]}...")

try:
    # Parse connection string
    parsed = urlparse(database_url)
    
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path[1:],  # Remove leading /
        user=parsed.username,
        password=parsed.password,
        sslmode='require'
    )
    
    cursor = conn.cursor()
    
    print("✅ Database connection successful")
    
    # Check if nexus schema exists
    cursor.execute("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name = 'nexus'
    """)
    
    schema_exists = cursor.fetchone()
    if schema_exists:
        print("✅ nexus schema exists")
    else:
        print("❌ nexus schema does NOT exist")
    
    # Check if consent_records table exists
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'nexus' AND table_name = 'consent_records'
    """)
    
    table_exists = cursor.fetchone()
    if table_exists:
        print("✅ consent_records table exists")
        
        # Check table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'nexus' AND table_name = 'consent_records'
            ORDER BY ordinal_position
        """)
        
        print("\nTable structure:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")
        
        # Check if there are any consent records
        cursor.execute("SELECT COUNT(*) FROM nexus.consent_records")
        count = cursor.fetchone()[0]
        print(f"\nExisting consent records: {count}")
        
    else:
        print("❌ consent_records table does NOT exist")
    
    # Check if memory_records table exists
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'nexus' AND table_name = 'memory_records'
    """)
    
    memory_table_exists = cursor.fetchone()
    if memory_table_exists:
        print("✅ memory_records table exists")
        
        cursor.execute("SELECT COUNT(*) FROM nexus.memory_records")
        memory_count = cursor.fetchone()[0]
        print(f"Existing memory records: {memory_count}")
    else:
        print("❌ memory_records table does NOT exist")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    import traceback
    traceback.print_exc()
