# ADR 010 — Framework agnóstico de domínio: discovery declara o escopo

- **Status:** Proposto (2026-05-28) — aguarda qa-critic rounds + aceite
- **Data:** 2026-05-28 · **Decisores:** Fabricio (mantenedor) + Claude (papel `architect`)
- **Substitui:** nenhum · **Substituído por:** nenhum
- **Relaciona-se a:** ADR-007 (régua §0), ADR-009 (método sênior + auto-observação), ADR-005 (modos de execução / HITL via execution-modes)
- **Fonte:** auto-observação 2026-05-28 — purgar âncoras hardcoded de domínio detectadas no próprio framework durante a tentativa de absorção do método sênior; memória `[[senior-discovery-method]]` carregava ALCOA+/ANP/FDA/BACEN como gatilhos (vazamento cross-projeto materializado).

## Contexto

A v1.10.0 (ADR-009) declarou o método sênior **"domain-agnóstico"**, mas o próprio texto do reforço (`.agent/skills/discovery/metodo-senior.md`) e da memória correspondente carregavam listas hardcoded de normas (ANP, ANVISA, FDA, BACEN, ABNT, ISO, GAMP, etc.) e ALCOA+ como exemplo recorrente de "regra de negócio com peso semântico". O mesmo padrão aparece em outros arquivos do núcleo:

- `.agent/rules/04-confidence-routing.md` acopla ALCOA+ ao roteamento por confiança (regulado → "reflexivo + ALCOA+/audit trail").
- `.agent/skills/discovery/SKILL.md` (banco de partida) e `mapeamento-de-processo.md` (fora-de-escopo) citam ALCOA+ como referência canônica.
- `AGENT-FRAMEWORK.md` §1 lista "ambiente regulado" como sinal automático de ativação do squad.
- `PROMPT-CHAT-WEB-v4.2.md` (raiz, parte do distribuído) trazia identidade hardcoded ("Tableau · distribuição de combustíveis · farmacêutico ANVISA/GAMP/COBIT") em §1 e §5.

**Diagnóstico operacional (2026-05-28):** as falhas observadas no case AIVI (citar ANP 884 = varejo como se regulasse distribuição; tratar ALCOA+ = pharma/GxP como âncora de combustível) **não foram falhas do "método cross-domain reconciliation"**. Foram sintomas de **vazamento cross-projeto** — o agente carregava nas próprias regras do framework convenções de outros projetos do mesmo dono (Vibra/distribuição + Natulab/farmácia), e ativava-as por similaridade semântica em qualquer projeto. O framework declarava-se agnóstico, mas operava com viés.

Diretriz do dono (2026-05-28): *"se há menção direta hardcoded nos prompts, não deveria ser removida, pois queremos um framework agnóstico de domínio?"* + *"ambiente regulado deve ser abordado se fizer parte do projeto, e confirmado pelo discovery"*.

## Decisão (1 frase ativa)

Adotar **agnosticismo estrito do núcleo** + **declaração de escopo via discovery por projeto**: nenhum arquivo do framework (skills, regras, ADRs vivos, prompt web, memórias-fonte) carrega listas ou exemplos hardcoded de normas/convenções/domínios; quando relevante, o discovery do projeto declara explicitamente (a) se é regulado/high-stakes, (b) quais normas/convenções aplicam, (c) quais gaps não-bloqueantes existem; os gates downstream (`high-stakes-gate`, reforço sênior, `04-confidence-routing`) carregam SOB DECLARAÇÃO, não por detecção semântica.

## Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Purga estrita + discovery-declara-escopo (escolhida)** | Resolve vazamento cross-projeto na raiz. Framework genuinamente agnóstico. HITL fica no eixo execution-modes (já existe via ADR-005 — sem duplicação). Régua §0: maioria dos edits é subtração; ADR registra decisão; net-negativo de superfície. | Discovery precisa perguntar explicitamente "regulado? quais normas?" como passo obrigatório quando há sinal — adiciona 1 lote temático ao discovery default. |
| 2 | Manter exemplos hardcoded como "pedagógicos" rotulados como `ex.:` | Mínimo esforço; exemplos ajudam quem nunca viu. | Não resolve o problema real — exemplos viram âncoras cognitivas (memória do agente os promove a regra). O case AIVI demonstrou isto: ALCOA+ entrou como âncora apesar de rotulado como exemplo. |
| 3 | Acoplar regulado→HITL na mesma decisão | "Tudo em um lugar". | Confunde 2 eixos independentes (domain × risk control). Casos comuns onde só um aplica (research read-only em projeto regulado; migração crítica em comercial) ficam mal-servidos. ADR-005 já cobre HITL via execution-modes — duplicaria. |
| 4 | Criar nova skill `domain-declarator` | Skill dedicada, fácil de auditar. | Régua §0: skill nova onde edição cirúrgica em discovery resolve. Adiciona superfície sem ganho líquido. |
| 5 | Não fazer (status quo) | Zero esforço. | Vazamento permanece; o próprio ADR-009 entra em contradição. Próximo case real reproduz o erro. |
| 6 | Purga + remoção do `_template-process/gap-analysis.md` exemplo ALCOA+ + saneamento de exemplos `H1-farma-*` | Cobre toda menção a domínios. | Exemplos rotulados em `docs/specs/exemplos/H1-farma-*` são DIDÁTICOS — labeled directory, intenção explícita. Mexer descaracteriza o catálogo de exemplos. Fora de escopo. Apenas `gap-analysis.md` (sumário executivo) ganha placeholder agnóstico. |

## Justificativa

Escolha pela **Alternativa 1** por 4 razões alinhadas com princípios já registrados:

- **Régua §0 (ADR-007):** o trabalho é majoritariamente **subtrativo** (remoção de listas hardcoded + reframing). Adição: ADR-010 + 1 princípio em §6 do AGENT-FRAMEWORK + bloco CHANGELOG + seção em CLAUDE/AGENTS + ~5 linhas em discovery `SKILL.md` para tornar a pergunta "regulado? quais normas?" parte do método. Net: superfície semântica hardcoded REMOVIDA é maior que adicionada.
- **ADR-005 reaproveitado:** HITL já está no eixo execution-modes (default prompts, avançado bloqueia em push/merge/PR, autosuficiente bypassa). Não duplicar como "gate de regulado". Regulado é DOMÍNIO; HITL é CONTROLE DE RISCO. Decouplagem natural.
- **ADR-009 coerência interna:** o ADR-009 declarava o método "domain-agnóstico" mas operacionalizava com listas. v1.11.0 fecha o gap de coerência.
- **Princípio 11 (auto-observação) ativado:** este ADR é exemplo da auto-observação funcionando — o framework detectou seu próprio vazamento via method-audit. ADR-010 valida o princípio 11.

## Princípios novos introduzidos

### Princípio 12 (`AGENT-FRAMEWORK.md` §6) — Framework agnóstico de domínio

> **Domínio é declarado pelo projeto via discovery, não inferido por sinais semânticos no framework.** O núcleo (`_shared/`, `.agent/skills/`, `.agent/rules/`, ADRs ativos, prompt web distribuído) NÃO carrega listas hardcoded de normas, convenções ou regras de domínio. Quando há sinal de contexto especializado (regulado, alto-risco, regra de negócio com peso semântico), o **discovery** pergunta explicitamente ao dono: *(a) este projeto opera sob alguma norma/convenção externa? (b) há regra de negócio com semântica específica declarada? (c) há decisão downstream de alto impacto?*. As respostas vão para o `requirements.md`/`research-brief.md` do projeto e disparam os gates downstream (`high-stakes-gate`, reforço sênior, roteamento reflexivo). **Sem declaração explícita do projeto, os gates ficam em default agnóstico.** Anti-vazamento: o agente NÃO importa convenção/norma de outro projeto (mesmo do mesmo dono) sem confirmação. Detalhe: **ADR-010**.

### Sub-princípio anexo (i) — Gaps não-bloqueantes são flagados, não silenciados

