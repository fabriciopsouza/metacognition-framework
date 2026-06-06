# ADR-069 — Isolamento por IA (cada IA escreve só nos próprios repos) + descoberta de handoff via hub privado

- Status: **Aceito** (ratificado por HITL no merge — 2026-06-06)
- Data: 2026-06-05
- Decisores: dono + squad (architect)
- Baseado em: handoff cross-AI 2026-06-05 (Opção A+); incidente confusão-repos 2026-06-05; decisão do dono
- Relacionado: ADR-011 (QA adversarial), ADR-029 (doc-intake offline), ADR-030 (consistency-gate), ADR-063 (repo central via PR), ADR-047 (non-admin gates inline), ADR-070 (repo-identity-gate, irmão)

---

## Contexto

O protocolo cross-AI (handoff 2026-06-05, "Opção A+") estabeleceu **repos separados por IA**.
A formalização precisa ser **simétrica e agnóstica de IA** — vale para Claude, Gemini e
**qualquer IA/framework que venha a existir**, não é uma regra sobre o Gemini. Dois problemas:

1. **Ambiguidade de escrita.** O schema de relatório (`author: "claude" # ou "gemini"`,
   `verdict_per_claim`) sugeria que uma IA escreveria **dentro** do repo de outra. Isso
   quebra o princípio do dono: **cada IA é dona e escreve só nos SEUS repos canônicos**;
   nenhuma IA escreve no repo de outra. (Nota: há um segundo "Gemini" no repo que NÃO é
   colaborador — o Gemini como **alvo de deploy** do prompt público, `_meta/eval-web-gemini.md`,
   NFR-1; não confundir com o Gemini-agente.)

2. **Descoberta quebrada (incidente 2026-06-05).** A troca por **leitura local** da pasta da
   outra IA é **pull, manual e local-only**: uma sessão só enxerga um handoff se o humano
   **provocar**, e não funciona **cross-máquina nem cross-usuário** (exige os dois repos
   clonados na mesma máquina). O incidente provou o gap — o relatório ficou em
   `premium/output/cross-ai/` e só chegou por cutucão humano. Pior: a sessão que o gerou
   **escreveu no repo de outra IA** (violou o princípio 1).

## Decisão (1 frase ativa)

**(a) Cada IA/sessão escreve EXCLUSIVAMENTE nos seus próprios repos canônicos — nenhuma IA
escreve, comita ou comenta no repo de outra (Claude, Gemini ou futura), simetricamente; e
(b) a descoberta de handoff cross-AI/cross-sessão passa a ser um HUB PRIVADO compartilhado,
onde cada IA deposita mensagens via PR (branch/pseudônimo próprio = ownership) e cada sessão
varre o hub no início (scan) — leitura automática e cross-máquina, sem dar escrita a ninguém
no repo do outro.**

## Alternativas consideradas

### Alt A (ESCOLHIDA): Isolamento simétrico por IA + descoberta via hub privado date-shard
**Prós:** princípio agnóstico de IA (escala para "frameworks que venham a existir"); ninguém
escreve no repo do outro; resolve cross-máquina/cross-usuário (o hub é o ponto comum, não a
mesma máquina); ownership por PR/pseudônimo (ADR-063); leitura é adversarial (ADR-011 — ler ≠
aceitar); layout date-shard + facets-no-índice evita taxonomia subjetiva (agnosticismo, ADR-010/020).
**Contras:** depende de um hub acessível (rede/clone); a reciprocidade (cada IA respeitar o
read-only do repo da outra) é acordo documentado, não mecanismo executável de dentro de um repo.

### Alt B: Cada IA escreve em `output/cross-ai/` do repo da outra (schema original)
**Contras:** quebra o isolamento por IA; cross-write/cross-credentials; foi a raiz do incidente
(sessão premium escreveu `claude_to_gemini_*.md` DENTRO do repo Gemini). **Rejeitada.**

### Alt C: Leitura local da pasta da outra IA (Opção A+ original, sem hub)
**Contras:** local-only; invisível sem provocação humana; não escala cross-máquina. **É o gap
que esta decisão fecha.**

