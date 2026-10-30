---
name: ux-design
description: "Ativar ao construir, alterar ou revisar uma tela, página, painel ou componente visual: escolher o perfil de estilo, planejar tokens antes do código, revisar contra os traços de 'cara de IA' e a lente de interface, e rodar o gate de UX antes de aprovar. NÃO ativar para especificar UX do zero (isso é a especificação DESIGN.md e EXPERIENCE.md do processo de produto) nem para gráfico isolado (skill de visualização de dados)."
version: 1.0.0
source: "decisão do dono, 30/10/2026 (opção A da pesquisa E:\\_GIT PROJECTS\\pesquisas\\2026-10-30_skills-design-ux, v3): absorver revisão e gate de UX no framework; perfis corporativo, minimalista, moderno, arrojado e outro"
last_review: 2026-10-30
role_order: null
consumes:
  - "DESIGN.md do projeto (perfil e exceções), quando existir"
  - "página renderizada (URL local) ou o código da tela"
produces:
  - "plano de tokens revisado antes do código"
  - "saída do gate: impeccable detect, auditoria de acessibilidade e tools/ux_gate.py"
pass_criteria: "PASS sse: (1) o perfil está declarado (DESIGN.md ou a resposta) e o plano de tokens (4 a 6 cores, tipos, layout com alinhamento, princípios) foi revisado contra o pedido antes do código; (2) a revisão percorreu os traços e a lente desta skill; (3) o gate rodou nas duas larguras e terminou sem achado, ou cada achado restante tem exceção declarada no DESIGN.md com motivo."
confidence_required: true
enforcement:
  ide: "gate por script: tools/ux_gate.py (exit 1 com achado) e impeccable detect (exit 2 com achado)"
  chat: "self-declared: sem navegador, o agente aplica perfil, plano e lente e declara o gate como não executado"
shared_refs:
  - _shared/output-format
  - _shared/confidence-classification
---

# ux-design — perfis, revisão e gate de interface

## Definições

- **Perfil:** direção de estilo do projeto, declarada no `DESIGN.md`; muda só os limites da tabela abaixo.
- **"Cara de IA":** escolha padrão que aparece em qualquer assunto, em vez de escolha feita para o pedido.
- **Gate:** medida por ferramenta que reprova a entrega; prosa desta skill orienta, o gate decide.

## Perfis (INFERIDO: propostos pela pesquisa, a calibrar com o dono)

| Perfil | Direção | Limite que muda |
|---|---|---|
| corporativo (padrão) | grade rígida, 1 família tipográfica, 1 cor de destaque, densidade média | — |
| minimalista | muito espaço, poucos elementos, sem decoração | legenda ≤ 8 palavras |
| moderno | tipografia de destaque, hierarquia forte, um único momento de movimento | — |
| arrojado | um elemento ousado, o resto disciplinado | como corporativo no script; o elemento ousado leva `data-ux-ignore` |
| outro | direção escrita pelo dono no `DESIGN.md` | como corporativo no script; regra própria do dono revisada à mão |

## Fluxo

1. **Perfil:** ler o `DESIGN.md`, se existir; sem ele, perguntar o perfil ou usar `corporativo` e declarar.
2. **Plano antes do código:** cores (4 a 6 hex nomeados), tipos e papéis, layout com regra de alinhamento
   (esquerda, centro, justificado) e princípios do que torna esta tela própria do assunto.
3. **Revisar o plano contra o pedido:** o que sairia igual em qualquer pedido parecido é trocado, dizendo o quê e por quê.
4. **Construir** com piso de qualidade: responsivo até 360 px, foco visível, movimento reduzido respeitado.
5. **Revisar** pelos traços, pela lente e pelas leis de texto abaixo.
6. **Gate** (seção final) nas larguras 360 e 1280; achado sem exceção declarada volta ao passo 4.

## Traços de "cara de IA" (evitar quando o pedido não os pede)

1. Fundo creme quente com serifa de alto contraste e destaque terracota.
2. Fundo quase preto com um único destaque verde-ácido ou vermelhão.
3. Layout de jornal: fios finos, cantos retos, colunas densas.
4. Kit de cartões: conteúdo picado em cartões iguais, mesmo raio e mesma sombra em tudo, degradê decorativo.
5. Moldura de modelo: rótulo em CAIXA ALTA espaçada sobre cada título, metadados com ponto médio, "PALAVRA — trecho",
   preto tingido no lugar de preto, fonte mono em rótulo pequeno, "→" no fim de link e botão.
