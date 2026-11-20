# Revisão complementar com Claude Desktop — 10/11/2026

Consulta realizada no aplicativo Claude Desktop, plano gratuito, na conversa de revisão do EduTrack já existente. Foi enviado apenas um resumo da arquitetura e das decisões de público; nenhum arquivo privado, segredo ou dado real de aluno foi compartilhado. A resposta foi lida no aplicativo. O Claude declarou não ter consultado a documentação oficial nesta revisão: suas hipóteses não são evidência de funcionamento nem parecer jurídico.

## Pontos úteis e encaminhamento

1. **Escopos OAuth:** a equivalência exibida pelo console precisa ser confirmada no retorno real e na leitura de atividades. O pedido da aplicação continua sendo `classroom.coursework.me.readonly`, conforme o endpoint oficial; a validação admite somente o nome alternativo explícito mostrado pelo console, sem correspondências por prefixo. Cinco testes simulados adicionais foram aprovados, mas falta o consentimento real e uma consulta autorizada. Não ampliar permissões como tentativa de corrigir um eventual erro 403.
2. **Público de 13 a 17 anos:** manter o chat externo desligado até escolher um provedor compatível e preparar avisos, tratamento de conteúdo inadequado, suporte, minimização de dados e regras de idade/consentimento aplicáveis. Uma declaração de maioridade não resolve a incompatibilidade do produto com os termos Gemini. O planejador local pode continuar sem transmitir dados a um provedor.
3. **Logs e retenção:** nunca registrar códigos OAuth, state, verificadores PKCE, tokens, secrets, cookies, prompts ou respostas educacionais em logs. A proteção do callback no Nginx e a execução sem access log da API já estavam implantadas. Prazo de limpeza de tentativas expiradas, backups e derivados deve continuar na revisão de retenção.
4. **Testes adversariais:** priorizar escopos insuficientes, callbacks trocados entre usuários, desconexão concorrente, isolamento das importações, exclusão de dados Classroom de todos os contextos externos e falhas do provedor. Verificar também corpo grande, HTML/Markdown malicioso e limites por usuário.

## Cuidados ao interpretar o parecer

- O Claude levantou a hipótese de que o nome alternativo possa representar outra permissão; isso não foi verificado por ele. A documentação de autenticação do Classroom descreve ambos como leitura de atividades e notas, e o console converteu a seleção. A documentação do endpoint lista o nome original; o teste real continua necessário.
- A sugestão de remover o aviso sobre notas se o alias fosse retirado **não foi adotada**: o escopo original também menciona notas na descrição oficial. O aplicativo não consulta/importa notas ou entregas; o aviso precisa explicar o alcance do consentimento.
- Não houve aceite de termos, alteração de serviços ou execução por instrução do Claude. As ações externas seguem exclusivamente as autorizações de Antonio.

## Fontes primárias utilizadas para conferir o parecer

- [Autenticação e escopos Classroom](https://developers.google.com/workspace/classroom/guides/auth)
- [courses.courseWork.list](https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork/list)
- [Termos Gemini](https://ai.google.dev/gemini-api/terms)
- [Preparação para público 13+](PUBLICO_13_MAIS.md)

Evidência visual local: `output/edutrack-ativacao-2026-11-10/claude-terceira-revisao.png`.
