# Execution-report — conversor Excel→PDF · tier OWNER (privado, não distribuído)

**Bloco:** `excel-para-pdf` — script de conversão Excel→PDF A4 (10–12/09/2026)
**Origem:** Claude Code / Opus 5 · projeto-utilitário fora do núcleo do framework
**Entregue em:** https://github.com/fabriciopsouza/excel-para-pdf (privado) · PR #1 merged
**Rota declarada:** multi-etapa → squad (discovery → developer → qa-critic → docops)

- **Tempo (wall-clock):** uma sessão
- **QA adversarial:** 3 rodadas, Sonnet isolado, primeiro plano. **REPROVOU 2×**
- **Achados:** 11 no total — 9 do crítico (5 ALTA + 2 MEDIA na r1; 2 ALTA + 2 MEDIA + 1 BAIXA
  na r2, dos quais 9 distintos), 1 meu, 1 da mutação. Todos quitados; ver placar §6
- **Testes:** 39, todos provados por mutação · **0 processos órfãos** em 4 cenários
- **Tokens / turnos:** NÃO MEDIDO

---

## 1. O que validou o mecanismo

**Todos os achados do QA tinham a mesma assinatura: PDF errado com `exit 0`.** Nenhum dava erro.
Esta é a classe que o framework nomeia como cara, e aqui ela apareceu em estado puro, num
domínio novo (automação COM) onde o núcleo não tinha nenhuma regra específica.

O achado mais instrutivo: `--colunas-titulo` alto fazia o Excel descartar a paginação e produzir
**uma página ilegível** enquanto o log prometia quatro — ou seja, **uma flag do próprio `--help`
reintroduzia exatamente a falha que o script existe para eliminar**. Nenhuma leitura de código
minha pegaria isso; foi o crítico executando.

Confirma a postura do ADR-011: crítico isolado, modelo diferente, hipótese-default-bug.

## 2. O modo de falha NOVO, nomeado

**`guard-enterrado-na-camada-que-exige-o-mundo-real`.**

Escrevi a correção do achado mais grave *dentro* de `_aplicar_pagesetup`, função que só roda com
o Excel aberto. Os 30 testes ficaram verdes. **A mutação mostrou que o guard não tinha cobertura
nenhuma** — removê-lo não matava teste algum.

A correção não foi escrever mais teste. Foi **extrair o predicado** (`deve_repetir_colunas_titulo`)
para fora da camada COM, onde vira lógica pura e testável.

O mesmo padrão reapareceu em escala maior na rodada 2: `main()` inteira estava fora da suíte. Como
ela **não depende de COM**, não havia justificativa — e foi exatamente ali que `NaN` se escondeu
(toda comparação com NaN é falsa, então `nan < 0` e `nan < 72` passavam os dois).

> **Generalização candidata:** a fronteira de teste certa não é "o que é fácil testar", é *empurrar
> a decisão para fora da camada que exige o mundo real*. Quando um guard só é alcançável com
> Excel/rede/banco vivo, ele não está protegido — está escondido.

## 3. O que a mutação provou (e o que ela custou não fazer antes)

| Mutante | Testes mortos |
|---|---|
| ignorar o piso de legibilidade | 5 |
| desligar a desambiguação de nome | 2 |
| remover a guarda de margem | 1 |
| remover o `isfinite` das margens | 1 |
| voltar o arredondamento da mensagem de erro | 1 |
| remover o guard dos títulos de coluna | 1 (**0 antes da extração**) |
| remover os tetos dos inteiros | 1 |

A linha que importa é a penúltima. Sem a rodada de mutação, o guard mais importante do projeto
teria ido para a `main` com zero cobertura e aparência de testado.

## 4. Lições por skill

- **developer:** `except Exception: pass` escondeu o primeiro bug real da sessão (toda planilha
  parecia vazia porque um `com_error` era engolido). Terceira ocorrência desse antipadrão neste
  corpo de trabalho. O QA achou a quarta (`_garantir_encerramento` silencioso) — corrigida para
  avisar em stderr com o comando `taskkill` exato.
- **qa-critic:** exigir prova **executável** no prompt mudou a qualidade do retorno. Todo achado
  veio com comando, saída medida e PID. Nenhum achado de leitura.
- **qa-critic (higiene):** na rodada 3 pedi explicitamente que o crítico contasse e encerrasse os
  processos que criasse. Ele reportou 3 criados / 3 encerrados. Na rodada 2, sem esse pedido,
  deixou um `EXCEL.EXE` vivo que **eu** tive de matar. *Instrução de higiene de recurso deveria ser
  padrão no prompt do crítico quando o alvo cria processo/arquivo/conexão.*
- **discovery:** o inventário da máquina (Excel 16.0 via COM presente, LibreOffice ausente) decidiu
  a arquitetura antes da primeira linha. Sem ele, teria reconstruído com reportlab — pior por
  escolha, e o dono só descobriria ao abrir o PDF sem a formatação condicional.
- **docops:** o README afirmava "18 testes" depois de virarem 30. Divergência pega pelo crítico
  (achado MEDIA). Documentação que cita número precisa do mesmo gate que código que cita número.

## 5. Gaps declarados

