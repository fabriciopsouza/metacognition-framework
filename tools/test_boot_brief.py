#!/usr/bin/env python3
"""Canario do boot-brief (ADR-101) — anti-repergunta.

POR QUE ESTE ARQUIVO EXISTE: o ADR-101 entregou `boot_brief.py` SEM canario. Quem apontou foi o
proprio gate `gate-precisa-de-canario` depois que o QA heterogeneo (2026-08-08) consertou seus
dois falsos-negativos — antes disso ele era silenciado por qualquer test_*.py tocado. Gate sem
canario e prosa executavel; este arquivo e o pagamento dessa divida.

O QUE TRAVA: o boot-brief existe para o agente parar de PERGUNTAR o que ja esta escrito. Se ele
listar nada, ou listar o projeto errado, ou despejar o CONTEUDO dos documentos no contexto, o
mecanismo falha em silencio — nenhum outro canario perceberia.
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "tools", "hooks", "boot_brief.py")

FAILS = []


def check(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def run(payload, env=None):
    r = subprocess.run([sys.executable, HOOK], input=json.dumps(payload), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=60, env=env)
    try:
        return json.loads((r.stdout or "").strip() or "{}"), r
    except ValueError:
        return {}, r


def ctx_of(payload, env=None):
    out, r = run(payload, env)
    return out.get("hookSpecificOutput", {}).get("additionalContext", ""), r


def write(path, txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)


def main():
    print("# test_boot_brief (ADR-101)")

    # --- 1. Projeto com artefatos decididos -> inventario com os caminhos.
    with tempfile.TemporaryDirectory() as d:
        write(os.path.join(d, "docs", "briefing.md"), "# Briefing\nobjetivo X\n")
        write(os.path.join(d, ".agent", "rules", "00-glossario.md"), "# Glossario\n")
        write(os.path.join(d, "docs", "adr", "001-alguma-decisao.md"), "# ADR 1\n")
        write(os.path.join(d, ".agent", "correlations.json"), "{}\n")
        ctx, _ = ctx_of({"cwd": d})
        check("docs/briefing.md" in ctx, "lista o briefing existente")
        check("00-glossario.md" in ctx, "lista o glossario existente")
        check("001-alguma-decisao.md" in ctx, "lista a ADR existente (decisao ja tomada)")
        check(".agent/correlations.json" in ctx, "lista as correlacoes declaradas")
        check("ANTES de perguntar" in ctx, "declara o proposito: nao reperguntar o que ja consta")

    # --- 2. Injeta PONTEIRO, nao CONTEUDO (ADR-029 — nao queimar contexto).
    with tempfile.TemporaryDirectory() as d:
        segredo = "CONTEUDO-INTEIRO-QUE-NAO-PODE-VAZAR-PRO-CONTEXTO"
        write(os.path.join(d, "docs", "briefing.md"), "# Briefing\n" + segredo * 200)
        ctx, _ = ctx_of({"cwd": d})
        check("docs/briefing.md" in ctx, "aponta o caminho do briefing")
        check(segredo not in ctx, "NAO despeja o conteudo do documento no contexto (so o ponteiro)")
        check(len(ctx) < 4000, f"inventario e barato ({len(ctx)} chars)")

    # --- 3. Projeto sem nada declarado -> contexto VAZIO, nunca invencao.
    with tempfile.TemporaryDirectory() as d:
        ctx, _ = ctx_of({"cwd": d})
        check(ctx == "", "projeto vazio -> additionalContext vazio (nao inventa artefato)")

    # --- 4. REGRESSAO ADR-101: audita o projeto do PAYLOAD, nunca o repo do framework.
    #     Foi o bug real de mission_gate/compaction_gate (`cwd = ROOT`): wirados globalmente,
    #     auditariam o framework enquanto o dono trabalha noutro repo — falso-OK.
    with tempfile.TemporaryDirectory() as d:
        write(os.path.join(d, "docs", "briefing.md"), "# Briefing do projeto do dono\n")
        ctx, _ = ctx_of({"cwd": d})
        check("001-ocultar-template-agente.md" not in ctx,
              "nao vaza as ADRs do repo-framework para o projeto do dono")
        check(ctx.count("briefing") >= 1, "reporta o briefing do projeto do payload")

    # --- 5. Fail-open: payload lixo nao pode crashar o boot.
    r = subprocess.run([sys.executable, HOOK], input="nao-e-json{{{", capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=60)
    check(r.returncode == 0, "payload invalido -> exit 0 (boot nunca crasha)")

    # --- 6. Diretorio inexistente no payload -> degrada sem excecao.
    out, r = run({"cwd": os.path.join(tempfile.gettempdir(), "nao-existe-mesmo-xyz-123")})
    check(r.returncode == 0, "cwd inexistente -> exit 0 (fail-open)")

    print("-" * 50)
    print(f"RESULTADO: {'PASS' if not FAILS else 'FAIL (' + str(len(FAILS)) + ')'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
