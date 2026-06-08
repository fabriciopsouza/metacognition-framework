#!/usr/bin/env python3
"""repo-identity-gate (ADR-070) — classificador ADVISORY, ancestry-first.

Classifica o repo atual em MASTER-CANONICO | SOMBRA-EXPORT | CLONE-VELHO/DIVERGENTE |
FOREIGN | AMBIGUO, usando a ancestralidade git como AUTORIDADE e o marker
`.repo-identity.json` apenas como DICA. Fecha o vetor do incidente 2026-06-05
(marker forjado por copia em export/clone) porque git vence o marker em conflito.

Honestidade (ADR-070): isto e ADVISORY. Em maquina que veta hooks (Kaspersky),
roda inline no 1o turno (Python on-demand nao e barrado). Nao alega "bloqueio".

Uso:
    python tools/repo_identity.py            # imprime a linha de anuncio + detalhe
    python tools/repo_identity.py --line     # so a 1 linha de anuncio
    python tools/repo_identity.py --json      # veredito estruturado
Saida (exit code): 0 = MASTER-CANONICO; 2 = qualquer outro (sinal p/ nudge de escrita).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

EXPORT_RE = re.compile(r"^(publish|export)\b.*@\s*[0-9a-f]{7,}", re.IGNORECASE)


def _norm_remote(url):
    """Canonicaliza um remote git p/ 'host/owner/repo' (minúsculo, sem .git) — equipara SSH e HTTPS.
    Sem isto, `git@github.com:o/r.git` != `https://github.com/o/r` e o master com origin SSH cai em
    FOREIGN (bug de identidade — o master deixa de ser writable). Domain-agnóstico (qualquer host)."""
    if not url:
        return ""
    u = re.sub(r"\.git$", "", url.strip())
    m = re.match(r"^[^@/]+@([^:/]+):(.+)$", u)                      # scp-like: git@host:owner/repo
    if not m:
        m = re.match(r"^[a-z][a-z0-9+.-]*://(?:[^@/]+@)?([^/]+)/(.+)$", u, re.IGNORECASE)  # scheme://host/owner/repo
    if m:
        u = f"{m.group(1)}/{m.group(2)}"
    return u.rstrip("/").lower()


def _git(*args):
    """Roda git e devolve (ok, stdout_strip). Nunca levanta."""
    try:
        out = subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=15
        )
        return out.returncode == 0, out.stdout.strip()
    except Exception:
        return False, ""


def _load_marker(root: Path):
    f = root / ".repo-identity.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return {"_parse_error": True}


def classify():
    ok_root, root_str = _git("rev-parse", "--show-toplevel")
    if not ok_root:
        return {
            "verdict": "FOREIGN",
            "confidence": "alta",
            "reason": "nao e um repositorio git",
            "writable_master": False,
            "marker_conflict": False,
        }
    root = Path(root_str)
    marker = _load_marker(root) or {}
    canon_remote = marker.get("canonical_remote")
    canon_branch = marker.get("canonical_branch", "main")
    threshold = int(marker.get("stale_behind_threshold", 50))
    marker_role = marker.get("role")

    _, origin = _git("remote", "get-url", "origin")

    # Sinal de export (heuristica fraca: so REBAIXA confianca, nunca promove a master)
    _, recent = _git("log", "-5", "--format=%s")
    is_export = any(EXPORT_RE.match(l) for l in recent.splitlines())

    # Ancestry vs origin/<canon_branch>
    ref = f"origin/{canon_branch}"
    ok_mb, _ = _git("merge-base", "HEAD", ref)
    ok_ab, ab = _git("rev-list", "--left-right", "--count", f"{ref}...HEAD")
    behind = ahead = None
    if ok_ab and ab:
        parts = ab.split()
        if len(parts) == 2:
            behind, ahead = int(parts[0]), int(parts[1])

    remote_matches = bool(canon_remote) and _norm_remote(origin) == _norm_remote(canon_remote)

    marker_conflict = False
    # --- decisao: git autoritativo ---
    if canon_remote and origin and not remote_matches:
        verdict, conf, reason = "FOREIGN", "alta", \
            f"origin ({origin}) != canonical_remote do marker"
    elif not ok_mb or (behind is not None and behind > threshold):
        verdict, conf = "CLONE-VELHO/DIVERGENTE", "alta"
        reason = ("linhagem disjunta (sem merge-base com %s)" % ref) if not ok_mb \
            else f"behind {behind} > limiar {threshold} vs {ref}"
        if marker_role == "master":
            marker_conflict = True  # marker forjado/stale: git vence
    elif marker_role == "shadow" or is_export:
        # SOMBRA: o marker role=shadow e carimbado PELO export-clean.py (trava fisica) -> confiavel.
        # is_export (commit '...@<hash>') e so sinal fraco secundario.
        sig = "marker role=shadow (carimbado pelo export-clean)" if marker_role == "shadow" \
            else "commit de export/publish (@<hash>) -- sinal fraco"
        verdict = "SOMBRA-EXPORT"
        conf = "alta" if marker_role == "shadow" else "media"
        reason = sig
    elif marker_role == "master" and remote_matches:
        # UNICO caminho MASTER positivo. SEGURO porque export-clean carimba role=shadow nos
        # exports: um export nunca chega aqui como 'master'. Fecha o falso-MASTER (qa-critic ALTO).
        # Residual documentado: copia manual/maliciosa re-carimbando 'master' (fora do fluxo).
        verdict, conf, reason = "MASTER-CANONICO", "media", \
            f"marker=master + origin canonico + nao-divergente (ahead={ahead}, behind={behind})"
    else:
        # DEFAULT SEGURO = AMBIGUO. Sem marker confiavel de master e sem sinal de shadow, git NAO
        # prova identidade (master x export-fiel sao indistinguiveis). Escrita exige confirmacao.
        marker_note = "marker ausente" if not marker else f"marker_role={marker_role}"
        verdict, conf, reason = "AMBIGUO", "baixa", \
            f"{marker_note}; git nao prova master vs export-fiel (ahead={ahead}, behind={behind})"

    return {
        "verdict": verdict,
        "confidence": conf,
        "reason": reason,
        "origin": origin,
        "ahead": ahead,
        "behind": behind,
        "is_export_signal": is_export,
        "marker_role": marker_role,
        "marker_conflict": marker_conflict,
        "writable_master": verdict == "MASTER-CANONICO",
    }


def is_export_shadow(r=None):
    """True SO p/ shadow de export GENUINO. Usado pelos gates fail-closed de processo
    (test_qa_evidence/test_posture_gate/test_dev_dogfood) p/ decidir o SKIP — conservador: na duvida
    NAO e shadow (enforce). Fecha 2 achados do process-critic (2026-06-08):
      - b1 (forja): editar o marker role=master->shadow no master real dava SOMBRA-EXPORT e pulava os
        gates. Discriminador anti-forja = `is_export_signal` (commit '...@<hash>' que SO o export-clean
        produz). Carimbo 'shadow' SEM commit de export + git parecendo master = suspeito -> enforce.
      - b2 (false-FAIL): a ordem de `classify()` poe FOREIGN antes de marker_role==shadow; um shadow
        legitimo com remote de distribuicao proprio cairia em FOREIGN e os gates falhariam na CI dele.
        Aqui lemos `marker_role` (carimbo fisico do export-clean) direto -> robusto a essa ordem.
    """
    r = r or classify()
    if r.get("marker_role") != "shadow":
        return False                       # so o carimbo fisico do export-clean conta
    if r.get("writable_master") or r.get("marker_conflict"):
        return False                       # git diz master / conflito declarado -> nao e shadow
    if not r.get("is_export_signal"):
        return False                       # carimbo shadow sem commit de export = forja suspeita
    return True


def announce_line(r):
    base = f"[repo-identity] {r['verdict']} ({r['confidence']}) -- {r['reason']}"
    if r.get("marker_conflict"):
        base += " [!] marker diz 'master' mas git diverge -- marker possivelmente forjado/stale"
    if not r["writable_master"]:
        base += " | ESCRITA exige confirmacao humana (ADR-069/070)"
    return base


def main(argv):
    # Guard de stdout no Windows (cp1252) — evita UnicodeEncodeError (licao execution-report).
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    r = classify()
    if "--json" in argv:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    elif "--line" in argv:
        print(announce_line(r))
    else:
        print(announce_line(r))
        print(f"   origin={r.get('origin')} ahead={r.get('ahead')} behind={r.get('behind')}")
    return 0 if r["writable_master"] else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
