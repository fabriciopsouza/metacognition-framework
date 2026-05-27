# ADR 007 — Régua §0 (GANHO LÍQUIDO) + Discovery em cascata (G1) + extensões de aprendizado e WIP

- **Status:** Aceito (2026-05-27 — mantenedor autorizou trabalho noturno autônomo; qa-critic adversarial 3 rounds: round 1 APROVADO_COM_RESSALVAS (2M+3B+3A), round 2 APROVADO_COM_RESSALVAS (1 cosmética), round 3 APROVADO LIMPO)
- **Data:** 2026-05-27 · **Decisores:** Fabricio (mantenedor) + Claude (papel `architect`)
- **Substitui:** nenhum · **Substituído por:** nenhum
- **Relaciona-se a:** ADR-002 (discovery v1.6.0), ADR-003 (progressive disclosure), ADR-004 (auto-boot), ADR-005 (modos), ADR-006 (auto-boot global)
- **Fonte:** `docs/_intake/2026-05-27-plano-otimizacao-framework.md` (briefing colado pelo mantenedor)

## Contexto

O mantenedor colou em 2026-05-27 um briefing único de otimização do framework (intake salvo em `docs/_intake/`). Diagnóstico-chave: o repo já resolveu 8 problemas estruturais (SSoT, context engineering, isolamento de subagente, roteamento por confiança, spec atômica, high-stakes-gate, observability, progressive disclosure) e o framework está em risco de **inflamento por adição pura**. O intake propõe uma régua de subtração-primeiro e identifica **1 gap real** (G1 — descoberta em cascata antes da spec) + 2 necessidades atendíveis por **extensão** (não por subsistema novo): aprendizado de fracassos (ex-G9) e WIP/nada-esquecido (ex-G11). Tudo o mais é adiado até dado de uso real justificar.

Pedido textual do mantenedor: *"SEMPRE buscando melhorar, otimizar, tornar mais eficiente no máximo autosuficiente com segurança, mas profundo, evolutivo, sênior, profissional, assertivo, etc"*. O ADR-007 é a aplicação inicial da régua §0 ao próprio framework.

Validação anti-snapshot (re-auditoria do repo vivo em 2026-05-27, pós-merge da v1.8.0):
- §3 "Já resolvido" do intake → CONFIRMADO no repo vivo.
- §3 "G1 ausente" → CONFIRMADO (não há companion `pesquisa-cascata.md` em `.agent/skills/discovery/` nem template `_template-research/`).
- §3 "Extensões via checkpoint/history" → INFERIDO viável (workflows e history existem).

## Decisão (1 frase ativa)

Adicionar a **régua §0 GANHO LÍQUIDO** como princípio 10 do `AGENT-FRAMEWORK.md` §6 (1 linha), criar o **companion `pesquisa-cascata.md`** do discovery (sub-modo G1 sob demanda) + template `_template-research/`, e **estender** `/checkpoint` + `history.md` + checklist de release para aprendizado de fracassos (ex-G9) e WIP/nada-esquecido (ex-G11) — sem criar workflows, pastas ou templates adicionais.

## Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Escopo enxuto v1.9.0: régua §0 + G1 + ex-G9/ex-G11 por extensão (escolhida)** | Aplica a própria régua: 1 companion + 1 template + 1 ADR + edições cirúrgicas. Resolve o único gap real + 2 necessidades. Sem custo fixo novo no caminho rápido. | 4 mudanças paralelas no mesmo PR (companion, template, AGENT-FRAMEWORK, checkpoint+history). Mitigado por serialização interna (uma seção por commit). |
| 2 | Escopo amplo: também implementar G2 (multi-spec + worktree) ou G3 (gate analyze) | Resolve mais necessidades de uma vez. | Inflar PR sem dado real de uso. Contraria régua §0 (adição sem critério (a)(b)(c)). Próprio intake §3 adia tudo isso. |
| 3 | Só régua §0 (sem G1 nem extensões) | PR mínimo (1 linha em 1 arquivo). | G1 é o único gap real identificado — não tratá-lo agora deixa a lacuna mais óbvia em aberto. |
| 4 | Régua §0 + G1, sem extensões ex-G9/ex-G11 | Menos arquivos tocados. | Perde a chance de fechar 2 necessidades reais por **extensão** (1-3 linhas cada). Custo de adicionar agora é mínimo. |
| 5 | Subsistema novo para aprendizado (workflow `retro.md` + pasta `lessons/`) | Aprendizado fica em arquivos próprios, fácil de auditar. | Falha a régua §0: cria estrutura ad-hoc duplicada de `history.md`+`checkpoint`+ADR. Próprio intake §1.4 rejeita. |
| 6 | Não fazer (status quo) | Zero esforço. | G1 segue ausente; aprendizado e WIP seguem informais. Intake §7 explicitamente pede ação. |

