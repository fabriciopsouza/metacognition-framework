# ADR 094 — Processo ADVERSARIAL mandatório (reforço por-turno) + canônico-prevalece + autonomia-limitada + EDR verificável

- Status: **Aceito** (2026-06-23 — diretriz do dono: *"o PROCESSO adversarial é o CORAÇÃO do framework e precisa ser mandatório; ANTES funcionava SEM bloquear; advisory parou de funcionar"*) · Decisores: dono + squad (architect) · pré-gate de código: qa-critic heterogêneo isolado
- Tipo: **EMENDA ADITIVA** — NÃO reescreve desenho aprovado, NÃO adiciona hard-block de merge (o dono confirmou que antes funcionava sem bloquear). Estende ADR-027 (route-gate → reforço adversarial por-turno), ADR-093 (`kind=process`), ADR-005 (fronteira da autonomia), `_shared/traceability` (regra de precedência).
- Relaciona: ADR-047/060/079 (EDR assumida→verificada), ADR-007 (régua §0), ADR-011/018 (qa-critic adversarial heterogêneo), ADR-074 (atestação de isolamento).

## Contexto (a causa-raiz REAL, após 3 reconciliações com o dono)
1. Hipótese 1 (minha): gates regrediram. **REFUTADA** por comparação histórica (git): hooks fail-closed sempre foram só de EFEITO crítico/irreversível; route-gate (processo) nasceu advisory; BMAD não advisory-izou nada.
2. Hipótese 2 (minha): falta hard-block. **REFUTADA pelo dono:** *"antes funcionava SEM bloquear"* — a postura adversarial operava sem trava de merge.
3. **Causa-raiz confirmada:** o CORAÇÃO do framework é o **comportamento ADVERSARIAL** — questionar o dono (surface-and-reconcile), ser cético na elicitação/pesquisa, rodar qa-critic por padrão, buscar exaustivamente antes de NÃO-SEI. Esse comportamento **degradou para reativo/fácil**, e eu agravei tratando "modo autônomo" (pontual) como licença para pular o processo e reabrir o canônico. O dono: *"isso não está funcionando, nunca ou quase nunca."* Não é falta de gate; é o comportamento que parou de ser default.

## Decisão (1 frase ativa)
Tornar o **processo adversarial MANDATÓRIO como modo-default**, **consolidado na Regra 6 de `_shared/traceability`** (reforça o `route-gate`/ADR-027 que JÁ injeta por-turno + ADR-011 QA bicelular — **SEM hook novo**, régua §0), **SEM hard-block de merge** (antes funcionava sem); + gravar **canônico-prevalece** e **autonomia-limitada** como regras de precedência; + tornar a premissa **EDR verificável** (`kind=process` no `boot_check`), não assumida. Tudo aditivo (régua §0).

## Mecanismo (re-afirmar o que já existe — régua §0 — + 1 mecanismo novo)
1. **Mandato adversarial — SEM hook novo (régua §0; o dono: "as regras já existiam e funcionavam"):** o `route-gate` (ADR-027, UserPromptSubmit) JÁ injeta por-turno e ADR-011 (QA bicelular até-PASS, process-critic único com rewind) JÁ define o adversarial; o defeito foi **não SEGUIR**. A **Regra 6** (`_shared`, abaixo) consolida e torna explícito o mandato-default — a CADA turno: **(a)** DESAFIAR o pedido (custo/consequência/premissa errada — o pedido do dono não é livre de erro); **(b)** classificar confiança; **(c)** declarar ROTA; **(d)** entregável → qa-critic adversarial ISOLADO (modelo≠autor, ADR-074) OBRIGATÓRIO por-default, não sob-provocação; **(e)** elicitação/pesquisa céticas e exaustivas antes de DESCONHECIDO; **(f)** NUNCA reabrir/sobrescrever canônico sem confirmação. Reusa route-gate/ADR-011; **não cria mecanismo novo**.
2. **Regra `_shared/traceability` Regra 6 — canônico-prevalece + autonomia-limitada + adversarial-mandatório:** (i) decisão/binding/nome/abordagem APROVADA é CANÔNICA e PREVALECE (data+aprovação); descoberta nova é CANDIDATA, entra só com ganho-líquido (§0) + confirmação do dono — APPEND, nunca rewrite. (ii) autonomia (ADR-005) acelera EXECUÇÃO de E1, NUNCA dispensa o processo adversarial nem autoriza reabrir o canônico. (iii) o processo adversarial é mandatório-default, não reativo.
3. **EDR verificável** (estende ADR-093, aditivo): `boot_check` `kind=process` detecta processo EDR real → `.agent/environment.json` marca APLICA/ESTALE a premissa do veto, fim do "hint-virou-causa".

## Alternativas consideradas
1. **Hard-block de merge (squad_gate ativado).** REJEITADA: o dono confirmou que antes funcionava SEM bloquear; bloquear muda o desenho aprovado e não era a causa. (`squad_gate` permanece como peça disponível, NÃO ativada — decisão futura do dono se algum dia advisory+reforço falharem.)
2. **Só prosa no boot (status quo).** Falhou: o mandato só no boot/marco não pega o turno-a-turno. Por isso o reforço é **por-turno**.
3. **Mandato adversarial por-turno + regras + EDR verificável, sem bloqueio (ESCOLHIDA).** Restaura o que funcionava (comportamento), no idioma que o dono pediu (hook/prosa por-turno), sem tocar o desenho aprovado nem travar merges.

## Consequências
**Positivas:** o mandato adversarial deixa de ser "lembrete de boot" e passa a bater a CADA turno (elicitação/pesquisa/crítica/desafio-ao-dono); canônico-prevalece e autonomia-limitada viram regra explícita (fecham os 2 erros desta sessão); EDR verificável encerra o "hint-virou-causa". Nada do aprovado é tocado; zero risco de travar merge. **Negativas/limite honesto:** reforço por-turno é injeção de prosa — aumenta a probabilidade de o agente seguir, mas NÃO força mecanicamente (nenhum hook força um LLM a ser cético). É o teto do que é seguro sem hard-block; se o dono concluir que ainda não basta, o `squad_gate` (pronto) é a escalada disponível (alt. 1).

## Implementação (após aceito — tudo aditivo)
- Ponteiro: branch `feature/adr-094-determinismo-squad-gate` · 2026-06-23 · grep `adversarial_mandate|canonico-prevalece|kind.*process`
- `_shared/traceability/SKILL.md`: **Regra 6** (consolida ADR-011/027/007 — adversarial-default + canônico-prevalece + autonomia-limitada). **SEM hook novo** (qa-critic ALTO-1: reusa route-gate/ADR-027 existente — régua §0).
- `tools/boot_check.py`: `kind=process` (+`_process_running`). `tools/test_environment_applicability.py`: caso process. `.agent/environment.example.json`: assumption EDR `kind=process`.
- **Sem nova capability** (qa-critic ALTO-2): `kind=process` ESTENDE a capability `environment-applicability-gate` (ADR-093) — não é feature nova (régua §0).
- NÃO mexer em route-gate/mission-gate (advisory por desenho). NÃO ativar squad_gate. **NÃO commitar `.claude/settings.json`** (qa-critic ALTO-3: acumula paths de cliente — fica em config local, fora do framework).
- Hash de commit: complemento opcional — nunca único (ADR-001/002).
