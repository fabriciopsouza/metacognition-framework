#!/usr/bin/env python3
"""runbook_analise.py — runbook de execução de uma análise em xlsx, no molde da Parte C (ADR-134, bloco B3).

Gera a planilha a partir de um conteúdo em JSON (o do projeto, ou o modelo de `tools/templates/runbook-analise.json`)
e confere o molde. As regras R1 a R14 e as decisões estão em `docs/specs/analise-acompanhada/b3-spec.md`.

Alcance da conferência: planilha produzida por este gerador, antes ou depois de marcada. Não prova que o texto está
certo: nome de tela, termo explicado e "uma ação por linha" são da revisão humana (seção 3a da especificação).

Uso:
    python tools/runbook_analise.py gerar --out <novo.xlsx> [--conteudo <conteudo.json>]
    python tools/runbook_analise.py conferir <planilha.xlsx> [--final]
JSON no stdout; exit 0 passa, 1 reprova, 2 erro de uso. `gerar` nunca sobrescreve e não grava o que reprova.
"""
import argparse
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import planilhas_projeto as pp  # noqa: E402

MODELO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "runbook-analise.json")
ABAS_ANTES = ["Painel", "Leia antes", "Roteiro", "Copiar e colar", "Referência", "Links"]
ABAS_DEPOIS = ["Pendências", "Decisões", "Histórico"]
FASES = ["1+2 Negócio e dados", "3 Preparação", "4 Modelagem", "5 Avaliação", "6 Implantação"]
COLS = ["Parte", "Nº", "Faça", "Onde no runbook", "Se der errado", "Status", "Data/hora",
        "Mensagem de erro ou observação", "Resposta do dono"]
OBRIGATORIAS = ["Parte", "Nº", "Faça", "Onde no runbook", "Se der errado"]
A_MARCAR = ["Status", "Data/hora", "Mensagem de erro ou observação", "Resposta do dono"]
STATUS = {"Pendente": "FFFFFF", "Feito": "C6EFCE", "Erro": "FFC7CE", "Pulado": "D9D9D9", "Substituído": "BDD7EE"}
COLS_PAINEL = ["Fase", "Feitos", "Pulados", "Total", "%", "Erros"]
COLS_ABA = {"Referência": ["Teste", "Esperado"],
            "Links": ["O que anotar", "Anotação"],
            "Pendências": ["ID", "O que falta", "Com quem", "Situação"],
            "Decisões": ["D-nn", "Decisão (literal)", "Data", "Alternativa descartada", "Efeito"],
            "Histórico": ["Versão/data", "O que mudou", "O que continua valendo"]}
COLS_RUNBOOK = ["Passo", "Faça", "Como saber que deu certo"]
CHAVES = {"titulo": str, "leia_antes": dict, "roteiro": list, "como_colar": str, "listas": dict, "referencia": list,
          "links": list, "runbooks": dict, "pendencias": list, "decisoes": list, "historico": list}
MARCA = "[PREENCHER"
COMO_MARCAR = [
    ("Como marcar: Feito", "o \"Deu certo\" do passo aconteceu."),
    ("Como marcar: Erro", "Status Erro e o texto exato da mensagem na coluna de observação."),
    ("Como marcar: Pulado", "não se aplica; escreva o motivo na coluna de observação."),
    ("Como marcar: Substituído", "o passo não serviu; marque sem apagar a linha (o Painel desconta do total). O passo "
                                 "novo entra na próxima versão da planilha."),
    ("Como marcar: Print", "nome do arquivo S_<Nº>_<item>_<hora>.png."),
    ("Como marcar: Resposta do dono", "escreva na coluna de mesmo nome a frase literal do dono, com a data; a decisão vai também "
                                     "para a aba Decisões."),
    ("Como marcar: Filtro", "use o filtro para ver uma situação; não ordene as linhas, porque o Painel lê a ordem do Roteiro."),
]


class ErroUso(Exception):
    """Entrada que impede trabalhar: exit 2."""


