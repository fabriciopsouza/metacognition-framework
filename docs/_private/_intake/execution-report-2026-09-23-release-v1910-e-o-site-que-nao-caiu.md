# Andamento — 23/09/2026: unificação das sessões, release v1.91.0, e o site que não caiu com o repo

**Escopo:** a sessão `FRAMEWORK [61ce85]` do `iniciar` ao fechamento do release. Não cobre o
backlog do framework — para isso, `python tools/trabalhos.py listar`.
**Modelo:** autor `claude-opus-5` · QA adversarial `sonnet` isolado, **6 rodadas** em 3 blocos.
**Formato:** o painel de fases aprovado em 21/09. Os percentuais são **derivados**: cada fase
mostra `(concluídos/total)` e a barra tem 12 blocos = `round(% × 12/100)`. Conferidos por script.

---

## Onde estamos, em uma linha

> **O release fechou e a maior parte do valor não estava nele.** v1.91.0 consolidou 36 dias e três
> seções não lançadas, mas o que este dia produziu foi: **cinco sessões viraram uma**, o
> repositório-fonte voltou a privado com 36 arquivos citando clientes, **o site que servia essa
> fonte continuou no ar depois disso** — e só caiu porque o QA testou a URL em vez de acreditar em
> mim. Fechei 4 pendências e **reabri uma**, porque a correção da manhã regrediu à noite.

---

## O cronograma

```
FASE 1 · ABERTURA E LIMPEZA DE BOOT                      (6/6) ████████████ 100%
  [✓] 23/09  modo dev · fetch --prune · boot_check OK · 2 skips declarados
  [✓] 23/09  WIP reconciliado: 2 registros obsoletos achados, não 1
  [✓] 23/09  adr-113-veredito-aprovativo → TRATADO
  [✓] 23/09  skill-service-valuation → atualizado, MANTIDO ABERTO (3 resíduos reais)
  [✓] 23/09  execution-report represado desde 21/09 → PR #142, merge efa7374
  [✓] 23/09  push direto RECUSADO (GH006): a main é protegida, exige PR

FASE 2 · UNIFICAÇÃO DAS 5 SESSÕES                        (7/7) ████████████ 100%
  [✓] 23/09  ListAgents: 4 interativas no framework + 1 Remote Control
  [✓] 23/09  as 4 responderam; escopo corrigido PELO DONO: unificar quem MELHORA
  [✓] 23/09  `da` (canário de workflows) e `c4` (RUNBOOK §3.2) = núcleo
  [✓] 23/09  `5e` (CAPA GQ) e `67` (budget-ti) = domínio, fora do escopo
  [✓] 23/09  reflog confirmou: um reset --hard destruiu 47 linhas de outra sessão
  [✓] 23/09  PR #143 mergeado (4b30fd4) — salvou o commit da `c4`, que só existia no disco
  [✓] 23/09  bastão do núcleo assumido por esta sessão, sozinha

FASE 3 · A FIXTURE DA UNIÃO                              (4/5) ██████████░░  80%
  [✓] 23/09  herdada da `da` em stage, SEM veredito, ao encerrar
  [✓] 23/09  QA forçou a exceção do auto-artefato para False: 2 de 5 testes → VERMELHO
  [✓] 23/09  PR #144 mergeado (f64cbd4), verde nas TRÊS plataformas
  [✓] 23/09  fechei `uniao-por-caminho-sem-teste-que-distinga` com essa prova
  [ ]        REGREDIU: em b6c5738 o ubuntu voltou a 36/37, mesma mutação. REABERTO

FASE 4 · INCIDENTE DE EXPOSIÇÃO                          (5/5) ████████████ 100%
  [✓] 23/09  medido: repo PÚBLICO com 36 arquivos citando Natulab/Vibra/Agidesk/Thanner
  [✓] 23/09  25 deles FORA de docs/_private (CHANGELOG, bootstrap.ps1, vereditos)
  [✓] 23/09  o dono decidiu: voltar a privado. forks=0 — ninguém copiou
  [✓] 23/09  export-clean PROVADO: Natulab/Vibra/Thanner = 0 nas distribuições
  [✓] 23/09  Pages da fonte REMOVIDO — repo privado NÃO desativa o Pages dele

FASE 5 · RELEASE v1.91.0                                 (7/7) ████████████ 100%
  [✓] 23/09  3 seções não lançadas, títulos inconsistentes, 475 linhas, 14 ADRs
  [✓] 23/09  consolidadas: CHANGELOG 3.034 → 3.066, +35/-3, nenhum bloco perdido
  [✓] 23/09  checkpoint datado no history.md (exigido fail-closed)
  [✓] 23/09  4 rodadas de QA: reprovar → corrigir → corrigir → aprovar_com_ressalvas
  [✓] 23/09  PR #145 mergeado com merge-commit (08c00d9), pela convenção das tags
  [✓] 23/09  tag anotada v1.91.0 criada e propagada ao export (links 200)
  [✓] 23/09  publish-clean sincronizou os 5 repos-sombra

FASE 6 · SITE E README                                   (5/5) ████████████ 100%
  [✓] 23/09  o site vinha do Pages da FONTE PRIVADA, não do export limpo
  [✓] 23/09  3 URLs de compartilhar apontavam para o domínio morto (2 percent-encodadas)
  [✓] 23/09  README linkava o mesmo domínio em 2 lugares
  [✓] 23/09  site religado do export: HTTP 200, ZERO nomes de cliente, 32 links ok
  [✓] 23/09  vitrine e 6 web-bundles regenerados em v1.91.0

FASE 7 · LIMPEZA DE DIRETÓRIOS                           (3/3) ████████████ 100%
  [✓] 23/09  varredura de órfãos em tools/: ZERO
  [✓] 23/09  referências de versão defasadas fora dos históricos: ZERO
  [✓] 23/09  NENHUM candidato a obsoletos/ — criar a pasta vazia seria adição pura
  ← ESTAMOS AQUI: este relatório é o último item do dia
```

