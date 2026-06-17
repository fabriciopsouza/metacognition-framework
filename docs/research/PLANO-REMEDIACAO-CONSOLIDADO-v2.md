# Plano de Remediação CONSOLIDADO — Framework Metacognitivo Agêntico

**Versão deste plano:** v2 (consolida a crítica adversarial sobre `v1.22.0`, as contribuições válidas da revisão Gemini, e a evidência de campo da execução **AIVI/Vibra 2026-05-31**).
**Alvo:** marcos incrementais **v1.23.0 → v1.32.0**.
**Método:** cada item é candidato de `discovery → architect/ADR → developer → qa-critic → docops`, sob régua §0 (ganho líquido).

> **Princípio reitor único (decisão do dono):** *linter, hook e ferramental são a BASE de toda a segurança do framework.* O objetivo desta revisão é **não depender de prosa**. Portanto: **todo item entrega um par executável (hook/linter/teste).** Prosa só permanece onde algo é **comprovadamente não-mecanizável** — e nesse caso é **declarada como limitação** no `LIMITS.md`, nunca vendida como garantia.

---

## 0. Três fluxos de evidência consolidados

Este plano funde três fontes. Cada item abaixo marca de qual veio (`[CRÍTICA]` minha análise do código · `[GEMINI]` contribuição válida da revisão externa · `[AIVI]` falha de campo real).

| Fluxo | O que trouxe | Peso |
|---|---|---|
| `[CRÍTICA]` | effect-gate estreito, evals em design-time, agnosticismo não-exaustivo, OWASP inferido, regras-miolo em prosa | médio (gaps estruturais) |
| `[GEMINI]` | sicofância como falha de 1ª classe; language-hooks-como-fatos; discovery→spec executável | médio (3 itens válidos; **resto descartado** — ver §12) |
| `[AIVI]` | **elicitação rasa de produto/domínio; viés de oráculo; overwrite não barrado; entry-point que quebra; telemetria ausente** | **alto (evidência de campo, não hipótese)** |

> **Reordenação que o AIVI força:** minha crítica original priorizava a borda destrutiva (effect-gate). O AIVI provou que **o gap mais caro é a elicitação proativa**, não a segurança de ação. O framework "brilhou na verificação e falhou na antecipação". Este plano coloca a **elicitação-consultiva** no centro (item 1) e reposiciona o effect-gate como item de robustez (item 7).

---

## 1. ⭐ Elicitação-consultiva mecanizada — banco agnóstico + linter que barra avanço

**Origem:** `[AIVI]` (causa-raiz nº 1) + `[GEMINI]` (discovery→spec executável).

**[GAP]** O agente AIVI "fez 4 perguntas (escopo, entrada, stack, oráculo). Não perguntou sobre produto/GUI." O dono teve de empurrar 7 regras de domínio + cobrar todo o produto (operador, GUI, escopo mensal+acumulado, recortes, persistência, log). O erro **não foi ausência de perguntas — foi perguntas de coletor de requisitos, não de consultor.** E mesmo havendo instrução de discovery em prosa, ela foi ignorada (o agente já tinha a regra e fez perguntas rasas).

**[DISTINÇÃO QUE PRESERVA O AGNOSTICISMO — P12]** Há dois tipos de pergunta e só um vive no núcleo:
- **Pergunta de domínio** ("descartar centros 7xxx?", "referência é variação interna?") — específica do projeto. **NUNCA entra no núcleo.** É *gerada* pelo discovery ao ler o material, não catalogada. O `check_core_agnostic.py` deve barrá-la se vazar.
- **Meta-pergunta de elicitação** ("quem opera?", "qual escopo temporal?", "precisa persistência?", "é regulado?", "que recortes de saída?") — **agnóstica, universal.** Vale para AIVI, dashboard ou pipeline qualquer. **Pode e deve viver no núcleo.**

