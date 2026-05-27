# history.md — Registro append-only do framework

> Single-writer = orquestrador (PMO). Append-only. Cada entrada com timestamp ISO.
> Formalizado pelo ADR-007 (v1.9.0). Já era referenciado pelo `AGENT-FRAMEWORK.md` §2.B
> (sequência de ativação do squad lê últimas 30 linhas).
>
> 3 seções: histórico cronológico de checkpoints (formato em `.agent/workflows/checkpoint.md`),
> `## Em aberto` (WIP — ex-G11), `## Aprendizado` (fracassos — ex-G9, com firewall).

---

## 2026-05-27T03:30 — Sessão noturna: gap intake↔realidade na v1.9.0 reconhecido

Aprendizado documental (não-bloqueante): o intake §4 estimou "~6 edições de 1-3 linhas + 2 linhas de princípio" para a v1.9.0. A realidade do PR foi 428 inserções. O conteúdo é justificável linha a linha pela régua §0 (ADR-007: 160 linhas decisórias; companion + template: ~160 linhas substantivas; edições cirúrgicas: ~100 linhas). Não há regressão funcional — apenas a estimativa do intake estava errada por ~70× porque não considerava ADR+companion+template como artefatos novos legítimos. Lição: estimativas em intake devem distinguir "edições" de "artefatos novos". Não vira ADR (caso isolado, não padrão recorrente — §Aprendizado).

---

## 2026-05-27T01:00 — Sessão noturna: ADR-006 + ADR-007 + Régua §0

Aprovado e funcionando:
- v1.7.1 mergeada em main (PR #7, commit 99cf801) — fix do gap ADR-005 (framework-sync.ps1 espelhado).
- v1.8.0 mergeada em main (PR #8, commit afb98aa) — auto-boot global do squad com allowlist (ADR-006).
- Modo `autosuficiente` ativado em campo (PC do mantenedor); ratchet ADR-005 validado.

Nomenclaturas estabelecidas:
- `framework-sync.ps1` (instância global) ≠ `sync-global.ps1` (fonte versionada) — par fonte/binário.
- `squad-owners.txt` — allowlist de owners para auto-boot global.
- Régua §0 = GANHO LÍQUIDO (princípio 10 do AGENT-FRAMEWORK §6).

Decisões permanentes:
- ADR-005: modos de execução (Aceito, mergeado).
- ADR-006: auto-boot global (Aceito, mergeado em PR #8).
- ADR-007: Régua §0 + G1 pesquisa-cascata + ex-G9 + ex-G11 (Aceito, em implementação v1.9.0).

Próximo passo: completar implementação v1.9.0 + qa-critic código + PR + merge; depois FASE C (backlog) + FASE D (sumário).

Riscos ativos: race condition humano vs orquestrador no history.md (mitigada por convenção append-only com timestamp — ADR-007 Risco 5).

---

## Em aberto

> WIP atual (ex-G11). Reconciliar com branches do git e ADRs em status `Proposto` no `/start-session` (modo squad).

- *(nenhum item em aberto além da implementação em curso da v1.9.0)*

---

## Aprendizado

> Notas de fracassos capturadas via `/checkpoint` (ex-G9). **Firewall:** notas são **inertes** — só viram comportamento via skill/regra destilada, aprovada via ADR e mergeada. Nota errada não propaga.

- *(nenhum aprendizado registrado nesta sessão — sem gatilho de fracasso disparado)*
