---
name: ux-design
description: "Ativar ao construir, alterar ou revisar uma tela, página, painel ou componente visual: escolher o perfil de estilo, planejar tokens antes do código, revisar contra os traços de 'cara de IA' e a lente de interface, e rodar o gate de UX antes de aprovar. NÃO ativar para especificar UX do zero (isso é a especificação DESIGN.md e EXPERIENCE.md do processo de produto) nem para gráfico isolado (skill de visualização de dados)."
version: 1.1.0
source: "decisão do dono, 30/10/2026 (opção A da pesquisa E:\\_GIT PROJECTS\\pesquisas\\2026-10-30_skills-design-ux, v3): absorver revisão e gate de UX no framework; calibração do dono no mesmo dia (v4, calibracao-dono.md): perfis com corporativo 2, limites de texto, cor fala e forma fala"
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

- **Perfil:** direção de estilo do projeto, declarada no `DESIGN.md`; muda o estilo, não os limites de texto.
- **Polaridade:** se subir é bom ou ruim para a métrica; declarada por métrica, nunca deduzida.
- **"Cara de IA":** escolha padrão que aparece em qualquer assunto, em vez de escolha feita para o pedido.
- **Gate:** medida por ferramenta que reprova a entrega; prosa desta skill orienta, o gate decide.

## Norte: cor fala, forma fala (dono, 30/10/2026)

Princípios de *Storytelling with Data* (Knaflic, 2015) como norte; variação pequena é aceita com motivo declarado.

1. **Cor fala:** cinza é a base; cor só onde há significado (polaridade, destaque). Vermelho só para negativo ou meta
   não alcançada. Sem polaridade declarada, a variação fica em cinza. Cor nunca é o único sinal (seta ▲/▼ junto).
2. **Forma fala:** linha para tendência, barra para comparação, tracejado para meta ou previsão, seta para direção.
3. Contexto antes do visual (quem lê, o que decide); visual adequado (sem pizza 3D nem eixo duplo).
4. Sem poluição: tira grade, borda, legenda separada e casa decimal que não muda a decisão; rótulo direto no dado.
5. Um destaque por vez (cor, tamanho ou posição); o título diz a conclusão, não o assunto.
6. Sem espaço vazio nem distribuição ruim: o conteúdo ocupa a área do componente.

Paleta de polaridade: verde `#1f7a4d` bom e vermelho `#b3261e` ruim; acessível: azul `#1170aa` e laranja `#c85200`
(paleta "Color Blind" do Tableau). Texto colorido tem contraste ≥ 4,5:1 com o fundo (tom suave ou claro conforme o fundo).

## Perfis (calibrados pelo dono, 30/10/2026)

Todos usam os limites de texto e a polaridade acima.

| Perfil | Direção |
|---|---|
| corporativo (padrão) | grade rígida, 1 família sem serifa, densidade média (margem 16 px, 10 px entre itens) |
| corporativo 2 (`corporativo-2`) | igual ao corporativo; a ousadia num lugar só: a variação em faixa compacta na cor da polaridade, texto branco 11 px |
| minimalista | muito espaço, poucos elementos, sem decoração; complemento em tom suave da polaridade; sem gráfico |
| moderno | tipografia de destaque, hierarquia forte, um único momento de movimento |
| arrojado | um elemento ousado, o resto disciplinado; o elemento ousado leva a cor da polaridade |
| outro | direção escrita pelo dono no `DESIGN.md`; regra própria revisada à mão |

## Cartão de indicador

Especificação do dono e versão 7 da página de calibração, aprovada em 30/10/2026 (registro no arquivo de calibração).
Título 14 px semibold · número 38 px bold, algarismos tabulares · complemento 12 px na cor da polaridade, com seta,
comparando com a base que casa com o período mostrado · ação ("Ver pedidos") à direita na linha do complemento, 11 px,
texto simples ou botão discreto · minigráfico opcional (sem, linha, barras ou cascata; cascata só no ano até a data) à
direita do número, até 180 px, último ponto na cor da polaridade, com link e com a ação visível em texto (dica não
aparece no toque).

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

1. Botão, opção, aba e cabeçalho: até 2 palavras, sem parêntese explicativo. Título até 4 palavras; legenda e nota
   até 8; linha até 80 caracteres (calibração do dono, 30/10/2026).
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
Sem Playwright: invocar no navegador a função da constante `EXTRATOR` de `tools/ux_gate.py`, sem alteração, como
`(EXTRATOR)()`, em 360 e 1280 px,
salvar `{"360": ..., "1280": ...}` e avaliar com `python tools/ux_gate.py --retrato <arquivo> --perfil <perfil>`.
Exceção legítima (tabela larga, bloco de código): atributo `data-ux-ignore` no elemento, com o motivo no
`DESIGN.md` ou em comentário junto do elemento. O medidor de alinhamento ignora elemento inline e caixa centralizada na área de conteúdo do pai (flex,
`margin: auto`); bloco de largura total dentro de pai com padding continua medido.
Sem navegador ou Node na máquina: declarar o gate como **não executado** (o script sai 2), nunca como aprovado.

## Créditos e licenças

- Traços de "cara de IA", plano de tokens, revisão do plano e linha < 80 caracteres: adaptados da skill
  `frontend-design` de anthropics/skills (Apache License 2.0; https://github.com/anthropics/skills, acesso 30/10/2026).
  Texto traduzido e resumido; não é o original.
- Lente de revisão: seleção traduzida das Web Interface Guidelines de vercel-labs (MIT;
  https://github.com/vercel-labs/web-interface-guidelines, acesso 30/10/2026).
- Leis de texto: pesquisa do dono `E:\_GIT PROJECTS\pesquisas\2026-10-17_metodo-texto-de-interface`; limites
  calibrados pelo dono em `E:\_GIT PROJECTS\pesquisas\2026-10-30_skills-design-ux\calibracao-dono.md`.
- Norte "cor fala, forma fala": dono; princípios das 6 lições de Cole Nussbaumer Knaflic, *Storytelling with Data*,
  Wiley, 2015 (resumo conferido em fontes de terceiros, acesso 30/10/2026; fontes no arquivo de calibração).
- Paleta acessível: "Color Blind" do Tableau, conferida nos dados do ggthemes (acesso 30/10/2026).
