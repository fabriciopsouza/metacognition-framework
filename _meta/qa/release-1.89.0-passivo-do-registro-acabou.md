# QA-evidence — release-1.89.0-passivo-do-registro-acabou

- **Data:** 2026-08-18T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar
- **Fecha release:** v1.89.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** o passivo foi lido capacidade a capacidade (docstring + sinais de bloqueio) antes de qualquer rotulo; a classificacao saiu da evidencia, e as 3 que resistiram viraram trabalho de canario em vez de rotulo conveniente
- **RRC:** PASSA - em cada rodada o critico foi apontado para a pergunta que poderia derrubar o bloco (rotulo desonesto? a emenda reabre o buraco? o fix esta guardado?), e respondeu com reproducao ao vivo nos dois sentidos
- **Metodo-senior:** file-first antes de afirmar; sabotagem manual com restauracao verificada em vez de confiar no relatorio do proprio auditor; e, ao bater no --no-verify, consertar a lacuna do gate em vez de contorna-la

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| alto | tools/test_marketing_claims.py (autoteste_contagem) | CORRIGIDO. Fixture nao distinguia 'tem o campo mutacao' de 'tem mutacao VALIDA'; o critico provou reescrevendo contar_vitrine sem a validacao e obtendo resultado identico. 5a fixture adicionada e provada. |
| alto | tools/squad_gate.py (_recente_o_bastante, ramo sem historico) | CORRIGIDO. Sem `ultimo` o merge-base nunca roda, entao sha_revisado ficava decorativo — o sha do primeiro commit liberava arquivo novo. Ramo passa a exigir sha == HEAD, com os dois lados normalizados por rev-parse (sha curto x 40 chars). |
| medio | tools/test_audit_enforcement.py (cobertura do fix CRLF) | CORRIGIDO. O fix da normalizacao CRLF nao tinha caso: reverte-lo deixava a suite verde. Caso (i-n) adicionado e provado. |
| medio | tools/audit_enforcement.py (rc do --provar) | ACEITO COMO DIVIDA, documentado onde engana. Com puladas e nenhuma falha, retorna 0 — indistinguivel de 'tudo provado' para quem le so o rc. Consistente com o precedente do worktree indisponivel; hoje inofensivo porque nada consome so o returncode. |
| medio | tools/qa_evidence.py (auto-atestacao do escopo_paths) | ACEITO COMO DIVIDA PRE-EXISTENTE. escopo_paths nao e validado contra o que o critico revisou, e quem grava o veredito e o orquestrador. Estrutural, anterior a este bloco. |

## Verificacoes executadas (anti-fabricacao)

- 52/52 provas de mutacao formais apos os commits (audit_enforcement --provar)
- audit_enforcement --passivo: 90 conformes, 0 no passivo, 0 novas sem prova
- varredura das 38 nao-fail-closed atras de padroes de bloqueio real: zero — nenhuma bloqueia sob rotulo mais fraco
- R2 reproduziu ao vivo que escopo amplo (inclusive combinado com explicito) segue barrando arquivo novo nao listado
- R2 reproduziu o sha decorativo: veredito com sha do primeiro commit liberava arquivo novo
- R3 reverteu cada fix em copia fora do repo e reexecutou o canario real: metodo que separa 'o fix funciona' de 'o fix esta guardado'
- run_canaries: 78 PASS / 1 SKIP / 0 FAIL (79 canarios)
