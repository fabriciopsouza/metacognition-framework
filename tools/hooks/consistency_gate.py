#!/usr/bin/env python3
"""consistency_gate — espelho de consistência do repo no FECHAMENTO (ADR-030, port do .ps1).

POR QUE ESTE ARQUIVO EXISTE. O mecanismo já existia em `consistency-gate.ps1` desde o ADR-030 e
**nunca foi ligado a evento nenhum** — nem hook, nem canário, nem chamada no fluxo. Medido em
2026-08-16: o `.claude/settings.json` tinha hooks em SessionStart, UserPromptSubmit, PreToolUse,
PostToolUse e PreCompact, e **nada** no encerramento. É a falha já catalogada duas vezes no
`## Aprendizado`: *"gate existe mas não disparou em 7 fechamentos"* (2026-06-02) e *"mecanismo
existe mas é hook-dependente onde o hook não roda"* (2026-06-08).

O port para Python não é cosmético: é a classe de hook comprovadamente viva nesta máquina, e
remove a dependência de PowerShell no caminho crítico do fechamento.

FAIL-SOFT POR DESENHO. Este gate **não bloqueia**. Ele é espelho: diz o que ficou pendente e
grava recibo. A LEI do fechamento continua sendo o canário de release (`test_consistency_closing`,
`test_release_checkpoint`, `qa-evidence`), pela doutrina do ADR-088/097 — canário é a camada-mestra,
hook é conveniência. Hook que bloqueia sessão vira hook que alguém desliga.

SETE DIMENSÕES. Equivalentes ao `.ps1` original — o qa-critic conferiu e achou UMA
divergência, já corrigida (o filtro de `000-*` valia só para 'Proposto', não para
duplicata de número). Onde eu escrevia 'idênticas, verificadas linha a linha', era
afirmação minha sem verificação independente. As dimensões:
  1. version-sync      README x topo do CHANGELOG
  2. adr-status        ADRs ainda em 'Proposto'
  3. checkpoint        history.md menciona a versão corrente
  4. contagens         ADR com número duplicado
  5. unpushed          commits que só existem neste PC
  6. transients        artefatos transientes esquecidos em docs/_intake/
  7. execution-report  relatório do bloco presente e não-vazio

Uso:
    python tools/hooks/consistency_gate.py             # relatório humano; exit = nº de pendências
    python tools/hooks/consistency_gate.py --json      # saída estruturada
    python tools/hooks/consistency_gate.py --hook      # modo hook Stop: NUNCA falha, grava recibo
    python tools/hooks/consistency_gate.py --repo DIR  # outra raiz (o canário usa isto)
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ_PADRAO = Path(__file__).resolve().parent.parent.parent
RECIBO = ".claude/closing-proof.json"


def _git(raiz, *args):
    try:
        r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=20)
        return (r.stdout or "").strip(), r.returncode
    except Exception:
        return "", 1


def _ler(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def auditar(raiz):
    """(pendencias, dimensoes) — sem efeito colateral; e' isto que o canario exercita."""
    raiz = Path(raiz)
    pend, dims = [], {}

    def anotar(dim, msg):
        pend.append({"dimensao": dim, "mensagem": msg})

    # 1. version-sync
    v_readme = v_clog = None
    readme = _ler(raiz / "README.md")
    if readme:
        m = re.search(r"(?im)^\s*>\s*\*\*Vers[ãa]o:\*\*\s*(\d+\.\d+\.\d+)", readme)
        v_readme = m.group(1) if m else None
    clog = _ler(raiz / "CHANGELOG.md")
    if clog:
        m = re.search(r"(?m)^\s*##\s*\[(\d+\.\d+\.\d+)\]", clog)
        v_clog = m.group(1) if m else None
    if v_readme and v_clog and v_readme != v_clog:
        anotar("version-sync", f"README ({v_readme}) != topo do CHANGELOG ({v_clog})")
    tag, _ = _git(raiz, "tag", "--sort=-v:refname")
    v_tag = tag.splitlines()[0].lstrip("v") if tag else None
    dims["version-sync"] = {"readme": v_readme, "changelog": v_clog, "tag": v_tag}

    # 2. adr-status + 4. contagens
    propostos, numeros = [], []
    adr_dir = raiz / "docs" / "adr"
    if adr_dir.is_dir():
        for f in sorted(adr_dir.glob("*.md")):
            # O `.ps1` original usa DOIS lacos com filtros diferentes, e a diferenca importa:
            # `000-*` (template) sai da lista de "Proposto", mas CONTA para duplicata de numero.
            # A 1a versao deste port fundiu os lacos e aplicou o filtro aos dois, perdendo a
            # deteccao de dois arquivos `000-*`. Achado MEDIO do qa-critic (Sonnet, 2026-08-16),
            # que tambem pegou o comentario deste arquivo afirmando "identicas ao original,
            # verificadas linha a linha" — afirmacao falsa, corrigida junto.
            m = re.match(r"^(\d{3})-", f.name)
            if m:
                numeros.append(int(m.group(1)))
            if f.name.startswith("000"):
                continue
            c = _ler(f) or ""
            if re.search(r"(?im)^\s*-?\s*\**Status:\**\s*\**Proposto", c):
                propostos.append(f.name)
    if propostos:
        anotar("adr-status", f"{len(propostos)} ADR(s) em 'Proposto': {', '.join(propostos)}")
    dims["adr-status"] = {"propostos": propostos}

    vistos, dups = set(), []
    for n in numeros:
        (dups.append(n) if n in vistos else vistos.add(n))
    if dups:
        anotar("contagens", f"ADR com numero DUPLICADO: {', '.join(map(str, dups))}")
    dims["contagens"] = {"adrs": len(numeros), "duplicados": dups}

    # 3. checkpoint
    hist = _ler(raiz / "history.md")
    alvo = v_clog or v_readme
    tem = bool(hist and alvo and alvo in hist)
    if hist is None:
        anotar("checkpoint", "history.md nao encontrado na raiz")
    elif not tem:
        anotar("checkpoint", f"history.md sem referencia a versao corrente ({alvo}) "
                             f"— checkpoint do bloco ausente?")
    dims["checkpoint"] = {"versao": alvo, "presente": tem}

    # 5. unpushed
    branch, _ = _git(raiz, "rev-parse", "--abbrev-ref", "HEAD")
    cnt, rc = _git(raiz, "rev-list", "--count", "@{upstream}..HEAD")
    ahead = None
    if rc == 0 and cnt.isdigit():
        ahead = int(cnt)
        if ahead:
            anotar("unpushed", f"{ahead} commit(s) nao-pushado(s) em '{branch}' "
                               f"— o que nao subiu nao esta protegido")
    else:
        anotar("unpushed", f"branch '{branch}' sem upstream — commits locais desprotegidos")
    dims["unpushed"] = {"branch": branch, "ahead": ahead}

    # 6. transients
    intake = raiz / "docs" / "_intake"
    transientes = sorted(p.name for p in intake.rglob("*") if p.is_file()) if intake.is_dir() else []
    if transientes:
        anotar("transients", f"{len(transientes)} artefato(s) transiente(s) em docs/_intake/: "
                             f"{', '.join(transientes)}")
    dims["transients"] = {"arquivos": transientes}

    # 7. execution-report
    alvo_rel = ("docs/_private/_intake/execution-report.md" if (raiz / "docs" / "_private").is_dir()
                else "telemetry/telemetry-report.md")
    conteudo = _ler(raiz / alvo_rel)
    ok_rep = bool(conteudo and conteudo.strip())
    if not ok_rep:
        anotar("execution-report", f"relatorio do bloco ausente/vazio ({alvo_rel}) "
                                   f"— gere com 'python tools/execution_report.py'")
    dims["execution-report"] = {"caminho": alvo_rel, "presente": ok_rep}

    # 8. quadro de gestao em dia (ADR-102). O gerador deriva backlog/cronograma/status report das
    # fontes; se elas andaram e ninguem regerou, o quadro virou ficcao. E' a dimensao que fecha o
    # pedido "atualiza sem provocacao humana": o fechamento avisa, nao o dono.
    quadro = raiz / "tools" / "projeto_docs.py"
    dims["quadro-de-gestao"] = {"em_dia": None}
    if quadro.is_file():
        try:
            r = subprocess.run([sys.executable, "-X", "utf8", str(quadro), "--verificar",
                                "--repo", str(raiz)], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=120,
                               stdin=subprocess.DEVNULL)
            dims["quadro-de-gestao"] = {"em_dia": r.returncode == 0}
            if r.returncode != 0:
                anotar("quadro-de-gestao", "backlog/cronograma/status report desatualizados "
                                           "— rode `python tools/projeto_docs.py`")
        except (OSError, subprocess.SubprocessError):
            pass

    return pend, dims


