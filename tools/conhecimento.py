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
    <raiz>/empresas/<empresa>/DICIONARIO.md           termos da empresa
    <raiz>/empresas/<empresa>/<area>/<assunto>.md     consultas, fatos, pesquisas, runbooks
Termo de projeto mora no projeto; o índice aponta para ele.

Entrada = bloco `## <nome>` com campos `- **Campo:** valor` (formato no README do modelo).

Uso:
    python tools/conhecimento.py verificar [<raiz>] [--trabalhos <dir>] [--hoje dd/mm/aaaa]
    python tools/conhecimento.py vencidos  [<raiz>] [--hoje dd/mm/aaaa]
Raiz padrão: docs/_private/conhecimento. Exit 1 com achado (verificar) ou com vencido (vencidos).
"""
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ_PADRAO = os.path.join(ROOT, "docs", "_private", "conhecimento")

TIPOS = {"termo", "consulta", "fato", "pesquisa", "runbook"}
CLASSES = {"estrutura", "configuração", "regra de negócio", "conceito", "retrato"}
RELACOES = {"é um", "parte de", "regulado por", "medido por", "sinônimo de"}
COMUNS = {"Tipo", "Fonte", "Verificado em", "Confiança"}
OBRIGATORIOS = {
    "termo": {"Definição"},
    "consulta": {"Pergunta", "Sistema", "Versão"},
    "fato": {"Classe"},
    "pesquisa": {"Pergunta"},
    "runbook": {"Pergunta"},
}
OPCIONAIS = {"Relações", "Campo", "Classe", "Sistema", "Versão", "Pergunta", "Evidência", "Aponta para",
             "Contestado em", "Definição"}
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
    if nivel == "dicionario" and tipo != "termo":
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


def _caminho_existe(v, raiz):
    v = v.strip().strip("`")
    alvo = v if os.path.isabs(v) or re.match(r"^[A-Za-z]:[\\/]", v) else os.path.join(raiz, v)
    return os.path.exists(alvo)


def carregar(raiz):
    """Lê a biblioteca inteira. Devolve (config, entradas, achados de estrutura)."""
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
    for base, _dirs, arquivos in os.walk(raiz):
        for nome in arquivos:
            if not nome.lower().endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(base, nome), raiz).replace("\\", "/")
            partes = rel.split("/")
            if rel in ("README.md", "INDICE-PROJETOS.md"):
                continue
            if len(partes) == 3 and partes[0] in ("perfis", "empresas") and partes[2] == "DICIONARIO.md":
                nivel = "dicionario"
            elif len(partes) == 4 and partes[0] == "empresas" and partes[3] != "DICIONARIO.md":
                nivel = "assunto"
            else:
                ach.append(f"{rel}: fora da estrutura (perfis/<p>/DICIONARIO.md, empresas/<e>/DICIONARIO.md, "
                           f"empresas/<e>/<area>/<assunto>.md)")
                continue
            lidas, a2 = _ler_entradas(os.path.join(base, nome), rel)
            ach += a2
            for e in lidas:
                e["nivel"] = nivel
                e["escopo"] = f"{partes[0]}/{partes[1]}"
            ents += lidas
    return cfg, ents, ach


def verificar(raiz, trabalhos_dir=None, hoje=None):
    hoje = hoje or datetime.date.today()
    cfg, ents, ach = carregar(raiz)
    termos = {}
    for e in ents:
        ach += _validar_entrada(e, e["nivel"])
        d = _data(e["campos"].get("Verificado em"))
        if d and d > hoje:
            ach.append(f"{e['arquivo']} · {e['nome']}: **Verificado em:** no futuro")
        if e["campos"].get("Tipo", "").strip().lower() == "termo":
            chave = e["nome"].strip().lower()
            if chave in termos:
                antes = termos[chave]
                if antes["escopo"] == e["escopo"]:
                    ach.append(f"termo '{e['nome']}' definido duas vezes em {e['escopo']}")
                elif antes["escopo"].split("/")[0] != e["escopo"].split("/")[0]:
                    ach.append(f"termo '{e['nome']}' definido em dois níveis ({antes['escopo']} e {e['escopo']})")
            termos.setdefault(chave, e)
        for k in ("Evidência", "Aponta para"):
            v = e["campos"].get(k)
            if v and not re.fullmatch(r"<[^>]*>", v.strip()) and not _caminho_existe(v, raiz):
                ach.append(f"{e['arquivo']} · {e['nome']}: **{k}:** aponta para caminho que não existe ({v.strip()})")
        tipo_estrutura = (e["campos"].get("Classe", "").strip().lower()
                          or CLASSE_DO_TIPO.get(e["campos"].get("Tipo", "").strip().lower())) == "estrutura"
        sist = e["campos"].get("Sistema", "").strip()
        if tipo_estrutura and sist and sist not in (cfg.get("versoes_atuais") or {}):
            ach.append(f"{e['arquivo']} · {e['nome']}: versão atual do sistema '{sist}' não declarada em "
                       f"conhecimento.json (versoes_atuais)")
    for e in ents:
        for rel, alvo in _relacoes(e["campos"].get("Relações", "")):
            if rel not in RELACOES:
                ach.append(f"{e['arquivo']} · {e['nome']}: relação '{rel}' desconhecida (use {', '.join(sorted(RELACOES))})")
            elif alvo and alvo.lower() not in termos:
                ach.append(f"{e['arquivo']} · {e['nome']}: relação '{rel}' aponta para termo inexistente '{alvo}'")
    ach += _verificar_indice(raiz, trabalhos_dir)
    for base, _d, arquivos in os.walk(raiz):
        for nome in arquivos:
            if nome.lower().endswith((".md", ".json")):
                p = os.path.join(base, nome)
                texto = open(p, encoding="utf-8-sig", errors="replace").read()
                for rx, rotulo in PROIBIDOS:
                    if rx.search(texto):
                        ach.append(f"{os.path.relpath(p, raiz)}: contém {rotulo} — nunca entra na biblioteca")
    return ach


# O próprio framework não é projeto do índice; o nome da pasta muda em worktree, o do repositório não.
FRAMEWORK_REPOS = {"metacognition-framework", os.path.basename(ROOT).lower()}
COLS_INDICE = ["projeto", "empresa", "perfil regulado", "caminho", "repositório", "estado", "especificação", "dicionário"]


def _verificar_indice(raiz, trabalhos_dir):
    p = os.path.join(raiz, "INDICE-PROJETOS.md")
    if not os.path.isfile(p):
        return []
    ach, repos = [], set()
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
        linha = dict(zip(COLS_INDICE, cel))
        repos.add(os.path.basename(linha["repositório"].strip("`/\\ ")).lower())
        for k in ("caminho", "especificação", "dicionário"):
            v = linha[k]
            if v and v not in ("—", "-") and not _caminho_existe(v, raiz):
                ach.append(f"INDICE-PROJETOS.md · {linha['projeto']}: {k} não existe ({v})")
    if trabalhos_dir and os.path.isdir(trabalhos_dir):
        for nome in sorted(os.listdir(trabalhos_dir)):
            if not nome.endswith(".md"):
                continue
            fm = open(os.path.join(trabalhos_dir, nome), encoding="utf-8", errors="replace").read()
            m_repo = re.search(r"(?m)^repo:\s*(.+)$", fm)
            m_st = re.search(r"(?m)^status:\s*(.+)$", fm)
            repo = os.path.basename((m_repo.group(1) if m_repo else "").strip().strip("/\\")).lower()
            if not repo or repo in FRAMEWORK_REPOS:
                continue  # trabalho do próprio framework não é projeto
            if m_st and m_st.group(1).strip().lower() != "aberto":
                continue
            if repo not in repos:
                ach.append(f"INDICE-PROJETOS.md: projeto '{repo}' tem trabalho aberto ({nome}) e não tem linha no índice")
    return ach


def vencidos(raiz, hoje=None):
    """[(entrada, motivo)] a reverificar: contestada, versão do sistema mudou, ou prazo da classe vencido."""
    hoje = hoje or datetime.date.today()
    cfg, ents, _ = carregar(raiz)
    prazos = dict(PRAZO_PADRAO, **(cfg.get("validade_meses") or {}))
    versoes = cfg.get("versoes_atuais") or {}
    out = []
    for e in ents:
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
    return out


def carregar_entradas(raiz=RAIZ_PADRAO):
    """Entradas no formato do `knowledge_catalog.recall` (campo `_tokens_full`). Biblioteca ausente = []."""
    if not os.path.isdir(raiz):
        return []
    _cfg, ents, _ = carregar(raiz)
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


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    args = [a for a in argv[1:]]
    if not args or args[0] not in ("verificar", "vencidos"):
        print(__doc__)
        return 2
    cmd, resto = args[0], args[1:]
    opts = {}
    for flag in ("--trabalhos", "--hoje"):
        if flag in resto:
            i = resto.index(flag)
            if i + 1 >= len(resto):
                print(__doc__)
                return 2
            opts[flag] = resto[i + 1]
            del resto[i:i + 2]
    raiz = resto[0] if resto else RAIZ_PADRAO
    hoje = _data(opts["--hoje"]) if "--hoje" in opts else None
    if "--hoje" in opts and hoje is None:
        print("RECUSADO: --hoje precisa de data dd/mm/aaaa")
        return 2
    if not os.path.isdir(raiz):
        print(f"RECUSADO: {raiz} não existe")
        return 2
    if cmd == "vencidos":
        itens = vencidos(raiz, hoje)
        for e, motivo in itens:
            print(f"  - {e['arquivo']} · {e['nome']}: {motivo}")
        print("-" * 50)
        print("RESULTADO:", f"{len(itens)} a reverificar" if itens else "nada vencido")
        return 1 if itens else 0
    ach = verificar(raiz, opts.get("--trabalhos"), hoje)
    for a in ach:
        print(f"  - {a}")
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({len(ach)})" if ach else "PASS (biblioteca consistente)")
    return 1 if ach else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
