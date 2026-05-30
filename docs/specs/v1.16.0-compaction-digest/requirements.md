# Requirements — v1.16.0 Compaction por threshold + digest (Onda 2)

## Objetivo
Trocar o gatilho qualitativo de compaction por **faixas medidas** e formalizar o **digest
persistente** (= §Pacote de handoff estendido) — importando do JARVIS a medida de contexto, filtrada
pela régua §0 (números = parâmetro, não dogma). EMENDA ao Princípio 8.

## Escopo IN
- Edição `AGENT-FRAMEWORK.md §2.5` alavanca 1 (Compaction) — faixas + proxy chat + ponteiro do digest.
- Extensão `.agent/workflows/checkpoint.md` — gatilho por faixa + ponteiro do template do digest.
- Template `docs/specs/_template-digest/digest.md` (5 campos [P14] + extensões de compaction).

## Escopo OUT
- Medidor automático de % no IDE (usa o nativo `/context`).
- Calibração empírica de percentuais e divisor ÷3 (micro-benchmark — [DESCONHECIDO], follow-up).
- Encaixe formal do digest em ALCOA+ — [DESCONHECIDO], não-bloqueante.

## Requisitos
- REQ-1: As 4 faixas com ações nomeadas substituem o gatilho qualitativo no §2.5 (alavanca 1).
- REQ-2: Proxy `chars ÷ 3` declarado para o chat como alarme de fumaça.
- REQ-3: Percentuais marcados escolha de engenharia [INFERIDO]/ajustável (P2 prova forma, não cortes).
- REQ-4: Digest inclui os 5 campos canônicos do §Pacote (marcados [P14]) + extensões — superset.
- REQ-5: Digest NÃO redefine o §Pacote — referencia/estende (anti-duplicação, régua §0).
- REQ-6: Nenhum módulo `_shared/` novo; só edições + 1 template.
- REQ-7: Agnóstico de domínio.

## Bloqueadores honestos (P11)
- ÷3 e 50/70/85 não-calibrados [DESCONHECIDO]; "espaço útil" no chat = estimativa grosseira.
- ALCOA+ do digest [DESCONHECIDO].
