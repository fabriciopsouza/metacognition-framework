#!/usr/bin/env python3
"""Canário de marketing ancorado em evidência (ADR-044 + ADR-059).

Prova:
(a) LIMITS.md em sync com os canários (build_limits --check);
(b) todo claim PROVADO do LIMITS aponta para um canário que EXISTE (zero ✅ órfão);
(c) nenhum doc de marketing (README + prompt web) carrega '✅ PROVADO' sem referência a canário;
(d) README linka o LIMITS.md;
(e) [ADR-059 G1 — fail-closed] o prompt web é DERIVADO de `web_export.PUBLIC_SRC` (fonte única) e
    EXISTE; há exatamente 1 `PROMPT-CHAT-WEB-v*.md` em disco e ele == PUBLIC_SRC. Mata o bug do
    skip silencioso por versão fixa defasada (antes apontava `v4.3` inexistente -> `continue`);
(f) [ADR-059 G2] a vitrine (`guia/web/index.html`) tem ZERO overclaim (absoluto-sem-hedge);
(g) [ADR-059 G3] a vitrine DISCLOSA os limites residuais (não pode overclaim E esconder o limite);
(i) a prosa PUBLICA que alega um CASO aponta onde conferir — mesma vara do (b), agora para
    narrativa e não só para claim PROVADO (gap medido em 19/08/2026: caso inventado na vitrine).

Uso: python tools/test_marketing_claims.py   (exit 0 PASS; 1 se qualquer gate falha)
"""
import glob
import os
import re
import sys

try:  # stdout UTF-8: Windows usa cp1252 e quebra no emoji ✅ (lição recorrente do incidente)
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import argparse  # noqa: E402
import io  # noqa: E402
from build_limits import CLAIMS, build, INTERNAL_ONLY  # noqa: E402
import web_export  # noqa: E402  (import-safe: main() só roda sob __main__)
from overclaim_lexicon import find_overclaims  # noqa: E402

VITRINE = os.path.join(ROOT, "guia", "web", "index.html")
WEB_PROMPT_RE = re.compile(r"PROMPT-CHAT-WEB-v.*\.md$")


UNIDADES = ("zero", "um", "dois", "tres", "quatro", "cinco", "seis", "sete",
            "oito", "nove", "dez", "onze", "doze", "treze", "quatorze", "quinze",
            "dezesseis", "dezessete", "dezoito", "dezenove")
DEZENAS = ("", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta",
           "setenta", "oitenta", "noventa")


def por_extenso(n: int, zero: str = "nenhuma") -> str:
    """O numero como ele aparece na frase de reconciliacao da vitrine.

    Existe para que a frase e o gate que a confere saiam da MESMA fonte. Antes,
    a frase era escrita a mao e o gate trazia um dicionario fixo de grafias:
    duas listas para manter em sincronia, e em 16/09/2026 a frase publicava
    'cinquenta e nove' numa arvore onde o numero medido era 57.

    `zero` e' parametro porque a frase diz "nenhuma declarada sem prova", nao
    "zero declaradas".
    """
    if n == 0:
        return zero
    if n < 20:
        return UNIDADES[n]
    if n < 100:
        dez, resto = divmod(n, 10)
        return DEZENAS[dez] + (f" e {UNIDADES[resto]}" if resto else "")
    if n == 100:
        return "cem"
    centos, resto = divmod(n, 100)
    cabeca = "cento" if centos == 1 else f"{UNIDADES[centos]}centos"
    return cabeca + (f" e {por_extenso(resto, zero)}" if resto else "")


def frase_de_reconciliacao(total, provadas, fc_sem_prova, fracos, sem_campo) -> str:
    """A frase publicada. UMA fonte para o texto e para a conferencia."""
    return (f"A conta fecha em <b>{total}</b>: {por_extenso(provadas)} provadas, "
            f"{por_extenso(fc_sem_prova)} declarada sem prova, "
            f"{por_extenso(fracos)} com proteção mais fraca, "
            f"{por_extenso(sem_campo)} sem declaração.")


