#!/usr/bin/env python3
"""planilhas_projeto.py — planilhas de confirmação e de verificação geradas do arquivo único (B3a-2, ADR-122).

Duas planilhas para a área responder, de qualquer projeto e sistema: as colunas são neutras e cada
projeto troca o texto do cabeçalho em `### Rótulos` da Parte I, sem mudar a ordem nem o papel da coluna.

  confirmacao_vN.xlsx  abas LEIA · REGRAS · VALORES POR CATEGORIA (esta só se declarada)
                       linhas: Parte I — Definições a confirmar (DEF-nn) + pontos para aprovação da Parte H (H-n)
  verificacao_vN.xlsx  abas COMO USAR · ANTES DE COMEÇAR · CHECKLIST · ACHADOS DO AMBIENTE · CORREÇÕES DA BASE ·
                       CONTROLE DE VERSÃO — linhas da Parte J — Roteiro de verificação (VER-nn, por `### Bloco:`),
                       15 colunas de base + as colunas de cada `### Rodada N — dd/mm/aaaa` (uma rodada no modelo;
                       para outra volta, acrescente a subseção seguinte e gere de novo)

Versão (decisão do dono, 27/09/2026): cada gravação cria vN+1; a anterior vai para `_obsoleto/`, as duas são
comparadas e a anterior só é apagada se TODA resposta da área nela estiver na nova. Divergência: a nova é
apagada, a anterior volta ao lugar e o comando reprova (rode `importar` antes). Planilha aberta no Excel
(arquivo `~$`) é recusada.

Projeto com impacto regulado: as categorias obrigatórias do perfil (`testes_obrigatorios_com_impacto`) que
faltarem como `### Bloco:` na Parte J são acrescentadas ao arquivo único pelo `gerar`; `verificar` reprova a falta.

Uso:
    python tools/planilhas_projeto.py verificar <spec.md>
    python tools/planilhas_projeto.py gerar <spec.md> --out-dir <pasta> [--so confirmacao|verificacao]
    python tools/planilhas_projeto.py importar <spec.md> --planilha <xlsx devolvido> --out-dir <pasta>
    python tools/planilhas_projeto.py situacao <spec.md> [--exigir]    # o que a área já respondeu, com nome e data
    python tools/planilhas_projeto.py rodada <spec.md> --data dd/mm/aaaa --ids VER-01,VER-03
    gerar ... --descartar "<frase do dono, dd/mm/aaaa>"   # aceita perder respostas de linhas removidas
"""
import argparse
import datetime
import hashlib
import os
import re
import shutil
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regulado  # noqa: E402
import spec_fonte  # noqa: E402

COLS_DEF = ["Definição", "Tema", "Regra, como entendemos", "Exemplo", "Como fica no sistema",
            "Exige alterar muitos registros?", "Situação hoje", "É possível? Como? Em massa?",
            "Links (fonte e tutorial)", "De onde tiramos", "Área confirma?", "Correção da área", "Nome e data"]
RESP_DEF = ["Área confirma?", "Correção da área", "Nome e data"]
COLS_VER = ["Verificação", "Onde olhar", "Item como aparece na tela", "Nome técnico", "O que o item faz",
            "Aplica-se a", "Regra / valor esperado", "Como conferir vários de uma vez",
            "Se estiver errado, o que acontece", "Criticidade", "Natureza da decisão", "Confiança",
            "Valor encontrado", "Conclusão da área", "Data / Visto"]
RESP_VER = ["Valor encontrado", "Conclusão da área", "Data / Visto"]
COLS_RODADA = ["Verificação", "Pergunta de volta", "Resposta da área", "O que fazer (valor, onde, quem)",
               "Situação", "Nome e data"]
RESP_RODADA = ["Resposta da área", "Nome e data"]
COLS_PONTO = ["#", "Ponto", "Por que importa"] + RESP_DEF
COLS_ACHADO = ["Achado", "O que foi constatado", "Por que muda a leitura", "O que fazer", "Confiança"]
COLS_CORRECAO = ["Correção", "O que constava", "Correção aplicada", "Motivo"]
COLS_VERSAO = ["Versão", "Data", "Autor", "Conteúdo", "Base utilizada"]
TIPOS = ("confirmacao", "verificacao")
_RODADA = re.compile(r"rodada\s+(\d+)\s*[—–-]\s*(\d{1,2}/\d{1,2}/\d{4})", re.I)
_VERSAO = re.compile(r"^(confirmacao|verificacao)_v(\d+)\.xlsx$")
_SEP = re.compile(r"^\|?\s*:?-{3,}")


class Recusa(Exception):
    """Operação recusada sem alterar nada (planilha aberta, versão errada, cabeçalho mudado)."""


# ---------------------------------------------------------------- leitura do arquivo único
def _celulas(ln):
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", ln.strip().strip("|"))]


def _md(v):
    """Valor de planilha → célula Markdown: quebra de linha vira <br>, '|' é escapado, e o texto literal
    '<br>' digitado pela área vira '&lt;br&gt;' para não voltar como quebra de linha."""
    return (_txt(v).replace("<br>", "&lt;br&gt;").replace("\r\n", "\n").replace("\n", "<br>")
            .replace("|", "\\|"))


def _xl(v):
    return (v or "").replace("<br>", "\n").replace("&lt;br&gt;", "<br>")


def _txt(v):
    if v is None:
        return ""
    if isinstance(v, (datetime.datetime, datetime.date)):
        return f"{v:%d/%m/%Y}"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def _norm(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(c)).casefold().strip()


def _secoes(texto):
    """[(título do ### em minúsculas ou '', [linhas])] na ordem."""
    out = [("", [])]
    for ln in (texto or "").splitlines():
        if ln.startswith("### "):
            out.append((ln[4:].strip(), []))
        else:
            out[-1][1].append(ln)
    return out


