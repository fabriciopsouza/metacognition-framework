# ADR-070 — repo-identity-gate (advisory, ancestry-first): classificar o repo atual antes de escrever

- Status: **Aceito** (ratificado por HITL no merge — 2026-06-06)
- Data: 2026-06-05
- Decisores: dono + squad (architect)
- Baseado em: incidente confusão-repos 2026-06-05 (Ação 6); decisão do dono
- Relacionado: ADR-069 (isolamento por IA, irmão), ADR-047 (gates inline non-admin), ADR-027 (route-gate/wiring), ADR-022 (mission-gate)

---

## Contexto

No incidente 2026-06-05 uma sessão **confundiu** três pastas homônimas — o **clone velho**
(OneDrive v2.2, linhagem disjunta), a **sombra/export** (premium) e o **master vivo** — e
disso concluiu "o master morreu / virou premium", **quase deixou trabalho não-commitado
desprotegido** e **escreveu no repo de outra IA**. A causa foi não haver, na abertura da
sessão, uma **classificação explícita do repo atual**. O dono pediu um guard que torne o
incidente **impossível de repetir silenciosamente**.

**Restrições duras (honestidade — não overclaimar):**
- **Hooks morrem calados nesta máquina** (Kaspersky AAC veta `check-repo-sync`/`check-core-agnostic`
  há dias). Um hook SessionStart que rode git tem o **mesmo failure mode** → não pode ser a única
  linha de defesa, nem ser anunciado como "bloqueio garantido".
- **O marker no repo é forjável por cópia:** um export/clone **copia `.repo-identity.json` verbatim**
  e passaria a alegar `role: master`. Logo o marker é **dica**, não autoridade.
- **Master × export-fiel no mesmo commit são indistinguíveis** por ahead/behind. A honestidade
  exige **declarar AMBÍGUO**, não fingir certeza.

## Decisão (1 frase ativa)

**Adotar um `repo-identity-gate` ADVISORY e agnóstico de IA que, na abertura da sessão,
classifica o repo atual via ANCESTRALIDADE GIT primeiro (origin + merge-base/ahead-behind),
usando o marker `.repo-identity.json` apenas como dica corroborante, anuncia o veredito em 1
linha e — quando o repo NÃO é o master canônico ou é AMBÍGUO — exige confirmação humana antes
de escrever/commitar, sem alegar enforcement que esta máquina não sustenta.**

## Classificação (ancestry-first; marker é dica, nunca autoridade)

Ordem de decisão (git manda; marker corrobora ou levanta alerta de divergência):

Ordem avaliada de cima para baixo (primeiro que casa vence):

| Veredito | Sinal (autoritativo) | Confiança |
|---|---|---|
| `FOREIGN` | sem `.git`, ou `origin` ≠ `canonical_remote` do marker | alta |
| `CLONE-VELHO/DIVERGENTE` | sem `merge-base` com `origin/<branch>`, **ou** `behind > N` | alta — se marker diz "master" aqui → **ALERTA marker forjado/stale** |
| `SOMBRA-EXPORT` | **marker `role: shadow`** (carimbado pelo `export-clean.py` — trava física) **OU** commit `…@<hash>` (sinal fraco secundário) | **alta** com marker; média só com commit |
| `MASTER-CANÔNICO` | **marker `role: master`** **e** `origin == canonical_remote` **e** não-divergente | média |
| `AMBÍGUO` | **default seguro** — qualquer outro caso (sem marker de master confiável, sem sinal de shadow) | baixa → **escrita exige confirmação** |

- **O falso-MASTER é fechado por MECANISMO, não por heurística** (qa-critic ALTO): o `export-clean.py`
  **carimba `role: shadow`** em toda árvore exportada → uma sombra/export **nunca** chega como `master`.
  Logo `marker role:master` é confiável o suficiente para promover a MASTER. A regex de commit-message
  (`…@<hash>`) vira só **sinal fraco secundário** (não-confiável sozinha; era código quase-morto).
- **AMBÍGUO é o default, não exceção:** sem `role:master` confiável e sem `role:shadow`, o git **não
  distingue** master de export-fiel → AMBÍGUO → escrita pede confirmação. Antes o `else` caía em MASTER
  (bug: export com commits locais virava MASTER). Corrigido.
- **Regra de ouro:** se o marker diz `master` mas o git diz DIVERGENTE/atrasado, **vence o git**.
- **`N`** (limiar behind) no marker (`stale_behind_threshold`, default 50).
- **Residual documentado:** cópia manual/maliciosa que re-carimbe `role:master` fora do `export-clean`
  seria promovida — fora do fluxo normal; o caso comum (clone velho) é pego por divergência.

