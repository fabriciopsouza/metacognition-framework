#!/usr/bin/env python3
"""regulado.py — motor do kit regulado sobre o arquivo único de especificação (ADR-119).

Neutro: não conhece nenhuma norma. As regras (normas revogadas, peças por categoria de software,
testes obrigatórios, categoria padrão por sistema) vêm do PERFIL declarado no próprio projeto
(`**Perfil regulado:** <nome>`), em `exemplos/dominio-regulado/compliance-profile-<nome>.json`.
Sem perfil padrão (decisão do dono, 26/09/2026): sem impacto e perfil registrados, nada é liberado.

Campos da Parte A:  **Impacto regulado:** sim|não · **Perfil regulado:** <nome>|nenhum · **Sistema:** <nome>
                    **Categoria de software:** <categoria do perfil> · **Categoria decidida por:** <nome, dd/mm/aaaa — motivo>
                    **Requisitos confirmados por:** <nome, dd/mm/aaaa> · linhas `- REQ-nn: ...`
Parte F — Riscos:   | Risco | Requisito | Falha | Impacto | Probabilidade | Detecção | Classe | Mitigação | Teste |
Parte G — Testes e evidências:
                    | Teste | Requisito | Categoria | Roteiro | Esperado | Resultado | Evidência | Nome e data |

Uso:
    python tools/regulado.py verificar <spec.md>                  # liberação: tudo executado (exit 1 com achado)
    python tools/regulado.py verificar <spec.md> --planejamento   # durante o projeto: aceita teste não executado
    python tools/regulado.py matriz <spec.md>                     # requisito -> risco -> teste -> evidência (md)
    python tools/regulado.py kit <spec.md>                        # peças exigidas (exit 1 sem registro)
    python tools/regulado.py documento <tipo> <spec.md> --out-dir <pasta> [--rascunho]   # documento do perfil (ADR-124)
    python tools/regulado.py mapa <perfil.json>                   # toda peça do perfil tem artigo no mapa ao lado
"""
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_fonte  # noqa: E402

PERFIS_DIR = os.path.join(ROOT, "exemplos", "dominio-regulado")
# Camada privada (ADR-128): `**Empresa:** <e>` na Parte A soma ao perfil público o arquivo
# <biblioteca da empresa>/perfis/compliance-profile-<perfil>.json. A biblioteca é resolvida por conhecimento.py.
RAIZ_CONHECIMENTO = os.path.join(ROOT, "docs", "_private", "conhecimento")
KIT_COMUM_SEM_PERFIL = ["TAP", "especificacao", "HANDOFF", "glossario", "cronograma"]
COLS_RISCO = ["risco", "requisito", "falha", "impacto", "probabilidade", "detecção", "classe", "mitigação", "teste"]
COLS_TESTE = ["teste", "requisito", "categoria", "roteiro", "esperado", "resultado", "evidência", "nome e data"]
CLASSES = {"alto", "médio", "medio", "baixo"}
CAMPOS = ["Impacto regulado", "Perfil regulado", "Empresa", "Sistema", "Categoria de software",
          "Categoria decidida por", "Requisitos confirmados por"]
# Definição de requisito: "- REQ-01:", "* REQ-01:", "1. REQ-01 —", "- **REQ-01:**". Toda outra menção a
# REQ-nn na Parte A sem definição é acusada: formato desconhecido não pode sumir em silêncio.
_DEF_REQ = re.compile(r"(?m)^\s*(?:[-*+]|\d+[.)])?\s*(?:\*\*)?\s*(REQ-\d+)\s*(?:\*\*)?\s*[:—–-]")
_DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
_VAZIO = {"", "-", "—", "n/a", "pendente", "<pendente>"}
MARCAS_MAPA = {"CONFIRMADO", "INFERIDO", "DESCONHECIDO", "NÃO SE APLICA"}


class Recusa(Exception):
    """Falta o registro que decide se o kit regulado se aplica (impacto e perfil)."""


def _campo(texto, nome):
    # [ \t], nunca \s: com o valor vazio, \s atravessava a quebra de linha e devolvia a linha do campo seguinte
    m = re.search(rf"(?im)^[ \t]*[-*]?[ \t]*\*\*{re.escape(nome)}:\*\*[ \t]*(.*?)[ \t]*$", texto or "")
    return m.group(1).strip() if m else ""


def _valor(texto, nome):
    """Valor do campo sem o ' — motivo'. Placeholder ('sim | não', '<...>') não casa com valor válido."""
    return re.split(r"\s+[—–-]\s+", _campo(texto, nome))[0].strip()


