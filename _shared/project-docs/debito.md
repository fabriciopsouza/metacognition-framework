> Parte de `_shared/project-docs/SKILL.md` (entrada enxuta desde 28/09/2026, B3c). Conteúdo copiado integral da versão anterior; a entrada aponta para cá.

## §8 — Débito declarado desta skill

- **§3.2 (RUNBOOK) é prosa sem gate, e as 5 marcas não são verificáveis por comando.** R1, R2 e
  R5 têm forma mecanizável (existe passo 0? cada passo declara resultado? cada item de R5 tem
  data?); R3 e R4 exigem julgamento. **Nada disso foi construído** — a §3.2 é cobrável em revisão
  adversarial e não bloqueia release, como o resto desta skill. *Quitação: ao segundo projeto que
  produzir runbook por este padrão, extrair o verificador das três marcas mecanizáveis — não das
  cinco, porque gate que adivinha qualidade erra e acaba desligado.*
  **Evidência de que o débito é real, com âncora:** o primeiro runbook produzido sob esta seção
  **falhou R5 em 100% dos itens** (nenhum datado) e falhou **R1 em duas das três portas**; a
  correção dessas falhas **introduziu um erro de sintaxe** no mesmo passo já reprovado. Três
  rodadas de revisão adversarial, **22–23/09/2026**, sobre um runbook de projeto de domínio (fora
  deste repositório, por anti-vazamento). **Nenhuma das três falhas seria pega por comando** — é
  exatamente isso que o débito acima pede.

  **Débito irmão, do mesmo item:** o registro `project-docs-standard` em `capabilities.json` ainda
  descreve a skill como "7 propriedades + conjunto graduado + 4 gates" — **não cita §3.1 nem
  §3.2**. Quitação junto com a extração do verificador.
- O conjunto graduado do §3 vem de **um** caso real bem-sucedido. Os portes "mínimo" e "médio"
  são **INFERIDOS** por decomposição, não medidos em projeto que os tenha adotado. Quitação:
  aplicar em dois projetos de portes diferentes e registrar o que sobrou e o que faltou.
- Os gates do §4 são descritos por intenção, não entregues como executável genérico — cada projeto
  escreve os seus. Quitação: extrair os dois primeiros (link quebrado, fronteira) para um
  utilitário do framework, se e quando repetirem em três projetos.
- **O §3.1 tem implementação de referência em UM projeto, não no framework.** O gerador de quadro
  com o gate das seis invariantes existe e está exercitado (8 casos que devem reprovar + a
  contraprova de que estado íntegro passa), mas vive no projeto onde nasceu:
  `copiloto-automacoes-sap/tools/quadro.py`. **Deliberadamente não foi promovido aqui**: um
  utilitário genérico extraído de um caso só é exatamente a adição preemptiva que a régua §0
  rejeita, e seria entregar como reutilizável algo nunca exercitado fora do berço. Quitação: ao
  segundo projeto que adotar o §3.1, comparar as duas instâncias e promover **o que sobreviver a
  ambas** — não a união das duas.
- **O registro em `capabilities.json` desta capacidade é `status: PARTIAL` / `enforcement: prose`
  / sem canário — e isso está correto:** o padrão é prosa aqui. Só sobe para determinístico quando
  o utilitário for promovido; declarar mecanismo que não existe neste repositório seria o teatro que
  a auditoria anti-teatro procura. *(A 1ª versão registrou `enforcement: manual`, que neste
  vocabulário significa "script existe, só não está no CI" — e nenhum script existia. Corrigido na
  1ª rodada de revisão; o texto acima ficou desatualizado e foi corrigido na 2ª.)*
