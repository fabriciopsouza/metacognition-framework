#!/usr/bin/env python3
"""shadow_drift — as distribuições publicadas acompanharam o canônico? (ADR-049/070/088)

O QUE RESOLVE. As cinco distribuições (`public`, `public-nonadmin`, `premium`, `web`,
`web-premium`) são geradas do canônico por um workflow no GitHub Actions. Quando o Actions esteve
desligado por billing, elas **congelaram por vinte releases sem nenhum alarme** — a deriva só foi
notada quando alguém foi olhar à mão, meses depois. Em 2026-08-17 medimos que o workflow voltou a
funcionar; o ponto único de falha, porém, continua o mesmo: se ele cair de novo, o silêncio volta.

Este verificador transforma esse silêncio em número. Ele **não publica nada** e não conserta nada:
diz quanto cada distribuição está atrás e quem precisa agir.

COMO MEDE. O workflow grava, na mensagem de commit de cada sombra, o SHA do canônico que originou
aquele export (`publish: export limpo da fonte privada @ abc1234`). Comparar esse SHA com o HEAD
do canônico dá a distância exata em commits — melhor que comparar versão, porque pega também os
casos em que o export rodou mas falhou no meio.

OFFLINE É SKIP, NÃO FALHA. O núcleo não exige rede, e um verificador que reprova por falta de
internet seria desligado na primeira viagem de avião. Sem `gh` autenticado ou sem rede, ele
declara `SKIP` e diz por quê — silêncio declarado, que é diferente de silêncio.

Uso:
    python tools/shadow_drift.py              # relatório
    python tools/shadow_drift.py --json
    python tools/shadow_drift.py --limite 5   # exit 1 se alguma passar de 5 commits atrás

Códigos de saída:
    0  medido, todas dentro da tolerância — ou SKIP global declarado (sem `gh`/rede)
    1  alguma passou da tolerância
    2  alguma NÃO pôde ser medida. Ausência de medição não é aprovação: foi assim
       que a deriva passou vinte releases despercebida.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ_PADRAO = Path(__file__).resolve().parent.parent
WORKFLOW = ".github/workflows/publish-clean.yml"
LIMITE_PADRAO = 3

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass


def sombras(raiz):
    """Lê a lista do próprio workflow — hardcodar aqui criaria uma segunda fonte para divergir."""
    try:
        txt = (Path(raiz) / WORKFLOW).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return sorted(set(re.findall(r'^\s*\w*_?REPO:\s*"([^"]+/[^"]+)"', txt, re.M)))


def _rodar(args, timeout=45):
    try:
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, stdin=subprocess.DEVNULL)
        return (r.stdout or "").strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def sha_publicado(mensagem):
    """Extrai o SHA do canônico que a mensagem de publicação carrega."""
    m = re.search(r"@\s*([0-9a-f]{7,40})", str(mensagem or ""))
    return m.group(1) if m else None


def distancia(raiz, sha):
    """(atras, situacao). `atras` é o nº de commits entre o SHA publicado e o HEAD canônico."""
    if not sha:
        return None, "a mensagem de publicacao nao diz de qual commit veio"
    if _rodar(["git", "-C", str(raiz), "cat-file", "-e", sha + "^{commit}"]) is None:
        return None, f"o commit {sha} nao existe neste repositorio (historico reescrito?)"
    if _rodar(["git", "-C", str(raiz), "merge-base", "--is-ancestor", sha, "HEAD"]) is None:
        return None, f"o commit {sha} nao e' ancestral do HEAD — a sombra saiu de outra linha"
    n = _rodar(["git", "-C", str(raiz), "rev-list", "--count", f"{sha}..HEAD"])
    return (int(n) if n and n.isdigit() else None), "ok"


def medir(raiz):
    """(resultado, motivo_do_skip). Sem rede/gh -> ([], motivo)."""
    raiz = Path(raiz)
    alvos = sombras(raiz)
    if not alvos:
        # Distinguir "o arquivo nao existe" de "existe e eu nao entendi". A 2a e' DEFEITO, nao
        # ausencia de dado: o workflow e' local, ler nao exige rede, e um rename de variavel ou
        # aspas simples zeravam a lista virando SKIP silencioso — o defeito original voltando
        # pela porta que este verificador deveria guardar. Achado ALTO do qa-critic (Fable).
        if (Path(raiz) / WORKFLOW).is_file():
            return [{"repo": WORKFLOW, "sha": None, "atras": None,
                     "situacao": "o workflow existe mas nao consegui extrair nenhuma "
                                 "distribuicao dele — formato mudou?"}], None
        return [], f"{WORKFLOW} nao existe neste repositorio"
    if _rodar(["gh", "auth", "status"], timeout=25) is None:
        return [], "`gh` ausente ou nao autenticado — sem como consultar as publicadas"

    saida = []
    for repo in alvos:
        msg = _rodar(["gh", "api", f"repos/{repo}/commits?per_page=1",
                      "--jq", ".[0].commit.message"])
        if msg is None:
            saida.append({"repo": repo, "atras": None, "sha": None,
                          "situacao": "nao consegui consultar (rede, permissao ou repo ausente)"})
            continue
        sha = sha_publicado(msg.splitlines()[0] if msg else "")
        atras, situacao = distancia(raiz, sha)
        saida.append({"repo": repo, "sha": sha, "atras": atras, "situacao": situacao})
    return saida, None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Deriva das distribuicoes publicadas (ADR-049/088).")
    ap.add_argument("--repo", default=str(RAIZ_PADRAO))
    ap.add_argument("--limite", type=int, default=LIMITE_PADRAO,
                    help=f"commits de atraso tolerados (default {LIMITE_PADRAO})")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    resultado, skip = medir(Path(a.repo))
    if skip:
        if a.json:
            print(json.dumps({"skip": skip, "sombras": []}, ensure_ascii=False, indent=2))
        else:
            print(f"[shadow-drift] SKIP declarado: {skip}")
            print("  Nao e' aprovacao — e' ausencia de medicao. Rode com rede para saber.")
        return 0

    atrasadas = [r for r in resultado if (r["atras"] or 0) > a.limite]
    duvidosas = [r for r in resultado if r["atras"] is None]

    if a.json:
        print(json.dumps({"limite": a.limite, "sombras": resultado}, ensure_ascii=False, indent=2))
    else:
        print(f"[shadow-drift] {len(resultado)} distribuicao(oes) · tolerancia {a.limite} commits")
        for r in resultado:
            if r["atras"] == 0:
                print(f"  em dia    {r['repo']}")
            elif r["atras"] is not None:
                marca = "ATRASADA " if r["atras"] > a.limite else "atras     "
                print(f"  {marca}{r['repo']} — {r['atras']} commit(s) atras (publicou {r['sha']})")
            else:
                print(f"  ?         {r['repo']} — {r['situacao']}")
        if atrasadas:
            print(f"\n  {len(atrasadas)} passou da tolerancia. O publish roda no GitHub Actions; "
                  f"se ele estiver parado, elas envelhecem em silencio.")
            print("  Conferir:  gh run list --workflow publish-clean.yml --limit 3")
        if duvidosas:
            print(f"\n  {len(duvidosas)} nao pode(m) ser medida(s) — ausencia de medicao nao e' "
                  f"aprovacao.")

    # Duvida NAO e' aprovacao. A 1a versao so' olhava `atrasadas`: se as cinco virassem "?" — por
    # falta de permissao, ou por o workflow mudar o formato da mensagem — o alarme saia ZERO para
    # sempre. Verde perpetuo com um interrogacao que ninguem le e' exatamente o defeito que este
    # arquivo existe para matar. Achado ALTO do qa-critic (Fable, 2026-08-17).
    if atrasadas:
        return 1
    return 2 if duvidosas else 0


if __name__ == "__main__":
    sys.exit(main())
