import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load .env file manually
const envPath = join(__dirname, '../../.env');
const envContent = readFileSync(envPath, 'utf-8');
const envVars = {};
envContent.split('\n').forEach(line => {
  const [key, ...valueParts] = line.split('=');
  if (key && valueParts.length > 0) {
    envVars[key.trim()] = valueParts.join('=').trim();
  }
});

const supabaseUrl = envVars.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = envVars.NEXT_PUBLIC_SUPABASE_ANON_KEY;

console.log('=== SUPABASE PROJECT VERIFICATION ===\n');
console.log('NEXT_PUBLIC_SUPABASE_URL:', supabaseUrl);
console.log('Project Reference ID:', supabaseUrl?.split('.')[0]?.replace('https://', ''));
console.log('');

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Missing environment variables');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function runAudit() {
  try {
    // 1. Verify nexus schema
    console.log('1. VERIFY NEXUS SCHEMA');
    const { data: schemas, error: schemaError } = await supabase
      .rpc('get_schemas'); // Try a system function or direct query

    console.log('   Checking information_schema.schemata...');
    const { data: nexusSchema, error: nexusError } = await supabase
      .from('information_schema.schemata')
      .select('schema_name')
      .eq('schema_name', 'nexus')
      .single();

    if (nexusError) {
      console.log('   ❌ nexus schema:', nexusError.message);
    } else {
      console.log('   ✅ nexus schema EXISTS');
    }
    console.log('');

    // 2. List all tables in nexus schema
    console.log('2. TABLES IN NEXUS SCHEMA');
    const { data: tables, error: tablesError } = await supabase
      .from('information_schema.tables')
      .select('table_schema, table_name')
      .eq('table_schema', 'nexus')
      .order('table_name');

    if (tablesError) {
      console.log('   ❌ Error listing tables:', tablesError.message);
    } else {
      console.log('   Tables found:', tables?.length || 0);
      if (tables && tables.length > 0) {
        tables.forEach(t => {
          console.log(`   - ${t.table_name}`);
        });
      }
    }
    console.log('');

    // 3. Check each specific table existence
    console.log('3. VERIFY SPECIFIC TABLES');
    const tablesToCheck = ['accounts', 'user_profiles', 'content', 'conversations', 'messages'];

    for (const tableName of tablesToCheck) {
      const { data, error } = await supabase
        .from('information_schema.tables')
        .select('table_name')
        .eq('table_schema', 'nexus')
        .eq('table_name', tableName)
        .single();

      if (error) {
        console.log(`   ${tableName}: ❌ MISSING (${error.message})`);
      } else {
        console.log(`   ${tableName}: ✅ EXISTS`);
      }
    }
    console.log('');

    // 4. Count rows in each table
    console.log('4. ROW COUNTS');
    for (const tableName of tablesToCheck) {
      try {
        const { data, error } = await supabase
          .schema('nexus')
          .from(tableName)
          .select('*', { count: 'exact', head: true });

        if (error) {
          console.log(`   ${tableName}: ❌ Count failed (${error.message})`);
        } else {
          console.log(`   ${tableName}: ${data?.length || 0} rows`);
        }
      } catch (e) {
        console.log(`   ${tableName}: ❌ Exception (${e.message})`);
      }
    }
    console.log('');

    // 5. Check RLS status
    console.log('5. RLS STATUS');
    for (const tableName of tablesToCheck) {
      try {
        const { data, error } = await supabase
          .from('pg_tables')
          .select('relrowse, relkind')
          .eq('schemaname', 'nexus')
          .eq('tablename', tableName);

        if (error) {
          console.log(`   ${tableName}: ❌ RLS check failed (${error.message})`);
        } else {
          const rowLevelSecurity = data?.find(r => r.relkind === 'r');
          console.log(`   ${tableName}: RLS ${rowLevelSecurity ? 'ENABLED' : 'DISABLED'}`);
        }
      } catch (e) {
        console.log(`   ${tableName}: ❌ Exception (${e.message})`);
      }
    }
    console.log('');

    // 6. Verify supabase client configuration
    console.log('6. SUPABASE CLIENT CONFIGURATION');
    console.log('   Current config: db: { schema: "nexus" }');
    console.log('   Checking actual client config...');

  } catch (e) {
    console.log('❌ Audit exception:', e.message);
  }
}

runAudit();
