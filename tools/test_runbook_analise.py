#!/usr/bin/env python3
"""Canário do runbook de análise e do pacote documental (ADR-134, B3) — `tools/runbook_analise.py`.

Prova:
  (a) o modelo gera, reabre e traz as abas e colunas do molde (literais deste arquivo) e o conteúdo mínimo por fase;
  (b) planilha marcada com os 5 Status continua passando;
  (c) uma sabotagem ou mais por regra R1 a R14, cada uma reprovada com o achado da própria regra (a do plano: Roteiro
      sem a coluna Status);
  (d) `gerar` não sobrescreve, não grava o que reprova e recusa conteúdo malformado; linha de comando com exit 0/1/2;
  (e) pacote documental com as 10 peças e a obrigatoriedade por nível; skill aponta as duas entregas.

Uso: python tools/test_runbook_analise.py   (exit 0 PASS; 1 FAIL; openpyxl ausente = SKIP, exit 0)
"""
import copy
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass
try:
    import openpyxl
except ImportError:
    print("SKIP: openpyxl ausente (tools/requirements-dev.txt)")
    sys.exit(0)
from openpyxl.formatting.formatting import ConditionalFormattingList  # noqa: E402

import runbook_analise as rb  # noqa: E402

FERRAMENTA = os.path.join(ROOT, "tools", "runbook_analise.py")
PACOTE = os.path.join(ROOT, ".agent", "skills", "analise-dados", "pacote-documental.md")
SKILL = os.path.join(ROOT, ".agent", "skills", "analise-dados", "SKILL.md")
ABAS_56 = ["Painel", "Leia antes", "Roteiro", "Copiar e colar", "Referência", "Links", "Pendências", "Decisões", "Histórico"]
COLS_C = ["Parte", "Nº", "Faça", "Onde no runbook", "Se der errado", "Status", "Data/hora",
          "Mensagem de erro ou observação", "Resposta do dono"]
CABS = {"Referência": ["Teste", "Esperado"], "Links": ["O que anotar", "Anotação"],
        "Pendências": ["ID", "O que falta", "Com quem", "Situação"],
        "Decisões": ["D-nn", "Decisão (literal)", "Data", "Alternativa descartada", "Efeito"],
        "Histórico": ["Versão/data", "O que mudou", "O que continua valendo"],
        "Runbook A": ["Passo", "Faça", "Como saber que deu certo"]}
FASES5 = ["1+2 Negócio e dados", "3 Preparação", "4 Modelagem", "5 Avaliação", "6 Implantação"]
MINIMO = {  # seção 3b da especificação: o que o modelo traz em cada fase
    FASES5[0]: ["modo", "ficha de insumo", "extrair", "perfilar", "oficial", "painel", "d-nn"],
    FASES5[1]: ["invariante", "filtro", "por script", "chave", "funil", "painel", "d-nn"],
    FASES5[2]: ["linha de base", "partição", "modelo", "painel", "d-nn"],
    FASES5[3]: ["linha de base", "viés", "robustez", "bateria", "painel", "aceite", "d-nn"],
    FASES5[4]: ["ficha de dados e de modelo", "revisão isolada", "guardar os valores", "1 item de teste", "conferir",
                "em massa", "canário", "monitoramento", "painel", "histórico"],
}
PALAVRAS = ["diário", "modo", "painel da fase", "D-nn", "ficha de insumo", "ficha de dados e de modelo", "invariante", "perfilar",
            "oficial", "cobertura", "monitoramento", "aceite", "deduplicação", "funil", "chave", "medida", "linha de base",
            "partição", "viés", "robustez", "bateria de casos", "canário", "revisão isolada"]
# peça: (N1, N2, N3)
PECAS = {"Briefing": ("se", "sim", "sim"), "Diagnóstico e proposta": ("não", "se", "sim"),
         "Análise crítica do existente": ("se", "se", "se"), "Inventário de dados": ("sim", "sim", "sim"),
         "Decisão de arquitetura": ("não", "não", "se"), "Especificação funcional (EF)": ("não", "não", "sim"),
         "Especificação técnica (ET)": ("não", "não", "sim"), "Questionário de elicitação": ("não", "se", "se"),
         "Checklist/runbook de execução": ("não", "se", "sim"),
         "Pedidos e respostas de QA por rodada": ("sim", "sim", "sim")}
ERRO = "Pare. Não repita. Copie o texto exato e avise o responsável."


