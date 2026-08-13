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
        rel = os.path.relpath(jpath, ROOT)
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


def main() -> int:
    if not os.path.isdir(QA_DIR):
        print("RESULTADO: SKIP (sem _meta/qa/ neste repo)")
        return 0
    problemas, pares, sem_par = verificar()
    print(f"integridade .json x .md: {pares} par(es) conferido(s)")
    for p in problemas:
        print(f"  DIVERGENTE {p}")
    if sem_par:
        print(f"  [debito pre-existente] {len(sem_par)} artefato(s) sem .md irmao "
              f"(gravados antes de o CLI emitir os dois; nao ha contradicao, so falta a "
              f"visao humana). NAO reprova, mas fica listado:")
        for s in sem_par:
            print(f"      - {s}")
    print("-" * 50)
    if problemas:
        print(f"RESULTADO: FAIL ({len(problemas)} divergencia(s) — regrave com "
              f"`python tools/qa_evidence.py --from-json`, NUNCA editando .json/.md a mao)")
        return 1
    print("RESULTADO: PASS (registro humano e registro-maquina contam a mesma historia)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
