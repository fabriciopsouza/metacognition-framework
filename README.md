# Framework Metacognitivo Agêntico — Flexível e Escalável

🌐 **Site (visão geral — UX, evidências e índice de docs):** https://fabriciopsouza.github.io/metacognition-framework/

**Um núcleo adaptável para orquestrar agentes de IA.** Eles classificam o que sabem (e dizem "não sei" em vez de inventar), **lembram entre sessões** (digest + memória), recusam inchar (régua de ganho líquido), passam por **QA adversarial** entre cada etapa, e **culminam em produto** — código, app, notebook ou pipeline conforme o briefing. É **método + estrutura** (papéis, junções binárias, decisões registradas em ADRs, hooks em runtime), não um prompt esperto. Open source (CC BY 4.0), sobre Claude Code, agnóstico de domínio (declarado por projeto).

**Comece:** [Instalar no VS Code](guia/INSTALAR-NO-VSCODE.md) · [Site](https://fabriciopsouza.github.io/metacognition-framework/) · [Releases](https://github.com/fabriciopsouza/metacognition-framework/releases) · [Segurança](SECURITY.md) · [Telemetria (opt-out)](TELEMETRY.md) · [Como foi construído](guia/COMO-FOI-CONSTRUIDO.md)

> **O que entrega hoje (honesto, ancorado em evidência):** ver [`LIMITS.md`](LIMITS.md) — cada capacidade com status ✅ PROVADO / 🟡 PARCIAL / ⏳ EM DESENVOLVIMENTO **derivado do canário que a prova** (gerado por `tools/build_limits.py`; o CI falha se divergir). A seção "o que NÃO fazemos" está lá também — andaime, não certificação (ADR-044).

> **Versão:** 1.68.0 · **Autor:** Fabricio Souza (github.com/fabriciopsouza/metacognition-framework) · **Base:** pesquisas A0–A3 · **PT-BR** · **CC BY 4.0** (ver [`LICENSE`](LICENSE) · [`NOTICE`](NOTICE))
> **Princípio:** o framework é **estritamente agnóstico de domínio** (ADR-010 / Princípio 12). Linguagens, ferramentas, normas setoriais, regulamentações, padrões técnicos, frameworks de validação, regras de negócio — **quaisquer** — são **aplicações/contextos**: não fazem parte do núcleo, **não aparecem hardcoded em prompts/regras/docs do framework** (nem como exemplo). Domínio é **declarado pelo discovery** por projeto. O que o núcleo oferece é **mecanismo flexível**: data integrity, audit trail, validação por risco, traceability, observabilidade — todos no `_shared/`.
> **Evolução por onda:** o histórico de capacidades (QA bicelular, handoff cross-sessão, série "prosa→mecanismo", runtime+produto, blueprints de domínio, modo non-admin) está em **[§Evolução](#evolução-por-onda)** abaixo e, em detalhe, no `CHANGELOG.md`. (Mantém o topo limpo — clareza > acúmulo.)

## Camadas
```
ROTEADOR     AGENT-FRAMEWORK.md (v2.3)   decide o MODO (contexto × complexidade)
NÚCLEO       _shared/                    regras transversais (fonte única)
PROCESSO     .agent/skills/              papéis flexíveis: pmo, discovery (+ sub-modo
                                         "mapeamento de processo" em v1.6.0), architect,
                                         developer, qa-critic, docops, explorer, _template
CONTRATO     docs/specs/                 requirements.md + validation.md (gate binário)
INFRA        _meta/                      isolamento de subagente, external-access, evals
APLICAÇÕES   exemplos/README.md          COMO criar aplicações (clonando _template) — vivem FORA do núcleo
```

## Tudo no núcleo é flexível (ADR-010 / Princípio 12)
**Estritamente agnóstico:** nenhum arquivo de `_shared/`, `.agent/` ou `docs/` (excluindo CHANGELOG histórico e exemplos didáticos rotulados em `docs/specs/exemplos/`) carrega listas hardcoded de produto, norma, convenção ou regra de domínio. O framework sabe **orquestrar, classificar, validar, isolar, rastrear** — para qualquer domínio. Quando há sinal de contexto especializado, **o `discovery` pergunta ao dono** (5 perguntas obrigatórias: regulado/alto-risco/regra-com-semântica/gaps-não-bloqueantes/**alimenta-outra-sessão**); a resposta vai para o `requirements.md`/`research-brief.md` em `## Escopo declarado pelo discovery` e dispara os gates downstream (incluindo Pacote de handoff cross-sessão se item (e) afirmativo — ADR-012 v1.13.0). **Anti-vazamento cross-projeto:** o agente não importa convenção/norma de outra sessão/projeto sem confirmação.

## Evolução por onda
Rastreabilidade das capacidades (detalhe completo no `CHANGELOG.md` + ADRs):
- **QA bicelular (ADR-011, P13):** 6 junções binárias forward-only (J0-J5) + process-critic adversarial isolado com rewind cascata; +**J6 PMO maestro** (ADR-045: re-orquestração na fronteira de bloco). TODO QA é adversarial.
- **Handoff cross-sessão (ADR-012, P14):** se a entrega alimenta outra sessão, Pacote de handoff obrigatório via J5.
- **Série "da prosa ao mecanismo" (ADR-013..020):** regras críticas ganharam par executável — contrato de skill, allowlist por efeito (`effect-gate`), telemetria/poda, QA heterogêneo, sync de repo, e **agnosticismo do núcleo** (`check_core_agnostic`).
- **Runtime + entrega de produto (ADR-021..023):** hooks (compaction/mission) + app `exemplos/dominio-software` (ux-designer + evals-engineer) — o framework **culmina em produto**.
- **Remediação v2 (ADR-033..044):** elicitação-consultiva, completude, anti-viés-de-oráculo, porta-do-usuário, overwrite-guard, execution-report, effect-gate motor, eval executado, catálogo regulado, `LIMITS.md` ancorado.
- **Blueprints de domínio (ADR-046):** software/processo/projeto carregados sob demanda; discovery **propõe a forma premium de uma vez** + dicionário-contrato (auto-detecção+validação de arquivos) + ux-gate premium.
- **Modo non-admin (ADR-047):** variante sem hooks p/ máquina com restrição de scripts; **gates anunciados** pelo agente (automação visível). Single-source → distribuições admin + non-admin (ver `guia/MODO-NON-ADMIN.md`).
- **Reparo do discovery (ADR-051):** o reforço sênior era prosa que **não disparava** (o filtro proibia inferência); agora **infere o stake** dos sinais e **mecaniza** a pesquisa de contexto + **verificação adversarial de âncora** (`check_context_brief`, barra J1 sob stake), proporcional ao modo de execução. Conserta ADR-009/010/033 provados inertes num caso de campo. + cláusula "pedido do dono não é imune a questionamento" (surface custo+consequência, override confirmado).

## Como aplicar a um contexto (escala por clonagem)
1. `cp -r .agent/skills/_template <aplicacao>` e preencher só o domínio.
2. Caso concreto → `cp -r docs/specs/_template docs/specs/<caso>`.
3. Sistema externo? → padrão `_meta/external-access` (MCP).
4. Eval-set (`_meta/eval-template`) — só entra em produção passando.
A aplicação herda `_shared/` automaticamente; mudar regra transversal = editar **um** arquivo.

## Setup em PC novo (idempotente)
- **Windows:** `pwsh ./bootstrap.ps1` (opcional `-MemoryRepo "<owner/repo>"` para sincronizar memória do Claude Code).
- **macOS/Linux:** `./bootstrap.sh` (opcional `--memory-repo <owner/repo>`).
- O script faz git config, garante `gh` CLI autenticado, clona o repo, e opcionalmente clona seu repo privado de memória no path esperado pelo Claude Code. Roda 2x sem destruir nada.

## Matriz de ambiente
| Recurso | Claude Code / SDK | Chat web |
|---|---|---|
| Ler `_shared/` via filesystem | sim | referência via contexto do Projeto |
| Isolamento real de subagente (explorer) | sim | hats sequenciais simulados |
| Hooks OTel / auditoria | sim | checklist manual |
| Spec, roteamento por confiança, papéis | sim | sim |

## Papéis (skills do framework)

| Papel | Quando ativa | Sub-modos |
|---|---|---|
| **pmo** | Entrada padrão · projeto novo · ambiguidade | — |
| **discovery** | Pedido novo/vago · spec rasa | (1) método universal · (2) revisar projeto existente · (3) **mapeamento de processo (v1.6.0)** — para processo de negócio com gatilhos/RACI/handoffs/exceções |
| **architect** | Decisão técnica > 1 arquivo · ADR | — |
| **developer** | Implementação de código/skill/template | — |
| **qa-critic** | Validação adversarial pós-developer | — |
| **docops** | Documentação final pós-aprovação | — |
| **explorer** | Auditoria read-only | — |

## Papéis emergentes (hats — sem skill nova; ver GUIA-EQUIPE)
skill-librarian · evals-engineer · governance-lead.

## Documentos (mapa)
- **Comece aqui:** `guia/INSTALAR-NO-VSCODE.md` (instalar) e `guia/SETUP.md` (3 modos).
- **Quem lê o quê:** `guia/ORIENTACAO.md` (humano × IA).
- **Uso diário:** `guia/GUIA-EQUIPE.md` · **Revisar repo:** `guia/COMO-REVISAR-OUTRO-REPO.md`.
- **Git/versão:** `guia/GIT-VERSIONAMENTO.md` · **Referências:** `guia/REFERENCIAS.md`.
- **Resiliência de acesso:** `guia/RESILIENCIA-ACESSO.md` (recovery de conta > chave local + push cedo).
- **Versão web:** `guia/web/index.html` (abre no navegador).
- **Prompt do chat web:** `PROMPT-CHAT-WEB-v4.4.md` (raiz) — encarnação do framework para
  ambientes sem filesystem (Claude.ai, Gemini). Mesmos princípios, mesmos resultados,
  papéis e subagentes simulados. Par dos outros load-bearing da raiz (`CLAUDE.md`,
  `AGENTS.md`, `AGENT-FRAMEWORK.md`).
- **Proveniência:** `CHANGELOG.md` (raiz). **Aplicações de domínio:** vivem FORA do núcleo —
  criadas clonando `.agent/skills/_template`. Ver `exemplos/README.md`.
