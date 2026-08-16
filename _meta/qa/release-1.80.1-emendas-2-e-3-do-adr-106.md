# QA-evidence — release-1.80.1-emendas-2-e-3-do-adr-106

- **Data:** 2026-08-16T00:40:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** v1.80.1

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** critica dos sete pedidos do dono contra o registro de capacidades e o historico de fracassos ANTES de qualquer plano — quatro dos sete repetiam tentativas ja catalogadas como falhas
- **RRC:** PASSA — os tres criticos reproduziram ao vivo o que afirmaram, em worktree isolado, rodando as provas por conta propria em vez de aceitar a mensagem do commit. O autor sabotou cada guarda nova para conferir que sabia ficar vermelha, e foi isso que denunciou um caso de teste proprio que passava pelo motivo errado.
- **Metodo-senior:** N/A: correcao de mecanismo existente sob ADR ja aceito; nenhuma norma ou spec nova foi autorada.

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| medio | tools/audit_enforcement.py (ENV_SEM_BYTECODE / _purgar_bytecode) | PYTHONPYCACHEPREFIX aponta o cache de bytecode para fora do worktree. A escrita continua barrada por PYTHONDONTWRITEBYTECODE=1, mas _purgar_bytecode varre apenas o worktree — um .pyc pre-existente nesse prefixo externo, deixado por outro processo, nao e' purgado e poderia ser lido. |
| baixo | tools/test_audit_enforcement.py (caso 'travas anti-cache de bytecode presentes') | A metade 'env' do caso confere a presenca da chave no dicionario, nao que o subprocesso de fato nao grave .pyc. A metade 'purga' e' comportamental de verdade. Assimetria real, registrada e nao mascarada. |
| baixo | capabilities.json (mutacao de rules-parity-guard) | A sabotagem troca N_CANON = len(CANON) por N_CANON = 3. E' honesta hoje (ataca o calculo dinamico virando constante), mas se um dia len(CANON) for exatamente 3 a mutacao vira no-op e a prova passa a falhar com 'continuou VERDE'. Dependencia implicita do estado atual do repo que a declaracao nao expoe. |

## Verificacoes executadas (anti-fabricacao)

- R1 Sonnet em worktree isolado no commit 4fbd5d1: leitura integral de modo_provar; construcao do cenario JSONDecodeError confirmando que o traceback cita json/decoder.py e nunca o arquivo de dados
- R2 Fable em worktree isolado no commit 40b7775: refez uma sabotagem por conta propria (if len(esp) < ESPERA_MIN -> if False) e confirmou que o caso vira [FALHA] — a prova do autor nao e' encenacao
- R2 Fable: experimento em model-policy — id de modelo invalido deixou o canario VERDE (rc 0); rename estrutural matou o canario por crash antes da verificacao. Capacidade improvavel pelos dois lados, defeito PRE-EXISTENTE do canario dela
- R3 Sonnet em worktree isolado no commit bf9578b: rodou --provar --id para risk-gate, rules-parity-guard e autonomy-retry-policy; as tres [PROVADO] com o motivo declarado, exit 0
- R3 Sonnet: confirmou que worktree recem-criado nao traz __pycache__ (git ls-files | grep pycache vazio) e que as DUAS execucoes do canario receberam env=ENV_SEM_BYTECODE
- R3 Sonnet: confirmou que ENV_SEM_BYTECODE e' superset de os.environ (nunca remove chave) e que o snapshot no import nao gera regressao, por o auditor rodar como processo novo a cada invocacao
- Autor: prova de mutacao das 5 guardas novas, cada uma sabotada e vista VERMELHA antes de valer — piso de 12 caracteres em espera, proibicao de sinal de crash em espera, deteccao de crash por DELTA, env anti-bytecode, purga de __pycache__
- Autor: prova deterministica do defeito de cache congelando o mtime com os.utime para simular o mesmo segundo — cache ligado deixou o canario VERDE (prova perdida), cache desligado VERMELHO (correto)
- Autor: achado contra o proprio trabalho — o caso novo do mecanismo .json passava pelo motivo errado (o literal 'dados.json' estava na linha que falhava e vazava para o traceback); so apareceu porque a guarda foi sabotada e nao mudou de cor. Fixture corrigida em 40b7775
- Canario do auditor 22 -> 28 verificacoes; suite completa 67 PASS / 1 SKIP / 0 FAIL no commit bf9578b
- Migracao sob a regra do R2: byo-ci-gate e qa-evidence-gate ficaram DE FORA porque os canarios deles nao ficaram vermelhos com a sabotagem candidata — debito nomeado, nao prova forcada
