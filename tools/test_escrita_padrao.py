#!/usr/bin/env python3
"""Canario da norma de escrita — exit 0 = PASS, exit 1 = FAIL.

O QUE FECHA. `_shared/output-format/SKILL.md` secao A.0 ("o texto se sustenta sozinho") era a unica
regra transversal do nucleo SEM canario: prosa boa, apontada por todos os papeis, e sem nada que
reprovasse quando alguem a desobedecesse. O dono cobrou em 18/08/2026 que o metodo de escrita
— compreensivel, conciso, direto, contextualizado, com referencia mas NAO solta, acionavel — seja
padrao do framework e do metodo, e nao preferencia de sessao.

O QUE ELE CHECA, e o que deliberadamente NAO checa:

  (a) ALCANCE — todo papel do squad aponta para `output-format`. Se alguem cria papel novo e esquece
      o ponteiro, a norma deixa de chegar ao papel em silencio. Isto e verificavel sem ambiguidade.

  (b) REFERENCIA SOLTA — frase cujo conteudo e' SO um codigo interno ("B0 contradiz secao 7, segundo
      P1"). A norma permite e incentiva a referencia, como apoio a verificacao; proibe que ela SEJA
      a explicacao. Mede-se contando as palavras da frase que nao sao a referencia.

  NAO checa qualidade de redacao. Gate que adivinha se um texto "esta bom" erra, e gate que erra e'
  desligado por quem tem pressa — e ai nao protege mais nada. A parte nao mecanizavel do A.0
  continua sendo cobrada em revisao adversarial, e isso esta declarado na propria secao.

EXCECOES, declaradas de proposito (a norma exige que o gate liste as suas):
  - Tabelas, blocos de codigo, frontmatter e linhas de citacao (`>`): formato tabular e' referencia
    por desenho.
  - LINHA DE PONTEIRO — a que comeca com `Detalhe:`, `Fonte:`, `Ver:`, `Leia:`. Ela existe PARA
    apontar, e a norma prescreve exatamente esse padrao: explique no corpo, aponte na linha seguinte.
    Sem esta excecao o gate acusa o comportamento que a norma pede.
  - O proprio `output-format/SKILL.md` e este arquivo: citam os codigos para ENSINAR o defeito.
  - Titulos e itens de indice: nome curto nao e' frase.

Rodar: python tools/test_escrita_padrao.py
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

# O console do Windows abre em cp1252 e engasga no simbolo de secao.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent

# Prosa que a norma governa: as portas de entrada, sempre inteiras, mais SO a secao mais nova do
# CHANGELOG e do history. O acervo historico e append-only por desenho (o proprio history.md declara
# isso) — cobrar norma nova de checkpoint de junho seria reescrever registro passado, que e outra
# decisao e nao esta tomada. EXCECAO DECLARADA, nao esquecimento.
ALVOS = ("CLAUDE.md", "AGENTS.md", "AGENT-FRAMEWORK.md")
ALVOS_SO_TOPO = {"CHANGELOG.md": r"^## \[", "history.md": r"^## 20\d\d-"}

ISENTOS = {"_shared/output-format/SKILL.md", "tools/test_escrita_padrao.py"}

#: Referencia interna: secao por numero, identificador de documento, codigo curto tipo B-01/P1/G-06.
REFERENCIA = re.compile(r"(?:§\s*\d+(?:\.\d+)*|\b(?:ADR|ATD|PR|RFC)[-\s]?\d+\b|"
                        r"\bse[cç][aã]o\s+\d+(?:\.\d+)*|\b[A-Z]{1,3}-?\d{1,3}\b)")
#: Palavras que nao contam como explicacao: ligacao e pontuacao.
VAZIAS = {"e", "ou", "de", "do", "da", "em", "no", "na", "o", "a", "os", "as", "que", "com", "por",
          "para", "ao", "aos", "um", "uma", "se", "ver", "cf", "vs", "x", "ate", "the",
          # [qa-critic Sonnet 19/08/2026] enchimento passava por explicacao: cinco frases-armadilha
          # atingiam o minimo de palavras sem dizer nada. Enchimento nao e explicacao.
          "conforme", "combinado", "exatamente", "isso", "isto", "aquilo", "assim", "mesmo", "mesma",
          "ali", "aqui", "la", "definido", "descrito", "tratado", "trata", "cobre", "cobrir", "segue",
          "seguir", "aplica", "aplicar", "sem", "duvida", "nenhuma", "ja", "esta", "este", "sera",
          "vale", "diz", "dito", "acima", "abaixo", "citado", "referido", "questao", "assunto",
          # [Fable 19/08/2026] adverbio de enchimento tambem nao e explicacao
          "obviamente", "naturalmente", "claramente", "evidentemente", "certamente", "logicamente",
          "simplesmente", "basicamente", "praticamente", "realmente", "efetivamente"}

MIN_PALAVRAS = 4

#: Prefixos de LINHA DE PONTEIRO. Ela existe PARA apontar, e a norma prescreve esse padrao:
#: explique no corpo, aponte na linha seguinte. Sem esta excecao o gate acusa o que a norma pede.
PREFIXOS_PONTEIRO = ("detalhe", "detalhes", "fonte", "fontes", "ver", "veja", "leia",
                     "referencia", "referência", "referencias", "referências")


def _sem_acento(s: str) -> str:
    """[qa-critic Fable 19/08/2026] a lista de palavras de enchimento guardava `ja`, `esta`, `sera`,
    `duvida` SEM acento, e o tokenizador preserva acento — entao metade da lista nunca casava, e
    "Isso ja esta, sem duvida, exatamente o que sera visto ali" passava contando 4 explicacoes."""
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def PONTEIRO(frase: str) -> bool:
    """[qa-critic Sonnet 19/08/2026] `startswith` sem fronteira de palavra isentava por acidente:
    "Vejamos", "Leiam" e "Fontes" disparavam a excecao de linha-de-ponteiro sem serem ponteiro."""
    base = frase.lstrip("-*_> ").lower()
    return bool(re.match(r"(?:%s)\b\s*:?" % "|".join(PREFIXOS_PONTEIRO), base))


def _texto(caminho: Path, so_topo: str | None):
    """Devolve as linhas do arquivo; com `so_topo`, apenas da 1a ate a 2a ocorrencia do marcador."""
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    if not so_topo:
        return list(enumerate(linhas, 1))
    achou, out = 0, []
    for n, linha in enumerate(linhas, 1):
        if re.match(so_topo, linha):
            achou += 1
            if achou == 2:
                break
        if achou == 1:
            out.append((n, linha))
    return out


def linhas_de_prosa(caminho: Path, so_topo: str | None = None):
    """Rende (numero, PARAGRAFO) — pula tabela, codigo, titulo, citacao.

    Junta linhas quebradas no MESMO paragrafo antes de devolver. Sem isto, a prosa hard-wrapped e'
    avaliada em fragmentos e o gate acusa "referencia solta" numa frase que continua na linha
    seguinte — foi o proprio defeito da primeira versao deste canario.
    """
    dentro_codigo = False
    buf, inicio = [], None
    for n, linha in _texto(caminho, so_topo):
        t = linha.strip()
        if t.startswith("```"):
            dentro_codigo = not dentro_codigo
            continue
        if dentro_codigo:
            continue
        ignorar = ((not t)
                   or t.startswith(("#", "|", ">", "---", "- [", "* [")) or linha.startswith("  "))
        if ignorar:
            if buf:
                yield inicio, " ".join(buf)
                buf, inicio = [], None
            continue
        if inicio is None:
            inicio = n
        buf.append(t)
    if buf:
        yield inicio, " ".join(buf)


def frases(texto: str):
    for f in re.split(r"(?<=[.!?])\s+", texto):
        f = f.strip()
        if f:
            yield f


def referencia_solta(caminho: Path, so_topo: str | None = None):
    achados = []
    for n, linha in linhas_de_prosa(caminho, so_topo):
        for f in frases(linha):
            refs = REFERENCIA.findall(f)
            if not refs:
                continue
            # A excecao do ponteiro vale na FRASE, e nao so na linha: o paragrafo junta linhas, e
            # "Detalhe: ADR-007 (caminho)" pode comecar no meio de um paragrafo cuja primeira linha
            # nao e ponteiro. Teste direto de prefixo em vez de expressao regular — mais simples de
            # ler e sem o risco de a expressao errar por causa de asterisco ou marcador de lista.
            if PONTEIRO(f):
                continue
            # [qa-critic Sonnet 19/08/2026] isentar TODA referencia entre parenteses abria a porta
            # para "O motivo e este (ADR-109)." — a citacao entre parenteses era a unica explicacao.
            # Agora o parentese continua sendo apoio, mas a frase ainda precisa dizer algo sem ele.
            sem_parenteses = re.sub(r"\([^)]*\)", " ", f)
            resto = REFERENCIA.sub(" ", sem_parenteses)
            palavras = [p for p in (_sem_acento(x) for x in re.findall(r"[\wÀ-ÿ]+", resto.lower()))
                        if p not in VAZIAS and not p.isdigit()]
            if len(palavras) < MIN_PALAVRAS:
                achados.append((n, f, len(palavras)))
    return achados


NORMA = "_shared/output-format/SKILL.md"
MARCADOR_NORMA = "## Parte A.0 — O texto se sustenta sozinho"


def norma_existe():
    """A norma que esta capacidade protege continua no arquivo dono?

    Sem esta verificacao, o canario guardava so os PONTEIROS para a norma: alguem podia apagar a
    secao inteira e todos os papeis continuariam apontando para um arquivo que nao diz mais nada —
    verde perfeito, norma morta. Achado do canario de auditoria de enforcement em 19/08/2026.
    """
    arq = RAIZ / NORMA
    if not arq.exists():
        return [f"{NORMA} nao existe — a norma que todos os papeis citam desapareceu"]
    if MARCADOR_NORMA not in arq.read_text(encoding="utf-8"):
        return [f"{NORMA} nao contem mais a secao da norma ({MARCADOR_NORMA!r}) — os papeis "
                f"continuam apontando para um arquivo que nao diz mais o que eles prometem seguir"]
    return []


def alcance():
    """Todo papel do squad tem de apontar para a norma de formato."""
    falta = []
    papeis = ("pmo", "discovery", "architect", "developer", "qa-critic", "docops", "explorer")
    for nome in papeis:
        skill = RAIZ / ".agent" / "skills" / nome / "SKILL.md"
        if not skill.exists():
            falta.append(f"{nome} (skill ausente)")
            continue
        if "output-format" not in skill.read_text(encoding="utf-8"):
            falta.append(str(skill.relative_to(RAIZ)).replace("\\", "/"))
    return falta


def main():
    falhas = []

    falhas += norma_existe()

    sem_ponteiro = alcance()
    if sem_ponteiro:
        falhas.append("papel(is) do squad sem ponteiro para a norma de formato — a norma nao chega "
                      f"ao papel e ninguem percebe: {', '.join(sem_ponteiro)}")
    else:
        print(f"  ok   alcance: todo papel do squad aponta para output-format")

    total = 0
    for nome in list(ALVOS) + list(ALVOS_SO_TOPO):
        p = RAIZ / nome
        if not p.exists() or nome in ISENTOS:
            continue
        achados = referencia_solta(p, ALVOS_SO_TOPO.get(nome))
        total += len(achados)
        if achados:
            for n, f, q in achados[:5]:
                falhas.append(f"{nome}:{n} referencia solta ({q} palavra(s) de explicacao, "
                              f"minimo {MIN_PALAVRAS}) — o leitor tem de abrir outro arquivo para "
                              f"saber se aquilo e bom ou ruim: {f[:110]}")
            if len(achados) > 5:
                falhas.append(f"{nome}: mais {len(achados)-5} caso(s) de referencia solta nao listados")
        else:
            print(f"  ok   {nome}: nenhuma referencia solta em prosa")

    print()
    if falhas:
        print(f"FAIL — {len(falhas)} problema(s) contra _shared/output-format secao A.0:\n")
        for f in falhas:
            print(f"  x {f}")
        print("\nA norma permite citar; proibe que a citacao SEJA a explicacao.")
        return 1
    print("PASS — norma de escrita alcanca todo papel, e a prosa entregue explica antes de citar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
