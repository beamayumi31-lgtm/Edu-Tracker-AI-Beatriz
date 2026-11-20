# Floresta de foco e ofensiva

Os cartões de tempo e ofensiva do dashboard agora são botões para `/cronometro` e `/ofensiva`. As duas telas carregam sob demanda e mantêm os temas existentes.

## Regras

- Uma sessão de foco concluída gera uma árvore; sessões históricas também aparecem na coleção. Nenhuma pontuação ou árvore fictícia é inserida.
- O estudante escolhe 15, 25, 45 ou 60 minutos e pode vincular uma tarefa. A pausa de descanso tem 5 minutos e não gera árvore nem ofensiva.
- O botão de pausar congela o tempo; continuar preserva o progresso. Encerrar exige confirmação e não altera conquistas anteriores.
- A contagem usa um prazo absoluto, não incrementos de `setInterval`. Navegar entre telas não desmonta o controlador. Ao reabrir, o rascunho de sessão é retomado e uma conclusão atrasada recebe a data do término previsto.
- Uma sessão concluída por dia local mantém a ofensiva. Sessões adicionais não aumentam a quantidade de dias. Ontem continua válido até acabar o dia atual; um dia inteiro sem sessão reinicia a sequência. O recorde e os marcos históricos são preservados.
- Os marcos são 3, 7, 14, 30 e 100 dias; a floresta apresenta metas a cada 5 árvores.

## Limite do protótipo atual

Os indicadores são derivados das sessões já existentes no protótipo, que usa armazenamento no navegador. Esta alteração não implementa autenticação real, sincronização entre dispositivos ou um novo banco. O cronômetro é um rascunho temporário salvo junto ao estado existente. O site não bloqueia outros aplicativos, não observa a atividade fora dele e não comprova estudo real.

Para integração com a futura API/SQL Server, o servidor deverá validar a propriedade das sessões, garantir unicidade pelo ID e oferecer a fonte definitiva do histórico. Até lá, não usar a pontuação local para ranking competitivo. Abas simultâneas continuam sujeitas às limitações do armazenamento local preexistente.

## Verificação

`node --experimental-strip-types --test tests/*.test.mjs` verifica contagem única, lacunas, virada de ano, dados inválidos, prazo do cronômetro, pausa e restauração. `pnpm exec tsc --noEmit` verifica os contratos das telas. As regras visuais usam ícones Lucide; não há imagens pesadas adicionais nem cópias dos ativos de Forest ou Duolingo.
