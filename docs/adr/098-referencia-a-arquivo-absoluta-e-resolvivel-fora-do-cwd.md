# ADR-098 — Referência a arquivo é ABSOLUTA e resolvível fora do cwd

- Status: **Aceito** (2026-08-01 — pedido explícito do dono: *"paths devem ser completos e links totalmente funcionais, visto que pode estar trabalhando em outro repo folder"*) · Decisores: dono + squad
- Tipo: **emenda ao SSoT de rastreabilidade** (`_shared/traceability/SKILL.md`, Regra 8) — não cria arquivo de regra novo, não altera roteamento nem gates.
- Relaciona: ADR-093 (premissa de ambiente é inferência com validade — mesma família: path é premissa), ADR-095 (procedência de trabalho fora do repo — mesma causa raiz: a cadeia quebra ao sair do repo), ADR-097 (conformance advisory × HARD — esta regra nasce advisory, ver §Pendências), ADR-007 (régua §0).

## Contexto

O agente opera rotineiramente com **mais de um repositório em jogo** e troca de `cwd` várias vezes
na mesma sessão. Nesse cenário, uma referência relativa só resolve na cabeça de quem a escreveu.

Diagnóstico file-first — três falhas **observadas na mesma sessão** (2026-08-01, validação de migração de dados):

1. **Temporário entregue como permanente.** Prompt de contextualização para outra IA foi entregue
   apontando para `%TEMP%\claude\...\scratchpad\` — diretório que some em limpeza de disco.
2. **Link relativo em documento que sai do repo.** O mesmo prompt usou link markdown relativo,
   destinado a ser lido por outra IA, em outro repositório: link morto no destino.
3. **Path sem declarar o repositório.** O agente afirmou que
   `<raiz>\Pasta Com Espaco\Planilha_Controle.xlsx` era "pasta inexistente". A pasta
   **existia** — no repo pai (`C:\Users\<user>\Projects\Projeto Cliente\`), não no repo
   extraído. O diagnóstico correto não era "path fantasma", era "repo errado".

Some-se um quarto, de forma: path com espaço (`Projeto Cliente`) entregue ao dono **sem aspas**,
que falha na hora no PowerShell.

Os quatro têm o mesmo defeito: **referência que só resolve no `cwd` de quem escreveu**.

**Cobertura prévia — o que já existia (não é regra nova do zero):** o **P14**
(`_shared/metacognition-core/SKILL.md`, ADR-012 v1.13.0) já exige, no pacote de handoff,
*"Localização — repositório (URL) e/ou path absoluto"*. Esta ADR **generaliza** essa exigência,
que valia só para o handoff, a todo output do agente, e acrescenta o que o P14 não cobria:
citação de path com espaço, diretório temporário como não-entrega, declaração de qual repositório
ancora o path, e verificação antes de emitir. A Regra 5 (ADR-093) é adjacente mas distinta: trata
de **verificar** premissa de ambiente, não de **emitir** referência.

## Decisão

**Invariante:** a referência resolve do ponto de vista do **destinatário**, não de quem escreveu.
Na mesma máquina isso é **path absoluto**; em consumo web (PR, issue) é **URL/permalink** — um
`F:\metacognition-framework\tools\handoff.py` numa página do GitHub é tão morto quanto um path
relativo. Relativo só dentro de arquivo cujo próprio local o ancora (import, include, link interno).

Derivadas: path com espaço vem citado no dialeto do shell alvo · diretório temporário não é
entrega (artefato reusável nasce ou é copiado para caminho permanente, e é esse que se informa) ·
declarar a qual repositório o path pertence quando houver mais de um · path é verificado antes de
emitido (Regra 1 — file-first).

Texto normativo: `_shared/traceability/SKILL.md`, **Regra 8**. Fonte única — não recopiar.

## Mecanização (entregue junto, não prometida)

- `tools/handoff.py` — o Pacote P14 passa a declarar a **raiz absoluta** da cópia
  (`raiz absoluta desta copia: <ROOT>`), o que torna resolvíveis os paths relativos que o pacote
  já listava; e `audit_paths()` audita o próprio pacote, emitindo `⚠️` para diretório temporário
  e link markdown relativo. Aviso **visível no artefato**, não bloqueante.
- `tools/test_path_absoluto.py` — canário com 10 casos: 5 que devem acusar, 5 que **não** devem
  (URL, âncora, absoluto Win, absoluto POSIX, path sem link). Conservador por desenho: falso
  positivo derruba a confiança no gate, e gate em que ninguém acredita é pior que nenhum gate.

## Régua §0 (ADR-007) — ganho líquido

Enquadra-se em **(c) destrava eval editando existente**: a regra chega com canário novo
(`test_path_absoluto.py`) e com `handoff.py` — ferramenta que já existia — passando a **emitir e
auditar** informação que antes o pacote P14 não trazia. Não é prosa a lembrar.

Sobre (a)/(b): esta emenda **não** funde nem remove, e **não** reduz tokens — a Regra 8 acrescenta
linhas ao SSoT carregado em contexto. Isso está declarado, não maquiado. O que paga o peso é a
classe de retrabalho eliminada, materializada quatro vezes numa única sessão, e o fato de a regra
nascer com mecanismo em vez de promessa de mecanismo.

## Consequências

**Positivas:** handoff e prompt de contextualização passam a ser acionáveis por outra sessão/IA
sem perguntar de volta — que é o teste binário do P14 (ADR-012). Reduz falso "arquivo não existe".

**Negativas:** paths absolutos são verbosos e **vazam layout da máquina do operador**
(`C:\Users\<user>\...`). ⚠️ **A mitigação não existe hoje:** verificado que
`tools/anonymize-map.txt` traz apenas um token de path, de um username **legado**, e
`tools/sensitive-denylist.txt` declara explicitamente que o username do mantenedor não entra
(*"AUTOR ≠ CLIENTE"*). Ou seja, o pipeline `export-clean` **não** anonimiza o path do operador.
Pendência registrada abaixo.

## Pendências

1. **Anonimização de path de usuário no pipeline público** — adicionar regra genérica
   (`C:\Users\<qualquer>` → token) ao `anonymize-map`, ou decidir explicitamente que o layout do
   mantenedor é aceitável no público. Hoje passa intacto.
2. **Cobertura parcial da mecanização:** HARD no handoff (auditado), **advisory** no restante do
   output do agente — não há canário sobre resposta ao dono, relatório ou mensagem de PR.
   Registrado em `capabilities.json` com `enforcement: advisory` — o gate emite aviso visível no artefato, não bloqueia. Não é declarado como completo.
3. **Fronteiras de julgamento:** "quando houver mais de um repositório em jogo" depende de o
   agente prever a audiência — não é auditável mecanicamente pelo process-critic.
