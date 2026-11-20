#!/usr/bin/env python3
"""bootstrap.py — setup NON-ADMIN do framework, SEM PowerShell e SEM privilégio (ADR-047).

Para máquinas corporativas onde a política (GPO) bloqueia scripts PowerShell — `bootstrap.ps1`
não roda. Este equivalente em **Python puro** (Python não é barrado pela política de PS) instala o
framework no perfil do usuário, ativa o **perfil non-admin** (hooks desligados) só onde o PowerShell
não executa os hooks, e NÃO exige admin.

O que faz (idempotente, 2x sem destruir):
  1. Espelha as skills/regras/workflows do framework para `~/.claude/` (auto-descoberta do Claude Code).
  2. Detecta se o PowerShell EXECUTA arquivo .ps1 como os hooks executam. Se SIM, mantém o perfil
     com hooks e não altera nenhum arquivo de configuração.
  3. Se NÃO, ativa o perfil **non-admin**: grava `"disableAllHooks": true` em
     `.claude/settings.local.json` (não versionado; demais chaves preservadas). O
     `.claude/settings.json` versionado nunca é tocado (ADR-047, emenda 20/11/2026).
NÃO faz: git config / gh (evita exigir rede/credencial); rode-os à parte se quiser.

Uso:
    python bootstrap.py                 # instala + ativa non-admin se o PowerShell não roda os hooks
    python bootstrap.py --check         # VERIFICA se a instalação funciona (runbook, guia/SETUP.md)
                                        # exit 1 se houver pendência BLOQUEIA; 0 se só AVISA
    python bootstrap.py --no-mirror     # não espelha p/ ~/.claude (só decide o perfil non-admin)
    python bootstrap.py --regras-globais  # SÓ grava as regras do dono em ~/.claude/CLAUDE.md
                                          # (ADR-116); é o que sync-global.ps1 e bootstrap.sh chamam
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HOME_CLAUDE = os.path.join(os.path.expanduser("~"), ".claude")
MIRROR = [".agent/skills", ".agent/rules", ".agent/workflows", "_shared", ".claude/commands"]


def sondar_powershell():
    """O PowerShell EXECUTA um arquivo .ps1 do jeito que os hooks executam
    (`powershell.exe -NoProfile -ExecutionPolicy Bypass -File`)? Devolve 'sim' | 'barrado' |
    'ausente' | 'indeterminado'. `-Command "exit 0"` nao serve: a politica de execucao (GPO) barra
    arquivo de script, nao comando inline, e o teste antigo dizia SIM na maquina restrita. So' o
    `powershell.exe` conta (e' o que os hooks chamam; `pwsh` sozinho seria falso SIM). Timeout ou
    erro da sonda = 'indeterminado': o chamador NAO grava override com base nisso (falso NAO
    desligaria os hooks do clone inteiro; 1a partida sob antivirus pode passar de 15 s)."""
    if not shutil.which("powershell.exe"):
        return "ausente"
    import tempfile
    ps1 = None
    try:
        fd, ps1 = tempfile.mkstemp(suffix=".ps1")
        with os.fdopen(fd, "w", encoding="ascii") as fh:
            fh.write("exit 0\n")
        for limite in (15, 60):
            try:
                r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                                    "-File", ps1], capture_output=True, timeout=limite)
            except subprocess.TimeoutExpired:
                continue
            return "sim" if r.returncode == 0 else "barrado"
        return "indeterminado"
    except Exception:
        return "indeterminado"
    finally:
        if ps1:
            try:
                os.remove(ps1)
            except OSError:
                pass


def ps_available():
    """True so' quando a sonda diz 'sim'."""
    return sondar_powershell() == "sim"


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


GLOBAL_INICIO = "<!-- framework:global:inicio"
GLOBAL_FIM = "<!-- framework:global:fim -->"


def renderizar_regras_globais(raiz):
    """Texto do bloco de regras globais com o caminho absoluto DESTA maquina (ADR-116).
    Mesma troca do sync-global.ps1: os dois instaladores tem de produzir o mesmo bloco."""
    src = os.path.join(raiz, ".claude", "global", "CLAUDE-global.md")
    with open(src, encoding="utf-8-sig") as fh:
        bloco = fh.read().strip()
    raiz_abs = os.path.abspath(raiz)
    if len(raiz_abs) > 1 and raiz_abs[1] == ":":  # c:\ e C:\ sao a mesma pasta; o bloco nao pode variar
        raiz_abs = raiz_abs[0].upper() + raiz_abs[1:]
    return (bloco.replace("{{FRAMEWORK_ROOT_URL}}", raiz_abs.replace("\\", "/"))
                 .replace("{{FRAMEWORK_ROOT}}", raiz_abs))


def instalar_regras_globais(raiz, home_claude):
    """Grava as regras permanentes do dono em <home_claude>/CLAUDE.md, lido pelo Claude Code em TODA
    pasta (ADR-116). Rota non-admin, espelho do sync-global.ps1 para onde PowerShell e' vetado.

    Troca so o bloco entre os marcadores; texto do usuario fora dele fica intacto e o BOM e' mantido.
    Marcadores fora do par exato (1 inicio + 1 fim, ou nenhum) = RECUSA escrever: casar um inicio
    orfao com o fim de outro bloco apagaria em silencio o texto do usuario entre eles.
    Devolve (situacao, detalhe) com situacao em
    {'instalado', 'em-dia', 'recusado', 'sem-fonte', 'falha-escrita'} — nunca levanta excecao de I/O.
    """
    import re
    try:
        bloco = renderizar_regras_globais(raiz)
    except OSError as e:
        return "sem-fonte", str(e)
    dst = os.path.join(home_claude, "CLAUDE.md")
    bruto = b""
    if os.path.isfile(dst):
        with open(dst, "rb") as fh:
            bruto = fh.read()
    com_bom = bruto.startswith(b"\xef\xbb\xbf")
    # Compara e edita em LF; devolve na quebra de linha que o arquivo do usuario ja usava. Comparar o
    # CRLF do disco com o bloco em LF reescrevia um arquivo identico a cada execucao (QA 25/09).
    atual_disco = bruto.decode("utf-8-sig") if bruto else ""
    # Estilo DOMINANTE: arquivo misto (algumas linhas CRLF, outras LF) sai no estilo da maioria. O
    # conteudo de cada linha e' preservado; so' o terminador e' uniformizado.
    n_crlf = atual_disco.count("\r\n")
    com_crlf = n_crlf > (atual_disco.count("\n") - n_crlf)
    atual = atual_disco.replace("\r\n", "\n")
    n_ini, n_fim = atual.count(GLOBAL_INICIO), atual.count(GLOBAL_FIM)
    if n_ini == 1 and n_fim == 1:
        padrao = re.compile(re.escape(GLOBAL_INICIO) + r".*?" + re.escape(GLOBAL_FIM), re.S)
        novo = padrao.sub(lambda _m: bloco, atual, count=1)
    elif n_ini == 0 and n_fim == 0:
        novo = (atual.rstrip() + "\n\n" + bloco + "\n") if atual.strip() else (bloco + "\n")
    else:
        return "recusado", (f"{dst} tem {n_ini} inicio(s) e {n_fim} fim(ns) de bloco - "
                            f"corrija a mao; nada foi escrito")
    if novo == atual:
        return "em-dia", dst
    # Falha de escrita (somente-leitura, ACL corporativa, arquivo travado) e' RESULTADO, nao crash: no
    # fluxo sem PowerShell uma excecao aqui abortava a ativacao inteira do perfil (QA 25/09, ALTA).
    try:
        os.makedirs(home_claude, exist_ok=True)
        with open(dst, "w", encoding="utf-8-sig" if com_bom else "utf-8", newline="") as fh:
            fh.write(novo.replace("\n", "\r\n") if com_crlf else novo)
    except OSError as e:
        return "falha-escrita", f"{dst}: {e.strerror or e} - nada foi alterado; corrija a permissao e rode de novo"
    return "instalado", dst


def main_regras_globais():
    """`python bootstrap.py --regras-globais` — a UNICA implementacao da instalacao (ADR-116).
    sync-global.ps1 (Windows) e bootstrap.sh (Mac/Linux) chamam isto em vez de repetir a logica:
    duas implementacoes divergiram tres vezes seguidas na revisao (caminho com barra final, CRLF,
    instalador esquecido). Nao toca em settings.json nem em mais nada. Saida de 1 linha para o
    chamador repassar; codigo 0 = instalado/em dia, 2 = recusado (marcadores), 3 = falha de escrita,
    1 = sem fonte."""
    situacao, detalhe = instalar_regras_globais(ROOT, HOME_CLAUDE)
    print(f"regras globais: {situacao} - {detalhe}")  # ASCII: o PS 5.1 que chama le em CP-1252
    return {"instalado": 0, "em-dia": 0, "recusado": 2, "falha-escrita": 3}.get(situacao, 1)


def ler_override_local(raiz=ROOT):
    """Le `.claude/settings.local.json` (nao versionado). Devolve (estado, dados, bytes_lidos, erro):
    estado = 'ausente' | 'ativo' | 'inativo' | 'invalido'. So o booleano True conta como ativo."""
    alvo = os.path.join(raiz, ".claude", "settings.local.json")
    if os.path.islink(alvo):
        return "invalido", None, None, "settings.local.json e' link; recuso seguir (poderia apontar para o settings.json versionado)"
    if not os.path.lexists(alvo):
        return "ausente", {}, None, ""
    if not os.path.isfile(alvo):
        return "invalido", None, None, "settings.local.json existe mas nao e' arquivo comum"
    try:
        with open(alvo, "rb") as fh:
            bruto = fh.read()
        dados = json.loads(bruto.decode("utf-8-sig"))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        return "invalido", None, None, f"settings.local.json ilegivel ou JSON invalido ({e}); comentario e virgula final nao sao aceitos"
    if not isinstance(dados, dict):
        return "invalido", None, None, "settings.local.json nao e' um objeto JSON"
    valor = dados.get("disableAllHooks", False)
    if valor is True:
        return "ativo", dados, bruto, ""
    if valor is False:
        return "inativo", dados, bruto, ""
    return "invalido", None, None, f"disableAllHooks com valor nao booleano ({valor!r})"


def activate_nonadmin(raiz=ROOT):
    """Perfil non-admin (ADR-047, emenda 20/11/2026): grava `"disableAllHooks": true` em
    `.claude/settings.local.json`, que o git ignora. NUNCA toca no `.claude/settings.json`
    versionado: copiar o perfil por cima dele desligava os hooks de todas as sessoes e sujava a
    arvore compartilhada (reincidiu 09/10 e 20/11/2026). Copiar o perfil sem hooks para o local nao
    funcionaria: hooks de arquivos diferentes se somam. Prova em
    docs/specs/bootstrap-preserva-settings/spec.md, secao 2a."""
    pasta = os.path.join(raiz, ".claude")
    alvo = os.path.join(pasta, "settings.local.json")
    estado, dados, bruto, erro = ler_override_local(raiz)
    if estado == "invalido":
        return False, f"{erro} - nada foi alterado; corrija o arquivo e rode de novo"
    if estado == "ativo":
        return True, "perfil non-admin ja ativo (disableAllHooks em .claude/settings.local.json); nada alterado"
    dados = dict(dados)
    dados["disableAllHooks"] = True
    texto = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
    import tempfile
    tmp = None
    try:
        os.makedirs(pasta, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".settings.local.", suffix=".tmp", dir=pasta)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(texto)
        # Outra sessao pode ter mexido no arquivo entre a leitura e agora: confere antes de trocar.
        agora = None
        if os.path.lexists(alvo):
            with open(alvo, "rb") as fh:
                agora = fh.read()
        if agora != bruto:
            return False, "settings.local.json mudou durante a gravacao (outra sessao?) - nada foi alterado; rode de novo"
        os.replace(tmp, alvo)
        tmp = None
    except (OSError, UnicodeError) as e:
        return False, f"falha ao gravar {alvo}: {getattr(e, 'strerror', None) or e} - nada foi alterado"
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
    return True, "perfil non-admin ativo (disableAllHooks em .claude/settings.local.json; settings.json versionado intocado)"


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


def diagnostico_perfil(raiz):
    """Parte do --check sobre o perfil. Diz so' o que inspecionou (settings.json do projeto e
    settings.local.json); hooks de usuario ou plugin ficam fora. Devolve [(nivel, item, como)]."""
    pend = []
    cur = os.path.join(raiz, ".claude", "settings.json")
    if not os.path.isfile(cur):
        pend.append(("AVISA   ", "nao ha .claude/settings.json no projeto",
                     "clone incompleto ou arquivo apagado: confira `git status .claude` e recupere do git"))
    else:
        try:
            cfg = json.load(open(cur, encoding="utf-8-sig"))
            print(f"[bootstrap.py] hooks no .claude/settings.json do projeto: {'sim' if cfg.get('hooks') else 'nao'}")
        except Exception as e:
            pend.append(("BLOQUEIA", f".claude/settings.json invalido: {e}",
                         "confira o diff (`git diff .claude/settings.json`), salve sua versao e recupere a do git"))
    estado, _d, _b, erro = ler_override_local(raiz)
    if estado == "invalido":
        pend.append(("BLOQUEIA", f".claude/settings.local.json: {erro}",
                     "corrija o arquivo (JSON objeto; disableAllHooks so' true ou false)"))
    else:
        print(f"[bootstrap.py] override local disableAllHooks (.claude/settings.local.json): "
              f"{'ATIVO - hooks deste projeto desligados' if estado == 'ativo' else 'inativo'}")
    return pend


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

    pend.extend(diagnostico_perfil(raiz))

    # ADR-116: sem o bloco em ~/.claude/CLAUDE.md, fora deste repo o agente nao recebe a ordem de
    # revisao adversarial nem a de caminho absoluto — e nada avisaria.
    try:
        esperado = renderizar_regras_globais(raiz)
        instalado = ""
        alvo_global = os.path.join(HOME_CLAUDE, "CLAUDE.md")
        if os.path.isfile(alvo_global):
            with open(alvo_global, encoding="utf-8-sig") as fh:
                instalado = fh.read()
        if esperado not in instalado:
            avisa("regras globais do dono ausentes ou desatualizadas em ~/.claude/CLAUDE.md",
                  "rode `python bootstrap.py` — sem elas, em outra pasta o agente pula a revisao "
                  "adversarial e usa link relativo")
    except OSError:
        avisa(".claude/global/CLAUDE-global.md ausente", "clone incompleto; refaca o clone")

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
    if "--regras-globais" in argv:  # antes de tudo: este modo nao pode ativar perfil nem espelhar nada
        return main_regras_globais()
    check_only = "--check" in argv
    no_mirror = "--no-mirror" in argv

    sonda = sondar_powershell()
    ps = sonda == "sim"
    print("[bootstrap.py] powershell.exe executa .ps1 como os hooks? " + {
        "sim": "SIM",
        "barrado": "NAO (barrado pela politica ou pelo antivirus) -> modo non-admin",
        "ausente": "NAO (powershell.exe ausente neste host) -> modo non-admin",
        "indeterminado": "INDETERMINADO (sonda sem resposta em 15 s + 60 s ou erro)"}[sonda])
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
        situacao, detalhe = instalar_regras_globais(ROOT, HOME_CLAUDE)
        print(f"[bootstrap.py] regras globais do dono (ADR-116): {situacao} — {detalhe}")
    if ensure_cofre():  # ADR-052/065: clone full sem cofre -> cria o cofre proprio (vira OWNER)
        print(f"[bootstrap.py] cofre proprio criado: {os.path.join(ROOT, 'docs', '_private')} (tier OWNER; cada clone o seu).")
    prompt_report_optin()  # ADR-064: opt-in 1x (TTY-guarded, fail-soft)
    if ps:
        # Trava (ADR-047, emenda 20/11/2026): onde o PowerShell executa os hooks, nao ha' motivo para
        # desliga-los, e o settings.local.json vale para TODAS as sessoes deste clone.
        print("[bootstrap.py] PowerShell executa os hooks aqui: nenhum arquivo de configuracao alterado.")
        estado, _d, _b, erro = ler_override_local()
        if estado == "ativo":
            print("[bootstrap.py] ATENCAO: o override local disableAllHooks continua ATIVO - os hooks deste clone seguem DESLIGADOS.")
            print("               Para religar: apague a chave disableAllHooks de .claude/settings.local.json.")
        elif estado == "invalido":
            print(f"[bootstrap.py] ATENCAO: .claude/settings.local.json: {erro}")
        else:
            print("               Hooks do projeto ativos. Para forcar o perfil sem hooks, ponha \"disableAllHooks\": true")
            print("               em .claude/settings.local.json (guia/MODO-NON-ADMIN.md).")
        return 0
    if sonda == "indeterminado":
        print("[bootstrap.py] Nada alterado: sem saber se os hooks rodam, nao desligo os hooks do clone inteiro.")
        print("               Rode de novo, ou ponha \"disableAllHooks\": true em .claude/settings.local.json a mao.")
        return 1
    ok, msg = activate_nonadmin()
    print(f"[bootstrap.py] {'OK' if ok else 'FALHA'}: {msg}")
    if ok:
        print("[bootstrap.py] Modo NON-ADMIN: os hooks automaticos NAO rodam, a partir da proxima sessao, em TODAS as sessoes")
        print("               deste clone. O agente APLICA e ANUNCIA cada gate inline (route/mission/action-safety/overwrite).")
        print("               Para remover o override local: apague a chave disableAllHooks de .claude/settings.local.json.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
