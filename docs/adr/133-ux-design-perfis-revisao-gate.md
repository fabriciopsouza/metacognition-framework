# ADR-133 — UX de interface: perfis, revisão e gate por medida

- **Status:** Aceito
- **Data:** 2026-10-30
- **Decisores:** dono (Fabricio), 30/10/2026: "A" (implementar no metacognition-framework as 3 camadas da pesquisa) e
  "a" (a sessão do orquestrador-multi-ia executa, como exceção à regra de cada sessão escrever só no próprio
  repositório). Autoria: Opus 5.5.
- **Relação:** pesquisa `E:\_GIT PROJECTS\pesquisas\2026-10-30_skills-design-ux\relatorio.md` (v3, QA aprovada com
  ressalvas corrigidas); reusa `2026-10-17_impeccable-design-agentes` e `2026-10-17_metodo-texto-de-interface`;
  emenda a skill `qa-critic` (checklist mínimo).

## Contexto

1. Telas entregues por agentes saíam com texto longo, desalinhamento, ação sem botão e "cara de IA". A especificação
   de UX (DESIGN.md e EXPERIENCE.md) já existe no processo de produto; faltava a revisão e o gate **depois** de construir.
2. Prosa sozinha não força: a pesquisa achou ferramentas determinísticas prontas (impeccable `detect`, axe-core,
   AccessLint) e 5 medidas que nenhuma cobre.

## Decisão

1. **Skill `ux-design`** (curta): 5 perfis (corporativo padrão, minimalista, moderno, arrojado, outro), plano de
   tokens revisado antes do código, traços de "cara de IA", lente de interface e leis de texto. Regra mensurável vai
   ao gate, não à prosa.
2. **Checklist do `qa-critic`:** item de UX; achado do gate sem exceção declarada, ou gate omitido sem declaração, é MÉDIA.
3. **Gate:** `impeccable detect` com versão fixa, telemetria desligada e sem hooks; axe-core (AccessLint só como
   alternativa conferida, sem cópia: sem licença declarada); `tools/ux_gate.py` para caracteres por linha (≤ 80),
   desalinhamento de irmãos em bloco alinhado à esquerda (2 a 16 px), rolagem horizontal em 360 e 1280 px, palavras por tipo de elemento e ação sem controle.
4. **Dependências** (novas, opcionais, só no momento do gate): Node para `npx`, Chrome ou Edge, Playwright para
   Python. Sem elas o gate é declarado **não executado**, nunca aprovado.

Régua §0 (ADR-007): enquadra em (c), destrava avaliação, porque converte em medida por script o que hoje só é opinião
do revisor; a skill fica curta e a regra mensurável sai da prosa.

## Limites declarados

1. Calibrado pelo dono em 30/10/2026 (emenda abaixo): perfis, limites de texto e o teto de 16 px que separa
   quase-alinhamento de recuo intencional (mantido).
2. INFERIDO: o pacote npm `impeccable@4.8.0` corresponde à tag `cli-v4.8.0`; conferir antes do primeiro uso.
3. O extrator Playwright de `tools/ux_gate.py` não roda nos canários (sem navegador na máquina de construção); o
   canário cobre a avaliação sobre o retrato, o caminho `--url` com o extrator substituído e a falha do Playwright
   (módulo falso): sai 2, "não executado". A função `centrado` do JavaScript é executada no Node pelo canário (SKIP
   declarado sem Node); a contagem de `linhas` e o extrator inteiro não têm teste automático; a versão anterior rodou
   num site real por outra sessão (30/10/2026: 211 elementos por largura, sem achado), via `--retrato`.
4. Textos de terceiros entram traduzidos e resumidos, com crédito e licença na própria skill (Apache-2.0 da Anthropic,
   MIT da Vercel).
5. O medidor de alinhamento compara só caixas de bloco que não estão centralizadas na área de conteúdo do pai (sem
   padding e borda); bloco de largura total continua medido. Redesenho em duas etapas: a r1 e a r2 acharam falso
   positivo em layout centralizado; a r3, falso negativo em pai com padding simétrico (3 reprovações seguidas na mesma
   família; seguida a recomendada da QA sem parar, pela regra D10 do dono). Limite conhecido: pai com barra de
   rolagem vertical (`overflow: auto`) desloca o centro em ~15 px e a caixa centralizada nele pode ser medida; todos os
   perfis usam os mesmos limites no script, e a diferença de estilo fica na revisão.
