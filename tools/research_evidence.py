#!/usr/bin/env python3
"""research_evidence — "NÃO SEI" só vale depois de busca provada (ADR-092).

O QUE RESOLVE. O manifesto declara dois comportamentos que dependem desta ferramenta e ela
nunca existiu, então o `squad_gate.py` marcava o papel como faltante para sempre — fail-closed
correto, mas nenhum caminho para passar:

  · `research_ou_ratificacao` — mexer em número regulado exige pesquisa OU ratificação humana;
  · `busca_exaustiva` — todo `[DESCONHECIDO]` que vai a decisão exige busca provada antes.

A regra que o manifesto justifica com todas as letras: *"NÃO SEI só é legítimo APÓS busca
provada — elimina o punt preguiçoso"*. Sem mecanismo, declarar desconhecimento era grátis. O que
esta ferramenta mecaniza é o **piso da busca**, não a onisciência: ela não sabe se a resposta está
certa, sabe se alguém procurou em fontes independentes e anexou o que achou.

DOIS CAMINHOS, e o segundo é tão legítimo quanto o primeiro:

1. **Pesquisa.** Um registro em `_meta/research/*.json` com pelo menos K **domínios distintos**
   (K vem de `behaviors/manifest.json`, hoje 2), cada fonte com endereço, `sha256` do que foi
   lido e a data em que a vigência foi conferida. Duas páginas do mesmo domínio contam como uma:
   citar o mesmo site duas vezes não é triangular.
2. **Ratificação humana.** Campo `ratificado_por` preenchido. Uma pessoa assume o número. Isso
   dispensa as fontes de propósito — há casos em que a resposta não está em lugar nenhum e alguém
   decide. O que não se aceita é o silêncio.

O que ela **não** faz: não visita a rede (offline por construção, como o resto do núcleo), não
julga se a fonte é boa, não confere se o `sha256` corresponde à página hoje. Ela confere que a
declaração existe, é completa e é plural.

Uso:
    python tools/research_evidence.py --paths data/catalog/bindings.json
    python tools/research_evidence.py --paths-from arquivo.txt
    python tools/research_evidence.py --listar
    python tools/research_evidence.py --modelo            # imprime um registro em branco

Códigos de saída: 0 coberto · 1 sem cobertura ou registro incompleto.
"""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

RAIZ_PADRAO = Path(__file__).resolve().parent.parent
DIR_REGISTROS = "_meta/research"
MANIFESTO = "behaviors/manifest.json"
K_PADRAO = 2

CAMPOS_FONTE = ("url", "sha256", "vigencia_verificada_em")

MODELO = {
    "assunto": "o que foi pesquisado, em uma frase",
    "escopo_paths": ["data/catalog/bindings.json"],
    "data": "2026-08-16",
    "conclusao": "o que ficou decidido, e por que as fontes sustentam isso",
    "ratificado_por": None,
    "fontes": [
        {"url": "https://dominio-a.exemplo/pagina", "sha256": "<sha256 do conteudo lido>",
         "vigencia_verificada_em": "2026-08-16", "oficial": True,
         "trecho": "o pedaco que sustenta a conclusao"},
        {"url": "https://dominio-b.exemplo/outra", "sha256": "<sha256 do conteudo lido>",
         "vigencia_verificada_em": "2026-08-16", "oficial": False,
         "trecho": "o pedaco que sustenta a conclusao"},
    ],
}


def _ler_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def k_exigido(raiz):
    """K vem do manifesto — mudar a exigencia e' editar dado, nao codigo (ADR-092)."""
    d = _ler_json(Path(raiz) / MANIFESTO) or {}
    try:
        return int(d.get("parametros", {}).get("K_dominios_distintos", K_PADRAO))
    except (TypeError, ValueError):
        return K_PADRAO


ESQUEMAS_ACEITOS = ("http", "https")


def dominio(url):
    """Dominio registravel, de forma grosseira e honesta: host sem `www`, minusculo.

    Nao usa lista de sufixos publicos (seria dependencia externa). Serve ao proposito:
    distinguir `a.gov.br` de `b.org`.

    DUAS BURLAS DE UM CARACTERE, fechadas apos o qa-critic (Fable, 2026-08-16) reproduzi-las:
    - **ponto final** (`a.exemplo.`): no DNS e' o MESMO site que `a.exemplo`, mas contava como
      dominio novo. Um caractere inflava a triangulacao.
    - **esquema nao-web** (`file://qualquer/x`): tinha netloc e contava como dominio. Uma fonte
      real mais um `file://` de host inventado passava por duas fontes independentes.

    LIMITE QUE CONTINUA VALENDO, declarado e nao escondido: subdominios do mesmo site
    (`docs.x.com` e `api.x.com`) contam como DOIS. Fechar isso exigiria lista de sufixos
    publicos, que e' dependencia externa — e a fraude exige ma-fe ativa, nao descuido.
    """
    try:
        partes = urlparse(str(url))
    except ValueError:
        return ""
    if partes.scheme.lower() not in ESQUEMAS_ACEITOS:
        return ""
    host = (partes.netloc or "").lower().split("@")[-1].split(":")[0].rstrip(".")
    return host[4:] if host.startswith("www.") else host


