# metacognition-framework — mãe Claude (identificador padrão)

> Cartão humano de identidade. Par de máquina: [`.repo-identity.json`](.repo-identity.json) (lido no boot
> por `tools/repo_identity.py`, ADR-070). Topologia dos 4 repos: ver §abaixo.

| Campo | Valor |
|---|---|
| **Papel (`role`)** | `master` — repo-mãe canônico |
| **Dono (`ai_owner`)** | `claude` (id cross-IA: `claude-master`) |
| **Visibilidade** | privado |
| **Quem escreve** | **só o Claude** (leitura livre) |
| **Canonical remote** | `https://github.com/fabriciopsouza/metacognition-framework` (branch `main`, protegido: PR + CI) |

**O que NÃO fazer aqui:** nenhuma outra IA escreve neste repo (read-only para o Gemini). O Claude **nunca**
escreve em `metacognition-gemini`. Cross-IA acontece **só pelo hub** (ver topologia).

## Topologia cross-IA (4 repos, uma "coisa" por repo — ADR-069/070/063)

| Repo | Papel | Visib. | `role` | Escreve |
|---|---|---|---|---|
| `metacognition-framework` | mãe Claude | privado | `master`/claude | só Claude |
| `metacognition-gemini` | mãe Gemini | privado | `master`/gemini | só Gemini |
| `metacognition-hub` | troca cross-IA (inbox/archive) | privado | `hub`/neutral | ambos, **via PR** |
| `metacognition-exec-reports` | corpus de aprendizado anonimizado | público | `corpus`/public | qualquer um, **via PR** |

**Isolamento = fronteira de repositório** (não subpasta: GitHub não tem ACL por-pasta). Trava física =
branch protection server-side + credencial escopada por-repo + reforço local (`settings.local.json` deny).
