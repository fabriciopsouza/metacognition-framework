# QA-evidence — adr-114-service-valuation-fechamento

- **Data:** 2026-08-31T00:00:00Z
- **Veredito (passou):** False
- **Recomendacao:** reprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | guia/web/index.html linha 256 + tools/test_marketing_claims.py | a frase de reconciliacao da vitrine se contradizia na propria frase (97 e 'trinta e nove' contra 98 e 40 medidos), e o gate dedicado passava porque so conferia presenca de substrings isoladas. Corrigido em duas metades: a frase, e uma checagem que le a frase como CONTA — provada por 3 mutacoes, incluindo a guarda contra a checagem virar decoracao se a redacao mudar. |
| ALTA | _shared/service-valuation/SKILL.md (front matter), docs/adr/114-*.md, CHANGELOG.md, docs/_private/service-valuation/HISTORICO-ENTREGAS.md, capabilities.json | '28x no preco' propagado do material de origem para 5 arquivos sem verificacao. 270.000/13.000 = 20,8; nenhum par das cifras citadas produz 28. Corrigido para o valor derivavel COM A CONTA A' VISTA em cada ocorrencia, e o canario passou a conferir a aritmetica das 6 razoes em 3 arquivos. A divergencia com a fonte ficou REGISTRADA no ADR, nao apagada. |
| BAIXA | capabilities.json | arquivo perdeu a newline final ao ser reescrito pelo autor. Restaurada. |
| BAIXA | _shared/service-valuation/SKILL.md | colisao de numeracao entre a Regra 12 da §1 e a secao ## 12. Nao ha ambiguidade de fato (o texto usa '§12' so para a secao), mas a Regra 12 diz 'no repositorio' sem apontar para a ordem de resolucao, ao contrario da Regra 8 que cita a secao explicitamente. Nota de estilo, nao ponteiro morto. |

## Verificacoes executadas (anti-fabricacao)

- critico rodou 6 mutacoes em copia sobre test_service_valuation.py — as 6 deram exit 1; baseline PASS
- critico refez a conta dos pisos a mao: 1,20x1,15x1,15x1,10 = 1,7457 -> 1,75, bate com o script
- critico rodou export-clean.py de verdade: _shared/service-valuation VIAJA, docs/_private/ NAO — premissa da decisao confirmada no mecanismo real, nao so no web_export.py
- critico rodou check_core_agnostic.py (PASS), test_web_export.py (PASS), test_shadow_write_guard.py (PASS)
- critico executou contar_vitrine do proprio auditor: {'total':98,'provadas':58,'fracos':40,'conformes':98} — provando 97/'trinta e nove' errados
- critico calculou 270000/13000 = 20.77 e 478/55 = 8.69, mostrando que o 8,7x confere e o 28x nao
- critico procurou a MEMORIA-CALCULO.md do caso H-01: so o TEMPLATE existe no repo — a fonte citada nao esta versionada
- autor, apos as correcoes: 3 mutacoes na frase da vitrine (97 de volta, 'trinta e nove' de volta, frase apagada) -> 3 exit 1
- autor, apos as correcoes: mutacao do 28x com a conta ao lado -> exit 1 com a mensagem apontando a divisao
- autor: run_canaries 86 PASS, 1 SKIP, 0 FAIL de 87
