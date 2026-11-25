# Handoff — B2 e B3 do plano "análise acompanhada" (20/11/2026)

- **Decisão do dono (20/11/2026):** B2 e B3 rodam cada um em **sessão limpa** (ADR-132).
- **Plano:** `C:\Users\fabriciosouza\pesquisas\2026-11-19_analise-acompanhada-humano-ia\relatorio.md`, seção 7.8 (linhas B2 e B3), invariantes na 7.6, abas do runbook na 5.6.
- **Base pronta:** B1 mesclado (PR #221, `34562f0`): ADR-134, skill `.agent/skills/analise-dados/SKILL.md`, sub-modo `produto-de-dados`, campo modo no `tools/handoff.py`. Correção do bootstrap mesclada (PR #222, `ad6d79a`).
- **Modo vigente na próxima sessão:** acompanhado (ADR-134).
- **Ordem:** B2 antes de B3 (o B3 cita a lista de verificação da QA de análise que o B2 cria). Podem rodar em paralelo só se o B3 não tocar `qa-critic`.

## Antes de escrever (as duas sessões)

1. ABRIR `C:\Users\fabriciosouza\.claude\coordenacao\QUADRO.md`, registrar a sessão (só com Edit).
2. TRABALHAR em worktree própria a partir de `origin/main` (a `main` canônica tem 7 commits locais alheios, da PR #201; não enviar).
3. NÃO rodar `python bootstrap.py` em clone anterior a `ad6d79a` sem restaurar `.claude\settings.json`.

## Prompt pronto — sessão B2

```
execute o B2 do plano em C:\Users\fabriciosouza\pesquisas\2026-11-19_analise-acompanhada-humano-ia\relatorio.md, seção 7.8.
Contexto: C:\Users\fabriciosouza\metacognition-framework\docs\_private\handoffs\2026-11-20-B2-B3-analise-acompanhada.md.
Faixa F2. Envie a cada marco SendMessage para "orquestrador-multi-ia-bb" (marco na 1a linha) e atualize a linha no QUADRO.
```

Entrega do B2 (linha da 7.8): conferência por invariante (stdlib, CSV) + lista de verificação da QA de análise; `qa-critic` ganha seção; CHANGELOG e `capabilities.json`; testes da skill e da capacidade do B1. Aceite: cada invariante da 7.6 tem caso legítimo que passa e defeito que reprova, inclusive troca de valores que preserva contagem e soma.

## Prompt pronto — sessão B3

```
execute o B3 do plano em C:\Users\fabriciosouza\pesquisas\2026-11-19_analise-acompanhada-humano-ia\relatorio.md, seção 7.8.
Contexto: C:\Users\fabriciosouza\metacognition-framework\docs\_private\handoffs\2026-11-20-B2-B3-analise-acompanhada.md.
Faixa F2. Envie a cada marco SendMessage para "orquestrador-multi-ia-bb" (marco na 1a linha) e atualize a linha no QUADRO.
```

Entrega do B3: modelo de runbook de análise (Parte C) e roteiro do pacote documental proporcional; só arquivos novos; CHANGELOG. Aceite: o modelo abre com as abas da 5.6; aba Roteiro sem coluna Status reprova a conferência do molde.
