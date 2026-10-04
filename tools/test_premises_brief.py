#!/usr/bin/env python3
"""Canario do premises_brief (ADR-109).

Exercita as tres lacunas que o hook existe para fechar. Gate nunca exercitado contra
entrada que DEVE reprovar e decoracao (project-docs SS3.1) - por isso cada caso aqui
tem a contraprova: o inventario NAO pode aparecer quando a evidencia nao existe.
"""
import json
import os
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hooks", "premises_brief.py")


def roda(cwd, home):
    env = dict(os.environ, USERPROFILE=home, HOME=home, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, HOOK], input=json.dumps({"cwd": cwd}),
                       capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
    assert r.returncode == 0, f"hook deve ser fail-open, saiu {r.returncode}: {r.stderr}"
    return json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]


def _projeto_com_memoria(home, slug, n):
    d = os.path.join(home, ".claude", "projects", slug, "memory")
    os.makedirs(d, exist_ok=True)
    linhas = "\n".join(f"- [reg{i}](reg{i}.md) - x" for i in range(n))
    with open(os.path.join(d, "MEMORY.md"), "w", encoding="utf-8") as f:
        f.write("# Memory Index\n\n" + linhas + "\n")


def test_projeto_virgem_nao_inventa():
    """Contraprova: sem artefato, sem memoria e sem git, o hook nao fabrica inventario."""
    with tempfile.TemporaryDirectory() as t:
        cwd, home = os.path.join(t, "proj"), os.path.join(t, "home")
        os.makedirs(cwd)
        os.makedirs(home)
        assert roda(cwd, home) == "", "projeto virgem deve emitir contexto vazio"


def test_lacuna_1_memoria_vazia_aponta_irmaos():
    """Memoria propria vazia NAO pode ser lida como ausencia de premissa."""
    with tempfile.TemporaryDirectory() as t:
        cwd, home = os.path.join(t, "proj"), os.path.join(t, "home")
        os.makedirs(os.path.join(cwd, "docs"))
        with open(os.path.join(cwd, "docs", "requirements.md"), "w", encoding="utf-8") as f:
            f.write("# req\n")
        _projeto_com_memoria(home, "irmao-com-premissa", 4)
        ctx = roda(cwd, home)
        assert "VAZIA ou ausente" in ctx, "deve declarar a memoria propria como vazia"
        assert "NAO e ausencia de premissa" in ctx, "deve negar o salto ausencia->inexistencia"
        assert "irmao-com-premissa" in ctx, "deve apontar a memoria do projeto irmao"


def test_lacuna_1_memoria_propria_e_encontrada_pelo_slug():
    """A memoria do proprio projeto e localizada pelo slug derivado do cwd."""
    with tempfile.TemporaryDirectory() as t:
        cwd, home = os.path.join(t, "proj"), os.path.join(t, "home")
        os.makedirs(cwd)
        slug = cwd.replace(":", "-").replace("\\", "-").replace("/", "-")
        _projeto_com_memoria(home, slug, 3)
        ctx = roda(cwd, home)
        assert "3 registro(s)" in ctx, f"deve contar os registros da memoria propria: {ctx}"
        assert "VAZIA ou ausente" not in ctx


def test_lacuna_2_delega_procedencia_e_o_delegado_existe():
    """Camada 2 (procedencia: branch defasada) e DELEGADA - o canario prova a delegacao.

    O ADR-109 nasceu mandando este hook medir branch/divergencia. A implementacao delegou a
    `check_repo_sync.py::baseline_staleness` (ADR-084), que ja mede HEAD..origin/main, PERSISTE
    marker e faz o route-gate repetir por turno - reimplementar aqui seria duplicacao mais fraca
    (regua de ganho liquido, ADR-007). O ADR foi emendado para registrar isso.

    Delegacao sem canario e buraco silencioso: se alguem remover o delegado, a camada 2 some e
    NINGUEM percebe, porque este hook nunca a mediu. Entao o canario checa os DOIS lados:
      (a) o ponteiro para o delegado esta sempre no texto injetado;
      (b) o delegado REALMENTE existe e expoe a funcao que assume a camada 2.
    """
    with tempfile.TemporaryDirectory() as t:
        cwd, home = os.path.join(t, "proj"), os.path.join(t, "home")
        os.makedirs(cwd)
        os.makedirs(home)
        with open(os.path.join(cwd, "mission.md"), "w", encoding="utf-8") as f:
            f.write("# mission\n")
        ctx = roda(cwd, home)
        # (a) o ponteiro nomeia o delegado - o agente nao pode presumir estar em dia
        assert "check-repo-sync" in ctx, f"deve apontar quem cobre a procedencia: {ctx}"
        assert "retrato congelado" in ctx or "branch defasada" in ctx, \
            "deve nomear o risco que a camada 2 cobre"
        # contraprova: nao pode FABRICAR a medicao que declarou nao fazer
        assert "commit(s) ATRAS" not in ctx, \
            "este hook nao mede divergencia - se passou a medir, a delegacao virou duplicacao"

    # (b) o delegado existe e expoe a funcao que assumiu a camada 2
    delegado = os.path.join(os.path.dirname(HOOK), "check_repo_sync.py")
    assert os.path.isfile(delegado), \
        f"delegado da camada 2 sumiu ({delegado}) - a camada 2 virou buraco silencioso"
    fonte = open(delegado, encoding="utf-8", errors="replace").read()
    assert "def baseline_staleness" in fonte, \
        "check_repo_sync perdeu baseline_staleness - a camada 2 delegada nao tem mais dono"


