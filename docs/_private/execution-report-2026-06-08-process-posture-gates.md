# Execution-report — bloco v1.51.0 (qa-evidence + posture-gate + hardening) · tier OWNER · privado

- **Tokens:** NÃO MEDIDO — sem telemetria de token exposta ao agente (dependência do host; ver LIMITS.md)
- **Tempo (wall-clock):** NÃO MEDIDO
- **Turnos:** sessão única, ~contínua
- **Arquivos tocados:** 18 (7 novos tools/canários, 6 docs/skills, capabilities.json+CAPABILITIES.md, ci.yml, history/CHANGELOG/README/vitrine)
- **Testes:** suíte de canários (objetivo: 0 FAIL pós release-artifact); 4 novos canários (qa_evidence, posture, context_budget, verify_hitl_proofs)
- **Rodadas de retrabalho:** 1 auto-revisão crítica (design flaw do shadow-skip pego antes do push)

## Placar gate × achado (quem pegou o quê)
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| 5 false-PASS nos gates v1.49/1.50 (substring de versão; placeholder 4 bytes; shadow 1-booleano) | qa-critic adversarial (subagente isolado, Sonnet) | os próprios gates — não tinham revisão adversarial na criação |
| Design flaw: shadow-skip por docs/_private faria qa-evidence/posture NUNCA disparar na CI | auto-revisão (eu, antes do push) | nenhum — corrigido para enforce-default |
| doc-intake não usado (li history inteiro) | DONO (provocou) | nenhum era prosa → agora context_budget |
| modo autosuficiente clobbado (settings={}) | DONO (relatou) | ensure-global-wiring (hook-gated, Kaspersky vetou) |

## Detecção: framework × humano (quem pegou o quê — mecanismo vs. revisão humana)
- **Mecanismo pegou:** orphan-canary (`test_capabilities`) barrou os 2 canários novos sem registro; `build_limits --check` validou a vitrine pós-bump.
- **qa-critic adversarial (subagente) pegou:** 5 false-PASS reais, provados com input adversarial — exatamente o valor que a sessão anterior (fast-mode, qa-critic 1×) deixou na mesa.
- **Eu (auto-crítica) peguei:** 1 — o design flaw do shadow-skip (raro: P11 diz que auto-detecção falha; aqui funcionou porque rastreei "este gate dispara mesmo na CI?").
- **Dono pegou:** 2 — doc-intake não-usado + regressão do modo autosuficiente. (Padrão recorrente P11: correções estruturais ainda vêm muito do dono.)

## Gaps (não-bloqueantes detectados — flagados, não silenciados)
- Enforcement pleno do context-budget exige hook PreToolUse(Read) — Kaspersky veta → fica doutrina (débito declarado).
- Itens 4/6 (hub) não exercidos: nenhum hub clonado nesta máquina; boot-scan wired mas não demonstrado contra hub real.
- `validate_owner_report` (estrito) diverge dos reports em prosa reais — drift validador↔report declarado como débito (não acoplei ao dev-dogfood para não false-FAIL).

## Melhorias (do framework/processo — adição passa pela régua §0)
- qa-evidence + posture-gate: convertem "qa-critic rodou" e "postura aplicada" de prosa→gate fail-closed (régua §0(c): destrava garantia inalcançável por prosa).
- Companion posture.md é lar ÚNICO; SKILL/checkpoint apontam (não duplicam).

## Boas práticas (o que funcionou — reutilizável)
- Rodar qa-critic adversarial ANTES de declarar pronto pegou 5 bugs reais; o artefato _meta/qa torna isso auditável.
- Commit atômico por bloco (A/B/C) — reversível isolado.
- Auto-pergunta "este gate dispara na CI?" pegou o design flaw — heurística a manter.

## Lições por skill (agnóstico de domínio — o que daqui serve a OUTRO projeto)
- dev: gate que depende de arquivo gitignored não enforça em CI — verificar o ambiente onde o gate roda, não só a lógica.
- discovery: fonte grande → fracionar (context_budget/doc-intake) antes de ler inteiro.
- architect: shadow-detection deve usar sinal POSITIVO (marker), não ausência de arquivo.
- qa-critic: input adversarial construído (temp dir, placeholder) > asserção verbal de false-PASS.
- docops: backfill retroativo = reconstruir da fonte canônica (CHANGELOG), append-only, rotulado.
