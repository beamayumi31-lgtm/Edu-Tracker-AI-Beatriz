/** Ponte de mesma origem. Nunca importar este módulo em componentes client. */
const COOKIE = 'edutrack_session';
const UUID = '[0-9a-fA-F-]{36}';
const routes: Record<string, RegExp> = {
  GET: new RegExp(`^(auth/options|admin/access|me|dashboard|courses|disciplines|tasks|study-sessions|search/disciplines|reports/(generate|progress\\.pdf)|edu-ia/(status|context)|integrations/google/(status|courses|disciplines/${UUID}/content)|(courses|disciplines|tasks)/${UUID})$`),
  POST: /^(auth\/(login|register|logout|request-verification|verify-email|forgot-password|reset-password)|courses|disciplines|tasks|study-sessions|edu-ia\/(chat|study-plan)|integrations\/google\/(start|callback|preview|import))$/,
  PUT: new RegExp(`^(me|(courses|disciplines|tasks)/${UUID})$`),
  DELETE: new RegExp(`^((courses|disciplines|tasks)/${UUID}|integrations/google/connection)$`),
};

function json(body: unknown, status = 200, headers: Record<string, string> = {}) {
  return Response.json(body, { status, headers: { 'Cache-Control': 'no-store', ...headers } });
}
function sessionCookie(value: string, seconds: number, secure: boolean) {
  return `${COOKIE}=${value}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${seconds}${secure ? '; Secure' : ''}`;
}
function readToken(request: Request) {
  const value = request.headers.get('cookie')?.split(';').map((part) => part.trim()).find((part) => part.startsWith(COOKIE + '='))?.slice(COOKIE.length + 1);
  return value && /^[A-Za-z0-9_.-]{1,4096}$/.test(value) ? value : null;
}

