# QA-evidence — release-1.86.0-vitrine-com-numeros-verificados

- **Data:** 2026-08-17T02:10:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** v1.86.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** derivou os numeros das fontes primarias antes de julgar o texto, em vez de comparar a pagina com o que o autor disse dela
- **RRC:** PASSA — o critico nao se contentou em conferir a aritmetica: foi olhar o que o numero SIGNIFICA, decompos as 38 em 11 mais 27, e foi isso que revelou o overclaim. Conferir se a conta fecha teria aprovado a pagina.
- **Metodo-senior:** N/A: revisao de vitrine e de canario, sem autoria de norma nova.

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| alto | guia/web/index.html (secao #provas) | CORRIGIDO. Overclaim mecanizado na pagina inicial: a frase afirmava sabotagem provada para 38 capacidades quando so 11 a tinham. O numero era verdadeiro; a explicacao dele nao. |
| medio | tools/test_marketing_claims.py (checagem g) | CORRIGIDO. A regra de 'conforme' era copiada do auditor em vez de importada. Se valida_mutacao mudar, o canario continua validando pela formula velha. |
| medio | tools/test_marketing_claims.py (comparacao por substring) | CORRIGIDO. Buscava a string no arquivo inteiro, cega a contexto e visibilidade. |
| baixo | guia/web/index.html (afirmacao sobre o runner) | NAO alterado, mas verificado apos a duvida do critico: a frase 'recusa arquivo que passaria sem executar assercao alguma' corresponde ao guard de canario cego em run_canaries.py, que existe e tem caso de teste. O critico nao o localizou por grep simples e declarou a duvida em vez de afirmar. |

## Verificacoes executadas (anti-fabricacao)

- R1 derivou os numeros por conta propria das fontes e confirmou que 89/38/51/77 batem com a vitrine — a aritmetica estava certa, a semantica nao
- R1 mediu a decomposicao: 11 conformes com campo mutacao, 27 contadas so por declararem enforcement nao-bloqueante
- R1 comparou a formula copiada no canario contra valida_mutacao do auditor real: 0 divergencias HOJE, mas por acaso e nao por garantia estrutural
- R1 conferiu numeracao das secoes (00-11 sequencial) e ancoras do menu: todas resolvem, sem regressao
- correcao do ALTO: a vitrine passa a separar os numeros e dizer o que cada um mede — 11 com sabotagem provada, 17 que declaram bloquear e nunca foram provadas, 27 com protecao mais fraca, 34 sem declaracao; e afirma explicitamente que 'conformidade' no registro nao significa 'foi sabotada'
- correcao dos MEDIOS: a checagem passa a IMPORTAR valida_mutacao do auditor, e a busca acontece so dentro da secao #provas com os comentarios HTML removidos
- os 3 ataques de evasao descritos pelo critico foram encenados e agora falham: numero visivel trocado -> codigo 1; numero certo escondido em comentario HTML -> codigo 1; numero certo fora da secao -> codigo 1; restaurado -> codigo 0
- a propria secao da vitrine passou a registrar o episodio: diz que a 1a versao afirmava 38 sabotadas e que o critico mostrou ser falso para 27
