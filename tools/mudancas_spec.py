#!/usr/bin/env python3
"""mudancas_spec.py — registro de mudança e versão gerado da especificação e do git (B3a-3, REQ-12, ADR-124).

Geral: vale para qualquer projeto, regulado ou não.
  Controle de versão   um commit por versão do `spec.md` (git log --follow): versão, data, autor, conteúdo, base
  O que mudou          linhas da seção `# Replanejamento` (data, item, o que mudou, por quê, quem aprovou)
  Correções da base    `### Correções da base` da Parte J, quando houver

Reprova (exit 1, nada gravado): versão sem data ou autor; mudança sem data válida ou sem quem aprovou; arquivo fora
do git. Sem nenhuma versão commitada, também reprova (não há histórico a registrar).

Uso:
    python tools/mudancas_spec.py <spec.md> --out-dir <pasta>
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regulado  # noqa: E402
import spec_fonte  # noqa: E402

COLS_REPLAN = ["data", "item", "o que mudou", "por quê", "quem aprovou"]
COLS_CORRECAO = ["correção", "o que constava", "correção aplicada", "motivo"]


def _linha(c):
    return "| " + " | ".join(x.replace("|", "/") for x in c) + " |"


def _secao_h1(texto, titulo):
    """Linhas da seção `# <titulo>` (fora de bloco de código) até o próximo título de nível 1."""
    out, dentro = [], False
    for ln, fora, h1 in spec_fonte._linhas_classificadas(texto):
        if h1:
            if dentro:
                break
            dentro = ln.strip().lstrip("#").strip().lower() == titulo.lower()
            continue
        if dentro:
            out.append(ln)
    return out


def _tabela(linhas, cols):
    rows = []
    for ln in linhas:
        s = ln.strip()
        if not s.startswith("|") or re.match(r"^\|?\s*:?-{3,}", s):
            continue
        cel = [c.strip() for c in re.split(r"(?<!\\)\|", s.strip("|"))]
        if [c.lower() for c in cel] == cols:
            continue
        if len(cel) == len(cols) and any(cel):
            rows.append(dict(zip(cols, cel)))
    return rows


def versoes(spec):
    pasta = os.path.dirname(os.path.abspath(spec))
    r = subprocess.run(["git", "-C", pasta, "log", "--follow", "--date=short", "--format=%h%x09%ad%x09%an%x09%s",
                        "--", os.path.basename(spec)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if r.returncode != 0:
        return None
    out = []
    for ln in r.stdout.splitlines():
        p = ln.split("\t")
        if len(p) == 4:
            out.append({"versão": p[0], "data": p[1], "autor": p[2], "conteúdo": p[3]})
    return list(reversed(out))


def montar(spec):
    texto = open(spec, encoding="utf-8-sig").read()
    ach = []
    vs = versoes(spec)
    if vs is None:
        ach.append("o arquivo não está num repositório git: não há histórico de versões")
        vs = []
    elif not vs:
        ach.append("nenhuma versão commitada da especificação")
    for i, v in enumerate(vs):
        v["base"] = vs[i - 1]["versão"] if i else "—"
        if not v["data"] or not v["autor"].strip():
            ach.append(f"versão {v['versão']} sem data ou autor")
    replan = _tabela(_secao_h1(texto, "Replanejamento"), COLS_REPLAN)
    for m in replan:
        if not regulado._tem_data(m["data"]):
            ach.append(f"mudança '{m['item']}' sem data válida (dd/mm/aaaa)")
        if regulado._vazio(m["quem aprovou"]):
            ach.append(f"mudança '{m['item']}' sem quem aprovou")
    parte_j = spec_fonte.ler_parte(spec, "verificacao") if spec_fonte.eh_unico(spec) else None
    correcoes = []
    if parte_j:
        dentro, linhas = False, []
        for ln in parte_j.splitlines():
            if ln.startswith("### "):
                dentro = ln[4:].strip().lower().startswith("correções da base")
                continue
            if dentro:
                linhas.append(ln)
        correcoes = _tabela(linhas, COLS_CORRECAO)
    titulo = next((ln[2:].strip() for ln in texto.splitlines() if ln.startswith("# ") and "Parte" not in ln), "")
    md = [f"# Mudança e versão — {titulo}", "", "## Controle de versão", "",
          _linha(["Versão", "Data", "Autor", "Conteúdo", "Base utilizada"]), _linha(["---"] * 5)]
    md += [_linha([v["versão"], v["data"], v["autor"], v["conteúdo"], v["base"]]) for v in vs]
    md += ["", "## O que mudou", ""]
    if replan:
        md += [_linha(["Data", "Item", "O que mudou", "Por quê", "Quem aprovou"]), _linha(["---"] * 5)]
        md += [_linha([m[c] for c in COLS_REPLAN]) for m in replan]
    else:
        md.append("Nenhuma mudança de escopo registrada.")
    if correcoes:
        md += ["", "## Correções da base", "", _linha(["Correção", "O que constava", "Correção aplicada", "Motivo"]),
               _linha(["---"] * 4)] + [_linha([c[k] for k in COLS_CORRECAO]) for c in correcoes]
    return "\n".join(md) + "\n", ach


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    args = [a for a in argv[1:] if not a.startswith("--")]
    out = argv[argv.index("--out-dir") + 1] if "--out-dir" in argv and argv.index("--out-dir") + 1 < len(argv) else None
    args = [a for a in args if a != out]
    if len(args) != 1 or not out:
        print(__doc__)
        return 2
    md, ach = montar(args[0])
    for a in ach:
        print(f"  - {a}")
    if ach:
        print("RESULTADO: FAIL — nada gravado")
        return 1
    import gen_exec_doc  # noqa: E402
    escritos, _ = gen_exec_doc.export(md, out, ["md", "docx"], basename="mudanca-e-versao")
    for p in escritos:
        print(f"gerado: {p}")
    print("RESULTADO: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
