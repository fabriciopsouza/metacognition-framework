#!/usr/bin/env python3
"""test_rotate_history.py — canario de tools/rotate_history.py (ADR-107). Standalone: exit 0 = PASS.

Prova as invariantes que tornam a rotacao SEGURA (mover != deletar):
  1. quente + arquivo = conjunto ORIGINAL de checkpoints (zero perda, zero duplicata);
  2. `## Em aberto` e `## Aprendizado` byte-a-byte intactos;
  3. sub-header `## Aprendizado (append...)` DENTRO de um checkpoint NAO quebra o bloco (trap real);
  4. idempotente — rodar 2x com o mesmo keep nao move mais nada;
  5. o checkpoint do TOPO permanece (contrato compaction_gate / ADR-007);
  6. --dry-run nao escreve.
"""
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rotate_history as rh  # noqa: E402

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


def make_history(n):
    """history sintetico: n checkpoints (mais-novo-primeiro, datas decrescentes), um deles com o
    sub-header-trap, + secoes vivas `## Em aberto` e `## Aprendizado`."""
    preamble = "# history.md\n\n> doutrina append-only.\n\n---\n\n"
    blocks = []
    for i in range(n):
        day = 28 - i  # 28,27,... datas distintas decrescentes (mais-novo-primeiro)
        b = f"## 2026-05-{day:02d} — Checkpoint C{i} (v1.{n - i}.0)\n\nCorpo do checkpoint {i}.\n\n"
        if i == 2:  # trap: sub-header com nome de secao DENTRO de um checkpoint
            b += "## Aprendizado (append desta sessao)\n\n- nota inerte do bloco.\n\n"
        b += "---\n\n"
        blocks.append(b)
    em_aberto = "## Em aberto\n\n- item WIP nao-resolvido A\n- item WIP B\n\n---\n\n"
    aprend = "## Aprendizado\n\n- licao firewall 1\n- licao firewall 2\n"
    return preamble + "".join(blocks) + em_aberto + aprend, em_aberto, aprend


def ckpt_ids(text):
    return re.findall(r"(?m)^## (\d{4}-\d{2}-\d{2} — Checkpoint C\d+).*$", text)


def run():
    n, keep = 20, 10
    with tempfile.TemporaryDirectory() as d:
        hist = os.path.join(d, "history.md")
        arch = os.path.join(d, "docs", "history", "history-archive.md")
        original, em_aberto, aprend = make_history(n)
        with open(hist, "w", encoding="utf-8") as f:
            f.write(original)
        orig_ids = ckpt_ids(original)
        check(len(orig_ids) == n, f"setup: esperava {n} checkpoints, achei {len(orig_ids)}")

        # --- dry-run nao escreve ---
        rh.rotate(hist, arch, keep, dry_run=True)
        check(open(hist, encoding="utf-8").read() == original, "dry-run NAO deveria escrever")
        check(not os.path.isfile(arch), "dry-run NAO deveria criar arquivo")

        # --- rotacao real ---
        r = rh.rotate(hist, arch, keep)
        check(r["rotated"] == n - keep, f"deveria rotacionar {n - keep}, rotacionou {r['rotated']}")
        hot = open(hist, encoding="utf-8").read()
        archived = open(arch, encoding="utf-8").read()

        hot_ids, arch_ids = ckpt_ids(hot), ckpt_ids(archived)
        # 1. conjunto preservado, sem perda, sem duplicata
        check(len(hot_ids) == keep, f"quente deveria ter {keep}, tem {len(hot_ids)}")
        check(len(arch_ids) == n - keep, f"arquivo deveria ter {n - keep}, tem {len(arch_ids)}")
        check(hot_ids + arch_ids == orig_ids, "UNIAO quente+arquivo != original (ordem/perda/dup!)")
        check(len(set(hot_ids) & set(arch_ids)) == 0, "checkpoint DUPLICADO entre quente e arquivo")

        # 2. secoes vivas intactas byte-a-byte
        check(em_aberto.strip() in hot, "## Em aberto NAO intacto no quente")
        check(aprend.strip() in hot, "## Aprendizado NAO intacto no quente")
        # 3. trap: o sub-header nao virou checkpoint (so C2 carrega o sub-header, e ele ficou no quente)
        check("## Aprendizado (append desta sessao)" in hot, "sub-header-trap deveria ficar com seu checkpoint (C2, no quente)")
        check(ckpt_ids(hot).count("2026-05-26 — Checkpoint C2") == 1, "C2 (dono do trap) deveria estar 1x no quente")
        # 5. topo preservado (compaction_gate exige >=1 e o handoff le o topo)
        check(re.search(r"(?m)^## \d{4}-\d{2}-\d{2}", hot) is not None, "quente perdeu o checkpoint do TOPO")
        check(ckpt_ids(hot)[0] == orig_ids[0], "checkpoint do TOPO mudou (deveria ser o mais novo)")

        # 4. idempotencia: 2a rodada com mesmo keep nao move nada
        before = hot
        r2 = rh.rotate(hist, arch, keep)
        check(r2["rotated"] == 0, f"2a rodada deveria rotacionar 0, rotacionou {r2['rotated']}")
        check(open(hist, encoding="utf-8").read() == before, "2a rodada NAO deveria mudar o quente (idempotencia)")

    if FAILS:
        print("FAIL test_rotate_history:")
        for m in FAILS:
            print("  - " + m)
        return 1
    print("PASS test_rotate_history: invariantes de rotacao (zero-perda, secoes-vivas, trap, idempotencia, topo) OK")
    return 0


if __name__ == "__main__":
    sys.exit(run())
