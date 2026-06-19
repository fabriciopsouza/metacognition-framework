# Workflow: generate-project-context (ADR-090)

> **Compõe geradores existentes — NÃO recria nenhum.** Produz, em 1 passo, um **doc de contexto
> consumível por IA** do projeto atual (para colar em outra sessão/IA ou abrir um bloco com contexto
> pleno). Equivalente adaptado de integração externa seletiva (proveniência: ADR-090).

## Quando usar
- Vai retomar um projeto numa sessão/IA nova e quer o contexto completo num só artefato.
- Brownfield: combinar com o `explorer` (mapa do existente) antes de elicitar gaps (fork do discovery, ADR-090).

## Composição (ordem; cada item é um gerador QUE JÁ EXISTE — reusar, não reimplementar)
1. **Briefing + glossário** — `docs/briefing.md` (objetivo/escopo/critério) + `.agent/rules/00-glossario.md` (nomes = fonte da verdade). Incluir verbatim.
2. **Handoff determinístico** — `python tools/handoff.py` (ADR-076): pacote P14 (artefato consumível + localização + acesso + prompt-pronto + pendências/premissas). É o núcleo do contexto.
3. **Índice de capacidades** — `CAPABILITIES.md` (gerado por `tools/build_capabilities.py`): o que o framework/projeto provê.
4. **Catálogo de conhecimento** — `python tools/knowledge_catalog.py` (ADR-068), se houver: fontes/docs do projeto.
5. **Mapa do existente (brownfield)** — **se já houver `docs/project-doc.md`** (gerado pelo `document-project`), usar como entrada e **pular a re-varredura** (não duplicar trabalho); senão delegar ao `explorer` (read-only): estrutura, convenções, dependências. Greenfield: pular.
6. **Estado** — checkpoint do TOPO de `history.md` (mais-novo-primeiro) + WIP `## Em aberto`.

## Saída
- **1 doc** `docs/project-context.md` (FORA do núcleo — é artefato de aplicação, ADR-070), montado dos itens acima na ordem.
- Teste binário (ADR-053): a próxima sessão/IA começa **sem perguntar nada**? Se não, o gap volta ao passo correspondente.

## Anti-reinvenção (régua §0)
Este workflow **orquestra**; não tem gerador próprio. Se um item já tem tool (handoff/capabilities/knowledge-catalog/explorer), chamar o tool — nunca duplicar a lógica aqui.
