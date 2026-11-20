/** Inicia somente o ambiente local. Não instala serviços nem altera o banco. */
import { spawn, spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { createServer } from 'node:net';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { setTimeout as delay } from 'node:timers/promises';

const frontend = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const backend = resolve(frontend, '../edutrack-api');
const python = join(backend, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const cli = join(frontend, 'node_modules/vinext/dist/cli.js');
const children = [];
let stopping = false;

function assertPortFree(port) {
  return new Promise((resolvePort, reject) => {
    const server = createServer();
    server.once('error', () => reject(new Error('A porta ' + port + ' está ocupada. Encerre a outra execução do EduTrack antes de iniciar; nenhum processo será encerrado automaticamente.')));
    server.listen(port, '127.0.0.1', () => server.close(resolvePort));
  });
}
function start(command, args, cwd, env) {
  const child = spawn(command, args, { cwd, env, stdio: 'inherit', windowsHide: true });
  children.push(child);
  child.once('error', (error) => { console.error('Não foi possível iniciar:', error.message); stop(1); });
  child.once('exit', (code) => { if (!stopping) { console.error('Um dos servidores encerrou (código ' + code + ').'); stop(code || 1); } });
  return child;
}
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  console.log('\nEncerrando somente os servidores iniciados por este comando…');
  for (const child of [...children].reverse()) {
    if (!child.pid || child.exitCode !== null || child.signalCode !== null) continue;
    if (process.platform === 'win32') {
      // IDs vêm dos processos filhos desta execução, nunca de uma busca genérica.
      spawnSync('taskkill.exe', ['/PID', String(child.pid), '/T', '/F'], { stdio: 'ignore', windowsHide: true });
    } else child.kill('SIGTERM');
  }
  process.exit(code);
}
async function ready(url, check = (response) => response.ok) {
  const deadline = Date.now() + 90000;
  while (!stopping && Date.now() < deadline) {
    try {
      const response = await fetch(url, { signal: AbortSignal.timeout(5000) });
      if (await check(response)) { await response.body?.cancel(); return; }
      await response.body?.cancel();
    } catch { /* Aguarda a inicialização, sem abrir um endereço ainda indisponível. */ }
    await delay(750);
  }
  throw new Error('O servidor não ficou pronto: ' + url + '. Confira os erros acima.');
}
function openChrome(urls) {
  if (process.platform !== 'win32') return;
  const candidates = [
    process.env.PROGRAMFILES && join(process.env.PROGRAMFILES, 'Google/Chrome/Application/chrome.exe'),
    process.env['PROGRAMFILES(X86)'] && join(process.env['PROGRAMFILES(X86)'], 'Google/Chrome/Application/chrome.exe'),
    process.env.LOCALAPPDATA && join(process.env.LOCALAPPDATA, 'Google/Chrome/Application/chrome.exe'),
  ];
  const chrome = candidates.find((candidate) => candidate && existsSync(candidate));
  if (!chrome) { console.log('Chrome não localizado. Abra os endereços acima no seu navegador.'); return; }
  // Sem perfil alternativo: reutiliza a sessão normal do Chrome do usuário.
  const browser = spawn(chrome, urls, { detached: true, stdio: 'ignore', windowsHide: false });
  browser.on('error', () => console.log('Abra os links acima manualmente no Chrome.'));
  browser.unref();
}
process.on('SIGINT', () => stop());
process.on('SIGTERM', () => stop());
try {
  if (!existsSync(python) || !existsSync(cli)) throw new Error('Dependências ausentes. Consulte work/edutrack-documentacao/COMECE_AQUI.md.');
  await Promise.all([assertPortFree(8000), assertPortFree(3002)]);
  console.log('EduTrack LOCAL — SQL Server localhost\\SQLEXPRESS / EduTrackIA');
  console.log('Cadastro e CRUD gravam dados reais nesse banco. Nenhuma tabela é criada ou alterada.');
  console.log('Para parar, mantenha esta janela aberta e pressione Ctrl+C.\n');
  start(python, ['-m', 'edutrack.run', '--local-sql-certificate'], backend, {
    ...process.env,
    EDUTRACK_ENVIRONMENT: 'development',
    EDUTRACK_DB_WRITES_ENABLED: 'true',
    EDUTRACK_SQL_SERVER: 'localhost\\SQLEXPRESS',
    EDUTRACK_SQL_DATABASE: 'EduTrackIA',
    EDUTRACK_DATABASE_URL: '',
    EDUTRACK_TRUST_SERVER_CERTIFICATE: 'true',
  });
  await ready('http://127.0.0.1:8000/ready');
  await ready('http://127.0.0.1:8000/docs');
  start(process.execPath, [cli, 'dev', '--host', '127.0.0.1', '--port', '3002', '--strictPort'], frontend, { ...process.env, EDUTRACK_API_URL: 'http://127.0.0.1:8000' });
  await ready('http://localhost:3002/login');
  await ready('http://localhost:3002/api/backend/me', (response) => response.status === 401);
  console.log('\nPRONTO');
  console.log('Site:    http://localhost:3002/login');
  console.log('Swagger: http://127.0.0.1:8000/docs');
  console.log('Contrato: http://127.0.0.1:8000/openapi.json');
  if (!process.argv.includes('--no-browser')) openChrome(['http://localhost:3002/login', 'http://127.0.0.1:8000/docs']);
  // Entrada usada também na validação automatizada do encerramento.
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (input) => { if (input.trim().toLowerCase() === 'sair') stop(); });
  process.stdin.resume();
} catch (error) {
  console.error('\n' + error.message);
  stop(1);
}

