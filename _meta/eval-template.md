# Eval-Set de Disparo — Template por Skill/Role

> Garante **reprodutibilidade do roteamento**: a skill certa ativa, a errada não.
> Fonte: pesquisa A2 (eval-sets + *description improver* do skill-creator Anthropic).
> Claude tende a **sub-ativar** skills → por isso descrições "pushy" + estes evals.

## Como usar
1. Para cada skill/role, escrever **8–12 should-trigger** e **8–10 should-NOT**.
2. Rodar mentalmente (ou via skill-creator) cada frase contra a `description`.
3. Falha (devia disparar e não disparou, ou vice-versa) → ajustar a `description`
   (mais gatilhos positivos ou exclusões mais explícitas) e reavaliar.
4. Registrar a versão da skill testada.

## Formato
| # | Frase de teste | Esperado | Resultado | OK? |
|---|---|---|---|---|
| 1 | <frase realista do usuário> | TRIGGER | | ☐ |
| ... | | | | |
| N | <frase que NÃO deve ativar> | NO-TRIGGER | | ☐ |

## Exemplo concreto — `python-fuel-forecaster`
**Should-trigger:** "prever volume de diesel por base no 2º semestre"; "validar
schema do CSV de vendas com Pandera"; "qual método de forecast para etanol na safra".
**Should-NOT (deve apontar outra role):** "criar um LOD no Tableau" (→ tableau);
"promover transport SAP para PRD" (→ pharma); "qual a capital da França" (→ resposta direta).

## Meta de cobertura
Cada role/skill nova **só entra em produção** com seu eval-set escrito e passando.