def test_regra_sempre_presente_quando_ha_inventario():
    with tempfile.TemporaryDirectory() as t:
        cwd, home = os.path.join(t, "proj"), os.path.join(t, "home")
        os.makedirs(cwd)
        os.makedirs(home)
        with open(os.path.join(cwd, "mission.md"), "w", encoding="utf-8") as f:
            f.write("# mission\n")
        ctx = roda(cwd, home)
        assert "[A-DEFINIR]" in ctx, "a regra anti-preenchimento tem de vir junto"
        assert "Diga o que procurou" in ctx


def test_carimba_liveness():
    """hooks-manifest.json so pode listar hook que carimba (ADR-061).

    Sem o carimbo, o route-gate declararia este gate ausente TODA sessao - falso-alarme
    que ensina o dono a ignorar o aviso. Confere tambem que a chave e a MESMA do manifesto.
    """
    with tempfile.TemporaryDirectory() as t:
        cwd, home = os.path.join(t, "proj"), os.path.join(t, "home")
        os.makedirs(cwd)
        os.makedirs(home)
        env = dict(os.environ, USERPROFILE=home, HOME=home, PYTHONIOENCODING="utf-8")
        payload = json.dumps({"cwd": cwd, "session_id": "sessao-xyz"})
        subprocess.run([sys.executable, HOOK], input=payload, capture_output=True,
                       text=True, encoding="utf-8", env=env, timeout=60)

        manifesto = json.load(open(os.path.join(os.path.dirname(HOOK), "hooks-manifest.json"),
                                  encoding="utf-8"))
        chaves = [h["key"] for h in manifesto["audited_hooks"]]
        assert "premises-brief" in chaves, "o hook deve estar no manifesto auditado"

        carimbo = os.path.join(cwd, ".claude", ".hooklive", "premises-brief")
        assert os.path.isfile(carimbo), f"carimbo de liveness ausente em {carimbo}"
        assert open(carimbo, encoding="utf-8").read() == "sessao-xyz", \
            "o carimbo deve conter o session_id recebido no stdin"


def test_carimba_mesmo_em_projeto_virgem():
    """Contraprova: contexto vazio nao pode significar 'hook nao rodou'."""
    with tempfile.TemporaryDirectory() as t:
        cwd, home = os.path.join(t, "proj"), os.path.join(t, "home")
        os.makedirs(cwd)
        os.makedirs(home)
        assert roda(cwd, home) == "", "projeto virgem emite contexto vazio"
        assert os.path.isfile(os.path.join(cwd, ".claude", ".hooklive", "premises-brief")), \
            "carimbo tem de existir mesmo quando o inventario sai vazio"


def _tem_git():
    try:
        return subprocess.run(["git", "--version"], capture_output=True, timeout=10).returncode == 0
    except Exception:
        return False


def _git_init(d):
    os.makedirs(d, exist_ok=True)
    for args in (["init", "-q", "-b", "main"], ["config", "user.email", "t@t"],
                 ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", d, *args], check=True, capture_output=True)


def _commit(d, nome, conteudo, msg):
    with open(os.path.join(d, nome), "w", encoding="utf-8") as f:
        f.write(conteudo)
    subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", d, "commit", "-q", "-m", msg], check=True, capture_output=True)


if __name__ == "__main__":
    falhas = 0
    for nome, fn in sorted((n, f) for n, f in globals().items() if n.startswith("test_")):
        try:
            fn()
            print(f"  PASS {nome}")
        except AssertionError as e:
            falhas += 1
            print(f"  FAIL {nome}: {e}")
        except Exception as e:  # noqa: BLE001
            falhas += 1
            print(f"  ERRO {nome}: {type(e).__name__}: {e}")
    print(f"\n{'FALHOU' if falhas else 'OK'} - {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
