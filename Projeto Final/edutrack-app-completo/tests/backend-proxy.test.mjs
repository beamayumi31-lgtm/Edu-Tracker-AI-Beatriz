import assert from 'node:assert/strict';
import { test } from 'node:test';
import { proxyBackend } from '../app/lib/backend-proxy.ts';
import { academicView } from '../app/lib/academic-api.ts';

const origin = 'http://localhost:3002';

test('Busca e relatório privado preservam autenticação, parâmetros e bytes PDF', async () => {
  const cookie = { Cookie: 'edutrack_session=abc.def.ghi' };
  const unreachable = () => { throw new Error('Não deveria chamar a API'); };
  for (const path of ['search/disciplines', 'reports/generate', 'reports/progress.pdf']) {
    assert.equal((await proxyBackend(request(path), undefined, unreachable)).status, 401);
  }
  const searched = await proxyBackend(request('search/disciplines?q=SQL&overdue=true&url=https://example.com', 'GET', undefined, cookie), 'http://127.0.0.1:8000', async (url) => {
    assert.equal(url.searchParams.get('q'), 'SQL'); assert.equal(url.searchParams.get('overdue'), 'true');
    assert.equal(url.searchParams.has('url'), false); return Response.json({ items: [], total: 0 });
  });
  assert.equal(searched.status, 200);
  const download = await proxyBackend(request('reports/progress.pdf', 'GET', undefined, cookie), 'http://127.0.0.1:8000', async () => new Response('%PDF-1.4\nconteudo-de-teste', { headers: { 'Content-Type': 'application/pdf' } }));
  assert.equal(download.status, 200); assert.match(await download.text(), /^%PDF-/);
  assert.equal(download.headers.get('cache-control'), 'no-store');
  assert.match(download.headers.get('content-disposition'), /attachment/);
  const invalid = await proxyBackend(request('reports/progress.pdf', 'GET', undefined, cookie), 'http://127.0.0.1:8000', async () => new Response('<html>erro</html>', { headers: { 'Content-Type': 'application/pdf' } }));
  assert.equal(invalid.status, 502);
  const denied = await proxyBackend(request('reports/progress.pdf', 'GET', undefined, cookie), 'http://127.0.0.1:8000', async () => Response.json({ detail: 'Expirou' }, { status: 401 }));
  assert.equal(denied.status, 401); assert.match(denied.headers.get('set-cookie'), /Max-Age=0/);
});

test('Conteúdo da turma exige sessão e preserva apenas parâmetros permitidos', async () => {
  const path = 'integrations/google/disciplines/12345678-1234-1234-1234-123456789012/content?tipo=material&offset=30&limit=30&url=https://example.com';
  const unreachable = () => { throw new Error('Não deve acessar o backend'); };
  assert.equal((await proxyBackend(request(path, 'GET'), undefined, unreachable)).status, 401);
  const response = await proxyBackend(request(path, 'GET', undefined, { Cookie: 'edutrack_session=abc.def.ghi' }), 'http://127.0.0.1:8000', async (url, options) => {
    assert.equal(url.searchParams.get('tipo'), 'material');
    assert.equal(url.searchParams.get('offset'), '30');
    assert.equal(url.searchParams.has('url'), false);
    assert.equal(options.headers.Authorization, 'Bearer abc.def.ghi');
    return Response.json({ items: [], total: 0 });
  });
  assert.equal(response.status, 200);
  assert.equal((await proxyBackend(request(path.split('?')[0], 'DELETE', undefined, { Cookie: 'edutrack_session=abc.def.ghi' }), undefined, unreachable)).status, 404);
});

test('Classroom exige sessão e Origin sem relaxar o cookie nem abrir proxy arbitrário', async () => {
  const cookie = { Cookie: 'edutrack_session=abc.def.ghi' };
  const unreachable = () => { throw new Error('Não deve acessar o backend'); };
  for (const path of ['start', 'callback', 'preview', 'import']) {
    const route = 'integrations/google/' + path;
    assert.equal((await proxyBackend(request(route, 'POST', {}), undefined, unreachable)).status, 401);
    assert.equal((await proxyBackend(request(route, 'POST', {}, { ...cookie, Origin: 'https://accounts.google.com' }), undefined, unreachable)).status, 403);
    const result = await proxyBackend(request(route, 'POST', { code: 'codigo-ficticio' }, cookie), 'http://127.0.0.1:8000', async (url, options) => {
      assert.equal(url.pathname, '/api/' + route);
      assert.equal(options.headers.Authorization, 'Bearer abc.def.ghi');
      assert.equal(options.redirect, 'manual');
      return Response.json({ ok: true });
    });
    assert.equal(result.status, 200);
    assert.equal(result.headers.get('set-cookie'), null);
  }
  assert.equal((await proxyBackend(request('integrations/google/connection', 'DELETE', undefined, cookie), 'http://127.0.0.1:8000', async () => Response.json({ connected: false }))).status, 200);
  assert.equal((await proxyBackend(request('integrations/google/token', 'POST', {}, cookie), undefined, unreachable)).status, 404);
  assert.equal((await proxyBackend(request('integrations/google/callback', 'GET', undefined, cookie), undefined, unreachable)).status, 404);
});

