# Especificação da Edu IA

## Purpose

Definir o comportamento da assistente de estudos e sua integração segura com o contexto acadêmico.

## Requirements

### Requirement: Compatibilidade do provedor com o público

O sistema SHALL manter Gemini indisponível quando o público configurado incluir adolescentes, mesmo com chave, modelo, serviço pago e declaração individual de maioridade. O público aprovado do EduTrack é 13+; outro provedor exige preparação e revisão das proteções antes da ativação.

#### Scenario: Gemini habilitado acidentalmente para público adolescente

- **WHEN** o público é `includes_teens` e uma chamada generativa tenta usar Gemini
- **THEN** a API recusa a chamada antes do provedor e preserva o planejador local

### Requirement: Gemini configurável e privacidade por modo

O sistema SHALL manter chave e modelo no servidor, permitir selecionar Gemini ou OpenAI e preservar o planejador local sem chave.

#### Scenario: Gemini gratuito

- **WHEN** o Gemini está configurado sem liberação explícita para contexto acadêmico
- **THEN** o chat envia apenas as mensagens autorizadas, sem ferramentas ou consulta automática ao contexto do aluno

#### Scenario: Conteúdo Classroom

- **WHEN** uma consulta generativa usa contexto acadêmico
- **THEN** disciplinas e tarefas de origem Classroom são excluídas, inclusive após desconexão

#### Scenario: Configuração incompleta ou cota

- **WHEN** a chave/modelo está ausente ou o provedor falha
- **THEN** a interface informa o estado real, permite revisar a pergunta e mantém o planejador local disponível

### Requirement: Conversa contextual

A Edu IA SHALL responder perguntas de estudo usando apenas o contexto acadêmico autorizado do usuário.

#### Scenario: Pergunta sobre disciplina

- **WHEN** o estudante seleciona uma disciplina e envia uma pergunta
- **THEN** a API inclui somente dados necessários dessa conta e retorna uma resposta contextual

### Requirement: Transparência da integração

A interface SHALL informar quando a IA real estiver conectada e quando estiver usando orientação local de demonstração.

#### Scenario: API indisponível

- **WHEN** a integração externa não estiver configurada ou falhar
- **THEN** a interface apresenta o estado correto sem fingir que houve uma resposta da IA remota

### Requirement: Limites e segurança

A API SHALL limitar frequência e tamanho das mensagens, SHALL proteger dados pessoais e SHALL manter o aviso de que respostas podem conter erros.

#### Scenario: Solicitação acima do limite

- **WHEN** uma conta excede o limite definido para mensagens
- **THEN** a API recusa temporariamente a solicitação com uma orientação clara para tentar depois


### Requirement: Experiência de conversa acessível

A interface SHALL separar conversa generativa e planejamento local, apresentar mensagens legíveis sem executar HTML, permitir copiar respostas e exportar a conversa em texto, e manter o rascunho quando uma solicitação falhar ou sua espera for interrompida.

#### Scenario: Chat não configurado

- **WHEN** o serviço informa que a IA não está configurada
- **THEN** a interface permite preparar o rascunho, bloqueia o envio e oferece o planejador local sem inventar respostas

#### Scenario: Resposta com código

- **WHEN** a resposta contém blocos de código ou texto com marcação HTML
- **THEN** os blocos são apresentados de forma legível e o HTML permanece texto, sem execução

#### Scenario: Continuação de conversa longa

- **WHEN** o estudante envia uma nova pergunta após várias trocas
- **THEN** o cliente transmite no máximo quatro pares anteriores e a pergunta atual, limitando cada mensagem a dois mil caracteres sem alterar o histórico visível

#### Scenario: Interrupção da espera

- **WHEN** o estudante interrompe a espera de uma resposta
- **THEN** a interface descarta a resposta tardia, preserva a pergunta e informa que uma solicitação já recebida ainda pode ser processada pelo provedor
