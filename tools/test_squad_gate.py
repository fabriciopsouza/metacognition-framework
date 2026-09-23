"""Canario do squad_gate (ADR-092) — FAIL-CLOSED. Prova que o gate:
- exige qa-critic para mudanca de codigo;
- so aceita evidencia ATESTADA (agentId + modelo != autor) — auto-atestacao NAO passa (anti-teatro);
- so aceita evidencia ESCOPADA aos paths avaliados (ADR-103 emenda 1) — evidencia antiga
  NAO e' carta-branca retroativa;
- exige architect para ADR;
- fecha juncao de release por match ANCORADO na versao, nao por substring.
Sem este teste verde, J3 do bloco do ADR-092 NAO fecha.
"""
import os
import io
import json

import squad_gate as sg

MANIFEST = sg.load_manifest()


def _ev(recomendacao="aprovar", agentId="", modelo="", autor="", escopo=("tools/", "docs/adr/"),
        sha="__HEAD__"):
    """Veredito de teste.

    `escopo` = escopo_paths declarado (ADR-103 emenda 1): veredito sem escopo NAO conta —
    passe escopo=() para exercitar esse caso.
    `sha` = sha_revisado (emenda 3): por padrao usa o HEAD, para que os testes de caminho
    feliz continuem exercitando o que querem exercitar; passe sha="" ou um sha antigo para
    exercitar a checagem de recencia.
    """
    if sha == "__HEAD__":
        sha = sg._git("rev-parse", "HEAD") or ""
    # `problemas` entra SEMPRE, mesmo vazia: desde o ADR-115 a chave e' obrigatoria, e um helper
    # que produzisse veredito sem ela estaria fabricando um objeto que o gate (com razao) recusa.
    return {"bloco": "x", "passou": True, "recomendacao": recomendacao,
            "escopo_paths": list(escopo), "sha_revisado": sha, "problemas": [],
            "atestacao": {"agentId": agentId, "modelo": modelo, "autor": autor}}


def test_classify_codigo_exige_qa_critic():
    assert "qa_critic" in sg.classify(["src/x.py"], MANIFEST)


def test_classify_adr_exige_architect_e_qa():
    req = sg.classify(["docs/adr/099-foo.md"], MANIFEST)
    assert "architect" in req and "qa_critic" in req


def test_codigo_sem_evidencia_BLOQUEIA():
    faltam, _ = sg.evaluate(["src/x.py"], MANIFEST, artifacts=[])
    assert "qa_critic" in faltam


