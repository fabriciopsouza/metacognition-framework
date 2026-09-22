# QA-evidence — adr-115-rodada-38-uniao-por-caminho

- **Data:** 2026-09-21T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| MEDIA | tools/squad_gate.py::_qa_critic_attested - o comentario da uniao, e a nota de fechamento no ledger | Entrada: ler a afirmacao 'avaliadas uma a uma, que e' mais estrito que avaliar o conjunto de uma vez'. Observado: falso numa dimensao especifica e reproduzivel — `_reprovacao_vigente` usa `any()` sobre o alvo, entao avaliada com um caminho so' ela ignora reprovacoes que caem sobre OUTROS caminhos do mesmo escopo amplo, coisa que o modo conjunto nao ignorava. NAO vira bypass no ponto de chamada real (o caminho reprovado falha o proprio teste e o `all()` exige todos os staged), mas a frase esta' errada. CORRIGIDO na prosa, nao no codigo: o veto ficou mais CIRURGICO — nao contamina vizinhos —, e isso e' defensavel como propriedade, sem ser 'mais estrito'. |
| BAIXA | tools/squad_gate.py::_um_veredito_cobre - alvo vazio | Entrada: `_qa_critic_attested(artifacts, None)` ou com lista vazia. Observado: devolvia True sempre que houvesse QUALQUER veredito valido no ledger, com QUALQUER escopo, porque `all(... for p in [])` e' verdade por vacuidade. Nao exploravel hoje — o unico chamador real passa o que esta' staged, e classify() nunca exige qa_critic para lista vazia — e ANTERIOR a uniao, herdado intacto na extracao. CORRIGIDO com `if not alvo: return False` no topo: vacuidade logica num gate e' divida que so' cobra juros quando alguem acrescentar o segundo chamador. |
| BAIXA | tools/test_mutacao_squad_gate.py - ausencia de mutacao para os mecanismos novos | Entrada: grep por `_um_veredito_cobre` e `blobs_revisados` na suite de mutacao. Observado: zero ocorrencias — as 34 mutacoes nao tocavam nenhum dos dois mecanismos novos, e as provas de mutacao deles tinham sido feitas a mao pelo autor, valendo como evidencia daquela vez e nao como gate continuo. CORRIGIDO com 3 mutacoes formais. Achado adicional do autor ao aplicar: as 3 SOBREVIVERAM na primeira tentativa, porque a suite roda so' os testes de TESTES_DO_BLOCO e os 13 canarios novos nao estavam na lista — o instrumento media uma coisa e o rotulo dizia outra, a mesma familia que este bloco vem catalogando. Ligados, 37/37 morrem. |
| BAIXA | CHANGELOG.md - paridade narrativa | O arquivo narra o ADR-115 rodada a rodada ate por volta da 24a e para — as rodadas 36 a 38, que sao justamente as que mais mudaram a semantica do gate, nao apareciam. Nao e' quebra de regra escrita (o gate de doc-sync so' exige o ADR presente), e' quebra do padrao proprio do arquivo. CORRIGIDO com secao dedicada. |

## Verificacoes executadas (anti-fabricacao)

- critico reproduziu contra o binario real, com veredito de escopo amplo ('tools/') e reprovacao CRITICO sobre um so' caminho: `_um_veredito_cobre` com o conjunto devolve False; por caminho devolve True para o nao-reprovado e False para o reprovado; e `_qa_critic_attested` com os dois juntos devolve False — mesmo resultado da regra antiga, logo sem bypass
- critico reproduziu a composicao de vereditos de SHAs diferentes cobrindo metades distintas: a uniao aceita, e o commit pode ser atestado sobre um estado que nunca existiu inteiro num snapshot revisado. Confirmado como risco real e ja' declarado ABERTO no artefato da 36a
- critico provou por MUTACAO que os 4 canarios negativos nao sao decorativos: copiou o modulo e o canario para baseline/ e mutant/, trocou `all` por `any`, e mediu baseline 96 PASS / 0 FAIL contra mutante 92 PASS / 4 FAIL — os 4 que morrem sao exatamente os 4 negativos declarados
- critico rodou test_squad_gate.py (96 PASS/0 FAIL), test_mutacao_squad_gate.py (34/34 na epoca), test_qa_evidence.py (PASS) e squad_gate.py (exit 0, com os 60 vereditos sem blobs impressos): todos os numeros que eu declarei conferem
- critico reproduziu a vacuidade logica: `_qa_critic_attested(artifacts, None)` e com lista vazia devolviam True sempre que houvesse QUALQUER veredito valido, por `all(... for p in [])` ser verdade por vacuidade
- critico confirmou por grep que test_mutacao_squad_gate.py nao tinha mutacao nenhuma tocando `_um_veredito_cobre` nem `blobs_revisados`
- critico leu `_recente_o_bastante` e verificou que ela ja' e' um AND por caminho, logo NAO tem a assimetria do achado 1 — tentou construir contraexemplo e nao conseguiu
- autor, APOS as correcoes: test_squad_gate.py 96 PASS / 0 FAIL; test_mutacao_squad_gate.py 37/37 mutacoes mortas (as 3 novas cobrem all->any, o desligamento da checagem de conteudo, e o alargamento da excecao do auto-carimbo); squad_gate.py exit 0
- autor mediu que as 3 mutacoes novas SOBREVIVERAM na primeira tentativa, e a causa nao era o mecanismo estar desprotegido: a suite de mutacao roda so' os testes nomeados em TESTES_DO_BLOCO, e os 13 canarios novos nao estavam na lista. Ligados, as 3 morrem.
