# Edu IA - experiência de conversa (16/11/2026)

## O que mudou

- Conversa como tela principal, com área de composição ampla e três sugestões de estudo.
- Aba separada para o planejador local, que funciona sem modelo generativo.
- Respostas com destaque simples, títulos e blocos de código. HTML retornado permanece texto escapado pelo React.
- Copiar resposta, baixar conversa TXT e iniciar nova conversa.
- Enter para enviar; Shift+Enter para nova linha; compatibilidade com composição de texto (IME).
- Interrupção da espera com AbortController. Não promete cancelar cobrança/processamento já iniciado pelo provedor.
- Pergunta preservada após erro ou interrupção; resposta tardia descartada.
- Contexto limitado às últimas quatro trocas mais a pergunta, até 2.000 caracteres por mensagem. O histórico visível completo não é truncado.
- Histórico somente em memória desta tela. Não foi criada persistência silenciosa no navegador ou servidor.
- Estado indisponível explícito: é possível preparar uma pergunta, mas o envio fica bloqueado. Nenhuma resposta fictícia é exibida como IA real.

## Estado da integração real

Verificado na VPS em 16/11, somente valores não secretos: provedor selecionado OpenAI, público includes_teens, configured=false, chaves e modelos ausentes. Gemini não habilitado. Nenhum modelo foi conectado, nenhuma chave foi criada/lida/exposta e nenhuma chamada paga foi feita.

Gemini API não é adequado ao público atual de 13+ do EduTrack. A aparência de conversa não muda essa restrição. O adaptador OpenAI existente não comprova adequação para adolescentes: ainda requer controles apropriados, revisão do fluxo e autorização de credencial/modelo/custos. Não mudar o público para liberar um provedor.

Fontes oficiais consultadas na revisão: https://aistudio.google.com/docs/terms e https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance . Consulte também PUBLICO_13_MAIS.md.

## Validação

- 48 testes frontend passaram (5 novos para parser seguro, exportação e limites de contexto).
- TypeScript e ESLint passaram; build Next/webpack de produção passou.
- OpenSpec: 11 itens válidos.
- Revisão adicional verificou cancelamento, respostas tardias, formatação sem execução de HTML e funcionamento do planejador independente da configuração de chat.
- Nenhuma alteração de backend ou de banco nesta etapa. Os 153 testes backend aprovados anteriormente não representam um novo teste de integração externa.

## Limite do QA visual

A fixture de teste usa dados/respostas explicitamente simulados e bloqueia chamadas externas. Ela foi compilada separadamente e não integra a publicação. O navegador local está indisponível; o navegador cloud não alcançou o servidor temporário, e apenas HTTP/HTTPS são permitidos. Portanto não houve inspeção visual nem teste de clique do chat neste ambiente. Não confundir compilação, testes unitários ou revisão de código com teste autenticado de IA real.

## Publicação concluída

Frontend-only publicado: `edutrack-chat-20261116-222336`. Serviço web saudável; página inicial, apresentação, login, privacidade e `/edu-ia`: 200. Quinze arquivos estáticos: 200. `/api/backend/me` e `/api/backend/edu-ia/status` sem sessão: 401. Containers API e SQL preservaram IDs. Configuração de IA permaneceu `configured=false`, sem chaves, Gemini desligado. Nenhuma chamada externa. Rollback: `edutrack-web:rollback-20261116-chat`.

A publicação não ativa a IA generativa. Acesse a Edu IA pelo menu após login; Planejar estudos continua funcional sem provedor externo.
