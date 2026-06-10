# Plano Anti-Bypass — lições sistêmicas do Gemini aplicadas ao framework Claude

> **Status:** PROPOSTO (aguarda gate humano antes de tocar núcleo) · **Data:** 2026-06-10
> **Origem:** auditoria dos relatórios cross-IA do Gemini (`~/.gemini/.../metacognition-gemini/reports-improve-cross-ai/`,
> `docs/_private/`, `history.md` Gemini, ADR-075) + reconciliação com o repo **vivo** deste framework.
> **Pedido do dono (literal):** *"é só pra garantir que vc não caia nos mesmos erros. se garantias existem,
> garantir que sejam sempre executadas e não bypassadas."* → **Não é adicionar gate novo. É enforcement.**

## Método (e armadilhas evitadas — lição do próprio PLANO-REMEDIACAO §1)
- **Régua §0 (ganho líquido):** adição pura rejeitada. Cada item funde/torna-executável algo que já existe.
- **Re-auditoria do repo vivo feita** (não confiei no snapshot dos relatórios): cada linha da tabela §1 tem
  evidência de arquivo verificado nesta sessão.
- **Convergência Claude×Gemini ≠ prova forte** (saíram de prompts irmãos). Tratada como corroboração parcial.
- **Anti-sicofância aplicada a mim mesmo:** não aceitei "este gap existe" de resumo de relatório sem `grep`
  no código vivo — fazê-lo seria cometer o erro nº1 do Gemini (aceitar premissa sem checar a fonte canônica).

---

## §1 — Erros sistêmicos do Gemini × estado VERIFICADO neste framework

Legenda: ✅ mecanizado e robusto · 🟡 mecanizado mas **bypassável** (foco do dono) · ⬜ ausente/debatível.

| # | Erro sistêmico (Gemini) | Estado aqui | Evidência (repo vivo) |
|---|---|---|---|
| 1 | Sicofância / aceitar premissa sem checar fonte canônica | ✅ canário CI | `tools/test_sycophancy.py`, qa-critic rule #9, ADR-041 |
| 2 | Falsa eficiência / atalho que fura isolamento | ✅ | `tools/hooks/shadow_write_guard.py`, `action-safety`, régua §0 |
| 3 | Iteração ilimitada (sem teto local na junção) | ⬜ debatível | `MAX_ROUND` só em `cross_ai_gate.py`; **Gemini revogou** seu próprio `MAX_ROUNDS=3` em favor do process-critic rewind → **não adotar** |
| 4 | Autoridade dupla de prompt / drift silencioso | 🟡 parcial | `check_core_agnostic.py` lista CORE_FILES mas checa **vazamento de domínio**, não **contradição entre** `CLAUDE.md`×`AGENTS.md`×`AGENT-FRAMEWORK.md` |
| 5 | Ataque adversarial raso (só segue checklist) | ✅ prosa em paridade | `qa-critic/SKILL.md:101` exige "revisão aberta adversarial… bugs novos não-listados" (mesmo nível do fix do Gemini, que também foi prosa) |
| 6 | Teste passa em silêncio quando falta runtime | ✅ **melhor que o Gemini** | `tools/test_effect_gate.py:102-105` faz **SKIP ruidoso** (stderr) sem reprovar CI; matriz 3-OS prova onde há PS; `test_parity.py` idem |
| 7 | Conflação developer×qa-critic (mesmo modelo) | ✅ | qa-critic em subagente isolado heterogêneo (ADR-018); `_meta/subagent-isolation.md` |
| 8 | Parada não-determinística entre papéis | 🟡 parcial | fluxo J0-J5 (`/handoff`); transição depende do agente — bypassável em prosa |
| 9 | Viés de oráculo / confiar em fonte sem verificar | ✅ canário CI | `tools/test_oracle_bias.py`; "ler antes de elicitar" no discovery |
| 10 | Perda de estado / sem heartbeat | ✅ | `history.md` append-only, `/checkpoint`, `compaction-gate` |
| 11 | Conformidade de produto (QA valida ADR, não requisito) | ✅ mesmo ADR | **ADR-036** "porta do usuário + ambiente limpo" + `check_entrypoint_tty.py` + `check_clean_env.py` (frameworks irmãos compartilham o nº) |
| 12 | Homologado ≠ commitado (entrega untracked) | 🟡 **bypassável** | `consistency-gate` checa `unpushed` mas é **fail-soft** e **não disparou em ~7 fechamentos** (`execution-report-2026-06-08-determinism-gates.md`) |