6. Uma só palavra destacada no título; marcadores 01/02/03 em conteúdo que não é sequência; entrada animada em cada seção.

O pedido do dono sempre vence: se ele pede um desses estilos, segue-se o pedido. Gaste a ousadia num lugar só.

## Lente de revisão de interface

Teclado em todo fluxo e foco visível · alvo de toque ≥ 24 px (44 px no celular) · navegação é link, ação é botão,
nunca `div` clicável · ação destrutiva pede confirmação ou permite desfazer · botão em carregamento mantém o rótulo
e mostra indicador · todo estado desenhado (vazio, pouco, muito, erro) · nenhuma tela sem saída · status nunca só
por cor · ícone com rótulo acessível · números comparáveis com algarismos tabulares · alinhamento intencional com
grade, borda ou base · sem barra de rolagem inútil · layout aguenta texto curto, médio e muito longo.

## Leis de texto de interface

1. Botão, opção, aba e cabeçalho: até 3 palavras, sem parêntese explicativo. Título até 6 palavras ou um fato curto;
   legenda até 12 (título e legenda: INFERIDO, a calibrar com o dono).
2. Datas e anos calculados do período, nunca escritos fixos.
3. Sem jargão interno na tela; o detalhe vai para a dica ou some.
4. Botão diz o que acontece ("Salvar alterações", não "Enviar"); a ação mantém o nome no fluxo ("Publicar" → "Publicado").
5. Erro diz o que houve e como resolver, sem desculpas; tela vazia convida a agir.
6. Se quem fez não entende lendo, o texto sai.

## Gate

| # | Medida | Comando | Reprova quando |
|---|---|---|---|
| 1 | Traços de "cara de IA" | `IMPECCABLE_NO_TELEMETRY=1 npx impeccable@4.8.0 detect <URL> --json` (só `detect`; sem hooks; versão fixa, INFERIDO que o pacote npm siga a tag `cli-v4.8.0`) | exit 2 |
| 2 | Contraste, alvo, rótulos | `npx @axe-core/cli <URL>` (precisa de Chrome); AccessLint só como alternativa conferida antes (sem licença declarada: só usar, não copiar) | violação séria ou crítica |
| 3 | Caracteres por linha (≤ 80), desalinhamento de bloco alinhado à esquerda (2 a 16 px), rolagem em 360 e 1280 px, palavras por tipo, ação sem controle | `python tools/ux_gate.py --url <URL> --perfil <perfil>` | exit 1 |
| 4 | Captura nas duas larguras | Playwright, anexada à revisão visual | — |

Pré-teste (o navegador abre de fato): `python -c "from playwright.sync_api import sync_playwright as s; p=s().start(); p.chromium.launch().close(); p.stop()"`.
Sem Playwright: rodar a constante `EXTRATOR` de `tools/ux_gate.py` sem alteração no navegador, em 360 e 1280 px,
salvar `{"360": ..., "1280": ...}` e avaliar com `python tools/ux_gate.py --retrato <arquivo> --perfil <perfil>`.
Exceção legítima (tabela larga, bloco de código): atributo `data-ux-ignore` no elemento, com o motivo no
`DESIGN.md` ou em comentário junto do elemento. O medidor de alinhamento ignora texto centralizado e elemento inline.
Sem navegador ou Node na máquina: declarar o gate como **não executado** (o script sai 2), nunca como aprovado.

## Créditos e licenças

- Traços de "cara de IA", plano de tokens, revisão do plano e linha < 80 caracteres: adaptados da skill
  `frontend-design` de anthropics/skills (Apache License 2.0; https://github.com/anthropics/skills, acesso 30/10/2026).
  Texto traduzido e resumido; não é o original.
- Lente de revisão: seleção traduzida das Web Interface Guidelines de vercel-labs (MIT;
  https://github.com/vercel-labs/web-interface-guidelines, acesso 30/10/2026).
- Leis de texto: pesquisa do dono `E:\_GIT PROJECTS\pesquisas\2026-10-17_metodo-texto-de-interface`.
