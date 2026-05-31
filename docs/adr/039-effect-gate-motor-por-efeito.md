# ADR 039 — effect-gate: de backstop de 5 padrões para motor de regras por classe de efeito

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.28.0) · Tipo: **EMENDA** (refatora o hook do ADR-015; política vira dado) — net-gain: amplia cobertura sem inflar o hook (a política sai do código para `effect-rules.json`).
- Origem no plano: item 7 (`[CRÍTICA]`). Relaciona: ADR-015 (effect-gate original), ADR-014 (allowlist por efeito), ADR-040 (paridade/CI), `_shared/action-safety`.

## Contexto

O effect-gate (ADR-015) era ~5 padrões grep hardcoded no hook (rm-raiz, mkfs/dd, push-force,
fork-bomb, firewall-off). Passavam: `find -delete`, `git reset --hard` + `clean -fdx`, reescrita de
histórico, `curl|bash`, exfiltração de segredo. A política estava **no código** — adicionar cobertura
exigia editar o hook (e duplicar em `.ps1`/`.sh`).

## Decisão (1 frase ativa)

Refatorar o effect-gate para **motor de regras** que interpreta `tools/effect-rules.json` (cada regra:
`family` · `tier` · `decision` deny/ask/allow · `all`[] + `none`[] de regex), mantendo **default-allow**
(backstop conservador, `ask` para T2 ambíguo), cobrindo **4+ famílias** (mass-destruction,
history-rewrite, escalation-persistence, exfiltration, resource-exhaustion) — o `.json` é a política,
o hook é o interpretador, e os regex ficam no **subconjunto comum .NET ∩ POSIX-ERE** para paridade `.ps1`/`.sh`.

## Alternativas consideradas (≥3)

1. **Manter os 5 padrões hardcoded.** Cobertura estreita; bypasses conhecidos passam. **Rejeitada — é o gap.**
2. **Adicionar mais if/grep no hook.** Infla o hook e duplica em 2 SOs; política some no código. **Rejeitada** (régua §0 + manutenção).
3. **Classificador "inteligente" (LLM/heurística) de efeito.** Não-determinístico; um backstop de segurança precisa ser previsível e auditável. **Rejeitada.**
4. **Motor de regras + política em JSON (ESCOLHIDA).** Prós: adicionar família/regra = editar dado (não código); `all`/`none` preserva a nuance do rm (recursivo E forçado E raiz) e do push-force (sem `--force-with-lease`); regex em subconjunto comum garante paridade. Contras: depende do `.json` (fail-open se ausente); regex tem de evitar `\s`/`\b` — **declarado** no header da política.

## Consequências

**Positivas:** cobertura por classe de efeito (4+ famílias) com anti-falso-positivo (≥2 benignos por
família no canário); política editável sem tocar o hook; `ask` para T2 (find-delete, reset --hard,
clean -fd, filter-branch, curl|bash, exfil) sem bloquear o fluxo legítimo. **Negativas:** o `.json` é
uma dependência do hook (mitigado por fail-open). **Riscos/limite declarado:** OWASP LLM06 só vira 🟢
**após** a matriz CI (3 SOs) + paridade 100% verdes (ADR-040) — até lá, o claim é 🟡 (honestidade
mecanizada em `LIMITS.md`/ADR-044). O `.sh` foi validado localmente por emulação `grep -E` (ERE) idêntica
ao `.ps1`; a prova final é o `test_parity` na matriz CI.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `effect-rules|effect-gate`
- Artefatos: `tools/effect-rules.json` (12 regras / 5 famílias), `tools/hooks/effect-gate.ps1` (ASCII-only,
  interpretador), `tools/hooks/effect-gate.sh` (jq + grep -E), `tools/test_effect_gate.py` (deny/ask/allow
  por família + fuzzing), `tools/test_parity.py` (decisão idêntica .ps1↔.sh).
- DONE quando: 4 famílias com anti-falso-positivo + paridade nos 3 SOs → reclassificar OWASP LLM06 🟡→🟢.