**Conclusão honesta:** 8 de 12 já são robustos aqui; 1 é debatível e **deliberadamente não-adotado** (#3);
os **3 itens reais** são **bypass**, não ausência: #4 (drift entre arquivos de autoridade), #8 e #12
(garantias session-side que não disparam). É exatamente o que o dono pediu para fechar.

---

## §2 — A fronteira do bypass (a causa-raiz comum)

Verificado nesta sessão: **gates CI fail-closed são inbypassáveis** (PR vermelho não mergeia) —
`qa-evidence`, `posture-gate`, `adr-changelog-sync`, `release-checkpoint`, `check_core_agnostic` (no CI).
**Gates session-side são bypassáveis** nesta máquina por dois motivos cumulativos:

1. **Hook PS inerte sob Kaspersky/EDR** (ADR-047/060/061): `check-repo-sync`, `consistency-gate.ps1`,
   `context-budget` (PreToolUse Read) **não rodam** aqui — o banner de liveness anuncia, mas não força.
2. **Passo manual skippável pelo agente:** `boot-scan` cross-IA e os passos 0.5/0.6 do `start-session`
   foram **pulados** (assumiu silêncio=vazio) — falha real registrada em 2026-06-08.

O liveness auditor (ADR-061) **detecta e avisa**, mas avisar ≠ executar. **Esse é o gap.**

---

## §3 — Plano de enforcement (lean; cada item = par executável OU limite declarado)

### E1 — Funde os passos de boot manuais num único self-check Python + prova de sessão  ⭐
**Problema:** os passos session-side estão espalhados (sync, agnosticismo, boot-scan, modo) e cada um é
skippável; sob Kaspersky os hooks que os fariam estão inertes.
**Mecanismo (ganho líquido — funde N passos em 1, não adiciona superfície):**
`tools/boot_check.py` que roda, em Python (não-hook, imune ao veto de EDR), TODAS as verificações de boot
que hoje são prosa/hook-inerte: `git fetch`+ahead/behind, `check_core_agnostic`, `cross_ai_hub boot-scan`,
sanidade de versão (anti-"v3.1 fantasma" do Gemini), modo de execução. **Grava prova** em
`.claude/boot-proof.json` (timestamp + resultado por verificação).
**Anti-bypass:** o banner de liveness (que JÁ roda via UserPromptSubmit) passa a apontar 1 comando único;
e um gate de **fechamento** (E2) reprova se a prova de boot não existir na sessão. Converte "nag advisory"
em "prova checável".
**Par:** `tools/test_boot_check.py`. **ADR:** emenda à ADR-061 (auditor de liveness ganha forma executável única).

### E2 — consistency-gate: de fail-soft-que-não-dispara → checável no fechamento (CI fail-closed)
**Problema:** `consistency-gate` (ADR-030) é fail-soft e não disparou em ~7 fechamentos.
**Mecanismo:** já existe `test_release_checkpoint.py` fail-closed no CI. **Estender** o canário de fechamento
para incluir as dimensões do consistency-gate hoje só em PS (version-sync, adr-status, **unpushed**, contagens).
Não cria gate novo — **funde** a checagem fail-soft órfã na fail-closed que já roda. Limite honesto:
"unpushed" no CI checa o que chegou ao PR, não a working tree local (essa parte fica no E1/boot-proof).
**ADR:** emenda à ADR-030 (mecaniza o disparo via o gate de release que já existe).

### E3 — Drift entre arquivos de autoridade (erro #4 do Gemini)
**Problema:** as **4 regras invioláveis** vivem em `CLAUDE.md`, `AGENTS.md`, CLAUDE.md global e
`AGENT-FRAMEWORK.md`. Nada detecta se divergirem (drift silencioso = erro #4 do Gemini).
**Mecanismo:** `tools/check_rules_parity.py` — extrai o bloco "regras invioláveis/sempre ativas" de cada
arquivo de autoridade e exige equivalência semântica (mesmas 4 regras, mesma ordem). Fail-closed no CI.
**Par:** `tools/test_rules_parity.py`. Pequeno, alto valor, **mecaniza** o que no Gemini virou só prosa (ADR-075).
**ADR:** novo, curto — único item que é "adição", justificado pela régua §0(c) (destrava garantia
inalcançável por prosa: o próprio erro #4 do Gemini prova que prosa não basta).

### Limites declarados (vão para `LIMITS.md`, não vendidos como garantia)
- **context-budget PreToolUse (Read)** sob Kaspersky: hook vetado → permanece **doutrina + banner**.
  E1 mitiga parcialmente (boot-proof lembra), mas forçar cada `Read` exige hook = **não-mecanizável aqui**.
- **#8 (parada entre papéis)** e **ataque adversarial genuíno (#5):** "o agente realmente aplicou postura"
  é parcialmente não-mecanizável (P11 honesto). `posture-gate` (CI fail-closed) já é o teto do mecanizável;
  o resto é limite declarado, não gap a "consertar" com mais prosa.

### O que NÃO fazer (anti-inflação — registrar a recusa)
- **Não** adicionar canário de oracle-bias/sicofância/effect-gate/conformidade — já existem (§1).
- **Não** adotar `MAX_ROUNDS=N` na junção: o próprio Gemini revogou; process-critic rewind é superior (#3).
- **Não** tratar convergência Claude×Gemini como validação independente.

---

## §4 — Fase 2: replicar no framework Gemini (após aprovação da Fase 1)
**Restrição dura — write-isolation (ADR-070):** este repo **escreve só em si**; **não faço push** ao Gemini.
A pasta `~/.gemini/.../metacognition-gemini` é working copy local do dono. Caminho correto:
1. Gerar o **mesmo gap-analysis** contra o repo vivo do Gemini (alguns itens lá já existem — ex. ADR-075,
   `verify_hitl_proofs.py`, `shadow_write_guard.py` já estão na pasta).
2. Entregar como **handoff cross-IA** (`docs/_private/cross-ai/outbox/…__to-gemini-master__…`) — o canal
   que o protocolo já define — em vez de editar o repo dele direto.
3. O Gemini aplica no próprio master (isolamento preservado). Confirmar com o dono se prefere handoff
   ou edição direta da working copy local (override explícito de write-isolation, com custo declarado).

---

## §5 — Próximos passos (param no gate humano)
1. **Dono aprova o escopo** desta Fase 1 (E1+E2+E3) — toca núcleo/CI → **gate humano**.
2. Implementar via squad: discovery (já feito aqui) → architect (ADRs E1/E2/E3) → developer → qa-critic
   adversarial isolado → docops. 1 commit por item, parar no PR.
3. Após merge: Fase 2 (handoff cross-IA para o Gemini).
</content>
</invoke>
