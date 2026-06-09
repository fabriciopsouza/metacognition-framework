# metacognition-exec-reports — corpus público de aprendizado (identificador padrão)

| Campo | Valor |
|---|---|
| **Papel** | `corpus` — aprendizado anonimizado que evolui o framework |
| **Dono** | public (corpus compartilhado) |
| **Visibilidade** | **PÚBLICO** |
| **Quem escreve** | qualquer um, **via PR** (contribuidor limitado, ADR-063) |
| **Canonical remote** | `https://github.com/fabriciopsouza/metacognition-exec-reports` |

**O que entra:** SÓ o `learnings-public` **anonimizado** (passa por `anonymize.py` + `sensitive-denylist`
**antes** do PR; a CI **re-valida** com whitelist + anti-PII e faz auto-merge só se verde). **Nunca** conteúdo
de domínio, PII, ou o report FULL (esse fica privado na mãe, `docs/_private/_intake/`).
**Layout:** `reports/<pseudônimo-aleatório>/<ISO-timestamp>__<exec-id>.md` (append-only).
**Opt-in:** `~/.claude/exec-report-consent.json` (o ato de gerar o consent é o opt-in informado — LGPD Art. 12).
