# Estado da entrega - 16/11/2026

## O que está publicado

O frontend foi atualizado em 16/11/2026, em https://srv1834976.hstgr.cloud, com apresentação acadêmica e exportação do plano. A base de funcionalidades publicada em 12/11 foi preservada. Inclui Classroom completo, migração 005 e modelo com 14 tabelas. A importação real foi validada com uma conta autorizada: 1 disciplina, 16 tarefas, 56 conteúdos e 43 links; a repetição não criou duplicatas.

Evidências: [publicação](PUBLICACAO_CLASSROOM_COMPLETO_2026-11-12.md), [importação real](IMPORTACAO_REAL_SQL_FUNDAMENTALS_2026-11-12.md) e [correção da busca](CORRECAO_BUSCA_CLASSROOM_2026-11-12.md). Estes registros históricos não equivalem a um novo teste de todas as integrações em produção.

## Revisão local de 16/11/2026

- Frontend: 43 testes passaram; TypeScript e ESLint passaram na revisão inicial.
- Backend: 153 testes passaram em SQLite em memória; Ruff sem problemas.
- OpenSpec: 11 itens válidos em modo estrito.
- Nova página `/apresentacao`, com visão do projeto, roteiro em cinco passos, arquitetura e limites reais. A página inicial ganhou um link para ela e deixou de anunciar IA como se estivesse ativa.
- Publicação isolada do frontend concluída; nenhuma alteração de banco real, envio de e-mail ou ativação de integração ocorreu nesta revisão.

## Funcionalidades implementadas

Login/cadastro e recuperação; cursos, disciplinas, tarefas e sessões; foco e calendário; relatórios semanais e CSV; planejamento local por regras; importação de materiais Classroom; isolamento por usuário. A validação matemática do CPF não verifica identidade e o CPF não é armazenado.

## Limites para apresentar ao professor

- Google OAuth está em modo de teste: a conexão exige conta previamente autorizada.
- Chat/IA externa permanece desativado. O planejador por regras é funcional, mas não é uma resposta de modelo generativo.
- SMS, pagamentos, Flutter, histórico persistente de conversas e administração irrestrita de terceiros não estão ativos.
- Testes isolados não confirmam SQL Server real, e-mail, OAuth nem IA externa.
- Os três vídeos e seus links finais ainda precisam de conferência. Roteiro e prints não substituem a entrega dos vídeos.
- Melhorias de 16/11 publicadas em `/apresentacao` e no planejador; inspeção visual no navegador não concluída por indisponibilidade do CUA.

## Entrega

Siga [o roteiro de avaliação](ROTEIRO_AVALIACAO_FINAL.md) e [a lista final de conferência](ENTREGA_PROFESSOR_2026-11-16.md). O site antigo no Sites é independente. O estado de 09/11 foi preservado em [histórico](ESTADO_HISTORICO_2026-11-09.md), mas não descreve a versão publicada mais recente.

Melhoria funcional adicional: o plano proposto pode ser baixado em TXT, incluindo blocos, alertas e quantidade de tarefas fora do período, sem exportar identificadores internos. Dois testes cobrem o formato e a ausência desses identificadores.

Verificação SSH somente leitura em 16/11 confirmou que o frontend efetivamente ativo estava na release 20261112-180444, posterior à primeira publicação registrada de 12/11. Web, API e SQL estavam saudáveis.

## Publicação final de 16/11

Release edutrack-ui-20261116-215209 publicada. Somente web recriado e saudável. Página inicial, apresentação, login e privacidade: HTTP 200; 11 recursos estáticos: 200; API sem sessão: 401. Containers API e SQL preservaram os mesmos IDs. Imagem anterior retida para rollback. Confira [validação](VALIDACAO_2026-11-16.md).

## Edu IA: experiência conversacional atualizada

Em 16/11 foi publicada a release frontend-only `edutrack-chat-20261116-222336`. Chat com sugestões, composição confortável, formatação segura, copiar/baixar conversa e interrupção da espera; planejador local em aba separada. 48 testes frontend, TypeScript, ESLint, build e OpenSpec passaram. Estado real permanece sem modelo/chave e chat generativo desativado. Não confundir nova interface com ativação do Gemini ou OpenAI. [Detalhes, evidências e limites](EDU_IA_EXPERIENCIA_2026-11-16.md).
