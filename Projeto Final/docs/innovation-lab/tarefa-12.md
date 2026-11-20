# Tarefa 12 — Cálculo de progresso em Python

EduTrack · Innovation Lab · Faculdade Impacta · 17/11/2026

**Situação:** Implementado e testado.

## Entrega e explicação

scripts/calculate_progress.py executa de forma independente, sem banco nem rede. A regra compartilhada está em edutrack/progress.py e também é usada pelo dashboard e pelo PDF.

Exemplo: `.venv\Scripts\python.exe scripts/calculate_progress.py --completed 3 --total 4` retorna `{"percentage": 75}`. Com zero concluídas e zero total, retorna 0. Valores negativos, não inteiros ou concluídas acima do total são recusados. O arredondamento é para o inteiro mais próximo, com metade para cima.

O progresso agregado usa a soma das tarefas elegíveis, não a média simples dos percentuais das disciplinas. Isso evita distorções quando as disciplinas têm tamanhos diferentes.

## Fontes e evidências

- [VS Code: versões e cálculo executados](evidencias/01-03-vscode-versoes.png)
- [Saída textual da verificação](evidencias/versoes-e-calculo.txt)

- [edutrack-api/scripts/calculate_progress.py](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-api/scripts/calculate_progress.py)
- [edutrack-api/edutrack/progress.py](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-api/edutrack/progress.py)

Consulte também o índice, a matriz de adaptações e os arquivos em `evidencias/` deste pacote.
