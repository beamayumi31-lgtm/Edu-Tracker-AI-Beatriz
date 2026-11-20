'use client';

import { useEffect, useRef, useState } from 'react';
import Link from './StudyLink';
import { BookOpen } from 'lucide-react';
import { api } from '../lib/academic-api';

export default function GoogleCallback() {
  const started = useRef(false);
  const [result, setResult] = useState('Concluindo a conexão com o Google Classroom…');
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    if (started.current) return;
    started.current = true;
    const query = new URLSearchParams(window.location.search);
    const code = query.get('code'), state = query.get('state'), denied = query.has('error');
    // Retirar o código da barra/histórico antes de qualquer requisição; não usar storage.
    window.history.replaceState(null, '', window.location.pathname);
    Promise.resolve().then(async () => {
      if (denied) throw new Error('A conexão não foi autorizada. Você pode tentar novamente em Integrações.');
      if (!code || !state) throw new Error('Autorização incompleta. Inicie a conexão pela página Integrações.');
      // O POST de mesma origem recebe o cookie Strict após o retorno do Google.
      await api('integrations/google/callback', { method: 'POST', body: JSON.stringify({ code, state }) });
      setResult('Conta conectada. Agora escolha quais turmas e atividades deseja importar.');
    }).catch((error) => { setFailed(true); setResult(error instanceof Error ? error.message : 'Não foi possível conectar.'); });
  }, []);
  return <main className="integration-callback"><section className="surface"><BookOpen size={38} /><span className="eyebrow">EduTrack + Google Classroom</span><h1>{failed ? 'Vamos tentar novamente?' : 'Conectando seus estudos'}</h1><p role={failed ? 'alert' : 'status'}>{result}</p><Link className="primary-button" href="/integracoes">Voltar para Integrações</Link>{failed && <Link className="secondary-button" href="/login">Entrar novamente</Link>}</section></main>;
}