def _tabela(linhas):
    """(cabeçalho, [linhas de dados]) da primeira tabela Markdown das linhas."""
    cab, dados = None, []
    for i, ln in enumerate(linhas):
        if not ln.strip().startswith("|"):
            if cab is not None and dados:
                break
            continue
        if cab is None:
            if i + 1 < len(linhas) and _SEP.match(linhas[i + 1].strip()):
                cab = _celulas(ln)
            continue
        if _SEP.match(ln.strip()):
            continue
        dados.append(_celulas(ln))
    return cab, dados


def _campos(linhas):
    out = []
    for ln in linhas:
        m = re.match(r"^\s*[-*]?\s*\*\*([^*]+):\*\*\s*(.+?)\s*$", ln)
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def carregar(spec):
    """Tudo que os comandos usam. `achados` = estrutura que reprova."""
    ach = []
    d = {"spec": spec, "definicoes": [], "valores": None, "rotulos": {}, "leia": [], "pontos": [],
         "blocos": [], "rodadas": [], "antes": [], "achados_amb": [], "correcoes": [], "versoes": [],
         "como_usar": [], "tem_i": False, "tem_j": False}
    parte_i = spec_fonte.ler_parte(spec, "definicoes")
    if parte_i is not None:
        d["tem_i"] = True
        for titulo, linhas in _secoes(parte_i):
            t = _norm(titulo)
            cab, dados = _tabela(linhas)
            if t == "":
                d["leia"] = _campos(linhas)
                d["definicoes"] = _linhas_id(cab, dados, COLS_DEF, "DEF", "Parte I", ach)
            elif t == "valores por categoria" and cab:
                if len(cab) < 7 or cab[:2] != ["Item", "Nome técnico"] or cab[-4:] != ["Regra"] + RESP_DEF:
                    ach.append("Valores por categoria: o cabeçalho tem de ser | Item | Nome técnico | <categorias> | "
                               "Regra | Área confirma? | Correção da área | Nome e data |")
                else:
                    d["valores"] = (cab, [r for r in dados if len(r) == len(cab) and not _vazio(r[0])])
                    for r in dados:
                        if len(r) != len(cab):
                            ach.append(f"Valores por categoria: '{r[0]}' com {len(r)} colunas, o cabeçalho tem {len(cab)}")
            elif t == "rotulos" and cab:
                todas = set(COLS_DEF + COLS_VER + COLS_RODADA)
                for r in dados:
                    if len(r) >= 2 and r[0] and not _vazio(r[1]):
                        if r[0] not in todas:
                            ach.append(f"Rótulos: coluna '{r[0]}' não existe no modelo")
                        else:
                            d["rotulos"][r[0]] = r[1]
    try:
        processo = spec_fonte.ler_parte(spec, "processo")
    except OSError:
        processo = None
    for titulo, linhas in _secoes(processo or ""):
        if _norm(titulo) == "pontos para aprovacao":
            cab, dados = _tabela(linhas)
            for r in dados:
                if r and re.fullmatch(r"\d+", r[0]) and len(r) >= 3 and not _vazio(r[1]):
                    d["pontos"].append(dict(zip(COLS_PONTO, r + [""] * (len(COLS_PONTO) - len(r)))))
    parte_j = spec_fonte.ler_parte(spec, "verificacao")
    if parte_j is not None:
        d["tem_j"] = True
        vistos = set()
        for titulo, linhas in _secoes(parte_j):
            t = _norm(titulo)
            cab, dados = _tabela(linhas)
            if t == "":
                d["como_usar"] = _campos(linhas)
            elif t.startswith("bloco:"):
                rows = _linhas_id(cab, dados, COLS_VER, "VER", f"Bloco '{titulo[6:].strip()}'", ach)
                for r in rows:
                    if r["Verificação"] in vistos:
                        ach.append(f"{r['Verificação']} repetida")
                    vistos.add(r["Verificação"])
                d["blocos"].append((titulo[6:].strip(), rows))
            elif t.startswith("rodada"):
                m = _RODADA.match(titulo)
                if not m:
                    ach.append(f"'### {titulo}': use '### Rodada N — dd/mm/aaaa'")
                    continue
                rows = _linhas_id(cab, dados, COLS_RODADA, "VER", f"Rodada {m.group(1)}", ach)
                d["rodadas"].append((int(m.group(1)), m.group(2), {r["Verificação"]: r for r in rows}))
            elif t == "antes de comecar":
                d["antes"] = [re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", ln).strip() for ln in linhas if ln.strip()
                              and not ln.strip().startswith(">")]
            elif t == "achados do ambiente":
                d["achados_amb"] = _linhas_livres(cab, dados, COLS_ACHADO, "Achados do ambiente", ach)
            elif t == "correcoes da base":
                d["correcoes"] = _linhas_livres(cab, dados, COLS_CORRECAO, "Correções da base", ach)
            elif t == "controle de versao":
                d["versoes"] = _linhas_livres(cab, dados, COLS_VERSAO, "Controle de versão", ach)
        nums = [n for n, _, _ in d["rodadas"]]
        if nums != list(range(1, len(nums) + 1)):
            ach.append(f"rodadas fora de sequência: {nums} (esperado 1, 2, 3...)")
        for n, _, rows in d["rodadas"]:
            for vid in rows:
                if vid not in vistos:
                    ach.append(f"Rodada {n}: {vid} não existe em nenhum bloco")
    d["achados"] = ach + _categorias_faltantes(d, apenas_achado=True)
    return d


def _vazio(v):
    v = (v or "").strip()
    return v.lower() in {"", "—", "-"} or bool(re.fullmatch(r"<[^>]*>", v))


