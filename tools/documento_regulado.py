#!/usr/bin/env python3
"""documento_regulado.py — documentos do kit regulado gerados do arquivo único (B3a-3, ADR-124).

Motor NEUTRO: não conhece norma nem documento. O PERFIL regulado declarado no projeto (`**Perfil regulado:**`,
`exemplos/dominio-regulado/compliance-profile-<nome>.json`) define, em `"documentos"`, cada documento que emite:
título, seções e rótulos. Um perfil sem o documento não o emite (decisão do dono, 27/09/2026: cada documento
regulado é do perfil que o exige; cada perfil traz os seus).

Seções que o motor sabe montar (o perfil escolhe quais e em que ordem):
  identificacao         projeto, sistema, categoria, perfil, versão da especificação (sha256)
  documento_controlado  código e versão do documento, da tabela `### Documentos controlados` da Parte A
                        (código vazio = "a preencher pela Qualidade"; nunca inventado)
  requisitos            `- REQ-nn: ...` da Parte A + colunas de `### Atributos dos requisitos` (nomes no perfil)
  riscos · testes       Partes F e G
  desvios               `### Desvios` da Parte G; teste reprovado sem desvio é achado
  prontidao             `### Prontidão para operação` da Parte G; itens obrigatórios vêm do perfil
  aprovacao             linhas de assinatura com os papéis do perfil

Sem `--rascunho`, qualquer lacuna reprova e nada é gravado. Com `--rascunho`, grava marcado "RASCUNHO" e com as
lacunas como PENDENTE.

Uso (pelo regulado.py):
    python tools/regulado.py documento <tipo> <spec.md> --out-dir <pasta> [--rascunho]
"""
import datetime
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regulado  # noqa: E402
import spec_fonte  # noqa: E402

# Descrição de cada REQ, LINHA A LINHA ([ \t], nunca \s): a lista de REQs é a do motor (regulado.carregar); aqui só
# se lê a descrição, sem atravessar para a linha seguinte (revisão de 28/09: REQ vazio engolia o seguinte).
_DESC_REQ = re.compile(r"(?m)^[ \t]*(?:[-*+]|\d+[.)])?[ \t]*(?:\*\*)?[ \t]*(REQ-\d+)[ \t]*(?:\*\*)?[ \t]*[:—–-][ \t]*(.*?)[ \t]*$")
RESULTADOS = {"aprovado", "reprovado"}
_SEP = re.compile(r"^\|?\s*:?-{3,}")
COLS_DOC = ["documento", "código", "versão"]
COLS_DESVIO = ["desvio", "teste", "descrição", "tratamento", "nome e data"]
COLS_PRONTIDAO = ["item", "situação", "onde está"]
PENDENTE = "PENDENTE"


class Recusa(Exception):
    """O perfil não emite este documento, ou falta o registro de enquadramento."""


def _linha(cels):
    return "| " + " | ".join(cels) + " |"


def _celulas(ln):
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", ln.strip().strip("|"))]


def _tabela_da_secao(texto, titulo):
    """(cabeçalho minúsculo, [linhas]) da tabela sob `### <titulo>` (sem acento/caixa), ou (None, [])."""
    alvo = regulado_norm(titulo)
    dentro, cab, linhas = False, None, []
    for ln in (texto or "").splitlines():
        if ln.startswith("### "):
            if dentro:
                break
            dentro = regulado_norm(ln[4:]) == alvo
            continue
        if not dentro or not ln.strip().startswith("|"):
            continue
        if _SEP.match(ln.strip()):
            continue
        cel = _celulas(ln)
        if cab is None:
            cab = [c.lower() for c in cel]
        else:
            linhas.append(cel)
    return cab, linhas


def regulado_norm(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(c)).casefold().strip()


def _vazio(v):
    return regulado._vazio(v) or bool(re.fullmatch(r"<[^>]*>", (v or "").strip()))


def definicao(perfil, tipo):
    docs = (perfil or {}).get("documentos") or {}
    if tipo not in docs:
        raise Recusa(f"o perfil não emite o documento '{tipo}' (documentos do perfil: "
                     f"{', '.join(sorted(k for k in docs if not k.startswith('_'))) or 'nenhum'})")
    return docs[tipo]


