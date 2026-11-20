# Integrar Google Classroom e preparar Gemini

## Why

O aluno precisa trazer suas disciplinas e tarefas do Classroom para organizar os estudos. A Edu IA precisa aceitar Gemini, preservando o funcionamento sem chave e o controle dos dados.

## What Changes

- Página Integrações com OAuth individual, prévia, seleção e importação idempotente.
- Callback compatível com cookie Strict; tokens cifrados e nova migração aditiva 004.
- Adaptador Gemini no backend, modo de perguntas gerais e limites de uso.
- Documentação, política de privacidade, scripts de configuração, testes e modelo de dados atualizados.

## Impact

Frontend Next, BFF, FastAPI, quatro tabelas novas e configuração privada. Nenhuma implantação ou migração real faz parte da implementação local sem aprovação. Google Cloud, OAuth e Gemini reais dependem de credenciais e requisitos do provedor.
