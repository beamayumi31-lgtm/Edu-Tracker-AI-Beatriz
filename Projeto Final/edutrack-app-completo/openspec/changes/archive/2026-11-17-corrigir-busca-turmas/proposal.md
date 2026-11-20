# Busca de turmas com resultado visível

## Why

A busca colocava o resultado somente em um select e apagava as escolhas anteriores. O aluno percebia o botão como sem resposta; a confirmação da importação ficava depois de uma lista longa.

## What Changes

- Cartões selecionáveis para cada turma, contagem e estado vazio explícitos.
- Carregamento, falhas e nova tentativa próximos à ação correspondente.
- Atualização da busca preserva turma, destino e seleção manual válida.
- Confirmação da importação antes da lista; vínculo existente e atalho da disciplina visíveis.
- Bloqueio síncrono contra cliques concorrentes e indicação do motivo de um botão desabilitado.

## Impact

Frontend apenas em produção, sem dependências novas, mudanças na API, migrações ou novos escopos Google. Fixture de teste permite falha única simulada na busca. Publicação depende de aprovação específica da VPS; testes locais não representam uma nova validação com Google real.
