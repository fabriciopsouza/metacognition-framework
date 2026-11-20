#!/usr/bin/env python3
"""Canário do perfil NON-ADMIN (ADR-047).

Invariante: o perfil non-admin INICIA sob restrição de scripts → `settings.nonadmin.json` NÃO pode
ter hooks de comando (que invocariam PowerShell). E a doutrina "gates anunciados" deve existir
(automação nunca invisível). Cross-platform (só lê arquivos).

Uso: python tools/test_nonadmin.py   (exit 0 PASS; 1 se o perfil non-admin tiver hooks ou faltar doutrina)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def checar_activate(bootstrap_path=None):
    """Roda activate_nonadmin em pastas temporarias. Devolve [(caso, passou)]."""
    import importlib.util
    import shutil
    import tempfile
    spec = importlib.util.spec_from_file_location("bootstrap_sob_teste", bootstrap_path or os.path.join(ROOT, "bootstrap.py"))
    bs = importlib.util.module_from_spec(spec)
    sem_pyc = sys.dont_write_bytecode
    sys.dont_write_bytecode = True  # nao deixar __pycache__ na raiz da arvore compartilhada
    try:
        spec.loader.exec_module(bs)
    finally:
        sys.dont_write_bytecode = sem_pyc
    res = []
    PROJ = b'{"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "x"}]}]}}\n'
    BAK = b'{"antigo": true}\n'

    def pasta(local=None):
        d = tempfile.mkdtemp(prefix="nonadmin-")
        os.makedirs(os.path.join(d, ".claude"))
        open(os.path.join(d, ".claude", "settings.json"), "wb").write(PROJ)
        open(os.path.join(d, ".claude", "settings.json.bak"), "wb").write(BAK)
        if local is not None:
            open(os.path.join(d, ".claude", "settings.local.json"), "wb").write(local)
        return d

    def ler(d, nome):
        p = os.path.join(d, ".claude", nome)
        return open(p, "rb").read() if os.path.isfile(p) else None

    def intocados(d):
        return ler(d, "settings.json") == PROJ and ler(d, "settings.json.bak") == BAK

    def ativar(d):
        """Excecao vira reprovacao do caso (None), nunca queda do canario sem dizer qual caso."""
        try:
            return bs.activate_nonadmin(d)
        except Exception as e:
            return None, f"excecao: {e!r}"

    casos = []
    # C1 ausente -> cria
    d = pasta(); ok, _ = ativar(d)
    casos.append(("C1 local ausente: cria disableAllHooks=true", ok and json.loads(ler(d, "settings.local.json")) == {"disableAllHooks": True} and intocados(d), d))
    # C2 preserva chaves (com BOM) e troca false por true
    d = pasta(b'\xef\xbb\xbf{"permissions": {"allow": ["Read"]}, "disableAllHooks": false}')
    ok, _ = ativar(d); b = ler(d, "settings.local.json")
    casos.append(("C2 preserva chaves, aceita BOM, false vira true, grava sem BOM",
                  ok and not b.startswith(b'\xef\xbb\xbf') and json.loads(b) == {"permissions": {"allow": ["Read"]}, "disableAllHooks": True} and intocados(d), d))
    # C3 ja ativo -> nao escreve (bytes iguais) e idempotente
    orig = b'{ "disableAllHooks" : true }'
    d = pasta(orig); ok1, _ = ativar(d); ok2, _ = ativar(d)
    casos.append(("C3 ja ativo: nao reescreve; 2a execucao igual", ok1 and ok2 and ler(d, "settings.local.json") == orig and intocados(d), d))
    # C4 invalidos -> recusa sem escrever
    for rot, conteudo in (("comentario", b'{// x\n"a": 1}'), ("nao-objeto", b'[1]'), ("valor nao booleano", b'{"disableAllHooks": 1}'),
                          ("string true", b'{"disableAllHooks": "true"}')):
        d = pasta(conteudo); ok, _ = ativar(d)
        casos.append((f"C4 recusa {rot} sem escrever", (ok is False) and ler(d, "settings.local.json") == conteudo and intocados(d), d))
    # C4 destino diretorio
    d = pasta(); os.makedirs(os.path.join(d, ".claude", "settings.local.json")); ok, _ = ativar(d)
    casos.append(("C4 recusa destino que e' diretorio", (ok is False) and intocados(d), d))
    # C5 explicito: settings.json identico apos ativar (ja coberto acima) + nenhum temporario sobrando
    d = pasta(); ativar(d)
    sobra = [n for n in os.listdir(os.path.join(d, ".claude")) if n.endswith(".tmp")]
    casos.append(("C5 settings.json e .bak byte a byte iguais; sem temporario sobrando", intocados(d) and not sobra, d))
    # A2 corrida: outra sessao grava o local entre a leitura e a troca -> recusa, mantem o da outra sessao
    d = pasta(b'{"a": 1}'); outro = b'{"a": 2}'
    real = bs.json.dumps

    def dumps_com_corrida(*a, **k):
        open(os.path.join(d, ".claude", "settings.local.json"), "wb").write(outro)
        return real(*a, **k)
    bs.json.dumps = dumps_com_corrida
    try:
        ok, _ = ativar(d)
    finally:
        bs.json.dumps = real
    casos.append(("A2 corrida com outra sessao: recusa e preserva a escrita alheia", (ok is False) and ler(d, "settings.local.json") == outro and intocados(d), d))
    # Trava: PowerShell executa os hooks -> main() nao chama activate_nonadmin; nao executa -> chama
    chamadas = []
    salvo = (bs.sondar_powershell, bs.activate_nonadmin, bs.ensure_cofre, bs.prompt_report_optin)
    bs.activate_nonadmin = lambda *a, **k: (chamadas.append(1), (True, "simulado"))[1]
    bs.ensure_cofre = lambda *a, **k: False
    bs.prompt_report_optin = lambda *a, **k: None
    try:
        bs.sondar_powershell = lambda: "sim"
        rc1, n1 = bs.main(["bootstrap.py", "--no-mirror"]), len(chamadas)
        bs.sondar_powershell = lambda: "barrado"
        rc2, n2 = bs.main(["bootstrap.py", "--no-mirror"]), len(chamadas)
        bs.sondar_powershell = lambda: "indeterminado"
        rc3, n3 = bs.main(["bootstrap.py", "--no-mirror"]), len(chamadas)
        # Com PowerShell e override ja ativo, a saida avisa que os hooks seguem desligados
        import contextlib
        import io
        real_ler = bs.ler_override_local
        bs.sondar_powershell = lambda: "sim"
        bs.ler_override_local = lambda *a, **k: ("ativo", {"disableAllHooks": True}, b"", "")
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                bs.main(["bootstrap.py", "--no-mirror"])
        finally:
            bs.ler_override_local = real_ler
        avisa_ativo = "continua ATIVO" in buf.getvalue()
    finally:
        bs.sondar_powershell, bs.activate_nonadmin, bs.ensure_cofre, bs.prompt_report_optin = salvo
    casos.append(("trava: com PowerShell e override ativo, avisa que os hooks seguem desligados", avisa_ativo, None))
    casos.append(("trava: sonda indeterminada nao grava override e sai com 1", rc3 == 1 and n3 == n2, None))
    casos.append(("trava: com PowerShell nao ativa; sem PowerShell ativa", rc1 == 0 and n1 == 0 and rc2 == 0 and n2 == 1, None))
    # A4 caractere que nao codifica em UTF-8 (surrogate isolado): recusa, bytes intactos, sem temporario
    orig = b'{"nota": "\\ud800"}'
    d = pasta(orig); ok, _ = ativar(d)
    sobra = [n for n in os.listdir(os.path.join(d, ".claude")) if n.endswith(".tmp")]
    casos.append(("A4 texto nao codificavel: recusa sem escrever nem deixar temporario",
                  (ok is False) and ler(d, "settings.local.json") == orig and not sobra and intocados(d), d))
    # A4 falha na troca do arquivo: recusa, original intacto, temporario apagado
    orig = b'{"a": 1}'
    d = pasta(orig); real_replace = bs.os.replace

    def replace_falha(*a, **k):
        raise PermissionError(13, "simulado: arquivo bloqueado")
    bs.os.replace = replace_falha
    try:
        ok, _ = ativar(d)
    finally:
        bs.os.replace = real_replace
    sobra = [n for n in os.listdir(os.path.join(d, ".claude")) if n.endswith(".tmp")]
    casos.append(("A4 falha ao trocar o arquivo: recusa, original intacto, sem temporario",
                  (ok is False) and ler(d, "settings.local.json") == orig and not sobra and intocados(d), d))
    # A5 link: recusa sem seguir (simulado; criar link no Windows exige privilegio)
    orig = b'{"a": 1}'
    d = pasta(orig); real_islink = bs.os.path.islink
    bs.os.path.islink = lambda p: p.endswith("settings.local.json") or real_islink(p)
    try:
        ok, _ = ativar(d)
    finally:
        bs.os.path.islink = real_islink
    casos.append(("A5 settings.local.json como link: recusa sem escrever", (ok is False) and ler(d, "settings.local.json") == orig and intocados(d), d))
    # A3/A8 --check: local invalido BLOQUEIA; local ativo nao gera pendencia do local
    d = pasta(b'{"disableAllHooks": "sim"}'); p1 = bs.diagnostico_perfil(d)
    d2 = pasta(b'{"disableAllHooks": true}'); p2 = bs.diagnostico_perfil(d2)
    casos.append(("--check: local invalido BLOQUEIA; local ativo sem pendencia",
                  any(n == "BLOQUEIA" and "settings.local.json" in i for n, i, _c in p1)
                  and not any("settings.local.json" in i for _n, i, _c in p2), d))
    shutil.rmtree(d2, ignore_errors=True)
    # A1 deteccao: so' powershell.exe conta; pwsh sozinho = NAO; rc != 0 = NAO
    real_which, real_run = bs.shutil.which, bs.subprocess.run

    class R:
        def __init__(self, rc):
            self.returncode = rc
    try:
        bs.shutil.which = lambda exe: "x" if exe == "pwsh" else None
        bs.subprocess.run = lambda *a, **k: R(0)
        so_pwsh = bs.ps_available()
        bs.shutil.which = lambda exe: "x" if exe == "powershell.exe" else None
        chamado = []
        bs.subprocess.run = lambda cmd, **k: (chamado.append(cmd), R(0))[1]
        ps_ok = bs.ps_available()
        formato = bool(chamado) and chamado[0][0] == "powershell.exe" and "-File" in chamado[0] and "Bypass" in chamado[0]
        bs.subprocess.run = lambda *a, **k: R(1)
        ps_barrado = bs.sondar_powershell()

        def estoura(*a, **k):
            raise bs.subprocess.TimeoutExpired("powershell.exe", k.get("timeout"))
        bs.subprocess.run = estoura
        ps_timeout = bs.sondar_powershell()
    finally:
        bs.shutil.which, bs.subprocess.run = real_which, real_run
    casos.append(("A1 deteccao: so' powershell.exe -ExecutionPolicy Bypass -File conta; pwsh sozinho e rc!=0 = NAO; timeout = indeterminado",
                  so_pwsh is False and ps_ok is True and formato and ps_barrado == "barrado" and ps_timeout == "indeterminado", None))
    for nome, ok, d in casos:
        if d is None:
            res.append((nome, bool(ok)))
            continue
        res.append((nome, bool(ok)))
        shutil.rmtree(d, ignore_errors=True)
    return res


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    fails = 0

    # 1. settings.nonadmin.json existe e NÃO tem hooks de comando
    na = os.path.join(ROOT, ".claude", "settings.nonadmin.json")
    if not os.path.isfile(na):
        print("FAIL: .claude/settings.nonadmin.json ausente"); return 1
    data = json.load(open(na, encoding="utf-8-sig"))
    hooks = data.get("hooks") or {}
    no_hooks = len(hooks) == 0
    if not no_hooks:
        fails += 1
    print(f"{'OK  ' if no_hooks else 'FAIL'} settings.nonadmin.json sem hooks de comando ({'inicia sob restrição' if no_hooks else 'TEM hooks!'})")

    # 2. bootstrap.py (instalação sem PowerShell) existe
    bp = os.path.isfile(os.path.join(ROOT, "bootstrap.py"))
    if not bp:
        fails += 1
    print(f"{'OK  ' if bp else 'FAIL'} bootstrap.py presente (setup sem PowerShell/admin)")

    # 3. doutrina "gates anunciados" presente (automação nunca invisível)
    doctrine = False
    for f in ("CLAUDE.md", "AGENTS.md"):
        p = os.path.join(ROOT, f)
        if os.path.isfile(p):
            t = open(p, encoding="utf-8-sig").read().lower()
            if "non-admin" in t and ("anuncia" in t or "anunciados" in t):
                doctrine = True
    if not doctrine:
        fails += 1
    print(f"{'OK  ' if doctrine else 'FAIL'} doutrina 'gates anunciados' em CLAUDE.md/AGENTS.md")

    # 4. guia presente
    guia = os.path.isfile(os.path.join(ROOT, "guia", "MODO-NON-ADMIN.md"))
    if not guia:
        fails += 1
    print(f"{'OK  ' if guia else 'FAIL'} guia/MODO-NON-ADMIN.md presente")

    # 5. ADR-047 emenda 1: activate_nonadmin grava o override no settings.local.json e NUNCA toca
    #    no settings.json versionado (casos C1 a C5 de docs/specs/bootstrap-preserva-settings/spec.md).
    for nome, ok in checar_activate():
        if not ok:
            fails += 1
        print(f"{'OK  ' if ok else 'FAIL'} activate_nonadmin: {nome}")

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (perfil non-admin inicia sob restrição; automação anunciada, não invisível)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
