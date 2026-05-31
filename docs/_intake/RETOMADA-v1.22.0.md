# RETOMADA — v1.22.0 (entrada determinística + consistency-gate + doc-intake)

> **Propósito:** salvaguarda de recuperação para execução autônoma noturna (2026-05-31 →).
> Se a sessão cair (web/tokens/PC), abra a branch `feat/v1.22.0-entrada-deterministica`,
> leia este arquivo e cole o **PROMPT DE RETOMADA** abaixo numa sessão nova.
> Este arquivo é atualizado a cada artefato concluído e **pushado** ao origin.
> **É transiente** (`docs/_intake/`): será removido no fechamento (consistency-gate).

## Contexto (por que esta sessão existe)
- Gatilho: relato `RELATO-FRAMEWORK-autorrevisao.md` (sessão AIVI) — o agente executou tarefa
  regulada/financeira **sem rotear** pelo framework. Causa-raiz confirmada por inspeção:
  roteamento era **prosa** (CLAUDE.md), não mecanismo; e o auto-boot global estava **desligado**
  (settings.json global sem `hooks` — clobber do mode-apply autosuficiente).
- Diretiva do dono: "nada importante em prosa → tudo vira ferramenta; ISSO NÃO PODE FALHAR
  (estou divulgando)". Modo **autosuficiente total**. Autorizado ir até **commit → PR → merge →
  fechar branch → limpeza** (override explícito do default "parar no PR", só nesta sessão).

## Decisões TRAVADAS (não re-perguntar)
1. **Escopo:** 027+030 plenos; 028+029 podem ser ADR+stub se faltar fôlego. 029 = skill+tool funcional.
2. **route-gate:** universal global (UserPromptSubmit), independe de git/owner/marker.
3. **Instalação:** bootstrap 1× + **auto-heal** agora; instalador one-shot = débito futuro.
   Desativável por projeto com memória (session.lock enriquecido) + reativação oferecida no start.
   Install **transparente** (anuncia o que wirou + como desativar — liga ADR-025).
4. **doc-intake (E):** parse determinístico (pdf/docx/xlsx/pptx/md/txt) → chunk → manifesto, **SEM
   embeddings** (offline/agnóstico; RAG-vetorial = ADR futuro com dep externa declarada).
5. **Resiliência de acesso (G):** doc `guia/RESILIENCIA-ACESSO.md` (recovery de CONTA GitHub é a
   proteção real, não a key local; push cedo) + dimensão "commits não-pushados" no consistency-gate.
6. **Merge/segurança:** verificar `gh pr view --json mergedAt` ANTES de deletar branch (incidente #25).

## Plano (4 ADRs) e ESTADO
- [x] route-gate.ps1 + route-gate.sh (tools/hooks/) — hook UserPromptSubmit, fail-open, 1x/sessão.
- [x] ensure-global-wiring.ps1 (self-heal hook-preserving) + sync-global mirror/heal + bootstrap DRY + project settings (UserPromptSubmit->route-gate).
- [x] ADR-027 doc (docs/adr/027-*.md) + disable-com-memória (enriquecer session.lock c/ timestamp+motivo + reativação oferecida no inject hook). — commit 0310c22
- [x] ADR-028 + cláusula precedência output-style×processo em metacognition-core (nível 7) + nota inviolável.
- [x] ADR-029 + skill doc-intake (_shared/) + tool doc_intake.py + canário (4 testes) + integração discovery.
- [x] ADR-030 + consistency-gate.ps1 (6 dimensões: version-sync, adr-status, checkpoint, contagens-dup, unpushed, transients; UTF-8 BOM; validado por dogfood).
- [x] guia/RESILIENCIA-ACESSO.md (recovery de conta > key local + push cedo + gate unpushed). Link no README pendente p/ item bump.
- [ ] Housekeeping: flipar ADR-024/025/026 → Aceito; checkpoint v1.21.2 ausente.
- [ ] qa-critic adversarial (subagente Sonnet isolado).
- [ ] Dogfood (ensure-global-wiring + route-gate disparando).
- [ ] Version bump v1.22.0 + atualizar README/CHANGELOG/web/CLAUDE/AGENTS/history.
- [ ] Commit→PR→merge verificado→deletar branch→limpeza (remover este RETOMADA).

## ATIVAÇÃO (reload) — por que e como (vale p/ QUALQUER usuário)
O `defaultMode: bypassPermissions` (modo autosuficiente) só entra em efeito na **próxima
abertura** do Claude Code (limitação documentada — execution-modes §8). Numa sessão já
aberta, o Claude Code pede confirmação ("Make this edit? Yes/No") a cada escrita — isso é
a camada de permissão do harness, não o agente perguntando. Para rodar sem prompts:
1. Salve (já está tudo committed+pushed) e abra **uma nova sessão** do Claude Code
   ("+ New session"). Se os prompts persistirem, faça **reload do VS Code**
   (Ctrl+Shift+P → "Developer: Reload Window") ou feche/reabra o VS Code.
2. Na sessão nova, o SessionStart roda o sync-global → ensure-global-wiring (auto-heal) e
   o bypass fica ativo. Confirme: a primeira escrita NÃO deve mais pedir Yes/No.

## PROMPT DE RETOMADA (colar numa sessão nova, repo aberto)
```
iniciar. Estou retomando a branch feat/v1.22.0-entrada-deterministica.
Leia docs/_intake/RETOMADA-v1.22.0.md, reconcilie com os commits já pushados
(git log --oneline origin/main..HEAD) e CONTINUE do primeiro item [ ] pendente,
em modo autosuficiente total, até commit→PR→merge verificado→limpeza.
NÃO re-perguntar as decisões travadas. Ao final, remova este arquivo.
```

## Arquivos-fonte chave (já lidos — não re-explorar)
- bootstrap.ps1 §6 (wiring global, hook-preserving merge já existe p/ inject; falta route-gate).
- .claude/hooks/sync-global.ps1 (espelha repo→~/.claude; ponto de Arquimedes do self-heal).
- .claude/hooks/inject-start-session.ps1 + inject-start-session-global.template.ps1 (auto-boot owner/marker-gated).
- .claude/hooks/check-execution-mode.ps1 (emite additionalContext; o mode-apply via skill é quem clobberou).
- tools/hooks/mission-gate.ps1 (padrão de gate: lê stdin, fail-soft).
- _shared/metacognition-core/SKILL.md §Precedência (linhas 14-21 — editar p/ 028).