# ---------------------------------------------------------------- geração
def ler_conteudo(caminho):
    try:
        with open(caminho, encoding="utf-8-sig") as fh:
            c = json.load(fh)
    except (OSError, ValueError, RecursionError) as e:
        raise ErroUso(f"conteúdo ilegível ({caminho}): {e}")
    if not isinstance(c, dict):
        raise ErroUso("conteúdo: o JSON tem de ser um objeto")
    ruins = [k for k, t in CHAVES.items() if not isinstance(c.get(k), t)] + [f"desconhecida: {k}" for k in c if k not in CHAVES]
    if ruins:
        raise ErroUso("conteúdo: chave ausente, de tipo errado ou desconhecida: " + ", ".join(ruins))
    la = c["leia_antes"]
    ok = (isinstance(la.get("passos"), list) and isinstance(la.get("regras"), list) and isinstance(la.get("palavras"), dict)
          and all(isinstance(s, list) and len(s) == len(OBRIGATORIAS) for s in c["roteiro"])
          and all(isinstance(v, list) for v in c["listas"].values())
          and all(isinstance(v, list) and all(isinstance(p, list) and len(p) == 2 for p in v) for v in c["runbooks"].values())
          and all(isinstance(x, list) and len(x) == len(COLS_ABA[aba]) for aba, k in (
              ("Referência", "referencia"), ("Links", "links"), ("Pendências", "pendencias"), ("Decisões", "decisoes"),
              ("Histórico", "historico")) for x in c[k]))
    textos = [x for k in ("passos", "regras") for x in la.get(k) or []] if ok else []
    textos += [x for k in ("roteiro", "referencia", "links", "pendencias", "decisoes", "historico") for l in c[k] for x in l] if ok else []
    textos += [x for v in c["listas"].values() for x in v] + [x for v in c["runbooks"].values() for p in v for x in p] if ok else []
    textos += list(la["palavras"].values()) if ok else []
    if not ok or any(not isinstance(x, str) for x in textos):
        raise ErroUso("conteúdo: formato das listas diferente do modelo (linhas com o número certo de textos)")
    if not c["roteiro"]:
        raise ErroUso("conteúdo: roteiro sem passo")
    textos += [c["titulo"], c["como_colar"]] + list(la["palavras"]) + list(c["listas"]) + list(c["runbooks"])
    for x in textos:  # o openpyxl recusaria o caractere com outra exceção e cortaria em silêncio o texto longo
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]", x) or len(x) > 32767:
            raise ErroUso(f"conteúdo: caractere que o xlsx não aceita ou mais de 32767 caracteres em {ascii(x[:40])}")
    nomes = [x.casefold() for x in c["runbooks"]]
    ruins = [x for x in c["runbooks"] if not re.fullmatch(r"Runbook[^\[\]:*?/\\'\x00-\x1f]{0,24}", x) or nomes.count(x.casefold()) > 1]
    if ruins:
        raise ErroUso("conteúdo: nome de aba de runbook inválido (começa por 'Runbook', até 31 caracteres, sem []:*?/\\' e sem "
                      "repetir): " + ", ".join(ruins))
    return c


def formulas_painel(n, linha):
    """Fórmulas do Painel para n passos (Roteiro!2..n+1); `linha` é a linha da fase no Painel."""
    p, nº, s = (f"Roteiro!${x}$2:${x}${n + 1}" for x in "ABF")
    conta = f'COUNTIFS({p},$A{linha},{s},'
    return {"onde": f'=IFERROR(INDEX({nº},MATCH(1,INDEX(({s}<>"Feito")*({s}<>"Pulado")*({s}<>"Substituído"),0),0)),"tudo encerrado")',
            "erros": f'=COUNTIF({s},"Erro")',
            "fase": [f'={conta}"Feito")', f'={conta}"Pulado")', f'=COUNTIFS({p},$A{linha})-{conta}"Substituído")',
                     f"=IF(D{linha}=0,0,(B{linha}+C{linha})/D{linha})", f'={conta}"Erro")']}


