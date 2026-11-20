# Roteiro da avaliação final — EduTrack

Os critérios permitem um vídeo para cada etapa. Grave com uma conta de demonstração, sem mostrar senhas, códigos, links de recuperação, chaves, .env ou dados de colegas. Os arquivos de configuração usados nos vídeos devem ser exemplos sem valores reais.

## Vídeo 1 — Funcionalidades (8 a 12 minutos)

1. **Introdução:** “O EduTrack organiza cursos de faculdade e cursos livres, disciplinas, atividades e tempo de estudo.” Mostre a tela inicial, os temas claro/escuro e o menu recolhível.
2. **Cadastro:** mostre campos e validações, inclusive CPF inválido, confirmação da senha e e-mail. Explique que CPF é validado matematicamente e descartado; isso não consulta Receita Federal nem comprova titularidade.
3. **Login:** entre com a conta de demonstração. Explique que os dados pertencem à conta e ficam na API/SQL Server.
4. **Esqueci minha senha:** solicite o link para um endereço autorizado, pause a gravação durante e-mail e senha, retome após a redefinição e demonstre o novo login. Não apresente captura de e-mail simulada como entrega real.
5. **Cursos → disciplinas → tarefas:** crie um registro “Demonstração da avaliação” em cada nível. Abra detalhes, edite uma tarefa, marque como concluída e recarregue a página para demonstrar persistência. Exclua somente os registros de demonstração sem histórico, na ordem tarefa → disciplina → curso. Explique o bloqueio de exclusões com vínculos.
6. **Foco e progresso:** escolha tarefa, inicie, pause e retome o cronômetro. Mostre floresta, ofensiva e calendário. Não aguarde 25 minutos em silêncio: use uma sessão já concluída ou uma gravação editada com o corte informado.
7. **Relatórios:** mostre datas da semana, resumo, gráfico, tabela, semana anterior e CSV. Explique que conclusão por disciplina é acumulada.
8. **Edu IA:** mostre o planejador usando as atividades da conta e suas restrições de tempo. Enquanto não houver chave configurada, declare que a conversa generativa está preparada e não ativada. Após ativação, solicite explicação de uma matéria e plano, autorize o contexto e confira a resposta.
9. **Administração e perfil:** demonstre o acesso restrito sem afirmar que há gestão completa de outros alunos. EduTrack Pro é somente uma proposta, sem cobrança.

## Vídeo 2 — Banco e modelo (4 a 6 minutos)

1. Abra `MODELO_DE_DADOS.md` com visualização Mermaid ou o DER exportado.
2. Explique o vínculo usuário → curso → disciplina → tarefa → sessão e as cardinalidades.
3. No SQL Server, mostre nomes de tabelas, PK, FK, restrições e coluna calculada da duração; oculte linhas reais de usuários.
4. Abra `DICIONARIO_DE_DADOS.md`. Explique UUID, UTC, hash de senha, HMAC dos códigos e hash de tokens temporários.
5. Diferencie o SQL para banco vazio das migrações incrementais. A migração 003 já foi aplicada no ambiente local com autorização.
6. Mostre Swagger local e um fluxo usando apenas dados autorizados de demonstração. Não grave o JWT em Authorize.

## Vídeo 3 — GitHub, estrutura e OpenSpec (4 a 6 minutos)

1. Abra o repositório final no GitHub e o README. Mostre a organização frontend, backend, documentação e especificações.
2. Explique React/TypeScript, a API FastAPI e a persistência SQL Server.
3. Abra a tela de recuperação e seu contrato HTTP; depois o serviço, o modelo e os testes. Demonstre como uma regra do OpenSpec corresponde ao código e ao teste.
4. Mostre o cálculo do relatório semanal e um teste que separa duas segundas-feiras de semanas diferentes.
5. Execute testes e validação OpenSpec. Mostre resultados atuais, sem reutilizar números de etapas antigas.
6. Explique que os segredos ficam fora do Git. Mostre `.env.example`, nunca o arquivo preenchido.
7. Se a Hostinger já estiver publicada, abra a URL verificada. Caso ainda não esteja, identifique explicitamente a demonstração como local.

## Checklist antes de enviar

- [ ] Áudio compreensível e texto legível em tela cheia.
- [ ] Login, cadastro, recuperação, IA/limite atual, relatórios, disciplinas e tarefas apresentados.
- [ ] Banco e modelo apresentados com os dados pessoais ocultos.
- [ ] GitHub com código final, README, documentação e OpenSpec acessíveis ao professor.
- [ ] Links dos vídeos abrem na conta ou no modo de acesso esperado pelo professor.
- [ ] Nenhuma chave, senha, CPF real, JWT ou link de recuperação aparece na gravação.
- [ ] O titular revisou e autorizou o envio. Anexar e clicar em Entregar no Classroom são etapas distintas.
