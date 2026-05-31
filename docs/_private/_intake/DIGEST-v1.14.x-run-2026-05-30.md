# Digest — Run autônomo v1.14.x "da prosa ao mecanismo" · 2026-05-30 · faixa 🔴 (~93%, auto-compact iminente)

> Dogfood do ADR-016: este é o digest de continuação (Pacote de handoff §P14 + carimbo). A próxima
> sessão/contexto retoma SÓ por este arquivo + git. Modo: **autosuficiente** (reverter a avançado no fim).

## [P14] Artefato consumível
Série v1.14.x em 5 ondas (PRs stacked). Branches preservadas, NENHUM merge (gate humano = dono).

## [P14] Localização (repo: github.com/fabriciopsouza/metacognition-framework)
- Onda 0 v1.14.0 `feat/v1.14.0-contrato-minimo-skill` → **PR #11** (base main). ADR-013. ✅ qa-critic R1 corrigido + CHANGELOG.
- Onda 1 v1.15.0 `feat/v1.15.0-allowlist-enforcement` → **PR #12** (base Onda 0). ADR-014/015. ✅ qa-critic 2 rounds APROVADO_LIMPO + CHANGELOG.
- Onda 2 v1.16.0 `feat/v1.16.0-compaction-digest` → tip `4117c9c` pushed (base Onda 1). ADR-016. ✅ qa-critic R1 (1 ALTO checkpoint + 2 MÉDIO + 4 BAIXO) corrigido. **FALTA criar PR (gh pr create base=feat/v1.15.0).**
- main = `3267628` (v1.13.0), intacto.

## [P14] Acesso
Modo autosuficiente (settings.json bypassPermissions). framework-mode.json com backup .modeswap.bak.
force-push está DENY (guard-rail) — usar reset --soft + commit novo p/ ff.

## [P14] Prompt pronto-para-colar (próxima sessão)
"Retomar run v1.14.x na branch feat/v1.16.0-compaction-digest (commit 4117c9c). FALTA: (1) criar PR
Onda 2 (gh pr create --base feat/v1.15.0-allowlist-enforcement); (2) ONDA 3 v1.17.0 telemetria+poda
— ADR-017 já ESCRITO mentalmente, ver digest §pesquisas: branch feat/v1.17.0-telemetria-poda já
criada, observability §Telemetria já EDITADO (verificar com grep '17-A' _shared/observability), falta
ADR-017 + history.md ##Telemetria + checkpoint gancho + spec + commit + qa-critic + PR; (3) ONDA 4
v1.18.0 QA 1-turno steelman→ataque→veredito + heterogeneidade (ADR-018/P6) — só edita qa-critic
SKILL + _shared; (4) method-audit notes (start-session git-fetch, buffer/pwsh — já em memory/); (5)
REVERTER modo p/ avançado (editar ~/.claude/framework-mode.json mode=avancado, NÃO apagar branches);
(6) crítica final + gaps vs plano. Fonte: docs/_intake/v1.14.x-digest-pesquisas.md (lastro P1-P7; movido de docs/specs/ em 2026-05-30).
Régua §0, agnóstico, honestidade ide≠chat. qa-critic sempre isolado+heterogêneo (model:sonnet).
AMBIENTE: pwsh NÃO no PATH bash (só via Python subprocess shutil.which); batch grande cancela em
cascata → sequencial + commit cedo; buffer de tool-results atrasa (dump→Read)."

## [P14] Pendências e premissas herdadas
- Ondas 3 e 4 NÃO implementadas. Onda 3 parcialmente (branch+observability edit).
- Bloqueadores §6 do plano: tratados como "implementar c/ default + documentar [DESCONHECIDO]" (escolha do dono).
- F star-commands: NÃO decidir (sem pesquisa).

---
## Extensões de compaction
- **Decisões:** 5 ondas = 5 MINOR (v1.14→v1.18), branches stacked, PRs sem merge — [CONFIRMADO, escolha do dono].
- **Detalhes caros:** validador `tools/validate_skills.py` (stdlib, 7/7 PASS); canary `tools/test_effect_gate.py` (auto-guarda); hook `tools/hooks/effect-gate.ps1` (3 checks rm). ADR-017 = ADR-pai 2 decisões (17-A blame só 2 métricas / 17-B tally+classe+poda Chesterton N=5-10), coletor único = history.md ##Telemetria.
- **Nomenclatura:** Onda0=contrato, Onda1=allowlist+enforcement, Onda2=compaction+digest, Onda3=telemetria+poda, Onda4=QA 1-turno. classe∈{salva-vidas,operacional,andaime}. E1-E6/T1-T3.
- **5 arquivos recentes:** docs/adr/016, .agent/workflows/checkpoint.md, _shared/observability/SKILL.md, docs/_intake/v1.14.x-digest-pesquisas.md, CHANGELOG.md.
