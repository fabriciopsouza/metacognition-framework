#!/usr/bin/env python3
"""decisoes_que_governam — o framework deixa de ser passivo diante de um pedido (ADR-051/094).

O QUE RESOLVE. A norma diz que *"o pedido do dono não é imune a questionamento: surface-and-
reconcile com custo e consequência"*. Isso era **prosa**: dependia de o agente lembrar de ir ler
o histórico e o registro de decisões antes de executar. Caso real medido em 2026-08-16 — o dono
pediu uma funcionalidade que colidia frontalmente com uma dívida que ele próprio havia aberto três
dias antes, e a colisão só apareceu porque um crítico independente foi varrer os registros. Custou
uma rodada inteira de agente para descobrir algo que é consulta determinística.

O QUE FAZ. Dado um conjunto de caminhos (ou palavras-chave), responde: **quais decisões
registradas governam isto, e quais delas têm dívida aberta.** Sem IA, sem heurística de linguagem
— só cruzamento de registros que já existem:

  · `capabilities.json`   caminho -> capacidade -> ADR que a decidiu
  · `docs/adr/*.md`       título e status (Proposto ainda não é decisão fechada)
  · `history.md`          seção `## Em aberto` -> dívidas que citam o caminho, a capacidade ou o ADR

O QUE **NÃO** FAZ, e é deliberado. Não julga se o pedido é bom, não obriga ninguém a discordar e
não bloqueia nada. "Gate de discordância obrigatória" produz discordância-formulário — o teatro
que o ADR-035/041 existe para pegar, e o ADR-097 registra o limite: *nenhum hook força um modelo a
ser cético*. O que se mecaniza é **trazer o conflito à mesa**; decidir continua humano.

Códigos de saída: 0 nada governa · 1 governado, sem dívida aberta · 2 governado COM dívida aberta.
O 2 é o sinal de "surface-and-reconcile antes de executar".

Uso:
    python tools/decisoes_que_governam.py tools/handoff.py CHANGELOG.md
    python tools/decisoes_que_governam.py --termo "documentacao de projeto"
    python tools/decisoes_que_governam.py --mudancas-desde main     # o que esta sessao tocou
    python tools/decisoes_que_governam.py --json tools/handoff.py
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# O console do Windows abre em cp1252 e derrubava a saida ao imprimir titulo de ADR com seta.
# Ferramenta de diagnostico nao pode morrer por acento — degrada o caractere, nunca o processo.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

RAIZ = Path(__file__).resolve().parent.parent


def _ler(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _capacidades(raiz):
    d = json.loads(_ler(raiz / "capabilities.json") or "{}")
    return d.get("capabilities", []) if isinstance(d, dict) else d


def _dividas_abertas(raiz):
    """Itens da seção `## Em aberto` do history.md — um por marcador de lista de 1o nivel."""
    texto = _ler(raiz / "history.md")
    m = re.search(r"(?ms)^## Em aberto\s*\n(.*?)(?=^## |\Z)", texto)
    if not m:
        return []
    itens, atual = [], []
    for linha in m.group(1).splitlines():
        if re.match(r"^- ", linha):
            if atual:
                itens.append(" ".join(atual).strip())
            atual = [linha[2:]]
        elif not linha.strip():
            continue
        elif atual:
            # Continuacao SEM recuo tambem conta. A 1a versao so aceitava linha indentada e
            # descartava em silencio o paragrafo quebrado sem recuo, que e' markdown comum —
            # suspeita levantada pelo qa-critic (Sonnet, 2026-08-16) e fechada aqui, em vez de
            # ficar dependendo de o `history.md` manter para sempre o recuo de 2 espacos.
            atual.append(linha.strip())
    if atual:
        itens.append(" ".join(atual).strip())
    return [i for i in itens if i]


def _adr_info(raiz, ref):
    """(titulo, status) do ADR apontado por `ref`, que pode ser caminho ou numero."""
    if not ref:
        return None, None
    alvo = raiz / ref if "/" in str(ref) else None
    if alvo is None or not alvo.is_file():
        return None, None
    txt = _ler(alvo)
    titulo = next((l.lstrip("# ").strip() for l in txt.splitlines() if l.startswith("# ")), None)
    ms = re.search(r"(?im)^\s*-?\s*\**Status:\**\s*\**([A-Za-zÀ-ÿ]+)", txt)
    return titulo, (ms.group(1) if ms else None)


def _numero_adr(ref):
    m = re.search(r"/(\d{3})-", str(ref or ""))
    return m.group(1) if m else None


def governam(raiz, caminhos=(), termos=()):
    """Lista de achados. Determinístico: só cruza registros existentes."""
    raiz = Path(raiz)
    caps = _capacidades(raiz)
    dividas = _dividas_abertas(raiz)
    alvos = [str(c).replace("\\", "/") for c in caminhos]
    termos_l = [t.lower() for t in termos]
    achados = []

    for cap in caps:
        campos = [str(cap.get("mechanism") or ""), str(cap.get("test") or "")]
        casou_caminho = [a for a in alvos if any(a and (a == f or a.endswith("/" + f)
                                                        or f.endswith("/" + a) or a == f)
                                                for f in campos if f)]
        texto_cap = f"{cap.get('id','')} {cap.get('title','')}".lower()
        casou_termo = [t for t in termos_l if t and t in texto_cap]
        if not casou_caminho and not casou_termo:
            continue

        adr_ref = cap.get("adr")
        titulo, status = _adr_info(raiz, adr_ref)
        num = _numero_adr(adr_ref)
        chaves = [k for k in (cap.get("id"), num and f"ADR-{num}", num) if k]
        relacionadas = [d for d in dividas
                        if any(str(k).lower() in d.lower() for k in chaves)]

        achados.append({
            "capacidade": cap.get("id"),
            "por": ("caminho: " + ", ".join(casou_caminho)) if casou_caminho
                   else ("termo: " + ", ".join(casou_termo)),
            "adr": adr_ref,
            "adr_titulo": titulo,
            "adr_status": status,
            "enforcement": cap.get("enforcement", "(nao declarado)"),
            "dividas_abertas": relacionadas,
        })
    return achados


def _mudancas_desde(raiz, base):
    try:
        r = subprocess.run(["git", "-C", str(raiz), "diff", "--name-only", f"{base}...HEAD"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=20)
        return [l.strip() for l in (r.stdout or "").splitlines() if l.strip()]
    except Exception:
        return []


def main(argv=None):
    ap = argparse.ArgumentParser(description="Quais decisoes registradas governam isto.")
    ap.add_argument("caminhos", nargs="*")
    ap.add_argument("--termo", action="append", default=[])
    ap.add_argument("--mudancas-desde", metavar="REF",
                    help="usa os arquivos alterados desde REF (ex.: main)")
    ap.add_argument("--repo", default=str(RAIZ))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    raiz = Path(a.repo)
    caminhos = list(a.caminhos)
    if a.mudancas_desde:
        caminhos += _mudancas_desde(raiz, a.mudancas_desde)
    if not caminhos and not a.termo:
        ap.error("informe ao menos um caminho, --termo ou --mudancas-desde")

    achados = governam(raiz, caminhos, a.termo)
    com_divida = [x for x in achados if x["dividas_abertas"]]

    if a.json:
        print(json.dumps({"achados": achados, "com_divida": len(com_divida)},
                         ensure_ascii=False, indent=2))
    elif not achados:
        print("[decisoes] nada no registro governa o que foi informado.")
    else:
        print(f"[decisoes] {len(achados)} decisao(oes) registrada(s) governam isto:")
        for x in achados:
            prop = " (ainda PROPOSTO — decisao nao fechada)" if x["adr_status"] == "Proposto" else ""
            print(f"\n  · {x['capacidade']}  [{x['enforcement']}]  — casou por {x['por']}")
            if x["adr_titulo"]:
                print(f"    decidido em {x['adr']}{prop}")
                print(f"    \"{x['adr_titulo'][:110]}\"")
            for d in x["dividas_abertas"]:
                print(f"    !! DIVIDA ABERTA: {d[:220]}")
        if com_divida:
            print(f"\n  {len(com_divida)} com DIVIDA ABERTA — traga o conflito ao dono com custo "
                  f"e consequencia ANTES de executar (ADR-051). Nao e' veto: e' nao ser passivo.")

    return 2 if com_divida else (1 if achados else 0)


if __name__ == "__main__":
    sys.exit(main())
