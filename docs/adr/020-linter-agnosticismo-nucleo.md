# ADR 020 — Linter de agnosticismo do núcleo (enforcement executável do Princípio 12)

- Status: Aceito
- Data: 2026-05-30 · Decisores: dono (diretiva "da prosa ao mecanismo" nesta sessão) + squad (autônomo)
- Tipo: **EMENDA** (Princípio 12 / ADR-010 ganha enforcement; regra #5 do qa-critic ganha par executável)
- Pesquisa/Lastro: method-audit recorrente `history.md ## Aprendizado` 2026-05-29 + 2026-05-30; risco residual de ADR-010 §Riscos
- Relaciona: ADR-010 (Princípio 12 agnóstico) · ADR-013 (padrão contrato→`validate_skills`) · ADR-015 (padrão regra→`effect-gate`) · ADR-019 (padrão hook SessionStart fail-soft)

## Contexto

O Princípio 12 (ADR-010) diz que o **núcleo NÃO carrega listas hardcoded de normas/convenções de
domínio**. O qa-critic codificou isso como **regra #5** (REPROVA rascunho que cite norma de domínio
em arquivo não-rotulado como exemplo). Ambos são **prosa** — dependem de um agente lê-los e aplicá-los.

**A prosa falhou ≥2× e sempre foi o DONO quem pegou, nunca a auto-observação do agente:**
- v1.11.0: `README.md` vazou `ALCOA+/ANP/FDA/BACEN/GAMP` "como exemplo didático" (history.md:154).
- v1.11.0/12.0: 3 inflações detectadas pelo dono antes do commit (history.md:157).
- 2026-05-30 (esta sessão): **eu mesmo** vazei `ALCOA+` ao justificar a preservação de um traço de
  pesquisa — o dono pegou de novo (history.md ## Aprendizado 2026-05-30T14:30).

Causa-raiz: agente que se auto-audita não detecta o próprio vazamento (viés; Princípio 11 honesto).
É exatamente a tese da série v1.14.x: **regra crítica que depende de boa-vontade do agente vira
mecanismo**. O Princípio 12 era o último elo da tese sem par executável.

**Régua §0 (Princípio 10):** APROVADO por §0(c) — destrava uma garantia **inalcançável por prosa**
(detecção determinística do vazamento, independente do viés do agente). Não é adição pura: substitui
"confiar que o agente aplica a regra #5" por verificação automática; a regra #5 permanece como o
contrato humano-legível (mesmo par contrato↔validador do ADR-013).

## Decisão (1 frase ativa)

Adicionar um **linter executável de agnosticismo** — `tools/check_core_agnostic.py` — que varre o
**núcleo operativo** (`_shared/**`, `.agent/skills/**`, `.agent/rules/**`, `.agent/workflows/**`,
`AGENT-FRAMEWORK.md`, `CLAUDE.md`, `AGENTS.md`, `README.md` — as pastas que o `CLAUDE.md` declara núcleo)
procurando identificadores de norma regulatória de domínio (denylist em
`tools/agnostic-denylist.txt`), falha (exit 1) ao achar vazamento, e roda como **hook SessionStart
fail-soft** (`.claude/hooks/check-core-agnostic.ps1` + `.sh`) + canário de CI/pré-merge
(`tools/test_core_agnostic.py`).

### Componentes
- **`tools/check_core_agnostic.py`** — linter stdlib. Exit 1 + `LEAK arquivo:linha` por vazamento. Aceita arquivos explícitos (usado pelo canário).
- **`tools/agnostic-denylist.txt`** — ruleset (1 regex/linha). Vive em `tools/` (INFRA, como o ruleset de um linter) → **não é varrido** e **não viola o Princípio 12** (não é conhecimento de domínio do núcleo; é a negativa).
- **`tools/test_core_agnostic.py`** — canário com efeito: núcleo-limpo-PASSA + vazamento-PEGA + sentinela-isenta + cada padrão detectável + agnóstico-genuíno-não-falso-positiva.
- **`.claude/hooks/check-core-agnostic.ps1` (+ `.sh`)** — hook SessionStart. Avisa via `additionalContext` se vazou; **nunca bloqueia** (exit 0). Espelhado para `~/.claude/hooks/` por `sync-global.ps1`.

### Exceção única e auditável: sentinela `lint-agnostic:allow`
Uma linha do núcleo pode citar norma SE portar o sentinela `lint-agnostic:allow` + justificativa
(estilo `# noqa`). Hoje há **um** uso legítimo: a própria regra #5 do qa-critic (cita normas para
DEFINIR a detecção). Determinístico > heurística de "é exemplo?" — porque o vazamento se esconde
justamente atrás de "como exemplo" (lição v1.11.0).

## Alternativas consideradas

