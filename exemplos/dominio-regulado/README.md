# exemplos/dominio-regulado — catálogo de perfis de conformidade (opt-in, ADR-043)

> **Fora do núcleo, por design.** O núcleo é agnóstico (P12): não carrega norma de domínio. Aqui vivem
> **perfis de conformidade clonáveis** — andaimes de partida quando o discovery declara "regulado? = sim"
> (passo 6(a)). NÃO são certificação nem garantia; são um **ponto de partida** dos controles que um
> ambiente regulado costuma exigir, para o dono adaptar à norma concreta do seu caso.

## Como usar
1. O discovery, ao declarar **regulado = sim** com a(s) norma(s), **oferece** o perfil mais próximo.
2. Clonar o `compliance-profile-*.json` mais próximo para o projeto e **preencher/ajustar** os controles
   à norma real (o perfil é seed, não verdade — a norma específica é declarada pelo dono, ADR-010).
3. Os controles preenchidos alimentam o `high-stakes-gate` (validação por risco + HITL + audit trail).

## Perfis disponíveis (arquétipos genéricos — NÃO clientes)
| Perfil | Arquétipo | Famílias típicas |
|---|---|---|
| `compliance-profile-saude-dispositivo.json` | dispositivo/saúde/laboratório | ISO 13485, CLIA, 21 CFR |
| `compliance-profile-financeiro.json` | relato financeiro/contábil | SOX, Sarbanes-Oxley, Basel |
| `compliance-profile-infosec.json` | segurança da informação | ISO 27001, SOC 2 |

> **Limite declarado (→ LIMITS.md):** "andaime de conformidade", não "pronto para regulado". A
> adequação à norma concreta é responsabilidade do dono + revisão humana (HITL). `check_core_agnostic`
> permanece verde: estes perfis vivem em `exemplos/` (fora do núcleo), nunca em `_shared/`/`.agent/`.