def montar(c):
    import openpyxl
    from openpyxl.formatting.rule import CellIsRule
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation
    wb = openpyxl.Workbook()
    n = len(c["roteiro"])
    # Painel: escrito aqui porque _aba_tabela transforma fórmula em texto
    ws = wb.active
    ws.title = "Painel"
    negrito, azul = Font(bold=True), PatternFill("solid", fgColor="1F4E78")
    f = formulas_painel(n, 0)
    for lin, (rot, val) in enumerate([("Análise", c["titulo"]), ("Onde parei", f["onde"]), ("Erros em aberto", f["erros"])], 1):
        ws.cell(lin, 1, rot).font = negrito
        ws.cell(lin, 2, val)
    ws.cell(1, 2).data_type = "s"
    for j, t in enumerate(COLS_PAINEL, 1):
        cel = ws.cell(5, j, t)
        cel.font, cel.fill = Font(bold=True, color="FFFFFF"), azul
    for lin, fase in enumerate([x for x in FASES if any(s[0] == x for s in c["roteiro"])], 6):
        ws.cell(lin, 1, fase)
        for j, v in enumerate(formulas_painel(n, lin)["fase"], 2):
            ws.cell(lin, j, v)
        ws.cell(lin, 5).number_format = "0%"
    ws.column_dimensions["A"].width = 26
    # Leia antes
    la = c["leia_antes"]
    pp._aba_texto(wb, "Leia antes",
                  [(f"O que você vai fazer {i}", t) for i, t in enumerate(la["passos"], 1)]
                  + [(f"Regra {i}", t) for i, t in enumerate(la["regras"], 1)]
                  + [(f"Palavra: {k}", v) for k, v in la["palavras"].items()] + COMO_MARCAR)
    # Roteiro
    ro = pp._aba_tabela(wb, "Roteiro", COLS, [dict(zip(OBRIGATORIAS, s), Status="Pendente") for s in c["roteiro"]], resp=A_MARCAR)
    for col, larg in zip("ABCDEFGHI", (20, 7, 80, 26, 46, 13, 16, 34, 28)):
        ro.column_dimensions[col].width = larg
    ro.auto_filter.ref = f"A1:I{n + 1}"
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUS) + '"', allow_blank=False, showErrorMessage=True)
    ro.add_data_validation(dv)
    dv.add(f"F2:F{n + 1}")
    for s, cor in STATUS.items():
        ro.conditional_formatting.add(f"F2:F{n + 1}", CellIsRule(operator="equal", formula=[f'"{s}"'],
                                                                fill=PatternFill("solid", bgColor=cor, fgColor=cor)))
    # Copiar e colar: uma coluna por lista, um valor por linha, como texto
    cc = wb.create_sheet("Copiar e colar")
    cc.cell(1, 1, "Como colar").font = negrito
    cc.cell(1, 2, c["como_colar"]).alignment = Alignment(wrap_text=True, vertical="top")
    for j, (nome, valores) in enumerate(c["listas"].items(), 1):
        cc.cell(3, j, nome).font = negrito
        for i, v in enumerate(valores, 4):
            cc.cell(i, j, v).number_format = "@"
    if not c["listas"]:
        cc.cell(3, 1, "Não se aplica")
    cc.column_dimensions["A"].width, cc.column_dimensions["B"].width = 30, 60
    # demais abas
    for aba, chave in (("Referência", "referencia"), ("Links", "links")):
        pp._aba_tabela(wb, aba, COLS_ABA[aba], [dict(zip(COLS_ABA[aba], x)) for x in c[chave]], resp=("Anotação",))
    for nome, passos in c["runbooks"].items():
        pp._aba_tabela(wb, nome, COLS_RUNBOOK,
                       [dict(zip(COLS_RUNBOOK, [str(i)] + p)) for i, p in enumerate(passos, 1)])
    for aba, chave in (("Pendências", "pendencias"), ("Decisões", "decisoes"), ("Histórico", "historico")):
        pp._aba_tabela(wb, aba, COLS_ABA[aba], [dict(zip(COLS_ABA[aba], x)) for x in c[chave]])
    for ws in wb.worksheets[4:]:
        for col in "BCDE":
            ws.column_dimensions[col].width = 60
    for ws in wb.worksheets:  # texto que começa com '=' fora do Painel não vira fórmula
        if ws.title != "Painel":
            for cel in (x for lin in ws.iter_rows() for x in lin if x.data_type == "f"):
                cel.data_type = "s"
    return wb


