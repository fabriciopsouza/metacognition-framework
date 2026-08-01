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

## Regra 7 — Trabalho executado FORA do repo deixa carimbo de procedência (ADR-095)

Quando o **diretório de trabalho é EXTERNO ao repositório** — drive corporativo sincronizado,
pasta de cliente, share de rede, pasta de demanda/chamado — essa pasta recebe um
`PROCEDENCIA.md` **antes de o bloco fechar**.

O gatilho é a **FORMA da situação** (destino de escrita fora do repo), **nunca** o nome do
cliente/produto/ferramenta — o núcleo permanece agnóstico (canário `core-no-vendor`; a
instância concreta vive na aplicação de domínio, não aqui).

O carimbo declara: **demanda** (id interno/externo, sistema/objeto, solicitante) ·
**pasta** e origem do material migrado · **framework + versão + commit + branch + sessão +
operador** · **modelo por papel** · **origem e STATUS de cada artefato**
(MINUTA / PROPOSTA / MIGRADO / APROVADO) · **o que o material NÃO é** · bloqueio e decisões
pendentes.

Mecanizado — não é prosa a preencher de memória:

```bash
python tools/handoff.py --provenance "<dir externo>" --write
```

Campos do repo são **determinísticos**; campos de domínio saem como **SLOT explícito** — slot
vazio é lacuna VISÍVEL, não silêncio. Recusa alvo dentro do repo (lá a procedência é o próprio
git). Não sobrescreve carimbo existente: apenda seção de sessão (Regra 3).

> Causa raiz desta regra: a cadeia decisão→fonte→versão (Regra 4) **quebra no ponto em que o
> artefato SAI do repo**. Quem abre a pasta meses depois não sabe qual framework/versão/sessão
> produziu, nem o que ali é minuta e o que é registro. Em ambiente regulado essa distinção é a
> diferença entre insumo e evidência — e uma minuta lida como registro é achado de auditoria.

## Regra 8 — Referência a arquivo resolve no cwd do DESTINATÁRIO (ADR-098)

Generaliza o que o **P14** (`_shared/metacognition-core`, ADR-012) já exigia do handoff
("Localização: repositório (URL) e/ou path absoluto") para **todo** path emitido a humano ou a
outro agente: prompt de contextualização, relatório, checkpoint, mensagem de PR, resposta ao dono.

**Invariante:** o path resolve de onde o LEITOR está, não de onde o agente estava. Na mesma
máquina isso é **path absoluto**; em consumo web (PR, issue) é **URL/permalink**. Relativo só
dentro de arquivo cujo próprio local o ancora (import, `include`, link interno do repo).

- **Path com espaço vem citado** no dialeto do shell alvo — `cd "C:\...\Projeto Cliente"`.
  Sem aspas no PowerShell não é ambiguidade: é erro de execução.
- **Diretório temporário não é entrega.** Scratchpad, `%TEMP%`, `/tmp` somem. Artefato reusável
  nasce (ou é copiado) em caminho **permanente**, e é esse que se informa.
- **Declare a qual repositório o path pertence** quando houver mais de um em jogo — repo pai ×
  repo extraído é caso normal, não exceção.
- **Verifique antes de emitir** (Regra 1). Path citado de memória é INFERIDO; path inexistente
  entregue como certo é o modo de falha que esta regra ataca.

Mecanizado no gerador do Pacote P14 — não é prosa a lembrar:

```bash
python tools/handoff.py            # emite ⚠️ por path relativo/temporário no pacote
python tools/test_path_absoluto.py # canário
```

Cobertura **HARD no handoff**; **advisory** no resto do output (ADR-097: advisory ≠ opcional).
Débito registrado em `capabilities.json` (`enforcement: advisory` — o aviso é visível, não bloqueia).

> Causa raiz: quatro falhas na MESMA sessão (2026-08-01) — prompt entregue apontando para o
> scratchpad temporário; link relativo em documento destinado a outra IA em outro repo; path com
> espaço passado sem aspas (falhou no PowerShell); e "pasta inexistente" declarada sobre um
> diretório que **existia no repo pai**, por não declarar a qual repo o path pertencia. Mesmo
> defeito nos quatro: **referência que só resolve no cwd de quem escreveu**. Narrativa completa
> no ADR-098 — não recopiar.
