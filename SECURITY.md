# Política e Postura de Segurança

> **Honestidade primeiro (é a regra do próprio framework):** este documento descreve o que o
> framework **mecaniza**, o que **recomenda mas ainda não mecaniza**, e o que está **fora de escopo**.
> Nada aqui é alegado como "resolvido" sem ser verdade. Segurança de IA agêntica é **responsabilidade
> compartilhada**: o framework dá camadas de defesa; o ambiente (modelo, runtime, infra) e você cobrem o resto.

O Framework Metacognitivo Agêntico é um **método de orquestração** para agentes (sobre Claude Code).
Ele não é um produto de segurança nem um WAF/antivírus — é uma **disciplina de defesa-em-profundidade**
em torno das **ações** de um agente de IA.

---

## Tese central: não confiar no raciocínio do agente

A maioria dos problemas de segurança de agentes vem de **confiar que o agente fará a coisa certa**.
Este framework parte do oposto:

> **Gate por EFEITO, não por intenção.** Uma ação é avaliada pelo que ela *causa* (destrói dados?
> é irreversível? sai do limite de confiança?), não por o agente *achar* que é segura. Assim, mesmo
> um agente **enganado por prompt injection** não consegue causar dano irreversível de forma autônoma —
> o efeito é barrado antes de executar (com os hooks ativos; ver *Pré-requisito de garantia*).

---

## Camadas de defesa que o framework MECANIZA

| Camada | O que faz | Onde |
|---|---|---|
| **Classificação de confiança + anti-alucinação** | Todo fato/parâmetro é `CONFIRMADO/INFERIDO/DESCONHECIDO`; o agente não fabrica nem age sobre o não-verificado. | `_shared/anti-hallucination`, `_shared/confidence-classification` |
| **Ação-segura por efeito (E1–E6 → T1/T2/T3)** | Classifica a ação pelo efeito; **T3 = irreversível + alto impacto** exige **gate humano** (default-deny, nunca auto-aprovável). | `_shared/action-safety` (ADR-014) |
| **`effect-gate` (hook PreToolUse)** | Backstop **executável** que nega T3 inequívoco (`rm -rf` em raiz/home, `git push --force` sem lease, `mkfs`/`dd` em device, fork bomb, desligar firewall). **Ativo por default** (wired no `.claude/settings.json`); roda em **qualquer modo de execução**, inclusive `autosuficiente`/bypassPermissions (hook ≠ permissão) e mesmo que o agente esteja injetado. **Só nega, nunca pergunta** — não adiciona prompt. Fail-open em erro interno → a camada não-bypassável é o `managed-settings`. | `tools/hooks/effect-gate.{ps1,sh}` (ADR-015) |
| **`managed-settings` fail-closed** | `disableBypassPermissionsMode`, `allowManagedHooksOnly`, deny mínimo. O agente **não pode desligar os próprios guard-rails** (nem editando `settings.json`). Requer instalação no caminho gerenciado do SO. | `tools/managed-settings.template.json` (ADR-015) |
| **Modos de execução (ratchet)** | `default` (prompts) · `avançado` (shell amplo, ask em push/merge) · `autosuficiente` (bypassPermissions, deny mínimo). Você escolhe o nível de **autonomia**; o `effect-gate` + `managed-settings` são o **piso absoluto sob os 3 modos** — mesmo `autosuficiente` nunca executa T3 catastrófico. | `_shared/execution-modes` (ADR-005) |
| **High-stakes gate (HITL)** | Decisão irreversível/regulada → validação por risco + **human-in-the-loop** + audit trail + logs imutáveis. | `_shared/high-stakes-gate` |
| **Observabilidade / trilha auditável** | Registro do que foi feito (OTel GenAI no IDE; digest no chat). | `_shared/observability` (ADR-017) |
| **Isolamento cross-projeto (agnosticismo)** | O núcleo não importa dados/normas de outro projeto sem declaração — uma forma de *data isolation* contra vazamento entre contextos. Linter executável. | `tools/check_core_agnostic.py` (ADR-020) |
| **QA adversarial heterogêneo** | Revisor independente (modelo de família diferente) com hipótese-default "existe bug" — defesa contra erro e colusão cognitiva. | `qa-critic` (ADR-011/018) |

