# ADR 084 — Sync de boot: defasagem vs a branch de INTEGRAÇÃO (baseline ortogonal ao `@{upstream}`)

- Status: **Aceito** (2026-06-16 — gate: qa-critic adversarial + canários C6/C7 PASS) · Data: 2026-06-16 · Decisores: dono (relato do bug em sessão real) + squad
- Tipo: **correção de bug recorrente** (não adição pura). Régua §0 (ADR-007): satisfaz a cláusula (c) — *destrava-eval editando existente*: estende o mecanismo e o canário já existentes (`check_repo_sync.py`/`test_repo_sync.py`), não cria gate paralelo. +1 capability NÃO criada — a `repo-sync-boot` foi **estendida**.
- Relaciona: ADR-019 (boot-sync), ADR-060 (resiliência EDR do sync), ADR-061 (liveness/route-gate), ADR-020 (núcleo agnóstico), ADR-027 (route-gate)

## Contexto

ADR-019/060 tornaram o sync de boot um **mecanismo** (hook que faz `git fetch` + mede ahead/behind + auto-`pull --ff-only` quando seguro). Mas a medição é contra `@{upstream}` — o upstream **da própria branch**. O fallback para `origin/main` só dispara quando **não há upstream algum**.

**Modo de falha (sessão real, 2026-06-16):** numa feature branch (`docs/test-session-2026-06-11`) com upstream próprio (`origin/docs/test-session-2026-06-11`), o gate reportou **"sync ok / em dia"** — corretíssimo vs o próprio espelho remoto (0 atrás) — enquanto a branch estava **6 commits atrás de `origin/main`** (framework já em v1.60.0). O agente emitiu STATUS e uma recomendação de merge sobre um **retrato congelado**. É a reincidência do modo de falha que o ADR-019 nasceu para matar (method-audit 2026-05-30: "operou 41 commits atrás de main").

**Por que a remediação anterior não pegou:** o canário `test_repo_sync.py` (C1–C5) monta sempre um clone **na `main`** rastreando `origin/main` — ali `@{upstream}` ≡ `origin/main`, então o bug é invisível. O ponto cego só aparece numa **feature branch com upstream próprio** (`@{upstream}` ≠ `origin/main`), topologia que o teste nunca exercia. *O teste validou o caminho feliz da topologia errada.*

## Decisão (1 frase ativa por item)

**(D1)** Adicionar ao `check_repo_sync.py` (e paridade no `.ps1`) uma **dimensão 2 ORTOGONAL**: medir `HEAD..<baseline>` contra a **branch de integração**, independente de `@{upstream}`. Roda DEPOIS do auto-pull da dimensão 1 (HEAD já movido). Guarda cirúrgica: se `baseline == @{upstream}` (ex.: estou NA main), a dimensão 1 já cobre → pular (preserva C1–C5 idênticos).

**(D2)** Resolver a baseline de forma **AGNÓSTICA (ADR-020)**: `git symbolic-ref refs/remotes/origin/HEAD` → fallback `origin/main` → `origin/master`. Hardcodar `main` feriria o núcleo agnóstico e tropeçaria no `check_core_agnostic`.

**(D3)** **Não auto-pular** a baseline (não se faz `ff-only` de `main` dentro de uma feature branch). Em vez disso, gravar marker persistente `.claude/.stale-vs-main` (behind, base, base_sha) e emitir aviso ALTO.

**(D4)** **Forçar reconhecimento** (escolha do dono sobre "só avisar"): o `route-gate` (.sh + .ps1) lê o marker e **repete o nudge por-turno** até (a) a branch ser atualizada — `behind==0` na re-verificação barata local → limpa marker; ou (b) o atraso ser reconhecido — `git rev-parse --short <base> > .claude/.stale-vs-main.ack`; o ack é invalidado quando a baseline avança de novo (re-nag). Fecha o modo de falha "agente passa batido por um status de boot".

**(D5)** Adicionar **canários C6 (feature branch em dia com o próprio upstream mas atrás de `origin/main` → AVISA + marker) e C7 (branch atualizada → marker removido, silencioso)** — reproduzem a topologia que falhou.

## Alternativas consideradas

1. **Só avisar no boot (sem persistência).** Rejeitada: o modo de falha não foi "faltou aviso" — foi "agente ignorou um status". Aviso que evapora no 1º turno tem a mesma fraqueza.
2. **Hardcode `origin/main`.** Rejeitada: fere ADR-020; quebra em repos com `master`/`develop`.
3. **Bloquear o boot quando atrás da baseline.** Rejeitada: gate de entrada nunca bloqueia (fail-open ADR-027); persistência + reconhecimento é proporcional.

## Consequências

**Positivas:** o blind spot feature-branch-vs-main é mecanizado e testado; baseline agnóstica; o nudge persistente é auto-resolvente (cala ao rebasear ou reconhecer); mudança cirúrgica (C1–C5 inalterados). **Negativas/limite (declarado):** a re-verificação por-turno do route-gate roda `git rev-list --count` local (sem fetch) — reflete o último fetch do boot, não o remoto vivo (aceitável: barato, e o boot fez o fetch). Em máquina onde o EDR veta `.ps1`, a dimensão 2 do `.ps1` não roda — mas o `.py` (porta definitiva, ADR-060) roda, e o route-gate.sh entrega o nudge. **Paridade:** lógica idêntica em `check_repo_sync.py` ↔ `check-repo-sync.ps1` e `route-gate.sh` ↔ `route-gate.ps1`.

## Implementação (ponteiro)

- `tools/hooks/check_repo_sync.py` + `.claude/hooks/check-repo-sync.ps1`: `resolve_baseline()` + `baseline_staleness()` + guarda `base==upstream`.
- `tools/hooks/route-gate.sh` + `route-gate.ps1`: leitura do marker + re-verificação barata + ack.
- `tools/test_repo_sync.py`: C6/C7.
- `.gitignore`: `.claude/.stale-vs-main` + `.ack`.
- `capabilities.json`: `repo-sync-boot` estendida (ADR-019 → ADR-084).
</content>
</invoke>
