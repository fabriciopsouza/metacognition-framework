# ADR 095 — Carimbo de PROCEDÊNCIA em trabalho executado FORA do repositório

- Status: **Aceito** (2026-07-22 — pedido do dono: *"indique em um arquivo o nome do repo/sessão/framework que está tratando, número chamado, etc; insira esta prática"*) · Decisores: dono + squad (architect) · pré-gate: qa-critic heterogêneo
- Tipo: **EMENDA ADITIVA** — estende `_shared/traceability` (Regra 7) e `tools/handoff.py` (ADR-076). NÃO cria ferramenta nova, NÃO cria hook, NÃO toca desenho aprovado.
- Relaciona: ADR-076 (gerador determinístico de handoff — reusado), ADR-070 (write-isolation), ADR-091 (núcleo product-free / proveniência só nos ADRs), ADR-007 (régua §0), ADR-012/053 (handoff cross-sessão).

## Contexto — onde a rastreabilidade quebrava

`_shared/traceability` Regra 4 exige a cadeia **decisão → fonte → versão**, e em ambiente regulado declara essa cadeia como *parte do entregável*. O mecanismo existente (`handoff.py`, ADR-076) cobre o handoff **cross-sessão dentro do repo**.

**O elo que faltava:** quando o trabalho é executado num diretório **externo** ao repositório — drive corporativo sincronizado, pasta de cliente, share de rede, pasta de demanda/chamado — os artefatos saem do alcance do git e a cadeia se rompe no ponto da entrega. Quem abre a pasta meses depois não sabe:

- qual framework/versão/commit/sessão produziu aquilo;
- quais modelos atuaram em quais papéis (e se houve revisor distinto do autor — ADR-018);
- **o que ali é minuta e o que é registro.**

**Caso de campo (2026-07-22, sessão `5b7dbb8d`):** bloco executado numa pasta de chamado em drive corporativo sincronizado, ambiente farmacêutico regulado. Foram produzidas minutas de dossiê de validação, uma proposta de código não compilada e um ADR não ratificado, ao lado de material migrado de ciclos anteriores e de documentos oficiais do cliente. Sem carimbo, um leitor externo não distingue insumo de evidência — e **minuta lida como registro é achado de auditoria**. A pasta continha, ela mesma, o precedente do risco: um rollback anterior mal rastreado que destruiu o código funcional.

## Decisão (1 frase ativa)

Quando o diretório de trabalho é **EXTERNO ao repositório**, essa pasta recebe um **`PROCEDENCIA.md`** antes de o bloco fechar, gerado por **`tools/handoff.py --provenance <dir> --write`** — com os campos do repo **determinísticos** e os campos de domínio como **SLOT explícito**.

## Mecanismo (estende o que existe — régua §0)

1. **`tools/handoff.py --provenance DIR [--write]`** — reusa `repo_state()` (versão do CHANGELOG, commit, branch, origin, não-commitado/não-pushado) e o timestamp determinístico do commit HEAD, já existentes para o Pacote P14. Sem tool nova, sem dependência nova, coberto pelo canário `tools/test_handoff.py` que já existia.
2. **Recusa alvo dentro do repo** (exit 2): lá a procedência é o próprio git; o carimbo seria ruído.
3. **Não sobrescreve carimbo existente** — apenda seção de sessão (`_shared/traceability` Regra 3, preservação).
4. **SLOT explícito para o domínio:** demanda, sistema/objeto, origem do material migrado, modelos por papel, status por artefato (MINUTA / PROPOSTA / MIGRADO / APROVADO), o que o material NÃO é, bloqueio e decisões pendentes. **Slot vazio é lacuna VISÍVEL, não silêncio** — é o mesmo princípio do `check_context_brief` (presença/estrutura, não qualidade).
5. **`_shared/traceability` Regra 7** (SSoT) + **`.agent/rules/05-procedencia-trabalho-externo.md`** (ponteiro fino, padrão das demais rules).

## Agnosticismo — o gatilho é a FORMA, não o cliente

O gatilho é **"o destino de escrita está fora do repo"**, nunca o nome de um cliente, produto ou ferramenta de sincronização. Isso não é apenas conformidade com o canário `core-no-vendor` (ADR-091: *proveniência só nos ADRs*) — é engenharia melhor: a regra vale para qualquer pasta externa, e o caso concreto vira **instância**, não exceção.

> **Instância que originou esta ADR (proveniência permitida aqui, e só aqui):** chamados de melhoria SAP tratados a partir de pastas de projeto em drive corporativo sincronizado (SharePoint) de um cliente do setor farmacêutico. A especialização de domínio — convenção de numeração de chamado, estrutura de pastas do dossiê, normas setoriais aplicáveis — vive na **aplicação**, fora do núcleo (`exemplos/README.md`, ADR-023/010).

## Alternativas consideradas

1. **Ferramenta nova dedicada (`tools/provenance.py`).** REJEITADA pela régua §0: adição pura, com canário próprio a manter, duplicando `repo_state()` que já existe em `handoff.py`.
2. **Estender `check_context_brief.py`.** REJEITADA: aquele gate trata **verificação de âncora de pesquisa** (vigência/pertinência de norma citada). Conflar procedência de entrega com pesquisa de contexto degradaria os dois.
3. **Só template markdown + regra em prosa, preenchido à mão.** REJEITADA: é exatamente o "Gap 8 — handoff improviso" que o ADR-076 já diagnosticou. Prosa a preencher de memória não sobrevive à pressa; os campos que o repo sabe devem ser determinísticos.
4. **Hook fail-closed barrando o fim do bloco sem carimbo.** REJEITADA por ora: o destino é externo ao repo e o hook não tem como saber, de forma confiável, que houve escrita fora. Fica como escalada disponível se a regra não pegar na prática.
5. **Carimbo por `--provenance`, reusando `handoff.py` (ESCOLHIDA).** Custo marginal, cobertura de canário herdada, agnóstico por construção.

## Consequências

**Positivas:** a cadeia decisão→fonte→versão passa a sobreviver à saída do repo; o status por artefato (MINUTA/PROPOSTA/MIGRADO/APROVADO) fica explícito no destino, onde o leitor está; o registro de modelo-por-papel torna auditável a heterogeneidade autor≠revisor (ADR-018); write-isolation (ADR-070) fica declarado no próprio artefato externo.

**Negativas / limite honesto:** o carimbo **não é forçado por mecanismo** — nenhum hook observa escrita fora do repo, então a Regra 7 depende de o agente segui-la (mesmo teto declarado no ADR-094). Os slots de domínio dependem de preenchimento correto: um slot preenchido com informação errada é pior que um slot vazio, e nenhum canário verifica isso — é julgamento, e cai no qa-critic. O gerador lê o estado do repo **no momento do carimbo**; se o repo mudar depois, o carimbo não se atualiza sozinho (por isso a instrução de apendar seção por sessão).

## Implementação

- `tools/handoff.py`: funções `provenance()` + `emit_provenance()`, flag `--provenance DIR`.
- `tools/test_handoff.py`: canário do modo procedência (recusa dentro do repo, campos determinísticos presentes, slots presentes).
- `_shared/traceability/SKILL.md`: **Regra 7**.
- `.agent/rules/05-procedencia-trabalho-externo.md`: ponteiro fino.
- `capabilities.json`: registro `external-work-provenance`.
