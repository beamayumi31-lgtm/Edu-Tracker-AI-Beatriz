'use client';
import { useEffect, useState } from 'react';
import { api } from '../lib/academic-api';
export type AccessPolicy = { restricted_adults_mode?: boolean; registration_enabled?: boolean };
export function useAccessPolicy() {
  const [policy, setPolicy] = useState<AccessPolicy | null>(null);
  useEffect(() => { let active = true; api<AccessPolicy>('auth/options').then(value => { if (active) setPolicy(value); }).catch(() => {}); return () => { active = false; }; }, []);
  return policy;
}
export default function AccessNotice() {
  const policy = useAccessPolicy();
  return policy?.restricted_adults_mode ? <p className="connection-notice"><strong>Acesso restrito a adultos convidados (18+).</strong> O cadastro público está fechado. Somente contas previamente aprovadas pelo responsável e com e-mail confirmado podem usar o aplicativo. Uma autodeclaração não concede acesso.</p> : null;
}
