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
import glob
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
    # (g) OS NUMEROS DA VITRINE SAO OS DO REPO, E SIGNIFICAM O QUE A PAGINA DIZ.
    #
    # A 1a versao desta checagem tinha DOIS defeitos, os dois achados pelo qa-critic (Sonnet,
    # 2026-08-17), e o primeiro era grave:
    #
    # (i) a pagina afirmava "38 de 89 capacidades tiveram o mecanismo SABOTADO de proposito". O
    #     numero batia com o auditor, mas a FRASE era falsa para 27 delas: "em conformidade" conta
    #     tambem quem declara protecao nao-bloqueante, sem sabotagem nenhuma. So' 11 tem `mutacao`.
    #     Era overclaim mecanizado — na pagina inicial do repo que existe para combater overclaim.
    #     Agora a vitrine separa os dois numeros e diz o que cada um mede.
    #
    # (ii) a comparacao era `substring in arquivo inteiro`, cega a contexto: a string dentro de um
    #      comentario HTML satisfazia o gate enquanto o numero VISIVEL estava errado. Agora os
    #      comentarios sao removidos e a busca acontece SO' dentro da secao `#provas`.
    #
    # A fórmula de "conforme" e' IMPORTADA do auditor, nao copiada: duplicar a regra faria este
    # canario validar contra uma versao velha dela sem ninguem perceber — o mesmo defeito que o
    # `test_qa_evidence` tinha e que foi corrigido na v1.85.0.
    if os.path.isfile(VITRINE):
        import json as _json
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        from audit_enforcement import valida_mutacao  # noqa: E402
        try:
            _caps = _json.load(open(os.path.join(ROOT, "capabilities.json"), encoding="utf-8"))
            _caps = _caps.get("capabilities", _caps)
            total = len(_caps)
            provadas = sum(1 for c in _caps
                           if c.get("mutacao") and valida_mutacao(c["mutacao"], c)[0])
            fc_sem_prova = sum(1 for c in _caps
                               if c.get("enforcement") == "fail-closed" and not c.get("mutacao"))
            sem_campo = sum(1 for c in _caps if not c.get("enforcement"))
            fracos = total - provadas - fc_sem_prova - sem_campo
            conformes = sum(1 for c in _caps if c.get("enforcement")
                            and (c.get("enforcement") != "fail-closed" or c.get("mutacao")))
            canarios = len(glob.glob(os.path.join(ROOT, "tools", "test_*.py")))
        except Exception as e:
            gate(False, f"nao consegui derivar os numeros da vitrine: {e}")
        else:
            visivel = re.sub(r"<!--.*?-->", "", vtext, flags=re.S)
            m = re.search(r'id="provas".*?</section>', visivel, re.S)
            secao = m.group(0) if m else ""
            gate(bool(secao), "vitrine sem a secao #provas — os numeros nao tem onde morar")
            for valor, oquee in ((f"{provadas} de {total}", "capacidades com sabotagem provada"),
                                 (f"{canarios} canários", "canarios na suite"),
                                 (f"{fc_sem_prova} capacidades", "declaram bloquear e nao foram provadas"),
                                 (f"<b>{sem_campo}</b>", "sem declaracao de protecao"),
                                 (f"<b>{fracos}</b>", "protecao nao-bloqueante"),
                                 (f"{conformes} de {total}", "em conformidade no registro")):
                gate(valor in secao,
                     f"a secao #provas nao afirma '{valor}' ({oquee}) — numero da pagina divergiu "
                     f"do repo, ou saiu da secao; atualize guia/web/index.html")

    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (marketing+vitrine ancorados: LIMITS sync · zero órfão · prompt web fail-closed · "
               "vitrine sem overclaim · limites disclosos)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
