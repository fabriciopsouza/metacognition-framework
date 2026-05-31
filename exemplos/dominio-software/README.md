# dominio-software — Aplicação de entrega SW/dados (ADR-023)

> **Aplicação de domínio**, não núcleo. É a **demonstração viva** prevista em `exemplos/README.md`
> §"Quando faz sentido ter algo aqui": esta é uma **distribuição especializada** do framework —
> especializada em **entregar produto de software/dados** ao usuário final, que é o que fazemos.
> O núcleo `_shared/` e o squad base permanecem **agnósticos e inalterados** (P12).

## Por que existe
O framework existe para **culminar em produto** (código, executável, GUI, análise de dados) conforme
o briefing. Os papéis base (pmo→architect→developer→qa-critic→docops→release) governam o *processo*;
esta aplicação adiciona os 2 papéis que melhoram o **produto entregue**:

| Papel | Quando ativa | Entrega |
|---|---|---|
| [`ux-designer`](ux-designer/SKILL.md) | produto com interface (gui-app, CLI interativo, dashboard) | `ux-spec` (contrato produto→developer) |
| [`evals-engineer`](evals-engineer/SKILL.md) | validação sistemática (notebook/ML/pipeline/produção) | `eval-report` (gold-set + taxa pass/fail) |

**NÃO incluídos** (cobertos pelo núcleo, sem duplicar — ADR-023): `governance-lead` ≈ `high-stakes-gate`
+ `action-safety` + escopo declarado pelo discovery; `skill-librarian` ≈ campo `classe` (poda
Chesterton, ADR-017) + `validate_skills.py`.

## Como os papéis são ativados
Pelo `product_type` declarado no `mission.md` (template em `docs/specs/_template/mission.md`). O hook
[`mission-gate`](../../tools/hooks/mission-gate.ps1) (ADR-022) lê [`product-types.txt`](product-types.txt)
e ecoa quais papéis ativam para o tipo declarado. A confirmação é proporcional ao **modo de execução**
(ADR-005): autosuficiente confirma 1× no briefing; avançado/padrão confirma durante o processo.

## Fluxo com os papéis da app
```
pmo → discovery → architect → [ux-designer*] → developer → [evals-engineer*] → qa-critic → docops → release
                              (*se product_type tem UI)   (*se precisa validação sistemática)
```

## Contrato
Os dois `SKILL.md` honram o **contrato de 8 campos** do núcleo (`tools/framework-schema.json`) e são
validados por `tools/validate_skills.py` (glob `exemplos/*/*/SKILL.md`). Regra: qualquer transversal que
o app precise ajustar deveria virar PR no núcleo, não viver aqui (`exemplos/README.md`).
