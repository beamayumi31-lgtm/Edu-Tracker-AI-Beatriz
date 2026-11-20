# Integração da Edu IA

> Documento histórico do protótipo. A versão conectada atual usa o BFF `/api/backend/edu-ia/*`, a API Python e contexto autorizado no servidor. Para configurar OpenAI/Gemini e consultar as restrições de dados do Classroom, use [CLASSROOM_E_GEMINI.md](../../edutrack-documentacao/CLASSROOM_E_GEMINI.md). Não aplique a configuração abaixo à versão atual sem verificar a arquitetura.

O frontend chama somente a rota interna `POST /api/edu-ia`. As credenciais nunca devem ser colocadas em `EduTrackApp.tsx` ou enviadas ao navegador.

## Opção preferencial: API externa do projeto

Configure no servidor:

```env
EDU_AI_API_URL=https://api.exemplo.com/edu-ia
EDU_AI_API_TOKEN=token-opcional
```

A API externa receberá um `POST` em JSON:

```json
{
  "messages": [
    { "role": "user", "content": "Explique normalização de banco de dados" }
  ],
  "context": {
    "mode": "duvidas",
    "selectedDiscipline": {
      "title": "Banco de Dados",
      "progress": 40,
      "goal": "3 horas"
    },
    "courses": [],
    "disciplines": [],
    "tasks": []
  },
  "instructions": "Instruções de comportamento geradas pelo servidor do EduTrack"
}
```

A resposta deve usar um destes formatos:

```json
{ "reply": "Resposta da assistente" }
```

ou:

```json
{ "message": "Resposta da assistente" }
```

Quando `EDU_AI_API_TOKEN` estiver configurado, o EduTrack envia `Authorization: Bearer <token>`.

## Modos aceitos

- `duvidas`: explicações, exemplos e perguntas de verificação;
- `planejamento`: organização de tarefas, prazos e sessões de estudo;
- `revisao`: resumos, revisão ativa e exercícios de fixação.

## Resiliência

Se a API não estiver configurada ou ficar indisponível, o frontend mantém orientações locais básicas. Para liberar a IA em produção, adicione autenticação de usuário, limite de requisições e monitoramento de custos antes de cadastrar uma chave real.