**[FONTE]** A2 (spec-driven, eval por papel) + A0 (decomposição). O `mission-gate` (ADR-022) já existe e injeta `additionalContext` no SessionStart lendo `product-types.txt` da app — é o gancho onde isto se pluga.

**[MECANISMO — 3 camadas, ferramental é a base]**
1. **Banco agnóstico versionado** `_shared/discovery/elicitation-dimensions.md` — lista as **dimensões universais** que toda elicitação de produto recorrente deve cobrir (NÃO perguntas de domínio): `operador/usuário` · `interface (CLI/GUI/web/planilha)` · `entrada + validação guiada` · `escopo temporal (mês/intervalo/ano/realizado+acumulado)` · `recortes de saída` · `persistência/memória entre execuções` · `auditoria/log` · `ambiente de execução (instala em máquina limpa?)` · `formato de saída`. São *categorias agnósticas*; o discovery gera a pergunta concreta a partir do material do projeto.
2. **Discovery recomenda defaults sêniores com trade-off** (decisão do dono: consultoria de verdade, não pergunta em aberto). Para cada dimensão o discovery propõe: *"isto é regulado e vai a decisão executiva → recomendo log de auditoria e GUI para analista não-técnico; confirma ou prefere outro caminho?"* — em vez de *"qual interface?"*.
3. **Linter que BARRA avanço** `tools/check_spec_depth.py` — falha (exit 1) se o `requirements.md` não tiver **decisão registrada para cada dimensão obrigatória** do banco. Verifica que a *dimensão foi endereçada*, não que a *resposta é boa* (isso é domínio/julgamento). É o equivalente do `validate_skills.py` para completude de elicitação. Wirado como gate antes de J2 (discovery→architect): **o developer não começa enquanto a spec não cobrir as dimensões.** Isto é o que teria impedido o agente AIVI de pular "quem opera / GUI / acumulado".

**[CANÁRIO]** `test_spec_depth.py`: spec sintética sem dimensão "operador" ou "log" → FAIL; spec completa (e os exemplos H1-farma) → PASS. Caso de regressão AIVI: uma spec que diz só "calcular indicador" sem operador/escopo/persistência → DEVE falhar.

**[DONE quando]** banco no `_shared/` + `check_spec_depth.py` no CI barrando J2 + `check_core_agnostic` confirmando que o banco não contém termo de domínio + ≥3 discoveries reais com cada dimensão decidida e registrada.

**[ADR]** `033-elicitacao-consultiva-banco-agnostico-linter-de-spec.md`.

> **Limite declarado:** o linter garante *cobertura de dimensão*, não *qualidade da decisão*. Que a recomendação default seja sênior depende do agente — isso vai para `LIMITS.md` como "mecanizado: cobertura; não-mecanizado: acerto do default".

---

## 2. ⭐ Completude vs pedido — o produto cobre cada substantivo do pedido?

**Origem:** `[AIVI]` (calculou 1 mês quando o pedido dizia "mês a mês" e "cada unidade").

**[GAP]** O escopo entregue (1 mês / 1 base) era subconjunto do pedido ("mês a mês", "cada unidade", acumulado implícito). Nenhum gate cruzou pedido × entrega.

**[MECANISMO]** `tools/check_completeness.py` — extrai os substantivos/quantificadores do pedido registrado na spec (`mês a mês`, `cada unidade`, `acumulado`) e confirma que o `validation.md` tem um critério binário cobrindo cada um. Substantivo do pedido sem critério correspondente = FAIL antes do PASS final (J4).

**[CANÁRIO]** `test_completeness.py`: pedido "mês a mês por unidade" + validation que só testa 1 mês → FAIL.

**[DONE quando]** gate no CI, wirado a J4. **[ADR]** `034-completeness-vs-request-gate.md`.

---

## 3. ⭐ Anti-viés-de-oráculo + estabilidade de decisão (NÃO é elicitação — é execução)

