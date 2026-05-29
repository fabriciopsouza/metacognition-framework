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
- Verificações: versões em sync (README × CHANGELOG × web × tag): [PASSA/FALHA] · Refs cruzadas válidas (ADR-N existe, arquivo/linha citada existe): [PASSA/FALHA] · Nomenclatura consistente: [PASSA/FALHA] · Sem contradições semânticas entre documentos: [PASSA/FALHA] · Anti-vazamento cross-projeto (sem norma/convenção importada sem declaração no projeto): [PASSA/FALHA].
- Inconsistências corrigidas neste checkpoint: <lista ou "nenhuma">.
- Veredito: PASSA / FALHA → se FALHA, NÃO declarar "pronto"; corrigir e re-rodar RRC.
```

**Atalhar RRC = não-sênior**. Se a sessão era trivial (1 arquivo editado, sem ADRs, sem release), o pass pode ser reportado como "trivial — N/A" justificadamente. Em release / ADR aceito / merge a main / bump de versão, RRC é mandatório com checklist binário completo.
