#!/usr/bin/env python3
"""spec_unificar.py — monta o `spec.md` único a partir de uma especificação no formato antigo (ADR-117).

Serve a duas coisas: (1) a PROVA de que o arquivo único não perde informação — o canário
`test_spec_unico.py` converte cada especificação existente e exige o mesmo veredito dos gates e todas
as linhas da origem no destino; (2) a migração opcional, pasta a pasta, por decisão de quem cuida dela.

Não apaga os arquivos antigos e não sobrescreve um `spec.md` existente sem `--forcar`.
O título de nível 1 de cada arquivo antigo não se perde: vira o comentário `<!-- titulo original: ... -->`.

Uso:
    python tools/spec_unificar.py <pasta-da-spec>                 # imprime o spec.md na saída
    python tools/spec_unificar.py <pasta-da-spec> --gravar        # grava <pasta>/spec.md
    python tools/spec_unificar.py <pasta-da-spec> --gravar --forcar
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_fonte  # noqa: E402
from check_context_brief import find_brief  # noqa: E402  (mesma busca que o gate usa)

class ConversaoRecusada(Exception):
    """A especificação tem uma forma que o arquivo único não comporta sem perda."""


def _fonte_da_parte(pasta, parte):
    antigo = spec_fonte.PARTES[parte][2]
    if parte == "contexto":
        req = os.path.join(pasta, "requirements.md")
        return find_brief(req) if os.path.isfile(req) else None
    p = os.path.join(pasta, antigo)
    return p if os.path.isfile(p) else None


def titulo_como_comentario(linha):
    """A linha de título de nível 1 do arquivo antigo, como aparece no arquivo único."""
    return f"<!-- titulo original: {linha.strip()[1:].strip()} -->"


def _linhas_da_parte(caminho):
    """Linhas do arquivo antigo com o título de nível 1 trocado por comentário. Usa a MESMA
    classificação do leitor (`spec_fonte`): um conversor com regra própria divergiria do leitor.
    Recusa se houver mais de um título de nível 1 fora de código (encerraria a parte) ou bloco de
    código aberto até o fim (engoliria as partes seguintes)."""
    with open(caminho, encoding="utf-8-sig") as fh:
        texto = fh.read()
    try:
        linhas = spec_fonte._linhas_classificadas(texto)
    except spec_fonte.SpecInvalida as e:
        raise ConversaoRecusada(f"{caminho}: {e}")
    titulos, saida = 0, []
    for ln, _fora, titulo in linhas:
        if titulo:
            titulos += 1
            if titulos > 1:
                raise ConversaoRecusada(f"{caminho}: mais de um título de nível 1 fora de bloco de "
                                        f"código — ele encerraria a parte no arquivo único")
            saida.append(titulo_como_comentario(ln))
            continue
        saida.append(ln)
    return saida


def unificar(pasta):
    """Texto do `spec.md` único equivalente à especificação antiga em `pasta`."""
    nome = os.path.basename(os.path.normpath(pasta))
    out = [spec_fonte.MARCA, f"# {nome} — Especificação", "",
           "> Convertido do formato antigo por `tools/spec_unificar.py` (ADR-117). As partes abaixo são",
           "> o conteúdo integral dos arquivos de origem, na ordem.", ""]
    achou = False
    for parte, (letra, titulo, antigo) in spec_fonte.PARTES.items():
        fonte = _fonte_da_parte(pasta, parte)
        if not fonte:
            continue
        achou = True
        rel = os.path.relpath(fonte, pasta).replace("\\", "/")
        out += [f"# Parte {letra} — {titulo}", f"<!-- origem: {rel} -->"]
        out += _linhas_da_parte(fonte)
        out.append("")
    if not achou:
        raise ConversaoRecusada(f"{pasta}: nenhum arquivo de especificação no formato antigo")
    return "\n".join(out) + "\n"


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 1 or not os.path.isdir(args[0]):
        print(__doc__)
        return 2
    pasta = args[0]
    try:
        texto = unificar(pasta)
    except ConversaoRecusada as e:
        print(f"RECUSADO: {e}")
        return 1
    if "--gravar" not in argv:
        sys.stdout.write(texto)
        return 0
    destino = os.path.join(pasta, spec_fonte.ARQUIVO_UNICO)
    if os.path.exists(destino) and "--forcar" not in argv:
        print(f"RECUSADO: {destino} já existe (use --forcar para sobrescrever)")
        return 1
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(texto)
    print(f"gravado: {destino}. Os arquivos antigos foram mantidos, mas a partir de agora a fonte é "
          f"o spec.md: na varredura sem argumento os gates ignoram os antigos desta pasta. Arquive-os "
          f"quando quiser — duas fontes para a mesma especificação divergem.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