def main(argv=None):
    ap = argparse.ArgumentParser(description="Espelho de consistencia do fechamento (ADR-030).")
    ap.add_argument("--repo", default=str(RAIZ_PADRAO))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hook", action="store_true",
                    help="modo hook Stop: nunca falha, grava recibo em .claude/closing-proof.json")
    a = ap.parse_args(argv)

    raiz = Path(a.repo)
    if not raiz.is_dir():
        print(f"[consistency-gate] raiz inexistente: {raiz}", file=sys.stderr)
        return 0

    pend, dims = auditar(raiz)
    resumo = {"repo": str(raiz), "pendencias": len(pend), "consistente": not pend,
              "dimensoes": dims, "itens": pend}

    if a.hook:
        # Recibo primeiro: se a impressao falhar por encoding, a prova de que o gate rodou fica.
        try:
            alvo = raiz / RECIBO
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(json.dumps(resumo, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
        except OSError:
            pass
        if pend:
            print(f"[consistency-gate ADR-030] {len(pend)} pendencia(s) de fechamento:")
            for i in pend:
                print(f"  - [{i['dimensao']}] {i['mensagem']}")
            print("  (fail-soft: nao bloqueia. A lei do fechamento e' o canario de release.)")
        return 0  # modo hook NUNCA falha a sessao, por desenho

    if a.json:
        print(json.dumps(resumo, ensure_ascii=False, indent=2))
        return len(pend)

    print(f"==== consistency-gate (ADR-030) — {raiz} ====")
    print(f"versao: README={dims['version-sync']['readme']} | "
          f"CHANGELOG={dims['version-sync']['changelog']} | tag={dims['version-sync']['tag']}")
    print(f"ADRs: {dims['contagens']['adrs']} | Proposto: "
          f"{', '.join(dims['adr-status']['propostos']) or 'nenhum'}")
    print(f"checkpoint da versao: {'OK' if dims['checkpoint']['presente'] else 'AUSENTE'}")
    print(f"nao-pushados em '{dims['unpushed']['branch']}': {dims['unpushed']['ahead']}")
    print(f"transientes em _intake: {', '.join(dims['transients']['arquivos']) or 'nenhum'}")
    print(f"execution-report: {'OK' if dims['execution-report']['presente'] else 'AUSENTE/VAZIO'}")
    print("-" * 50)
    if not pend:
        print("RESULTADO: CONSISTENTE (0 pendencias)")
    else:
        print(f"RESULTADO: {len(pend)} pendencia(s):")
        for i in pend:
            print(f"  [{i['dimensao']}] {i['mensagem']}")
    return len(pend)


if __name__ == "__main__":
    sys.exit(main())
