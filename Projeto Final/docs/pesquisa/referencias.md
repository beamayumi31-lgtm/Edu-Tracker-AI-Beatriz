# Referências de design e arquitetura

Pesquisa realizada em 17/11/2026 para a tarefa 06 de Innovation Lab. As páginas públicas foram consultadas no Chrome. Os dois arquivos foram duplicados nos rascunhos da conta conectada; as páginas e camadas das cópias foram consultadas pelo Figma MCP.

## 1. Dashboard for E-Learning

- Autor: Ivan Fadila.
- [Cópia editável na conta do aluno](https://www.figma.com/design/eynzTOKZjTZxRZ3PxtaLjM/Dashboard-for-E-Learning--Community-).
- Estrutura inspecionada: páginas Cover, Page e Thanks; frame Main de 1440 × 900, Sidebar, Nav Wrap, RightSidebar e cartões de atividade. O ícone BookOpenOutline (nó 1:149) foi exportado em SVG para a evidência acadêmica, com atribuição.
- [Arquivo no Figma Community](https://www.figma.com/community/file/991159230399487066/dashboard-for-e-learning).
- Recurso gratuito identificado pela tag `freebie`, botão “Abrir no Figma” e licença CC BY 4.0 exibida na página.
- Aplicação ao EduTrack: estudar a separação entre navegação, visão geral e conteúdo das disciplinas. Esse padrão ajuda a tornar visível o próximo passo do aluno sem colocar todas as informações no mesmo bloco.
- Decisão: manter a marca e as telas existentes do EduTrack; usar o template como referência de hierarquia, não como origem retrospectiva do código já construído.

## 2. Obra shadcn ui kit - Community edition

- Autor: Obra Studio.
- [Cópia editável na conta do aluno](https://www.figma.com/design/bIblNlbMMPdkQpioJkikqm/shadcn-ui-kit-community-edition--Community-).
- Estrutura inspecionada: Colors, Typography, Icons, Shadows e páginas por componente, incluindo Button, Card, Input, Dialog e Table. Páginas marcadas PRO ONLY foram identificadas como fora do material gratuito utilizado.
- [Arquivo no Figma Community](https://www.figma.com/community/file/1514746685758799870/shadcn-ui-kit-community-edition).
- A página descreve uma edição gratuita com componentes reutilizáveis, variáveis de tema, cores Tailwind e ícones Lucide. A edição atual gratuita contém modo claro; o modo escuro é anunciado em ofertas separadas. Nenhuma compra foi feita.
- Aplicação ao EduTrack: estudar estados de botões, formulários e variáveis semânticas para evitar regras visuais duplicadas. O projeto já usa Lucide e variáveis CSS próprias para claro/escuro.
- Decisão: reaproveitar a ideia de componentes pequenos e consistentes. Não trocar a biblioteca do projeto nem copiar recursos pagos.

## Estrutura de backend: adaptação autorizada

O projeto utiliza SQL Server e Python/FastAPI por decisão do aluno, confirmada em 17/11/2026. A pesquisa de Xano Marketplace é substituída pela leitura dos contratos e padrões equivalentes:

- [FastAPI: segurança e JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/): referência para autorização no servidor; o EduTrack mantém sua implementação própria com Argon2, JWT e isolamento por usuário.
- [SQLAlchemy: consultas ORM](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html): consultas parametrizadas e relacionamentos, utilizados no CRUD e na busca.
- [ReportLab: Paragraph](https://docs.reportlab.com/reportlab/userguide/ch6_paragraphs/): texto com quebra automática de linhas, escapando marcação fornecida pelo aluno antes de compor o relatório.

## Reflexão para a atividade

A principal conclusão da pesquisa é que consistência vem da reutilização de componentes e de uma hierarquia clara de informações. No EduTrack, isso se traduz em navegação previsível, formulários com os mesmos estados de erro e ações visíveis para estudar, organizar atividades e acompanhar o progresso. O design serve à rotina do aluno; copiar um template inteiro não garante que o fluxo funcione.

## Limite da evidência

Pesquisa, duplicação e leitura da estrutura documentadas; não foram feitas assinaturas, compras ou instalações no Xano. Os links das cópias respeitam as permissões existentes do Figma; não foi concedido acesso público. A aceitação das adaptações SQL Server/FastAPI e React depende do professor. Nenhuma mensagem foi enviada ao Classroom.
