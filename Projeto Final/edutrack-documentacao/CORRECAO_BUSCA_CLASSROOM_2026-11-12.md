# Correção da busca de turmas — 12/11/2026

## Situação

Publicada após aprovação explícita do titular, no pacote `edutrack-entrega-final-20261112-180444`, SHA-256 `6bb9475a4f0f0ba3dbf64303e410c905761edd6a7b0b3fa35f167f81d40cda09`. Build Linux, healthcheck do frontend, HTTPS e readiness aprovados. IDs dos containers da API, SQL e CRM, além dos hashes da configuração Nginx, permaneceram iguais. Apenas o frontend foi reconstruído e reiniciado; nenhuma turma foi importada durante a publicação. Após login do titular no Chrome, a busca real retornou seis turmas em cartões e a prévia de SQL Fundamentals carregou corretamente.

## Diagnóstico

Conferência posterior em 17/11/2026: a VPS aponta para `edutrack-closed-20261116-230807`, uma publicação mais recente. Seu componente de integrações mantém os cartões de turmas, a preservação da seleção e a confirmação antes da lista. `/`, `/login` e `/integracoes` responderam HTTP 200; web e API estavam saudáveis. Essa conferência foi somente de leitura, sem substituir a publicação posterior. A validação com a conta Google descrita abaixo pertence à entrega de 12/11; não representa uma nova importação em 17/11.

Na interface anterior, Buscar turmas preenchia somente um select com o texto inicial “Escolha uma turma”. Repetir a busca apagava a seleção e a prévia. A confirmação de importação aparecia depois da lista completa de atividades. Isso dificultava perceber o resultado e concluir a ação.

As consultas de turmas observadas na produção retornaram HTTP 200. A seleção de SQL Fundamentals e a prévia funcionaram durante a investigação. Não foi reproduzida falha no serviço Google nessa sessão; portanto, este diagnóstico não afirma que toda falha relatada foi de backend. A sessão Chrome de produção havia expirado; o titular entrou novamente e permitiu validar a nova interface publicada.

## Alterações

- Cartões com nome e seção das turmas, resultado contado e seleção destacada.
- Estado inicial orienta buscar primeiro, sem preencher um curso antes.
- Indicador de carregamento, erro próximo da operação e nova tentativa de busca/prévia.
- Atualizar preserva turma, destino e seleção manual ainda disponível; avisa se a turma desapareceu.
- Destino e importação aparecem após selecionar uma turma; o botão de confirmar vem antes das atividades e informa por que está desabilitado.
- Turma já importada fica vinculada ao curso original e oferece Abrir disciplina existente.
- Cliques concorrentes bloqueados; rolagem respeita preferência por movimento reduzido.

Mudanças de produção limitadas a `app/ui/ConnectedIntegrations.tsx` e `app/integrations.css`. Sem alteração de API, banco, permissões Google ou dependências. A flag `EDUTRACK_QA_CLASSROOM_FAIL_FIRST_SEARCH` existe apenas na fixture descartável de testes.

## Testes

Chrome local com API em 8014, frontend em 3014, SQLite temporário e Google simulado. Nenhuma turma real foi importada nesta validação.

| Cenário | Resultado observado |
|---|---|
| Primeira busca retorna 503 simulado | Erro visível e botão Tentar buscar novamente |
| Nova tentativa | Dois cartões: SQL Classroom e Python |
| Atualizar busca com uma atividade marcada | Turma, nome do curso e checkbox preservados; confirmação habilitada |
| Primeira importação completa | 1 curso, 1 disciplina, 2 tarefas, 5 conteúdos e 4 links |
| Reimportar no mesmo curso | 0 disciplinas, tarefas ou conteúdos novos; 5 conteúdos atualizados e 3 registros pessoais preservados |
| Prévia de turma indisponível | Mensagem junto da etapa, nova tentativa e importação desabilitada |
| Abrir disciplina existente | Navegação correta; 2 tarefas e 5 conteúdos na disciplina |
| Celular 390 px | Documento 375 px, sem excesso horizontal |
| Temas | Claro em desktop e escuro em celular conferidos |

TypeScript, ESLint do componente, 41 testes frontend, Ruff da fixture e build de produção Hostinger aprovados. As capturas em `evidencias/busca-turmas-2026-11-12/` mostram somente dados fictícios. A fixture contém texto adversarial deliberado como conteúdo; não é instrução.

## Plano de publicação executado após aprovação

1. Conferir SHA-256 e manifesto do novo ZIP, além do diff contra a release pública.
2. Conferir que API de produção, migrações e infraestrutura são idênticas; registrar IDs de API/SQL/CRM e hashes Nginx.
3. Copiar pacote para uma nova release e preservar a imagem atual do frontend para reversão.
4. Reconstruir apenas `web` e executar `up -d --no-deps --no-build --wait web` com o compose existente. Pode haver breve indisponibilidade do EduTrack.
5. Confirmar HTTPS, readiness e preservação dos IDs de API/SQL/CRM e hashes Nginx; só então apontar `current` à nova release.
6. **Concluído com a sessão do titular:** Buscar turmas exibiu seis turmas reais. SQL Fundamentals mostrou 16 atividades, 24 materiais, 16 avisos e 43 links. Atualizar turmas manteve seleção e vínculo ao curso Ciência da Computação. Abrir disciplina existente mostrou a biblioteca com 56 conteúdos, e a lista Disciplinas confirmou uma disciplina com 14 atividades pendentes (duas tarefas já concluídas pelo aluno). Nenhuma turma adicional foi importada, nem tarefas alteradas.

Não executa migração, comando SQL, alteração de credenciais, DNS, certificados ou configuração Nginx. Reversão prevista: retomar a imagem anterior apenas do frontend e manter o apontamento anterior; nunca remover volumes.
