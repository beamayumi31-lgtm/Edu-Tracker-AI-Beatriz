# Decisões

1. Preservar a arquitetura Next/BFF/FastAPI/SQL Server e o cookie HttpOnly Strict.
2. Fazer callback com POST autenticado após hidratação e remoção da query, sem tokens em storage.
3. Usar OAuth Web com PKCE e state hash consumido atomicamente; cifrar refresh token e verifier com Fernet vinculado ao usuário.
4. Reconsultar dados no servidor na confirmação. Não confiar no payload visual da prévia.
5. Preservar itens importados, sem merge automático de campos ou recriação de exclusões.
6. Manter o planejador local independente de LLM. Gemini gratuito sem contexto acadêmico automático; dados Classroom excluídos de todos os provedores.
7. Testar com transportes HTTP simulados e banco descartável. Ativação real e SQL Server real exigem etapas posteriores documentadas.

## Limites

Não importa notas, anexos, materiais, submissões nem avisos. Não vincula turmas a disciplinas manuais. Não faz sincronização em segundo plano. A página importa uma turma por vez. Limites de frequência são locais ao processo; Redis é necessário antes de múltiplos workers. Não há verificação de credenciais reais nesta etapa.
