# Documentação do EduTrack

Índice de consulta do projeto no VS Code. Abra `EduTrack.code-workspace`, na pasta FACULDADE, para encontrar o frontend, backend e estes documentos juntos, sem mover ou duplicar os códigos.

## Guias em Markdown

- [Google Classroom e Gemini: implementação, privacidade e configuração](CLASSROOM_E_GEMINI.md).
- [Validação das integrações — 09/11/2026](VALIDACAO_INTEGRACOES.md).
- [Estado da entrega final](ESTADO_ATUAL.md).
- [Resultados da validação final](VALIDACAO_FINAL.md).
- [Preparação para Hostinger](HOSTINGER.md).
- [Plano específico da VPS, aprovado e executado](PLANO_HOSTINGER.md).
- [Publicação, acesso e operação na Hostinger](PUBLICACAO_HOSTINGER.md).
- [Roteiro dos vídeos da avaliação](ROTEIRO_AVALIACAO_FINAL.md).
- [Modelo de dados / DER](MODELO_DE_DADOS.md).
- [Recuperação de senha](RECUPERACAO_DE_SENHA.md).
- [Mapa do projeto e inicialização](COMECE_AQUI.md).
- [API e instruções do backend](../edutrack-api/README.md).
- [Testar as APIs pelo Swagger](TESTAR_APIS.md).
- [Dicionário de dados](DICIONARIO_DE_DADOS.md).
- [CPF e verificação por e-mail](CPF_E_EMAIL.md).
- [Calendário de estudos inspirado no GitHub](../edutrack-app-completo/docs/CALENDARIO-DE-ESTUDOS.md).
- [Foco e ofensiva](../edutrack-app-completo/docs/FOCO-E-OFENSIVA.md).
- [Integração da Edu IA](../edutrack-app-completo/docs/INTEGRACAO_EDU_IA.md).

## OpenSpec

O OpenSpec está instalado como dependência de desenvolvimento do frontend. Não é uma tela do site nem substitui a documentação das APIs.

- [Configuração e contexto](../edutrack-app-completo/openspec/config.yaml).
- [Autenticação](../edutrack-app-completo/openspec/specs/autenticacao/spec.md).
- [Organização acadêmica](../edutrack-app-completo/openspec/specs/organizacao-academica/spec.md).
- [Administração](../edutrack-app-completo/openspec/specs/administracao/spec.md).
- [Edu IA](../edutrack-app-completo/openspec/specs/edu-ia/spec.md).
- [Integrações Google](../edutrack-app-completo/openspec/specs/integracoes-google/spec.md).
- [Calendário de estudos](../edutrack-app-completo/openspec/specs/calendario-de-estudos/spec.md).
- [Relatórios semanais](../edutrack-app-completo/openspec/specs/relatorios/spec.md).

Na pasta do frontend, `pnpm run openspec:list` lista as especificações e `pnpm run openspec:validate` confere sua estrutura. A pasta `openspec/changes` é reservada ao acompanhamento de mudanças.

## Como interpretar o estado do projeto

As especificações descrevem requisitos; não são comprovação de implementação, testes ou publicação. Alguns documentos anteriores descrevem etapas de protótipo e propostas futuras. Consulte o código e os registros da etapa correspondente antes de afirmar que algo funciona em produção.

O código atual possui integração local e uma instalação na Hostinger entre frontend, API Python/FastAPI e SQL Server. A área administrativa tem controle de acesso, mas não oferece gestão completa de outros usuários. A IA generativa depende de configuração e consentimento; o planejador por regras não equivale a uma resposta de modelo externo.

Site local: <http://localhost:3002/login>. Swagger local: <http://127.0.0.1:8000/docs>. Esses endereços dependem dos servidores ligados. Abrir este workspace ou ler a documentação não inicia serviços, não altera o banco e não publica o site.

Não inclua senhas, tokens, arquivos `.env` ou códigos de verificação em documentos de entrega. Operações de teste que gravem no SQL Server exigem autorização; prefira testes isolados.
