# ADR 009 — Método sênior de discovery (domain-agnóstico) + auto-melhoria do framework

- **Status:** Aceito (2026-05-28 — qa-critic rounds 1+2+3 incorporados em commits `01e598a` (2 ALTO + 4 MEDIO + 1 BAIXO), `f622f89` (4 MEDIO + 1 BAIXO + 2 ADV), `3d96d94` (3 MEDIO + 1 BAIXO + 2 ADV); round 4 confirmou substância LIMPA — único bloqueador residual era a auto-referência meta-recursiva do próprio campo Status (sempre 1 round atrás), resolvido nesta promoção. Total: 4 rounds adversariais, 16 findings endereçados.)
- **Data:** 2026-05-28 · **Decisores:** Fabricio (mantenedor) + Claude (papel `architect`)
- **Substitui:** nenhum · **Substituído por:** nenhum (integral) · **EMENDADO por ADR-051** (2026-06-01): o **passo-1 (filtro de entrada)** — que mandava "não inferir por sinais semânticos" e exigia fonte declarada — era o **bug provado** (o método nunca carregou no caso AIVI/Vibra). ADR-051 muda o gatilho para **disparar também por sinais de stake INFERIDOS** (`context-signals.txt`) e **mecaniza** vigência+pertinência no `context-brief` (gate `check_context_brief.py`).
- **Relaciona-se a:** ADR-002 (discovery v1.6.0), ADR-003 (progressive disclosure), ADR-007 (régua §0 + pesquisa-cascata + ex-G9/ex-G11), **ADR-051 (reparo do gatilho + mecanização)**
- **Fonte:** case real AIVI (2026-05-27, repo `LIMITES-BATENTES-RECALC` branch `claude/discovery-aivi-metodo-2026-05-27`); audit trail em memória `[[framework-gaps-from-aivi-case-2026-05-27]]`; substância em `[[senior-discovery-method]]` e `[[framework-self-improvement]]`.

## Contexto

O case AIVI (distribuição de combustíveis Vibra, ambiente regulado, decisão executiva, perda financeira real) foi o **case real de validação** do framework. A esteira `start-session → explorer → discovery sub-modo pesquisa-cascata → research-brief → spec numerada` foi executada e funcionou conceitualmente — produziu 3 artefatos auditáveis em ~uma sessão. **Mas** o nível sênior necessário só foi atingido após ~10 correções do dono numa única sessão. Padrões de falha observados:

1. Citei norma (ANP 58/2014) sem checar vigência — estava revogada há 7 meses.
2. Conflei norma de outro segmento (ANP 884 = varejo) como se regulasse distribuidor — analogia tratada como regra.
3. Despriorizei regra de negócio (Gate-C ≥50%) como "cosmética" sem entender semântica anti-fraude.
4. Não antecipei pontos pertinentes que o dono não pediu (biodiesel, FCV vs ambiente, estoque mandatório, audit trail).
5. Critiquei só o produto (código), não o método (a própria discovery).
6. Inflei várias vezes, exigindo correção explícita "lean, consciente, não preguiçoso".
7. Várias correções repetiram o mesmo padrão entre turnos — o framework não internalizou estruturalmente.

Diagnóstico: o framework é capaz de produzir output sênior, mas o **default operacional** ainda não é sênior. Sob peer pressure, sim. Por padrão, não. E **não se auto-melhora** — depende do dono carregar o ônus de re-ensinar entre sessões.

Pedido textual do dono (2026-05-27): "este approach sênior deve ser método do framework em si, aplicável em QUALQUER domínio". E: "o framework deve perceber estes insights sozinho, e propor a melhoria, focado em lean, otimização, eficiência, eficácia, resultado, mas sênior e preciso".

## Decisão (1 frase ativa)

Adicionar **(a) o método sênior de discovery em 8 passos** como reforço condicional do discovery — domain-agnóstico, carregado sob demanda quando há fonte canônica/normativa citada (companion `metodo-senior.md`, ADR-003) — e **(b) o princípio de auto-observação** do framework no §6 do `AGENT-FRAMEWORK.md` (princípio 11) + mecanismo lean de method-audit autônomo no `/checkpoint`, sem criar workflows/templates/pastas novas.

## Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Escopo enxuto: ADR + 1 companion + 9 edições cirúrgicas (escolhida — escopo cresceu de 4 para 9 pós-qa-critic rounds 1 e 2; ver §Implementação)** | Aplica régua §0 (1 novo arquivo de decisão + 1 companion progressive disclosure + edições 1-3 linhas em 4 arquivos existentes). Resolve as 2 propriedades-chave (método sênior agnóstico + auto-observação). Sem custo fixo novo no caminho rápido. | Senior method fica em companion (não inline na SKILL.md) — risco de não ser lido sob demanda. Mitigação: filtro de entrada explícito + gatilhos no SKILL.md base. |
| 2 | Inline na `discovery/SKILL.md` (sem companion) | Sempre carregado, garantido visível. | Infla SKILL.md em ~50 linhas para algo que só vale quando há fonte canônica. Fere ADR-003. Caminho rápido (modo PMO sem discovery) paga custo desnecessário. |
| 3 | Nova skill independente `senior-discovery` | Skill própria, fácil de auditar. | Duplica responsabilidade do discovery; fere SSoT. Régua §0 rejeita criação de skill onde companion + edição cirúrgica resolve. |
| 4 | Apenas o ADR + edições, sem companion (princípio sem detalhe acessível) | Mínimo absoluto. | Os 8 passos ficam só no ADR — não-carregáveis pelo agente no runtime. Reduz à decisão registrada sem operacionalização. |
| 5 | Aplicar só método sênior, deixar auto-melhoria para outro ADR | PR menor, foco. | Os dois nasceram do mesmo case e se reforçam (método observado + observação automática). Separar dobra superfície administrativa. |
| 6 | Não fazer (status quo) | Zero esforço. | O dono explicitamente pediu absorção: "isso é o objetivo maior aqui". Framework regride à média a cada sessão. |

## Justificativa

Escolha pela **Alternativa 1** segue 4 princípios:

- **Régua §0 (ADR-007)**: 1 novo arquivo de decisão (ADR-009) + 1 companion progressive disclosure (`metodo-senior.md`) + 9 edições cirúrgicas (1-3 linhas cada; 5 nasceram dos rounds 1 e 2 do qa-critic). Adição mínima necessária; rejeita criação de workflow/template/skill nova.
- **Progressive disclosure (ADR-003)**: companion carregado sob demanda quando há fonte canônica/normativa citada — não infla SKILL.md, não paga custo no caminho rápido.
- **SSoT**: o método agnóstico vive em UM lugar (companion); SKILL.md referencia, demais skills referenciam o discovery. Sem duplicação.
- **Pertinência ao objetivo do dono**: método **agnóstico de domínio** (não restrito a "regulado"); aplicável em dev/BI/BPM/regulado/qualquer caso onde há fonte citada.

Decisão pela auto-observação no §6 (princípio 11) ao invés de skill nova: princípio é onde já vivem os invariantes do framework; method-audit é a operacionalização dele no `/checkpoint` (que já é o ponto de captura de aprendizado pela ADR-007). Plugar no existente > criar paralelo.

### Decisões internas do architect

1. **Princípio 11 vai no §6** (após princípio 10 / régua §0). 1 linha; referencia este ADR.
2. **Companion `metodo-senior.md`** segue ADR-003: carregado sob demanda, NÃO infla SKILL.md base. Filtro de entrada explícito (passo 1 do algoritmo).
3. **`anti-hallucination/SKILL.md` ganha 1 anti-pattern**: "citar norma/spec/doc externa sem checar vigência (em vigor? alterada? revogada?)" — atende item B dos insights AIVI; integrado ao núcleo SSoT, não duplicado.
4. **`checkpoint.md` ganha 2-3 linhas**: mecanismo de **method-audit notes** autônomo (0-3 notes/sessão), plugado no `## Aprendizado` da history.md (ex-G9 / ADR-007), com firewall preservado (notas inertes até virar skill/regra mergeada).
5. **Discovery `SKILL.md` ganha 3 linhas**: aponta para o companion sob a condição "há fonte canônica/normativa citada" — não vira sub-modo (não é um modo, é um reforço transversal).
6. **Sem edição em `output-format` e `high-stakes-gate`** nesta v1.10.0: antecipações como entregável vivem no companion (cita output-format por referência); auto-load do high-stakes-gate fica como follow-up (low-risk, alta complexidade de gatilhos — separar bloco).
7. **CHANGELOG.md** ganha bloco [1.10.0]; **CLAUDE.md + AGENTS.md ATUALIZADOS** com seção v1.10.0 (decisão revisada pós-qa-critic round 1: precedente v1.9.0 manda atualizar entry points para features de magnitude equivalente — não-bloqueante mas honra de consistência).
8. **Bump v1.9.0 → v1.10.0** (feature minor: novo reforço + novo princípio; compatível).

