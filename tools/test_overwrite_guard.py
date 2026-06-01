#!/usr/bin/env python3
"""Canário do overwrite-guard (ADR-037, item 5 do plano de remediação v2).

Reproduz o MODO de falha: sobrescrever um arquivo que JÁ TEM conteúdo, sem ler/criar nesta sessão.
- Write sobre arquivo pré-existente FORA do manifesto -> BLOQUEIA (exit 2).
- Write sobre arquivo registrado no manifesto (lido/criado nesta sessão) -> allow.
- Write de arquivo novo -> allow. Arquivo vazio -> allow. Read registra (depois Write -> allow).

Testa o .ps1; se houver bash+jq, exige **paridade** de veredito .ps1↔.sh (fecha o `[DESCONHECIDO]`
deste hook). SKIP se faltar pwsh. Zero domínio.

Uso: python tools/test_overwrite_guard.py   (exit 0 PASS/SKIP; 1 se o gate não protege/diverge)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "tools", "hooks")
PS1 = os.path.join(HOOKS, "overwrite-guard.ps1")
SH = os.path.join(HOOKS, "overwrite-guard.sh")


def find_pwsh():
    for exe in ("pwsh", "powershell"):
        if shutil.which(exe):
            return exe
    return None


def run_ps1(pwsh, payload, manifest):
    env = dict(os.environ, OVERWRITE_GUARD_MANIFEST=manifest)
    p = subprocess.run([pwsh, "-NoProfile", "-NonInteractive", "-File", PS1],
                       input=json.dumps(payload), capture_output=True, text=True, env=env)
    return p.returncode


def run_sh(bash, payload, manifest):
    env = dict(os.environ, OVERWRITE_GUARD_MANIFEST=manifest)
    p = subprocess.run([bash, SH], input=json.dumps(payload), capture_output=True, text=True, env=env)
    return p.returncode


def payload(event, tool, fp, cwd, sid="sess-canary"):
    return {"hook_event_name": event, "tool_name": tool, "session_id": sid,
            "cwd": cwd, "tool_input": {"file_path": fp}}


def main():
    pwsh = find_pwsh()
    if not pwsh:
        print("SKIP: pwsh/powershell ausente — canário não executado (CI prova).", file=sys.stderr)
        return 0
    bash = shutil.which("bash")
    jq = shutil.which("jq")
    # .sh e hook POSIX; no Windows (git-bash) recebe paths backslash fora do contrato. Paridade
    # .sh roda nos runners POSIX; no Windows testa-se so o .ps1 nativo. (ver test_parity)
    parity = bool(bash and jq) and os.name != "nt"

    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        existing = os.path.join(tmp, "relato.md")
        with open(existing, "w", encoding="utf-8") as fh:
            fh.write("conteudo anterior importante\n")
        empty = os.path.join(tmp, "vazio.md")
        open(empty, "w").close()
        novo = os.path.join(tmp, "novo.md")  # não existe

        def fresh_manifest(seed=None):
            m = os.path.join(tmp, f"manifest_{fresh_manifest.n}.json")
            fresh_manifest.n += 1
            if seed:
                with open(m, "w", encoding="utf-8") as fh:
                    json.dump(seed, fh)
            return m
        fresh_manifest.n = 0

        # (desc, payload, manifest_seed, expected_rc)
        cases = []
        cases.append(("Write sobre pré-existente FORA do manifesto -> bloqueia",
                      payload("PreToolUse", "Write", existing, tmp), None, 2))
        # "arquivo registrado -> allow" é coberto de forma ROBUSTA pelo fluxo record->allow no fim
        # (usa a MESMA normalização GetFullPath do hook; seed manual com os.path.normpath divergia da
        # canonicalização do hook em alguns runners Windows — falso-FAIL).
        cases.append(("Write de arquivo novo -> allow",
                      payload("PreToolUse", "Write", novo, tmp), None, 0))
        cases.append(("Write sobre arquivo vazio -> allow",
                      payload("PreToolUse", "Edit", empty, tmp), None, 0))

        for desc, pl, seed, exp in cases:
            m = fresh_manifest(seed)
            rc = run_ps1(pwsh, pl, m)
            ok = rc == exp
            if not ok:
                fails += 1
            line = f"{'OK  ' if ok else 'FAIL'} [ps1 rc {rc}, esperado {exp}] {desc}"
            if parity:
                m2 = fresh_manifest(seed)
                rc_sh = run_sh(bash, pl, m2)
                agree = rc_sh == rc
                if not agree:
                    fails += 1
                line += f"  | .sh rc {rc_sh} {'==' if agree else '!= (DIVERGE)'}"
            print(line)

        # fluxo record->allow: PostToolUse Read registra; depois Write -> allow
        m = fresh_manifest()
        run_ps1(pwsh, payload("PostToolUse", "Read", existing, tmp), m)
        rc = run_ps1(pwsh, payload("PreToolUse", "Write", existing, tmp), m)
        ok = rc == 0
        if not ok:
            fails += 1
        print(f"{'OK  ' if ok else 'FAIL'} [ps1 rc {rc}, esperado 0] Read registra -> Write subsequente allow")

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else f"PASS (overwrite-guard protege; {'paridade .ps1↔.sh ok' if parity else 'paridade .sh -> CI'})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
