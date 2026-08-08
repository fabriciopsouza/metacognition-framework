#!/usr/bin/env python3
"""Canario do wiring portatil de gates (ADR-101).

Trava a falha-raiz medida em 2026-08-07: o wiring GLOBAL tinha 2 gates contra 17 do repo-framework,
e os 2 eram .ps1. Todo projeto que nao o repo-mae rodava sem gates -> "so acontece se provocado".
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import wire_gates  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    print("# test_wire_gates (ADR-101)")
    gates = wire_gates.load_gates()

    check(len(gates) >= 10, f"manifesto tem gates suficientes ({len(gates)})")

    # 1. Todo gate declara os campos que o wiring precisa.
    for g in gates:
        ok = all(g.get(k) for k in ("key", "event", "scope", "script"))
        check(ok, f"gate `{g.get('key', '?')}` declara key/event/scope/script")

    # 2. Nenhum comando pode ser PowerShell: foi o que sobrou capado no global (ADR-060).
    for scope in ("framework", "both"):
        hooks = wire_gates.build_hooks(gates, scope, base=ROOT if scope == "both" else "")
        cmds = [h["command"] for blocks in hooks.values() for b in blocks for h in b["hooks"]]
        check(all(".ps1" not in c.lower() for c in cmds),
              f"scope={scope}: nenhum hook depende de PowerShell")
        check(all(c.startswith("python") for c in cmds),
              f"scope={scope}: todo hook e Python (portatil Windows/Linux/macOS)")

    # 3. O script de todo gate existe em disco (wiring nao pode apontar p/ vazio).
    for g in gates:
        p = os.path.join(ROOT, g["script"].split(" ", 1)[0].replace("/", os.sep))
        check(os.path.isfile(p), f"script existe: {g['script'].split(' ', 1)[0]}")

    # 4. REGRESSAO-CHAVE: o conjunto portatil ('both') precisa cobrir os gates que protegem
    #    QUALQUER projeto. Se alguem marcar um destes como 'framework', o global volta a ser capado.
    portable = {g["key"] for g in gates if g.get("scope") == "both"}
    for key in ("inject-start-session", "route-gate", "effect-gate", "overwrite-guard",
                "mission-gate", "context-budget", "compaction-gate", "closing-gate",
                "check-author-tier", "boot-brief"):
        check(key in portable, f"gate portatil presente no escopo global: `{key}`")

    check(len(portable) >= 10,
          f"escopo global tem >= 10 gates (medido: {len(portable)}; era 2 antes do ADR-101)")

    # 5. O auto-boot (ADR-006) NAO pode sumir do global — seria regressao silenciosa.
    check("inject-start-session" in portable, "auto-boot do squad preservado no global (ADR-006)")

    # 6. build_hooks preserva matcher e agrupa por evento na ordem canonica.
    hooks = wire_gates.build_hooks(gates, "framework")
    pre = hooks.get("PreToolUse", [])
    check(all("matcher" in b for b in pre), "todo PreToolUse declara matcher")
    check("Stop" in hooks, "evento Stop presente (encerramento deterministico)")

    # 7. write_settings preserva chaves alheias (traceability Regra 3).
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "settings.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"model": "opus", "permissions": {"allow": ["Read"]}, "hooks": {}}, f)
        wire_gates.write_settings(p, hooks, quiet=True)
        with open(p, encoding="utf-8") as f:
            got = json.load(f)
        check(got.get("model") == "opus", "write_settings preserva `model`")
        check(got.get("permissions", {}).get("allow") == ["Read"],
              "write_settings preserva `permissions`")
        check(got.get("hooks") == hooks, "write_settings grava os hooks do manifesto")
        changed = wire_gates.write_settings(p, hooks, quiet=True)
        check(changed is False, "write_settings e idempotente (2a chamada nao muda)")

    # 8. O diagnostico roda sem estourar e responde os dois escopos.
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "wire_gates.py"), "--check"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    check(r.returncode in (0, 1), "`--check` termina com exit 0/1 (diagnostico, nao crash)")
    check("global" in r.stdout and "projeto" in r.stdout, "`--check` reporta os dois escopos")

    print("-" * 50)
    print(f"RESULTADO: {'PASS' if not FAILS else 'FAIL (' + str(len(FAILS)) + ')'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
