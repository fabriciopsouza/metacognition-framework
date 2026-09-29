#!/usr/bin/env python3
"""Canário do formato executivo (`tools/hooks/resposta_executiva.py`, regra do dono de 27/09 e 28/09/2026; ADR-129).

Transcripts sintéticos no formato do Claude Code (JSONL). Prova:
  (a) resposta no formato não gera achado; tabela e código não contam como prosa;
  (b) prosa longa é SINAL, não limite: 200 palavras passam; muito longa vira achado; pedido de detalhe isenta;
  (c) pedido ao dono no meio do turno vira achado; o mesmo pedido no fim passa;
  (d) bloco "★ Insight" vira achado;
  (e) tabela de decisão sem recomendação e tabelas coladas sem título viram achado;
  (f) o hook de Stop NUNCA bloqueia (exit 0 sempre) — bloquear depois de exibir duplicava a resposta;
  (g) o lembrete injeta o molde sempre e os achados da resposta anterior UMA vez, por sessão;
  (h) resultado de ferramenta, subagente e notificação do sistema não contam como pedido do dono;
  (i) regra global e wiring citam o hook nos dois eventos;
  (R4, ADR-130 — incidente de 28/09/2026: wiring novo + script antigo bloqueou todo prompt)
    R4a script antigo + wiring novo não bloqueia: a sonda recusa e remove a entrada --lembrete;
    R4b flag desconhecida e ausência de flag saem com 0, uso só no stderr;
    R4c/R4d --lembrete com prompt normal e com <task-notification> saem com 0;
    R4x exceção em --lembrete e em --hook sai com 0 e vai para o stderr;
    R4e script, ensure instalado e ensure executado vêm do mesmo commit (origin/main), não do working tree.

Uso: python tools/test_resposta_executiva.py              (exit 0 PASS; 1 FAIL)
     python tools/test_resposta_executiva.py --so-r4      (só os canários do ADR-130)
     python tools/test_resposta_executiva.py --mutacoes   (cada mutação, numa cópia, tem de derrubar o seu canário)
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "tools", "hooks", "resposta_executiva.py")
ESTADO = tempfile.mkdtemp()

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

falhas = []


def check(nome, cond, detalhe=""):
    print(("  PASS " if cond else "  FAIL ") + nome + ("" if cond else f" — {detalhe}"))
    if not cond:
        falhas.append(nome)


def user(texto):
    return {"type": "user", "isSidechain": False, "message": {"role": "user", "content": texto}}


def tool_result():
    return {"type": "user", "isSidechain": False,
            "message": {"role": "user", "content": [{"type": "tool_result", "content": "Qual é a sua cor? ok"}]}}


def asst(texto, lado=False):
    return {"type": "assistant", "isSidechain": lado, "message": {"role": "assistant",
                                                                 "content": [{"type": "text", "text": texto}]}}


def tool_use():
    return {"type": "assistant", "isSidechain": False, "message": {"role": "assistant",
                                                                  "content": [{"type": "tool_use", "name": "Bash"}]}}


def _executar(modo, dados):
    return subprocess.run([sys.executable, HOOK] + ([modo] if modo else []), input=json.dumps(dados),
                          capture_output=True, text=True,
                          encoding="utf-8", env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
                                                     RESPOSTA_EXECUTIVA_DIR=ESTADO))


def rodar(entradas, sessao="s1", caminho=None, final=None):
    """(exit do Stop, achados guardados para a sessão). `final` = last_assistant_message do evento."""
    if caminho is None:
        fd, caminho = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            for e in entradas:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    dados = {"transcript_path": caminho, "session_id": sessao}
    if final is not None:
        dados["last_assistant_message"] = final
    r = _executar("--hook", dados)
    p = os.path.join(ESTADO, f"{sessao}.json")
    achados = json.load(open(p, encoding="utf-8"))["motivos"] if os.path.isfile(p) else []
    return r.returncode, achados


def lembrete(sessao="s1"):
    return _executar("--lembrete", {"session_id": sessao}).stdout


def tem(achados, trecho):
    return any(trecho in a for a in achados)


EXEC = ("## Resultado\n\n| Bloco | O que é | Situação |\n|---|---|---|\n| B1 | kit | ✅ |\n\n"
        "## Sua ação\n\nresponder D1.")
PROSA = lambda n: " ".join(["palavra"] * n)  # noqa: E731
TABELA_GRANDE = "| a | b |\n|---|---|\n" + "\n".join(f"| linha {i} com muitas palavras de conteúdo | x |" for i in range(80))
CODIGO = "```\n" + "\n".join("palavra " * 20 for _ in range(30)) + "\n```\nPronto."
DECISAO_SEM = "## Decisões\n\n| # | Decisão | Opções |\n|---|---|---|\n| 1 | x | a · b |"
DECISAO_COM = "## Decisões\n\n| # | Decisão | Opções | Recomendo |\n|---|---|---|---|\n| 1 | x | a · b | a |"
COLADAS = "| A | B |\n|---|---|\n| 1 | 2 |\n\n| C | D |\n|---|---|\n| 3 | 4 |"
SEPARADAS = "## Um\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n## Dois\n\n| C | D |\n|---|---|\n| 3 | 4 |"


PS = shutil.which("powershell") or shutil.which("pwsh")
ENSURE = os.path.join(ROOT, "tools", "hooks", "ensure-global-wiring.ps1")
SYNC = os.path.join(ROOT, ".claude", "hooks", "sync-global.ps1")
# Réplica do comportamento do script anterior ao ADR-129 que estava instalado no incidente: sem --lembrete; flag
# desconhecida imprime o uso no stdout e sai com 2 (no UserPromptSubmit, exit 2 bloqueia o prompt).
ANTIGO = ('"""script antigo: sem --lembrete"""\nimport sys\n\n\ndef main(argv):\n    if "--hook" not in argv:\n'
          '        print(__doc__)\n        return 2\n    sys.stdin.read()\n    return 0\n\n\nsys.exit(main(sys.argv))\n')
QUEBRA_HOOK = '"""stub: falha no --hook"""\nimport sys\nsys.stdin.read()\nsys.exit(1 if "--hook" in sys.argv else 0)\n'
FALA = '"""stub: escreve no stdout"""\nimport sys\nsys.stdin.read()\nprint("contexto indevido")\n'
NOTIF = '"""stub: bloqueia notificação"""\nimport sys\nsys.exit(2 if "task-notification" in sys.stdin.read() else 0)\n'
# ensure anterior ao ADR-130 (sem ENSURE-CONTRATO): ignora -Ref e copia do working tree.
ENSURE_ANTIGO = ("param([string]$RepoDir = '')\nCopy-Item (Join-Path $RepoDir 'tools\\hooks\\resposta_executiva.py') "
                 "(Join-Path $env:USERPROFILE '.claude\\hooks\\resposta_executiva.py') -Force\nexit 10\n")
PROMPT_OI = {"hook_event_name": "UserPromptSubmit", "session_id": "t", "prompt": "oi"}
PROMPT_NOTIF = dict(PROMPT_OI, prompt="<task-notification><task-id>x</task-id></task-notification>")
# Arquivos do repo que os canários R4 executam (cópia para --mutacoes).
ARQUIVOS_R4 = ["tools/test_resposta_executiva.py", "tools/hooks/resposta_executiva.py",
               "tools/hooks/ensure-global-wiring.ps1", "tools/hooks/route-gate.ps1", ".claude/hooks/sync-global.ps1",
               ".claude/hooks/inject-start-session-global.template.ps1", ".claude/global/CLAUDE-global.md"]


def _home():
    home = tempfile.mkdtemp(prefix="home-r4-")
    os.makedirs(os.path.join(home, ".claude", "hooks"))
    return home


def _ps(script, args, home, env_extra=None):
    """Roda um .ps1 com home falso: nada toca o ~/.claude real."""
    env = {k: v for k, v in os.environ.items() if k not in ("FRAMEWORK_HOOKS_REF", "CLAUDE_PROJECT_DIR")}
    env.update(USERPROFILE=home, PYTHONDONTWRITEBYTECODE="1", **(env_extra or {}))
    return subprocess.run([PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script] + args, env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)


def _settings(home):
    p = os.path.join(home, ".claude", "settings.json")
    return json.load(open(p, encoding="utf-8-sig")) if os.path.isfile(p) else {}


def _sha(caminho):
    return hashlib.sha256(open(caminho, "rb").read()).hexdigest().upper()


def _git(repo, *args):
    return subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def _instalar(home, codigo):
    with open(os.path.join(home, ".claude", "hooks", "resposta_executiva.py"), "w", encoding="utf-8") as fh:
        fh.write(codigo)


def _gravar_settings(home, cfg):
    with open(os.path.join(home, ".claude", "settings.json"), "w", encoding="utf-8") as fh:
        fh.write(cfg if isinstance(cfg, str) else json.dumps(cfg))


def _eventos(home, evento):
    return json.dumps(_settings(home).get("hooks", {}).get(evento, []))


def _wirado(home):
    """route-gate + resposta_executiva nos dois eventos, apontando para o script instalado."""
    cmd = f'python "{os.path.join(home, ".claude", "hooks", "resposta_executiva.py")}"'
    rota = "powershell.exe -NoProfile -File route-gate.ps1"
    return {"hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": rota}]},
                                           {"hooks": [{"type": "command", "command": cmd + " --lembrete"}]}],
                      "Stop": [{"hooks": [{"type": "command", "command": cmd + " --hook"}]}]}}


def _repo(origin=True, ensure_commitado=None):
    """Repo git sintético: um commit com os fontes atuais (ou com `ensure_commitado`), publicado como origin/main se
    `origin`; depois o working tree diverge (script antigo), como o repo principal em outro branch no incidente."""
    repo = tempfile.mkdtemp(prefix="repo-r4-")
    for rel in ARQUIVOS_R4[1:6]:  # só hooks e sync: sem CLAUDE-global.md o sync não chama o bootstrap.py
        d = os.path.join(repo, *rel.split("/"))
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, *rel.split("/")), d)
    p_ensure = os.path.join(repo, "tools", "hooks", "ensure-global-wiring.ps1")
    if ensure_commitado is not None:
        with open(p_ensure, "w", encoding="utf-8") as fh:
            fh.write(ensure_commitado)
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    commit = _git(repo, "commit-tree", _git(repo, "write-tree"), "-m", "origin/main de teste")  # sem hooks de git
    if origin:
        _git(repo, "update-ref", "refs/remotes/origin/main", commit)
    with open(os.path.join(repo, "tools", "hooks", "resposta_executiva.py"), "w", encoding="utf-8") as fh:
        fh.write(ANTIGO)
    if ensure_commitado is None:
        with open(p_ensure, "a", encoding="utf-8") as fh:
            fh.write("\n# versao do working tree\n")
    return repo, commit


def _sync(repo, home, env=None):
    return _ps(os.path.join(repo, ".claude", "hooks", "sync-global.ps1"), [], home,
               dict({"CLAUDE_PROJECT_DIR": repo}, **(env or {})))


def r4():
    print("(R4b) flag desconhecida ou ausente: fail-open")
    for modo in ("--flag-inexistente", None):
        r = _executar(modo, PROMPT_OI)
        check(f"R4b {modo or 'sem flag'}: exit 0 e stdout vazio (uso só no stderr)",
              r.returncode == 0 and not r.stdout.strip() and "Uso:" in r.stderr, (r.returncode, r.stdout[:80]))

    print("(R4c/R4d) --lembrete com prompt normal e com notificação")
    r = _executar("--lembrete", PROMPT_OI)
    check("R4c --lembrete com prompt normal: exit 0", r.returncode == 0, (r.returncode, r.stderr[:120]))
    r = _executar("--lembrete", PROMPT_NOTIF)
    check("R4d --lembrete com <task-notification>: exit 0", r.returncode == 0, (r.returncode, r.stderr[:120]))

    print("(R4x) exceção não bloqueia")
    with open(os.path.join(ESTADO, "exc.json"), "w", encoding="utf-8") as fh:
        fh.write("[1]")  # estado que não é objeto: .get() levanta AttributeError
    r = _executar("--lembrete", {"session_id": "exc"})
    check("R4x exceção em --lembrete: exit 0 e erro no stderr", r.returncode == 0 and "erro ignorado" in r.stderr,
          (r.returncode, r.stderr[-160:]))
    r = _executar("--hook", {"session_id": "exc2", "transcript_path": {"nao": "texto"}})
    check("R4x exceção em --hook: exit 0 e erro no stderr", r.returncode == 0 and "erro ignorado" in r.stderr,
          (r.returncode, r.stderr[-160:]))

    if not PS:
        print("  SKIP R4a/R4e: PowerShell ausente (os canários de wiring rodam só onde há powershell)")
        return

    print("(R4a) script antigo + wiring novo não bloqueia a sessão")
    home = _home()
    _instalar(home, ANTIGO)
    _gravar_settings(home, _wirado(home))
    r = _ps(ENSURE, [], home)
    ups = _eventos(home, "UserPromptSubmit")
    check("R4a entrada --lembrete incompatível removida; route-gate preservado",
          "--lembrete" not in ups and "route-gate" in ups, (r.returncode, ups, r.stderr[-300:]))
    check("R4a remoção registrada no log", "sonda falhou" in r.stderr and "removida" in r.stderr, r.stderr[-300:])
    os.remove(os.path.join(home, ".claude", "settings.json"))
    _ps(ENSURE, [], home)
    check("R4a settings vazio + script antigo: --lembrete não é ligado",
          "resposta_executiva" not in _eventos(home, "UserPromptSubmit"), _eventos(home, "UserPromptSubmit"))
    home = _home()
    _instalar(home, QUEBRA_HOOK)
    _gravar_settings(home, _wirado(home))
    r = _ps(ENSURE, [], home)
    check("R4a Stop: script que falha no --hook tem a entrada do Stop removida (e só ela)",
          "resposta_executiva" not in _eventos(home, "Stop") and "--lembrete" in _eventos(home, "UserPromptSubmit"),
          (_eventos(home, "Stop"), r.stderr[-300:]))

    print("(R4f/R4d) sonda: stdout vazio e notificação")
    home = _home()
    _instalar(home, FALA)
    _gravar_settings(home, _wirado(home))
    _ps(ENSURE, [], home)
    check("R4f script que escreve no stdout (viraria contexto de todo prompt) não fica ligado",
          "resposta_executiva" not in _eventos(home, "UserPromptSubmit"), _eventos(home, "UserPromptSubmit"))
    home = _home()
    _instalar(home, NOTIF)
    _ps(ENSURE, [], home)
    check("R4d sonda com <task-notification>: script que bloqueia notificação não é ligado",
          "resposta_executiva" not in _eventos(home, "UserPromptSubmit"), _eventos(home, "UserPromptSubmit"))

    print("(R4g) backup com timestamp; erro não restaura backup antigo")
    home = _home()
    _instalar(home, ANTIGO)
    _gravar_settings(home, _wirado(home))
    claude = os.path.join(home, ".claude")
    velho = os.path.join(claude, "settings.json.heal.bak")
    with open(velho, "w", encoding="utf-8") as fh:
        fh.write("BACKUP-ANTIGO")
    _ps(ENSURE, [], home)
    novos = [f for f in os.listdir(claude) if f.startswith("settings.json.heal-") and f.endswith(".bak")]
    check("R4g mudança grava backup com timestamp e não sobrescreve o antigo",
          len(novos) == 1 and open(velho, encoding="utf-8").read() == "BACKUP-ANTIGO", (novos, os.listdir(claude)))
    _gravar_settings(home, "{ json quebrado")
    r = _ps(ENSURE, [], home)
    check("R4g erro antes do backup: settings intacto e backup antigo não volta",
          r.returncode == 1 and open(os.path.join(claude, "settings.json"), encoding="utf-8").read() == "{ json quebrado"
          and open(velho, encoding="utf-8").read() == "BACKUP-ANTIGO", r.returncode)

    print("(R4p) python ausente: não remove wiring bom")
    home = _home()
    shutil.copyfile(HOOK, os.path.join(home, ".claude", "hooks", "resposta_executiva.py"))
    _gravar_settings(home, _wirado(home))
    sistema = os.environ.get("SystemRoot", r"C:\Windows")
    r = _ps(ENSURE, [], home, {"PATH": os.path.join(sistema, "System32") + os.pathsep
                               + os.path.join(sistema, "System32", "WindowsPowerShell", "v1.0")})
    check("R4p sem python no PATH: wiring existente mantido e log diz por quê",
          "--lembrete" in _eventos(home, "UserPromptSubmit") and "resposta_executiva" in _eventos(home, "Stop")
          and "python ausente" in r.stderr, (r.stderr[-300:], _eventos(home, "Stop")))

    print("(R4e) script e wiring da mesma origem (origin/main), não do working tree")
    repo, commit = _repo()
    home = _home()
    r = _sync(repo, home)
    hooks = os.path.join(home, ".claude", "hooks")
    p_marca = os.path.join(hooks, "hooks-origem.json")
    marca = json.load(open(p_marca, encoding="utf-8-sig")) if os.path.isfile(p_marca) else {}
    sha_script, sha_ensure = _sha(HOOK), _sha(ENSURE)
    inst = os.path.join(hooks, "resposta_executiva.py")
    check("R4e script instalado = o do origin/main (não o do working tree)",
          os.path.isfile(inst) and _sha(inst) == sha_script, (marca, r.stdout[-200:]))
    check("R4e ensure instalado e ensure executado = o do origin/main",
          marca.get("arquivos", {}).get("ensure-global-wiring.ps1") == sha_ensure
          and marca.get("ensure_executado") == sha_ensure, marca)
    check("R4e carimbo de origem aponta o commit do origin/main", marca.get("commit") == commit, marca)
    ups = _eventos(home, "UserPromptSubmit")
    check("R4e com script compatível, --lembrete é ligado", "--lembrete" in ups, ups)
    ligados = [h["command"] for g in _settings(home).get("hooks", {}).get("UserPromptSubmit", [])
               for h in g.get("hooks", []) if "resposta_executiva" in h.get("command", "")]
    rcs = [subprocess.run(c, shell=True, input=json.dumps(PROMPT_NOTIF), capture_output=True, text=True).returncode
           for c in ligados]
    check("R4e comando ligado, executado como o harness executa, não bloqueia a notificação",
          bool(rcs) and all(x == 0 for x in rcs), rcs)
    home = _home()
    _ps(ENSURE, ["-RepoDir", repo], home)
    inst = os.path.join(home, ".claude", "hooks", "resposta_executiva.py")
    check("R4e ensure sem -Ref instala do origin/main (default)", os.path.isfile(inst) and _sha(inst) == sha_script)

    print("(R4h/R4i/R4j) origin/main defasado, sem origin/main e opt-in WORKTREE")
    repo, _ = _repo(ensure_commitado=ENSURE_ANTIGO)
    home = _home()
    r = _sync(repo, home)
    check("R4h origin/main com ensure anterior ao ADR-130: não roda, nada vem do working tree, aviso na sessão",
          not os.path.exists(os.path.join(home, ".claude", "hooks", "resposta_executiva.py"))
          and "anterior ao ADR-130" in r.stdout, r.stdout[-300:])
    repo, _ = _repo(origin=False)
    home = _home()
    r = _sync(repo, home)
    check("R4i sem origin/main: sync avisa e não instala nada",
          "ausente" in r.stdout and not os.path.exists(os.path.join(home, ".claude", "hooks", "resposta_executiva.py")),
          r.stdout[-300:])
    r = _ps(ENSURE, ["-RepoDir", repo], home)
    s = json.dumps(_settings(home))
    check("R4i sem origin/main: ensure não liga evento cujo script não existe",
          "route-gate" not in s and "inject-start-session" not in s and "resposta_executiva" not in s, s)
    repo, _ = _repo()
    home = _home()
    _sync(repo, home, {"FRAMEWORK_HOOKS_REF": "WORKTREE"})
    inst = os.path.join(home, ".claude", "hooks", "resposta_executiva.py")
    check("R4j opt-in WORKTREE instala o working tree, e a sonda recusa o script antigo",
          os.path.isfile(inst) and open(inst, encoding="utf-8").read() == ANTIGO
          and "resposta_executiva" not in _eventos(home, "UserPromptSubmit"), _eventos(home, "UserPromptSubmit"))


# Cada mutação desfaz UMA parte da correção numa cópia; o canário indicado tem de ficar vermelho.
MUTACOES = [
    ("M1 uso volta a sair com 2", "tools/hooks/resposta_executiva.py",
     [("print(__doc__, file=sys.stderr)\n        return 0", "print(__doc__)\n        return 2")], "R4b"),
    ("M2 script do incidente (sem --lembrete, uso com 2)", "tools/hooks/resposta_executiva.py",
     [('if "--hook" not in argv and "--lembrete" not in argv:', 'if "--hook" not in argv:'),
      ("print(__doc__, file=sys.stderr)\n        return 0", "print(__doc__)\n        return 2")], "R4c"),
    ("M2 script do incidente, notificação", "tools/hooks/resposta_executiva.py",
     [('if "--hook" not in argv and "--lembrete" not in argv:', 'if "--hook" not in argv:'),
      ("print(__doc__, file=sys.stderr)\n        return 0", "print(__doc__)\n        return 2")], "R4d"),
    ("M3 except estreito de novo", "tools/hooks/resposta_executiva.py",
     [("except Exception as erro:", "except (OSError, ValueError) as erro:")], "R4x"),
    ("M4 sem sonda no wiring", "tools/hooks/ensure-global-wiring.ps1",
     [("$falha = Test-HookScript -Script $respExec -Flag $s.flag -Eventos $s.json", "$falha = ''")], "R4a"),
    ("M5 sync roda o ensure do working tree", ".claude/hooks/sync-global.ps1",
     [("$ref = if ($env:FRAMEWORK_HOOKS_REF) { $env:FRAMEWORK_HOOKS_REF } else { 'origin/main' }",
       "$ref = 'WORKTREE'")], "R4e"),
    ("M6 ensure copia do working tree", "tools/hooks/ensure-global-wiring.ps1",
     [("if ($ehGit -and $ref -ne 'WORKTREE') {", "if ($false) {")], "R4e"),
    ("M7 sonda não confere o stdout", "tools/hooks/ensure-global-wiring.ps1",
     [('if ("$saida".Trim()) { return "stdout inesperado com $Flag" }', "")], "R4f"),
    ("M8 sonda falha mas não remove a entrada", "tools/hooks/ensure-global-wiring.ps1",
     [('if (Remove-HookEntries -Cfg $cfg -EventName $s.evento -Pattern "*resposta_executiva*$($s.flag)*") {',
       "if ($false) {")], "R4a Stop"),
    ("M9 sonda sem o prompt de notificação", "tools/hooks/ensure-global-wiring.ps1",
     [('"prompt":"<task-notification>sonda</task-notification>"', '"prompt":"oi"')], "R4d sonda"),
    ("M10 default do ensure vira WORKTREE", "tools/hooks/ensure-global-wiring.ps1",
     [("elseif ($env:FRAMEWORK_HOOKS_REF) { $env:FRAMEWORK_HOOKS_REF } else { 'origin/main' }",
       "else { 'WORKTREE' }")], "R4e ensure sem -Ref"),
    ("M11 erro restaura backup antigo", "tools/hooks/ensure-global-wiring.ps1",
     [("if ($bak -and (Test-Path $bak)) {", '$bak = "$settings.heal.bak"; if (Test-Path $bak) {')], "R4g erro"),
    ("M12 backup com nome fixo (sobrescreve)", "tools/hooks/ensure-global-wiring.ps1",
     [("$bak = \"$settings.heal-$(Get-Date -Format 'yyyyMMdd-HHmmss-fff').bak\"", '$bak = "$settings.heal.bak"')],
     "R4g mudança"),
    ("M13 python ausente remove wiring bom", "tools/hooks/ensure-global-wiring.ps1",
     [("if ($falha -eq 'SEM-PYTHON') {", "if ($false) {")], "R4p"),
    ("M14 sync roda ensure sem contrato", ".claude/hooks/sync-global.ps1",
     [("return [bool]($m -and [int]$m.Matches[0].Groups[1].Value -ge 2)", "return (Test-Path $p)")], "R4h"),
    ("M15 liga route-gate sem o script instalado", "tools/hooks/ensure-global-wiring.ps1",
     [("if (-not (Test-Path $routeGate)) {", "if ($false) {")], "R4i sem origin/main: ensure"),
]


def mutacoes():
    for nome, rel, trocas, canario in MUTACOES:
        tmp = tempfile.mkdtemp(prefix="mut-r4-")
        for a in ARQUIVOS_R4:
            d = os.path.join(tmp, *a.split("/"))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copyfile(os.path.join(ROOT, *a.split("/")), d)
        alvo = os.path.join(tmp, *rel.split("/"))
        texto = open(alvo, encoding="utf-8").read()
        aplicavel = all(texto.count(velho) == 1 for velho, _ in trocas)
        check(f"{nome}: trecho mutado existe uma vez (mutação não é vazia)", aplicavel, rel)
        if not aplicavel:
            continue
        for velho, novo in trocas:
            texto = texto.replace(velho, novo)
        with open(alvo, "w", encoding="utf-8") as fh:
            fh.write(texto)
        r = subprocess.run([sys.executable, os.path.join(tmp, "tools", "test_resposta_executiva.py"), "--so-r4"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        morreu = any(ln.strip().startswith(f"FAIL {canario}") for ln in r.stdout.splitlines())
        check(f"{nome}: derruba {canario}", morreu, r.stdout[-400:])


def main(argv):
    if "--mutacoes" in argv:
        mutacoes()
    elif "--so-r4" in argv:
        r4()
    else:
        tudo()
        r4()
    print(f"\nRESULTADO: {'FAIL' if falhas else 'PASS'} ({len(falhas)} falha(s))")
    return 1 if falhas else 0


def tudo():
    print("(a) resposta no formato")
    rc, a = rodar([user("status"), tool_use(), tool_result(), asst(EXEC)])
    check("seções + tabela + ação no fim: sem achado", a == [], a)
    rc, a = rodar([user("status"), asst(TABELA_GRANDE)])
    check("tabela grande não conta como prosa", a == [], a)
    rc, a = rodar([user("gere"), asst(CODIGO)])
    check("bloco de código não conta como prosa", a == [], a)

    print("(b) prosa: sinal, não limite")
    rc, a = rodar([user("status"), asst(PROSA(200))])
    check("200 palavras passam (número não é regra fixa)", a == [], a)
    rc, a = rodar([user("status"), asst(PROSA(400))])
    check("prosa muito longa vira achado de sinal", tem(a, "sinal, não limite"), a)
    rc, a = rodar([user("explique em detalhe por que mudou"), asst(PROSA(400))])
    check("com pedido de detalhe, prosa longa passa", a == [], a)
    rc, a = rodar([user("escreva o ADR do formato executivo"), asst(PROSA(400))])
    check("artefato pedido (escreva o ADR) passa", a == [], a)
    for frase in ("quero revisar o documento com você", "qual o status do relatório?"):
        rc, a = rodar([user(frase), asst(PROSA(400))])
        check(f"conversa sobre artefato não isenta: '{frase}'", tem(a, "prosa longa"), a)

    print("(c) pedido no meio do turno")
    rc, a = rodar([user("faça X"), asst("Quer que eu siga pela opção A?"), tool_use(), tool_result(), asst(EXEC)])
    check("pergunta ao dono no meio do turno vira achado", tem(a, "meio do processamento"), a)
    rc, a = rodar([user("faça X"), asst("Rodando os testes."), tool_use(), tool_result(), asst(EXEC + "\n\nSigo pela A?")])
    check("o mesmo pedido no fim da mensagem final passa", a == [], a)
    rc, a = rodar([user("faça X"), asst("```\nif x?\n```\nRodando."), tool_use(), tool_result(), asst("Feito.")])
    check("'?' dentro de bloco de código no meio não conta", a == [], a)

    print("(d) estilo explicativo")
    rc, a = rodar([user("faça"), asst("`★ Insight ─────`\nexplicação\n`─────`\n" + EXEC)])
    check("bloco ★ Insight vira achado", tem(a, "Insight"), a)

    print("(e) estrutura")
    rc, a = rodar([user("faça"), asst(DECISAO_SEM)])
    check("tabela de decisão sem recomendação vira achado", tem(a, "sem coluna de recomendação"), a)
    rc, a = rodar([user("faça"), asst(DECISAO_COM)])
    check("tabela de decisão com recomendação passa", a == [], a)
    rc, a = rodar([user("faça"), asst(COLADAS)])
    check("tabelas coladas sem título viram achado", tem(a, "sem título entre elas"), a)
    rc, a = rodar([user("faça"), asst(SEPARADAS)])
    check("tabelas com título entre elas passam", a == [], a)
    rc, a = rodar([user("faça"), asst("```\n| A |\n|---|\n\n| B |\n|---|\n```\nFeito.")])
    check("tabelas dentro de bloco de código não contam", a == [], a)
    rc, a = rodar([user("faça"), asst("## Parâmetros\n\n| Parâmetro | Opções | Padrão |\n|---|---|---|\n| x | a · b | a |")])
    check("tabela de referência com 'Opções' não é tabela de decisão", a == [], a)

    print("(f) nunca bloqueia")
    rc, a = rodar([user("faça X"), asst("Decida entre A e B."), tool_use(), tool_result(), asst(DECISAO_SEM + "\n\n" + PROSA(500))])
    check("com vários achados, o Stop sai com 0 (não duplica a resposta na tela)", rc == 0 and len(a) >= 3, (rc, a))
    rc, a = rodar([], caminho=os.path.join(tempfile.gettempdir(), "nao-existe-123.jsonl"))
    check("transcript ausente não trava (exit 0)", rc == 0, rc)

    print("(f2) mensagem final vem do evento (last_assistant_message)")
    rc, a = rodar([user("faça X"), asst("Rodando os testes.")], final=DECISAO_SEM)
    check("transcript sem a final: mede a do evento", tem(a, "sem coluna de recomendação"), a)
    rc, a = rodar([user("faça X"), asst(DECISAO_SEM)], final=DECISAO_SEM)
    check("final já no transcript não é contada duas vezes", len([x for x in a if "sem coluna" in x]) == 1, a)
    rc, a = rodar([user("faça X"), asst("Quer que eu siga?")], final=EXEC)
    check("texto do transcript vira intermediário quando a final vem do evento", tem(a, "meio do processamento"), a)
    for branco in ("\r\n", "  "):
        rc, a = rodar([user("faça X"), asst(f"Resumo feito.{branco}\n\nSigo com o deploy?")],
                      final="Resumo feito.\n\nSigo com o deploy?")
        check(f"final igual à do transcript salvo branco ({branco!r}) não vira pedido no meio", a == [], a)
    antes = sorted(os.listdir(ESTADO))
    rc, a = rodar([user("faça"), asst(DECISAO_SEM)], sessao="")
    check("sem id de sessão nada é gravado", sorted(os.listdir(ESTADO)) == antes, os.listdir(ESTADO))

    print("(g) lembrete")
    rodar([user("faça"), asst(DECISAO_SEM)], sessao="s2")
    l1, l2 = lembrete("s2"), lembrete("s2")
    check("lembrete traz o achado da resposta anterior e aponta a regra", "sem coluna de recomendação" in l1
          and "CLAUDE.md" in l1, l1)
    check("o achado aparece uma vez; sem achado, nada é injetado", l2.strip() == "", l2)
    sys.path.insert(0, os.path.dirname(HOOK))
    import resposta_executiva as rex  # noqa: E402
    rex.ESTADO_DIR = ESTADO
    h = os.path.join(ESTADO, "historico.jsonl")
    base = len(open(h, encoding="utf-8").read().splitlines())
    rex.registrar("h", [])
    check("histórico cresce por acréscimo", len(open(h, encoding="utf-8").read().splitlines()) == base + 1)
    with open(h, "w", encoding="utf-8") as fh:  # recomeça do zero para contar a poda com exatidão
        fh.write("")
    for _ in range(rex.HISTORICO_MAX + 10):
        rex.registrar("h", [])
    check("abaixo do dobro não poda (a reescrita do arquivo é rara)",
          len(open(h, encoding="utf-8").read().splitlines()) == rex.HISTORICO_MAX + 10)
    for _ in range(rex.HISTORICO_MAX):
        rex.registrar("h", [])
    n = len(open(h, encoding="utf-8").read().splitlines())
    check("passando do dobro, o histórico é podado às últimas 500 medições", rex.HISTORICO_MAX <= n <= 2 * rex.HISTORICO_MAX
          and n < base + 1 + 2 * rex.HISTORICO_MAX, n)
    rodar([user("faça"), asst(DECISAO_SEM)], sessao="s3")
    check("achado de outra sessão não vaza", "sem coluna" not in lembrete("s4"), lembrete("s4"))
    rodar([user("faça"), asst(EXEC)], sessao="s3")
    check("resposta corrigida limpa o achado pendente", "sem coluna" not in lembrete("s3"))
    check("histórico das medições é gravado", os.path.isfile(os.path.join(ESTADO, "historico.jsonl")))

    print("(h) ferramenta, subagente e sistema")
    rc, a = rodar([user("status"), tool_use(), tool_result(), asst(EXEC)])
    check("'?' em resultado de ferramenta não é pedido ao dono", a == [], a)
    rc, a = rodar([user("status"), asst("Posso seguir?", lado=True), asst(EXEC)])
    check("texto de subagente não conta", a == [], a)
    notif = user("<task-notification>\n<task-id>x</task-id>\n<status>completed</status>\n</task-notification>")
    rc, a = rodar([user("explique em detalhe o motivo"), asst("Rodando."), notif, asst(PROSA(400))])
    check("notificação do sistema não vira pedido do dono (a isenção de detalhe continua)", a == [], a)
    rc, a = rodar([user("status"), asst("Posso seguir com A?"), notif, asst(EXEC)])
    check("turno anterior à notificação não é medido de novo", a == [], a)
    rc, a = rodar([user("status"), user("<qualquer-tag>explique em detalhe</qualquer-tag>"), asst(PROSA(400))])
    check("mensagem que começa com tag com hífen é envelope de sistema", tem(a, "prosa longa"), a)
    rc, a = rodar([user("<br> no texto? explique em detalhe"), asst(PROSA(400))])
    check("HTML colado pelo dono (<br>) continua sendo pedido dele", a == [], a)

    print("(i) regra e wiring")
    glob = open(os.path.join(ROOT, ".claude", "global", "CLAUDE-global.md"), encoding="utf-8").read()
    check("regra global cita o hook e o critério sem número fixo",
          "resposta_executiva" in glob and "nunca omisso" in glob and "150" not in glob)
    wiring = open(os.path.join(ROOT, "tools", "hooks", "ensure-global-wiring.ps1"), encoding="utf-8").read()
    check("wiring instala o Stop (--hook) e o UserPromptSubmit (--lembrete)",
          "'Stop'" in wiring and "--hook" in wiring and "--lembrete" in wiring and "|| true" not in wiring)
    check("wiring isolada (-RepoDir) instala o hook", "tools/hooks/resposta_executiva.py" in wiring)
    sync = open(os.path.join(ROOT, ".claude", "hooks", "sync-global.ps1"), encoding="utf-8").read()
    check("sync-global não copia o hook do working tree; delega ao ensure do ref (ADR-130)",
          "tools\\hooks\\resposta_executiva.py" not in sync and "archive" in sync)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
