# ADR 055 — Desambiguação do namespace "avançado" (eixo execução × eixo profundidade-de-discovery) + regra anti-silêncio-de-stake no qa-critic

- Status: **Aceito** · Data: 2026-06-02 · Decisores: dono + squad (architect)
- Onda: encarnação web (v1.40.0) · Tipo: clarificação semântica de núcleo (vale IDE e web) · Atende: REQ-SAFE-2 da spec web; pendência herdada de sessão anterior.
- Política: **EMENDA** — afina a nomenclatura sem mudar decisão. Relaciona: ADR-005 (execution-modes), ADR-051 (método sênior proporcional ao modo), ADR-011 (qa-critic adversarial), ADR-054 (pacote web).

## Contexto

Existem **dois eixos ortogonais** que usavam, informalmente, a palavra "avançado", criando colisão de namespace:

1. **Eixo MODO DE EXECUÇÃO** (ADR-005): `default → avançado → autosuficiente`. Governa **quanta confirmação humana** o agente pede antes de agir (cadência de HITL).
2. **Eixo PROFUNDIDADE DE DISCOVERY** (ADR-009/051): `universal` (discovery padrão) × `reforço-sênior` (método sênior carregado quando há fonte canônica ou sinal de stake). Governa **quão fundo** o discovery investiga.

Chamar a profundidade de discovery de "avançado" colide com o modo de execução e confunde os dois — especialmente no pacote web, onde tudo é prosa lida pelo modelo (sem state file que desambigue por estrutura).

Pior: há uma **propriedade contraintuitiva** que a colisão escondia. Pelo ADR-051, o método sênior é **proporcional ao modo de execução**: `default` valida a pesquisa com o humano; `autosuficiente` **infere autônomo e reporta**. Ou seja, **subir o modo de execução afrouxa a validação humana do método sênior**. Num modo alto, a decisão *"este caso não tem stake → não aplico o reforço sênior"* corre o risco de virar **silêncio** (ninguém confirma) em vez de achado.

## Decisão (1 frase ativa)

**Fixar a nomenclatura:** "avançado" é termo **exclusivo do eixo modo-de-execução** (ADR-005); o eixo profundidade-de-discovery usa **`universal` / `reforço-sênior`**, nunca "avançado". E **mecanizar o anti-silêncio**: em postura `autosuficiente` (ou `avançado`), a conclusão "não há stake → não aplico reforço sênior" é um **achado explícito, registrado e ATACÁVEL pelo qa-critic** (hipótese default = há stake não-visto), nunca uma omissão tácita.

## Por quê (a propriedade que precisa ficar visível)

O modo alto dispensa a confirmação humana **da pesquisa** (efeito read-only E1) — isso é correto (pedir autorização para pesquisar contradiz o modo). Mas o **efeito de alto risco** (publicar número regulado, commitar artefato que vai a decisão) **continua no gate humano T3** (action-safety/high-stakes), ortogonal ao modo. A troca é: validação-humana-da-pesquisa → **auto-verificação adversarial mecanizada** (qa-critic ataca a ausência-de-stake + a tabela de âncora do `context-brief`), não confiança cega. Sem essa regra, "modo alto" degradaria silenciosamente para "pulei o reforço sênior e ninguém viu".

## Alternativas consideradas

1. **Deixar como está (ambíguo).** Mantém a colisão e o risco de silêncio. **Rejeitada.**
2. **Renomear o modo de execução** (tirar "avançado" do eixo execução). Quebra ADR-005 e todo o state file/histórico já gravado — anti-rename sem ganho. **Rejeitada.**
3. **Renomear o eixo discovery para `universal`/`reforço-sênior` + regra anti-silêncio no qa-critic (ESCOLHIDA).** Toca o eixo mais novo/menos acoplado, preserva ADR-005, e converte o risco de silêncio em achado atacável. Net-gain.

## Consequências

**Positivas:** fim da colisão; o pacote web pode falar dos dois eixos sem confundir; o qa-critic passa a **caçar a ausência-de-stake em modo alto** (não confiar que "sem stake" é verdade só porque o modo é autônomo). **Negativas/limite:** adiciona uma checagem ao qa-critic (custo pequeno, proporcional ao modo — só dispara em `avançado`/`autosuficiente`). **Aplicação:** vale IDE (ADR-051 já está no main) e web (a nota entra no `prompt-web-*` e no `discovery` consolidado — REQ-SAFE-2).

## Implementação (ponteiro)

- Nota de desambiguação no `discovery/SKILL.md` (eixo profundidade = `universal`/`reforço-sênior`) e no futuro `prompt-web-*`. Regra no `qa-critic/SKILL.md`: *"em postura avançado/autosuficiente, a conclusão 'sem stake → sem reforço sênior' é achado atacável: tente refutá-la (há perda material? número que vai a decisão? norma citada não-investigada?). Silêncio = FAIL."* DONE quando a nota e a regra existem; canário opcional no eval do discovery. Edições cirúrgicas — sem código novo.