> Abordagem sênior de discovery: gaps detectados que NÃO bloqueiam entrega (ex.: cobertura parcial de fonte, dimensão sem dados mas dispensável) **ainda são apresentados explicitamente** no output (seção `## Gaps não-bloqueantes`) com (i) descrição, (ii) impacto se não tratado, (iii) decisão registrada do dono ("manter gap" / "tratar follow-up"). Silenciar gap não-bloqueante = perda de assertividade. Aplicação: `metodo-senior.md` (output esperado) + `_template-research/research-brief.md` (§7 Antecipações ganha sub-seção).

### Sub-princípio anexo (ii-a) — Briefing inequívoco e ubíquo dispensa interview-mode

> **Determinístico quando o input já é completo:** o passo 6 do discovery (lote temático "Escopo declarado") tem DOIS modos:
>
> 1. **Interview-mode (default):** 4 perguntas explícitas ao dono — quando briefing é silente, ambíguo ou parcial.
> 2. **Transcribe-mode (determinístico):** quando briefing (`docs/briefing.md` ou doc fornecida) contém declaração nominal explícita, **sustentada em ≥2 lugares**, com **fonte/dono nomeado** ("declarado por <stakeholder> em <doc>") → discovery TRANSCREVE para `## Escopo declarado pelo discovery` marcando origem ("via briefing — citar trechos") **sem re-asking**.
>
> **Critério binário do transcribe-mode** (todos obrigatórios; falha em qualquer um → cair em interview-mode):
> - (i) **Declaração nominal:** "este projeto opera sob norma X" / "alto-risco confirmado em Y" — não inferência por keyword.
> - (ii) **Ubiquidade:** mencionado em ≥2 seções/documentos independentes (não 1 menção tangencial).
> - (iii) **Autoria:** stakeholder/dono nomeado como fonte da declaração (não declaração anônima).
> - (iv) **Sem contradição:** outras seções do briefing não negam ou enfraquecem a declaração.
>
> **Anti-vazamento mantido:** transcribe-mode lê só o briefing DESTE projeto. Não importa declaração de outro projeto/sessão. Sem essa válvula, framework vira teatro burocrático em projetos com briefing maduro; com ela, briefing inequívoco é honrado e dono não precisa re-declarar o que já declarou.

### Sub-princípio anexo (ii-b) — Novas skills só via discovery + gate humano régua §0

> **Flexibilidade SEM porta aberta:** discovery PODE surfacear "candidate-skill" como antecipação no `research-brief.md`/`requirements.md` quando o método sênior identificar gap recorrente que não cabe em edição cirúrgica. **O dono aplica gate binário régua §0 (ADR-007) sobre a proposta:** (a) funde/remove ≥ adiciona? (b) reduz tokens/latência? (c) destrava eval inalcançável editando existente? Falha em todas as 3 → vira `method-audit-note` (firewall ADR-007: inerte). Passa em ao menos uma → vira ADR proposta com qa-critic adversarial. **Não é autorização para agente criar skill** — é canal estruturado para PROPOR, com gate humano + ADR + qa-critic obrigatórios.

### Sub-princípio anexo (ii) — Read-and-Review-for-Coherence (RRC) obrigatório