def _linhas_id(cab, dados, cols, prefixo, onde, ach):
    if cab is None:
        return []
    if cab != cols:
        ach.append(f"{onde}: cabeçalho difere do modelo — esperado | {' | '.join(cols)} |")
        return []
    out = []
    for r in dados:
        if not re.fullmatch(rf"{prefixo}-\d+", r[0]):
            continue
        if len(r) != len(cols):
            ach.append(f"{onde}: {r[0]} com {len(r)} colunas, o modelo tem {len(cols)}")
            continue
        out.append(dict(zip(cols, r)))
    ids = [r[cols[0]] for r in out]
    for x in sorted({i for i in ids if ids.count(i) > 1}):
        ach.append(f"{onde}: {x} repetida")
    return out


def _linhas_livres(cab, dados, cols, onde, ach):
    if cab is None:
        return []
    if cab != cols:
        ach.append(f"{onde}: cabeçalho difere do modelo — esperado | {' | '.join(cols)} |")
        return []
    return [dict(zip(cols, r)) for r in dados if len(r) == len(cols) and not _vazio(r[0])]


def _obrigatorias(spec):
    """Categorias obrigatórias do perfil, quando o projeto declara impacto regulado."""
    try:
        reg = regulado.carregar(spec)
    except OSError:
        return []
    if reg["impacto"] != "sim" or not reg["perfil"]:
        return []
    return list(reg["perfil"].get("testes_obrigatorios_com_impacto", []))


def _categorias_faltantes(d, apenas_achado=False):
    blocos = {_norm(n) for n, _ in d["blocos"]}
    falta = [c for c in _obrigatorias(d["spec"]) if _norm(c) not in blocos]
    if apenas_achado:
        return [f"categoria obrigatória do perfil sem '### Bloco: {c}' na Parte J" for c in falta]
    return falta


def verificar(spec):
    d = carregar(spec)
    ach = list(d["achados"])
    if not d["tem_i"] and not d["pontos"] and not d["tem_j"]:
        ach.append("sem Parte I, sem pontos para aprovação na Parte H e sem Parte J: nada a gerar")
    if d["tem_j"] and not any(rows for _, rows in d["blocos"]):
        ach.append("Parte J sem verificações (linhas `| VER-nn | ...` dentro de `### Bloco: <nome>`)")
    return d, ach


# ---------------------------------------------------------------- escrita no arquivo único
def _mapa(linhas):
    """Para cada linha do arquivo: (letra da parte, título do ### em minúsculas sem acento)."""
    parte, sec, out = None, "", []
    for ln, fora, titulo in spec_fonte._linhas_classificadas("\n".join(linhas)):
        if titulo:
            m = spec_fonte._PARTE.match(ln)
            parte, sec = (m.group(1) if m else None), ""
        elif fora and ln.startswith("### "):
            sec = _norm(ln[4:])
        out.append((parte, sec))
    return out


def _linha_md(cels):
    return "| " + " | ".join(cels) + " |"


def acrescentar_categorias(spec):
    """Acrescenta à Parte J um `### Bloco:` por categoria obrigatória ausente. Devolve as acrescentadas."""
    d = carregar(spec)
    falta = _categorias_faltantes(d)
    if not falta or not d["tem_j"]:
        return []
    linhas, nl = _ler_spec(spec)
    mapa = _mapa(linhas)
    idx_j = [i for i, (p, _) in enumerate(mapa) if p == "J"]
    blocos = [i for i in idx_j if mapa[i][1].startswith("bloco:")]
    outras = [i for i in idx_j if linhas[i].startswith("### ") and not mapa[i][1].startswith("bloco:")]
    if blocos:
        pos = next((i for i in outras if i > blocos[-1]), idx_j[-1] + 1)
    else:
        pos = outras[0] if outras else idx_j[-1] + 1
    n = max([int(r["Verificação"][4:]) for _, rows in d["blocos"] for r in rows] or [0])
    novo = []
    for c in falta:
        n += 1
        cel = ["a definir"] * len(COLS_VER)
        cel[0] = f"VER-{n:02d}"
        cel[4] = f"Categoria obrigatória do perfil: {c}. A área define o roteiro."
        for k in RESP_VER:
            cel[COLS_VER.index(k)] = ""
        novo += [f"### Bloco: {c}", _linha_md(COLS_VER), _linha_md(["---"] * len(COLS_VER)), _linha_md(cel), ""]
    linhas[pos:pos] = novo
    _gravar_spec(spec, linhas, nl)
    return falta


def _ler_spec(spec):
    """(linhas, terminador): o terminador do arquivo (CRLF ou LF) é preservado ao gravar — regravar tudo em
    outro terminador marcaria o arquivo inteiro como alterado e esconderia a mudança real no diff."""
    with open(spec, "rb") as fh:
        bruto = fh.read()
    return bruto.decode("utf-8-sig").splitlines(), ("\r\n" if b"\r\n" in bruto else "\n")


def _gravar_spec(spec, linhas, nl="\n"):
    with open(spec, "w", encoding="utf-8", newline="") as fh:
        fh.write(nl.join(linhas) + nl)


def _atualizar(linhas, mapa, parte, sec_pred, chave, cols, valores):
    """Grava `valores` {coluna: texto} na linha da tabela cuja 1ª célula é `chave`. True se achou."""
    for i, (p, s) in enumerate(mapa):
        if p != parte or not sec_pred(s) or not linhas[i].strip().startswith("|"):
            continue
        cel = _celulas(linhas[i])
        if cel[0] != chave:
            continue
        cel = [c.replace("|", "\\|") for c in cel] + [""] * (len(cols) - len(cel))
        for k, v in valores.items():
            cel[cols.index(k)] = _md(v)
        linhas[i] = _linha_md(cel)
        return True
    return False


