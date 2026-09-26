# QA-evidence — b4-circuit-breaker-estilo

- **Data:** 2026-09-26T03:28:22Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inline: pedido do dono de 25/09 (circuit breaker, debitos, comandos de sessao, estilo, fontes em arquivo) + conciliacao 'plano aprovado nao expira'; plano B4 aprovado com D1-D3
- **RRC:** PASSA
- **Metodo-senior:** N/A: mecanismo do proprio framework

## Substitui vereditos anteriores deste bloco

> **ATENCAO: este veredito substitui uma REPROVACAO.** Leia os antecedentes antes de tratar o bloco como aprovado.

- rodada 1 · 2026-09-26T03:14:39Z · **corrigir** · sha `f481329f84f9` · agentId `aa6d78150a6035586`
  - cobria 6 caminho(s): .claude/global/CLAUDE-global.md, tools/qa_evidence.py, tools/test_qa_evidence.py, tools/check_field_mapping.py …
- rodada 2 · 2026-09-26T03:22:33Z · **corrigir** · sha `f481329f84f9` · agentId `ab67c3c3bc4cbf5b7`
  - cobria 4 caminho(s): tools/qa_evidence.py, tools/test_qa_evidence.py, tools/check_field_mapping.py, docs/adr/118-circuit-breaker-de-qa-comandos-de-sessao-e-estilo.md

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| MEDIA | 5 arquivos com a frase do limite | r3: frase identica duplicada em 5 arquivos; reduzida a 1 linha de referencia ao ADR-118 (edicao pos-rodada: so texto, sem codigo). |
| BAIXA | tools/qa_evidence.py destrava_breaker | r3: tokens curtos e data real antiga destravam; limite declarado no ADR-118 e fixado em teste (14o caso). |

## Verificacoes executadas (anti-fabricacao)

- test_qa_evidence (14 casos do breaker), test_spec_unico, test_rules_parity (14/14), test_capabilities, test_consistency_closing, test_marketing_claims -> PASS (revisora r3 e autor)
- revisora r3: bypasses da r2 (99/99/9999, 'x'*20) recusados; casos legitimos gravam; aprovacao entra com breaker armado
- revisora r2: mutacao registrada qa-circuit-breaker aplicada numa copia -> canario falha com a string esperada; 101 artefatos reais lidos sem erro
- autor: 4 sabotagens (D1, D2, regex do mapeamento, clausula plano-nao-expira) pegas pelo motivo declarado
- fotografia dos 4 gates de especificacao nas 11 especificacoes antigas: 0 diferencas
