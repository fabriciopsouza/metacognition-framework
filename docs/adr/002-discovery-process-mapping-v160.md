# ADR 002 — Papel `discovery` v1.6.0: sub-modo "mapeamento de processo" + saneamentos adjacentes

- **Status:** Aceito (2026-05-25 — pelo mantenedor; pipeline avançou para developer com aprovação implícita)
- **Data:** 2026-05-25 · **Decisores:** Fabricio (mantenedor) + Claude (papel `architect`)
- **Substitui:** nenhum · **Substituído por:** nenhum
- **Complementado por:** [ADR-003](003-progressive-disclosure-companion-files.md) — aplicado após este ADR para refatorar a estrutura física da skill via progressive disclosure. **Nota histórica:** as menções deste ADR a "SKILL.md cresce de ~90 linhas para ~220-260" (Contexto e Consequência Negativa #1) refletem a projeção monolítica original; a v1.6.0 entregue tem `SKILL.md` core em ~100 linhas + 2 companion files (mapeamento-de-processo.md ~97 linhas, revisar-projeto-existente.md ~20 linhas) graças ao ADR-003. As decisões D1-D7 deste ADR permanecem válidas — apenas a forma física da skill mudou.
- **Spec de origem:** `docs/specs/discovery-process-mapping/requirements.md` (entregue pelo papel `discovery` em 2026-05-25, com revisão adversarial aplicada — 13 gaps fechados + 4 oportunidades adjacentes incorporadas)
- **Gabarito de validação:** `docs/specs/discovery-process-mapping/validation.md`

## Contexto

O papel `discovery` (introduzido em v1.5.0) elicita por **9 dimensões genéricas universais** e tem dois acelerador-padrão hoje: o método universal puro e o sub-modo "revisar projeto existente". A trilha "BA/processo" do banco de partida (`.agent/skills/discovery/SKILL.md` linhas 54-55) é apenas uma linha com 6 termos — insuficiente quando o trabalho do usuário é **processo de negócio** (fluxo cross-funcional com gatilhos, donos, RACI, regras, handoffs, exceções).

A v1.6.0 introduz capacidade BPM-sênior **sem fragmentar o framework**: nem skill nova, nem subagente novo, nem acoplamento entre skills (padrão inexistente). Em paralelo, a revisão adversarial detectou 4 oportunidades de saneamento adjacente que o mantenedor optou por endereçar no mesmo ciclo, em vez de postergar: divergência de versão no frontmatter da skill, anti-padrão no template ADR-000, assimetria ergonômica entre os dois sub-modos do discovery, e ausência de gabarito de validação.

Este ADR ratifica as **7 decisões arquiteturais** que compõem o pacote v1.6.0 e as justifica adversarialmente (≥3 alternativas por decisão, incluindo "não fazer"). A implementação física fica para `developer`, regida pelos 12 itens binários do `requirements.md` e pelo `validation.md`.

---

## Decisão (resumo executivo, 1 frase)

v1.6.0 adiciona ao `discovery` um **sub-modo nomeado "mapeamento de processo"** com filtro de entrada formal, 13 dimensões BPM organizadas em MUST/MAY/anti-raso, 3 níveis de profundidade configuráveis, output em 3 arquivos e integração com `explorer` — preservando 100% do método universal v1.5.0 e harmonizando, na mesma entrega, a ergonomia do sub-modo "revisar projeto existente", o frontmatter de versão da skill, o template ADR e o gabarito de validação.

---

## D1 — Encaixe = sub-modo do `discovery`

### Decisão
A capacidade de mapeamento de processo entra como **sub-modo nomeado interno** do papel `discovery`, ativado por filtro de entrada formal após a 1ª pergunta universal sobre natureza do trabalho.

### Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Sub-modo interno (escolhida)** | Reusa o precedente do sub-modo "revisar projeto existente" (já existe). Boundary clara (ativa só quando natureza=processo). Menor risco arquitetural — não cria padrão novo. Reversível (vira skill em v2.0 se crescer demais) | Skill `discovery/SKILL.md` cresce de ~90 linhas para ~220-260. Operador precisa entender o conceito de sub-modos |
| 2 | Dimensões sempre-on | Cobertura ampla, sem ativação explícita. Sem novo conceito (sub-modo) | Polui casos não-BPM. Discovery genérico vira mais pesado mesmo quando o trabalho não é processo |
| 3 | Skill irmã (`process-mapping/SKILL.md`) | Boundary máxima. Skill especializada com vida própria | Cria padrão de delegação inter-skills que **não existe no framework**. Custo arquitetural alto, ROI marginal. Two-skills-to-maintain |
| 4 | Template-only (sem mudar skill) | Mínimo esforço | Insuficiente: o método BPM vive na CONDUÇÃO da elicitação, não no artefato final. Trocar template não muda comportamento da skill |
| 5 | Não fazer | Zero esforço, zero risco de regressão | A trilha "BA/processo" do banco de partida continua rasa. Cenários como H1 (regulado), H2 (operacional), H3 (gerencial) ficam sem vocabulário sênior |

### Justificativa
O precedente do sub-modo "revisar projeto existente" prova que o padrão funciona em v1.5.0. Reusar é o caminho de menor risco e maior coerência arquitetural. Alternativa #3 (skill irmã) seria precedente novo no framework — alto custo de manutenção sem ganho proporcional. Alternativa #5 (não fazer) é honesta mas deixa o gap evidente.

---

## D2 — Sweep da linha "BA/processo" no banco de partida (mudança subtrativa)

### Decisão
A linha atual em `.agent/skills/discovery/SKILL.md` linhas 54-55:

```
- **BA/processo:** as-is × to-be, donos do processo, regras de negócio, exceções,
  indicadores de sucesso, mudança organizacional.
```

DEVE ser substituída por:

```
- **BA/processo:** processo de negócio/BPM → usar sub-modo "mapeamento de processo" (EARS-W1).
```

### Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Substituir por redirect (escolhida)** | Aponta o usuário direto para o sub-modo (sem dois caminhos paralelos). Linha curta no banco de partida. Sem duplicação de método | Quem referenciou a linha externa (raro mas possível) perde os 6 termos. Mudança subtrativa exige registro neste ADR |
| 2 | Manter linha atual + adicionar redirect | Não-subtrativo. Preserva backward compat puro | Cria dois caminhos para o mesmo objetivo (linha rasa + sub-modo profundo). Operador fica confuso sobre qual usar |
| 3 | Expandir a linha in-place sem sub-modo | Sem novo conceito | Expandir os 6 termos para os 13 do mapeamento explode o banco de partida (que existe para ser **ponto de partida**, não exaustivo) |
| 4 | Não tocar a linha | Zero risco de regressão | Linha rasa continua a ser usada por inércia, sub-modo novo ignorado |

### Justificativa
Manter dois caminhos paralelos (alternativa #2) gera confusão de produto. Expandir in-place (alternativa #3) viola o espírito do banco de partida ("nunca gaiola, sempre ponto de partida"). Substituir por redirect é mudança subtrativa pequena, **registrada formalmente neste ADR** conforme regra anti-rename adaptada para mudança subtrativa de texto público — coerente com o spec da regra: anti-rename existe para preservar nomes aprovados; aqui o "nome aprovado" (a linha) está sendo intencionalmente reorientada por decisão arquitetural documentada.

### Consequência subtrativa registrada
Texto removido: `as-is × to-be, donos do processo, regras de negócio, exceções, indicadores de sucesso, mudança organizacional` (6 termos sumiram da linha). Esses 6 termos passam a viver, expandidos e refinados, dentro do sub-modo "mapeamento de processo" — não há perda semântica, apenas relocação.

---

## D3 — Harmonização ergonômica do sub-modo "revisar projeto existente"

### Decisão
O sub-modo "revisar projeto existente" (já existente em v1.5.0, hoje **puramente narrativo** sem filtro de ativação formal) DEVE ganhar um cabeçalho `### Filtro de entrada` simétrico ao do novo sub-modo "mapeamento de processo", listando o que ATIVA o modo (sistema já existe; relatório do explorer; pedido de auditoria/saneamento) e o que NÃO ativa (pedido de feature nova). Comportamento downstream (3 passos: delegar ao explorer · elicitar sobre o relatório · produzir requirements.md do saneamento) **preservado intacto**.

### Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Harmonizar agora (escolhida)** | Os dois sub-modos passam a ter ergonomia idêntica. Operador (humano ou subagente) tem um único padrão de ativação a aprender. Cura assimetria que o explorer detectou na auditoria | Acresce escopo à v1.6.0 (toca um sub-modo existente além de criar o novo). Risco baixo de regressão se comportamento downstream for preservado |
| 2 | Postergar para v1.7.0 | v1.6.0 fica focada na feature nova | Assimetria persiste por mais um ciclo. Cada nova feature acumula dívida ergonômica |
| 3 | Manter assimetria permanentemente | Sem trabalho extra | Documentação fica inconsistente; subagentes automatizados (persona 4) precisam de lógica diferente para cada sub-modo |
| 4 | Não fazer | Zero risco | A assimetria foi explicitamente detectada e o usuário escolheu endereçar. Não fazer contraria a decisão do mantenedor |

### Justificativa
A v1.5.0 introduziu o sub-modo "revisar" sem filtro formal porque era o primeiro — a v1.6.0 introduz um segundo sub-modo e estabelece o **padrão ergonômico** que vale para os dois. Harmonizar agora consolida o padrão antes que apareça um terceiro sub-modo divergente. Custo: pequena edição na SKILL.md, sem mudança comportamental.

---

## D4 — Bump de versão da skill: `1.0.0` → `1.5.0` → `1.6.0`

### Decisão
O frontmatter de `.agent/skills/discovery/SKILL.md` será corrigido na sequência: `version: 1.0.0` (estado atual divergente) → `version: 1.5.0` (refletindo o estado real entregue em v1.5.0 do framework) → `version: 1.6.0` (bump da feature deste ADR). O CHANGELOG documenta a correção retroativa explicitamente.

### Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Sequência 1.0→1.5→1.6 (escolhida)** | Restaura o histórico real. Frontmatter passa a refletir o que o CHANGELOG documenta. Drift eliminado | Dois bumps "fantasma" no log de versão (1.5.0 e 1.6.0 saem juntos) |
| 2 | Bump direto 1.0.0 → 1.6.0 | Mais rápido. Um único commit de versão | Perde o registro do 1.5.0 no próprio arquivo. Histórico do componente passa a divergir do histórico do framework |
| 3 | Política nova: frontmatter ≠ versão do framework | Não precisa corrigir | Cria regra nova ad-hoc para esconder o drift. Adia decisão |
| 4 | Não corrigir | Zero esforço | O drift continua. qa-critic e auditorias futuras vão reflagar |

### Justificativa
A divergência foi detectada pelo explorer e o usuário pediu correção. A sequência 1.0→1.5→1.6 (alternativa #1) preserva a história — o componente teve mudança em v1.5.0 (entrada do papel discovery) e tem mudança em v1.6.0 (sub-modo). Dois commits de versão é um custo trivial em troca de coerência permanente.

---

## D5 — Atualização proativa do `docs/adr/000-template.md`

### Decisão
A seção "Implementação" do template ADR (atualmente `(commit hash após aceito)`) DEVE ser alterada para:

```
## Implementação (ponteiro após aceito)
- Ponteiro: branch <nome> · data <YYYY-MM-DD> · grep <pattern para localizar a implementação>
- Hash de commit: opcional como complemento — NUNCA único, porque rewrites (rebase, --reset-author, history surgery) invalidam o hash silenciosamente. Lição registrada no ADR-001 e na memória do mantenedor.
```

### Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Atualizar template proativamente (escolhida)** | Próximos ADRs nascem com o padrão certo. A lição do ADR-001 vira convenção codificada, não folklore | Toca um arquivo que não é parte da feature principal. Expande o escopo da v1.6.0 |
| 2 | ADR-002 desvia do template sem corrigi-lo | Mínimo esforço neste ciclo | Próximo ADR vai cair na mesma armadilha. A lição de memória do mantenedor não se manifesta no código do projeto |
| 3 | Postergar (issue separada) | v1.6.0 fica focada na feature | Cada novo ADR escrito antes da correção repete o anti-padrão |
| 4 | Política externa (CLAUDE.md) | Sem editar template | Quem usa o template não lê CLAUDE.md no momento de criar o ADR |

### Justificativa
Templates são contratos com o futuro: a próxima pessoa que copiar o `000-template.md` segue o que está lá. Postergar é garantir que a próxima ADR-N cairá na armadilha. Atualizar agora custa 3 linhas e elimina a categoria de falha.

---

## D6 — Handoff `discovery → architect` via arquivo separado `gap-analysis.md`

### Decisão
O sub-modo "mapeamento de processo" entrega **3 arquivos lado a lado** em `docs/specs/<caso>/`: `requirements.md` (dimensões), `process-map-as-is.md` (mapa), e `gap-analysis.md` (diagnóstico). O architect recebe o `gap-analysis.md` como entrada explícita para produzir to-be design via ADR(s). Cada arquivo tem leitor distinto.

### Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **3 arquivos separados (escolhida)** | Cada arquivo serve um leitor: BA lê requirements; operador lê process-map; architect lê gap. Em processo pequeno, cada arquivo fica curto naturalmente. Permite versionamento independente | Cerimônia maior. 3 arquivos a manter sincronizados |
| 2 | 2 arquivos (mapa+req juntos, gap separado) | Menos arquivos. Gap fica explicitamente para architect | Mapa no requirements.md polui o documento de spec com diagramas pesados em casos `deep` |
| 3 | 1 arquivo monolítico | Mais simples | Pesado quando o processo é grande. Difícil de ler. Architect tem que filtrar mentalmente |
| 4 | Acoplamento automático (discovery → architect direto) | Sem handoff manual | Contra o espírito do framework: papéis isolados, validação humana entre estágios |

### Justificativa
3 arquivos preserva o princípio de **um arquivo, um leitor** que já existe em `docs/specs/_template/` (requirements.md + validation.md). Em processo pequeno, arquivos ficam curtos — não é cerimônia, é separação semântica que paga.

---

## D7 — Protocolo `discovery + explorer` (EARS-W5)

### Decisão
Quando o processo está implementado em código/sistema (BPMS, n8n, Airflow, workflow de SaaS), discovery (etnografia humana) e explorer (auditoria de código) rodam:

- **Modo single-thread (default — Claude Code sem subagentes):** discovery e explorer rodam em **sequência rápida com síntese explícita**, mesmo turno. Discovery faz a etnografia, depois pede ao usuário o relatório do explorer (ou roda explorer logo em seguida no mesmo turno), e consolida ambos em `gap-analysis.md`.
- **Modo persona-4 (pipeline automatizado com infraestrutura):** discovery e explorer rodam **como subagentes reais em paralelo**, cada um produzindo seu artefato, e um passo final de **cruzamento** (executado pelo orquestrador do pipeline) produz o `gap-analysis.md` consolidado.

Em ambos os modos, o **cruzamento** é feito pelo discovery (que consolida), não pelo architect.

### Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Sequência rápida + paralelo real por persona (escolhida)** | Cobre os dois cenários (single-thread e pipeline). Realista — não pretende que single-thread tem paralelismo verdadeiro. Discovery consolida (anti-padrão #1 do BPM em mãos do papel certo) | Definição mais longa, dois protocolos a documentar |
| 2 | Só sequência (sem paralelo real) | Mais simples de documentar | Persona 4 (pipeline) perde eficiência onde a paralelização real é possível |
| 3 | Só paralelo real | Mais arquitetonicamente puro | Single-thread (caso mais comum) fica forçado a um modelo que não suporta |
| 4 | Architect consolida | Architect fica com input cross-fonte | Borra fronteira: cruzamento é diagnóstico, não design — pertence ao discovery |

### Justificativa
A palavra "paralelo" é metáfora em single-thread e literal em pipeline — o ADR deixa explícito qual é qual, evitando que developer interprete EARS-W5 como paralelismo mágico no Claude Code. Discovery consolida porque cruzar declarativo×observacional é diagnóstico, e diagnóstico cabe em quem descreve, não em quem decide.

---

## Consequências (positivas / negativas / riscos)

### Positivas
1. Framework ganha capacidade BPM-sênior sem fragmentação (1 skill estendida, 0 skills novas).
2. Ergonomia entre os dois sub-modos do discovery torna-se simétrica.
3. Drift de versão no frontmatter da skill é corrigido permanentemente.
4. Template ADR-000 deixa de instruir o anti-padrão de hash; próximos ADRs nascem com ponteiro robusto.
5. 13 gaps detectados na revisão adversarial fechados antes da implementação — economiza ciclos do qa-critic.
6. Output determinístico (cabeçalho YAML obrigatório quando persona=4) permite consumo por subagentes automatizados.
7. Backward compatibility preservada: nenhum comportamento existente do discovery v1.5.0 é alterado (incluindo o sub-modo "revisar", que só ganha filtro formal sem mudar downstream).

### Negativas
1. Skill `discovery/SKILL.md` cresce de ~90 linhas para ~220-260 (~2.5x). Cognitive load maior para quem lê pela primeira vez. Mitigação: 3 níveis de profundidade (`quick`/`standard`/`deep`) permitem que operador use só o que precisa.
2. Escopo da v1.6.0 cresceu ~40% após revisão adversarial (8 → 12 itens no critério de aceite). Mais trabalho para o developer. Mitigação: o validation.md já está pronto e cobre cada item binariamente — qa-critic roda mecanicamente.
3. 13 dimensões nominais (4 MUST + 4 MAY + 1 condicional + 4 anti-raso) podem assustar operador humano. Mitigação: modo `quick` reduz a 5 blocos operacionais.

### Riscos
1. **Modo prospectivo** — sem dor real vivida, o primeiro caso real pode revelar dimensão não prevista. Mitigação: exemplo H1 trabalhado força stress-test em ambiente regulado (caso mais carregado). Se algo escapar, vira v1.6.1 (PATCH).
2. **Subagente automatizado + validação stakeholder** — pipeline produz `[BLOQUEADOR: validação humana pendente]` com exit-code não-zero. Risco: orquestradores downstream podem ignorar exit-code não-zero e seguir mesmo assim. Mitigação: documentado no validation.md como reprovação binária; orquestradores que ignorarem violam o contrato.
3. **Sweep "BA/processo" sem aviso prévio** — terceiros que clonaram o repo em v1.5.0 podem ter referenciado os 6 termos da linha. Mitigação: CHANGELOG documenta o sweep com texto antes/depois; ADR-002 registra a decisão; quem lê CHANGELOG ao atualizar entende.
4. **Auto-sync hook em SessionStart** — propaga skill atualizada ao global automaticamente. Risco: alguém testando v1.6.0 em sessão local antes do merge pode ter o global atualizado com versão de trabalho. Mitigação: documentado na NF7 do requirements.md (escopo do hook explicitado).

---

## Implementação (ponteiro após aceito)

- **Ponteiro:**
  - Branch: `feat/discovery-process-mapping-v160` (a criar pelo developer a partir de `main`)
  - Data: a preencher após merge (`YYYY-MM-DD`)
  - Grep para localizar implementação: `git log --all --grep "v1.6.0" --grep "process-mapping" --grep "discovery 1.6.0"`
- **Hash de commit:** opcional como complemento após merge. NUNCA único — rewrites invalidam (lição registrada no ADR-001 e na memória do mantenedor `feedback_adr_hash_pattern.md`).
- **Validação:** `qa-critic` roda o gabarito de `docs/specs/discovery-process-mapping/validation.md`. Reprovação em qualquer um dos 12 itens (Bloco A) ou qualquer gap não fechado (Bloco B) ou anti-raso ausente (Bloco C) ou princípio violado (Bloco D) bloqueia o merge.
- **Pipeline esperado:** ARCHITECT (este ADR) → DEVELOPER (implementa 12 itens) → QA-CRITIC (valida com validation.md) → DOCOPS (CHANGELOG, README, sweep de referência órfã) → merge.

---

## Referências

- Spec: [docs/specs/discovery-process-mapping/requirements.md](../specs/discovery-process-mapping/requirements.md)
- Gabarito de validação: [docs/specs/discovery-process-mapping/validation.md](../specs/discovery-process-mapping/validation.md)
- ADR precedente: [docs/adr/001-ocultar-template-agente.md](001-ocultar-template-agente.md) (lição do hash registrada)
- Skill atual a ser estendida: `.agent/skills/discovery/SKILL.md` (v1.5.0 efetiva, frontmatter divergente)
- Roteador a ser atualizado: `AGENT-FRAMEWORK.md` linhas 90-99 (Gatilho do discovery)
- Eval a ser estendido: `_meta/eval-results-papeis.md` (seções G+G' como gabarito; H+H' a adicionar com ≥9+9=18 casos)
- Auto-sync hook (propagação ao global): `.claude/hooks/sync-global.ps1` (escopo restrito a SKILL.md, conforme NF7)