def _ampliar_pontos(linhas, mapa):
    """Tabela de pontos da Parte H com 3 colunas ganha as 3 de resposta (cabeçalho, separador e linhas)."""
    for i, (p, s) in enumerate(mapa):
        if p == "H" and s == "pontos para aprovacao" and linhas[i].strip().startswith("|"):
            cel = _celulas(linhas[i])
            if len(cel) >= len(COLS_PONTO):
                continue
            if _SEP.match(linhas[i].strip()):
                linhas[i] = _linha_md(["---"] * len(COLS_PONTO))
            elif cel[0] == "#":
                linhas[i] = _linha_md(COLS_PONTO)
            else:
                linhas[i] = _linha_md([c.replace("|", "\\|") for c in cel] + [""] * (len(COLS_PONTO) - len(cel)))


def _acrescentar_na_rodada(linhas, mapa, n, vid, valores):
    idx = [i for i, (p, s) in enumerate(mapa) if p == "J" and re.match(rf"rodada {n}\b", s)
           and linhas[i].strip().startswith("|")]
    if not idx:
        raise Recusa(f"Rodada {n} não existe na Parte J")
    cel = [""] * len(COLS_RODADA)
    cel[0] = vid
    for k, v in valores.items():
        cel[COLS_RODADA.index(k)] = _md(v)
    linhas.insert(idx[-1] + 1, _linha_md(cel))


# ---------------------------------------------------------------- planilhas
def _rot(d, col):
    return d["rotulos"].get(col, col)


def _sha(spec):
    with open(spec, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:12]


def _estilo(ws, cab, resp, larguras=None):
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    azul, amarelo = PatternFill("solid", fgColor="1F4E78"), PatternFill("solid", fgColor="FFF2CC")
    for j, c in enumerate(cab, 1):
        cel = ws.cell(row=1, column=j)
        cel.font, cel.fill = Font(bold=True, color="FFFFFF"), azul
        cel.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(j)].width = (larguras or {}).get(j, 24)
    for row in ws.iter_rows(min_row=2):
        for cel in row:
            cel.alignment = Alignment(wrap_text=True, vertical="top")
            if isinstance(cel.value, str) and cel.value.startswith("="):
                cel.data_type = "s"  # texto que começa com '=' fica texto, não vira fórmula
            if cel.column <= len(cab) and cab[cel.column - 1] in resp:
                cel.fill = amarelo
                cel.number_format = "@"  # o que a área digitar fica como texto (ex.: '=03/2026' não vira fórmula)
    ws.freeze_panes = "B2"


def _aba_texto(wb, nome, pares):
    from openpyxl.styles import Alignment, Font
    ws = wb.create_sheet(nome)
    for i, (a, b) in enumerate(pares, 1):
        ws.cell(row=i, column=1, value=a).font = Font(bold=True)
        ws.cell(row=i, column=2, value=b).alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 28, 110


def _aba_tabela(wb, nome, cab, rows, resp=(), rotulo=lambda c: c):
    ws = wb.create_sheet(nome)
    ws.append([rotulo(c) for c in cab])
    for r in rows:
        ws.append([_xl(r.get(c, "")) for c in cab])
    _estilo(ws, [rotulo(c) for c in cab], {rotulo(c) for c in resp})
    return ws


def _validacao_sim_nao(ws, col, n):
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
    if n < 2:
        return
    dv = DataValidation(type="list", formula1='"Sim,Não,Com correção"', allow_blank=True)
    ws.add_data_validation(dv)
    L = get_column_letter(col)
    dv.add(f"{L}2:{L}{n}")


def linhas_confirmacao(d):
    rows = list(d["definicoes"])
    for p in d["pontos"]:
        r = {c: "—" for c in COLS_DEF}
        r.update({"Definição": f"H-{p['#']}", "Tema": "Processo", "Regra, como entendemos": p["Ponto"],
                  "De onde tiramos": f"Desenho do processo (Parte H). Por que importa: {p['Por que importa']}"})
        for k in RESP_DEF:
            r[k] = p.get(k, "")
        rows.append(r)
    return rows


def montar_confirmacao(d, versao, destino):
    import openpyxl
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    leia = list(d["leia"]) + [
        ("O que a área faz", "Em cada linha das abas REGRAS e VALORES POR CATEGORIA, preencha só as três últimas "
         "colunas (em amarelo): Área confirma? (Sim, Não ou Com correção), Correção da área e Nome e data. "
         "Não altere as outras colunas, os títulos nem a ordem."),
        ("Versão", f"v{versao}, gerada em {datetime.date.today():%d/%m/%Y} do arquivo único "
         f"{os.path.basename(os.path.dirname(os.path.abspath(d['spec'])))}/spec.md (sha256 {_sha(d['spec'])})."),
    ]
    _aba_texto(wb, "LEIA", leia)
    rows = linhas_confirmacao(d)
    ws = _aba_tabela(wb, "REGRAS", COLS_DEF, rows, RESP_DEF, lambda c: _rot(d, c))
    _validacao_sim_nao(ws, COLS_DEF.index("Área confirma?") + 1, len(rows) + 1)
    if d["valores"]:
        cab, dados = d["valores"]
        ws = wb.create_sheet("VALORES POR CATEGORIA")
        ws.append([_rot(d, c) for c in cab])
        for r in dados:
            ws.append([_xl(x) for x in r])
        _estilo(ws, [_rot(d, c) for c in cab], {_rot(d, c) for c in RESP_DEF})
        _validacao_sim_nao(ws, len(cab) - 2, len(dados) + 1)
    wb.properties.keywords = f"planilhas_projeto:confirmacao:v{versao}:{_sha(d['spec'])}"
    wb.save(destino)


