#!/usr/bin/env python3
"""Canario de INTEGRIDADE da evidencia de QA (.json x .md) — ADR-103, 3a rodada.

GAP que fecha, observado ao vivo em 13/08/2026: o autor editou
`_meta/qa/<bloco>.json` A MAO para registrar um veredito de REPROVAR e nao regravou o `.md`
irmao. Resultado: o `.md` (formato humano, o que docops e handoff tendem a citar) dizia
`aprovar_com_ressalvas` enquanto o `.json` — o que o squad_gate le — dizia `reprovar`.

O gate nao foi enganado (ele le o .json), mas a AUDITORIA foi: quem lesse o registro humano
concluiria o oposto do veredito real. E' o antipadrao "doc nao pode mentir" (ADR-044) cometido
dentro do proprio mecanismo de evidencia que existe para impedi-lo.

Regra: `.json` e `.md` de um mesmo bloco tem que CONCORDAR em veredito. A unica forma
suportada de gravar e' `python tools/qa_evidence.py --from-json` (regrava os dois juntos).
Editar qualquer um dos dois a mao e' o que este canario detecta.

Uso: python tools/test_qa_evidence_integrity.py   (exit 0 PASS; 1 se falha)
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA_DIR = os.path.join(ROOT, "_meta", "qa")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _md_campo(texto: str, rotulo: str) -> str:
    m = re.search(r"\*\*" + re.escape(rotulo) + r":?\*\*\s*(.+)", texto)
    return m.group(1).strip() if m else ""


def verificar(qa_dir: str = QA_DIR):
    """Retorna (problemas, n_pares, sem_par).

    REPROVA so CONTRADICAO — que e' o defeito que motivou este canario: os dois arquivos
    contando historias opostas sobre o mesmo veredito.

    Ausencia de `.md` irmao NAO reprova: e' divida PRE-EXISTENTE (artefatos gravados antes
    de o CLI passar a emitir os dois), e nao ha contradicao onde nao ha segundo documento.
    Ela e' LISTADA em voz alta a cada rodada — nao silenciada — para nao virar normal.
    """
    problemas, pares, sem_par = [], 0, []
    for jpath in sorted(glob.glob(os.path.join(qa_dir, "*.json"))):
        mpath = jpath[:-5] + ".md"
        try:
            rel = os.path.relpath(jpath, ROOT)
        except ValueError:
            # Drive diferente do repo: `relpath` estoura no Windows (runner da CI monta o
            # repo em D: e o tempdir em C:). O rotulo e' cosmetico — nunca pode derrubar o
            # canario. Mesma armadilha ja registrada no test_handoff.py caso (j), la com
            # `commonpath`. Pega pela matriz da CI; localmente tudo mora no mesmo drive.
            rel = jpath
        if not os.path.isfile(mpath):
            sem_par.append(rel)
            continue
        pares += 1
        try:
            v = json.load(open(jpath, encoding="utf-8"))
        except ValueError as e:
            problemas.append(f"{rel}: JSON invalido ({str(e)[:60]})")
            continue
        md = open(mpath, encoding="utf-8").read()

        rec_json = str(v.get("recomendacao", "")).strip()
        rec_md = _md_campo(md, "Recomendacao")
        if rec_json and rec_md and rec_json != rec_md:
            problemas.append(f"{rel}: recomendacao divergente — json='{rec_json}' md='{rec_md}'")

        passou_json = v.get("passou")
        passou_md = _md_campo(md, "Veredito (passou)")
        if passou_md and passou_json is not None:
            if str(passou_json) != passou_md.split()[0]:
                problemas.append(f"{rel}: 'passou' divergente — json={passou_json} md={passou_md}")
    return problemas, pares, sem_par


def autoteste():
    """Fixtures que este canario e OBRIGADO a acertar (ADR-106).

    Classe `mechanism == test`: como o repo real esta coerente, sabotar a comparacao deixava o
    canario VERDE — o gate deixava de existir sem nenhum sinal. As fixtures montam pares
    .json/.md que CONTRADIZEM um ao outro, que e' exatamente o defeito que originou o canario.
    """
    falhas = []
    with tempfile.TemporaryDirectory(prefix="qa-integridade-fx-") as td:
        def par(nome, rec_json, rec_md, passou_json, passou_md, com_md=True):
            with open(os.path.join(td, nome + ".json"), "w", encoding="utf-8") as fh:
                json.dump({"recomendacao": rec_json, "passou": passou_json}, fh)
            if com_md:
                with open(os.path.join(td, nome + ".md"), "w", encoding="utf-8") as fh:
                    fh.write(f"**Recomendacao:** {rec_md}\n\n**Veredito (passou):** {passou_md}\n")

        par("coerente", "aprovar", "aprovar", True, "True")
        problemas, pares, sem_par = verificar(td)
        if problemas:
            falhas.append(f"par COERENTE foi acusado (falso-positivo): {problemas}")
        if pares != 1:
            falhas.append(f"contagem de pares = {pares}, esperado 1")

    with tempfile.TemporaryDirectory(prefix="qa-integridade-fx2-") as td:
        par_rec = os.path.join(td, "divergente.json")
        with open(par_rec, "w", encoding="utf-8") as fh:
            json.dump({"recomendacao": "reprovar", "passou": True}, fh)
        with open(os.path.join(td, "divergente.md"), "w", encoding="utf-8") as fh:
            fh.write("**Recomendacao:** aprovar\n\n**Veredito (passou):** True\n")
        problemas, _, _ = verificar(td)
        if not any("recomendacao divergente" in p for p in problemas):
            falhas.append("recomendacao CONTRADITORIA entre .json e .md nao foi pega — "
                          "detector cego (e' o defeito que originou este canario)")

    with tempfile.TemporaryDirectory(prefix="qa-integridade-fx3-") as td:
        with open(os.path.join(td, "passou.json"), "w", encoding="utf-8") as fh:
            json.dump({"recomendacao": "aprovar", "passou": False}, fh)
        with open(os.path.join(td, "passou.md"), "w", encoding="utf-8") as fh:
            fh.write("**Recomendacao:** aprovar\n\n**Veredito (passou):** True\n")
        problemas, _, _ = verificar(td)
        if not any("'passou' divergente" in p for p in problemas):
            falhas.append("campo 'passou' CONTRADITORIO nao foi pego — um veredito pode dizer "
                          "reprovado na maquina e aprovado para o humano")

    with tempfile.TemporaryDirectory(prefix="qa-integridade-fx4-") as td:
        with open(os.path.join(td, "orfao.json"), "w", encoding="utf-8") as fh:
            json.dump({"recomendacao": "aprovar", "passou": True}, fh)
        problemas, pares, sem_par = verificar(td)
        if problemas:
            falhas.append("artefato SEM .md irmao reprovou — e' divida pre-existente, "
                          "listada e nao bloqueante por decisao registrada")
        if len(sem_par) != 1:
            falhas.append(f"artefato sem par nao foi LISTADO (sem_par={sem_par}) — "
                          f"silencia-lo o tornaria normal")
    return falhas


def main() -> int:
    if not os.path.isdir(QA_DIR):
        print("RESULTADO: SKIP (sem _meta/qa/ neste repo)")
        return 0
    problemas, pares, sem_par = verificar()
    falhas_canario = autoteste()
    print(f"integridade .json x .md: {pares} par(es) conferido(s)")
    for p in problemas:
        print(f"  DIVERGENTE {p}")
    if sem_par:
        print(f"  [debito pre-existente] {len(sem_par)} artefato(s) sem .md irmao "
              f"(gravados antes de o CLI emitir os dois; nao ha contradicao, so falta a "
              f"visao humana). NAO reprova, mas fica listado:")
        for s in sem_par:
            print(f"      - {s}")
    print(f"auto-teste do detector (6 fixtures) - {'OK' if not falhas_canario else 'FAIL'}")
    for f in falhas_canario:
        print("  -", f)
    print("-" * 50)
    if problemas or falhas_canario:
        print(f"RESULTADO: FAIL ({len(problemas)} divergencia(s), "
              f"{len(falhas_canario)} falha(s) do proprio detector - regrave com "
              f"`python tools/qa_evidence.py --from-json`, NUNCA editando .json/.md a mao)")
        return 1
    print("RESULTADO: PASS (registro humano e registro-maquina contam a mesma historia; "
          "detector provado contra fixture)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
