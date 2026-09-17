#!/usr/bin/env python3
"""Canario dev-dogfood DETERMINISTICO (ADR-074 emendado): um repo-MASTER (dev) que fecha bloco DEVE
ter os artefatos de dogfood — execution-report (telemetria de processo) + handoff cross-IA. NAO e
opt-in nem provocado: o opt-in e so a PUBLICACAO publica (ADR-062/063); a GERACAO dev-side e exigida.

Shadow-aware (ADR-070): so MASTER gera cross-IA. Detecta master pela presenca de `docs/_private/`
(o cofre, stripado dos shadows por export-clean) -> num shadow, este canario PASSA (nao cobra cross-IA).

FORWARD-floor honesto: exige que os artefatos EXISTAM (CI vermelho num master sem eles -> forca o
dogfood). Frescor por-release e disciplina do /checkpoint (ADR-074 camada de oferta); o EXISTIR e o
piso determinista que tira o "so gera se o dono pedir".

Uso: python tools/test_dev_dogfood.py   (exit 0 PASS; 1 se falha)
"""
import glob
import os
import sys
import tempfile

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


def autoteste():
    """Fixtures que este canario e OBRIGADO a acertar (ADR-106).

    O piso anti-placeholder (`_is_real_doc`) nasceu de um achado do qa-critic em 2026-06-08:
    `glob != []` era gameavel por um arquivo de 4 bytes. Mas o piso em si nunca foi testado —
    classe `mechanism == test`: com os documentos reais presentes no repo, afrouxar o piso
    deixava o canario VERDE, e o gate voltava a ser gameavel sem nenhum sinal.
    """
    falhas = []
    corpo = ("texto de verdade. " * 40)          # ~700 chars, acima dos dois pisos
    with tempfile.TemporaryDirectory(prefix="dogfood-fx-") as td:
        def doc(nome, conteudo):
            p = os.path.join(td, nome)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(conteudo)
            return p

        bom = doc("bom.md", "# Titulo" + chr(10) + chr(10) + "## Secao" + chr(10) + corpo)
        if not _is_real_doc(bom, MIN_REPORT_CHARS):
            falhas.append("documento REAL (tamanho + secao) foi rejeitado — detector cego")

        curto = doc("curto.md", "# t" + chr(10) + "## Secao" + chr(10) + "meia duzia de palavras")
        if _is_real_doc(curto, MIN_REPORT_CHARS):
            falhas.append("placeholder CURTO passou no piso de tamanho — e' exatamente a fraude "
                          "que o piso existe para barrar (arquivo de 4 bytes gameava o glob)")

        sem_secao = doc("sem-secao.md", "# So um titulo" + chr(10) + corpo)
        if _is_real_doc(sem_secao, MIN_REPORT_CHARS):
            falhas.append("documento SEM secao markdown passou — placeholder de 1 linha "
                          "com muito texto continuaria valendo como dogfood")

        if _is_real_doc(os.path.join(td, "nao-existe.md"), MIN_REPORT_CHARS):
            falhas.append("arquivo INEXISTENTE foi aceito — fail-closed furado")

        if MIN_HANDOFF_CHARS >= MIN_REPORT_CHARS:
            falhas.append(f"pisos incoerentes: handoff ({MIN_HANDOFF_CHARS}) deveria ser menor "
                          f"que report ({MIN_REPORT_CHARS})")
    return falhas


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

    falhas_canario = autoteste()
    if falhas_canario:
        print("auto-teste do detector (5 fixtures) - FAIL")
        for f in falhas_canario:
            print("  -", f)
        print("RESULTADO: FAIL (o piso anti-placeholder do dogfood esta furado)")
        return 1
    print("auto-teste do detector (5 fixtures) - OK")

    fails = []
    # OS DOIS CAMINHOS, e a razao e' um achado, nao zelo.
    #
    # `execution_report.py` escreve o relatorio canonico em `docs/_private/_intake/`.
    # Este gate varria SO' `docs/_private/`, onde moram sete arquivos de junho/2026 —
    # e passava por causa deles, cego aos dez relatorios do caminho atual. Gate
    # fail-closed permanentemente VERDE por artefato morto.
    #
    # Como se descobriu: o critico da 26a rodada apagou os sete por acidente e o gate
    # ficou vermelho na hora. Sem o acidente, ele seguiria verde sem olhar nada do que
    # esta sessao produziu. Varrer o caminho ERRADO nao e' o mesmo que nao varrer: e'
    # pior, porque o placar diz que olhou.
    execs = [p for padrao in (os.path.join(priv, "execution-report-*.md"),
                              os.path.join(priv, "_intake", "execution-report*.md"))
             for p in glob.glob(padrao) if _is_real_doc(p, MIN_REPORT_CHARS)]
    handoffs = [p for p in glob.glob(os.path.join(priv, "cross-ai", "outbox", "*.md"))
                if _is_real_doc(p, MIN_HANDOFF_CHARS)]
    if not execs:
        fails.append("MASTER sem execution-report nao-trivial (docs/_private/ OU "
                     f"docs/_private/_intake/, >={MIN_REPORT_CHARS} chars + secao) — "
                     f"dogfood dev nao gerado/placeholder")
    if not handoffs:
        fails.append("MASTER sem handoff cross-IA nao-trivial (docs/_private/cross-ai/outbox/*.md, "
                     f">={MIN_HANDOFF_CHARS} chars + secao) — melhoria nao propagada/placeholder")

    print(f"master(docs/_private)=True; execution-reports validos={len(execs)}; "
          f"handoffs cross-IA validos={len(handoffs)} — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (master tem dogfood dev determinista: report + handoff cross-IA nao-triviais)"
          if not fails else f"FAIL ({len(fails)} — dogfood dev exigido, nao opt-in)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