test('origem canônica funciona atrás do proxy sem confiar em Forwarded do visitante', async () => {
  const upstream = async () => Response.json({ access_token: 'abc.def.ghi', expires_in: 1200, user: { id: '1' } });
  const req = new Request('http://localhost:3000/api/backend/auth/login', { method: 'POST', headers: { Origin: 'https://edutrack.example.com', 'Content-Type': 'application/json' }, body: '{}' });
  const result = await proxyBackend(req, 'http://127.0.0.1:8000', upstream, 'https://edutrack.example.com');
  assert.equal(result.status, 200);
  assert.match(result.headers.get('set-cookie'), /Secure/);
  const denied = await proxyBackend(request('auth/login', 'POST', {}, { Origin: 'https://malicioso.example', 'X-Forwarded-Host': 'malicioso.example' }), 'http://127.0.0.1:8000', upstream, 'https://edutrack.example.com');
  assert.equal(denied.status, 403);
});

test('alias local é aceito somente no loopback e na porta correta', async () => {
  const upstream = async () => Response.json({ message: 'ok' });
  const local = request('auth/forgot-password', 'POST', {}, { Host: '127.0.0.1:3002', Origin: 'http://127.0.0.1:3002' });
  assert.equal((await proxyBackend(local, 'http://127.0.0.1:8000', upstream)).status, 200);
  const remote = request('auth/forgot-password', 'POST', {}, { Host: 'malicioso.example', Origin: 'http://malicioso.example' });
  assert.equal((await proxyBackend(remote, 'http://127.0.0.1:8000', upstream)).status, 403);
});

test('acesso administrativo exige sessão e preserva recusa do servidor', async () => {
  const unreachable = () => { throw new Error('Não deveria chamar a API'); };
  assert.equal((await proxyBackend(request('admin/access'), undefined, unreachable)).status, 401);
  const result = await proxyBackend(request('admin/access', 'GET', undefined, { Cookie: 'edutrack_session=abc.def.ghi' }), 'http://127.0.0.1:8000', async (_, options) => {
    assert.equal(options.headers.Authorization, 'Bearer abc.def.ghi');
    return Response.json({ detail: 'Acesso exclusivo para administradores.' }, { status: 403 });
  });
  assert.equal(result.status, 403);
  assert.equal((await proxyBackend(request('admin/access', 'POST', {}), undefined, unreachable)).status, 404);
});

test('confirmação de e-mail passa pelo proxy sem expor JWT e mantém CSRF', async () => {
  for (const path of ['auth/request-verification', 'auth/verify-email', 'auth/forgot-password', 'auth/reset-password']) {
    const result = await proxyBackend(request(path, 'POST', { email: 'teste@example.com', senha: 'senha-teste', codigo: '123456' }), 'http://127.0.0.1:8000', async (_, options) => {
      assert.equal(options.headers.Authorization, undefined);
      return Response.json({ message: 'Recebido' });
    });
    assert.equal(result.status, 200);
    assert.equal(result.headers.get('set-cookie'), null);
    const rejected = await proxyBackend(request(path, 'POST', {}, { Origin: 'https://outra.example' }), 'http://127.0.0.1:8000');
    assert.equal(rejected.status, 403);
  }
  const options = await proxyBackend(request('auth/options'), 'http://127.0.0.1:8000', async () => Response.json({ email_verification_required: true }));
  assert.equal(options.status, 200);
});

