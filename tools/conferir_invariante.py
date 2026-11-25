#!/usr/bin/env python3
"""Conferência por invariante de operação de dado (ADR-134, B2 do plano da análise acompanhada).

Confere, sobre CSV de antes e de depois, a invariante da operação declarada na seção 3 da skill
`.agent/skills/analise-dados/SKILL.md`. Só biblioteca padrão.

Operações e o que reprova:
  filtro       linhas de antes = linhas de depois + excluídas (multiconjunto de linhas inteiras, todas as colunas de
               antes; nas excluídas só a coluna de motivo pode sobrar);
               --saiu N confere o total excluído; --motivo COL conta as excluídas por motivo.
  juncao       cardinalidade declarada (lado "1" com chave única); órfãs contadas dos dois lados;
               resultado = multiconjunto das linhas que a junção (interna ou à esquerda) produziria, valor a valor.
               Coluna não-chave com o mesmo nome nos dois lados: renomear antes (exit 2).
  agregacao    soma da medida por grupo preservada entre o detalhe e o agregado (e o total); mesmos grupos dos
               dois lados; uma linha por grupo no agregado. --tolerancia T aceita |diferença| <= T (padrão 0, exato;
               use para ruído de ponto flutuante, ex.: 0.000001).
  dedup        chave única depois; removidas = duplicadas contadas antes; cada linha de depois existe antes.
  identidade   contagem igual; com --chave, cada linha comparada pela chave; sem chave, multiconjunto de linhas;
               com --grupo e --medida, soma por grupo igual. --renomear velho=novo mapeia colunas renomeadas
               (aplicado antes: --chave e --grupo usam o nome novo).

Contagem e soma iguais não provam integridade: troca de valores entre linhas preserva as duas. Por isso a
identidade compara linha a linha (chave ou multiconjunto) e a agregação compara a soma por grupo.
Limite declarado: soma por grupo não vê troca entre linhas do MESMO grupo; para isso, use --chave.

Uso:
  python tools/conferir_invariante.py filtro --antes a.csv --depois d.csv --excluidas x.csv [--motivo COL] [--saiu N]
  python tools/conferir_invariante.py juncao --esquerda l.csv --direita r.csv --resultado j.csv --chave K
         --cardinalidade 1:1|1:N|N:1 [--tipo interna|esquerda]
  python tools/conferir_invariante.py agregacao --antes det.csv --depois agg.csv --grupo G[,G2] --medida M
         [--tolerancia T]
  python tools/conferir_invariante.py dedup --antes a.csv --depois d.csv --chave K[,K2]
  python tools/conferir_invariante.py identidade --antes a.csv --depois d.csv [--chave K] [--grupo G --medida M]
         [--renomear velho=novo,...]
  Comuns: --sep ";"  --decimal virgula  --encoding utf-8-sig
Saída: JSON no stdout. Exit 0 PASSA; 1 REPROVA; 2 erro de uso ou de leitura (CSV com cabeçalho repetido ou vazio,
linha com número de campos diferente do cabeçalho, opção que não se aplica à operação, lista de colunas vazia,
medida não finita ou com |expoente ajustado| acima de 10 000, inclusive em zero; com --decimal virgula, milhar malformado:
"1.2,5", "1.23"). Com --decimal virgula, "1.234" é sempre mil duzentos e trinta e quatro.
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter
from decimal import (MAX_EMAX, MAX_PREC, MIN_EMIN, Context, Decimal, DecimalException, DivisionByZero, Inexact,
                     InvalidOperation, Overflow, localcontext)

# Soma exata: precisão máxima e Inexact como erro. O contexto padrão (28 dígitos) arredonda e gera falso PASSA
# (10^28 + 1 = 10^28) e falso REPROVA (10^28 + 1 - 10^28 = 0). Qualquer exceção aritmética vira ErroUso (exit 2).
EXATO = Context(prec=MAX_PREC, Emax=MAX_EMAX, Emin=MIN_EMIN,
                traps=[InvalidOperation, Overflow, Inexact, DivisionByZero])
# Limite declarado: |expoente ajustado| <= 10 000. A soma exata de 1e999999999 com 1 materializa um bilhão de dígitos
# e trava a máquina; nenhum dado realista chega perto. Acima do limite: exit 2, nunca resultado.
EXPOENTE_MAX = 10_000
# --decimal virgula: ponto só como separador de milhar bem formado (1.234,5); expoente opcional.
NUMERO_VIRGULA = re.compile(r"[+-]?(\d{1,3}(\.\d{3})+|\d+)?(,\d*)?([eE][+-]?\d+)?")


class ErroUso(Exception):
    pass


def ler_csv(caminho, sep, encoding):
    try:
        with open(caminho, newline="", encoding=encoding) as f:
            registros = list(csv.reader(f, delimiter=sep))
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        raise ErroUso(f"não leu {caminho}: {e}")
    if not registros:
        raise ErroUso(f"{caminho} vazio (sem cabeçalho)")
    colunas = [c.strip() for c in registros[0]]
    if any(c == "" for c in colunas):
        raise ErroUso(f"cabeçalho com coluna sem nome em {caminho}")
    repetidas = sorted(c for c, n in Counter(colunas).items() if n > 1)
    if repetidas:
        raise ErroUso(f"cabeçalho com coluna repetida em {caminho}: {', '.join(repetidas)}")
    linhas = []
    for n, reg in enumerate(registros[1:], start=2):
        if reg == []:
            continue
        if len(reg) != len(colunas):
            raise ErroUso(f"{caminho} linha {n}: {len(reg)} campo(s), cabeçalho tem {len(colunas)}")
        linhas.append(dict(zip(colunas, reg)))
    return colunas, linhas


def lista(valor):
    return [c.strip() for c in valor.split(",") if c.strip()] if valor else []


def exigir_colunas(colunas, pedidas, arquivo):
    faltam = [c for c in pedidas if c not in colunas]
    if faltam:
        raise ErroUso(f"coluna ausente em {arquivo}: {', '.join(faltam)}")


def item_colunas(nome_arquivo, colunas_antes, colunas_destino, extras_permitidas=()):
    """Toda coluna de antes tem de estar no destino; coluna a mais só a permitida (ex.: motivo nas excluídas)."""
    faltam = [c for c in colunas_antes if c not in colunas_destino]
    sobram = [c for c in colunas_destino if c not in colunas_antes and c not in extras_permitidas]
    return item(f"colunas de antes preservadas em {nome_arquivo}", not faltam and not sobram,
                f"faltam {faltam}, a mais {sobram}")


def numero(texto, decimal):
    t = (texto or "").strip()
    if t == "":
        return None
    if decimal == "virgula":
        # Palavra (NaN, Infinity) segue para Decimal, que a recusa abaixo com a própria mensagem.
        if re.search(r"\d", t) and not NUMERO_VIRGULA.fullmatch(t):
            raise ErroUso(f"valor não numérico na medida: {texto!r}")
        t = t.replace(".", "").replace(",", ".")
    try:
        v = Decimal(t)
    except InvalidOperation:
        raise ErroUso(f"valor não numérico na medida: {texto!r}")
    if not v.is_finite():
        raise ErroUso(f"valor não finito na medida: {texto!r}")
    # O zero também: 0e-999999999 somado a 5e5000 materializa um bilhão de dígitos (MemoryError).
    if abs(v.adjusted()) > EXPOENTE_MAX:
        raise ErroUso(f"valor fora do limite de expoente (|e| <= {EXPOENTE_MAX}): {texto!r}")
    return v


def soma_por_grupo(linhas, grupo, medida, decimal):
    somas, vazios = {}, 0
    for ln in linhas:
        v = numero(ln[medida], decimal)
        if v is None:
            vazios += 1
            continue
        k = tuple(ln[g] for g in grupo)
        somas[k] = somas.get(k, Decimal(0)) + v
    return somas, vazios


def tupla(ln, colunas):
    return tuple(ln.get(c) for c in colunas)


def item(nome, ok, detalhe):
    return {"nome": nome, "ok": bool(ok), "detalhe": detalhe}


def conferir_filtro(a, d, x, motivo=None, saiu=None):
    (ca, la), (cd, ld), (cx, lx) = a, d, x
    cols = ca
    antes = Counter(tupla(r, cols) for r in la)
    resto = Counter(tupla(r, cols) for r in ld) + Counter(tupla(r, cols) for r in lx)
    sobra, falta = antes - resto, resto - antes
    res = [item("funil fecha (entrou = ficou + saiu)", len(la) == len(ld) + len(lx),
                f"entrou {len(la)}, ficou {len(ld)}, saiu {len(lx)}"),
           item("linhas preservadas (multiconjunto)", not sobra and not falta,
                f"{sum(sobra.values())} linha(s) de antes sem destino; {sum(falta.values())} linha(s) sem origem"),
           item_colunas("depois", ca, cd), item_colunas("excluidas", ca, cx, (motivo,) if motivo else ())]
    if saiu is not None:
        res.append(item("excluídas = esperado", len(lx) == saiu, f"saiu {len(lx)}, esperado {saiu}"))
    if motivo:
        exigir_colunas(cx, [motivo], "excluidas")
        por = Counter(r[motivo] for r in lx)
        res.append(item("excluídas por motivo", all(k.strip() for k in por), dict(sorted(por.items()))))
    return res


def conferir_juncao(e, r, j, chave, cardinalidade, tipo="interna"):
    (ce, le), (cr, lr), (cj, lj) = e, r, j
    exigir_colunas(ce, chave, "esquerda")
    exigir_colunas(cr, chave, "direita")
    exigir_colunas(cj, chave, "resultado")
    ne, nr = Counter(tupla(x, chave) for x in le), Counter(tupla(x, chave) for x in lr)
    res = []
    if cardinalidade not in ("1:1", "1:N", "N:1"):
        raise ErroUso("cardinalidade deve ser 1:1, 1:N ou N:1")
    lado_e_um = cardinalidade in ("1:1", "1:N")
    lado_r_um = cardinalidade in ("1:1", "N:1")
    if lado_e_um:
        dup = sum(1 for v in ne.values() if v > 1)
        res.append(item("chave única na esquerda", dup == 0, f"{dup} chave(s) repetida(s)"))
    if lado_r_um:
        dup = sum(1 for v in nr.values() if v > 1)
        res.append(item("chave única na direita", dup == 0, f"{dup} chave(s) repetida(s)"))
    if tipo not in ("interna", "esquerda"):
        raise ErroUso("tipo deve ser interna ou esquerda")
    so_dir = [c for c in cr if c not in chave]
    colisao = [c for c in so_dir if c in ce]
    if colisao:
        raise ErroUso(f"coluna não-chave nos dois lados: {', '.join(colisao)}; renomeie antes de conferir")
    cols = ce + so_dir
    por_chave = {}
    for x in lr:
        por_chave.setdefault(tupla(x, chave), []).append(x)
    esperado = Counter()
    for x in le:
        pares = por_chave.get(tupla(x, chave))
        if pares:
            for y in pares:
                esperado[tupla(x, ce) + tupla(y, so_dir)] += 1
        elif tipo == "esquerda":
            esperado[tupla(x, ce) + ("",) * len(so_dir)] += 1
    obtido = Counter(tupla(x, cols) for x in lj)
    orf_e = sum(v for k, v in ne.items() if k not in nr)
    orf_r = sum(v for k, v in nr.items() if k not in ne)
    res.append(item("órfãs contadas (informativo)", True, {"esquerda": orf_e, "direita": orf_r}))
    res.append(item_colunas("resultado", cols, cj))
    res.append(item("linhas do resultado = esperado", len(lj) == sum(esperado.values()),
                    f"resultado {len(lj)}, esperado {sum(esperado.values())} (junção {tipo})"))
    res.append(item("valores do resultado = junção esperada (multiconjunto)", obtido == esperado,
                    f"{sum((esperado - obtido).values())} linha(s) esperada(s) ausente(s); "
                    f"{sum((obtido - esperado).values())} linha(s) sem origem"))
    return res


def conferir_agregacao(a, d, grupo, medida, decimal=None, tolerancia=Decimal(0), agregado=True):
    try:
        with localcontext(EXATO):
            return _conferir_agregacao(a, d, grupo, medida, decimal, tolerancia, agregado)
    except DecimalException as e:
        raise ErroUso(f"aritmética decimal fora do suportado na medida: {type(e).__name__}")


def _conferir_agregacao(a, d, grupo, medida, decimal, tolerancia, agregado):
    (ca, la), (cd, ld) = a, d
    exigir_colunas(ca, grupo + [medida], "antes")
    exigir_colunas(cd, grupo + [medida], "depois")
    sa, va = soma_por_grupo(la, grupo, medida, decimal)
    sd, _ = soma_por_grupo(ld, grupo, medida, decimal)
    dif = sorted(k for k in set(sa) | set(sd) if abs(sa.get(k, Decimal(0)) - sd.get(k, Decimal(0))) > tolerancia)
    ta, td = sum(sa.values(), Decimal(0)), sum(sd.values(), Decimal(0))
    ga, gd = Counter(tupla(x, grupo) for x in la), Counter(tupla(x, grupo) for x in ld)
    res = [item("soma total preservada", abs(ta - td) <= tolerancia,
                f"detalhe {ta}, agregado {td}, tolerância {tolerancia}; vazios no detalhe {va}"),
           item("soma por grupo preservada", not dif,
                f"{len(dif)} grupo(s) divergente(s)" + (f": {[list(k) for k in dif[:5]]}" if dif else "")),
           item("mesmos grupos", set(ga) == set(gd),
                f"{len(set(ga) - set(gd))} grupo(s) sumiram, {len(set(gd) - set(ga))} grupo(s) sem origem")]
    if agregado:
        rep_ = sum(1 for v in gd.values() if v > 1)
        res.append(item("grupo único no agregado", rep_ == 0, f"{rep_} grupo(s) com mais de uma linha"))
    return res


def conferir_dedup(a, d, chave):
    (ca, la), (cd, ld) = a, d
    exigir_colunas(ca, chave, "antes")
    exigir_colunas(cd, chave, "depois")
    na, nd = Counter(tupla(x, chave) for x in la), Counter(tupla(x, chave) for x in ld)
    duplicadas = sum(v - 1 for v in na.values())
    cols = ca
    origem = Counter(tupla(x, cols) for x in la)
    sem_origem = sum((Counter(tupla(x, cols) for x in ld) - origem).values())
    return [item("chave única depois", all(v == 1 for v in nd.values()),
                 f"{sum(1 for v in nd.values() if v > 1)} chave(s) repetida(s) depois"),
            item("removidas = duplicadas antes", len(la) - len(ld) == duplicadas,
                 f"removidas {len(la) - len(ld)}, duplicadas antes {duplicadas}"),
            item("nenhuma chave perdida", set(na) == set(nd), f"{len(set(na) - set(nd))} chave(s) sumiram"),
            item("linhas de depois existem antes", sem_origem == 0, f"{sem_origem} linha(s) sem origem"),
            item_colunas("depois", ca, cd)]


def conferir_identidade(a, d, chave=None, grupo=None, medida=None, renomear=None, decimal=None,
                        tolerancia=Decimal(0)):
    (ca, la), (cd, ld) = a, d
    mapa = renomear or {}
    la = [{mapa.get(k, k): v for k, v in x.items()} for x in la]
    ca = [mapa.get(c, c) for c in ca]
    cols = [c for c in ca if c in cd]
    res = [item("contagem igual", len(la) == len(ld), f"antes {len(la)}, depois {len(ld)}"),
           item("mesmas colunas", sorted(ca) == sorted(cd),
                f"só antes {sorted(set(ca) - set(cd))}, só depois {sorted(set(cd) - set(ca))}")]
    if chave:
        exigir_colunas(ca, chave, "antes")
        exigir_colunas(cd, chave, "depois")
        ia = {tupla(x, chave): x for x in la}
        idd = {tupla(x, chave): x for x in ld}
        if len(ia) != len(la) or len(idd) != len(ld):
            raise ErroUso("chave não é única; use a identidade sem --chave (multiconjunto)")
        difs = [k for k in set(ia) | set(idd)
                if k not in ia or k not in idd or tupla(ia[k], cols) != tupla(idd[k], cols)]
        res.append(item("linhas iguais pela chave", not difs,
                        f"{len(difs)} chave(s) com linha diferente ou ausente"
                        + (f": {[list(k) for k in sorted(difs)[:5]]}" if difs else "")))
    else:
        ma, md = Counter(tupla(x, cols) for x in la), Counter(tupla(x, cols) for x in ld)
        res.append(item("linhas iguais (multiconjunto)", ma == md,
                        f"{sum((ma - md).values())} linha(s) de antes sem par depois"))
    if medida:
        g = grupo or []
        exigir_colunas(ca, g + [medida], "antes")
        exigir_colunas(cd, g + [medida], "depois")
        res += conferir_agregacao((ca, la), (cd, ld), g, medida, decimal, tolerancia, agregado=False)
    return res


def veredito(operacao, verificacoes):
    ok = all(v["ok"] for v in verificacoes)
    return {"operacao": operacao, "veredito": "PASSA" if ok else "REPROVA", "verificacoes": verificacoes}


OPCOES_POR_OPERACAO = ("antes", "depois", "excluidas", "esquerda", "direita", "resultado", "chave", "grupo",
                       "medida", "motivo", "cardinalidade", "renomear", "tipo", "saiu", "tolerancia")
PERMITIDAS = {
    "filtro": {"antes", "depois", "excluidas", "motivo", "saiu"},
    "juncao": {"esquerda", "direita", "resultado", "chave", "cardinalidade", "tipo"},
    "agregacao": {"antes", "depois", "grupo", "medida", "tolerancia"},
    "dedup": {"antes", "depois", "chave"},
    "identidade": {"antes", "depois", "chave", "grupo", "medida", "renomear", "tolerancia"},
}


def main(argv=None):
    p = argparse.ArgumentParser(description="Conferência por invariante de operação de dado (ADR-134).")
    p.add_argument("operacao", choices=["filtro", "juncao", "agregacao", "dedup", "identidade"])
    for nome in ("antes", "depois", "excluidas", "esquerda", "direita", "resultado",
                 "chave", "grupo", "medida", "motivo", "cardinalidade", "renomear"):
        p.add_argument("--" + nome)
    p.add_argument("--tipo")
    p.add_argument("--saiu", type=int)
    p.add_argument("--tolerancia")
    p.add_argument("--sep", default=",")
    p.add_argument("--decimal", choices=["ponto", "virgula"], default="ponto")
    p.add_argument("--encoding", default="utf-8-sig")
    a = p.parse_args(argv)

    def ler(campo):
        caminho = getattr(a, campo)
        if not caminho:
            raise ErroUso(f"--{campo} é obrigatório para {a.operacao}")
        return ler_csv(caminho, a.sep, a.encoding)

    def exigir(campo):
        if not getattr(a, campo):
            raise ErroUso(f"--{campo} é obrigatório para {a.operacao}")
        return getattr(a, campo)

    def tol():
        if a.tolerancia is None:
            return Decimal(0)
        try:
            v = numero(a.tolerancia, a.decimal)
        except ErroUso:
            v = None
        if v is None or v < 0:
            raise ErroUso(f"--tolerancia inválida: {a.tolerancia!r}")
        return v

    def colunas_de(campo, obrigatorio):
        bruto = getattr(a, campo)
        if bruto is None and not obrigatorio:
            return []
        cols = lista(exigir(campo))
        if not cols:
            raise ErroUso(f"--{campo} sem nome de coluna: {bruto!r}")
        return cols

    try:
        aceitas = PERMITIDAS[a.operacao]
        indevidas = [n for n in OPCOES_POR_OPERACAO if getattr(a, n) is not None and n not in aceitas]
        if indevidas:
            raise ErroUso(f"opção que não se aplica a {a.operacao}: " + ", ".join("--" + n for n in indevidas))
        if a.operacao == "filtro":
            v = conferir_filtro(ler("antes"), ler("depois"), ler("excluidas"), a.motivo, a.saiu)
        elif a.operacao == "juncao":
            v = conferir_juncao(ler("esquerda"), ler("direita"), ler("resultado"), colunas_de("chave", True),
                                exigir("cardinalidade"), a.tipo or "interna")
        elif a.operacao == "agregacao":
            v = conferir_agregacao(ler("antes"), ler("depois"), colunas_de("grupo", True), exigir("medida"), a.decimal,
                                   tol())
        elif a.operacao == "dedup":
            v = conferir_dedup(ler("antes"), ler("depois"), colunas_de("chave", True))
        else:
            if a.grupo is not None and not a.medida:
                raise ErroUso("--grupo exige --medida na identidade")
            ren = {}
            for par in lista(a.renomear):
                if "=" not in par:
                    raise ErroUso(f"--renomear espera velho=novo: {par!r}")
                velho, novo = par.split("=", 1)
                ren[velho.strip()] = novo.strip()
            v = conferir_identidade(ler("antes"), ler("depois"), colunas_de("chave", False), colunas_de("grupo", False), a.medida, ren,
                                    a.decimal, tol())
    except ErroUso as e:
        print(json.dumps({"operacao": a.operacao, "veredito": "ERRO", "erro": str(e)}, ensure_ascii=False))
        return 2
    r = veredito(a.operacao, v)
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
    return 0 if r["veredito"] == "PASSA" else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
