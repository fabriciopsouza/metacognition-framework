#!/usr/bin/env python3
"""Canario do check_rules_parity (E3 do plano anti-bypass): prova que o detector de DRIFT das 4 regras
invioláveis (a) PASSA no repo real e (b) PEGA cada classe de drift em fixtures sinteticas. Sem (b), o
linter poderia estar quebrado e ninguem saberia (false-PASS). Fail-closed.

Uso: python tools/test_rules_parity.py   (exit 0 PASS; 1 se falha)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_rules_parity as crp  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GOOD_CLAUDE = """# CLAUDE.md

## Regras invioláveis (de _shared/, não redefinir)
1. Classificar afirmação: CONFIRMADO | INFERIDO | DESCONHECIDO.
2. Anti-rename: não renomear nome aprovado sem ADR.
3. File-first: ler/inspecionar antes de assumir.
4. NÃO SEI direto — nunca inventar.

## Outro
"""

GOOD_AF = """# AGENT-FRAMEWORK

## 6. Princípios
só as 4 regras invioláveis seguem ativas — todas referenciando
`_shared/` (classificação, anti-rename, file-first, NÃO SEI/nunca-inventar).

## Outro
"""

GOOD_AGENTS = """# AGENTS

## Regras sempre ativas
Ver .agent/rules/ (todas referenciam _shared/).