## Implementação

### Arquivos criados/alterados na v1.10.0

Escopo: **2 novos + 9 edições cirúrgicas (incluindo CHANGELOG)** — post-qa-critic rounds 1 e 2 (escopo original na proposta era 2 novos + 4 + 1 CHANGELOG; cresceu 5 arquivos pela incorporação adversarial — todas edições de 1-3 linhas):

| Arquivo | Mudança | Justificativa régua §0 |
|---|---|---|
| `docs/adr/009-metodo-senior-discovery-auto-melhoria-framework.md` | **NOVO** (este arquivo) | Critério (c): registra decisão arquitetural inalcançável editando ADR existente |
| `.agent/skills/discovery/metodo-senior.md` | **NOVO companion** (~70 linhas) | Critério (c) + ADR-003: detalha 8 passos sob demanda; não infla SKILL.md base |
| `.agent/skills/discovery/SKILL.md` | **+3 linhas** | Aponta para companion sob condição; cirúrgico |
| `_shared/anti-hallucination/SKILL.md` | **+2 linhas** | Anti-pattern de citar sem vigência; cirúrgico |
| `.agent/workflows/checkpoint.md` | **+3 linhas** | Method-audit autônomo plugado em `## Aprendizado` existente |
| `AGENT-FRAMEWORK.md` (§6) | **+1 linha** (princípio 11) | Auto-observação do framework |
| `docs/specs/_template-research/research-brief.md` | **+§7 Antecipações + §8 Backlog + renumeração 7→9, 8→10** (round 1 fix A2) | Gate funcional do output sênior; sem template a obrigatoriedade era fictícia |
| `CLAUDE.md` | **+1 seção** v1.10.0 (round 1 fix M5) | Entry point Claude Code; precedente v1.9.0 |
| `AGENTS.md` | **+1 seção** v1.10.0 (round 2 fix BAIXO-1) | Entry point cross-tool; sync com CLAUDE.md |
| `.agent/skills/discovery/pesquisa-cascata.md` | **+1 nota** de reciprocidade no output (round 2 fix ADV-2) | Sobreposição cascata+sênior explicitada (evita omissão silenciosa) |
| `CHANGELOG.md` | **+1 bloco** [1.10.0] | Convenção |

**Total efetivo:** 2 novos + 9 edições de 1-3 linhas (incluindo CHANGELOG). Sem nova pasta. Sem novo workflow. Sem nova skill.

### Mecanismo de method-audit autônomo (princípio 11)

A cada `/checkpoint`, o orquestrador (PMO) avalia se observou nas últimas N rodadas:

- Citação de fonte externa sem validity-check (sintoma da skill atualizada `anti-hallucination`).
- Correções repetidas do dono sobre o mesmo padrão (sintoma de skill ausente/fraca).
- Despriorização de regra de negócio sem entender semântica.
- Violação da régua §0 (artefato novo onde edição cirúrgica bastaria).
- Loop/retrabalho que indica passo anterior raso.

Se observou: emite **0-3 method-audit notes** em `history.md ## Aprendizado` no formato:
```
- [<ISO>] Method-audit: <gap observado>
  Causa-raiz no framework: <skill/regra ausente ou fraca>
  Proposta de melhoria (lean): <artefato a editar ≥ criar>
```

**Firewall** preservado (ADR-007): notas são inertes; só viram comportamento via ADR aprovada e mergeada. Anti-fabricação: nota errada não propaga.

Critério de promoção (release checklist em `guia/GIT-VERSIONAMENTO.md`):
- Padrão recorrente (≥3 ocorrências) → propor ADR (já existia em ADR-007).
- **Adição v1.10.0**: gap isolado (1×) pode promover SE for high-signal (afeta integridade em ambiente regulado/alto-risco ou viola invariante de método).

### Algoritmo do reforço sênior (companion `metodo-senior.md`)

Detalhado no companion. Em uma linha: 8 passos — mapear fontes / verificar VIGÊNCIA / complementações / reconciliar cross-domain / pertinência método↔objetivo / backlog de elicitação / classificar / pass adversarial.

## Consequências

### Positivas

