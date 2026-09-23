# QA-evidence — adr-115-fail-closed-no-veredito

- **Data:** 2026-09-18T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Substitui vereditos anteriores deste bloco

- rodada 1 · 2026-09-13T00:00:00Z · **reprovar** · sha `None` · agentId `a2cbfa35535c834f5`
- rodada 33 · 2026-09-18T00:00:00Z · **aprovar** · sha `f6794764729e` · agentId `acd0a2246ccb7acb0`

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| BAIXA | _meta/qa/adr-115-rodada-{23,24,25,27}-*.json | Os vereditos de quatro rodadas do PROPRIO bloco que esta sendo fechado estavam NAO RASTREADOS (`??`), deixando buraco na cadeia decisao->fonte->versao do ADR-115. Nao e' risco de perda — os arquivos seguem em disco e nada e' apagado em silencio — mas fechar um bloco com as proprias rodadas de QA fora do git e' lacuna de rastreabilidade. CORRIGIDO: os quatro foram staged neste mesmo commit, a pedido do critico. |
| BAIXA | shell / quoting do --raiz | Higiene registrada pelo critico: `--raiz "C:\\tmp\\pr25"` com barra invertida dupla faz o Bash quebrar o path e o script morrer em NotADirectoryError no `git worktree prune`. Com `"C:/tmp/pr25"` roda limpo. Nao e' defeito do audit_enforcement — e' armadilha de quoting do shell, da mesma familia ja registrada em memoria (MSYS engole argumento com barra inicial). |
| BAIXA | debitos do bloco, confirmados sem bloqueio | O critico reconferiu os quatro debitos ja' registrados e confirmou que seguem debito, nao bloqueio: indexacao do ledger pelo slug de `bloco` (renomear escapa da cadeia) — merece ADR proprio; audit_enforcement.py nao roda no CI hoje — decisao de arquitetura pendente com o dono; dois escapes declarados na regex anti-vazamento: numero por extenso e taxa sem marcador de moeda; _numeradas sem deteccao de ciclo (outro repositorio). Registrados aqui em `problemas` e nao num campo proprio: a allowlist de topo do gate existe para que achado nao se esconda em chave que ele nao le, e inventar um campo para acomodar prosa e' exatamente o que ela impede. |

## Verificacoes executadas (anti-fabricacao)

- run_canaries.py -> 88 PASS · 1 SKIP · 0 FAIL (de 89), conferido linha a linha
- audit_enforcement.py --provar --raiz C:/tmp/pr25 -> 60 provas de mutacao, 0 falha
- test_audit_enforcement.py -> 37/37
- test_qa_evidence.py -> PASS (release v1.90.0 com evidencia; junction-ledger OK)
- check_core_agnostic.py -> PASS
- hooks/consistency_gate.py -> CONSISTENTE (0 pendencias)
- squad_gate.py -> BLOQUEADO exatamente nos 4 paths esperados, nada alem
- varredura de git status --porcelain nos 83 arquivos: NENHUM `D` staged com arquivo ainda em disco — a classe de risco que quase apagou o execution-report NAO se repete
- RATE-CARD.example.md: integro [DESCONHECIDO] em toda tabela de taxas, zero numero real
- RATE-CARD.md privado: tem taxas reais; confirmado em export-clean.py que STRIP_BEFORE remove docs/_private inteiro antes do export publico
- execution-report.md: tres afirmacoes numericas conferidas contra o repo — '70 staged' = 70 exato; '89 canarios' confirmado; 'de 7 para 17 relatorios validos' = 17 exato. As tres batem
- execution-report-2026-09-12: internamente consistente, pendencias marcadas [D], causa tecnica coerente com o codigo do squad_gate.py
