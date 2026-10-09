#!/usr/bin/env python3
"""conhecimento.py — verificador da biblioteca de conhecimento reutilizável (B3e + DB1, ADR-120).

A biblioteca guarda, por empresa, o que um trabalho já descobriu e outro não deve refazer: termo (dicionário
semântico com relações), consulta, fato medido, pesquisa e runbook. O MODELO e o MÉTODO são deste framework
(`exemplos/conhecimento/_modelo/`); o CONTEÚDO de cada empresa é das sessões de domínio. A busca é a do
`knowledge_catalog --recall` (uma entrada só), que lê as entradas por `carregar_entradas`.

Estrutura (fora dela = achado):
    <raiz>/conhecimento.json                          prazos de validade e versão atual de cada sistema
    <raiz>/INDICE-PROJETOS.md                         uma linha por projeto
    <raiz>/perfis/<perfil>/DICIONARIO.md              termos do perfil regulado
    <raiz>/assuntos/<assunto>/DICIONARIO.md           termos de saber puro de assunto, sem dado de empresa
    <raiz>/assuntos/<assunto>/<tema>.md               consultas, fatos, pesquisas, runbooks de assunto
    <raiz>/empresas/<empresa>/DICIONARIO.md           termos da empresa (+ entrada `## Identificadores`)
    <raiz>/empresas/<empresa>/<area>/<assunto>.md     consultas, fatos, pesquisas, runbooks
Termo de projeto mora no projeto; o índice aponta para ele.

Isolamento entre empresas (regra do dono, 27/09/2026): o conhecimento de uma empresa nunca aparece no trabalho de
outra. Com `--empresa <e>`, só `empresas/<e>/`, `assuntos/` e `perfis/` são lidos; `--empresa nenhuma` lê só
`assuntos/` e `perfis/`; `--empresa todas` é a manutenção da biblioteca inteira. Sem `--empresa`, a empresa sai do
`INDICE-PROJETOS.md` pelo diretório atual (projeto cujo Caminho o contém); sem resolução, o comando RECUSA.
Empresa aponta para assunto e perfil; assunto e perfil não apontam para empresa; empresa não aponta para outra.
Entrada em `assuntos/` com identificador de empresa reprova (padrões de cliente e identificadores das empresas).

Entrada = bloco `## <nome>` com campos `- **Campo:** valor` (formato no README do modelo).

Uso:
    python tools/conhecimento.py verificar [<raiz>] [--empresa <e>|nenhuma|todas] [--trabalhos <dir>] [--hoje dd/mm/aaaa]
    python tools/conhecimento.py vencidos  [<raiz>] [--empresa <e>|nenhuma|todas] [--hoje dd/mm/aaaa]
    python tools/conhecimento.py publicar  [<raiz>] --empresa <e>   # sha256 dos identificadores em assuntos/_identificadores/
    python tools/conhecimento.py contexto  [<raiz>] [--cwd <pasta>]  # empresa/projeto/biblioteca da pasta (boot)
    python tools/conhecimento.py encerramento [<raiz>] --desde dd/mm/aaaa [hh:mm] [--cwd <pasta>] [--declarar "<motivo>"]
contexto: EMPRESA | PRODUTO-PRÓPRIO (pasta do framework ou "sem_empresa" no conhecimento.json) → exit 0;
FORA-DO-ÍNDICE | AMBÍGUO | SEM-BIBLIOTECA → exit 1. encerramento: 0 registrado/declarado, 1 falta, 2 recusado.
`vencidos` também acusa entrada cuja **Fonte:** (arquivo local) mudou depois do **Verificado em:**.
Bibliotecas de empresa fora da raiz (repositório próprio): `conhecimento.json` → "bibliotecas": [<pasta>], com o
marcador `.conhecimento-empresa` (nome da empresa) na raiz da biblioteca da empresa.
Raiz padrão: docs/_private/conhecimento. Exit 1 com achado (verificar) ou com vencido (vencidos); 2 = recusado.
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ_PADRAO = os.path.join(ROOT, "docs", "_private", "conhecimento")

TIPOS = {"termo", "consulta", "fato", "pesquisa", "runbook", "identificadores"}
TODAS, NENHUMA = "todas", "nenhuma"
# Padrões de dado de cliente que não dependem de empresa (REQ-04): valem em qualquer máquina. Objeto de cliente:
# Z/Y + letra e mais 2 (ZMARA, ZMM001), Z/Y + dígito (Z1ABC) ou Z/Y + sublinhado (Z_MRP); só letras Z/Y ("YYYY") e
# palavras comuns em maiúsculas ficam fora — lista não exaustiva, limite declarado no ADR. Tipo de movimento só com
# rótulo ao lado (número de 3 dígitos solto é preço, página, quantidade). Caminho de usuário ignora o placeholder.
_PALAVRAS_ZY = r"ZERO|ZONA|ZONAS|ZONE|ZONES|ZOOM|YEAR|YEARS|YELLOW|YIELD|YOUR|YOUTUBE"
PADROES_DE_CLIENTE = [
    (re.compile(rf"\b(?![YZ]+\b)(?!(?:{_PALAVRAS_ZY})\b)[ZY](?:[A-Z][A-Z0-9_]{{2,29}}|[0-9][A-Z0-9_]*|_[A-Z0-9_]+)\b"),
     "objeto no namespace de cliente (Z*/Y*)"),
    (re.compile(r"\b(?:ZZ|YY)(?![YZ]*\b)[A-Z0-9_]{2,}\b"), "campo de cliente (ZZ*/YY*)"),
    (re.compile(r"(?i)\b(?:tipo(?:s)? de movimento|movimento|mov\.|bwart)\s*[:=]?\s*(?-i:9\d\d|[XYZ][A-Z0-9]{2})\b"),
     "tipo de movimento de cliente (9xx, X/Y/Z)"),
    (re.compile(r"(?i)\b[A-Z]:[\\/]Users[\\/](?!<)[^\\/\s]+[\\/]|(?:/home|/Users)/(?!<)[^/\s]+/"),
     "caminho de usuário ou de projeto"),
]
CLASSES = {"estrutura", "configuração", "regra de negócio", "conceito", "retrato"}
RELACOES = {"é um", "parte de", "regulado por", "medido por", "sinônimo de"}
COMUNS = {"Tipo", "Fonte", "Verificado em", "Confiança"}
OBRIGATORIOS = {
    "termo": {"Definição"},
    "consulta": {"Pergunta", "Sistema", "Versão"},
    "fato": {"Classe"},
    "pesquisa": {"Pergunta"},
    "runbook": {"Pergunta"},
    "identificadores": {"Valores"},
}
OPCIONAIS = {"Relações", "Campo", "Classe", "Sistema", "Versão", "Pergunta", "Evidência", "Aponta para",
             "Contestado em", "Definição", "Valores"}
PRAZO_PADRAO = {"configuração": 6, "regra de negócio": 12, "conceito": 12}
CLASSE_DO_TIPO = {"termo": "conceito", "consulta": "estrutura", "pesquisa": "conceito", "runbook": "configuração"}
# Nunca entram: credencial e documento de identificação de pessoa. Valor de negócio entra (repositório privado).
# Credencial = valor único após "chave:" ou "chave=", seguido só de fim de linha, comentário ou anotação entre
# parênteses ("senha: abc123", "api_key = XYZ # teste", "senha: abc (trocar)"); parâmetro de URL ("?token=...");
# cabeçalho de autorização ("Authorization: Bearer ..."). Prosa que descreve um campo ("o campo token: armazena o
# ID da sessão") não é credencial. Limite: segredo no meio de uma frase comum escapa (declarado no ADR-120).
_CHAVES = r"senha|password|passwd|pwd|token|secret|segredo|api[_-]?key|client[_-]?secret|access[_-]?token"
PROIBIDOS = [
    (re.compile(rf"(?im)\b({_CHAVES})\s*[:=]\s*[\"']?[^\s\"']+[\"']?\s*(\(.*\)|#.*|//.*)?\s*$"), "credencial"),
    (re.compile(rf"(?i)[?&]({_CHAVES})=[^\s&]+"), "credencial em URL"),
    (re.compile(r"(?i)\bauthorization\s*:\s*(bearer|basic)\s+\S+"), "credencial em cabeçalho de autorização"),
    (re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"), "documento de identificação (CPF)"),
]
_CAMPO = re.compile(r"^\s*[-*]\s*\*\*(?P<k>[^*]+?):\*\*\s*(?P<v>.*?)\s*$")
_DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
_CERCA = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def _data(v):
    """Primeira data de calendário válida no texto, ou None."""
    for d, m, a in _DATA.findall(str(v or "")):
        try:
            return datetime.date(int(a), int(m), int(d))
        except ValueError:
            pass
    return None


def _meses(desde, ate):
    return (ate.year - desde.year) * 12 + (ate.month - desde.month) - (ate.day < desde.day)


def _blocos(texto):
    """([linhas antes do 1º `## `], [(nome, [linhas])]) fora de bloco de código. Cerca aberta até o fim = erro."""
    preambulo, blocos, atual, aberta = [], [], None, None
    for ln in texto.splitlines():
        m = _CERCA.match(ln)
        if m:
            aberta = None if aberta == m.group(1)[0] else (aberta or m.group(1)[0])
        elif aberta is None and ln.startswith("## "):
            atual = (ln[3:].strip(), [])
            blocos.append(atual)
            continue
        (atual[1] if atual is not None else preambulo).append(ln)
    if aberta is not None:
        raise ValueError("bloco de código aberto e nunca fechado")
    return preambulo, blocos


def _ler_entradas(caminho, rel):
    """Entradas de um arquivo. Devolve (entradas, achados)."""
    ach, ents = [], []
    try:
        texto = open(caminho, encoding="utf-8-sig").read()
    except OSError as e:
        return [], [f"{rel}: ilegível ({e})"]
    try:
        preambulo, blocos = _blocos(texto)
    except ValueError as e:
        return [], [f"{rel}: {e}"]
    if any(_CAMPO.match(ln) for ln in preambulo):
        ach.append(f"{rel}: campos antes do primeiro `## <nome>` — entrada sem título, ficaria fora da biblioteca")
    for nome, linhas in blocos:
        campos, tem_codigo, aberta, no_corpo = {}, False, None, False
        for ln in linhas:
            cerca = _CERCA.match(ln)
            if cerca:
                tem_codigo = True  # código faz parte da entrada (consulta); campo depois dele é legítimo
                aberta = None if aberta == cerca.group(1)[0] else (aberta or cerca.group(1)[0])
                continue
            if aberta:
                continue  # dentro do bloco de código: texto da consulta, não campo
            m = _CAMPO.match(ln)
            if m and no_corpo:
                # campo depois de PROSA é outra entrada sem `## ` (ex.: `###`); depois de código, não
                ach.append(f"{rel} · {nome}: campo **{m.group('k').strip()}:** depois do corpo — "
                           f"parece outra entrada sem `## <nome>`")
                continue
            if m:
                k = m.group("k").strip()
                if k in campos:
                    ach.append(f"{rel} · {nome}: campo **{k}:** repetido")
                campos[k] = m.group("v")
            elif ln.strip():
                no_corpo = True
        ents.append({"nome": nome, "campos": campos, "arquivo": rel, "corpo": "\n".join(linhas),
                     "_tem_codigo": tem_codigo})
    return ents, ach


def _validar_entrada(e, nivel):
    """Achados de uma entrada, pelas regras do tipo. `nivel` = 'dicionario' ou 'assunto'."""
    c, onde, ach = e["campos"], f"{e['arquivo']} · {e['nome']}", []
    tipo = c.get("Tipo", "").strip().lower()
    if not tipo:
        return [f"{onde}: formato não reconhecido (sem **Tipo:**)"]
    if tipo not in TIPOS:
        return [f"{onde}: tipo '{tipo}' desconhecido (use {', '.join(sorted(TIPOS))})"]
    if tipo == "identificadores" and not (nivel == "dicionario" and e.get("escopo", "").startswith("empresas/")):
        ach.append(f"{onde}: **Tipo:** identificadores só mora no DICIONARIO.md de uma empresa")
    elif tipo == "identificadores":
        curtos = [v.strip() for v in re.split(r"\s*[;,]\s*", c.get("Valores", "")) if v.strip()
                  and not _identificador_util(v)]
        if curtos:
            ach.append(f"{onde}: **Valores:** curtos demais para identificar a empresa ({', '.join(curtos)}): use 4+ "
                       f"caracteres ou com dígito — sigla de módulo reprovaria saber puro de assunto")
    elif nivel == "dicionario" and tipo not in ("termo", "identificadores"):
        ach.append(f"{onde}: só termo mora no DICIONARIO.md")
    if nivel == "assunto" and tipo == "termo":
        ach.append(f"{onde}: termo mora no DICIONARIO.md do nível dele, não em arquivo de assunto")
    for k in sorted((COMUNS | OBRIGATORIOS[tipo]) - set(c)):
        ach.append(f"{onde}: falta **{k}:**")
    for k in sorted(set(c) - COMUNS - OPCIONAIS):
        ach.append(f"{onde}: campo **{k}:** não reconhecido")
    for k, v in c.items():
        if not v.strip() or re.fullmatch(r"<[^>]*>", v.strip()):
            ach.append(f"{onde}: **{k}:** vazio ou placeholder")
    if "Verificado em" in c:
        d = _data(c["Verificado em"])
        if d is None:
            ach.append(f"{onde}: **Verificado em:** sem data válida dd/mm/aaaa")
    conf = c.get("Confiança", "").strip()
    if conf and not re.match(r"(?i)^(CONFIRMADO\s+por\s+\S|INFERIDO\b|REFUTADO\b)", conf):
        ach.append(f"{onde}: **Confiança:** use 'CONFIRMADO por <quem>', 'INFERIDO' ou 'REFUTADO'")
    classe = c.get("Classe", "").strip().lower()
    if classe and classe not in CLASSES:
        ach.append(f"{onde}: classe '{classe}' desconhecida (use {', '.join(sorted(CLASSES))})")
    if (classe or CLASSE_DO_TIPO.get(tipo)) == "estrutura" and not (c.get("Sistema") and c.get("Versão")):
        ach.append(f"{onde}: classe estrutura exige **Sistema:** e **Versão:**")
    if "Contestado em" in c and _data(c["Contestado em"]) is None:
        ach.append(f"{onde}: **Contestado em:** sem data válida")
    if tipo == "consulta" and not e["_tem_codigo"]:
        ach.append(f"{onde}: consulta sem bloco de código com o texto pronto")
    return ach


def _relacoes(v):
    """[(relação, alvo)] de 'é um: A; parte de: B, C'."""
    pares = []
    for parte in re.split(r"\s*;\s*", v or ""):
        if not parte.strip():
            continue
        if ":" not in parte:
            pares.append((parte.strip(), None))
            continue
        rel, alvos = parte.split(":", 1)
        for alvo in re.split(r"\s*,\s*", alvos.strip()):
            if alvo:
                pares.append((rel.strip().lower(), alvo.strip()))
    return pares


def _expandir(v):
    """`~\\pasta` ou `~/pasta` → pasta do usuário desta máquina (o índice guarda caminhos com `~`, emenda 3).
    Aceita as duas barras em qualquer sistema; o resto do texto fica como está."""
    v = v.strip().strip("`")
    if re.match(r"^~(?:[\\/]|$)", v):
        partes = [p for p in re.split(r"[\\/]+", v[1:]) if p]
        return os.path.join(os.path.expanduser("~"), *partes)
    return v


def _nome_repo(v):
    """Último trecho de um caminho ou nome de repositório, com `\\` ou `/` em qualquer sistema (no Linux,
    `os.path.basename` não separa pela barra invertida e o caminho Windows inteiro virava o nome)."""
    limpo = re.sub(r"^[`\s/\\]+|[`\s/\\]+$", "", str(v or ""))  # mesmo strip("`/\\ ") de antes, nas duas pontas
    partes = [p for p in re.split(r"[\\/]+", limpo) if p]
    return partes[-1].lower() if partes else ""


def _caminho_existe(v, raiz):
    v = _expandir(v)
    alvo = v if os.path.isabs(v) or re.match(r"^[A-Za-z]:[\\/]", v) else os.path.join(raiz, v)
    return os.path.exists(alvo)


class Recusa(Exception):
    """Empresa não informada nem resolvida pelo índice: o comando não lê nada (falha fechada)."""


MARCADOR = ".conhecimento-empresa"  # 1ª linha = nome da empresa; marca a raiz da biblioteca de uma empresa


def _cfg_raiz(raiz):
    try:
        return json.load(open(os.path.join(raiz, "conhecimento.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def bibliotecas_externas(raiz):
    """{empresa: pasta} das bibliotecas de empresa FORA da raiz (repositório próprio, D1 — emenda 2 do ADR-120).
    `conhecimento.json` → `"bibliotecas": [<pasta relativa à raiz ou absoluta>, ...]`; em cada pasta vale o marcador
    `.conhecimento-empresa` na própria pasta ou em `empresas/<e>/`. Pasta ausente (outra máquina) é ignorada."""
    out = {}
    for item in _cfg_raiz(raiz).get("bibliotecas") or []:
        base = item if os.path.isabs(item) else os.path.normpath(os.path.join(raiz, item))
        cands = [base] + ([os.path.join(base, "empresas", d) for d in sorted(os.listdir(os.path.join(base, "empresas")))]
                          if os.path.isdir(os.path.join(base, "empresas")) else [])
        for d in cands:
            m = os.path.join(d, MARCADOR)
            if os.path.isfile(m):
                with open(m, encoding="utf-8-sig") as fh:
                    texto = fh.read().strip()
                nome = texto.splitlines()[0].strip().lower() if texto else ""
                if re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", nome):
                    out.setdefault(nome, d)
    return out


def dir_empresa(raiz, empresa):
    return bibliotecas_externas(raiz).get(empresa) or os.path.join(raiz, "empresas", empresa)


def _arquivos(raiz, empresa=None, exts=(".md",)):
    """(caminho, rel virtual 'empresas/<e>/...', base) de todo arquivo da biblioteca no recorte. A biblioteca externa
    de uma empresa aparece como se estivesse em `empresas/<e>/`. Arquivo de empresa fora do recorte não é listado."""
    externas = bibliotecas_externas(raiz)
    fontes = [(raiz, "")] + [(d, f"empresas/{e}/") for e, d in sorted(externas.items())]
    for base, prefixo in fontes:
        if prefixo and not _visivel(prefixo.rstrip("/"), empresa):
            continue
        for pasta, dirs, arquivos in os.walk(base):
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            for nome in sorted(arquivos):
                if not nome.lower().endswith(exts):
                    continue
                rel = prefixo + os.path.relpath(os.path.join(pasta, nome), base).replace("\\", "/")
                partes = rel.split("/")
                if not prefixo and partes[0] == "empresas" and len(partes) >= 2 and partes[1].lower() in externas:
                    continue  # a biblioteca externa da empresa prevalece sobre uma cópia antiga na raiz
                if len(partes) >= 2 and partes[0] == "empresas" and not _visivel(f"empresas/{partes[1].lower()}", empresa):
                    continue
                yield os.path.join(pasta, nome), rel, base


def empresas_presentes(raiz):
    p = os.path.join(raiz, "empresas")
    locais = {d for d in os.listdir(p) if os.path.isdir(os.path.join(p, d))} if os.path.isdir(p) else set()
    return sorted(locais | set(bibliotecas_externas(raiz)))


def _visivel(escopo, empresa):
    """Escopo 'empresas/x', 'assuntos/y' ou 'perfis/z' é lido no recorte `empresa`?"""
    if empresa in (None, TODAS) or not escopo.startswith("empresas/"):
        return True
    return empresa != NENHUMA and escopo == f"empresas/{empresa}"


def _norm_caminho(p):
    return os.path.normcase(os.path.normpath(os.path.abspath(_expandir(p))))


def linhas_indice(raiz):
    """Linhas dos INDICE-PROJETOS.md (raiz + o de cada biblioteca externa de empresa presente na máquina)."""
    arquivos = [os.path.join(raiz, "INDICE-PROJETOS.md")] + \
        [os.path.join(d, "INDICE-PROJETOS.md") for d in bibliotecas_externas(raiz).values()]
    out, ach = [], []
    for p in arquivos:
        if os.path.isfile(p):
            o, a = _linhas_de_um_indice(p)
            out += o
            ach += a
    return out, ach


def _linhas_de_um_indice(p):
    out, ach = [], []
    for ln in open(p, encoding="utf-8-sig").read().splitlines():
        s = ln.strip()
        if not s.startswith("|") or set(s) <= set("|-: "):
            continue
        cel = [c.strip() for c in s.strip("|").split("|")]
        if [c.lower() for c in cel] == COLS_INDICE:
            continue
        if len(cel) != len(COLS_INDICE):
            ach.append(f"INDICE-PROJETOS.md: linha com {len(cel)} colunas, o modelo tem {len(COLS_INDICE)}: {s[:60]}")
            continue
        out.append(dict(zip(COLS_INDICE, cel)))
    return out, ach


def _projetos(raiz):
    """[(caminho normalizado, empresa, repositório)] dos projetos do índice com caminho."""
    out = []
    for linha in linhas_indice(raiz)[0]:
        v = linha["caminho"]
        if v and v not in ("—", "-"):
            out.append((_norm_caminho(v), linha["empresa"].strip().lower(),
                        _nome_repo(linha["repositório"])))
    return out


def _dentro(base, alvo):
    return alvo == base or alvo.startswith(base.rstrip(os.sep) + os.sep)


def _contem(base, alvo):
    """`alvo` está em `base`, na forma escrita ou com atalhos resolvidos (no macOS /var é atalho de /private/var).
    A forma resolvida só entra AQUI: o caminho guardado continua o escrito, que é o que o texto de `assuntos/` cita
    (com realpath em `_norm_caminho`, unidade mapeada virava UNC e o detector de vazamento deixava de casar)."""
    if _dentro(base, alvo):
        return True
    real = lambda p: os.path.normcase(os.path.normpath(os.path.realpath(p)))  # noqa: E731
    return _dentro(real(base), real(alvo))


def projetos_da_pasta(raiz, cwd=None):
    """Linhas do índice do projeto mais específico cujo Caminho contém `cwd` ([] = fora do índice)."""
    alvo = _norm_caminho(cwd or os.getcwd())
    cands = [(len(_norm_caminho(ln["caminho"])), ln) for ln in linhas_indice(raiz)[0]
             if ln["caminho"] not in ("", "—", "-") and _contem(_norm_caminho(ln["caminho"]), alvo)]
    if not cands:
        return []
    maior = max(n for n, _ in cands)
    return [ln for n, ln in cands if n == maior]


def resolver_empresa(raiz, cwd=None):
    """(empresa, como) pelo projeto do índice cujo Caminho contém `cwd` (o mais específico). Levanta Recusa
    quando nenhum projeto contém o diretório ou quando dois de empresas diferentes empatam."""
    alvo = _norm_caminho(cwd or os.getcwd())
    linhas = projetos_da_pasta(raiz, alvo)
    if not linhas:
        raise Recusa(f"a empresa não foi informada e o diretório atual ({alvo}) não está no Caminho de nenhum projeto "
                     f"do INDICE-PROJETOS.md. Informe --empresa <empresa> (ou --empresa nenhuma, só assuntos e "
                     f"perfis). Nada foi lido.")
    topo = {ln["empresa"].strip().lower() for ln in linhas}
    if len(topo) > 1:
        raise Recusa(f"o diretório atual está em projetos de mais de uma empresa no índice; informe --empresa. "
                     f"Nada foi lido.")
    e = topo.pop()
    return e, f"resolvida pelo INDICE-PROJETOS.md a partir de {alvo}"


def escolher_empresa(raiz, empresa=None, cwd=None):
    """(empresa, como). `empresa` explícita vale como está (validada); senão, resolve pelo índice."""
    if empresa:
        e = empresa.strip().lower()
        if e not in (TODAS, NENHUMA) and not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", e):
            raise Recusa(f"--empresa '{empresa}' inválida")
        return e, "informada por --empresa"
    return resolver_empresa(raiz, cwd)


def carregar(raiz, empresa=None):
    """Lê a biblioteca no recorte `empresa` (None ou 'todas' = inteira). Devolve (config, entradas, achados).
    Arquivo de outra empresa não é aberto."""
    ach, ents = [], []
    cfg_path = os.path.join(raiz, "conhecimento.json")
    cfg = {}
    if not os.path.isfile(cfg_path):
        ach.append("falta conhecimento.json na raiz")
    else:
        try:
            cfg = json.load(open(cfg_path, encoding="utf-8"))
        except (OSError, ValueError) as e:
            ach.append(f"conhecimento.json inválido ({e})")
    if not os.path.isfile(os.path.join(raiz, "INDICE-PROJETOS.md")):
        ach.append("falta INDICE-PROJETOS.md na raiz")
    for caminho, rel, base in _arquivos(raiz, empresa):
        partes = rel.split("/")
        if rel in ("README.md", "INDICE-PROJETOS.md"):
            continue
        if len(partes) == 3 and partes[0] == "empresas" and partes[2] in ("README.md", "INDICE-PROJETOS.md"):
            continue  # README e índice da biblioteca da empresa (repositório próprio)
        if len(partes) == 3 and partes[0] in ("perfis", "empresas", "assuntos") and partes[2] == "DICIONARIO.md":
            nivel = "dicionario"
        elif len(partes) == 4 and partes[0] == "empresas" and partes[3] != "DICIONARIO.md":
            nivel = "assunto"
        elif len(partes) == 3 and partes[0] == "assuntos":
            nivel = "assunto"
        else:
            ach.append(f"{rel}: fora da estrutura (perfis/<p>/DICIONARIO.md, assuntos/<a>/DICIONARIO.md, "
                       f"assuntos/<a>/<tema>.md, empresas/<e>/DICIONARIO.md, empresas/<e>/<area>/<assunto>.md)")
            continue
        if partes[1] != partes[1].lower():
            ach.append(f"{rel}: pasta '{partes[1]}' com maiúscula — use minúsculas (o recorte por empresa compara "
                       f"em minúsculas)")
        lidas, a2 = _ler_entradas(caminho, rel)
        ach += a2
        for e in lidas:
            e["_base"] = base  # caminho relativo em Evidência/Aponta para é relativo à biblioteca de origem
            e["nivel"] = nivel
            e["escopo"] = f"{partes[0]}/{partes[1].lower()}"  # empresa sempre minúscula (--empresa também é)
        ents += lidas
    return cfg, ents, ach


def _termos_de_outras(raiz, empresa):
    """Nomes de termo (minúsculos) de empresas FORA do recorte — só para dizer que a relação cruza empresa.
    Nada delas é impresso."""
    nomes = set()
    if empresa in (None, TODAS):
        return nomes
    for outra in empresas_presentes(raiz):
        if _visivel(f"empresas/{outra}", empresa):
            continue
        p = os.path.join(dir_empresa(raiz, outra), "DICIONARIO.md")
        if os.path.isfile(p):
            for e in _ler_entradas(p, "")[0]:
                nomes.add(e["nome"].strip().lower())
    return nomes


def cfg_do_escopo(raiz, cfg, escopo):
    """Configuração que vale para uma entrada: a da raiz (assuntos e perfis) mais, para entrada de empresa, o
    `empresas/<e>/conhecimento.json` dela, que prevalece. Versão de sistema de uma empresa é dado dela."""
    if not escopo.startswith("empresas/"):
        return cfg
    p = os.path.join(dir_empresa(raiz, escopo.split("/", 1)[1]), "conhecimento.json")
    if not os.path.isfile(p):
        return cfg
    try:
        prop = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return cfg
    out = dict(cfg)
    for chave in ("versoes_atuais", "validade_meses"):
        out[chave] = dict(cfg.get(chave) or {}, **(prop.get(chave) or {}))
    return out


def _identificador_util(v):
    """Identificador que não vira falso positivo em saber puro: 4+ caracteres ou com dígito ("1001", "ZNAT").
    Sigla curta só de letras ("MM", "PP", "SD") é nome de módulo, não de empresa."""
    v = v.strip()
    return len(v) >= 4 or (len(v) >= 2 and any(ch.isdigit() for ch in v))


def _pode_apontar(de, para):
    """Empresa → própria, assunto, perfil. Assunto e perfil → assunto, perfil. Nunca empresa → outra empresa."""
    if para.startswith("empresas/"):
        return de == para
    return True


def identificadores_de_empresa(raiz):
    """{valor normalizado: empresa} — nome da pasta de cada empresa presente, **Valores:** da entrada
    `## Identificadores` do DICIONARIO.md dela, e caminho e repositório de cada projeto dela no índice."""
    out = {}
    for emp in empresas_presentes(raiz):
        out[emp.lower()] = emp
        p = os.path.join(dir_empresa(raiz, emp), "DICIONARIO.md")
        if os.path.isfile(p):
            for e in _ler_entradas(p, "")[0]:
                if e["campos"].get("Tipo", "").strip().lower() == "identificadores":
                    for v in re.split(r"\s*[;,]\s*", e["campos"].get("Valores", "")):
                        if _identificador_util(v):
                            out[v.strip().lower()] = emp
    for caminho, emp, repo in _projetos(raiz):
        out[caminho] = emp
        if repo:
            out[repo] = emp
    return out


# Identificadores publicados em hash (D2, emenda 2 do ADR-120): cada empresa publica em
# `assuntos/_identificadores/<id>.txt` o sha256 dos seus identificadores normalizados; a máquina que não tem a
# biblioteca daquela empresa ainda reprova o identificador dela em `assuntos/`, sem ver o texto claro.
DIR_HASHES = os.path.join("assuntos", "_identificadores")
_TOKEN = re.compile(r"[a-z0-9][a-z0-9_.\-]*[a-z0-9]|[a-z0-9]")


def _hash(v):
    return hashlib.sha256(("id:" + v.strip().lower()).encode("utf-8")).hexdigest()


def arquivo_hashes(raiz, empresa):
    nome = hashlib.sha256(("empresa:" + empresa).encode("utf-8")).hexdigest()[:16]
    return os.path.join(raiz, DIR_HASHES, f"{nome}.txt")


def hashes_esperados(raiz, empresa):
    """sha256 dos identificadores de `empresa` que cabem num texto (nome, **Valores:**, repositório; caminho não)."""
    return sorted({_hash(v) for v, e in identificadores_de_empresa(raiz).items()
                   if e == empresa and os.sep not in v and "/" not in v})


def publicar_identificadores(raiz, empresa):
    p = arquivo_hashes(raiz, empresa)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# sha256 de identificadores normalizados de uma empresa — gerado por `conhecimento.py publicar`; "
                 "não editar\n" + "\n".join(hashes_esperados(raiz, empresa)) + "\n")
    return p


def _ler_hashes(p):
    try:
        return {ln.strip() for ln in open(p, encoding="utf-8") if re.fullmatch(r"[0-9a-f]{64}", ln.strip())}
    except OSError:
        return set()


def hashes_de_ausentes(raiz):
    """Hashes publicados por empresas cuja biblioteca NÃO está nesta máquina (as presentes são checadas em claro)."""
    pasta = os.path.join(raiz, DIR_HASHES)
    presentes = {os.path.normcase(arquivo_hashes(raiz, e)) for e in empresas_presentes(raiz)}
    out = set()
    if os.path.isdir(pasta):
        for nome in os.listdir(pasta):
            p = os.path.join(pasta, nome)
            if nome.endswith(".txt") and os.path.normcase(p) not in presentes:
                out |= _ler_hashes(p)
    return out


def _tokens(texto):
    out = set()
    for t in _TOKEN.findall(texto.lower()):
        out.add(t)
        out.update(x for x in re.split(r"[.\-]", t) if x)
    return out


def mencao_de_outra_empresa(raiz, empresa):
    """Predicado texto -> bool: o texto cita empresa fora do recorte (nome, identificador em claro de empresa presente
    ou em hash de empresa ausente)? 'todas' nunca filtra. Usado pelo --recall nos relatórios de sessão (D3)."""
    if empresa in (None, TODAS):
        return lambda _t: False
    claros = {v for v, e in identificadores_de_empresa(raiz).items()
              if e != empresa and os.sep not in v and "/" not in v}
    claros |= {e for e in empresas_presentes(raiz) if e != empresa}
    claros |= {ln["empresa"].strip().lower() for ln in linhas_indice(raiz)[0]
               if ln["empresa"].strip().lower() not in ("", "—", "-", empresa)}
    ocultos = hashes_de_ausentes(raiz) - set(hashes_esperados(raiz, empresa))

    def cita(texto):
        toks = _tokens(texto or "")
        return bool(toks & claros) or any(_hash(t) in ocultos for t in toks)
    return cita


def verificar_assunto(texto, idents, empresa, ocultos=frozenset()):
    """Achados de identificador de empresa num texto de `assuntos/`. O valor só aparece na mensagem quando é da
    própria empresa do recorte (ou na manutenção 'todas'); senão sai a linha, sem o valor. `ocultos` = hashes de
    empresas ausentes da máquina."""
    ach = []
    for n, ln in enumerate(texto.splitlines(), 1):
        if ocultos and any(_hash(t) in ocultos for t in _tokens(ln)):
            ach.append(f"linha {n}: identificador de empresa (lista publicada em hash; valor omitido)")
        for rx, rotulo in PADROES_DE_CLIENTE:
            m = rx.search(ln)
            if m:
                ach.append(f"linha {n}: {rotulo} ('{m.group(0)}')")
        baixo = ln.lower()
        norm = os.path.normcase(ln)
        for valor, emp in idents.items():
            achou = (valor in norm) if (os.sep in valor or "/" in valor) else \
                re.search(rf"(?<![\w-]){re.escape(valor)}(?![\w-])", baixo)
            if achou:
                mostra = empresa in (None, TODAS) or emp == empresa
                ach.append(f"linha {n}: identificador de empresa" + (f" ('{valor}', {emp})" if mostra else
                                                                    " (de empresa fora do recorte; valor omitido)"))
    return ach


def verificar(raiz, trabalhos_dir=None, hoje=None, empresa=None):
    """Achados no recorte `empresa` (None ou 'todas' = biblioteca inteira)."""
    hoje = hoje or datetime.date.today()
    cfg, ents, ach = carregar(raiz, empresa)
    if empresa not in (None, TODAS, NENHUMA) and empresa not in empresas_presentes(raiz):
        # sem isto, verificar daria PASS sem ter lido nada (submódulo não inicializado nesta máquina)
        ach.append(f"biblioteca de {empresa} não encontrada nesta máquina (nem em empresas/{empresa} nem nas "
                   f"'bibliotecas' do conhecimento.json): nada da empresa foi verificado — inicialize o submódulo "
                   f"ou crie a biblioteca")
    termos = {}  # nome minúsculo -> [escopos que o definem]
    vistos = {}
    projetos = _projetos(raiz)
    for e in ents:
        ach += _validar_entrada(e, e["nivel"])
        d = _data(e["campos"].get("Verificado em"))
        if d and d > hoje:
            ach.append(f"{e['arquivo']} · {e['nome']}: **Verificado em:** no futuro")
        if e["campos"].get("Tipo", "").strip().lower() == "termo":
            chave = e["nome"].strip().lower()
            for antes in vistos.get(chave, []):
                if antes["escopo"] == e["escopo"]:
                    ach.append(f"termo '{e['nome']}' definido duas vezes em {e['escopo']}")
                elif antes["escopo"].split("/")[0] != e["escopo"].split("/")[0]:
                    # perfil × assunto × empresa; duas empresas com o mesmo termo NÃO é achado (cada uma o seu)
                    ach.append(f"termo '{e['nome']}' definido em dois níveis ({antes['escopo']} e {e['escopo']})")
            vistos.setdefault(chave, []).append(e)
            termos.setdefault(chave, []).append(e["escopo"])
        for k in ("Evidência", "Aponta para"):
            v = e["campos"].get(k)
            if not v or re.fullmatch(r"<[^>]*>", v.strip()):
                continue
            bruto = _expandir(v)  # `~\` também: senão o bloqueio de outra empresa seria pulado (emenda 4)
            alvo = _norm_caminho(bruto) if (os.path.isabs(bruto) or re.match(r"^[A-Za-z]:[\\/]", bruto)) else None
            dono = next((emp for c, emp, _r in projetos if alvo and _contem(c, alvo)), None)
            if dono and e["escopo"] != f"empresas/{dono}":
                ach.append(f"{e['arquivo']} · {e['nome']}: **{k}:** aponta para caminho de projeto de outra empresa "
                           f"ou de empresa a partir de {e['escopo'].split('/')[0]} — bloqueante (isolamento entre empresas)")
            elif not _caminho_existe(v, e.get("_base", raiz)):
                ach.append(f"{e['arquivo']} · {e['nome']}: **{k}:** aponta para caminho que não existe ({v.strip()})")
        tipo_estrutura = (e["campos"].get("Classe", "").strip().lower()
                          or CLASSE_DO_TIPO.get(e["campos"].get("Tipo", "").strip().lower())) == "estrutura"
        sist = e["campos"].get("Sistema", "").strip()
        if tipo_estrutura and sist and sist not in (cfg_do_escopo(raiz, cfg, e["escopo"]).get("versoes_atuais") or {}):
            ach.append(f"{e['arquivo']} · {e['nome']}: versão atual do sistema '{sist}' não declarada em "
                       f"conhecimento.json (versoes_atuais) da raiz ou da empresa")
    outras = _termos_de_outras(raiz, empresa)
    for e in ents:
        for rel, alvo in _relacoes(e["campos"].get("Relações", "")):
            if rel not in RELACOES:
                ach.append(f"{e['arquivo']} · {e['nome']}: relação '{rel}' desconhecida (use {', '.join(sorted(RELACOES))})")
                continue
            if not alvo:
                continue
            escopos = termos.get(alvo.lower(), [])
            if any(_pode_apontar(e["escopo"], s) for s in escopos):
                continue
            if escopos or alvo.lower() in outras:
                ach.append(f"{e['arquivo']} · {e['nome']}: relação '{rel}' aponta para termo de empresa fora do escopo "
                           f"de {e['escopo']} — bloqueante (isolamento entre empresas)")
            else:
                ach.append(f"{e['arquivo']} · {e['nome']}: relação '{rel}' aponta para termo inexistente '{alvo}'")
    idents = identificadores_de_empresa(raiz)
    ocultos = hashes_de_ausentes(raiz)
    for base, _d, arquivos in os.walk(os.path.join(raiz, "assuntos")):
        for nome in sorted(arquivos):
            if nome.lower().endswith(".md"):
                p = os.path.join(base, nome)
                rel_p = os.path.relpath(p, raiz).replace("\\", "/")
                for a in verificar_assunto(open(p, encoding="utf-8-sig", errors="replace").read(), idents, empresa,
                                           ocultos):
                    ach.append(f"{rel_p}: {a} — assunto não guarda dado de empresa (bloqueante)")
    alvo_pub = [] if empresa == NENHUMA else ([empresa] if empresa not in (None, TODAS) else empresas_presentes(raiz))
    for emp in alvo_pub:
        if emp in empresas_presentes(raiz) and _ler_hashes(arquivo_hashes(raiz, emp)) != set(hashes_esperados(raiz, emp)):
            ach.append(f"identificadores de {emp} não publicados ou desatualizados em {DIR_HASHES}: rode "
                       f"`python tools/conhecimento.py publicar <raiz> --empresa {emp}`")
    ach += _verificar_indice(raiz, trabalhos_dir, empresa)
    for p, rel, _base in _arquivos(raiz, empresa, exts=(".md", ".json")):
        texto = open(p, encoding="utf-8-sig", errors="replace").read()
        for rx, rotulo in PROIBIDOS:
            if rx.search(texto):
                ach.append(f"{rel}: contém {rotulo} — nunca entra na biblioteca")
    return ach


# O próprio framework não é projeto do índice; o nome da pasta muda em worktree, o do repositório não.
FRAMEWORK_REPOS = {"metacognition-framework", os.path.basename(ROOT).lower()}
COLS_INDICE = ["projeto", "empresa", "perfil regulado", "caminho", "repositório", "estado", "especificação", "dicionário"]


def _verificar_indice(raiz, trabalhos_dir, empresa=None):
    """Caminhos conferidos só nas linhas da empresa do recorte: projeto de outra empresa mora em outra máquina e
    não reprova esta. A lista de repositórios (para os trabalhos abertos) usa todas as linhas."""
    if not os.path.isfile(os.path.join(raiz, "INDICE-PROJETOS.md")):
        return []
    linhas, ach = linhas_indice(raiz)
    repos = set()
    for linha in linhas:
        repos.add(_nome_repo(linha["repositório"]))
        if not _visivel(f"empresas/{linha['empresa'].strip().lower()}", empresa):
            continue
        for k in ("caminho", "especificação", "dicionário"):
            # especificação/dicionário aceitam vários caminhos separados por `;` (cada um é conferido)
            partes = [linha[k]] if k == "caminho" else re.split(r"\s*;\s*", linha[k])
            for v in partes:
                if v and v not in ("—", "-") and not _caminho_existe(v, raiz):
                    ach.append(f"INDICE-PROJETOS.md · {linha['projeto']}: {k} não existe ({v})")
    # Trabalho aberto sem linha no índice: o trabalho não diz a empresa e a mensagem traz o nome do repositório;
    # por isso só na manutenção da biblioteca inteira (sem recorte), nunca no recorte de uma empresa.
    if trabalhos_dir and os.path.isdir(trabalhos_dir) and empresa in (None, TODAS):
        for nome in sorted(os.listdir(trabalhos_dir)):
            if not nome.endswith(".md"):
                continue
            fm = open(os.path.join(trabalhos_dir, nome), encoding="utf-8", errors="replace").read()
            m_repo = re.search(r"(?m)^repo:\s*(.+)$", fm)
            m_st = re.search(r"(?m)^status:\s*(.+)$", fm)
            repo = _nome_repo(m_repo.group(1) if m_repo else "")
            if not repo or repo in FRAMEWORK_REPOS:
                continue  # trabalho do próprio framework não é projeto
            if m_st and m_st.group(1).strip().lower() != "aberto":
                continue
            if repo not in repos:
                ach.append(f"INDICE-PROJETOS.md: projeto '{repo}' tem trabalho aberto ({nome}) e não tem linha no índice")
    return ach


# caminho até vírgula, ponto e vírgula, crase ou fim; pode ter espaço ("OneDrive - X\spec.md, §2")
_CAMINHO_FONTE = re.compile(r"(?:~[\\/]|[A-Za-z]:[\\/])[^,;`\n]+")


def _arquivo_citado(bruto):
    """Arquivo local citado no trecho: tenta o trecho inteiro e vai tirando palavras do fim ("regra.md linha 12",
    "spec.md."); None se nada existir nesta máquina."""
    partes = bruto.strip().split(" ")
    while partes:
        caminho = _expandir(" ".join(partes).rstrip(".):"))
        if os.path.isfile(caminho):
            return caminho
        partes.pop()
    return None


def data_da_fonte(caminho):
    """Data da última mudança de um arquivo: último commit (git); com edição não commitada ou fora do git, a data
    de modificação."""
    pasta, nome = os.path.dirname(caminho), os.path.basename(caminho)
    rc, st = _git(pasta, "status", "--porcelain", "--", nome)
    rc_log, s = _git(pasta, "log", "-1", "--format=%cs", "--", nome)
    if rc == 0 and not st and rc_log == 0 and s:
        try:
            return datetime.date.fromisoformat(s)
        except ValueError:
            pass
    return datetime.date.fromtimestamp(os.path.getmtime(caminho))


def _fonte_alterada(c, verificado, data_fonte, cache):
    """Primeiro arquivo local citado em **Fonte:** que mudou depois de `verificado`: (caminho, data) ou None.
    Regra superada no projeto sem a biblioteca saber (caso de 03/10/2026, emenda 3)."""
    trechos = [t for b in _CAMINHO_FONTE.findall(c.get("Fonte", "")) for t in re.split(r"\s+(?:e|ou)\s+", b)]
    for bruto in trechos:  # "~\a.md e ~\b.md": cada arquivo é conferido
        caminho = _arquivo_citado(bruto)
        if not caminho:
            continue
        if caminho not in cache:
            cache[caminho] = data_fonte(caminho)
        if cache[caminho] and cache[caminho] > verificado:
            return bruto, cache[caminho]
    return None


def vencidos(raiz, hoje=None, empresa=None, data_fonte=data_da_fonte):
    """[(entrada, motivo)] a reverificar: contestada, versão do sistema mudou, prazo da classe vencido, ou arquivo
    citado em **Fonte:** alterado depois do **Verificado em:**. `data_fonte` é injetável para teste."""
    hoje = hoje or datetime.date.today()
    cfg0, ents, _ = carregar(raiz, empresa)
    out, cache = [], {}
    for e in ents:
        cfg = cfg_do_escopo(raiz, cfg0, e["escopo"])
        prazos = dict(PRAZO_PADRAO, **(cfg.get("validade_meses") or {}))
        versoes = cfg.get("versoes_atuais") or {}
        c = e["campos"]
        if "Contestado em" in c:
            out.append((e, f"contestado em {c['Contestado em'].strip()}"))
            continue
        classe = c.get("Classe", "").strip().lower() or CLASSE_DO_TIPO.get(c.get("Tipo", "").strip().lower(), "")
        # retrato não tem prazo em `prazos`: histórico datado, não vence, é citado com a data
        if classe == "estrutura":
            atual = versoes.get(c.get("Sistema", "").strip())
            if atual is not None and c.get("Versão", "").strip() != str(atual):
                out.append((e, f"versão do sistema mudou ({c.get('Versão', '').strip()} → {atual})"))
            continue
        d = _data(c.get("Verificado em"))
        if d and classe in prazos and _meses(d, hoje) >= prazos[classe]:
            out.append((e, f"{classe}: verificado há {_meses(d, hoje)} meses (prazo {prazos[classe]})"))
            continue
        alterada = _fonte_alterada(c, d, data_fonte, cache) if d and classe != "retrato" else None
        if alterada:
            out.append((e, f"fonte alterada em {alterada[1]:%d/%m/%Y}, depois da verificação de {d:%d/%m/%Y} "
                           f"({alterada[0]})"))
    return out


def carregar_entradas(raiz=RAIZ_PADRAO, empresa=None):
    """Entradas do recorte `empresa` no formato do `knowledge_catalog.recall` (campo `_tokens_full`). Biblioteca
    ausente = []. A lista de identificadores não é conhecimento de busca: fica fora."""
    if not os.path.isdir(raiz):
        return []
    _cfg, ents, _ = carregar(raiz, empresa)
    ents = [e for e in ents if e["campos"].get("Tipo", "").strip().lower() != "identificadores"]
    for e in ents:
        e["_tokens_full"] = " ".join([e["nome"], *e["campos"].values(), e["corpo"]])
    return ents


def rotulo(e):
    """Linha de resultado de busca. Retrato sai SEMPRE com a data: nunca é lido como valor atual."""
    c = e["campos"]
    classe = c.get("Classe", "").strip().lower()
    conteudo = [ln.strip() for ln in e["corpo"].splitlines()
                if ln.strip() and not _CAMPO.match(ln) and not _CERCA.match(ln)]
    texto = c.get("Definição") or c.get("Pergunta") or (conteudo[0] if conteudo else "")
    data = c.get("Verificado em", "").strip()
    prefixo = f"em {data}: " if classe == "retrato" else ""
    return f"- **{e['nome']}** ({c.get('Tipo', '?').strip()}, `{e['arquivo']}`) — {prefixo}{str(texto or '').strip()[:160]}"


# Contexto da pasta no boot e cobrança no encerramento (emenda 3 do ADR-120, pedido do dono de 04/10/2026).
EMPRESA, PROPRIO, FORA, AMBIGUO, SEM_BIBLIOTECA = "EMPRESA", "PRODUTO-PRÓPRIO", "FORA-DO-ÍNDICE", "AMBÍGUO", \
    "SEM-BIBLIOTECA"


def contexto(raiz, cwd=None, data_fonte=data_da_fonte):
    """Empresa, projeto e biblioteca da pasta `cwd`. Produto próprio = a pasta deste framework ou uma pasta de
    `conhecimento.json` → "sem_empresa" (declaração do dono). Devolve dict com `estado` e o que achou."""
    alvo = _norm_caminho(cwd or os.getcwd())
    proprios = [ROOT] + [_expandir(p) if os.path.isabs(_expandir(p)) else os.path.join(raiz, p)
                         for p in (_cfg_raiz(raiz).get("sem_empresa") or []) if str(p).strip()]
    # o índice vem antes: projeto de empresa sob a pasta do framework (worktree, raiz padrão) não vira produto próprio
    linhas = projetos_da_pasta(raiz, alvo) if os.path.isdir(raiz) else []
    if not linhas and any(_contem(_norm_caminho(p), alvo) for p in proprios):
        return {"estado": PROPRIO, "pasta": alvo}
    if not os.path.isdir(raiz):
        return {"estado": SEM_BIBLIOTECA, "pasta": alvo, "raiz": raiz}
    if not linhas:
        return {"estado": FORA, "pasta": alvo, "n_empresas": len(empresas_presentes(raiz)), "raiz": raiz}
    if len({ln["empresa"].strip().lower() for ln in linhas}) > 1:
        return {"estado": AMBIGUO, "pasta": alvo}
    ln = linhas[0]
    e = ln["empresa"].strip().lower()
    return {"estado": EMPRESA, "pasta": alvo, "empresa": e, "projeto": ln["projeto"],
            "especificação": ln["especificação"], "dicionário": ln["dicionário"],
            "biblioteca": dir_empresa(raiz, e), "a_reverificar": len(vencidos(raiz, empresa=e, data_fonte=data_fonte))}


def texto_contexto(ctx):
    """Uma linha para o boot. Fora do índice, diz o que fazer no 1º turno."""
    est = ctx["estado"]
    if est == EMPRESA:
        rev = f"; {ctx['a_reverificar']} entrada(s) a reverificar (conhecimento.py vencidos)" if ctx["a_reverificar"] else ""
        cmd = (f'python "{os.path.join(ROOT, "tools", "conhecimento.py")}" encerramento --cwd "{ctx["pasta"]}" '
               f'--desde "<dd/mm/aaaa hh:mm do início>"')
        return (f"empresa {ctx['empresa']} · projeto {ctx['projeto']} · especificação {ctx['especificação']} · "
                f"dicionário {ctx['dicionário']} · biblioteca {ctx['biblioteca']}{rev}. Ler antes de agir; ao "
                f"encerrar, registrar o conhecimento novo lá e provar: {cmd}")
    if est == PROPRIO:
        return f"produto próprio ({ctx['pasta']}): sem empresa; o conhecimento fica no próprio repositório."
    if est == FORA:
        # só a contagem: o nome de uma empresa não aparece no trabalho de outra (isolamento, emenda 1)
        return (f"{ctx['pasta']} não está no INDICE-PROJETOS de nenhuma empresa desta máquina "
                f"({ctx['n_empresas']} biblioteca(s) de empresa presentes). No 1º turno, pergunte ao dono a empresa e "
                f"acrescente a linha no INDICE-PROJETOS.md dela; se for produto próprio, declare a pasta em "
                f"{os.path.join(ctx['raiz'], 'conhecimento.json')} → \"sem_empresa\".")
    if est == AMBIGUO:
        return f"{ctx['pasta']} está em projetos de mais de uma empresa no índice: pergunte ao dono e corrija o índice."
    return f"biblioteca de conhecimento ausente ({ctx['raiz']}): empresa não resolvida."


def _git(pasta, *args):
    try:  # stdin fechado: git herdando a entrada de um processo em segundo plano chegou a travar (04/10/2026)
        p = subprocess.run(["git", *args], cwd=pasta, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return 1, str(e)
    return p.returncode, p.stdout.strip()


def encerramento(raiz, desde, cwd=None, declarar=None):
    """(código, linhas). 0 = conhecimento registrado (commit na biblioteca da empresa desde `desde`, sem pendência
    e sem push faltando) ou declarado; 1 = falta registro, commit ou push; 2 = empresa não resolvida."""
    ctx = contexto(raiz, cwd)
    if ctx["estado"] == PROPRIO:
        return 0, ["PASS: produto próprio — sem empresa; o conhecimento fica no próprio repositório."]
    if ctx["estado"] != EMPRESA:
        return 2, [f"RECUSADO: {texto_contexto(ctx)}"]
    lib, linhas = ctx["biblioteca"], [f"empresa: {ctx['empresa']} · biblioteca: {ctx['biblioteca']}"]
    rc, raiz_git = _git(lib, "rev-parse", "--show-toplevel") if os.path.isdir(lib) else (1, "")
    if rc != 0:
        return 1, linhas + ["FAIL: a biblioteca da empresa não é um repositório git nesta máquina — sem como provar o registro."]
    _rc, pend = _git(lib, "status", "--porcelain", "--", ".")
    if pend:
        return 1, linhas + ["FAIL: alterações não commitadas na biblioteca:"] + [f"  {x}" for x in pend.splitlines()[:10]]
    desde = desde if isinstance(desde, datetime.datetime) else datetime.datetime.combine(desde, datetime.time())
    _rc, commits = _git(lib, "log", f"--since={desde:%Y-%m-%d %H:%M}", "--format=%h %cs %s", "--", ".")
    rc, adiante = _git(lib, "rev-list", "--count", "@{u}..HEAD", "--", ".")  # só commits da biblioteca
    if commits and (rc != 0 or adiante != "0"):
        return 1, linhas + [f"FAIL: commit sem push na biblioteca ({adiante if rc == 0 else 'sem upstream'})."]
    if commits:
        return 0, linhas + [f"PASS: conhecimento registrado desde {desde:%d/%m/%Y}:"] + \
            [f"  {x}" for x in commits.splitlines()[:10]]
    if declarar and declarar.strip():
        return 0, linhas + [f"PASS: declarado — nada a registrar desde {desde:%d/%m/%Y}: {declarar.strip()}"]
    return 1, linhas + [f"FAIL: nenhum registro na biblioteca desde {desde:%d/%m/%Y}. Registre o conhecimento novo "
                        f"(commit + push) ou declare: --declarar \"<por que não há o que registrar>\"."]


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    args = [a for a in argv[1:]]
    if not args or args[0] not in ("verificar", "vencidos", "publicar", "contexto", "encerramento"):
        print(__doc__)
        return 2
    cmd, resto = args[0], args[1:]
    opts = {}
    for flag in ("--trabalhos", "--hoje", "--empresa", "--cwd", "--desde", "--declarar"):
        if flag in resto:
            i = resto.index(flag)
            if i + 1 >= len(resto):
                print(__doc__)
                return 2
            opts[flag] = resto[i + 1]
            del resto[i:i + 2]
            if flag == "--desde" and i < len(resto) and re.fullmatch(r"\d{1,2}:\d{2}", resto[i]):
                opts[flag] += " " + resto.pop(i)  # `--desde 04/10/2026 14:30` sem aspas
    raiz = resto[0] if resto else RAIZ_PADRAO
    hoje = _data(opts["--hoje"]) if "--hoje" in opts else None
    if "--hoje" in opts and hoje is None:
        print("RECUSADO: --hoje precisa de data dd/mm/aaaa")
        return 2
    if cmd == "contexto":
        ctx = contexto(raiz, opts.get("--cwd"))
        print(f"{ctx['estado']}: {texto_contexto(ctx)}")
        return 0 if ctx["estado"] in (EMPRESA, PROPRIO) else 1
    if cmd == "encerramento":
        desde = _data(opts.get("--desde"))
        if desde is None:
            print("RECUSADO: encerramento exige --desde dd/mm/aaaa [hh:mm] (início do trabalho)")
            return 2
        hm = re.search(r"\b(\d{1,2}):(\d{2})\b", opts["--desde"])
        if hm:
            if int(hm.group(1)) > 23 or int(hm.group(2)) > 59:
                print(f"RECUSADO: hora inválida em --desde ({hm.group(0)})")
                return 2
            desde = datetime.datetime.combine(desde, datetime.time(int(hm.group(1)), int(hm.group(2))))
        rc, linhas = encerramento(raiz, desde, opts.get("--cwd"), opts.get("--declarar"))
        print("\n".join(linhas))
        return rc
    if not os.path.isdir(raiz):
        print(f"RECUSADO: {raiz} não existe")
        return 2
    try:
        empresa, como = escolher_empresa(raiz, opts.get("--empresa"))
    except Recusa as e:
        print(f"RECUSADO: {e}")
        return 2
    print(f"empresa: {empresa} ({como})")
    if cmd == "publicar":
        if empresa in (TODAS, NENHUMA) or empresa not in empresas_presentes(raiz):
            print(f"RECUSADO: publicar exige a empresa cuja biblioteca está nesta máquina ({empresa})")
            return 2
        print(f"publicado: {publicar_identificadores(raiz, empresa)} ({len(hashes_esperados(raiz, empresa))} hashes)")
        return 0
    if cmd == "vencidos":
        itens = vencidos(raiz, hoje, empresa)
        for e, motivo in itens:
            print(f"  - {e['arquivo']} · {e['nome']}: {motivo}")
        print("-" * 50)
        print("RESULTADO:", f"{len(itens)} a reverificar" if itens else "nada vencido")
        return 1 if itens else 0
    ach = verificar(raiz, opts.get("--trabalhos"), hoje, empresa)
    for a in ach:
        print(f"  - {a}")
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({len(ach)})" if ach else "PASS (biblioteca consistente)")
    return 1 if ach else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