> **Comportamento sênior absorvido:** antes de declarar "pronto" qualquer mudança substantiva (release, bloco aprovado, ADR aceito, merge para main), o agente DEVE executar um pass **RRC** auditável:
>
> 1. **LER todos os artefatos potencialmente afetados** — não só os que ele próprio editou. Inclui: ADRs vinculadas, skills relacionadas (via `referencias` cruzadas), `CLAUDE.md`/`AGENTS.md`/`README.md` (entry points), `CHANGELOG.md`, `history.md ## Em aberto`, `_shared/` dependências, prompt distribuído (`PROMPT-CHAT-WEB`), `web/index.html`.
> 2. **VERIFICAR coerência** — versões em sync (versão no README × versão na tag × versão no web/index × CHANGELOG); referências cruzadas válidas (ADR-N citado existe; arquivo citado existe; linha citada existe); nomenclatura consistente (nome aprovado em todos os arquivos); contradições semânticas (ex.: ADR-X declara "agnóstico" mas exemplo Y carrega norma específica).
> 3. **REPORTAR** ao dono em formato auditável binário (passa/não-passa por critério). Inconsistência detectada = corrigir ANTES da declaração de "pronto", não depois.
>
> **Atalhar este passo = comportamento não-sênior**. O case AIVI demonstrou: 4 rounds de qa-critic na v1.10.0 absorção surgiram porque a coerência cross-documentos não foi verificada antes do round 1 — múltiplos lugares precisavam ser ajustados (research-brief template, CLAUDE.md, AGENTS.md, pesquisa-cascata) e foram descobertos pelo crítico, não pelo autor. v1.11.0 absorve o protocolo para o autor (agente) executar antes do crítico.
>
> **Aplicação:** método sênior ganha **passo 9 (Coherence Pass)** em `.agent/skills/discovery/metodo-senior.md`; `/checkpoint` workflow ganha **gate de saída RRC** (não fecha checkpoint sem RRC executado); `qa-critic` continua como crítico adversarial — mas RRC pré-qa deve reduzir achados de coerência a zero (qa-critic foca em substância, não em sync básico).

## Implementação

### Arquivos editados na v1.11.0

Escopo: **1 novo + 11 edições cirúrgicas (mais purga em 1 prompt distribuído)** — majoritariamente subtração:

| Arquivo | Mudança | Tipo |
|---|---|---|
| `docs/adr/010-framework-agnostico-discovery-declara-escopo.md` | **NOVO** (este arquivo) | Adição — critério (c) régua §0 |
| `.agent/skills/discovery/metodo-senior.md` | Linha 13: remover lista (ANP/ANVISA/FDA/BACEN/...) → "norma regulatória/padrão técnico externo declarado pelo discovery". Linha 15: remover ALCOA+. Linha 56: remover ALCOA+. **+1 seção "Gaps não-bloqueantes"** no output esperado. | Subtração (3) + adição cirúrgica (1) |
| `.agent/skills/discovery/SKILL.md` | Linha 58: remover ALCOA+ do banco de partida regulado. Linha 116: remover ALCOA+ do compliance. **+lote temático "Escopo de domínio do projeto"** ao método universal (passo 4 ou 5). | Subtração (2) + adição cirúrgica (1) |
| `.agent/skills/discovery/mapeamento-de-processo.md` | Linha 72: remover ALCOA+ do "fora de escopo". | Subtração (1) |
| `.agent/rules/04-confidence-routing.md` | Linha 17: desacoplar HITL/regulado; HITL fica no eixo execution-modes (ADR-005); roteamento reflexivo carrega SOB DECLARAÇÃO do discovery. | Subtração + reframe |
| `_shared/high-stakes-gate/SKILL.md` | Linha 32: substituir lista (GAMP 5/ANVISA/SOX/LGPD/ITIL) por placeholder agnóstico. Linha nova após §"Quando este gate é obrigatório": "carga é DECLARADA pelo discovery do projeto, não inferida por sinais semânticos do framework." | Subtração + reframe + 1 linha |
| `AGENT-FRAMEWORK.md` §6 | **+1 linha** (princípio 12: framework agnóstico). Linha 41 da §1: "ambiente regulado" → "ambiente declarado regulado pelo discovery" (reframe). | Adição mínima + reframe |
| `PROMPT-CHAT-WEB-v4.2.md` | §1 Identidade e §5 Domínio: substituir conteúdo hardcoded (Vibra/Natulab/Tableau/ANVISA/GAMP) por **template com placeholders** instruindo o usuário a customizar. Manter estrutura. | Subtração massiva + template |
| `docs/specs/_template-process/gap-analysis.md` | Sumário executivo (linha 23): trocar exemplo ALCOA+ por exemplo agnóstico. | Subtração + reframe |
| `CHANGELOG.md` | **+1 bloco** [1.11.0]. | Convenção |
| `CLAUDE.md` + `AGENTS.md` | **+1 seção** v1.11.0 (precedente v1.9.0/v1.10.0). | Convenção |