def _vazio(v):
    return str(v or "").strip().lower() in _VAZIO


def _tem_data(v):
    for d, m, a in _DATA.findall(str(v or "")):
        try:
            datetime.date(int(a), int(m), int(d))
            return True
        except ValueError:
            pass
    return False


def _nome_e_data(v):
    """Assinatura mínima: data de calendário válida E um nome além dela."""
    return _tem_data(v) and bool(re.sub(_DATA, "", str(v or "")).strip(" ,;-—"))


def _tabela(texto, cols, prefixo):
    """Linhas da tabela cujo 1º campo é <prefixo>-nn, como dicts pelas colunas do modelo."""
    linhas, erros = [], []
    for ln in (texto or "").splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cel = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s.strip("|"))]
        if not re.fullmatch(rf"{prefixo}-\d+", cel[0]):
            continue
        if len(cel) != len(cols):
            erros.append(f"{cel[0]}: {len(cel)} colunas, o modelo tem {len(cols)}")
            continue
        linhas.append(dict(zip(cols, cel)))
    return linhas, erros


def _refs(v, prefixo):
    return set(re.findall(rf"\b{prefixo}-\d+\b", str(v or "")))


_METADADOS = {"profile", "note", "orgao", "wires_to"}  # descrevem o arquivo; não são exigência da norma


def _somar(base, extra, via=""):
    """(perfil somado, conflitos). A camada privada só ACRESCENTA: chave nova entra, dicionários somam por chave,
    listas se unem sem repetir. Nula, troca de tipo ou valor simples diferente do público é conflito e o público fica:
    a camada não pode enfraquecer a exigência da norma (null apagava os testes obrigatórios; QA do ADR-128)."""
    out, conflitos = dict(base), []
    for k, v in extra.items():
        nome, atual = f"{via}{k}", out.get(k)
        if k.startswith("_") or k in _METADADOS:
            continue  # descrição da camada, não exigência; `profile` já foi conferido em camada_privada
        if v is None:
            conflitos.append(f"{nome} nulo")
        elif k not in out:
            out[k] = v
        elif isinstance(v, dict) and isinstance(atual, dict):
            out[k], sub = _somar(atual, v, nome + ".")
            conflitos += sub
        elif isinstance(v, list) and isinstance(atual, list):
            out[k] = atual + [x for x in v if x not in atual]
        elif v != atual:
            conflitos.append(f"{nome} ({atual!r} -> {v!r})")
    return out, conflitos


def camada_privada(perfil_nome, empresa):
    """(camada ou None, caminho, erro ou None). Biblioteca da empresa ausente na máquina é erro: liberar sem os
    procedimentos internos seria falso PASS."""
    import conhecimento  # noqa: E402  (resolve biblioteca interna ou externa da empresa, ADR-120)
    d = conhecimento.dir_empresa(RAIZ_CONHECIMENTO, empresa)
    if not os.path.isdir(d):
        return None, d, (f"empresa '{empresa}' declarada, mas a biblioteca dela não está nesta máquina ({d}): "
                         f"a camada privada do perfil não foi lida")
    p = os.path.join(d, "perfis", f"compliance-profile-{perfil_nome.lower()}.json")
    if not os.path.isfile(p):
        return None, p, None
    try:
        with open(p, encoding="utf-8-sig") as fh:
            camada = json.load(fh)
    except ValueError as e:
        return None, p, f"camada privada ilegível ({p}): {e}"
    if not isinstance(camada, dict):
        return None, p, f"camada privada {p} não é um objeto JSON ({type(camada).__name__})"
    if str(camada.get("profile", perfil_nome)).lower() != perfil_nome.lower():
        return None, p, f"camada privada {p} é do perfil '{camada.get('profile')}', não de '{perfil_nome}'"
    return camada, p, None


