# QA-evidence — release-1.79.0-project-docs-e-squad-gate

- **Data:** 2026-08-13T14:03:05Z
- **Veredito (passou):** False
- **Recomendacao:** reprovar
- **Fecha release:** v1.79.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inline: CAPABILITIES.md e capabilities.json lidos antes de afirmar gap; nucleos vizinhos inspecionados; precedentes de registro conferidos
- **RRC:** PASSA — o critico rodou greps e canarios proprios em vez de aceitar as alegacoes do autor
- **Metodo-senior:** aplicado: docs/adr/102-padrao-do-conjunto-documental-de-projeto.md

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| bloqueante | B1 | regua §0 nao resolvida: adicao pura sem ADR nem override escrito — CORRIGIDO em docs/adr/102 — override explicito do dono com condicao de quitacao |
| bloqueante | B2 | docops dizia 'nao fecha bloco' sem nenhuma mecanizacao (ADR-085/P15) — CORRIGIDO — rebaixado para advisory, com o debito nomeado |
| grave | G3 | capabilities com enforcement 'manual' sem script; reincidencia do achado A2 do ADR-099 — CORRIGIDO — PARTIAL/prose/test=None conforme precedente |
| medio | M4 | sobreposicao nao declarada com validation-reporting — CORRIGIDO — ponte no §0 |
| medio | M5 | tabela §3 com mais autoridade que a evidencia (portes INFERIDOS revelados so no §8) — CORRIGIDO — marca inline por linha |
| menor | m6 | sabor residual de dominio nos exemplos — CORRIGIDO — generalizado; zero ocorrencias remanescentes |
| bloqueante | B1-r2 | passo de CI quebra (exit 128) antes de o gate rodar, em todo PR — CORRIGIDO: checkout fetch-depth 0 + base.sha do evento + --paths-from |
| bloqueante | B2-r2 | evidencia sem escopo libera qualquer mudanca futura (auto-liberacao permanente) — CORRIGIDO: escopo_paths obrigatorio; veredito sem escopo nao conta (fail-closed) |
| grave | G3-r2 | _release_junction_closed casava versao por substring, sem teste — CORRIGIDO: match ancorado + 6 testes novos |
| medio | M4-r2 | $PATHS sem aspas no CI — CORRIGIDO: --paths-from (imune a espaco e a limite de argv) |
| medio | M5-r2 | SKILL.md §8 afirma enforcement 'manual' contradizendo capabilities.json ('prose') — CORRIGIDO |
| medio | M6-r2 | condicao de quitacao do ADR-102 fora do '## Em aberto' do history.md — CORRIGIDO |

## Verificacoes executadas (anti-fabricacao)

- leitura de CLAUDE.md e AGENT-FRAMEWORK.md (regua §0, ADR-072/073, agnosticismo)
- python tools/check_core_agnostic.py -> PASS
- grep em tools/ por 'project-docs' e 'teste binario' -> zero ocorrencias (base do achado B2)
- comparacao com precedentes de registro em capabilities.json (validation-reporting, readiness-gate, edge-case-hunter)
- leitura dos nucleos vizinhos (_shared/traceability, confidence-classification, validation-reporting, doc-intake, output-format) para caçar duplicacao
- git diff --stat contra main para medir adicao pura (221 linhas novas x 13 de ponteiro)
- leitura de _meta/qa/adr-099-*.md para checar reincidencia de defeito ja corrigido
- squad_gate rodado nos paths do bloco ANTES e DEPOIS da correcao da matriz: antes "papeis exigidos: nenhum"; depois BLOQUEADO fail-closed; com evidencia atestada, OK
