# ADR 041 — Sicofância como dimensão de teste de 1ª classe (canário adversarial)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.26.0) · Tipo: **novo** (1 canário) — net-gain por destravar verificação inalcançável: hoje a heterogeneidade do QA (ADR-018) é processo sem teste que a prove.
- Origem no plano: item 9 (`[GEMINI]` contribuição válida + `[campo]` o agente concordou consigo ao validar a coluna errada por bater o alvo). Relaciona: ADR-035 (anti-viés-oráculo), ADR-018 (QA heterogêneo turno único), ADR-040 (CI).

## Contexto

Sicofância = falha de limite entre **alinhamento social** e **integridade epistêmica**: o crítico
"concorda com o número bonito". O QA heterogêneo (ADR-018) existe como processo, mas **não havia teste
que provasse que o crítico discorda quando deve**. No incidente, bater o valor-alvo validou a coluna
errada (viés de auto-aprovação).

## Decisão (1 frase ativa)

Criar **`tools/test_sycophancy.py`** — canário adversarial que alimenta o gate com uma "entrega" que
**bate o número-alvo mas tem erro semântico plantado** (mapeamento para a coluna-irmã que atinge o alvo
porém é só um componente, **sem registro**) e exige que o gate **reprove**; se aprovasse (concordou com
o resultado bonito), FAIL — reusando o mecanismo do ADR-035 (`check_field_mapping`) como prova determinística.

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** A heterogeneidade fica como promessa não-medida. **Rejeitada — é o gap.**
2. **Rodar um LLM-juiz no CI para medir sicofância.** Não-determinístico, caro, depende de telemetria/modelo no CI. **Rejeitada** — o canário tem de ser binário e offline.
3. **Canário próprio que reimplementa um "detector de sicofância".** Duplicaria lógica; a sicofância concreta do incidente É "abençoar mapeamento não-registrado que bate o alvo". **Rejeitada** — reusar `check_field_mapping` (ADR-035) é a régua §0 (não duplicar).
4. **Canário que reusa o gate de campo-fonte com erro plantado (ESCOLHIDA).** Prós: determinístico, offline, liga sicofância ↔ anti-viés-oráculo, prova que o gate discorda do número bonito. Contras: prova só o **erro plantado conhecido**.

## Consequências

**Positivas:** a heterogeneidade gerador↔crítico ganha um teste que a prova; "aprovou o número bonito"
vira FAIL de canário. **Negativas:** nenhuma estrutural (reusa mecanismo existente). **Riscos/limite
declarado:** o canário prova que o gate reprova o erro plantado conhecido; **não** prova ausência de
sicofância em casos novos (não-mecanizável) → `LIMITS.md` ("mecanizado: catch do erro plantado;
não-mecanizado: sicofância em caso novo — fica no protocolo adversarial do qa-critic, ADR-018").

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `test_sycophancy`
- Artefatos: `tools/test_sycophancy.py` (reusa `check_field_mapping.check_text`), referência na qa-critic rule #9.
- DONE quando: canário no CI; heterogeneidade gerador↔crítico documentada com o teste que a prova. [CONFIRMADO]
