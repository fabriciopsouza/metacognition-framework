#!/usr/bin/env python3
"""Canario dev-dogfood DETERMINISTICO (ADR-074 emendado): um repo-MASTER (dev) que fecha bloco DEVE
ter os artefatos de dogfood — execution-report (telemetria de processo) + handoff cross-IA. NAO e
opt-in nem provocado: o opt-in e so a PUBLICACAO publica (ADR-062/063); a GERACAO dev-side e exigida.

Shadow-aware (ADR-070): so MASTER gera cross-IA. Detecta master pela presenca de `docs/_private/`
(o cofre, stripado dos shadows por export-clean) -> num shadow, este canario PASSA (nao cobra cross-IA).

FORWARD-floor honesto: exige que os artefatos EXISTAM (CI vermelho num master sem eles -> forca o
dogfood).

[ADR-101, 2026-08-08] FRESCOR TAMBEM E MECANISMO. Ate aqui o frescor por-release era "disciplina do
/checkpoint" — ou seja, PROSA. Resultado medido pelo dono: o outbox cross-IA parou em 2026-06-09 e
este canario seguiu VERDE por dois meses, porque arquivos velhos satisfazem "existe". Um gate que
mede existencia e se anuncia como dogfood mede menos do que promete. Agora exige-se tambem que
>=1 execution-report E >=1 handoff cross-IA CITEM a release do topo do CHANGELOG.
Ancora por CONTEUDO, nao por mtime: clone/checkout do git reescreve mtime, entao data de arquivo
nao e evidencia. Forward-only: cobra a release ATUAL, nao reprova o historico.

Uso: python tools/test_dev_dogfood.py   (exit 0 PASS; 1 se falha)
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Pisos anti-placeholder (qa-critic 2026-06-08): `glob != []` era gameavel por arquivo trivial
# de 4 bytes ("# x"). Exigir tamanho nao-trivial + esqueleto markdown real (>=1 secao `## `).
MIN_REPORT_CHARS = 500
MIN_HANDOFF_CHARS = 300


def _is_real_doc(path, min_chars):
    """Arquivo existe, tem tamanho nao-trivial e ao menos uma secao markdown (## ...)."""
    try:
        t = open(path, encoding="utf-8-sig").read()
    except Exception:
        return False
    if len(t.strip()) < min_chars:
        return False
    # ao menos um heading de secao real (nao so "# x") -> placeholder de 1 linha reprova
    return any(ln.lstrip().startswith("## ") for ln in t.splitlines())


def _current_release():
    """Versao do TOPO do CHANGELOG (ex.: '1.78.0'). None se ilegivel — frescor vira FAIL, nunca OK."""
    import re
    try:
        t = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8-sig").read()
    except Exception:  # noqa: BLE001
        return None
    m = re.search(r"^##\s*\[(\d+\.\d+\.\d+)\]", t, re.M)
    return m.group(1) if m else None


def _cites(path, release):
    """O artefato menciona a release atual? Ancora por CONTEUDO — mtime de arquivo nao e evidencia
    (git reescreve na clonagem). Aceita '1.78.0' e 'v1.78.0'."""
    if not release:
        return False
    try:
        t = open(path, encoding="utf-8-sig").read()
    except Exception:  # noqa: BLE001
        return False
    return release in t


def _is_genuine_shadow():
    """docs/_private ausente -> so e SHADOW legitimo se repo_identity confirmar (defesa em
    profundidade, qa-critic MEDIO). Master degradado (sem _private mas git=master) NAO e isento.
    Fail-soft: se repo_identity indisponivel, mantem o sinal unico (comportamento antigo)."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import repo_identity
        # SHADOW legitimo = export carimbado COM commit de export (anti-forja b1/b2, process-critic
        # 2026-06-08). MASTER/AMBIGUO sem _private = anomalia (nao isenta).
        if repo_identity.is_export_shadow():
            return True, "repo_identity.is_export_shadow (carimbo + commit de export) — shadow legitimo"
        v = repo_identity.classify().get("verdict")
        if v == "MASTER-CANONICO":
            return False, f"repo_identity={v} mas docs/_private AUSENTE — master degradado, NAO isento"
        return None, f"repo_identity={v} — ambiguo; cai no fail-soft do sinal unico"
    except Exception as e:
        return None, f"repo_identity indisponivel ({type(e).__name__}) — fail-soft sinal unico"


def main():
    priv = os.path.join(ROOT, "docs", "_private")
    if not os.path.isdir(priv):
        genuine, why = _is_genuine_shadow()
        if genuine is False:
            print(f"docs/_private ausente MAS {why}")
            print("RESULTADO: FAIL (master sem _private — estado anomalo, dogfood nao verificavel)")
            return 1
        # True (shadow confirmado) ou None (fail-soft) -> PASS, nao cobra cross-IA
        print(f"docs/_private ausente -> SHADOW. {why}. PASS (nao cobra dogfood).")
        print("RESULTADO: PASS (shadow — sem cobranca de cross-IA)")
        return 0

    fails = []
    execs = [p for p in glob.glob(os.path.join(priv, "execution-report-*.md"))
             if _is_real_doc(p, MIN_REPORT_CHARS)]
    handoffs = [p for p in glob.glob(os.path.join(priv, "cross-ai", "outbox", "*.md"))
                if _is_real_doc(p, MIN_HANDOFF_CHARS)]
    if not execs:
        fails.append("MASTER sem execution-report nao-trivial (docs/_private/execution-report-*.md, "
                     f">={MIN_REPORT_CHARS} chars + secao) — dogfood dev nao gerado/placeholder")
    if not handoffs:
        fails.append("MASTER sem handoff cross-IA nao-trivial (docs/_private/cross-ai/outbox/*.md, "
                     f">={MIN_HANDOFF_CHARS} chars + secao) — melhoria nao propagada/placeholder")

    # [ADR-101] FRESCOR por release, ancorado em CONTEUDO (mtime nao sobrevive a clone/checkout).
    rel = _current_release()
    fresh_e = [p for p in execs if _cites(p, rel)] if rel else []
    fresh_h = [p for p in handoffs if _cites(p, rel)] if rel else []
    if not rel:
        fails.append("release do topo do CHANGELOG ilegivel — frescor NAO verificavel (nunca falso-OK)")
    else:
        if execs and not fresh_e:
            fails.append(f"execution-report(s) existem mas NENHUM cita a release {rel} — "
                         f"artefato velho satisfazia 'existe' e o gate passava verde (era o furo)")
        if handoffs and not fresh_h:
            fails.append(f"handoff cross-IA existe mas NENHUM cita a release {rel} — a propagacao "
                         f"cross-IA parou e o gate nao acusava (relato do dono 2026-08-07)")

    print(f"master(docs/_private)=True; execution-reports validos={len(execs)} (frescos p/ {rel}: "
          f"{len(fresh_e)}); handoffs cross-IA validos={len(handoffs)} (frescos: {len(fresh_h)}) — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (master tem dogfood dev determinista: report + handoff cross-IA nao-triviais)"
          if not fails else f"FAIL ({len(fails)} — dogfood dev exigido, nao opt-in)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
