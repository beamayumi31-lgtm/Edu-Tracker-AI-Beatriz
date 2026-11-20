# EduTrack para público a partir de 13 anos

Decisão do responsável em 10/11/2026: atender pessoas a partir de 13 anos, incluindo adolescentes de 13 a 17. Este documento registra a preparação; **não declara a adaptação concluída nem autoriza chamadas pagas**.

## Situação técnica

- O sistema existente mantém dados acadêmicos separados por titular, consentimento individual para Classroom, tokens cifrados, prévia antes da importação e planejador local sem envio a IA externa.
- Gemini está desativado na configuração real. A chave criada foi revogada sem uso. O bloqueio adicional local em `Settings.ai_configured` exige público `adults_only` para Gemini; o padrão é `includes_teens`. Não alterar essa classificação para liberar o provedor no EduTrack atual.
- A autodeclaração de 18 anos da tela antiga não torna Gemini compatível com um aplicativo destinado a adolescentes. O bloqueio vale também para Gemini pago.
- Já existe adaptador OpenAI, mas existência de código não comprova adequação para adolescentes, saldo, credencial válida ou ativação. Não houve contratação ou envio de dados a outro provedor.
- A proteção adicional e este documento ainda não foram publicados na VPS. O servidor publicado permanece sem credenciais de IA.

## Preparação necessária antes da abertura para adolescentes

1. Definir e implementar a aferição de idade apropriada ao risco, com coleta mínima. Não confundir CPF matematicamente válido, e-mail verificado ou checkbox com comprovação de idade. Definir o tratamento das contas existentes e de usuários abaixo de 13 anos.
2. Revisar a base legal, o melhor interesse dos adolescentes, a participação dos responsáveis quando aplicável e os requisitos brasileiros vigentes. Validar esses pontos com o responsável pelo serviço antes de coletar novos dados. A idade mínima comercial de 13 anos não substitui essa avaliação.
3. Adaptar cadastro, avisos de privacidade e apresentação da Edu IA em linguagem clara. Explicar dados enviados, provedor, retenção, direitos e como solicitar ajuda ou remoção.
4. Escolher provedor compatível, aprovar custos/limites e configurar credencial privada. A OpenAI publica orientações para aplicações com menores; sua integração exige filtros adequados à idade, mecanismos de denúncia, monitoramento proporcional e encaminhamento de situações de risco.
5. Manter ferramentas da IA somente de leitura, limites por usuário, separação entre contas e exclusão de dados Classroom do contexto externo. Avaliar remoção de dados pessoais também de textos digitados e do contexto manual, sem prometer anonimização perfeita.
6. Implementar controles de entrada e saída, respostas de segurança e testes adversariais de conteúdo, privacidade e isolamento. Nunca usar dados reais de adolescentes nos testes de desenvolvimento.
7. Revisar a liberação de aplicativos pela instituição de ensino. Ativar Classroom API não contorna bloqueios administrativos de contas escolares.
8. Publicar somente após testes e autorização da atualização de produção, registrando quais medidas foram implementadas e suas limitações.

## Opções de IA

- **API compatível com adolescentes:** reutilizar o adaptador OpenAI após as adaptações, configuração e aprovação de custos. Não presumir uso gratuito ou que uma assinatura de chat já concede saldo de API.
- **Manter sem provedor externo por enquanto:** o planejador local continua organizando estudos; ele não é um chatbot generativo e não responde livremente a qualquer pergunta.
- **Modelo hospedado na própria infraestrutura:** exige avaliar licença, recursos computacionais, desempenho e moderação. Não está preparado nem tem gratuidade garantida na VPS atual.

## Fontes consultadas em 10/11/2026

- [Gemini API — restrições etárias](https://aistudio.google.com/docs/terms): o serviço não permite clientes destinados a, ou provavelmente acessados por, menores de 18 anos.
- [OpenAI — orientações para menores](https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance): proteção adequada à idade e requisitos adicionais para dados de crianças abaixo de 13 anos ou da idade de consentimento digital aplicável.
- [ANPD — tratamento de dados de crianças e adolescentes](https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-divulga-enunciado-sobre-o-tratamento-de-dados-pessoais-de-criancas-e-adolescentes): análise concreta do melhor interesse e das bases legais.
- [ANPD — ECA Digital](https://www.gov.br/anpd/pt-br/assuntos/noticias/semana-da-crianca-compromisso-da-anpd-com-a-protecao-de-criancas-e-adolescentes-no-ambiente-digital): necessidade de acompanhar a regulamentação aplicável ao ambiente digital.

As fontes não equivalem a uma certificação de conformidade do EduTrack. Verificar termos e regras vigentes novamente antes da liberação.
