# validation.md — Gabarito de validação do v1.6.0

> Companion do `requirements.md` (mesma pasta). Define **como** o `qa-critic` valida
> cada um dos 12 itens do critério de aceite + os 13 gaps corrigidos + os 4
> anti-raso BPM. Cada seção é um procedimento binário (PASS/FAIL) — sem grau,
> sem interpretação.

## Como usar

Quando v1.6.0 entrar em qa-critic, executar cada seção abaixo na ordem.
Reprovação em **qualquer** item bloqueia o merge. Reprovações têm que ser
fechadas com fix ou redocumentadas via ADR antes de re-rodar.

---

## Bloco A — Validação dos 12 itens do critério de aceite

### Item 1 — Skill atualizada (com progressive disclosure pós-ADR-003)
- **Método (pós-ADR-003 — companion files):**
  - (a) `grep -E "^# Sub-modo \"mapeamento de processo\"" .agent/skills/discovery/mapeamento-de-processo.md` → DEVE retornar 1 match (companion file existe e tem o cabeçalho de identidade).
  - (b) grep dos cabeçalhos `###` esperados DENTRO de `mapeamento-de-processo.md`: `Filtro de entrada`, `Profundidade`, `Notação plugável`, `Formalidade configurável`, `Matriz de dimensões`, `Output em 3 arquivos`, `Integração com explorer (EARS-W5)`, `Validação com stakeholders (anti-raso A4)`.
  - (c) `grep -E "^### Filtro de entrada" .agent/skills/discovery/revisar-projeto-existente.md` → DEVE retornar 1 match (sub-modo "revisar" também é companion, com filtro de entrada simétrico — item 11 do critério).
  - (d) `grep -E "Sub-modos \(progressive disclosure" .agent/skills/discovery/SKILL.md` → DEVE retornar 1 match (SKILL.md core tem a tabela de apontadores para companions).
- **PASS:** todos os 8 cabeçalhos `###` presentes em `mapeamento-de-processo.md` + 1 cabeçalho `###` em `revisar-projeto-existente.md` + tabela de apontadores na SKILL.md core.
- **FAIL:** qualquer cabeçalho ausente, qualquer companion file ausente, ou SKILL.md core sem a tabela de apontadores.

### Item 2 — Template novo
- **Método:** `ls docs/specs/_template-process/` → DEVE listar 3 arquivos (`requirements.md`, `process-map-as-is.md`, `gap-analysis.md`). Em `process-map-as-is.md`, grep do bloco `^---$` + chaves YAML (`mode`, `depth`, `notation`, `formality`, `personas`, `validation_status`). Em `gap-analysis.md`, grep de `^## Itens para architect$`.
- **PASS:** 3 arquivos + cabeçalho YAML completo + seção "Itens para architect".
- **FAIL:** qualquer arquivo ausente, YAML incompleto, ou seção sem o cabeçalho exato.

### Item 3 — Roteador atualizado
- **Método:** grep `### Sub-modo mapeamento de processo (v1.6.0)` em `AGENT-FRAMEWORK.md`. Depois, ler 5 linhas após o cabeçalho e confirmar menção a: filtro de entrada, EARS-W1, 3 artefatos.
- **PASS:** cabeçalho presente + 3 termos no corpo.
- **FAIL:** qualquer ausência.

