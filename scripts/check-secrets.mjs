import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

const tracked = execFileSync(
  'rg',
  ['--files', '-g', '!node_modules/**', '-g', '!**/dist/**', '-g', '!**/.next/**'],
  { encoding: 'utf8' },
)
  .trim()
  .split(/\r?\n/)
  .filter(Boolean);
const suspicious =
  /(?:sk-[A-Za-z0-9]{20,}|-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----|AKIA[0-9A-Z]{16})/;
for (const file of tracked)
  if (!file.endsWith('.lock')) {
    if (suspicious.test(readFileSync(file, 'utf8')))
      throw new Error(`Potential secret detected in ${file}`);
  }
process.stdout.write('Secret scan passed\n');
