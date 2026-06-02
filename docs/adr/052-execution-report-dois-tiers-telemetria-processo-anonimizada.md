# ADR 052 — Execution-report de dois tiers + telemetria de PROCESSO anonimizada (owner full · externo estruturado opt-out)

- Status: **Aceito** (implementado neste bloco) · Data: 2026-06-02 · Decisores: dono + squad (architect)
- Onda: retroalimentação do framework (v1.39.0) · Tipo: **EMENDA/estende** — funde no `execution_report.py` (ADR-038) e reusa `anonymize.py`/`export-clean.py` (incidente 2026-05-31); **realiza** o ADR-048 (owner tier) e o **estende** com o tier externo. Net-gain régua §0: cláusula (c) — destrava aprendizado de processo a partir de instalações de terceiros, hoje inalcançável, sem novo subsistema.
- Política: **EMENDA** o ADR-048 (§Implementação: de "Pendente" para "implementado e estendido por ADR-052"). Relaciona: ADR-038 (execution_report), ADR-026 (project_report/tokens), ADR-030 (consistency-gate), ADR-049 (tiers de distribuição premium/baseline), incidente de vazamento 2026-05-31 (postura de anonimização-como-gate), ADR-005 (execution-modes).

## Contexto

O placar gate×achado (ADR-038) foi o insumo que mais acelerou o framework. Hoje ele é gerado **só no repo do mantenedor, sob invocação**. Dois gaps:

1. **Owner (ADR-048, Proposto, nunca implementado):** todo bloco no privado deveria gerar o report **automaticamente**, sem cobrança.
2. **Externo (novo):** instalações de **terceiros** (public/non-admin/premium) executam o framework e **batem nos mesmos pontos de falha** — gate que não disparou, hook que falhou, prosa que não pegou, onde o usuário teve de corrigir. Esse sinal é ouro para melhoria contínua, mas o framework **não tem como recebê-lo** (é um repo clonado, sem servidor) e **não pode** coletar conteúdo de terceiros (lição do incidente 2026-05-31: regex só anonimiza tokens conhecidos, não PII arbitrária de um estranho).

**Restrição inviolável (dono, 2026-06-02):** *sem risco de vazamento, dados anonimizados, foco nos pontos de falha / decisão / gate (processo, abordagem, método) — não no conteúdo de domínio.*

## Decisão (1 frase ativa)

Tornar o `execution_report.py` **dois-tiers com detecção por invariante**: se `docs/_private/` existe (= repo-fonte do mantenedor; o `export-clean` o remove de TODA distribuição) → **tier OWNER** (relatório full, sem filtro, sem anonimização, gravado em `docs/_private/_intake/`); senão → **tier EXTERNAL** (telemetria **só de sinais de PROCESSO codificados** — sem texto livre, sem conteúdo de domínio — validada por **whitelist de schema** + heurística anti-PII + backstop de anonimização, gravada em `telemetry/`, **opt-out** por switch, para o usuário **commitar/PR no próprio fork se quiser**).

## Por que o detector é por presença de `docs/_private/` (e não flag/config)

`docs/_private/` é removido pelo `export-clean.py` (`STRIP_BEFORE`) em **toda** distribuição. Logo sua presença é prova de que a árvore é o repo-fonte do dono — invariante que **não pode ser burlado por config** e não exige nova flag manual. Owner → full; ausente → external. (ADR-049: as distribuições premium/baseline também não têm `_private/` → caem corretamente no tier externo.)

## Tier EXTERNAL — como "zero vazamento" é gate, não confiança

O payload externo é uma **whitelist**: cada linha não-comentário casa `^<chave>: <valor>` onde a chave é de um vocabulário fixo e o valor é **enum controlado | inteiro | versão | hash opaco | "NÃO MEDIDO"**. Texto livre/parágrafo/prosa = **FAIL** de validação. Três camadas (defesa-em-profundidade, lição do incidente):

1. **Schema-whitelist** (`validate_report(tier="external")`): rejeita qualquer linha fora do esquema codificado. PII de terceiro não passa porque não há campo de texto livre onde caiba.
2. **Heurística anti-PII**: rejeita e-mail, CPF/CNPJ, telefone, ou string longa entre aspas mesmo dentro de um slug.
3. **Backstop de anonimização**: quando disponível (`anonymize.py`/`--sensitive`), roda como rede final. *Nota:* o map sensível é stripped das distribuições (ADR-incidente) — por isso a garantia primária no campo é o **schema-whitelist**, que não depende do map.

