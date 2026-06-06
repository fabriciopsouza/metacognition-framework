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

    remote_matches = bool(canon_remote) and origin.rstrip("/").replace(".git", "") == \
        canon_remote.rstrip("/").replace(".git", "")

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
    elif is_export:
        verdict, conf, reason = "SOMBRA-EXPORT", "media", \
            "commit de export/publish recente (@<hash>)"
    elif behind == 0 and (ahead == 0 or ahead is None) and not is_export:
        # mesmo HEAD do canonico, sem sinal de export -> indistinguivel
        if marker_role == "master" and remote_matches:
            verdict, conf, reason = "MASTER-CANONICO", "media", \
                "origin canonico + em sync; marker=master (corrobora)"
        else:
            verdict, conf, reason = "AMBIGUO", "baixa", \
                "em sync com o canonico, mas indistinguivel de export-fiel sem marker confiavel"
    else:
        # ahead num branch de feature que trackeia o canonico = trabalho normal no master
        verdict, conf, reason = "MASTER-CANONICO", "media", \
            f"origin canonico, ancestral de {ref} (ahead={ahead}, behind={behind})"

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
