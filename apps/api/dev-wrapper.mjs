import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';

// Load .env from project root
const __filename = fileURLToPath(import.meta.url);
const projectRoot = path.resolve(path.dirname(__filename), '..', '..');
dotenv.config({ path: path.join(projectRoot, '.env') });

// Use pnpm exec to run tsx with the loaded environment
const serverPath = path.join(path.dirname(__filename), 'src', 'server.ts');
const tsx = spawn('pnpm', ['exec', 'tsx', 'watch', serverPath], {
  stdio: 'inherit',
  shell: true,
  env: { ...process.env }
});

tsx.on('exit', (code) => process.exit(code ?? 0));
