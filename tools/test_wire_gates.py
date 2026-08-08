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
        wire_gates.write_settings(p, hooks, gates, quiet=True)
        with open(p, encoding="utf-8") as f:
            got = json.load(f)
        check(got.get("model") == "opus", "write_settings preserva `model`")
        check(got.get("permissions", {}).get("allow") == ["Read"],
              "write_settings preserva `permissions`")
        check(got.get("hooks") == hooks, "write_settings grava os hooks do manifesto")
        changed = wire_gates.write_settings(p, hooks, gates, quiet=True)
        check(changed is False, "write_settings e idempotente (2a chamada nao muda)")

    # 7b. REGRESSAO BLOQUEANTE (QA heterogeneo 2026-08-08): a chave `hooks` era OVERWRITE total.
    #     Como `sync-global` roda --install-global a CADA boot, hook PROPRIO do dono (ou de outro
    #     plugin/MCP) em evento/matcher fora do manifesto sumia em silencio. Tem que sobreviver.
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "settings.json")
        alheio = {"hooks": [{"type": "command", "command": "python meu_script_pessoal.py",
                             "statusMessage": "hook do dono"}]}
        antigo = {"hooks": [{"type": "command",
                             "command": 'powershell .claude/hooks/ensure-global-wiring.ps1',
                             "statusMessage": "wiring legado"}]}
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"hooks": {"Notification": [alheio], "SessionStart": [antigo]}}, f)
        wire_gates.write_settings(p, hooks, gates, quiet=True)
        with open(p, encoding="utf-8") as f:
            got = json.load(f)
        cmds = [h.get("command", "") for bl in got.get("hooks", {}).values()
                for b in bl for h in b.get("hooks", [])]
        check(any("meu_script_pessoal.py" in c for c in cmds),
              "write_settings PRESERVA hook do dono em evento fora do manifesto")
        check(got.get("hooks", {}).get("Notification") == [alheio],
              "write_settings nao mexe no evento que so tem hook do dono")
        check(not any("ensure-global-wiring.ps1" in c for c in cmds),
              "write_settings REMOVE wiring legado do framework (migracao .ps1 -> Python)")
        check(any("closing_gate.py" in c for c in cmds),
              "write_settings instala os gates do manifesto junto com os do dono")

    # 7c. settings.json corrompido NAO pode ser sobrescrito: apagaria permissions/model/env.
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "settings.json")
        with open(p, "w", encoding="utf-8") as f:
            f.write('{"model": "opus", "permissions": {,,,')  # truncado/invalido
        try:
            wire_gates.write_settings(p, hooks, gates, quiet=True)
            check(False, "write_settings ABORTA em settings.json corrompido (nao sobrescreve)")
        except wire_gates.CorruptSettings:
            check(True, "write_settings ABORTA em settings.json corrompido (nao sobrescreve)")
        with open(p, encoding="utf-8") as f:
            check('"model": "opus"' in f.read(), "arquivo corrompido fica INTACTO p/ conserto manual")

    # 7d. Backup em profundidade: 1 geracao so protegia contra o ultimo erro.
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "settings.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"v": 1, "hooks": {}}, f)
        wire_gates.write_settings(p, hooks, gates, quiet=True)
        h2 = {k: v for k, v in list(hooks.items())[:1]}
        wire_gates.write_settings(p, h2, gates, quiet=True)
        check(os.path.isfile(p + ".wire.bak"), "backup .wire.bak criado")
        check(os.path.isfile(p + ".wire.bak.2"), "backup rotaciona (>=2 geracoes preservadas)")

    # 7e. Comparacao imune ao case do drive no Windows — a causa do falso DIVERGE 13x13.
    a = {"SessionStart": [{"hooks": [{"type": "command", "command": r'python "c:\x\y.py"'}]}]}
    b = {"SessionStart": [{"hooks": [{"type": "command", "command": r'python "C:\x\y.py"'}]}]}
    check((wire_gates._cmp_key(a) == wire_gates._cmp_key(b)) == (os.name == "nt"),
          "comparacao normaliza case do drive no Windows (falso DIVERGE 13x13)")
    check(wire_gates.ROOT == wire_gates._canon(wire_gates.ROOT),
          "ROOT e canonico (drive maiusculo) — wiring estavel entre processos")

    # 8. O diagnostico roda sem estourar, responde os dois escopos e NAO acusa falso positivo.
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "wire_gates.py"), "--check"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    check(r.returncode in (0, 1), "`--check` termina com exit 0/1 (diagnostico, nao crash)")
    check("global" in r.stdout and "projeto" in r.stdout, "`--check` reporta os dois escopos")
    # Quando diverge, tem que DIZER o que diverge — "disco=13 x manifesto=13" e diagnostico mudo.
    if "DIVERGE" in r.stdout:
        check("faltam" in r.stdout or "obsoletos" in r.stdout or "comando difere" in r.stdout,
              "`--check` NOMEIA a divergencia (nao so conta gates)")

    print("-" * 50)
    print(f"RESULTADO: {'PASS' if not FAILS else 'FAIL (' + str(len(FAILS)) + ')'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
