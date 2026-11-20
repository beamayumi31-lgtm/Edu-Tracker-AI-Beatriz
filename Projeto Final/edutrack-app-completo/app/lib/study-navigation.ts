const localPages = new Set([
  '/dashboard', '/cursos', '/disciplinas', '/tarefas', '/cronometro',
  '/relatorios', '/edu-ia', '/descobrir', '/perfil', '/upgrade', '/ofensiva', '/integracoes',
]);

/** Apenas telas do protótipo com dados locais podem dispensar uma nova resposta RSC. */
export function isLocalStudyPage(pathname: string): boolean {
  return localPages.has(pathname) || /^\/(cursos|disciplinas)\/[^/]+$/.test(pathname);
}

/** Login, administração, URLs externas e futuras rotas de API seguem pelo roteador. */
export function canNavigateLocally(currentUrl: string, destination: string): boolean {
  try {
    const current = new URL(currentUrl);
    const next = new URL(destination, current);
    return next.origin === current.origin && !next.hash &&
      isLocalStudyPage(current.pathname) && isLocalStudyPage(next.pathname);
  } catch {
    return false;
  }
}
