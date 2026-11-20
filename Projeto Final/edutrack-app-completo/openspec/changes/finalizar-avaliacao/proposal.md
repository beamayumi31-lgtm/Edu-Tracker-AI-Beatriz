## Why

A avaliação exige demonstrar login, recuperação de senha, cadastro, IA, relatórios, disciplinas, tarefas, banco/modelo e código com OpenSpec. A auditoria identificou recuperação apenas demonstrativa, relatório sem filtro semanal e documentação desatualizada.

## What Changes

- Recuperação real por SendGrid com token temporário de uso único e invalidação das sessões antigas.
- Relatórios com semana local, navegação, tabela acessível e CSV.
- DER, dicionário e SQL para banco vazio gerados do modelo; roteiro de apresentação e pacote de código organizado.
- Distribuição Node do frontend para Hostinger, preservando a execução local existente.
- Integração da Edu IA preparada para configuração posterior da chave, conforme decisão do usuário.

## Impact

- Migração aditiva 003 em SQL Server; nenhuma conta ou registro acadêmico removido.
- Sessões existentes precisam de novo login devido à assinatura vinculada ao hash da senha.
- API, SMTP e IA exigem configuração privada. Não publicar segredos ou dados reais no GitHub.
- Deploy, DNS, certificados e operações da VPS exigem aprovação concreta após inspeção do plano.
- SMS, cobrança, Flutter e administração irrestrita de alunos continuam fora desta entrega.
