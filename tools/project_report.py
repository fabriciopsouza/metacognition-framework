#!/usr/bin/env python3
"""project_report.py — Relatório de consumo de tokens + história compactada por projeto (ADR-026).

Lê os transcripts do Claude Code (`~/.claude/projects/<slug>/*.jsonl`) e produz um relatório Markdown:
- **tokens** (input / output / cache) total do projeto e média por sessão;
- **timeline compactada** por sessão (período, # mensagens, # tool calls, tokens);
base auditável para **documentação + reconstrução** (complementa o digest do ADR-016).

Honesto sobre limites: Claude Code-only; o formato do transcript é interno e **version-dependent**
— degrada com segurança se um campo faltar. **NÃO transmite nada** (sem phone-home — ADR-025); só lê
local e escreve um arquivo/saída que VOCÊ controla.

Uso:
  python tools/project_report.py [--dir <pasta dos .jsonl>] [--out report.md]
  (sem --dir: tenta `~/.claude/projects/<slug derivado do cwd>`)
"""
import argparse
from datetime import datetime
import glob
import json
import os
import sys


def derive_slug(cwd):
    """Claude Code troca separadores e ':' por '-' no nome da pasta do projeto."""
    return cwd.replace("\\", "-").replace("/", "-").replace(":", "-")


def find_dir(explicit):
    if explicit:
        return explicit
    base = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    cwd = os.getcwd()
    cand = os.path.join(base, derive_slug(cwd))
    if os.path.isdir(cand):
        return cand
    bn = os.path.basename(cwd).lower()
    if os.path.isdir(base):
        for d in os.listdir(base):
            if d.lower().endswith(bn):
                return os.path.join(base, d)
    return cand  # devolve o candidato p/ mensagem de erro


def parse_session(path):
    tot = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0}
    asst = 0
    tools = 0
    ts = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("timestamp"):
                ts.append(str(obj["timestamp"]))
            msg = obj.get("message") or {}
            usage = msg.get("usage") or obj.get("usage") or {}
            if usage:
                tot["input"] += usage.get("input_tokens", 0) or 0
                tot["output"] += usage.get("output_tokens", 0) or 0
                tot["cache_read"] += usage.get("cache_read_input_tokens", 0) or 0
                tot["cache_creation"] += usage.get("cache_creation_input_tokens", 0) or 0
                asst += 1
            content = msg.get("content")
            if isinstance(content, list):
                tools += sum(1 for c in content if isinstance(c, dict) and c.get("type") == "tool_use")
    return {
        "file": os.path.basename(path), "tokens": tot, "assistant_msgs": asst,
        "tool_uses": tools, "start": min(ts) if ts else None, "end": max(ts) if ts else None,
    }


def _parse_iso(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def session_duration_min(start, end):
    """Duração (min) da sessão = último − primeiro timestamp. None se indeterminável."""
    a, b = _parse_iso(start), _parse_iso(end)
    if a and b and b >= a:
        return (b - a).total_seconds() / 60.0
    return None


def build_report(directory, sessions):
    g = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0}
    for s in sessions:
        for k in g:
            g[k] += s["tokens"][k]
        s["dur_min"] = session_duration_min(s["start"], s["end"])
    n = len(sessions) or 1
    billable = g["input"] + g["output"]
    durs = [s["dur_min"] for s in sessions if s["dur_min"] is not None]
    total_min = sum(durs)
    nd = len(durs) or 1
    L = []
    L.append("# Relatório do projeto — tokens + tempo + história compactada")
    L.append(f"> Fonte: transcripts do Claude Code em `{directory}` · {len(sessions)} sessões · "
             f"gerado por `tools/project_report.py` (ADR-026). Sem transmissão (ADR-025).")
    L.append("")
    L.append("## Tokens (total do projeto)")
    L.append(f"- input: **{g['input']:,}** · output: **{g['output']:,}** · "
             f"cache-read: {g['cache_read']:,} · cache-creation: {g['cache_creation']:,}")
    L.append(f"- **input+output (aprox. faturável): {billable:,}** · "
             f"**média por sessão: {billable // n:,}**")
    L.append("")
    L.append("## Tempo (processamento + interação) — proxy de custo")
    L.append(f"- **total: {total_min / 60:.1f} h** ({total_min:,.0f} min de interação somada, "
             f"{len(durs)}/{len(sessions)} sessões com timestamp) · "
             f"**média por sessão: {total_min / nd:,.0f} min**")
    if total_min > 0:
        L.append(f"- throughput: ~**{billable / total_min:,.0f} tokens/min** (input+output)")
    L.append("> Tempo = janela 1º→último timestamp por sessão (inclui pausas humanas — é "
             "tempo de **interação**, não só CPU). Útil para custo por projeto/processo em corporações.")
    L.append("")
    L.append("## Timeline compactada (por sessão)")
    L.append("| Sessão | Período (UTC) | Duração | Msgs(asst) | Tools | input | output |")
    L.append("|---|---|---|---|---|---|---|")
    for s in sessions:
        per = f"{(s['start'] or '?')[:16]} → {(s['end'] or '?')[:16]}"
        dur = f"{s['dur_min']:,.0f} min" if s["dur_min"] is not None else "?"
        L.append(f"| `{s['file'][:8]}` | {per} | {dur} | {s['assistant_msgs']} | {s['tool_uses']} "
                 f"| {s['tokens']['input']:,} | {s['tokens']['output']:,} |")
    L.append("")
    L.append("> **Base de documentação + reconstrução:** o quê/quanto/quando vem daqui; o digest "
             "(ADR-016) dá as decisões; o detalhe (prompts/respostas) fica nos próprios transcripts — "
             "não copiado aqui (privacidade/tamanho). Nada é transmitido (ADR-025).")
    return "\n".join(L)


def main():
    try:  # stdout em UTF-8 (Windows usa cp1252 por default e quebra em '→')
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", help="pasta com os .jsonl de transcript")
    ap.add_argument("--out", help="arquivo Markdown de saída (default: stdout)")
    args = ap.parse_args()

    directory = find_dir(args.dir)
    if not directory or not os.path.isdir(directory):
        print(f"NAO ENCONTRADO: pasta de transcripts. Use --dir <path>. (tentado: {directory})",
              file=sys.stderr)
        return 1
    files = sorted(glob.glob(os.path.join(directory, "*.jsonl")))
    if not files:
        print(f"sem .jsonl em {directory}", file=sys.stderr)
        return 1
    sessions = [parse_session(f) for f in files]
    report = build_report(directory, sessions)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(report + "\n")
        print(f"relatorio escrito em {args.out} ({len(sessions)} sessoes)")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
