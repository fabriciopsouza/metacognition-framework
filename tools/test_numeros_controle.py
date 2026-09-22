#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canario dos NUMEROS DA PROSA do pacote controle_* — exit 0 = PASS, exit 1 = FAIL.

POR QUE ESTE ARQUIVO EXISTE, e por que ele e' separado.

Numero em prosa e' a unica parte deste pacote que nenhum outro gate olha. O dono ja disse que
fabricacao em prosa e' o ponto cego do sistema: os canarios cobrem codigo e dado, nao narrativa. E
nesta entrega tres numeros do ADR estavam errados — nenhum inventado, todos numeros REAIS de outra
coisa, que e' o modo de erro mais dificil de pegar em leitura porque o texto soa conferido.

A PRIMEIRA VERSAO DESTE CANARIO VIVIA DENTRO DE `test_controle_projeto.py` E ALEGAVA MAIS DO QUE
FAZIA. Ele dizia "confere os numeros contra a realidade MEDIDA", mas media UM (linhas de nucleo.py)
e bloqueava QUATRO strings de numeros ja refutados. Um numero novo e errado — "200 verificacoes" —
passava batido. **Achado do QA rodada 3**, e a critica estava certa: denylist nao e' verificacao.

Mora fora do outro canario por um motivo mecanico: para MEDIR quantas verificacoes um canario
executa, e' preciso RODA-LO. Um teste que roda a si mesmo nao termina.

O que ele faz, e o que NAO faz:
  FAZ   mede, rodando de verdade, quantas verificacoes cada canario executa e quantas sao
        sabotagem; conta as mutacoes provadas; le as linhas de nucleo.py; e exige que TODO numero
        dessas familias que aparecer na prosa bata com a medicao.
  FAZ   bloqueia numeros ja REFUTADOS, para o erro corrigido nao voltar por copia.
  NAO FAZ  conferir numero que nao seja destas familias (linhas de diff, contagem de arquivos,
        datas). Esses continuam por conta de quem escreve — e isto fica DITO aqui, em vez de a
        docstring prometer cobertura que o mecanismo nao tem.

Rodar: python tools/test_numeros_controle.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
try:
    # O console default do Windows e' cp1252, e um glifo fora dele derruba o `print` com
    # UnicodeEncodeError — matando o canario no meio, sem veredito, e levando o runner junto.
    # [ACHADO ALTA DO QA DA FRONTEIRA, rodada 2] aconteceu de verdade: 68 canarios deixaram de
    # rodar. As ferramentas ja se blindavam; os canarios, nao.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                    # pragma: no cover
    pass

falhou = []


def checar(nome, condicao, detalhe=""):
    if condicao:
        print(f"  ok   {nome}")
    else:
        print(f"  FAIL {nome} {detalhe}")
        falhou.append(nome)


