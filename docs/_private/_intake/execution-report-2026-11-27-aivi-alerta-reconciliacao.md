# Execution-report — encerramento de bloco (ADR-038/052 · tier OWNER · privado, não distribuído)

Sessão 852b6cd5 (26–27/11/2026, PC VBR EAP9CQXC64): diagnóstico do alerta diário de uma carga de indicador, texto do alerta
mais claro (PR #564 do repositório do indicador), respostas a três sessões paralelas e reconciliação chave a chave de um
export SAP com a tabela SAP do hub de dados.

- **Tokens:** NÃO MEDIDO — sem telemetria de token exposta ao agente (dependência do host; ver LIMITS.md)
- **Tempo (wall-clock):** ~2 dias de calendário, sessão interativa com interrupções (NÃO MEDIDO em horas)
- **Turnos:** NÃO MEDIDO
- **Arquivos tocados:** 8 em 4 repositórios (indicador, biblioteca da empresa, orquestrador, framework) + 3 memórias
- **Testes:** parse PowerShell 5.1 + ASCII + simulação com log real (alerta); reconciliação reproduzível por script (s17);
  verificador da biblioteca sem achado novo (218 = linha de base)
- **Rodadas de retrabalho:** QA isolado Sonnet no alerta (PASS com ressalvas, 2 corrigidas); QA isolado Sonnet na reconciliação: rodada 1 FAIL (conclusão central falsa), corrigida e levada à rodada 2

## Placar gate × achado (quem pegou o quê)
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Alerta genérico "provas falharam" repetido 10 dias; causa = planilha do Portal vencida | dono (print) | nenhum: o alerta não dizia a ação |
| Texto específico podia esconder outra prova reprovada junto | QA isolado | — (funcionou) |
| Autor indicou a outra sessão uma tabela inexistente, lida de log em modo simulação ("destino seria …") | sessão parceira, ao conferir | anti-alucinação: faltou `get_table` antes de repassar |
| "9,5% de divergência" vinha de LEFT JOIN somando bases diferentes; real = −352.560 L em 3 chaves | autor, ao refazer com FULL OUTER JOIN | R-02 da biblioteca (passo 5) já dizia "contar os três grupos" |
| Divergências eram de foto antiga do export (08/07) | autor (data_export por mês) | — |
| Autor afirmou "efeito zero no oficial" pelo rótulo da perna (`excel_fallback`); a definição da view lia o próprio export: 20 chaves de 06/2026 (16,35 mi L) sairiam do oficial | QA isolado (Sonnet), ao ler a view | nenhum: a conclusão foi tirada do nome, não da definição |
| Autor contou 17 chaves no impacto, e não 20, por formato diferente do código de produto entre tabelas | autor, ao conferir o número da QA | — (corrigido com normalização no script) |
| Edit sem Read barrado | hook overwrite-guard | — (funcionou) |
| `rm -rf` em pasta temporária barrado | hook effect-gate | — (funcionou; usei pasta nova) |

## Detecção: framework × humano
- Mecanismo: hooks overwrite-guard e effect-gate; verificador da biblioteca (pegou bullets em negrito lidos como campo).
- QA isolado: ressalva de texto enganoso no alerta.
- Sessão parceira: a tabela inexistente.
- Humano (dono): o alerta repetido; a ordem de seguir o recomendado até o merge.

## Gaps (não-bloqueantes — flagados)
- Sumiço dos grupos GASOLINA_PODIUM_SIMP de 06/2026 no SAP: destino do volume DESCONHECIDO.
- O export de 08/07 omitiu 1.078 chaves LT/LM/SUPER de fev–mai: motivo DESCONHECIDO.
- A carga não roda nos dias em que o PC está desligado (14, 20 e 25/11).

## Melhorias (régua §0)
- Checklist do qa-critic para reconciliação: "soma comparada só nas casadas; três grupos contados" (edição de checklist existente, sem código).
- Anti-alucinação: "objeto citado a outro agente tem existência provada; destino de simulação não é objeto" (edição de regra existente).

## Boas práticas (o que funcionou — reutilizável)
- Worktree separada por repositório quando o checkout principal tem trabalho de outra sessão ou alimenta tarefa agendada.
- Rótulo [EXPLORATÓRIO-CONFIRMAR] segurou a troca de fonte até a reconciliação.
- Verificador da biblioteca rodado antes e depois da entrada, comparando com a linha de base (218 → 218).

## Lições por skill
- **validation-reporting:** fonte que é foto tem data por recorte; divergência posterior à foto é atualização.
- **anti-hallucination:** linha de log de simulação descreve intenção, não estado. O nome de uma perna de view ("fallback", "excel") não diz a tabela de origem: ler a definição antes de afirmar impacto.
- **developer:** alerta diz se o dado foi gravado e qual a ação; marcador acoplado por string é limite declarado no código.