def cab_checklist(d):
    cab = [_rot(d, c) for c in COLS_VER]
    for n, data, _ in d["rodadas"]:
        cab += [f"Rodada {n} ({data}) · {_rot(d, c)}" for c in COLS_RODADA[1:]]
    return cab


def montar_verificacao(d, versao, destino):
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    como = list(d["como_usar"]) + [
        ("Como preencher", "Na aba CHECKLIST, confira cada linha no sistema e preencha as colunas em amarelo: "
         "Valor encontrado, Conclusão da área e Data / Visto; em cada rodada, Resposta da área e Nome e data. "
         "Não altere as outras colunas, os títulos nem a ordem."),
        ("Como acrescentar uma rodada", "Quando a equipe precisar devolver perguntas à área, rode "
         "`python tools/planilhas_projeto.py rodada <spec.md> --data dd/mm/aaaa --ids VER-01,VER-03`: a próxima "
         "rodada entra na Parte J do arquivo único, uma linha por verificação questionada. Escreva a pergunta de "
         "volta de cada uma e gere de novo: a rodada aparece como novas colunas no CHECKLIST."),
        ("Versão", f"v{versao}, gerada em {datetime.date.today():%d/%m/%Y} (sha256 {_sha(d['spec'])})."),
    ]
    _aba_texto(wb, "COMO USAR", como)
    _aba_texto(wb, "ANTES DE COMEÇAR", [(f"{i}.", t) for i, t in enumerate(d["antes"], 1)] or [("—", "Sem armadilhas registradas.")])
    ws = wb.create_sheet("CHECKLIST")
    cab = cab_checklist(d)
    ws.append(cab)
    faixa = PatternFill("solid", fgColor="D9E1F2")
    linhas_bloco = []
    for nome, rows in d["blocos"]:
        ws.append([f"BLOCO: {nome}"])
        linhas_bloco.append(ws.max_row)
        for r in rows:
            vals = [_xl(r[c]) for c in COLS_VER]
            for _, _, rod in d["rodadas"]:
                rr = rod.get(r["Verificação"], {})
                vals += [_xl(rr.get(c, "")) for c in COLS_RODADA[1:]]
            ws.append(vals)
    resp = {_rot(d, c) for c in RESP_VER} | {h for h in cab if any(h.endswith("· " + _rot(d, c)) for c in RESP_RODADA)}
    _estilo(ws, cab, resp)
    for i in linhas_bloco:
        for cel in ws[i]:
            cel.fill, cel.font = faixa, Font(bold=True)
    _aba_tabela(wb, "ACHADOS DO AMBIENTE", COLS_ACHADO, d["achados_amb"])
    _aba_tabela(wb, "CORREÇÕES DA BASE", COLS_CORRECAO, d["correcoes"])
    auto = {"Versão": f"v{versao}", "Data": f"{datetime.date.today():%d/%m/%Y}",
            "Autor": "tools/planilhas_projeto.py", "Conteúdo": "gerada do arquivo único",
            "Base utilizada": f"spec.md sha256 {_sha(d['spec'])}"}
    _aba_tabela(wb, "CONTROLE DE VERSÃO", COLS_VERSAO, list(d["versoes"]) + [auto])
    wb.properties.keywords = f"planilhas_projeto:verificacao:v{versao}:{_sha(d['spec'])}"
    wb.save(destino)


# ---------------------------------------------------------------- respostas lidas de uma planilha
def _abrir(xlsx, **kw):
    """Carrega pelos bytes: o openpyxl deixa o arquivo preso no Windows (WinError 32 ao mover a versão)."""
    import io
    import openpyxl
    with open(xlsx, "rb") as fh:
        return openpyxl.load_workbook(io.BytesIO(fh.read()), **kw)


def respostas(xlsx, tipo, d, por_posicao=False):
    """{(aba, id, coluna do modelo): valor} de toda resposta NÃO vazia. Recusa cabeçalho mudado.

    Lê SEM `data_only`: texto que começa com '=' volta como foi digitado, e fórmula sem valor calculado não
    some. `por_posicao`: versão anterior gerada por nós — o rótulo pode ter mudado no arquivo único depois
    dela; vale a posição (fixa), conferindo só a quantidade de colunas."""
    wb = _abrir(xlsx)
    out = {}

    def ler(aba, esperado, resp, chave_re):
        if aba not in wb.sheetnames:
            raise Recusa(f"{os.path.basename(xlsx)}: aba {aba} ausente")
        ws = wb[aba]
        cab = [_txt(c.value) for c in ws[1]]
        while cab and cab[-1] == "":
            cab.pop()
        rot = [r for r, _ in esperado]
        if (len(cab) != len(rot)) if por_posicao else (cab != rot):
            raise Recusa(f"{os.path.basename(xlsx)}: aba {aba} com cabeçalho diferente do gerado — a área mudou "
                         f"título ou ordem, ou o `### Rótulos` do arquivo único mudou depois desta versão. Esperado {rot}, encontrado {cab}")
        for row in ws.iter_rows(min_row=2, values_only=True):
            chave = _txt(row[0] if row else None)
            if not chave or not re.fullmatch(chave_re, chave):
                continue
            for j, (_, modelo) in enumerate(esperado):
                if modelo in resp and j < len(row):
                    v = _txt(row[j])
                    if v:
                        out[(aba, chave, modelo)] = v

    if tipo == "confirmacao":
        ler("REGRAS", [(_rot(d, c), c) for c in COLS_DEF], set(RESP_DEF), r"(DEF-\d+|H-\d+)")
        if "VALORES POR CATEGORIA" in wb.sheetnames:
            ws = wb["VALORES POR CATEGORIA"]
            cab = [_txt(c.value) for c in ws[1]]
            while cab and cab[-1] == "":
                cab.pop()
            modelo = d["valores"][0] if d["valores"] else []
            if (len(cab) != len(modelo)) if por_posicao else (cab != [_rot(d, c) for c in modelo]):
                raise Recusa(f"{os.path.basename(xlsx)}: aba VALORES POR CATEGORIA com cabeçalho diferente do gerado")
            for row in ws.iter_rows(min_row=2, values_only=True):
                chave = _txt(row[0] if row else None)
                if not chave:
                    continue
                for j, c in enumerate(modelo):
                    if c in RESP_DEF and j < len(row) and _txt(row[j]):
                        out[("VALORES POR CATEGORIA", chave, c)] = _txt(row[j])
    else:
        esperado = [(_rot(d, c), c) for c in COLS_VER]
        for n, data, _ in d["rodadas"]:
            esperado += [(f"Rodada {n} ({data}) · {_rot(d, c)}", f"R{n}:{c}") for c in COLS_RODADA[1:]]
        resp = set(RESP_VER) | {f"R{n}:{c}" for n, _, _ in d["rodadas"] for c in RESP_RODADA}
        ler("CHECKLIST", esperado, resp, r"VER-\d+")
    return out


