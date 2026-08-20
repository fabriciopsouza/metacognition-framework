# QA-evidence — vitrine-sem-jargao-e-correcoes-do-qa-final

- **Data:** 2026-08-19T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | guia/web/index.html secao 00 | caso INVENTADO apresentado como fato consumado em pagina publica, sem lastro em lugar nenhum do repositorio. Removido por inteiro. Nunca chegou a um commit. |
| BAIXA | guia/web/index.html secao 00 | o mesmo paragrafo duplicava o bullet 'Alucina nomes de campo' duas linhas acima. A remocao fecha os dois achados. |
| INFORMATIVO | CHANGELOG.md + tools/model-policy.json | aviso da lacuna da branch e registro do model_ids conferidos contra bde8976 e git log -S; ambos factualmente corretos, sem amenizacao. |

## Verificacoes executadas (anti-fabricacao)

- r1: buscou lastro do caso alegado em history.md, docs/adr, docs/_private e git log --follow — zero
- r1: comparou o paragrafo 'o que nos surpreendeu' frase a frase com o ledger de QA do bloco anterior
- r1: conferiu balanceamento de tags (p 42/42, div 131/131, section 12/12) e ancoras 00..11
- r1: bateu as 4 causas citadas no aviso da branch contra o commit fundador bde8976
- r2: `git log --all -S` provou que o texto inventado nunca foi commitado
- r2: varredura integral da pagina por tempo verbal de fato consumado, com verificacao de fonte item a item
- r2: reauditou CHANGELOG e model-policy.json, que haviam mudado desde a r1
- canarios: test_marketing_claims PASS (6 numeros da vitrine batendo), test_overclaim_lexicon PASS (20/20 veneno, 10/10 honestas)
- suite completa: 80 PASS, 1 SKIP, 0 FAIL de 81