def contar_vitrine(caps):
    """Numeros que a secao #provas da vitrine tem de afirmar. Extraida de main() para que a
    fixture abaixo exercite a MESMA contagem que roda contra o registry real."""
    from audit_enforcement import valida_mutacao  # local: o import de main() nao alcanca aqui
    total = len(caps)
    provadas = sum(1 for c in caps
                   if c.get("mutacao") and valida_mutacao(c["mutacao"], c)[0])
    fc_sem_prova = sum(1 for c in caps
                       if c.get("enforcement") == "fail-closed" and not c.get("mutacao"))
    sem_campo = sum(1 for c in caps if not c.get("enforcement"))
    fracos = total - provadas - fc_sem_prova - sem_campo
    conformes = sum(1 for c in caps if c.get("enforcement")
                    and (c.get("enforcement") != "fail-closed" or c.get("mutacao")))
    return {"total": total, "provadas": provadas, "fc_sem_prova": fc_sem_prova,
            "sem_campo": sem_campo, "fracos": fracos, "conformes": conformes}


def autoteste_contagem():
    """Registry sintetico com UMA capacidade de cada classe — a contagem tem de separa-las.

    A fixture `e` tem o campo `mutacao` preenchido mas ESTRUTURALMENTE invalido (o `arquivo`
    nao e' o `mechanism` da capacidade), e `valida_mutacao` a recusa. E' ela que separa
    'provada' de 'tem o campo mutacao': sem ela, uma contagem ingenua que nunca chamasse
    `valida_mutacao` passaria identica — medido pelo qa-critic em 2026-08-18, que reescreveu
    a funcao sem a validacao e obteve o MESMO resultado. Era canario cego, a classe que o
    proprio ADR-106 existe para proibir.
    """
    falhas = []
    fake = [
        {"id": "a", "enforcement": "fail-closed", "mechanism": "tools/x.py",
         "test": "tools/test_x.py",
         "mutacao": {"arquivo": "tools/x.py", "de": "A", "para": "B",
                     "canario": "tools/test_x.py", "espera": "mensagem suficientemente longa"}},
        {"id": "b", "enforcement": "fail-closed"},
        {"id": "c", "enforcement": "advisory"},
        {"id": "d"},
        # tem `mutacao`, mas o `arquivo` nao e o `mechanism` -> valida_mutacao RECUSA.
        # Conta como protecao mais fraca, nunca como provada.
        {"id": "e", "enforcement": "fail-closed", "mechanism": "tools/y.py",
         "test": "tools/test_y.py",
         "mutacao": {"arquivo": "tools/OUTRO.py", "de": "A", "para": "B",
                     "canario": "tools/test_y.py", "espera": "mensagem suficientemente longa"}},
    ]
    n = contar_vitrine(fake)
    # `e` NAO pode entrar em `provadas` (mutacao invalida) nem em `fc_sem_prova` (tem o
    # campo). Cai em `fracos`, que e o resto — e e por isso que `fracos` sobe de 1 para 2.
    esperado = {"total": 5, "provadas": 1, "fc_sem_prova": 1, "sem_campo": 1,
                "fracos": 2, "conformes": 3}
    for k, v in esperado.items():
        if n[k] != v:
            falhas.append(f"contagem '{k}' = {n[k]}, esperado {v} — a vitrine publicaria "
                          f"um numero errado sem ninguem notar")
    if n["provadas"] + n["fc_sem_prova"] + n["sem_campo"] + n["fracos"] != n["total"]:
        falhas.append("as quatro classes nao somam o total — a conta da pagina nao fecha")
    return falhas



