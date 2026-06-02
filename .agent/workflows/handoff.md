# /handoff <papel> — Transição entre papéis (genérico)

## O papel atual entrega
Artefato · classificação CONFIRMADO|INFERIDO|DESCONHECIDO · fontes consultadas ·
próximos passos · escalações.

## O recebedor faz
1. Confirmar recebimento. 2. Reler briefing + glossário. 3. Aceitar ou rejeitar
com motivo específico. 4. Prosseguir conforme sua skill.

## Papéis válidos
pmo | architect | developer | qa-critic | docops | explorer
(+ qualquer aplicação de domínio que sua equipe tenha criado clonando `_template`)

## Junções binárias forward-only (ADR-011 / Princípio 13 v1.12.0)

`/handoff` opera dentro de **arquitetura bicelular de QA**: 6 junções (J0-J5) com **gates binários declarados** + **process-critic adversarial final** com rewind cascata. DENTRO da junção: iterações até PASS (binário). ENTRE junções: forward-only (circuit-breaker contra loop eterno). TODO QA é adversarial.

### Gates obrigatórios por junção

| # | Junção | Artefato-gate | Critério binário | Quem aplica |
|---|---|---|---|---|
| **J0** | PMO → discovery | STATUS-line PMO + (opcional) UMA pergunta de desambiguação | natureza nomeada + dimensão escolhida + ambiguidade resolvida (Sim/Não) | PMO adversarial |
| **J1** | discovery → architect | `requirements.md` OU `research-brief.md` | requisitos classificados + critério de aceite binário + (se reforço sênior) §7+§8+§7.1 ADR-009/010 preenchidas + **(produto recorrente) `check_spec_depth.py` PASS — dimensões de elicitação decididas (ADR-033)** + **(sob sinal de stake) `check_context_brief.py` PASS — context-brief com verificação de âncora, ou exceção consciente (ADR-051)** | PMO adversarial |
| **J2** | architect → developer | ADR `Status: Aceito` | Aceito + ponteiro + alternativas + consequências | PMO adversarial |
| **J3** | developer → qa-critic | commits + diff + testes (se aplicável) | cobre TODOS REQ + sem regressão + RRC self-applied (ADR-010 §ii) | PMO adversarial |
| **J4** | qa-critic → docops | resultado adversarial subagente | `APROVADO_LIMPO` (não `_COM_RESSALVAS` nem `REPROVADO`) | qa-critic subagente isolado |
| **J5** | docops → release | `validation.md` do release | TODOS V1-Vn = PASSA | PMO + dono (revisão humana) |
| **PC** | **process-critic FINAL** | revisão adversarial do bloco completo | LIMPO → merge/tag; ELSE → rewind cascata J_i + iterações até re-PASS | qa-critic subagente isolado (mesma instância expandida em escopo) |
| **J6** | **PMO re-orquestração de bloco** (ADR-045) | `RE-ORQUESTRAÇÃO:` no `history.md` | após PC `APROVADO_LIMPO`, PMO registra **1** decisão: `prosseguir \| re-priorizar X \| rewind J_i \| injetar escopo Y \| reativar estágio Z` (`tools/check_reorchestration.py`) | PMO (maestro) |

### Invariantes operacionais (ADR-011)

- **Binário-com-iterações DENTRO da junção:** autor itera até gate PASS (emenda no mesmo artefato via STATUS-field; rounds N-1, N, N+1 não criam novos artefatos).
- **Forward-only ENTRE junções:** uma vez gate PASS, junção não volta no fluxo normal. **Sem essa cláusula, oscilação entre junções não-finais = loop eterno.**
- **Process-critic dispara em:** (a) final de cada BLOCO APROVADO (release, ADR aceito, spec fechada, feature delivered) — mandatório; (b) on-demand do dono; (c) opcional em `/checkpoint` substantivo como backstop.
- **J6 — PMO maestro na FRONTEIRA DE BLOCO (ADR-045), NÃO por gate:** após o PC emitir `APROVADO_LIMPO`, o controle volta ao **PMO** para UMA decisão de re-orquestração registrada no `history.md` (`RE-ORQUESTRAÇÃO: ...`). **Voltar ao PMO a cada gate é REJEITADO** (custo+loop+gargalo, ADR-045): o intra-bloco segue **forward-only** (circuit-breaker preservado). J6 é onde o fluxo pode re-priorizar/reativar/injetar escopo entre blocos — de forma bounded e auditável.
- **Rewind cascata default:** process-critic manda de volta a J_i → todos agentes downstream (J_i → J_5) re-rodam. Cirúrgico fica pendente (v1.13.0) para casos onde cascata se mostrar custosa.
- **SUPLANTA × EMENDA pós-rewind:** §Decisão/§Alternativas muda → SUPLANTA novo ADR + `Substituído por:` no antigo. §Implementação/§Consequências muda → EMENDA in-place via STATUS-field. Within-junction rounds = EMENDA (não conta como rewind).

### Antes de invocar `/handoff B`

Autor (papel A) declara explicitamente:
```
/handoff <B> — junção <J_n> PASS
artefato-gate: <link/path>
critério binário: [PASSA] — <evidência objetiva>
```

Se autor não declarar PASS, ou se PMO adversarial bouncer → autor itera mesma junção até PASS. **Não há atalho.**