def _meta(xlsx):
    wb = _abrir(xlsx)
    m = re.fullmatch(r"planilhas_projeto:(\w+):v(\d+):(\w+)", wb.properties.keywords or "")
    return (m.group(1), int(m.group(2))) if m else (None, None)


# ---------------------------------------------------------------- versões
def _ultima(out_dir, tipo):
    vs = [int(m.group(2)) for f in os.listdir(out_dir) if (m := _VERSAO.match(f)) and m.group(1) == tipo] \
        if os.path.isdir(out_dir) else []
    return max(vs) if vs else 0


def _aberta(caminho):
    pasta, nome = os.path.split(caminho)
    return any(os.path.exists(os.path.join(pasta, "~$" + n)) for n in (nome, nome[2:]))


def gerar_tipo(spec, tipo, out_dir, log=print, descartar=None):
    """Cria vN+1; move vN para _obsoleto/, compara, e só então apaga vN. Recusa → nada muda.

    `descartar` ("<frase do dono, dd/mm/aaaa>"): aceita perder respostas de linhas REMOVIDAS do arquivo
    único; a vN fica guardada em `_obsoleto/` (não é apagada). Resposta de linha que continua no arquivo
    único nunca é descartável: pede `importar`."""
    if descartar is not None and not regulado._nome_e_data(descartar):
        raise Recusa("--descartar exige a frase do dono com data válida (dd/mm/aaaa)")
    d, ach = verificar(spec)
    if ach:  # vale também para quem chama direto (importar): arquivo único vazio ou quebrado não gera nada
        raise Recusa("arquivo único com achados de estrutura: " + "; ".join(ach))
    os.makedirs(out_dir, exist_ok=True)
    n = _ultima(out_dir, tipo)
    antiga = os.path.join(out_dir, f"{tipo}_v{n}.xlsx") if n else None
    if antiga and _aberta(antiga):
        raise Recusa(f"{antiga} está aberta no Excel (arquivo ~$): feche antes de gerar")
    nova = os.path.join(out_dir, f"{tipo}_v{n + 1}.xlsx")
    obsoleta = None
    if antiga:
        os.makedirs(os.path.join(out_dir, "_obsoleto"), exist_ok=True)
        obsoleta = os.path.join(out_dir, "_obsoleto", os.path.basename(antiga))
        shutil.move(antiga, obsoleta)
    guardar = False
    try:
        (montar_confirmacao if tipo == "confirmacao" else montar_verificacao)(d, n + 1, nova)
        if obsoleta:
            velhas = respostas(obsoleta, tipo, _carregar_como_gerada(d, obsoleta, tipo), por_posicao=True)
            novas = respostas(nova, tipo, d)
            perdidas = {k: v for k, v in velhas.items() if novas.get(k) != v}
            vivas = _ids_gerados(nova)
            removidas = sorted({(a, i) for a, i, _ in perdidas if (a, i) not in vivas})
            pendentes = sorted({(a, i) for a, i, _ in perdidas if (a, i) in vivas})
            if pendentes:
                raise Recusa(f"v{n} tem resposta(s) da área ainda não gravadas no arquivo único em {pendentes} — "
                             f"rode `importar --planilha <a v{n}>` antes de gerar")
            if removidas and descartar is None:
                raise Recusa(f"v{n} tem resposta(s) da área em linha(s) que saíram do arquivo único: {removidas}. "
                             f"Devolva a linha ao arquivo único, ou registre a decisão com "
                             f"--descartar \"<frase do dono, dd/mm/aaaa>\" (a v{n} fica guardada em _obsoleto/)")
            guardar = bool(removidas)
            if guardar:
                log(f"descartadas as respostas de {removidas} — decisão: {descartar}; v{n} guardada em {obsoleta}")
    except BaseException:
        if os.path.exists(nova):
            os.remove(nova)
        if obsoleta:
            shutil.move(obsoleta, antiga)
            _limpar_obsoleto(out_dir)
        raise
    if obsoleta and not guardar:
        try:
            os.remove(obsoleta)
            _limpar_obsoleto(out_dir)
        except OSError as e:
            log(f"AVISO: v{n} comparada (respostas preservadas na v{n + 1}), mas não foi apagada de _obsoleto/: {e}. "
                f"Apague {obsoleta} quando o arquivo for liberado")
            return nova
    log(f"{nova} gerada" + (f"; v{n} comparada (respostas preservadas) e apagada" if n and not guardar else ""))
    return nova