def montar(spec, tipo):
    """(markdown, achados)."""
    d = regulado.carregar(spec)
    faltas = regulado.registro(d)
    if faltas:
        raise Recusa("; ".join(faltas))
    if d["impacto"] != "sim" or not d["perfil"]:
        raise Recusa("projeto sem impacto regulado declarado: o kit regulado não se aplica")
    df = definicao(d["perfil"], tipo)
    parte_a = spec_fonte.ler_parte(spec, "requisitos") or ""
    parte_g = spec_fonte.ler_parte(spec, "testes") or ""
    texto = d["texto"]
    titulo_proj = next((ln[2:].strip() for ln in texto.splitlines() if ln.startswith("# ") and "Parte" not in ln), "")
    sha = hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]
    ach, md = [], [f"# {df.get('titulo', tipo)}", ""]

    def P(v):
        return v if not _vazio(v) else PENDENTE

    for sec in df.get("secoes", []):
        if sec == "identificacao":
            md += ["## Identificação", "", "| Campo | Valor |", "|---|---|",
                   f"| Projeto | {titulo_proj} |", f"| Sistema | {P(d['sistema'])} |",
                   f"| Categoria de software | {P(d['categoria'])} |", f"| Perfil regulado | {d['perfil_nome']} |",
                   f"| Especificação de origem | {os.path.basename(os.path.dirname(os.path.abspath(spec)))}/spec.md "
                   f"(sha256 {sha}) |", f"| Gerado em | {datetime.date.today():%d/%m/%Y} |", ""]
        elif sec == "documento_controlado":
            cab, linhas = _tabela_da_secao(parte_a, "Documentos controlados")
            linha = None
            if cab == COLS_DOC:
                nomes = {regulado_norm(tipo), regulado_norm(df.get("titulo", ""))}
                linha = next((dict(zip(COLS_DOC, c)) for c in linhas if regulado_norm(c[0]) in nomes), None)
            if linha is None:
                ach.append(f"`### Documentos controlados` da Parte A sem linha para '{tipo}' "
                           f"(| Documento | Código | Versão |)")
                linha = {"código": "", "versão": ""}
            cod = linha["código"] if not _vazio(linha["código"]) else "a preencher pela Qualidade"
            md += ["## Documento controlado", "", f"- **Código:** {cod}",
                   f"- **Versão:** {P(linha['versão'])}", ""]
        elif sec == "requisitos":
            campos = [c.lower() for c in df.get("requisito_campos", [])]
            cab, linhas = _tabela_da_secao(parte_a, "Atributos dos requisitos")
            attrs = {}
            if campos:
                if cab != ["requisito"] + campos:
                    ach.append(f"`### Atributos dos requisitos` da Parte A: cabeçalho deve ser | Requisito | "
                               f"{' | '.join(df['requisito_campos'])} |")
                else:
                    attrs = {c[0]: dict(zip(campos, c[1:])) for c in linhas if len(c) == len(cab)}
            descricoes = {}
            for rid, desc in _DESC_REQ.findall(parte_a):
                descricoes.setdefault(rid, desc.strip("* ").strip())
            reqs = []
            for rid in regulado.duplicados_reqs(d["reqs"]):
                ach.append(f"{rid} definido mais de uma vez na Parte A")
            for rid in dict.fromkeys(d["reqs"]):  # fonte única: a mesma lista que verificar/kit usam
                desc = descricoes.get(rid, "")
                if _vazio(desc):
                    ach.append(f"{rid} sem descrição na Parte A")
                reqs.append((rid, desc if not _vazio(desc) else PENDENTE))
            if not reqs:
                ach.append("nenhum requisito `- REQ-nn: ...` na Parte A")
            rot = df.get("requisito_campos", [])
            md += ["## Requisitos", "", _linha(["Requisito", "Descrição"] + rot), _linha(["---"] * (2 + len(rot)))]
            for rid, desc in reqs:
                vals = []
                for c in campos:
                    v = attrs.get(rid, {}).get(c, "")
                    if _vazio(v):
                        ach.append(f"{rid} sem '{c}' em `### Atributos dos requisitos`")
                    vals.append(P(v))
                md.append(_linha([rid, desc.replace("|", "/")] + vals))
            md.append("")
        elif sec == "riscos":
            md += ["## Riscos", "", "| Risco | Requisito | Falha | Classe | Mitigação | Teste |",
                   "|---|---|---|---|---|---|"]
            md += [f"| {r['risco']} | {r['requisito']} | {r['falha']} | {r['classe']} | {r['mitigação']} | "
                   f"{r['teste']} |" for r in d["riscos"]] + [""]
        elif sec == "testes":
            md += ["## Testes executados", "", "| Teste | Requisito | Categoria | Resultado | Evidência | Nome e data |",
                   "|---|---|---|---|---|---|"]
            md += [f"| {t['teste']} | {t['requisito']} | {t['categoria']} | {P(t['resultado'])} | "
                   f"{P(t['evidência'])} | {P(t['nome e data'])} |" for t in d["testes"]] + [""]
            ach += [f"verificação do kit: {a}" for a in regulado.verificar(spec)]
        elif sec == "desvios":
            cab, linhas = _tabela_da_secao(parte_g, "Desvios")
            desvios = []
            if cab is not None and cab != COLS_DESVIO:
                ach.append("`### Desvios` da Parte G: cabeçalho deve ser | Desvio | Teste | Descrição | Tratamento | "
                           "Nome e data |")
            elif cab is not None:
                desvios = [dict(zip(COLS_DESVIO, c)) for c in linhas if len(c) == len(COLS_DESVIO)]
            com_desvio = set().union(*[regulado._refs(x["teste"], "TESTE") for x in desvios]) if desvios else set()
            for t in d["testes"]:
                res = regulado_norm(t["resultado"])
                if res not in RESULTADOS:
                    # enum fechado: sinônimo ("não aprovado", "rejeitado") não pode escapar da exigência de desvio
                    ach.append(f"{t['teste']} com Resultado '{t['resultado']}': use aprovado ou reprovado")
                elif res == "reprovado" and t["teste"] not in com_desvio:
                    ach.append(f"{t['teste']} reprovado sem desvio registrado em `### Desvios`")
            for x in desvios:
                for k in ("descrição", "tratamento"):
                    if _vazio(x[k]):
                        ach.append(f"{x['desvio']} sem {k}")
                if not regulado._nome_e_data(x["nome e data"]):
                    ach.append(f"{x['desvio']} sem nome e data")
            md += ["## Desvios", ""]
            if desvios:
                md += ["| Desvio | Teste | Descrição | Tratamento | Nome e data |", "|---|---|---|---|---|"]
                md += [f"| {x['desvio']} | {x['teste']} | {P(x['descrição'])} | {P(x['tratamento'])} | "
                       f"{P(x['nome e data'])} |" for x in desvios]
            else:
                md.append("Nenhum desvio registrado.")
            md.append("")
        elif sec == "prontidao":
            itens = df.get("itens", [])
            cab, linhas = _tabela_da_secao(parte_g, "Prontidão para operação")
            reg = {}
            if cab != COLS_PRONTIDAO:
                ach.append("`### Prontidão para operação` da Parte G: cabeçalho deve ser | Item | Situação | Onde está |")
            else:
                reg = {regulado_norm(c[0]): dict(zip(COLS_PRONTIDAO, c)) for c in linhas if len(c) == 3}
            md += ["## Prontidão para operação", "", "| Item | Situação | Onde está |", "|---|---|---|"]
            for it in itens:
                r = reg.get(regulado_norm(it))
                if r is None or _vazio(r["situação"]) or _vazio(r["onde está"]):
                    ach.append(f"prontidão: item '{it}' sem situação ou sem onde está")
                md.append(f"| {it} | {P((r or {}).get('situação', ''))} | {P((r or {}).get('onde está', ''))} |")
            md.append("")
        elif sec == "aprovacao":
            md += ["## Aprovação", "", "| Papel | Nome | Data | Assinatura |", "|---|---|---|---|"]
            md += [f"| {p} |  |  |  |" for p in df.get("aprovacao", [])]
            md += ["", df.get("nota_aprovacao", "A aprovação formal acontece no sistema de documentos controlados."), ""]
        else:
            ach.append(f"seção '{sec}' do perfil não é conhecida pelo motor")
    return "\n".join(md) + "\n", ach


