# ADR 027 — Roteamento determinístico (route-gate) + wiring global self-heal (prosa→mecanismo da entrada)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: entrada determinística (v1.22.0) · Tipo: novo (2 hooks + self-heal + wiring de projeto/global)
- Relaciona: ADR-006 (auto-boot global owner/marker-gated), ADR-005 (modos de execução — o clobber veio do mode-apply autosuficiente), ADR-025 (proteção de autoria transparente — a instalação anuncia o que wira), CLAUDE.md §Roteador.

## Contexto

**Causa-raiz confirmada por inspeção (relato `RELATO-FRAMEWORK-autorrevisao.md`, sessão AIVI, 2026-05-31):**
um agente executou cálculo de indicador **regulado/financeiro SEM rotear** pelo framework — sem
declarar rota, sem PMO, sem `high-stakes-gate`. Duas falhas independentes se somaram:

1. **Roteamento era PROSA, não mecanismo.** A instrução "classifique contexto×complexidade e roteie"
   vivia no `CLAUDE.md` (declarativa). Dependia do modelo *lembrar* de rotear, competindo com (a) o
   viés de "progredir na tarefa" e (b) a persona de output-style injetada no SessionStart. [CONFIRMADO]
2. **Auto-boot global estava DESLIGADO.** O `~/.claude/settings.json` global estava **sem a chave
   `hooks`** — clobber do mode-apply autosuficiente (ADR-005 §5 manda "preservar hooks", mas isso era
   PROSA; o disco mostrou zero hooks). Sem wiring global, abrir o Claude em qualquer pasta não-framework
   dispara **zero hooks**. [CONFIRMADO por inspeção do settings.json]

Diretiva do dono: *"nada importante em prosa → tudo vira ferramenta; ISSO NÃO PODE FALHAR (estou divulgando)."*

## Decisão (1 frase ativa)

Mecanizar a entrada em duas camadas: **(a) `route-gate.ps1/.sh`** — hook `UserPromptSubmit` **universal**
(independe de git/owner/marker) que injeta lembrete de rota 1×/sessão, fail-open; e **(b)
`ensure-global-wiring.ps1`** — self-heal hook-preserving chamado pelo `sync-global.ps1` (que roda do
settings.json de PROJETO, versionado e estável) para **re-afirmar a wiring global a cada abertura do
repo-framework**, derrotando o clobber de forma mecânica — mais **disable-com-memória** (session.lock
enriquecido + oferta de reativação no boot) preservando a soberania do usuário.

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** Roteamento continua prosa; clobber global continua. **Rejeitada — é o gap que causou o incidente.**
2. **Instalador one-shot que reescreve o settings global.** Prós: simples de pensar. Contras: não auto-cura
   (o próximo clobber do mode-apply re-quebra); exige o usuário re-rodar; é *snapshot*, não *mecanismo*. **Rejeitada como solução principal** — vira débito futuro (registrado: decisão travada #3).
3. **route-gate como `PreToolUse` (bloqueante) em vez de `UserPromptSubmit` (injeção).** Prós: força a rota. Contras: um gate de entrada que BLOQUEIA trava o usuário em qualquer falha — viola a régua de fail-open e o princípio anti-loop. **Rejeitada** — escolhemos injeção fail-open (lembra, não tranca).
4. **self-heal via hook próprio no SessionStart global.** Contras: o próprio hook global pode ter sido clobberado (galinha-e-ovo). **Rejeitada** — o ponto de Arquimedes é o settings.json de PROJETO (versionado, imune ao clobber do global); por isso o `sync-global` chama o `ensure-global-wiring`.

## Consequências

**Positivas:** roteamento deixa de depender de memória do modelo (mecanismo determinístico); o clobber do
mode-apply é curado automaticamente a cada abertura do repo-framework (idempotente, hook-preserving, com
backup `.heal.bak` + validação JSON antes de gravar); universal (route-gate dispara em qualquer pasta, não
só repos do owner); soberania preservada (locks desativam com memória + oferta de reativação).
**Negativas:** mais dois hooks para manter; o route-gate injeta em todo 1º prompt substantivo (mitigado:
marker por `session_id`, triviais filtrados, fail-open silencioso). A cura do clobber só acontece quando o
repo-framework é aberto (mitigado: é o repo que o dono mais abre; e o `sync-global` roda no SessionStart dele).
**Riscos:** se o schema do `UserPromptSubmit`/`additionalContext` mudar no Claude Code, o route-gate degrada
para no-op (fail-open) — re-validar em upgrade. [DESCONHECIDO não-bloqueante] estabilidade do contrato de hooks entre versões.
**Escopo de plataforma [CONFIRMADO]:** o **auto-wiring** (`ensure-global-wiring.ps1`, chamado pelo `sync-global.ps1`)
é **Windows/PowerShell** — como toda a camada de hooks deste repo (settings.json referencia `.ps1`). O `route-gate.sh`
acompanha para **setup manual em Linux/Mac**, mas **não é wirado automaticamente** (não há equivalente `.sh` do
ensure-global-wiring). Usuário Unix instala o hook à mão no seu `settings.json`. Fonte dos `.ps1` gravada com **UTF-8 BOM**
(PS 5.1 lê fonte sem-BOM em ANSI e o não-ASCII vira mojibake no contexto injetado — lição compartilhada com ADR-030).

## §disable-com-memória (soberania do usuário)

O usuário pode silenciar o framework por projeto (`​.claude/session.lock`) ou global (`~/.claude/session.lock`).
Para que a desativação tenha **memória** e o usuário não esqueça que desligou:

- **Quando (read-only):** o boot lê o `CreationTime` do lock (filesystem) — sem escrever no arquivo do usuário.
- **Por quê (opcional):** se o lock contiver uma linha `reason: <motivo>` (ou qualquer texto), o boot a exibe.
- **Oferta de reativação:** ao detectar um **project-lock**, o `inject-start-session-global` emite uma nota
  curta (additionalContext + systemMessage): *"squad desativado neste projeto desde X (motivo: Y) — reative
  deletando `.claude/session.lock`"*. Não faz boot completo (respeita o opt-out); apenas lembra + oferece.
- **Global-lock** permanece silencioso (opt-out amplo e consciente; oferecer em todo projeto seria ruído).

Teste binário: o usuário reabre um projeto que silenciou semanas atrás → **sabe que silenciou e como religar**
sem precisar caçar documentação.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.22.0-entrada-deterministica` · `2026-05-31` · grep `route-gate` / `ensure-global-wiring`
- Artefatos: `tools/hooks/route-gate.ps1` + `.sh` (hook UserPromptSubmit, fail-open, 1×/sessão por `session_id`);
  `tools/hooks/ensure-global-wiring.ps1` (self-heal hook-preserving, exit 0/10/1, backup `.heal.bak`);
  `.claude/hooks/sync-global.ps1` (espelha repo→`~/.claude` + chama ensure-global-wiring); `bootstrap.ps1`
  (DRY via ensure-global-wiring); `.claude/settings.json` de projeto (UserPromptSubmit→route-gate);
  `.claude/hooks/inject-start-session-global.template.ps1` (§disable-com-memória: oferta de reativação no project-lock).