test('login não confirmado preserva o código de erro sem criar sessão', async () => {
  const result = await proxyBackend(request('auth/login', 'POST', {}), 'http://127.0.0.1:8000', async () => Response.json({ detail: { code: 'EMAIL_VERIFICATION_REQUIRED', message: 'Confirme seu e-mail.' } }, { status: 403 }));
  assert.equal(result.status, 403);
  assert.equal((await result.json()).detail.code, 'EMAIL_VERIFICATION_REQUIRED');
  assert.equal(result.headers.get('set-cookie'), null);
});
function request(path, method = 'GET', body, extra = {}) {
  return new Request(origin + '/api/backend/' + path, { method, headers: { Origin: origin, 'Content-Type': 'application/json', ...extra }, ...(body === undefined ? {} : { body: JSON.stringify(body) }) });
}
test('login mantém JWT somente no cookie HttpOnly', async () => {
  const result = await proxyBackend(request('auth/login', 'POST', {}), 'http://127.0.0.1:8000', async () => Response.json({ access_token: 'abc.def.ghi', expires_in: 1200, user: { id: '1' } }));
  assert.deepEqual(await result.json(), { user: { id: '1' } });
  assert.match(result.headers.get('set-cookie'), /HttpOnly; SameSite=Strict; Max-Age=1200/);
  assert.equal(result.headers.get('cache-control'), 'no-store');
});
test('proxy bloqueia CSRF, acesso anônimo e destinos inválidos', async () => {
  const unreachable = () => { throw new Error('Não deveria chamar a API'); };
  assert.equal((await proxyBackend(request('courses', 'POST', {}, { Origin: 'https://malicioso.example' }), undefined, unreachable)).status, 403);
  assert.equal((await proxyBackend(request('courses'), undefined, unreachable)).status, 401);
  assert.equal((await proxyBackend(request('admin'), undefined, unreachable)).status, 404);
  assert.equal((await proxyBackend(request('auth/login', 'POST', {}), 'http://externo.example', unreachable)).status, 503);
});
test('erros, expiração, logout e idempotência são preservados', async () => {
  const cookie = { Cookie: 'edutrack_session=abc.def.ghi' };
  const key = '12345678-1234-1234-1234-123456789abc';
  const result = await proxyBackend(request('study-sessions', 'POST', {}, { ...cookie, 'Idempotency-Key': key, 'X-EduTrack-User': 'aluno-1' }), 'http://127.0.0.1:8000', async (_, options) => {
    assert.equal(options.headers.Authorization, 'Bearer abc.def.ghi');
    assert.equal(options.headers['Idempotency-Key'], key);
    assert.equal(options.headers['X-EduTrack-User'], 'aluno-1');
    return Response.json({ detail: 'Vínculo existente' }, { status: 409 });
  });
  assert.equal(result.status, 409);
  const expired = await proxyBackend(request('me', 'GET', undefined, cookie), 'http://127.0.0.1:8000', async () => Response.json({ detail: 'Expirou' }, { status: 401 }));
  assert.match(expired.headers.get('set-cookie'), /Max-Age=0/);
  const logout = await proxyBackend(request('auth/logout', 'POST', {}), undefined);
  assert.equal(logout.status, 200);
  assert.match(logout.headers.get('set-cookie'), /Max-Age=0/);
});
test('falha de rede e payload excessivo não simulam sucesso', async () => {
  assert.equal((await proxyBackend(request('auth/login', 'POST', {}), 'http://localhost:8000', async () => { throw new Error('offline'); })).status, 503);
  assert.equal((await proxyBackend(request('auth/login', 'POST', { text: 'a'.repeat(65536) }), 'http://localhost:8000')).status, 413);
});
test('mapeamento usa somente dados retornados e exclui canceladas do progresso', () => {
  const result = academicView({
    courses: [{ id: 'c', nome: 'Curso', instituicao: null, data_inicio: null, data_fim: null }],
    disciplines: [{ id: 'd', curso_id: 'c', nome: 'SQL', professor: null, carga_horaria: 30 }],
    tasks: ['concluida', 'pendente', 'cancelada'].map((status, i) => ({ id: String(i), disciplina_id: 'd', titulo: 'Tarefa', status, descricao: null, data_prevista: null, minutos_estimados: 25 })),
    sessions: [{ id: 's', tarefa_id: '0', iniciado_em: '2026-10-01T12:00:00Z', finalizado_em: '2026-10-01T12:25:00Z', duracao_minutos: 25 }],
  }, { nome: 'Aluno autenticado' });
  assert.equal(result.courses[0].progress, 50);
  assert.equal(result.disciplines[0].progress, 50);
  assert.equal(result.profile.name, 'Aluno autenticado');
  assert.equal(result.tasks[2].status, 'Cancelada');
  assert.equal(result.sessions[0].minutes, 25);
});
