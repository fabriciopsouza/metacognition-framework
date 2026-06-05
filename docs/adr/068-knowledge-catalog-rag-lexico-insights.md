# ADR-068 — Catálogo de insights + RAG léxico sobre corpus de relatórios (knowledge-catalog)

- Status: **Aceito**
- Data: 2026-06-05
- Decisores: dono + squad (architect/developer)
- EMENDA de: ADR-062 (execution-report), ADR-029 (doc-intake offline)
- Baseado em: discovery J0→J1 sessão 2026-06-05

---

## Contexto

ADR-062..065 construíram a **camada de coleta**: relatórios gerados em estrutura
semântica (seções obrigatórias: gaps · melhorias · boas-práticas · lições-por-skill ·
detecção framework×humano), anonimizados e publicados via PR num corpus central
(`metacognition-exec-reports`). A camada de **retroalimentação** — catalogar →
indexar → recuperar insights relevantes → surfacear durante sessões — não existe.

Sem retroalimentação, os relatórios acumulam mas o framework NÃO aprende de si
mesmo de forma mecanizada. O princípio 11 (observação meta-cognitiva — ADR-010)
e o princípio 13 (QA adversarial — ADR-011) dependem de que os achados dos
relatórios ALIMENTEM as sessões seguintes, não fiquem soterrados em arquivos.

**Restrições duras (do contexto):**
- Kaspersky AAC veta hooks que spawnam Python → hook NÃO pode chamar processo externo.
- Zero dep externa no core offline (ADR-029 decisão #4) → sem embeddings, sem LLM no retrieval.
- Corpus inicial pequeno (1–2 relatórios) → overclaiming "insight rico de imediato" = overclaim;
  valor cresce com uso (declarado em LIMITS).

---

## Decisão

Implementar `tools/knowledge_catalog.py` com três modos CLI:

| Modo | Comando | O que faz |
|------|---------|-----------|
| Build | `--build` | Parse todos os .md em `docs/_private/_intake/` → catalog.json + session-insights.md + patterns.md |
| Recall | `--recall [--context "kws" \| --from-briefing PATH]` | BM25 query offline → markdown de top-N insights |
| Patterns | `--patterns` | Agrega padrões recorrentes cross-relatório → patterns.md |

**Armazenamento:** `docs/_private/_catalog/` (gitignored, owner-only, não distribuído).

**Injeção no boot:** `inject-start-session.ps1` lê `session-insights.md` como arquivo
estático (sem spawn). Fail-soft: arquivo ausente = silêncio.

**Engine de retrieval:** BM25 stdlib puro (sem dep). Tokenização simples
(`re.findall(r'[a-z0-9a-záéíóúàâêîôûãõçü]+', text.lower())`). Parâmetros k1=1.5, b=0.75.

---

## Alternativas consideradas

### Alt A (ESCOLHIDA): Tool Python + arquivo pré-renderizado
**Prós:** zero dep; hook só lê arquivo (não spawna); fail-soft em toda a cadeia;
alinha ADR-029 padrão offline; `--recall` disponível on-demand durante sessão.
**Contras:** `session-insights.md` é contexto-livre (rebuild manual após novos relatórios).

### Alt B: Hook spawna Python por sessão (per-query)
**Prós:** context-aware desde o boot.
**Contras:** Kaspersky pode vetar spawn (mesmo failure mode de check-repo-sync/check-core-agnostic);
sem fallback garantido.

### Alt C: Embeddings vetoriais (sentence-transformers)
**Prós:** similaridade semântica rica.
**Contras:** ~500MB dep; contra ADR-029 decisão #4; não cabe no core offline.

### Alt D: Prosa no start-session (sem código)
**Prós:** zero esforço.
**Contras:** contra ADR-021/027 "prosa→mecanismo"; sem garantia de execução.

---

## Estrutura do catálogo

```
docs/_private/_catalog/          ← gitignored, owner-only
  catalog.json                   ← entradas estruturadas indexadas
  session-insights.md            ← top-N pré-renderizado para boot (hook lê)
  patterns.md                    ← padrões recorrentes cross-relatório
```

### Entrada do catálogo (por relatório)
```json
{
  "report_id": "sha256[:8]-do-path",
  "date": "2026-06-03",
  "source": "docs/_private/_intake/execution-report.md",
  "skills": ["dev", "discovery", "architect", "qa-critic", "docops"],
  "route": "squad",
  "gaps": ["texto do gap 1", "texto do gap 2"],
  "melhorias": ["melhoria 1"],
  "boas_praticas": ["boa prática 1"],
  "licoes": {"dev": ["lição 1"], "discovery": ["lição 2"]},
  "detecao": ["achado 1"],
  "tokens_full": "texto completo concatenado para BM25"
}
```

---

## Consequências

**Positivas:**
- Framework aprende de si mesmo: insights de sessões anteriores surfaceados no boot.
- Padrões agnósticos extraídos e reutilizáveis em qualquer domínio.
- Zero dep nova (stdlib puro); fail-soft em toda a cadeia.
- `--recall` on-demand: PMO pode consultar durante sessão por contexto específico.

**Negativas / Limites (honestidade — ADR-044/059):**
- Corpus inicial de 1–2 relatórios: BM25 é pobre. Valor cresce com uso → declarado em LIMITS.md.
- `session-insights.md` é contexto-livre (top-N global, não por briefing). On-demand `--recall` é
  context-aware mas requer chamada explícita do PMO.
- Anonimização do corpus central (ADR-063) remove contexto → relatórios públicos têm menos sinal
  que os OWNER; source primária = `docs/_private/_intake/`.
- Rebuild manual (`--build`) para atualizar insights quando novos relatórios são adicionados.

---

## Pendências

- [ ] ADR-029 §RAG-vetorial futuro: quando corpus > ~50 relatórios, avaliar dep de embeddings.
- [ ] Pull opcional do repo central (`metacognition-exec-reports`) como fonte secundária — deferido
  (dep de rede + auth gh; fora do escopo offline).
- [ ] LIMITS.md: adicionar linha sobre corpus inicial pequeno.