def gerar(conteudo, destino):
    c = ler_conteudo(conteudo)
    buf = io.BytesIO()
    montar(c).save(buf)
    import openpyxl
    achados = conferir_wb(openpyxl.load_workbook(io.BytesIO(buf.getvalue())))
    if not achados:
        try:
            with open(destino, "xb") as fh:
                fh.write(buf.getvalue())
        except FileExistsError:
            raise ErroUso(f"destino já existe: {destino}. Versão nova tem nome novo (Parte C, item 9).")
        except OSError as e:
            raise ErroUso(f"não gravou {destino}: {e}")
    return achados


# ---------------------------------------------------------------- conferência
def _t(v):
    return "" if v is None else str(v).strip()


def _cab(ws):
    cab = [_t(c.value) for c in ws[1]]
    while cab and not cab[-1]:
        cab.pop()
    return cab


def _dados(ws, cab):
    """[(nº da linha, {coluna: texto})] das linhas com algum valor. Parte e Status vêm sem tirar espaço: o Painel conta o
    texto exato da célula."""
    out = []
    for lin in ws.iter_rows(min_row=2, max_col=max(len(cab), 1)):
        v = {cab[i]: ("" if c.value is None else str(c.value)) if cab[i] in ("Parte", "Status") else _t(c.value)
             for i, c in enumerate(lin) if i < len(cab)}
        if any(x.strip() for x in v.values()):
            out.append((lin[0].row, v))
    return out


def _cobertas(faixas, coluna):
    """Linhas da coluna cobertas pelas faixas (ex.: 'F2:F20 F25')."""
    linhas = set()
    for f in str(faixas).split():
        m = re.fullmatch(r"\$?([A-Z]+)\$?(\d+)(?::\$?([A-Z]+)\$?(\d+))?", f)
        if m and (m.group(1), m.group(3) or m.group(1)) == (coluna, coluna):
            linhas |= set(range(int(m.group(2)), int(m.group(4) or m.group(2)) + 1))
    return linhas


def _titulo(faca):
    return faca.split(".", 1)[0].strip()


def listas_de(ws):
    """{nome da lista: [valores]} da aba Copiar e colar (nomes na linha 3)."""
    out = {}
    for c in ws[3] if ws.max_row >= 3 else []:
        if _t(c.value):
            out[_t(c.value)] = [x for x in (ws.cell(i, c.column) for i in range(4, ws.max_row + 1)) if _t(x.value)]
    return out


def _r1_abas(wb):
    nomes = wb.sheetnames
    a = [f"R1 falta a aba {x}" for x in ABAS_ANTES + ABAS_DEPOIS if x not in nomes]
    if a:
        return a
    meio = nomes[len(ABAS_ANTES):len(nomes) - len(ABAS_DEPOIS)]
    if nomes[:len(ABAS_ANTES)] != ABAS_ANTES or nomes[-len(ABAS_DEPOIS):] != ABAS_DEPOIS:
        a.append("R1 abas fora da ordem: " + " · ".join(nomes))
    elif not meio or any(not x.startswith("Runbook") for x in meio):
        a.append("R1 entre Links e Pendências só abas de runbook (nome começa por 'Runbook'), ao menos uma: " + repr(meio))
    return a


