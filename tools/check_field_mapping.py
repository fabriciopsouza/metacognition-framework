#!/usr/bin/env python3
"""Gate de ambiguidade de campo-fonte — mapeamento termo->coluna é DECISÃO REGISTRADA (ADR-035).

GAP de campo (o erro mais caro da sessão): existiam colunas-irmãs com nomes próximos; o agente
mapeou um termo de domínio para a coluna **literal** por inferência, bateu/quase-bateu o número-alvo,
e **abandonou um resultado já validado** sem prova numérica. Gatilhos: (a) bater valor-alvo tratado
como validar semântica; (b) over-correção por rótulo; (c) mapear termo->coluna por inferência.

O que É mecanizável (e este gate faz): a **exigência de REGISTRO**. Quando o `requirements.md` declara
um mapeamento de campo-fonte (seção `## Mapeamento de campo-fonte`), CADA linha de mapeamento deve
carregar: (i) **confirmação do dono** (não inferência) e (ii) **justificativa** (porquê). Linha sem
confirmação ou sem justificativa = FAIL — o gate recusa abençoar um mapeamento por inferência, mesmo
que bata o número.

O que NÃO é mecanizável (e fica adversarial → LIMITS.md): se a justificativa está semanticamente
CERTA. "Bater valor != validar semântica" e "não abandonar resultado validado sem prova numérica"
são regras do qa-critic (julgamento adversarial); este gate garante que a decisão foi REGISTRADA.

Uso:
    python tools/check_field_mapping.py <requirements.md> [...]
    python tools/check_field_mapping.py            # docs/specs/*/requirements.md

Exit 0 se todo mapeamento declarado está registrado (confirmação + justificativa); 1 caso contrário.
O gate só dispara quando HÁ seção de mapeamento (ausência = nada a registrar).
"""
import glob
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIRM_RX = re.compile(
    r"\[\s*confirmado\b|confirmad[oa]\s+pelo\s+dono|decis[aã]o\s+do\s+dono|"
    r"registrad[oa]\s+pelo\s+dono|dono\s+confirmou|confirma[cç][aã]o\s*:\s*\S",
    re.IGNORECASE)
JUSTIFY_RX = re.compile(r"porqu[eê]\s*[:=]\s*\S|justificativa\s*[:=]\s*\S|raz[aã]o\s*[:=]\s*\S",
                        re.IGNORECASE)
# Linha de mapeamento: tem termo -> coluna (seta) ou "coluna:" explícito.
MAP_LINE_RX = re.compile(r"->|→|\bcoluna\b|\bcampo\b", re.IGNORECASE)


def _norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s.strip().lower())


def mapping_section(text):
    lines = text.splitlines()
    out, in_sec, lvl = [], False, 0
    for ln in lines:
        h = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if h:
            t = _norm(h.group(2))
            if not in_sec and ("campo-fonte" in t or "campo fonte" in t
                               or "mapeamento de campo" in t or "field mapping" in t):
                in_sec, lvl = True, len(h.group(1))
                continue
            if in_sec and len(h.group(1)) <= lvl:
                break
        if in_sec:
            out.append(ln)
    return out


def check_text(text):
    """Retorna (tem_secao, linhas_nao_registradas)."""
    sec = mapping_section(text)
    if not sec:
        return False, []
    bad = []
    for ln in sec:
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith(">"):
            continue
        # só linhas que parecem um mapeamento (lista/tabela com seta ou 'coluna/campo')
        if not (s[0] in "-*|" and MAP_LINE_RX.search(s)):
            continue
        if s.startswith("|") and set(s.replace("|", "").strip()) <= {"-", ":", " "}:
            continue  # separador de tabela
        has_confirm = bool(CONFIRM_RX.search(s))
        has_justify = bool(JUSTIFY_RX.search(s))
        if not (has_confirm and has_justify):
            falta = []
            if not has_confirm:
                falta.append("confirmação-do-dono")
            if not has_justify:
                falta.append("justificativa(porque:)")
            bad.append((s[:90], falta))
    return True, bad


def check_spec(path):
    try:
        text = open(path, encoding="utf-8-sig").read()
    except OSError as e:
        return False, True, [(f"<io {e}>", ["io"])]
    has_sec, bad = check_text(text)
    return (len(bad) == 0), has_sec, bad


def main(argv):
    targets = argv[1:]
    if not targets:
        targets = [t for t in glob.glob(os.path.join(ROOT, "docs", "specs", "**", "requirements.md"),
                                        recursive=True) if "_template" not in t]
    if not targets:
        print("nenhum requirements.md para checar (gate só dispara quando há mapeamento).")
        return 0
    any_fail = False
    for path in targets:
        try:  # spec em drive/mount diferente do framework (Windows) → relpath lança ValueError (§13.1)
            rel = os.path.relpath(path, ROOT) if os.path.isabs(path) else path
        except ValueError:
            rel = path
        ok, has_sec, bad = check_spec(path)
        if not has_sec:
            print(f"PASS {rel}  (sem seção de mapeamento de campo-fonte — nada a registrar)")
            continue
        if ok:
            print(f"PASS {rel}  (todo mapeamento registrado: confirmação + justificativa)")
        else:
            any_fail = True
            print(f"FAIL {rel}  — mapeamento por inferência (sem registro):")
            for snippet, falta in bad:
                print(f"      - '{snippet}'  falta: {', '.join(falta)}")
    print("-" * 50)
    print("RESULTADO:", "FAIL (mapeamento termo->coluna sem decisão registrada do dono)" if any_fail
          else "PASS (mapeamentos de campo-fonte registrados)")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
