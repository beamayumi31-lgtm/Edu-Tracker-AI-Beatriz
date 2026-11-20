/** Inicializa a distribuição Node compilada, sem instalar dependências nem alterar o banco. */
import { cp, access } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const standalone = resolve(root, '.next-hostinger/standalone');
await access(resolve(standalone, 'server.js'));
await cp(resolve(root, 'public'), resolve(standalone, 'public'), { recursive: true });
await cp(resolve(root, '.next-hostinger/static'), resolve(standalone, '.next-hostinger/static'), { recursive: true });
const child = spawn(process.execPath, [resolve(standalone, 'server.js')], {
  cwd: standalone, stdio: 'inherit', windowsHide: true,
  env: { ...process.env, HOSTNAME: process.env.HOSTNAME || '127.0.0.1', PORT: process.env.PORT || '3002' },
});
process.on('SIGINT', () => child.kill('SIGINT'));
process.on('SIGTERM', () => child.kill('SIGTERM'));
child.once('error', () => { console.error('Não foi possível iniciar o frontend compilado.'); process.exitCode = 1; });
child.once('exit', (code) => { process.exitCode = code || 0; });
