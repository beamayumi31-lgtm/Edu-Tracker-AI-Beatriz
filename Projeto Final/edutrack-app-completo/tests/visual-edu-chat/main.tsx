import { createRoot } from 'react-dom/client';
import ConnectedEduAI from '../../app/ui/ConnectedEduAI';
import '../../app/globals.css';
import '../../app/connected.css';
import '../../app/integrations.css';
const mode = new URLSearchParams(location.search).get('mode');
// Fixture de teste: não lê credenciais, não chama a API e não grava dados.
window.fetch = async (input, options) => {
  const path=String(input);
  if(path.endsWith('/edu-ia/status')) return Response.json({configured:mode !== 'off',provider:'openai',academic_context_allowed:false});
  if(path.endsWith('/edu-ia/chat')) {
    await new Promise((resolve,reject)=>{const id=setTimeout(resolve,mode==='slow'?8000:500);options?.signal?.addEventListener('abort',()=>{clearTimeout(id);reject(new DOMException('Aborted','AbortError'));},{once:true});});
    if(mode==='error') return Response.json({detail:'Falha simulada de teste.'},{status:503});
    return Response.json({reply:'## Exemplo simulado\n**Isto não é uma resposta real de IA.**\n\nUma consulta pode selecionar colunas:\n```sql\nSELECT nome FROM alunos;\n```\nTexto de teste: <script>alert(1)</script>',plan:null});
  }
  if(path.endsWith('/edu-ia/study-plan')) return Response.json({origem:'regras',resumo:'Plano fictício para testar a interface.',alertas:[],somente_proposta:true,tarefas_nao_planejadas:[],blocos:[{data:'2026-11-16',tarefa_id:'demo',disciplina_id:'demo',curso_id:'demo',titulo:'Revisar SQL (exemplo fictício)',minutos:25,orientacao:'Revisar SELECT e filtros.'}]});
  throw new Error('A fixture bloqueia toda chamada de rede.');
};
createRoot(document.getElementById('root')!).render(<><div style={{padding:8,textAlign:'center',background:'#fef3c7',color:'#78350f',fontSize:12}}>TESTE ISOLADO · dados e respostas simulados · sem conexão externa</div><ConnectedEduAI /></>);
