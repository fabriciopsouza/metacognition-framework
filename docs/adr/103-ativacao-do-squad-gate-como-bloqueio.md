# ADR-103 — Ativação do squad-gate como bloqueio, e a matriz que não cobria skills

> **Leia o ADR-104 antes deste.** A ativação foi revertida para advisory na mesma sessão, por
> decisão do dono, após a 3ª reprovação seguida. O que continua valendo aqui: o diagnóstico dos
> dois defeitos medidos e a **ampliação da matriz**, que foi entregue.

- **Status:** SUPERADO nesta entrega — ver ADR-104 (desacoplamento). O diagnostico e a
  ampliacao da matriz permanecem validos e ENTREGUES; a ATIVACAO como bloqueio saiu.
- **Data:** 2026-08-13
- **Decisores:** dono (Fabricio), decisão explícita
- **Substitui/emenda:** **emenda o ADR-094** (que registrou a decisão de NÃO ativar o
  `squad_gate`) e completa o ADR-092 (que o construiu). Não altera o desenho do gate —
  altera seu **estado** (dormente → ativo) e **cobertura** (matriz).

## Contexto — a condição que o próprio ADR-094 escreveu

O ADR-092 construiu `tools/squad_gate.py`: fail-closed, deriva papéis exigidos do path
alterado, e — contra teatro — só aceita evidência com **atestação de isolamento**
(`agentId` de subagente) e **modelo ≠ autor**.

O ADR-094 decidiu **não ativá-lo**: *"o dono confirmou que antes funcionava SEM bloquear...
`squad_gate` permanece como peça disponível, NÃO ativada — decisão futura do dono se algum
dia advisory+reforço falharem."* O mesmo ADR declarou o limite com honestidade: *"reforço
por-turno é injeção de prosa — aumenta a probabilidade de o agente seguir, mas NÃO força
mecanicamente (nenhum hook força um LLM a ser cético)."*

**Em 13/08/2026 a condição se cumpriu, com caso concreto.** Uma sessão alterou o núcleo do
framework (`_shared/project-docs/SKILL.md`, `.agent/skills/docops/SKILL.md`,
`capabilities.json`) e **commitou sem revisão adversarial**. O agente declarou a lacuna no
fim do relato, mas declarar não é impedir. O reforço advisory não bastou — exatamente o
cenário previsto.

## Dois defeitos, medidos

**1. A matriz não cobria o núcleo.** `behaviors/manifest.json` exigia `qa_critic` para
`.py` e `docs/adr/`, e para mais nada de comportamento. Medido antes da correção:

```
$ python tools/squad_gate.py --paths _shared/project-docs/SKILL.md .agent/skills/docops/SKILL.md
[squad-gate] 2 path(s) staged -> papeis exigidos: nenhum
```

Alterar uma linha de código exigia revisão adversarial; **reescrever a skill que governa o
comportamento de toda sessão futura não exigia nada.** Está invertido: skill de núcleo tem
alavancagem maior que a maioria do código, porque atravessa todas as sessões e todos os
projetos que consomem o framework.

**2. Nada aplicava o gate a mudanças reais.** O canário `test_squad_gate.py` roda na suíte
(descoberta automática do `run_canaries.py`) e passa — mas ele testa a **lógica** do gate,
não sua **aplicação**. `.git/hooks/` está vazio (condição não-admin do ADR-047) e não havia
nenhuma referência a `squad_gate` em `.github/`. Gate testado, gate nunca aplicado.

## Decisão

1. **Ampliar a matriz** para cobrir o que governa comportamento: `_shared/`,
   `.agent/skills/`, `.agent/rules/`, `behaviors/manifest.json` (a própria matriz — senão o
   gate se auto-afrouxa), `AGENT-FRAMEWORK.md`, `CLAUDE.md`, `AGENTS.md`. Usa `prefix`,
   que o `squad_gate.py` já suporta — **sem tocar no código do gate**.
2. **Ativar o gate como bloqueio no CI**, em `pull_request`. Passa a barrar merge sem
   veredito atestado. Roda só em PR (em push de branch a evidência ainda está sendo
   produzida) e num único sistema operacional da matriz (o gate é independente de SO).

## Consequências

**Positivas.** A revisão adversarial deixa de depender da disciplina do agente. O caso que
originou este ADR passa a ser impossível: o mesmo commit hoje é barrado, e foi verificado —
o gate acusou `BLOQUEADO (fail-closed): faltam evidencias atestadas: ['qa_critic']` e só
liberou depois do veredito atestado registrado via `tools/qa_evidence.py`.

**Negativas, declaradas.** Todo bloco que toque código, ADR, skill, regra ou roteador passa
a custar um subagente crítico antes de fechar — mais lento e mais caro. É o custo aceito
conscientemente, e reverter é editar um passo do CI.

**O que este gate NÃO faz, para ninguém confundir enforcement com garantia:**

- Não força o agente a ser cético. Ele exige **evidência atestada**, não bom julgamento.
- Não roda localmente onde o EDR impede hooks (ADR-047). A trava real é o CI, server-side.
- Não detecta um crítico incompetente nem um veredito complacente. Reduz risco; não o zera.
- Se uma restrição de harness impedir spawnar o crítico, o bloco **para e avisa** — em vez
  de seguir e declarar a lacuna depois. Essa é a mudança de comportamento que importa.

## Lição registrada

O gate certo existia, testado, há semanas — e não impediu nada, porque estava desligado e a
matriz não cobria a superfície de maior alavancagem. **Capacidade construída e não aplicada
é indistinguível de capacidade ausente**, e o índice de capacidades a exibia como `PROVIDES`.
Vale para toda entrada do registro: `status` deve descrever o que está **aplicado**, não o
que está **disponível**.
