#!/usr/bin/env python3
"""Canario de consistencia de fechamento FAIL-CLOSED no CI (emenda ADR-030 / plano anti-bypass E2).

O `consistency-gate.ps1` (ADR-030) e **fail-soft** E e **hook PowerShell** -> vetado pelo Kaspersky
nesta maquina -> "nao disparou em ~7 fechamentos" (falha real, execution-report 2026-06-08). O gate
EXISTE mas nao e enforcado. Aqui as dimensoes CI-decidiveis viram **FAIL-CLOSED em Python**
(nao-vetoavel, roda na suite run_canaries): mecaniza o gap "gate existe mas nao disparou".

NAO duplica (regua §0) — estas dims ja sao enforcadas por outros canarios:
  - checkpoint-no-history        -> test_release_checkpoint.py
  - ADR Aceito presente no CHANGELOG -> test_adr_changelog_sync.py
  - versao README x CHANGELOG x vitrine -> test_marketing_claims.py

Aqui ficam as dims do consistency-gate AINDA nao enforcadas em lugar nenhum:
  (1) numero de ADR DUPLICADO (dim 'contagens')
  (2) ADR citado no CHANGELOG (= mudanca entregue) mas ainda `Status: Proposto` — bug RECORRENTE
      (ADR-051 mergeado-como-Proposto; complementa o sentido inverso do adr_changelog_sync).
  (3) VERSION-CLAIM (P1/ADR-077): commit recente que declara `vX.Y.Z` na mensagem DEVE ter heading
      `## [X.Y.Z]` no CHANGELOG — o INVERSO do adr_changelog_sync. Fecha o Escape A do caso real
      v1.55.0 (2026-06-11): bloco mergeado declarando versao no commit sem entrada no CHANGELOG ->
      NENHUM gate de release acordou (todos ancoram no evento "versao nova no CHANGELOG").
      Janela: ultimos 200 commits (forward-only; provado sem falso-positivo na historia real).
Dims nao-decidiveis no CI (unpushed: CI e pos-push; transients _intake; CI-override via gh — P2/ADR-077)
sao ADVISORY: informa, nao reprova.

Uso: python tools/test_consistency_closing.py   (exit 0 PASS; 1 se falha)
"""
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    fails = []
    try:
        chg = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8-sig").read().lower()
    except Exception as e:
        print(f"RESULTADO: FAIL (CHANGELOG.md ilegivel: {e})")
        return 1

    nums = {}
    proposto_shipped = []
    for a in sorted(glob.glob(os.path.join(ROOT, "docs", "adr", "*.md"))):
        name = os.path.basename(a)
        if "template" in name.lower():
            continue
        m = re.match(r"(\d+)-", name)
        if not m:
            continue
        n = m.group(1)
        nums.setdefault(n, []).append(name)
        txt = open(a, encoding="utf-8").read()
        # ancora na LINHA do campo Status (como consistency-gate.ps1) — senao casa a palavra
        # "Proposto" no corpo do ADR (ex.: "ADRs em 'Proposto'") e gera falso-positivo.
        is_proposto = bool(re.search(r"(?im)^\s*-?\s*Status:\s*(?:\*\*)?\s*proposto", txt))
        # (2) entregue (citado no CHANGELOG) mas ainda Proposto = o bug recorrente ADR-051
        if is_proposto and f"adr-{n}" in chg:
            proposto_shipped.append(name)

    # (1) numeros de ADR duplicados (dim 'contagens')
    dups = {n: fs for n, fs in nums.items() if len(fs) > 1}
    for n, fs in sorted(dups.items()):
        fails.append(f"ADR numero {n} DUPLICADO: {', '.join(fs)}")
    for name in proposto_shipped:
        fails.append(f"{name} citado no CHANGELOG (entregue) mas ainda Status: Proposto "
                     f"(flip para Aceito ou remova do CHANGELOG — bug recorrente ADR-051)")

    # (3b) raiz-limpa (ADR-079): arquivo RASTREADO na raiz, 0 bytes e sem extensao = destroço de
    # shell (caso real 2026-06-11: payload de hook executado por cmd interativo criou ~20 arquivos;
    # 8 chegaram a commit). Fail-closed: nao ha arquivo legitimo nesse formato na raiz.
    try:
        ls = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
        for fn in (ls.stdout or "").splitlines():
            if "/" in fn or "\\" in fn or "." in fn:
                continue
            fp = os.path.join(ROOT, fn)
            try:
                if os.path.isfile(fp) and os.path.getsize(fp) == 0:
                    fails.append(f"arquivo rastreado VAZIO e sem extensao na raiz: '{fn}' — destroço "
                                 f"de shell commitado (ADR-079); remova com git rm")
            except OSError:
                continue
    except Exception:
        pass

    # (3) version-claim (P1/ADR-077): vX.Y.Z em mensagem de commit recente -> heading no CHANGELOG.
    # fail-soft se git indisponivel (mesma postura das advisories); fail-CLOSED quando decidivel.
    claimed_missing = []
    try:
        log = subprocess.run(["git", "-C", ROOT, "log", "--format=%s", "-200"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
        if log.returncode == 0 and log.stdout:
            heads = set(re.findall(r"(?m)^## \[(\d+\.\d+\.\d+)\]", chg))
            # claim = vX.Y.Z em qualquer posicao; X.Y.Z sem prefixo SO conta com contexto de versao
            # no subject (changelog/release/vers/bump) — evita falso-positivo tipo "python 3.12.1"
            # (achado MEDIO do process-critic v1.56.0; hibrido validado sem FP em 200 commits reais).
            ctx = re.compile(r"(?i)changelog|release|vers|bump")
            for subj in log.stdout.splitlines():
                claims = set(re.findall(r"\bv(\d+\.\d+\.\d+)\b", subj))
                if ctx.search(subj):
                    claims |= set(re.findall(r"\b(\d+\.\d+\.\d+)\b", subj))
                for v in claims:
                    if v not in heads and v not in claimed_missing:
                        claimed_missing.append(v)
    except Exception:
        pass
    for v in claimed_missing:
        fails.append(f"commit recente declara v{v} mas o CHANGELOG NAO tem heading [{v}] — "
                     f"version-claim sem entrada = fechamento pulado (P1/ADR-077; caso real v1.55.0)")

    # --- ADVISORY (nao reprova): dims que o CI nao decide ---
    # (4) CI-override (P2/ADR-077): ultimo PR mergeado com check vermelho/pulado -> exige rastro
    # OVERRIDE: no history.md (ADR-051: override com custo/consequencia, nunca silencioso).
    # Best-effort via gh (rede/auth) — advisory por construcao.
    try:
        pr = subprocess.run(["gh", "pr", "list", "--state", "merged", "--limit", "1",
                             "--json", "number,statusCheckRollup"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace",
                            timeout=15)
        if pr.returncode == 0 and pr.stdout.strip():
            import json as _json
            items = _json.loads(pr.stdout)
            if items:
                checks = items[0].get("statusCheckRollup") or []
                bad = [c for c in checks if str(c.get("conclusion", "")).upper()
                       not in ("SUCCESS", "NEUTRAL", "SKIPPED", "")]
                if bad:
                    hist = ""
                    try:
                        hist = open(os.path.join(ROOT, "history.md"), encoding="utf-8-sig").read()
                    except Exception:
                        pass
                    if "OVERRIDE" not in hist:
                        print(f"[advisory] PR #{items[0].get('number')} mergeado com check nao-verde "
                              f"e SEM 'OVERRIDE:' no history.md (ADR-051/P2: override declarado, "
                              f"nunca silencioso)")
    except Exception:
        pass
    try:
        cnt = subprocess.run(["git", "-C", ROOT, "rev-list", "--count", "@{upstream}..HEAD"],
                             capture_output=True, text=True).stdout.strip()
        if cnt.isdigit() and int(cnt) > 0:
            print(f"[advisory] {cnt} commit(s) nao-pushado(s) (recovery real = conta GitHub; push antes de fechar)")
    except Exception:
        pass
    try:
        stray = [f for f in os.listdir(ROOT)
                 if "." not in f and os.path.isfile(os.path.join(ROOT, f))
                 and os.path.getsize(os.path.join(ROOT, f)) == 0]
        if stray:
            print(f"[advisory] {len(stray)} arquivo(s) vazio(s) sem extensao na raiz (destroço de "
                  f"shell? — ADR-079): {', '.join(sorted(stray))} — remover antes do commit")
    except Exception:
        pass
    intake = os.path.join(ROOT, "docs", "_intake")
    if os.path.isdir(intake):
        leftover = [f for f in os.listdir(intake) if os.path.isfile(os.path.join(intake, f))]
        if leftover:
            print(f"[advisory] {len(leftover)} transiente(s) em docs/_intake/ (remover no fechamento): {', '.join(leftover)}")

    # PONTEIRO MORTO EM GUIA. "Toda doc alinhada com o que fazemos" so' se sustenta se algo
    # conferir: guia que manda rodar ferramenta inexistente e' pior que guia ausente — quem segue
    # descobre errando, e passa a desconfiar do resto do documento. Varre os arquivos que o usuario
    # de fato le e exige que cada `tools/*.py` citado exista.
    docs_vivos = sorted(glob.glob(os.path.join(ROOT, "guia", "*.md"))) + [
        os.path.join(ROOT, n) for n in ("CLAUDE.md", "AGENTS.md", "AGENT-FRAMEWORK.md")]
    mortos = []
    for doc in docs_vivos:
        if not os.path.isfile(doc):
            continue
        try:
            txt = open(doc, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for ref in sorted(set(re.findall(r"tools/[A-Za-z0-9_\-]+\.py", txt))):
            if not os.path.isfile(os.path.join(ROOT, ref)):
                mortos.append(f"{os.path.basename(doc)} cita {ref}, que nao existe")
    fails += mortos

    print(f"{len(nums)} ADR(s); duplicatas: {len(dups)}; entregue-mas-Proposto: {len(proposto_shipped)}; "
          f"version-claim sem heading: {len(claimed_missing)}; ponteiro morto em guia: "
          f"{len(mortos)} — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (fechamento consistente: sem duplicata de ADR; nada entregue ainda "
          "Proposto; todo version-claim tem entrada no CHANGELOG)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
