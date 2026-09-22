---
description: Política de lançamento do projeto — o que pode ir ao portal, o que está retido e por quê (ADR-113)
---

Execute o **controle de lançamento** do projeto em trabalho, seguindo
`_shared/controle-projeto/SKILL.md` (fonte única — não duplicar a lógica aqui).

## Passo a passo

1. **Resolver o projeto.** `python tools/controle_projeto.py --situacao`
   (de dentro do repo do projeto: `python tools/nucleo.py controle_projeto`).
   O comando resolve a raiz por env → pasta corrente para cima, e **declara como achou**.
   Sem `projeto.json` ele não chuta: manda criar com `--iniciar`.

2. **Revisar adoção ANTES de qualquer outra coisa** — `--revisar-adocao`.
   Feature nova no núcleo nasce sem ninguém ter dito se este projeto a usa. Se houver pendência,
   trate primeiro: feature que nenhum projeto adota é feature órfã.

3. **Ler a situação e RELATAR ao dono**, não só imprimir: quantas podem ir, quantas estão retidas
   e por qual das duas regras. Retenção silenciosa é como tarefa some sem ninguém notar.

4. **Se o comando sair com código 2, o sprint acabou.** Aí PERGUNTE ao dono, em conversa:
   *"o sprint terminou — adiantar tarefas?"* — e diga quantas cabem sem estourar a capacidade.
   **Nunca adiante por conta própria** (ADR-111): autorização é ativa. `"siga"`/`"ok"` continuam o
   escopo declarado, não abrem adiantamento.

5. **Regra 4 — `--auto`.** Liste o que é automatizável e está sem impedimento, e **execute**,
   deixando prova. O que estiver fora das classes permitidas **não** se executa: a regra do dono é
   *"tudo que envolver decisão, número, valor, crítico, deve ser revisado por humano"*.

6. **Ao terminar, atualize o que deriva do estado** — quadro, cronograma, espelho no portal —
   pela ferramenta determinística do projeto, nunca por edição à mão.

## O que NÃO fazer

- Não lançar tarefa sem executor: ela aparece para o time inteiro e polui o backlog geral.
- Não mover tarefa entre sprints "para caber": mover prazo tem consequência, e ela se declara.
- Não editar o backlog derivado — ele é gerado; a edição some na próxima regeneração.