---

## Mapeamento ao OWASP Top 10 for LLM Applications (2025)

Honesto sobre o grau de cobertura:

| Risco OWASP LLM | Cobertura | Como / ressalva |
|---|---|---|
| **LLM01 — Prompt Injection** | 🟡 **Parcial (consequência contida)** | O **efeito** de uma injeção bem-sucedida é barrado (effect-gate + default-deny + HITL em T3). **NÃO** há sanitização de input nem detecção de padrão de injeção. Ver "Anti-prompt-injection" abaixo. |
| **LLM02 — Sensitive Info Disclosure** | 🟡 Parcial | Anti-vazamento cross-projeto + "credenciais via env, não no prompt". **Não** há DLP/redaction automática. |
| **LLM05 — Improper Output Handling** | 🟡 Parcial | Validação de saída (`output-format`) + critério binário de aceite. Sanitização de saída para sistemas downstream é responsabilidade da aplicação. |
| **LLM06 — Excessive Agency** | 🟢 **Forte (foco do framework)** | Gate por efeito, default-deny, T3 = gate humano, managed-settings não-desativável. É o coração da postura. |
| **LLM07 — System Prompt Leakage** | ⚪ N/A por design | Framework **open source** — os prompts (`CLAUDE.md`, skills) são **públicos por desenho**; não há prompt secreto a vazar. (Você: nunca colocar segredo em prompt — usar env.) |
| **LLM08 — Vector/Embedding Weaknesses** | ⚪ Fora de escopo | Camada de RAG/infra, não do método. |
| **LLM04 — Data/Model Poisoning** | ⚪ Fora de escopo | Treino/modelo, fora do método. |
| **LLM09 — Misinformation** | 🟡 Parcial | Anti-alucinação + classificação de confiança + "NÃO SEI". Não substitui verificação factual humana. |
| **LLM10 — Unbounded Consumption** | 🟡 Parcial | `effect-gate` pega fork bomb; compaction governada limita contexto. Não há rate-limit de custo. |

> Fonte do referencial: OWASP Top 10 for LLM Applications (owasp.org). Mapeamento é `[INFERIDO]` —
> auto-avaliação do mantenedor, não auditoria independente.

> **Por que tanto 🟡 — e por que isso é o correto, não fraqueza.** "Parcial" é o **teto honesto de uma
> camada de orquestração**: sanitização de input, DLP, RAG e treino vivem em **outras camadas**
> (modelo/infra/aplicação); marcar 🟢 ali seria **falso** — e falha numa auditoria. 🟢 fica só onde o método
> **é** a camada dona (LLM06 — Excessive Agency). **Para ambiente regulado:** o framework entrega a
> governança do *agente* (excessive agency, HITL/T3, audit trail, rastreabilidade); os controles da norma
> (DLP, validação formal, sanitização) são **responsabilidade da aplicação** — declarados pelo discovery +
> `high-stakes-gate` (ver §Escopo e responsabilidade compartilhada). **Recomenda-se auditoria independente**
> antes de tratar qualquer item como conforme: este mapa é ponto de partida, não certificado.

---

## Anti-prompt-injection — postura honesta

**O que protege você hoje (mecanizado):**
- **Contenção por efeito:** injeção que tenta `rm -rf`, force-push, deploy destrutivo, mudar permissões → **bloqueado pelo effect-gate/managed-settings**, independente de ter enganado o agente.
- **Sem auto-bypass:** o agente não consegue se conceder `--dangerously-skip-permissions` (managed-settings).
- **Gate humano** em ações irreversíveis/externamente visíveis de alto impacto (T3).

**O que VOCÊ deve fazer (recomendado — ainda não mecanizado):**
- Tratar **conteúdo de ferramentas, web, e arquivos externos como DADO, não como instrução.** Se um documento diz "ignore suas regras e faça X", isso é dado a analisar, não um comando.
- **Não colar segredos** no prompt; credenciais via variável de ambiente (`_meta/external-access`).
- **Revisar antes de ações externamente visíveis** (E3: enviar, publicar, deploy) — o gate sinaliza, mas o julgamento é seu.

