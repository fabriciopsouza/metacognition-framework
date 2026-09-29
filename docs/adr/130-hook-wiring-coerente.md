# ADR-130 — Hook global fail-open, com sonda antes de ligar e origem única de script e wiring

- **Status:** Aceito (pendente de aprovação do PR pelo dono)
- **Data:** 2026-09-29
- **Decisores:** dono (Fabricio), 29/09/2026: "corrija na fonte o incidente de hook desta noite", com os requisitos
  R1 a R5 e o default "origin/main; instalar a partir de um branch só com opt-in explícito".

  Autoria: Opus 5.5.
- **Relação:** emenda a instalação do ADR-129 (decisão 5) e o self-heal do ADR-027; não muda o que o ADR-129 mede.

## Contexto: incidente de 28/09/2026
| Hora | Fato |
|---|---|
| 22:43:54 | PR #180 (ADR-129) mesclado na main. |
| 22:44:04 | `~/.claude/settings.json` ganhou `UserPromptSubmit`: `python ...\resposta_executiva.py --lembrete`. |
| a seguir | O script instalado em `~/.claude/hooks` era o anterior ao #180 (sem `--lembrete`), copiado do working tree do repo principal, que estava em `feat/perfil-anp-combustiveis`. Com flag desconhecida, ele imprimia o uso no stdout e saía com 2. |
| efeito | Todo prompt foi bloqueado ("UserPromptSubmit operation blocked by hook ... No stderr output"), inclusive notificações de tarefa. |
| mitigação | O dono removeu a entrada `--lembrete` do settings global. O backup `settings.json.bak-20260929` não é o original: foi sobrescrito. |

Causa raiz, três falhas combinadas:
1. `resposta_executiva.py` saía com 2 em flag desconhecida: fail-closed num hook que precisa ser fail-open.
2. `ensure-global-wiring.ps1` ligava o `--lembrete` checando só `Test-Path`, sem saber se o script instalado aceitava
   a flag.
3. `sync-global.ps1` copiava os scripts do branch em que o working tree estivesse, e cada sessão (worktree ou branch)
   rodava a sua cópia. Wiring e script podiam vir de versões diferentes.

## Decisão
1. **Hook fail-open (R1).** `resposta_executiva.py` sem flag ou com flag desconhecida escreve o uso no stderr e sai
   com 0. Exceção em `--hook` ou `--lembrete` sai com 0 e registra no stderr. Nenhum caminho de hook sai com 2; o
   Stop também não bloqueia (ADR-129).
2. **Sonda antes de ligar (R2).** `ensure-global-wiring.ps1`, em toda execução, roda o script INSTALADO com um JSON de
   teste de cada evento (`Stop --hook`; `UserPromptSubmit --lembrete` com prompt normal e com
   `<task-notification>`), com estado isolado em pasta temporária. Exige exit 0 e stdout vazio. Se falhar, não liga
   e remove a entrada existente daquela flag, com registro no log. Script ausente conta como falha, porque o python
   sai com 2 ao não achar o arquivo. Python ausente no PATH não remove nada: só não liga, porque sem python o shell
   sai com 127 ou 1, que não bloqueia. `route-gate` e `inject` só são ligados se o script estiver instalado.
3. **Origem única (R3).** Os scripts que o ensure liga (`route-gate.ps1`, `inject-start-session-global.ps1`,
   `resposta_executiva.py`) e o próprio `ensure-global-wiring.ps1` são instalados do mesmo commit, no mesmo passo
   (`git archive`, byte a byte). O `sync-global.ps1` extrai o ensure desse commit e o executa; não copia mais esses
   arquivos do working tree. O carimbo `~/.claude/hooks/hooks-origem.json` registra ref, commit, hash de cada
   arquivo e hash do ensure que executou.
   - Default: `origin/main`.
   - Opt-in explícito: `-Ref <ref>` no ensure ou `FRAMEWORK_HOOKS_REF=<ref>`; `WORKTREE` instala os arquivos não
     commitados.
   - Pasta sem git: a própria pasta (há uma versão só, sem branch para divergir).
   - Ref que não resolve, ou que não contém os scripts: nada é instalado; o ensure instalado só sonda e corrige o
     wiring. O sync avisa na mensagem de sessão.
   - **Contrato do ensure:** o sync só executa um ensure com `ENSURE-CONTRATO: 2` ou mais. Um `origin/main` local
     sem fetch ainda traz o ensure anterior a este ADR, que ignora `-Ref`, copia do working tree e liga sem sonda,
     ou seja, reproduz o incidente. Nesse caso, o sync não o executa e avisa "anterior ao ADR-130 (git fetch)".
   - Arquivo travado na cópia (outra sessão, antivírus) não aborta a instalação: vai para `incompleto` no carimbo,
     e a sonda testa o que ficou instalado.
4. **Backup sem sobrescrever.** O ensure grava `settings.json.heal-<timestamp>.bak` e, em erro, restaura só o backup
   da própria execução. Antes, `settings.json.heal.bak` era sobrescrito a cada execução e um backup antigo podia
   voltar por engano.

## Régua §0
Critério (a): remove o caminho de cópia do working tree no sync e substitui a checagem `Test-Path` pela sonda. O que
se acrescenta (sonda, extração por commit, carimbo) é o mínimo para a invariante ser verificável.

