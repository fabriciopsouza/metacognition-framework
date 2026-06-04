#!/usr/bin/env python3
"""Canário de marketing ancorado em evidência (ADR-044 + ADR-059).

Prova:
(a) LIMITS.md em sync com os canários (build_limits --check);
(b) todo claim PROVADO do LIMITS aponta para um canário que EXISTE (zero ✅ órfão);
(c) nenhum doc de marketing (README + prompt web) carrega '✅ PROVADO' sem referência a canário;
(d) README linka o LIMITS.md;
(e) [ADR-059 G1 — fail-closed] o prompt web é DERIVADO de `web_export.PUBLIC_SRC` (fonte única) e
    EXISTE; há exatamente 1 `PROMPT-CHAT-WEB-v*.md` em disco e ele == PUBLIC_SRC. Mata o bug do
    skip silencioso por versão fixa defasada (antes apontava `v4.3` inexistente -> `continue`);
(f) [ADR-059 G2] a vitrine (`guia/web/index.html`) tem ZERO overclaim (absoluto-sem-hedge);
(g) [ADR-059 G3] a vitrine DISCLOSA os limites residuais (não pode overclaim E esconder o limite).

Uso: python tools/test_marketing_claims.py   (exit 0 PASS; 1 se qualquer gate falha)
"""
import os
import re
import sys

try:  # stdout UTF-8: Windows usa cp1252 e quebra no emoji ✅ (lição recorrente do incidente)
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from build_limits import CLAIMS, build, INTERNAL_ONLY  # noqa: E402
import web_export  # noqa: E402  (import-safe: main() só roda sob __main__)
from overclaim_lexicon import find_overclaims  # noqa: E402

VITRINE = os.path.join(ROOT, "guia", "web", "index.html")
WEB_PROMPT_RE = re.compile(r"PROMPT-CHAT-WEB-v.*\.md$")


def main():
    fails = 0

    def gate(ok, desc):
        nonlocal fails
        print(f"{'OK  ' if ok else 'FAIL'} {desc}")
        if not ok:
            fails += 1

    # (e) ADR-059 G1 — prompt web DERIVADO de web_export.PUBLIC_SRC + fail-closed (anti skip silencioso)
    src = web_export.PUBLIC_SRC
    src_base = os.path.basename(src)
    src_exists = os.path.isfile(src)
    on_disk = sorted(f for f in os.listdir(ROOT) if WEB_PROMPT_RE.search(f))
    gate(src_exists, f"prompt web (PUBLIC_SRC={src_base}) existe [fail-closed, não skip]")
    gate(on_disk == [src_base],
         f"exatamente 1 PROMPT-CHAT-WEB-v*.md e == PUBLIC_SRC (anti-drift; on_disk={on_disk})")

    marketing_docs = [os.path.join(ROOT, "README.md")] + ([src] if src_exists else [])

    # (a) LIMITS.md em sync com os canários
    target = os.path.join(ROOT, "LIMITS.md")
    in_sync = os.path.isfile(target) and open(target, encoding="utf-8-sig").read().strip() == build().strip()
    gate(in_sync, "LIMITS.md em sync com os canários (build_limits)")

    # (b) todo claim PROVADO aponta para canário existente (interno não conta — roda na fonte/CI)
    orphan = [c for c, canary, *_ in CLAIMS
              if canary not in INTERNAL_ONLY and not os.path.isfile(os.path.join(ROOT, "tools", canary))]
    gate(not orphan, f"todo claim do LIMITS aponta p/ canário existente "
                     f"({'zero órfão' if not orphan else orphan})")

    # (c) nenhum '✅ PROVADO' órfão em marketing — agora RODA no prompt web real (F1 destrava)
    seal = []
    for p in marketing_docs:
        for i, line in enumerate(open(p, encoding="utf-8-sig").read().splitlines(), 1):
            if "✅" in line and re.search(r"provado", line, re.IGNORECASE):
                if "tools/test_" not in line and "LIMITS.md" not in line:
                    seal.append(f"{os.path.basename(p)}:{i}")
    gate(not seal, f"sem selo PROVADO órfão em marketing ({'nenhum' if not seal else seal})")

    # (d) README linka o LIMITS.md
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8-sig").read()
    gate("LIMITS.md" in readme, "README linka o LIMITS.md")

    # (f) ADR-059 G2 — vitrine sem overclaim (absoluto-sem-hedge)
    if not os.path.isfile(VITRINE):
        gate(False, f"vitrine ausente: {VITRINE} [fail-closed]")
    else:
        vtext = open(VITRINE, encoding="utf-8-sig").read()
        low = vtext.lower()
        vio = find_overclaims(vtext, strip_html=True)
        gate(not vio, f"vitrine sem overclaim ({'nenhum' if not vio else [f'{lab}:{hit}' for lab, hit, _ in vio]})")

        # (g) ADR-059 G3 — disclosure REAL de alucinação residual (proximidade, anti-teatro: 'residual'
        # solto noutra seção não conta — achado MÉD-1 do qa-critic).
        discloses = re.search(r"alucina\w*\s+residual|residual[^.]{0,30}alucina", low) is not None
        gate(discloses, "vitrine disclosa alucinação residual (proximidade real, anti-teatro)")

        # (h) ADR-059 — vitrine não cita prompt web inexistente (anti drift de LINK; achado ALTO-1).
        refs = set(re.findall(r"PROMPT-CHAT-WEB-v[\d.]+\.md", vtext))
        dead = sorted(r for r in refs if not os.path.isfile(os.path.join(ROOT, r)))
        gate(not dead, f"vitrine sem link de prompt morto ({'nenhum' if not dead else dead})")

        # (i) ADR-059 — versão de release citada na vitrine == main (anti drift de VERSÃO; achado ALTO-2).
        mv = web_export.main_version()
        rel = set(re.findall(r"(?:releases/tag/|archive/refs/tags/)v(\d+\.\d+\.\d+)", vtext))
        rel |= set(re.findall(r"<b>\s*v?(\d+\.\d+\.\d+)\s*</b>", vtext))
        stale = sorted(v for v in rel if v != mv)
        gate(mv != "0.0.0" and not stale,
             f"versões de release na vitrine == main v{mv} (stale={stale or 'nenhum'})")

    print("-" * 60)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (marketing+vitrine ancorados: LIMITS sync · zero órfão · prompt web fail-closed · "
               "vitrine sem overclaim · limites disclosos)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