## Marker `.repo-identity.json` (raiz do repo — dica declarada, versionada)
```json
{
  "schema_version": "1.0",
  "role": "master",                       // master | shadow | clone-archive
  "ai_owner": "claude",                   // IA dona deste repo (agnóstico; ADR-069)
  "canonical_remote": "https://github.com/fabriciopsouza/metacognition-framework",
  "canonical_branch": "main",
  "stale_behind_threshold": 50,
  "note": "Dica corroborante. A autoridade e a ancestralidade git; em conflito, git vence."
}
```

## Aplicação (advisory — honesta sobre o que esta máquina sustenta)

1. **Inline declare-and-apply (ADR-047) — caminho PRIMÁRIO nesta máquina:** o agente roda
   `python tools/repo_identity.py` no 1º turno e **anuncia em 1 linha** o veredito. Python
   on-demand **não** é barrado pelo Kaspersky (só hooks que spawnam). Funde-se ao route-gate
   (já declara rota no 1º turno) — **uma linha a mais, zero arquivo de wiring novo** (régua §0).
2. **Hook SessionStart (onde a máquina permitir):** mesmo classificador, oportunístico.
   **Fail-open e anunciado**; se vetado, o passo 1 cobre. **Não é a única defesa.**
3. **Write/commit nudge (advisory, NÃO bloqueio):** se o veredito ≠ `MASTER-CANÔNICO` (ou for
   `AMBÍGUO`), antes de escrever conteúdo/commitar o agente **declara o risco e pede confirmação
   humana** (encarna ADR-069: cada IA só escreve no próprio repo canônico). Honestidade: dado
   Kaspersky + non-admin, isto é **gate humano declarado**, não enforcement de runtime — **não
   anunciar como "bloqueia"**.
4. **Untracked-at-risk nudge:** ao abrir/encerrar, se houver artefato de alto valor não-rastreado
   (`git status` com `docs/adr/*.md`, `.mailmap`, etc.) → avisar. **Teria pego o ADR-069 antes do risco.**

## Alternativas consideradas

### Alt A (ESCOLHIDA): advisory ancestry-first + inline primário + hook oportunístico
**Prós:** honesto com a restrição Kaspersky; não-forjável (git manda); funde no route-gate (§0);
declara ambiguidade em vez de fingir certeza.
**Contras:** advisory ≠ enforcement — depende de o agente rodar e o humano confirmar.

### Alt B: hook SessionStart como ÚNICO enforcement "que bloqueia"
**Contras:** morre calado no Kaspersky (mesmo failure mode dos hooks já vetados); marker-first seria
forjável; **overclaim** ("bloqueia") que a máquina não sustenta. **Rejeitada** (foi a falha-modo do incidente).

### Alt C: marker-first (confiar no `.repo-identity.json`)
**Contras:** o marker viaja no clone/export → forjável por cópia; reintroduz exatamente a confusão. **Rejeitada.**

### Alt D: não fazer
**Contras:** o incidente repete silenciosamente; o dono pediu explicitamente o guard. **Rejeitada.**

## Consequências

**Positivas:**
- Identidade do repo **anunciada em 1 linha** na abertura — o incidente fica visível, não silencioso.
- Ancestry-first **fecha o vetor do marker forjado**; ambiguidade é **declarada**, não mascarada.
- Reusa route-gate/inline (§0): custo marginal ~1 chamada Python + 1 linha; zero wiring novo obrigatório.
- Untracked-nudge teria evitado o risco do ADR-069.

**Negativas / Limites (honestidade):**
- **Advisory**, não enforcement: nesta máquina é gate humano declarado (Kaspersky veta hooks).
- Master × export-fiel no mesmo HEAD permanece **AMBÍGUO** por git — resolvido só pelo marker+contexto
  (e o marker é dica). Mitigação: export deve carimbar `role: shadow` no próprio `.repo-identity.json`.
- Heurística de SOMBRA por commit-message é frágil (só rebaixa confiança).

## Implementação (ponteiro após aceito)
- branch `feat/adr-070-repo-identity-gate` · data `2026-06-05`
- artefatos: `.repo-identity.json` (marker do master), `tools/repo_identity.py` (classificador on-demand),
  `tools/export-clean.py` (`stamp_shadow_identity` — **trava física** que carimba `role: shadow` no export)
- grep: `repo_identity`, `repo-identity`, `stale_behind_threshold`, `stamp_shadow_identity`
- testado: master=MASTER-CANONICO (exit 0); OneDrive=CLONE-VELHO/DIVERGENTE; premium=SOMBRA-EXPORT (exit 2);
  export-clean produz `role: shadow`. Achados ALTO do qa-critic (falso-MASTER, SOMBRA código-morto,
  AMBÍGUO) corrigidos.
- Pendência: `role: clone-archive` no clone OneDrive (Ação 4 do incidente — confirmar com o dono).