### Memória do agente (fora do repo, mas crítica)

`~/.claude/projects/c--Users-fabriciosouza-metacognition-framework/memory/senior-discovery-method.md`:
- Linha 30: "anti-fraude, audit, ALCOA+, fairness" → "anti-fraude, audit, fairness".
- Linha 32: "ambiente regulado, decisão executiva, perda financeira real, ALCOA+, ANP, FDA, BACEN, etc." → "contexto declarado pelo discovery como regulado/decisão executiva/perda material → high-stakes-gate é default. SEM declaração, NÃO é default."

Esta memória é minha (do agente) — não está no repo, mas é a fonte de viés cross-sessão. Purgar é parte do v1.11.0 mesmo não sendo versionado.

### Mecanismo: como o discovery declara escopo

Discovery (universal ou sub-modo) adiciona **lote temático obrigatório** quando há QUALQUER sinal de contexto especializado (norma citada pelo dono, regra de negócio com peso semântico, decisão de alto impacto). Perguntas explícitas:

1. **Regulado?** Este projeto opera sob alguma norma/convenção externa? Quais? (Resposta `[CONFIRMADO]`/`[INFERIDO]`/`[DESCONHECIDO]` por norma.)
2. **Alto-risco?** Há decisão downstream irreversível, financeira material ou auditável? (Sim/Não + justificativa.)
3. **Regras com semântica?** Há regra de negócio onde o "como" importa tanto quanto o "quê" (anti-fraude, audit trail, fairness)? (Sim/Não + lista.)
4. **Gaps conhecidos?** Há dimensões/dados sabidos ausentes mas não-bloqueantes? (Lista + decisão "manter/tratar".)

Output vai para o `requirements.md`/`research-brief.md` em seção **`## Escopo declarado pelo discovery`** (4 sub-seções acima). Gates downstream carregam conforme declaração.

### Mecanismo: como os gates carregam sob declaração

- `_shared/high-stakes-gate`: carrega quando `## Escopo declarado` contém (1) ou (2) afirmativos.
- `.agent/skills/discovery/metodo-senior.md`: carrega quando (1) afirmativo com norma declarada OU (3) afirmativo.
- `.agent/rules/04-confidence-routing.md` reflexivo: carrega quando (1) OU (2) OU (3) afirmativo. HITL adicional: governado por modo de execução (ADR-005).
- Sem declaração afirmativa de qualquer dos 3 → defaults agnósticos (discovery universal + roteamento linear + sem high-stakes).

## Consequências

### Positivas

1. **Framework genuinamente agnóstico** — coerência interna com ADR-009; sem viés cross-projeto.
2. **Discovery ganha responsabilidade explícita** de declarar escopo — substantivo, auditável, registrado no output.
3. **Gates downstream confiáveis** — disparam por declaração, não por correspondência de string. Reduz falsos positivos e falsos negativos.
4. **Régua §0 honrada** — purga > adição.
5. **ADR-009 validado por uso** — princípio 11 (auto-observação) detectou o gap; ADR-010 é o output. O framework se auto-melhorou.
6. **Anti-vazamento cross-projeto** — explícito no princípio 12; default do agente passa a ser "perguntar antes de invocar contexto de outra sessão".
7. **HITL desacoplado** — execution-modes (ADR-005) continua como único eixo de HITL operacional; sem duplicação.

### Negativas

1. **Discovery default ganha lote temático "escopo de domínio"** — 4 perguntas a mais quando há sinal. Mitigado: as 4 só disparam se há sinal; em projeto puramente operacional (sem norma citada), discovery universal permanece igual.
2. **Exemplos didáticos perdidos** — `regulado:` no banco de partida (linha 58 da SKILL) vira "trilha de auditoria, validação, aprovação, rollback" sem âncora concreta. Mitigado: companion sênior (`metodo-senior.md`) ainda existe para casos confirmados; banco de partida não é exaustivo por design.
3. **PROMPT-CHAT-WEB-v4.2.md perde "identidade personalizada"** distribuída — usuário precisa customizar §1 e §5 ao plugar no Claude.ai. Mitigado: template explícito com placeholders + instrução clara de customização.

