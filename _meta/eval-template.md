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

## Exemplo concreto (genérico — adapte ao seu domínio)
Suponha uma aplicação `<minha-aplicacao>` criada via `cp -r .agent/skills/_template`.
**Should-trigger:** frases típicas do domínio em que ela DEVE agir (3+ exemplos com
verbos e entidades que aparecem no fluxo real do usuário).
**Should-NOT:** frases que pertencem a OUTRA aplicação ou a um papel de processo
(devem apontar para a aplicação/papel correto, não disparar esta), + frases casuais
que devem ser respondidas direto sem skill alguma.

> Cada aplicação mantém seu próprio eval-set junto do seu SKILL.md, não aqui.
> Este arquivo é apenas o **template** do formato.

## Meta de cobertura
Cada role/skill nova **só entra em produção** com seu eval-set escrito e passando.
