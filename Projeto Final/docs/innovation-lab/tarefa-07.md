# Tarefa 07 — Projeto de frontend, tema e API

EduTrack · Innovation Lab · Faculdade Impacta · 17/11/2026

**Situação:** Adaptado para React.

## Entrega e explicação

O frontend existente foi mantido para preservar o trabalho e os dados do projeto. app/globals.css define tokens, tipografia e estados claros/escuros; app/connected.css contém estilos dos fluxos conectados. Componentes usam Lucide e o roteador compartilhado do EduTrack.

O equivalente ao API Group é app/lib/academic-api.ts: centraliza chamadas e tratamento de sessão. app/lib/backend-proxy.ts mantém uma lista de rotas permitidas e faz a ponte de mesma origem com FastAPI. Segredos ficam no servidor; nenhum token de provedor é colocado no código público.

Não foi criado projeto FlutterFlow. A evidência é o código React, telas executáveis e contrato da API; a equivalência precisa ser aceita pelo professor.

## Fontes e evidências

- [edutrack-app-completo/app/globals.css](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-app-completo/app/globals.css)
- [edutrack-app-completo/app/lib/academic-api.ts](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-app-completo/app/lib/academic-api.ts)

Consulte também o índice, a matriz de adaptações e os arquivos em `evidencias/` deste pacote.