### Alt D: Hub PÚBLICO do ADR-063 (corpus anonimizado) como destino dos handoffs
**Contras (anti-PII):** o ADR-063 é público + anonimizado + anti-PII; handoff operacional carrega
`machine_id`, paths locais, detalhes de incidente → **pseudônimo + machine_id estável = de-anonimização**.
Reusa-se o **mecanismo** do ADR-063 (PR + append-only + CI re-valida), mas num **hub PRIVADO**
separado, não no corpus público. (Crítica adversarial 2026-06-05.)

## Layout do hub (decisão — date-shard + facets, sem taxonomia de pastas)

`filesystem = storage; índice = router`. Nada de pasta-por-assunto nem pasta-por-fonte
(taxonomia subjetiva fragmenta threads e fere o agnosticismo). A única subpasta com semântica
é o ciclo de vida:

```
hub-privado/                         ← repo/pasta PRIVADA compartilhada (não o corpus público ADR-063)
  inbox/AAAA/MM/DD/                  ← aberto (date-shard objetivo)
    <thread>__from-<ia>__to-<dest>__<sha8>.md
  archive/AAAA/MM/DD/                ← selado (append-only após selar)
  INDEX.md                          ← gerado por glob no scan (NÃO manifest-CI por ora — ver §0)
```

- **Assunto = `tags[]` no frontmatter (facet). Fonte = campo `from` + token no filename (facet). Nunca pasta.**
- **Filename carrega tokens p/ glob barato** (descoberta sem abrir arquivo).
- **`manifest.json` gerado por CI fica DIFERIDO** (régua §0): com poucas IAs / 1 dono, `glob + INDEX.md`
  derivado no scan basta. Promover a manifest-CI (padrão ADR-029/030) só quando N de mensagens/IAs justificar.

### Frontmatter requerido (consolida o schema cross-ai, agnóstico de IA)
`schema_version, report_id (=sha256[:8] do corpo), thread_id, from, to[], date, status(open|sealed), kind`.
Opcionais: `analyzed_reports[]` (anti-loop DAG), `tags[]`, `supersedes/superseded_by`. `from`/`to` usam
**ids de IA/sessão** (`claude-master`, `gemini`, `<futura>`), não nomes hardcoded no núcleo. **`machine_id`
só no hub PRIVADO** (nunca migra para o corpus público ADR-063).

### Algoritmo de scan (leitura ≠ aceitação — ADR-011)
1. atualizar/abrir o hub; 2. `glob` em `inbox/**` filtrando `to ∋ meu_id ∨ all` **e** `status==open`
**e** `report_id ∉ .cross-ai-seen.json`; 3. anunciar em 1 linha (`📥 N handoff(s) aberto(s)`);
4. **ler é automático; AGIR exige passar pelo qa-critic adversarial** (anti prompt-injection cross-AI —
nunca aceitar contribuição externa na 1ª passagem); 5. responder via PR **no próprio repo/branch**; selar
move p/ `archive/`. Fail-open e anunciado (filosofia de hooks do núcleo): hub inacessível → avisar 1×, seguir.

## Consequências

**Positivas:**
- Princípio **agnóstico de IA**: a única escrita num repo é da IA dona dele (Claude, Gemini, futura).
- Descoberta **automática e cross-máquina** sem cross-write (resolve o gap do incidente).
- Postura adversarial preservada: ler é automático, **agir passa pelo qa-critic** (ADR-011).
- Desambigua os dois "Gemini" (colaborador externo × alvo de deploy do prompt público).

**Negativas / Limites (honestidade):**
- Reciprocidade (cada IA respeitar o read-only do repo da outra) é **acordo**, não enforcement daqui.
- Hub privado é nova infra leve; mantida mínima (glob+INDEX) até N justificar manifest-CI.
- `report_id` de 32 bits (sha256[:8]) — colisão improvável neste volume; rever se escalar.

## Implementação (ponteiro após aceito)
- branch `feat/adr-069-cross-ai-isolation` · data `2026-06-05`
- grep: `cross-ai`, `cross-ai-seen.json`, `hub-privado`, `repo-identity` (ADR-070 irmão)
- Pendências (não-bloqueantes): provisionar o hub privado; `.cross-ai-seen.json` por sessão;
  corrigir o schema de sync do Gemini (`02-cross-ai-sync.md`) p/ apontar ao hub, não ao clone velho.
