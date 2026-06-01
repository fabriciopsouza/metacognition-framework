# exemplos/ — Aplicações vivem FORA do núcleo

> O framework é flexível por desenho — domínio, ferramenta, norma setorial e contexto
> operacional são **aplicações**, não núcleo. Numa distribuição **flexível**, a sua aplicação
> reside no seu repositório, não aqui.
>
> **Exceção declarada (ADR-023):** esta é uma **distribuição especializada em entrega de
> software/dados** — então mantemos uma aplicação como **demonstração viva**:
> [`dominio-software/`](dominio-software/README.md) (papéis `ux-designer` + `evals-engineer`,
> ativados por `product_type`). O núcleo `_shared/` e o squad base seguem **agnósticos e inalterados**.

## Como criar uma aplicação (escala por clonagem)

```bash
cp -r .agent/skills/_template <minha-aplicacao>/
# preencha SÓ o domínio dentro do <minha-aplicacao>/SKILL.md:
#   - identidade do papel (ex.: "analista de X em contexto Y")
#   - regras de negócio específicas que o núcleo não conhece
#   - convenções de nomenclatura (prefixos, padrões)
#   - referências às skills de _shared/ que esta aplicação consome
```

Para um caso concreto (uma feature, um indicador, uma migração):

```bash
cp -r docs/specs/_template docs/specs/<meu-caso>/
# preencha requirements.md (entradas/saídas/aceite) e validation.md
# (test cases binários — o gate do qa-critic se ancora aqui)
```

## Por que aplicações não ficam no núcleo

1. **SSoT real:** o núcleo `_shared/` define COMO classificar, validar, isolar
   e rastrear — sem conhecer nenhum domínio. Misturar aplicações específicas
   no repositório do núcleo tende a vazar premissas de domínio para regras
   transversais (causa-raiz #1 de "skill sprawl" — ver pesquisa A2).

2. **Versionamento independente:** sua aplicação evolui no ritmo do seu negócio;
   o núcleo evolui no ritmo das pesquisas A0–A3. Acoplá-los no mesmo repo
   trava as duas evoluções.

3. **Reuso real:** uma aplicação que importa o núcleo via subtree/submodule
   pode ser substituída sem reescrever o núcleo. O contrário não.

## O que herda automaticamente

Sua aplicação **herda** sem copiar:
- as 4 regras invioláveis (anti-rename, file-first, classificação, NÃO SEI);
- todas as skills de `_shared/` (basta o SKILL.md da aplicação carregá-las);
- os papéis de processo (`pmo`, `architect`, `developer`, `qa-critic`, `docops`);
- os workflows base (`/start-session`, `/feature-plan`, `/implement`, `/handoff`,
  `/checkpoint`).

Você adiciona **somente o domínio**. Qualquer regra transversal que precisar
ajustar significa que ela deveria virar PR no núcleo, não viver na aplicação.

## Quando faz sentido ter algo aqui

Em forks pessoais ou em distribuições especializadas do framework, você pode
manter uma aplicação de exemplo aqui para servir de demonstração viva — é o caso
de [`dominio-software/`](dominio-software/README.md) nesta distribuição (ADR-023).
Numa distribuição **flexível** do framework, esta pasta permanece vazia (exceto este
README) por princípio.
