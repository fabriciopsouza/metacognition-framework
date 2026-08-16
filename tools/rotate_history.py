#!/usr/bin/env python3
"""rotate_history.py — rotacao DETERMINISTICA do history.md (ADR-107): mantem os ultimos N
checkpoints cronologicos no arquivo QUENTE + `## Em aberto` + `## Aprendizado` INTEIROS; move os
mais antigos para `docs/history/history-archive.md`. NUNCA deleta (mover != apagar; o git tambem
guarda). Mecaniza a poda do hot-file que era prosa ("Higiene v1.58.1") -> regra §0: reduz tokens do
boot (o contrato ADR-007 ja le so o checkpoint do TOPO + Em aberto + Aprendizado).

PORQUE: o history.md cresceu a ~37k tokens (55 checkpoints) e onera o contexto imediato a cada boot,
disparando o context-budget. Os consumidores programaticos (handoff.py le so o topo; compaction_gate
exige >=1 checkpoint; check_reorchestration audita o bloco recente) so precisam dos recentes -> o
resto e historia fria, melhor servida sob demanda.

INVARIANTE PROVADA pelo canario (test_rotate_history.py): quente + arquivo = conjunto original de
checkpoints (zero perda, zero duplicata); `## Em aberto` e `## Aprendizado` byte-a-byte intactos;
idempotente (rodar 2x com mesmo N = no-op); o checkpoint do topo permanece (compaction_gate).

Uso:
  python tools/rotate_history.py [--keep N] [--dry-run]
  python tools/rotate_history.py --file <path> --archive <path>   # testavel (canario)
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DEFAULT_KEEP = 10
CKPT_RE = re.compile(r"(?m)^## \d{4}-\d{2}-\d{2}")       # header de checkpoint datado
TAIL_RE = re.compile(r"(?m)^## Em aberto\b")             # inicio das secoes vivas (unico)
SENTINEL = "<!-- history-archive-pointer -->"

ARCHIVE_PREAMBLE = (
    "# history-archive.md — Arquivo FRIO de checkpoints rotacionados (ADR-107)\n\n"
    "> Checkpoints antigos movidos do `history.md` quente por `tools/rotate_history.py`.\n"
    "> Mesma ordem (mais-novo-primeiro). NADA aqui foi deletado do registro — so realocado\n"
    "> para nao onerar o boot. O `history.md` mantem os ultimos N + `## Em aberto` + `## Aprendizado`.\n\n"
    "---\n\n"
)


def split_history(text):
    """Retorna (preamble, [blocos_de_checkpoint], tail). Preamble = antes do 1o checkpoint
    (pointer antigo removido). Tail = de `## Em aberto` ao fim (vivo, intacto). Blocos splitados
    SO em `^## YYYY-MM-DD` — sub-headers tipo `## Aprendizado (append...)` dentro de um checkpoint
    NAO quebram o bloco."""
    tm = TAIL_RE.search(text)
    head = text[:tm.start()] if tm else text
    tail = text[tm.start():] if tm else ""

    starts = [m.start() for m in CKPT_RE.finditer(head)]
    if not starts:
        return head, [], tail
    preamble = head[:starts[0]]
    # remove pointer-note antigo do preamble (idempotencia)
    preamble = re.sub(
        re.escape(SENTINEL) + r".*?" + re.escape(SENTINEL) + r"\n*",
        "", preamble, flags=re.S)
    bounds = starts + [len(head)]
    blocks = [head[bounds[i]:bounds[i + 1]] for i in range(len(starts))]
    return preamble, blocks, tail


def count_ckpts(text):
    return len(CKPT_RE.findall(text))


def pointer_note(archived_total, kept_count, eol="\n"):
    # kept_count = blocos REAIS no quente (nao o --keep pedido): se keep > nº de blocos, o quente tem
    # menos; o pointer deve refletir a realidade, nao o alvo (achado MEDIO qa-critic 2026-06-20).
    return (f"{SENTINEL}{eol}"
            f"> **Poda de contexto (ADR-107):** este arquivo quente mantem os ultimos **{kept_count}** "
            f"checkpoints + `## Em aberto` + `## Aprendizado`. **{archived_total}** checkpoints mais "
            f"antigos estao em [`docs/history/history-archive.md`](docs/history/history-archive.md) "
            f"(nada deletado — so realocado). Rotacao: `python tools/rotate_history.py`.{eol}"
            f"{SENTINEL}")


def _detect_eol(text):
    # preserva o line-ending dominante do arquivo (repo Windows = CRLF); escrever LF poluiria o git
    # diff com centenas de linhas falsas (achado BAIXO qa-critic 2026-06-20).
    return "\r\n" if "\r\n" in text else "\n"


def rotate(hist_path, arch_path, keep, dry_run=False):
    # newline="" => NAO traduz EOL na leitura/escrita; preservamos exatamente o do arquivo.
    with open(hist_path, encoding="utf-8-sig", newline="") as f:
        text = f.read()
    eol = _detect_eol(text)
    g = eol * 2  # cola entre preamble/pointer/blocos
    preamble, blocks, tail = split_history(text)

    if len(blocks) <= keep:
        # nada a rotacionar; ainda assim normaliza o pointer p/ idempotencia. kept_count = REAL (len(blocks)).
        arch_total = count_ckpts(open(arch_path, encoding="utf-8-sig", newline="").read()) if os.path.isfile(arch_path) else 0
        new_hist = preamble.rstrip("\r\n") + g + pointer_note(arch_total, len(blocks), eol) + g + "".join(blocks) + tail
        changed = new_hist != text
        if changed and not dry_run:
            with open(hist_path, "w", encoding="utf-8", newline="") as f:
                f.write(new_hist)
        return {"rotated": 0, "kept": len(blocks), "archived_total": arch_total,
                "changed": changed, "msg": f"nada a rotacionar (>= {len(blocks)} <= keep={keep})"}

    kept = blocks[:keep]
    moving = blocks[keep:]

    # arquivo: prepend dos blocos rotacionados (mais novos que os ja arquivados) apos o preamble
    if os.path.isfile(arch_path):
        with open(arch_path, encoding="utf-8-sig", newline="") as f:
            arch = f.read()
        am = CKPT_RE.search(arch)
        arch_pre = arch[:am.start()] if am else (arch.rstrip("\r\n") + g)
        arch_body = arch[am.start():] if am else ""
    else:
        arch_pre, arch_body = ARCHIVE_PREAMBLE.replace("\n", eol), ""
    new_arch = arch_pre + "".join(moving) + arch_body
    arch_total = count_ckpts(new_arch)

    new_hist = preamble.rstrip("\r\n") + g + pointer_note(arch_total, len(kept), eol) + g + "".join(kept) + tail

    if not dry_run:
        os.makedirs(os.path.dirname(arch_path), exist_ok=True)
        with open(arch_path, "w", encoding="utf-8", newline="") as f:
            f.write(new_arch)
        with open(hist_path, "w", encoding="utf-8", newline="") as f:
            f.write(new_hist)
    return {"rotated": len(moving), "kept": len(kept), "archived_total": arch_total,
            "changed": True, "msg": f"rotacionados {len(moving)} -> arquivo; quente fica com {len(kept)}"}


def main(argv):
    ap = argparse.ArgumentParser(description="Rotacao deterministica do history.md (ADR-107).")
    ap.add_argument("--keep", type=int, default=DEFAULT_KEEP, help=f"checkpoints no hot file (default {DEFAULT_KEEP})")
    ap.add_argument("--file", default=os.path.join(ROOT, "history.md"))
    ap.add_argument("--archive", default=os.path.join(ROOT, "docs", "history", "history-archive.md"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv[1:])
    if not os.path.isfile(a.file):
        print(f"[rotate-history] {a.file} nao encontrado.", file=sys.stderr)
        return 1
    r = rotate(a.file, a.archive, a.keep, dry_run=a.dry_run)
    tag = "[dry-run] " if a.dry_run else ""
    print(f"{tag}[rotate-history] {r['msg']} · arquivo total={r['archived_total']} · changed={r['changed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
