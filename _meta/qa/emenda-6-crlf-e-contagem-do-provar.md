# QA-evidence — emenda-6-crlf-e-contagem-do-provar

- **Data:** 2026-08-18T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** PASSA - o critico separou as duas perguntas que quase sempre sao confundidas: 'o fix funciona?' e 'o fix esta guardado?'. Reverteu cada um numa copia para responder a segunda, que e a unica que sobrevive ao proximo refactor
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| medio | tools/test_audit_enforcement.py (cobertura do fix CRLF) | CORRIGIDO E PROVADO. O fix da normalizacao CRLF nao tinha caso de teste: o critico reverteu numa copia e a suite seguiu verde, ou seja, o fix podia ser removido amanha reintroduzindo o falso-SKIP sem nada acusar. Adicionado o caso (i-n), que grava o mesmo CONTEUDO com quebra de linha diferente e exige [PROVADO] em vez de SKIP. |
| medio | tools/audit_enforcement.py (codigo de saida do --provar) | ACEITO COMO DIVIDA, com o limite documentado onde engana. Com capacidades puladas e nenhuma falha, --provar retorna 0 — indistinguivel de 'tudo provado' para quem olhar so o rc. E consistente com o precedente do worktree indisponivel no mesmo arquivo, e hoje e inofensivo porque nada consome o comando so pelo returncode. Mas e a armadilha de 'verde nao e evidencia' na interface da propria ferramenta que a combate. Documentado na linha de codigos de saida; rc distinto para 'nada foi provado' fica como follow-up. |

## Verificacoes executadas (anti-fabricacao)

- reversao isolada de cada fix em copia fora do repo + reexecucao do canario real: metodo que separa 'o fix funciona' de 'o fix esta guardado'
- confirmado que Path.read_text ja faz universal-newline, entao _sem_crlf nao pode mascarar diferenca de CONTEUDO — so alinha a checagem ao que a prova enxerga
- tracado o fluxo do loop: cada cid termina em exatamente um destino (falhas | pulados | PROVADO), com continue apos cada append -> a subtracao nao pode contar duplo
- confirmado que o resumo 'OK: N prova(s)' so e alcancado quando falhas esta vazio
- test_audit_enforcement: 33/33 apos o caso novo; run_canaries: 78 PASS / 1 SKIP / 0 FAIL
- prova negativa do caso novo: reverter a normalizacao CRLF derruba 2 verificacoes
