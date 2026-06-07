# Execution-report — bloco "índice + enforcement + hub cross-IA" (2026-06-06 · tier OWNER · privado)

> Simula/registra o **uso** do framework neste bloco (o par cross-IA registra a **melhoria do main**).
> ADR-038/052. Tokens/tempo/turnos = NÃO MEDIDO (sem telemetria de token exposta — LIMITS.md).

## Placar gate × achado (quem pegou o quê)
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| 18 canários sem registro no índice | **canário órfão** (`test_capabilities` #8) | o próprio (funcionou na 1ª) |
| `export-shadow-stamp` PROVIDES sem canário real (overclaim) | **qa-critic** (Sonnet isolado) | canário de status (não distingue test que não exercita o mechanism) |
| `mechanism == test` em 6 entradas (nonadmin/parity reais alhures) | **qa-critic** | — (smell, corrigido) |
| `execution-report` cross_ai sem `enforcement` | **canário de enforcement** (#9) | o próprio (funcionou) |
| master com origin SSH classificado FOREIGN | **dogfood** (canário de onboarding falhou→investiguei) | `repo_identity` não normalizava SSH↔HTTPS (bug pré-existente ADR-070) |
| colisão de sessão paralela (mesmos nomes de arquivo) | **file-first** (inspeção antes de assumir) | `session.lock`/WIP-limit (não usado entre abas) |

## Detecção: framework × humano (mecanismo vs. revisão humana)
- **Humano (dono) pegou (5×):** o agente reportou "infra cross-IA não existe" quando `cross_ai_gate`/
  hub-README/`.mailmap`/handoff real **já existiam**. Mecanismo nenhum pegou — **era a ausência do índice**.
  → motivou ADR-072. Também: o cerne "prosa→mecanismo" recorrente; a necessidade de 2 níveis no índice;
  o risco de truncamento; "premium/public não fazem cross-IA". **Fonte legítima (princípio 11 honesto).**
- **Framework (mecanismo) pegou:** órfão-canário (18), qa-critic (overclaim shadow + smell mechanism==test),
  enforcement-canário (cross_ai sem enforcement), o bug SSH↔FOREIGN (via dogfood do onboarding).
- **Lição:** o gap "agente esquece o que existe" só virou detectável DEPOIS do índice. Antes, dependia do
  humano. Agora o índice + canário órfão tornam a cobertura auditável (mecanismo, não prosa).

## Gaps (não-bloqueantes, flagados)
- `enforcement` só obrigatório em `cross_ai` hoje; núcleo preenche incrementalmente (régua §0).
- 5 capacidades cross-IA ainda não fail-closed (`[debito-mecanizacao]`: 2 ci-ready, 1 advisory, 1 fail-soft, 1 manual) — visíveis no canário.
- Hub não provisionado / branch protection ausente → enforcement server-side pendente (PLANO-CROSS-IA.md, ação do dono).

## Melhorias do framework (régua §0)
- ADR-072 índice derivado + canário órfão (garantia além de prosa; converge com LIMITS.md, não soma).
- ADR-073 `enforcement` declarado + débito visível (operacionaliza o Princípio 12 prosa→mecanismo).
- ADR-067 EMENDA (popup só master) + bugfix `_norm_remote` (reuso do ADR-070, não adição).
- `cross_ai_hub.py` mecaniza a doutrina de scan/deposit do ADR-069.

## Boas práticas reutilizáveis
- **Canário que se auto-completa:** exigir que todo `test_*` esteja referenciado força o registro de
  features novas — o índice não apodrece. Padrão aplicável a qualquer catálogo derivado.
- **Veredito honesto > overclaim:** PROVIDES→PARTIAL quando o canário não exercita o mecanismo (qa-critic).
- **Dogfood do próprio bloco:** este report + o handoff cross-IA usam os mecanismos construídos no bloco.
