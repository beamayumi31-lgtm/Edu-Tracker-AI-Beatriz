# Validação local - 16/11/2026

## Mudanças revisadas

- Página pública `/apresentacao`: visão do projeto, arquitetura, roteiro e limitações.
- Link da página inicial para a apresentação; textos e metadados sem promessa de IA ativa.
- Botão de download TXT do plano de estudos: blocos, orientações, alertas e quantidade de tarefas não planejadas. Exportação não inclui os identificadores internos.
- Documentação atualizada e checklist de entrega dos três vídeos.

## Resultados

- Frontend: 43 testes aprovados (inclui dois novos de exportação).
- TypeScript sem erros; ESLint sem erros.
- Backend: 153 testes aprovados em SQLite em memória; Ruff sem problemas.
- OpenSpec: 11 validações aprovadas.
- Next/webpack: build de produção concluído, incluindo nova rota estática.
- Servidor compilado temporário, sem API/banco: `/`, `/apresentacao`, `/login` e `/privacidade` retornaram HTTP 200.
- Os 11 recursos estáticos referenciados na apresentação retornaram HTTP 200.
- Título principal, aviso de OAuth e link para login presentes; nenhuma substituição de caractere inválido no HTML.
- Servidor temporário encerrado após os testes.

## Limites

Isto não substitui inspeção visual: o inventário de CUA não encontrou navegador conectado e a tentativa de abrir Chrome terminou com `Transport closed`. Não há alegação de screenshot, teste real em celular, clique no download ou teste autenticado em produção. E-mail, SQL Server, OAuth e IA externa não foram exercitados pela bateria local. Nenhum dado real foi alterado nos testes.

## Publicação verificada

Release `edutrack-ui-20261116-215209`, publicada em 16/11. Build Linux e TypeScript passaram. Somente web foi recriado; serviço saudável. `/`, `/apresentacao`, `/login`, `/privacidade` e os 11 recursos JS/CSS retornaram 200. `/api/backend/me` sem sessão retornou 401. IDs dos containers API e SQL permaneceram idênticos. Não foram alterados banco, backend, credenciais, Nginx nem permissões. Imagem anterior preservada em `edutrack-web:rollback-20261116-professor`.

A evidência operacional está em `output/edutrack-ui-20261116/verificacao-publicacao.json` no projeto; verificação de saúde/HTTP, não inspeção visual autenticada. Não houve envio ao professor nem confirmação dos vídeos.