# --- (i) PROCEDENCIA DE AFIRMACAO NARRATIVA -------------------------------------------------
# Gap medido em 19/08/2026: o autor INVENTOU um caso ("pediram a um agente uma extracao de dados
# ... tres nomes de campo nao existiam") e o pos na vitrine PUBLICA em tempo de fato consumado.
# Nenhum canario podia pegar: (f) caca overclaim LEXICO (promessa absoluta) e caso fabricado e' o
# oposto — modesto, plausivel, especifico. Ironia registrada: o lexico tem como frase PROIBIDA
# "O framework jamais inventa nomes de campo", e a fabricacao foi um caso SOBRE isso.
#
# O PRINCIPIO nao e' novo — (b) ja exige que todo claim PROVADO aponte para um canario que
# existe — mas o MECANISMO aqui e' novo e independente: (b) valida o PAR claim-canario via
# CLAIMS; este so verifica presenca de ponteiro. Chamar isso de "apenas estender (b)" seria
# enquadramento generoso, e o QA de juncao apontou a generosidade: em linhas, e' adicao. A
# justificativa e' de SUBSTANCIA, nao de forma — um incidente medido em que conteudo
# fabricado chegou a prosa publica e nenhum gate existente podia ve-lo (regua §0 porta c:
# destrava um eval que nao existia, e o eval reprovou no ato de ser ligado).
# Aqui a mesma regra vale para CASO: se a prosa publica alega que algo aconteceu, ela diz onde
# conferir. Padrao declarado ("alucina nomes de campo com confianca") NAO e' alegacao de caso e
# passa — a pagina precisa poder descrever comportamento sem citar processo.
#
# LIMITE DECLARADO, e ESPECIFICO — limite vago e' sobre-promessa disfarcada. O QA de juncao de
# 19/08/2026 executou as fugas; ficam nomeadas em vez de resumidas num "nao pega tudo":
#   (1) abertura sem gatilho lexical: "Em um projeto recente, o agente..." — escapa;
#   (2) invencao embutida no meio da frase, sem abrir a sentenca — escapa;
#   (3) conjugacao fora da lista: "Um cliente PEDIU uma extracao" (singular, voz ativa) — escapa.
#       NAO ampliado de proposito: "pediu" solto casa com prosa legitima ("o dono pediu que...") e
#       o falso positivo custa mais que a fuga, dado o modelo de ameaca abaixo;
#   (4) FONTE DECORATIVA: qualquer ponteiro citado no bloco satisfaz TEM_FONTE, mesmo sem
#       relacao nenhuma com o caso — arquivo .md, URL solta, ADR-NNN solto, 'decisao 109'.
#       O QA de juncao testou os quatro e todos lavam. Vale tambem via bloco SEGUINTE. E' bar mais fraco que o do gate (b), que valida o PAR claim-canario. Aceito
#       porque o alvo e' o AUTOR DESATENTO — que inventa sem perceber e nao cola fonte falsa — e
#       nao um adversario. Contra adversario este gate nao serve, e dizer o contrario seria mentira.
# A calibragem estreita e' deliberada (decisao do dono, 19/08/2026): detector de linguagem natural
# com falso positivo vira gate desligado, e gate desligado protege menos que gate estreito.
# ESCOPO: vitrine + prompt web. README nao e' varrido — hoje nao tem trecho que dispare, e ampliar
# sem necessidade medida e' o oposto da regua §0. Se um caso aparecer la, entra aqui.
ABRE_CASO = re.compile(
    r"(?i)\b("
    r"um caso concreto|um caso real|certo caso|um exemplo real|um caso pratico|um caso pr[áa]tico|"
    r"certa vez|uma vez,|houve um caso|aconteceu que|"
    r"pediram a|pediu-se a|solicitaram a|"
    r"num[a]? (sess[ãa]o|projeto|cliente|empresa|reposit[óo]rio) (real|espec[íi]fic)"
    r")\b")

