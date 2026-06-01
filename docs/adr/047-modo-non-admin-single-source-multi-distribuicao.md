# ADR 047 — Modo NON-ADMIN (sem hooks PS) + pipeline single-source → multi-distribuição

- Status: Aceito
- Data: 2026-06-01 · Decisores: dono + squad (architect)
- Tipo: **novo** (perfil de distribuição + variante de export) — net-gain: destrava o uso do framework em máquina corporativa com restrição de scripts (hoje **não inicia**).
- Origem: dono — máquina corporativa com GPO `Restricted` bloqueia PowerShell; os hooks (`powershell.exe -ExecutionPolicy Bypass`) não rodam → framework não inicia. A versão de ~5 dias atrás (menos hooks) iniciava. Relaciona: ADR-005 (modos), ADR-027 (route-gate), ADR-022 (mission-gate), ADR-037 (overwrite-guard), publish-clean.

## Contexto

A política `Restricted` via Group Policy **ignora `-ExecutionPolicy Bypass`** → todo `.ps1` é barrado;
os hooks de SessionStart/PreToolUse falham e a abertura quebra. **Python não é barrado** pela política de
PS. A versão ADMIN (com hooks) **continua sendo a default** e não muda. Falta uma variante **non-admin**
que **inicie sob restrição sem perder funcionalidade** — pelo trade-off do dono: **automação nunca
invisível**; o que era hook silencioso vira **gate anunciado e aplicado pelo agente** (avisado, solicitado,
com orientação).

## Decisão (1 frase ativa)

Criar um **perfil non-admin** (`.claude/settings.nonadmin.json` SEM hooks + `bootstrap.py` em Python puro
que o ativa sem admin/PS + doutrina **"gates anunciados"** em `CLAUDE.md`/`AGENTS.md`: o agente declara e
aplica inline cada gate que o hook faria) e estender o **pipeline de export para single-source →
multi-distribuição**: do **único** repo privado, cada release regenera **todas** as distribuições públicas
— **admin** (com hooks) e **non-admin** (settings sem hooks) — **cada uma mantendo suas características
próprias**, sempre, a partir do mesmo trabalho.

## Alternativas consideradas (≥3)

1. **Remover/enfraquecer os hooks no admin (status quo regressivo).** Quebraria o enforcement automático que a versão admin entrega. **Rejeitada** — o dono quer o admin **intacto**.
2. **Portar todos os hooks para Python no admin.** Esforço grande; muda a versão admin; e a doutrina "anunciado" é o trade-off pedido (visibilidade), não "hooks invisíveis em outra linguagem". **Rejeitada por ora** (candidato futuro).
3. **Só documentar "desligue os hooks manualmente".** Frágil, sem distribuição pronta nem garantia de início. **Rejeitada.**
4. **Perfil non-admin + variante de export + pipeline multi-distribuição (ESCOLHIDA).** Prós: inicia sob restrição (clone-and-go do público non-admin OU `python bootstrap.py`), admin intacto, single-source (uma mudança atualiza todas as distribuições), gates anunciados (visíveis). Contras: enforcement non-admin depende do agente aplicar — mitigado tornando o **anúncio obrigatório** (doutrina) + linters Python on-demand.

## Consequências

**Positivas:** framework inicia em máquina restrita; admin segue com hooks; uma única fonte gera N
distribuições, cada uma com sua característica preservada; trade-off honesto (visível > silencioso).
**Negativas:** +1 repo público (non-admin) + variante no export/publish. **Riscos/limite declarado:** no
non-admin o enforcement é **anunciado-pelo-agente**, não hook — por isso a doutrina exige declarar cada
gate; risco residual de o agente pular → vai a `LIMITS.md`. Hooks `.ps1` continuam no pacote non-admin
(inertes sob restrição) para reativação se a máquina permitir.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.34-non-admin` · `2026-06-01` · grep `nonadmin|non-admin|bootstrap.py`
- Artefatos: `.claude/settings.nonadmin.json`, `bootstrap.py` (+ `--check`), `guia/MODO-NON-ADMIN.md`,
  doutrina em `CLAUDE.md`/`AGENTS.md` (§Modo non-admin), `tools/export-clean.py --variant nonadmin`
  (troca settings.json pelo sem-hooks), `publish-clean` empurra **admin + non-admin** do mesmo source.
- Repo público non-admin: `metacognition-framework-public-nonadmin` (settings.json sem hooks; clone-and-go).
- DONE quando: público non-admin clonável inicia sob restrição + pipeline regenera ambos a cada release.