1. **Manter só a prosa (regra #5 + Princípio 12).** Rejeitada: falhou ≥2× empiricamente; sem mecanismo, depende do viés que ela tenta corrigir.
2. **Heurística "permitir se a linha diz 'exemplo'".** Rejeitada: o vazamento v1.11.0 estava rotulado "como exemplo didático" e ainda assim era violação. Marcador semântico é gameável; sentinela explícito não.
3. **Hardcodar a denylist dentro de uma skill do núcleo.** Rejeitada: seria o próprio anti-padrão (norma de domínio no núcleo). Por isso a denylist vive em `tools/` (infra).
4. **Linter executável + denylist em infra + hook fail-soft (ESCOLHIDA).** Espelha ADR-013/015/019. Prós: determinístico, agnóstico, auditável. Contras: denylist não-exaustiva (ver Riscos).

## Consequências

**Positivas:** Princípio 12 deixa de depender de boa-vontade; vazamento é pego no boot e na CI, não pelo dono em review; trilha auditável (sentinela em diff). Fecha o risco residual de ADR-010 §Riscos ("detector de vazamento ausente").
**Negativas:** +4 artefatos em `tools/`/`hooks/` (~200 linhas) + 1 entrada no SessionStart (custo de boot ~ rodar 1 script Python).
**Riscos:**
- (a) **Denylist não-exaustiva [DESCONHECIDO/por-design]** — surgem normas novas ("...podem existir OUTROS", dono 2026-05-30). O linter REDUZ, não ELIMINA; a regra #5 (semântica, qa-critic) continua como backstop. Mitigação: editar a denylist quando uma norma nova aparecer.
- (b) **Sentinela é loophole potencial** (como `# noqa`): alguém pode silenciar um vazamento real. Mitigação: aparece no diff/review + a justificativa é obrigatória por convenção; qa-critic revisa adições de sentinela.
- (c) **Paridade `.sh` [DESCONHECIDO]** — não testada em Linux/macOS (consistente com ADR-015/019 §Riscos). O `.ps1` é o caminho validado nesta versão.
- (d) **Falso-positivo** se um token de norma for substring legítima em outro contexto — mitigado por `\b` word-boundaries na denylist (todos os padrões, inclusive `\bALCOA\+?` após qa-critic round 2); canário §5 prova que texto agnóstico não dispara.
- (e) **Token dividido entre linhas** (ex.: `ALC\nOA+`) NÃO é detectado pelo scanner linha-a-linha [INFERIDO/intrínseco] — exige intenção adversarial, improvável em prosa real; backstop = regra #5 semântica do qa-critic. Documentado, não corrigido (custo > risco).

## Implementação (ponteiro após aceito)
- Ponteiro: branch `chore/reconciliacao-divida-v1.14-v1.19` · data `2026-05-30` · grep `check_core_agnostic|agnostic-denylist|lint-agnostic:allow`
- Artefatos: `tools/check_core_agnostic.py`, `tools/agnostic-denylist.txt`, `tools/test_core_agnostic.py`, `.claude/hooks/check-core-agnostic.{ps1,sh}`, wiring em `.claude/settings.json` + `sync-global.ps1`, sentinela em `.agent/skills/qa-critic/SKILL.md` (regra #5).
- Verificação: `python tools/check_core_agnostic.py` → PASS (núcleo limpo) **E** `python tools/test_core_agnostic.py` → PASS (canário com efeito).

---

## EMENDA v1.22.x — Tier SENSÍVEL (anti-vazamento de dado de cliente)

- Status: **Emendado** (§Implementação estendida; decisão original intacta — política SUPLANTA×EMENDA do ADR-011)
- Data: 2026-05-31 · Gatilho: **incidente de vazamento confirmado** — identificadores de cliente/caso/repo (de dogfood em casos reais) tinham vazado para o núcleo, ADRs, CHANGELOG, history e hooks num repositório que estava **público**. Registro completo (com dados reais): `docs/_private/INCIDENTE-VAZAMENTO-2026-05-31.md`.

**Causa-raiz:** o linter original tinha **categoria e escopo errados** para este vazamento:
1. A denylist (`agnostic-denylist.txt`) só listava **normas regulatórias** — nomes de cliente/caso/repo **não são normas**, então o linter nunca os procurou.
2. O escopo excluía `docs/**` (correto p/ norma-como-exemplo; **errado** p/ identificador de cliente, que não pode vazar nem como exemplo).
3. Falso-negativo institucionalizado: o linter "passava" porque não olhava para esses tokens.

**Arquitetura escolhida — fonte privada full + distribuição limpa gerada (one-way):**
A **fonte privada** (este repo) mantém TUDO em full: nomes reais visíveis, histórico, `docs/_private/`
— é o cofre de **acesso total** do dono. A **distribuição pública** é um **artefato GERADO**
(anonimizado, sem `docs/_private/`, sem história), nunca editado à mão. O link é um **flow
automático** (GitHub Action) que regenera e publica a cada push.

**Emenda (régua §0 — estende o existente, não cria mecanismo novo):**
- **Tier SENSÍVEL** novo: `tools/sensitive-denylist.txt` (identificadores de CLIENTE/CASO/REPO),
  escopo **repo inteiro** (exceto `.git/`, `docs/_private/`, os denylists/map e binários). Sentinela
  `lint-sensitive:allow`. **AUTOR ≠ CLIENTE:** o nome do mantenedor (atribuição legal) NÃO entra.
- **OPT-IN (`--sensitive`)** — o tier sensível é o **gate de EXPORT**, NÃO de boot: a fonte privada
  carrega nomes por design, então rodá-lo no boot só geraria ruído. O boot (hooks `check-core-agnostic`)
  segue só no tier **norma**; o canário cobre os dois mecanismos.
- **Pipeline determinístico** (torna o "limpo" AUTOMÁTICO, não edição manual):
  `tools/anonymize-map.txt` (regras regex→genérico ordenadas) → `tools/anonymize.py` (aplica) →
  `tools/export-clean.py` (copia, strip `docs/_private`, anonimiza, **GATE `--sensitive`**, strip infra) →
  `.github/workflows/publish-clean.yml` (force-push da árvore limpa ao repo público a cada push na main).
  Se um caso novo traz um token não-mapeado, o **gate falha o build** — o dono adiciona 1 regra ao map.
- **Risco (f) novo:** denylist/map são **não-exaustivos** — mas o gate `--sensitive` no export é o
  backstop determinístico (nada publica sem passar). Regra #5 semântica do qa-critic continua de apoio.