### Item 4 — Eval atualizado
- **Método:** ler `_meta/eval-results-papeis.md`. Localizar seção H (mínimo 9 casos numerados sequencialmente após o último de G') + seção H' (mínimo 9 casos). Contar linhas da tabela em cada uma. Verificar marca `[EMERGENTE — DESIGN-TIME, NÃO EXECUTADO]` em todos. Confirmar colunas idênticas a G+G': `# | Frase | Esperado | Roteou para | OK`.
- **PASS:** ≥ 9 casos em H + ≥ 9 casos em H' (total ≥ 18), todos marcados emergente, colunas corretas.
- **FAIL:** contagem abaixo do mínimo OU coluna divergente OU marca ausente.

### Item 5 — Exemplo trabalhado H1
- **Método:** `ls docs/specs/exemplos/H1-farma-liberacao-de-lote/` → 3 arquivos. Em cada, verificar cabeçalho YAML obrigatório (`mode: standard`, `personas: [...]`, etc.). No `process-map-as-is.md`: grep de tags `[DECLARADO]` e `[OBSERVADO]` (≥ 5 ocorrências combinadas). Grep do bloco `validation_status: VALIDADO — fictício para didática`. Grep menção explícita "compliance OUT — delegado ao high-stakes-gate" em pelo menos um dos 3 arquivos. RACI deve mencionar QC, QA e Produção.
- **PASS:** todos os checks acima.
- **FAIL:** qualquer ausência. Listar o que falta.

### Item 6 — ADR formal
- **Método:** `ls docs/adr/002-discovery-process-mapping-v160.md` → existe. Ler. Validar 5 sub-decisões na seção "Decisão" ou "Consequências": (a) feature do sub-modo, (b) sweep do "BA/processo" com texto antes/depois literal, (c) harmonização "revisar projeto existente", (d) bump de versão da skill, (e) atualização `000-template.md`. Validar ponteiro = formato `branch <nome> / data <YYYY-MM-DD> / grep <pattern>` (NÃO `Commit: <hash>`).
- **PASS:** 5 sub-decisões nomeadas + ponteiro no formato correto.
- **FAIL:** qualquer sub-decisão ausente OU ponteiro com hash como único registro.

### Item 7 — CHANGELOG
- **Método:** grep `## \[1.6.0\]` em `CHANGELOG.md`. Ler bloco. Confirmar menção a: sub-modo, 3 artefatos, filtro de entrada, 13 dimensões, 4 anti-raso, EARS-W5, exemplo H1, bump versão skill, harmonização sub-modos, atualização template ADR.
- **PASS:** todos os 10 termos presentes no bloco da v1.6.0.
- **FAIL:** qualquer termo ausente.

### Item 8 — README tabela de papéis
- **Método:** grep `mapeamento de processo` em `README.md`. Localizar contexto — deve estar em linha relativa ao papel discovery.
- **PASS:** match presente + contexto correto.
- **FAIL:** ausente ou em contexto errado.

### Item 9 — Versão da skill harmonizada
- **Método:** grep `^version: 1.6.0` em frontmatter de `.agent/skills/discovery/SKILL.md`. Verificar no CHANGELOG bloco da v1.6.0 que documenta explicitamente a correção `1.0.0` → `1.5.0` → `1.6.0`.
- **PASS:** frontmatter em 1.6.0 + correção documentada em CHANGELOG.
- **FAIL:** frontmatter divergente ou correção não-documentada.

### Item 10 — Template ADR atualizado
- **Método:** grep `Ponteiro: branch \+ data \+ grep` em `docs/adr/000-template.md`. Verificar que a linha antiga `(commit hash após aceito)` foi alterada ou complementada. ADR-001 fica intocado (já entregue).
- **PASS:** novo texto presente, lição da memória registrada no próprio template.
- **FAIL:** texto antigo intacto sem complemento.

### Item 11 — Sub-modos harmonizados (pós-ADR-003 — agora em companion files)
- **Método (pós-progressive-disclosure):** grep `^### Filtro de entrada` em CADA companion file da pasta `.agent/skills/discovery/`. DEVE retornar 1 match em `mapeamento-de-processo.md` E 1 match em `revisar-projeto-existente.md` (simetria ergonômica entre os dois sub-modos). Confirmar que o comportamento downstream do "revisar" foi preservado (texto dos 3 passos: delegar ao explorer · elicitar sobre relatório · produzir requirements.md do saneamento).
- **PASS:** 1 match em cada companion + comportamento downstream preservado em `revisar-projeto-existente.md`.
- **FAIL:** ausência de simetria, companion ausente, OU regressão no comportamento downstream.

### Item 12 — Validation gabarito existe
- **Método:** `ls docs/specs/discovery-process-mapping/validation.md` → existe. Verificar que cobre os 12 itens (este próprio arquivo).
- **PASS:** arquivo existe e cobre 12 itens.
- **FAIL:** ausente ou incompleto.

---

## Bloco B — Validação dos 13 gaps fechados pós-revisão

| # | Gap | Como confirmar fechamento |
|---|---|---|
| 1 | NF1 × NF4/NF5 (parseabilidade vs plugabilidade) | EARS-WH3 existe no requirements.md + cabeçalho YAML obrigatório no `_template-process/process-map-as-is.md` |
| 2 | Persona 4 + A4 sem escalação | EARS-I5 existe + exit-code não-zero documentado |
| 3 | Critério item 1 não-binário | Critério reescrito com cabeçalhos nomeados (verificável por grep) |
| 4 | `_template-process/` classificação errada | Reclassificado `[A CRIAR]` no item 2 do critério e em EARS-W6 |
| 5 | "Sweep leve" sem texto | NF3 contém o texto antes/depois literal |
| 6 | R2 mitigação adjetiva | Matriz MUST tem 3 colunas operacionais por nível (quick/standard/deep) |
| 7 | OUT O2 handoff vago | Template `gap-analysis.md` (item 2) tem seção `## Itens para architect` |
| 8 | Eval H+H' contagem aberta | Critério item 4 fixa ≥ 9 H + ≥ 9 H' = ≥ 18 |
| 9 | Sweep BA/processo sem ADR | Critério item 6 inclui sub-decisão (b) com texto antes/depois |
| 10 | EARS-W5 "paralelo" sem protocolo | EARS-W5 distingue single-thread vs persona-4 + diz quem cruza |
| 11 | `exemplos/H1-...` classificação errada | Reclassificado `[A CRIAR]` no item 5 do critério |
| 12 | Lacunas abertas contraditório | Seção reformulada (vide requirements.md) |
| 13 | NF7 enganoso (escopo do hook) | NF7 lista exatamente o que é/não é espelhado |

**Método:** ler `requirements.md` e cruzar cada linha acima com a localização indicada. Cada gap deve estar visivelmente fechado.

---

## Bloco C — Validação dos 4 anti-raso BPM (registro auditável)

| # | Anti-raso BPM | Validação |
|---|---|---|
| A1 | Voice of Customer / CTQ explícito | Skill: cabeçalho VoC obrigatório em `process-map-as-is.md` template. Verificar grep de "VoC" ou "Voice of Customer" no template `_template-process/process-map-as-is.md` |
| A2 | Boundaries do processo | Skill: pergunta MUST "onde COMEÇA / onde TERMINA" registrada. Template tem seção dedicada |
| A3 | Declarativo × Observacional | Skill: descrição de tags `[DECLARADO]`/`[OBSERVADO]` por atividade. Exemplo H1 (item 5 do critério) usa ≥ 5 tags |
| A4 | Validação com stakeholders | Skill: passo MUST de encerramento + EARS-I4 (humano) + EARS-I5 (persona 4) |

---

## Bloco D — Validação dos princípios invioláveis preservados

O qa-critic confirma que NENHUM dos princípios `_shared/` foi violado durante a entrega:

1. **Classificação CONFIRMADO/INFERIDO/DESCONHECIDO** — toda afirmação relevante no `requirements.md` v1.6.0 tem classificação. PASS se 0 afirmações órfãs encontradas via grep `[CONFIRMADO|INFERIDO|DESCONHECIDO]`.
2. **Anti-rename** — nenhum arquivo aprovado foi renomeado fora do ADR-002. PASS se `git log --diff-filter=R` na branch v1.6.0 retornar 0 OU se todo rename estiver listado em ADR-002.
3. **File-first** — todos os paths declarados existem após a entrega. PASS se `ls` confirma os 6 novos artefatos (template/_template-process/3 arquivos, exemplos/H1/3 arquivos, ADR-002, validation.md, fix do skill.md, fix do AGENT-FRAMEWORK.md).
4. **NÃO SEI direto, nunca inventar** — lacunas residuais marcadas `[DESCONHECIDO — runtime]`, não `[CONFIRMADO]` falso. PASS se a seção "Lacunas abertas" do requirements.md tem framing não-contraditório (gap #12 fechado).

---

## Bloco E — Critério de reprovação binário (cheat sheet)

Reprovar imediatamente se QUALQUER um destes for verdadeiro:
- Algum item do Bloco A está `FAIL`.
- Algum gap do Bloco B não está visivelmente fechado.
- Algum anti-raso BPM do Bloco C está ausente do template.
- Algum princípio do Bloco D foi violado.
- Algum arquivo declarado no critério não existe quando o `ls` roda.
- O exit-code do dry-run de persona 4 (item 5 + EARS-I5 simulado) não é não-zero quando deveria ser.

Aprovar (PASS final da v1.6.0) somente quando os 5 blocos passarem sem ressalva.

---

## Notas

- Este gabarito foi escrito pelo discovery (auto-elicitação meta) ANTES da implementação — é o **alvo** do qa-critic do v1.6.0, não um relatório retroativo.
- Estrutura espelha o padrão do `_template/validation.md` mas vai mais fundo porque o spec é meta (estende o próprio papel).
- Se o developer encontrar item infactível durante a implementação, deve voltar ao requirements.md (não burlar este gabarito). Ajustes no spec passam por discovery → architect → qa-critic.