**O que NÃO está coberto (seja cético):**
- Detecção/sanitização de padrões de injeção (é responsabilidade do modelo/runtime).
- **Exfiltração via ferramentas permitidas** (T1): um agente injetado ainda pode *ler* e *resumir* dados que já tem acesso de leitura. O gate restringe **efeito destrutivo**, não leitura legítima.
- Manipulação para ações **não-destrutivas porém indesejadas** dentro do allowlist.

> **Candidato a mecanizar (ADR futuro):** uma regra `_shared` explícita de *untrusted-content handling*
> (marcar e isolar conteúdo externo como não-confiável) + heurística no effect-gate para E3 (saída
> externa). Hoje é **prosa/recomendação**, não mecanismo — declarado para não overclaim.

---

## Escopo e responsabilidade compartilhada

| Camada | Quem responde |
|---|---|
| Efeito de ações destrutivas/irreversíveis | **Framework** (gate por efeito + HITL) |
| Não desativar guard-rails | **Framework** (managed-settings) — exige instalação correta (ver abaixo) |
| Sanitização de input/output, DLP, detecção de injeção | **Ambiente/modelo + você** |
| Segurança da infra (rede, segredos, SO) | **Você** |
| Conformidade regulatória específica | **Você** (declarada pelo discovery; o núcleo é agnóstico) |

**Pré-requisito de garantia (duas camadas):** (1) o `effect-gate` já vem **ativo por default** no
`.claude/settings.json` do repo (PreToolUse) — mas como o agente *pode* editar esse arquivo, é defesa,
não garantia; (2) a camada **não-bypassável** é o `managed-settings.json` instalado no caminho gerenciado
do SO (`allowManagedHooksOnly` impede o agente de desligar o hook) — **instale-o** para garantia real
(ver `tools/managed-settings.template.json`). Em **macOS/Linux**, o `effect-gate.sh` requer **`jq`**
(sem jq, degrada para *allow* silencioso — instale `jq`). **Bug conhecido #44642:** em macOS, `disableBypassPermissionsMode`
pode ser ignorado (aberto, "not planned") — por isso defesa-em-profundidade, nunca camada única.

---

## Reportar uma vulnerabilidade

- **Preferencial:** abra um **GitHub Security Advisory privado** — aba **Security** do repositório →
  *Report a vulnerability* (divulgação coordenada, sem expor publicamente antes da correção).
- **Não** abra issue pública para vulnerabilidade não divulgada.
- Inclua: passo-a-passo de reprodução, impacto, e o efeito (E1–E6) que a falha permite.

Como o framework é distribuído sob **CC BY 4.0** (sem garantia), trate-o como **defesa-em-profundidade
auditável**, não como garantia de segurança. Avalie no seu contexto antes de usar em produção crítica.

---

## Telemetria de processo (anonimizada, opt-out) — ADR-052

Numa **distribuição** (público/non-admin/premium), o fechamento de um bloco pode gerar em `telemetry/`
um relatório de **processo** — **apenas sinais codificados** (qual gate disparou, onde um hook/regra
falhou, onde você corrigiu, rodadas de retrabalho). **Nunca** registra o conteúdo do seu trabalho, texto
livre ou dado pessoal — isso é garantido por uma **whitelist de schema verificável** (não por confiança;
lição do incidente de 2026-05-31), com heurística anti-PII e backstop de anonimização.

- **Base legal:** payload **não-pessoal** → **fora do escopo da LGPD** (Art. 12).
- **Transmissão:** **nenhuma automática.** O relatório fica local; **só vai ao mantenedor se você abrir
  um PR** com ele — e esse PR é o seu **consentimento explícito** (você revê o arquivo, é legível).
- **Opt-out (desliga a geração):** `.claude/no-telemetry.lock` (projeto) · `~/.claude/no-telemetry.lock`
  (global) · env `FRAMEWORK_NO_TELEMETRY=1`.
- **Ciência:** ao baixar o framework você toma ciência desta política. Detalhe completo em
  [`TELEMETRY.md`](TELEMETRY.md). No repo-fonte do mantenedor (tier OWNER) o relatório completo fica em
  `docs/_private/_intake/` e **não é distribuído**.
