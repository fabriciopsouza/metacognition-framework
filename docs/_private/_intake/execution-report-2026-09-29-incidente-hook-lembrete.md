# Execution-report — encerramento de bloco (ADR-038/052 · tier OWNER · privado, não distribuído)

Bloco: ADR-130 — incidente do hook `UserPromptSubmit --lembrete` (28/09/2026), corrigido na fonte.

- **Tokens:** NÃO MEDIDO — sem telemetria de token exposta ao agente (dependência do host; ver LIMITS.md)
- **Tempo (wall-clock):** NÃO MEDIDO
- **Turnos:** 2 (abertura de sessão; pedido de correção)
- **Arquivos tocados:** `tools/hooks/resposta_executiva.py`, `tools/hooks/ensure-global-wiring.ps1`,
  `.claude/hooks/sync-global.ps1`, `bootstrap.ps1`, `tools/test_resposta_executiva.py`,
  `docs/adr/130-hook-wiring-coerente.md`, `capabilities.json`, `CAPABILITIES.md`, `CHANGELOG.md`, `history.md`,
  `guia/web/index.html`, este report
- **Testes:** `test_resposta_executiva` PASS (R4a a R4j); `--mutacoes` M1 a M15 (16 verificações);
  `test_capabilities`, `test_consistency_closing`, `test_marketing_claims`, `check_core_agnostic`,
  `test_rules_parity`, `audit_enforcement` PASS
- **Rodadas de retrabalho:** 1 (QA rodada 1: PASS-COM-RESSALVAS, 3 MÉDIA e 4 BAIXA corrigidos; ver o "Estado do QA"
  do ADR-130)

## Linha do tempo do incidente
| Hora (28/09/2026) | Fato |
|---|---|
| 22:43:54 | PR #180 (ADR-129) mesclado na main |
| 22:44:04 | `~/.claude/settings.json` ganha `UserPromptSubmit`: `python ...\resposta_executiva.py --lembrete` |
| a seguir | O script em `~/.claude/hooks` era o anterior ao #180, copiado do working tree do repo principal (em `feat/perfil-anp-combustiveis`); com flag desconhecida, uso no stdout e exit 2 |
| a seguir | Todo prompt bloqueado ("UserPromptSubmit operation blocked by hook ... No stderr output"), inclusive task-notifications |
| 29/09 manhã | O dono remove a entrada `--lembrete`; `settings.json.bak-20260929` foi sobrescrito e não é o original |

## Causa raiz
1. Hook fail-closed: flag desconhecida saía com 2 (`resposta_executiva.py`).
2. Wiring sem conferir o script instalado: `ensure-global-wiring.ps1` checava só `Test-Path`.
3. Origem dupla: `sync-global.ps1` copiava do branch do working tree; sessões em branches diferentes instalavam
   versões diferentes de script e de wiring.

## Placar gate × achado (quem pegou o quê)
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Wiring `--lembrete` com script incompatível | dono (sessão travada) | sonda do ensure (não existia; criada no ADR-130) |
| `--hook` do script instalado (ADR-123) ainda bloqueia o Stop | autor, ao inspecionar `~/.claude/hooks` | carimbo de origem (criado no ADR-130) |
| `settings.json.heal.bak` sobrescrito a cada execução do ensure | autor, lendo o ensure | canário de backup (não existia) |
| `lembrete()` com estado não-objeto gerava AttributeError não capturado | autor, lendo o script | R4x (criado) |
| Branch antigo reinstala o script antigo ao abrir sessão | autor, lendo o sync do repo principal | nenhum: limite declarado no ADR-130 |
| `origin/main` local sem fetch traz o ensure antigo, que ignora `-Ref` (o incidente de volta) | qa-critic Sonnet, rodada 1 | autor (a invariante de origem não previa versão do próprio ensure); agora `ENSURE-CONTRATO` + R4h |
| Sem `origin/main`, ligava hooks para scripts ausentes | qa-critic Sonnet, rodada 1 | R4i (criado) |
| 4 de 10 mutações do revisor sobreviviam (stdout, Stop, notificação, default, backup) | qa-critic Sonnet, rodada 1 | autor, nos canários R4; agora R4f/R4g/R4p e M7 a M15 |

## Detecção: framework × humano (quem pegou o quê — mecanismo vs. revisão humana)
O incidente foi pego pelo dono, com a sessão travada. Nenhum mecanismo conferia se o script instalado aceitava a
flag ligada. Os canários do ADR-129 testavam o script do repo, nunca o par instalado (script + wiring).

## Gaps (não-bloqueantes detectados — flagados, não silenciados)
- Branch anterior ao ADR-130 continua com o sync antigo; a defesa é trazer a main antes de abrir sessão nele.
- Skills, agents e workflows continuam sendo copiados do working tree (sem wiring com flag; fora do escopo).

## Melhorias (do framework/processo — adição passa pela régua §0)
- A sonda testa o artefato instalado, não o do repo: é a prova de que o que o harness vai executar aceita o contrato.

## Boas práticas (o que funcionou — reutilizável)
- Canário de instalação com home falso (`USERPROFILE` temporário) e repo git sintético (`commit-tree` sem hooks):
  prova a instalação real sem tocar o `~/.claude` do dono.
- Mutações executáveis no próprio canário (`--mutacoes`), com a checagem de que o trecho mutado existe uma vez.

## Lições por skill (agnóstico de domínio — o que daqui serve a OUTRO projeto)
- dev: hook que o harness executa em todo evento é fail-open por construção; o único exit que bloqueia é o que o
  contrato pede.
- dev: quem liga um comando precisa executar o comando instalado antes de ligar.
- architect: script e configuração que o referencia saem da mesma versão, no mesmo passo, com carimbo verificável.
- qa-critic: testar o par instalado, não só a fonte.
- docops: backup com timestamp; restaurar só o backup da própria execução.
- discovery / research/spec/ux: NENHUM.
