# ADR 066 — READMEs web com uso/config detalhados, anti-confusão web×full, e cofre próprio por clone

- Status: **Aceito** (2026-06-05 — CI verde 3 SOs + qa-critic; -premium full verificado via gh) · Data: 2026-06-05 · Decisores: dono + squad (developer)
- Onda: distribuição/adoção · Tipo: **EMENDA** de ADR-054/058 (READMEs web) + ADR-049/052 (tiers/cofre). Atende: dono tentou usar o premium em outro PC, clonou o `-web-premium` (skills-only) esperando o full; "os repos web deveriam ter instruções detalhadas"; "cada clone seu próprio cofre".

## Contexto

Dois problemas reais de campo: (1) **confusão `-web-premium` × `-premium`** — ambos têm "premium" no nome; o `-web-premium` é a versão CHAT (prompt+skills, sem filesystem, **por design**), o `-premium` é o framework FULL (clona-e-roda, menos cofre). O dono clonou o errado. Os READMEs web eram **tersos** (não diziam COMO usar/configurar). (2) **Cofre por clone:** `detect_tier()` marca OWNER só se `docs/_private` existir; as distribuições vêm **sem** cofre (stripped) → um clone full era tratado como EXTERNAL até o usuário criar o cofre à mão. O dono espera "cada clone seu próprio cofre".

## Decisão (1 frase ativa)

**(a) READMEs web gerados (`web_export.py`) passam a trazer USO + CONFIG passo-a-passo** (Claude.ai Projects: instruções=prompt, conhecimento=skills/; Gemini/ChatGPT: colar; o que o chat NÃO faz — anti-JARVIS) **+ redireção anti-confusão** (header gritante no `-web-premium`: "versão CHAT; para o full clona-e-roda use `metacognition-framework-premium`"; ambos READMEs apontam o repo full); **(b) o `bootstrap.py` cria o COFRE PRÓPRIO** (`docs/_private/_intake/` + README) quando ausente — um clone full vira **OWNER** do seu cofre (idempotente; "cada clone o seu"), com o README do cofre avisando que publicar learnings exige o **`sensitive-denylist` próprio** (as distros não trazem a do mantenedor → senão fail-closed).

## Consequências

**Positivas:** ninguém mais confunde chat × full (header + redireção + instruções claras); o premium-web vira utilizável de fato (passo-a-passo de config por plataforma); clone full nasce OWNER com cofre próprio (relatório FULL local), sem passo manual; o README do cofre explica o pré-requisito do denylist próprio (evita o "por que o publish recusa?"). **Negativas/limite:** o scaffold do cofre está no `bootstrap.py` (Python, universal) — o `bootstrap.ps1` (admin) ainda não o faz (follow-up; ou o agente garante no `/start-session`); os READMEs web são gerados → editar no `web_export.py`, não no repo `-web` (sentido único). **Cascata:** republica nos `-web`/`-web-premium` no próximo export. **EMENDA** in-place de ADR-054/058/049/052.

## Implementação (ponteiro)

`tools/web_export.py`: READMEs público e premium reescritos (uso/config + anti-confusão). `bootstrap.py`: `ensure_cofre()` (idempotente, fail-soft) chamado no `main`. `test_web_export` segue verde (determinístico). **DONE quando:** o `-web-premium` deixa claro que é chat e aponta o full; um clone full bootstrapado tem `docs/_private/` próprio (tier OWNER). Status→Aceito após verificação.
