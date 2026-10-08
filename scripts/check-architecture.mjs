import { existsSync, readFileSync, readdirSync } from 'node:fs';

const forbidden = [
  ['packages/domain/src', '@nexusai/ai-core'],
  ['apps/web', 'DATABASE_URL'],
  ['packages/ai-core/src', 'API_KEY'],
];
for (const [root, token] of forbidden) {
  if (!existsSync(root)) continue;
  // This lightweight guard is intentionally lexical; deeper dependency rules belong to later tooling.
  const files = [];
  const walk = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const path = `${dir}/${entry.name}`;
      if (entry.isDirectory()) walk(path);
      else if (/\.(ts|tsx|mjs|js)$/.test(entry.name)) files.push(path);
    }
  };
  walk(root);
  for (const file of files)
    if (readFileSync(file, 'utf8').includes(token))
      throw new Error(`Architecture boundary violated: ${file} contains ${token}`);
}
process.stdout.write('Architecture guardrails passed\n');