1. **Default operacional do framework sobe para sênior** quando há fonte canônica citada — sem inflação no caminho rápido.
2. **Auto-observação estrutural** — framework para de regredir à média entre sessões.
3. **Domain-agnóstico** — vale em dev/BI/BPM/regulado/qualquer caso (atende explícitamente a instrução do dono).
4. **Régua §0 mantida** — 2 novos + 9 edições (cresceu de 4 para 9 pela incorporação adversarial; ainda dentro do princípio); sem nova skill, workflow ou template.
5. **Validity-check integrado ao SSoT** (`anti-hallucination`) — não vira regra órfã.

### Negativas

1. **Companion adiciona 1 arquivo no diretório do discovery** — manutenção marginal. Mitigado por ADR-003: companion é o padrão estabelecido.
2. **Mecanismo de method-audit depende de disciplina do orquestrador** — se PMO esquecer, notes não vêm. Mitigação: checklist explícito no `/checkpoint` (passo obrigatório).
3. **Output-format e high-stakes-gate ficam para próxima v** — auto-load de high-stakes-gate e seção "antecipações" no template padrão são follow-ups conhecidos.

### Riscos

1. **Companion ignorado**: agente pode pular o reforço sênior. Mitigação: filtro de entrada explícito ("há fonte canônica/normativa citada") + lembrete no SKILL.md base.
2. **Method-audit vira ruído**: 0-3 por sessão é o limite. Padrão recorrente vira ADR; isolado de baixo signal é descartado pelo gate humano.
3. **Validity-check externa pode exigir web research**: explorer é repo-only; gap conhecido (item J de `[[framework-gaps-from-aivi-case-2026-05-27]]`). Tratado em follow-up; nesta v, validity-check é princípio + delegação manual ao WebSearch quando necessário.

## Implementação (ponteiro após aceito)

- **Branch:** `feat/v1.10.0-senior-discovery-method-auto-improvement`
- **Data:** 2026-05-28
- **Grep:** `git log --all --grep "v1.10.0" --grep "ADR-009"`
- **Hash de commit:** opcional como complemento; nunca único.
- **Validação:** qa-critic adversarial em rounds até LIMPO + reaplicação do método em próximo case real (AIVI fechamento ou outro domínio) verificando se as ~10 correções do dono caem para ≤3.

## Pendências e follow-ups

- ~~**High-stakes-gate auto-load** por gatilhos contextuais — próximo ciclo.~~ **ABSORVIDO PELO ADR-010 (v1.11.0):** carga é declarada pelo discovery do projeto (modo Transcribe se briefing inequívoco/ubíquo; modo Interview caso contrário). Sem listas hardcoded de gatilhos — framework agnóstico estrito.
- **Template `docs/specs/_template/requirements.md` para caminho universal+sênior** — o template `_template-research/research-brief.md` cobre cascata+sênior (§7+§8); o universal+sênior (discovery universal com fonte canônica citada) usa `requirements.md` que ainda não tem seções equivalentes. Decisão consciente de adiar: cobertura cascata+sênior basta para o caso AIVI atual; estender o `requirements.md` quando surgir caso real universal+sênior. Levantado por qa-critic round 3 ADV-R2.
- **Antecipações no template padrão de `output-format`** — propagar do companion para o output base. Próximo ciclo.
- **External research handle no discovery pesquisa-cascata** — explorer EXTERNAL via WebSearch/WebFetch; gap conhecido (item J).
- **Detector de drift hook deployado-vs-versionado** (framework-boot.ps1 órfão) — gap de infra, item I.
- **AIVI fechamento** (validar a esteira completa): implementar REQ-001..007 + qa-critic + run + CA-1..6. Fora deste repo.

## Referências

- Memórias-fonte: `[[senior-discovery-method]]` (substância), `[[framework-self-improvement]]` (auto-observação), `[[framework-gaps-from-aivi-case-2026-05-27]]` (audit trail).
- Case real: `github.com/fabriciopsouza/LIMITES-BATENTES-RECALC` branch `claude/discovery-aivi-metodo-2026-05-27` (commits `74bd613`, `039fd6d`).
- ADRs irmãos: ADR-003 (progressive disclosure), ADR-007 (régua §0 + ex-G9/ex-G11).
- `_shared/anti-hallucination` · `_shared/metacognition-core` · `_shared/output-format`.
- Workflows tocados: [`checkpoint.md`](../../.agent/workflows/checkpoint.md).
