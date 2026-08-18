# QA-evidence — emenda-squad-gate-arquivo-novo

- **Data:** 2026-08-18T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** PASSA - a pergunta feita ao critico foi a unica que importa numa mudanca de gate ('a emenda reabre o buraco que a regra fechava?'), e ele respondeu com reproducao ao vivo nos dois sentidos: mostrou o que continua fechado E achou o que ficou aberto
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| alto | tools/squad_gate.py (_recente_o_bastante, ramo `not ultimo`) | CORRIGIDO E PROVADO. Sem `ultimo` nao ha merge-base para rodar, entao o `sha_revisado` nao tinha efeito algum neste ramo: o critico reproduziu liberando um arquivo novo com o sha do primeiro commit da historia. E a versao estreita do 'revisado uma vez = liberado para sempre' que este arquivo ja tratou como bloqueante duas vezes. Agora o ramo exige sha == HEAD. |
| medio | tools/qa_evidence.py + tools/squad_gate.py (auto-atestacao) | ACEITO COMO DIVIDA PRE-EXISTENTE, ampliada em raio. `escopo_paths` nao e validado contra o que o critico revisou, e quem grava o veredito e o orquestrador, nao o subagente. Isso ja valia antes. O que muda: antes, forjar escopo para arquivo novo nao adiantava (bloqueio incondicional); agora funciona. Com a correcao do ALTO o custo volta a nao ser trivial (exige o sha da ponta), mas a divida estrutural continua aberta. |
| baixo | tools/squad_gate.py (ramo `not ultimo`) | LIMITE DECLARADO no codigo. A checagem por HEAD nao cobre edicao do arquivo DEPOIS do veredito e ANTES do commit — sem historico, o git nao registra essa mudanca. Fechar exigiria carimbar hash de CONTEUDO no veredito. Fica como debito explicito, nao como propriedade que o gate finge ter. |

## Verificacoes executadas (anti-fabricacao)

- escopo amplo + explicito juntos contra um SEGUNDO arquivo novo nao listado: _recente_o_bastante = False (a lavagem da 8a rodada segue fechada)
- arquivo COM historico e sha antigo + escopo explicito: False (a emenda so afeta o ramo `not ultimo`)
- variacoes de string em _listado_explicitamente (barra invertida, ./, case, absoluto, espacos): todas falham no sentido SEGURO, nenhuma abre bypass
- reproducao ao vivo do ALTO: veredito com sha do primeiro commit liberava arquivo novo -> corrigido exigindo a ponta da branch
- test_squad_gate.py: 27/27 PASS; run_canaries: 78 PASS / 1 SKIP / 0 FAIL
- prova negativa das duas travas: remover a excecao explicita OU a checagem de sha derruba o canario nomeando o caso
