# ADR 062 — Relatório de execução enriquecido + corpus público anonimizado de APRENDIZADO (por colaborador / por skill)

- Status: **Aceito** (2026-06-04 — gate de aceite: CI verde 3 SOs + qa-critic; verificação na máquina deferida pelo dono) · Data: 2026-06-04 · Decisores: dono + squad (discovery→architect) · Modo: autosuficiente (mas as decisões reguladas LGPD/acesso passaram por gate humano — high-stakes × execução, ortogonais)
- Onda: telemetria/aprendizado (alvo v1.42.0) · Tipo: **EMENDA + extensão** de ADR-038/052. Atende: "todo fim de execução gera relatório estilo-AIVI (erros/acertos/detecção framework×humana/gaps/melhorias/boas práticas/lições reutilizáveis por skill); modo público sem dados sensíveis, commitado; dono vê todos, colaborador só o seu; conformidade LGPD como preço de uso; agnóstico de domínio, especializado por skill".
- Aplica/herda: **ADR-038/052** (execution_report dois-tiers — BASE), **ADR-026** (project_report — fonte de tokens), **ADR-017** (2 métricas: junção-origem do rewind + rounds qa-critic), **ADR-021** (padrão gate "artefato persistido antes do evento"), **ADR-030** (consistency-gate — 7ª dimensão), **ADR-012** (o relatório é parte do handoff cross-sessão — *ganho não-imediato*: alimenta a próxima sessão/colaborador), **ADR-044** (LIMITS honesto — anti-fabricação), **ADR-020** (agnosticismo + anonimização/denylist como backstop do público).

## Contexto

O `execution_report.py` (ADR-038/052) **já** entrega dois tiers (OWNER full em `docs/_private/_intake/`; EXTERNAL estruturado-whitelist em `telemetry/`), anti-fabricação de tokens, opt-out e detecção de tier por `docs/_private/`. **Régua §0: estender, não reinventar.** Faltam 3 deltas vs. o pedido: (1) o OWNER é um placar terso — falta a riqueza estilo-AIVI (**detecção framework×humana**, gaps, melhorias, boas práticas, **lições reutilizáveis por skill**); (2) o EXTERNAL é estruturado-whitelist (zero texto livre) → **não carrega lições narrativas** para o corpus de melhoria; (3) o público hoje fica `telemetry/` in-repo, não num **repo compartilhado**, e não há modelo **por-colaborador** nem **opt-in/aviso LGPD**.

## Decisão (1 frase ativa)

**Enriquecer o relatório OWNER com seções de aprendizado (estilo-AIVI, especializadas por skill) e introduzir um 3º artefato — o "learnings report" PÚBLICO ANONIMIZADO** (o OWNER passado por `anonymize.py` + gate da `sensitive-denylist`, o mesmo trust-model do `export-clean`), publicado num **repo PÚBLICO compartilhado** (`metacognition-exec-reports`, corpus de melhoria agnóstico) e, por colaborador, num **repo PRIVADO próprio** (`metacognition-exec-reports-<user>`, dono como colaborador → dono vê todos, cada um só o seu); a **obrigação** vira mecanismo (7ª dimensão fail-soft do consistency-gate, padrão ADR-021/030) no **fim de bloco + fim de sessão**; o público é **opt-in registrado na adoção** (aviso de finalidade + minimização — LGPD), o **preço de melhorar o framework**.

## Alternativas consideradas

1. **Reinventar um relatório novo.** Ignora ADR-038/052 já implementados e testados. **Rejeitada (régua §0).**
2. **Pôr lições narrativas no tier EXTERNAL estruturado.** Texto livre quebra a whitelist (= risco de PII/vazamento). **Rejeitada.**
3. **Enriquecer OWNER + 3º artefato público-anonimizado + repos por-colaborador (ESCOLHIDA).** Narrativa rica fica privada; o público é o OWNER **anonimizado** (mesmo trust-model do export-clean: anonymize + denylist-gate + `check_core_agnostic --sensitive`), carregando lições agnósticas sem cliente/PII. Estruturado-whitelist (EXTERNAL) permanece para as 2 métricas (ADR-017).

## Consequências

**Positivas:** todo bloco/sessão deixa trilha de aprendizado reutilizável (dev/discovery/architect/qa/docops/research/ux — "o que daqui serve a qualquer projeto"); o corpus público melhora o framework sem expor domínio (anonimização + denylist + gate, já provados no export-clean); dono tem visão total, colaborador só o seu (GitHub não isola por-arquivo → **um repo privado por colaborador** é o único modelo nativo que satisfaz isso); LGPD: público anônimo de fato (Art. 12 — fora do escopo) + opt-in informado; o relatório integra o **handoff cross-sessão** (ADR-012, ganho não-imediato). **Negativas/limite:** anonimização por regex **não é prova** como a whitelist — por isso o gate `sensitive-denylist`/`check_core_agnostic --sensitive` é o backstop **obrigatório** antes de qualquer push público (anonimização não-exaustiva por design — declarado em LIMITS); **criação dos repos é ação do dono** (gh) — o framework gera o conteúdo + o script de publicação, não cria conta/repo; o gate de obrigação é fail-soft (não trava o fechamento, declara o débito — padrão ADR-021). **SUPLANTA×EMENDA:** muda a decisão de modelo de acesso/LGPD → novo ADR; ajuste de seções/denylist → EMENDA.

## Implementação (ponteiro)

- `execution_report.py`: `build_owner_report` + `REQUIRED` ganham seções **Detecção (framework×humano)**, **Gaps**, **Melhorias**, **Boas práticas**, **Lições por skill** (anti-fabricação: heading obrigatório, conteúdo "— (nenhum neste bloco)" é válido, não fabricado). +modo `--learnings-public <owner.md> --out <pub.md>` = anonymize + recusa se token da denylist sobrevive.
- `docs/REPORTS-CONTRIBUTION.md`: aviso LGPD + finalidade + minimização + **opt-in** registrado (`~/.claude/exec-report-consent.json`) + modelo por-colaborador/público + "preço de uso".
- `docops/SKILL.md §Encerramento`: EMENDA — gerar OWNER enriquecido + (se opt-in) learnings-public + publicar.
- `consistency-gate.ps1`: 7ª dimensão fail-soft "execution-report do bloco presente + não-vazio?".
- **Owner infra (gh, fora do código):** criar `metacognition-exec-reports` (público) + `-exec-reports-<user>` (privado, dono colaborador). **DONE quando:** fim de bloco gera OWNER enriquecido; com opt-in, o learnings-public anonimizado passa o denylist-gate e é publicável; consistency-gate declara se faltou. Status→Aceito após verificação + merge.
