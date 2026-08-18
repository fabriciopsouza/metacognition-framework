# QA-evidence — release-1.90.0-procedencia-do-veredito

- **Data:** 2026-08-18T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** v1.90.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** o furo foi MEDIDO antes de ser atacado: inspecionei os transcripts para descobrir quais fatos o harness grava e o agente nao produz, e so entao desenhei a prova em cima deles
- **RRC:** PASSA - o critico reprovou cinco vezes e a cada uma o conserto foi mais estreito que a classe; a 6a so passou quando o mecanismo parou de adivinhar e virou contrato
- **Metodo-senior:** file-first nos transcripts antes de afirmar o que dava para provar; limites declarados no codigo e no ADR em vez de propriedades fingidas; e aceitar a recomendacao de NAO perseguir o residual

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| alto | tools/verify_qa_attestation.py | CORRIGIDO em 5 rodadas: leitura da conclusao abandonou heuristica de posicao e passou a contrato (sentinela unico) com ambiguidade resolvida por contagem. |
| medio | tools/verify_qa_attestation.py | LIMITE DECLARADO por recomendacao do critico: exemplo que e a ultima coisa escrita nao e distinguivel de conclusao por nenhuma regra de forma. Nao sera perseguido. |
| medio | tools/verify_qa_attestation.py | DIVIDA com criterio de monitoramento: sem_leitura e ressalva tem o mesmo custo (exit 3). Se sem_leitura seguir majoritario depois de a norma pegar, e evasao e nao legado. |

## Verificacoes executadas (anti-fabricacao)

- 6 rodadas com reproducao em codigo, cada vetor derrubado virou caso de canario provado por reversao
- 18 vereditos com procedencia provada contra o relatorio real do critico
- run_canaries: 77 PASS / 1 SKIP / 0 FAIL apos o veredito de release
- audit_enforcement: 91 conformes, 0 no passivo, 0 novas sem prova
