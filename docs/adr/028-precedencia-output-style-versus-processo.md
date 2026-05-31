# ADR 028 — Output-style nunca suplanta processo (precedência persona × roteamento/gates)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: entrada determinística (v1.22.0) · Tipo: **edição de existente** (1 nível na precedência do `metacognition-core` — régua §0: funde regra na fonte única, não cria arquivo de regra novo)
- Relaciona: ADR-027 (route-gate mecaniza o lembrete de rota), `_shared/metacognition-core` §Precedência de instruções, `_shared/anti-hallucination`, CLAUDE.md §Regras invioláveis.

## Contexto

Mesma falha-raiz do relato `RELATO-FRAMEWORK-autorrevisao.md` (sessão AIVI, 2026-05-31): o agente
executou um cálculo regulado/financeiro **sem rotear**. Além do roteamento ser prosa (tratado no
ADR-027), havia uma **segunda força**: o output-style injetado no SessionStart (ex.: `learning`,
`explanatory`) instala uma **persona** com instruções fortes de *como* responder ("ensine", "vá
direto ao ponto", "produza insights"). Essas instruções **competem** com o processo do framework
(declarar rota, classificar confiança, file-first, acionar gates) e, sem uma regra de precedência
explícita, a persona — que chega volumosa e imperativa no início do contexto — vence o roteamento. [CONFIRMADO por inspeção do relato]

O núcleo já tinha uma lista de precedência (`metacognition-core` §Precedência), mas ela **não
nomeava output-style** — deixava ambíguo onde uma persona injetada se encaixa.

## Decisão (1 frase ativa)

Adicionar à precedência do `metacognition-core` o **nível 7 — output-style/persona**, declarando que
ela governa **tom e formato** (entra no nível dos templates de formato) e **NUNCA suplanta** o nível 2
(regras invioláveis: anti-rename, file-first, classificação) nem o nível 5 (roteamento/gates): se a
persona empurra para "resolver/ensinar direto" e isso colide com declarar a rota ou rodar um gate,
**o processo vence**.

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** A ambiguidade persiste; a persona continua podendo atropelar o processo. **Rejeitada — é metade do gap do incidente.**
2. **Criar um arquivo de regra novo (`.agent/rules/NN-output-style.md`).** Contras: viola a régua §0 (adição pura quando a fonte única — `metacognition-core` §Precedência — já é o lugar canônico de precedência); fragmenta a regra. **Rejeitada.**
3. **Resolver só com o route-gate (ADR-027).** O route-gate *lembra* ("output-style governa tom, não processo"), mas lembrete em `additionalContext` é mecanismo de *runtime*; falta a **regra normativa** que ele encarna. Sem a cláusula no núcleo, o lembrete fica órfão de fonte. **Rejeitada como suficiente** — ADR-027 e ADR-028 são complementares (mecanismo + norma).
4. **Editar a fonte única — nível 7 na precedência (ESCOLHIDA).** Prós: net-gain (funde na lista existente, zero arquivo novo); dá lar normativo ao lembrete do route-gate; domínio-agnóstico. Contras: nenhum material.

## Consequências

**Positivas:** precedência deixa de ser ambígua — qualquer output-style futuro (concise, etc.) já está
coberto; o lembrete do route-gate (ADR-027) passa a citar uma regra real; reforça que persona ≠ processo.
**Negativas:** nenhuma material (é uma linha de regra + nota). **Riscos:** se um output-style futuro
trouxer instrução que tente desabilitar gates explicitamente, a cláusula resolve a favor do processo —
re-validar se a Anthropic introduzir um style que mude semântica de execução (improvável). [DESCONHECIDO não-bloqueante]

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.22.0-entrada-deterministica` · `2026-05-31` · grep `ADR-028` em `_shared/metacognition-core/SKILL.md`
- Artefato: `_shared/metacognition-core/SKILL.md` §Precedência de instruções — **nível 7** + nota inviolável "Output-style ≠ processo"; frontmatter `version: 1.2.0`. O route-gate (ADR-027) já injeta o lembrete operacional correspondente.