def passo(parte, n, acao, meio="1) Abra a tela. 2) Salve.", onde="Runbook A, passo 1"):
    return [parte, n, f"{acao}. {meio} Deu certo: a tela confirma.", onde, ERRO]


BASE = {"titulo": "=caso fictício", "como_colar": "Cole na tela, um por linha.",
        "leia_antes": {"passos": ["a", "b", "c"], "regras": ["r1", "r2"], "palavras": {"canário": "teste curto."}},
        "roteiro": [passo(FASES5[0], "1.1", "EXTRAIR OS DADOS"), passo(FASES5[0], "1.2", "ANOTAR O TOTAL", meio="1. Anote o total.", onde="Runbook B, passo 2"),
                    passo(FASES5[4], "6.1", "GUARDAR OS VALORES"), passo(FASES5[4], "6.2", "ALTERAR 1 ITEM DE TESTE"),
                    passo(FASES5[4], "6.3", "CONFERIR O ITEM"),
                    passo(FASES5[4], "6.4", "PUBLICAR EM MASSA", meio="1) Cole a lista \"Itens\".")],
        "listas": {"Itens": ["001", "=1+1"]}, "referencia": [["t", "e"]], "links": [["l", ""]],
        "runbooks": {"Runbook A": [["faça", "ok"]], "Runbook B": [["x", "y"], ["z", "w"]]},
        "pendencias": [], "decisoes": [], "historico": [["v1", "x", "y"]]}

falhas = []


def check(nome, ok, extra=""):
    if not ok:
        falhas.append(nome)
        print(f"  FAIL {nome} {extra}")


def reabrir(wb):
    buf = io.BytesIO()
    wb.save(buf)
    return openpyxl.load_workbook(io.BytesIO(buf.getvalue()))


def base(muda=None):
    c = copy.deepcopy(BASE)
    if muda:
        muda(c)
    return reabrir(rb.montar(c))


