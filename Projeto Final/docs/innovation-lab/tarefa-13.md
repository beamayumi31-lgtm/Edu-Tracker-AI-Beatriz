# Tarefa 13 — APIs CRUD de disciplinas

EduTrack · Innovation Lab · Faculdade Impacta · 17/11/2026

**Situação:** Executado no FastAPI.

## Entrega e explicação

Rotas preservadas: GET /api/disciplines; POST /api/disciplines; PUT /api/disciplines/{id}; DELETE /api/disciplines/{id}. O PUT mantém o contrato existente em lugar do PATCH ilustrativo do enunciado.

O usuário vem da autenticação do servidor. O curso precisa pertencer à mesma conta, e consultas e alterações são restritas ao proprietário. IDs de outra conta não conferem autorização. O teste cobre criação, leitura, edição, exclusão e isolamento.

Swagger de QA: http://127.0.0.1:8014/docs enquanto a prévia estiver em execução. Instalação local normal: http://127.0.0.1:8000/docs. O OpenAPI exportado permite examinar o contrato mesmo com o servidor desligado.

## Exemplo de entrada e saída

As imagens seguintes mostram a execução real de POST /api/disciplines com JSON: curso_id, nome, professor e carga_horaria. A resposta HTTP 201 devolveu os mesmos campos, o id criado e as datas criado_em e atualizado_em. O Swagger registrou 156 ms nesta execução; esse valor é uma observação local, não uma medição de desempenho da produção.

O teste usou uma conta fictícia e SQLite temporário em 17/11/2026, às 22:10 de São Paulo. Os horários retornados estão em UTC. Nenhum dado real de aluno nem a VPS foi alterado.

## Fontes e evidências

- [Print da requisição JSON](evidencias/13-api-requisicao.png)
- [Print da resposta HTTP 201](evidencias/13-api-resposta-201.png)
- [Registro de entrada e saída sem credenciais](evidencias/13-api-requisicao-resposta.json)

- [edutrack-api/edutrack/routes.py](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-api/edutrack/routes.py)
- [edutrack-api/docs/openapi.json](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-api/docs/openapi.json)

Consulte também o índice, a matriz de adaptações e os arquivos em `evidencias/` deste pacote.
