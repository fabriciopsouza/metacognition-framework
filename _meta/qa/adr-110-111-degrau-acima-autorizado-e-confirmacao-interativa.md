# QA-evidence — adr-110-111-degrau-acima-autorizado-e-confirmacao-interativa

- **Data:** 2026-08-19T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/handoff.py:suggest_model + tools/model-policy.json:roles | handoff.py: papeis compostos (autoral + mecanico) resolviam abaixo do baseline; a ordem de roles E' precedencia e a regra autoral estava DEPOIS da mecanica. Reordenado + canario de produto cartesiano. |
| ALTA | tools/model-policy.json:qa_final_duplo.excecao_declarada | model-policy.json: qa_final_duplo.excecao_declarada afirmava cross-ai em max e PENDENTE, contradizendo roles no mesmo commit. Reescrito. |
| MEDIA | history.md (criterio de aceite da pendencia prioritaria) | history.md: criterio de aceite exigia o degrau acima incondicionalmente, impossivel de fechar sem violar o ADR-110. Emendado com 'quando autorizado' + ausencia declarada. |
| MEDIA | docs/adr/110-autorizacao-ativa-do-degrau-acima-e-autor-sempre-default.md | ADR-110 citava numeros de sessao sem artefato no repo. Substituidos por referencia a assercao executavel. |
| MEDIA-ALTA | tools/test_handoff.py (produto cartesiano autoral x mecanico) | [introduzido pela correcao, achado na r2] o teste cartesiano derivava chaves autorais de lista escrita a mao, deixando architect/discovery fora do espaco. Passou a derivar de tier=baseline. |
| BAIXA | tools/check_rules_parity.py + tools/test_rules_parity.py | guarda de ponteiro morto varria texto cru; blocos de codigo dariam falso positivo. Passou a suprimir ``` e ganhou fixture que prova os dois lados. |

## Verificacoes executadas (anti-fabricacao)

- r1: executou handoff.suggest_model com papeis compostos e provou developer/author/implement/produz/autor + gatilho mecanico -> haiku
- r1: conferiu roles[cross-ai].tier contra o texto de excecao_declarada no mesmo arquivo
- r1: conferiu numeracao 00..11 e todos os href ancora do site apos a troca de secoes
- r1: bateu '54 de 92' e '81 canarios' da vitrine contra capabilities.json e run_canaries
- r2: atacou o casador com composicoes de 3 tokens, ordem invertida, caixa, acento e pontuacao
- r2: enumerou os 8 papeis mecanicos puros e confirmou que nenhum subiu de tier apos a reordenacao
- r2: reproduziu a mutacao do canario cartesiano e conferiu a contagem 112 citada no ADR
- r2: testou ponteiro morto dentro e fora de bloco de codigo na guarda do linter
- autor: mutacao de architect apos a mecanica -> 96 composicoes acusadas (furo da r2 fechado)
- autor: mutacao removendo re.sub de blocos ``` -> fixture acusa falso positivo
- suite completa: 80 PASS, 1 SKIP, 0 FAIL de 81 canarios