def _r3_passos(passos):
    a = [] if passos else ["R3 Roteiro sem passo"]
    for lin, p in passos:
        a += [f"R3 linha {lin}: {c} vazio" for c in OBRIGATORIAS if not p[c]]
    ns = [p["Nº"] for _, p in passos if p["Nº"]]
    a += [f"R3 Nº repetido: {x}" for x in sorted({x for x in ns if ns.count(x) > 1})]
    if any(not re.fullmatch(r"\d+(\.\d+)*", x) for x in ns):
        a.append("R3 Nº fora do formato 1.1")
    else:
        ordem = [[int(y) for y in x.split(".")] for x in ns]
        if ordem != sorted(ordem):
            a.append("R3 linhas fora da ordem do Nº: desfaça a ordenação (para ver uma situação, use o filtro)")
    partes = [p["Parte"] for _, p in passos if p["Parte"]]
    fora = sorted({x for x in partes if x not in FASES})
    if fora:
        a.append("R3 Parte que não é fase: " + ", ".join(fora))
    elif [FASES.index(x) for x in partes] != sorted(FASES.index(x) for x in partes):
        a.append("R3 fases fora de ordem ou não contíguas no Roteiro")
    return a


def _r4_faca(n, faca):
    t = _titulo(faca)
    corpo = faca[len(t):]
    if len(re.findall(r"[^\W\d_]", t)) < 4 or t != t.upper():
        return [f"R4 passo {n}: não começa pela AÇÃO EM MAIÚSCULAS seguida de ponto"]
    um = re.search(r"(?<!\S)1[).]\s+\S", corpo)
    fim = re.search(r"Deu certo:\s*\S", corpo)
    if not um:
        return [f"R4 passo {n}: sem o clique a clique numerado"]
    if not fim or re.search(r"(?<!\S)\d+[).]\s+\S", corpo[fim.start():]):
        return [f"R4 passo {n}: não termina em 'Deu certo: <como saber>'"]
    return []


def _r5_onde(wb, n, onde):
    m = re.fullmatch(r"(Runbook.*), passo (\S+)", onde)
    if not m or m.group(1) not in wb.sheetnames:
        return [f"R5 passo {n}: 'Onde no runbook' não aponta '<aba de runbook>, passo <n>': {onde!r}"]
    if m.group(2) not in [_t(c.value) for c in wb[m.group(1)]["A"][1:]]:
        return [f"R5 passo {n}: {m.group(1)} não tem o passo {m.group(2)}"]
    return []


def _r6_erro(n, txt):
    falta = [x for x, rx in (("Pare ou Siga", r"\b(pare|siga)\b"), ("não repita", r"não repita"),
                             ("copie o texto exato", r"copie o texto exato"), ("avise <quem>", r"\bavise\s+\S"))
             if not re.search(rx, txt, re.I)]
    return [f"R6 passo {n}: 'Se der errado' sem: " + ", ".join(falta)] if falta else []


def _r7_status(ws, passos):
    a = []
    cobre = set()
    for dv in ws.data_validations.dataValidation:
        itens = [x.strip() for x in _t(dv.formula1).strip('"').split(",")]
        if dv.type == "list" and itens == list(STATUS):
            cobre |= _cobertas(dv.sqref, "F")
    falta = [lin for lin, _ in passos if lin not in cobre]
    if falta:
        a.append(f"R7 lista de Status ({', '.join(STATUS)}) não cobre as linhas {falta}")
    for lin, p in passos:
        s, obs = p["Status"], p["Mensagem de erro ou observação"]
        if s not in STATUS:
            a.append(f"R7 linha {lin}: Status {s!r} fora da lista")
        if s == "Erro" and not obs:
            a.append(f"R7 linha {lin}: Erro sem o texto da mensagem")
        if s == "Pulado" and not obs:
            a.append(f"R7 linha {lin}: Pulado sem o motivo")
    return a


def _r8_visual(ws, passos):
    a = []
    cores = {s: set() for s in STATUS}
    for faixa in ws.conditional_formatting:
        for r in faixa.rules:
            for s in STATUS:
                if (r.type == "cellIs" and r.operator == "equal" and r.formula == [f'"{s}"'] and r.dxf and r.dxf.fill
                        and str(r.dxf.fill.bgColor.rgb)[-6:] == STATUS[s]):
                    cores[s] |= _cobertas(faixa.sqref, "F")
    for s, linhas in cores.items():
        if any(lin not in linhas for lin, _ in passos):
            a.append(f"R8 sem cor para o Status {s} em todas as linhas")
    ult = max((lin for lin, _ in passos), default=1)
    m = re.fullmatch(r"\$?A\$?1:\$?I\$?(\d+)", _t(ws.auto_filter.ref))
    if not m or int(m.group(1)) < ult:
        a.append("R8 filtro não cobre o Roteiro a partir do cabeçalho")
    if not re.fullmatch(r"[A-Z]+2", _t(ws.freeze_panes)):
        a.append("R8 cabeçalho do Roteiro não congelado")
    return a