def carregar(spec):
    """Tudo que os comandos usam, lido pelo leitor único (spec_fonte)."""
    req = spec_fonte.ler_parte(spec, "requisitos") or ""
    riscos, e1 = _tabela(spec_fonte.ler_parte(spec, "riscos"), COLS_RISCO, "RISCO")
    testes, e2 = _tabela(spec_fonte.ler_parte(spec, "testes"), COLS_TESTE, "TESTE")
    perfil_nome = _valor(req, "Perfil regulado")
    if perfil_nome and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", perfil_nome):
        perfil_nome = ""  # caminho, espaço ou placeholder não é nome de perfil = não registrado
    perfil = None
    if perfil_nome and perfil_nome.lower() != "nenhum":
        caminho = os.path.join(PERFIS_DIR, f"compliance-profile-{perfil_nome.lower()}.json")
        if os.path.isfile(caminho):
            with open(caminho, encoding="utf-8") as fh:
                perfil = json.load(fh)
    # Lista do que é ACEITO (redesenho após 3 rodadas de QA, ADR-128): vazio, placeholder na forma do modelo
    # (`<...>` ou `<...> | nenhuma`), 'nenhuma' ou nome da biblioteca. Todo o resto é achado — nunca some calado.
    # Valor INTEIRO: só o travessão (" — "/" – ") separa comentário. O hífen não: "acme - filial" viraria "acme" e a
    # camada de outra empresa entraria calada (rodada 4 do QA).
    empresa = re.split(r"\s+[—–]\s+", _campo(req, "Empresa"))[0].strip().lower()
    camada, camada_path, erro_camada = None, "", None
    if re.fullmatch(r"<[^<>|]*>(\s*\|\s*nenhuma)?", empresa):
        empresa = ""  # modelo não preenchido = empresa não declarada (o campo é opcional)
    elif empresa and not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", empresa):
        erro_camada = (f"**Empresa:** '{empresa}' fora do formato da biblioteca (minúsculas, dígitos, _ . -): "
                       f"a camada privada não foi lida")
        empresa = ""
    if perfil is not None and empresa and empresa != "nenhuma":
        camada, camada_path, erro_camada = camada_privada(perfil_nome, empresa)
        if camada:
            perfil, conflitos = _somar(perfil, camada)
            if conflitos:
                erro_camada = (f"camada privada {camada_path} tenta alterar ou remover exigência do perfil público "
                               f"(só pode acrescentar): {'; '.join(conflitos)}")
    duplicados = [c for c in CAMPOS if len(re.findall(
        rf"(?im)^\s*[-*]?\s*\*\*{re.escape(c)}:\*\*", req)) > 1]
    return {
        "texto": open(spec, encoding="utf-8-sig").read(),
        "reqs": _DEF_REQ.findall(req),
        "reqs_citados": set(re.findall(r"\bREQ-\d+\b", req)),
        "duplicados": duplicados,
        "impacto": _valor(req, "Impacto regulado").lower(),
        "perfil_nome": perfil_nome, "perfil": perfil,
        "empresa": empresa, "camada_privada": camada_path if camada else "", "erro_camada": erro_camada,
        "categoria": _valor(req, "Categoria de software"),
        "sistema": _campo(req, "Sistema"),
        "decidida_por": _campo(req, "Categoria decidida por"),
        "confirmados_por": _campo(req, "Requisitos confirmados por"),
        "riscos": riscos, "testes": testes, "erros_tabela": e1 + e2,
    }


def registro(d):
    """Achados do registro de enquadramento. Vazio = o projeto disse se o kit regulado se aplica e sob
    qual perfil. Sem isso nenhum comando libera nada (critério 6 do plano B3)."""
    ach = [f"campo **{c}:** aparece mais de uma vez — deixe só a resposta" for c in d["duplicados"]]
    if d["impacto"] not in ("sim", "não", "nao"):
        ach.append("impacto regulado não registrado (campo **Impacto regulado:** sim|não)")
    if not d["perfil_nome"]:
        ach.append("perfil regulado não registrado (campo **Perfil regulado:** <nome>|nenhum) — não há perfil padrão")
    elif d["perfil_nome"].lower() != "nenhum" and d["perfil"] is None:
        ach.append(f"perfil '{d['perfil_nome']}' sem arquivo compliance-profile-{d['perfil_nome'].lower()}.json")
    if d["impacto"] == "sim" and d["perfil_nome"].lower() == "nenhum":
        ach.append("projeto com impacto regulado declarado sem perfil regulado")
    if d.get("erro_camada"):
        ach.append(d["erro_camada"])
    return ach


def duplicados_reqs(reqs):
    """REQs definidos mais de uma vez (regra única, usada também pelos documentos do perfil)."""
    return sorted({r for r in reqs if reqs.count(r) > 1})