def rodar(*args):
    r = subprocess.run([sys.executable, FERRAMENTA, *args], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


def sab(nome, regra, trecho, muda_wb=None, muda_c=None, final=False):
    """Defeito → a conferência reprova, e SÓ com achado da regra esperada."""
    wb = base(muda_c)
    if muda_wb:
        muda_wb(wb)
    a = rb.conferir_wb(reabrir(wb), final)
    check(f"{regra} {nome}", a and any(x.startswith(regra + " ") and trecho in x for x in a)
          and all(x.startswith(regra + " ") for x in a), a)


def ro(cel, valor):
    return lambda wb: wb["Roteiro"].__setitem__(cel, valor)


def faca(i, texto):
    return lambda c: c["roteiro"][i].__setitem__(2, texto)


def inverte(c):
    for i, (p, n) in enumerate(zip(c["roteiro"][4:1:-1], ("6.1", "6.2", "6.3")), 2):
        c["roteiro"][i] = [p[0], n] + p[2:]


def marca_massa(cel, situacao):
    def f(wb):
        ws = wb["Roteiro"]
        for lin in (4, 5, 6, 7):
            ws[f"F{lin}"] = "Feito"
        ws[cel], ws["H" + cel[1:]] = situacao, "motivo"
    return f


def sem_lista(wb):
    wb["Roteiro"].data_validations.dataValidation = []


def lista_tipo(wb):
    wb["Roteiro"].data_validations.dataValidation[0].type = "custom"


def formula_texto(wb):
    wb["Painel"]["B3"].data_type = "s"


def lista_curta(wb):
    wb["Roteiro"].data_validations.dataValidation[0].sqref = openpyxl.worksheet.cell_range.MultiCellRange("F2:F6")


def lista_outra(wb):
    wb["Roteiro"].data_validations.dataValidation[0].formula1 = '"Pendente,Feito,Erro,Pulado"'


def sem_cor(wb):
    ws = wb["Roteiro"]
    regras = [(str(f.sqref), r) for f in ws.conditional_formatting for r in f.rules]
    ws.conditional_formatting = ConditionalFormattingList()
    for faixa, r in regras:
        if r.formula != ['"Pulado"']:
            ws.conditional_formatting.add(faixa, r)


def cor_vazia(wb):
    for f in wb["Roteiro"].conditional_formatting:
        for r in f.rules:
            if r.formula == ['"Feito"']:
                r.dxf.fill = openpyxl.styles.PatternFill()


def cor_curta(wb):
    ws = wb["Roteiro"]
    regras = [r for f in ws.conditional_formatting for r in f.rules]
    ws.conditional_formatting = ConditionalFormattingList()
    for r in regras:
        ws.conditional_formatting.add("F2:F5" if r.formula == ['"Feito"'] else "F2:F7", r)


def atribui(aba, attr, val):
    return lambda wb: setattr(wb[aba], attr, val)


def celula(aba, cel, val):
    return lambda wb: wb[aba].__setitem__(cel, val)


def linha_leia(wb, rotulo):
    return next(r for r in wb["Leia antes"].iter_rows() if r[0].value == rotulo)


def apaga_leia(rotulo):
    def f(wb):
        linha_leia(wb, rotulo)[1].value = None
    return f


def formatar(cel, fmt):
    return lambda wb: setattr(wb["Copiar e colar"][cel], "number_format", fmt)


def modelo_e_marcada(tmp):
    destino = os.path.join(tmp, "modelo.xlsx")
    rc, saida = rodar("gerar", "--out", destino)
    check("modelo: gerar exit 0", rc == 0 and json.loads(saida)["veredito"] == "PASSA", saida)
    rc, saida = rodar("conferir", destino)
    check("modelo: conferir exit 0", rc == 0, saida)
    wb = rb.pp._abrir(destino)
    check("modelo: abas da 5.6, na ordem", [x for x in wb.sheetnames if not x.startswith("Runbook")] == ABAS_56, wb.sheetnames)
    i = wb.sheetnames.index("Links")
    check("modelo: abas de runbook entre Links e Pendências", wb.sheetnames[i + 1].startswith("Runbook")
          and wb.sheetnames[-4].startswith("Runbook"), wb.sheetnames)
    check("modelo: colunas do Roteiro", [c.value for c in wb["Roteiro"][1]] == COLS_C)
    for aba, cab in CABS.items():
        nome = aba if aba in wb.sheetnames else "Runbook Dados"
        check(f"modelo: cabeçalho de {nome}", [c.value for c in wb[nome][1]][:len(cab)] == cab)
    por_fase = {}
    for lin in wb["Roteiro"].iter_rows(min_row=2, values_only=True):
        por_fase.setdefault(lin[0], []).append(lin[2].lower())
    check("modelo: as 5 fases, na ordem", list(por_fase) == FASES5, list(por_fase))
    for fase, termos in MINIMO.items():
        texto = " ".join(por_fase.get(fase, []))
        falta = [t for t in termos if t not in texto]
        check(f"modelo: conteúdo mínimo de {fase}", not falta, falta)
    cmds = [str(c.value) for c in wb["Runbook Invariantes"]["B"]]
    for op in ("filtro", "dedup"):
        check(f"modelo: comando {op} com separador", any(f"conferir_invariante.py {op}" in x and '--sep ";"' in x for x in cmds))
    rotulos = [c.value for c in wb["Leia antes"]["A"]]
    falta = [p for p in PALAVRAS if f"Palavra: {p}" not in rotulos]
    check("modelo: termos definidos em Leia antes", not falta, falta)
    p52 = next(lin[2].value for lin in wb["Roteiro"].iter_rows(min_row=2) if lin[1].value == "5.2")
    check("modelo: 5.2 diz grupos e escolhas a preencher", "[PREENCHER: grupos]" in p52 and "escolhas mais contestáveis]" in p52, p52)
    rc, saida = rodar("conferir", destino, "--final")
    check("modelo: --final reprova as marcas por preencher", rc == 1 and "R13" in saida)
    # legítimos
    check("base passa", rb.conferir_wb(base(), final=True) == [], rb.conferir_wb(base(), final=True))
    wb = base()
    ws = wb["Roteiro"]
    for cel, s in (("F2", "Feito"), ("F3", "Pulado"), ("F4", "Feito"), ("F5", "Feito"), ("F6", "Feito"), ("F7", "Erro")):
        ws[cel] = s
    ws["H3"], ws["H7"], ws["G2"] = "não se aplica nesta base", "mensagem exata", "24/11/2026 10:00"
    wb["Pendências"].append(["P-1", "=1+1", "y", "aberta"])
    check("campos a marcar como texto", all(ws.cell(2, j).number_format == "@" for j in (6, 7, 8, 9))
          and wb["Links"]["B2"].number_format == "@")
    check("marcada passa", rb.conferir_wb(reabrir(wb), final=True) == [], rb.conferir_wb(reabrir(wb), final=True))
    wb = base()
    wb["Roteiro"]["F3"] = "Substituído"
    check("Substituído passa", rb.conferir_wb(reabrir(wb)) == [])
    wb = base()
    wb["Roteiro"]["F4"], wb["Roteiro"]["H4"] = "Erro", "mensagem exata"
    check("GUARDAR com Erro e em massa Pendente passa", rb.conferir_wb(reabrir(wb)) == [])
    check("sem lista e sem passo em massa passa",
          rb.conferir_wb(base(lambda c: (c["roteiro"].pop(), c.__setitem__("listas", {})))) == [])
    check("lista vazia não usada em massa passa", rb.conferir_wb(base(lambda c: c["listas"].__setitem__("Outra", []))) == [])
    wb = base()
    check("texto '=...' fica texto", wb["Copiar e colar"]["A5"].data_type == "s" and wb["Painel"]["B1"].data_type == "s")
    # fórmulas do Painel: literais, para a conferência não validar a si mesma
    p = wb["Painel"]
    esperado = {"B2": '=IFERROR(INDEX(Roteiro!$B$2:$B$7,MATCH(1,INDEX((Roteiro!$F$2:$F$7<>"Feito")*(Roteiro!$F$2:$F$7<>"Pulado")*(Roteiro!$F$2:$F$7<>"Substituído"),0),0)),"tudo encerrado")',
                "B3": '=COUNTIF(Roteiro!$F$2:$F$7,"Erro")',
                "B7": '=COUNTIFS(Roteiro!$A$2:$A$7,$A7,Roteiro!$F$2:$F$7,"Feito")',
                "C7": '=COUNTIFS(Roteiro!$A$2:$A$7,$A7,Roteiro!$F$2:$F$7,"Pulado")',
                "D7": '=COUNTIFS(Roteiro!$A$2:$A$7,$A7)-COUNTIFS(Roteiro!$A$2:$A$7,$A7,Roteiro!$F$2:$F$7,"Substituído")',
                "E7": "=IF(D7=0,0,(B7+C7)/D7)", "F7": '=COUNTIFS(Roteiro!$A$2:$A$7,$A7,Roteiro!$F$2:$F$7,"Erro")',
                "A6": FASES5[0], "A7": FASES5[4]}
    for cel, v in esperado.items():
        check(f"Painel {cel}", p[cel].value == v, p[cel].value)


def sabotagens():
    for aba in ABAS_56:
        sab(f"sem a aba {aba}", "R1", aba, lambda wb, x=aba: wb.remove(wb[x]))
    sab("aba fora da ordem", "R1", "ordem", lambda wb: wb.move_sheet("Links", 2))
    sab("aba estranha no meio", "R1", "Runbook", lambda wb: wb.create_sheet("Extra", 6))
    for i, col in enumerate(COLS_C, 1):
        sab(f"Roteiro sem a coluna {col}", "R2", col, lambda wb, j=i: wb["Roteiro"].delete_cols(j))
    sab("colunas trocadas", "R2", "ordem", lambda wb: (ro("F1", "Data/hora")(wb), ro("G1", "Status")(wb)))
    sab("Nº vazio", "R3", "Nº", ro("B2", None))
    sab("Nº repetido", "R3", "repetido", ro("B3", "1.1"))
    sab("Nº fora do formato", "R3", "formato", ro("B3", "b"))
    sab("linhas ordenadas dentro da fase", "R3", "ordenação", lambda wb: (ro("B2", "1.2")(wb), ro("B3", "1.1")(wb)))
    wb = base()
    wb["Roteiro"]["A2"] = FASES5[0] + " "
    check("R3 Parte com espaço a mais", any(x.startswith("R3 Parte que não é fase") for x in rb.conferir_wb(reabrir(wb))))
    wb = base()
    for lin in range(2, 8):
        for col in range(1, 10):
            wb["Roteiro"].cell(lin, col).value = None
    check("R3 sem passo", "R3 Roteiro sem passo" in rb.conferir_wb(reabrir(wb)))
    for cel, rotulo in (("A3", "Parte"), ("C3", "Faça"), ("D3", "Onde no runbook"), ("E3", "Se der errado")):
        wb = base()
        wb["Roteiro"][cel] = None
        check(f"R3 {rotulo} vazio", f"R3 linha 3: {rotulo} vazio" in rb.conferir_wb(reabrir(wb)))
    wb = base()
    wb["Roteiro"]["A2"] = "0 Outra"
    check("R3 Parte fora das fases", any(x.startswith("R3 Parte que não é fase") for x in rb.conferir_wb(reabrir(wb))))
    sab("fase não contígua", "R3", "contíguas",
        muda_c=lambda c: c["roteiro"].insert(3, passo(FASES5[0], "1.3", "VER O TOTAL")))
    sab("sem maiúsculas", "R4", "MAIÚSCULAS", muda_c=faca(0, "Extrair os dados. 1) Abra. Deu certo: ok."))
    sab("ação curta", "R4", "MAIÚSCULAS", muda_c=faca(0, "IR. 1) Abra. Deu certo: ok."))
    sab("número colado em palavra não é clique", "R4", "clique", muda_c=faca(0, "EXTRAIR OS DADOS. Abra o item1) x. Deu certo: ok."))
    sab("sem clique a clique", "R4", "clique", muda_c=faca(0, "EXTRAIR OS DADOS. Abra a tela. Deu certo: ok."))
    sab("sem 'Deu certo'", "R4", "Deu certo", muda_c=faca(0, "EXTRAIR OS DADOS. 1) Abra a tela."))
    sab("'Deu certo' vazio", "R4", "Deu certo", muda_c=faca(0, "EXTRAIR OS DADOS. 1) Abra a tela. Deu certo:"))
    sab("'Deu certo' antes do fim", "R4", "Deu certo", muda_c=faca(0, "EXTRAIR OS DADOS. 1) Abra. Deu certo: ok. 2) Salve."))
    sab("passo '2.' depois do 'Deu certo'", "R4", "Deu certo", muda_c=faca(0, "EXTRAIR OS DADOS. 1. Abra. Deu certo: ok. 2. Apague."))
    sab("'Deu certo' antes do clique", "R4", "Deu certo", muda_c=faca(0, "EXTRAIR OS DADOS. Deu certo: ok 1) Abra."))
    sab("runbook inexistente", "R5", "Runbook Z", muda_c=lambda c: c["roteiro"][0].__setitem__(3, "Runbook Z, passo 1"))
    sab("passo inexistente", "R5", "passo 9", muda_c=lambda c: c["roteiro"][0].__setitem__(3, "Runbook A, passo 9"))
    sab("onde sem formato", "R5", "não aponta", muda_c=lambda c: c["roteiro"][0].__setitem__(3, "ver o manual"))
    for tira, nome in (("Pare. ", "Pare ou Siga"), ("Não repita. ", "não repita"), ("Copie o texto exato e ", "copie o texto exato"),
                       ("avise o responsável", "avise")):
        sab(f"sem {nome}", "R6", nome, muda_c=lambda c, t=tira: c["roteiro"][0].__setitem__(4, ERRO.replace(t, "")))
    sab("sem lista de Status", "R7", "não cobre", sem_lista)
    sab("validação que não é lista", "R7", "não cobre", lista_tipo)
    sab("lista curta", "R7", "[7]", lista_curta)
    sab("lista sem Substituído", "R7", "não cobre", lista_outra)
    sab("Status fora da lista", "R7", "fora da lista", ro("F2", "Ok"))
    sab("Status com espaço a mais", "R7", "fora da lista", ro("F2", "Feito "))
    sab("Status vazio", "R7", "fora da lista", ro("F2", None))
    sab("Erro sem mensagem", "R7", "texto da mensagem", ro("F2", "Erro"))
    sab("Pulado sem motivo", "R7", "motivo", ro("F2", "Pulado"))
    sab("sem cor de um Status", "R8", "Pulado", sem_cor)
    sab("regra sem cor", "R8", "Feito", cor_vazia)
    sab("cor não cobre as linhas", "R8", "Feito", cor_curta)
    sab("sem filtro", "R8", "filtro", lambda wb: setattr(wb["Roteiro"].auto_filter, "ref", None))
    sab("filtro curto", "R8", "filtro", lambda wb: setattr(wb["Roteiro"].auto_filter, "ref", "A1:I4"))
    sab("cabeçalho solto", "R8", "congelado", atribui("Roteiro", "freeze_panes", None))
    for cel, nome in (("B2", "Onde parei"), ("B3", "Erros em aberto")):
        sab(f"{nome} digitado", "R9", nome, celula("Painel", cel, "1.1"))
    for cel, nome in (("B6", "Feitos"), ("C6", "Pulados"), ("D6", "Total"), ("E6", "%"), ("F6", "Erros")):
        sab(f"{nome} digitado", "R9", nome, celula("Painel", cel, 1))
    sab("Total sem descontar Substituído", "R9", "Total", celula("Painel", "D6", "=COUNTIFS(Roteiro!$A$2:$A$7,$A6)"))
    sab("espaço dentro do texto da fórmula", "R9", "Erros em aberto", celula("Painel", "B3", '=COUNTIF(Roteiro!$F$2:$F$7,"Er ro")'))
    sab("fórmula como texto", "R9", "Erros em aberto", formula_texto)
    sab("Painel sem uma fase", "R9", "fases", celula("Painel", "A7", None))
    sab("cabeçalho do Painel", "R9", "cabeçalho", celula("Painel", "D5", "Qtde"))
    sab("só 2 passos", "R10", "3 passos", apaga_leia("O que você vai fazer 2"))
    sab("regra sem número", "R10", "regras", apaga_leia("Regra 1"))
    sab("nenhuma regra", "R10", "regras", muda_c=lambda c: c["leia_antes"].__setitem__("regras", []))
    sab("sem palavras", "R10", "palavras", apaga_leia("Palavra: canário"))
    for k in ("Feito", "Erro", "Pulado", "Substituído", "Print", "Resposta do dono", "Filtro"):
        sab(f"como marcar {k}", "R10", k, apaga_leia(f"Como marcar: {k}"))
    sab("sem como colar", "R11", "Como colar", celula("Copiar e colar", "B1", None))
    sab("valor sem formato de texto", "R11", "texto", formatar("A4", "General"))
    sab("valor numérico", "R11", "texto", celula("Copiar e colar", "A4", 1))
    sab("dois valores na linha", "R11", "mais de um", muda_c=lambda c: c["listas"]["Itens"].__setitem__(0, "a\nb"))
    sab("fórmula na lista", "R11", "texto", celula("Copiar e colar", "A4", "=1+1"))
    for aba in CABS:
        sab(f"cabeçalho de {aba}", "R12", aba, celula(aba, "A1", "X"))
    sab("Histórico sem versão", "R12", "Histórico", lambda wb: wb["Histórico"].delete_rows(2))
    sab("marca por preencher", "R13", "PREENCHER", muda_c=lambda c: c["links"].append(["[PREENCHER: x]", ""]), final=True)
    sab("Referência vazia", "R13", "Referência", muda_c=lambda c: c.__setitem__("referencia", []), final=True)
    for i, nome in ((2, "GUARDAR"), (3, "1 ITEM DE TESTE"), (4, "CONFERIR")):
        sab(f"sem {nome}", "R14", nome, muda_c=lambda c, j=i: c["roteiro"].pop(j))
    sab("ordem invertida", "R14", "EM MASSA", muda_c=inverte)
    sab("GUARDAR duas vezes não vale o teste", "R14", "1 ITEM DE TESTE",
        muda_c=lambda c: c["roteiro"].__setitem__(3, passo(FASES5[4], "6.2", "GUARDAR DE NOVO")))
    sab("GUARDAR Substituído não conta", "R14", "GUARDAR", ro("F4", "Substituído"))
    for cel, nome in (("F4", "GUARDAR"), ("F5", "1 ITEM DE TESTE"), ("F6", "CONFERIR")):
        for s in ("Pulado", "Erro", "Pendente"):
            sab(f"em massa Feito com {nome} {s}", "R14", "(Feito)", marca_massa(cel, s))
    sab("2º passo em massa sem a sequência", "R14", "6.5",
        muda_c=lambda c: c["roteiro"].append(passo(FASES5[4], "6.5", "APAGAR EM MASSA", meio="1) Cole a lista \"Itens\".")))
    sab("lista vazia em massa", "R14", "lista preenchida", muda_c=lambda c: c["listas"].__setitem__("Itens", []))
    sab("lista inexistente", "R14", "lista preenchida",
        muda_c=lambda c: c["roteiro"][5].__setitem__(2, "PUBLICAR EM MASSA. 1) Cole a lista \"X\". Deu certo: ok."))
    sab("em massa sem citar lista", "R14", "lista preenchida", muda_c=faca(5, "PUBLICAR EM MASSA. 1) Cole tudo. Deu certo: ok."))
    wb = base()
    for x in ("Runbook A", "Runbook B"):
        wb.remove(wb[x])
    check("R1 sem aba de runbook", any(x.startswith("R1 ") and "ao menos uma" in x for x in rb.conferir_wb(reabrir(wb))))


def linha_de_comando(tmp):
    def conteudo(nome, muda=None, bruto=None):
        c = copy.deepcopy(BASE)
        if muda:
            muda(c)
        arq = os.path.join(tmp, nome)
        with open(arq, "w", encoding="utf-8") as fh:
            fh.write(bruto if bruto is not None else json.dumps(c, ensure_ascii=False))
        return arq
    ok = conteudo("ok.json")
    destino = os.path.join(tmp, "x.xlsx")
    with open(destino, "wb") as fh:
        fh.write(b"marcada")
    rc, saida = rodar("gerar", "--conteudo", ok, "--out", destino)
    with open(destino, "rb") as fh:
        check("gerar recusa destino existente, bytes intactos", rc == 2 and "já existe" in saida and fh.read() == b"marcada", saida)
    novo = os.path.join(tmp, "y.xlsx")
    rc, saida = rodar("gerar", "--conteudo", conteudo("ruim.json", faca(0, "extrair")), "--out", novo)
    check("gerar que reprova não grava", rc == 1 and "R4" in saida and not os.path.exists(novo), saida)
    ruins = {"quebrado.json": dict(bruto="{"), "lista.json": dict(bruto="[]"),
             "falta.json": dict(muda=lambda c: c.pop("roteiro")), "tipo.json": dict(muda=lambda c: c.__setitem__("listas", [])),
             "extra.json": dict(muda=lambda c: c.__setitem__("roteirro", [])),
             "curta.json": dict(muda=lambda c: c["roteiro"][0].pop()), "numero.json": dict(muda=lambda c: c["listas"]["Itens"].append(1)),
             "nulo.json": dict(muda=lambda c: c["referencia"].append(["t", None])),
             "palavra.json": dict(muda=lambda c: c["leia_antes"].__setitem__("palavras", [])),
             "controle.json": dict(muda=lambda c: c.__setitem__("titulo", "\u0001")),
             "fffe.json": dict(muda=lambda c: c.__setitem__("titulo", "\ufffe")),
             "surrogate.json": dict(bruto=json.dumps(dict(BASE, titulo="X")).replace('"X"', '"\\ud800"')),
             **{f"nome-{i}.json": dict(bruto=json.dumps(BASE).replace('"Runbook A":', f'"Runbook {x}":'))
                for i, x in enumerate(("\\ud800", "\\ufffe", "\\uffff"))},
             "fundo.json": dict(bruto="[" * 200000),
             "vazio.json": dict(muda=lambda c: c.__setitem__("roteiro", [])),
             "longo.json": dict(muda=lambda c: c.__setitem__("como_colar", "x" * 32768)),
             "aba31.json": dict(muda=lambda c: c["runbooks"].__setitem__("Runbook " + "x" * 24, [["a", "b"]])),
             "abarep.json": dict(muda=lambda c: c["runbooks"].__setitem__("Runbook a", [["a", "b"]])),
             "abanome.json": dict(muda=lambda c: c["runbooks"].__setitem__("Manual", [["a", "b"]])),
             "aba.json": dict(muda=lambda c: c["runbooks"].__setitem__("Runbook [x]", [["a", "b"]]))}
    for nome, kw in ruins.items():
        rc, saida = rodar("gerar", "--conteudo", conteudo(nome, **kw), "--out", novo)
        check(f"conteúdo {nome}: exit 2 sem gravar", rc == 2 and '"ERRO"' in saida and not os.path.exists(novo), (rc, saida))
    rc, saida = rodar("gerar", "--conteudo", ok, "--out", os.path.join(tmp, "nao", "existe.xlsx"))
    check("pasta de destino ausente: exit 2", rc == 2, saida)
    rc, saida = rodar("gerar", "--conteudo", ok, "--out", novo)
    check("gerar: exit 0 e arquivo", rc == 0 and os.path.isfile(novo), saida)
    rc, _ = rodar("conferir", novo, "--final")
    check("conferir --final: exit 0", rc == 0)
    wb = rb.pp._abrir(novo)
    wb["Roteiro"].delete_cols(6)
    semst = os.path.join(tmp, "sem-status.xlsx")
    wb.save(semst)
    rc, saida = rodar("conferir", semst)
    check("SABOTAGEM DO PLANO: Roteiro sem a coluna Status reprova", rc == 1 and "R2 Roteiro sem a coluna Status" in saida, saida)
    for nome in ("nao-existe.xlsx", "ok.json", "x.xlsx"):
        rc, saida = rodar("conferir", os.path.join(tmp, nome))
        check(f"conferir {nome}: exit 2", rc == 2 and '"ERRO"' in saida, saida)


def checar_pacote(txt, skill):
    a = []
    linhas = {}
    for ln in txt.splitlines():
        cel = [c.strip() for c in ln.strip().strip("|").split("|")]
        if ln.startswith("|") and len(cel) == 7:
            linhas[cel[0]] = cel
    if linhas.pop("Peça", [None] * 7)[1:] != ["N1", "N2", "N3", "Quando entra", "Quem produz", "Pronto quando"]:
        a.append("pacote: cabeçalho da tabela de peças")
    linhas.pop("---", None)
    if sorted(linhas) != sorted(PECAS):
        a.append(f"pacote: peças {sorted(set(linhas) ^ set(PECAS))}")
    for p, niveis in PECAS.items():
        cel = linhas.get(p, [""] * 7)
        if tuple(cel[1:4]) != niveis:
            a.append(f"pacote: {p} com níveis {cel[1:4]}, esperado {niveis}")
        if not all(cel[4:7]):
            a.append(f"pacote: {p} sem quando, quem ou pronto quando")
    for n in ("N1 ", "N2 ", "N3 "):
        if not re.search(rf"^\| {n}[^|]+\| [^|]{{20,}}\|$", txt, re.M):
            a.append(f"pacote: nível {n.strip()} sem critério de entrada")
    if "Sempre, em qualquer nível: diário da análise" not in txt or "decisões D-nn" not in txt:
        a.append("pacote: diário e D-nn obrigatórios")
    for op in ("gerar --conteudo", "conferir \""):
        if not re.search(r"na pasta do framework: `python tools/runbook_analise\.py " + op + r"[^`]*<caminho completo", txt):
            a.append(f"pacote: comando {op} sem a pasta do framework ou o caminho completo")
    if "na pasta do framework, copiar `tools/templates/runbook-analise.json`" not in txt:
        a.append("pacote: cópia do modelo sem a pasta do framework")
    s5 = skill.split("## 5. Catálogo", 1)[-1].split("\n## ", 1)[0]
    s7 = skill.split("## 7. Documentação", 1)[-1].split("\n## ", 1)[0]
    if "tools/runbook_analise.py" not in s5:
        a.append("skill: seção 5 sem tools/runbook_analise.py")
    if "pacote-documental.md" not in s7 or "prevalece sobre o resumo abaixo" not in s7:
        a.append("skill: seção 7 sem pacote-documental.md ou sem dizer que ele prevalece")
    return a


def pacote():
    with open(PACOTE, encoding="utf-8") as fh:
        txt = fh.read()
    with open(SKILL, encoding="utf-8") as fh:
        skill = fh.read()
    check("pacote e ponteiros", checar_pacote(txt, skill) == [], checar_pacote(txt, skill))
    for nome, t, s in (("sem uma peça", re.sub(r"(?m)^\| Inventário.*\n", "", txt), skill),
                       ("questionário obrigatório", txt.replace("| Questionário de elicitação | não |", "| Questionário de elicitação | sim |"), skill),
                       ("sem quem produz", txt.replace("| fase 1+2 | esta skill |", "| fase 1+2 |  |"), skill),
                       ("sem N2", txt.replace("| N2 com terceiro |", "| X |"), skill),
                       ("sem diário", txt.replace("diário da análise", "x"), skill),
                       ("skill sem a ferramenta", txt, skill.replace("tools/runbook_analise.py", "x")),
                       ("comando sem a pasta", txt.replace("na pasta do framework: `python tools/runbook_analise.py gerar", "`python tools/runbook_analise.py gerar"), skill),
                       ("conferir sem caminho completo", txt.replace("conferir \"<caminho completo>", "conferir \"<nome>"), skill),
                       ("skill sem 'prevalece'", txt, skill.replace("e prevalece sobre o resumo abaixo", "")),
                       ("skill sem o pacote", txt, skill.replace("pacote-documental.md", "x"))):
        check(f"pacote, sabotagem: {nome}", (t, s) != (txt, skill) and checar_pacote(t, s) != [])


def main():
    tmp = tempfile.mkdtemp(prefix="runbook-analise-")
    try:
        modelo_e_marcada(tmp)
        sabotagens()
        linha_de_comando(tmp)
        pacote()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"RESULTADO: {'FAIL' if falhas else 'PASS'} ({len(falhas)} falha(s))")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
