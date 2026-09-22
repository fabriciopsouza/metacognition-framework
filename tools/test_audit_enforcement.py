#!/usr/bin/env python3
"""
test_audit_enforcement.py — canario do auditor de enforcement (ADR-106).

Este canario obedece a propria rule #12 que o ADR-106 institui:
  1. confere a MENSAGEM, nunca so o codigo de saida (bloqueio pelo motivo errado
     e' indistinguivel de bloqueio pelo motivo certo quando so se olha `rc != 0`);
  2. prova o COMPORTAMENTO contra fixtures em pasta temporaria (teste que depende do
     estado do repo passa por acidente) — E, no fim, roda o auditor UMA vez contra o
     `capabilities.json` real. Sem essa ultima chamada, nada no CI olharia o registro
     de verdade e o modo (a) seria script manual, nao gate (achado 2 do qa-critic);
  3. traz a PROVA DE MUTACAO de si mesmo: sabota o auditor e exige que o caso que
     antes barrava passe a nao barrar — provando que a checagem e' quem carrega o peso.

Uso: python tools/test_audit_enforcement.py     (exit 0 = PASS)
NAO usa IA.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AUDITOR = RAIZ / "tools" / "audit_enforcement.py"
PY = sys.executable

# Passivo congelado na adocao do ADR-106. Mudar exige atualizar estes dois valores no
# MESMO commit, com motivo — e' o que impede escapar do modo (a) acrescentando o proprio
# id ao passivo (achado #4 do qa-critic, 2026-08-14).
BASELINE_N = 80
BASELINE_SHA = "242303796e01f06be26c5a9f4e2694f4121641d7876924e65f945e024828dc74"

MUTACAO_OK = {"arquivo": "tools/x.py", "de": "return 1", "para": "return 0",
              "canario": "tools/test_x.py", "espera": "DETECTOU: VALOR alterado"}


def rodar(auditor, caps, baseline, *extra):
    """Executa o auditor contra fixtures. Devolve (codigo, saida)."""
    r = subprocess.run([PY, "-X", "utf8", str(auditor), "--capabilities", str(caps),
                        "--baseline", str(baseline), *extra],
                       capture_output=True, text=True, encoding="utf-8", cwd=str(RAIZ))
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def escrever(tmp, capacidades, ids_baseline=()):
    caps = tmp / "caps.json"
    base = tmp / "baseline.json"
    caps.write_text(json.dumps({"capabilities": capacidades}, ensure_ascii=False),
                    encoding="utf-8")
    base.write_text(json.dumps({"ids": list(ids_baseline)}, ensure_ascii=False),
                    encoding="utf-8")
    return caps, base


def caso(nome, codigo_esperado, trecho_esperado, codigo, saida, resultados):
    """Confere codigo E mensagem. Sem a mensagem, o teste nao e' falsificavel."""
    ok = codigo == codigo_esperado and trecho_esperado.lower() in saida.lower()
    print(f"  [{'PASS' if ok else 'FALHA'}] {nome}")
    print(f"          codigo {codigo} (esperado {codigo_esperado}) · "
          f"mensagem contem {trecho_esperado!r}: "
          f"{'sim' if trecho_esperado.lower() in saida.lower() else 'NAO'}")
    if not ok:
        print(f"          saida: {saida.strip()[:300]}")
    resultados.append(ok)
    return ok


