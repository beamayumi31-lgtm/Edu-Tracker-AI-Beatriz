'use client';

import { GraduationCap, Moon, Sun } from 'lucide-react';
import { useRouter } from 'next/navigation';

export function Brand({ compact = false }: { compact?: boolean }) {
  const router = useRouter();
  return (
    <button className="brand" onClick={() => router.push('/')} aria-label="Ir para a tela inicial">
      <span className="brand-mark"><GraduationCap size={compact ? 20 : 25} /></span>
      {!compact && <span>EduTrack</span>}
    </button>
  );
}

export function ThemeToggle({ compact = false }: { compact?: boolean }) {
  function toggleTheme() {
    const root = document.documentElement;
    const nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = nextTheme;
    try {
      window.localStorage.setItem('edutrack-theme', nextTheme);
    } catch {
      // A troca visual continua funcionando mesmo sem armazenamento local.
    }
  }

  return (
    <button
      className={'theme-toggle ' + (compact ? 'compact' : '')}
      type="button"
      onClick={toggleTheme}
      aria-label="Alternar entre modo claro e escuro"
      title="Alternar tema"
    >
      <Sun className="theme-sun" size={18} />
      <Moon className="theme-moon" size={18} />
      {!compact && <span>Alternar tema</span>}
    </button>
  );
}
