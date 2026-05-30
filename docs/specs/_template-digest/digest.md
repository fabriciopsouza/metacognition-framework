# Digest — <projeto/bloco> · v<versão> · <timestamp ISO> · faixa <🟡/🟠/🔴 + %≈>

> Template do digest persistente (ADR-016). O digest **É** o Pacote de handoff cross-sessão
> (`_shared/metacognition-core/SKILL.md` §Pacote — Princípio 14/ADR-012): os **5 campos canônicos**
> do Pacote são obrigatórios e marcados **[P14]** abaixo. As demais seções são **extensões de
> compaction** (ADR-016) — tornando o digest um **superset** do Pacote, não um artefato paralelo
> (régua §0). **Teste binário (herda P14):** a próxima sessão começa SEM perguntar nada de volta?
> Clonar, preencher, versionar (commit). Sobrevive ao reset da janela de contexto.

## Carimbo de faixa (extensão ADR-016)
- **Versão ativa:** v<x.y.z> · **Timestamp:** <ISO 8601> · **Faixa no digest:** <🟠 ~75%> · **Modo:** <default|avançado|autosuficiente>

## [P14] Artefato consumível — com versão
<qual documento/dado a outra sessão lê, com versão>

## [P14] Localização
<repositório (URL) e/ou path absoluto; estado (branch/commit/PR)>

## [P14] Acesso
<visibilidade (público/privado) + permissões + o que NÃO foi versionado e por quê + como obter>

## [P14] Prompt pronto-para-colar
<papel da outra sessão + objetivo + critério de aceite + o que ela deve produzir/decidir, citando o artefato>

## [P14] Pendências e premissas herdadas
<o que fica aberto + o que a outra sessão deve assumir>

---
## Extensões de compaction (ADR-016 — o que evita re-derivar)
- **Decisões (com fonte + confiança):** <decisão> — <ADR/arquivo/pesquisa> — [CONFIRMADO|INFERIDO|DESCONHECIDO]
- **Detalhes caros (nomes EXATOS):** <campo/arquivo/parâmetro/comando que custou descobrir>
- **Nomenclatura fixada:** <nome aprovado> = <significado> (anti-rename sem ADR)
- **Ponteiros just-in-time:** <arquivo/seção> — <para quê> (ler só quando precisar)
- **5 arquivos mais recentes:** 1.<path> … 5.<path>
