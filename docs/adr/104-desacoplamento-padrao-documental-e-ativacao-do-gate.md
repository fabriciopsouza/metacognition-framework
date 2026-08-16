# ADR-104 — Desacoplar o padrão documental da ativação do gate

- **Status:** Aceito
- **Data:** 2026-08-13
- **Decisores:** dono (Fabricio), após a 3ª reprovação seguida
- **Substitui/emenda:** **emenda o ADR-103** (ativação do squad-gate). Não toca o ADR-102.

## Contexto

Uma única entrega carregava duas coisas de maturidade muito diferente: o **padrão documental de
projeto** (ADR-102) e a **ativação do squad-gate como bloqueio** (ADR-103). Ela foi submetida a
três rodadas de revisão adversarial por modelo distinto do autor e **reprovou nas três**.

A distribuição dos achados é o dado que importa:

| rodada | achados no ADR-102 (padrão documental) | achados no ADR-103 (ativação do gate) |
|---|---|---|
| 1ª | 2 bloqueantes, 4 menores | — (ainda não existia) |
| 2ª | — | 2 bloqueantes, 1 grave, 3 médios |
| 3ª | **nenhum** | 2 bloqueantes, 2 médios |

Na 3ª rodada o crítico aplicou a **regra de escalonamento** do framework — *três reprovações
seguidas significam que o problema é o desenho, não a execução* — e nomeou o desenho: **ativar um
gate bloqueante agora pressupõe uma cadeia madura** (evidência atestada + CI + ledger de junção), e
essa cadeia provou ao vivo que ainda tem elos manuais. Os dois bloqueantes da 3ª rodada foram
exatamente isso: evidência editada à mão sem passar pelo CLI canônico, e uma nota de débito inserida
no lugar errado por um match posicional frágil.

## Decisão

**Separar as duas entregas.**

1. **ADR-102 segue** nesta entrega. Está limpo: zero achados na 3ª rodada, depois de os seis da 1ª
   terem sido tratados.
2. **A ativação como bloqueio sai.** O passo de CI vira **advisory** (`continue-on-error: true`):
   ele roda, avalia e **avisa**, sem barrar. `continue-on-error` é o único ponto a mexer quando a
   ativação voltar — a diferença entre avisar e barrar é uma linha.
3. **O trabalho de endurecimento é preservado**, não descartado, na branch
   `feat/adr-103-squad-gate-endurecimento`.

**O que foi entregue e PERMANECE, porque não depende da ativação:**

- **Matriz ampliada** — `_shared/`, `.agent/skills/`, `.agent/rules/`, a própria matriz e os
  roteadores da raiz passaram a exigir revisão. Antes, mudar uma linha de `.py` exigia revisão e
  reescrever a skill que governa toda sessão futura não exigia nada.
- **Escopo obrigatório na evidência** (`escopo_paths`) — sem isso, um veredito aprovativo em
  qualquer ponto do histórico liberava qualquer mudança futura, para sempre.
- **Match ancorado de versão** e **cobertura de teste** onde antes havia zero para as funções
  novas (`pytest tools/test_squad_gate.py -q` diz quantos são hoje — o número envelhece, a
  consulta continua respondendo; princípio do ADR-105, aplicado depois que este ADR nasceu
  dizendo "19" e o valor virou 20).
- **Canário de integridade** `.json` × `.md` — nasceu do defeito da 3ª rodada e o reprova.

## Consequências

**Positivas.** O padrão documental não fica refém do endurecimento do gate. O gate volta a avisar —
que é o estado do ADR-094, e nenhuma capacidade se perde. O ganho estrutural (matriz + escopo +
testes + canário) entra agora e torna a próxima ativação bem mais barata.

**Negativas, declaradas sem maquiar.** Volta a valer o que falhou e originou tudo isto: **o gate
avisa e o agente pode ignorar**. Foi assim que um bloco alterou o núcleo sem revisão em 13/08/2026.
A diferença em relação a antes é que agora a matriz cobre o núcleo e a evidência é escopada — então
quando a ativação voltar, ela pega o que precisa pegar.

**Condição para reativar** (não é "algum dia"): (a) um caminho que impeça evidência de ser gravada
fora do `tools/qa_evidence.py`, e (b) o passo de CI exercitado contra um PR real, não apenas
raciocinado. Enquanto as duas não existirem, ativar de novo repete a mesma sessão.

## Lição

A entrega estava certa e o **empacotamento** estava errado. Amarrar uma norma madura a uma mudança
de enforcement imatura fez a norma reprovar três vezes por defeitos que não eram dela. Maturidade
diferente pede bloco diferente — e o sinal de que era hora de separar estava disponível desde a 2ª
rodada, quando 100% dos achados já vinham de um só dos dois lados.
