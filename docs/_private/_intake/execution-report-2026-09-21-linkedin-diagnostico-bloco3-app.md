# Execution-report — bloco 3 "app v0.1 no modo gratuito + 10 rodadas de QA" (ADR-062 · privado)

> **Represamento encerrado** (23/09/2026): este arquivo ficou UNTRACKED de propósito entre 21 e
> 23/09/2026, porque a sessão de origem congelou commits no framework a pedido da sessão
> `metacognition-framework-7c` (bloco ADR-113/114/115 em revisão). **A condição de saída foi
> cumprida:** o bloco entrou na `main` em 22/09/2026 pelo PR #139 (commit `5305ae2`), e este
> arquivo foi commitado por caminho explícito na abertura de sessão de 23/09/2026 — exatamente
> como a nota original mandava. O texto abaixo é o do dia 21 e não foi alterado.

- **Sessão:** 21/09/2026 · **Repos:** `perfildoctor-app` (novo, privado) + `linkedin-diagnostico`
- **Pedido:** "o que conseguimos fazer de graça? dá para desenvolver assim, para testes?" → "siga";
  depois "tenho Gemini pago/créditos e Claude"; e "várias sessões, cada uma num repo — NÃO posso
  perder trabalhos nem misturá-los"
- **Modelo:** autor **Fable 5.1** (o dono perguntou; avaliei que o fechamento cabe em Opus e que
  Fable volta para o 2º QA final e o desenho do bloco 4) · QA adversarial **Sonnet isolado, 1
  crítico, 10 rodadas** (r1–r9 REPROVADO, r10 APROVADO-COM-RESSALVAS)
- **Decisão de desenho declarada:** diagnóstico gratuito **100% no navegador** — 6 regras
  determinísticas, sem LLM, sem rede (CA-12), sem score (CA-3); LLM (Gemini tier pago) só na
  reescrita paga (bloco 4)
- **Arquivos:** app 20 arquivos · **13 commits** na branch `fix/qa-r1` · 57 → **253 asserções**,
  5 → 14 perfis sintéticos, smoke da UI, `check_ca.py` (8 CA + segredos) · runbooks R-01/R-02 v2
- **Ambiente:** **não há Node** — testes rodam em Chrome headless (`--dump-dom`)

---

## Placar gate × achado (10 rodadas, só o critério 4 "experiências com resultado")

| Rodada | Achado (raiz) | Quem pegou | Gate que deveria ter pego |
|---|---|---|---|
| r1 | "Desde 2021" não era data → falso verde; 9/10 verbos comuns fora da lista → falso vermelho; CA-12 burlável | QA | nenhum — regras escritas sem oráculo negativo |
| r2 | as 3 "redes de segurança" da r1 criaram 3 regressões (marca em -i vira verbo; "10 - 5 dias" vira cargo; "Atendi 2019 clientes" vira data) | QA | nenhum — **cada mecanismo novo precisa de oráculo negativo** |
| r3 | classificação por **formato do número, sem âncora semântica** — mesmo bug com roupa nova | QA nomeou a raiz | nenhum |
| r4 | a âncora criou **ponto único de falha** (lista de exclusão compartilhada); gatilho = duração nativa do LinkedIn "· 3 anos 7 meses" | **meu probe** achou antes; QA confirmou | nenhum |
| r5 | cargo "por eliminação" nunca fecha → bullets viram cargo fantasma; qualificadores "Tempo integral/Presencial" | QA; **meu probe** achou os qualificadores | nenhum |
| r6 | layout nativo de 3 linhas deixava cargo órfão → **vermelho** onde é amarelo (recusou minha ressalva, com razão) | **meu probe** achou; QA mediu o dano | nenhum |
| r7 | puxar linhas para o título **move número** entre cargos → falso verde | QA | nenhum |
| r8 | órfão **espremido** engolido pela puxada → falso verde | QA | nenhum — meu oráculo de órfão só cobria o caso "no fim" |
| r9 | lista de palavras de cargo exclui profissões inteiras (Tesoureiro, Motorista…) → falso verde; ampliar engole bullets | QA mediu; **meu probe** achou o bullet | nenhum |
| r10 | 2 limites declarados confirmados; gatilho exige desvio do formato nativo | QA | — |

**Leitura:** 10 rodadas para um critério. O padrão das reprovações: **eu corrigia o caso e criava
um mecanismo novo sem oráculo negativo**; o crítico achava a regressão. O que virou o jogo
(r4→r10) foi trocar listas de exclusão por **definições positivas** (data = só vocabulário de
data; cargo = adjacência a linha com ano; número nunca migra; resultado só na descrição) e
declarar o limite do que sobrou. O probe no scratchpad, feito **enquanto** o crítico lia, achou
antes dele 4 dos 10 achados — vale como prática.

## Melhorias (aprendizado transferível)

1. **Oráculo dos dois lados antes de escrever a regra.** Positivos e negativos, incluindo o
   formato nativo da fonte (o que o LinkedIn exporta), não só o caso que motivou o fix.
2. **Lista fechada é dívida, não regra.** Verbos, unidades, qualificadores, palavras de cargo —
   todas falharam do mesmo jeito. Quando uma lista é inevitável (verbos), declarar o limite.
3. **Nunca mover conteúdo entre unidades de avaliação.** Adjacência serve para CONTAR, não para
   MOVER. Número que migra completa resultado que não existe.
4. **Ponto único de falha em critérios compartilhados.** Data e cargo dependiam da mesma
   exclusão; um furo derrubava os dois. Definições independentes e positivas.
5. **Probe próprio em paralelo ao crítico**, em cópia no scratchpad, sem tocar o arquivo que ele
   lê — e aplicar as duas coisas num commit só.
6. **Crítico único com contexto preservado** (SendMessage) por 10 rodadas: cada rodada reconfirmou
   as anteriores (13 cenários) e recusou ressalva prematura com dano medido. Custo: ~530k tokens
   do crítico. Valeu para o núcleo do produto; não para documentação.

## Boas práticas confirmadas

- Não há Node → Chrome headless como runner; `check_ca.py` mecaniza 8 critérios de aceite.
- Cada parada: commit por caminho explícito → push → PR → merge; framework congelado por respeito
  à sessão 7c (execution-report untracked).
- Regra do dono "não misturar trabalhos": esta sessão só escreveu em 2 repos próprios.

## Gaps declarados

- Ressalvas 1–3 do README do app (empresa em minúscula em órfão sem data; sigla à direita de
  " - "; verbo fora da lista) — **medir na QA amostral de uso real** (R-02 Parte A, Passo 5).
- Textos legais oficiais seguem INFERIDOS (fetch bloqueado).
- Deploy no Cloudflare Pages e execução dos runbooks: do dono.

## Próximo passo

Dono: R-02 Parte A (~25 min) → link `pages.dev` para 3 pessoas. Bloco 4 (reescrita paga):
desenho em Fable, implementação em Opus, QA Sonnet, 2º QA final Fable com autorização.
