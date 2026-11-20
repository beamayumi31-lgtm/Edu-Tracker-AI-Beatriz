# Acesso adulto fechado e conta limpa para gravacao

Estado executado em 16/11/2026, apos autorizacao explicita do titular. Site: https://srv1834976.hstgr.cloud. Release: `edutrack-closed-20261116-230807`.

## Publicacao

- Acesso restrito somente a conta academica existente aprovada pelo titular, com email confirmado. Cadastro fechado para todos; nenhum professor ou novo usuario foi criado.
- API e frontend saudaveis. SQL e CRM mantiveram os mesmos containers. Nenhuma migracao, mudanca DNS/certificado ou permissao foi realizada.
- Cinco paginas e quinze assets HTTP 200; rotas privadas sem sessao 401; cadastro 403. Guard de acesso real validado por leitura: conta aprovada permitida, conta excluida negada. Nenhuma sessao foi fabricada e nao houve login real pelo navegador nesta verificacao.
- Vinte testes de acesso fechado passaram na imagem Linux com rede desativada e SQLite temporario. Testes locais completos e Ruff foram aprovados; os detalhes estao nos registros de validacao.
- A primeira verificacao operacional esperava um objeto de erro, mas o proxy devolveu mensagem textual e acionou rollback automatico. O validador foi corrigido e a segunda publicacao passou integralmente.

## IA e custo zero

Gemini permanece OFF, sem chave presente; OpenAI tambem sem chave. Nenhuma chamada generativa ou cobranca realizada. Ainda faltam o handoff privado da chave e a verificacao do projeto/modelo com cota gratuita e sem faturamento. Se o custo zero nao puder ser confirmado, nao ativar. A flag de contexto gratuito nao e uma trava de cobranca. Nao ha fallback para outro modelo/provedor pago.

## Limpeza reversivel concluida

Somente os dados academicos locais da conta autorizada foram removidos:

| Categoria | Antes | Depois |
|---|---:|---:|
| Cursos | 1 | 0 |
| Disciplinas | 1 | 0 |
| Tarefas | 16 | 0 |
| Conteudos locais Classroom | 56 | 0 |
| Vinculos de disciplinas Classroom | 1 | 0 |
| Vinculos de tarefas Classroom | 16 | 0 |
| Sessoes de estudo | 0 | 0 |
| Relatorios semanais | 0 | 0 |

Perfil, confirmacao de email, credenciais, conexao Google e demais usuarios foram preservados por comparacao de hashes. Nenhuma chamada modificou o Google Classroom. A importacao no aplicativo exige clique explicito e nao repovoa a conta automaticamente ao entrar.

Antes do commit: backup SQL COPY_ONLY/CHECKSUM e RESTORE VERIFYONLY; snapshot JSON tipado completo; ensaio em transacao SERIALIZABLE de exclusao e restauracao com comparacao exata de IDs, datas, textos e fingerprints protegidos, seguido de ROLLBACK. So depois a limpeza final foi confirmada e relida como vazia.

## Recuperacao privada

Backup SQL: `/opt/edutrack/backups/sql/EduTrackIA_20261116T231358Z.bak`, 7.856.128 bytes. SHA-256: `dbd7461255f9978a81d4e0b088165dfc6eabff3d930835366b1ffd1204104ede`.

Snapshot por titular, helper e procedimento de restauracao ficam no diretorio privado `/opt/edutrack/backups/academic-20261116-recording/`, fora do site/pacote publico. O snapshot nao inclui usuarios, senhas nem tokens Google. Hash do arquivo: `5cc21acfa58974b945e402eea004d71be0a1bc65823b1f0ec5fdcce30162f5de`.

Restauracao exige nova autorizacao e conta ainda sem dados academicos. O operador pode executar no servidor o procedimento privado `python3 /opt/edutrack/backups/academic-20261116-recording/restore_owner.py --restore-authorized`. Ele valida hash, identifica o titular, exige destino vazio e preserva outros dados. Nao sobrescrever dados novos nem restaurar o banco inteiro sobre outros usuarios para desfazer esta limpeza.

Rollback de codigo: imagens `edutrack-api:rollback-20261116-closed` e `edutrack-web:rollback-20261116-closed`; release anterior preservada `edutrack-chat-20261116-222336`; configuracao anterior em arquivo privado de backup. Restaurar configuracao antiga pode reabrir acesso/cadastro e depende de decisao explicita. Rollback de codigo nao restaura os dados academicos; usar o procedimento por titular para isso. Nunca usar `docker compose down -v`.

Evidencias sem conteudos privados: `output/edutrack-closed-20261116/verificacao-publicacao.json`, `account-guard.json`, `testes-linux.log`; e `output/edutrack-cleanup-20261116/backup-proof.json`, `restore-rehearsal.json`, `cleanup-result.json`. A conta esta vazia para iniciar a gravacao; IA real ainda nao esta ativa.