# o que conta como FONTE: arquivo do repo, ADR, canario, ou link — a mesma vara de (b)
# [QA de juncao 19/08/2026, achado ALTA] a 1a versao reconhecia QUATRO formatos de fonte e
# reprovava prosa honesta que citasse de qualquer outro jeito: "ver secao 09", link markdown sem
# extensao, "decisao 109" sem o prefixo ADR. O critico executou os quatro. Gate que reprova o certo
# e' desligado por quem tem pressa — e este arquivo ja carrega essa licao em outro achado. A vara
# passa a ser "aponta para ALGUM lugar conferivel", nao "cita no formato que eu previ".
TEM_FONTE = re.compile(
    r"(?i)("
    r"\b[\w./-]+\.(md|py|json|html|yml|yaml|txt)\b|"        # arquivo citado
    r"\b(ADR|RFC)[-\s]?\d+\b|"                              # decisao registrada, por sigla
    r"\bdecis(ao|ão|oes|ões)\s+n?[ºo°]?\s*\d+|"             # ...ou por extenso
    r"\[fonte:|\]\(|\bhttps?://|"                           # link (marcador, markdown, url)
    r"\bver\s+(a|o|as|os)?\s*"                               # ponteiro explicito, generico:
    r"(se(c|ç)(ao|ão)|cap(itulo|ítulo)|anexo|hist[óo]ri[ac]|"   # "ver secao 9", "ver o anexo B"...
    r"history|CHANGELOG|LIMITS|ledger|registro|veredito)"
    r")")


def _paragrafos(texto_visivel: str):
    """Blocos separados por linha em branco — a unidade em que a fonte pode morar."""
    return [b for b in re.split(r"\n\s*\n", texto_visivel) if b.strip()]


def casos_sem_procedencia(texto_visivel: str):
    """Devolve [(trecho, motivo)] de paragrafos que ABREM um caso e nao dizem onde conferir.

    [QA de juncao 19/08/2026] a fonte vale no bloco do caso OU no bloco imediatamente seguinte —
    "caso num paragrafo, nota-fonte no proximo" e' padrao de escrita comum e honesto, e exigir os
    dois no mesmo bloco reprovava texto correto. Nao vale dois blocos adiante: a partir dai a fonte
    deixa de estar visivel junto da afirmacao, que e' o ponto.
    """
    blocos = _paragrafos(texto_visivel)
    achados = []
    for k, bloco in enumerate(blocos):
        m = ABRE_CASO.search(bloco)
        if not m:
            continue
        vizinhanca = bloco + "\n" + (blocos[k + 1] if k + 1 < len(blocos) else "")
        if TEM_FONTE.search(vizinhanca):
            continue
        trecho = re.sub(r"\s+", " ", bloco).strip()
        achados.append((trecho[:120], f"abre caso em {m.group(0)!r} e nao aponta fonte"))
    return achados


def autoteste_procedencia():
    """Prova o detector contra o caso REAL que ele deveria ter pego, e contra prosa honesta.
    Sem isto o gate seria mais uma promessa nao verificada — a classe que este repo mede."""
    fabricado = ("Um caso concreto, para sair do abstrato: pediram a um agente uma extracao de "
                 "dados de um sistema corporativo. Ele devolveu um script coerente, com nomes de "
                 "campo plausiveis - e tres deles nao existiam naquele sistema.")
    # [QA de juncao 19/08/2026] os quatro primeiros sao FALSOS POSITIVOS que o critico executou
    # contra a versao anterior: prosa honesta que citava a fonte fora do formato previsto, ou no
    # bloco seguinte. Ficam aqui como regressao — voltar a reprova-los reprova o canario.
    honestos = [
        "Um caso real regulado validado com delta 0.000000, ver a secao 09.",
        "Um caso real: o agente inventou campos. [confira aqui](https://exemplo.com/casos/1)",
        "Certa vez o critico reprovou o autor, conforme decisao 109.",
        "Um caso concreto aconteceu aqui.\n\nFonte: docs/adr/110-decisao.md",
        "Um caso real regulado validado com delta 0.000000 contra o baseline, ver COMO-FOI-CONSTRUIDO.md.",
        "Alucina nomes de campo, sintaxe e regras com confianca - e voce so descobre depois.",
        "O runner recusa arquivo que passaria sem executar assercao alguma.",
        "Certa vez o critico reprovou o autor, conforme docs/adr/110-decisao.md.",
    ]
    fails = []
    if not casos_sem_procedencia(fabricado):
        fails.append("o detector NAO pega o caso fabricado que motivou este gate (19/08/2026)")
    for h in honestos:
        if casos_sem_procedencia(h):
            fails.append(f"falso positivo em prosa honesta: {h[:60]!r}")
    return fails


