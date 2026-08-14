# ADR-102 — Padrão do conjunto documental de projeto

- **Status:** Aceito
- **Data:** 2026-08-13
- **Decisores:** dono (Fabricio) — override explícito; autoria Opus, crítica adversarial Sonnet
- **Substitui/emenda:** nada. Complementa `docops` (que fecha **bloco**) e
  `validation-reporting` (que valida **dado contra referência**). Esta ADR trata do
  **conjunto documental de um PROJETO**.

## Contexto

O `docops` cobria o fechamento de **bloco**: CHANGELOG, ADR aceito, execution-report. Não
havia norma alguma para o **conjunto documental de um projeto** — o que precisa existir para
que outra pessoa, outra sessão ou outra IA retome o trabalho sem perguntar nada.

O gap apareceu na prática. Um projeto de domínio produziu, em 12–13/08/2026, um conjunto
documental que passou por **5 rodadas de revisão adversarial e foi reprovado 3 vezes**. Os
achados que barraram o merge não foram de estilo: duplicação que o próprio mapa de fontes
negava, termos de glossário perdidos numa consolidação, nomes sem procedência sob um
cabeçalho que prometia verificação, e uma junção que não dá erro e devolve resultado
corrompido — justamente na consulta usada para provar uma refutação regulatória.

Declaração do dono: *"isto PRECISA ser padrão... preciso deste padrão de documentação em
todos os projetos, e poderemos melhorar depois."*

## Decisão

Criar `_shared/project-docs/SKILL.md` como núcleo SSoT do conjunto documental de projeto,
codificando **propriedades**, não uma lista de arquivos:

1. **Teste binário** — a próxima pessoa/sessão retoma sem perguntar nada.
2. **7 propriedades obrigatórias** — dono único por fato · marca de confiança (com REFUTADO
   que nunca se apaga) · prova com consulta reproduzível · número com data · ponto de
   retomada com nome de quem destrava e de quem decide · jargão explicado · fronteira
   declarada.
3. **Conjunto graduado por porte** — mínimo · médio · completo.
4. **4 gates executáveis** e **6 modos de falha observados** (os achados reais acima).

`docops` aponta para ela e ganha seção de escopo bloco × projeto. Registro em
`capabilities.json` como **PARTIAL / prose / sem canário** — seguindo o precedente de
`validation-reporting`, `readiness-gate` e `edge-case-hunter`.

## Régua §0 (ADR-007) — aplicada honestamente

A entrega é **adição pura**: 221 linhas novas contra 13 de ponteiro no `docops`, sem fusão,
sem remoção, sem redução medida de tokens e sem eval destravado.

**Nenhuma das portas (a), (b) ou (c) é alegada.** Alegá-las seria racionalização — foi
exatamente o defeito que o ADR-099 cometeu (alegou a porta (c) e o crítico derrubou os três
predicados, dentro do ADR que citava essa lição).

A base desta decisão é **override explícito do dono (ADR-051)**, com custo declarado:
o núcleo cresce em 221 linhas de prosa que nenhum canário cobra.

**Condição de quitação do débito**, para o override não virar permissão permanente:

1. Aplicar o padrão em **dois projetos de portes diferentes** e registrar o que sobrou e o
   que faltou — os portes *mínimo* e *médio* são hoje **INFERIDOS** de um único caso, e a
   tabela do §3 declara isso inline.
2. Extrair os gates 1 e 2 do §4 (link quebrado, fronteira) para utilitário do framework
   **se e quando repetirem em três projetos** — aí a skill deixa de ser prosa e o registro
   sobe de PARTIAL/prose para PROVIDES com canário.

## Consequências

**Positivas.** Documentação de projeto deixa de depender de quem escreveu. Os 6 modos de
falha viram checklist com evidência, não folclore. O conjunto graduado impede que o padrão
vire burocracia num projeto de duas semanas — a régua §0 aplicada à própria norma.

**Negativas / limite honesto.** É **prosa sem mecanismo**: nada impede um projeto de
ignorá-la. O passo 0 do `docops` é **advisory**, não bloqueante — chamá-lo de gate sem
canário seria o teatro que o ADR-085/P15 proíbe. E o padrão nasce de **um** caso
bem-sucedido: o risco de generalizar demais está declarado no §8 da skill e na marca de
confiança da tabela do §3.

## Registro da crítica adversarial

A 1ª versão foi **REPROVADA** por crítico de modelo distinto (Sonnet, isolado), com 2
bloqueantes e 4 achados menores. Corrigidos antes deste ADR: (1) régua §0 não resolvida —
resolvida aqui por override explícito com débito; (2) linguagem de bloqueio sem mecanismo —
rebaixada para advisory; (3) `enforcement: manual` sem script — corrigido para
PARTIAL/prose conforme precedente; (4) ponte com `validation-reporting` ausente —
acrescentada; (5) tabela do §3 sem marca de confiança inline — acrescentada; (6) sabor
residual de domínio nos exemplos — generalizado.
