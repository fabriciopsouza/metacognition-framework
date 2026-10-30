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

1. INFERIDO, a calibrar com o dono: os perfis, o limite de título (6 palavras) e de legenda (12; 8 no minimalista) e o
   teto de 16 px que separa quase-alinhamento de recuo intencional.
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
   família; seguida a recomendada da QA sem parar, pela regra D10 do dono); perfis `arrojado` e `outro` usam os limites do corporativo no
   script, e a diferença deles fica em `data-ux-ignore` e na revisão.
6. AccessLint: o CLI antigo está arquivado; axe-core é o caminho padrão (QA Sonnet r1, 30/10/2026).
