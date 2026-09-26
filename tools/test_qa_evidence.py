#!/usr/bin/env python3
"""Canario qa-evidence (ADR-074 emenda 2, parte FAIL-CLOSED no master): o release ATUAL (versao do
topo do CHANGELOG) DEVE ter um artefato de veredito qa-critic APROVATIVO em `_meta/qa/*.json` com
`release == <versao>`. Mecaniza "o qa-critic rodou no bloco" — antes era disciplina/prosa minha
(maior debito de processo admitido em 2026-06-07).

Shadow-aware (espelha test_dev_dogfood, ADR-070): docs/_private ausente + repo_identity != master
-> PASS (so master desenvolve e fecha bloco com qa-critic). Master degradado (sem _private mas
git=master) NAO e isento.

FORWARD-ONLY (regua §0): so gateia o release atual — nao exige artefato qa p/ as versoes historicas
(que nunca tiveram artefato; fabricar seria desonesto, mesma doutrina do test_release_checkpoint).

APROVATIVO = recomendacao em {aprovar, aprovar_com_ressalvas}. Um veredito "corrigir"/"reverter"
NAO fecha release (forca o fix + re-review antes do release) — exatamente o fluxo correto.

Uso: python tools/test_qa_evidence.py   (exit 0 PASS; 1 se falha)
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA_DIR = os.path.join(ROOT, "_meta", "qa")

# APPROVING vem do MECANISMO, nao de uma copia local. A 1a versao redefinia o conjunto aqui — o
# canario tinha a propria copia da regra e, por isso, NAO dependia do codigo que devia guardar:
# alterar `APPROVING` em `qa_evidence.py` para aceitar "reprovar" nao deixava este canario
# vermelho. Teste que duplica a regra em vez de importa-la nao testa nada; confirma a si mesmo.
# Medido em 2026-08-16 ao sabotar a capacidade `qa-evidence-gate` e ver o verde persistir.
sys.path.insert(0, os.path.join(ROOT, "tools"))
from qa_evidence import APPROVING  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _is_genuine_shadow():
    """Este gate cobre artefato COMMITADO (_meta/qa, versionado) — DIFERENTE do test_dev_dogfood
    (que cobre docs/_private, cofre LOCAL gitignored). Logo NAO pode usar 'docs/_private ausente'
    como sinal de shadow: na CI do PROPRIO master docs/_private esta ausente (gitignored) mas
    _meta/qa esta presente -> o gate DEVE disparar. Pula SO em shadow POSITIVO (repo_identity=
    SOMBRA-EXPORT, carimbado por export-clean). Default = ENFORCE. (Falha de design pega na
    auto-revisao 2026-06-08: o sinal docs/_private faria o gate nunca disparar na CI do master.)"""
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import repo_identity
        if repo_identity.is_export_shadow():
            return True, "repo_identity.is_export_shadow (carimbo shadow + commit de export) — shadow legitimo"
    except Exception:
        pass
    return False, "nao-shadow (enforce — so export-shadow genuino pula; anti-forja)"


def _test_junction_ledger():
    """Casos do ledger de juncoes (P3/P4, ADR-077) — self-contained em tempdir, nao toca o repo."""
    import tempfile
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import qa_evidence
    fails = []
    with tempfile.TemporaryDirectory() as td:
        saved = qa_evidence.QA_DIR
        qa_evidence.QA_DIR = td
        try:
            def expect_ok(label, **kw):
                try:
                    qa_evidence.append_junction("bloco-t", **kw)
                except ValueError as e:
                    fails.append(f"{label}: recusou indevidamente ({e})")

            def expect_fail(label, **kw):
                try:
                    qa_evidence.append_junction("bloco-t", **kw)
                    fails.append(f"{label}: aceitou indevidamente (deveria recusar)")
                except ValueError:
                    pass

            expect_ok("J0 inicial", junction="J0", artefato="a", evidencia="PASS: e")
            expect_ok("J1 forward", junction="J1", artefato="a", evidencia="PASS: e")
            expect_ok("J1 repetida (within-junction)", junction="J1", artefato="a", evidencia="round 2")
            expect_fail("J0 regressao sem rewind", junction="J0", artefato="a", evidencia="e")
            expect_ok("J0 com rewind explicito", junction="J0", artefato="a", evidencia="e", rewind=True)
            expect_fail("J3 sem validation/justificativa", junction="J3", artefato="a", evidencia="e")
            expect_ok("J3 com justificativa", junction="J3", artefato="a", evidencia="e",
                      justificativa="doc-only, sem codigo executavel")
            expect_fail("juncao invalida", junction="J9", artefato="a", evidencia="e")
            expect_fail("evidencia vazia", junction="J4", artefato="a", evidencia="  ")
            led = os.path.join(td, "junctions", "bloco-t.jsonl")
            # corrupcao -> fail-closed (nao zera forward-only em silencio)
            with open(led, "a", encoding="utf-8") as f:
                f.write("{nao-e-json\n")
            expect_fail("ledger corrompido recusa append", junction="J4", artefato="a", evidencia="e")
            with open(led, encoding="utf-8") as f:
                good = [x for x in f if x.strip() and not x.startswith("{nao")]
            with open(led, "w", encoding="utf-8") as f:
                f.writelines(good)
            if not os.path.isfile(led):
                fails.append("ledger jsonl nao foi criado")
            else:
                lines = [json.loads(x) for x in open(led, encoding="utf-8") if x.strip()]
                if len(lines) != 5:
                    fails.append(f"ledger com {len(lines)} linhas (esperado 5 registros aceitos)")
        finally:
            qa_evidence.QA_DIR = saved
    for f in fails:
        print("  - [junction-ledger]", f)
    print(f"junction-ledger (P3/P4 ADR-077): {'OK (10 casos)' if not fails else 'FAIL'}")
    return not fails


def _test_circuit_breaker():
    """Circuit breaker do laço de QA (ADR-118) — tempdir, não toca o repo nem o registro de trabalhos
    (`write_artifact` não declara débito; quem declara é o `main` da linha de comando)."""
    import tempfile
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import qa_evidence
    fails = []

    def veredito(bloco, rec, rodada, achados=("ALTA|a.py",), **extra):
        v = {"bloco": bloco, "passou": rec in qa_evidence.APPROVING, "recomendacao": rec,
             "rodada": rodada, "data": f"2026-09-25T0{rodada}:00:00Z", "verificacoes_executadas": ["x"],
             "problemas": [{"severidade": a.split("|")[0], "local": a.split("|")[1],
                            "descricao": f"achado {i}", "estado": "aberto"}
                           for i, a in enumerate(achados)]}
        v.update(extra)
        return v

    def grava(v):
        try:
            qa_evidence.write_artifact(v)
            return "ok"
        except ValueError as e:
            return str(e)

    with tempfile.TemporaryDirectory() as td:
        saved = qa_evidence.QA_DIR
        qa_evidence.QA_DIR = td
        try:
            # D1: 3 reprovações seguidas (achados diferentes) -> a 4ª é recusada
            for r, a in ((1, "ALTA|a.py"), (2, "ALTA|b.py"), (3, "ALTA|c.py")):
                if grava(veredito("d1", "corrigir", r, (a,))) != "ok":
                    fails.append(f"D1: rodada {r} recusada antes do limite")
            if "CIRCUIT BREAKER" not in grava(veredito("d1", "corrigir", 4, ("ALTA|d.py",))):
                fails.append("D1: 4ª rodada após 3 reprovações foi ACEITA")
            if grava(veredito("d1", "corrigir", 4, ("ALTA|d.py",), redesenho="uma implementação só, os instaladores só chamam")) != "ok":
                fails.append("D1: rodada com redesenho registrado foi recusada")
            if grava(veredito("d1", "corrigir", 5, ("ALTA|e.py",))) != "ok":
                fails.append("D1: o redesenho não reiniciou a contagem")
            # D2: 2 reprovações seguidas com os MESMOS achados -> a 3ª é recusada
            grava(veredito("d2", "corrigir", 1, ("ALTA|x.py",)))
            grava(veredito("d2", "corrigir", 2, ("ALTA|x.py",)))
            if "sem progresso" not in grava(veredito("d2", "corrigir", 3, ("ALTA|y.py",))):
                fails.append("D2: 3ª rodada após 2 rodadas sem progresso foi ACEITA")
            if grava(veredito("d2", "corrigir", 3, ("ALTA|y.py",),
                              override_dono="sem limite de rodadas de QA, 25/09/2026")) != "ok":
                fails.append("D2: ordem do dono registrada foi recusada")
            # aprovação SEMPRE entra, mesmo com o breaker armado (achado CRÍTICO de 26/09)
            for r in (1, 2, 3):
                grava(veredito("ap2", "corrigir", r, (f"ALTA|{r}.py",)))
            if grava(veredito("ap2", "aprovar", 4, ())) != "ok":
                fails.append("aprovação recusada com o breaker armado (ela é que encerra o laço)")
            # destravar exige conteúdo: 'x' não é redesenho nem ordem do dono
            for r in (1, 2, 3):
                grava(veredito("tri", "corrigir", r, (f"ALTA|{r}.py",)))
            if "CIRCUIT BREAKER" not in grava(veredito("tri", "corrigir", 4, ("ALTA|z.py",), override_dono="x")):
                fails.append("override_dono='x' (sem data) destravou o breaker")
            if "CIRCUIT BREAKER" not in grava(veredito("tri", "corrigir", 4, ("ALTA|z.py",), redesenho="mudei")):
                fails.append("redesenho trivial destravou o breaker")
            if "CIRCUIT BREAKER" not in grava(veredito("tri", "corrigir", 4, ("ALTA|z.py",), redesenho="x" * 25)):
                fails.append("redesenho de uma palavra repetida destravou o breaker")
            if "CIRCUIT BREAKER" not in grava(veredito("tri", "corrigir", 4, ("ALTA|z.py",),
                                                       override_dono="ordem do dono, 99/99/9999")):
                fails.append("override com data impossível (99/99/9999) destravou o breaker")
            # LIMITE DECLARADO (ADR-118): o destravamento prova forma, não conteúdo. Estes passam de
            # propósito; se um dia deixarem de passar, o ADR tem de ser atualizado junto.
            for r in (1, 2, 3):
                grava(veredito("lim", "corrigir", r, (f"ALTA|{r}.py",)))
            if grava(veredito("lim", "corrigir", 4, ("ALTA|z.py",), redesenho="ab cd ef gh ab cd ef gh")) != "ok":
                fails.append("limite declarado mudou: redesenho de tokens curtos passou a ser recusado (atualize o ADR-118)")
            # aprovação no meio zera a sequência
            grava(veredito("ap", "corrigir", 1, ("ALTA|a.py",)))
            grava(veredito("ap", "corrigir", 2, ("ALTA|b.py",)))
            grava(veredito("ap", "aprovar_com_ressalvas", 3, ("BAIXA|c.py",)))
            if grava(veredito("ap", "corrigir", 4, ("ALTA|d.py",))) != "ok":
                fails.append("aprovação no meio não zerou a sequência de reprovações")
            # a reprovação que dispara é GRAVADA (nunca se perde)
            hist = json.load(open(os.path.join(td, "d1.json"), encoding="utf-8")).get("substitui") or []
            if len(hist) < 4:
                fails.append(f"histórico de d1 com {len(hist)} rodadas (reprovações sumiram)")
        finally:
            qa_evidence.QA_DIR = saved
    for f in fails:
        print("  - [circuit-breaker]", f)
    print(f"circuit-breaker (ADR-118): {'OK (14 casos)' if not fails else 'FAIL'}")
    return not fails


def conferir_cadeia():
    """A cadeia do ledger acumula atraves de VARIAS regravacoes? (falhas).

    POR QUE TRES E NAO DUAS: com duas gravacoes o defeito NAO aparece — uma
    cadeia de profundidade 1 parece correta. Ele so' se revela na terceira,
    quando o elo mais antigo deveria continuar la'. Foi exatamente por testar
    com duas que o autor afirmou "testado ponta a ponta" sobre um mecanismo
    quebrado, e foi o QA adversarial de 17/09/2026 que mediu a terceira.

    O defeito: `historico = list(verdict.get("substitui") or [])` lia o campo do
    veredito que ENTRA — sempre vazio, porque o qa-critic nao carrega historico
    — em vez do campo do ANTERIOR, onde o elo antigo mora. Como o arquivo e'
    reescrito inteiro, a rodada 1 desaparecia na 3a gravacao. Num bloco com 30
    rodadas, o artefato final mostraria um unico elo.
    """
    import json
    import tempfile
    import qa_evidence

    falhas = []
    antes = qa_evidence.QA_DIR
    qa_evidence.QA_DIR = tempfile.mkdtemp(prefix="cadeia-")
    try:
        base = dict(bloco="bloco-da-cadeia", papel="qa_critic", passou=False,
                    data="2026-09-17T00:00:00Z", escopo_paths=["a.py"],
                    problemas=[], verificacoes_executadas=["rodou"],
                    atestacao={"agentId": "a1", "modelo": "sonnet",
                               "autor": "opus", "isolamento": "subagente"})
        caminho = None
        for rodada, decisao in ((1, "reprovar"), (2, "reprovar"), (3, "aprovar")):
            caminho, _md = qa_evidence.write_artifact(
                dict(base, rodada=rodada, recomendacao=decisao,
                     resumo=f"rodada {rodada}", passou=(decisao == "aprovar")))

        final = json.load(open(caminho, encoding="utf-8"))
        cadeia = final.get("substitui") or []
        rodadas = [a.get("rodada") for a in cadeia]
        if rodadas != [1, 2]:
            falhas.append(f"a cadeia perdeu historico: esperava [1, 2], veio {rodadas}")
        if not all(a.get("recomendacao") for a in cadeia):
            falhas.append("antecedente sem `recomendacao` — o campo obrigatorio do schema")
        if final.get("substitui_reprovacao") is not True:
            falhas.append("aprovativo que substitui REPROVACAO nao se declarou")

        md = open(caminho[:-5] + ".md", encoding="utf-8").read()
        if "Substitui vereditos anteriores" not in md:
            falhas.append("a cadeia existe no JSON e some no .md, que e' o que humano le")
        elif "REPROVACAO" not in md:
            falhas.append("o .md nao destaca que houve reprovacao substituida")
    finally:
        qa_evidence.QA_DIR = antes
    return falhas


def conferir_substitui_malformado():
    """JSON ja' gravado com `substitui` fora do schema tem de RECUSAR, nao mesclar.

    O fail-open: `list(anterior.get("substitui") or [])` aceita uma STRING e a
    fragmenta em caracteres, sem erro naquela linha. O crash so' aparecia depois,
    em `render_md` — e a essa altura o `json.dump` JA' TINHA GRAVADO a corrupcao,
    porque ele roda antes. Cada regravacao fazia a lista de fragmentos crescer, e
    o `.md` ficava permanentemente desatualizado.

    Este arquivo ja' tinha aprendido a licao com `problemas`; ela nao foi
    generalizada para `substitui`. [achado do QA de 17/09/2026]
    """
    import json
    import os
    import tempfile
    import qa_evidence

    falhas = []
    antes = qa_evidence.QA_DIR
    qa_evidence.QA_DIR = tempfile.mkdtemp(prefix="malformado-")
    try:
        base = dict(bloco="bloco-corrompido", papel="qa_critic", passou=False,
                    data="2026-09-17T00:00:00Z", escopo_paths=["a.py"], problemas=[],
                    verificacoes_executadas=["rodou"], recomendacao="reprovar",
                    resumo="r1", rodada=1,
                    atestacao={"agentId": "a1", "modelo": "sonnet",
                               "autor": "opus", "isolamento": "subagente"})
        caminho, _ = qa_evidence.write_artifact(dict(base))

        for rotulo, veneno in (("string", "nao sou lista"),
                               ("lista de nao-dicts", ["x", 3])):
            disco = json.load(open(caminho, encoding="utf-8"))
            disco["substitui"] = veneno
            json.dump(disco, open(caminho, "w", encoding="utf-8"), ensure_ascii=False)
            antes_bytes = os.path.getsize(caminho)
            try:
                qa_evidence.write_artifact(dict(base, rodada=2, recomendacao="aprovar",
                                                passou=True, resumo="r2"))
                falhas.append(f"`substitui` como {rotulo} foi ACEITO — deveria recusar")
            except ValueError as erro:
                if "substitui" not in str(erro):
                    falhas.append(f"recusou {rotulo}, mas sem dizer o campo: {erro}")
            except Exception as erro:
                falhas.append(f"{rotulo} quebrou com {type(erro).__name__}, nao com ValueError")
            if os.path.getsize(caminho) != antes_bytes:
                falhas.append(f"o ledger foi ESCRITO mesmo com {rotulo} invalido — "
                              f"recusar depois de gravar nao adianta")

        # e o veredito que ENTRA com `substitui` torto tambem e' recusado
        try:
            qa_evidence.write_artifact(dict(base, bloco="outro", substitui="torto"))
            falhas.append("`substitui` invalido no veredito que ENTRA foi aceito")
        except ValueError:
            pass
    finally:
        qa_evidence.QA_DIR = antes
    return falhas


def conferir_carimbo_de_blobs():
    """`write_artifact` carimba `blobs_revisados`, e normaliza o separador do caminho.

    Duas garantias, e a segunda e' a que quase escapou (ALTA da 37a rodada): `git rev-parse
    :tools\\x.py` nao resolve contra o indice, e a funcao caia no fallback que le o DISCO.
    Num arquivo com staged diferente do disco, o carimbo gravado seria o do conteudo NAO
    revisado — carimbar uma coisa e commitar outra, em silencio, do lado de quem escreve a
    prova.
    """
    import json
    import tempfile
    import qa_evidence

    falhas = []
    alvo = "tools/squad_gate.py"
    esperado = qa_evidence._blob_indexado(alvo)
    if not esperado:
        return falhas                      # sem git utilizavel; nao inventa resultado

    antes = qa_evidence.QA_DIR
    qa_evidence.QA_DIR = tempfile.mkdtemp(prefix="carimbo-")
    try:
        base = dict(bloco="bloco-do-carimbo", papel="qa_critic", passou=True,
                    recomendacao="aprovar", problemas=[], verificacoes_executadas=["rodou"],
                    resumo="r1", rodada=1,
                    atestacao={"agentId": "a1", "modelo": "sonnet",
                               "autor": "opus", "isolamento": "subagente"})

        caminho, _ = qa_evidence.write_artifact(dict(base, escopo_paths=[alvo]))
        d = json.load(open(caminho, encoding="utf-8"))
        b = d.get("blobs_revisados")
        if not isinstance(b, dict) or not b:
            falhas.append("write_artifact nao carimbou `blobs_revisados`")
        elif b.get(alvo) != esperado:
            falhas.append(f"carimbou {b.get(alvo)!r}, esperado {esperado!r} (hash do INDICE)")

        # o MESMO caminho escrito com barra invertida tem de produzir o MESMO carimbo,
        # e a CHAVE tem de sair normalizada — senao o leitor nunca a encontra e o veredito
        # bloqueia para sempre, empurrando para --no-verify.
        invertida = alvo.replace("/", chr(92))
        caminho2, _ = qa_evidence.write_artifact(
            dict(base, bloco="bloco-do-carimbo-2", escopo_paths=[invertida]))
        d2 = json.load(open(caminho2, encoding="utf-8"))
        b2 = d2.get("blobs_revisados") or {}
        if alvo not in b2:
            falhas.append(f"chave nao foi normalizada: {sorted(b2)} (esperava {alvo!r})")
        elif b2.get(alvo) != esperado:
            falhas.append("barra invertida carimbou hash diferente da barra normal — "
                          "o fallback leu o DISCO em vez do indice")
    finally:
        qa_evidence.QA_DIR = antes
    return falhas


def main():
    falhas_cadeia = (conferir_cadeia() + conferir_substitui_malformado()
                     + conferir_carimbo_de_blobs())
    for f in falhas_cadeia:
        print(f"  FAIL cadeia do ledger: {f}")
    if falhas_cadeia:
        print("RESULTADO: FAIL (a cadeia de vereditos nao preserva a historia)")
        return 1
    print("  ok   a cadeia do ledger acumula por 3 gravacoes e aparece no .md")

    shadow, why = _is_genuine_shadow()
    if shadow:
        print(f"{why}. PASS (shadow — nao cobra artefato qa-critic).")
        print("RESULTADO: PASS (shadow — sem cobranca de qa-evidence)")
        return 0

    try:
        chg = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8-sig").read()
    except Exception as e:
        print(f"RESULTADO: FAIL (CHANGELOG ilegivel: {e})")
        return 1
    vers = re.findall(r"(?m)^## \[(\d+\.\d+\.\d+)\]", chg)
    if not vers:
        print("RESULTADO: FAIL (nenhuma versao no CHANGELOG)")
        return 1
    latest = vers[0]

    if not os.path.isdir(QA_DIR):
        print(f"_meta/qa/ ausente — release v{latest} sem evidencia qa-critic")
        print("RESULTADO: FAIL (release sem artefato qa-critic — rode qa_evidence.py com o veredito)")
        return 1

    approving = []
    for jf in glob.glob(os.path.join(QA_DIR, "*.json")):
        try:
            v = json.load(open(jf, encoding="utf-8"))
        except Exception:
            continue
        if str(v.get("release", "")) == latest and v.get("recomendacao") in APPROVING:
            approving.append(os.path.basename(jf))

    ok = bool(approving)
    if ok:
        print(f"release atual v{latest}: veredito qa-critic aprovativo presente — {approving} — OK")
    else:
        print(f"release atual v{latest}: SEM artefato qa-critic aprovativo (release==v{latest} + "
              f"recomendacao em {sorted(APPROVING)}) em _meta/qa/")
    ledger_ok = _test_junction_ledger()
    breaker_ok = _test_circuit_breaker()
    ok = ok and ledger_ok and breaker_ok
    print("-" * 50)
    print("RESULTADO:", f"PASS (release v{latest} tem evidencia qa-critic; junction-ledger e circuit breaker OK)" if ok
          else f"FAIL (release v{latest}: evidencia qa-critic ausente OU junction-ledger quebrado — "
               f"qa-critic e processo, nao opt-in)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
