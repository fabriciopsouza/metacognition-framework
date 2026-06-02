#!/usr/bin/env python3
"""Gate de PESQUISA DE CONTEXTO — barra J1 quando há sinal de STAKE e falta o context-brief (ADR-051).

Conserta a inércia PROVADA de ADR-009/033: o reforço sênior (`metodo-senior.md`) era prosa
sob-demanda cujo filtro PROIBIA inferência (logo não disparava), e o coverage-gate
(`check_spec_depth`) só media dimensões de PRODUTO — uma spec sem pesquisa de entidade nem
verificação de âncora regulatória passava. Caso de campo (alias AIVI; evidência no cofre): a âncora
regulatória citada era de OUTRA atividade da cadeia — referencial, não mandatória; ninguém verificou
até a pesquisa de contexto ser de fato executada.

Mecanismo (determinístico, sem deps): se o requirements.md/mission.md exibe SINAIS DE STAKE
(`_shared/discovery/context-signals.txt` — agnóstico, auto-retroalimentado), exige um
`context-brief.md` irmão com (a) tabela de VERIFICAÇÃO DE ÂNCORA (vigência+pertinência),
(b) ≥1 fonte com data, (c) classificação de confiança. Verifica PRESENÇA/ESTRUTURA, NÃO a
qualidade/correção da pesquisa (julgamento + qa-critic adversarial; limite → LIMITS.md).

Uso:
    python tools/check_context_brief.py <requirements.md> [...]   # checa specs dadas
    python tools/check_context_brief.py                           # varre docs/specs/**/requirements.md
Exit 0 se ok (ou nenhum stake/spec); 1 se projeto com stake não tem context-brief válido.
"""
import glob
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIGNALS_PATH = os.path.join(ROOT, "_shared", "discovery", "context-signals.txt")


def _norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s.strip().lower())


def load_signals(path=SIGNALS_PATH):
    """Sinais-semente (uma frase por linha, '#' comenta). Normalizados."""
    sigs = []
    try:
        with open(path, encoding="utf-8-sig") as fh:
            for line in fh:
                line = line.split("#", 1)[0].strip()
                if line:
                    sigs.append(_norm(line))
    except OSError:
        pass
    return [s for s in sigs if s]


def spec_has_stake(text, signals):
    """Sinais de stake no texto, por WORD-BOUNDARY (não substring: 'norma' não casa
    'normalizar' — falso-positivo que o check_spec_depth já ensinou a evitar)."""
    t = _norm(text)
    return sorted({s for s in signals if re.search(r"\b" + re.escape(s) + r"\b", t)})


def learn_signal(sig, path=SIGNALS_PATH):
    """Auto-retroalimentação SEM HITL (ADR-051): registra um sinal novo detectado em operação.
    Append idempotente na lista-semente. Retorna True se adicionou. Agnóstico: o chamador é
    responsável por não passar nome de norma/domínio (check_core_agnostic protege o arquivo)."""
    sig_n = _norm(sig)
    if not sig_n or sig_n in set(load_signals(path)):
        return False
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(sig_n + "\n")
    return True


def find_brief(spec_path):
    """context-brief.md irmão (mesma pasta, ./EVIDENCIAS, ou ../EVIDENCIAS)."""
    d = os.path.dirname(os.path.abspath(spec_path))
    cands = []
    for name in ("context-brief.md", "context_brief.md"):
        cands += [os.path.join(d, name),
                  os.path.join(d, "EVIDENCIAS", name),
                  os.path.join(os.path.dirname(d), "EVIDENCIAS", name)]
    for c in cands:
        if os.path.isfile(c):
            return c
    return None


def brief_ok(text):
    """(ok, faltas) — verifica estrutura mínima do context-brief, não a qualidade."""
    nt = _norm(text)
    faltas = []
    if not ("ancora" in nt and ("pertinen" in nt or "vigenc" in nt)):
        faltas.append("tabela de verificacao-de-ancora (vigencia+pertinencia)")
    has_source = ("http" in nt or "acesso em" in nt or
                  ("fonte" in nt and re.search(r"(19|20)\d{2}", nt)))
    if not has_source:
        faltas.append("fonte com data")
    if not re.search(r"confirmado|inferido|desconhecido", nt):
        faltas.append("classificacao de confianca (CONFIRMADO/INFERIDO/DESCONHECIDO)")
    return (not faltas), faltas


def check_spec(path, signals):
    """(ok, motivo, detalhe)."""
    try:
        with open(path, encoding="utf-8-sig") as fh:
            text = fh.read()
    except OSError as e:
        return False, f"erro io: {e}", []
    stake = spec_has_stake(text, signals)
    if not stake:
        return True, "sem sinal de stake — gate não dispara", []
    # Exceção CONSCIENTE (flag-não-silencia): spec sem entidade externa (ex.: spec interna do
    # framework) pode dispensar o brief com razão registrada — `context-brief: nao-aplicavel — <razão>`.
    if re.search(r"context[- ]brief\s*:\s*(nao[- ]aplicavel|n/?a|isento)", _norm(text)):
        return True, "exceção consciente registrada (sem entidade externa)", []
    brief = find_brief(path)
    if not brief:
        return False, f"stake detectado ({', '.join(stake[:4])}…) e context-brief.md AUSENTE", stake
    with open(brief, encoding="utf-8-sig") as fh:
        ok, faltas = brief_ok(fh.read())
    if ok:
        return True, "context-brief presente e estruturado", []
    return False, "context-brief INCOMPLETO", faltas


def main(argv):
    # stdout ascii-safe / utf-8 (Windows cp1252 quebra em acento/seta — lição de campo + ADR-040)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    # auto-retroalimentação: `--learn <sinal>` registra sinal novo sem HITL (ADR-051)
    if len(argv) >= 3 and argv[1] == "--learn":
        added = learn_signal(" ".join(argv[2:]))
        print(f"sinal {'adicionado' if added else 'já presente/inválido'}: {_norm(' '.join(argv[2:]))}")
        return 0
    signals = load_signals()
    if not signals:
        print("registro de sinais vazio/ilegível — nada a verificar", file=sys.stderr)
        return 1
    targets = argv[1:]
    if not targets:
        targets = glob.glob(os.path.join(ROOT, "docs", "specs", "**", "requirements.md"),
                            recursive=True)
        targets += glob.glob(os.path.join(ROOT, "docs", "specs", "**", "mission.md"),
                             recursive=True)
        targets = [t for t in targets if "_template" not in t]
    if not targets:
        print("nenhum requirements.md/mission.md para checar (gate só dispara com spec).")
        return 0
    any_fail = False
    for path in targets:
        try:
            rel = os.path.relpath(path, ROOT)
        except ValueError:
            rel = path
        ok, motivo, detalhe = check_spec(path, signals)
        if ok:
            print(f"PASS {rel}  — {motivo}")
        else:
            any_fail = True
            print(f"FAIL {rel}  — {motivo}")
            if detalhe:
                print(f"      faltando: {', '.join(detalhe)}")
                print("      -> produza/complete o context-brief.md (perfil de entidade + "
                      "verificacao de ancora + fontes datadas + confianca). Ver ADR-051.")
    print("-" * 50)
    print("RESULTADO:", "FAIL (gate barra J1: contexto/âncora não pesquisado)" if any_fail
          else "PASS (todo projeto com stake tem context-brief válido)")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
