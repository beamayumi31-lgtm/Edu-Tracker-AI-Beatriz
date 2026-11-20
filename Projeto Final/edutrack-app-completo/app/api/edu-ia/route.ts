// A rota antiga recebia contexto acadêmico do cliente sem autenticação.
// Toda IA passa agora pelo backend autenticado e pelo contexto da conta no SQL Server.
export function GET() {
  return Response.json({ detail: 'Use /api/backend/edu-ia com a sessão autenticada.' }, { status: 410, headers: { 'Cache-Control': 'no-store' } });
}
export const POST = GET;
