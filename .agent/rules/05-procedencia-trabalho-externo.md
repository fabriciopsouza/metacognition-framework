# Regra 05 — Procedência de trabalho externo

**Fonte única:** `_shared/traceability/SKILL.md` (Regra 7).

Não redefinida aqui. Resumo: quando o diretório de trabalho é EXTERNO ao
repositório (drive corporativo sincronizado, pasta de cliente, share de rede,
pasta de demanda/chamado), essa pasta recebe um `PROCEDENCIA.md` antes de o
bloco fechar — declarando demanda, framework/versão/commit/sessão, modelo por
papel, e o STATUS de cada artefato (MINUTA / PROPOSTA / MIGRADO / APROVADO).

Mecanismo: `python tools/handoff.py --provenance "<dir>" --write`.

O gatilho é a FORMA da situação (escrita fora do repo), nunca o nome do
cliente/produto — núcleo agnóstico (canário `core-no-vendor`). O "porquê"
(a cadeia decisão→fonte→versão quebra quando o artefato sai do repo) está em
`_shared/traceability`.
