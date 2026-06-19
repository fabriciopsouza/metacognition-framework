# Workflow: document-project (ADR-090)

> **Brownfield: documenta um projeto EXISTENTE de forma padronizada.** Compõe `explorer` (mapa
> read-only) + `docops` (redação) — NÃO recria nenhum. Equivalente adaptado de integração externa
> seletiva (proveniência: ADR-090).

## Quando usar
- Você (ou outra IA) precisa entender/herdar um projeto existente: arquitetura, estrutura, convenções, dependências, regras embutidas no código.
- Antes de mudar um projeto que você não escreveu (brownfield — fork do discovery, ADR-090).

## Composição (geradores QUE JÁ EXISTEM)
1. **Mapa do existente** — delegar ao **`explorer`** (subagente read-only): varrer estrutura de pastas, módulos, dependências, pontos de entrada, convenções de nome, regras de negócio embutidas. É leitura, não alteração.
2. **Redação padronizada** — **`docops`** transforma o mapa num doc com seções fixas: Visão geral · Arquitetura/estrutura · Convenções · Dependências · Pontos de entrada · Regras de negócio observadas · Gaps/riscos.
3. **Classificação** — cada afirmação sobre o código = `[CONFIRMADO]` (lido no arquivo, citar path:linha) vs `[INFERIDO]` (deduzido) vs `[DESCONHECIDO]`. File-first/anti-alucinação.

## Saída
- **1 doc** `docs/project-doc.md` (FORA do núcleo — artefato de aplicação, ADR-070), seções padronizadas acima.
- Alimenta o `generate-project-context` (passo 5) e o fork brownfield do discovery (elicitar só os gaps sobre este doc).

## Anti-reinvenção (régua §0)
`explorer` faz o mapa; `docops` escreve. Este workflow só encadeia os dois — sem mapeador/redator próprio.
