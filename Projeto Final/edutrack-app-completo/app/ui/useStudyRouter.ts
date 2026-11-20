'use client';

import { useRouter } from 'next/navigation';
import { useMemo } from 'react';
import { canNavigateLocally } from '../lib/study-navigation';

export function useStudyRouter() {
  const router = useRouter();
  return useMemo(() => ({
    ...router,
    push(href: string, options?: { scroll?: boolean }) {
      if (!canNavigateLocally(window.location.href, href)) {
        router.push(href, options);
        return;
      }
      // Next/Vinext sincroniza usePathname com a History API nativa.
      // A mesma árvore de telas permanece montada, preservando os dados locais.
      const target = new URL(href, window.location.href);
      if (target.href !== window.location.href) {
        window.history.pushState(null, '', target.pathname + target.search);
      }
      if (options?.scroll !== false) window.scrollTo({ top: 0, behavior: 'instant' });
    },
  }), [router]);
}
