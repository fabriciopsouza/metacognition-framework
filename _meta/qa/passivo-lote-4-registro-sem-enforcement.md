# QA-evidence — passivo-lote-4-registro-sem-enforcement

- **Data:** 2026-08-18T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** PASSA - o critico nao perguntou se a classificacao esta bonita, perguntou se algum rotulo mais fraco esconde um mecanismo que BLOQUEIA, que e a unica forma de este bloco ser fraude; e provou o achado ALTO reescrevendo a funcao em vez de opinar sobre ela
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| alto | tools/test_marketing_claims.py (autoteste_contagem) | CORRIGIDO E PROVADO. A fixture nao tinha caso com `mutacao` presente mas ESTRUTURALMENTE invalida, entao uma contagem ingenua (provadas = tem o campo mutacao) passava identica — o critico demonstrou reescrevendo a funcao. Acrescentada a 5a fixture (arquivo != mechanism, recusada por valida_mutacao) e provado que agora remover a validacao derruba o canario. |
| medio | tools/audit_enforcement.py (modo_provar) | CORRIGIDO E PROVADO (emenda 6). O modo materializa o HEAD, entao mecanismo/canario com mudanca nao-commitada rodava a versao ANTIGA e reportava 'mutacao obsoleta'/'continuou VERDE' — acusando a MUTACAO por um problema de ESTADO DO REPO. O dano nao e o falso-positivo: e o habito de descartar [FALHA] como 'coisa do HEAD'. Agora e SKIP declarado com o motivo e o que fazer, guardado pelo caso (i-m) do canario do auditor. |

## Verificacoes executadas (anti-fabricacao)

- run_canaries: 78 PASS / 1 SKIP / 0 FAIL (79)
- audit_enforcement --passivo: 90 conformes, 0 no passivo, 0 novas sem prova
- --provar sem --id contra HEAD: 49/52 PROVADO; os 3 restantes sao os canarios alterados NESTE bloco (nao-commitados), verificados a mao com restauracao byte-a-byte
- varredura das 38 capacidades nao-fail-closed atras de decision:deny e sys.exit(2): zero ocorrencias — nenhuma bloqueia de fato sob rotulo mais fraco
- mechanism corrigido em oracle-bias-canary/sycophancy-canary/discovery-eval conferido contra os imports reais dos canarios
- test_skill_contract.py novo: 5 fixtures nas duas direcoes, usando as MESMAS funcoes do validador real (nao reimplementacao)
- test_doc_intake.py: os 5 testes seguem executando mesmo com falha (try/except por teste); nao mascara
- vitrine recalculada: 52+0+38+0=90; 79 canarios bate com ls tools/test_*.py
