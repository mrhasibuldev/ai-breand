import dotenv from 'dotenv';
import path from 'path';

const envPath = path.resolve(process.cwd(), '.env');
console.log('Loading .env from:', envPath);

const config = dotenv.config({ path: envPath });
console.log('Dotenv error:', config.error);
console.log('DATABASE_URL:', process.env.DATABASE_URL ? 'SET' : 'NOT SET');
console.log('All env keys:', Object.keys(process.env).filter(k => k.includes('DATABASE') || k.includes('SUPABASE')));
