#!/usr/bin/env python3
"""execution_report.py — relatório de execução automático no encerramento de bloco (ADR-038).

Estende o `project_report.py` (ADR-026): além de tokens/tempo, emite o **placar gate × achado**
("quem pegou o quê"), rodadas de retrabalho, arquivos tocados, testes — o que faltava para o
framework **aprender com a própria execução** (meta-gap nº1 do incidente: nada disso era medido,
e o placar só existiu porque o dono cobrou).

INVARIANTE ANTI-FABRICAÇÃO (o ponto): quando a telemetria de token **não está exposta**, o campo
tokens é literalmente **"NÃO MEDIDO"** — NUNCA um número inventado. Um número de token só é válido
se vier com **fonte declarada** (transcripts ADR-026 / telemetria do host). `validate_report()`
reprova report ausente, sem o placar, ou com token fabricado sem fonte.

Expor a telemetria de token ao agente em tempo real é **dependência externa do host** (não
mecanizável pelo framework sozinho) → declarada em `LIMITS.md`. O que o framework mecaniza: o
report auto-gerado, o placar, e a recusa de fabricar o número.

Uso:
    python tools/execution_report.py [--from-transcripts] [--out report.md]
    python tools/execution_report.py --validate <report.md>

Exit 0 ok; 1 falha de validação/geração.
"""
import argparse
import os
import re
import sys
import unicodedata

REQUIRED = {
    "tokens": ["token"],
    "tempo": ["tempo", "wall-clock", "wall clock", "duracao"],
    "turnos": ["turno"],
    "arquivos": ["arquivo"],
    "testes": ["teste"],
    "retrabalho": ["retrabalho", "rework"],
    "placar": ["placar", "gate x achado", "gate × achado", "quem pegou"],
}
SOURCE_KEYS = ("fonte:", "transcript", "telemetria", "usage", "adr-026")
NAO_MEDIDO = "NÃO MEDIDO"


def _norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s.lower()


def token_value_ok(text):
    """A linha de tokens diz 'NÃO MEDIDO' OU tem número COM fonte declarada. Número sem fonte = fabricado."""
    n = _norm(text)
    # localizar a(s) linha(s) que falam de token
    token_lines = [ln for ln in n.splitlines() if "token" in ln]
    if not token_lines:
        return False, "sem campo de tokens"
    for ln in token_lines:
        if "nao medido" in ln:
            return True, "NÃO MEDIDO (honesto)"
        if re.search(r"\d{2,}", ln):
            if any(k in ln for k in SOURCE_KEYS):
                return True, "número com fonte declarada"
            return False, "número de token sem fonte declarada (fabricado)"
    # campo de tokens existe mas sem número e sem 'não medido' -> exigir explícito
    return False, "campo de tokens sem 'NÃO MEDIDO' nem número+fonte"


def validate_report(text):
    """Retorna (ok, problemas)."""
    problems = []
    if not text or not text.strip():
        return False, ["report ausente/vazio (encerramento sem execution-report)"]
    n = _norm(text)
    for sec, needles in REQUIRED.items():
        if not any(_norm(x) in n for x in needles):
            problems.append(f"seção ausente: {sec}")
    ok_tok, why = token_value_ok(text)
    if not ok_tok:
        problems.append(f"tokens: {why}")
    return (len(problems) == 0), problems


def build_report(tokens_line=None, wall_clock="NÃO MEDIDO", turnos="NÃO MEDIDO",
                 arquivos=None, testes="NÃO MEDIDO", retrabalho="NÃO MEDIDO", placar=None):
    if tokens_line is None:
        tokens_line = f"{NAO_MEDIDO} — sem telemetria de token exposta ao agente (dependência do host; ver LIMITS.md)"
    arquivos = arquivos or "NÃO MEDIDO"
    placar = placar or [("(preencher por bloco)", "quem pegou", "gate que deveria")]
    L = []
    L.append("# Execution-report — encerramento de bloco (ADR-038, estende ADR-026)")
    L.append("")
    L.append(f"- **Tokens:** {tokens_line}")
    L.append(f"- **Tempo (wall-clock):** {wall_clock}")
    L.append(f"- **Turnos:** {turnos}")
    L.append(f"- **Arquivos tocados:** {arquivos}")
    L.append(f"- **Testes:** {testes}")
    L.append(f"- **Rodadas de retrabalho:** {retrabalho}")
    L.append("")
    L.append("## Placar gate × achado (quem pegou o quê)")
    L.append("| Achado | Quem pegou | Gate que deveria ter pego |")
    L.append("|---|---|---|")
    for achado, quem, gate in placar:
        L.append(f"| {achado} | {quem} | {gate} |")
    return "\n".join(L)


def tokens_from_transcripts():
    """Tenta ler tokens dos transcripts (project_report, ADR-026). None se indisponível."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import project_report as pr  # noqa
        import glob
        directory = pr.find_dir(None)
        if not directory or not os.path.isdir(directory):
            return None
        files = sorted(glob.glob(os.path.join(directory, "*.jsonl")))
        if not files:
            return None
        g = {"input": 0, "output": 0}
        for f in files:
            s = pr.parse_session(f)
            g["input"] += s["tokens"]["input"]
            g["output"] += s["tokens"]["output"]
        if g["input"] + g["output"] == 0:
            return None
        return (f"input {g['input']:,} + output {g['output']:,} = {g['input'] + g['output']:,} "
                f"(fonte: transcripts do Claude Code, ADR-026)")
    except Exception:
        return None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-transcripts", action="store_true", help="preencher tokens via project_report (ADR-026)")
    ap.add_argument("--out", help="arquivo de saída (default stdout)")
    ap.add_argument("--validate", help="validar um report existente em vez de gerar")
    args = ap.parse_args()

    if args.validate:
        try:
            text = open(args.validate, encoding="utf-8-sig").read()
        except OSError as e:
            print(f"FAIL: {e}")
            return 1
        ok, problems = validate_report(text)
        print("PASS: execution-report válido" if ok else "FAIL: " + "; ".join(problems))
        return 0 if ok else 1

    tokens_line = tokens_from_transcripts() if args.from_transcripts else None
    report = build_report(tokens_line=tokens_line)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(report + "\n")
        print(f"execution-report escrito em {args.out}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
