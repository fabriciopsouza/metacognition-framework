# QA-evidence — regra-07-nao-abandonar-trabalho

- **Data:** 2026-08-20T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | docs/adr/112-nao-abandonar-trabalho-em-curso.md, secao Regua §0 | alegava porta (a) — absorcao de regra que nunca esteve no repositorio. Adicao pura com justificativa falsa. Corrigido: alegacao honesta como override do dono, e absorcao tornada real. |
| BAIXA | CHANGELOG.md | gramatica quebrada e ASCII sem acento destoando do arquivo. |

## Verificacoes executadas (anti-fabricacao)

- grep por 'STOP explicito' em .agent, _shared, docs, CLAUDE.md e AGENTS.md — zero, provando que a regra nunca esteve no repo
- localizou a regra real no diretorio de memoria do Claude Code, fora do git
- rodou check_rules_parity: a guarda de ponteiro morto cobre .agent/rules/07 citado no CLAUDE.md
- conferiu numeracao de ADR 110/111/112 sem colisao
- autor apos a correcao: run_canaries 80 PASS, 1 SKIP, 0 FAIL
