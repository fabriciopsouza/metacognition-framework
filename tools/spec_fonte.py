#!/usr/bin/env python3
"""spec_fonte.py — leitor ÚNICO das partes de uma especificação, nos dois formatos (ADR-117).

POR QUE EXISTE. A especificação de uma feature morava em até 5 arquivos (`requirements.md`,
`validation.md`, `context-brief.md`, `mission.md`, `data-dictionary.md`), e 5 gates abriam esses
arquivos pelo NOME. O dono decidiu (25/09/2026): um arquivo só — `spec.md` com a marca
`<!-- spec-unico:v1 -->` — **desde que nenhum mecanismo quebre e nenhuma informação se perca**.

Este módulo é o único lugar que sabe onde cada parte mora. Os gates pedem "a parte requisitos desta
especificação" e recebem o MESMO texto que antes liam do arquivo antigo; a lógica de verificação de
cada gate não muda. O formato antigo continua aceito: nada é migrado à força.

Formato do arquivo único: partes em título de nível 1 — `# Parte A — Requisitos`, `# Parte B —
Aceite`, `# Parte C — Contexto e âncoras`, `# Parte D — Missão`, `# Parte E — Dicionário de dados`.
A parte vai do seu título ao próximo título de nível 1 FORA de bloco de código. Título com até 3
espaços de recuo conta como título (é assim no Markdown). Bloco de código aberto e não fechado, ou a
mesma parte duas vezes, fazem o arquivo ser RECUSADO (`SpecInvalida`, que é um `OSError`: cada gate já
reprova em erro de leitura) — engolir a parte seguinte em silêncio foi o defeito que a revisão de
25/09 reproduziu.
"""
import glob
import os
import re

MARCA = "<!-- spec-unico:v1 -->"
ARQUIVO_UNICO = "spec.md"

# parte -> (letra no arquivo único, título canônico, arquivo antigo equivalente)
PARTES = {
    "requisitos": ("A", "Requisitos", "requirements.md"),
    "aceite": ("B", "Aceite", "validation.md"),
    "contexto": ("C", "Contexto e âncoras", "context-brief.md"),
    "missao": ("D", "Missão", "mission.md"),
    "dicionario": ("E", "Dicionário de dados", "data-dictionary.md"),
}
_CERCA = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_PARTE = re.compile(r"^ {0,3}#\s+Parte\s+([A-Z])\b")
_H1 = re.compile(r"^ {0,3}#\s")


class SpecInvalida(OSError):
    """O arquivo único tem forma que faria uma parte engolir outra. É OSError de propósito: todo
    gate já reprova em erro de leitura, então a recusa é fail-closed sem mudar a lógica dos gates."""


def _ler(caminho):
    with open(caminho, encoding="utf-8-sig") as fh:
        return fh.read()


def eh_unico(caminho) -> bool:
    """True se `caminho` é um `spec.md` no formato único (tem a marca)."""
    if os.path.basename(caminho) != ARQUIVO_UNICO or not os.path.isfile(caminho):
        return False
    try:
        return MARCA in _ler(caminho)
    except OSError:
        return False


def _linhas_classificadas(texto):
    """(linha, fora_de_codigo, é_titulo_nivel_1). Cerca fecha só com o MESMO caractere que abriu
    (``` não fecha ~~~). Levanta SpecInvalida se um bloco de código ficar aberto até o fim."""
    aberta = None
    saida = []
    for ln in texto.splitlines():
        m = _CERCA.match(ln)
        if m:
            marca = m.group(1)[0]
            if aberta is None:
                aberta = marca
            elif marca == aberta:
                aberta = None
            saida.append((ln, False, False))
            continue
        fora = aberta is None
        saida.append((ln, fora, fora and bool(_H1.match(ln))))
    if aberta is not None:
        raise SpecInvalida("bloco de código aberto e nunca fechado — ele engoliria as partes seguintes")
    return saida


def validar_unico(texto):
    """Recusa o que faria uma parte sumir em silêncio: cerca aberta e parte repetida."""
    vistas = set()
    for ln, _fora, titulo in _linhas_classificadas(texto):
        if titulo:
            m = _PARTE.match(ln)
            if m:
                if m.group(1) in vistas:
                    raise SpecInvalida(f"'Parte {m.group(1)}' aparece duas vezes — a segunda seria "
                                       f"descartada sem aviso")
                vistas.add(m.group(1))


def extrair_parte(texto, parte):
    """Texto da parte `parte` dentro de um arquivo único, ou None se a parte não existe."""
    letra = PARTES[parte][0]
    dentro, saida = False, []
    for ln, _fora, titulo in _linhas_classificadas(texto):
        if titulo:
            if dentro:
                break  # próximo título de nível 1 encerra a parte
            m = _PARTE.match(ln)
            if m and m.group(1) == letra:
                dentro = True
                continue
        if dentro:
            saida.append(ln)
    return "\n".join(saida) + "\n" if dentro else None


def ler_parte(caminho, parte):
    """Texto da `parte` da especificação apontada por `caminho`.

    - pasta: o `spec.md` único dela, se houver; senão o arquivo antigo da parte (None se não houver);
    - `spec.md` único: a parte extraída (None se a parte não existe); forma inválida → SpecInvalida;
    - qualquer outro arquivo: o próprio arquivo, inteiro — comportamento idêntico ao dos gates antes.
    `OSError` sobe quando o arquivo indicado não abre: cada gate já trata esse erro do jeito dele.
    """
    antigo = PARTES[parte][2]
    if os.path.isdir(caminho):
        unico = os.path.join(caminho, ARQUIVO_UNICO)
        if eh_unico(unico):
            return ler_parte(unico, parte)
        alvo = os.path.join(caminho, antigo)
        return _ler(alvo) if os.path.isfile(alvo) else None
    if eh_unico(caminho):
        texto = _ler(caminho)
        validar_unico(texto)
        return extrair_parte(texto, parte)
    # Arquivo indicado que NÃO é o formato único: lê exatamente ele, com qualquer nome — era o que
    # cada gate fazia antes. Se não existir, o OSError sobe como antes.
    return _ler(caminho)


def alvos_unicos(raiz):
    """Todos os `spec.md` no formato único sob docs/specs (para o modo sem argumento dos gates)."""
    base = os.path.join(raiz, "docs", "specs", "**", ARQUIVO_UNICO)
    return sorted(p for p in glob.glob(base, recursive=True) if eh_unico(p))


def sombreado_por_unico(caminho) -> bool:
    """True se `caminho` é arquivo do formato ANTIGO numa pasta que já tem o `spec.md` único.

    Depois de `spec_unificar.py --gravar`, os arquivos antigos ficam na pasta (a ferramenta não
    apaga nada). No modo sem argumento, os gates usavam os dois e davam dois vereditos para a mesma
    feature. Regra: havendo o arquivo único, ele é a fonte; o antigo da mesma pasta sai da varredura
    (continua lido se for passado explicitamente como argumento)."""
    if os.path.basename(caminho) == ARQUIVO_UNICO:
        return False
    return eh_unico(os.path.join(os.path.dirname(os.path.abspath(caminho)), ARQUIVO_UNICO))
