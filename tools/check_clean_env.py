#!/usr/bin/env python3
"""Gate de AMBIENTE LIMPO — os requirements de fato instalam do zero? (ADR-036)

GAP de campo: criou-se `requirements.txt` mas **nunca se rodou `pip install`**. "Funcionou" só
porque as libs já estavam no ambiente. Nunca testado limpo → entrega não-pronta disfarçada.

MECANISMO: `pip install -r requirements.txt` em **venv descartável** (isolado), depois importa os
módulos top-level declarados. Instalação que não resolve = entrega não-pronta. Para CI rápido/offline,
o modo `--check` usa `pip install --dry-run` (resolução sem instalar) e `--no-network` força
`--no-index` (determinístico sem PyPI) — é o que o canário usa.

Uso:
    python tools/check_clean_env.py <requirements.txt> [modulo1 modulo2 ...]   # venv real + import
    python tools/check_clean_env.py <requirements.txt> --check [--no-network]  # só resolução (rápido)

Exit 0 se resolve/instala (e importa, no modo venv); 1 se falha; 2 erro de uso/ambiente.
"""
import os
import subprocess
import sys
import tempfile
import venv


def resolve_only(req_path, no_network=False, timeout=180):
    """Resolução sem instalar (pip --dry-run). Retorna (ok, output). Rápido e offline-friendly."""
    cmd = [sys.executable, "-m", "pip", "install", "--dry-run", "-r", req_path]
    if no_network:
        cmd.insert(4, "--no-index")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, "timeout na resolução"
    except OSError as e:
        return False, f"pip indisponível: {e}"
    return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")


def install_in_venv(req_path, modules=None, timeout=600):
    """Cria venv descartável, instala -r requirements, importa os módulos. (ok, output)."""
    modules = modules or []
    with tempfile.TemporaryDirectory() as d:
        venv.create(d, with_pip=True)
        bindir = "Scripts" if os.name == "nt" else "bin"
        py = os.path.join(d, bindir, "python.exe" if os.name == "nt" else "python")
        if not os.path.isfile(py):
            return False, "venv sem interpretador (ambiente sem python -m venv?)"
        try:
            inst = subprocess.run([py, "-m", "pip", "install", "-r", req_path],
                                  capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, "timeout no pip install"
        if inst.returncode != 0:
            return False, "pip install falhou:\n" + (inst.stderr or inst.stdout)
        for mod in modules:
            imp = subprocess.run([py, "-c", f"import {mod}"], capture_output=True, text=True)
            if imp.returncode != 0:
                return False, f"import '{mod}' falhou em ambiente limpo:\n{imp.stderr}"
        return True, "instalou + importou em venv limpo"


def main(argv):
    args = argv[1:]
    if not args:
        print("uso: check_clean_env.py <requirements.txt> [modulos...] | --check [--no-network]",
              file=sys.stderr)
        return 2
    req = args[0]
    if not os.path.isfile(req):
        print(f"requirements inexistente: {req}", file=sys.stderr)
        return 2
    if "--check" in args:
        ok, out = resolve_only(req, no_network=("--no-network" in args))
        print(("PASS" if ok else "FAIL") + f": resolução de {req}")
        if not ok:
            print(out.strip()[:400])
        return 0 if ok else 1
    modules = [a for a in args[1:] if not a.startswith("-")]
    ok, out = install_in_venv(req, modules)
    print(("PASS" if ok else "FAIL") + f": ambiente limpo para {req} -> {out.splitlines()[0] if out else ''}")
    if not ok:
        print(out.strip()[:400])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