## Outro
"""


# [QA rodada 2] fixtures da guarda de ponteiro morto. As crases sao montadas em runtime porque
# payload com crase nao sobrevive a um shell — licao ja registrada neste repo.
_CRASE = chr(96)
_FENCE = _CRASE * 3
EXEMPLO_EM_BLOCO = (
    "\n" + _FENCE + "\nexemplo: " + _CRASE + ".agent/rules/98-so-ilustracao.md" + _CRASE
    + "\n" + _FENCE + "\n")
PONTEIRO_FORA_DO_BLOCO = (
    "\nDetalhe real: " + _CRASE + ".agent/rules/97-fora-do-bloco.md" + _CRASE + ".\n")


# Fixture das regras globais: le a FONTE REAL (as mutacoes abaixo apagam clausula por clausula dela),
# mas a lista do que tem de existir vem do checker — e o teste (b4) prova que cada item dela reprova.
with open(os.path.join(ROOT, crp.GLOBAL_SRC), encoding="utf-8") as _f:
    GOOD_GLOBAL = _f.read()
GOOD_INSTALLER = ("# fixture\n$bootPy = Join-Path $projectRoot 'bootstrap.py'\n"
                  "        $saida = & $py.Source $bootPy --regras-globais 2>&1\n")
GOOD_SH = '# fixture\n    "$PY_BIN" "$PROJECT_DIR/bootstrap.py" --regras-globais || echo aviso\n'
GOOD_BOOTSTRAP = ("def instalar_regras_globais(raiz, home_claude):\n    pass\n\n\ndef main(argv):\n"
                  "    situacao, detalhe = instalar_regras_globais(ROOT, HOME_CLAUDE)\n")


def write_fixture(d, claude=GOOD_CLAUDE, af=GOOD_AF, agents=GOOD_AGENTS,
                  global_rules=GOOD_GLOBAL, installer=GOOD_INSTALLER, bootstrap=GOOD_BOOTSTRAP,
                  sh=GOOD_SH):
    for name, content in (("CLAUDE.md", claude), ("AGENT-FRAMEWORK.md", af), ("AGENTS.md", agents),
                          (crp.GLOBAL_SRC, global_rules), (crp.GLOBAL_INSTALLER, installer),
                          (crp.GLOBAL_INSTALLER_PY, bootstrap), ("bootstrap.sh", sh)):
        path = os.path.join(d, name)
        if content is None:
            if os.path.exists(path):
                os.remove(path)
            continue
        os.makedirs(os.path.dirname(path) or d, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


def main():
    fails = []

    # (a) repo REAL passa (o digesto/referencia/delegacao estao em sync)
    real = crp.audit(ROOT)
    if real:
        fails.append(f"repo real deveria PASSAR mas reportou drift: {real}")

    with tempfile.TemporaryDirectory() as d:
        # (b0) fixture boa = 0 issues (sanidade do fixture)
        write_fixture(d)
        if crp.audit(d):
            fails.append(f"fixture BOA reportou drift indevidamente: {crp.audit(d)}")

        # (b1) CLAUDE.md perde a 4a regra (anti-alucinacao) -> drift (contagem + conceito)
        claude3 = GOOD_CLAUDE.replace("4. NÃO SEI direto — nunca inventar.\n", "")
        write_fixture(d, claude=claude3)
        if not crp.audit(d):
            fails.append("NAO pegou: CLAUDE.md com 3 regras (anti-alucinacao removida)")
        # [ADR-111] a guarda de ponteiro morto: fixture cita uma regra que nao existe -> tem de
        # reprovar. Sem esta prova, a guarda seria mais uma promessa nao verificada — que e'
        # exatamente a classe que este repo mede.
        write_fixture(d)
        os.makedirs(os.path.join(d, ".agent", "rules"), exist_ok=True)
        with open(os.path.join(d, "CLAUDE.md"), "a", encoding="utf-8") as f:
            f.write("\nDetalhe: `.agent/rules/99-regra-que-nao-existe.md`.\n")
        if not any("ponteiro morto" in i for i in crp.audit(d)):
            fails.append("NAO pegou: ponteiro para `.agent/rules/` inexistente (guarda ADR-111)")
        # e com o arquivo no lugar, para de reclamar
        with open(os.path.join(d, ".agent", "rules", "99-regra-que-nao-existe.md"), "w",
                  encoding="utf-8") as f:
            f.write("# regra de fixture\n")
        if any("ponteiro morto" in i for i in crp.audit(d)):
            fails.append("falso positivo: ponteiro com arquivo existente foi acusado de morto")
        # [QA rodada 2, 19/08/2026] a supressao de blocos de codigo na guarda de ponteiro morto
        # so era verdade porque alguem testou a mao — e o proprio critico apontou que reverter o
        # re.sub amanha nao reprovaria nada. Ponteiro citado DENTRO de bloco de codigo e'
        # ilustracao e nao pode reprovar; FORA do bloco, continua sendo promessa e reprova.
        write_fixture(d)
        with open(os.path.join(d, 'CLAUDE.md'), 'a', encoding='utf-8') as f:
            f.write(EXEMPLO_EM_BLOCO)
        if any('ponteiro morto' in i for i in crp.audit(d)):
            fails.append('falso positivo: ponteiro dentro de bloco de codigo tratado como promessa')
        with open(os.path.join(d, 'CLAUDE.md'), 'a', encoding='utf-8') as f:
            f.write(PONTEIRO_FORA_DO_BLOCO)
        if not any('ponteiro morto' in i for i in crp.audit(d)):
            fails.append('NAO pegou: ponteiro morto FORA do bloco, logo apos um bloco de codigo')
        write_fixture(d)  # restaura
        write_fixture(d)  # restaura

        # (b2) AGENT-FRAMEWORK cita contagem divergente (3 != 4 do CLAUDE)
        af_bad = GOOD_AF.replace("4 regras invioláveis", "3 regras invioláveis")
        write_fixture(d, af=af_bad)
        if not crp.audit(d):
            fails.append("NAO pegou: AGENT-FRAMEWORK com contagem divergente (3 vs 4)")
        write_fixture(d)

        # (b3) AGENTS redefine sem referenciar a SSoT -> risco dual-authority
        agents_bad = "# AGENTS\n\n## Regras sempre ativas\n1. classificar tudo inline aqui.\n\n## Outro\n"
        write_fixture(d, agents=agents_bad)
        if not crp.audit(d):
            fails.append("NAO pegou: AGENTS.md sem referencia a SSoT (dual-authority)")
        write_fixture(d)

        # (b4) regras globais do dono: apagar QUALQUER clausula reprova (mutacao uma a uma, com
        # contagem — "passou em 1 exemplo" nao prova a classe); fonte ausente reprova; instalador que
        # deixou de instalar reprova.
        import re as _re
        mordidas = 0
        for label, sig in crp.GLOBAL_RULES:
            mutante = _re.sub(sig, "", GOOD_GLOBAL, flags=_re.I)
            write_fixture(d, global_rules=mutante)
            if any(label in i for i in crp.audit(d)):
                mordidas += 1
            else:
                fails.append(f"NAO pegou: fonte global sem a clausula '{label}'")
        if mordidas != len(crp.GLOBAL_RULES):
            fails.append(f"mutacao das regras globais: {mordidas}/{len(crp.GLOBAL_RULES)} reprovadas")
        write_fixture(d, global_rules=None)
        if not any("CLAUDE-global.md" in i for i in crp.audit(d)):
            fails.append("NAO pegou: fonte das regras globais ausente")
        write_fixture(d, installer="# instalador sem a linha\n")
        if not any("nao instala mais" in i for i in crp.audit(d)):
            fails.append("NAO pegou: sync-global deixou de instalar as regras globais")
        # a mutacao realista: a chamada sai, o comentario que a descreve fica
        so_comentario = ("# - .claude/global/CLAUDE-global.md -> ~/.claude/CLAUDE.md\n"
                         "        # $saida = & $py.Source $bootPy --regras-globais 2>&1\n")
        write_fixture(d, installer=so_comentario)
        if not any("sync-global.ps1 nao instala" in i for i in crp.audit(d)):
            fails.append("NAO pegou: sync-global com a chamada apagada e so o comentario")
        write_fixture(d, sh='# "$PY_BIN" "$PROJECT_DIR/bootstrap.py" --regras-globais\necho pronto\n')
        if not any("bootstrap.sh nao instala" in i for i in crp.audit(d)):
            fails.append("NAO pegou: bootstrap.sh (Mac/Linux) sem a chamada — so' comentario")
        # texto de AJUDA que so' menciona o comando nao e' chamada (furo real, confirmado em 25/09)
        write_fixture(d, sh='    echo "  aviso: rode: python3 bootstrap.py --regras-globais"\n')
        if not any("bootstrap.sh nao instala" in i for i in crp.audit(d)):
            fails.append("NAO pegou: bootstrap.sh so' com a mensagem de ajuda citando o comando")
        # o texto EXATO da chamada dentro de uma string nunca executada (mutacao da revisao 4)
        for texto_ps in ("        Write-Host \"rode: python $bootPy --regras-globais\"\n",
                         "        if ($false) { Write-Host \"iria rodar: & $py.Source $bootPy --regras-globais\" }\n"):
            write_fixture(d, installer="$bootPy = Join-Path $projectRoot 'bootstrap.py'\n" + texto_ps)
            if not any("sync-global.ps1 nao instala" in i for i in crp.audit(d)):
                fails.append(f"NAO pegou: sync-global so' com string citando o comando: {texto_ps.strip()[:50]}")
        write_fixture(d, bootstrap=("def instalar_regras_globais(raiz, home_claude):\n    pass\n\n\n"
                                    "def main(argv):\n"
                                    "    print(f\"seria chamado: instalar_regras_globais(ROOT, HOME_CLAUDE)\")\n"))
        if not any("bootstrap.py nao instala" in i for i in crp.audit(d)):
            fails.append("NAO pegou: bootstrap.py so' com print citando a chamada")
        # e o bootstrap.sh REAL, com a chamada apagada (fica so' a ajuda), tem de reprovar
        with open(os.path.join(ROOT, "bootstrap.sh"), encoding="utf-8-sig") as _f:
            _sh_real = _f.read()
        _sem_chamada = "\n".join(l for l in _sh_real.splitlines()
                                 if not ('"$PY_BIN"' in l and "--regras-globais" in l))
        write_fixture(d, sh=_sem_chamada)
        if not any("bootstrap.sh nao instala" in i for i in crp.audit(d)):
            fails.append("NAO pegou: bootstrap.sh real com a chamada apagada")
        # e os chamadores REAIS do repo tem de casar (sem isto o fixture poderia divergir deles)
        with open(os.path.join(ROOT, crp.GLOBAL_INSTALLER), encoding="utf-8-sig") as _f1, \
                open(os.path.join(ROOT, "bootstrap.sh"), encoding="utf-8-sig") as _f2:
            write_fixture(d, installer=_f1.read(), sh=_f2.read())
        if any("nao instala mais" in i for i in crp.audit(d)):
            fails.append(f"falso positivo: chamador real acusado: {crp.audit(d)}")
        write_fixture(d)
        # rota non-admin: bootstrap.py que so' DEFINE a funcao (ou a chama num comentario) nao instala
        so_def = ("def instalar_regras_globais(raiz, home_claude):\n    pass\n\n\ndef main(argv):\n"
                  "    # instalar_regras_globais(ROOT, HOME_CLAUDE)\n    pass\n")
        write_fixture(d, bootstrap=so_def)
        if not any("bootstrap.py nao instala" in i for i in crp.audit(d)):
            fails.append("NAO pegou: bootstrap.py com a chamada apagada (so' a definicao e um comentario)")
        with open(os.path.join(ROOT, crp.GLOBAL_INSTALLER_PY), encoding="utf-8-sig") as _f:
            write_fixture(d, bootstrap=_f.read())
        if any("bootstrap.py nao instala" in i for i in crp.audit(d)):
            fails.append("falso positivo: o bootstrap.py real foi acusado de nao instalar")
        write_fixture(d)

    # (b5) COMPORTAMENTO do instalador Python (rota non-admin), numa pasta de usuario falsa.
    sys.path.insert(0, ROOT)
    sys.dont_write_bytecode = True  # importar bootstrap.py nao pode deixar __pycache__ na raiz do repo
    import bootstrap as bs  # noqa: E402
    esperado = bs.renderizar_regras_globais(ROOT)
    _raiz = os.path.abspath(ROOT)
    if len(_raiz) > 1 and _raiz[1] == ":":
        _raiz = _raiz[0].upper() + _raiz[1:]
    _url = "file:///" + _raiz.replace("\\", "/") + "/tools/model-policy.json"
    if "{{FRAMEWORK_ROOT" in esperado or _url not in esperado:
        fails.append("o bloco renderizado nao trocou o marcador pelo caminho absoluto desta maquina")
    with tempfile.TemporaryDirectory() as home:
        alvo = os.path.join(home, "CLAUDE.md")

        def bytes_de():
            with open(alvo, "rb") as fh:
                return fh.read()
        with open(alvo, "w", encoding="utf-8") as fh:
            fh.write("nota do usuario com $dinheiro e acentuação\n")
        s1 = bs.instalar_regras_globais(ROOT, home)[0]
        b1 = bytes_de()
        s2 = bs.instalar_regras_globais(ROOT, home)[0]
        if (s1, s2) != ("instalado", "em-dia") or bytes_de() != b1:
            fails.append(f"instalador python nao e' idempotente: {s1}, {s2}")
        texto = b1.decode("utf-8")
        if "nota do usuario com $dinheiro e acentuação" not in texto or texto.count(bs.GLOBAL_INICIO) != 1:
            fails.append("instalador python apagou texto do usuario ou duplicou o bloco")
        # marcador orfao: recusa e nao toca em nada
        orfao = "topo\n" + bs.GLOBAL_INICIO + " antigo\nLINHA DO USUARIO\n"
        with open(alvo, "w", encoding="utf-8") as fh:
            fh.write(orfao)
        antes = bytes_de()
        if bs.instalar_regras_globais(ROOT, home)[0] != "recusado" or bytes_de() != antes:
            fails.append("NAO pegou: marcador orfao — o instalador python escreveu por cima")
        # BOM preservado
        with open(alvo, "wb") as fh:
            fh.write(b"\xef\xbb\xbfnota com BOM\n")
        bs.instalar_regras_globais(ROOT, home)
        if not bytes_de().startswith(b"\xef\xbb\xbfnota com BOM"):
            fails.append("instalador python descartou o BOM do arquivo do usuario")
        # outros pares de marcadores inconsistentes que a revisao testou: 0+1 e 2+2
        for ruim in (bs.GLOBAL_FIM + "\nsobra\n",
                     (bs.GLOBAL_INICIO + " a\n" + bs.GLOBAL_FIM + "\n") * 2):
            with open(alvo, "w", encoding="utf-8") as fh:
                fh.write(ruim)
            antes = bytes_de()
            if bs.instalar_regras_globais(ROOT, home)[0] != "recusado" or bytes_de() != antes:
                fails.append(f"NAO pegou: marcadores inconsistentes {ruim[:30]!r}")
        # CRLF: arquivo do usuario em CRLF com o bloco ja em dia -> "em-dia", sem reescrever
        crlf = ("nota\n\n" + esperado + "\n").replace("\n", "\r\n").encode("utf-8")
        with open(alvo, "wb") as fh:
            fh.write(crlf)
        if bs.instalar_regras_globais(ROOT, home)[0] != "em-dia" or bytes_de() != crlf:
            fails.append("CRLF: bloco em dia foi reescrito (comparacao sensivel a quebra de linha)")
        # quebra MISTA com bloco velho: sai no estilo dominante e nenhuma linha do usuario se perde
        misto = ("linha lf 1\nlinha crlf 1\r\nlinha crlf 2\r\nlinha crlf 3\r\n"
                 + bs.GLOBAL_INICIO + " velho\r\n" + bs.GLOBAL_FIM + "\r\nfim do usuario\r\n")
        with open(alvo, "wb") as fh:
            fh.write(misto.encode("utf-8"))
        bs.instalar_regras_globais(ROOT, home)
        saida = bytes_de().decode("utf-8")
        linhas_usuario = ("linha lf 1", "linha crlf 1", "linha crlf 2", "linha crlf 3", "fim do usuario")
        if not all(l in saida for l in linhas_usuario) or esperado.replace("\n", "\r\n") not in saida:
            fails.append("quebra mista: perdeu linha do usuario ou nao gravou o bloco no estilo dominante (CRLF)")
        if saida.replace("\r\n", "").count("\n") != 0:
            fails.append("quebra mista: sobrou LF avulso — o estilo dominante nao foi aplicado ao arquivo todo")
        # somente-leitura: devolve 'falha-escrita', nao levanta excecao, nao altera o arquivo
        import stat
        with open(alvo, "w", encoding="utf-8") as fh:
            fh.write("nota protegida\n")
        antes = bytes_de()
        os.chmod(alvo, stat.S_IREAD)
        try:
            try:
                sit = bs.instalar_regras_globais(ROOT, home)[0]
            except Exception as e:  # o defeito da revisao 4 era exatamente este traceback
                sit = f"EXCECAO {type(e).__name__}"
            if sit != "falha-escrita" or bytes_de() != antes:
                fails.append(f"somente-leitura: esperado 'falha-escrita' sem alterar o arquivo, veio {sit}")
        finally:
            os.chmod(alvo, stat.S_IREAD | stat.S_IWRITE)

    # (b6) PONTA A PONTA: o comando que sync-global.ps1 e bootstrap.sh chamam, num home falso. Tem de
    # instalar e NAO pode tocar no settings.json do projeto (o bootstrap normal troca esse arquivo).
    import hashlib
    import subprocess
    _settings = os.path.join(ROOT, ".claude", "settings.json")

    def _hash():
        return hashlib.sha256(open(_settings, "rb").read()).hexdigest() if os.path.isfile(_settings) else None
    with tempfile.TemporaryDirectory() as home:
        antes = _hash()
        env = dict(os.environ, USERPROFILE=home, HOME=home, PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, os.path.join(ROOT, "bootstrap.py"), "--regras-globais"],
                           capture_output=True, text=True, env=env, timeout=60, stdin=subprocess.DEVNULL)
        instalado = os.path.join(home, ".claude", "CLAUDE.md")
        ok = r.returncode == 0 and os.path.isfile(instalado)
        if ok:
            with open(instalado, encoding="utf-8-sig") as fh:
                ok = esperado in fh.read()
        if not ok:
            fails.append(f"`bootstrap.py --regras-globais` nao instalou no home falso: "
                         f"codigo {r.returncode}, {r.stdout.strip()[-120:]} {r.stderr.strip()[-120:]}")
        if _hash() != antes:
            fails.append("`bootstrap.py --regras-globais` alterou o .claude/settings.json do projeto")

    print(f"repo real PASS; 4 classes de drift pegas em fixture — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (linter pega drift e nao da falso-positivo no repo real)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