def conferir_falha_de_subprocess(resultados):
    """Falha ao EXECUTAR o canario vira `[FALHA]` da capacidade, nao crash do lote.

    O conserto do `TimeoutExpired` nao tinha canario nenhum — `grep Timeout
    tools/test_*.py` dava ZERO. E o QA provou que `OSError`, da mesma familia,
    atravessava `modo_provar` inteiro e subia ate `main()` (que nao tem
    try/except), reproduzindo LITERALMENTE o crash total do lote que a captura
    do timeout existia para eliminar.

    "O conserto foi provado?" tinha virado "os testes do arquivo estao 34/34?" —
    e eles nunca tocavam nesse caminho. [achado do QA de 17/09/2026]
    """
    sys.path.insert(0, str(RAIZ / "tools"))
    import audit_enforcement as ae

    registro = json.loads((RAIZ / "capabilities.json").read_text(encoding="utf-8"))
    registro = registro.get("capabilities", registro)
    alvo = next((c for c in registro if c.get("mutacao")), None)
    if alvo is None:
        print("  [FALHA] nenhuma capacidade com `mutacao` para exercitar")
        resultados.append(False)
        return

    original = ae.subprocess.run

    def derruba_o_canario(erro):
        def run(cmd, *a, **kw):
            texto = " ".join(str(x) for x in
                             (cmd if isinstance(cmd, (list, tuple)) else [cmd]))
            if "utf8" in texto:                    # a execucao do canario
                raise erro
            return original(cmd, *a, **kw)
        return run

    for rotulo, erro in (
            ("TimeoutExpired", subprocess.TimeoutExpired(cmd="x", timeout=300)),
            ("OSError", OSError(1450, "recursos insuficientes (simulado)")),
            ("SubprocessError", subprocess.SubprocessError("generica (simulado)"))):
        ae.subprocess.run = derruba_o_canario(erro)
        try:
            codigo = ae.modo_provar([alvo], alvo["id"], RAIZ)
            ok = codigo != 0
            print(f"  [{'PASS' if ok else 'FALHA'}] {rotulo} vira falha da capacidade, "
                  f"nao crash do lote (codigo {codigo})")
            resultados.append(ok)
        except Exception as e:                     # noqa: BLE001 — e' o ponto do teste
            print(f"  [FALHA] {rotulo} ESCAPOU de modo_provar como "
                  f"{type(e).__name__} — derruba o lote sem relatorio")
            resultados.append(False)
        finally:
            ae.subprocess.run = original


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    print("=== O AUDITOR DE ENFORCEMENT BARRA MESMO? ===\n")
    resultados = []
    with tempfile.TemporaryDirectory(prefix="audit-enf-") as t:
        tmp = Path(t)

        # (a) capacidade NOVA que se declara fail-closed sem prova -> BARRA
        caps, base = escrever(tmp, [{"id": "nova", "enforcement": "fail-closed"}])
        c, s = rodar(AUDITOR, caps, base)
        caso("nova `fail-closed` sem `mutacao` declarada", 1,
             "sem `mutacao` declarada", c, s, resultados)

        # (a) capacidade NOVA sem o campo enforcement -> BARRA
        caps, base = escrever(tmp, [{"id": "nova", "title": "x"}])
        c, s = rodar(AUDITOR, caps, base)
        caso("nova sem campo `enforcement`", 1, "invisivel a auditoria", c, s, resultados)

        # mutacao que nao sabota nada -> BARRA
        m = dict(MUTACAO_OK, para="return 1")
        caps, base = escrever(tmp, [{"id": "nova", "enforcement": "fail-closed", "mutacao": m}])
        c, s = rodar(AUDITOR, caps, base)
        caso("`mutacao` com `de` == `para`", 1, "nao sabota nada", c, s, resultados)

        # mutacao incompleta -> BARRA, dizendo QUAL campo falta
        m = {k: v for k, v in MUTACAO_OK.items() if k != "canario"}
        caps, base = escrever(tmp, [{"id": "nova", "enforcement": "fail-closed", "mutacao": m}])
        c, s = rodar(AUDITOR, caps, base)
        caso("`mutacao` sem o campo `canario`", 1, "sem os campos: canario", c, s, resultados)

        # (b) MESMA falta, mas no passivo herdado -> NAO barra (decisao do dono)
        caps, base = escrever(tmp, [{"id": "velha", "enforcement": "fail-closed"}],
                              ids_baseline=["velha"])
        c, s = rodar(AUDITOR, caps, base)
        caso("passivo herdado sem prova (modo b: advisory)", 0, "no passivo herdado",
             c, s, resultados)

        # o relatorio do passivo mostra o item, sem barrar
        c, s = rodar(AUDITOR, caps, base, "--passivo")
        caso("relatorio do passivo cita o item", 0, "velha", c, s, resultados)

        # caso legitimo -> PASSA. Auditor que barra tudo tambem e' inutil.
        caps, base = escrever(tmp, [{"id": "nova", "enforcement": "fail-closed",
                                     "mechanism": "tools/x.py", "test": "tools/test_x.py",
                                     "mutacao": MUTACAO_OK}])
        c, s = rodar(AUDITOR, caps, base)
        caso("nova com `mutacao` completa (deve passar)", 0, "nenhuma nova sem prova",
             c, s, resultados)

        # Omitir `mechanism`/`test` NAO pode desligar o cross-check em silencio — bastaria
        # nao declarar os campos para a prova provar qualquer arquivo (achado 3 residual,
        # qa-critic rodada 2).
        caps, base = escrever(tmp, [{"id": "nova", "enforcement": "fail-closed",
                                     "mutacao": MUTACAO_OK}])
        c, s = rodar(AUDITOR, caps, base)
        caso("`fail-closed` sem `mechanism`/`test` declarados", 1,
             "sem mechanism e sem test", c, s, resultados)

        # JSON quebrado -> mensagem tratada, nao stack trace (achado 8 da auditoria externa)
        ruim = tmp / "ruim.json"
        ruim.write_text('{"capabilities": [ }', encoding="utf-8")
        c, s = rodar(AUDITOR, ruim, base)
        ok = caso("JSON invalido devolve mensagem tratada", 1, "nao e' json valido",
                  c, s, resultados)
        if ok and "Traceback" in s:
            print("          FALHA extra: ainda imprime Traceback")
            resultados[-1] = False

        # --- modo --provar exercitado contra um repo-fixture --------------------------
        # O modo forte do auditor (aplica a mutacao de verdade e exige vermelho) so vale
        # se ele proprio for exercitado. Fixture: um repo git com um mecanismo e um canario.
        print("\n  --- modo --provar, contra repo-fixture ---")
        fix = tmp / "fixture"
        (fix / "tools").mkdir(parents=True)
        (fix / "tools" / "x.py").write_text("# comentario inofensivo\nVALOR = 42\n",
                                            encoding="utf-8")
        # O canario da fixture FALA: sem mensagem na saida nao da para testar a exigencia
        # "vermelho pelo motivo declarado" (emenda 1). A linha 'conferindo x.py' sai SEMPRE
        # e serve de isca para o caso que rejeita `espera` que ja aparece antes da mutacao.
        (fix / "tools" / "test_x.py").write_text(
            "import sys, pathlib\n"
            "print('conferindo x.py')\n"
            "t = (pathlib.Path(__file__).parent / 'x.py').read_text(encoding='utf-8')\n"
            "if 'VALOR = 42' in t:\n"
            "    sys.exit(0)\n"
            "print('DETECTOU: VALOR alterado')\n"
            "sys.exit(1)\n", encoding="utf-8")
        # Par y/test_y: aqui o canario IMPORTA o mecanismo, entao sabotar a sintaxe o MATA.
        # E' o unico jeito de exercitar a recusa de "vermelho por crash".
        (fix / "tools" / "y.py").write_text("VALOR = 42\n", encoding="utf-8")
        (fix / "tools" / "test_y.py").write_text(
            "import sys, pathlib\n"
            "sys.path.insert(0, str(pathlib.Path(__file__).parent))\n"
            "import y\n"
            "print('conferindo y.py')\n"
            "if y.VALOR != 42:\n"
            "    print('DETECTOU: y.VALOR fora do declarado')\n"
            "    sys.exit(1)\n"
            "sys.exit(0)\n", encoding="utf-8")
        # Par defensivo/test_defensivo: o canario CAPTURA a propria excecao e
        # reformata no stdout. `str(excecao)` nunca traz o nome da classe, entao a
        # marca de crash some do texto — e sair no stdout derruba tambem o filtro
        # por canal. E' o ataque CRITICO da 27a rodada: so' a PRE-CONDICAO (parsear
        # o arquivo sabotado antes de rodar) consegue barra-lo.
        (fix / "tools" / "defensivo.py").write_text("VALOR = 42\n", encoding="utf-8")
        (fix / "tools" / "test_defensivo.py").write_text(
            "import sys, pathlib\n"
            "sys.path.insert(0, str(pathlib.Path(__file__).parent))\n"
            "def main():\n"
            "    try:\n"
            "        import defensivo\n"
            "        assert defensivo.VALOR == 42\n"
            "    except Exception as e:\n"
            "        print(f'FAIL regra-de-negocio-violada: {e}')\n"
            "        return 1\n"
            "    print('PASS regra-de-negocio-violada')\n"
            "    return 0\n"
            "sys.exit(main())\n", encoding="utf-8")
        # Par dados.json/test_dados: mecanismo que NAO e' Python. Quebrar o JSON mata o canario
        # com `JSONDecodeError`, cujo traceback cita `json/decoder.py` e NUNCA `dados.json` —
        # a escapatoria que o qa-critic achou em 2026-08-15. `model-policy` e' um caso real disto.
        (fix / "tools" / "dados.json").write_text('{"limite": 7}\n', encoding="utf-8")
        # O nome do arquivo NAO pode aparecer na linha que falha: o traceback do Python imprime a
        # linha de codigo, e um literal 'dados.json' ali dentro faz o nome surgir no traceback por
        # acidente — foi assim que a 1a versao deste caso passou pelo motivo errado (medido por
        # mutacao em 2026-08-15). Aqui o caminho e' montado antes e a falha ocorre em outra linha.
        (fix / "tools" / "test_dados.py").write_text(
            "import json, pathlib, sys\n"
            "print('conferindo o arquivo de dados')\n"
            "P = pathlib.Path(__file__).parent / ('dad' + 'os.js' + 'on')\n"
            "bruto = P.read_text(encoding='utf-8')\n"
            "d = json.loads(bruto)\n"
            "sys.exit(0 if d.get('limite') == 7 else 1)\n", encoding="utf-8")
        # Par acento/test_acento: o canario detecta e REPORTA COM ACENTO — como a maioria
        # dos canarios reais deste repo. Existe para prender a emenda 5: a saida do canario
        # tem de ser lida como utf-8, nao com o encoding do locale.
        (fix / "tools" / "acento.py").write_text("LIMITE = 7\n", encoding="utf-8")
        (fix / "tools" / "test_acento.py").write_text(
            "import sys, pathlib\n"
            "print('conferindo o limite')\n"
            "t = (pathlib.Path(__file__).parent / 'acento.py').read_text(encoding='utf-8')\n"
            "if 'LIMITE = 7' in t:\n"
            "    sys.exit(0)\n"
            "print('DETECTOU: limite fora da toler\u00e2ncia declarada')\n"
            "sys.exit(1)\n", encoding="utf-8")
        git = ["git", "-c", "user.email=c@x", "-c", "user.name=canario"]
        pronto = all(subprocess.run(c, capture_output=True, cwd=str(fix)).returncode == 0
                     for c in (["git", "init", "-q"], ["git", "add", "-A"],
                               git + ["commit", "-qm", "fixture"]))
        if not pronto:
            print("  [SKIP declarado] git indisponivel para montar o fixture — "
                  "modo --provar NAO exercitado nesta execucao.")
        else:
            def cap_fx(**mut):
                """Capacidade-fixture do par x/test_x, com a mutacao passada por campo."""
                base_mut = {"arquivo": "tools/x.py", "de": "VALOR = 42", "para": "VALOR = 99",
                            "canario": "tools/test_x.py",
                            "espera": "DETECTOU: VALOR alterado"}
                base_mut.update(mut)
                return [{"id": "fx", "enforcement": "fail-closed", "mechanism": "tools/x.py",
                         "test": "tools/test_x.py", "mutacao": base_mut}]

            # (i) mutacao que REALMENTE quebra -> o canario fica vermelho -> PROVADO
            caps, base = escrever(tmp, cap_fx())
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("mutacao real derruba o canario", 0, "[provado]", c, s, resultados)

            # (ii) mutacao que o canario NAO enxerga -> auditor acusa, codigo 2
            caps, base = escrever(tmp, cap_fx(de="# comentario inofensivo", para="# nada muda"))
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("canario cego a mutacao e' acusado", 2, "continuou verde", c, s, resultados)

            # --- emenda 1: vermelho NAO basta; tem de ser vermelho pelo motivo declarado ---

            # (i-b) mutacao sem o campo `espera` -> BARRA. Sem isto, a prova volta a conferir
            # so o codigo de saida, que e' o achado 1 do proprio ADR-106.
            sem_espera = cap_fx()
            del sem_espera[0]["mutacao"]["espera"]
            caps, base = escrever(tmp, sem_espera)
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("mutacao sem `espera` e' barrada", 2, "sem os campos: espera",
                 c, s, resultados)

            # (i-c) `espera` que o canario ja imprime SEMPRE -> nao distingue nada -> BARRA
            caps, base = escrever(tmp, cap_fx(espera="conferindo x.py"))
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("`espera` que ja aparece antes da mutacao e' barrada", 2,
                 "ja aparece na saida antes", c, s, resultados)

            # (i-d) canario fica vermelho, mas a mensagem declarada nao aparece -> BARRA.
            # E' o caso "reprovou por outro motivo" — vermelho por acidente nao e' prova.
            caps, base = escrever(tmp, cap_fx(espera="MENSAGEM QUE NUNCA SAI"))
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("vermelho pelo motivo ERRADO e' barrado", 2, "nao pelo motivo declarado",
                 c, s, resultados)

            # (i-e) sabotagem que so quebra a SINTAXE mata o canario no import -> BARRA.
            # Foi assim que a fraude foi medida em 2026-08-15: `imprt argparse` levava [PROVADO].
            caps, base = escrever(tmp, [{"id": "fy", "enforcement": "fail-closed",
                "mechanism": "tools/y.py", "test": "tools/test_y.py", "mutacao": {
                "arquivo": "tools/y.py", "de": "VALOR = 42", "para": "VALOR = (42",
                "canario": "tools/test_y.py", "espera": "y.VALOR divergiu"}}])
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            # A recusa continua sendo exit 2 — o que mudou foi ONDE ela nasce. Ate a 26a
            # rodada era inferida da SAIDA do canario ("morreu processando"); desde a 27a e'
            # PRE-CONDICAO do arquivo (`ast.parse`/`json.loads` no texto sabotado, antes de
            # rodar qualquer coisa), porque um canario que captura a propria excecao apaga o
            # sinal de crash do texto. O codigo 2 e' que prova a regra; a frase so' a nomeia.
            caso("vermelho por CRASH (sintaxe quebrada) e' barrado", 2, "QUEBROU a sintaxe",
                 c, s, resultados)

            # (i-f) crash em mecanismo NAO-Python: o traceback do JSONDecodeError nao cita
            # `dados.json`. A 1a versao da recusa exigia o nome do arquivo e deixava passar.
            # Achado ALTO 1 do qa-critic (Sonnet, 2026-08-15).
            caps, base = escrever(tmp, [{"id": "fj", "enforcement": "fail-closed",
                "mechanism": "tools/dados.json", "test": "tools/test_dados.py", "mutacao": {
                "arquivo": "tools/dados.json", "de": '{"limite": 7}', "para": '{"limite": 7,}',
                "canario": "tools/test_dados.py", "espera": "limite fora do declarado"}}])
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("crash em mecanismo .json (traceback sem o nome) e' barrado", 2,
                 "QUEBROU a sintaxe", c, s, resultados)

            # (i-g) O CANARIO DEFENSIVO — achado CRITICO da 27a rodada, e a razao de a
            # recusa ter virado pre-condicao. Um canario que faz
            #     except Exception as e: print(f"FAIL regra-violada: {e}")
            # apaga o sinal para sempre: `str(excecao)` em Python NUNCA traz o nome da
            # classe, isso so' aparece quando o INTERPRETADOR formata traceback nao
            # capturado. E o texto sai no stdout, entao nem filtrar por canal resolvia.
            # Com sabotagem PURAMENTE sintatica, isto saia [PROVADO].
            caps, base = escrever(tmp, [{"id": "fd", "enforcement": "fail-closed",
                "mechanism": "tools/defensivo.py", "test": "tools/test_defensivo.py",
                "mutacao": {
                "arquivo": "tools/defensivo.py", "de": "VALOR = 42", "para": "VALOR = (42",
                "canario": "tools/test_defensivo.py",
                "espera": "FAIL regra-de-negocio-violada"}}])
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("canario DEFENSIVO (captura a excecao) nao mascara crash", 2,
                 "QUEBROU a sintaxe", c, s, resultados)

            # (i-i) mutacao que preserva o TAMANHO do arquivo, em mecanismo IMPORTADO. Se a prova
            # aceitar cache de bytecode, o interpretador reusa o `.pyc` velho quando o horario cai
            # no mesmo segundo, roda o codigo NAO sabotado e o canario fica verde — prova perdida,
            # de forma intermitente. Medido em `autonomy-retry-policy` (48 bytes antes e depois),
            # 2026-08-15. A fixture x.py nunca pegou isto porque LE o arquivo como texto; so
            # mecanismo importado sofre.
            caps, base = escrever(tmp, [{"id": "fi", "enforcement": "fail-closed",
                "mechanism": "tools/y.py", "test": "tools/test_y.py", "mutacao": {
                "arquivo": "tools/y.py", "de": "VALOR = 42", "para": "VALOR = 41",
                "canario": "tools/test_y.py",
                "espera": "DETECTOU: y.VALOR fora do declarado"}}])
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("mutacao do MESMO tamanho em modulo importado se prova", 0, "[provado]",
                 c, s, resultados)

            # (i-j) as duas travas contra cache de bytecode existem de fato. Deterministico:
            # o caso (i-i) so reprova quando a corrida do relogio e' perdida, e canario que
            # depende de sorte nao e' canario.
            import ast
            import inspect
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location("_audenf", AUDITOR)
            _mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            ok_env = _mod.ENV_SEM_BYTECODE.get("PYTHONDONTWRITEBYTECODE") == "1"
            _lixo = Path(tmp) / "pycache-probe" / "__pycache__"
            _lixo.mkdir(parents=True, exist_ok=True)
            (_lixo / "x.pyc").write_bytes(b"\x00")
            _mod._purgar_bytecode(_lixo.parent)
            caso("travas anti-cache de bytecode presentes (env + purga)", 0, "",
                 0 if (ok_env and not _lixo.exists()) else 1, "", resultados)

            # (i-k) `espera` ACENTUADA. As duas execucoes do canario usavam text=True SEM
            # encoding, entao a saida utf-8 era decodificada com o encoding do LOCALE (cp1252
            # no Windows pt-BR): os bytes do acento viravam dois caracteres e a comparacao
            # `espera not in saida` dava SEMPRE verdadeiro. Prova valida era recusada como
            # "vermelho pelo motivo errado" — acusando o canario por um defeito do LEITOR.
            # Emenda 5 (2026-08-17), medida em `project-onboarding`. Pior que o falso-negativo:
            # ensina o migrador a escolher `espera` so em ASCII, fugindo justamente da frase
            # especifica que o canario imprime.
            caps, base = escrever(tmp, [{"id": "fk", "enforcement": "fail-closed",
                "mechanism": "tools/acento.py", "test": "tools/test_acento.py", "mutacao": {
                "arquivo": "tools/acento.py", "de": "LIMITE = 7", "para": "LIMITE = 9",
                "canario": "tools/test_acento.py",
                "espera": "limite fora da toler\u00e2ncia declarada"}}])
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("`espera` com acento casa end-to-end (nao distingue o fix — ver (i-l))", 0,
                 "[provado]", c, s, resultados)

            # (i-l) A trava REAL da emenda 5, estrutural e deterministica.
            # O caso (i-k) acima NAO consegue reprovar quando o fix e removido: `rodar()`
            # lanca o auditor com `-X utf8`, e em modo UTF-8 `locale.getpreferredencoding()`
            # ja devolve UTF-8 — ou seja, o caso end-to-end mede um ambiente onde o bug nao
            # existe. MEDIDO em 2026-08-17: passa com e sem o fix. O defeito aparece quando o
            # auditor roda SEM modo UTF-8 (humano chamando `python tools/audit_enforcement.py
            # --provar`, que foi como ele apareceu). Como reproduzir isso depende do locale da
            # maquina, a trava e' estrutural: as DUAS execucoes do canario em `modo_provar`
            # tem de declarar `encoding="utf-8"`. Mesmo precedente do caso (i-j).
            # Contar `encoding="utf-8"` no fonte NAO serve: ele ja aparece 3x em
            # `modo_provar` (read_text + os dois write_text), logo um limiar >=2 passa
            # mesmo com as duas chamadas de subprocess sem encoding. Medido em 2026-08-17,
            # na 1a versao desta propria verificacao. Por isso a checagem e por AST: acha as
            # chamadas que executam o CANARIO e exige `encoding` em TODAS elas.
            _arv = ast.parse(inspect.getsource(_mod.modo_provar))
            _runs = [n for n in ast.walk(_arv) if isinstance(n, ast.Call)
                     and getattr(n.func, "attr", "") == "run"
                     and "canario" in ast.unparse(n)]
            # Conferir a PRESENCA da chave `encoding` NAO basta: `encoding=None` ou
            # `encoding=locale.getpreferredencoding(False)` reintroduzem exatamente o bug
            # original (decodificar pelo locale) e passariam na checagem. Achado MEDIO do
            # qa-critic (Sonnet, 2026-08-17), reproduzido em memoria antes de virar codigo.
            # Exigimos o VALOR literal utf-8, nao so a chave.
            def _le_utf8(n):
                for k in n.keywords:
                    if k.arg == "encoding":
                        return (isinstance(k.value, ast.Constant)
                                and str(k.value.value).lower().replace("-", "") == "utf8")
                return False
            _sem_enc = [n for n in _runs if not _le_utf8(n)]
            caso(f"as {len(_runs)} execucoes do canario leem a saida como utf-8 "
                 f"(sem utf-8 literal: {len(_sem_enc)}; esperado 2 e 0)", 0, "",
                 0 if (len(_runs) == 2 and not _sem_enc) else 1, "", resultados)

            # (i-m) mecanismo com mudanca NAO-COMMITADA -> SKIP declarado, nunca [FALHA].
            # A prova roda contra o HEAD (worktree --detach). Se o arquivo vivo difere, o que
            # seria testado e a versao ANTIGA, e as mensagens genericas ("mutacao obsoleta",
            # "continuou VERDE") acusariam a mutacao por um problema de estado do repo.
            # Achado MEDIO do qa-critic (2026-08-18): o dano nao e o falso-positivo, e o
            # habito de descartar [FALHA] como "coisa do HEAD" — que deixa passar mutacao
            # genuinamente quebrada. Emenda 6.
            _vivo = fix / "tools" / "x.py"
            _antes_txt = _vivo.read_text(encoding="utf-8")
            try:
                _vivo.write_text(_antes_txt + "# alteracao nao-commitada\n", encoding="utf-8")
                caps, base = escrever(tmp, cap_fx())
                c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
                caso("mecanismo nao-commitado vira SKIP declarado (nao acusa a mutacao)",
                     0, "skip declarado", c, s, resultados)
                # E o resumo NAO pode contar a pulada como prova: "OK: 1 prova(s)" com uma
                # pulada e a mesma classe de mentira que este auditor combate. Pego ao usar
                # a emenda 6 pela primeira vez, que reportava 52 provas com 1 SKIP.
                caso("skip NAO e contado como prova no resumo", 0, "0 prova(s)",
                     c, s, resultados)
            finally:
                _vivo.write_text(_antes_txt, encoding="utf-8")

            # (i-n) diferenca SO de quebra de linha NAO e' mudanca pendente. O git converte
            # LF<->CRLF ao materializar o worktree, entao comparar bytes crus reportava
            # arquivo IDENTICO como nao-commitado — foi o que aconteceu com
            # `test_skill_contract.py`, recem-commitado, na primeira execucao da emenda 6.
            # Buraco de cobertura apontado pelo qa-critic: sem este caso, alguem
            # 'simplifica' de volta para read_bytes() e a suite inteira segue verde.
            _p = fix / 'tools' / 'x.py'
            _txt = _p.read_text(encoding='utf-8')
            try:
                # mesmo CONTEUDO, quebra de linha diferente do que esta no HEAD
                _p.write_bytes(_txt.replace('\n', '\r\n').encode('utf-8'))
                caps, base = escrever(tmp, cap_fx())
                c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
                caso("diferenca so de quebra de linha NAO vira skip", 0, "[provado]",
                     c, s, resultados)
            finally:
                _p.write_text(_txt, encoding='utf-8', newline='')

            # (i-g) `espera` curta demais vira curinga: "Error" casa com qualquer excecao.
            # Achado ALTO 2 do mesmo crítico.
            caps, base = escrever(tmp, cap_fx(espera="Error"))
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("`espera` curta demais e' barrada", 2, "minimo 12", c, s, resultados)

            # (i-h) `espera` que declara o proprio crash como sinal esperado -> BARRA.
            # Sem isto, bastaria declarar `espera: "Traceback"` para reabrir o buraco.
            caps, base = escrever(tmp, cap_fx(espera="Traceback (most recent call last)"))
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("`espera` que e' sinal de crash e' barrada", 2, "sinal de crash",
                 c, s, resultados)

            # (iii) mutacao obsoleta (trecho `de` nao existe mais) -> acusa, nao passa calado
            caps, base = escrever(tmp, [{"id": "fx", "enforcement": "fail-closed",
                "mechanism": "tools/x.py", "test": "tools/test_x.py", "mutacao": {
                "arquivo": "tools/x.py", "de": "TRECHO QUE NAO EXISTE", "para": "z",
                "canario": "tools/test_x.py", "espera": "DETECTOU: VALOR alterado"}}])
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("mutacao obsoleta e' acusada", 2, "obsoleta", c, s, resultados)

            # (iv) canario que JA nasce vermelho -> a prova nao diz nada, tem de acusar.
            # Este caso faltava na 1a rodada, e o ADR AFIRMAVA que ele existia — achado
            # bloqueante #1 do qa-critic em 2026-08-14. A afirmacao veio antes do teste.
            (fix / "tools" / "test_sempre_vermelho.py").write_text(
                "import sys\nsys.exit(1)\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], capture_output=True, cwd=str(fix))
            subprocess.run(git + ["commit", "-qm", "canario sempre vermelho"],
                           capture_output=True, cwd=str(fix))
            caps, base = escrever(tmp, [{"id": "fx", "enforcement": "fail-closed",
                "mechanism": "tools/x.py", "test": "tools/test_sempre_vermelho.py", "mutacao": {
                "arquivo": "tools/x.py", "de": "VALOR = 42", "para": "VALOR = 99",
                "canario": "tools/test_sempre_vermelho.py", "espera": "irrelevante aqui"}}])
            c, s = rodar(AUDITOR, caps, base, "--provar", "--raiz", str(fix))
            caso("canario ja vermelho ANTES da mutacao e' acusado", 2,
                 "ja estava vermelho antes", c, s, resultados)

        # mutacao apontando para arquivo que NAO e' o mecanismo da capacidade -> BARRA.
        # Sem isto, a "prova" provaria outra coisa (achado 3 do qa-critic).
        caps, base = escrever(tmp, [{"id": "nova", "enforcement": "fail-closed",
                                     "mechanism": "tools/verdadeiro.py",
                                     "test": "tools/test_verdadeiro.py",
                                     "mutacao": MUTACAO_OK}])
        c, s = rodar(AUDITOR, caps, base)
        caso("`mutacao.arquivo` diferente do `mechanism` declarado", 1,
             "nao e' o mecanismo", c, s, resultados)

        caps, base = escrever(tmp, [{"id": "nova", "enforcement": "fail-closed",
                                     "mechanism": "tools/x.py",
                                     "test": "tools/test_verdadeiro.py",
                                     "mutacao": MUTACAO_OK}])
        c, s = rodar(AUDITOR, caps, base)
        caso("`mutacao.canario` diferente do `test` declarado", 1,
             "nao e' o canario", c, s, resultados)

        # --gerar-baseline tinha zero cobertura (achado 7 do qa-critic)
        alvo_base = tmp / "gerado.json"
        caps, _ = escrever(tmp, [{"id": "um"}, {"id": "dois"}])
        c, s = rodar(AUDITOR, caps, alvo_base, "--gerar-baseline")
        ok = c == 0 and alvo_base.is_file() and \
            json.loads(alvo_base.read_text(encoding="utf-8")).get("ids") == ["dois", "um"]
        print(f"  [{'PASS' if ok else 'FALHA'}] --gerar-baseline congela os ids ordenados")
        resultados.append(ok)

        # --- PROVA DE MUTACAO DO PROPRIO CANARIO (rule #12) --------------------------
        # Sabota o auditor e exige que o 1o caso deixe de barrar. Se continuar barrando,
        # e' porque outra coisa estava derrubando o processo e este canario nao provava nada.
        print("\n  --- prova de mutacao: sabotando o proprio auditor ---")
        fonte = AUDITOR.read_text(encoding="utf-8")
        alvo = 'problema = "declara `fail-closed` sem `mutacao` declarada"'
        if alvo not in fonte:
            print("  [FALHA] trecho da mutacao nao encontrado — prova obsoleta")
            resultados.append(False)
        else:
            sabotado = tmp / "audit_sabotado.py"
            sabotado.write_text(fonte.replace(alvo, "problema = None", 1), encoding="utf-8")
            caps, base = escrever(tmp, [{"id": "nova", "enforcement": "fail-closed"}])
            c, s = rodar(sabotado, caps, base)
            ok = c == 0
            print(f"  [{'PASS' if ok else 'FALHA'}] auditor sabotado deixa de barrar "
                  f"(codigo {c}, esperado 0)")
            if not ok:
                print("          A checagem sabotada NAO era a responsavel pelo bloqueio.")
                print(f"          saida: {s.strip()[:300]}")
            resultados.append(ok)

    # --- O ESTADO REAL DO REPO, e nao so fixtures ---------------------------------
    # Fixtures provam o COMPORTAMENTO; sem esta secao nada no CI olharia o
    # `capabilities.json` de verdade, e o modo (a) seria script manual, nao gate
    # (achado bloqueante #2 do qa-critic, 2026-08-14). E' esta chamada que faz o
    # `run_canaries.py` barrar uma capacidade nova sem prova de mutacao.
    print("\n  --- o repo REAL passa no modo (a)? ---")
    r = subprocess.run([PY, "-X", "utf8", str(AUDITOR)], capture_output=True, text=True,
                       encoding="utf-8", cwd=str(RAIZ))
    saida = (r.stdout or "") + (r.stderr or "")
    ok = r.returncode == 0 and "nenhuma nova sem prova" in saida
    print(f"  [{'PASS' if ok else 'FALHA'}] capabilities.json real sem capacidade nova "
          f"sem prova (codigo {r.returncode})")
    if not ok:
        print(f"          {saida.strip()[:400]}")
    resultados.append(ok)

    # Baseline PINADO: sem isto, escapar do modo (a) seria so acrescentar o proprio id
    # a lista do passivo (achado #4 do qa-critic). Mexer no passivo agora quebra o CI
    # e exige decisao explicita — que e' o ponto.
    ids = json.loads((RAIZ / "_meta" / "enforcement-baseline.json")
                     .read_text(encoding="utf-8")).get("ids", [])
    h = hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()
    ok = len(ids) == BASELINE_N and h == BASELINE_SHA
    print(f"  [{'PASS' if ok else 'FALHA'}] passivo intacto: {len(ids)} ids "
          f"(esperado {BASELINE_N}), sha256 {'confere' if h == BASELINE_SHA else 'DIVERGE'}")
    if not ok:
        print("          O passivo mudou. Migrar capacidade do passivo e' decisao "
              "declarada: atualize BASELINE_N/BASELINE_SHA no mesmo commit, com motivo.")
    resultados.append(ok)

    print("\n  --- falha ao EXECUTAR o canario nao derruba o lote ---")
    conferir_falha_de_subprocess(resultados)

    print(f"\nRESULTADO: {sum(resultados)}/{len(resultados)} verificacoes passaram")
    if not all(resultados):
        print("O AUDITOR NAO FAZ O QUE PROMETE. Corrigir antes de confiar nele.")
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