export async function proxyBackend(request: Request, backendUrl: string | undefined, fetcher: typeof fetch = fetch, publicOrigin?: string) {
  const url = new URL(request.url);
  const path = url.pathname.slice('/api/backend/'.length);
  const method = request.method.toUpperCase();
  if (!url.pathname.startsWith('/api/backend/') || !routes[method]?.test(path)) return json({ detail: 'Rota não disponível.' }, 404);
  let origin = url.origin;
  if (publicOrigin) {
    try {
      const canonical = new URL(publicOrigin);
      const local = ['localhost', '127.0.0.1', '[::1]'].includes(canonical.hostname);
      if (canonical.username || canonical.password || canonical.search || canonical.hash || canonical.pathname !== '/' || (canonical.protocol !== 'https:' && !(local && canonical.protocol === 'http:'))) throw new Error('Origem inválida');
      origin = canonical.origin;
    } catch { return json({ detail: 'URL pública inválida na configuração do servidor.' }, 503); }
  } else if (['localhost', '127.0.0.1', '[::1]'].includes(url.hostname)) {
    // Next pode normalizar a URL interna para localhost. Aceitar o Host somente no loopback e na mesma porta.
    const host = request.headers.get('host');
    if (host) {
      try {
        const local = new URL(url.protocol + '//' + host);
        if (['localhost', '127.0.0.1', '[::1]'].includes(local.hostname) && local.port === url.port) origin = local.origin;
      } catch { /* Preserva a origem original quando o Host não é válido. */ }
    }
  }
  const secure = new URL(origin).protocol === 'https:';
  // Cookies só autorizam escritas vindas da mesma origem, protegendo contra CSRF.
  if (method !== 'GET' && request.headers.get('origin') !== origin) return json({ detail: 'Origem da solicitação não autorizada.' }, 403);
  if (path === 'auth/logout') return json({ ok: true }, 200, { 'Set-Cookie': sessionCookie('', 0, secure) });
  const publicRoute = ['auth/login', 'auth/register', 'auth/options', 'auth/request-verification', 'auth/verify-email', 'auth/forgot-password', 'auth/reset-password'].includes(path);
  const token = readToken(request);
  if (!publicRoute && !token) return json({ detail: 'Entre na sua conta para continuar.' }, 401);
  if (!backendUrl) return json({ detail: 'API local não configurada. Inicie o projeto pelo comando de desenvolvimento do workspace.' }, 503);

  let base: URL;
  try {
    base = new URL(backendUrl);
    // HTTP sem TLS é permitido apenas no loopback local; nunca aceitar URL vinda do cliente.
    if (base.username || base.password || base.search || base.hash || (base.protocol !== 'https:' && !(base.protocol === 'http:' && ['127.0.0.1', 'localhost', '[::1]'].includes(base.hostname)))) throw new Error('URL inválida');
  } catch { return json({ detail: 'Configuração da API inválida no servidor.' }, 503); }

  let body: string | undefined;
  if (method === 'POST' || method === 'PUT') {
    if (!request.headers.get('content-type')?.startsWith('application/json')) return json({ detail: 'Envie os dados em JSON.' }, 415);
    if (Number(request.headers.get('content-length') || 0) > 65536) return json({ detail: 'Solicitação muito grande.' }, 413);
    const reader = request.body?.getReader();
    const chunks: Uint8Array[] = [];
    let size = 0;
    if (reader) {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        size += value.byteLength;
        if (size > 65536) { await reader.cancel(); return json({ detail: 'Solicitação muito grande.' }, 413); }
        chunks.push(value);
      }
    }
    const buffer = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) { buffer.set(chunk, offset); offset += chunk.length; }
    body = new TextDecoder().decode(buffer);
    try { JSON.parse(body); } catch { return json({ detail: 'JSON inválido.' }, 400); }
  }
  const headers: Record<string, string> = { Accept: 'application/json', 'Content-Type': 'application/json' };
  if (token && !publicRoute) headers.Authorization = 'Bearer ' + token;
  const expectedUser = request.headers.get('x-edutrack-user');
  if (expectedUser && !publicRoute) headers['X-EduTrack-User'] = expectedUser;
  const idempotency = request.headers.get('idempotency-key');
  if (idempotency && path === 'study-sessions') {
    if (!/^[0-9a-f-]{36}$/i.test(idempotency)) return json({ detail: 'Identificador de sessão inválido.' }, 400);
    headers['Idempotency-Key'] = idempotency;
  }
  try {
    const target = new URL('api/' + path, base.href.endsWith('/') ? base.href : base.href + '/');
    for (const key of ['limit', 'offset', 'curso_id', 'disciplina_id', 'status', 'tipo', 'q', 'overdue']) {
      const value = url.searchParams.get(key);
      if (value !== null) target.searchParams.set(key, value);
    }
    const upstream = await fetcher(target, { method, headers, body, redirect: 'manual', cache: 'no-store', signal: AbortSignal.timeout(path.startsWith('edu-ia/') ? 125000 : path.startsWith('integrations/google/') ? 65000 : 15000) });
    if (upstream.status >= 300 && upstream.status < 400) return json({ detail: 'A API retornou um redirecionamento não permitido.' }, 502);
    const responseHeaders: Record<string, string> = {};
    if (upstream.status === 401) responseHeaders['Set-Cookie'] = sessionCookie('', 0, secure);
    if (upstream.headers.has('retry-after')) responseHeaders['Retry-After'] = upstream.headers.get('retry-after')!;
    if (upstream.status === 204) return new Response(null, { status: 204, headers: { 'Cache-Control': 'no-store' } });
    if (path === 'reports/progress.pdf' && upstream.ok && upstream.headers.get('content-type')?.split(';')[0] === 'application/pdf') {
      // O documento é privado e limitado; não propagar cabeçalhos arbitrários da API.
      const reader = upstream.body?.getReader();
      if (!reader) return json({ detail: 'Relatório vazio.' }, 502);
      const chunks: Uint8Array[] = []; let size = 0;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        size += value.byteLength;
        if (size > 3 * 1024 * 1024) { await reader.cancel(); return json({ detail: 'Relatório acima do limite de download.' }, 502); }
        chunks.push(value);
      }
      const pdf = new Uint8Array(size); let position = 0;
      for (const chunk of chunks) { pdf.set(chunk, position); position += chunk.length; }
      if (new TextDecoder().decode(pdf.slice(0, 5)) !== '%PDF-') return json({ detail: 'Documento PDF inválido.' }, 502);
      return new Response(pdf, { headers: { 'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename="edutrack-progresso.pdf"', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' } });
    }
    if (!upstream.headers.get('content-type')?.includes('application/json')) return json({ detail: 'A API não retornou uma resposta válida.' }, 502);
    const result = await upstream.json() as Record<string, unknown> | null;
    if (path === 'auth/login' && upstream.ok) {
      if (!result || typeof result.access_token !== 'string' || !/^[A-Za-z0-9_.-]{1,4096}$/.test(result.access_token) || !result.user) return json({ detail: 'Resposta de login inválida.' }, 502);
      const seconds = Math.min(3600, Math.max(1, Number(result.expires_in) || 1200));
      responseHeaders['Set-Cookie'] = sessionCookie(result.access_token, seconds, secure);
      // Não retornar o JWT para JavaScript nem guardar tokens no localStorage.
      return json({ user: result.user }, 200, responseHeaders);
    }
    return json(result, upstream.status, responseHeaders);
  } catch (cause) {
    // Diagnóstico no servidor: nunca registrar cabeçalhos, credenciais ou dados acadêmicos.
    console.warn('EduTrack: falha na conexão com a API', cause instanceof Error ? cause.message : 'Erro de rede');
    return json({ detail: 'Não foi possível conectar à API. Confira se o servidor Python está ligado e tente novamente.' }, 503);
  }
}
