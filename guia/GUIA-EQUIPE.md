# Guia de Equipe — Uso Diário

> Material curto para capacitar a equipe. 5 minutos de leitura.

## 1. O modelo decide o modo sozinho
- Pergunta rápida / 1 fórmula / debug → **metacognição** (resposta direta validada).
- Projeto / >2 arquivos / >2 etapas / regulado → **squad** (papéis + workflows).
- Você pode forçar: "use o squad" ou "responde direto".

## 2. As 4 regras que nunca caem (de `_shared/`)
1. **Classificar** toda afirmação relevante: CONFIRMADO / INFERIDO / DESCONHECIDO.
2. **Anti-rename** — não renomear campo aprovado sem ADR.
3. **File-first** — ler o arquivo / inspecionar colunas antes de assumir.
4. **NÃO SEI** dito na cara, sem inventar.

## 3. Começar um caso novo (o jeito reprodutível)
1. Preencher `docs/briefing.md` + `00-glossario.md`.
2. `/feature-plan <X>` → gera a spec (`requirements.md` + `validation.md`).
3. `/implement <X>` → Developer → QA-Critic (valida contra `validation.md`) → DocOps.
4. `/checkpoint` ao fim do bloco.

## 4. Frameworks de decisão (do A2)
| Se… | Então… |
|---|---|
| feature crítica, multi-arquivo, regulada | spec completa (SDD) |
| bug < 30 min, < 3 arquivos | direto, com testes |
| padrão repete em 3+ contextos | virar skill, não spec ad-hoc |
| subtarefa polui contexto / tools diferentes | isolar em subagente |
| decisão irreversível | manter no principal + confirmação humana |
| número vai a decisão executiva ou é regulado | roteamento reflexivo (QA + revisão humana) |

## 5. Comandos
`/start-session` (toda sessão) · `/feature-plan` · `/implement` · `/handoff <papel>` · `/checkpoint`
> Comandos específicos de domínio (ex.: `/sap-change`, `/bi-deliverable`) são adicionados
> pela sua aplicação — não vivem no núcleo. Crie em `<sua-aplicacao>/workflows/`.

## 6. Onde mudar uma regra
Regra transversal → edite **um** arquivo em `_shared/` (propaga p/ todas as aplicações).
Domínio específico (BI, regulado, contexto X) → a aplicação correspondente (criada
clonando `.agent/skills/_template`); vive FORA do núcleo. Ver `exemplos/README.md`.
Nunca duplique — se a regra existe em `_shared/`, referencie.

## 7. Sinais de que algo saiu do trilho
- Pediram "posso prosseguir?" 2× → deveria ter avançado com premissa.
- Campo renomeado sem ADR → reverter.
- Número entregue sem classificação ou sem rastreio à fonte → recusar.

## 8. Papéis emergentes são *hats*, não skills novas (pesquisa A2)
Em equipe pequena, a mesma pessoa veste o chapéu quando necessário — não cria arquivo:
- **skill-librarian** — cura, versiona e revisa as skills; evita "skill sprawl".
- **evals-engineer** — dono dos eval-sets (`_meta/eval-template`); skill nova só entra passando.
- **governance-lead** — políticas, auditoria, compliance; aciona `_shared/high-stakes-gate`.

## 9. Núcleo × aplicação (regra de ouro)
O framework é genérico. Domínio (BI, regulado, contexto X) nasce clonando
`.agent/skills/_template` → vai para uma aplicação. Nunca coloque domínio no núcleo.
