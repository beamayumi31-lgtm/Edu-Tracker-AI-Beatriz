# Desempenho do EduTrack

## Alterações

- A página inicial tem um componente próprio e não importa o painel acadêmico completo.
- Tutorial e editor são módulos carregados sob demanda, com indicação de carregamento e cancelamento.
- A ilustração do dashboard usa WebP nos tamanhos 620 e 1240 pixels, com `sizes` responsivo. O PNG original foi preservado.
- A fonte monoespaçada, que não era utilizada na interface, deixou de ser pré-carregada.
- O Tailwind procura classes somente em `app/`, excluindo documentação e instruções de ferramentas da geração de estilos.
- As telas acadêmicas com dados locais usam a History API integrada ao Next/Vinext. Login, cadastro, administração, URLs externas e API continuam pelo roteador normal. O acesso direto às URLs continua disponível no servidor.
- Os totais do cronômetro são recalculados somente quando as sessões mudam ou o dia vira, não a cada segundo.
- Efeitos de desfoque em elementos fixos foram reduzidos em telas pequenas e seções do dashboard abaixo da dobra usam renderização adiada.
- `public/_headers` solicita cache prolongado apenas para arquivos com nomes versionados. HTML e API não recebem essa regra. É necessário conferir os cabeçalhos reais após cada publicação, pois o provedor pode aplicar suas próprias regras.

## Limites

Medição de 08/09/2026: a soma dos tamanhos gzip dos arquivos iniciais (JS, CSS e fontes pré-carregadas) da página inicial passou de 227.224 para 164.432 bytes, redução de aproximadamente 28%. A ilustração passou de 1.073.212 bytes (PNG) para 123.860 bytes (WebP grande) ou 47.806 bytes (WebP pequeno). Esses números descrevem os arquivos, não um percentual de melhora no tempo de carregamento.

A navegação local é apropriada ao protótipo atual, cujos dados acadêmicos ficam no navegador. Quando a API de autenticação e dados for conectada, cada tela deverá consultar e validar os dados autorizados; não se deve usar navegação local para contornar verificações do servidor.

Os tempos HTTP incluem rede e hospedagem e variam entre medições. Tamanho de arquivos e tempo de resposta não equivalem a uma medição de interação ou renderização no navegador.

## Referências

- [Navegação no Next.js](https://nextjs.org/docs/app/getting-started/linking-and-navigating)
- [Detecção de classes no Tailwind](https://tailwindcss.com/docs/detecting-classes-in-source-files)
- [Cabeçalhos de arquivos estáticos no Cloudflare Workers](https://developers.cloudflare.com/workers/static-assets/headers/)