def registros(raiz):
    d = Path(raiz) / DIR_REGISTROS
    return sorted(d.glob("*.json")) if d.is_dir() else []


def avaliar(reg, k):
    """(valido, motivo, dominios) para UM registro ja carregado."""
    if not isinstance(reg, dict):
        return False, "registro nao e' objeto JSON", []
    bruto = reg.get("ratificado_por")
    if isinstance(bruto, bool):
        # `"ratificado_por": true` virava ratificado por "True" — ninguem assumia o numero e
        # passava. Achado do qa-critic (Fable, 2026-08-16). Ratificacao e' uma PESSOA, com nome.
        return False, "`ratificado_por` e' booleano — precisa do NOME de quem assume o numero", []
    ratificador = str(bruto or "").strip()
    if ratificador and not any(c.isalpha() for c in ratificador):
        return False, f"`ratificado_por` ({ratificador!r}) nao parece nome de pessoa", []
    if ratificador:
        if not str(reg.get("conclusao") or "").strip():
            return False, "ratificado_por preenchido mas sem `conclusao` — assinar o que?", []
        return True, f"ratificado por {ratificador}", []

    fontes = reg.get("fontes")
    if not isinstance(fontes, list) or not fontes:
        return False, "sem `fontes` e sem `ratificado_por` — nenhum dos dois caminhos", []

    for i, f in enumerate(fontes):
        if not isinstance(f, dict):
            return False, f"fonte {i} nao e' objeto", []
        faltam = [c for c in CAMPOS_FONTE if not str(f.get(c) or "").strip()]
        if faltam:
            return False, f"fonte {i} ({f.get('url', 's/ url')}) sem: {', '.join(faltam)}", []

    doms = sorted({dominio(f["url"]) for f in fontes} - {""})
    if len(doms) < k:
        return (False, f"{len(doms)} dominio(s) distinto(s), exigido {k} — "
                       f"citar o mesmo site duas vezes nao e' triangular ({', '.join(doms)})", doms)
    return True, f"{len(doms)} dominios distintos: {', '.join(doms)}", doms


def cobertura(raiz, paths):
    """(cobertos, descobertos, achados) — quais paths tem registro VALIDO que os declare."""
    k = k_exigido(raiz)
    alvos = {str(p).replace("\\", "/") for p in paths}
    cobertos, achados = set(), []
    for arq in registros(raiz):
        reg = _ler_json(arq)
        if reg is None:
            achados.append((arq.name, False, "arquivo ilegivel ou JSON invalido", set()))
            continue
        escopo = {str(x).replace("\\", "/") for x in (reg.get("escopo_paths") or [])}
        atinge = alvos & escopo
        if not atinge:
            continue
        valido, motivo, _ = avaliar(reg, k)
        achados.append((arq.name, valido, motivo, atinge))
        if valido:
            cobertos |= atinge
    return cobertos, alvos - cobertos, achados


def main(argv=None):
    ap = argparse.ArgumentParser(description="Evidencia de pesquisa para numero regulado e "
                                             "para [DESCONHECIDO] que vai a decisao (ADR-092).")
    ap.add_argument("--paths", nargs="*", default=[])
    ap.add_argument("--paths-from")
    ap.add_argument("--repo", default=str(RAIZ_PADRAO))
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--modelo", action="store_true")
    a = ap.parse_args(argv)
    raiz = Path(a.repo)

    if a.modelo:
        print(json.dumps(MODELO, ensure_ascii=False, indent=2))
        return 0

    k = k_exigido(raiz)
    if a.listar:
        regs = registros(raiz)
        print(f"[research] {len(regs)} registro(s) em {DIR_REGISTROS}/ · K exigido = {k}")
        for arq in regs:
            reg = _ler_json(arq)
            valido, motivo, _ = avaliar(reg, k) if reg is not None else (False, "ilegivel", [])
            print(f"  [{'OK ' if valido else 'NAO'}] {arq.name} — {motivo}")
            if reg:
                print(f"        cobre: {', '.join(reg.get('escopo_paths') or []) or '(nada)'}")
        return 0

    paths = list(a.paths)
    if a.paths_from:
        try:
            paths += [l.strip() for l in Path(a.paths_from).read_text(
                encoding="utf-8").splitlines() if l.strip()]
        except OSError as e:
            print(f"[research] nao consegui ler {a.paths_from}: {e}")
            return 1
    if not paths:
        ap.error("informe --paths, --paths-from, --listar ou --modelo")

    cobertos, descobertos, achados = cobertura(raiz, paths)
    for nome, valido, motivo, atinge in achados:
        marca = "OK " if valido else "NAO"
        print(f"[research] [{marca}] {nome} -> {', '.join(sorted(atinge))} — {motivo}")

    if descobertos:
        print(f"[research] BLOQUEADO: {len(descobertos)} path(s) sem evidencia de pesquisa "
              f"valida: {', '.join(sorted(descobertos))}")
        print(f"  Exigido: registro em {DIR_REGISTROS}/ com >= {k} dominios DISTINTOS "
              f"(url + sha256 + vigencia por fonte), OU o campo `ratificado_por`.")
        print("  Modelo pronto: python tools/research_evidence.py --modelo")
        return 1

    print(f"[research] OK — {len(cobertos)} path(s) com evidencia de pesquisa valida.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
