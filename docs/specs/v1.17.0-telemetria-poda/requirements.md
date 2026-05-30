# Requirements — v1.17.0 Telemetria mínima de processo + poda (Onda 3)

## Objetivo
Auto-observação **mínima e acionável**: converter "rewind cego" em "rewind direcionado" (P5) e dar à
régua §0 um eixo **temporal** de poda de regra (P7) — importando do JARVIS a medição, mas rejeitando
o andaime que o derrubou (11 coletores, matriz instrumentada). EMENDA aos Princípios 10 e 11.
**Coletor único** (DOSSIÊ §3): P5 e P7 num só artefato, não dois sistemas.

## Escopo IN
- ADR-017 (pai, 2 decisões): 17-A blame (P5) + 17-B poda (P7), fronteira de coletor único.
- Extensão `_shared/observability/SKILL.md` — §Telemetria mínima (2 métricas + poda Chesterton).
- Seção `## Telemetria` em `history.md` (coletor físico cross-sessão) — com 17-A e 17-B já populados desta sessão.
- Gancho em `.agent/workflows/checkpoint.md`.

## Escopo OUT
- Matriz de relevância instrumentada — **REPROVADA** (P7; logits/N+1 passes inviável).
- Dashboards, latência fina, %verde, múltiplos coletores — reprovados (P5).
- Calibração empírica de N (5–10) e da confiabilidade do tally — [DESCONHECIDO], follow-up.

## Requisitos
- REQ-1: Exatamente 2 métricas em 17-A (junção-origem do rewind + rounds qa-critic até PASS).
- REQ-2: 17-B: tally S/N + classe + poda só `andaime` (N=5–10); `salva-vidas` nunca poda por desuso.
- REQ-3: Coletor único — 17-A e 17-B na mesma seção física (`history.md ## Telemetria`), não dois sistemas.
- REQ-4: `classe` reusa o campo do contrato (ADR-013), não cria campo novo.
- REQ-5: Régua §0 — estende observability + history.md; nenhum módulo/dashboard novo.
- REQ-6: Agnóstico de domínio.
- REQ-7: Tally autorreportado marcado falível [DESCONHECIDO]; N=5–10 marcado parâmetro [INFERIDO].

## Bloqueadores honestos (P11)
- Confiabilidade do tally autorreportado [DESCONHECIDO] — cruzar com sinal externo quando possível.
- N calibrado empiricamente [DESCONHECIDO].
- Convenção OTel para "junção de governança" não é padrão [DESCONHECIDO] — atributo custom.
