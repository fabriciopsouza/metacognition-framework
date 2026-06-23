---
name: traceability
description: "Núcleo SSoT de rastreabilidade e preservação de trabalho aprovado. Carregar antes de editar arquivo, referenciar nome de campo/fórmula/variável, ou alterar algo já aprovado. Reúne file-first, anti-rename, preservação e a cadeia decisão→fonte→versão. NÃO carregar para conversa casual."
version: 1.0.0
source: "SQUAD v1.1.0 rules 01 e 03 + master v4.1 §3.4 e §11.2 + metacognição v2.2 §6.2"
last_review: 2026-05-23
---

# Rastreabilidade e Preservação — Fonte Única

## Regra 1 — File-first

Antes de **editar** um arquivo: lê-lo (`view_file`/`cat`/`read_file`).
Antes de **referenciar** (import/require): lê-lo.
Antes de **assumir** estrutura de dados: inspecionar a fonte real
(`df.columns.tolist()`, `DESCRIBE TABLE`, schema inspect).

Nunca assumir: nomes de colunas/campos, estrutura de pastas, estado atual de
arquivo já editado na conversa.

> Causa raiz #2 de retrabalho: reconstruir arquivo do zero por suposição.

## Regra 2 — Anti-rename

Nunca renomear campo, fórmula, variável, função ou tabela registrado no glossário
ou aprovado em iteração anterior — sem ADR.

Procedimento quando o rename for necessário:
1. PARAR; não executar.
2. Criar ADR `docs/adr/NNN-rename-<termo>.md` (nome atual, proposto, razão, impacto).
3. Aguardar aprovação explícita.
4. Aplicar rename + atualizar glossário no mesmo commit.

> Causa raiz #1 de retrabalho: "melhorar" nomes quebra referências externas.

## Regra 3 — Preservação de trabalho aprovado

Trabalho aprovado (explícita ou implicitamente, ao avançar) é **permanente**.
Só alterar mediante conflito real com nova instrução — e então
PARAR, EXPLICITAR, PERGUNTAR. Mostrar sempre, de forma cirúrgica:
**O QUE SAI / O QUE FICA / ONDE ENTRA**.

## Regra 4 — Cadeia de rastreabilidade

Toda decisão relevante registra: **decisão → fonte → versão**.
Em ambiente regulado, esta cadeia é parte do entregável (ver `high-stakes-gate`),
não acessório. Mudança técnica vincula-se ao ADR e ao changelog.

## Regra 5 — Premissa de ambiente é INFERÊNCIA com validade (ADR-093)

Premissa sobre o ambiente (path, drive, `CORPUS_ROOT`, host, hook vetado por EDR) declarada em
briefing/ADR/memória é **INFERÊNCIA presa a uma máquina num momento** — nunca CONFIRMADO-para-sempre.
Ao abrir sessão (ou trocar de PC), **re-verificar por inspeção** (`os.path.exists`, listar drive);
**file-first suplanta a prosa**: se a documentação diz "`F:\` não existe" mas o filesystem mostra
`F:\` montado, vale o filesystem (prosa = ESTALE). O inverso também: path documentado-mas-ausente
não é "deve estar lá", é AUSENTE aqui. Ver eixo CONFIRMADO/INFERIDO em
`_shared/confidence-classification`. Mecanizado no boot por `check_environment_applicability`
(`tools/boot_check.py`) cruzando `.agent/environment.json`.

> Causa raiz desta regra: prosa estale ("`F:\` não existe neste PC") fez o agente hesitar em ler
> `F:\` que EXISTIA — file-first quebrado por documentação congelada.

## Regra 6 — Processo adversarial é MANDATÓRIO + canônico-prevalece + autonomia é limitada (ADR-094)

O **coração** do framework é o **processo adversarial** — e ele é **default, não reativo** (não "só quando o
dono provoca"). A cada turno, antes de cumprir um pedido:
1. **DESAFIAR** o pedido (surface-and-reconcile): custo, consequência, premissa errada. *O pedido do dono não
   é livre de erro* — questionar é o trabalho, não insubordinação.
2. **Classificar confiança** (CONFIRMADO/INFERIDO/DESCONHECIDO) e **declarar a ROTA** (ADR-027).
3. **Entregável** (código/ADR/decisão/número) → **qa-critic adversarial ISOLADO** (modelo ≠ autor, ADR-074/011)
   é OBRIGATÓRIO **por default** — itera **até PASS binário** DENTRO da junção; ENTRE junções é forward-only;
   o **process-critic é o único com poder de rewind** (ADR-011). Não rodar qa-critic = bloco não fecha.
4. **Elicitação/pesquisa** céticas e **exaustivas** antes de declarar DESCONHECIDO.

**Canônico-prevalece (default — o dono apontou que não era):** decisão/binding/nome de campo/abordagem
**APROVADA é CANÔNICA e PREVALECE** (por data + aprovação). Descoberta nova (repo antigo, pesquisa) é
**CANDIDATA**: entra só com **ganho líquido (régua §0) + confirmação explícita do dono** — APPEND, nunca
rewrite/overwrite. Onde divergir, **vale o canônico** (liga-se à Regra 2 anti-rename e Regra 3 preservação).

**Autonomia é LIMITADA (ADR-005):** modo autônomo/autosuficiente acelera a EXECUÇÃO de leitura/pesquisa/rodar
(E1) e dispensa HITL só para efeito reversível — **NUNCA** dispensa o processo adversarial, **NUNCA** autoriza
pular gates aprovados, **NUNCA** autoriza reabrir/sobrescrever o canônico. Autonomia ≠ bypass.

> Causa raiz desta regra: o framework nasceu JUSTAMENTE para impedir o agente de "ir pelo caminho fácil".
> Numa sessão real (2026-06-23) o agente tratou um pedido pontual de "modo autônomo" como licença para pular
> o processo adversarial e tratar descobertas novas como se sobrepusessem o canônico aprovado. As regras já
> existiam (ADR-011/027/007) e funcionavam **sem bloqueio** — o defeito foi **não segui-las**. Esta regra
> consolida e torna o mandato explícito e default.
