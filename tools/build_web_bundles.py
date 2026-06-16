#!/usr/bin/env python3
"""build_web_bundles.py — gera os COACHES cross-IA (ADR-083) DETERMINISTICAMENTE de
web-bundles/coaches.json + nucleo do framework + phrasing-map anti-JARVIS (reusa web_export).

Cada coach vira um prompt AUTOCONTIDO web-bundles/<id>.md para colar como Gem (Gemini) /
Custom GPT (ChatGPT) / Projeto (Claude.ai). Mesmo padrao GERADO+COMMITTED+CANARIO de
CAPABILITIES.md (build_capabilities + test_capabilities): a fonte e o JSON; o .md e derivado;
o canario test_web_bundles.py barra drift (fail-closed) e prova determinismo.

Determinismo: iteracao ordenada pela ordem do JSON, sem relogio. Anti-JARVIS: o vocabulario passa
pelo web-phrasing-map.txt e um GATE final FALHA se sobrar asercao de mecanismo que o chat nao executa.

Uso: python tools/build_web_bundles.py [--check]
  (sem args: escreve web-bundles/<id>.md; --check: nao escreve, falha se drift vs committed)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import web_export  # noqa: E402  (reusa load_map/phrase/main_version/anti_jarvis_gate)

SRC = os.path.join(ROOT, "web-bundles", "coaches.json")
OUT_DIR = os.path.join(ROOT, "web-bundles")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CORE = [
    "## Nucleo do metodo (vale por LEITURA — no chat nao ha filesystem nem gate automatico)",
    "- Classifique toda afirmacao factual: **CONFIRMADO | INFERIDO | DESCONHECIDO**. Nunca invente numero, nome ou data.",
    "- File-first-por-pergunta: o que voce nao sabe, **PERGUNTE** — nao assuma.",
    "- Anti-raso: pergunte o que um **senior** NESTE campo levantaria que o leigo nao sabe pedir, e responda proativamente.",
    "- Ressalva de ambiente (anti-JARVIS): aqui o metodo vale por disciplina de leitura, **nao** por mecanismo. Efeito irreversivel/alto-impacto **sempre confirma com voce** antes de seguir.",
]


def load_coaches():
    with open(SRC, encoding="utf-8") as f:
        return json.load(f)


def render(coach, version, rules):
    L = [f"# {coach['title']} — Coach cross-IA do Framework Metacognitivo · v{version}", "",
         "> GERADO de `web-bundles/coaches.json` por `tools/build_web_bundles.py` — **nao editar a mao**.",
         "> Cole isto como instrucao de um **Gem** (Gemini), **Custom GPT** (ChatGPT) ou **Projeto** (Claude.ai).", ""]
    L += CORE + [""]
    L += ["## Papel", coach["objective"], "", f"**Artefato-alvo:** {coach['artifact']}", ""]
    L += ["## Elicitar (em LOTES tematicos — nao 1 por vez nem 50 de uma vez)"]
    L += [f"- {e}" for e in coach["elicit"]]
    L += [""]
    L += ["## Metodo"]
    L += [f"- {m}" for m in coach["method"]]
    L += [""]
    L += [f"## Saida — estrutura de **{coach['artifact']}**"]
    L += [f"{i+1}. {s}" for i, s in enumerate(coach["output_sections"])]
    L += ["", "> Cada secao traz as afirmacoes classificadas (CONFIRMADO/INFERIDO/DESCONHECIDO); "
          "**[DESCONHECIDO]** explicito onde falta dado, com como/onde validar — nunca um chute disfarcado.", ""]
    L += ["## Handoff para o IDE (metacognition-framework)",
          "Quando o artefato estiver pronto, traga-o para o **metacognition-framework** (IDE): o squad "
          "(discovery -> architect -> developer -> qa-critic) implementa. O planejamento rodou aqui (assinatura "
          "flat-rate); a implementacao roda la. Economia declarada: planejamento nao consome tokens metered do IDE.", ""]
    text = "\n".join(L) + "\n"
    return web_export.phrase(text, rules)


def build(check=False):
    rules, forbidden = web_export.load_map()
    version = web_export.main_version()
    data = load_coaches()
    coaches = data["coaches"]
    results = {}  # id -> rendered text
    for c in coaches:
        results[c["id"]] = render(c, version, rules)

    # anti-JARVIS: falha se sobrar asercao de mecanismo (mesmo gate do web_export)
    violations = []
    for cid, txt in results.items():
        for rx in forbidden:
            for m in rx.finditer(txt):
                violations.append(f"{cid}.md: '{m.group(0)[:60]}'")

    drift = []
    if check:
        for cid, txt in results.items():
            p = os.path.join(OUT_DIR, cid + ".md")
            cur = open(p, encoding="utf-8").read() if os.path.isfile(p) else None
            if cur != txt:
                drift.append(cid)
    else:
        for cid, txt in results.items():
            with open(os.path.join(OUT_DIR, cid + ".md"), "w", encoding="utf-8", newline="\n") as f:
                f.write(txt)

    return version, list(results.keys()), violations, drift


def main(argv):
    check = "--check" in argv
    version, ids, violations, drift = build(check=check)
    if violations:
        print("GATE anti-JARVIS FALHOU — asercao de mecanismo no coach:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1
    if check and drift:
        print(f"DRIFT: web-bundles/{{{','.join(drift)}}}.md != coaches.json (rode "
              f"`python tools/build_web_bundles.py` e commite)", file=sys.stderr)
        return 1
    verb = "checado (sem drift)" if check else "gerado"
    print(f"web-bundles {verb} (v{version}): {len(ids)} coaches — {', '.join(ids)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