- **Não há canário para a classe "guard só alcançável com o mundo real vivo".** A mutação pegou
  por acaso, porque eu a rodei. Não é mecanizado.
- **O prompt do qa-critic não exige higiene de recurso** (processo/arquivo/conexão criados no
  teste). Custou um órfão real nesta sessão.
- **Arquivo `.xlsx` real do dono não foi testado** — ele escolheu validar só com a planilha
  sintética. Fidelidade em planilha de produção é INFERIDO, não CONFIRMADO.
- Limite de caminho de 260 caracteres do Windows: documentado, não tratado.

## 6. Placar: gate × achado (quem pegou o quê)

| Achado | Quem pegou | Gate que DEVERIA ter pego |
|---|---|---|
| `com_error` engolido fazia toda planilha parecer vazia | eu, ao rodar `--plano` | nenhum — `except` mudo não tem canário |
| `--colunas-titulo` alto descarta a paginação | qa-critic r1 | nenhum |
| colisão de nome em `--por-aba` sobrescreve saída | qa-critic r1 | nenhum |
| `.csv` lido pela localidade → 30×1 | qa-critic r1 | nenhum |
| `--max-paginas-largura 0` ignora o enquadramento | qa-critic r1 | validação de argumento (ausente) |
| margem ≥ 14,85 cm → div/0 ou zoom negativo | qa-critic r1 | validação de argumento (ausente) |
| README dizia 18 testes com 30 existentes | qa-critic r1 | version-claim (existe no framework, não aqui) |
| `NaN` atravessa a validação inteira | qa-critic r2 | teste de `main()` (ausente) |
| `PrintCommunication` não restaurado → órfão | qa-critic r2 | nenhum |
| mensagem sugere máximo que ela mesma rejeita | qa-critic r2 | nenhum |
| guard sem cobertura | **mutação**, não o crítico | nenhum |

**Leitura:** 9 dos 11 vieram do crítico adversarial, 1 de mim, 1 da mutação. **Zero vieram de
gate automatizado** — este projeto nasceu fora do núcleo e não herdou canário nenhum.

## 7. Detecção: framework × humano

- **Mecanismo (framework):** a obrigatoriedade do QA adversarial em modelo isolado (ADR-011) é o
  que produziu 9 dos 11 achados. Não foi julgamento meu — foi o processo rodando.
- **Humano (dono):** as 3 decisões de design (piso 60% + quebra · 1 PDF com `--por-aba` ·
  validação sintética) vieram do dono, em uma única interrupção antes do bloco (ADR-111). Nenhuma
  delas era derivável do código.
- **Nem um nem outro:** o guard sem cobertura só apareceu porque rodei mutação por hábito. Não é
  mecanizado, e é o gap mais acionável deste report.

## 8. Retrabalho

- **Rodadas de retrabalho:** 2 (QA reprovou r1 e r2; aprovou com ressalvas na r3, ressalvas quitadas)
- **Custo:** duas rodadas completas de correção + 7 testes novos + extração de 2 predicados.
- **O que teria evitado:** validar argumentos na CLI desde o início (3 dos 7 achados ALTA) e
  escrever `main()` já testável. Ambos são hábito, não descoberta.

## 9. Melhorias (passam pela régua §0 — editam existente, não adicionam)

- **Prompt do qa-critic ganha cláusula de higiene de recurso** quando o alvo cria processo,
  arquivo ou conexão: "conte e encerre o que você criou; reporte o saldo". Edita o prompt que já
  existe; custo zero de token novo. Provado nesta sessão: com a cláusula, 3 criados / 3 encerrados;
  sem ela, um órfão que o dono herdaria.
- **`deve_repetir_*` como padrão nomeado:** quando um guard só é alcançável com o mundo real vivo,
  extrair o predicado. Cabe como parágrafo na skill `developer` existente — não é skill nova.

## 10. Boas práticas (reutilizável)

- **Inventariar a máquina ANTES de escolher a arquitetura.** `Excel COM presente / LibreOffice
  ausente` decidiu tudo em uma chamada, antes da primeira linha de código.
- **Fixture hostil por motivo declarado.** Cada uma das 7 abas existe para provar uma falha
  nomeada. A aba `SoFormatacao` (pintada sem conteúdo) sozinha provou que `UsedRange` mente.
- **Prova por mutação em toda correção.** Foi o que revelou o guard sem cobertura — teste verde
  não é evidência de nada até você tentar quebrá-lo.
- **Exigir prova executável do crítico.** "Achado sem comando e saída medida não conta" mudou o
  retorno de opinião para medição.
- **Medir exit code sem pipe.** Nesta sessão reportei `exit=0` errado porque `$?` pegou o `tail`.
  Refiz a medição antes de afirmar — em bloco cujo tema é "falha silenciosa com exit 0", medir o
  exit code errado teria sido a ironia cara.

## 11. Rastro

- Repo: `fabriciopsouza/excel-para-pdf` (privado) · commit de merge `940127b`
- Memória gravada: `excel-com-armadilhas.md` (4 armadilhas do COM que falham com exit 0)
- Gates INERTES no boot desta sessão (`check-repo-sync`, `check-core-agnostic`) aplicados
  manualmente antes das ações de efeito: `git fetch --prune` + `check_core_agnostic.py` → PASS