def verificar(spec, planejamento=False):
    d = carregar(spec)
    ach = registro(d)
    if ach or d["impacto"] != "sim":
        return ach  # sem impacto regulado registrado, o kit regulado não se aplica
    ach += d["erros_tabela"]
    if not d["reqs"]:
        ach.append("nenhum requisito numerado na Parte A (formato `- REQ-01: ...`)")
    for r in sorted(d["reqs_citados"] - set(d["reqs"])):
        ach.append(f"{r} citado na Parte A sem linha de definição (`- {r}: ...`)")
    for r in duplicados_reqs(d["reqs"]):
        ach.append(f"{r} definido mais de uma vez na Parte A")
    if not d["riscos"]:
        ach.append("Parte F sem risco registrado")
    if not d["testes"]:
        ach.append("Parte G sem teste registrado")
    perfil = d["perfil"]
    cats = perfil.get("categorias_software") or {}
    if d["categoria"] not in [k for k in cats if not k.startswith("_") and k != "kit_comum"]:
        ach.append(f"categoria de software '{d['categoria']}' ausente ou fora do perfil")
    for sist, padrao in (perfil.get("categoria_padrao_por_sistema") or {}).items():
        if sist.lower() in d["sistema"].lower() and d["categoria"] and d["categoria"] != padrao:
            if not _nome_e_data(d["decidida_por"]):
                ach.append(f"sistema {sist} com categoria {d['categoria']} (padrão {padrao}) sem registro "
                           f"de quem decidiu e quando (**Categoria decidida por:**)")
    if not planejamento and not _nome_e_data(d["confirmados_por"]):
        ach.append("confirmação dos requisitos sem nome e data (**Requisitos confirmados por:**)")
    reqs = set(d["reqs"])
    ids_teste = {t["teste"] for t in d["testes"]}
    testados = set().union(*[_refs(t["requisito"], "REQ") for t in d["testes"]]) if d["testes"] else set()
    for r in sorted(reqs - testados):
        ach.append(f"{r} sem teste")
    for x in d["riscos"] + d["testes"]:
        for r in sorted(_refs(x["requisito"], "REQ") - reqs):
            ach.append(f"{x.get('risco') or x.get('teste')} aponta para {r}, que não existe na Parte A")
    for r in d["riscos"]:
        classe = r["classe"].strip().lower()
        if classe not in CLASSES:
            ach.append(f"{r['risco']} com classe '{r['classe']}' — use alto, médio ou baixo")
        refs = _refs(r["teste"], "TESTE")
        for t in sorted(refs - ids_teste):
            ach.append(f"{r['risco']} aponta para {t}, que não existe na Parte G")
        if classe == "alto":
            if _vazio(r["mitigação"]):
                ach.append(f"{r['risco']} (alto) sem mitigação")
            if not refs:
                ach.append(f"{r['risco']} (alto) sem teste")
    for t in d["testes"]:
        executado = not _vazio(t["resultado"])
        if not executado and not planejamento:
            ach.append(f"{t['teste']} sem resultado")
        if executado and _vazio(t["evidência"]):
            ach.append(f"{t['teste']} com resultado e sem evidência")
        if executado and not _nome_e_data(t["nome e data"]):
            ach.append(f"{t['teste']} com resultado sem nome e data de quem executou")
    cats_testadas = " | ".join(t["categoria"].lower() for t in d["testes"])
    for obrig in perfil.get("testes_obrigatorios_com_impacto") or []:
        if obrig.lower() not in cats_testadas:
            ach.append(f"categoria de teste obrigatória ausente: {obrig}")
    for ln in d["texto"].splitlines():
        if "revogad" in ln.lower():
            continue  # citação que declara a revogação é permitida
        for nr in perfil.get("normas_revogadas") or []:
            if re.search(nr["padrao"], ln, re.I):
                ach.append(f"cita norma revogada (usar {nr['substituida_por']}): {ln.strip()[:80]}")
    return ach


def kit(spec):
    d = carregar(spec)
    faltas = registro(d)
    if faltas:
        raise Recusa("; ".join(faltas))
    cats = (d["perfil"] or {}).get("categorias_software") or {}
    pecas = list(cats.get("kit_comum") or KIT_COMUM_SEM_PERFIL)
    if d["impacto"] == "sim":
        pecas += [p for p in cats.get(d["categoria"], []) if p not in pecas]
    return pecas


def matriz(spec):
    d = carregar(spec)
    out = ["| Requisito | Riscos | Testes | Resultado | Evidência | Lacuna |", "|---|---|---|---|---|---|"]
    for r in d["reqs"]:
        rs = [x["risco"] for x in d["riscos"] if r in _refs(x["requisito"], "REQ")]
        ts = [x for x in d["testes"] if r in _refs(x["requisito"], "REQ")]
        res = "; ".join(x["resultado"] for x in ts if not _vazio(x["resultado"]))
        ev = "; ".join(x["evidência"] for x in ts if not _vazio(x["evidência"]))
        lac = "sem teste" if not ts else ("não executado" if not res else ("sem evidência" if not ev else ""))
        out.append(f"| {r} | {', '.join(rs) or '—'} | {', '.join(x['teste'] for x in ts) or '—'} | "
                   f"{res or '—'} | {ev or '—'} | {lac} |")
    return "\n".join(out)


