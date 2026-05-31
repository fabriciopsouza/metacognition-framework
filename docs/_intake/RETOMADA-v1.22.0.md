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
- [ ] ADR-027 + ensure-global-wiring.ps1 (self-heal) + wiring em bootstrap/sync-global/settings + disable-com-memória.
- [ ] ADR-028 + cláusula precedência output-style×processo em metacognition-core + disciplina de orientação no boot.
- [ ] ADR-029 + skill doc-intake + tool de parse/chunk + integração discovery.
- [ ] ADR-030 + consistency-gate.ps1 (version-sync + ADR-status-on-merge + checkpoint + contagens + unpushed).
- [ ] guia/RESILIENCIA-ACESSO.md.
- [ ] Housekeeping: flipar ADR-024/025/026 → Aceito; checkpoint v1.21.2 ausente.
- [ ] qa-critic adversarial (subagente Sonnet isolado).
- [ ] Dogfood (ensure-global-wiring + route-gate disparando).
- [ ] Version bump v1.22.0 + atualizar README/CHANGELOG/web/CLAUDE/AGENTS/history.
- [ ] Commit→PR→merge verificado→deletar branch→limpeza (remover este RETOMADA).

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
