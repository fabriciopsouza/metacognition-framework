# QA-evidence — ADR-099 — metodo de validacao ponto a ponto com reporte para humano

- **Data:** 2026-08-02T23:04:47Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** vv1.76.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inline: escopo declarado pelo dono ao fim do bloco de validacao ('incorpore como um dos metodos... este e o metodo que deve valer para o framework agora'). Nao houve elicitacao separada: o requisito nasceu de OITO correcoes concretas do dono sobre um artefato real, cada uma nomeada nas secoes §2/§3/§6/§7/§9 da skill. Regulado/alto-risco: NAO (skill de metodo, nucleo agnostico). Handoff cross-sessao: SIM — a skill E o artefato de handoff.
- **RRC:** PASSA — ADR-099 Aceito com entrada no CHANGELOG [1.76.0]; README bumpado 1.75.0 -> 1.76.0; capabilities.json + CAPABILITIES.md regerados (77); qa-evidence este arquivo; checkpoint no history.md.
- **Metodo-senior:** aplicado: docs/adr/099-metodo-de-validacao-ponto-a-ponto-com-reporte-para-humano.md — ADR nova com contexto, decisao, regua §0 honesta (override declarado apos o gate derrubar a alegacao de porta (c)), alternativas rejeitadas com razao, consequencias e verificacao com pendencia declarada.

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| critico | docs/adr/099-metodo-de-validacao-ponto-a-ponto-com-reporte-para-humano.md §Regua §0 | A1 — ADR alegava regua §0 pela porta (c); os 3 predicados eram falsos (100% aditivo, zero eval, zero fusao). Corrigido: override explicito do dono (ADR-051) com debito e condicao de quitacao. |
| alto | capabilities.json | A2 — enforcement 'advisory' afirmava avisador inexistente; precedentes edge-case-hunter/party-mode/readiness-gate usam 'prose'. Corrigido para 'prose'. |
| alto | _shared/validation-reporting/SKILL.md §0 | A3 — sem ponte para confidence-classification ('unica definicao do ecossistema') nem para high-stakes-gate/risk_score: dual-SSoT latente. Corrigido com §0 nova declarando os eixos (status do DADO x origem da AFIRMACAO). |
| alto | _shared/validation-reporting/SKILL.md §6 | A4 — materialidade sem escopo de nivel contradizia a tolerancia zero do nivel A e tensionava o fail-closed da §5; permitiria aprovar divergencia de dinheiro sub-limiar. Corrigido: §6 restrita a niveis B/C, residual vira item da lista §5. |
| alto | _shared/validation-reporting/SKILL.md §8 | A5 — 'ressalva' indefinida e NAO CONFERIDO ausente da tabela de veredito: ressalva podia mascarar nao-conferido, o pecado que a §2 proibe. Corrigido: definicao fechada de ressalva + nivel A nao conferido => INCONCLUSIVO + veredito declara cobertura por nivel. |
| alto | _shared/validation-reporting/SKILL.md §9 | A6 — a decisao 'formato recomendado, conteudo obrigatorio' vivia so no ADR, que sessao futura nao carrega; a SSoT prescrevia planilha e .xlsx como norma. Corrigido no texto normativo da §9; nome ESTAVEL em vez de extensao hardcoded. |
| medio | _shared/validation-reporting/SKILL.md | A7 — frontmatter sem version/source/last_review, fora do padrao das skills _shared. Corrigido. |
| medio | CHANGELOG.md | A8 — CHANGELOG marcava [CONSOLIDADO] contradizendo o proprio ADR ('metodo provado uma vez; generalizacao INFERIDO'). Corrigido para [EMERGENTE]. |
| baixo | _shared/validation-reporting/SKILL.md + ADR-099 | A9 — overclaims aritmeticos: 'correcoes nomeadas em cada secao' (falso para §4/§5/§8/§10) e 'dez secoes' seguido de lista com nove. Corrigido. |
| baixo | _shared/validation-reporting/SKILL.md §2 | A10 — §2 'derivado de campo validado = nao se aplica' podia engolir o B-DEC que a §3 manda medir. Corrigido com clausula distinguindo derivado-sem-ressalva de derivado-com-diferenca-tolerada. |
| baixo | _shared/validation-reporting/ | DEBITO ACEITO, nao corrigido: a skill nao tem canario proprio — conformidade avaliada por leitura, o que viola a §10 dela mesma. Declarado em tres lugares (ADR §Regua §0 e §Verificacao, CHANGELOG, note do registro) e refletido no status PARTIAL / enforcement prose. |

## Verificacoes executadas (anti-fabricacao)

- check_core_agnostic.py -> PASS (norma): a skill nao cita cliente, produto, vendor nem norma de dominio
- test_capabilities.py -> PASS: 77 capacidades, registry honesto, indice em sync, PROVIDES tem canario
- test_consistency_closing.py -> PASS: 95 ADRs, 0 duplicatas, 0 entregue-mas-Proposto, todo version-claim com heading
- build_capabilities.py -> CAPABILITIES.md regerado (77 capacidades)
- README bumpado 1.75.0 -> 1.76.0 (version-sync)
- qa-critic heterogeneo (fable, subagente isolado, modelo != autor): 1a rodada NAO LIBERADO; 10 achados corrigidos, 1 aceito como debito declarado
