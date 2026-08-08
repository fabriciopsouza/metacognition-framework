#!/usr/bin/env python3
"""Canario COMPORTAMENTAL do gate de tier-autor (ADR-082) — fecha o ponto cego que o process-critic
heterogeneo (Sonnet) pegou: o gate NASCEU de um false-PASS (Sonnet auto-aprovou gate vermelho), mas
sua logica de warn nao tinha canario. Se order.index()/baseline fosse invertido por acidente, os
outros canarios passariam e a falha ORIGINAL recorreria sem deteccao. Aqui provamos o COMPORTAMENTO:
autor < baseline -> warn; autor >= baseline -> ok; desconhecido -> warn(declare); baseline indisponivel
declarado -> downgrade ok. Fail-closed (exit 1 se a logica divergir).

Uso: python tools/test_author_tier.py   (exit 0 PASS; 1 se falha)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import boot_check  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    fails = []
    # ambiente determinístico: sem indisponibilidade herdada
    saved = os.environ.pop("FRAMEWORK_MODELS_UNAVAILABLE", None)
    # [ADR-101] Os 6 asserts abaixo provam a LOGICA DE TIER pura (declaração → veredito). A partir
    # do ADR-101 a detecção do transcript pode SOBREPOR a declaração quando esta superestima; se
    # deixássemos a detecção ativa aqui, o resultado dependeria de qual modelo roda o canário — o
    # canário viraria não-determinístico. Neutralizamos a detecção para a lógica pura e provamos a
    # sobreposição em asserts PRÓPRIOS (bloco anti-overclaim, no fim).
    _real_detect = boot_check.detect_session_model
    boot_check.detect_session_model = lambda: ""
    try:
        # autor ABAIXO do baseline (sonnet/haiku) -> warn LOUD (passa o id explicito p/ nao auto-detectar)
        for mid in ("claude-sonnet-4-6", "claude-haiku-4-5-20251001"):
            r = boot_check.check_author_tier(mid)
            if r["status"] != "warn" or "ABAIXO do baseline" not in r["detail"]:
                fails.append(f"autor {mid} deveria WARN 'ABAIXO do baseline', veio {r['status']}: {r['detail'][:60]}")

        # autor NO baseline (opus) -> ok
        r = boot_check.check_author_tier("claude-opus-4-8")
        if r["status"] != "ok":
            fails.append(f"autor opus (=baseline) deveria OK, veio {r['status']}: {r['detail'][:60]}")

        # autor ACIMA do baseline (fable) -> ok (anti-inversao: se a comparacao invertesse, fable daria warn)
        r = boot_check.check_author_tier("claude-fable-5")
        if r["status"] != "ok":
            fails.append(f"autor fable (>baseline) deveria OK, veio {r['status']}: {r['detail'][:60]} "
                         f"(possivel INVERSAO de order.index — o bug que este canario existe p/ pegar)")

        # modelo desconhecido -> warn 'declare' (nunca falso-OK)
        r = boot_check.check_author_tier("modelo-inexistente-xyz")
        if r["status"] != "warn" or "NAO detectado" not in r["detail"]:
            fails.append(f"modelo desconhecido deveria WARN 'NAO detectado', veio {r['status']}: {r['detail'][:60]}")

        # baseline DECLARADO indisponivel -> autor sonnet desce sem nag (downgrade ok)
        os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = "opus"
        r = boot_check.check_author_tier("claude-sonnet-4-6")
        if r["status"] != "ok" or "indisponivel" not in r["detail"]:
            fails.append(f"baseline indisponivel: autor sonnet deveria OK (downgrade declarado), "
                         f"veio {r['status']}: {r['detail'][:60]}")
        os.environ.pop("FRAMEWORK_MODELS_UNAVAILABLE", None)

        # ---- [ADR-101] DECLARACAO NAO PODE SUPERESTIMAR A MEDICAO -------------------------
        # Falha REAL de 2026-08-08: o dono rodou `/model claude-fable-5`, o harness nao aplicou, e
        # o agente declarou `--author-model claude-fable-5` ao boot_check. A flag sobrepos a
        # deteccao e o gate carimbou "autor='fable' >= baseline" — repetindo a suposicao do
        # auditado de volta como se fosse medicao. Um gate que aceita a autodeclaracao do auditado
        # nao e gate. Aqui a deteccao e FIXADA em opus e provamos as 3 direcoes.
        boot_check.detect_session_model = lambda: "claude-opus-5"

        r = boot_check.check_author_tier("claude-fable-5")  # declara ACIMA do detectado
        if r["status"] != "warn" or "IGNORADA" not in r["detail"] or "opus" not in r["detail"]:
            fails.append("OVERCLAIM: declarar 'fable' com deteccao 'opus' deveria WARN e IGNORAR a "
                         f"declaracao, veio {r['status']}: {r['detail'][:90]}")

        r = boot_check.check_author_tier("claude-haiku-4-5-20251001")  # declara ABAIXO = confissao
        if r["status"] != "warn" or "ABAIXO do baseline" not in r["detail"]:
            fails.append("CONFISSAO: declarar 'haiku' abaixo do detectado deve continuar valendo "
                         f"(rebaixar e permitido), veio {r['status']}: {r['detail'][:90]}")

        r = boot_check.check_author_tier("claude-opus-5")  # declaracao BATE com a medicao
        if r["status"] != "ok" or "IGNORADA" in r["detail"]:
            fails.append("COERENTE: declarar o mesmo que o detectado deve ser OK e silencioso, "
                         f"veio {r['status']}: {r['detail'][:90]}")
    finally:
        boot_check.detect_session_model = _real_detect
        if saved is not None:
            os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = saved

    print(f"author-tier comportamental (ADR-082/101): 9 asserts (sonnet/haiku warn, opus/fable ok, "
          f"desconhecido warn, baseline-indisp downgrade, + overclaim/confissao/coerente) — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (gate de tier-autor com comportamento provado)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
