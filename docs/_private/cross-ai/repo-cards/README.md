# repo-cards — identificadores padronizados dos 4 repos (templates para o DONO depositar)

> **Por que estão aqui e não nos repos-alvo:** isolamento (ADR-069). O Claude **só escreve no
> `metacognition-framework`**. Os cartões do `hub`, `exec-reports` e `gemini` são **gerados aqui como
> template** e o **dono** os deposita em cada repo (HITL — nenhuma IA cria/escreve no repo do outro).

## Como usar (ação do dono)

Para cada repo-alvo, copie o par `<repo>.repo-identity.json` → `.repo-identity.json` (na raiz do repo) e
`<repo>.REPO.md` → `REPO.md`, e commite **no próprio repo**.

| Arquivo aqui | Vai para | Como |
|---|---|---|
| `metacognition-hub.repo-identity.json` + `.REPO.md` | repo `metacognition-hub` (raiz) | dono commita |
| `metacognition-exec-reports.repo-identity.json` + `.REPO.md` | repo `metacognition-exec-reports` (raiz) | dono commita |
| `metacognition-gemini.repo-identity.json` + `.REPO.md` | repo `metacognition-gemini` (raiz) | **o Gemini** commita no próprio repo (é a mãe dele) |

> O par do `metacognition-framework` (mãe Claude) **já está commitado na raiz deste repo**
> (`.repo-identity.json` + `REPO.md`) — é o exemplar de referência.

## Nota sobre `role: hub` e `role: corpus`

O classificador `repo_identity.py` (ADR-070) só reconhece `master`/`shadow` como identidade positiva.
`hub` e `corpus` caem em **AMBIGUO** de propósito → "escrita exige confirmação". Isso é **correto**: nesses
repos a escrita é **PR-gated** (branch protection + CI), nunca push direto. O campo `role` aqui é
**identificador documental**; a trava real é server-side.
