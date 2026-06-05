# ADR-069 — Isolamento cross-AI: Gemini é read-only neste repo (Claude-exclusivo)

- Status: **Aceito**
- Data: 2026-06-05
- Decisores: dono + squad (architect)
- Baseado em: handoff cross-AI 2026-06-05 (Opção A+); decisão explícita do dono
- Relacionado: ADR-011 (QA adversarial), ADR-029 (doc-intake offline), ADR-015 (effect-gate)

---

## Contexto

O protocolo cross-AI (handoff 2026-06-05, "Opção A+") estabeleceu **repos completamente
separados**: cada AI toca exclusivamente o próprio repo; a troca é por **leitura local**
de `output/cross-ai/` do repo do outro (mesma máquina), sem credenciais cruzadas.

Porém o **schema de relatório** declarado no handoff (`author: "claude" # ou "gemini"`,
`verdict_per_claim`) é **ambíguo**: lido isoladamente, sugere que o Gemini escreveria
relatórios/vereditos **dentro** de `output/cross-ai/` *deste* repo. Isso contradiz a
Opção A+ e o princípio do dono de que **este repo é Claude-exclusivo**.

Há ainda um **segundo "Gemini"** no repo que NÃO é colaborador e não deve ser confundido:
o Gemini como **alvo de deploy** do prompt público (`_meta/eval-web-gemini.md`, NFR-1) —
ali Gemini é plataforma-destino, não escreve nada no repo.

## Decisão (1 frase ativa)

**O Gemini é read-only neste repositório: nunca escreve, comita ou "comenta" aqui — seus
relatórios e vereditos vivem no repo DELE, e o Claude os consome por leitura local (subagente
`explorer` read-only); a direção inversa (Claude→Gemini) é simétrica e fora do escopo deste repo.**

## Alternativas consideradas

### Alt A (ESCOLHIDA): Isolamento estrito + leitura cross-pasta
**Prós:** honra Opção A+; zero credencial cruzada; superfície de escrita = só o dono/Claude;
o subagente `explorer` (read-only por design, ADR-011) é o mecanismo natural de ingestão;
audita via `output/cross-ai/processed.json` (anti-loop DAG).
**Contras:** troca depende das duas pastas na mesma máquina (ou clone manual do repo Gemini).

### Alt B: Pasta compartilhada de dropbox de relatórios (Gemini escreve em `output/cross-ai/` daqui)
**Prós:** troca sem clone.
**Contras:** quebra "Claude-exclusivo"; Gemini ganha escrita no repo; risco de poluição/loop;
contradiz a Opção A+ já decidida. **Rejeitada pelo dono.**

### Alt C: Não fazer (manter o schema ambíguo)
**Prós:** zero esforço.
**Contras:** ambiguidade vira bug — uma sessão futura pode deixar o Gemini escrever aqui
"porque o schema permitia". Prosa→mecanismo (ADR-021/027) exige desfazer a ambiguidade.

## Consequências

**Positivas:**
- Fronteira de confiança explícita: a única escrita neste repo é do dono/Claude.
- Postura adversarial preservada (ADR-011): Claude **lê e critica** o Gemini, não co-edita.
- Desambigua os dois "Gemini" (colaborador externo × alvo de deploy do prompt público).

**Negativas / Limites:**
- A reciprocidade (Claude read-only no repo Gemini) é **acordo**, não mecanismo executável daqui —
  fora do nosso controle; documentado, não garantido por código.
- Troca exige a pasta/clone do repo Gemini acessível localmente (declarado em `.claude/cross-ai-repos.json`).

## Implementação (ponteiro após aceito)
- Schema corrigido no protocolo: handoff cross-AI — campo `author` deixa explícito que
  `gemini` só aparece em relatórios **lidos do repo Gemini**, nunca escritos aqui.
- Guia operacional: `guia/RELATORIOS-RECUPERAR-APLICAR-CRITICAR.md` (ciclo read-only).
- grep: `cross-ai-repos.json`, `output/cross-ai/processed.json`, `explorer`
- Pendência: `.claude/cross-ai-repos.json` (criar quando o path/URL do repo Gemini for declarado).
