# QA-evidence — b1-9-escada-anti-excesso

- **Data:** 2026-09-25T20:18:20Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inline: estudo do repositorio DietrichGebert/ponytail por agente de pesquisa so-leitura; decisao de adaptar a ideia sem o pacote (Node.js e cerca de 20 adaptadores)
- **RRC:** PASSA
- **Metodo-senior:** N/A: edicao de skill do proprio framework, sem fonte canonica regulada

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| CRITICO | .claude/agents/qa-critic.md + CHANGELOG.md | rodada 1: a regra de so-leitura era prosa apresentada como correcao da causa. Corrigido declarando-a PROSA no CHANGELOG, explicando por que o bloqueio generico barraria a sessao principal, e registrando a pendencia subagente-revisor-so-leitura com primeiro passo mensuravel. |
| MEDIA | docs/specs/plano-modo-planejado/PLANO.md | rodada 1: aceite do B1.9 citava canario de paridade de skill inexistente; reescrito com os tres canarios que existem e rodam. |
| BAIXA | CHANGELOG.md, PLANO.md | rodada 1: numero de adaptadores divergente (20 x 18); unificado. |
| BAIXA | .agent/skills/developer/SKILL.md, CHANGELOG.md | rodada 1: frase sugeria que o ADR-007 ja cobria codigo de projeto; reescrita como extensao nova deste bloco. |

## Verificacoes executadas (anti-fabricacao)

- python tools/test_capabilities.py -> PASS (revisora, rodadas 1 e 2)
- python tools/test_marketing_claims.py -> PASS, 102/41/61 batem com o site (revisora)
- python tools/test_audit_enforcement.py -> 37/37 (revisora)
- leitura de tools/hooks/effect_gate.py e tools/effect-rules.json: nenhum campo de identidade de subagente; deny generico barraria a sessao principal (revisora, confirma o argumento do CHANGELOG)
- grep por espelhos do checklist do qa-critic (Gemini/Copilot/Kiro): nenhum alem da skill e do subagente (revisora, rodada 1)
