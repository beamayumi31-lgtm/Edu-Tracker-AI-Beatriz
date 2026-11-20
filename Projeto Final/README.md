# EduTrack — Projeto Final

Gestão acadêmica com **React/TypeScript**, **Python/FastAPI**, **SQL Server** e **OpenSpec**.
Entrega de Innovation Lab preparada em **17/11/2026**, com 16 respostas, código e evidências.

## Comece por aqui
- [PR final #2 — aberto para revisão](https://github.com/antoniobrites/Faculdade-Impacta/pull/2)
- [Índice das 16 tarefas](docs/innovation-lab/LEIA-ME.md)
- [Adaptações para avaliação](docs/innovation-lab/ADAPTACOES.md)
- [Relatório final em PDF](docs/innovation-lab/RELATORIO_FINAL.pdf)
- [Validação e limites](docs/innovation-lab/VALIDACAO.md)
- [Pesquisa e cópias do Figma](docs/pesquisa/referencias.md)
- [PR de documentação integrado](https://github.com/antoniobrites/Faculdade-Impacta/pull/1)

O PR final permanece aberto para revisão do professor. Estes arquivos não publicam o site nem enviam trabalhos ao Classroom.
O endereço já utilizado pelo projeto é https://srv1834976.hstgr.cloud; esta entrega local não comprova atualização ou disponibilidade atual desse ambiente.

## Organização
| Pasta | Finalidade |
|---|---|
| edutrack-app-completo | Frontend, componentes, tema, proxy e OpenSpec |
| edutrack-api | API, modelos, migrações, cálculos, relatórios e testes |
| edutrack-documentacao | Documentação histórica, DER e dicionário |
| docs/innovation-lab | Entrega atual, respostas e evidências fictícias |
| deploy | Configuração existente; executar somente com autorização |

Abra **EduTrack.code-workspace** no VS Code. Documentos históricos preservam seu contexto; para as tarefas atuais, prevalecem as evidências datadas em docs/innovation-lab.

## Instalação para desenvolvimento
Requisitos: Node >=22.13, pnpm, Python 3.12. Para banco real: SQL Server e Microsoft ODBC Driver 18.

Na pasta edutrack-api:
```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.venv\Scripts\python.exe -m pip install --no-deps -e .
```
Na pasta edutrack-app-completo:
```powershell
pnpm install --frozen-lockfile
```
Use apenas .env.example como referência. Segredos reais ficam fora do Git. Migrações não são automáticas e exigem autorização; nunca execute o esquema de banco vazio sobre um banco existente.

## Demonstração isolada, sem banco real
Terminal 1, em edutrack-api:
```powershell
$env:EDUTRACK_QA_PREVIEW='1'
.venv\Scripts\python.exe -m tests.preview_app
```
Terminal 2, em edutrack-app-completo:
```powershell
$env:EDUTRACK_API_URL='http://127.0.0.1:8014'
$env:EDUTRACK_PUBLIC_ORIGIN='http://localhost:3016'
pnpm exec next dev --webpack --hostname 127.0.0.1 --port 3016
```
Abra http://localhost:3016/login e http://127.0.0.1:8014/docs.
Conta **exclusivamente fictícia dessa fixture**: avaliacao@example.com / Demonstracao-local-2026.
Ela não é criada em produção. A fixture usa SQLite temporário e não envia e-mail nem chama Google/IA reais. Mantenha os dois terminais abertos.

## Testes e build
```powershell
# Backend
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\ruff.exe check edutrack scripts tests
.venv\Scripts\python.exe scripts/calculate_progress.py --completed 3 --total 4
# Frontend
node --test tests/*.test.mjs
pnpm exec tsc --noEmit
pnpm run lint
pnpm run build:hostinger
pnpm run openspec:validate
```
Resultados: 200 testes de API aprovados; 16 casos POSIX pulados no Windows. Frontend: 49 testes aprovados. Build Hostinger, lint e TypeScript verificados localmente.

## Novas funcionalidades desta entrega
- Busca por nome da disciplina **OU** tarefas atrasadas, com paginação e isolamento por usuário.
- Cálculo Python compartilhado, validação e JSON para a tarefa 12.
- PDF privado de progresso acumulado com ReportLab, download autenticado e limites explícitos.
- Especificações, auditoria de modelos existentes e arquivo do planejamento de notas (não implementado).

SQL Server/Python e React substituem Xano/FlutterFlow conforme a arquitetura mantida pelo aluno. A aceitação pedagógica das adaptações depende do professor. Autenticação Gemini Code Assist institucional não foi comprovada.
