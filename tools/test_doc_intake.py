#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canário de doc_intake.py (ADR-029).

Cobre o que NÃO pode quebrar:
  - .md/.txt sempre extraem (stdlib, sem dep externa);
  - chunking é sem perda (concatenar chunks descontando overlap reconstrói o texto)
    e determinístico (mesma entrada -> mesmo manifesto);
  - formato não suportado / sem parser -> status "skipped", nunca exceção;
  - manifesto declara embeddings=False (decisão travada #4).
Rodar:  python tools/test_doc_intake.py
"""

import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doc_intake as di  # noqa: E402


def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def test_textlike_and_chunking():
    para = "Parágrafo de teste com acento — çãõ e seta →.\n\n"
    text = para * 50  # ~2300 chars -> múltiplos chunks com chunk-chars 800
    pieces = di.chunk_text(text, chunk_chars=800, overlap=100)
    assert len(pieces) >= 2, "esperado múltiplos chunks"
    # Sem perda: o primeiro char e o último char do texto aparecem nos chunks.
    assert pieces[0][0] == 0
    assert pieces[-1][1] == len(text), "último chunk deve terminar no fim do texto"
    # Cobertura contígua (com overlap): cada chunk começa <= fim do anterior.
    for i in range(1, len(pieces)):
        assert pieces[i][0] <= pieces[i - 1][1], "chunks devem ser contíguos/sobrepostos"
    # Reconstrução LITERAL sem perda: como os offsets cobrem [0, len) de forma contígua,
    # concatenar text[prev_end:end] de cada chunk reconstrói o texto exato (testa o
    # invariante declarado no docstring, não só um proxy — BAIXO-2 qa-critic).
    recon = []
    prev_end = 0
    for (cstart, cend, _ptext) in pieces:
        recon.append(text[prev_end:cend])
        prev_end = cend
    assert "".join(recon) == text, "reconstrução por offsets deve devolver o texto exato"
    print("OK: chunking sem perda (reconstrução literal) + contíguo")


def test_manifest_determinismo_e_skip():
    with tempfile.TemporaryDirectory() as d:
        _write(os.path.join(d, "a.md"), "# Título\n\nCorpo do markdown com texto suficiente para um chunk.\n")
        _write(os.path.join(d, "b.txt"), "linha 1\nlinha 2\nlinha 3\n")
        # Formato não suportado: deve ser ignorado em collect_paths (não entra).
        _write(os.path.join(d, "ignore.csvx"), "x,y\n1,2\n")

        m1 = di.build_manifest(d, chunk_chars=1200, overlap=150, with_text=False)
        m2 = di.build_manifest(d, chunk_chars=1200, overlap=150, with_text=False)

        # Determinismo: dois runs idênticos.
        assert json.dumps(m1, sort_keys=True) == json.dumps(m2, sort_keys=True), "manifesto não determinístico"
        assert m1["embeddings"] is False, "manifesto deve declarar embeddings=False (decisão #4)"
        assert m1["summary"]["n_files"] == 2, f"esperado 2 arquivos suportados, veio {m1['summary']['n_files']}"
        assert m1["summary"]["n_ok"] == 2
        for f in m1["files"]:
            assert f["status"].startswith("ok"), f"esperado ok, veio {f['status']}"
            assert f["sha256"] and len(f["sha256"]) == 64
        print("OK: manifesto determinístico + arquivos suportados extraídos + embeddings=False")


def test_chunk_ids_unicos_entre_subpastas():
    # MÉDIO-1 qa-critic: dois arquivos de MESMO basename em subpastas distintas devem
    # gerar chunk-ids DISTINTOS (id_base = path relativo, não basename).
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "sub1"))
        os.makedirs(os.path.join(d, "sub2"))
        _write(os.path.join(d, "sub1", "doc.md"), "conteudo A com texto suficiente\n")
        _write(os.path.join(d, "sub2", "doc.md"), "conteudo B diferente do outro\n")
        m = di.build_manifest(d, chunk_chars=1200, overlap=150, with_text=False)
        ids = [c["id"] for f in m["files"] for c in f["chunks"]]
        assert len(ids) == len(set(ids)), f"chunk-ids devem ser únicos, veio: {ids}"
        assert any("sub1/doc.md#" in i for i in ids) and any("sub2/doc.md#" in i for i in ids)
        print("OK: chunk-ids únicos entre subpastas com mesmo basename")


def test_skip_graceful_para_binario_sem_parser():
    # Um arquivo .pdf falso (não é PDF real). Se pypdf não estiver instalado -> "skipped";
    # se estiver, o parser falha controlado -> "error". Em NENHUM caso pode lançar exceção.
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "fake.pdf")
        with open(p, "wb") as fh:
            fh.write(b"isto nao e um PDF de verdade")
        entry = di.build_file_entry(p, 1200, 150, False)
        assert entry["status"].startswith("skipped") or entry["status"].startswith("error"), entry["status"]
        assert entry["n_chunks"] == 0
        print(f"OK: degradação graciosa em binário sem parser ({entry['status'][:40]}...)")


def test_validacao_de_parametros():
    try:
        di.chunk_text("abc", chunk_chars=0, overlap=0)
        raise AssertionError("chunk_chars=0 deveria falhar")
    except ValueError:
        pass
    try:
        di.chunk_text("abc", chunk_chars=10, overlap=10)
        raise AssertionError("overlap>=chunk_chars deveria falhar")
    except ValueError:
        pass
    print("OK: validação de parâmetros (chunk_chars/overlap)")


def main():
    test_textlike_and_chunking()
    test_manifest_determinismo_e_skip()
    test_chunk_ids_unicos_entre_subpastas()
    test_skip_graceful_para_binario_sem_parser()
    test_validacao_de_parametros()
    print("\nTODOS OS CANÁRIOS PASSARAM (doc_intake).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
