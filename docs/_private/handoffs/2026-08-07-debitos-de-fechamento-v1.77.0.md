# Handoff — débitos de fechamento do bloco v1.77.0

> **Tipo:** handoff de JULGAMENTO (achados + recomendação). Complementa — não substitui — o
> Pacote P14 determinístico, que é **regenerável a qualquer momento** com `python tools/handoff.py`
> (ADR-076). O que está aqui é o que a ferramenta não deriva sozinha.
>
> **Capturado em:** 2026-08-07 (sexta), sessão de `/start-session` · papel: pmo · autor: opus
> **Repositório:** `https://github.com/fabriciopsouza/metacognition-framework` (privado)
> **Âncora do estado capturado:** `main` @ `8820608` — versão declarada **v1.77.0**
> **Origem dos achados:** retrospective gate (passo 4 do `/start-session`, ADR-024) sobre o
> último bloco entregue (v1.77.0 / ADR-100, merge do PR #115 em 2026-08-04 21:27 -03).

---

## REGRA DE APLICAÇÃO — leia antes de tocar em qualquer coisa

Este documento **não autoriza mudança**. Ele registra achados congelados em `8820608`.

**Nenhum item pode ser aplicado sem antes ser RE-VALIDADO contra a versão vigente no momento
da aplicação.** O repositório pode ter avançado; qualquer um dos achados pode já ter sido
corrigido, ou ter mudado de forma. Cada item abaixo traz:

1. **Comando de re-validação** — roda primeiro, sem escrever nada.
2. **Aplicar SÓ SE** — o predicado binário que precisa ser verdadeiro *agora*.
3. **Se o predicado for falso** — o achado está quitado: **remova-o daqui** e registre no
   checkpoint. Não "reaplique por via das dúvidas".

Ordem sugerida: F1 → F2 → F4. O F3 não é código (ver a limitação declarada nele).

Gate obrigatório antes de fechar qualquer aplicação: `python tools/run_canaries.py`
(o CI do GitHub Actions **não** é o portão deste repo).

---

## Estado congelado na captura (para comparação futura)

| fato | valor em `8820608` (2026-08-07) |
| --- | --- |
| topo do `CHANGELOG.md` | `1.77.0` |
| tags existentes | até `v1.75.0` (`v1.76.0` e `v1.77.0` **ausentes**, local e em `origin`) |
| 1º checkpoint do `history.md` | `## 2026-08-02 — Release v1.76.0` (linha 12) |
| 2º checkpoint do `history.md` | `## 2026-08-03 — Release v1.77.0` (linha 69) |
| `boot_check` | OK — 5 PASS, 2 skips declarados (`cross-ai-boot-scan`, `env-applicability`) |
| `trabalhos.py listar` | `nenhum trabalho em aberto` (diretório `~/.claude/trabalhos/` inexistente) |
| branches remotas vivas | `main`, `feature/history-rotation` (1 commit, ADR-092), `feat/adr-100-registro-de-trabalhos` (órfã, já mergeada no #115) |

---

## F1 — `history.md` está fora de ordem, e isso corrompe o Pacote P14 em silêncio

**Confiança: CONFIRMADO** (observado ao vivo na sessão de captura).

O cabeçalho do próprio arquivo (`history.md`, linhas 3–5) declara a invariante: os checkpoints
são **mais-novo-primeiro** e *"o estado atual é o checkpoint do TOPO"*. A invariante está
quebrada: o bloco de **v1.77.0 (2026-08-03)** foi inserido **abaixo** do de **v1.76.0
(2026-08-02)**, em vez de acima.

**Consequência medida, não teórica:** `tools/handoff.py`, função `latest_checkpoint_field()`,
usa `re.search` do **primeiro** `## YYYY-MM-DD` do arquivo — é posicional e confia na
invariante. Com a ordem invertida, `python tools/handoff.py` emitiu como objetivo da próxima
sessão *"escrever o canário da `validation-reporting`"* — o **Próximo passo de v1.76.0**, não
o de v1.77.0 (*"validar o mecanismo no uso real"*). O pacote apontou para o alvo errado sem
nenhum aviso. Nenhum canário compara a ordem dos checkpoints.

**Comando de re-validação:**

```bash
grep -n "^## [0-9]\{4\}-" history.md | head -5
```

**Aplicar SÓ SE** as datas retornadas **não** estiverem em ordem decrescente.

**Correção:** mover o bloco `## 2026-08-03 — Release v1.77.0 …` (do seu `##` até a linha
imediatamente anterior ao `##` seguinte) para **acima** do bloco de v1.76.0. É movimentação de
texto — nenhuma palavra do conteúdo muda.

**Observação secundária (INFERIDO, não bloqueia):** o checkpoint declara `2026-08-03`, mas o
commit correspondente (`ca39f46`) e o merge (`8820608`) são de `2026-08-04 21:23/21:27 -03`.
Provável sessão virada de data escrita antes do commit. Não altera o achado — mesmo com a data
declarada de 08-03, o bloco deveria estar acima do de 08-02. Se for corrigir, corrija a data
junto; se não, deixe como está e não reabra.

---

## F2 — v1.76.0 e v1.77.0 não têm tag (2ª ocorrência de uma falha já catalogada)

**Confiança: CONFIRMADO.**

A política no topo do `CHANGELOG.md` (linhas 8–9) diz: *"Tag, número no `README.md` e nome do
.zip sobem juntos a cada release"*. As duas últimas releases estão no CHANGELOG e no README e
**não foram tagueadas** — nem local nem em `origin`.

Por que passou: `boot_check` → `version-sanity` lê a versão do **CHANGELOG**, não do `git tag`,
e declarou "v1.77.0" com ✅. O `consistency-gate` (ADR-030) é fail-soft no `docops §Encerramento`
e fechar sem tag não derruba nada. Os dois gates olham a release; nenhum olha a tag.

**Não é a primeira vez.** O `## Aprendizado` do `history.md` registra em **2026-06-02** o mesmo
defeito (*"3 tags ausentes (v1.36/37/38)"*), com a proposta marcada como *"não-preemptiva,
aguarda 2ª ocorrência confirmatória"*. **Esta é a 2ª ocorrência confirmada — o gatilho que o
próprio bloco definiu foi atingido.**

**Comando de re-validação:**

```bash
git tag -l "v1.76.0" "v1.77.0"
git ls-remote --tags origin | grep -E "v1\.7[67]\.0"
```

**Aplicar SÓ SE** ambos vierem vazios (ou só um deles — nesse caso aplique só o que falta).

**Correção — convenção verificada:** a tag aponta para o **merge commit do PR**, não para o
commit da feature (`v1.75.0` → `d2180cf` = merge do #112; `v1.73.0`/`v1.74.0` → `d4c7d61` =
merge do #110).

| tag | commit alvo | o que é |
| --- | --- | --- |
| `v1.76.0` | `1f3e6db` | merge do PR #113 — ADR-099 validation-reporting |
| `v1.77.0` | `8820608` | merge do PR #115 — ADR-100 registro de trabalhos |

> **Confirme os hashes contra o log vigente antes de taguear** — se houve rebase/force-push
> desde a captura, eles mudaram. `git log --oneline --merges -6` resolve.

**GATE HUMANO (action-safety T3 — efeito externo, irreversível na prática):** `git push origin
<tag>` publica no `origin`. **Requer confirmação explícita do dono.** Tag empurrada e depois
removida deixa rastro em quem já buscou. Criar a tag local é reversível; empurrar não é.

---

## F3 — o registro de trabalhos do ADR-100 foi entregue e nunca foi alimentado

**Confiança: CONFIRMADO na máquina de captura. NÃO VALIDÁVEL de outra máquina** — ver limitação.

O critério de aceite escrito no próprio checkpoint de v1.77.0 era: *"abrir a próxima sessão e
confirmar que o trabalho registrado é oferecido na abertura sem que ninguém peça"*. Na sessão
de captura:

- **Passou:** o gate `trabalhos-abertos` rodou e **falou** — `nenhum trabalho em aberto`. Não
  ficou silencioso, que era metade do requisito.
- **Falhou:** `~/.claude/trabalhos/` **não existe**. O caso de origem — a validação com 2,88
  milhões de comparações, 17 objetos pendentes e 3 decisões esperando o dono — nunca foi
  registrado. Com registro vazio, o critério de aceite é **inatingível**.

O padrão é o já catalogado três vezes no `## Aprendizado`: *mecanismo existe mas não dispara*.
Aqui a parte que não dispara **não é mecanizável** — o próprio ADR-100 declara: *"o conteúdo do
resumo é escrito pelo agente e não é mecanizável — só o ciclo de vida é"*.

**Comando de re-validação:**

```bash
python tools/trabalhos.py listar
```

**LIMITAÇÃO DECLARADA — leia se estiver em outra máquina:** o registro vive em
`~/.claude/trabalhos/`, **fora do git, por decisão do ADR-100** (para ser cross-repositório).
Consequência: **em qualquer máquina diferente, `listar` retornará vazio, e isso não é
evidência de nada.** Este achado só é verificável na máquina onde o trabalho de origem rodou.
Não conclua "quitado" a partir de um `listar` vazio numa máquina nova.

**Não há correção de código.** É uma decisão sua: (a) registrar o trabalho de origem
retroativamente, se ainda tiver pendências vivas; ou (b) declarar o critério de aceite do
ADR-100 como **não atendido nesta rodada** e registrar isso no próximo checkpoint — o que já
seria honesto e suficiente.

---

## F4 — candidato de mecanização (o que impede F1 e F2 de voltarem)

**Status: proposta. Exige ADR? Não** — é asserção em gate existente, não decisão de arquitetura.
Mas exige **qa-critic heterogêneo** antes de fechar (autor foi opus → crítico em tier max).

F1 e F2 são a mesma classe de defeito: **invariante escrita em prosa, sem mecanismo que a
compare com a realidade**. O alvo já existe — `tools/test_consistency_closing.py` já é o gate de
*version-claim* no fechamento. Ganha duas asserções:

1. **ordem dos checkpoints:** as datas dos `^## \d{4}-\d{2}-\d{2}` do `history.md` em ordem
   decrescente — falha se não estiverem.
2. **tag × topo do CHANGELOG:** `git tag` contém a versão do topo do `CHANGELOG.md` — falha se
   não contiver.

**Régua §0 (ADR-007):** passa pela porta **(c)** — destrava eval **editando arquivo existente**,
sem canário novo. *Se ao implementar isso virar arquivo novo, a alegação da porta (c) cai e a
régua §0 precisa ser re-argumentada — não racionalize (precedente ruim: ADR-098/ADR-099).*

**Nota de escopo:** o backlog do `history.md` já tem um item vizinho — *"Canário README × topo do
CHANGELOG inexistente"*, com trigger *"2ª ocorrência OU dono declarar"*. É a **mesma asserção,
outro par de arquivos**. Ao implementar F4, **funda os dois** em vez de somar um terceiro
comparador — isso muda a régua §0 da porta (c) para a porta (a) (funde/remove ≥ adiciona), que é
mais forte.

---

## Como recuperar este handoff de qualquer máquina

```bash
git clone https://github.com/fabriciopsouza/metacognition-framework
cd metacognition-framework
git pull --ff-only
cat docs/_private/handoffs/2026-08-07-debitos-de-fechamento-v1.77.0.md
```

Não depende do `cwd` de quem escreveu, de pasta temporária, nem de `~/.claude/` local (ADR-098,
regra 8). Os paths citados aqui são **relativos à raiz do repositório acima**.

**Como ele volta a ser oferecido sem ninguém pedir:** há uma linha-ponteiro na seção
`## Em aberto` do `history.md`. Essa seção é lida por `tools/handoff.py` → `em_aberto()` e sai
em **todo** Pacote P14, em toda sessão, em qualquer máquina. Enquanto a linha existir, o handoff
é oferecido.

**Como encerrar:** quando os itens forem aplicados (ou declarados quitados), remova a
linha-ponteiro de `## Em aberto` **e** registre o fechamento num checkpoint datado — é a higiene
v1.58.1 já declarada naquela seção. Remover sem registrar apaga o rastro.

---

## O que este handoff NÃO cobre

- `docs/_private/handoffs/handoff-latest.md` (de 2026-07-28, v1.74.0) segue **não-commitado e
  obsoleto**. É saída gerada — regenerável com `python tools/handoff.py`. Não foi commitado de
  propósito: versionar um retrato errado do estado é pior que não ter retrato.
- Branch `origin/feat/adr-100-registro-de-trabalhos` — órfã, já mergeada no PR #115. Limpeza
  trivial, fora do escopo deste handoff.
- Branch `origin/feature/history-rotation` — 1 commit não-mergeado (ADR-092, rotação do
  `history.md`, status `Proposto`). **Vizinho relevante:** o hook `context-budget` reclamou 3
  vezes na sessão de captura — `history.md` tem ~44k tokens contra orçamento de 6k. A rotação
  que resolveria isso está parada nessa branch. Decisão sua, não achado.
- Skip declarado no boot: `.agent/environment.json` ausente (ADR-093).
