# docs/_private/ — COFRE DO MANTENEDOR · NÃO DISTRIBUIR

> **Visibilidade:** só o dono do repositório. Esta pasta é **rastreada no repo PRIVADO**
> (backup em git) mas **EXCLUÍDA de qualquer distribuição pública/limpa**.
>
> **Regra de ouro:** o histórico completo (com nomes de cliente e dados de domínio) **não
> pode ser perdido** — ele vive aqui e no histórico git do repo privado. A versão de
> distribuição é uma EXPORTAÇÃO limpa que **não** copia esta pasta.

## Por que existe
Em 2026-05-31 detectou-se que identificadores de cliente/caso/repo (de dogfood real do
framework em casos de cliente) tinham vazado para o núcleo agnóstico e para o histórico
versionado, num repositório que estava **público**. A correção tem duas metades:
1. **Preservar** o registro real e completo aqui (debug/estudo/auditoria do ocorrido).
2. **Limpar** a superfície de distribuição (anonimizar mantendo a LIÇÃO, sem o identificador).

## Conteúdo
- `INCIDENTE-VAZAMENTO-2026-05-31.md` — registro completo: o que vazou, onde, causa-raiz,
  decisões, **token-map (real → genérico)** para reverter qualquer doc anonimizado.
- `_leak-scan-raw.txt` — saída bruta do linter (as 95 linhas de vazamento, com snippets reais).
- `_intake/` — notas de trabalho internas (ex-`docs/_intake/`), movidas para fora da distribuição.

## Procedimento de EXPORTAÇÃO LIMPA (quando for distribuir)
Como o histórico git contém os dados sensíveis em commits passados, distribuir com segurança
exige **não** carregar o histórico nem esta pasta:
1. Garantir `python tools/check_core_agnostic.py` = **PASS** (zero vazamento na árvore atual).
2. Exportar só a árvore limpa, sem histórico e sem `docs/_private/`:
   `git archive --format=tar HEAD | tar -x -C ../export-limpo` e então remover `docs/_private/`,
   OU criar repo novo com um único commit "squash" da árvore limpa.
3. Rodar o linter de novo no export. Só então publicar.

> Nunca tornar este repo público de novo sem ter feito a exportação limpa separada.