def medir(canario: str) -> tuple[int, int]:
    """Roda o canario de verdade e conta o que ele executou. Contar `checar(` no fonte nao serve:
    ha lacos, e o numero da prosa e' o que a pessoa VE na tela."""
    r = subprocess.run([sys.executable, str(RAIZ / "tools" / canario)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    linhas = [l for l in (r.stdout or "").splitlines() if re.match(r"^  (ok|FAIL) ", l)]
    sabot = [l for l in linhas if "sabotagem detectada" in l]
    return len(linhas), len(sabot)


def prosa() -> dict[str, str]:
    """Os documentos que falam deste pacote, com o texto ACHATADO.

    Achatar nao e' detalhe: a versao anterior desta varredura usava `grep "~50 linhas"` e nao achou
    nada, porque a frase estava QUEBRADA EM DUAS LINHAS e nao existia como texto contiguo. A
    ferramenta de verificacao tinha o mesmo ponto cego do texto verificado."""
    alvos = [RAIZ / "CHANGELOG.md", RAIZ / "_shared" / "controle-projeto" / "SKILL.md",
             *sorted((RAIZ / "docs" / "adr").glob("113-*.md")),
             *sorted((RAIZ / ".claude" / "commands").glob("controle-*.md"))]
    out = {}
    for a in alvos:
        if not a.is_file():
            continue
        bruto = a.read_text(encoding="utf-8").replace("\r\n", "\n")
        if a.name == "CHANGELOG.md":
            # ESCOPO. O CHANGELOG inteiro tem numeros de dezenas de outras entregas, e sem recorte
            # este canario reprovava por "14 verificacoes" de um ADR antigo. Canario que reprova por
            # dado alheio e' pior que canario ausente: ensina a pessoa a ignorar o vermelho.
            i = bruto.find("### ADR-113")
            if i < 0:
                return {"CHANGELOG.md:AUSENTE": ""}     # o bloco sumiu — o canario tem de gritar
            resto = bruto[i + 3:]
            j = resto.find("\n### ")
            k = resto.find("\n## ")
            fim = min([x for x in (j, k) if x >= 0], default=-1)
            bruto = resto[:fim] if fim >= 0 else resto
        out[a.name] = re.sub(r"\s+", " ", bruto)
    return out


# Numeros que ja foram AFIRMADOS e REFUTADOS. Nao podem voltar como afirmacao — mencao historica
# ("a primeira redacao dizia X") e' legitima e esta excluida pelo contexto.
# Afirmacao que NAO PODE ser verificada de dentro da suite, e por isso nao deve ser feita.
# [achado ALTA do QA rodada 8] o CHANGELOG dizia "83 PASS" e a suite dava 84 — quarta ocorrencia da
# classe "numero real, medido em outra hora". Medi-lo daqui seria recursao: este canario faz parte
# da suite. Entao proibe-se afirmar, e aponta-se a fonte.
NAO_AFIRMAVEL = [
    (r"\d+ PASS\b", "contagem da suite nao e' verificavel de dentro dela; aponte "
                     "`python tools/run_canaries.py` em vez de afirmar o numero"),
    (r"\d+ can[aá]rios? na su[ií]te", "idem: a suite cresce, e o numero envelhece sozinho"),
]

REFUTADOS = [
    (r"encolheu 485 linhas", "485 era so o lado da subtracao; o liquido e' -283"),
    (r"`nucleo\.py` \(~ ?50", "nucleo.py tem 124 linhas"),
    (r"~ ?50 linhas, a única coisa", "nucleo.py tem 124 linhas"),
    (r"30 verifica\w* por sabotagem", "sao 11 sabotagens"),
]
MOLDURA_HISTORICA = ("primeira redação dizia", "primeira redação desta seção dizia",
                     "A primeira redação")


def _e_historico(texto: str, pos: int) -> bool:
    """O numero em `pos` pertence a uma frase que fala do PASSADO?

    [ACHADO MEDIA DO QA RODADA 4] a versao anterior olhava 130 caracteres para tras e aceitava a
    moldura em qualquer lugar dessa janela. Bastava uma frase historica terminar 90 caracteres antes
    para um numero ATUAL e errado passar batido — a moldura virava esconderijo.

    Agora a moldura tem de estar na MESMA FRASE do numero: a busca para no ponto final anterior."""
    trecho = texto[max(0, pos - 260):pos]
    corte = max(trecho.rfind(". "), trecho.rfind("! "), trecho.rfind("? "))
    frase = trecho[corte + 1:] if corte >= 0 else trecho
    return any(h in frase for h in MOLDURA_HISTORICA)


# Como a prosa ATRIBUI um numero de verificacoes ao canario de onde ele saiu. A chave e' o nome do
# arquivo ou o nome do bloco; o valor e' o rotulo interno usado na medicao.
# [ACHADO ALTA DO QA RODADA 10] sem isto o teste so conferia PERTENCIMENTO ao conjunto, e um numero
# atribuido ao modulo ERRADO passava — que e' exatamente a classe "numero real, de outra coisa".
ATRIBUICAO = {
    "test_controle_base": "base", "controle_base": "base", "fronteira": "base",
    "test_controle_projeto": "politica", "controle_projeto": "politica",
    "politica": "politica", "política": "politica",
    "test_controle_sharepoint": "sharepoint", "controle_sharepoint": "sharepoint",
    "list": "sharepoint",
}


def _a_quem(texto: str, pos: int) -> str | None:
    """De qual canario e' o numero que esta em `pos`? A atribuicao mais PROXIMA antes dele ganha.

    Olhar para tras ate 140 caracteres cobre a celula da tabela e a frase; mais que isso comecaria a
    pegar a linha de cima, e atribuicao errada e' pior que atribuicao ausente."""
    antes = texto[max(0, pos - 140):pos].lower()
    # [ACHADO ALTA DO QA RODADA 11] isto casava por SUBSTRING, e "list" cabe dentro de "lista" —
    # palavra corriqueira em portugues. Um numero CERTO sobre a politica seria acusado de errado
    # porque a frase anterior falava de uma "lista". Falso positivo, e o proprio cabecalho deste
    # arquivo diz que falso positivo e' pior que canario ausente: ensina a ignorar o vermelho.
    #
    # E' a TERCEIRA aparicao da mesma familia nesta serie — a primeira foi "Ana-Maria" tratada como
    # marcador porque "-" cabia dentro dela. Casamento por substring nao respeita palavra.
    achados = []
    for chave, quem in ATRIBUICAO.items():
        # [ACHADO ALTA DO QA RODADA 12] a fronteira era ASCII pura (`[0-9a-z_]`), entao letra
        # ACENTUADA contava como fronteira e "listável" reabria o falso positivo que a rodada 11
        # fechou para "lista". Num canario que audita prosa em PORTUGUES, ignorar acento e' ignorar
        # o alfabeto do texto. `\w` em Python 3 ja e' Unicode por padrao para `str`.
        for m in re.finditer(r"(?<!\w)" + re.escape(chave) + r"(?!\w)", antes):
            achados.append((m.start(), quem))
    return max(achados)[1] if achados else None


def divergencias(texto: str, familias):
    """Numeros da prosa que NAO batem com o medido, com o contexto para a mensagem.

    [ACHADO ALTA DO QA RODADA 5] esta funcao existia, mas `main()` tinha uma COPIA PROPRIA da
    logica — e quando `_e_historico` foi corrigida, a copia ficou com a versao antiga. O auto-teste
    provava que ESTA funcao enxerga, enquanto o canario aprovava documento pelo outro caminho, com
    o defeito vivo. Logica duplicada que divergiu, que e' a classe em que este pacote mais tropecou.
    Agora ha um caminho so: `main` e o auto-teste chamam daqui."""
    fora = []
    for padrao, validos, rotulo in familias:
        atribuivel = isinstance(validos, dict)     # familia por canario -> exige atribuicao
        for m in re.finditer(padrao, texto):
            if _e_historico(texto, m.start()):
                continue
            valor = int(m.group(1))
            trecho = texto[max(0, m.start() - 60):m.end() + 20]
            if atribuivel:
                quem = _a_quem(texto, m.start())
                if quem is None:
                    fora.append((valor, rotulo + " SEM ATRIBUICAO", sorted(validos.values()),
                                 trecho + "  [diga de qual canario e' este numero]"))
                elif valor != validos[quem]:
                    fora.append((valor, f"{rotulo} atribuido a `{quem}`", [validos[quem]], trecho))
            elif valor not in validos:
                fora.append((valor, rotulo, sorted(validos), trecho))
    return fora


def _bate(texto: str, familias) -> list[int]:
    """So os numeros divergentes. Acucar para o auto-teste."""
    return [d[0] for d in divergencias(texto, familias)]


def auto_teste(familias) -> None:
    """O detector ainda enxerga?

    [EXIGIDO PELO GATE audit_enforcement] neste canario o MECANISMO e' o proprio canario, entao
    sabota-lo nao produz vermelho — produz verde por engano. Detector que so olha para fora nao
    consegue provar que enxerga. Estes tres casos sao a prova, e um deles e' a moldura historica,
    que existe para o texto poder CITAR o numero errado ao explicar o erro."""
    achou = _bate("O canario test_controle_base.py roda 99999 verificações — 77 por sabotagem.",
                  familias)
    checar("auto-teste: numero inventado na prosa e' pego", 99999 in achou,
           "-> o detector parou de comparar; a partir daqui ele carimba em vez de verificar")
    # [ACHADO ALTA DO QA RODADA 10] o caso que faltava: numero VERDADEIRO atribuido ao modulo
    # ERRADO. E' a classe "numero real, so era o numero de outra coisa" — a mesma que criou este
    # canario — e ele nao a pegava.
    # os numeros medidos saem da propria familia, nao do escopo de quem chama
    por_canario = next((v for _p, v, _r in familias if isinstance(v, dict)), {})
    _pol, _base = por_canario.get("politica"), por_canario.get("base")
    if _pol is not None and _base is not None and _pol != _base:
        trocado = _bate(f"O canario test_controle_base.py roda {_pol} verificações.", familias)
        checar("auto-teste: numero certo no modulo ERRADO e' pego", _pol in trocado,
               "-> conferir pertencimento a um conjunto nao e' conferir correspondencia")
        checar("auto-teste: numero certo no modulo certo passa",
               not _bate(f"O canario test_controle_base.py roda {_base} verificações.", familias))
    # [ACHADO ALTA DO QA RODADA 11] "list" casava dentro de "lista", palavra corriqueira em
    # portugues, e um numero CERTO da politica era acusado de errado. Falso positivo — e o
    # cabecalho deste arquivo diz que falso positivo e' pior que canario ausente.
    if _pol is not None:
        # a palavra-armadilha tem de estar MAIS PERTO do numero que a atribuicao correta — senao
        # a escolha por proximidade ja acerta sozinha e o teste nao prova nada. A prova de mutacao
        # acusou isso: com o substring reintroduzido o canario continuava verde.
        armadilha = _bate(f"O canario test_controle_projeto.py confere cada item da lista e roda "
                          f"{_pol} verificações.", familias)
        checar("auto-teste: a palavra 'lista' NAO rouba a atribuicao da politica", not armadilha,
               f"-> acusou {armadilha}; 'list' casava dentro de 'lista' por substring")
        # [ACHADO ALTA DO QA RODADA 12] a fronteira era ASCII pura, entao letra ACENTUADA contava
        # como fronteira e "listável" reabria o falso positivo. Num canario que audita prosa em
        # portugues, ignorar acento e' ignorar o alfabeto do texto.
        for palavra in ("listável", "listagem", "listão", "alistá-lo"):
            checar(f"auto-teste: {palavra!r} nao rouba a atribuicao",
                   not _bate(f"O canario test_controle_projeto.py deixa o item {palavra} e roda "
                             f"{_pol} verificações.", familias),
                   "-> acento nao pode virar fronteira de palavra num texto em portugues")
        checar("auto-teste: 'checklist' tambem nao rouba",
               not _bate(f"O canario test_controle_projeto.py segue o checklist e roda "
                         f"{_pol} verificações.", familias))
    if _base is not None:
        checar("auto-teste: a palavra 'List' de verdade continua atribuindo",
               _bate(f"A List do SharePoint. O canario test_controle_base.py roda "
                     f"{_base + 1} verificações.", familias),
               "-> consertar o falso positivo nao pode cegar o caso legitimo")
    # [ACHADO ALTA DO QA RODADA 13] o cabecalho do ADR-113 dizia "9 correcoes provadas por
    # mutacao" enquanto o mecanismo declarava 34, e o gate deixou passar porque procurava a
    # palavra `defeito`. Numero estale escapando pelo SINONIMO. Estes casos provam que a familia
    # agora cobre os dois substantivos, e que o numero certo continua passando nos dois.
    _mut = next((sorted(v)[0] for p, v, _r in familias
                 if "por muta" in p and not isinstance(v, dict)), None)
    if _mut is not None:
        for palavra in ("defeitos", "correções", "correcoes"):
            checar(f"auto-teste: numero errado em '{palavra} provadas por mutacao' e' pego",
                   _mut + 1 in _bate(f"O pacote teve {_mut + 1} {palavra} provadas por mutação.",
                                     familias),
                   "-> o gate procurava a palavra, nao o numero; sinonimo era rota de fuga")
            checar(f"auto-teste: numero certo em '{palavra}' continua passando",
                   not _bate(f"O pacote teve {_mut} {palavra} provadas por mutação.", familias),
                   "-> ampliar o padrao nao pode criar falso positivo")

    sem_fonte = _bate("Aqui ela vive uma vez, com 42 verificações.", familias)
    checar("auto-teste: numero de verificacoes SEM atribuicao e' pego", 42 in sem_fonte,
           "-> numero que nao diz de onde vem nao da' para conferir, e nao deve ser afirmado")
    checar("auto-teste: sabotagem inventada tambem e' pega", 77 in achou)
    limpo = _bate("A primeira redação dizia 99999 verificações, e estava errado.", familias)
    checar("auto-teste: mencao historica NAO e' acusada", 99999 not in limpo,
           "-> sem isto o texto nao poderia citar o numero errado ao explicar o erro")
    # [ACHADO MEDIA DO QA RODADA 4] o caso que o auto-teste anterior NAO cobria: numero atual e
    # errado PERTO de uma frase historica, mas em outra frase. A moldura virava esconderijo.
    vizinho = _bate("A primeira redação dizia um numero antigo que nao vem ao caso agora. "
                    "Hoje sao 99999 verificações, valor atual deste paragrafo.", familias)
    checar("auto-teste: moldura historica em OUTRA frase nao protege numero atual",
           99999 in vizinho,
           "-> bastaria escrever 'a primeira redacao dizia' antes para esconder numero errado")


def main() -> int:
    textos = prosa()
    checar("os documentos do pacote foram encontrados", len(textos) >= 4,
           f"-> achei {sorted(textos)}; se a lista esvaziar, este canario vira carimbo")
    checar("o bloco ADR-113 existe no CHANGELOG", "CHANGELOG.md" in textos,
           "-> sem o bloco nao ha o que conferir, e passar assim seria carimbo")

    print("\nMedindo a realidade (rodando os canarios de verdade):")
    n_pol, sab_pol = medir("test_controle_projeto.py")
    n_list, _ = medir("test_controle_sharepoint.py")
    # [reabertura do desenho 21/08/2026] a fronteira virou bloco proprio; sem medi-la aqui, o
    # numero dela na prosa ficaria sem gate — que e' exatamente o buraco que este canario existe
    # para nao ter.
    n_base, _ = medir("test_controle_base.py")
    # quantas mutacoes a prova declara — o numero da prosa passa a sair daqui, medido, em vez de
    # ser contado a mao. [achado MEDIA do QA rodada 8]
    import importlib.util as _iu
    _spec = _iu.spec_from_file_location("_mut", RAIZ / "tools" / "test_mutacao_controle.py")
    _mod = _iu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    n_mut = len(_mod.MUTACOES)
    nucleo = RAIZ.parent / "migracao-sac" / "tools" / "nucleo.py"
    n_nucleo = len(nucleo.read_text(encoding="utf-8").splitlines()) if nucleo.is_file() else None
    print(f"  fronteira: {n_base} verificacoes")
    print(f"  mutacoes declaradas: {n_mut}")
    print(f"  politica: {n_pol} verificacoes, {sab_pol} sabotagens")
    print(f"  List:     {n_list} verificacoes")
    print(f"  nucleo.py: {n_nucleo if n_nucleo is not None else 'nao encontrado (projeto ausente)'}")
    checar("o canario da politica executa alguma coisa", n_pol > 0,
           "-> zero verificacoes significa que ele quebrou e este canario nao pode confiar nele")
    checar("o canario da List executa alguma coisa", n_list > 0)
    checar("o canario da fronteira executa alguma coisa", n_base > 0)

    # Cada familia: o padrao que a acha na prosa, e o valor medido que ela tem de citar.
    familias = [
        # dicionario, e nao conjunto: o teste passa a exigir que a prosa diga DE QUEM e' o numero,
        # e confere contra aquele canario. [ACHADO ALTA DO QA RODADA 10]
        (r"(\d+) verifica\w*", {"base": n_base, "politica": n_pol, "sharepoint": n_list},
         f"verificacoes (medido: fronteira={n_base}, politica={n_pol}, List={n_list})"),
        (r"(\d+) (?:por|delas por) sabotagem", {sab_pol}, f"sabotagens (medido: {sab_pol})"),
        # [ACHADO ALTA DO QA RODADA 13] o padrao exigia a palavra literal `defeito`, e o cabecalho
        # do ADR-113 dizia "9 correcoes provadas por mutacao": numero estale que furou o gate PELA
        # PALAVRA, nao pelo valor. E' o irmao do achado da rodada 11 ("list" dentro de "lista") —
        # a familia se defende do valor errado e nao do sinonimo. Agora cobre os dois substantivos
        # e a concordancia (provados/provadas).
        (r"(\d+) (?:defeitos?|correc\w+|correç\w+) provad\w+ por muta", {n_mut},
         f"mutacoes (medido: {n_mut})"),
    ]
    if n_nucleo is not None:
        familias.append((r"`nucleo\.py` \((\d+)\)", {n_nucleo}, f"linhas de nucleo.py ({n_nucleo})"))
        familias.append((r"nucleo\.py.{0,30}?(\d+) linhas", {n_nucleo}, f"linhas de nucleo.py ({n_nucleo})"))

    print("\nO detector ainda enxerga? (auto-teste, com texto sintetico)")
    auto_teste(familias)

    print("\nTodo numero destas familias na prosa bate com o medido?")
    # UM caminho so: o mesmo `divergencias` que o auto-teste exercita. [QA rodada 5]
    for nome, texto in sorted(textos.items()):
        ruins = divergencias(texto, familias)
        checar(f"{nome}: os numeros conferem", not ruins,
               "; ".join(f"a prosa diz {v} ({rot}), o repositorio diz {ok}; trecho: ...{trecho}..."
                         for v, rot, ok, trecho in ruins[:3]))

    print("\nAfirmacao que nao da' para verificar de dentro nao pode ser feita:")
    for nome, texto in sorted(textos.items()):
        for padrao, por_que in NAO_AFIRMAVEL:
            vivos = [m for m in re.finditer(padrao, texto) if not _e_historico(texto, m.start())]
            checar(f"{nome} nao afirma {padrao!r}", not vivos, f"-> {por_que}")

    print("\nNumero ja refutado nao pode voltar como afirmacao:")
    for nome, texto in sorted(textos.items()):
        for padrao, por_que in REFUTADOS:
            vivos = [m for m in re.finditer(padrao, texto) if not _e_historico(texto, m.start())]
            checar(f"{nome} sem {padrao!r}", not vivos, f"-> {por_que}")

    print("\nO QUE ESTE CANARIO NAO COBRE, dito de proposito: contagem de linhas de diff (-490/+207/")
    print("-283), numero de arquivos, datas, e qualquer numero fora das familias acima. Esses")
    print("dependem de quem escreve. Prometer cobertura que o mecanismo nao tem foi exatamente o")
    print("defeito que o QA rodada 3 achou na versao anterior deste bloco.")

    print()
    if falhou:
        print(f"FAIL — {len(falhou)} verificacao(oes) falharam: {falhou}")
        return 1
    print(f"PASS — os numeros da prosa batem com o medido, e nenhum numero refutado voltou.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
