# Estado da entrega final — atualização local de 09/11/2026

## Atualização local: Classroom e Gemini

Implementada a página Integrações, OAuth por aluno, prévia e importação de disciplinas/tarefas com deduplicação, desconexão e proteção de contexto. Adaptador Gemini e configuração segura preparados; o planejador local permanece disponível. Ver [guia completo](CLASSROOM_E_GEMINI.md) e [validação](VALIDACAO_INTEGRACOES.md).

Esta atualização ainda não foi publicada na Hostinger/GitHub. A migração 004 está preparada, não aplicada. O modelo alvo tem treze tabelas; o último estado confirmado de produção continua com nove. Não há chave Gemini nem cliente OAuth real configurados. Os resultados abaixo descrevem a entrega anterior, de 03/11/2026.

Este documento distingue implementação, testes locais e publicação. Não interpretar os resultados antigos como prova de publicação atual.

## Implementado

- Login, cadastro, validação matemática de CPF sem armazenamento e verificação por e-mail via SendGrid.
- Recuperação de senha por link de 15 minutos, uso único, respostas neutras e invalidação das sessões anteriores.
- Cursos, disciplinas, tarefas e sessões com API, SQL Server e separação entre usuários.
- Dashboard, calendário de estudos, floresta de foco, ofensiva, menu recolhível, tutorial e temas claro/escuro.
- Relatórios por semana local, navegação entre semanas, dados acessíveis e exportação CSV.
- Planejador por regras com contexto da conta; agente de IA generativa implementado para futura ativação.
- Controle de acesso administrativo. A área não oferece gestão irrestrita de outros alunos.
- Swagger local, DER, dicionário, SQL para banco vazio, migrações, testes e OpenSpec.

## Ativação local conferida

A migração 003 foi aplicada após autorização explícita. As nove tabelas foram verificadas por consultas sem dados; as quantidades das tabelas anteriores permaneceram iguais. A configuração privada local ativa recuperação por e-mail e mantém o remetente SendGrid existente. Nenhuma senha real foi redefinida e nenhum e-mail novo foi enviado durante esta etapa.

92 testes de backend e 39 de frontend passaram. A configuração de envio é substituída por captura em memória nos testes. A compilação Node/Next 16.4.5 para Hostinger passou; TypeScript, ESLint e Ruff também passaram. OpenSpec: 7 itens válidos. Auditoria das dependências de produção do frontend: nenhuma vulnerabilidade conhecida. [Detalhes e limites da validação](VALIDACAO_FINAL.md).

## Dependências externas

- **IA generativa:** o usuário informou que ainda não possui chave e solicitou apenas preparar a integração. `scripts/configure_ai.py` recebe a chave em entrada oculta e a salva fora do Git/OneDrive. Não há chamada paga ou resposta real de modelo validada.
- **Hostinger:** publicado em <https://srv1834976.hstgr.cloud>, após autorização. API e frontend saudáveis; SQL Server Express com nove tabelas, TLS e banco novo. SendGrid e recuperação habilitados. Não houve migração de contas locais. [Evidências e limites](PUBLICACAO_HOSTINGER.md).
- **GitHub:** destino autorizado `antoniobrites/Faculdade-Impacta`, pasta `2-semestre/Projeto Final`. Código completo, testes, documentação e OpenSpec separados de segredos e dados dos alunos.
- **Vídeos:** o roteiro está pronto. Gravação e links finais precisam ser conferidos; prints e roteiro não equivalem a vídeo entregue.

## Escopo preservado

SMS, pagamentos, Flutter, histórico persistente de conversas e administração completa de terceiros continuam fora da versão atual. Os requisitos antigos que descrevem esses recursos são planejamento, não comprovação de funcionamento.

O endereço público antigo no Sites permanece separado. Use o novo endereço Hostinger acima. Endereços localhost dependem dos processos em execução.
