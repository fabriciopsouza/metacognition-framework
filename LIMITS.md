# LIMITS.md — o que o framework GARANTE, prova, e o que NÃO faz (gerado por tools/build_limits.py, ADR-044)

> **Honestidade mecanizada.** Cada linha tem status derivado do **canário** que a prova (verde na matriz CI = PROVADO; ausente = EM DESENVOLVIMENTO). O `build_limits.py --check` falha o CI se este arquivo divergir dos canários — **o doc não pode mentir**. `PROVADO` = há canário e a suíte roda verde no CI (ADR-040). NÃO confunda com certificação.

## O que entrega hoje
| Capacidade | Status | Canário (prova) | Mecanizado | NÃO-mecanizado (limite) | ADR |
|---|---|---|---|---|---|
| Elicitação cobre as dimensões de produto antes de codar | ✅ PROVADO | `tools/test_spec_depth.py` | cobertura de dimensão (gate barra J1) | qualidade sênior do default (adversarial) | ADR-033 |
| Entrega cobre cada quantificador do pedido | ✅ PROVADO | `tools/test_completeness.py` | quantificadores do lexicon vs validation | quantificador fora do lexicon | ADR-034 |
| Mapeamento de campo-fonte é decisão registrada | ✅ PROVADO | `tools/test_oracle_bias.py` | exigência de registro (confirmação+justificativa) | correção semântica do mapeamento | ADR-035 |
| Gate reprova número-alvo com erro plantado (anti-sicofância) | ✅ PROVADO | `tools/test_sycophancy.py` | catch do erro plantado conhecido | sicofância em caso novo (adversarial) | ADR-041 |
| Entry-point roda pela porta do usuário (sem TTY) | ✅ PROVADO | `tools/test_entrypoint_no_tty.py` | input() bloqueante = FAIL | — | ADR-036 |
| Requirements instalam em ambiente limpo | ✅ PROVADO | `tools/test_clean_env.py` | resolução offline (--dry-run --no-index) | venv real depende de rede/PyPI | ADR-036 |
| Não sobrescreve artefato não-lido/não-criado na sessão | ✅ PROVADO | `tools/test_overwrite_guard.py` | bloqueio (exit 2) de overwrite cego | paridade .sh provada só na matriz CI | ADR-037 |
| Execution-report auto + token honesto | ✅ PROVADO | `tools/test_execution_report.py` | report+placar+anti-fabricação (NÃO MEDIDO) | telemetria de token real-time (dep. do host) | ADR-038 |
| Backstop por efeito (4+ famílias) com anti-falso-positivo | ✅ PROVADO | `tools/test_effect_gate.py` | deny T3 / ask T2 por família | OWASP LLM06 🟢 só após matriz CI 3 SOs + paridade 100% | ADR-039 |
| Paridade de veredito .ps1 ↔ .sh | ✅ PROVADO | `tools/test_parity.py` | decisão idêntica (provada na matriz CI) | SKIP local sem jq — prova é no CI | ADR-040 |
| Discovery cobre dimensões (eval EXECUTADO, não design-time) | ✅ PROVADO | `tools/test_discovery_eval.py` | cobertura + discriminação raso×sênior | qualidade sênior do default | ADR-042 |
| Cobertura regulada da denylist | ✅ PROVADO | `tools/test_regulatory_coverage.py` | famílias conhecidas têm representante | denylist NÃO-EXAUSTIVA por design | ADR-043 |
| Auto-detecção + validação de arquivos de entrada (dicionário-contrato) | ✅ PROVADO | `tools/test_input_contract.py` | arquivos detectados na pasta + colunas obrigatórias validadas | mapeamento semântico correto (qa-critic) | ADR-046 |
| Pesquisa de contexto + verificação de âncora antes de codar (sob stake) | ✅ PROVADO | `tools/test_context_brief.py` | context-brief presente + tabela de âncora (gate barra J1 sob sinal de stake) ou exceção consciente | qualidade/correção da pesquisa (adversarial); sinais não-exaustivos | ADR-051 |
| Modo non-admin inicia sob restrição de scripts (gates anunciados) | ✅ PROVADO | `tools/test_nonadmin.py` | settings sem hooks + doutrina + bootstrap.py (sem PowerShell) | enforcement anunciado depende do agente (não hook) | ADR-047 |
| 3 distribuições de fonte única (premium/baseline) — core do discovery preservado | ✅ PROVADO | `tools/test_premium_tier.py` (interno¹) | premium marcado e stripável; core intacto no baseline | feature premium nova precisa ser marcada (senão vaza) | ADR-049 |
| Núcleo sem termo de domínio/cliente | ✅ PROVADO | `tools/test_core_agnostic.py` (interno¹) | tier norma + tier sensível (export) | vazamento semântico novo (qa-critic é o backstop) | ADR-020 |
| Entrega navegável: índice guiado, auto-verificado (sem link órfão/pro vazio) | ✅ PROVADO | `tools/test_make_index.py` | html+txt, ordem de leitura, lista só o que existe, resumo anti-fabricação | estética do índice (não medida) | ADR-050 |
| Vitrine honesta: sem overclaim + anti-drift de versão/link + prompt web fail-closed | ✅ PROVADO | `tools/test_marketing_claims.py` | léxico absoluto-sem-hedge na vitrine; prompt web derivado de PUBLIC_SRC (fail-closed); versão/link da vitrine == main; disclosure de alucinação residual (proximidade) | paráfrase de overclaim (léxico não-exaustivo, anti-FP > recall); qa-critic é o backstop | ADR-059 |
| Corpus público de aprendizado anonimizado (learnings) com fail-closed + opt-in | ✅ PROVADO | `tools/test_execution_report.py` | anonymize + gate sensitive-denylist (recusa se map/denylist ausente, regex inválida ou token sobrevive) + consent opt-in no CLI | anonimização por regex NÃO-exaustiva: token fora do map E da denylist passa — revisão humana antes do push | ADR-062 |

> ¹ **canário interno**: roda na fonte e no CI, mas é **removido da distribuição pública** (reconstrói fragmentos de token de cliente para testar o linter sensível — não pode ser publicado). O status PROVADO reflete a fonte/CI; no pacote público o arquivo não existe **por design**.

## O que NÃO fazemos (anti-overclaim)
- **Não certificamos conformidade.** Os perfis de `exemplos/dominio-regulado/` são **andaime de partida**, não auditoria — a adequação à norma concreta é do dono + revisão humana (HITL).
- **Não medimos tokens em tempo real** sem telemetria exposta pelo host — nesse caso o execution-report diz literalmente `NÃO MEDIDO` (nunca fabricamos número).
- **Não garantimos ausência de viés/sicofância em casos novos** — provamos o catch do erro plantado conhecido; o resto é o protocolo adversarial do qa-critic (ADR-018).
- **Não prometemos detecção exaustiva** de normas (denylist não-exaustiva) nem de comandos destrutivos (effect-gate é backstop conservador, não classificador completo).
- **Não substituímos o gate humano** em decisão irreversível/regulada (high-stakes-gate).
- **Não geramos documentos com polimento visual** (gráficos, branding, capa formatada): a geração automatizada (`gen_exec_doc`, premium) produz a **estrutura correta** e pagina o conteúdo — formatação fina é manual ou ADR futuro (ADR-050 §limite).

> Gerado de `tools/build_limits.py`. Para atualizar: adicione o canário e rode o gerador; não edite à mão (o `--check` reprova divergência).
