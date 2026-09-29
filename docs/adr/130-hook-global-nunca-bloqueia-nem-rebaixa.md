# ADR-130 — Hook global nunca bloqueia a mensagem; sincronização nunca rebaixa ~/.claude

- **Status:** Aceito
- **Data:** 2026-09-29
- **Decisores:** dono (Fabricio), 29/09/2026: "priorize a correção para não ocorrer mais o erro". Erro relatado:
  `UserPromptSubmit operation blocked by hook: [python "...resposta_executiva.py" --lembrete]: No stderr output`.

  Autoria: Opus 5.5.
- **Relação:** emenda o ADR-129 (hook de resposta executiva) e a sincronização global (ADR-027; `sync-global.ps1`).

## Contexto
O dono não conseguia enviar mensagem em outro repositório: toda mensagem era barrada. A causa mediu-se assim:
1. `~/.claude/settings.json` já chamava `resposta_executiva.py --lembrete` no UserPromptSubmit (ADR-129).
2. A sincronização de início de sessão rodou no clone principal, que estava num branch criado antes do ADR-129. Ela copiou para `~/.claude/hooks` a versão **antiga** do script, e o arquivo instalado tinha 0 ocorrências de "lembrete".
3. A versão antiga não conhece `--lembrete`: imprime a ajuda no stdout e sai com 2.
4. No UserPromptSubmit, exit 2 **bloqueia** a mensagem, com stderr vazio.

São duas causas. O comando do hook podia bloquear, e a sincronização aceitava copiar de um clone atrasado.

## Decisão
1. **O hook nunca bloqueia.**
   - Os comandos instalados passam a ser `python "<hook>" --hook || true` e `python "<hook>" --lembrete || true`: qualquer versão, qualquer erro, sai com 0.
   - `ensure-global-wiring.ps1` repara a instalação anterior, acrescentando `|| true` ao comando que não o tem, sem duplicar o hook.
2. **A sincronização não rebaixa.** `sync-global.ps1` só copia skills, agentes e hooks para `~/.claude` quando o clone **contém** `origin/main` (`git merge-base --is-ancestor origin/main HEAD`). Clone atrasado ou em branch antigo: a sincronização é pulada por inteiro, sem cópia, regras globais nem reparo, e o aviso diz o que fazer (atualizar o branch e reabrir a sessão). Sem git no PATH, ou com `origin/main` quebrado, a guarda não decide e a sincronização segue (fail-open declarado).
3. **A mesma guarda na cópia direta.** `ensure-global-wiring.ps1 -RepoDir`, chamado também pelo `bootstrap.ps1`, não copia os scripts de um clone que não contém `origin/main`.

## Régua §0
Critério (c): uma falha que travou o dono vira duas guardas verificadas por canário. Não acrescenta ferramenta: são 2 scripts existentes alterados.

## Limites
- **O clone principal que ainda estiver num branch antigo roda o `sync-global.ps1` antigo, que ainda não tem a guarda de rebaixamento.** A proteção imediata é o `|| true` já aplicado em `~/.claude/settings.json`: com ele, a versão antiga do script não bloqueia, só injeta o próprio texto de ajuda. A guarda de rebaixamento passa a valer quando o clone receber este ADR.
- **A guarda compara com o `origin/main` LOCAL, sem `fetch` no início da sessão:** um fetch ali custaria rede e poderia travar sem conexão. Um clone antigo cujo `origin/main` local também esteja velho passa pela guarda. Nesse caso a proteção é o `|| true`, e a sincronização de repositório (`check-repo-sync`, que faz o fetch) avisa o atraso no mesmo início de sessão.
- **Branch de trabalho criado de um `main` que depois avançou deixa de sincronizar** até receber o `main`. É intencional: é o sinal de que está atrasado.

## Prova
`tools/test_resposta_executiva.py`, seção (j), em Windows:
- a instalação antiga ganha `|| true` sem duplicar;
- o Stop já sai instalado com a guarda;
- o comando com a guarda sai com 0 mesmo quando o script sai com 2;
- clone sem `origin/main`: sincronização pulada e avisada, nada copiado;
- clone com `origin/main`: sincroniza;
- `ensure -RepoDir` de clone atrasado não copia o hook;
- `origin/main` quebrado: a sincronização segue (fail-open).

Na máquina do dono, em 29/09/2026:
- o hook atual e a versão antiga (lida do branch atrasado), rodados pelo comando com a guarda, saem os dois com 0;
- `~/.claude/settings.json` foi reparado, com backup em `settings.json.antes-adr130.bak`.

## Estado do QA
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 1 | Sonnet isolado (ad0df1ef2b1a10913) | PASS-COM-RESSALVAS | travamento resolvido pelo `\|\| true` nos três shells possíveis; reparo sem duplicar e sem tocar outros hooks. MÉDIA: guarda compara com `origin/main` local sem fetch. MÉDIA: `ensure -RepoDir` e `bootstrap.ps1` copiavam o hook sem a guarda. BAIXA: fail-open com ref quebrada não testado nem declarado. 5 de 6 mutações mortas. | guarda também no `ensure -RepoDir`; limite do `origin/main` local declarado; teste de ref quebrada (mata a mutação sobrevivente) |