### Riscos

1. **Discovery pode esquecer de declarar escopo** — gate fica em default agnóstico quando deveria carregar high-stakes. Mitigação: lote temático no `SKILL.md` com filtro de entrada explícito ("se há QUALQUER citação de norma ou regra com semântica, este lote é obrigatório").
2. **Declaração superficial do dono** — dono responde "sim, regulado" sem citar normas → gates carregam sem detalhe operacional. Mitigação: perguntas estruturadas exigem `[CONFIRMADO]`/`[DESCONHECIDO]` por item.
3. **Memória do agente continua vazando entre sessões** — mesmo purgando `senior-discovery-method.md`, outras memórias podem trazer viés. Mitigação: princípio 12 explícito no `AGENT-FRAMEWORK.md` força o agente a perguntar antes de invocar.

### Correção honesta §C-1 — princípio 11 reescrito

Diagnóstico (case AIVI 2026-05-27): 3 violações file-first foram apontadas pelo dono, NÃO auto-observadas pelo agente. Chamar isso de "auto-observação" overstates a capability. O princípio 11 (ADR-009) foi reescrito em v1.11.0 para refletir realidade:

- **Antes (ADR-009):** "Auto-observação do framework (método sênior)".
- **Depois (v1.11.0):** "Observação meta-cognitiva (captura estruturada de feedback)" — agente registra notes proativamente quando consegue e via feedback do dono (fonte legítima). Auto-detecção é falível por design. Firewall ADR-007 mantido.

**Por que essa correção é necessária:** sem ela, o framework promete capacidade que não tem. Crítica auto-aplicada da própria sessão v1.11.0: o RRC self-applied passou pelo `README.md:4` ("ALCOA+/ANP/FDA/BACEN/GAMP" como exemplo didático) sem flagar — exatamente o tipo de viés que feedback do dono captura e o agente sozinho não. **Renomear não muda capacidade; muda a representação honesta dela.** Princípio 11 continua valioso (registra structured feedback é melhor que perder); só não promete o que não entrega.

## Implementação (ponteiro após aceito)

- **Branch:** `feat/v1.11.0-framework-agnostic`
- **Data:** 2026-05-28
- **Grep:** `git log --all --grep "v1.11.0" --grep "ADR-010"`
- **Validação:** qa-critic adversarial em rounds até LIMPO + verificar `grep -r` para `ALCOA\|ANVISA\|FDA\|BACEN\|GAMP\|ANP\b` no núcleo após purga = 0 ocorrências (excluindo CHANGELOG histórico e `docs/specs/exemplos/H1-farma-*` rotulado).

## Pendências e follow-ups (fora desta v1.11.0)

- **Templates `_template-research/research-brief.md` e `_template/requirements.md`** ganham seção `## Escopo declarado pelo discovery` no próximo ciclo (não-bloqueante: por enquanto os gates leem do output produzido por discovery).
- **Validação operacional em case real** — próximo projeto que dispare discovery declara explicitamente o escopo? Method-audit no `/checkpoint` verifica.
- **Exemplos `docs/specs/exemplos/H1-farma-*`** ficam intencionalmente intocados — diretório rotulado como exemplo didático regulado-pharma. Quem clonar entende que é exemplo, não regra do framework.

## Referências

- Memória-fonte: `[[senior-discovery-method]]` (purgada nesta v1.11.0), `[[framework-gaps-from-aivi-case-2026-05-27]]` (audit trail das 3 violações cross-projeto).
- ADRs irmãs: ADR-005 (HITL via execution-modes), ADR-007 (régua §0), ADR-009 (método sênior + auto-observação que detectou este gap).
- Workflows tocados: nenhum nesta v1.11.0 (purga é semântica, não estrutural).
