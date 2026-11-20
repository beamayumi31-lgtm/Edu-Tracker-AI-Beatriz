# Validação local — 05/10/2026

## Verificado

- 45 testes automatizados aprovados em Python 3.12, com SQLite em memória, FK habilitada e contas fictícias.
- CRUD completo de cursos, disciplinas e tarefas; validação de vínculos; conclusão/reabertura de tarefa; proteção contra perda de histórico.
- Senhas Argon2id; tokens inválidos/expirados recusados; escalada de perfil e injeção de titularidade rejeitadas.
- Leitura/edição/exclusão de IDs de outra conta bloqueadas e contexto da IA separado por aluno.
- Planejamento limitado por dias/minutos, priorização por prazo, avisos de capacidade insuficiente e ausência de dados.
- Ferramentas da IA testadas com provedor simulado, inclusive tentativas de executar SQL ou informar outro usuário.
- Consentimento externo obrigatório, transparência quando a IA não está configurada e limites de solicitações/corpo.
- `ruff check edutrack tests scripts`: sem problemas.
- `pip check`: sem conflitos de dependências.
- API iniciada em `127.0.0.1:8000` e conferida por HTTP: `/health` 200; `/ready` 200; `/docs` 200; `/api/me` sem token 401; rota inexistente 404.
- SQL Server real: **83 verificações de integração aprovadas após autorização**, com gravações reais, confirmações em conexões independentes e limpeza limitada às contas de teste. As seis tabelas terminaram vazias, como antes; comparação de dados e metadados sem diferenças. Nenhuma migração executada.
- O teste encontrou e permitiu corrigir o mapeamento de `duracao_minutos`: a coluna já é calculada pelo banco e a API não deve tentar gravá-la. Correção apenas no código, com três testes de regressão adicionais. Detalhes em `TESTES_SQLSERVER.md`.
- Contrato OpenAPI 3.1 salvo em `openapi.json`, com 27 operações em 17 caminhos.
- Todos os seis diretórios do workspace do VS Code existem. O frontend atual permaneceu sem alterações, no commit `d58dcce`.

Há um aviso de descontinuação de `httpx` no TestClient do Starlette; não houve falha nos testes. Ele se refere à ferramenta de teste, não a uma resposta de erro da aplicação.

## Ainda não verificado / não executado

- Chamada real à IA: nenhuma chave configurada e nenhum crédito consumido por este backend durante os testes.
- Integração do frontend com a nova API e teste ponta a ponta do navegador.
- Publicação da API, alteração de VPS/DNS e atualização do site público.

Esses resultados não certificam segurança/escala de produção nem substituem a validação ponta a ponta após configuração. O servidor de verificação é encerrado ao concluir; use a tarefa do VS Code para iniciá-lo novamente.

A rotina de integração SQL usa o cliente ASGI da aplicação, sem iniciar um servidor acessível na rede. A configuração padrão de escrita continua desativada após o teste. A autorização recebida foi aplicada somente aos dados fictícios e à sua remoção.