def gerar(spec, tipo, out_dir, rascunho=False):
    """(achados, arquivos). Sem rascunho e com achado: nada é gravado."""
    md, ach = montar(spec, tipo)
    if ach and not rascunho:
        return ach, []
    if rascunho:
        md = md.replace("# ", "# RASCUNHO — ", 1).replace(
            "\n", "\n\nRASCUNHO com lacunas (PENDENTE): não usar como documento controlado.\n", 1)
    import gen_exec_doc  # noqa: E402
    try:
        escritos, _pulados = gen_exec_doc.export(md, out_dir, ["md", "docx"], basename=tipo)
    except OSError as e:  # arquivo aberto no editor, sem permissão: mensagem legível, não traceback
        raise Recusa(f"não consegui gravar em {out_dir} ({e}); feche o arquivo aberto e rode de novo")
    return ach, escritos


def main(argv):
    """argv: [tipo, spec, --out-dir, pasta, (--rascunho)]."""
    args = [a for a in argv if not a.startswith("--")]
    rascunho = "--rascunho" in argv
    out = None
    if "--out-dir" in argv:
        i = argv.index("--out-dir")
        out = argv[i + 1] if i + 1 < len(argv) else None
        args = [a for a in args if a != out]
    if len(args) != 2 or not out:
        print(__doc__)
        return 2
    tipo, spec = args
    try:
        ach, escritos = gerar(spec, tipo, out, rascunho)
    except (Recusa, regulado.Recusa) as e:
        print(f"RECUSADO: {e}")
        return 1
    for a in ach:
        print(f"  - {a}")
    for p in escritos:
        print(f"gerado: {p}")
    print("-" * 50)
    print("RESULTADO:", ("RASCUNHO gerado com lacunas" if rascunho else f"FAIL ({len(ach)}) — nada gravado")
          if ach else "PASS")
    return 1 if (ach and not rascunho) else 0