def pecas_do_perfil(perfil):
    """Tudo o que o perfil exige: peças por categoria, documentos emitidos, itens deles e testes obrigatórios."""
    out = []
    for k, v in (perfil.get("categorias_software") or {}).items():
        if not k.startswith("_"):
            out += v
    for k, v in (perfil.get("documentos") or {}).items():
        if not k.startswith("_"):
            out += [k] + list(v.get("itens") or [])
    out += perfil.get("testes_obrigatorios_com_impacto") or []
    return list(dict.fromkeys(out))


def verificar_mapa(perfil_arquivo):
    """Mapa peça -> norma ao lado do perfil (`<profile>-mapa-normas.md`, B3b): toda peça do perfil tem linha,
    toda linha tem marca de confiança válida, a citada tem norma e artigo, e nenhuma linha fala de peça que o
    perfil não tem."""
    with open(perfil_arquivo, encoding="utf-8") as fh:
        perfil = json.load(fh)
    mapa = os.path.join(os.path.dirname(perfil_arquivo), f"{perfil.get('profile', '?')}-mapa-normas.md")
    if not os.path.isfile(mapa):
        return [f"mapa peça -> norma ausente: {os.path.basename(mapa)}"]
    try:
        texto = open(mapa, encoding="utf-8-sig").read()
    except UnicodeDecodeError as e:
        return [f"{os.path.basename(mapa)} não está em UTF-8: {e}"]
    pecas, ach, vistas = pecas_do_perfil(perfil), [], set()
    for ln in texto.splitlines():
        m = re.match(r"^\|\s*`([^`]+)`\s*\|", ln)
        if not m:
            continue
        cel = [c.strip() for c in re.split(r"(?<!\\)\|", ln.strip().strip("|"))]
        peca, marca = m.group(1), cel[-1]
        vistas.add(peca)
        if len(cel) != 5:
            ach.append(f"{peca}: {len(cel)} colunas, o mapa tem 5 (escape '|' no trecho como '\\|')")
            continue
        if peca not in pecas:
            ach.append(f"linha do mapa para peça que o perfil não tem: {peca}")
        if marca not in MARCAS_MAPA:
            ach.append(f"{peca}: marca '{marca}' fora de {sorted(MARCAS_MAPA)}")
        elif marca in ("CONFIRMADO", "INFERIDO") and (_vazio(cel[1]) or _vazio(cel[2])):
            ach.append(f"{peca}: marca {marca} sem norma e artigo")
    ach += [f"peça do perfil sem linha no mapa: {p}" for p in pecas if p not in vistas]
    return ach


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if len(argv) > 1 and argv[1] == "documento":
        import documento_regulado  # noqa: E402  (B3a-3, ADR-124: documento com modelo vindo do perfil)
        return documento_regulado.main(argv[2:])
    if len(argv) == 3 and argv[1] == "mapa":
        ach = verificar_mapa(argv[2])
        for a in ach:
            print(f"  - {a}")
        print("RESULTADO:", f"FAIL ({len(ach)})" if ach else "PASS")
        return 1 if ach else 0
    flags = [a for a in argv[1:] if a.startswith("--")]
    args = [a for a in argv[1:] if not a.startswith("--")]
    if (len(args) != 2 or args[0] not in ("verificar", "matriz", "kit")
            or any(f != "--planejamento" for f in flags) or (flags and args[0] != "verificar")):
        print(__doc__)
        return 2
    cmd, spec = args
    if not spec_fonte.eh_unico(spec):
        print(f"RECUSADO: {spec} não é um arquivo único de especificação (marca {spec_fonte.MARCA})")
        return 2
    try:
        d = carregar(spec)
        if d.get("camada_privada"):
            print(f"camada privada: {d['camada_privada']} (empresa {d['empresa']})")
        if cmd == "kit":
            print("\n".join(f"- {p}" for p in kit(spec)))
            return 0
        if cmd == "matriz":
            print(matriz(spec))
            return 0
        ach = verificar(spec, planejamento=bool(flags))
    except Recusa as e:
        print(f"RECUSADO: {e}")
        return 1
    except OSError as e:
        print(f"FAIL {spec}: {e}")
        return 1
    for a in ach:
        print(f"  - {a}")
    print("-" * 50)
    modo = " (planejamento: testes não executados aceitos)" if flags else ""
    print("RESULTADO:", f"FAIL ({len(ach)})" if ach else f"PASS{modo}")
    return 1 if ach else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