6. AccessLint: o CLI antigo está arquivado; axe-core é o caminho padrão (QA Sonnet r1, 30/10/2026).

## Emenda — calibração do dono (30/10/2026)

Decisão do dono, numa página interativa de calibração (texto colado: "manter os 5 perfis e incluir o corporativo 2;
título até 4; legenda até 8; botão até 2; linha até 80; desalinhamento: manter 2 a 16 px"; norte "COR FALA; FORMA FALA",
com *Storytelling with Data*). Fontes em `E:\_GIT PROJECTS\pesquisas\2026-10-30_skills-design-ux\calibracao-dono.md`.

1. Gate: botão, opção, aba e cabeçalho até 2 palavras (era 3, regra do dono de 17/10/2026); título até 4 (era 6);
   legenda até 8 (era 12); os limites valem em todos os perfis; perfil novo `corporativo-2`.
2. Skill `ux-design` 1.1.0: norte cor fala e forma fala, polaridade declarada por métrica (sem ela, variação em cinza),
   cartão de indicador e paleta acessível conferida ("Color Blind" do Tableau: #1170aa e #c85200).
3. Efeito: telas já aprovadas com botão ou cabeçalho de 3 palavras, título de 5 ou 6 e legenda de 9 a 12 passam a ter
   achado na próxima rodada do gate; corrigir ou declarar exceção (`data-ux-ignore` com motivo).
4. A "cor fala" não é medida pelo script (depende da polaridade, que é dado da métrica): fica na revisão.

## Emenda — painel de indicadores e tamanho igual (30/10/2026)

Decisão do dono na página de calibração dos painéis (v2, aprovada): "não gosto quando elementos ficam de tamanhos
diferentes"; "ambas são muito boas e são opções válidas" (duas variantes do painel de visão geral). Fonte:
`E:\_GIT PROJECTS\pesquisas6-10-30_skills-design-ux\calibracao-dono.md`, seção "Calibração de painéis".

1. Skill `ux-design` 1.2.0, seção "Painel de indicadores": slots fixos do cartão, tamanho igual, meta abaixo do número,
   percentual antes do valor, comparação na linha da referência, gráfico embaixo com tipo pelo significado, nota curta
   e ação sem "→"; duas variantes da visão geral, a variante 1 como exceção declarada ao traço 5 (caixa alta).
2. Gate: `tools/ux_gate.py` acusa irmãos do mesmo tipo (mesma tag e primeira classe) com tamanho diferente acima de
   2 px. Item de `grid`: largura entre os da mesma posição de trilhas (`grid-column`), altura entre os lado a lado.
   Item de `flex`, com ou sem quebra: só altura entre os lado a lado. Gráfico (`svg`, `canvas` com classe e largura
   ≥ 60 px no grupo): largura e altura. Filhos de pais do mesmo grupo entram no mesmo grupo (o gráfico de cada cartão é
   comparado com os outros). Redesenho da QA Sonnet r1: a 1ª versão comparava a largura em `flex` com quebra (chip e
   link de navegação acusavam) e media ícone `svg` como gráfico.
3. Limites: tolerância de 2 px INFERIDA, a calibrar pelo dono; a primeira classe é tratada como o tipo (classe
   utilitária primeiro, como no Tailwind, agrupa errado); grade com colunas de tamanhos intencionais (`2fr 1fr`) e
   mesma classe acusa: exceção com `data-ux-ignore`; `img` não é medida (foto varia de proporção); cartões em `flex`
   com larguras diferentes não são acusados na largura, só na altura (débito declarado, preço de não acusar chip).
   **Não verificado:** o extrator não rodou num navegador nesta máquina (Playwright ausente); as funções `arranjo`,
   `trilhas` e `classe` rodam no Node pelo canário.
4. Efeito: painéis já aprovados com cartões ou gráficos de tamanhos diferentes passam a ter achado na próxima rodada.
5. Retrato salvo antes desta emenda (sem `tag`, `classe` e `em_grade`) é erro (sai 2): extrair de novo.