def test_codigo_com_evidencia_atestada_PASSA():
    ev = _ev(agentId="a4c1ac49", modelo="claude-haiku", autor="claude-opus")
    faltam, _ = sg.evaluate(["tools/squad_gate.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" not in faltam


def test_auto_atestacao_NAO_passa():
    # modelo == autor (mesmo agente) -> teatro -> rejeitado
    ev = _ev(agentId="self", modelo="claude-opus", autor="claude-opus")
    faltam, _ = sg.evaluate(["src/x.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam


def test_sem_agentId_NAO_passa():
    ev = _ev(agentId="", modelo="claude-haiku", autor="claude-opus")
    faltam, _ = sg.evaluate(["src/x.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam


def test_doc_comum_nao_exige_qa():
    assert sg.classify(["docs/guia/leia.md"], MANIFEST) == set()


def test_adr_com_qa_atestado_passa():
    ev = _ev(agentId="a4c1", modelo="claude-haiku", autor="claude-opus")
    faltam, _ = sg.evaluate(["docs/adr/103-ativacao-do-squad-gate-como-bloqueio.md"], MANIFEST, artifacts=[ev])
    # architect OK (path e adr) e qa_critic OK (atestado) -> nada falta
    assert faltam == []



# --- fail-closed no veredito (ADR-115) ---------------------------------------------------
# O gate exigia apenas o ROTULO aprovativo e a atestacao de isolamento; nunca olhava a
# severidade nem o estado dos achados. Um 'aprovar_com_ressalvas' carregando um ALTA em
# aberto passava. Em 13/09/2026 havia um veredito real (rodada 14) com ALTA — corrigido, mas
# nada no mecanismo garantia isso.

def _ev_com(problemas, recomendacao="aprovar_com_ressalvas"):
    v = _ev(recomendacao=recomendacao, agentId="a1", modelo="sonnet", autor="opus")
    v["problemas"] = problemas
    return v


def test_aprovativo_com_ALTA_aberto_NAO_passa():
    v = _ev_com([{"severidade": "ALTA", "estado": "aberto", "descricao": "x"}])
    assert not sg._atestacao_valida(v), "ALTA em aberto nao pode passar como aprovativo"


def test_aprovativo_com_ALTA_corrigido_passa():
    v = _ev_com([{"severidade": "ALTA", "estado": "corrigido", "descricao": "x"}])
    assert sg._atestacao_valida(v), "ALTA corrigido deve passar"


def test_severidade_reconhecida_em_TODAS_as_grafias_do_ledger():
    """O ledger escreve a mesma gravidade de muitas formas; casar so com 'ALTA' deixa passar o
    resto. Sem numero aqui de proposito — docstring nao tem quem o recalcule (12a rodada)."""
    for grafia in ("ALTA", "ALTO", "CRITICO", "BLOQUEANTE", "GRAVE", "MEDIA-ALTA",
                   "ALTO-EVITADO", "alta", " Alto "):
        v = _ev_com([{"severidade": grafia, "estado": "aberto"}])
        assert not sg._atestacao_valida(v), "grafia %r deveria bloquear" % grafia


def test_grafia_DESCONHECIDA_bloqueia_fail_closed():
    """Vocabulario que ninguem previu trava o gate e pede classificacao — nao passa mudo."""
    v = _ev_com([{"severidade": "CATASTROFICO", "estado": "aberto"}])
    assert not sg._atestacao_valida(v), "severidade desconhecida tem de bloquear"


def test_severidade_AUSENTE_bloqueia():
    """Quem nao declarou severidade nao classificou — nao da para assumir que e' leve."""
    assert not sg._atestacao_valida(_ev_com([{"estado": "aberto", "descricao": "x"}]))


def test_estado_AUSENTE_bloqueia_em_veredito_do_SCHEMA_NOVO():
    """Basta um achado declarar `estado` para o veredito inteiro ser cobrado."""
    v = _ev_com([{"severidade": "BAIXA", "estado": "corrigido"},
                 {"severidade": "ALTA", "descricao": "sem estado"}])
    assert not sg._atestacao_valida(v), "schema novo com estado faltando tem de bloquear"


def test_veredito_LEGADO_ENUMERADO_nao_e_cobrado_mas_e_DECLARADO():
    """So os 20 vereditos nominais, COM o conteudo original, sao isentos — e ficam listados."""
    nome = "v1.54.0-release.json"
    legado = _ev_com([{"severidade": "ALTO", "descricao": "CORRIGIDO. algo"}])
    legado["_arquivo"] = nome
    legado["_sha256"] = sg.VEREDITOS_LEGADOS[nome]
    assert sg.veredito_legado(legado)
    assert sg._atestacao_valida(legado), "legado nao pode ser reprovado retroativamente"
    assert sg.legados_declarados(), "a divida legada tem de ficar VISIVEL, nao perdoada"


def test_legado_SOBRESCRITO_perde_a_isencao():
    """O bypass da 2a rodada: `qa_evidence.write_artifact` grava sem checar existencia, entao
    bastava SOBRESCREVER um dos 20 arquivos congelados para herdar a isencao dele."""
    v = _ev_com([{"severidade": "CRITICO", "descricao": "bypass por sobrescrita"}])
    v["_arquivo"] = "v1.54.0-release.json"      # nome legitimo
    v["_sha256"] = "deadbeefdeadbeef"           # conteudo trocado
    assert not sg.veredito_legado(v), "conteudo alterado nao herda a isencao do nome"
    assert not sg._atestacao_valida(v), "CRITICO em aberto tem de bloquear"


def test_legado_SEM_hash_nao_e_legado():
    """Veredito sintetico, ou vindo de fora do ledger, nao compra isencao por ter o nome certo."""
    v = _ev_com([{"severidade": "CRITICO", "descricao": "x"}])
    v["_arquivo"] = "v1.54.0-release.json"
    assert not sg.veredito_legado(v), "sem `_sha256` nao da para afirmar que o conteudo e' o original"


def test_hash_dos_legados_BATE_com_o_disco():
    """Detector de deriva: se algum dos 20 arquivos legados mudou, o congelamento e' mentira.

    Sem isto, editar um legado passaria despercebido — o gate diria 'nao e' legado' e o achado
    seria cobrado (fail-closed, ok), mas ninguem saberia que a lista congelada envelheceu.
    """
    import os
    divergentes = []
    for nome, esperado in sorted(sg.VEREDITOS_LEGADOS.items()):
        caminho = os.path.join(sg.QA_DIR, nome)
        if not os.path.exists(caminho):
            divergentes.append((nome, "SUMIU"))
            continue
        real = sg.sha_do_veredito(caminho)
        if real != esperado:
            divergentes.append((nome, "%s != %s" % (real, esperado)))
    assert not divergentes, "vereditos legados alterados desde o congelamento: %s" % divergentes


def test_OMITIR_estado_NAO_compra_isencao():
    """O bypass que a revisao adversarial reproduziu contra o binario real.

    A 1a versao detectava legado por SCHEMA: 'nenhum achado tem estado'. Como o AUTOR controla
    se o campo existe, bastava omiti-lo para um CRITICO em aberto passar. Agora a isencao e'
    NOMINAL e congelada — omitir campo nao compra nada.
    """
    v = _ev_com([{"severidade": "CRITICO", "descricao": "nunca resolvido, sem campo estado"}])
    assert not sg.veredito_legado(v), "veredito sem `_arquivo` nao pode ser legado"
    assert not sg._atestacao_valida(v), "CRITICO em aberto tem de bloquear"


def test_legado_FORJADO_por_nome_inventado_nao_passa():
    v = _ev_com([{"severidade": "ALTO", "descricao": "x"}])
    v["_arquivo"] = "v9.99.9-que-nunca-existiu.json"
    assert not sg.veredito_legado(v), "nome fora da lista congelada nao e' legado"
    assert not sg._atestacao_valida(v)


def test_listado_explicitamente_tambem_normaliza_a_caixa():
    """19a rodada: a NONA assimetria, e a primeira da serie que e' puramente FAIL-CLOSED.

    `_cobre` ganhou casefold na 18a; a irma que faz a mesma pergunta para arquivo NOVO nao ganhou.
    O efeito nao e' deixar passar — e' RECUSAR cobertura legitima, empurrando o operador para
    `--no-verify`, que e' pior que o buraco. As duas tem de responder igual para o mesmo par.
    """
    v = {"escopo_paths": ["Tools/Foo.py"]}
    assert sg._cobre(v["escopo_paths"], "tools/foo.py"), "premissa: _cobre reconhece"
    assert sg._listado_explicitamente(v, "tools/foo.py"), "a irma tem de reconhecer tambem"
    assert not sg._listado_explicitamente({"escopo_paths": ["tools/outro.py"]}, "tools/foo.py"), (
        "arquivo diferente continua fora")
    assert not sg._listado_explicitamente({"escopo_paths": ["tools/"]}, "tools/foo.py"), (
        "prefixo de diretorio NAO e' mencao nominal — esta funcao existe justamente para exigir o nome")


def test_cobre_NAO_se_deixa_enganar_pela_caixa_do_escopo():
    """18a rodada, e a OITAVA assimetria entre irmaos: `classify` ganhou casefold na 15a, `_cobre` nao.

    O caminho destravado era o pior: `_cobre` serve aos DOIS lados, entao uma reprovacao com CRITICO
    aberto, mesmo sha, mesmo arquivo, deixava de invalidar o aprovativo so' porque `escopo_paths`
    trazia `Tools/Squad_Gate.py` em vez de `tools/squad_gate.py`.
    """
    assert sg._cobre(["Tools/Squad_Gate.py"], "tools/squad_gate.py"), "mesmo arquivo, outra caixa"
    assert sg._cobre(["TOOLS/"], "tools/x.py"), "prefixo de diretorio idem"
    assert not sg._cobre(["tools/outro.py"], "tools/squad_gate.py"), "arquivo diferente segue fora"

    sha = sg._git("rev-parse", "HEAD") or ""
    alvo = ["tools/squad_gate.py"]
    apr = _ev(recomendacao="aprovar", agentId="a1", modelo="m2", autor="m1",
              escopo=tuple(alvo), sha=sha)
    rep = _ev(recomendacao="reprovar", agentId="a2", modelo="m2", autor="m1",
              escopo=("Tools/Squad_Gate.py",), sha=sha)
    rep["problemas"] = [{"severidade": "CRITICO", "estado": "aberto", "descricao": "vivo"}]
    assert sg._reprovacao_vigente([apr, rep], apr, alvo), "a reprovacao tem de morder"
    assert not sg._qa_critic_attested([apr, rep], alvo), "e o aprovativo nao pode passar"


def test_chave_JSON_duplicada_nao_apaga_achado():
    """24a rodada, e o furo mais barato dos vinte e quatro: `json.load` colapsa chave duplicada.

    A segunda ocorrencia vence e a primeira some, SEM erro — antes de qualquer validacao deste
    arquivo rodar. Entao `CAMPOS_CONHECIDOS`, `CAMPOS_DO_ACHADO`, a chave obrigatoria `problemas` e
    a defesa contra homoglifo ficam todas inuteis: o dict chega com uma unica chave, canonica, de
    tipo certo. Nao precisa de Unicode nem de ma-fe — copiar um template e esquecer de apagar o
    bloco anterior basta.

    Cobre as DUAS formas, e exige que a recusa seja BARULHENTA: descartar calado seria fail-open do
    lado da reprovacao, porque um veredito reprovativo com chave duplicada sumiria e pararia de
    morder.
    """
    import contextlib
    import io as _io
    import shutil
    import tempfile

    sha = sg._git("rev-parse", "HEAD") or ""
    casos = {
        "estado_duplicado.json":
            '{"recomendacao":"aprovar","atestacao":{"agentId":"s","modelo":"m2","autor":"m1"},'
            '"escopo_paths":["tools/squad_gate.py"],"sha_revisado":"%s",'
            '"problemas":[{"severidade":"CRITICO","estado":"aberto","estado":"corrigido",'
            '"descricao":"o achado some"}]}' % sha,
        "problemas_duplicado.json":
            '{"recomendacao":"aprovar","atestacao":{"agentId":"s","modelo":"m2","autor":"m1"},'
            '"escopo_paths":["tools/squad_gate.py"],"sha_revisado":"%s",'
            '"problemas":[{"severidade":"CRITICO","estado":"aberto","descricao":"x"}],'
            '"problemas":[]}' % sha,
    }
    tmp = tempfile.mkdtemp(prefix="qa-dup-canario-")
    try:
        for nome, conteudo in casos.items():
            _io.open(os.path.join(tmp, nome), "w", encoding="utf-8").write(conteudo)
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            arts = sg.load_evidence(tmp)
            faltam, _det = sg.evaluate(["tools/squad_gate.py"], sg.load_manifest(), arts)
        aviso = buf.getvalue().lower()

        # CONTRATO CORRIGIDO na 25a rodada. A 24a exigia aqui `arts == []` — ou seja, que o arquivo
        # ilegivel simplesmente SUMISSE. Era o contrato errado, e o teste passava justamente por
        # isso: uma reprovacao LEGITIMA com chave duplicada num campo irrelevante desaparecia do
        # julgamento e o aprovativo ao lado passava sozinho. O certo e' "nao consigo confirmar =>
        # nao passa": o ilegivel entra MARCADO e o gate TRAVA.
        assert any(isinstance(a, dict) and a.get("_recusado") for a in arts), (
            "o arquivo ilegivel tem de entrar MARCADO, nao sumir: %r" % arts)
        assert faltam, "evidencia ilegivel no ledger tem de TRAVAR o gate, nao so' gerar aviso"
        for nome in casos:
            assert nome.lower() in aviso, (
                "a recusa tem de NOMEAR o arquivo (%s), senao ninguem sabe o que corrigir. "
                "Saida:\n%s" % (nome, aviso))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # e o ledger REAL continua carregando — a checagem nao pode ser um bloqueio geral
    assert sg.load_evidence(), "o ledger real deixou de carregar"


def test_TODA_forma_de_ilegivel_trava_o_gate():
    """26a rodada: a correcao da 25a cobria SO' `ChaveDuplicada`. O resto sumia em silencio.

    Metade da correcao pela segunda vez seguida. A regra "nao consigo confirmar => nao passa" nao
    admite excecao por TIPO de erro: arquivo truncado, vazio, `null` no topo, lista no topo,
    encoding invalido — todos escondem exatamente a mesma coisa, uma reprovacao que deixou de ser
    lida.

    O vetor nao e' hipotetico: `qa_evidence.write_artifact()` grava com `json.dump` direto no
    arquivo final, SEM temp-file + rename. Interrupcao durante a escrita deixa .json truncado.
    """
    import contextlib
    import io as _io
    import shutil
    import tempfile

    sha = sg._git("rev-parse", "HEAD") or ""
    aprovativo = ('{"recomendacao":"aprovar","atestacao":{"agentId":"s","modelo":"m2",'
                  '"autor":"m1"},"escopo_paths":["tools/squad_gate.py"],"sha_revisado":"%s",'
                  '"problemas":[]}' % sha)
    bom = ('{"recomendacao":"reprovar","escopo_paths":["tools/squad_gate.py"],'
           '"sha_revisado":"%s","problemas":[{"severidade":"CRITICO","estado":"aberto",'
           '"descricao":"vigente"}]}' % sha)
    formas = {
        "truncado": bom[:-5],
        "vazio": "",
        "null_no_topo": "null",
        "lista_no_topo": "[1,2,3]",
        "chave_duplicada": bom[:-1] + ',"resumo":"a","resumo":"b"}',
    }
    for nome, conteudo in formas.items():
        tmp = tempfile.mkdtemp(prefix="qa-ileg-")
        try:
            _io.open(os.path.join(tmp, "aprovativo.json"), "w", encoding="utf-8").write(aprovativo)
            _io.open(os.path.join(tmp, "rep.json"), "w", encoding="utf-8").write(conteudo)
            buf = _io.StringIO()
            with contextlib.redirect_stdout(buf):
                arts = sg.load_evidence(tmp)
                faltam, _ = sg.evaluate(["tools/squad_gate.py"], sg.load_manifest(), arts)
            assert faltam, "forma %r nao travou o gate — a reprovacao sumiu" % nome
            assert "rep.json" in buf.getvalue(), (
                "forma %r nao NOMEIA o arquivo a corrigir: %s" % (nome, buf.getvalue()))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # encoding invalido precisa de bytes crus
    tmp = tempfile.mkdtemp(prefix="qa-ileg-enc-")
    try:
        _io.open(os.path.join(tmp, "aprovativo.json"), "w", encoding="utf-8").write(aprovativo)
        with open(os.path.join(tmp, "rep.json"), "wb") as fh:
            fh.write(b'{"recomendacao":"reprovar","x":"\xff\xfe"}')
        with contextlib.redirect_stdout(_io.StringIO()):
            arts = sg.load_evidence(tmp)
            faltam, _ = sg.evaluate(["tools/squad_gate.py"], sg.load_manifest(), arts)
        assert faltam, "encoding invalido nao travou o gate"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # A checagem nao pode virar bloqueio geral: diretorio SO' com evidencia legivel nao trava.
    # Deterministico de proposito — a versao anterior desta assercao usava o ledger REAL do
    # repositorio e ficava vermelha dentro da arvore temporaria da prova por mutacao, onde o gate
    # bloqueia por falta de cobertura. E' a mesma armadilha que a 21a rodada pegou: teste cujo
    # significado muda com o estado do repo nao mede o que diz medir.
    tmp = tempfile.mkdtemp(prefix="qa-ileg-ok-")
    try:
        _io.open(os.path.join(tmp, "aprovativo.json"), "w", encoding="utf-8").write(aprovativo)
        with contextlib.redirect_stdout(_io.StringIO()):
            limpo = sg.load_evidence(tmp)
        assert not any(isinstance(a, dict) and a.get("_recusado") for a in limpo), (
            "evidencia legivel nao pode ser marcada como ilegivel")
        assert not sg.evaluate(["tools/squad_gate.py"], sg.load_manifest(), limpo)[0], (
            "diretorio so' com evidencia legivel nao pode travar")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_reprovacao_ILEGIVEL_nao_deixa_o_aprovativo_passar():
    """25a rodada: a correcao da 24a trocou um fail-open por outro, e este canario guarda o certo.

    Cenario reproduzido pelo critico: uma reprovacao LEGITIMA — CRITICO aberto correto, mesmo
    `sha_revisado`, mesmo escopo — com uma chave duplicada num campo IRRELEVANTE (`resumo`). A 24a
    descartava o arquivo e seguia; a reprovacao sumia do julgamento e o aprovativo ao lado passava
    sozinho, reabrindo exatamente o que as rodadas 8, 9 e 10 fecharam.

    O gate jogava fora a PROVA do bloqueio em vez de trata-la COMO bloqueio.
    """
    import contextlib
    import io as _io
    import shutil
    import tempfile

    sha = sg._git("rev-parse", "HEAD") or ""
    tmp = tempfile.mkdtemp(prefix="qa-ilegivel-")
    try:
        _io.open(os.path.join(tmp, "aprovativo.json"), "w", encoding="utf-8").write(
            '{"recomendacao":"aprovar","atestacao":{"agentId":"s","modelo":"m2","autor":"m1"},'
            '"escopo_paths":["tools/squad_gate.py"],"sha_revisado":"%s","problemas":[]}' % sha)
        _io.open(os.path.join(tmp, "reprovativo_dup.json"), "w", encoding="utf-8").write(
            '{"recomendacao":"reprovar","escopo_paths":["tools/squad_gate.py"],'
            '"sha_revisado":"%s","resumo":"a","resumo":"b",'
            '"problemas":[{"severidade":"CRITICO","estado":"aberto","descricao":"vigente"}]}' % sha)
        with contextlib.redirect_stdout(_io.StringIO()):
            arts = sg.load_evidence(tmp)
            faltam, _ = sg.evaluate(["tools/squad_gate.py"], sg.load_manifest(), arts)
        assert faltam, (
            "aprovativo limpo ao lado de reprovacao ILEGIVEL nao pode passar — a reprovacao pode "
            "ser justamente a que o derrubaria")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_matriz_cobre_os_INTERRUPTORES_do_proprio_mecanismo():
    """16a rodada: a matriz protegia o codigo e esquecia quem LIGA e DESLIGA o gate.

    `.github/workflows/` e' onde `continue-on-error` decide se o squad-gate e' advisory ou
    bloqueante (ADR-104); `.claude/agents/` e' onde mora a definicao do proprio qa-critic, que
    declara "contexto isolado" e "hipotese default: existe bug". Editar qualquer um dos dois nao
    exigia papel nenhum — dava para religar o advisory, remover o step, ou reescrever o criterio do
    critico, em silencio.

    Este canario guarda a CLASSE, nao os dois casos: todo arquivo que controla o comportamento do
    gate tem de exigir alguem. Se a matriz perder qualquer um, aqui fica vermelho.
    """
    man = sg.load_manifest()
    interruptores = [
        ".github/workflows/ci.yml",          # liga/desliga o gate no CI
        ".claude/agents/qa-critic.md",       # define o que o critico e'
        "behaviors/manifest.json",           # e' a propria matriz
        "tools/squad_gate.py",               # e' o gate
        "CLAUDE.md",                         # e' a regra que manda rodar tudo isso
        ".claude/settings.json",             # configura os hooks: desarma o gate sem tocar nele
        "tools/model-policy.json",           # define o que e' "um degrau abaixo do autor"
        ".agent/workflows/start-session.md",  # orquestra a sequencia do squad (sync, WIP, boot)
        ".claude/settings.nonadmin.json",     # o bootstrap copia isto POR CIMA do settings.json
        ".gitignore",                        # decide o que o git VE, logo o que o gate avalia
        "tools/hooks/effect-gate.ps1",        # bloqueia acao destrutiva; fallback ativo em NON-ADMIN
        ".claude/hooks/check-repo-sync.ps1",  # o gate de sincronia, so' existe em .ps1
        "tools/hooks/effect-gate.sh",         # o mesmo gate para host POSIX (paridade ADR-039/040)
        # Os arquivos de DADOS que os gates LEEM. 23a rodada: `suffix: .py` cobria o
        # codigo e deixava de fora a lista que ele consulta — remover uma linha aqui
        # desarma o gate sem tocar no gate, e a matriz dizia "papel nenhum".
        "tools/sensitive-denylist.txt",       # o que o export/publish RECUSA publicar
        "tools/anonymize-map.txt",            # o que o anonimizador troca antes de publicar
        "tools/effect-rules.json",            # o que o effect-gate considera destrutivo
        "tools/agnostic-denylist.txt",        # o que conta como vazamento no nucleo
        # Os interruptores da RAIZ, onde nenhum prefixo de pasta alcanca.
        # 24a e 25a rodadas: `capabilities.json` decide o que e' fail-closed, e
        # `.repo-identity.json` parametriza o classificador que libera escrita.
        "capabilities.json",                  # decide enforcement e se ha' prova
        "CAPABILITIES.md",                    # espelho publico do registro
        ".repo-identity.json",                # editar um campo = writable_master
        "_meta/enforcement-baseline.json",    # dispensa do bloqueio: desliga o ALVO
        ".claude/commands/start-session.md",  # a "primeira acao obrigatoria" do CLAUDE.md
    ]
    for alvo in interruptores:
        assert sg.classify([alvo], man), "%s controla o gate e nao exige papel nenhum" % alvo
        faltam, _ = sg.evaluate([alvo], man, [])
        assert faltam, "%s com ledger vazio nao pode passar" % alvo


def test_classify_normaliza_o_prefixo_ponto_barra():
    """16a rodada (BAIXA): `./_shared/x.md` nao casava com o prefixo `_shared/`.

    Os dois pontos de invocacao reais (`git diff --cached --name-only` e o `--paths-from` do CI)
    nao emitem `./`, entao a reprodutibilidade e' baixa — mas `--paths` aceita o que lhe derem, e
    normalizar custa uma linha.
    """
    man = sg.load_manifest()
    for p in ("_shared/foo.md", "docs/adr/999-x.md", "tools/x.py"):
        assert sg.classify(["./" + p], man) == sg.classify([p], man), (
            "./%s tem de ser o mesmo que %s" % (p, p))

    # LIMITE DECLARADO, guardado aqui para a prosa do ADR nao envelhecer sozinha (17a rodada):
    # `../` e caminho absoluto NAO sao resolvidos. O casamento por SUFIXO sobrevive a eles (`.py`
    # continua no fim da string); o casamento por PREFIXO e por EXACT, nao. Nenhuma das duas formas
    # vem de `git diff --cached`, que e' sempre relativo a raiz.
    assert sg.classify(["../tools/x.py"], man) == sg.classify(["tools/x.py"], man), (
        "sufixo tem de sobreviver ao ../")
    assert not sg.classify(["../_shared/foo.md"], man), (
        "prefixo com ../ nao casa — se passar a casar, a tabela do ADR ficou errada")


def test_classify_NAO_se_deixa_enganar_pela_caixa_do_path():
    """15a rodada, e o bypass mais barato dos quinze: `tools/backdoor.PY` nao exigia papel nenhum.

    `classify` comparava suffix/prefix/exact como string crua. Sem forjar atestacao, sem Unicode,
    sem homoglifo — so' trocando a caixa da extensao, um .py NOVO passava com ledger vazio.
    """
    man = sg.load_manifest()
    for disfarce, canonico in (("tools/backdoor.PY", "tools/backdoor.py"),
                               ("tools/Backdoor.Py", "tools/backdoor.py"),
                               ("Docs/ADR/999-x.MD", "docs/adr/999-x.md")):
        esperado = sg.classify([canonico], man)
        if not esperado:
            continue                      # a matriz nao cobre este caminho; nada a provar
        assert sg.classify([disfarce], man) == esperado, (
            "%r tem de exigir os mesmos papeis que %r" % (disfarce, canonico))
        faltam, _ = sg.evaluate([disfarce], man, [])
        assert faltam, "%r com ledger vazio nao pode passar" % disfarce


def test_norm_modelo_funde_separador_AUSENTE_sem_colidir_modelos_reais():
    """15a rodada: trocar separador por espaco so' funde quando os DOIS lados tem separador.

    `gpt-4` virava 'gpt 4' e `gpt4` continuava 'gpt4' — mesmo modelo, gate via dois. Basta OMITIR
    um hifen. A segunda metade do teste guarda o defeito INVERSO: normalizacao agressiva demais
    faria o gate REJEITAR evidencia legitima, que e' pior do que o bypass.
    """
    iguais = [("gpt-4", "gpt4"), ("claude-sonnet-5", "claudesonnet5"),
              ("claude-opus-5", "claude opus 5"), ("o1", "O1"), ("haiku_4_5", "haiku-4-5")]
    for a, b in iguais:
        assert sg._norm_modelo(a) == sg._norm_modelo(b), "%r e %r sao o mesmo modelo" % (a, b)

    reais_distintos = ["claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5", "claude-fable-5-1",
                       "gpt-4", "gpt-4o", "o1", "o3-mini", "gemini-2-5-pro", "llama-3-70b"]
    vistos = {}
    for nome in reais_distintos:
        n = sg._norm_modelo(nome)
        assert n not in vistos, "colisao entre modelos DIFERENTES: %r e %r" % (vistos.get(n), nome)
        vistos[n] = nome


def test_autoatestacao_disfarcada_por_caixa_espaco_ou_invisivel():
    """14a rodada: `modelo != autor` era comparacao de string CRUA.

    O mesmo modelo escrito com caixa diferente, espaco duplo ou zero-width space passava como se
    fossem dois modelos. A vizinha `assinatura_valida` ja normalizava contra isso no mesmo arquivo.
    """
    base = {"recomendacao": "aprovar", "problemas": [],
            "escopo_paths": ["tools/squad_gate.py"], "sha_revisado": "0" * 40}
    disfarces = [
        ("Claude-Sonnet-5", "claude-sonnet-5"),          # caixa
        ("claude-sonnet-5\u200b", "claude-sonnet-5"),    # zero-width space
        ("claude  sonnet-5", "claude sonnet-5"),         # espaco duplo interno
        ("claude_sonnet_5", "claude-sonnet-5"),          # separador diferente
        (" claude-sonnet-5 ", "claude-sonnet-5"),        # espaco nas pontas
    ]
    for modelo, autor in disfarces:
        v = dict(base, atestacao={"agentId": "x", "modelo": modelo, "autor": autor})
        assert not sg._atestacao_valida(v), "autoatestacao disfarcada: %r vs %r" % (modelo, autor)
    # e modelos DE VERDADE diferentes continuam valendo
    for modelo, autor in (("sonnet", "opus"), ("claude-sonnet-5", "claude-opus-5"),
                          ("haiku-4-5", "fable-5-1")):
        v = dict(base, atestacao={"agentId": "x", "modelo": modelo, "autor": autor})
        assert sg._atestacao_valida(v), "par legitimo tem de passar: %r vs %r" % (modelo, autor)


def test_git_que_FALHA_nao_e_o_mesmo_que_nada_staged():
    """14a rodada, o achado mais grave: main() lia stdout sem olhar returncode.

    Git que falha devolve stdout vazio; 'nao consegui perguntar' virava 'nada staged', nenhum papel
    era exigido e o gate saia 0 — e o pre-commit instalado so' olha a mensagem quando o codigo e'
    != 0. Commit liberado sem avaliar evidencia, sem aviso.
    """
    import subprocess as _sp
    real = sg.subprocess.run
    chamadas = []

    class _R:
        returncode, stdout, stderr = 128, "", "fatal: detected dubious ownership in repository"

    def falso(cmd, *a, **k):
        if list(cmd[:3]) == ["git", "diff", "--cached"]:
            chamadas.append(cmd)
            return _R()
        return real(cmd, *a, **k)

    sg.subprocess.run = falso
    try:
        rc = sg.main([])
    finally:
        sg.subprocess.run = real
    assert chamadas, "o teste nao chegou a exercitar o caminho do git"
    assert rc != 0, "git quebrado tem de BLOQUEAR, nunca sair 0 como se nada estivesse staged"


def test_atestacao_SEM_campo_autor_nao_prova_isolamento():
    """13a rodada, e o bypass mais barato dos treze: `autor` era opcional.

    `(not autor or modelo != autor)` devolvia True quando o campo faltava — o autor podia escrever
    o proprio veredito aprovativo do proprio codigo sem mentir em nada, so' omitindo uma linha, e o
    gate chamava isso de evidencia de critico isolado. Na checagem que da NOME ao mecanismo.
    """
    base = {"recomendacao": "aprovar", "problemas": [],
            "escopo_paths": ["tools/squad_gate.py"], "sha_revisado": "0" * 40}
    teatro = dict(base, atestacao={"agentId": "qualquer", "modelo": "claude-opus"})
    assert not sg._atestacao_valida(teatro), "atestacao sem `autor` nao prova isolamento"
    for vazio in ("", "   ", None):
        assert not sg._atestacao_valida(dict(base, atestacao={
            "agentId": "x", "modelo": "sonnet", "autor": vazio})), "autor vazio idem"
    assert not sg._atestacao_valida(dict(base, atestacao={
        "agentId": "x", "modelo": "sonnet", "autor": "sonnet"})), "autoatestacao continua barrada"
    assert sg._atestacao_valida(dict(base, atestacao={
        "agentId": "x", "modelo": "sonnet", "autor": "opus"})), "atestacao completa passa"
    assert sg._atestacao_valida(dict(base, atestacao={
        "agentId": "x", "modelo": "sonnet", "modelo_autor": "opus"})), "o nome legado do campo vale"

    # e o caminho que o main() usa de verdade, nao so' a funcao isolada
    faltam, det = sg.evaluate(["tools/squad_gate.py"], sg.load_manifest(), [teatro])
    assert det.get("qa_critic") is not True, "o teatro nao pode chegar ao veredito do gate"


def test_reprovacao_SEM_achado_estruturado_ainda_veta():
    """11a rodada, e o ADR ao contrario: dez rodadas cacaram o aprovativo que ESCONDE achado, e
    sobrou a reprovacao que nao MOSTRA achado nenhum — lida como 'ja tratada', nao vetava nada.

    Cobre os dois irmaos na mesma assercao, porque o predicado passou a ser compartilhado.
    """
    import re
    sha = sg._git("rev-parse", "HEAD") or ""
    alvo = ["tools/squad_gate.py"]
    apr = _ev(recomendacao="aprovar", agentId="b", modelo="m2", autor="m1",
              escopo=tuple(alvo), sha=sha)
    for vazia in ({}, {"problemas": []}):
        rep = _ev(recomendacao="reprovar", agentId="a", modelo="m2", autor="m1",
                  escopo=tuple(alvo), sha=sha)
        rep.pop("problemas", None)
        rep.update(vazia)
        assert sg._reprovacao_vigente([apr, rep], apr, alvo), (
            "reprovacao sem achado estruturado nao pode passar por tratada: %r" % vazia)

    pad = re.compile(re.escape("1.79.0"))
    apr_r = _release("aprovar", "1.79.0", [])
    rep_r = _release("reprovar", "1.79.0", [])
    assert not sg._release_verdict_approving([apr_r, rep_r], pad), "mesmo buraco no irmao do release"


def test_sha_revisado_SIMBOLICO_nao_vale_como_hash():
    """10a rodada: `rev-parse --verify HEAD^{commit}` resolve qualquer ref, e ref SE MOVE.

    `sha_revisado: "HEAD"` nunca envelheceria — reabre o B2/B2-r2 pela porta do FORMATO. Mesma
    licao do ADR: nao enumerar as refs proibidas, enumerar a forma certa (hex, 7 a 40).
    """
    for simbolico in ("HEAD", "main", "origin/main", "HEAD~1", "v1.79.0", "@", "refs/heads/main"):
        assert not sg._eh_sha_hex(simbolico), "%r nao e' hash" % simbolico
        assert sg._sha_pleno(simbolico) == "", "%r nao pode virar commit" % simbolico
        v = _ev(recomendacao="aprovar", agentId="b", modelo="m2", autor="m1",
                escopo=("tools/squad_gate.py",), sha=simbolico)
        assert not sg._recente_o_bastante(v, ["tools/squad_gate.py"]), (
            "%r nao pode atestar recencia" % simbolico)
    sha = sg._git("rev-parse", "HEAD") or ""
    if len(sha) == 40:
        assert sg._eh_sha_hex(sha) and sg._eh_sha_hex(sha[:7]), "hash real vale, curto e longo"


def test_reprovacao_JA_TRATADA_nao_trava_o_proprio_bloco():
    """Achado do AUTOR entre a 9a e a 10a rodada, e a 3a assimetria entre irmaos deste ADR.

    `_reprovacao_vigente` contava qualquer reprovacao de mesmo sha+escopo, sem olhar se restava
    achado ABERTO — enquanto `_reprovacao_de_release_vigente`, escrita na mesma rodada e tres
    funcoes abaixo, ja olhava. Neste fluxo a correcao acontece na ARVORE DE TRABALHO, entao o
    commit nao muda e os dois vereditos compartilham o sha: sem esta checagem, um bloco que
    corrigiu tudo trava para sempre. Fail-closed nao e' o mesmo que travado.
    """
    sha = sg._git("rev-parse", "HEAD") or ""
    alvo = ["tools/squad_gate.py"]
    apr = _ev(recomendacao="aprovar", agentId="b", modelo="m2", autor="m1",
              escopo=tuple(alvo), sha=sha)
    tratada = _ev(recomendacao="reprovar", agentId="a", modelo="m2", autor="m1",
                  escopo=tuple(alvo), sha=sha)
    tratada["problemas"] = [{"severidade": "CRITICO", "estado": "corrigido", "descricao": "ja foi"}]
    assert not sg._reprovacao_vigente([apr, tratada], apr, alvo), "reprovacao tratada nao trava"

    aberta = _ev(recomendacao="reprovar", agentId="a", modelo="m2", autor="m1",
                 escopo=tuple(alvo), sha=sha)
    aberta["problemas"] = [{"severidade": "CRITICO", "estado": "aberto", "descricao": "vivo"}]
    assert sg._reprovacao_vigente([apr, aberta], apr, alvo), "reprovacao aberta continua travando"


def test_reprovacao_SEM_escopo_paths_cobre_tudo():
    """9a rodada: `escopo_paths` e' opcional, e `if escopo_r and ...` fazia reprovacao sem escopo
    nunca invalidar nada. Reprovacao que nao delimita o que revisou e' MAIS ampla, nao menos."""
    sha = sg._git("rev-parse", "HEAD") or ""
    alvo = ["tools/squad_gate.py"]
    apr = _ev(recomendacao="aprovar", agentId="b", modelo="m2", autor="m1",
              escopo=tuple(alvo), sha=sha)
    rep = _ev(recomendacao="reprovar", agentId="a", modelo="m2", autor="m1", sha=sha)
    rep.pop("escopo_paths", None)
    rep["problemas"] = [{"severidade": "CRITICO", "estado": "aberto", "descricao": "sem escopo"}]
    assert sg._reprovacao_vigente([apr, rep], apr, alvo), "reprovacao sem escopo tem de cobrir tudo"
    rep["escopo_paths"] = []
    assert sg._reprovacao_vigente([apr, rep], apr, alvo), "escopo vazio idem"


def test_reprovacao_com_sha_CURTO_e_detectada():
    """9a rodada: 27 dos 29 vereditos com `sha_revisado` gravam 7 chars; rev-parse devolve 40.
    `_recente_o_bastante` ja normalizava e esta funcao nao — mesmo commit, deteccao perdida."""
    sha = sg._git("rev-parse", "HEAD") or ""
    if len(sha) != 40:
        return                       # sem git nao ha o que provar aqui
    alvo = ["tools/squad_gate.py"]
    apr = _ev(recomendacao="aprovar", agentId="b", modelo="m2", autor="m1",
              escopo=tuple(alvo), sha=sha)
    rep = _ev(recomendacao="reprovar", agentId="a", modelo="m2", autor="m1",
              escopo=tuple(alvo), sha=sha[:7])
    rep["problemas"] = [{"severidade": "CRITICO", "estado": "aberto", "descricao": "sha curto"}]
    assert sg._reprovacao_vigente([apr, rep], apr, alvo), "curto e longo sao o mesmo commit"


def _release(rec, rel, problemas):
    return {"recomendacao": rec, "release": rel, "problemas": problemas,
            "atestacao": {"agentId": "a-" + rec, "modelo": "m2", "autor": "m1"}}


def test_juncao_de_RELEASE_nao_fecha_com_reprovacao_aberta_do_mesmo_release():
    """9a rodada, e o achado mais incomodo: eu AFIRMEI no ADR e no docstring que este papel ja
    tinha a defesa da 8a rodada. Nunca teve — inferi pelo NOME de um teste que cobre outro caso."""
    import re
    pad = re.compile(re.escape("1.79.0"))
    apr = _release("aprovar", "1.79.0", [])
    rep = _release("reprovar", "1.79.0",
                   [{"severidade": "CRITICO", "estado": "aberto", "descricao": "aberto"}])
    assert not sg._release_verdict_approving([apr, rep], pad), "reprovacao aberta trava o release"
    assert sg._release_verdict_approving([apr], pad), "release limpo continua fechando"
    ok = _release("reprovar", "1.79.0",
                  [{"severidade": "CRITICO", "estado": "corrigido", "descricao": "ja resolvido"}])
    assert sg._release_verdict_approving([apr, ok], pad), "achado RESOLVIDO nao pode travar"


def test_REPROVACAO_vigente_invalida_aprovativo_do_mesmo_escopo():
    """O bypass da 8a rodada: bastava depositar um aprovativo vazio ao lado da reprovacao.

    `_qa_critic_attested` devolvia True no PRIMEIRO aprovativo, sem olhar se havia reprovacao para
    o mesmo `sha_revisado` e o mesmo escopo.

    RETRATACAO: a versao anterior deste docstring dizia que "o mecanismo ja existia para
    `juncao_release`". Era FALSO — a 9a rodada provou que nunca existiu ali; eu inferi pelo NOME de
    um teste, sem ler o corpo. O ADR, o CHANGELOG e o docstring em `squad_gate.py` foram retratados
    na hora; ESTE arquivo passou batido, e a 10a rodada encontrou a alegacao falsa viva aqui. Uma
    retratacao que nao varre todos os arquivos e' meia retratacao.
    """
    sha = sg._git("rev-parse", "HEAD") or ""
    alvo = ["tools/squad_gate.py"]
    rep = _ev(recomendacao="reprovar", agentId="a", modelo="m2", autor="m1",
              escopo=tuple(alvo), sha=sha)
    rep["problemas"] = [{"severidade": "CRITICO", "estado": "aberto", "descricao": "real"}]
    apr = _ev(recomendacao="aprovar", agentId="b", modelo="m2", autor="m1",
              escopo=tuple(alvo), sha=sha)
    assert not sg._qa_critic_attested([rep, apr], alvo), "reprovacao vigente tem de vencer"
    assert sg._qa_critic_attested([apr], alvo), "aprovativo sozinho continua liberando"


def test_reprovacao_de_OUTRO_sha_nao_invalida():
    """Reprovacao de um estado anterior do codigo nao pode travar o commit para sempre."""
    alvo = ["tools/squad_gate.py"]
    apr = _ev(recomendacao="aprovar", agentId="b", modelo="m2", autor="m1", escopo=tuple(alvo))
    rep = _ev(recomendacao="reprovar", agentId="a", modelo="m2", autor="m1",
              escopo=tuple(alvo), sha="0" * 40)
    rep["problemas"] = [{"severidade": "CRITICO", "estado": "aberto", "descricao": "antiga"}]
    assert sg._qa_critic_attested([rep, apr], alvo), "reprovacao de outro sha nao e' vigente"


def test_assinatura_recusa_PLACEHOLDER_e_ate_a_frase_que_NEGA():
    """`aceito_por: "nao assinado"` TEM letra latina — e nega a assinatura. Passava."""
    for falso in ("nao assinado", "N/A", "n/a", "x", "-", "Nao", "ok", "sim", "pendente",
                  "a definir", "ninguem", "TBD", "autor", "dono"):
        v = _ev_com([{"severidade": "CRITICO", "estado": "aceito", "aceito_por": falso}])
        assert not sg._atestacao_valida(v), "%r nao e' assinatura" % falso
    for real in ("Fabricio", "F. Souza", "José da Conceição"):
        v = _ev_com([{"severidade": "CRITICO", "estado": "aceito", "aceito_por": real}])
        assert sg._atestacao_valida(v), "%r e' assinatura" % real


def test_achado_ANINHADO_dentro_de_achado_leve_nao_escapa():
    """A 7a rodada escondeu um CRITICO/aberto DENTRO de um achado BAIXA, em chave arbitraria."""
    v = _ev_com([{"severidade": "BAIXA", "descricao": "cosmetico",
                  "sub_achado": {"severidade": "CRITICO", "estado": "aberto"}}])
    assert not sg._atestacao_valida(v), "achado aninhado tem de bloquear"


def test_campo_DESCONHECIDO_dentro_do_achado_bloqueia():
    v = _ev_com([{"severidade": "BAIXA", "descricao": "x", "campo_inventado": 1}])
    assert not sg._atestacao_valida(v)


def test_LEDGER_REAL_so_usa_campos_de_achado_conhecidos():
    """Contra-prova: a allowlist do achado nao pode reprovar os 243 achados que ja existem."""
    fora = [(v.get("_arquivo"), i, sg.campos_de_achado_desconhecidos(p))
            for v in sg.load_evidence() if isinstance(v, dict)
            for i, p in enumerate(v.get("problemas") or []) if isinstance(p, dict)
            and sg.campos_de_achado_desconhecidos(p)]
    assert not fora, "achados com campo fora de CAMPOS_DO_ACHADO: %s" % fora[:3]


def test_assinatura_exige_letra_LATINA_nao_so_categoria_L():
    """U+3164 HANGUL FILLER TEM categoria `Lo` — para o Unicode e' letra, para o olho e' vazio.

    Por isso a regra e' de SCRIPT, nao de categoria. O limite (so latino) e' declarado no codigo.
    """
    for vazio in (chr(0x3164), chr(0x2800), chr(0x180E), chr(0x200B), " ", ""):
        v = _ev_com([{"severidade": "CRITICO", "estado": "aceito", "aceito_por": vazio}])
        assert not sg._atestacao_valida(v), "%r nao e' assinatura" % vazio
    # Isola a regra de SCRIPT: nomes de 2+ letras que passam por comprimento e por placeholder,
    # e so caem pela exigencia de latino. Sem estes, a checagem de tamanho mascarava a de script
    # e a mutacao correspondente sobrevivia — canario que nao isola a defesa nao a prova.
    for nao_latino in ("Иван", "あい", "李明", "ㅤㅤ"):
        v = _ev_com([{"severidade": "CRITICO", "estado": "aceito", "aceito_por": nao_latino}])
        assert not sg._atestacao_valida(v), (
            "%r nao e' latino — limite DECLARADO no codigo, nao descuido" % nao_latino)
    # "F." normaliza para "f": UMA letra nao assina aceite de risco critico. O minimo e' 2.
    for nome in ("Fabricio", "José da Conceição", "F. Souza"):
        v = _ev_com([{"severidade": "CRITICO", "estado": "aceito", "aceito_por": nome}])
        assert sg._atestacao_valida(v), "%r e' assinatura de verdade" % nome


def test_atestacao_MALFORMADA_bloqueia_sem_derrubar_o_gate():
    """`atestacao` como lista derrubava o processo com AttributeError.

    Um unico .json ruim em _meta/qa/ travava o gate para TODO commit — fail-closed por crash
    nao e' fail-closed: nega o trabalho legitimo sem diagnostico.
    """
    for ruim in (["x"], "texto", 7, None):
        v = _ev_com([])
        v["atestacao"] = ruim
        assert sg._atestacao_valida(v) is False, "atestacao %r tem de bloquear, nao explodir" % ruim


def test_chave_homoglifa_UNICODE_ao_lado_da_canonica_nao_esconde():
    """O bypass da 6a rodada: declarar `problemas: []` limpa e esconder o CRITICO na irma.

    `problemаs` com 'a' CIRILICO e' visualmente identico e nao colide com nada em ASCII. Exigir
    a chave canonica nao bastava, porque o atacante TAMBEM a declara. A defesa e' a allowlist:
    campo de topo que o gate nao conhece bloqueia.
    """
    cirilico = "problem" + chr(0x430) + "s"
    v = _ev(recomendacao="aprovar", agentId="a1", modelo="sonnet", autor="opus")
    v[cirilico] = [{"severidade": "CRITICO", "estado": "aberto", "descricao": "escondido"}]
    assert sg.campos_desconhecidos(v) == [cirilico]
    assert not sg._atestacao_valida(v), "achado sob chave homoglifa Unicode tem de bloquear"


def test_campo_de_topo_DESCONHECIDO_bloqueia():
    """Qualquer chave fora do conjunto conhecido e' esconderijo em potencial."""
    v = _ev(recomendacao="aprovar", agentId="a1", modelo="sonnet", autor="opus")
    v["campo_que_ninguem_declarou"] = "x"
    assert not sg._atestacao_valida(v)


def test_LEDGER_REAL_so_usa_campos_conhecidos():
    """Contra-prova: a allowlist nao pode reprovar o ledger que ja existe."""
    fora = [(v.get("_arquivo"), sg.campos_desconhecidos(v)) for v in sg.load_evidence()
            if isinstance(v, dict) and sg.campos_desconhecidos(v)]
    assert not fora, "vereditos com campo fora de CAMPOS_CONHECIDOS: %s" % fora


def test_assinatura_INVISIVEL_nao_encerra_achado_bloqueante():
    """`aceito_por = "\u200b"`: str.strip() nao remove zero-width, e o CRITICO ficava 'assinado'."""
    for invisivel in (chr(0x200B), chr(0xFEFF), chr(0x00AD), chr(0x200B) + " "):
        v = _ev_com([{"severidade": "CRITICO", "estado": "aceito", "aceito_por": invisivel}])
        assert not sg._atestacao_valida(v), "assinatura invisivel (%r) nao e' assinatura" % invisivel
    real = _ev_com([{"severidade": "CRITICO", "estado": "aceito", "aceito_por": "Fabricio Souza"}])
    assert sg._atestacao_valida(real), "assinatura de verdade tem de passar"


def test_HOMOGLIFO_na_chave_nao_esconde_o_achado():
    """`probIemas` (I maiusculo no lugar do l) escapava da lista de grafias e virava passe livre.

    A defesa nao e' reconhecer o homoglifo — e' exigir a chave canonica. Depois de I/l viria
    O/0, depois cirilico, depois zero-width: enumerar grafia errada e' corrida perdida.
    """
    v = _ev(recomendacao="aprovar", agentId="a1", modelo="sonnet", autor="opus")
    v.pop("problemas")                      # o atacante nao declara a canonica...
    v["probIemas"] = [{"severidade": "CRITICO", "estado": "aberto", "descricao": "escondido"}]
    assert not sg._atestacao_valida(v), "achado sob chave homoglifa tem de bloquear"


def test_chave_problemas_AUSENTE_bloqueia():
    """Ausencia de campo nao e' ausencia de achado: sem `problemas`, o gate nao sabe nada."""
    v = _ev(recomendacao="aprovar", agentId="a1", modelo="sonnet", autor="opus")
    v.pop("problemas")                      # o helper sempre declara; aqui tiramos de proposito
    assert not sg._atestacao_valida(v), "veredito sem a chave canonica tem de bloquear"


def test_problemas_VAZIO_declarado_passa():
    """Declarar `problemas: []` e' a forma de dizer 'revisei e nao achei nada'."""
    assert sg._atestacao_valida(_ev_com([])), "lista vazia declarada deve passar"


def test_problemas_MALFORMADO_bloqueia_em_vez_de_isentar():
    """`problemas` como dict ou lista de strings caia no ramo de isencao SEM crash.

    `"estado" in p` faz SUBSTRING quando p e' string — schema malformado virava passe livre.
    """
    como_dict = _ev_com({"a": {"severidade": "ALTA", "estado": "aberto"}})
    como_strings = _ev_com(["ALTA em aberto: falha X"])
    assert not sg._atestacao_valida(como_dict), "problemas como dict tem de bloquear"
    assert not sg._atestacao_valida(como_strings), "problemas como lista de str tem de bloquear"


def test_CHAVE_problemas_com_MAIUSCULA_nao_esconde_o_achado():
    """O bypass da rodada 3, reproduzido pelo critico contra o binario real (exit 0).

    As rodadas 1-3 validaram o que estava DENTRO de `problemas` e nunca a propria chave:
    `v.get("problemas")` e' sensivel a maiuscula, e chave ausente significava "nada a cobrar".
    Um CRITICO em aberto sob `Problemas` desaparecia — ausencia de dado e dado ilegivel
    colapsavam no mesmo ramo.
    """
    achado = [{"severidade": "CRITICO", "estado": "aberto", "descricao": "furo grave"}]
    for grafia in ("Problemas", "PROBLEMAS", "achados", "Findings", "ocorrencias", "problemas_"):
        v = _ev(recomendacao="aprovar_com_ressalvas", agentId="a1", modelo="sonnet", autor="opus")
        v[grafia] = achado
        assert not sg._atestacao_valida(v), (
            "chave %r escondeu um CRITICO em aberto — o gate passaria" % grafia)


def test_DUAS_chaves_de_achados_e_ambiguo_e_bloqueia():
    """`problemas: []` ao lado de `ACHADOS: [CRITICO]` nao pode virar 'nada a cobrar'."""
    v = _ev_com([])
    v["ACHADOS"] = [{"severidade": "CRITICO", "estado": "aberto"}]
    assert not sg._atestacao_valida(v), "duas chaves de achados tem de bloquear por ambiguidade"


def test_chave_canonica_DECLARADA_vazia_ou_nula_passa():
    """Contra-prova: exigir a chave nao pode transformar veredito limpo em bloqueio.

    Este teste nasceu na 4a rodada afirmando que a AUSENCIA da chave continuava passando. A 5a
    rodada mostrou que era justamente por ai que um homoglifo (`probIemas`) escondia um CRITICO,
    e a chave virou obrigatoria — o nome e a justificativa antigos deste teste ficaram FALSOS,
    e ele passou a nao testar o que dizia. Reescrito: o que passa e' a chave DECLARADA vazia ou
    nula; ausencia e' bloqueio, coberto por `test_chave_problemas_AUSENTE_bloqueia`.

    Medido em 13/09/2026: os 64 vereditos do ledger ja declaram `problemas`, entao exigi-la nao
    reescreve o passado.
    """
    vazio = _ev(recomendacao="aprovar", agentId="a1", modelo="sonnet", autor="opus")
    assert vazio["problemas"] == [], "o helper tem de declarar a chave, mesmo vazia"
    assert sg._atestacao_valida(vazio), "`problemas: []` e' 'revisei e nao achei' — passa"
    nulo = _ev_com(None, recomendacao="aprovar")
    assert sg._atestacao_valida(nulo), "`problemas: null` e' 'nada declarado', nao malformado"


def test_LEDGER_REAL_so_usa_a_chave_canonica():
    """Detector de deriva: se um veredito novo entrar com outra grafia, isto acusa.

    Sem este teste a regra acima seria uma afirmacao sobre o passado que ninguem re-verifica.
    """
    import glob, json, os
    fora = []
    for caminho in sorted(glob.glob(os.path.join(sg.QA_DIR, "*.json"))):
        try:
            v = json.load(io.open(caminho, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(v, dict):
            continue
        for k in v:
            if k not in sg.CAMPOS_CONHECIDOS:
                fora.append((os.path.basename(caminho), k))
    assert not fora, "vereditos com chave de achados nao-canonica: %s" % fora


def test_main_IMPRIME_a_divida_legada():
    """O ADR afirma que a divida legada 'fica visivel, nao perdoada em silencio'. Aqui se EXECUTA.

    Historico deste teste, que e' a licao:

    1. A 1a versao LIA O TEXTO-FONTE e procurava a string `legados_declarados()`. Prova textual
       dentro do canario de um ADR que existe para cacar isso. A 20a rodada provou o ponto cego
       desligando a CONDICAO e mantendo a chamada: o teste seguiu verde com a impressao morta.
    2. A 2a versao passou a EXECUTAR `main()` — e isso achou um defeito real: a divida so' era
       impressa no caminho de SUCESSO. Corrigido no `main()`.
    3. Mas o docstring da 2a versao AFIRMAVA que "se a linha sumir, por qualquer motivo, isto fica
       vermelho", e a 21a rodada mostrou que era FALSO: a chamada caia no caminho de sucesso contra
       o ledger real, exatamente onde o bug antigo TAMBEM imprimia. O teste nao distinguia "sempre
       imprime" de "imprime quando da certo".

    Esta versao forca os DOIS caminhos de proposito. O de bloqueio e' forcado por substituicao de
    `evaluate`, nao pela escolha de um path que por acaso nao tenha cobertura hoje — assim o teste
    nao muda de significado quando o ledger muda.
    """
    import contextlib
    import io as _io

    if not sg.legados_declarados():
        return                      # sem divida legada nao ha o que imprimir; nada a provar

    def _saida_de_main(forcar_bloqueio):
        real = sg.evaluate
        if forcar_bloqueio:
            sg.evaluate = lambda *a, **k: (["qa_critic"], {"qa_critic": False})
        buf = _io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                try:
                    sg.main(["--paths", "tools/squad_gate.py"])
                except SystemExit:
                    pass
        finally:
            sg.evaluate = real      # restaura SEMPRE, inclusive se a assercao abaixo estourar
        return buf.getvalue().lower()

    passou = _saida_de_main(False)
    assert "divida legada declarada" in passou, (
        "main() nao imprimiu a divida no caminho de SUCESSO. Saida:\n" + passou[-600:])

    bloqueou = _saida_de_main(True)
    assert "bloqueado" in bloqueou, "o caminho de bloqueio nao foi forcado — o teste nao prova nada"
    assert "divida legada declarada" in bloqueou, (
        "main() nao imprimiu a divida no caminho de BLOQUEIO — e' exatamente o defeito que a 20a "
        "rodada corrigiu, e quem esta bloqueado e' quem mais precisa ver o passivo. Saida:\n"
        + bloqueou[-600:])

def test_severidade_LEVE_em_aberto_nao_bloqueia():
    for grafia in ("BAIXA", "BAIXO", "MEDIA", "MEDIO", "INFORMATIVO", "MENOR"):
        v = _ev_com([{"severidade": grafia, "estado": "aberto"}])
        assert sg._atestacao_valida(v), "%r e' leve e nao deveria bloquear" % grafia


def test_ALTA_aceita_exige_ASSINATURA_de_quem_assumiu():
    """'aceito' sozinho nao encerra achado bloqueante: risco alto assumido tem dono."""
    sem = _ev_com([{"severidade": "ALTA", "estado": "aceito"}])
    com = _ev_com([{"severidade": "ALTA", "estado": "aceito", "aceito_por": "Fabricio Souza"}])
    assert not sg._atestacao_valida(sem), "aceito sem assinatura nao pode passar"
    assert sg._atestacao_valida(com), "aceito COM assinatura deve passar"


def test_nenhum_veredito_do_ledger_quebra_com_a_regra():
    """Regra nova nao pode reescrever o passado em silencio: medido, zero quebras.

    Usa `load_evidence` — o caminho REAL de carregamento do gate — e nao um json.load proprio:
    e' ele que marca `_arquivo`, e sem essa marca o teste mediria um mundo que nao existe.
    """
    quebrados = [v.get("_arquivo") for v in sg.load_evidence()
                 if isinstance(v, dict) and v.get("recomendacao") in sg.APPROVING
                 and sg.achados_bloqueantes_abertos(v)]
    assert not quebrados, "vereditos aprovativos com bloqueante aberto: %s" % quebrados


# ---------------------------------------------------------------------------
# Matriz ampliada (ADR-103): skill de nucleo/papel e regra sempre-ativa passam a
# exigir revisao. Antes devolviam "papeis exigidos: nenhum" — medido na sessao.
# ---------------------------------------------------------------------------

def test_skill_de_nucleo_exige_qa_critic():
    assert "qa_critic" in sg.classify(["_shared/project-docs/SKILL.md"], MANIFEST)


def test_skill_de_papel_e_regra_exigem_qa_critic():
    assert "qa_critic" in sg.classify([".agent/skills/docops/SKILL.md"], MANIFEST)
    assert "qa_critic" in sg.classify([".agent/rules/00-glossario.md"], MANIFEST)


def test_a_propria_matriz_exige_qa_critic():
    """Sem isto o gate se auto-afrouxa: bastaria editar a matriz sem revisao."""
    assert "qa_critic" in sg.classify(["behaviors/manifest.json"], MANIFEST)


# ---------------------------------------------------------------------------
# ADR-103 emenda 1 — achados BLOQUEANTE 2 e GRAVE 3 da 2a rodada (2026-08-13).
# Antes destes testes as funcoes novas nao tinham cobertura NENHUMA.
# ---------------------------------------------------------------------------

def test_evidencia_SEM_escopo_declarado_NAO_libera():
    """O gate se auto-liberava para sempre: UM veredito aprovativo em qualquer lugar de
    _meta/qa/ bastava para QUALQUER mudanca futura. Sem escopo declarado, nao conta."""
    ev = _ev(agentId="a1", modelo="claude-sonnet", autor="claude-opus", escopo=())
    faltam, _ = sg.evaluate(["src/x.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam


def test_evidencia_de_OUTRO_escopo_NAO_libera():
    """Veredito que revisou src/ nao pode liberar mudanca em _shared/."""
    ev = _ev(agentId="a1", modelo="claude-sonnet", autor="claude-opus", escopo=("src/",))
    faltam, _ = sg.evaluate(["_shared/project-docs/SKILL.md"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam


def test_evidencia_ESCOPADA_libera_so_o_que_cobre():
    ev = _ev(agentId="a1", modelo="claude-sonnet", autor="claude-opus",
             escopo=("_shared/", "docs/adr/"))
    faltam, _ = sg.evaluate(["_shared/project-docs/SKILL.md",
                             "docs/adr/102-padrao-do-conjunto-documental-de-projeto.md"],
                            MANIFEST, artifacts=[ev])
    assert faltam == []


def test_escopo_parcial_NAO_libera_o_conjunto():
    """Cobrir 1 de 2 paths nao basta — o gate avalia o conjunto."""
    ev = _ev(agentId="a1", modelo="claude-sonnet", autor="claude-opus", escopo=("_shared/",))
    faltam, _ = sg.evaluate(["_shared/a/SKILL.md", "tools/outro.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam


def test_cobre_e_prefixo_de_PATH_nao_de_string():
    assert sg._cobre(["_shared"], "_shared/a/SKILL.md") is True
    assert sg._cobre(["_shared"], "_shared_antigo/a/SKILL.md") is False


def test_juncao_release_match_ANCORADO(tmp_path, monkeypatch):
    """Substring livre casava versao errada: '1.79.0' in 'release-21.79.0-x' era True."""
    qa = tmp_path / "qa"
    (qa / "junctions").mkdir(parents=True)
    (tmp_path / "CHANGELOG.md").write_text("# c\n\n## [1.79.0] - x\n", encoding="utf-8")
    monkeypatch.setattr(sg, "QA_DIR", str(qa))
    monkeypatch.setattr(sg, "ROOT", str(tmp_path))
    led = qa / "junctions" / "l.jsonl"

    # (a) versao DIFERENTE que contem a corrente como substring -> NAO libera
    led.write_text(json.dumps({"junction": "PC", "bloco": "release-21.79.0-x"}) + "\n",
                   encoding="utf-8")
    assert sg._release_junction_closed() is False

    # (b) fechamento de OUTRA versao -> NAO libera
    led.write_text(json.dumps({"junction": "PC", "bloco": "v1.58.0-adr-079-080"}) + "\n",
                   encoding="utf-8")
    assert sg._release_junction_closed() is False

    # (c) juncao que nao e' de fechamento -> NAO libera
    led.write_text(json.dumps({"junction": "J2", "bloco": "v1.79.0-project-docs"}) + "\n",
                   encoding="utf-8")
    assert sg._release_junction_closed() is False

    # (d) fechamento da versao corrente MAS sem veredito aprovativo vigente -> NAO libera
    #     (emenda 2 do ADR-103: presenca no ledger nao basta; ver o teste dedicado abaixo)
    led.write_text(json.dumps({"junction": "PC", "bloco": "v1.79.0-project-docs"}) + "\n",
                   encoding="utf-8")
    assert sg._release_junction_closed([]) is False

    # (e) fechamento legitimo + veredito aprovativo atestado do MESMO release -> libera
    ok = _ev(agentId="a1", modelo="sonnet", autor="opus")
    ok["release"] = "1.79.0"
    assert sg._release_junction_closed([ok]) is True


def test_juncao_release_REPROVACAO_POSTERIOR_invalida_o_PC(tmp_path, monkeypatch):
    """Achado BLOQUEANTE da 3a rodada (2026-08-13), reproduzido no repo real.

    O ledger e append-only e o PC e escrito UMA vez, no inicio do bloco. Sem checagem de
    veredito vigente, esse registro seguia liberando `juncao_release` mesmo depois de o QA
    REPROVAR o release duas vezes. Caso real: o unico registro de v1.79.0 nasceu em 4faf971
    (1o commit da serie) com `evidencia` dizendo "REPROVOU a 1a rodada", vieram 10 commits e
    2 reprovacoes, e `squad_gate --paths CHANGELOG.md` respondia OK.
    """
    qa = tmp_path / "qa"
    (qa / "junctions").mkdir(parents=True)
    (tmp_path / "CHANGELOG.md").write_text("## [1.79.0] - x\n", encoding="utf-8")
    monkeypatch.setattr(sg, "QA_DIR", str(qa))
    monkeypatch.setattr(sg, "ROOT", str(tmp_path))
    (qa / "junctions" / "l.jsonl").write_text(
        json.dumps({"junction": "PC", "bloco": "v1.79.0-project-docs"}) + "\n", encoding="utf-8")

    reprovado = _ev(recomendacao="reprovar", agentId="a1", modelo="sonnet", autor="opus")
    reprovado["release"] = "1.79.0"
    assert sg._release_junction_closed([reprovado]) is False, \
        "PC no ledger nao pode liberar release cujo veredito vigente REPROVA"

    # auto-atestacao (critico no MESMO modelo do autor) tambem nao vale como fechamento
    homogeneo = _ev(agentId="a1", modelo="opus", autor="opus")
    homogeneo["release"] = "1.79.0"
    assert sg._release_junction_closed([homogeneo]) is False, \
        "veredito sem heterogeneidade de modelo nao fecha juncao de release"

    # veredito aprovativo de OUTRO release nao serve
    outro = _ev(agentId="a1", modelo="sonnet", autor="opus")
    outro["release"] = "1.58.0"
    assert sg._release_junction_closed([outro]) is False


def test_juncao_release_SEM_ledger_bloqueia(tmp_path, monkeypatch):
    (tmp_path / "CHANGELOG.md").write_text("## [9.9.9] - x\n", encoding="utf-8")
    monkeypatch.setattr(sg, "QA_DIR", str(tmp_path / "qa"))
    monkeypatch.setattr(sg, "ROOT", str(tmp_path))
    assert sg._release_junction_closed() is False


def test_juncao_release_linha_corrompida_nao_libera(tmp_path, monkeypatch):
    """Fail-closed em ledger corrompido: linha invalida nao pode virar fechamento."""
    qa = tmp_path / "qa"
    (qa / "junctions").mkdir(parents=True)
    (tmp_path / "CHANGELOG.md").write_text("## [1.79.0] - x\n", encoding="utf-8")
    monkeypatch.setattr(sg, "QA_DIR", str(qa))
    monkeypatch.setattr(sg, "ROOT", str(tmp_path))
    (qa / "junctions" / "l.jsonl").write_text("{lixo nao-json\n", encoding="utf-8")
    assert sg._release_junction_closed() is False


def test_arquivo_NOVO_sem_historico_NAO_e_liberado_por_escopo_amplo():
    """Achado GRAVE da 8a rodada: o gemeo do defeito que a emenda 3 conserta.

    Antes, path sem historico no git fazia `continue`, e um veredito de escopo amplo
    ("tools/") com sha valido liberava um arquivo que nenhum critico jamais viu.
    """
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=("tools/",))
    assert sg._recente_o_bastante(ev, ["tools/_arquivo_que_nunca_existiu_xyz.py"]) is False
    faltam, _ = sg.evaluate(["tools/_arquivo_que_nunca_existiu_xyz.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam, "arquivo sem historico nao pode ser liberado por escopo amplo"

def test_arquivo_NOVO_passa_SO_com_escopo_EXPLICITO():
    """Emenda (2026-08-18): o `return False` seco tornava TODO arquivo novo permanentemente
    nao-commitavel — nao havia caminho legitimo para o primeiro commit de um arquivo que o
    critico REVISOU, e a regra empurrava para `--no-verify`, que e' pior que o buraco.

    O criterio que separa os casos e' o TIPO de cobertura, nao a existencia de historico:
    escopo AMPLO nao pode alcancar arquivo que nunca existiu (a lavagem que a 8a rodada
    barrou); path EXPLICITO so pode ter sido escrito por quem sabia que o arquivo existe.

    Este teste guarda as DUAS metades — sem a segunda assercao, a emenda teria reaberto o
    buraco original.
    """
    novo = "tools/_arquivo_que_nunca_existiu_xyz.py"

    # (a) escopo EXPLICITO libera: e' declaracao de que o critico viu ESTE arquivo.
    ex = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=(novo,))
    assert sg._recente_o_bastante(ex, [novo]) is True
    faltam, _ = sg.evaluate([novo], MANIFEST, artifacts=[ex])
    assert "qa_critic" not in faltam, "path explicito no escopo deveria liberar arquivo novo"

    # (b) escopo AMPLO continua barrando — a metade que nao pode regredir.
    amplo = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=("tools/",))
    assert sg._recente_o_bastante(amplo, [novo]) is False

    # (c) o auxiliar nao confunde prefixo com path exato.
    assert sg._listado_explicitamente(amplo, novo) is False
    assert sg._listado_explicitamente(ex, novo) is True

    # (d) Achado ALTO do qa-critic: path explicito sozinho deixava `sha_revisado` DECORATIVO
    #     neste ramo — sem `ultimo`, o merge-base nunca roda. Um veredito com o sha do
    #     PRIMEIRO commit da historia liberava o arquivo novo. Agora exige a ponta da branch.
    primeiro = sg._git("rev-list", "--max-parents=0", "HEAD").split()[0]
    velho = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=(novo,), sha=primeiro)
    assert sg._recente_o_bastante(velho, [novo]) is False, (
        "sha antigo nao pode liberar arquivo novo — seria 'revisado uma vez, liberado sempre'")

    # (e) sha inexistente tambem nao passa por aqui (fail-closed antes de chegar ao ramo).
    fake = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=(novo,), sha="0" * 40)
    assert sg._recente_o_bastante(fake, [novo]) is False
    # (f) sha CURTO (7 chars) e o que os vereditos reais gravam; o HEAD vem com 40.
    #     Comparar as strings cruas reprovava veredito legitimo — pego ao usar a emenda
    #     pela primeira vez. Os dois lados passam por rev-parse.
    curto = sg._git("rev-parse", "--short", "HEAD")
    ev_curto = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=(novo,), sha=curto)
    assert sg._recente_o_bastante(ev_curto, [novo]) is True, (
        "sha curto do HEAD deve ser aceito — e o formato que qa_evidence grava")


def test_recencia_veredito_SEM_sha_revisado_NAO_libera():
    """Emenda 3 (7a rodada): evidencia que nao diz sobre qual estado foi emitida nao vale."""
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=("src/",), sha="")
    assert sg._recente_o_bastante(ev, ["src/x.py"]) is False


def test_recencia_sha_inexistente_NAO_libera():
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=("src/",))
    ev["sha_revisado"] = "0" * 40  # sha que nao existe no repo
    assert sg._recente_o_bastante(ev, ["tools/squad_gate.py"]) is False


def test_recencia_sha_ANTIGO_nao_cobre_arquivo_editado_depois():
    """O caso real: veredito de 22:50 liberando arquivo modificado as 22:55.

    Pega o penultimo commit que tocou o proprio squad_gate.py e usa como `sha_revisado`:
    o ultimo commit do arquivo NAO e' ancestral dele, entao nao pode liberar.
    """
    historico = (sg._git("log", "-2", "--format=%H", "--", "tools/squad_gate.py") or "").split()
    if len(historico) < 2:
        return  # repo raso demais para exercitar; nao inventa resultado
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=("tools/",))
    ev["sha_revisado"] = historico[1]          # penultimo = anterior a ultima edicao
    assert sg._recente_o_bastante(ev, ["tools/squad_gate.py"]) is False


def test_recencia_sha_ATUAL_cobre():
    ultimo = sg._git("log", "-1", "--format=%H", "--", "tools/squad_gate.py")
    if not ultimo:
        return
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=("tools/",))
    ev["sha_revisado"] = ultimo
    assert sg._recente_o_bastante(ev, ["tools/squad_gate.py"]) is True


def test_evidencia_escopada_mas_ANTIGA_nao_libera_o_gate():
    """Integracao: escopo cobre, mas o veredito e' anterior -> `qa_critic` continua faltando."""
    historico = (sg._git("log", "-2", "--format=%H", "--", "tools/squad_gate.py") or "").split()
    if len(historico) < 2:
        return
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=("tools/",))
    ev["sha_revisado"] = historico[1]
    faltam, _ = sg.evaluate(["tools/squad_gate.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam, "veredito anterior a edicao nao pode liberar o gate"


# ---------------------------------------------------------------------------
# ADR-103 emenda 2 (3a e 4a rodadas, 2026-08-13/14): este arquivo e' pytest PURO. Sem o
# bloco abaixo, `run_canaries.py` o executava como script, o import definia as funcoes,
# o processo saia com 0 e o runner reportava PASS -- SEM rodar uma unica assercao.
# os testes do gate que governa o squad inteiro nunca haviam rodado no runner canonico.
#
# 4a RODADA — a 1a versao deste bloco delegava a `python -m pytest` e REPROVOU: o ADR-040
# ja rejeitara "pytest como entrypoint dos canarios", `pytest` nao esta em
# `requirements-dev.txt`, e a CI quebrou nos 3 SOs com "No module named pytest".
# Isso feria o principio declarado no proprio requirements-dev.txt: **ambiente nao
# reprova build**. Agora o entrypoint e' STDLIB PURA: implementa os dois unicos fixtures
# que estes testes usam (`tmp_path`, `monkeypatch`), descobre as funcoes `test_*` por
# introspecao e as executa. O arquivo continua coletavel por pytest para quem o tiver.
# ---------------------------------------------------------------------------
class _MonkeyPatch:
    """Substituto stdlib do fixture `monkeypatch` — so o que estes testes usam."""

    def __init__(self):
        self._undo = []

    def setattr(self, alvo, nome, valor):
        self._undo.append((alvo, nome, getattr(alvo, nome)))
        setattr(alvo, nome, valor)

    def desfazer(self):
        for alvo, nome, antigo in reversed(self._undo):
            setattr(alvo, nome, antigo)
        self._undo.clear()


def _descobrir():
    """Funcoes `test_*` DEFINIDAS NESTE ARQUIVO, em ordem de linha.

    Filtra por `__module__` e `isfunction` porque um callable `test_*` importado de outro
    modulo faria `getsourcelines` levantar OSError e derrubar a descoberta inteira antes de
    qualquer teste rodar (achado GRAVE latente da 5a rodada).
    """
    import inspect

    achadas = []
    for nome, obj in globals().items():
        if not nome.startswith("test_") or not inspect.isfunction(obj):
            continue
        if obj.__module__ != __name__:
            continue
        try:
            linha = inspect.getsourcelines(obj)[1]
        except OSError:
            linha = 10 ** 9  # nao localizavel: roda por ultimo, mas RODA
        achadas.append((linha, nome, obj))
    return [(n, f) for _, n, f in sorted(achadas)]


def _contar_no_fonte():
    """Quantas funcoes `test_*` de TOPO existem no ARQUIVO, por AST.

    A 1a versao usava regex `^def (test_\\w+)` e a 6a rodada achou o falso positivo: um
    exemplo dentro de docstring cuja linha comeca com `def test_algo():` era contado como
    definicao, a barreira disparava e reprovava o release inteiro por um artefato de prosa,
    com diagnostico enganoso. AST nao confunde texto com codigo.

    Retorna `None` so se o fonte nao puder ser lido — e nesse caso a barreira reprova, em
    vez de ser pulada em silencio (a versao anterior era fail-open aqui, contradizendo o
    proprio cabecalho FAIL-CLOSED deste arquivo).
    """
    import ast

    try:
        src = open(__file__, encoding="utf-8", errors="replace").read()
        arvore = ast.parse(src)
    except (OSError, SyntaxError):
        return None
    return sum(1 for no in arvore.body
               if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
               and no.name.startswith("test_"))


def _rodar_sem_pytest():
    import pathlib
    import shutil
    import tempfile
    import traceback
    import inspect

    testes = _descobrir()

    # ------------------------------------------------------------------
    # BARREIRA DE COMPLETUDE (5a rodada, 2026-08-13). Sem ela, um `def test_*`
    # escrito DEPOIS do bloco `if __name__` — o lugar mais natural para um dev
    # acrescentar codigo — nao existe em globals() quando a descoberta roda, e o
    # canario reporta "20 PASS / 0 FAIL" ignorando o teste novo em silencio.
    # O guard estatico do run_canaries.py nao pega isso: o bloco `if __name__`
    # ESTA no arquivo. Aqui a conta e' direta: descoberto tem de bater com o que
    # existe no fonte. Divergencia REPROVA.
    # ------------------------------------------------------------------
    # SQUAD_GATE_TESTES: filtro opcional, so para a prova por mutacao, que roda este canario 16
    # vezes e nao precisa dos 63 testes — precisa dos do bloco. Corta a suite em ~4x. Quando a
    # variavel nao esta setada (todo uso normal, incluindo run_canaries), NADA muda: roda tudo, e
    # a barreira de completude abaixo continua valendo. Filtrar por padrao seria canario cego.
    _filtro = os.environ.get("SQUAD_GATE_TESTES", "").strip()
    if _filtro:
        _quer = set(_filtro.split(","))
        testes = [(n, f) for n, f in testes if n in _quer]
        faltando = _quer - {n for n, _ in testes}
        if faltando:
            print("FAIL filtro pede teste(s) que nao existem: %s" % sorted(faltando))
            return 1
        falhas = []
        for nome, fn in testes:
            try:
                fn()
            except Exception:
                falhas.append((nome, traceback.format_exc()))
        for nome, tb in falhas:
            print("FAIL %s\n%s" % (nome, tb))
        print("RESULTADO: %d PASS / %d FAIL (de %d testes do squad_gate, FILTRADO)"
              % (len(testes) - len(falhas), len(falhas), len(testes)))
        return 1 if falhas else 0

    no_fonte = _contar_no_fonte()
    if no_fonte is None:
        # fail-closed: nao conseguir ler o proprio fonte nao pode virar "barreira pulada"
        print("FAIL barreira-de-completude: nao foi possivel ler/parsear o proprio arquivo "
              "para conferir a contagem de testes.")
        print("RESULTADO: 0 PASS / 1 FAIL (barreira de completude inoperante)")
        return 1
    if no_fonte != len(testes):
        print(f"FAIL barreira-de-completude: o arquivo define {no_fonte} funcao(oes) `test_*` "
              f"de topo, mas o entrypoint descobriu {len(testes)}.")
        print("     Causas possiveis, em ordem: (a) teste definido DEPOIS do bloco "
              "`if __name__ == \"__main__\":` — nao existe em globals() na hora da descoberta;")
        print("     (b) teste registrado dinamicamente em globals(), que nao aparece no fonte;")
        print("     (c) funcao `test_*` importada de outro modulo (o filtro por __module__ a "
              "descarta).")
        print("     Um teste que nao roda e' pior que um teste ausente: o verde mente.")
        print(f"RESULTADO: 0 PASS / {no_fonte} FAIL (de {no_fonte} testes do squad_gate)")
        return 1

    falhas = []
    for nome, fn in testes:
        params = inspect.signature(fn).parameters
        tmp = mp = None
        try:
            kwargs = {}
            if "tmp_path" in params:
                tmp = tempfile.mkdtemp(prefix="canario_sg_")
                kwargs["tmp_path"] = pathlib.Path(tmp)
            if "monkeypatch" in params:
                mp = _MonkeyPatch()
                kwargs["monkeypatch"] = mp
            desconhecidos = set(params) - set(kwargs)
            if desconhecidos:
                raise RuntimeError(
                    f"fixture nao suportado pelo entrypoint stdlib: {sorted(desconhecidos)} "
                    f"— implemente-o aqui ou o teste NAO roda no runner canonico"
                )
            fn(**kwargs)
        # BaseException, nao Exception (5a rodada): `SystemExit` herda de BaseException.
        # Um `sys.exit(0)` no meio da suite matava o processo ANTES da linha RESULTADO,
        # com stdout vazio e returncode 0 — e o run_canaries.py taggeava PASS sem que
        # uma unica assercao tivesse rodado. KeyboardInterrupt segue interrompendo.
        except KeyboardInterrupt:
            raise
        except BaseException:
            falhas.append((nome, traceback.format_exc()))
        finally:
            try:
                if mp is not None:
                    mp.desfazer()
            finally:
                if tmp:
                    shutil.rmtree(tmp, ignore_errors=True)

    for nome, tb in falhas:
        print(f"FAIL {nome}\n{tb}")
    print(f"RESULTADO: {len(testes) - len(falhas)} PASS / {len(falhas)} FAIL "
          f"(de {len(testes)} testes do squad_gate)")
    return 1 if falhas else 0


# ---------------------------------------------------------------------------------
# CONTEUDO ANTES DE COMMIT — achado ALTA da 36a rodada, endurecido na 37a.
#
# Os testes de recencia acima medem ancestralidade de COMMIT. No pre-commit de um bloco
# isso mede o que nao muda: por definicao todo arquivo do bloco esta' fora do HEAD, entao a
# resposta e' a mesma antes e depois de qualquer edicao nao commitada. Medido ao vivo: tres
# vereditos aprovativos de AGOSTO seguiam "recentes" para arquivos editados em SETEMBRO.
#
# CRITERIO DE ACEITE, medido e nao prometido: removendo o bloco `blobs` de
# `_recente_o_bastante`, os testes `IGUAL_ao_revisado_cobre` e `DIFERENTE_do_revisado_NAO_cobre`
# ficam VERMELHOS. A 1a versao deste comentario afirmava isso e era FALSA para o primeiro,
# porque ele usava `sha_revisado=HEAD` e a regra antiga tambem o cobria — o teste passava com
# ou sem o mecanismo. Agora o sha aponta para um commit ANTIGO, que a ancestralidade NAO cobre:
# so' o mecanismo novo explica o True.
# ---------------------------------------------------------------------------------
def _hash_do_indice_independente(path):
    """Hash do blob staged por subprocess PROPRIO — nunca via `sg._blob_indexado`.

    Derivar o esperado da funcao sob teste e' a fixture que le a propria constante: o critico
    da 37a rodada provou que, trocando `_blob_indexado` por uma que devolve hash fixo, o teste
    seguia verde porque os dois lados concordavam no erro. [ALTA da 37a rodada]
    """
    import subprocess
    r = subprocess.run(["git", "-C", sg.ROOT, "rev-parse", ":" + path],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", stdin=subprocess.DEVNULL)
    s = (r.stdout or "").strip()
    return s if (r.returncode == 0 and len(s) == 40) else None


def _sha_antigo_que_ancestralidade_nao_cobre(path):
    """Commit ANTERIOR a ultima edicao de `path`: a regra antiga reprova sobre ele."""
    hist = (sg._git("log", "-2", "--format=%H", "--", path) or "").split()
    return hist[1] if len(hist) >= 2 else None


def test_blobs_conteudo_IGUAL_ao_revisado_cobre():
    """Hash gravado == hash do indice: e' byte a byte o que o critico leu.

    O `sha_revisado` e' ANTIGO de proposito — a ancestralidade nao cobre este caso, entao um
    True aqui so' pode vir do mecanismo de conteudo.
    """
    alvo = "tools/squad_gate.py"
    atual = _hash_do_indice_independente(alvo)
    antigo = _sha_antigo_que_ancestralidade_nao_cobre(alvo)
    if not atual or not antigo:
        return                                  # repo raso ou sem git; nao inventa resultado
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=(alvo,))
    ev["sha_revisado"] = antigo
    assert sg._recente_o_bastante(ev, [alvo]) is False, (
        "a montagem do teste esta' errada: sem `blobs_revisados` este sha antigo TEM de reprovar, "
        "senao o caso nao discrimina mecanismo presente de ausente")
    ev["blobs_revisados"] = {alvo: atual}
    assert sg._recente_o_bastante(ev, [alvo]) is True


def test_blobs_conteudo_DIFERENTE_do_revisado_NAO_cobre():
    """O defeito que este campo fecha: arquivo editado depois da revisao, sem commit.

    Hash LITERAL, nao derivado da funcao sob teste (licao das rodadas 20, 21 e 37).
    """
    alvo = "tools/squad_gate.py"
    if not _hash_do_indice_independente(alvo):
        return
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=(alvo,))
    ev["blobs_revisados"] = {alvo: "1111111111111111111111111111111111111111"}
    assert sg._recente_o_bastante(ev, [alvo]) is False


def test_blobs_path_avaliado_SEM_carimbo_NAO_cobre():
    """Carimbar um caminho e cobrir outro nao vale — fail-closed por omissao."""
    alvo = "tools/squad_gate.py"
    atual = _hash_do_indice_independente(alvo)
    if not atual:
        return
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=(alvo, "tools/qa_evidence.py"))
    ev["blobs_revisados"] = {alvo: atual}       # o segundo path ficou de fora do carimbo
    assert sg._recente_o_bastante(ev, [alvo, "tools/qa_evidence.py"]) is False


def test_blobs_NAO_dispensam_sha_revisado_valido():
    """Achado CRITICO da 37a rodada: o atalho pulava a validacao de `sha_revisado`.

    `sha_revisado` nao serve so' a esta funcao — e' a CHAVE que `_reprovacao_vigente` usa para
    achar a reprovacao irma do mesmo estado do codigo. Com sha invalido a chave vira "" e uma
    reprovacao legitima deixa de invalidar o aprovativo. O atalho pode dispensar a
    ANCESTRALIDADE; nao pode dispensar a IDENTIDADE do commit revisado.
    """
    alvo = "tools/squad_gate.py"
    atual = _hash_do_indice_independente(alvo)
    if not atual:
        return
    for sha_ruim in ("HEAD", "main", "deadbeef", ""):
        ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=(alvo,))
        ev["sha_revisado"] = sha_ruim
        ev["blobs_revisados"] = {alvo: atual}   # conteudo CERTO, identidade PODRE
        assert sg._recente_o_bastante(ev, [alvo]) is False, (
            "sha_revisado=%r passou pelo atalho de blobs" % sha_ruim)


def test_blobs_path_com_barra_invertida_resolve_no_INDICE():
    """Achado ALTA da 37a rodada: `:tools\\x.py` nao resolve, e o fallback lia o DISCO.

    Num arquivo `MM` isso carimbava o conteudo NAO revisado. As duas formas de escrever o
    mesmo caminho tem de devolver o mesmo hash.
    """
    normal = "tools/squad_gate.py"
    invertida = normal.replace("/", chr(92))
    a = sg._blob_indexado(normal)
    b = sg._blob_indexado(invertida)
    if not a:
        return
    assert a == b, "barra invertida devolveu %r, barra normal devolveu %r" % (b, a)


def test_veredito_SEM_blobs_cai_na_regra_antiga_e_vira_divida_declarada():
    """Campo novo NAO e' retroativo: veredito antigo segue valendo e entra no relatorio.

    Fabricar o hash para veredito velho seria inventar a procedencia que o campo prova.
    """
    ultimo = sg._git("log", "-1", "--format=%H", "--", "tools/squad_gate.py")
    if not ultimo:
        return
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=("tools/",))
    ev["sha_revisado"] = ultimo
    assert "blobs_revisados" not in ev
    assert sg._recente_o_bastante(ev, ["tools/squad_gate.py"]) is True
    assert isinstance(sg.divida_sem_blobs(), list)


def test_veredito_cobre_o_PROPRIO_artefato_sem_carimbo():
    """A regressao infinita, quebrada onde o repo ja' a quebrava.

    O artefato de um veredito nao pode carregar o hash de si mesmo: quando `write_artifact`
    carimba, o arquivo ainda nao existe. Cobri-lo por um veredito seguinte so' empurra o
    problema. 15 vereditos do ledger ja' declaram os proprios `_meta/qa/*` em `escopo_paths`;
    a regra de conteudo nao pode tornar impossivel o que a regra antiga permitia, senao o
    efeito pratico e' empurrar para --no-verify. [37a rodada]
    """
    alvo = "tools/squad_gate.py"
    atual = _hash_do_indice_independente(alvo)
    if not atual:
        return
    proprio_json = "_meta/qa/veredito-fixture-xyz.json"
    proprio_md = "_meta/qa/veredito-fixture-xyz.md"
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus",
             escopo=(alvo, proprio_json, proprio_md))
    ev["_arquivo"] = "veredito-fixture-xyz.json"
    ev["blobs_revisados"] = {alvo: atual}       # so' o codigo carimbado; os dois artefatos nao
    assert sg._recente_o_bastante(ev, [alvo, proprio_json, proprio_md]) is True


def test_veredito_NAO_cobre_artefato_de_OUTRO_veredito():
    """A excecao e' estreita: vale para os dois arquivos do proprio veredito e mais nada."""
    alvo = "tools/squad_gate.py"
    atual = _hash_do_indice_independente(alvo)
    if not atual:
        return
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus",
             escopo=(alvo, "_meta/qa/veredito-de-OUTRO.json"))
    ev["_arquivo"] = "veredito-fixture-xyz.json"
    ev["blobs_revisados"] = {alvo: atual}
    assert sg._recente_o_bastante(ev, [alvo, "_meta/qa/veredito-de-OUTRO.json"]) is False


def test_excecao_do_artefato_NAO_alcanca_codigo():
    """Nem com `_arquivo` apontando para o ledger: codigo sem carimbo nunca passa."""
    alvo = "tools/squad_gate.py"
    outro = "tools/qa_evidence.py"
    atual = _hash_do_indice_independente(alvo)
    if not atual:
        return
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus", escopo=(alvo, outro))
    ev["_arquivo"] = "veredito-fixture-xyz.json"
    ev["blobs_revisados"] = {alvo: atual}
    assert sg._recente_o_bastante(ev, [alvo, outro]) is False


def test_veredito_SEM_arquivo_nao_tem_excecao():
    """Sintetico/de fora do ledger nao tem artefato proprio: fail-closed."""
    alvo = "tools/squad_gate.py"
    atual = _hash_do_indice_independente(alvo)
    if not atual:
        return
    ev = _ev(agentId="a1", modelo="sonnet", autor="opus",
             escopo=(alvo, "_meta/qa/qualquer.json"))
    ev["blobs_revisados"] = {alvo: atual}       # sem `_arquivo`
    assert sg._recente_o_bastante(ev, [alvo, "_meta/qa/qualquer.json"]) is False


# ---------------------------------------------------------------------------------
# UNIAO POR CAMINHO — achado MEDIA da 36a rodada, fechado na 37a.
#
# A regra anterior exigia UM veredito cobrindo TODOS os caminhos avaliados. O efeito era o
# inverso do pretendido: fechar um bloco de 91 caminhos exigia um veredito que DECLARASSE os
# 91, e nenhum critico sozinho revisou 91 arquivos — a regra FABRICAVA o veredito-cobertor,
# cuja forma sugere um exame unico que nao houve. O proprio veredito da 36a registrou isso
# contra si mesmo.
#
# O que estes canarios protegem NAO e' a uniao funcionar (isso e' o caso feliz) — e' ela nao
# virar porta: caminho sem veredito nenhum continua barrando, e cada caminho segue exigindo
# atestacao, recencia e ausencia de reprovacao vigente, agora AVALIADAS uma a uma, que e'
# mais estrito do que avaliar o conjunto de uma vez.
# ---------------------------------------------------------------------------------
def _ev_artefato(slug, **kw):
    """Veredito cujo escopo e' o PROPRIO artefato — recencia sem tocar no git por caminho.

    `_artefato_do_proprio_veredito` reconhece `_meta/qa/<slug>.json|.md` e PULA a checagem de
    conteudo antes de qualquer `git log`/`rev-parse` de caminho. Sobra so' o piso de sha, que
    e' `rev-parse HEAD` e existe em qualquer repo com um commit.

    POR QUE ASSIM, e o historico vale mais que a regra: a v1 destes testes usava caminhos
    inexistentes e caia no ramo "sem historico no git" — matava a mutacao `uniao vira any` no
    Windows (37/37) e NAO matava no ubuntu (36/37), mesmo sha, medido pela CI em 23/09/2026.
    A v2 usava caminhos reais com carimbo, e no sandbox da suite de mutacao o hash voltava None:
    os testes faziam `return` em silencio e a mutacao sobrevivia nas DUAS plataformas — troquei
    "mede em uma" por "nao mede em nenhuma". Fixture que consulta o ambiente mede o ambiente;
    para provar logica pura (`all` contra `any`), a fixture tem de ser pura.

    DEPENDENCIA INCIDENTAL, declarada porque o qa-critic a mediu e ela nao era obvia: se a
    excecao do auto-artefato quebrar, estes testes vao a VERMELHO — mas por acidente, nao por
    desenho. Sem a excecao, `_recente_o_bastante` cai no ramo `_blob_indexado`, e o caminho
    sintetico `_meta/qa/<slug>.json` nao existe em disco nem no indice: `git rev-parse :<path>`
    sai com codigo 128, `_git()` devolve None e a regra fecha. O fail-closed depende, portanto,
    de o arquivo sintetico NAO existir de fato. Se um dia houver um `_meta/qa/` com esse nome, a
    protecao muda de comportamento sem ninguem notar. Medido pelo qa-critic em 23/09/2026,
    forcando `_artefato_do_proprio_veredito` para False: 2 dos 5 testes de uniao foram a
    vermelho, os outros 3 nao dependem da excecao.
    """
    ev = _ev(escopo=("_meta/qa/" + slug + ".json",), **kw)
    ev["_arquivo"] = slug + ".json"
    ev["sha_revisado"] = sg._git("rev-parse", "HEAD")
    ev["blobs_revisados"] = {"_meta/qa/" + slug + ".json": "0" * 40}
    return ev


_A1 = "_meta/qa/veredito-uniao-a.json"
_A2 = "_meta/qa/veredito-uniao-b.json"


def test_uniao_dois_vereditos_parciais_cobrem_o_conjunto():
    """A e B revisaram metades diferentes: juntos cobrem, e isso agora vale."""
    a = _ev_artefato("veredito-uniao-a", agentId="a1", modelo="sonnet", autor="opus")
    b = _ev_artefato("veredito-uniao-b", agentId="a2", modelo="sonnet", autor="opus")
    assert sg._qa_critic_attested([a, b], [_A1, _A2]) is True


def test_uniao_NAO_cobre_caminho_que_ninguem_revisou():
    """A porta que a uniao nao pode abrir — e e' ESTE que mata a mutacao `uniao vira any`.

    Com `all`, o caminho descoberto derruba o conjunto; com `any`, o coberto liberaria tudo.
    A primeira assercao existe porque foi exatamente ela que faltou nas duas versoes anteriores:
    se o caminho coberto NAO passar sozinho, `all` e `any` coincidem em False, a mutacao fica
    indistinguivel e o teste fica verde sem medir nada.
    """
    a = _ev_artefato("veredito-uniao-a", agentId="a1", modelo="sonnet", autor="opus")
    assert sg._um_veredito_cobre([a], [_A1]) is True, (
        "montagem invalida: o caminho coberto TEM de passar sozinho, senao este teste nao "
        "distingue uniao de any")
    assert sg._qa_critic_attested([a], [_A1, _A2]) is False


def test_uniao_NAO_aceita_veredito_sem_atestacao():
    """Cada caminho segue exigindo atestacao valida — a uniao nao relaxa o item."""
    a = _ev_artefato("veredito-uniao-a", agentId="a1", modelo="sonnet", autor="opus")
    b = _ev_artefato("veredito-uniao-b", agentId="a2", modelo="sonnet", autor="opus")
    b.pop("atestacao", None)
    assert sg._qa_critic_attested([a, b], [_A1, _A2]) is False


def test_uniao_NAO_aceita_veredito_sem_escopo():
    """Evidencia sem `escopo_paths` nao vira carta-branca por estar acompanhada."""
    a = _ev_artefato("veredito-uniao-a", agentId="a1", modelo="sonnet", autor="opus")
    b = _ev_artefato("veredito-uniao-b", agentId="a2", modelo="sonnet", autor="opus")
    b["escopo_paths"] = []
    assert sg._qa_critic_attested([a, b], [_A1, _A2]) is False


def test_uniao_NAO_atravessa_reprovacao_vigente():
    """Reprovacao vigente num caminho derruba aquele caminho, e com ele o conjunto."""
    a = _ev_artefato("veredito-uniao-a", agentId="a1", modelo="sonnet", autor="opus")
    b = _ev_artefato("veredito-uniao-b", agentId="a2", modelo="sonnet", autor="opus")
    rep = _ev_artefato("veredito-uniao-b", agentId="a3", modelo="sonnet", autor="opus")
    rep["recomendacao"] = "reprovar"
    rep["passou"] = False
    rep["problemas"] = [{"severidade": "CRITICO", "estado": "aberto",
                         "local": _A2, "descricao": "defeito real"}]
    assert sg._qa_critic_attested([a, b, rep], [_A1, _A2]) is False


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(_rodar_sem_pytest())
