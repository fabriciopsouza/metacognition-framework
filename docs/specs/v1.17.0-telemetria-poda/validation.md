# Validation — v1.17.0 Telemetria mínima + poda (gate binário)

| # | Critério | Como verificar | V/F |
|---|---|---|---|
| V1 | ADR-017 é ADR-pai com 2 decisões (17-A blame, 17-B poda) sob coletor único | leitura | — |
| V2 | 17-A define SÓ 2 métricas (junção-origem + qa_rounds); reprova dashboards/latência/%verde | leitura | — |
| V3 | 17-B define tally S/N + classe (salva-vidas/operacional/andaime) + poda só andaime N=5–10 | leitura | — |
| V4 | `salva-vidas` nunca poda por desuso (gera nota); sem classe = conservador (salva-vidas) | leitura | — |
| V5 | Fronteira de coletor único explícita: 17-A=entre junções; 17-B=ao longo de sessões; mesmo artefato | leitura | — |
| V6 | matriz de relevância instrumentada REPROVADA explicitamente (P7) | ADR-017 §"Decisão 17-B"/§Alternativas-2 + §Régua §0 dizem "matriz...rejeitada/reprovada" | — |
| V7 | `_shared/observability` estendido (não módulo novo); coletor = `history.md ## Telemetria` | git diff + grep | — |
| V8 | `history.md` tem seção `## Telemetria` com 17-A e 17-B populados | grep | — |
| V9 | checkpoint.md tem gancho de telemetria+poda apontando para observability | grep | — |
| V10 | classe reusa o campo do contrato ADR-013 (não cria campo novo) | cross-ref | — |
| V11 | Régua §0: EMENDA (P10/P11), nenhum dashboard, nenhum coletor duplicado, agnóstico | PC | — |
| V12 | Tally autorreportado marcado falível [DESCONHECIDO]; N=5–10 marcado [INFERIDO] | grep | — |
| V13 | (regressão) Contrato Onda 0: 7/7 PASS | `python tools/validate_skills.py` | — |
| V14 | Poda operacionalizável: tally tem contador `sem-disparo:K` (ADR + observability + history) | grep "sem-disparo" | — |
| V15 | Coletor único = mecanismo (transcrição de span no checkpoint), não só política | leitura ADR §Fronteira | — |
| V16 | 17-A blame-de-rewind honestamente marcado [não-exercido nesta onda] (P11) | grep "não-exercido" history | — |
| V17 | checkpoint.md aponta p/ observability (não relista classes/N — anti-stale) | leitura | — |

