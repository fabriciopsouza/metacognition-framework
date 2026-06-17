# Análise do ecossistema BMAD — escopo, mecanismo de enforcement e brainstorming (com fontes)

> **Por que este doc existe:** o ADR-081 (integração seletiva BMAD, 2026-06-16) concluiu "o que integrar"
> analisando **apenas o repo core `BMAD-METHOD`** e **sem registrar fonte** (URL/data/versão). O dono pediu
> (1) certeza sobre quantos repos foram olhados (1 vs todos) e (2) sourcing nas docs "como já devemos fazer".
> Este doc fecha esse furo de rastreabilidade. **Classificação epistêmica aplicada por afirmação.**

## Fontes (acesso 2026-06-16/17, via WebFetch)

| # | Fonte | URL | O que forneceu |
|---|---|---|---|
| F1 | Org `bmad-code-org` — lista de repositórios | https://github.com/orgs/bmad-code-org/repositories | inventário dos 13 repos [CONFIRMADO] |
| F2 | Core `BMAD-METHOD` (README) | https://github.com/bmad-code-org/BMAD-METHOD | install `npx bmad-method install`; 12+ agentes, 34+ workflows; v6.8.0 (25/05/2026) [CONFIRMADO] |
| F3 | `bmad-module-creative-intelligence-suite` (README) | https://github.com/bmad-code-org/bmad-module-creative-intelligence-suite | brainstorming real (CIS); v0.2.1 (17/05/2026) [CONFIRMADO] |
| F4 | ADR-081 (nosso) | docs/adr/081-integracao-bmad-elicitation-edge-case-party-readiness.md | escopo da análise anterior (1 repo) [CONFIRMADO] |

> **Limite declarado:** o WebFetch intermedia a leitura por um modelo pequeno — fatos de alto risco (sintaxe exata
> de comando, contagem precisa de técnicas) ficam **MÉDIA confiança**; o que é estrutural/estável é ALTA.
> `docs/.../core-architecture.md` retornou 404 (v6 reestruturou os caminhos) — o mecanismo de enforcement abaixo
> vem do README core (F2), não do doc de arquitetura.

## 1. Escopo: olhamos 1 de 13 repos [CONFIRMADO]

A org tem **13 repositórios** (F1). O ADR-081 analisou só o **core `BMAD-METHOD`** (F4). Não examinados:

- **bmad-module-creative-intelligence-suite (CIS)** — brainstorming/criatividade ← **o mais relevante** (ver §3)
- bmad-method-test-architecture-enterprise (TEA) — estratégia de teste risk-based
- bmad-builder / bmad-module-template — criar agentes/módulos
- bmad-method-ui (extensão VS Code), bmad-plugins-marketplace, bmad-method-wds-expansion (UX/WDS)
- bmad-automator, bmad-utility-skills, bmad-method-sample-data, .github

## 2. Mecanismo de enforcement do BMAD vs o nosso [F2; comparação INFERIDO/ALTA]

| | BMAD | metacognition |
|---|---|---|
| Como força a etapa | Template/workflow com paradas de elicitação + persona instruída a parar; story files como unidade | **Hooks determinísticos no harness** (route-gate, mission-gate, qa-evidence, boot_check) que rodam independente do modelo |
| Onde mora o processo | Markdown do agente + workflow/template | Skills (auto-trigger) + gates Python + ADR/ledger |
| Domínio | Agile/produto de software (12+ agentes, 34+ workflows) | Agnóstico (ADR-020) |
| Ponto fraco | agente "esquece" de seguir o template | hook vetado por EDR (ADR-047/060) |
| Igual | personas/skills em markdown; classificação epistêmica (`Confirmed/Deduced/Hypothesized` ≡ `CONFIRMADO/INFERIDO/DESCONHECIDO`); fases com handoff | idem |

**Diferença de fundo:** o BMAD confia na disciplina do template+persona; nós tiramos confiança do modelo e
botamos no hook executável.

## 3. Brainstorming: a alegação de cobertura do ADR-081 é PARCIALMENTE refutada [F3; INFERIDO/ALTA]

O ADR-081 extraiu **`advanced-elicitation`** (69 métodos) do `bmad-advanced-elicitation` (no core) e tratou
brainstorming como coberto. Mas o brainstorming **profundo** do BMAD vive no **CIS** (F3), que NÃO foi olhado:

- CIS é módulo **separado** (v0.2.1), instalado por cima do core (`npx bmad-method@alpha install` → escolher CIS).
- Comando dedicado `/cis-brainstorm`; agente "Brainstorming Coach"; técnicas **generativas/divergentes**:
  **SCAMPER, Reverse Brainstorming**, Design Thinking, Storyteller, Problem Solver, Innovation Strategist.

**Distinção que importa:** `advanced-elicitation` = métodos de **raciocínio/análise estruturada** (Tree of Thoughts,
Pre-mortem, Assumption Audit…) — *convergentes/críticos*. CIS = **ideação criativa** (*divergente/generativa*).
São categorias diferentes. Nosso `web-bundles/brainstorming-coach.md` (v1.60.0) é um coach web fino, não a
profundidade do CIS. **Conclusão:** temos boa cobertura de elicitação analítica; cobertura **fraca** de ideação
criativa estruturada (SCAMPER/reverse/design-thinking). Débito declarado, não resolvido aqui.

## 4. Recomendação (régua §0 — NÃO implementar sem decisão do dono)

- **Rastreabilidade:** emendar ADR-081 com bloco de fontes + "1/13 repos; recorte declarado" (cita este doc).
- **Brainstorming:** avaliar extrair 2–3 técnicas generativas do CIS (SCAMPER, reverse) para `advanced-elicitation`
  OU para um coach dedicado — **só se passar a régua §0** (ganho líquido vs o que já temos). Decisão do dono.
- O resto dos 11 repos: baixa prioridade aparente (UI, marketplace, sample-data, automator) — varredura rasa
  feita; deep-dive só sob trigger.