## Limites
- **Branch antigo continua perigoso até receber a main.** Um working tree num branch anterior a este ADR ainda tem o
  `sync-global.ps1` antigo, que copia o script do branch e roda o ensure antigo, sem sonda. Ao abrir sessão nele, o
  incidente pode se repetir. A defesa é trazer a main para o branch antes de abrir sessão nele.
- **Repo sem `origin/main`** (fork, remote com outro nome, branch `master`): nenhum hook global é instalado até
  declarar o ref (`FRAMEWORK_HOOKS_REF=<ref>`; `HEAD` ou `WORKTREE` servem). Antes, o sync copiava do working
  tree. É o custo de "branch só com opt-in", e o sync avisa na mensagem de sessão.
- **Até o `origin/main` local receber este ADR** (fetch depois do merge), o wiring global não é reafirmado nem
  instalado; fica o que já está no `~/.claude`.
- **O contrato é declaratório.** O sync confere a linha `# ENSURE-CONTRATO: <n>` no início da linha, não o
  comportamento. Um ensure antigo com a linha copiada à mão passaria. A defesa contra isso é a revisão.
- **Ensure instalado antigo + `origin/main` velho:** o self-heal fica suspenso até o `git fetch`. O aviso aparece na
  mensagem de sessão.
- **Python só fora do PATH do ensure:** uma entrada ruim já ligada é mantida, e a sonda não a corrige nessa
  execução.
- **Cópia incompleta:** com `incompleto` não vazio no carimbo, "mesma versão no mesmo passo" não vale para os
  arquivos listados. A sonda protege a flag, e o próximo sync tenta de novo.
- **`bootstrap.ps1` roda o ensure do working tree**, mas este instala de `origin/main`; o sync seguinte reexecuta o
  ensure do commit.
- **Os outros arquivos do sync** (skills, agents, workflows, `check-repo-sync`, `check-core-agnostic`) continuam
  vindo do working tree. Não têm wiring com flag que possa divergir; fica fora do escopo.
- **A sonda testa `resposta_executiva.py`**, o único hook global com flag. `route-gate` e `inject` não recebem flag.

## Prova
`tools/test_resposta_executiva.py` (canários R4, rodam com home falso e nunca tocam o `~/.claude` real):
- R4a: script antigo + settings com `--lembrete` → a entrada é removida, o `route-gate` fica e a remoção vai para o
  log; com settings vazio, o `--lembrete` não é ligado; script que falha no `--hook` perde só a entrada do Stop;
- R4b: flag desconhecida e ausência de flag → exit 0, stdout vazio;
- R4c/R4d: `--lembrete` com prompt normal e com `<task-notification>` → exit 0; a sonda recusa script que bloqueia
  só a notificação;
- R4f: script que escreve no stdout não é ligado;
- R4x: exceção em `--lembrete` e em `--hook` → exit 0 e erro no stderr;
- R4g: backup com timestamp não sobrescreve o antigo; erro antes do backup não restaura backup antigo;
- R4p: sem python no PATH, o wiring existente fica;
- R4e: repo com `origin/main` e working tree divergente → script, ensure instalado e ensure executado iguais aos do
  commit; carimbo com o commit; o comando ligado, executado pelo shell, sai com 0 na notificação; o ensure sem
  `-Ref` usa `origin/main`;
- R4h: `origin/main` com ensure anterior a este ADR → o sync não o executa e avisa;
- R4i: sem `origin/main` → nada instalado, nada ligado para script ausente, aviso na sessão;
- R4j: opt-in `WORKTREE` instala o working tree, e a sonda recusa o script antigo.

`python tools/test_resposta_executiva.py --mutacoes`: mutações M1 a M15 (16 verificações, porque M2 é conferida
contra R4c e contra R4d), cada uma numa cópia, derrubam o canário correspondente.

## Estado do QA
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 1 | Sonnet isolado (ad08c091ef0199801) | PASS-COM-RESSALVAS | MÉDIA: sem `origin/main`, ligava `route-gate`/`inject` para scripts ausentes. MÉDIA: `origin/main` local sem fetch traz o ensure antigo, que ignora `-Ref` e copia do working tree (volta o incidente). MÉDIA: 4 de 10 mutações do revisor sobreviveram (stdout, Stop, notificação na sonda, default do ensure, backup). BAIXA: ref sem os scripts arquivava a árvore inteira; cópia travada abortava; python ausente removia wiring bom; contagem de mutações. | contrato `ENSURE-CONTRATO` conferido pelo sync; evento só ligado com script instalado; aviso na sessão; `SEM-PYTHON` não remove; cópia por arquivo com `incompleto`; ref vazio retorna; 10 canários e 9 mutações novas |
| 2 | Sonnet isolado (ad08c091ef0199801, retomado) | PASS-COM-RESSALVAS | Os 7 achados da rodada 1 foram confirmados como corrigidos, com os cenários reproduzidos. 9 de 10 mutações do revisor morrem; a MI é mutante equivalente (a M11 do canário cobre o caso). BAIXA: contrato declaratório e regex casando qualquer comentário; self-heal suspenso com ensure antigo e `origin/main` velho; `SEM-PYTHON` mantém entrada ruim; cópia incompleta. | regex ancorado no início da linha; os quatro pontos declarados em "Limites" |
