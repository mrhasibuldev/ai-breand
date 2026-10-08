import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const portValue = process.env.WEB_PORT ?? '3000';
const port = Number(portValue);
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  process.stderr.write('WEB_PORT must be an integer from 1 to 65535.\n');
  process.exit(1);
}

const nextCli = fileURLToPath(new URL('./node_modules/next/dist/bin/next', import.meta.url));
const child = spawn(process.execPath, [nextCli, 'dev', '-p', String(port)], {
  stdio: 'inherit',
  env: process.env,
});
child.on('error', (error) => {
  process.stderr.write(`Unable to start the web development server: ${error.message}\n`);
  process.exitCode = 1;
});
for (const signal of ['SIGINT', 'SIGTERM'])
  process.once(signal, () => {
    if (child.exitCode === null) child.kill(signal);
  });
child.on('exit', (code, signal) => {
  process.exitCode = code ?? (signal ? 1 : 0);
});
