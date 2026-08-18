# QA-evidence — passivo-lote-3-classe-mechanism-igual-test

- **Data:** 2026-08-17T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** PASSA — o critico nao perguntou se os canarios passam (passam por construcao), perguntou se o auto-teste testa a MESMA funcao que roda em producao, que e a unica forma de a fixture significar alguma coisa; e conferiu as duas direcoes de cada uma
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| baixo | docs/adr/106-prova-de-mutacao-para-capacidade-fail-closed.md | CORRIGIDO. Observacao redacional: a frase 'era 22 no registro do ADR' misturava o censo historico de 2026-08-14 com as 8 restantes deste bloco — exigia que o leitor ja soubesse de qual censo vinha o 22. Nao era erro factual. Reescrita para citar a data do censo. |

## Verificacoes executadas (anti-fabricacao)

- 8 mutacoes aplicadas manualmente e revertidas com verificacao de sha256 antes/depois: 8/8 vermelho pelo motivo declarado
- confirmado que main() e autoteste() chamam a MESMA funcao extraida nos 8 arquivos (nao reimplementacao paralela que apodreceria em silencio)
- confirmado que os 8 autotestes cobrem as DUAS direcoes (caso sujo que deve ser pego + caso limpo que nao pode ser acusado)
- ambiguidade de `de`: contagem literal nos arquivos-alvo das 29 capacidades com mutacao -> todas count==1
- test_consistency_closing.py real: as 5 checagens originais (duplicatas, proposto-entregue, raiz-limpa, version-claim, ponteiro-morto) seguem executando e reportando apos o refactor de main()
- return 1 antecipado em posture-gate/dev-dogfood conferido: ocorre DEPOIS do shadow-check e ANTES da logica do gate — mais estrito, nao mais frouxo
- vitrine recalculada do zero: 29+0+27+34=90; distribuicao de enforcement soma 27; 29/90=0,322 confirma 'menos de um terco'; 'classe foi a zero' verificado contando fail-closed sem mutacao = 0
- run_canaries.py completo: 77 PASS / 1 SKIP / 0 FAIL (78)
