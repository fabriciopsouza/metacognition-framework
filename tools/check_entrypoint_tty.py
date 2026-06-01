#!/usr/bin/env python3
"""Gate "teste pela porta do usuário" — roda o entry-point SEM TTY (ADR-036).

GAP de campo: o entry-point nunca foi executado como o usuário o executaria. Tinha `input()`
bloqueante como única via → no terminal real, sem TTY interativo, ele quebra/trava
(`KeyboardInterrupt`/`EOFError`). "Funcionava" só na cabeça do agente.

MECANISMO: executa `[python, <entrypoint>, *args]` com **stdin fechado** (`DEVNULL`) e timeout.
- TIMEOUT (travou esperando input que nunca vem) → FAIL.
- saída não-zero com sinal de leitura de stdin (`EOFError`/`KeyboardInterrupt`/"reading from stdin")
  → FAIL (input() bloqueante como única via).
- returncode 0 dentro do timeout → PASS (roda pela porta do usuário, não-interativo).

Um entry-point pronto deve ter um caminho não-interativo (argv/flag/env), não só `input()`.

Uso:
    python tools/check_entrypoint_tty.py <entrypoint.py> [-- arg1 arg2 ...]
    python tools/check_entrypoint_tty.py <entrypoint.py> --timeout 8 -- --batch

Exit 0 PASS · 1 FAIL · 2 erro de uso.
"""
import os
import subprocess
import sys

STDIN_SIGNS = ("EOFError", "KeyboardInterrupt", "reading from stdin", "input(")


def run_no_tty(entrypoint, args=None, timeout=10, python=None):
    """Roda o entry-point sem TTY. Retorna (verdict, detail) com verdict em {PASS, FAIL}."""
    python = python or sys.executable
    args = args or []
    if not os.path.isfile(entrypoint):
        return "FAIL", f"entry-point inexistente: {entrypoint}"
    try:
        proc = subprocess.run(
            [python, entrypoint, *args],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return "FAIL", f"travou {timeout}s sem TTY (input() bloqueante sem caminho não-interativo)"
    if proc.returncode == 0:
        return "PASS", "rodou não-interativo (returncode 0)"
    err = (proc.stderr or "") + (proc.stdout or "")
    if any(s in err for s in STDIN_SIGNS):
        return "FAIL", "quebrou lendo stdin sem TTY (input() bloqueante como única via)"
    return "FAIL", f"saída não-zero ({proc.returncode}) ao rodar não-interativo: {err.strip()[:160]}"


def main(argv):
    args = argv[1:]
    if not args:
        print("uso: check_entrypoint_tty.py <entrypoint.py> [--timeout N] [-- args...]", file=sys.stderr)
        return 2
    timeout = 10
    if "--timeout" in args:
        i = args.index("--timeout")
        try:
            timeout = int(args[i + 1])
        except (IndexError, ValueError):
            print("--timeout requer inteiro", file=sys.stderr)
            return 2
        del args[i:i + 2]
    entry = args[0]
    rest = args[1:]
    if rest and rest[0] == "--":
        rest = rest[1:]
    verdict, detail = run_no_tty(entry, rest, timeout=timeout)
    print(f"{verdict}: {entry} -> {detail}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
