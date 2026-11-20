# Preparação de acesso adulto fechado e Gemini gratuito

Nova instrução do responsável em 16/11/2026: manter a integração permanente no site e limitar o serviço a maiores de 18, sem qualquer cobrança nova. Isto substitui a proposta anterior de demonstração local; não comprova que a mudança já está ativa.

## Preparado localmente, ainda não publicado

- Modo fechado no servidor para contas adultas previamente aprovadas e com e-mail confirmado.
- Cadastro público recusado; lista vazia ou público incompatível falha fechado.
- Sessões antigas e OAuth não ignoram a aprovação.
- Interface lê política pública sem expor a lista, mostra18+ e oculta cadastro.
- Nenhuma conta ou dado existente é apagado.
- Configuração padrão continua inalterada até ativação explícita.

## Antes de ativar

1. Confirmar a conta existente do titular antes de restringir acesso e confirmar uso adulto. O professor nao acessara: o grupo gravara um video usando a conta do titular. Nao criar conta do professor nem pedir seu e-mail. Nao compartilhar senha nem inferir idade pelo e-mail.
2. Publicar e testar primeiro o controle fechado com IA ainda desligada. Verificar login aprovado, bloqueio de não aprovados com sessão antiga, cadastro recusado e proteção OAuth/API.
3. Conferir no projeto da chave do AI Studio: nível Free, faturamento não ativado, modelo gratuito disponível e cotas. Se houver faturamento ou incerteza de custo, parar. Não habilitar billing, upgrades, ferramentas pagas ou fallback para outro modelo.
4. Fornecer a chave por entrada oculta/handoff seguro e armazená-la apenas na configuração privada do backend na VPS, nunca chat, frontend, GitHub ou arquivos de entrega. Uso permanente foi autorizado; isso não autoriza cobranças nem envio de dados pessoais.
5. Ativar Gemini somente com acesso fechado validado, público adulto, modelo gratuito confirmado e contexto acadêmico desligado. Usar perguntas fictícias para o teste autorizado. Não enviar Classroom, perfis, e-mails nem dados privados automaticamente.
6. O usuário da aplicação autoriza envio de suas perguntas antes de conversar. O modo gratuito pode usar conteúdo para melhoria de produtos e revisão humana; avisar claramente para não incluir dados pessoais/confidenciais.
7. Preservar backup privado da configuração e imagens anteriores. Rollback deve restaurar configuração SEM IA antes de qualquer imagem antiga que não tenha o bloqueio de acesso.

## Limites e pontos pendentes

- `gemini_paid_service=false` controla contexto e não impede faturamento no Google.
- Cotas variam por projeto/modelo; quota excedida deve gerar erro claro, nunca cobrança/upgrade automático.
- Acesso18+ aqui significa convite/aprovação de contas adultas, não apenas um rótulo ou checkbox. Não equivale a uma validação jurídica geral do serviço.
- Falta confirmar a conta existente do titular e uso adulto, executar handoff seguro da chave e confirmar Free/cota. Nenhuma chave foi recebida, gravada ou usada nesta preparacao.

Fontes verificadas: https://aistudio.google.com/docs/terms ; https://aistudio.google.com/docs/pricing ; https://aistudio.google.com/docs/rate-limits .