def main(argv=None):
    """`--corrigir` grava na vitrine os numeros MEDIDOS, em vez de reprovar.

    Sem a bandeira o comportamento e' o de sempre: so' verifica. A gravacao e'
    para quem acabou de mexer na arvore (autor, ou o `export-clean.py` sobre a
    copia exportada) — nunca automatica dentro de um gate.
    """
    args = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    args.add_argument("--corrigir", action="store_true",
                      help="grava na vitrine a contagem medida nesta arvore")
    corrigir = args.parse_args(
        (argv if argv is not None else sys.argv[1:])).corrigir
    fails = 0

    def gate(ok, desc):
        nonlocal fails
        print(f"{'OK  ' if ok else 'FAIL'} {desc}")
        if not ok:
            fails += 1

    # (e) ADR-059 G1 — prompt web DERIVADO de web_export.PUBLIC_SRC + fail-closed (anti skip silencioso)
    src = web_export.PUBLIC_SRC
    src_base = os.path.basename(src)
    src_exists = os.path.isfile(src)
    on_disk = sorted(f for f in os.listdir(ROOT) if WEB_PROMPT_RE.search(f))
    gate(src_exists, f"prompt web (PUBLIC_SRC={src_base}) existe [fail-closed, não skip]")
    gate(on_disk == [src_base],
         f"exatamente 1 PROMPT-CHAT-WEB-v*.md e == PUBLIC_SRC (anti-drift; on_disk={on_disk})")

    marketing_docs = [os.path.join(ROOT, "README.md")] + ([src] if src_exists else [])

    # (a) LIMITS.md em sync com os canários
    target = os.path.join(ROOT, "LIMITS.md")
    in_sync = os.path.isfile(target) and open(target, encoding="utf-8-sig").read().strip() == build().strip()
    gate(in_sync, "LIMITS.md em sync com os canários (build_limits)")

    # (b) todo claim PROVADO aponta para canário existente (interno não conta — roda na fonte/CI)
    orphan = [c for c, canary, *_ in CLAIMS
              if canary not in INTERNAL_ONLY and not os.path.isfile(os.path.join(ROOT, "tools", canary))]
    gate(not orphan, f"todo claim do LIMITS aponta p/ canário existente "
                     f"({'zero órfão' if not orphan else orphan})")

    # (c) nenhum '✅ PROVADO' órfão em marketing — agora RODA no prompt web real (F1 destrava)
    seal = []
    for p in marketing_docs:
        for i, line in enumerate(open(p, encoding="utf-8-sig").read().splitlines(), 1):
            if "✅" in line and re.search(r"provado", line, re.IGNORECASE):
                if "tools/test_" not in line and "LIMITS.md" not in line:
                    seal.append(f"{os.path.basename(p)}:{i}")
    gate(not seal, f"sem selo PROVADO órfão em marketing ({'nenhum' if not seal else seal})")

    # (d) README linka o LIMITS.md
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8-sig").read()
    gate("LIMITS.md" in readme, "README linka o LIMITS.md")

    # (f) ADR-059 G2 — vitrine sem overclaim (absoluto-sem-hedge)
    if not os.path.isfile(VITRINE):
        gate(False, f"vitrine ausente: {VITRINE} [fail-closed]")
    else:
        vtext = open(VITRINE, encoding="utf-8-sig").read()
        low = vtext.lower()
        vio = find_overclaims(vtext, strip_html=True)
        gate(not vio, f"vitrine sem overclaim ({'nenhum' if not vio else [f'{lab}:{hit}' for lab, hit, _ in vio]})")

        # (g) ADR-059 G3 — disclosure REAL de alucinação residual (proximidade, anti-teatro: 'residual'
        # solto noutra seção não conta — achado MÉD-1 do qa-critic).
        discloses = re.search(r"alucina\w*\s+residual|residual[^.]{0,30}alucina", low) is not None
        gate(discloses, "vitrine disclosa alucinação residual (proximidade real, anti-teatro)")

        # (h) ADR-059 — vitrine não cita prompt web inexistente (anti drift de LINK; achado ALTO-1).
        refs = set(re.findall(r"PROMPT-CHAT-WEB-v[\d.]+\.md", vtext))
        dead = sorted(r for r in refs if not os.path.isfile(os.path.join(ROOT, r)))
        gate(not dead, f"vitrine sem link de prompt morto ({'nenhum' if not dead else dead})")

        # (i) ADR-059 — versão de release citada na vitrine == main (anti drift de VERSÃO; achado ALTO-2).
        mv = web_export.main_version()
        rel = set(re.findall(r"(?:releases/tag/|archive/refs/tags/)v(\d+\.\d+\.\d+)", vtext))
        rel |= set(re.findall(r"<b>\s*v?(\d+\.\d+\.\d+)\s*</b>", vtext))
        stale = sorted(v for v in rel if v != mv)
        gate(mv != "0.0.0" and not stale,
             f"versões de release na vitrine == main v{mv} (stale={stale or 'nenhum'})")

    print("-" * 60)
    # (g) OS NUMEROS DA VITRINE SAO OS DO REPO, E SIGNIFICAM O QUE A PAGINA DIZ.
    #
    # A 1a versao desta checagem tinha DOIS defeitos, os dois achados pelo qa-critic (Sonnet,
    # 2026-08-17), e o primeiro era grave:
    #
    # (i) a pagina afirmava "38 de 89 capacidades tiveram o mecanismo SABOTADO de proposito". O
    #     numero batia com o auditor, mas a FRASE era falsa para 27 delas: "em conformidade" conta
    #     tambem quem declara protecao nao-bloqueante, sem sabotagem nenhuma. So' 11 tem `mutacao`.
    #     Era overclaim mecanizado — na pagina inicial do repo que existe para combater overclaim.
    #     Agora a vitrine separa os dois numeros e diz o que cada um mede.
    #
    # (ii) a comparacao era `substring in arquivo inteiro`, cega a contexto: a string dentro de um
    #      comentario HTML satisfazia o gate enquanto o numero VISIVEL estava errado. Agora os
    #      comentarios sao removidos e a busca acontece SO' dentro da secao `#provas`.
    #
    # A fórmula de "conforme" e' IMPORTADA do auditor, nao copiada: duplicar a regra faria este
    # canario validar contra uma versao velha dela sem ninguem perceber — o mesmo defeito que o
    # `test_qa_evidence` tinha e que foi corrigido na v1.85.0.
    if os.path.isfile(VITRINE):
        import json as _json
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        from audit_enforcement import valida_mutacao  # noqa: E402
        try:
            _caps = _json.load(open(os.path.join(ROOT, "capabilities.json"), encoding="utf-8"))
            _caps = _caps.get("capabilities", _caps)
            _n = contar_vitrine(_caps)
            total, provadas = _n["total"], _n["provadas"]
            fc_sem_prova, sem_campo = _n["fc_sem_prova"], _n["sem_campo"]
            fracos, conformes = _n["fracos"], _n["conformes"]
            for _f in autoteste_contagem():
                gate(False, f"auto-teste da contagem da vitrine: {_f}")
            canarios = len(glob.glob(os.path.join(ROOT, "tools", "test_*.py")))
            # O numero de canarios e' um denominador que o PROPRIO ciclo
            # alimenta: todo bloco novo acrescenta `tools/test_*.py`. Mantido a
            # mao, ele envelhece a cada commit e o gate fica vermelho por
            # desatualizacao, nao por defeito — foi o que aconteceu em
            # 16/09/2026 (pagina 88, arvore 89, pacote publico 87).
            #
            # E sao DOIS numeros legitimos, para duas plateias: a arvore de
            # desenvolvimento tem canarios que NAO viajam para o pacote
            # (`test_core_agnostic.py`, `test_premium_tier.py` testam a propria
            # maquinaria de export). Por isso a correcao nao e' escolher um
            # numero: e' GERAR, em cada arvore, como o `build_limits.py` ja'
            # faz para o LIMITS.md — mesma medicao, dois resultados corretos.
            if corrigir:
                trocas = (
                    (r"<b>\d+ de \d+</b> capacidades",
                     f"<b>{provadas} de {total}</b> capacidades"),
                    (r"\d+ canários", f"{canarios} canários"),
                    (r"<b>\d+</b> ainda não", f"<b>{sem_campo}</b> ainda não"),
                    (r"<b>\d+</b> declaram", f"<b>{fracos}</b> declaram"),
                    (r"A conta fecha em <b>\d+</b>:.{0,220}?\.",
                     frase_de_reconciliacao(total, provadas, fc_sem_prova,
                                            fracos, sem_campo)),
                    (r"<b>\d+ de \d+</b> de", f"<b>{conformes} de {total}</b> de"),
                )
                novo = vtext
                for padrao, troca in trocas:
                    novo = re.sub(padrao, troca.replace("\\", "\\\\"), novo,
                                  count=1, flags=re.S)
                if novo != vtext:
                    io.open(VITRINE, "w", encoding="utf-8",
                            newline="\n").write(novo)
                    print(f"     vitrine: {provadas}/{total} provadas · "
                          f"{canarios} canários · {fracos} fracas · "
                          f"{conformes}/{total} conformes")
                    vtext = novo
        except Exception as e:
            gate(False, f"nao consegui derivar os numeros da vitrine: {e}")
        else:
            visivel = re.sub(r"<!--.*?-->", "", vtext, flags=re.S)
            m = re.search(r'id="provas".*?</section>', visivel, re.S)
            secao = m.group(0) if m else ""
            gate(bool(secao), "vitrine sem a secao #provas — os numeros nao tem onde morar")
            for valor, oquee in ((f"{provadas} de {total}", "capacidades com sabotagem provada"),
                                 (f"{canarios} canários", "canarios na suite"),
                                 (f"{fc_sem_prova} capacidades", "declaram bloquear e nao foram provadas"),
                                 (f"<b>{sem_campo}</b>", "sem declaracao de protecao"),
                                 (f"<b>{fracos}</b>", "protecao nao-bloqueante"),
                                 (f"{conformes} de {total}", "em conformidade no registro")):
                gate(valor in secao,
                     f"a secao #provas nao afirma '{valor}' ({oquee}) — numero da pagina divergiu "
                     f"do repo, ou saiu da secao; atualize guia/web/index.html")

            # [ACHADO ALTA DO QA DO ADR-114] as checagens acima conferem PRESENCA de cada
            # substring, uma por uma. Elas passavam com a pagina se contradizendo DENTRO da mesma
            # frase: "A conta fecha em 97: ... trinta e nove ..." convivia com "98 de 98" logo ao
            # lado, porque as duas substrings certas existiam em OUTRO ponto da secao. Presenca nao
            # e' coerencia. A frase de reconciliacao e' uma CONTA, e passa a ser conferida como tal.
            # Derivado de `por_extenso`, nao digitado: um dicionario fixo de
            # grafias e' uma segunda lista para manter em sincronia, e listas
            # paralelas derivam. A checagem continua valendo — ela confere se o
            # numero ESCRITO e' um dos MEDIDOS, e isso independe de quem grafou.
            POR_EXTENSO = {por_extenso(n): n for n in range(0, 200)}
            mrec = re.search(r"A conta fecha em <b>(\d+)</b>:(.{0,220}?)\.", secao, re.S)
            gate(mrec is not None,
                 "a frase 'A conta fecha em <b>N</b>: ...' sumiu da secao #provas — sem ela esta "
                 "checagem vira decoracao; reancore o padrao ou remova a checagem")
            if mrec:
                gate(int(mrec.group(1)) == total,
                     f"a frase de reconciliacao diz que a conta fecha em {mrec.group(1)}, mas o "
                     f"registro tem {total} capacidades")
                corpo = mrec.group(2)
                # Por PALAVRA INTEIRA e pelo casamento MAIS LONGO. `n in corpo`
                # era comparacao por substring: "cinquenta e nove" contem
                # "cinquenta" e contem "nove", e a frase passava a ser acusada
                # de citar 50 e 9. O mapa escrito a mao nao expunha isso porque
                # so' trazia grafias longas — o defeito estava na comparacao, e
                # so' apareceu quando o mapa deixou de ser curado a mao.
                alternativas = "|".join(re.escape(n) for n in
                                        sorted(POR_EXTENSO, key=len, reverse=True))
                achados = {m2.group(1): POR_EXTENSO[m2.group(1)] for m2 in
                           re.finditer(rf"\b({alternativas})\b", corpo)}
                gate(bool(achados),
                     "a frase de reconciliacao nao tem numero por extenso reconhecivel — se a "
                     "redacao mudou, atualize POR_EXTENSO; senao esta checagem nao mede nada")
                for nome, valor in achados.items():
                    gate(valor in (provadas, fracos, fc_sem_prova, sem_campo),
                         f"a frase de reconciliacao diz '{nome}' ({valor}), que nao e' nenhum dos "
                         f"numeros medidos (provadas={provadas}, fracos={fracos}, "
                         f"fc_sem_prova={fc_sem_prova}, sem_campo={sem_campo})")

    # (i) procedencia de afirmacao NARRATIVA na prosa publica (vitrine + prompt web)
    for _f in autoteste_procedencia():
        gate(False, f"auto-teste do detector de procedencia narrativa: {_f}")
    # [QA de juncao r2, 19/08/2026] o auto-teste acima prova a FUNCAO; NAO provava a FIACAO.
    # O critico demonstrou em copia: trocando este laco por uma tupla vazia — sem tocar em
    # casos_sem_procedencia nem no auto-teste — o caso fabricado injetado na vitrine passava
    # batido, com o gate reportando PASS. Detector perfeito ligado a lista vazia reporta PASS
    # para sempre. E' o mesmo modo de falha que este arquivo ja registra ter causado o bug do
    # gate (e) (skip silencioso). O contador abaixo fecha isso: se nada foi varrido, reprova.
    _varridos = 0
    for _rot, _caminho in (("vitrine", VITRINE), ("prompt web", src)):
        if not os.path.isfile(_caminho):
            continue
        _varridos += 1
        with open(_caminho, encoding="utf-8") as _fh:
            _bruto = _fh.read()
        _vis = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", _bruto, flags=re.S | re.I)
        _vis = re.sub(r"<!--.*?-->", " ", _vis, flags=re.S)
        # [autocorrecao 19/08/2026] a 1a versao apagava as tags ANTES de procurar a fonte,
        # entao todo `href` sumia para a funcao que o procurava: o detector reprovava frase
        # que TINHA link. O link vira marcador textual e sobrevive a limpeza.
        _vis = re.sub(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>', r' [fonte:\1] ',
                      _vis, flags=re.I)
        # paragrafo em HTML e' BLOCO, nao linha em branco: separa pelos fechamentos de bloco
        _vis = re.sub(r'</(p|li|div|section|h[1-6])>', '\n\n', _vis, flags=re.I)
        _vis = re.sub(r"<[^>]+>", " ", _vis)
        _achados = casos_sem_procedencia(_vis)
        gate(not _achados,
             f"{_rot}: {len(_achados)} trecho(s) alegam um CASO sem dizer onde conferir — "
             f"prosa publica que afirma fato precisa apontar fonte, como todo claim PROVADO ja "
             f"precisa apontar canario. {_achados[:2]}")

    gate(_varridos >= 1,
         f"o detector de procedencia varreu {_varridos} arquivo(s) reais — zero significa que a"
         f" fiacao quebrou e o gate virou carimbo: ele reportaria PASS sem olhar nada")

    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (marketing+vitrine ancorados: LIMITS sync · zero órfão · prompt web fail-closed · "
               "vitrine sem overclaim · limites disclosos)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
