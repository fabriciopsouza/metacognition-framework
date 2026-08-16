#!/usr/bin/env python3
"""bootstrap.py — setup NON-ADMIN do framework, SEM PowerShell e SEM privilégio (ADR-047).

Para máquinas corporativas onde a política (GPO) bloqueia scripts PowerShell — `bootstrap.ps1`
não roda. Este equivalente em **Python puro** (Python não é barrado pela política de PS) instala o
framework no perfil do usuário, ativa o **perfil non-admin** (settings sem hooks) e NÃO exige admin.

O que faz (idempotente, 2x sem destruir):
  1. Espelha as skills/regras/workflows do framework para `~/.claude/` (auto-descoberta do Claude Code).
  2. Ativa o perfil **non-admin**: copia `.claude/settings.nonadmin.json` → `.claude/settings.json`
     do PROJETO (sem hooks → inicia sob restrição). Backup do anterior em `settings.json.bak`.
  3. Detecta se PowerShell roda; se SIM, avisa que o modo admin (com hooks) está disponível.
NÃO faz: git config / gh (evita exigir rede/credencial); rode-os à parte se quiser.

Uso:
    python bootstrap.py                 # instala + ativa non-admin
    python bootstrap.py --check         # VERIFICA se a instalação funciona (runbook, guia/SETUP.md)
                                        # exit 1 se houver pendência BLOQUEIA; 0 se só AVISA
    python bootstrap.py --no-mirror     # não espelha p/ ~/.claude (só ativa settings non-admin)
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HOME_CLAUDE = os.path.join(os.path.expanduser("~"), ".claude")
MIRROR = [".agent/skills", ".agent/rules", ".agent/workflows", "_shared", ".claude/commands"]


def ps_available():
    """True se PowerShell consegue EXECUTAR um script trivial (não só existir)."""
    for exe in ("pwsh", "powershell", "powershell.exe"):
        if not shutil.which(exe):
            continue
        try:
            r = subprocess.run([exe, "-NoProfile", "-NonInteractive", "-Command", "exit 0"],
                               capture_output=True, timeout=15)
            if r.returncode == 0:
                return True
        except Exception:
            continue
    return False


def mirror_skills():
    os.makedirs(os.path.join(HOME_CLAUDE, "skills"), exist_ok=True)
    n = 0
    src = os.path.join(ROOT, ".agent", "skills")
    if os.path.isdir(src):
        for name in os.listdir(src):
            s = os.path.join(src, name)
            d = os.path.join(HOME_CLAUDE, "skills", name)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
                n += 1
    return n


def activate_nonadmin():
    na = os.path.join(ROOT, ".claude", "settings.nonadmin.json")
    target = os.path.join(ROOT, ".claude", "settings.json")
    if not os.path.isfile(na):
        return False, "settings.nonadmin.json ausente"
    if os.path.isfile(target):
        shutil.copyfile(target, target + ".bak")
    shutil.copyfile(na, target)
    return True, "perfil non-admin ativo (settings.json sem hooks; backup em settings.json.bak)"


def ensure_cofre():
    """ADR-052/065: o cofre `docs/_private` define o tier OWNER. As distribuições (premium/public) vêm
    SEM ele (stripped). Num clone FULL, cria o COFRE PRÓPRIO vazio → o usuário vira OWNER do SEU cofre
    (relatório de execução FULL local). Idempotente (não toca se já existe). 'Cada clone seu próprio cofre.'"""
    cofre = os.path.join(ROOT, "docs", "_private")
    if os.path.isdir(cofre):
        return False
    try:
        os.makedirs(os.path.join(cofre, "_intake"), exist_ok=True)
        with open(os.path.join(cofre, "README.md"), "w", encoding="utf-8") as fh:
            fh.write(
                "# docs/_private — SEU cofre (tier OWNER, ADR-052/065)\n\n"
                "Privado e LOCAL. Sua presenca define o tier OWNER (relatorio de execucao FULL em "
                "`_intake/`, nao anonimizado). As distribuicoes vem SEM cofre; **este e o seu** — cada "
                "clone tem o proprio.\n\n"
                "- **Nao tornar publico** (e privado por natureza).\n"
                "- **Para publicar learnings (ADR-062/063)** voce precisa do SEU `tools/sensitive-denylist.txt` "
                "(clientes/casos a anonimizar) — as distros nao trazem a do mantenedor. Sem ela, o publish "
                "RECUSA (fail-closed, seguro).\n")
        return True
    except Exception:
        return False


def prompt_report_optin():
    """ADR-064: pergunta 1x (privacy-by-default, TTY-guarded) sobre contribuir aprendizado anonimizado.
    Idempotente (consent OU declined.lock -> nao re-pergunta). Fail-soft: nunca quebra o bootstrap."""
    home = os.path.expanduser("~")
    consent = os.path.join(home, ".claude", "exec-report-consent.json")
    declined = os.path.join(home, ".claude", "exec-report-declined.lock")
    if os.path.exists(consent) or os.path.exists(declined) or not sys.stdin.isatty():
        return
    try:
        print("[bootstrap.py] Contribuir relatorios de execucao ANONIMIZADOS p/ melhorar o framework?")
        print("               (so licoes agnosticas, sem cliente/PII; opt-in; ver docs/REPORTS-CONTRIBUTION.md)")
        ans = input("               Contribuir? [s/N] ").strip().lower()
        os.makedirs(os.path.dirname(consent), exist_ok=True)
        if ans in ("s", "sim", "y", "yes"):
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))
            from execution_report import init_consent
            _, pseudo, _ = init_consent()
            print(f"[bootstrap.py] opt-in registrado (pseudonimo aleatorio {pseudo}). "
                  "Dono: rode 'python tools/setup_central_reports.py' p/ criar o repo central.")
        else:
            open(declined, "w", encoding="utf-8").write("declined\n")
            print("[bootstrap.py] ok, sem contribuicao (mude depois com 'python tools/execution_report.py --init-consent').")
    except Exception as e:
        print(f"[bootstrap.py] (opt-in pulado, nao-bloqueante: {e})")


VERSAO_PYTHON_MINIMA = (3, 8)


def verificar(raiz):
    """Diz o que impede esta instalacao de funcionar. Lista de (nivel, item, como resolver).

    POR QUE ISTO EXISTE. O `--check` antigo respondia duas perguntas — PowerShell roda? hooks
    ligados? — e chamava aquilo de diagnostico. Nao dizia se a instalacao FUNCIONA. Quem clonava
    em outra maquina descobria o que faltava errando, um erro por vez.

    BLOQUEIA = o framework nao opera assim. AVISA = opera, com menos garantia.
    Nao instala nada e nao escreve nada: e' so' leitura, para poder rodar antes e depois.
    """
    import glob
    pend = []

    def bloqueia(item, como):
        pend.append(("BLOQUEIA", item, como))

    def avisa(item, como):
        pend.append(("AVISA   ", item, como))

    if sys.version_info < VERSAO_PYTHON_MINIMA:
        v = ".".join(map(str, VERSAO_PYTHON_MINIMA))
        bloqueia(f"Python {sys.version.split()[0]} — o framework exige {v} ou mais novo",
                 f"instale Python >= {v} e rode de novo")

    if not os.path.isdir(os.path.join(raiz, ".git")):
        bloqueia("nao e' um repositorio git",
                 "clone o repositorio em vez de baixar o .zip — varios gates leem o historico")
    else:
        try:
            r = subprocess.run(["git", "-C", raiz, "rev-parse", "HEAD"], capture_output=True,
                               text=True, timeout=20)
            if r.returncode != 0:
                bloqueia("git presente mas o repositorio nao responde",
                         "confira se o clone terminou: git status")
        except (OSError, subprocess.SubprocessError):
            bloqueia("git nao esta no PATH",
                     "instale o git e reabra o terminal — o framework le historico para decidir")

    for rel, porque in (("tools/run_canaries.py", "e' o portao real do repo"),
                        ("capabilities.json", "e' o registro de tudo que existe"),
                        ("behaviors/manifest.json", "diz quais papeis sao obrigatorios"),
                        ("CLAUDE.md", "e' a entrada do framework")):
        if not os.path.isfile(os.path.join(raiz, rel)):
            bloqueia(f"{rel} ausente — {porque}", "clone incompleto; refaca o clone")

    cur = os.path.join(raiz, ".claude", "settings.json")
    if not os.path.isfile(cur):
        avisa("nao ha .claude/settings.json no projeto",
              "rode `python bootstrap.py` para ativar o perfil non-admin")
    else:
        try:
            cfg = json.load(open(cur, encoding="utf-8-sig"))
            modo = "admin (com hooks)" if cfg.get("hooks") else "non-admin (sem hooks)"
            print(f"[bootstrap.py] perfil ativo: {modo}")
        except Exception as e:
            bloqueia(f".claude/settings.json invalido: {e}",
                     "restaure de settings.json.bak ou rode `python bootstrap.py`")

    espelhadas = glob.glob(os.path.join(HOME_CLAUDE, "skills", "*"))
    if not espelhadas:
        avisa("skills nao espelhadas em ~/.claude/skills",
              "rode `python bootstrap.py` — sem isso o auto-trigger de skill nao acontece")

    # A prova final: o portao do repo roda? Se ele nao roda, nada aqui e' verificavel.
    alvo = os.path.join(raiz, "tools", "run_canaries.py")
    if os.path.isfile(alvo):
        try:
            r = subprocess.run([sys.executable, alvo, "test_capabilities"], capture_output=True,
                               text=True, cwd=raiz, timeout=180, stdin=subprocess.DEVNULL)
            if r.returncode != 0:
                avisa("a suite de canarios nao passou nesta maquina",
                      "rode `python tools/run_canaries.py` e leia o que falhou")
            else:
                print("[bootstrap.py] canario de sanidade: PASSA")
        except subprocess.TimeoutExpired:
            avisa("a suite demorou demais para responder",
                  "rode `python tools/run_canaries.py` a mao e veja onde trava")
        except (OSError, subprocess.SubprocessError) as e:
            avisa(f"nao consegui rodar a suite: {e}", "rode `python tools/run_canaries.py`")

    return pend


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    check_only = "--check" in argv
    no_mirror = "--no-mirror" in argv

    ps = ps_available()
    print(f"[bootstrap.py] PowerShell executa scripts? {'SIM' if ps else 'NAO (politica restrita) -> modo non-admin recomendado'}")
    if check_only:
        pendencias = verificar(ROOT)
        print("-" * 60)
        if not pendencias:
            print("[bootstrap.py] INSTALACAO OK — nenhuma pendencia.")
            return 0
        bloqueiam = [p for p in pendencias if p[0] == "BLOQUEIA"]
        print(f"[bootstrap.py] {len(pendencias)} pendencia(s), {len(bloqueiam)} bloqueante(s):")
        for nivel, item, comoresolver in pendencias:
            print(f"  [{nivel}] {item}")
            print(f"           -> {comoresolver}")
        return 1 if bloqueiam else 0

    if not no_mirror:
        n = mirror_skills()
        print(f"[bootstrap.py] espelhadas {n} skills para {os.path.join(HOME_CLAUDE, 'skills')}")
    if ensure_cofre():  # ADR-052/065: clone full sem cofre -> cria o cofre proprio (vira OWNER)
        print(f"[bootstrap.py] cofre proprio criado: {os.path.join(ROOT, 'docs', '_private')} (tier OWNER; cada clone o seu).")
    prompt_report_optin()  # ADR-064: opt-in 1x (TTY-guarded, fail-soft)
    ok, msg = activate_nonadmin()
    print(f"[bootstrap.py] {'OK' if ok else 'FALHA'}: {msg}")
    print("[bootstrap.py] Modo NON-ADMIN: os hooks automaticos NAO rodam. O agente APLICA e ANUNCIA")
    print("               cada gate inline (route/mission/action-safety/overwrite) — ver CLAUDE.md §Modo non-admin.")
    if ps:
        print("[bootstrap.py] (PowerShell disponivel aqui: para o modo admin com hooks, use bootstrap.ps1 ou restaure settings.json.bak.)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
