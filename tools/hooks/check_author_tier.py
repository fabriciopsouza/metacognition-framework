#!/usr/bin/env python3
"""check_author_tier.py — Hook UserPromptSubmit (ADR-082): a CADA turno, detecta o modelo ATIVO da
sessao (do transcript) e, se o AUTOR roda ABAIXO do baseline com baseline disponivel, ANUNCIA um
banner LOUD (additionalContext) exigindo /model <baseline>. Mecaniza "checar o modelo ativo e alertar
automaticamente" (pedido do dono 2026-06-16) — o modelo da sessao e do harness, fora do model-policy,
e antes nada o auditava (Sonnet virou autor em silencio no v1.59.0 e auto-aprovou gate vermelho).

NAO troca o modelo (o /model interativo e do harness — limite declarado ADR-082): alerta, nao forca.
Para NOVAS sessoes, settings.json `"model"` ja lanca no baseline. Onde Kaspersky/EDR veta hook, este
fica inerte e o boot_check.py (manual, EDR-proof) cobre a deteccao no boot.

Contrato UserPromptSubmit: le JSON no stdin (transcript_path). Emite additionalContext se autor<baseline;
senao silencioso. SEMPRE exit 0 (fail-open — nunca quebra o turno)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def _emit(ctx):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                             "additionalContext": ctx}}, ensure_ascii=True))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    transcript = payload.get("transcript_path") or ""
    try:
        import boot_check
        model = boot_check.detect_session_model(transcript)
        pol = json.load(open(os.path.join(ROOT, "tools", "model-policy.json"), encoding="utf-8"))
    except Exception:
        return 0  # fail-open
    ba = pol.get("baseline_author", {})
    baseline = (ba.get("model") or "").lower()
    order = []
    for t in ("max", "balanced", "economy"):
        for fam in pol.get("tiers", {}).get(t, {}).get("chain", []):
            if fam not in order:
                order.append(fam)
    unavailable = {x.strip().lower() for x in os.environ.get("FRAMEWORK_MODELS_UNAVAILABLE", "").split(",") if x.strip()}
    if baseline in unavailable or not baseline:
        return 0  # baseline indisponivel declarado -> downgrade ok, sem nag
    # DIVERGENCIA DELIBERADA vs boot_check (process-critic Sonnet 2026-06-16): se o modelo NAO e
    # detectavel (sem transcript_path no payload OU sessao nova ainda sem turn em disco), o boot_check
    # emite warn 'declare' UMA vez no boot; o hook (per-turn) fica SILENCIOSO no desconhecido para nao
    # naggar todo turno por falta de dado. O boot e o lugar do 'declare'; o hook so dispara no caso
    # POSITIVO (autor detectado < baseline). Silencio aqui = 'nao sei', nunca 'esta ok'.
    fam = ""
    for f, mid in pol.get("model_ids", {}).items():
        if f in (model or "").lower() or str(mid).lower() in (model or "").lower():
            fam = f
            break
    if fam and fam in order and baseline in order and order.index(fam) > order.index(baseline):
        _emit(f"[author-tier ADR-082] Você (AUTOR) está rodando em '{fam}', ABAIXO do baseline "
              f"'{baseline}' (disponível). Sonnet/Haiku só como CRÍTICO/docops — nunca como autor com "
              f"baseline disponível. TROQUE agora: /model {baseline}  (ou declare indisponibilidade via "
              f"FRAMEWORK_MODELS_UNAVAILABLE). O framework não troca o modelo da sessão por você (limite "
              f"do harness) — esta é a correção da cegueira que deixou Sonnet auto-aprovar no v1.59.0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
