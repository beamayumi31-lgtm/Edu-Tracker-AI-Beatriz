# EduTrack — mapa completo do projeto

Índice de consulta: [DOCUMENTACAO.md](DOCUMENTACAO.md), com os guias em Markdown e as especificações OpenSpec. Para a nova versão do topo do dashboard, veja [Calendário de estudos](../edutrack-app-completo/docs/CALENDARIO-DE-ESTUDOS.md).

Abra o arquivo **EduTrack.code-workspace**, na pasta `FACULDADE`, para visualizar os códigos juntos no VS Code. Os arquivos continuam salvos em suas pastas; o workspace apenas os organiza, sem duplicar nem mover o projeto original.

## Onde fica cada parte

| Pasta no VS Code | Conteúdo |
|---|---|
| **Frontend** | Site atual completo: telas, estilos, imagens, cronômetro, floresta, ofensiva, testes, OpenSpec e documentação original. |
| **Backend** | Nova API Python, modelos SQL Server, validação, autenticação, CRUD, agente Edu IA e testes automatizados. |
| **Documentacao** | Este guia e o dicionário do banco existente. |
| **Referencia - site anterior** | Versão anterior preservada. Não confundir com o site atual. |
| **Referencia - modelos visuais** | Estudos de aparência preservados. |
| **Referencia - telas** | Layouts/telas de referência preservados. |

As dependências e pastas de build estão ocultas na lateral para facilitar a leitura. Não foram apagadas.

## Ordem sugerida para estudar o código

1. `Frontend/app/ui/EduTrackApp.tsx`: sessão autenticada, navegação e operações da conta. `EduTrackViews.tsx` contém a apresentação das telas.
2. `Frontend/app/ui/ConnectedAuth.tsx`, `ConnectedEditModal.tsx` e `ConnectedEduAI.tsx`: login/cadastro, formulários e planejamento conectados. `app/lib/academic-api.ts` mapeia contratos; `app/lib/backend-proxy.ts` mantém o token em cookie HttpOnly.
3. `Frontend/app/ui/FocusGarden.tsx`, `StudyStreak.tsx`, `useFocusClock.ts`: foco e gamificação.
4. `Backend/edutrack/models.py` e `schemas.py`: tabelas e contratos da API.
5. `Backend/edutrack/security.py` e `routes.py`: autenticação e operações acadêmicas.
6. `Backend/edutrack/study_context.py`, `planning.py`, `agent.py`, `ai_routes.py`: contexto do aluno, planejamento e agente.
7. `Backend/tests`: exemplos executáveis de funcionamento, isolamento e bloqueios de segurança.
8. `Frontend/openspec`: especificações do produto; algumas funcionalidades ainda são propostas, não implementações reais.

## Histórico das etapas anteriores (consulte ESTADO_ATUAL.md)

**Atualização CPF e e-mail:** validação de CPF no cadastro e na API (sem armazenar o número). Confirmação por código ativada apenas no localhost, com remetente verificado e chave SendGrid restrita fora do Git/OneDrive. Um teste real foi aceito para envio (HTTP 202); chegada à caixa de entrada e confirmação real de conta ainda dependem do titular. Veja [CPF_E_EMAIL.md](CPF_E_EMAIL.md). O site público não foi alterado.

A API foi criada como serviço independente, compatível com as tabelas existentes do SQL Server. O agente lê somente dados acadêmicos da conta autenticada e cria propostas de estudo. A estrutura não dá ao agente acesso administrativo aos alunos.

**Integração local concluída:** as telas usam API e SQL Server para login/cadastro, perfil (nome), cursos, disciplinas, tarefas e sessões. O planejador consulta a conta. Passaram 49 testes isolados da API, 21 do frontend, 52 verificações HTTP pelo proxy e uma conferência no Chrome. Build e TypeScript passaram. O site público não foi alterado; a conversa generativa depende de chave/modelo no servidor.

Os testes identificaram uma correção necessária no tempo de estudo: a duração é calculada no banco. O código foi ajustado sem modificar tabelas. Todos os dados fictícios foram removidos e o banco voltou ao estado anterior. Consulte `Backend/docs/TESTES_SQLSERVER.md` para o relatório e `Backend/scripts/test_sqlserver_integration.py` para o código do teste.

O controle administrativo foi implementado em etapa posterior. Continuam fora da versão atual: armazenamento de CPF/telefone, SMS, pagamentos, migração do localStorage e persistência de planos/chat. O adaptador de e-mail foi implementado, mas exige a ativação descrita acima; entrega real não é simulada como concluída.

## Atalhos do VS Code

Use **Terminal → Run Task / Executar Tarefa**:

- **EduTrack: iniciar API local (consulta)**: disponibiliza Swagger em `http://127.0.0.1:8000/docs`, sem habilitar escrita.
- **EduTrack: testar API (dados isolados)**: executa testes descartáveis, sem tocar o SQL Server.
- **EduTrack: verificar SQL Server (somente leitura)**: confere conexão e colunas.
- **EduTrack: iniciar site + API + Swagger**: inicia a versão conectada, com gravação habilitada no banco local, e abre site e Swagger no Chrome.
- **EduTrack: iniciar somente frontend (API deve estar ligada)**: inicia apenas o frontend na porta 3002.

Também é possível dar dois cliques em **Iniciar EduTrack.cmd**, na pasta FACULDADE. Mantenha a janela aberta. Encerre com **Ctrl+C** ou digite **sair** e Enter. O inicializador encerra somente seus próprios processos.

Swagger: **http://127.0.0.1:8000/docs**. Site: **http://localhost:3002/login**. Só respondem com os servidores ligados. Leia [TESTAR_APIS.md](TESTAR_APIS.md) para exemplos de cadastro, Authorize, CRUD e planejamento. Para instalar a API em outra máquina, siga `Backend/README.md`; o ambiente `.venv` não deve ser copiado entre máquinas.

## Fluxo implementado localmente

```text
Telas do EduTrack
       │ Mesma origem + cookie HttpOnly (HTTP apenas no loopback local)
       ▼
Proxy /api/backend/*
       │ Token enviado somente entre servidores
       ▼
API Python / FastAPI ───────── SQL Server / EduTrackIA
       │                        dados separados por usuario_id
       ├─ CRUD acadêmico
       └─ Edu IA
           ├─ consulta do aluno autenticado
           ├─ planejador por prazos e disponibilidade
           └─ modelo de IA externo, somente com configuração e consentimento
```

Nenhuma chave real está no código. Não compartilhe `.env`, tokens de sessão ou arquivos de banco em apresentações. Os exemplos nos testes são fictícios.

O cronômetro exige tarefa vinculada e usa chave de repetição para evitar duplicatas. Conquistas só aparecem após confirmação no banco. Tema, menu e rascunho do cronômetro permanecem locais; novos rascunhos são separados por usuário. Os dados antigos do navegador foram preservados, sem importação automática.

Para publicar a integração será necessário hospedar a API com HTTPS. O site público não consegue acessar o localhost do seu computador.