def _ids_gerados(xlsx):
    """{(aba, id)} das linhas da planilha recém-gerada: o que continua existindo no arquivo único."""
    wb = _abrir(xlsx)
    out = set()
    for aba in ("REGRAS", "VALORES POR CATEGORIA", "CHECKLIST"):
        if aba in wb.sheetnames:
            for row in wb[aba].iter_rows(min_row=2, max_col=1, values_only=True):
                if _txt(row[0]):
                    out.add((aba, _txt(row[0])))
    return out


def _carregar_como_gerada(d, xlsx, tipo):
    """A versão anterior pode ter outra lista de rodadas (rodada nova acrescentada depois): o cabeçalho
    esperado dela vem do próprio arquivo, com os rótulos atuais."""
    if tipo != "verificacao":
        return d
    wb = _abrir(xlsx)
    cab = [_txt(c.value) for c in next(wb["CHECKLIST"].iter_rows(min_row=1, max_row=1))]
    rod = []
    for h in cab:
        m = re.match(r"Rodada (\d+) \((\d{1,2}/\d{1,2}/\d{4})\)", h)
        if m and (int(m.group(1)), m.group(2)) not in [(a, b) for a, b, _ in rod]:
            rod.append((int(m.group(1)), m.group(2), {}))
    return dict(d, rodadas=rod)


def _limpar_obsoleto(out_dir):
    p = os.path.join(out_dir, "_obsoleto")
    if os.path.isdir(p) and not os.listdir(p):
        os.rmdir(p)


def importar(spec, planilha, out_dir, log=print):
    """Grava no arquivo único as respostas da planilha devolvida e gera a versão seguinte."""
    if _aberta(planilha):
        raise Recusa(f"{planilha} está aberta no Excel (arquivo ~$): feche antes de importar")
    tipo, versao = _meta(planilha)
    if tipo not in TIPOS:
        raise Recusa(f"{planilha} não foi gerada por planilhas_projeto.py (sem a marca de versão)")
    ultima = _ultima(out_dir, tipo)
    if versao != ultima:
        raise Recusa(f"{planilha} é a v{versao}; a versão vigente em {out_dir} é a v{ultima}. Importe só "
                     f"respostas da versão vigente — a área respondeu uma versão superada")
    d = carregar(spec)
    if d["achados"]:
        raise Recusa("arquivo único com achados de estrutura: " + "; ".join(d["achados"]))
    resp = respostas(planilha, tipo, _carregar_como_gerada(d, planilha, tipo))
    linhas, nl = _ler_spec(spec)
    if tipo == "confirmacao" and any(k[1].startswith("H-") for k in resp):
        _ampliar_pontos(linhas, _mapa(linhas))
    por_linha = {}
    for (aba, chave, col), v in resp.items():
        por_linha.setdefault((aba, chave), {})[col] = v
    faltou = []
    for (aba, chave), vals in por_linha.items():
        mapa = _mapa(linhas)
        if aba == "REGRAS" and chave.startswith("H-"):
            ok = _atualizar(linhas, mapa, "H", lambda s: s == "pontos para aprovacao", chave[2:], COLS_PONTO, vals)
        elif aba == "REGRAS":
            ok = _atualizar(linhas, mapa, "I", lambda s: s == "", chave, COLS_DEF, vals)
        elif aba == "VALORES POR CATEGORIA":
            ok = _atualizar(linhas, mapa, "I", lambda s: s == "valores por categoria", chave, d["valores"][0], vals)
        else:
            base = {c: v for c, v in vals.items() if ":" not in c}
            ok = not base or _atualizar(linhas, mapa, "J", lambda s: s.startswith("bloco:"), chave, COLS_VER, base)
            for n in sorted({int(c[1:c.index(":")]) for c in vals if ":" in c}):
                rv = {c.split(":", 1)[1]: v for c, v in vals.items() if c.startswith(f"R{n}:")}
                if not _atualizar(linhas, _mapa(linhas), "J", lambda s, n=n: re.match(rf"rodada {n}\b", s),
                                  chave, COLS_RODADA, rv):
                    _acrescentar_na_rodada(linhas, _mapa(linhas), n, chave, rv)
        if not ok:
            faltou.append(f"{aba}/{chave}")
    if faltou:
        raise Recusa(f"linhas da planilha sem correspondente no arquivo único: {faltou} — nada foi gravado")
    _gravar_spec(spec, linhas, nl)
    log(f"{len(resp)} resposta(s) gravadas em {spec}")
    return gerar_tipo(spec, tipo, out_dir, log)


# ---------------------------------------------------------------- situação e rodada (comandos, não instrução)
def situacao(spec):
    """Conta, sem julgamento, o que a área já respondeu. Devolve (linhas de relatório, pendências).

    Confirmação: linha respondida = 'Área confirma?' preenchida E 'Nome e data' com nome e data válida;
    pendência = sem resposta assinada, ou resposta diferente de 'Sim' (Não / Com correção = a tratar).
    Verificação: linha concluída = 'Conclusão da área' preenchida E 'Data / Visto' com data válida;
    rodada: pergunta de volta sem resposta da área assinada é pendência."""
    d = carregar(spec)
    if d["achados"]:
        raise Recusa("arquivo único com achados de estrutura: " + "; ".join(d["achados"]))
    rel, pend = [], []

    def conf(nome, chave, r):
        if not (r.get("Área confirma?", "").strip() and regulado._nome_e_data(r.get("Nome e data", ""))):
            pend.append(f"{nome} {chave}: sem resposta assinada (Área confirma? + Nome e data)")
        elif _norm(r["Área confirma?"]) != "sim":
            pend.append(f"{nome} {chave}: área respondeu '{r['Área confirma?']}' — tratar a correção")

    linhas_conf = [("definição", r["Definição"], r) for r in d["definicoes"]]
    linhas_conf += [("ponto", f"H-{p['#']}", p) for p in d["pontos"]]
    if d["valores"]:
        cab, dados = d["valores"]
        linhas_conf += [("valor", r[0], dict(zip(cab, r))) for r in dados]
    for nome, chave, r in linhas_conf:
        conf(nome, chave, r)
    n_conf = sum(1 for p in pend if ": sem resposta" in p)
    rel.append(f"confirmação: {len(linhas_conf) - n_conf} de {len(linhas_conf)} linha(s) com resposta assinada")
    vers = [r for _, rows in d["blocos"] for r in rows]
    antes = len(pend)
    for r in vers:
        if not (r["Conclusão da área"].strip() and regulado._tem_data(r["Data / Visto"])):
            pend.append(f"verificação {r['Verificação']}: sem conclusão da área com data")
    rel.append(f"verificação: {len(vers) - (len(pend) - antes)} de {len(vers)} linha(s) concluídas")
    for n, data, rows in d["rodadas"]:
        for vid, r in rows.items():
            if r["Pergunta de volta"].strip() and not (r["Resposta da área"].strip()
                                                       and regulado._nome_e_data(r["Nome e data"])):
                pend.append(f"rodada {n} ({data}) {vid}: pergunta de volta sem resposta assinada")
    return rel, pend