**Foco no que o dono pediu:** os campos são `gates_fired`, `failure_points` (mecanismo hook/gate/tool/prose + id + tipo de falha + junção), `correction_events` (rewind/override/redirect/reject/clarify + junção + turno), `retrabalho`, `route`, `execution_mode`. **Nenhum** campo de conteúdo/domínio.

## LGPD / consentimento (base legal) + o LOOP de recebimento

Payload estruturado de processo = **não é dado pessoal** → **fora do escopo da LGPD** (Art. 12 — dado anonimizado não é dado pessoal). Por isso **opt-out documentado** basta para a *geração* (cláusula em `LICENSE`/`SECURITY.md`/`TELEMETRY.md` + ciência ao baixar) — **sem popup**. Switch de desligar a geração: `.claude/no-telemetry.lock` (projeto) ou `~/.claude/no-telemetry.lock` (global) ou env `FRAMEWORK_NO_TELEMETRY=1`. Owner tier ignora o switch (é o repo privado do próprio dono).

**Loop de recebimento (decisão do dono, 2026-06-02 — "eu, no repo master, recebo o relatório dele, com consentimento"):**
1. O usuário externo gera o relatório em `telemetry/` do **seu clone/fork** (opt-out respeitado).
2. Como o arquivo é **estruturado e legível**, ele **revisa** exatamente o que vai enviar.
3. Ele abre um **PR para o repo master** (`fabriciopsouza/metacognition-framework`). **Esse PR É o consentimento** — ato explícito, informado e específico (LGPD Art. 8, embora o dado já seja não-pessoal). **Nenhuma transmissão automática.**
4. O dono **recebe** os relatórios em `telemetry/` do master (zona de pouso), revisa/aceita o PR e agrega para retroalimentar o framework.

Esse desenho dá consentimento **mais forte** que opt-out: o usuário vê e submete o próprio arquivo. O opt-out cobre quem nem quer gerar; o PR cobre quem quer contribuir.

## Alternativas consideradas (≥3)

1. **Status quo (só owner, sob invocação).** Não aprende de terceiros nem mecaniza o privado. **Rejeitada — é o gap.**
2. **Coletar resumos de texto livre anonimizados por regex.** Regex não pega PII desconhecida de estranho → herda o incidente 2026-05-31. **Rejeitada** (decisão do dono: só estruturado).
3. **Endpoint de telemetria automático (servidor).** Exige infra + política de privacidade + vira controlador de dados de terceiros (exposição LGPD máxima). **Rejeitada** (decisão do dono: auto-commit no fork + PR opt-in; sem servidor).
4. **Dois tiers no mesmo tool, schema-whitelist + opt-out + detector por `_private/` (ESCOLHIDA).** Prós: reusa execution_report/anonymize, zero infra, garantia por whitelist (não por confiança), fora da LGPD. Contras: menos rico que texto livre; sinal depende do usuário commitar (aceito).

## Consequências

**Positivas:** privado mecaniza o report (ADR-048 realizado); terceiros podem retroalimentar pontos de falha **sem qualquer risco de vazamento** (whitelist); base legal limpa (não-pessoal → opt-out). **Negativas/limite:** telemetria externa só chega se o usuário commitar/PR (sem transmissão automática — por decisão); tokens seguem "NÃO MEDIDO" sem telemetria de host (herdado do ADR-038); o sinal é categórico, não narrativo. **Trigger cross-modo:** wirado no `docops §Encerramento` (mandatório, funciona em non-admin sem hooks) + dimensão fail-soft no `consistency-gate`; **não** depende de hook de runtime (alt 2 do ADR-048).

## Implementação (ponteiro)

- Branch deste bloco · 2026-06-02 · grep `execution_report` / `detect_tier` / `tier="external"`.
- Artefatos: `tools/execution_report.py` (tiers + whitelist + anti-PII + opt-out + detector), `tools/test_execution_report.py` (casos novos), `TELEMETRY.md`, cláusula em `SECURITY.md`/`README.md`/`LICENSE`/`NOTICE`, wiring `docops/SKILL.md` §Encerramento (corrige path `docs/_intake`→`docs/_private/_intake`) e `consistency-gate`. DONE quando: owner gera full em `docs/_private/_intake`; externo gera estruturado validado por whitelist em `telemetry/`, respeitando opt-out. [CONFIRMADO após testes]