def _r9_painel(ws, passos):
    def formula(cel):
        return _t(cel.value) if cel.data_type == "f" else None
    a = []
    n = max((lin for lin, _ in passos), default=1) - 1
    f = formulas_painel(n, 0)
    for lin, rot, esp in ((2, "Onde parei", f["onde"]), (3, "Erros em aberto", f["erros"])):
        if _t(ws.cell(lin, 1).value) != rot or formula(ws.cell(lin, 2)) != esp:
            a.append(f"R9 Painel: '{rot}' sem a fórmula do molde")
    if [_t(ws.cell(5, j).value) for j in range(1, 7)] != COLS_PAINEL:
        a.append("R9 Painel: cabeçalho diferente de " + " · ".join(COLS_PAINEL))
    fases = [x for x in FASES if any(p["Parte"] == x for _, p in passos)]
    no_painel = [_t(ws.cell(i, 1).value) for i in range(6, ws.max_row + 1) if _t(ws.cell(i, 1).value)]
    if no_painel != fases:
        a.append(f"R9 Painel: fases {no_painel} diferentes das do Roteiro {fases}")
        return a
    for lin, fase in enumerate(fases, 6):
        for j, esp in enumerate(formulas_painel(n, lin)["fase"], 2):
            if formula(ws.cell(lin, j)) != esp:
                a.append(f"R9 Painel: {fase}, coluna {COLS_PAINEL[j - 1]} sem a fórmula do molde")
    return a


def _r10_leia(ws):
    pares = [(_t(r[0].value), _t(r[1].value)) for r in ws.iter_rows(max_col=2) if _t(r[0].value)]
    rot = [k for k, v in pares if v]
    a = []
    if [k for k in rot if k.startswith("O que você vai fazer")] != [f"O que você vai fazer {i}" for i in (1, 2, 3)]:
        a.append("R10 Leia antes: 'O que você vai fazer' em 3 passos")
    regras = [k for k in rot if k.startswith("Regra")]
    if not regras or regras != [f"Regra {i}" for i in range(1, len(regras) + 1)]:
        a.append("R10 Leia antes: regras numeradas")
    if not any(re.match(r"Palavra: \S", k) for k in rot):
        a.append("R10 Leia antes: palavras usadas")
    for k, v in COMO_MARCAR:
        if dict(pares).get(k) != v:
            a.append(f"R10 Leia antes: '{k}' ausente ou diferente do molde")
    return a


def _r11_colar(wb):
    ws = wb["Copiar e colar"]
    a = []
    if _t(ws["A1"].value) != "Como colar" or not _t(ws["B1"].value):
        a.append("R11 Copiar e colar sem 'Como colar' no topo")
    for nome, celulas in listas_de(ws).items():
        a += [f"R11 lista {nome!r}, {c.coordinate}: valor não está como texto" for c in celulas
              if c.data_type != "s" or c.number_format != "@"]
        a += [f"R11 lista {nome!r}, {c.coordinate}: mais de um valor na linha" for c in celulas if "\n" in _t(c.value)]
    return a


def _r12_cabecalhos(wb):
    esperado = dict(COLS_ABA, **{x: COLS_RUNBOOK for x in wb.sheetnames if x.startswith("Runbook")})
    a = [f"R12 {aba}: cabeçalho diferente de " + " · ".join(cab) for aba, cab in esperado.items() if _cab(wb[aba]) != cab]
    if not _dados(wb["Histórico"], COLS_ABA["Histórico"]):
        a.append("R12 Histórico sem versão")
    return a


