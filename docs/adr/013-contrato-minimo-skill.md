# ADR 013 — Contrato mínimo de interface para roles/skills

- Status: Aceito
- Data: 2026-05-30 · Decisores: dono (briefing v1.14.x) + squad (autônomo)
- Onda: 0 (fundação de schema) · Pesquisa: **P3** · Tipo: **EMENDA** (Princípio 5 — SSoT)
- Série: v1.14.x "da prosa ao mecanismo" (importa runtime do JARVIS filtrado pela régua §0)

## Contexto

As 7 skills de processo (`pmo, discovery, architect, developer, qa-critic, docops, explorer`) e o
núcleo `_shared/` já seguem convenções de frontmatter "por boa vontade" (`name`, `description`,
`version`, `source`, `last_review`) — mas nada **verifica** essas convenções, e a fronteira de
entrada/saída de cada role (o que consome, o que produz, qual o critério de PASS) vive em prosa no
corpo do SKILL.md, não declarada. P3 mostra que a ausência de contrato verificável é causa-raiz
documentada de falha multi-agente (GitHub Blog 2026; CrewAI: backstories/fronteiras claras reduzem
alucinação). Os frameworks maduros (Anthropic SKILL.md, CrewAI, OpenAI Agents SDK, MS Agent
Framework, LangGraph) convergem num contrato mínimo: **identidade + fronteira I/O + ganchos
transversais**, poucos obrigatórios, resto opcional.

P1/P6/P7 (ondas seguintes) precisam de campos declaráveis (`enforcement`, `classe`). Fixar o schema
**antes** evita retrabalho — daí esta ser a Onda 0 (DOSSIÊ §3).

**Régua §0 (Princípio 10):** APROVADO como **otimização**, não adição pura — funde convenções
dispersas das 7 skills num schema único (reforça P5), troca revisão manual por gate automatizável,
não adiciona runtime/dependência/papel. A lição JARVIS (contrato com 5/8 camadas vazias = andaime
morto) é o teto: **nenhum campo obrigatório sem verificação que o consuma**.

## Decisão (1 frase ativa)

Formalizar um **contrato mínimo de skill** — 8 campos obrigatórios (identidade + fronteira I/O +
ganchos transversais) + 5 opcionais — descrito em `tools/framework-schema.json`, verificado por
`tools/validate_skills.py` (gate de CI no IDE) e por auto-check de 1 linha no chat, aplicado às
7 skills de processo (`_template` é molde inerte, excluído do gate; não é um role ativo).

### Contrato (frontmatter)

**Obrigatórios (8):**
| Campo | Tipo | Regra |
|---|---|---|
| `name` | string | `^[a-z0-9-]+$`, ≤64, = nome da pasta |
| `description` | string | ≤1024, não-vazia, sem tags XML |
| `role_order` | int\|null | posição PMO→release (0=pmo…6=release); `null` p/ skill não-sequencial (_shared, explorer auxiliar) |
| `consumes` | lista | pré-condição: artefatos/contexto de entrada (pode ser `[]` p/ entry-point) |
| `produces` | lista | pós-condição: artefato-gate de saída |
| `pass_criteria` | string | critério BINÁRIO de PASS (sem zona cinza) |
| `confidence_required` | bool | a skill classifica confiança? (liga P1) |
| `shared_refs` | lista | regras de `_shared/` que a skill carrega |

**Opcionais (5, declarar só quando usados):** `version` (SemVer), `allowed-tools`, `rewind_target`
(P13), `enforcement` (`{ide, chat}` — P1/ADR-015), `classe` (`salva-vidas|operacional|andaime` — P7/ADR-017).

> Os campos legados `source`, `last_review` e `metadata` permanecem **permitidos** (não quebram), mas
> não são obrigatórios — evita rewrite gratuito das 7 skills e tolera o shape de `_shared/` (régua §0).
> Total no schema: **5 opcionais de contrato + 3 legados permitidos = 8 propriedades opcionais**; só os
> 5 de contrato contam como "opcionais do contrato" (cada um com gate que o consome).

### Verificação por ambiente (mesma regra, mecanismo diferente — sem prometer paridade)
- **IDE/SDK:** `tools/validate_skills.py` lê `framework-schema.json`, valida frontmatter de toda
  skill, emite PASS/FAIL, exit≠0 em falha → gate de CI/pré-merge. Precedente: `quick_validate.py` (Anthropic skill-creator).
- **Chat web:** auto-check de 1 linha ao ativar a skill (consumes/produces/pass_criteria/confidence
  declarados) — higiene declarada, **não** gate. Texto no `_shared/output-format`.

## Alternativas consideradas

> Verificação efetiva (qa-critic round 1): o validador enforça `minimum` (role_order≥0),
> `name`=nome da pasta, existência dos paths de `shared_refs`, ausência de tags XML em `description`,
> e `additionalProperties:false` em sub-esquemas — fechando o gap "schema declara, gate não verifica"
> (REQ-6). Sem isso, o contrato seria andaime parcial (lição JARVIS).

1. **Não fazer (status quo).** Prós: zero esforço. Contras: convenções seguem não-verificáveis;
   P1/P6/P7 reespecificariam schema ad-hoc (retrabalho). Rejeitada — gatilho de ≥2 implementações já
   atingido (7 skills).
2. **Contrato gordo (estilo camadas JARVIS / CrewAI completo: `goal`+`backstory`+`tags`+`author`).**
   Prós: "completo". Contras: campos que nenhuma skill preenche de verdade = andaime morto; força
   preenchimento → induz alucinação (colide com P1). Rejeitada pela régua §0.
3. **Contrato mínimo verificável (ESCOLHIDA).** 8 obrigatórios + 5 opcionais de contrato, cada um com
   gate que o consome. Prós: otimiza, SSoT, automatizável. Contras: exige o validador (pago pelo ganho de CI).

## Consequências

**Positivas:** fronteira I/O explícita; QA e revisão humana ganham critério objetivo; P1/P6/P7
herdam campos prontos; auditável (regulado).
**Negativas:** +1 schema + 1 validador (~150 linhas) para manter; frontmatter das skills cresce ~8 linhas cada.
**Riscos:** (a) campos `consumes/produces/pass_criteria` são extensão não-padrão do Agent Skills —
clientes "puros" podem ignorá-los; **mitigação:** são aditivos, loaders conformes ignoram chaves
extras (a confirmar empiricamente — **[DESCONHECIDO]**, P3 §7). (b) Aceitação regulatória do
schema+log de CI como evidência de validação ALCOA+ **[DESCONHECIDO]** — não bloqueante fora de GxP.

## Implementação (ponteiro após aceito)
- Ponteiro: branch `feat/v1.14.0-contrato-minimo-skill` · data `2026-05-30` · grep `framework-schema|validate_skills|role_order`
- Artefatos: `tools/framework-schema.json`, `tools/validate_skills.py`, `docs/specs/v1.14.0-contrato-minimo/{requirements,validation}.md`, frontmatter de 7 skills + `_template`.
- Verificação: `python tools/validate_skills.py` → todas PASS (critério de aceite da spec).
