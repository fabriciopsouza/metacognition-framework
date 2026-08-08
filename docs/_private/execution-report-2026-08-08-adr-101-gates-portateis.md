# Execution-report — encerramento de bloco (ADR-038/052 · tier OWNER · privado, não distribuído)

- **Release:** v1.78.0 · **ADR:** 101 · **Data:** 2026-08-08
- **Autor:** `claude-opus-5` (MEDIDO no transcript, 194 ocorrências) · **Crítico:** `claude-sonnet-5` (heterogêneo)
- **Tokens:** input 29.573 + output 1.873.930 = 1.903.503 (transcripts do Claude Code, ADR-026)
- **Tempo (wall-clock):** NÃO MEDIDO · **Turnos:** NÃO MEDIDO
- **Arquivos tocados:** 23 · **Testes:** 68 canários (2 novos, +45 asserções)
- **Rodadas de retrabalho:** 2 (bug do `porcelain`; atribuição de modelo errada)

## Origem do bloco

Auditoria falada do dono: onze queixas de que o framework "só funciona se provocado", mais comuns
**fora** do repo-mãe. A tentação era tratar onze itens. A medição mostrou **três buracos
estruturais** — espacial (enforcement não viajava), temporal (nada vigiava o fim) e relacional
(acoplamento não era modelado) — mais um erro de premissa (EDR suposto em vez de medido).

## Placar gate × achado (quem pegou o quê)

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Global com 2 gates × 17 locais; framework capado fora de casa | **dono** (queixa) → confirmado por medição | nenhum existia — virou `test_wire_gates` |
| Nenhum gate em `Stop`; encerramento parcial | **dono** (queixa) → confirmado no `settings.json` | nenhum existia — virou `closing_gate` |
| Par correlato só atualizado sob provocação | **dono** (queixa) | nenhum existia — virou `correlated.py` |
| `mission_gate`/`compaction_gate` com `cwd = ROOT` (auditariam o framework, não o projeto) | **agente**, ao preparar o wiring global | nenhum — só aparece quando os gates viajam |
| `porcelain()` cortando 1 char do 1º path (`.strip()` no helper git) | **canário do próprio bloco** | `test_closing_gate` (criado no bloco) |
| `test_dev_dogfood` verde há 2 meses medindo só existência | **agente**, ao investigar a queixa cross-IA | o próprio, que delegava frescor a "disciplina do `/checkpoint`" = prosa |
| README(1.77.0) × CHANGELOG defasado sem canário | dívida pré-existente do backlog | `test_marketing_claims` (+1 asserção agora) |
| **Autor declarado `fable` quando o transcript dizia `opus`** | **dono** | `author-tier-gate` — DETECTAVA certo, mas aceitava `--author-model` como override incondicional |
| Vitrine em 1.77.0 | `test_marketing_claims` | ele mesmo (funcionou) |

## Detecção: framework × humano

- **Framework pegou:** 4 (canário de capacidade órfã, marketing/vitrine, `test_closing_gate` pegando
  o bug do autor, `correlated` cobrando CHANGELOG/AGENTS/PROMPT-WEB do próprio autor).
- **Humano (dono) pegou:** 3 — as três queixas estruturais **e** a atribuição de modelo errada.
- **Leitura honesta:** o dono continua sendo o detector mais eficaz dos furos de processo. Os gates
  pegam o que já foi mecanizado; ninguém mecaniza o que ainda não percebeu. Princípio 11 honesto.

## Gaps (flagados, não silenciados)

- **Cascata master → espelhos (public/premium/nonadmin/gemini) colide com ADR-069/070.** O
  `shadow_write_guard` nega, em código, master→remote-alheio e shadow→push. Automatizar exige
  emendar um controle **anti-injeção de prompt**. Registrado como trabalho `adr-102-cascata-distribuicoes`;
  recomendação inicial: inverter o sentido (cada espelho PUXA por Action agendada), preservando a
  write-isolation e ainda assim sem depender de ordem do dono.
- `bootstrap.py` ainda instala o perfil non-admin (sem hooks) como default — agora contrariado pela
  medição do `--init-env`. Revisar se o modo se justifica.
- `PROMPT-CHAT-WEB` recebeu a regra nova como **prosa** (§3.7): ambiente sem filesystem não tem hook.
  Limite honesto, não descuido.

## Melhorias do framework (régua §0 declarada por porta)

- (a) fusão: `wire_gates.py` substitui `ensure-global-wiring.ps1` + parte de `sync-global.ps1`;
  `_project.py` funde 3 resoluções ad-hoc de raiz.
- (c) destrava eval: `closing_gate` (gates que existiam e nunca disparavam), `--init-env`
  (`env-applicability` em skip permanente), `correlated` (meia-atualização era inavaliável),
  frescor do dogfood (existência ≠ prática), trava anti-overclaim do `author-tier`.

## Boas práticas (reutilizável)

- **Medir antes de projetar.** "17 × 2 gates" mudou o diagnóstico de "onze queixas" para "três
  buracos". Sem `Get-Content settings.json` dos dois escopos, eu teria escrito onze remendos.
- **Deixar o gate novo rodar contra o próprio autor.** `correlated` cobrou de mim o CHANGELOG e o
  PROMPT-WEB; o `overwrite-guard` me bloqueou por não ter lido o `AGENTS.md`. Gate que só vale para
  os outros é teatro.
- **Ler o docstring como suspeito.** `test_dev_dogfood` **confessava** por escrito que frescor era
  "disciplina do /checkpoint". A confissão estava lá há dois meses e ninguém leu.

## Lições por skill (agnóstico — servem a outro projeto)

- **dev:** helper que faz `.strip()` genérico corrompe formato onde coluna 1 é significativa
  (`git status --porcelain`). Só a 1ª linha quebra — bug que passa em revisão visual.
- **qa-critic:** heterogeneidade **medida**, não pretendida. Spawnar o crítico "no outro modelo"
  sem verificar qual é o seu dá auto-revisão com aparência de gate.
- **architect:** pedido legítimo do dono pode colidir com controle de segurança aceito. Surface a
  colisão e proponha o caminho que preserva o controle (inverter o sentido do fluxo), em vez de
  furar o gate ou recusar o pedido.
- **pmo:** onze sintomas raramente são onze causas. Agrupar por **mecanismo ausente** (espaço,
  tempo, relação) rendeu 3 correções em vez de 11 remendos.
- **docops:** versão vive em ≥4 lugares (README, CHANGELOG, vitrine, prompt web). Sem canário
  comparando o par, um deles fica para trás — e ficou.

## Método-audit (para o `## Aprendizado` do history)

**A falha mais instrutiva do bloco foi minha, e é sobre este framework.** Eu presumi que o
`/model claude-fable-5` do dono tinha pegado, e **alimentei o gate com a suposição**
(`--author-model claude-fable-5`). O `author-tier-gate` detecta corretamente pelo transcript —
mas aceitava a flag como override incondicional, então repetiu minha suposição de volta como se
fosse medição, e ainda me deu ✅. Consequência em cascata: spawnei o qa-critic no meu próprio
modelo, quebrando a heterogeneidade do ADR-011/078.

Causa-raiz: **um gate que aceita a autodeclaração do auditado não é gate.** Corrigido no mesmo
bloco (declaração só pode rebaixar; superestimar cai para o detectado, com aviso).

Quem pegou foi o dono — perguntando *"tem certeza que não pegou um snapshot e usou como verdade?"*.
Vale registrar que a pergunta dele foi mais eficaz que qualquer canário: nenhum mecanismo do repo
compara "o que o agente afirma sobre si" com "o que o transcript mostra", exceto agora este.
