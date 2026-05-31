# ADR 036 — "Teste pela porta do usuário" + verificação de ambiente limpo

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.25.0) · Tipo: **novo** (2 linters + 2 canários) — net-gain por destravar verificação inalcançável: hoje ninguém roda o entry-point como o usuário nem testa ambiente limpo.
- Origem no plano: item 4 ⭐ (`[campo]`: entry-point quebra com `KeyboardInterrupt` no terminal; `requirements` nunca instalado em ambiente limpo). Relaciona: ADR-023 (app SW/dados), ADR-034 (completude), ADR-040 (CI).

## Contexto

O entry-point **nunca foi executado como o usuário o executaria**: tinha `input()` bloqueante como
única via, que sem TTY interativo quebra. Os `requirements` "funcionaram" só porque as libs já estavam
no ambiente — **nunca testado limpo**. Ambos são gaps de **"definição de pronto"** específicos de
produto de software/dado (não do núcleo agnóstico).

## Decisão (1 frase ativa)

Criar **`tools/check_entrypoint_tty.py`** (roda o entry-point com stdin fechado + timeout; `input()`
bloqueante como única via = FAIL) e **`tools/check_clean_env.py`** (`pip install -r` em venv descartável
+ import dos módulos; modo `--check`/`--no-network` rápido e offline para CI), com canários
(`test_entrypoint_no_tty.py`, `test_clean_env.py`), wirados ao **gate de entrega de software** do
`evals-engineer` (app `exemplos/dominio-software`, ADR-023) — mantendo o núcleo `_shared/` inalterado.

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** Entry-point que quebra no terminal e requirements não-testados passam como "pronto". **Rejeitada — é o gap.**
2. **Detecção só estática (`grep input(`).** Pega o caso óbvio mas não prova que o produto roda; falso-negativo (input via outra API) e falso-positivo (input() guardado por argv). **Rejeitada** — o dinâmico (rodar sem TTY) é a prova real.
3. **Colocar os checks no núcleo `_shared`/qa-critic genérico.** Entry-point/requirements são conceitos de **produto de software** — colocá-los no núcleo viola o agnosticismo (P12). **Rejeitada** — vivem na app SW/dados (ADR-023); o qa-critic só aponta para eles quando `product_type` é software.
4. **2 linters dinâmicos + canários + wiring na app SW/dados (ESCOLHIDA).** Prós: prova de comportamento real, offline-friendly no CI, núcleo intacto. Contras: rodar entry-point arbitrário tem custo/risco — mitigado por timeout + stdin fechado + o caller declarar a invocação não-interativa.

## Consequências

**Positivas:** "pronto" ganha definição mecânica para software; o `KeyboardInterrupt`-no-terminal e o
"requirements não resolve do zero" viram FAIL de canário. **Negativas:** o gate de ambiente limpo real
(venv) é mais lento — por isso o canário usa o modo resolução (`--dry-run --no-index`) e o venv completo
fica para o gate de release da app. **Riscos/limite declarado:** `check_clean_env` real depende de
rede/PyPI; o canário é offline (`--no-index`) → `LIMITS.md` ("mecanizado offline: resolução; venv real: gate de release").

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `check_entrypoint_tty|check_clean_env`
- Artefatos: `tools/check_entrypoint_tty.py`, `tools/check_clean_env.py`, `tools/test_entrypoint_no_tty.py`,
  `tools/test_clean_env.py`, edição `evals-engineer/SKILL.md` (§Gate de entrega de software).
- DONE quando: ambos no gate de entrega de software (app SW/dados, ADR-023). [CONFIRMADO — canários verdes]
