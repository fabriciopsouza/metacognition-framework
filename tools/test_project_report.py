#!/usr/bin/env python3
"""Canary do project_report (ADR-026): confirma que agrega tokens dos transcripts corretamente.

Cria um .jsonl sintético com campos de usage conhecidos e verifica que o relatório soma certo
e degrada com segurança em linhas malformadas.

Uso: python tools/test_project_report.py   (exit 0 se ok; 1 caso contrário)
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import project_report as pr  # noqa: E402


def main():
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "sess1.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            # 2 mensagens com usage + 1 linha malformada + 1 user sem usage
            fh.write(json.dumps({"timestamp": "2026-05-31T10:00:00Z",
                                 "message": {"usage": {"input_tokens": 100, "output_tokens": 50,
                                                       "cache_read_input_tokens": 10},
                                             "content": [{"type": "tool_use"}]}}) + "\n")
            fh.write("{ malformado json >>>\n")
            fh.write(json.dumps({"timestamp": "2026-05-31T10:05:00Z",
                                 "message": {"usage": {"input_tokens": 200, "output_tokens": 70}}}) + "\n")
            fh.write(json.dumps({"type": "user", "message": {"content": "oi"}}) + "\n")

        s = pr.parse_session(path)
        checks = [
            ("input soma", s["tokens"]["input"], 300),
            ("output soma", s["tokens"]["output"], 120),
            ("cache_read soma", s["tokens"]["cache_read"], 10),
            ("msgs com usage", s["assistant_msgs"], 2),
            ("tool_uses", s["tool_uses"], 1),
            ("duracao (10:00->10:05 = 5 min)", pr.session_duration_min(s["start"], s["end"]), 5.0),
        ]
        for name, got, exp in checks:
            ok = got == exp
            print(f"{'OK  ' if ok else 'FAIL'} {name}: {got} (esperado {exp})")
            if not ok:
                fails += 1

        report = pr.build_report(d, [s])
        if "300" not in report or "120" not in report:
            print("FAIL relatorio nao contem os totais esperados")
            fails += 1
        else:
            print("OK   relatorio agrega input/output")

    print("-" * 40)
    print(f"RESULTADO: {'PASS (agrega tokens; degrada em linha malformada)' if not fails else f'FAIL ({fails})'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
