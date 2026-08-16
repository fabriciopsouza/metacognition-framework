# QA-evidence — release-1.83.0-busca-provada-e-instalacao-verificavel

- **Data:** 2026-08-16T14:30:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** v1.83.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** leitura do manifesto para saber o que a ferramenta deveria conferir, antes de escrever; e inventario dos guias existentes antes de propor runbook novo
- **RRC:** PASSA — o critico construiu as burlas com comando reproduzivel e refez a prova de mutacao do canario de instalacao por conta propria, sem aceitar a do autor.
- **Metodo-senior:** N/A: fecha peca faltante de ADR ja aceito e estende ferramenta existente.

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| medio | tools/research_evidence.py (funcao dominio) | CORRIGIDO. Ponto final no host inflava a contagem de dominios distintos. Nao estava declarado como limite — era burla de um caractere. |
| medio | tools/research_evidence.py (funcao dominio) | CORRIGIDO. Esquema nao-web era aceito. Agora so' http e https contam. |
| baixo | tools/research_evidence.py (avaliar) | CORRIGIDO. `ratificado_por: true` virava a string 'True'. Ratificacao e' uma pessoa, com nome. |
| baixo | guia/SETUP.md (passo 4 do runbook) | CORRIGIDO. O texto sugeria gate duro ('instalacao que nao executa o proprio portao nao esta instalada') mas o mecanismo emite AVISO e roda um subconjunto, nao a suite inteira. Overclaim em documentacao. |
| baixo | tools/squad_gate.py (_research_atestada) | NAO corrigido, declarado. O gate descarta a saida da ferramenta, entao 'reprovou' e 'quebrou' chegam iguais ao operador. Nao afeta a decisao (ambos bloqueiam) mas atrapalha o diagnostico. |
| baixo | tools/research_evidence.py (funcao dominio) | LIMITE DECLARADO, nao corrigido por decisao: subdominios do mesmo site contam como dois. Fechar exigiria lista de sufixos publicos, que e' dependencia externa, e a fraude exige ma-fe ativa. |

## Verificacoes executadas (anti-fabricacao)

- critico rodou os dois canarios novos: research_evidence 13/13 e bootstrap_check 9/9
- probe adversarial da funcao dominio(): conferiu que http x https, porta explicita, userinfo@, www. e maiusculas ja caiam no mesmo dominio; e reproduziu as duas burlas nao declaradas
- critico provou a falsificabilidade do canario de instalacao por conta propria: trocou bloqueia() por avisa() no ramo do .git ausente e o caso certo ficou vermelho; restaurou por reversao textual, sem git, e reconfirmou verde
- critico avaliou _research_atestada e concluiu que a direcao esta correta: so' o codigo 0 aprova, entao crash ou timeout viram bloqueio, nunca aprovacao indevida — o inverso do defeito que ele achou hoje no install_git_hooks
- correcoes do autor com prova de mutacao, cada guarda vista vermelha antes de valer: ponto final -> [FALHA]; file:// -> [FALHA]; booleano -> [FALHA]; restauradas, 16/16
- runbook corrigido: passa a dizer que roda `test_capabilities` e nao a suite inteira, e que o resultado e' AVISO e nao bloqueio
