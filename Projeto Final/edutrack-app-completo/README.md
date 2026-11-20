# EduTrack — frontend

Interface acadêmica em React, TypeScript e Next.js, integrada à API Python/FastAPI em `../edutrack-api` e ao SQL Server. A documentação consolidada está em `../edutrack-documentacao/DOCUMENTACAO.md`; consulte `ESTADO_ATUAL.md` para distinguir implementação, teste e publicação.

## Recursos

- Login, cadastro, validação matemática de CPF, verificação por e-mail e recuperação de senha pela API.
- Cursos, disciplinas, tarefas e sessões de estudo isolados por usuário.
- Dashboard, calendário anual de estudos, cronômetro, floresta de foco e ofensiva.
- Relatórios com semanas locais, tabela acessível e exportação CSV.
- Planejador por regras e integração preparada para IA generativa, dependente de chave, modelo e consentimento.
- Administração protegida por função, navegação responsiva, tutorial e temas claro/escuro.

SMS, pagamentos e aplicativo Flutter continuam planejados. A área administrativa não oferece gestão completa de terceiros.

## Desenvolvimento local no Windows

Requisitos: Node.js 22.13 ou superior, pnpm, Python 3.12, dependências do backend, ODBC Driver 18 e SQL Server configurado. O iniciador não cria nem migra tabelas.

```powershell
pnpm install --frozen-lockfile
pnpm run dev:local
```

O comando inicia os dois serviços em loopback e abre o Chrome. Site: `http://localhost:3002/login`. Swagger: `http://127.0.0.1:8000/docs`. Mantenha o terminal aberto; Ctrl+C encerra os processos criados pelo iniciador. O CRUD grava no banco local configurado.

## Distribuição Node para hospedagem

```powershell
pnpm run build:hostinger
pnpm run start:hostinger
```

Configure `EDUTRACK_API_URL` no servidor e `EDUTRACK_SITE_URL` com a origem pública HTTPS exata. `PORT` e `HOSTNAME` controlam a escuta (padrão local: 3002 e 127.0.0.1). A API Python e o SQL Server precisam de hospedagem própria compatível; GitHub Pages estático não executa esses serviços.

O comando prepara e executa `.next-hostinger/standalone/server.js`, copiando os arquivos públicos e estáticos. Compilar não publica e não altera o banco. `pnpm build`/`pnpm start` preservam a distribuição Vinext utilizada anteriormente.

## Verificação

```powershell
node --experimental-strip-types --test tests/*.test.mjs
pnpm exec tsc --noEmit
pnpm lint
pnpm run openspec:validate
```

Os dados da prévia em `tests/visual-study-activity` e da API `tests/preview_app.py` são fictícios e não devem ser implantados como ambiente de alunos.

## Segurança e fontes

Não publicar `.env`, chaves, senhas, cópias do banco ou sessões de navegador. Configurações locais privadas ficam em `%LOCALAPPDATA%/EduTrack/backend.env`. A chave de IA e o SendGrid pertencem exclusivamente ao backend.

`.openai/hosting.json` identifica o projeto Sites histórico. O site público antigo só muda por uma publicação explícita; alterações neste checkout não são automaticamente enviadas para ele. A hospedagem escolhida para a próxima entrega é a Hostinger, sujeita à conferência do plano e implantação autorizada.