**Origem:** `[AIVI]` (item #2 do placar — o erro mais caro da sessão).

**[GAP — e por que NÃO cabe no discovery]** O agente bateu 97,82% com a coluna certa, rotulou "total", o dono disse "interna", o agente pegou a coluna *literal* "Variação Interna" (só um componente), caiu para 95,62% **abandonando um resultado já validado**, e o dono provou 3× com a fonte. Isto aconteceu **depois da spec, na execução**. Gatilhos: (a) bater valor-alvo tratado como validar semântica (viés de confirmação); (b) abandonar resultado validado sem prova numérica; (c) mapear termo-de-domínio→coluna por inferência, não por confirmação. **Nenhuma elicitação previne isto** — é gap de qa-critic/disciplina de execução.

**[MECANISMO]**
- **Gate de ambiguidade de campo-fonte** no qa-critic: quando existem colunas-irmãs (`Variação Interna` / `Manual` / `Total`), o mapeamento termo→coluna é **decisão registrada do dono**, não inferência. O qa-critic reprova PASS se um campo-fonte com nome ambíguo foi mapeado sem confirmação explícita na spec.
- **Anti-viés-de-oráculo (regra de turno único, ADR-018):** antes de aceitar que bateu o oráculo, o crítico **deve** responder por escrito: *"que outra interpretação de campo produziria este mesmo número?"* — bater valor ≠ validar semântica.
- **Anti-over-correção:** abandonar um resultado já validado exige **prova numérica** de que o anterior estava errado, registrada no diff. Reverter por rótulo/palavra = REPROVADO.

**[CANÁRIO]** `test_oracle_bias.py`: cenário com duas colunas que batem números próximos ao alvo; o gate DEVE exigir registro de qual é a referência e por quê. (Mecaniza a *exigência de registro*; o julgamento semântico permanece adversarial — declarado em `LIMITS.md`.)

**[DONE quando]** regras no `qa-critic/SKILL.md` com critério binário + canário do registro-obrigatório no CI. **[ADR]** `035-anti-vies-oraculo-estabilidade-decisao.md`.

---

## 4. ⭐ "Teste pela porta do usuário" + verificação de ambiente limpo

**Origem:** `[AIVI]` (`run_aivi.py` quebra com `KeyboardInterrupt` no PowerShell; `requirements` nunca instalado em ambiente limpo).

**[GAP]** O entry-point nunca foi executado como o usuário o executaria (`input()` bloqueante → quebra sem TTY). Os `requirements` "funcionaram" só porque as libs já estavam no ambiente — nunca testado limpo.

**[MECANISMO]**
- **qa-critic — execução pela porta do usuário:** o gate de entrega de software roda o entry-point **sem TTY** (stdin fechado / não-interativo). `input()` bloqueante como única via = REPROVAR. Mecanizável: `subprocess` com `stdin=DEVNULL` e timeout; se travar/quebrar → FAIL.
- **Verificação de ambiente limpo:** `pip install -r requirements.txt` em venv descartável faz parte do "pronto". `tools/check_clean_env.py` cria venv, instala, importa os módulos top-level; falha = entrega não-pronta.

**[CANÁRIO]** `test_entrypoint_no_tty.py` (entry-point com `input()` sem fallback → FAIL; com `argv`/flag não-interativa → PASS); `test_clean_env.py` (requirements que não resolvem → FAIL).

**[DONE quando]** ambos no gate de entrega de software (app `exemplos/dominio-software`, ADR-023). **[ADR]** `036-teste-porta-do-usuario-e-ambiente-limpo.md`.

---

## 5. ⭐ Action-safety em overwrite de artefato não-criado-na-sessão

**Origem:** `[AIVI]` (item #13 — agente sobrescreveu `RELATO-FRAMEWORK-autorrevisao.md`, que já tinha conteúdo, sem ler nem avisar).

**[GAP]** `action-safety` classifica por efeito mas o effect-gate só inspeciona Bash/PowerShell. Overwrite via tool `Write`/`Edit` sobre arquivo **com conteúdo anterior não-criado nesta sessão** é efeito destrutivo (E1) que passou.

**[MECANISMO]** Hook `PreToolUse` para `Write`/`Edit`: se o path existe, tem conteúdo, e **não está no manifesto de arquivos criados nesta sessão** (`.agent/brain/session-files.json`) → exigir `ask` (ler + avisar antes de sobrescrever). Liga ao bug GitHub #37210 (deny pode ser ignorado p/ Edit/MCP) → usar `exit 2` para esses tools, não `permissionDecision:deny`.

**[CANÁRIO]** `test_overwrite_guard.py`: Write sobre arquivo pré-existente fora do manifesto → `ask`/bloqueio; Write sobre arquivo criado na sessão → allow; Write de arquivo novo → allow.

**[DONE quando]** hook no CI + paridade `.sh`/`.ps1` (item 8). **[ADR]** `037-action-safety-overwrite-non-session.md`.

---

## 6. ⭐ Telemetria exposta + `execution-report` automático

**Origem:** `[AIVI]` (meta-gap nº 1: tokens/custo/tempo NÃO MEDIDOS; placar "quem pegou o quê" só existiu porque o dono cobrou).

**[GAP]** Sem trilha de consumo por sessão não há accountability (crítico em regulado), nem controle de custo (os vários retrabalhos do AIVI teriam custo acionável), nem aprendizado de processo (cada lição dependeu do dono cobrar).

**[MECANISMO]**
- **`execution-report` automático** no encerramento (docops / `consistency-gate`, ADR-030): emite tokens (quando a telemetria expuser; senão literalmente `NÃO MEDIDO` — anti-fabricação), wall-clock, nº de turnos, arquivos tocados, testes, **rodadas de retrabalho**, e o **placar gate × achado** ("quem pegou o quê").
- **Expor telemetria de token ao agente** como ferramenta é pré-requisito de governança — registrado como dependência externa (não-mecanizável pelo framework sozinho; vai a `LIMITS.md` enquanto o host não expuser).

**[CANÁRIO]** `test_execution_report.py`: encerramento sem report gerado → FAIL; report com número de token fabricado quando a telemetria está ausente → FAIL (deve dizer `NÃO MEDIDO`).

**[DONE quando]** report auto-gerado em todo encerramento de bloco. **[ADR]** `038-execution-report-telemetria.md` (estende ADR-026).

---

## 7. Effect-gate: de backstop de 5 padrões para cobertura de classe de efeito

**Origem:** `[CRÍTICA]`.

**[GAP]** ~5 padrões grep (rm-raiz, mkfs/dd, push-force, fork-bomb, firewall-off). `find -delete`, `shred`, `truncate`, `>` sobre path crítico, `git reset --hard`+`clean -fdx`, `curl|bash` passam.

**[MECANISMO]** Refatorar para motor de regras por efeito carregado de `tools/effect-rules.json` (padrão→tier→efeito→deny/ask/allow); o `.json` é a política, o hook é o interpretador. Famílias novas: destruição em massa, reescrita de histórico, escalada/persistência, exfiltração. Manter default-allow (backstop, não classificador), com `ask` para T2 ambíguo.

**[CANÁRIO]** estender `test_effect_gate.py`: ≥2 deny + ≥2 benignos por família + fuzzing de flag/aspas/espaço (a lição dos bypasses `rm -r -f`).

**[DONE quando]** 4 famílias com anti-falso-positivo, paridade nos 3 SOs (item 8) → reclassificar OWASP LLM06 🟡→🟢. **[ADR]** `039-effect-gate-motor-por-efeito.md`.

---

## 8. Paridade cross-platform real (não `[DESCONHECIDO]`)

**Origem:** `[CRÍTICA]` + backlog `D4`.

**[GAP]** Toda a cadeia de hooks nasceu PowerShell-only; os `.sh` são paridade declarada não-validada (headers `[DESCONHECIDO]`). Limita o teto regulado (farma valida em Linux herda gate não-testado).

**[MECANISMO]** Matriz CI `ubuntu + macos + windows` com `pwsh`, rodando toda a suíte de canários; `test_parity.py` exige veredito idêntico `.sh`↔`.ps1` por payload.

**[DONE quando]** 3 SOs verdes + paridade 100% → só então remover `[DESCONHECIDO]` dos headers e atualizar a matriz de ambiente do README. **[ADR]** `040-paridade-cross-platform-ci.md`.

---

## 9. Sicofância como dimensão de teste de 1ª classe

**Origem:** `[GEMINI]` (contribuição válida) + `[AIVI]` (o agente *concordou consigo* ao validar a coluna errada por bater o alvo — viés de auto-aprovação).

**[GAP]** O QA heterogêneo (ADR-018) existe como processo, mas não há **teste que prove que o crítico discorda quando deve**. Sicofância = falha de limite entre alinhamento social e integridade epistêmica.

**[MECANISMO]** `tools/test_sycophancy.py` — canário adversarial: alimenta o qa-critic com uma "entrega" que bate o número-alvo **mas tem erro semântico plantado** (espelha o caso AIVI da coluna). O gate DEVE reprovar. Se aprovar (concordou com o resultado bonito), FAIL. Liga ao item 3 (anti-viés-de-oráculo) e ao protocolo steelman→ataque→veredito (ADR-018).

**[DONE quando]** canário no CI; heterogeneidade gerador↔crítico documentada com o teste que a prova. **[ADR]** `041-sicofancia-canario-adversarial.md`.

> **Limite declarado:** o canário prova que o gate reprova *o erro plantado conhecido*. Não prova ausência de sicofância em casos novos — isso é não-mecanizável e vai a `LIMITS.md`.

---

## 10. Discovery: sair de DESIGN-TIME (provar a senioridade declarada)

**Origem:** `[CRÍTICA]` + backlog `D3`.

**[GAP]** Os evals dos papéis `discovery` (G) e *mapeamento de processo* (H) estão **NÃO EXECUTADOS** (colunas "—", status ⏳). A senioridade central é promessa não medida.

**[MECANISMO]** Executar de fato G e H (preencher "Roteou para", iterar `description` até convergir, como foi feito para A–F que chegou a 33/33). Eval funcional ponta-a-ponta do discovery contra ≥3 briefings reais, medindo se cobre as dimensões do item 1. Registrar em `_meta/eval-results-discovery.md`.

**[DONE quando]** G e H **EXECUTADO** (não design-time). **[ADR]** `042-discovery-eval-executado.md`.

---

## 11. Abrangência regulada + catálogo clonável (sem quebrar agnosticismo)

**Origem:** `[CRÍTICA]` + `[GEMINI]` (ambientes regulados/críticos).

**[GAP]** `agnostic-denylist.txt` é seed de ~12 normas, não-exaustiva (ITIL/COBIT/SOX/ISO-13485 passam). E o `high-stakes-gate` delega 100% da norma ao discovery, sem catálogo de partida.

**[MECANISMO]**
- **Núcleo (agnóstico):** expandir a denylist (SOX, ISO-13485/27001, COBIT, ITIL, Basel, SOC 2, NIST, CLIA) + `check_regulatory_coverage.py` que avisa o que falta. Mantém o aviso "não-exaustiva".
- **Fora do núcleo (opt-in):** `exemplos/dominio-regulado/` com perfis de conformidade clonáveis (`compliance-profile.json`: campos de audit, HITL suficiente, retenção, assinatura eletrônica). O discovery oferece o perfil quando a dimensão "regulado?" = sim. O AIVI/Vibra (indicador que alimenta MEREO, vai a decisão executiva) é exatamente o caso que ativaria isso.

**[DONE quando]** denylist expandida + ≥3 perfis + `check_core_agnostic` ainda verde. **[ADR]** `043-catalogo-perfis-regulados.md`.

---

## 12. Reconciliação de fontes — o que da revisão Gemini foi DESCARTADO e por quê

O framework exige (anti-alucinação P1) que se sinalize divergência de fontes em vez de engolir. Confrontado com os arquivos reais clonados, **a maior parte da fundação do documento Gemini não descreve este repositório:**

| Afirmação Gemini | Veredito | Motivo |
|---|---|---|
| Base em Education Endowment Foundation, "Modelo de 7 Passos", Metacognitive Teaching Framework, Teaching Quality Index, Protégé Effect, "Cognitive Mirror / teachable novice" | **DESCARTADO** `[INFERIDO]` | `guia/REFERENCIAS.md` declara Anthropic + padrões abertos (SemVer/ADR/OWASP/OTel) + pesquisas A0–A3. **Nenhuma** fonte pedagógica cognitiva consta no repo. |
| Pentaho, PostgreSQL, oci-cli/AWS/Azure CLI, "governança de datacenter" | **DESCARTADO** | Não constam no repo. Provável contaminação com outros projetos do autor ou alucinação de escopo. |
| "Universal prompt engineering framework for critical AI validation" | **DESCARTADO** | Descrição real: "Framework Metacognitivo Agêntico — distribuição pública". |
| Sicofância como falha de 1ª classe | **ADOTADO** → item 9 | Sobrevive independente da fundação errada; reforçado pelo AIVI. |
| Language-hooks como "fatos computacionais, não pesos" | **ADOTADO** → princípio reitor + itens 5/7 | Articula bem o critério de aceite "ferramenta, não prosa". |
| Discovery → spec executável (BPMN/YAML/parametrizável) | **ADOTADO PARCIAL** → item 1 | Adotada a ideia de spec executável; **não** a stack BPMN/CoRE específica (não está no repo). |

> Tratar a fundação pedagógica do Gemini como base do plano violaria o P1. As 3 contribuições adotadas valem por si; o resto fica registrado como descartado, com a razão — procedência auditável.

---

## 13. `LIMITS.md` mecanizado + marketing ancorado em evidência

**Origem:** `[CRÍTICA]` (transparência dispersa) + decisão do dono (marketing honesto).

**[MECANISMO]**
- `tools/build_limits.py` gera o `LIMITS.md` a partir do estado real dos canários: verde→**garante** (link pro teste); ausente→**não provado**; `[EMERGENTE]`/`[DESCONHECIDO]`→**em desenvolvimento**. CI falha se `LIMITS.md` divergir dos testes — **não pode mentir.**
- Site/README/PITCH: cada claim recebe selo ✅ **PROVADO** (link canário) · 🟡 **PARCIAL** · ⏳ **EM DESENVOLVIMENTO**. `tools/test_marketing_claims.py` falha o build se houver ✅ sem canário verde. Trocar "pronto para regulado" por "andaime de conformidade" onde não há prova de campo.
- Tabela "o que entrega hoje" no topo, gerada do `LIMITS.md`. Seção "o que NÃO fazemos".

**[DONE quando]** `LIMITS.md` em sync com CI, linkado no topo; zero claim ✅ órfão. **[ADR]** `044-limits-e-marketing-ancorado.md`.

---

## 14. Sequência de execução (incremental, AIVI-first)

A ordem prioriza a evidência de campo (AIVI) e respeita dependências.

| Marco | Item | Origem | Destrava |
|---|---|---|---|
| **v1.23.0** | 8 — CI cross-platform + paridade | CRÍTICA | provar todo o resto nos 3 SOs |
| **v1.24.0** | **1 — elicitação-consultiva + linter de spec** | **AIVI** | o maior gap de campo |
| **v1.25.0** | **2 — completude vs pedido** · **4 — porta do usuário + ambiente limpo** | **AIVI** | entrega vira produto, não script |
| **v1.26.0** | **3 — anti-viés-oráculo** · **9 — sicofância** | AIVI+GEMINI | estabilidade de decisão |
| **v1.27.0** | **5 — overwrite guard** · **6 — execution-report** | **AIVI** | segurança de escrita + governança |
| **v1.28.0** | 7 — effect-gate motor por efeito | CRÍTICA | OWASP LLM06 🟢 |
| **v1.29.0** | 10 — discovery eval executado | CRÍTICA | senioridade provada |
| **v1.30.0** | 11 — catálogo regulado | CRÍTICA+GEMINI | abrangência |
| **v1.31.0** | 13 — LIMITS + marketing ancorado | CRÍTICA+dono | honestidade mecanizada |

> Cross-platform primeiro (destrava prova de tudo). Elicitação logo em seguida (maior gap de campo). LIMITS por último (só dá pra gerar honestidade ancorada depois que os canários existem).

---

## 15. Critério binário único — "esta revisão não reapresenta os gaps"

Todas verdadeiras (binário):

1. `pytest` verde nos **3 SOs** + paridade `.sh`↔`.ps1` 100%.
2. **`check_spec_depth.py` barra J2** se a spec não cobrir as dimensões agnósticas de elicitação; banco no `_shared/` passa no `check_core_agnostic`.
3. **`check_completeness.py`** reprova entrega que cobre subconjunto do pedido.
4. **Anti-viés-de-oráculo** com registro obrigatório de mapeamento campo-fonte; **`test_sycophancy.py`** reprova erro semântico que bate o alvo.
5. **Entry-point testado sem TTY** + **ambiente limpo verificado** no gate de software.
6. **Overwrite guard** barra escrita sobre artefato não-criado-na-sessão.
7. **`execution-report` auto-gerado** em todo encerramento, com placar gate×achado; token = `NÃO MEDIDO` quando ausente (nunca fabricado).
8. **effect-gate** cobre 4 famílias de efeito; OWASP só vira 🟢 com canário.
9. **discovery G/H EXECUTADO** (não design-time).
10. **`LIMITS.md` gerado do CI**, em sync, linkado; zero claim ✅ órfão.

> **Preservar a força (não mexer):** método sênior (decompor→classificar→validar→refletir), governança SemVer+ADR+changelog-ligado-à-pesquisa, régua §0 anti-inflação, QA bicelular adversarial heterogêneo, file-first, anti-fabricação, e a **transparência** — que esta revisão **mecaniza** (via `LIMITS.md` e selos de marketing) em vez de substituir por promessa.

---

## 16. Mapa final: cada gap → seu balde correto (anti-"joga tudo no discovery")

| Gap de campo (AIVI) | Balde correto | Item |
|---|---|---|
| Produto não elicitado (GUI/operador/escopo/persistência/log) | **discovery-consultivo** | 1 |
| Calculou subconjunto do pedido | qa-critic / completude | 2 |
| Viés de oráculo + over-correção sem prova | **qa-critic / execução** | 3 |
| Entry-point quebra no terminal | qa-critic / porta do usuário | 4 |
| Requirements não testados em ambiente limpo | qa-critic / ambiente | 4 |
| Overwrite de relato sem avisar | **action-safety** | 5 |
| Tokens/custo/placar não medidos | telemetria / execution-report | 6 |
| Sicofância (aprovou número bonito) | qa-critic adversarial | 9 |

> A lição estrutural do AIVI: **nem tudo é discovery.** Elicitação resolve o que dá para antecipar *antes* de codar; o resto é disciplina de execução, segurança de ação e governança — cada um no seu mecanismo. Empurrar tudo para "discovery melhor" faria os erros de execução reaparecerem.

---

*Plano consolidado v2. Consumir via `discovery → architect/ADR → developer → qa-critic → docops`. Ferramental (linter/hook/teste) é a base de cada item; prosa só onde não-mecanizável, e então declarada em `LIMITS.md`. Nada em produção sem eval executado. CC BY 4.0.*
