'use client';

import { useEffect, useRef, useState } from 'react';
import { remainingSeconds, type FocusRun } from '../lib/study-game';

/** O relógio fica na raiz: navegar entre telas não reinicia o foco. */
export function useFocusClock(run: FocusRun | null, ready: boolean, finish: (run: FocusRun) => void) {
  const [now, setNow] = useState(() => Date.now());
  const completedId = useRef<string | null>(null);
  useEffect(() => {
    if (!ready || !run || run.endsAt === null) return;
    const tick = () => {
      const timestamp = Date.now();
      setNow(timestamp);
      if (remainingSeconds(run, timestamp) === 0 && completedId.current !== run.id) {
        completedId.current = run.id;
        finish(run);
      }
    };
    tick();
    const interval = window.setInterval(tick, 1000);
    document.addEventListener('visibilitychange', tick);
    return () => { window.clearInterval(interval); document.removeEventListener('visibilitychange', tick); };
  }, [run, ready, finish]);
  return run ? remainingSeconds(run, now) : 0;
}
