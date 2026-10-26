"""
Run migration with Python psycopg2 directly
"""

import psycopg2
import urllib.parse

# Original password
password = "[Nancy1000M@#$1]"
url_encoded_password = urllib.parse.quote(password, safe='')

# Build DATABASE_URL
database_url = f"postgresql://postgres:{url_encoded_password}@db.qzfynpuvbybqgqmbaccu.supabase.co:5432/postgres"

print(f"Connecting to database...")

try:
    # Connect to database
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    print("Connected successfully!")
    
    # Read migration file
    with open(r"C:\Users\Nusaiba\Desktop\Ai Breand\packages\database-core\migrations\013_knowledge_tables.sql", 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print("Executing migration...")
    
    # Execute migration
    cursor.execute(migration_sql)
    conn.commit()
    
    print("Migration completed successfully!")
    
    # Verify tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'nexus' 
        AND table_name IN ('knowledge_sources', 'documents', 'document_chunks', 'document_metadata', 'ingestion_runs', 'knowledge_gaps')
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print(f"\nCreated tables: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
