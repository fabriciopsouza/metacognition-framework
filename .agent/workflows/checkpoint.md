# /checkpoint — Salvar estado (genérico)

Registra em history.md o estado atual (compaction + structured note-taking —
`_shared/metacognition-core`).

## Formato
```
## YYYY-MM-DD HH:MM — <título do bloco>
Aprovado e funcionando: <itens>
Nomenclaturas estabelecidas: <do glossário>
Decisões permanentes (ADRs): <ADR-NNN: decisão → razão>
Próximo passo: <tarefa + critério de aceite>
Riscos ativos: <risco + mitigação>
```

## Quando
Fim de bloco aprovado · antes de encerrar · ao mudar direção · a cada ≥20 turnos.

## Gatilho por faixa de ocupação (ADR-016 — v1.16.0)
Além dos gatilhos acima, dispara por **faixa medida** (degradação é gradiente, não penhasco;
fronteira inclusiva à esquerda): 🟢<50% normal · 🟡50–69% anotar · 🟠70–84% **produzir digest** ·
🔴≥85% **compactar a partir do digest** + 5 arquivos recentes. Medida: IDE = % real (`/context`);
chat = proxy `chars÷3` (alarme de fumaça, ±20–40%).

**Digest (faixa 🟠/🔴)** = Pacote de handoff (`_shared/metacognition-core` §Pacote / Princípio 14)
estendido com campos de compaction + carimbo de faixa — superset, não artefato paralelo.
**Formato: `docs/specs/_template-digest/digest.md`** (fonte única; não relistar campos aqui).
Teste binário (herda P14): a próxima sessão começa sem perguntar nada de volta?

> **ADR-011 (v1.12.0):** `/checkpoint` é **save-point + gate RRC** (ADR-010 §ii) — NÃO invoca process-critic adversarial automaticamente. Process-critic (qa-critic adversarial em subagente isolado, com poder de rewind cascata) é mandatório no FINAL DE BLOCO APROVADO (release, ADR aceito, spec fechada, feature delivered) e on-demand sob escalação do dono. **Backstop opcional em /checkpoint** ativado explicitamente pelo dono ("rode process-critic agora") — não default.

## Aprendizado (ex-G9 / ADR-007)
Se gatilho de fracasso disparou (anti-loop, qa-critic reprovou ≥2×, file-first violado, estouro de token, [CONFIRMADO] que se revelou falso) → anotar em `history.md` sob `## Aprendizado`. Single-writer (orquestrador), append-only com timestamp.

**Firewall:** notas de aprendizado são **inertes** — só viram comportamento via skill/regra destilada, aprovada via ADR e mergeada. Nota errada não propaga.

## Method-Audit autônomo (ADR-009)
Em sessão substantiva (≥10 turnos — critério inline; OU contexto **declarado pelo discovery** como regulado/alto-risco — ADR-010), o PMO emite **0-3 method-audit notes** em `history.md ## Aprendizado` no formato: `Method-audit: <gap observado> · Causa-raiz: <skill/regra ausente ou fraca> · Proposta (lean): <artefato a editar ≥ criar>`. Sinais a captar: norma citada sem vigência, regra despriorizada sem semântica, correções repetidas do dono sobre mesmo padrão, violação régua §0, loops/retrabalho, vazamento cross-projeto (importação de norma/convenção de outra sessão sem declaração no projeto atual — ADR-010). Firewall preservado.

## Read-and-Review-for-Coherence (RRC) — gate de saída obrigatório (ADR-010 v1.11.0)
**Antes de declarar `/checkpoint` concluído**, o agente DEVE executar pass RRC e reportar em formato binário no próprio checkpoint:

```
## RRC (ADR-010) — coherence pass
- Artefatos lidos: <lista nominal — não só editados; inclui ADRs vinculadas, CLAUDE/AGENTS/README, CHANGELOG, history "Em aberto", _shared/ dependências, web/index.html, PROMPT-CHAT-WEB se afetado>.
- Verificações: versões em sync (README × CHANGELOG × web × tag): [PASSA/FALHA] · Refs cruzadas válidas (ADR-N existe, arquivo/linha citada existe): [PASSA/FALHA] · Nomenclatura consistente: [PASSA/FALHA] · Sem contradições semânticas entre documentos: [PASSA/FALHA] · **Contagens em sync** ("N passos", "N seções obrigatórias", N de qualquer enumeração igual em todos os arquivos que mencionam): [PASSA/FALHA] · Anti-vazamento cross-projeto (sem norma/convenção importada sem declaração no projeto): [PASSA/FALHA].
- Inconsistências corrigidas neste checkpoint: <lista ou "nenhuma">.
- Veredito: PASSA / FALHA → se FALHA, NÃO declarar "pronto"; corrigir e re-rodar RRC.
```

**Atalhar RRC = não-sênior**. Se a sessão era trivial (1 arquivo editado, sem ADRs, sem release), o pass pode ser reportado como "trivial — N/A" justificadamente. Em release / ADR aceito / merge a main / bump de versão, RRC é mandatório com checklist binário completo.