def _r13_final(wb):
    a = [f"R13 {w.title} {c.coordinate}: marca {MARCA} por preencher" for w in wb.worksheets for lin in w.iter_rows()
         for c in lin if MARCA in _t(c.value)]
    if not _dados(wb["Referência"], COLS_ABA["Referência"]):
        a.append("R13 Referência sem linha")
    return a


def _r14_massa(wb, passos):
    """Antes de cada passo em massa: GUARDAR → 1 ITEM DE TESTE → CONFERIR. Passo em massa já Feito exige os três Feitos;
    nos demais, só não conta o Substituído."""
    a = []
    listas = listas_de(wb["Copiar e colar"])
    nomes = ("GUARDAR", "1 ITEM DE TESTE", "CONFERIR")
    antes = []
    for _, p in passos:
        if p["Status"] == "Substituído":
            continue
        if "EM MASSA" not in _titulo(p["Faça"]):
            antes.append(p)
            continue
        etapa = 0
        for x in antes:
            t = _titulo(x["Faça"])
            if p["Status"] == "Feito" and x["Status"] != "Feito":
                continue
            if (etapa == 0 and t.startswith("GUARDAR")) or (etapa == 1 and "1 ITEM DE TESTE" in t) or (
                    etapa == 2 and t.startswith("CONFERIR")):
                etapa += 1
        if etapa < 3:
            a.append(f"R14 passo {p['Nº']}: EM MASSA sem {' → '.join(nomes[etapa:])} antes"
                     + (" (Feito)" if p["Status"] == "Feito" else ""))
        m = re.search(r'lista "([^"]+)"', p["Faça"])
        if not m or not listas.get(m.group(1)):
            a.append(f"R14 passo {p['Nº']}: EM MASSA sem lista preenchida na aba Copiar e colar")
        antes = []
    return a


def conferir_wb(wb, final=False):
    a = _r1_abas(wb)
    if any("falta a aba" in x for x in a):
        return a
    ws = wb["Roteiro"]
    cab = _cab(ws)
    if cab != COLS:
        faltam = [c for c in COLS if c not in cab]
        a.append("R2 Roteiro sem a coluna " + ", ".join(faltam) if faltam else "R2 Roteiro: colunas fora da ordem ou a mais")
    else:
        passos = _dados(ws, COLS)
        a += _r3_passos(passos)
        for _, p in passos:
            a += _r4_faca(p["Nº"], p["Faça"]) + _r5_onde(wb, p["Nº"], p["Onde no runbook"]) + _r6_erro(p["Nº"], p["Se der errado"])
        a += _r7_status(ws, passos) + _r8_visual(ws, passos) + _r9_painel(wb["Painel"], passos) + _r14_massa(wb, passos)
    a += _r10_leia(wb["Leia antes"]) + _r11_colar(wb) + _r12_cabecalhos(wb)
    return a + (_r13_final(wb) if final else [])


def main(argv=None):
    p = argparse.ArgumentParser(description="Runbook de análise no molde da Parte C (ADR-134).")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gerar")
    g.add_argument("--out", required=True)
    g.add_argument("--conteudo", default=MODELO)
    c = sub.add_parser("conferir")
    c.add_argument("planilha")
    c.add_argument("--final", action="store_true", help="reprova marca [PREENCHER e Referência vazia")
    a = p.parse_args(argv)
    try:
        try:
            import openpyxl  # noqa: F401
        except ImportError:
            raise ErroUso("openpyxl ausente: pip install -r tools/requirements-dev.txt")
        if a.cmd == "gerar":
            achados = gerar(a.conteudo, a.out)
        else:
            try:
                wb = pp._abrir(a.planilha)
            except Exception as e:  # arquivo ausente, não é xlsx ou xlsx corrompido
                raise ErroUso(f"não abriu {a.planilha}: {type(e).__name__}: {e}")
            achados = conferir_wb(wb, a.final)
    except ErroUso as e:
        print(json.dumps({"comando": a.cmd, "veredito": "ERRO", "erro": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"comando": a.cmd, "veredito": "REPROVA" if achados else "PASSA", "achados": achados},
                     ensure_ascii=False, indent=1))
    return 1 if achados else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