## Justificativa

A escolha pela **Alternativa 1** segue 3 princípios:

- **A régua se valida no próprio ADR.** Mudança líquida: companion + template + extensões somam ~150 linhas, todas justificadas por critério (c) (destravam capacidade não existente) ou (a) (fundem em artefato existente em vez de criar paralelo). Adição pura: zero.
- **G1 é o único gap real** (intake §3 confirmado pelo repo). Tratar agora é mais barato do que voltar depois.
- **Extensões por refactor cirúrgico** (1-3 linhas em arquivos existentes) custam menos do que workflow/pasta nova e mantêm `_shared/` como SSoT.

A escolha pelo escopo **excluir G2-G10 e R2-R5** segue o intake §3: adiar até necessidade comprovada + eval pago (que ainda não foram pagos).

A escolha pela numeração **ADR-007** (intake propunha "ADR-005"): conflita com ADR-005 já mergeado ("Modos de execução"). Próximo número livre = 007 (ADR-006 = auto-boot global, mergeado em main como PR #8). Audit trail no §"Histórico desta revisão" do ADR-006 documenta a sequência.

### Decisões internas do architect

1. **Régua §0 entra como princípio 10** do §6 (após "Override do usuário vence o roteamento automático"). 1 linha; referencia este ADR.
2. **WIP-limit não vira princípio §6** — vira sub-regra na seção do `start-session` (escopo: modo squad). Pela régua §0: princípio é mais caro que sub-regra; aplicar onde dói. **Diverge do intake §4** (que propunha "no §6 junto da régua") — override consciente do architect aplicando a própria régua §0 ao escopo: WIP-limit só vale em modo squad, princípio §6 vale para tudo; sub-regra é mais barata e cirúrgica. Override registrado aqui para audit trail (qa-critic round 1, ressalva C2).
3. **Discovery bumpa 1.6.0 → 1.7.0** (companion novo sob demanda = feature MINOR).
4. **Sistema bumpa 1.8.0 → 1.9.0** (feature nova compatível).
5. **Companion `pesquisa-cascata.md`** segue o padrão do ADR-003 (carregado sob demanda; não infla a SKILL.md). Inclui **STORM nomeado + 1 passo de pergunta adversarial obrigatório** (R3 do intake, dobrado em 2 linhas).
6. **`history.md` ganha 2 seções**: `## Em aberto` (WIP) e `## Aprendizado` (fracassos). Single-writer = orquestrador (PMO), append-only.
7. **Entregáveis do intake omitidos** (qa-critic round 1, ressalva sobre fidelidade):
   - "+subseção curta no AGENT-FRAMEWORK.md §2.B" → **omitido**: §2.B já tem a subseção "Gatilho do discovery" (linhas 90-99) que descreve a fronteira PMO→discovery→architect. Adicionar nova subseção seria duplicação. Por critério (a) da régua §0.
   - "+item no README.md" → **omitido**: adição pura sem critério (a)(b)(c). README é entry-point humano; sub-modo novo no discovery não exige menção lá (a tabela do discovery/SKILL.md basta).

## Implementação

### Arquivos criados/alterados na v1.9.0

Escopo: **5 arquivos** (1 novo companion + 1 novo template + 4 edições cirúrgicas):

| Arquivo | Mudança |
|---|---|
| `AGENT-FRAMEWORK.md` | **+1 linha no §6**: princípio 10 "Otimização líquida — adição só passa se (a) funde/remove ≥ adiciona, (b) reduz tokens/latência, ou (c) destrava eval. Adição pura é rejeitada por padrão. Detalhe: ADR-007." |
| `.agent/skills/discovery/pesquisa-cascata.md` | **NOVO companion** (sob demanda; ~80 linhas). Filtro de entrada: trabalho exige pesquisa antes da spec (não há trilha pronta). Método: decompor pergunta → buscar via `explorer` → refletir → ramificar → sintetizar `research-brief.md` (single-thread, monólito). **R3 do intake (anti-raso):** após sintetizar, ATAQUE adversarial obrigatório: persona read-only ataca os achados (lacunas, viés de confirmação, fontes fracas) antes de fechar. Output: `research-brief.md` com achados classificados (`CONFIRMADO|INFERIDO|DESCONHECIDO`). |
| `.agent/skills/discovery/SKILL.md` | **+1 linha** na tabela de sub-modos (apontando para o companion novo) + **bump de versão** 1.6.0 → 1.7.0. |
| `docs/specs/_template-research/research-brief.md` | **NOVO template** do artefato de saída (~40 linhas; cabeçalho YAML + seções: questão decomposta, fontes consultadas, achados classificados, gaps, sugestão ao orquestrador). |
| `.agent/workflows/checkpoint.md` | **+2 linhas** (ex-G9 + firewall): linha 1 — "Se gatilho de fracasso disparou (anti-loop, qa-critic reprovou ≥2×, file-first violado, estouro de token, [CONFIRMADO] que se revelou falso), anotar em `history.md` sob `## Aprendizado`. Single-writer (orquestrador), append-only." Linha 2 (qa-critic round 1, ressalva firewall C7) — "Notas de aprendizado são **inertes**: só viram comportamento via skill/regra destilada, aprovada via ADR e mergeada. Nota errada não propaga." |
| `.agent/workflows/start-session.md` | **+1 linha** (ex-G11): "STATUS reconcilia `## Em aberto` do `history.md` + branches do git + ADRs `Proposto` (modo squad apenas)." |
| `guia/GIT-VERSIONAMENTO.md` | **+1 linha** (ex-G9): "Antes do release, revisar `## Aprendizado` do `history.md`; padrão recorrente (≥3) → propor ADR." |
| `history.md` (raiz) | **NOVO** (arquivo). 2 seções vazias: `## Em aberto` e `## Aprendizado`. Single-writer = orquestrador. |
| `CHANGELOG.md` | Bloco `[1.9.0]` (MINOR). |
| `CLAUDE.md` + `AGENTS.md` | Atualizar para v1.9.0 + nota da régua §0. |

**Total efetivo:** 1 novo companion + 1 novo template + 1 novo `history.md` + 4 edições de 1 linha + bump versões + doc. 

### Régua de carregamento do companion (progressive disclosure ADR-003)

Discovery carrega `pesquisa-cascata.md` **apenas** quando a natureza do trabalho exige pesquisa antes da spec (ex.: "Como o GAMP 5 trata ferramenta com componente generativo?" — sem fonte canônica no contexto). Default: não carrega; SKILL.md cobre os outros sub-modos.

### Algoritmo do sub-modo pesquisa-cascata (resumo no companion)

```
1. Filtro de entrada: confirma que e pesquisa antes da spec
2. Decompor: pergunta principal → 3-5 sub-perguntas multi-hop
3. Buscar: delegar a explorer (read-only, contexto isolado por sub-pergunta)
4. Refletir: sintetizar achados; classificar (CONFIRMADO|INFERIDO|DESCONHECIDO)
5. Ramificar: lacunas viraram novas sub-perguntas → volta ao passo 3 (limite N=2 rodadas)
6. Sintetizar: monólito single-thread em research-brief.md
7. ATAQUE ANTI-RASO (R3 obrigatorio): persona read-only ataca achados
8. Refinar: incorporar achados do ataque; fechar QUANDO (criterio binario,
   qa-critic round 1 C4): lacunas que BLOQUEAM decisao de spec ou que, se
   erradas, invalidam a hipotese principal, estiverem todas marcadas como
   DESCONHECIDO com sugestao de validacao. Lacunas perifericas nao bloqueiam.
9. Handoff: research-brief.md → discovery (continua spec) ou architect
```

### Eval seção I (intake §4 — rodar antes de pronto)

Test plan binário (8 casos):
1. Trabalho exige pesquisa, contexto sem fonte → companion carrega.
2. Trabalho exige pesquisa, contexto tem fonte canônica → companion NÃO carrega (cai no método universal).
3. Decomposição produz 3-5 sub-perguntas (não 1 nem 20).
4. Cada busca delegada ao explorer em contexto isolado.
5. Classificação aplicada em cada achado.
6. Ataque anti-raso registrado (não opcional).
7. `research-brief.md` segue template (cabeçalho YAML correto).
8. Lacunas críticas viraram `[DESCONHECIDO]` com sugestão de validação.
9. **Falha do explorer** (qa-critic round 1, ressalva eval C10): se explorer retornar vazio/falhar em todas as sub-perguntas de uma rodada, registrar a sub-pergunta como `[DESCONHECIDO]` com sugestão de fonte alternativa; NÃO repetir a mesma sub-pergunta na rodada N+1. Evita loop quando a fonte simplesmente não existe.

## Consequências

### Positivas

1. **Gap real fechado.** G1 (descoberta em cascata) deixa de ser ausência.
2. **Régua §0 explícita.** Princípio 10 do §6 vira ponto de apoio para rejeitar inflamento futuro.
3. **Aprendizado de fracassos formalizado** sem subsistema novo. `history.md` + `/checkpoint` + release checklist cobrem.
4. **WIP visível** no STATUS de toda sessão squad. Nada planejado/pausado/em-revisão fica órfão.
5. **Discovery mais robusto** sem inflar SKILL.md (companion sob demanda — ADR-003).
6. **Aplica a régua a si mesmo.** O próprio ADR é otimização líquida.

### Negativas

1. **5 arquivos editados + 3 novos.** Manutenção aceitável: 1-3 linhas cada nos editados; companion + template + history são auto-contidos.
2. **`history.md` precisa de hábito.** Single-writer (orquestrador) exige disciplina; nota errada pode propagar se o firewall não for respeitado.
3. **Eval seção I é design-time inicialmente.** Cumprir antes de declarar bloco "pronto" (instrução do intake §5.2).

### Riscos

1. **Companion `pesquisa-cascata.md` virar onda nova de cargo culting.** Mitigação: filtro de entrada explícito (passo 1 do algoritmo) rejeita casos que não exigem pesquisa.
2. **`history.md` `## Aprendizado` virar inflamento.** Mitigação: append-only single-writer; firewall (notas inertes — só viram comportamento via skill/regra aprovada).
3. **Régua §0 vira fardo retórico.** Mitigação: princípio 10 referencia este ADR; qualquer reprovação cita critério (a)/(b)/(c).
4. **Acoplamento ao start-session** (qa-critic round 1, adversarial; round 2 baixa cosmética: ver decisão interna 2 para o raciocínio de escopo). Reconciliação de 3 fontes só em **modo squad**; vigiar STATUS > 4 linhas → refatorar.
5. **Race condition humano vs orquestrador** (qa-critic round 1, adversarial). Se o mantenedor editar `history.md` manualmente fora de sessão (ex.: adicionar item em `## Em aberto` por outro PC) e o orquestrador fizer append simultâneo, há merge conflict não gerenciado. Mitigação: convenção append-only com timestamp por entrada (`## Em aberto / [2026-05-27 - ...]`); resolução via git merge padrão.
6. **SKILL.md desatualizada como gate do eval** (qa-critic round 1, adversarial). O eval seção I caso 1 requer que o companion carregue — só executável após o developer implementar a edição na tabela de sub-modos do `discovery/SKILL.md`. Gate explícito documentado no campo "Validação" (próximo): eval só roda após PR mergeado, não em design-time.

## Implementação (ponteiro após aceito)

- **Ponteiro:**
  - Branch: `feat/discovery-cascata-v190`
  - Data: 2026-05-27
  - Grep: `git log --all --grep "v1.9.0" --grep "ADR-007"`
- **Hash de commit:** opcional como complemento; nunca único (lição ADR-001/003).
- **Validação:** eval seção I (8 casos binários acima) + qa-critic adversarial em rounds até LIMPO + validação manual em campo (ao menos 1 pesquisa-cascata real disparada via discovery).

## Pendências e follow-ups

- **ADR cross-platform** (porte `.sh` da cadeia de hooks): continua candidato (ADR-006 §Pendências).
- **G2 (multi-spec + worktree)**, **G3 (gate analyze)**, **G4 (EARS obrigatório)**, **G5/G7 (regulado: Golden Datasets/OOS)**, **G6 (`--quick`)**, **G10 (Harness Fit)**, **R2/R4/R5**: adiados até dado de uso real + eval pago (intake §3). Backlog formal em `docs/_backlog/gaps-otimizacao.md` (FASE C desta sessão).
- **Eval G/H/I em design-time:** dívida do framework (intake §1.3). Próximo ciclo pago.

## Referências

- Intake: [`docs/_intake/2026-05-27-plano-otimizacao-framework.md`](../_intake/2026-05-27-plano-otimizacao-framework.md)
- ADRs irmãos: ADR-002 (discovery v1.6.0) · ADR-003 (progressive disclosure) · ADR-006 (auto-boot global)
- `_shared/anti-hallucination` · `_shared/confidence-classification` · `_shared/metacognition-core`
- Workflows tocados: [`checkpoint.md`](../../.agent/workflows/checkpoint.md) · [`start-session.md`](../../.agent/workflows/start-session.md)
