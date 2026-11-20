import { proxyBackend } from '../../../lib/backend-proxy';

export const dynamic = 'force-dynamic';
export function GET(request: Request) { return proxyBackend(request, process.env.EDUTRACK_API_URL, fetch, process.env.EDUTRACK_SITE_URL); }
export const POST = GET;
export const PUT = GET;
export const DELETE = GET;
