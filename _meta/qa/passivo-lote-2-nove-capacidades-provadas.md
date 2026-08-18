# QA-evidence — passivo-lote-2-nove-capacidades-provadas

- **Data:** 2026-08-17T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** PASSA - o critico nao revisou se as provas passam (o auditor ja diz isso), revisou se elas provam a COISA CERTA, que e a unica pergunta que importa aqui; e achou o buraco na trava do proprio autor
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| medio | tools/test_audit_enforcement.py (caso i-l) | CORRIGIDO. A checagem por AST exigia so a existencia do keyword `encoding`, nunca o valor. O critico reproduziu em memoria: `encoding=None` ou `encoding=locale.getpreferredencoding(False)` nas duas chamadas reintroduz exatamente o bug original e passa na trava. Passou a exigir o valor literal utf-8 (ast.Constant), e a correcao foi provada contra os DOIS cenarios. |
| medio | docs/adr/106-prova-de-mutacao-para-capacidade-fail-closed.md | CORRIGIDO. O codigo nomeava 'EMENDA 5' mas o ADR - fonte canonica da decisao - parava na Emenda 4, quebrando o padrao das emendas 1-4. Emenda 5 registrada, incluindo a licao das tres tentativas de canario verde-sem-significado. Dois numeros defasados no proprio ADR corrigidos junto (19 -> 30 verificacoes; passivo 35/22 -> 34/8 com o motivo das 8 restantes). |
| baixo | capabilities.json (elicitation-gate, project-onboarding) | ACEITO COMO DIVIDA. Os `de` 'ADR-089' e 'knowledge_catalog' sao curtos: hoje count=1, mas se um commit nao relacionado adicionar uma 2a mencao, o replace(...,1) do auditor sabota a PRIMEIRA ocorrencia, que pode nao ser mais a certa. O auditor detecta `de` que SUMIU ('mutacao obsoleta'), nunca `de` que DUPLICOU - o sintoma seria silencioso. Vira pendencia de manutencao do auditor, nao deste bloco. |

## Verificacoes executadas (anti-fabricacao)

- as 9 capacidades migradas rodadas uma a uma com --provar: 9/9 [PROVADO] pelo motivo declarado
- trecho de/para lido no mecanismo real de cada uma das 9 (nao so confiando no auditor): todas sabotam o if/constante que decide o comportamento protegido
- contagem de ocorrencias de cada `de` no arquivo-alvo: count=1 nas 9, logo o replace(...,1) do auditor nao pode acertar o trecho errado hoje
- correcao de mechanism do advanced-elicitation conferida contra test_elicitation_catalog.py:20, que le literalmente methods.md; git log confirma que o catalogo mudou de arquivo na v1.64.0 -> correcao de ponteiro factual, nao rename
- fixture acento conferida como criada ANTES do git add -A do repo-fixture (test_audit_enforcement.py:190-202)
- numeros da vitrine recalculados do zero a partir do capabilities.json: 21+8+27+34=90; 21+27=48 bate com --passivo; 21/90=23,3% torna verdadeira a frase 'menos de um quarto'
- run_canaries.py: 77 PASS / 1 SKIP / 0 FAIL (78 canarios), test_audit_enforcement 30/30
- APOS as correcoes: prova negativa dupla do caso (i-l) - sem a chave encoding E com encoding=None, o canario reprova nomeando o caso (rc 1 nos dois)