def nova_rodada(spec, data, ids, log=print):
    """Acrescenta `### Rodada N — data` (N = próxima) à Parte J com uma linha por verificação em `ids`."""
    if not regulado._tem_data(data) or not re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", data.strip()):
        raise Recusa("--data exige dd/mm/aaaa válida")
    d = carregar(spec)
    if d["achados"]:
        raise Recusa("arquivo único com achados de estrutura: " + "; ".join(d["achados"]))
    if not d["tem_j"]:
        raise Recusa("sem Parte J — Roteiro de verificação")
    existentes = {r["Verificação"] for _, rows in d["blocos"] for r in rows}
    ids = list(dict.fromkeys(i.strip() for i in ids if i.strip()))  # repetido em --ids entra uma vez
    faltam = [i for i in ids if i not in existentes]
    if not ids or faltam:
        raise Recusa(f"--ids precisa listar verificações existentes; inexistentes: {faltam or 'nenhuma informada'}")
    n = len(d["rodadas"]) + 1
    linhas, nl = _ler_spec(spec)
    mapa = _mapa(linhas)
    idx_j = [i for i, (p, _) in enumerate(mapa) if p == "J"]
    secs = [i for i in idx_j if linhas[i].startswith("### ")]
    ancora = [i for i in secs if mapa[i][1].startswith(("bloco:", "rodada"))]
    pos = next((i for i in secs if i > ancora[-1]), idx_j[-1] + 1) if ancora else idx_j[-1] + 1
    novo = [f"### Rodada {n} — {data.strip()}", _linha_md(COLS_RODADA), _linha_md(["---"] * len(COLS_RODADA))]
    novo += [_linha_md([i] + [""] * (len(COLS_RODADA) - 1)) for i in ids] + [""]
    linhas[pos:pos] = novo
    _gravar_spec(spec, linhas, nl)
    log(f"Rodada {n} — {data.strip()} acrescentada com {len(ids)} verificação(ões); escreva a pergunta de volta "
        f"de cada uma e gere de novo")
    return n


# ---------------------------------------------------------------- CLI
def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("comando", choices=["verificar", "gerar", "importar", "situacao", "rodada"])
    ap.add_argument("spec")
    ap.add_argument("--out-dir")
    ap.add_argument("--so", choices=TIPOS)
    ap.add_argument("--planilha")
    ap.add_argument("--descartar", help="\"<frase do dono, dd/mm/aaaa>\": aceita perder respostas de linhas removidas")
    ap.add_argument("--exigir", action="store_true", help="situacao: exit 1 se houver pendência")
    ap.add_argument("--data", help="rodada: dd/mm/aaaa")
    ap.add_argument("--ids", help="rodada: VER-01,VER-03")
    a = ap.parse_args(argv)
    try:
        if a.comando == "verificar":
            _, ach = verificar(a.spec)
            for x in ach:
                print(f"ACHADO: {x}")
            print("RESULTADO:", "FAIL" if ach else "PASS")
            return 1 if ach else 0
        if a.comando == "situacao":
            rel, pend = situacao(a.spec)
            for x in rel:
                print(x)
            for x in pend:
                print(f"PENDENTE: {x}")
            print("RESULTADO:", ("FAIL" if pend else "PASS") if a.exigir else f"{len(pend)} pendência(s)")
            return 1 if (a.exigir and pend) else 0
        if a.comando == "rodada":
            if not a.data or not a.ids:
                ap.error("rodada exige --data e --ids")
            nova_rodada(a.spec, a.data, a.ids.split(","))
            return 0
        if not a.out_dir:
            ap.error("--out-dir é obrigatório")
        if a.comando == "importar":
            if not a.planilha:
                ap.error("--planilha é obrigatório")
            importar(a.spec, a.planilha, a.out_dir)
            return 0
        for c in acrescentar_categorias(a.spec):
            print(f"acrescentado à Parte J: ### Bloco: {c} (categoria obrigatória do perfil)")
        d, ach = verificar(a.spec)
        if ach:
            for x in ach:
                print(f"ACHADO: {x}")
            print("RESULTADO: FAIL — nada foi gerado")
            return 1
        tipos = [a.so] if a.so else [t for t in TIPOS if (t == "confirmacao" and (d["tem_i"] or d["pontos"]))
                                     or (t == "verificacao" and d["tem_j"])]
        for t in tipos:
            gerar_tipo(a.spec, t, a.out_dir, descartar=a.descartar)
        return 0
    except (Recusa, OSError) as e:
        print(f"RECUSADO: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
