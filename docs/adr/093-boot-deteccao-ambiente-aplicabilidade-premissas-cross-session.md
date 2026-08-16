# ADR 093 — Detecção de ambiente no boot + checagem de aplicabilidade das premissas (cross-session)

- Status: **Aceito** (2026-06-22 — ratificado pelo dono via popup de escopo "ambos + `.agent/environment.json`"; pré-gate de código: qa-critic heterogêneo) · Data: 2026-06-22 · Decisores: dono (pedido explícito, sessão cross-app vinda de vibra-kb-rag 2026-06-22b) + squad (architect)
- Onda: falha de campo real — premissa de ambiente ESTALE quebrou file-first (briefing/ADR dizia "CORPUS_ROOT `F:\` NÃO existe neste PC" → agente hesitou em ler `F:\`, mas `F:\` EXISTIA na máquina; dono confirmou) · Tipo: **enhancement de boot/SessionStart** + nova REGRA transversal em `_shared/`
- Relaciona: ADR-061 (`boot_check.py` — host do novo gate), ADR-019/060 (sync de boot resiliente a EDR — mesma classe de "estado real vs. retrato congelado"), ADR-069 (hub cross-IA — sink do registro), ADR-020 (agnosticismo do núcleo — premissas são DADO, não código), confidence-classification + traceability (`_shared/` — eixo CONFIRMADO/INFERIDO e file-first)

## Contexto

Premissas de **ambiente** declaradas em briefings/ADRs/memória — paths (`F:\`, `CORPUS_ROOT`), drives, hooks vetados por EDR — são tratadas pelo agente como **CONFIRMADO-para-sempre**. Mas elas são, na verdade, **INFERÊNCIA presa a uma máquina num momento**: trocam quando a sessão muda de PC, quando um drive é montado, ou quando a config de EDR muda. Sem re-verificação no boot, o agente opera sob **restrição FALSA**.

Falha real desta onda (sessão `2026-06-22b`, app vibra-kb-rag): o briefing/ADR afirmava que `CORPUS_ROOT F:\` **não existia** naquele PC. O agente **hesitou em ler arquivos em `F:\`** — porém `F:\` **existia** (dono confirmou). A prosa estale **suplantou o filesystem vivo** — uma violação de file-first disfarçada de "respeitar a premissa documentada". O espelho inverso é igualmente perigoso: ao trocar de máquina, assumir que um path documentado existe quando não existe.

**Diagnóstico (causa-raiz, dupla):**
1. **Falta um mecanismo** que, no boot, detecte o ambiente real (host/SO/drives/hooks) e **cruze** com as premissas declaradas, marcando cada uma como APLICA nesta máquina vs. ESTALE.
2. **Falta uma regra de confiança**: nada classifica premissa-de-ambiente como INFERÊNCIA-com-validade. Entre dois boots, o agente continua confiando na prosa. O fix mecânico sozinho não cobre o turno-a-turno; a regra sozinha não deixa prova nem registro cross-IA. **Por isso: ambos** (decisão do dono, 2026-06-22).

O núcleo NÃO pode hardcodar `F:\`/`CORPUS_ROOT`/path de domínio — o linter de agnosticismo (`check_core_agnostic.py`, ADR-020) varre `_shared/`, `.agent/**` e raiz por norma e o **repo inteiro** por tokens sensíveis (paths/cliente). Logo as premissas têm de viver como **DADO declarativo por-projeto** que o núcleo só lê pelo schema.

## Decisão (1 frase ativa)

Adicionar (a) um **manifesto declarativo por-projeto `.agent/environment.json`** onde cada projeto declara suas premissas de ambiente (paths, drives, hooks, env), versionado no núcleo apenas como **template genérico `.agent/environment.example.json`** (sem path real — ver §Agnosticismo); (b) um check **`check_environment_applicability()`** em `boot_check.py` (na lista `CHECKS`, contrato `{name,status,detail,stamps}`, herdando prova/liveness/EDR-imunidade) que **detecta o ambiente real** (host/SO via `platform`; existência de path/drive via `os.path.exists`, nunca probe de rede) e **cruza** com o manifesto pela **matriz de polaridade** (§Matriz), marcando cada premissa **APLICA · ESTALE · AUSENTE**, gravando o resultado em `.claude/boot-proof.json` (**sink garantido, local**) e — **quando o hub cross-IA estiver configurado** — propagando via `cross_ai_hub.py deposit()` montando o **envelope de handoff** exigido (fail-soft, ADR-069); e (c) uma **REGRA transversal em `_shared/traceability/SKILL.md`** (lar do file-first; link cruzado a confidence-classification) que reclassifica premissa-de-ambiente como **INFERÊNCIA com validade** — re-verificável por inspeção, com **file-first suplantando prosa sobre o filesystem**.

## Alternativas consideradas

1. **Não fazer / só nota de Aprendizado.** Prosa inerte — a premissa estale repete no próximo PC. **Rejeitada** (framework = prosa→mecanismo; a falha já é reincidente em classe com ADR-019/060).
2. **Hardcodar a detecção dos paths do domínio no núcleo** (ex.: checar `F:\corpus`). Quebra agnosticismo (ADR-020) → `check_core_agnostic` FAIL + vazamento sensível no export; e não escala a outros projetos. **Rejeitada por limite real** (linter de boot/export).
3. **Parsear premissas da prosa do briefing/ADR via regex.** Zero artefato novo, mas frágil e não-determinístico — exatamente o anti-padrão "hint-virou-causa" que já nos mordeu. **Rejeitada** (não-determinismo).
4. **Só mecanismo (sem regra).** Cobre o boot, mas entre boots o agente ainda confia na prosa estale; não reclassifica a premissa no eixo de confiança. **Rejeitada** (não cobre o turno-a-turno — decisão do dono por "ambos").
5. **Só regra (sem mecanismo).** Sempre-ativa e barata, mas sem prova determinística nem registro cross-sessão/cross-IA — outra IA repete o erro. **Rejeitada** (sem prova nem propagação).
6. **Manifesto declarativo `.agent/environment.json` + check no `boot_check.py` + regra em `_shared/traceability` + propagação via `cross_ai_hub.py deposit()` (ESCOLHIDA).** Agnóstico (núcleo lê só o schema; valores são do projeto; núcleo versiona só o `.example.json`); determinístico (entrada = arquivo local + `platform`/`os.path.exists`, nunca rede); reusa a infra de boot e o `deposit()` existente (§0 ganho-líquido por reuso, não adição pura); regra cobre o turno-a-turno; hub propaga cross-IA quando configurado.

## Matriz de polaridade do veredito (corrige furo ALTO-2 do qa-critic — cobre o caso-raiz `expect_present:false`)

Cada premissa declara `expect_present` (a polaridade: o projeto AFIRMA presença `true` ou AUSÊNCIA `false`). O check observa `found` (realidade viva via `os.path.exists`/detecção). Veredito determinístico:

| `expect_present` | `found` (real) | Veredito | Significado |
|---|---|---|---|
| `true`  | `true`  | **APLICA** | premissa de presença confirmada nesta máquina |
| `true`  | `false` | **AUSENTE** | esperado aqui, mas não existe (ex.: path documentado some ao trocar de PC) |
| `false` | `false` | **APLICA** | premissa de ausência confirmada (ex.: "F:\ não existe" e de fato não existe) |
| `false` | `true`  | **ESTALE** | **← o caso-raiz**: prosa afirma ausência, mas existe (F:\ "não existe" mas está montado) → file-first suplanta a prosa |

Regra de ação: **ESTALE e AUSENTE** disparam banner LOUD ("não confie na premissa documentada — a realidade desta máquina diverge"); **APLICA** é silencioso. O agente sempre opera pela coluna `found`, nunca pela prosa.

## Consequências

**Positivas:** premissa de ambiente deixa de ser ponto cego — no boot, cada uma vira APLICA/ESTALE/AUSENTE com prova checável; o caso `F:\`-existe-mas-prosa-diz-que-não vira **ESTALE LOUD** em vez de hesitação; ao trocar de PC, path documentado-mas-ausente vira ESTALE antes de o agente assumir; registro cross-IA evita que Claude/Gemini/outros repitam a premissa errada; o núcleo permanece agnóstico (premissas são dado do projeto); reuso de `boot_check.py`/`cross_ai_hub.py` satisfaz a régua §0 (caso (c): destrava garantia inalcançável por prosa, reusando infra). A regra em `_shared/` torna o fix sempre-ativo, independente de hook.

**Negativas / limite (declarado):** o check é **fail-soft** (`boot_check` nunca trava o boot — só reporta); **sem `.agent/environment.json`** o check vira no-op declarado (status "skip: sem manifesto" — nunca falso-OK), exigindo que o projeto preencha o manifesto para ter valor (mesma classe do briefing.md vazio); a detecção de drives/hosts é **local** (não cobre paths de rede montados sob demanda nem credenciais — declarado); o registro cross-IA depende do hub configurado (ADR-069) — sem hub, só prova local (fail-soft). A regra adiciona ~poucas linhas a um SKILL de `_shared/` — ganho-líquido justificado por fundir-com a postura file-first existente (não cria skill nova).

## Mecanismo em 3 camadas (detectar + cruzar + propagar)

1. **DETECTAR (auto, sem cooperação do agente, determinístico):** host (`platform.node()`), SO (`platform.system()`). Para premissas `kind ∈ {path, drive}` a observação `found` é **`os.path.exists(value)`** — primitivo único que cobre Windows e POSIX e devolve a verdade viva: um drive ejetado/inacessível dá `False` (= a realidade que o agente precisa), não um falso-presente por "letra reservada". Para `kind=env`, `os.environ.get`. Para `kind=hook`, checagem do marcador de liveness/inércia já existente. Nunca probe de rede. *(Resolve MÉDIO-1 do qa-critic: API de detecção especificada.)*
2. **CRUZAR (contra o manifesto, pela Matriz de polaridade acima):** para cada premissa de `.agent/environment.json`, combina `expect_present` × `found` → **APLICA · ESTALE · AUSENTE**. Grava no bloco `environment` de `.claude/boot-proof.json`.
3. **PROPAGAR (cross-session/cross-IA, só quando há ESTALE/AUSENTE):** monta o **envelope de handoff** com os campos que `cross_ai_hub.deposit()` exige (`schema_version, report_id, topic_fingerprint, thread_id, from, to, date, status, kind, round`) e **escreve-o no próprio outbox** (`docs/_private/cross-ai/outbox/`) — o **depósito no hub é o fluxo de PR existente (ADR-069: claude-master nunca auto-deposita no repo de outra IA)**, não uma chamada automática a `deposit()`. **Fail-soft:** outbox não-gravável → **só prova local**, declarado no output. *(Resolve ALTO-1 do qa-critic: NÃO existe função "publish"; o envelope segue o contrato REQUIRED de `deposit`, mas a publicação é via PR. Sink garantido = `boot-proof.json` local.)*

**Limites honestos (declarados):**
- O mecanismo **detecta e anuncia** — não reescreve o briefing/ADR estale automaticamente (isso exige decisão do dono / docops). Dá ao agente a verdade viva; a correção da fonte é ação consciente.
- O `boot-proof.json` é **snapshot por-boot, datado** — é "última realidade observada nesta máquina/sessão", **nunca premissa congelada**. O próximo boot **re-detecta** e sobrescreve; nenhuma sessão deve tratar o veredito anterior como CONFIRMADO-para-sempre (seria recriar o anti-padrão que o ADR combate). *(Resolve BAIXO-1 do qa-critic: risco de auto-referência circular declarado e neutralizado pela re-detecção.)*

## Esboço do schema do manifesto (referência ao developer; valores são EXEMPLO genérico, não normativos)

Versionado no núcleo como `.agent/environment.example.json` (placeholders genéricos). O `.agent/environment.json` real é **per-projeto**:

```json
{
  "schema_version": 1,
  "assumptions": [
    { "id": "corpus-root",   "kind": "path", "expect_present": true,  "value": "<PATH-DO-PROJETO>", "note": "raiz do corpus (esperado presente)" },
    { "id": "scratch-legacy","kind": "path", "expect_present": false, "value": "<PATH-LEGADO>",     "note": "diretório que NÃO deve existir aqui (caso da falha-raiz)" },
    { "id": "edr-veta-hooks","kind": "hook", "expect_present": true,  "note": "hooks PS inertes nesta máquina" }
  ]
}
```
`kind ∈ {path, drive, host, env, hook}`. **`expect_present` é obrigatório** (a polaridade — ver Matriz). O núcleo lê **só o schema** — `value`/`note` são dados do projeto (agnosticismo preservado). O developer fecha o schema exato + canário.

## Agnosticismo — escopo do linter (corrige furo ALTO-3 do qa-critic)

`check_core_agnostic.py` (tier NORMA, que roda no boot) varre apenas `CORE_GLOBS` de `*.md` — **`.agent/environment.json` (`.json`) está FORA** desse escopo. Decisão de design para não vazar:
1. O núcleo versiona **só `.agent/environment.example.json` com placeholders genéricos** (`<PATH-DO-PROJETO>`), nunca um manifesto real → zero path de cliente no repo-núcleo.
2. O `.agent/environment.json` real (com paths concretos) é **per-projeto**; em export, o **tier SENSÍVEL** (`--sensitive`, varre o repo inteiro incl. `.agent/`) o cobre — é o gate que barra path/cliente na distribuição.
3. O canário inclui asserção de que **nenhum path concreto** é introduzido no `.example.json` versionado (mantém o núcleo limpo no boot, onde o tier norma não alcança `.json`).

## Implementação (ponteiro após aceito)
- Ponteiro: branch `feature/adr-093-env-applicability` · data `2026-06-22` · grep `check_environment_applicability`
- `tools/boot_check.py`: `detect_environment()` + `check_environment_applicability()` no `CHECKS` — **contrato `{name, status, detail, stamps}`** (status ∈ ok/warn/fail/skip; "skip" já no glyph map; `stamps=[]` salvo confirmar execução). `boot-proof.json` ganha bloco `environment`.
- `.agent/environment.example.json`: template genérico (schema_version 1, placeholders). O `.agent/environment.json` real é per-projeto (não versionado no núcleo).
- `_shared/traceability/SKILL.md`: REGRA "premissa de ambiente = INFERÊNCIA com validade; re-verificar por inspeção; file-first suplanta prosa sobre o FS" + **link cruzado a `_shared/confidence-classification`** (eixo CONFIRMADO/INFERIDO). Decidido aqui (não em confidence-classification) por ser primariamente file-first — evita duplicação/skill nova (§0).
- `tools/cross_ai_hub.py`: **reuso de `deposit()`** (NÃO há função "publish" — montar o envelope `.md` com os 10 campos e chamar deposit); fail-soft sem hub.
- `tools/test_environment_applicability.py`: canário — **4 quadrantes da matriz** (incl. `expect_present:false` × found:true = ESTALE) + sem-manifesto=skip + `.example.json` sem path concreto + contrato do dict.
- `capabilities.json`: `environment-applicability-gate` (+1; enforcement=fail-soft, declarado) + `python tools/build_capabilities.py`.
- `.agent/workflows/start-session.md` + `CLAUDE.md`: passo de boot menciona o check (já roda via `boot_check.py`).
- Hash de commit: complemento opcional — nunca único (ADR-001/002).