---

## De onde saímos → onde chegamos

| De manhã se achava | À noite se sabe | Como |
|---|---|---|
| 1 sessão concorrente | **5**, três escrevendo; e um `reset --hard` já tinha destruído trabalho | ListAgents + mtime + reflog |
| repo público é decisão de visibilidade | **expõe 36 arquivos com nome de cliente**, 25 fora de `_private` | `git grep -il` |
| tornar privado resolve | **não** — o Pages continua `public=true` e serve | `curl` deu 200 depois |
| o site sai do export limpo | **saía da fonte privada**; o correto estava dormente ao lado | API do Pages nos dois repos |
| `--force` do `trabalhos.py` preserva | **3 portas de perda**, todas silenciosas | 3 sessões, 3 respostas, 1 medição |
| a v3 consertou a união | **não** — regrediu no mesmo dia, mesma mutação | CI em b6c5738 |
| `canarios-local` protege o merge | **é cego** a este defeito, 2 vezes medido | Windows verde, ubuntu vermelho |

---

## O que eu errei, e o que derrubou cada erro

| Meu erro | O que o derrubou |
|---|---|
| citei `git reflog HEAD@{4}` como prova | índice de reflog desliza; o evento estava em outro |
| editei à mão um arquivo que se declara GERADO | o crítico **rodou** `projeto_docs.py` e ele me contradisse |
| escrevi "domínio desativado" | o crítico fez `curl` e trouxe **200** |
| troquei 4 links para uma tag inexistente | o crítico conferiu `git tag -l` |
| declarei débito já consertado no mesmo changeset | o crítico leu o diff ao lado |
| fechei a pendência da união com **um** run verde | o CI da noite |
| passei texto com crase pelo shell | o registro saiu mutilado, sem erro |

**O padrão é um só:** eu escrevia números e estados que *pareciam* medidos. O que os derrubou não
foi leitura mais atenta — foi alguém **rodar o comando**.

---

## Procedência

| Afirmação | Origem | Classificação |
|---|---|---|
| v1.91.0 mergeada em `08c00d9`, tag anotada | `gh pr view` · `git log -1 v1.91.0` | CONFIRMADO |
| site em HTTP 200 com zero nomes de cliente | `curl` + `grep` no HTML servido | CONFIRMADO |
| Pages da fonte removido | API devolve 404; CDN virou 404 no teste do QA | CONFIRMADO |
| 36 arquivos citando clientes, 25 fora de `_private` | `git grep -il` | CONFIRMADO |
| a regressão da união em `b6c5738` | log do CI: `SOBREVIVEU`, `36/37` | CONFIRMADO |
| a causa é o sandbox copiar `_meta/qa` real | `copytree` lido no código; **não reproduzido** | INFERIDO |
| os 5 sombras seguirão sincronizados | depende de cota de Actions no repo privado | DESCONHECIDO |
