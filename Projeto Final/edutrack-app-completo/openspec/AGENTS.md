# Guia OpenSpec do EduTrack

Guia complementar criado para a avaliação; configuração atual em config.yaml e regras do projeto em ../AGENTS.md.
1. Analise a arquitetura e a spec existente.
2. Proponha a mudança em changes/<nome>/proposal.md, design.md, tasks.md e specs/<capacidade>/spec.md.
3. Em deltas use ADDED, MODIFIED ou REMOVED Requirements. Em specs consolidadas use Requirements.
4. Todo requisito deve usar SHALL/MUST e incluir cenário WHEN/THEN. Recursos privados precisam de caso de acesso negado.
5. Valide, implemente, teste e registre resultados. Não marque publicação só porque o build passou.
6. Arquive depois de sincronizar a spec, sem encerrar pendências não executadas.

Comandos na pasta do frontend:
```powershell
npm run openspec -- --version
npm run openspec:validate
npm run openspec -- list
```
