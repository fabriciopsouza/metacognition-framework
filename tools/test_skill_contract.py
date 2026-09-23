#!/usr/bin/env python3
"""Canario do CONTRATO DE SKILL (ADR-013) — liga um validador que estava dormente.

GAP fechado: `tools/validate_skills.py` existia, passava, e **nada o executava** — nem o
`ci.yml`, nem o `run_canaries.py`. Um validador de contrato que ninguem invoca e' documentacao
com sintaxe colorida: nao impede nada. Medido em 2026-08-18, ao migrar o passivo do ADR-106
(a capacidade `skill-contract` nao declarava `enforcement` porque nao havia canario nenhum).

Prova as duas direcoes, que e' o que torna a capacidade PROVAVEL (ADR-106):
  (a) o conjunto REAL de skills do repo passa;
  (b) frontmatter quebrado e' PEGO — fixtures sinteticas para cada classe de violacao.
Sem (b), este canario seria indistinguivel de um canario cego: varreria, nao acharia nada e
ficaria verde, exatamente como os 8 casos `mechanism == test` migrados no v1.88.0.

Uso: python tools/test_skill_contract.py   (exit 0 PASS; 1 se falha)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import validate_skills as vs  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _erros(frontmatter, schema):
    """Roda o MESMO caminho do validador real: parse do frontmatter + schema."""
    data, err = vs.extract_frontmatter(frontmatter)
    if err:
        return [err]
    return vs.validate_against_schema(data, schema)


def autoteste(schema):
    """Fixtures que este canario e OBRIGADO a acertar."""
    falhas = []
    # Fixture VALIDA: precisa carregar o contrato INTEIRO (8 campos obrigatorios). Escrever
    # so `name`+`description` fazia o caso (a) reprovar por incompletude e mascarar o que ele
    # existe para medir — falso-positivo do proprio canario, pego na 1a execucao.
    bom = ("---\n"
           "name: skill-de-teste\n"
           "description: Skill sintetica usada so pelo canario do contrato.\n"
           "role_order: null\n"
           "consumes: []\n"
           "produces: [artefato-de-teste]\n"
           "pass_criteria: o canario roda e devolve verde\n"
           "confidence_required: false\n"
           "shared_refs: []\n"
           "---\n\n# Corpo\n")

    if _erros(bom, schema):
        falhas.append(f"skill VALIDA foi reprovada (falso-positivo): {_erros(bom, schema)}")

    sem_fm = "# Sem frontmatter nenhum\n\ntexto\n"
    if not _erros(sem_fm, schema):
        falhas.append("arquivo SEM frontmatter passou — o contrato deixou de existir")

    fm_aberto = "---\nname: x\ndescription: y\n\n# esqueceu de fechar\n"
    if not _erros(fm_aberto, schema):
        falhas.append("frontmatter NAO FECHADO passou — parse aceita documento truncado")

    sem_name = ("---\n"
                "description: Skill sem o campo name, que e obrigatorio.\n"
                "---\n\n# Corpo\n")
    if not _erros(sem_name, schema):
        falhas.append("skill sem `name` passou — campo obrigatorio deixou de ser exigido")

    sem_desc = "---\nname: skill-sem-descricao\n---\n\n# Corpo\n"
    if not _erros(sem_desc, schema):
        falhas.append("skill sem `description` passou — e' o campo que decide o auto-trigger")
    return falhas


# ---------------------------------------------------------------------------------
# WORKFLOWS: procedencia da sigla e classe de efeito (debito `canario-para-workflows`)
# ---------------------------------------------------------------------------------
WORKFLOWS_DIR = os.path.join(ROOT, ".agent", "workflows")

# Quem DEFINE cada sigla. Fonte: docs/adr/011-qa-bicelular-... (juncoes J0-J5 e o
# process-critic) e docs/adr/045-pmo-maestro-reorquestracao-... (J6).
DONO_DA_SIGLA = {
    "J0": "011", "J1": "011", "J2": "011", "J3": "011", "J4": "011", "J5": "011",
    "J6": "045", "PROCESS-CRITIC": "011",
}
# `re.I` porque "Process-critic" no inicio de frase e' portugues normal, nao ofuscacao —
# e sem isto a frase do bug real escapava das DUAS checagens so' por comecar maiuscula.
# [achado MEDIA do qa-critic, 23/09/2026]
_RE_SIGLA = re.compile(r"\bJ[0-6]\b|process-critic", re.I)
_RE_EFEITO = re.compile(r"\bE([1-6])\b")
# Vocabulario de REVERSIBILIDADE, usado dos DOIS lados: para descobrir quais classes de
# efeito falam disso (lendo action-safety) e se a LINHA do workflow fala disso.
_RE_REVERSIVEL = re.compile(
    r"revers|irrevers|idempot|destr[o\u00f3u]|irrecuper|perde\s+dados", re.I)
# Uma linha que NEGA tratar de reversibilidade nao pode ser cobrada como se tratasse.
# [achado MEDIA do qa-critic: "NAO fala de reversibilidade" era flagado por engano]
_RE_NEGA_ASSUNTO = re.compile(
    r"n[a\u00e3]o\s+(?:fala|trata|[e\u00e9])\s+(?:de\s+|sobre\s+)?revers", re.I)
# O conjunto que a fonte deve produzir HOJE. NAO e' usado para julgar workflow — quem julga
# continua sendo a derivacao. E' um canario SOBRE a derivacao: se a fonte mudar de um jeito
# que altere o conjunto, isto reprova ALTO em vez de a checagem ficar silenciosamente mais
# permissiva. [achado ALTA do qa-critic: bastava a palavra "irreversivel" aparecer na
# definicao de E3 para E3 virar classe de reversibilidade, com PASS e exit 0]
REVERSIBILIDADE_CANONICA = {"E1", "E2"}


def classes_de_reversibilidade(caminho=None):
    """(todas, reversiveis) lidas de `_shared/action-safety/SKILL.md`.

    Derivado da fonte, nunca cravado: se as classes forem renumeradas, o julgamento segue
    junto em vez de virar a segunda fonte de verdade. A trava contra deriva silenciosa esta'
    no autoteste, comparando com REVERSIBILIDADE_CANONICA.
    """
    caminho = caminho or os.path.join(ROOT, "_shared", "action-safety", "SKILL.md")
    try:
        texto = open(caminho, encoding="utf-8-sig").read()
    except OSError:
        return set(), set()
    todas, reversiveis = set(), set()
    for linha in texto.splitlines():
        m = re.match(r"\s*[-*]\s*\*{0,2}(E[1-6])\*{0,2}\s*[\u2014-]\s*(.+)", linha)
        if not m:
            continue
        classe, definicao = m.group(1), m.group(2)
        todas.add(classe)
        if _RE_REVERSIVEL.search(definicao):
            reversiveis.add(classe)
    return todas, reversiveis


def conferir_workflows(dirpath=None, todas=None, reversiveis=None):
    """Problemas encontrados nos workflows. Lista vazia = OK."""
    dirpath = dirpath or WORKFLOWS_DIR
    if todas is None or reversiveis is None:
        todas, reversiveis = classes_de_reversibilidade()
    problemas = []
    if not os.path.isdir(dirpath):
        return problemas
    for nome in sorted(os.listdir(dirpath)):
        if not nome.endswith(".md"):
            continue
        try:
            texto = open(os.path.join(dirpath, nome), encoding="utf-8-sig").read()
        except OSError as e:
            problemas.append(f"{nome}: ilegivel ({e})")
            continue
        texto_alto = texto.upper()

        # (1) PROCEDENCIA DA SIGLA, no arquivo. Fraca de proposito — e' um PISO: exige que a
        # fonte seja mencionada em algum lugar. Teria pego os dois bugs reais de 21/09, que
        # nao citavam ADR nenhuma. O caso forte vem em (1b).
        for bruta in set(_RE_SIGLA.findall(texto)):
            sigla = bruta.upper()
            adr = DONO_DA_SIGLA.get(sigla)
            if adr and f"ADR-{adr}" not in texto_alto:
                problemas.append(
                    f"{nome}: cita `{bruta}` e nao cita ADR-{adr}, que e' quem o define — "
                    f"sigla sem procedencia foi como a conflacao 'process-critic de J6' entrou")

        # (1b) CONFLACAO NA MESMA LINHA. O achado MEDIA do qa-critic mostrou que (1) e'
        # ganhavel: basta citar as duas ADRs num rodape sem relacao. Entao a frase que
        # EQUIPARA duas siglas de ADRs diferentes e' cobrada por LINHA, e so' passa se a
        # propria linha citar as duas fontes — ai' quem le ve que sao coisas distintas.
        for n, linha in enumerate(texto.splitlines(), 1):
            donos = {DONO_DA_SIGLA.get(s.upper()) for s in _RE_SIGLA.findall(linha)}
            donos.discard(None)
            if len(donos) > 1:
                alto = linha.upper()
                faltando = [f"ADR-{d}" for d in sorted(donos) if f"ADR-{d}" not in alto]
                if faltando:
                    problemas.append(
                        f"{nome}:{n}: a linha junta siglas de ADRs diferentes e nao cita "
                        f"{faltando} NELA — e' a forma exata da conflacao 'process-critic de "
                        f"J6', que fazia corte de GATE parecer corte de CERIMONIA")

        # (2) CLASSE DE EFEITO CONTRA A DEFINICAO VIVA.
        for n, linha in enumerate(texto.splitlines(), 1):
            citadas = {"E" + g for g in _RE_EFEITO.findall(linha)}
            if not citadas:
                continue
            inexistentes = citadas - todas if todas else set()
            if inexistentes:
                problemas.append(
                    f"{nome}:{n}: cita {sorted(inexistentes)}, que nao existe(m) em "
                    f"_shared/action-safety/SKILL.md")
            if not reversiveis or _RE_NEGA_ASSUNTO.search(linha):
                continue
            if _RE_REVERSIVEL.search(linha) and not (citadas & reversiveis):
                problemas.append(
                    f"{nome}:{n}: a linha fala de reversibilidade e cita "
                    f"{sorted(citadas)}, mas quem define reversibilidade em action-safety "
                    f"e' {sorted(reversiveis)}")
    return problemas


# Contado da fonte, nunca digitado: cada chamada de `so(...)` em autoteste_workflows
# monta um workflow e afere um caso. Ver o comentario em main().
CASOS_AUTOTESTE_WORKFLOW = 7


def autoteste_workflows():
    """Fixtures que este canario e' OBRIGADO a acertar — os DOIS bugs reais de 21/09, mais
    as regressoes que o qa-critic levantou em 23/09."""
    import tempfile
    falhas = []
    todas, reversiveis = classes_de_reversibilidade()
    if not todas:
        return ["nao consegui ler as classes de efeito de _shared/action-safety/SKILL.md — "
                "sem a fonte este canario nao mede nada e nao pode dizer OK"]

    # TRAVA CONTRA DERIVA SILENCIOSA [achado ALTA]. A derivacao continua mandando no
    # julgamento; o que esta linha impede e' ela mudar sem ninguem ver.
    if reversiveis != REVERSIBILIDADE_CANONICA:
        falhas.append(
            f"a derivacao mudou: action-safety agora produz {sorted(reversiveis)} como classes "
            f"de reversibilidade, e o canonico e' {sorted(REVERSIBILIDADE_CANONICA)}. Ou a fonte "
            f"foi reformulada de proposito (entao atualize REVERSIBILIDADE_CANONICA e diga por "
            f"que), ou uma edicao de prosa contaminou o conjunto e a checagem ficou mais "
            f"permissiva EM SILENCIO")

    with tempfile.TemporaryDirectory(prefix="wf-fx-") as d:
        def so(nome, conteudo):
            for velho in os.listdir(d):
                os.remove(os.path.join(d, velho))
            with open(os.path.join(d, nome), "w", encoding="utf-8") as fh:
                fh.write(conteudo)
            return conferir_workflows(d, todas, reversiveis)

        # BUG REAL 1 — conflacao sem citar nenhum dos dois ADRs
        if not any("procedencia" in p for p in so(
                "conflacao.md", "# quick\n\nO que corta: o process-critic de J6.\n")):
            falhas.append("a conflacao 'process-critic de J6' SEM citar ADR-011/045 passou")

        # BUG REAL 1, so' com maiuscula diferente [achado MEDIA]
        if not any("procedencia" in p for p in so(
                "caixa.md", "# quick\n\nProcess-Critic de J6 fica de fora.\n")):
            falhas.append("a mesma conflacao escrita 'Process-Critic' escapou — falta re.I")

        # CONFLACAO BLINDADA por citacao fora de contexto [achado MEDIA]
        if not any("conflacao" in p for p in so(
                "blindada.md", "# quick\n\nO passo final corta o process-critic de J6.\n\n"
                               "Notas sem relacao: ver ADR-045 e ADR-011 sobre outro assunto.\n")):
            falhas.append("a conflacao passou so' porque as ADRs apareciam num rodape "
                          "descolado — a checagem por linha nao mordeu")

        # SIGLA COM O ADR ERRADO [achado BAIXA]
        if not any("ADR-045" in p for p in so(
                "adr-errado.md", "# x\n\nJ6 encerra o bloco, conforme ADR-011.\n")):
            falhas.append("J6 citando so' ADR-011 passou — o dono da sigla e' o ADR-045")

        # BUG REAL 2 — reversibilidade citando a classe errada
        if not any("reversibilidade" in p for p in so(
                "efeito.md", "# quick\n\n| 4 | e' reversivel (sem E5/E6) |\n")):
            falhas.append("o gatilho dizendo que reversibilidade e' E5/E6 passou")

        # NEGACAO nao pode ser cobrada [achado MEDIA]
        ruido = so("negacao.md", "# x\n\nEste paragrafo nao fala de reversibilidade, "
                                 "apenas cita E5 por outro motivo.\n")
        if any("reversibilidade" in p for p in ruido):
            falhas.append(f"linha que NEGA tratar de reversibilidade foi acusada: {ruido}")

        # CONTROLE NEGATIVO
        ruido = so("ok.md", "# quick\n\nCorta J6 (ADR-045); o process-critic do ADR-011 fica.\n"
                            "Reversivel: sem E1 nem E2 do action-safety.\n")
        if ruido:
            falhas.append(f"workflow CORRETO foi acusado (falso-positivo): {ruido}")
    return falhas


def main():
    schema = vs.load_schema()
    falhas_canario = autoteste(schema)

    # (a) o conjunto REAL do repo — o validador rodando pela primeira vez dentro da suite
    reais, ruins = 0, []
    for path in vs.glob_default():
        reais += 1
        try:
            texto = open(path, encoding="utf-8-sig").read()
        except OSError as e:
            ruins.append(f"{os.path.relpath(path, ROOT)}: ilegivel ({e})")
            continue
        for e in _erros(texto, schema):
            ruins.append(f"{os.path.relpath(path, ROOT)}: {e}")

    print(f"skill-contract: {reais} skill(s) do repo validadas — "
          f"{'OK' if not ruins else 'FAIL'}")
    for r in ruins:
        print("  -", r)
    print(f"auto-teste do validador (5 fixtures) — {'OK' if not falhas_canario else 'FAIL'}")
    for f in falhas_canario:
        print("  -", f)
    # (c) workflows: procedencia da sigla e classe de efeito contra a definicao viva
    wf_ruins = conferir_workflows()
    wf_falhas = autoteste_workflows()
    print(f"workflows: {len(wf_ruins)} problema(s) — "
          f"{'OK' if not wf_ruins else 'FAIL'}")
    for r in wf_ruins:
        print("  -", r)
    # O numero sai da CONTAGEM, nao de um literal que envelhece. A 1a versao dizia "3
    # fixtures" e passaram a ser 7 depois do QA de 23/09 — rotulo afirmando sobre si mesmo
    # algo que deixou de ser verdade, que e' a classe exata que este bloco persegue.
    print(f"auto-teste do validador de workflow ({CASOS_AUTOTESTE_WORKFLOW} fixtures) — "
          f"{'OK' if not wf_falhas else 'FAIL'}")
    for f in wf_falhas:
        print("  -", f)
    print("-" * 50)
    if ruins or falhas_canario or wf_ruins or wf_falhas:
        print(f"RESULTADO: FAIL ({len(ruins)} skill(s) fora do contrato, "
              f"{len(falhas_canario)} falha(s) do proprio validador, "
              f"{len(wf_ruins)} problema(s) de workflow, "
              f"{len(wf_falhas)} falha(s) do validador de workflow)")
        return 1
    print("RESULTADO: PASS (contrato de skill e de workflow vigentes; os dois validadores provados contra fixture)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
