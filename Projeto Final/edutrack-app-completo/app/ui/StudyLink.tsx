'use client';

import type { PropsWithChildren } from 'react';
import { useStudyRouter } from './useStudyRouter';

/** Link acessível com o roteador compartilhado pelos modos Next e Vinext. */
export default function StudyLink({ href, className, children }: PropsWithChildren<{ href: string; className?: string }>) {
  const router = useStudyRouter();
  return <a href={href} className={className} onClick={(event) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.defaultPrevented) return;
    event.preventDefault();
    router.push(href);
  }}>{children}</a>;
}
