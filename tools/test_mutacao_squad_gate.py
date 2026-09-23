# -*- coding: utf-8 -*-
"""Prova por MUTACAO do fail-closed no veredito (ADR-115).

Existe porque a 2a rodada da revisao adversarial apontou, com razao: as "mutacoes mortas" eram
PROSA — nao havia artefato no repositorio que permitisse refazer a prova. Alegacao de sabotagem
que so vive no relatorio e' a classe que o ADR-106 proibe.

A 3a rodada REPROVOU a primeira versao DESTE arquivo, e o achado era grave: ele mutava
`tools/squad_gate.py` NO REPOSITORIO e so restaurava no `finally`. Morto de fora (timeout de CI,
taskkill, disco cheio), o `finally` nao roda e o gate fica SABOTADO em disco — em estado
fail-OPEN, sem aviso. O critico reproduziu ao vivo: matou `run_canaries.py` por timeout e o
arquivo ficou com a mutacao "severidade desconhecida vira LEVE" aplicada. O mecanismo que prova
que o gate e' fail-closed podia deixar o gate fail-open.

Agora nada e' escrito dentro do repositorio: tudo acontece numa arvore temporaria, como
`tools/test_mutacao_controle.py` ja fazia — o padrao que a versao anterior alegava seguir e nao
seguia.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (nome, trecho_original, trecho_sabotado)
MUTACOES = [
    # --- mecanismos das rodadas 36 a 38: conteudo antes do commit, e uniao por caminho ---
    ("uniao vira `any` (um caminho revisado liberaria todos)",
     "    return all(_um_veredito_cobre(artifacts, [p]) for p in alvo)",
     "    return any(_um_veredito_cobre(artifacts, [p]) for p in alvo)"),
    ("desliga a checagem de conteudo (volta a recencia cega no pre-commit)",
     '    blobs = v.get("blobs_revisados")',
     "    blobs = None"),
    ("excecao do auto-carimbo passa a valer para QUALQUER caminho",
     "            if _artefato_do_proprio_veredito(v, p):",
     "            if True:"),
    ("desliga a checagem no _atestacao_valida",
     "    if achados_bloqueantes_abertos(v):\n        return False\n",
     "    pass\n"),
    ("severidade desconhecida vira LEVE (fail-OPEN)",
     'return _norm(problema.get("severidade")) not in SEVERIDADE_LEVE',
     'return _norm(problema.get("severidade")) in {"ALTA"}'),
    ("'aceito' basta sem assinatura de quem assumiu",
     'if estado == "aceito" and assinatura_valida(p.get("aceito_por")):',
     'if estado == "aceito":'),
    ("legado volta a ser AUTODECLARADO por schema (bypass da 1a rodada)",
     '    nome = os.path.basename(str(v.get("_arquivo") or ""))',
     '    return not any("estado" in p for p in (v.get("problemas") or []))\n'
     '    nome = os.path.basename(str(v.get("_arquivo") or ""))'),
    ("legado volta a valer so por NOME, ignorando o hash (bypass da 2a rodada)",
     'return bool(esperado) and str(v.get("_sha256") or "") == esperado',
     'return bool(esperado)'),
    ("schema malformado volta a ISENTAR em vez de bloquear",
     '    if not isinstance(ps, list):\n'
     '        return None, "campo `problemas` nao e\' lista (e\' %s)" % type(ps).__name__\n',
     '    if not isinstance(ps, list):\n        return [], ""\n'),
    ("main() para de imprimir a divida legada",
     "    _leg = legados_declarados()",
     "    _leg = []"),
    ("estado ausente passa a encerrar o achado",
     "        if estado in ESTADO_RESOLVIDO:\n            continue\n",
     "        if estado in ESTADO_RESOLVIDO or not estado:\n            continue\n"),
    ('o print da divida legada e desligado pela CONDICAO (ponto cego da 20a rodada)',
     '    if _leg:\n',
     '    if False:\n'),
    ('a divida legada volta a ser impressa SO no caminho de sucesso (regressao da 20a rodada)',
     '    _leg = legados_declarados()\n',
     '    _leg = [] if faltam else legados_declarados()\n'),
    ('chave JSON duplicada volta a ser aceita em silencio (bypass da 24a rodada)',
     '        if chave in visto:\n            raise ChaveDuplicada(chave)\n',
     '        pass\n'),
    ('evidencia ilegivel volta a SUMIR em vez de travar o gate (bypass da 25a rodada)',
     '                        out.append({"_recusado": f, "_motivo": "chave duplicada: %s" % e})\n',
     '                        pass\n'),
    ('JSON truncado/ilegivel volta a sumir em silencio (bypass da 26a rodada)',
     '                    out.append({"_recusado": f, "_motivo": "%s: %s" % (type(e).__name__, e)})\n',
     '                    pass\n'),
    ("`_listado_explicitamente` volta a comparar caixa crua (achado da 19a rodada)",
     '    p = path.replace("\\\\", "/").strip().casefold()\n    return any(str(e).replace("\\\\", "/").strip().casefold() == p\n               for e in (v.get("escopo_paths") or []))\n',
     '    p = path.replace("\\\\", "/").strip()\n    return any(str(e).replace("\\\\", "/").strip() == p\n               for e in (v.get("escopo_paths") or []))\n'),
    ("`_cobre` volta a comparar caixa crua (bypass da 18a rodada)",
     "    for e in escopo:\n        e = str(e).replace",
     "    p = p.upper()\n    for e in escopo:\n        e = str(e).replace"),
    ("classify volta a nao normalizar `./` (achado BAIXA da 16a rodada)",
     '            pb = p[2:] if p.startswith("./") else p',
     "            pb = p"),
    ("classify volta a ser case-sensitive (bypass 1 da 15a rodada)",
     "            pb = pb.casefold()",
     "            pb = pb"),
    ("separador volta a virar espaco em vez de sumir (bypass 2 da 15a rodada)",
     '    for sep in ("-", "_", ".", "/", " "):\n        s = s.replace(sep, "")',
     '    for sep in ("-", "_", ".", "/"):\n        s = s.replace(sep, " ")'),
    ("`modelo != autor` volta a ser comparacao crua (bypass 2 da 14a rodada)",
     "    return bool(agent and modelo and autor and _norm_modelo(modelo) != _norm_modelo(autor))",
     "    return bool(agent and modelo and autor and modelo != autor)"),
    ("falha do git volta a ser lida como `nada staged` (bypass 1 da 14a rodada)",
     "        if r.returncode != 0:",
     "        if False:"),
    ("campo `autor` volta a ser opcional na atestacao (bypass da 13a rodada)",
     "    return bool(agent and modelo and autor and _norm_modelo(modelo) != _norm_modelo(autor))",
     "    return bool(agent and modelo and (not autor or _norm_modelo(modelo) != _norm_modelo(autor)))"),
    ("reprovacao sem achado estruturado volta a contar como tratada (bypass da 11a rodada)",
     "    if not isinstance(p, list) or not p:\n        return False",
     "    if False:\n        return False"),
    ("sha_revisado volta a aceitar referencia simbolica (bypass da 10a rodada)",
     "    return 7 <= len(s) <= 40 and all(c in \"0123456789abcdefABCDEF\" for c in s)",
     "    return bool(s)"),
    ("reprovacao JA TRATADA volta a travar o bloco (autoachado pos-9a rodada)",
     "        if _reprovacao_tratada(r):\n            continue                       # reprovacao ja tratada nao trava (ver docstring)\n",
     "        pass\n"),
    ("reprovacao SEM escopo volta a nao contar (bypass 1 da 9a rodada)",
     "        if not escopo_r or any(_cobre(escopo_r, p) for p in alvo):",
     "        if escopo_r and any(_cobre(escopo_r, p) for p in alvo):"),
    ("sha volta a ser comparado como string crua (bypass 2 da 9a rodada)",
     '    pleno = _git("rev-parse", "--verify", "--quiet", s + "^{commit}")\n    return pleno or s',
     "    return s"),
    ("juncao de RELEASE volta a ignorar reprovacao do mesmo release (bypass 3 da 9a rodada)",
     "        if _reprovacao_de_release_vigente(artifacts, v, padrao):\n            continue",
     "        pass"),
    ("reprovacao vigente deixa de invalidar o aprovativo (bypass da 8a rodada)",
     "        if _reprovacao_vigente(artifacts, v, alvo):\n            continue\n",
     "        pass\n"),
    ("assinatura volta a aceitar placeholder ('nao assinado')",
     "    return norm not in NAO_SAO_ASSINATURA and len(norm) >= 2",
     "    return True"),
    ("allowlist DENTRO do achado desligada (bypass do aninhamento, 7a rodada)",
     "    return sorted(k for k in p.keys() if k not in CAMPOS_DO_ACHADO)",
     "    return []"),
    ("assinatura volta a aceitar qualquer categoria L (U+3164 HANGUL FILLER)",
     'if not any(unicodedata.name(c, "").startswith("LATIN") for c in s):',
     'if not any(unicodedata.category(c).startswith("L") for c in s):'),
    ("atestacao malformada volta a derrubar o processo",
     "    if not isinstance(at, dict):\n        return False",
     "    if False:\n        return False"),
    ("allowlist de campos desligada (bypass da chave cirilica, 6a rodada)",
     "    estranhos = campos_desconhecidos(v)",
     "    estranhos = []"),
    ("chave `problemas` deixa de ser OBRIGATORIA (bypass do homoglifo, 5a rodada)",
     '    if "problemas" not in v:',
     '    if False:'),
]


def _monta_arvore(tmp):
    """Copia o MINIMO para a arvore temporaria: tools/ do gate + o ledger que ele le.

    `squad_gate` deriva ROOT de __file__, entao a copia precisa da mesma forma de diretorio
    (tmp/tools/...), senao ele procuraria o ledger na raiz errada.
    """
    os.makedirs(os.path.join(tmp, "tools"), exist_ok=True)
    for nome in ("squad_gate.py", "test_squad_gate.py"):
        shutil.copyfile(os.path.join(RAIZ, "tools", nome), os.path.join(tmp, "tools", nome))
    origem_qa = os.path.join(RAIZ, "_meta", "qa")
    if os.path.isdir(origem_qa):
        shutil.copytree(origem_qa, os.path.join(tmp, "_meta", "qa"),
                        ignore=shutil.ignore_patterns("junctions"))
    origem_b = os.path.join(RAIZ, "behaviors")
    if os.path.isdir(origem_b):
        shutil.copytree(origem_b, os.path.join(tmp, "behaviors"))
    # A copia ganha um git PROPRIO. Sem ele, 4 testes de evidencia/escopo/recencia falhavam por
    # AMBIENTE, e a regua tinha de ser afrouxada para "a mutacao acrescenta falhas" — regua fraca
    # e' ponto cego: uma mutacao que quebrasse so um teste JA quebrado passaria por sobrevivente.
    # Com git na copia o baseline volta a ser ZERO falhas, e qualquer falha e' sabotagem.
    G = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q"], cwd=tmp, capture_output=True)
    subprocess.run(G + ["add", "-A"], cwd=tmp, capture_output=True)
    subprocess.run(G + ["commit", "-q", "-m", "base"], cwd=tmp, capture_output=True)
    # DOIS commits: ha testes que comparam um sha VELHO contra um arquivo tocado DEPOIS dele
    # ("revisado uma vez, liberado sempre"). Com um commit so, nao existe 'velho' e eles falham
    # por ausencia de historico, nao por defeito.
    io.open(os.path.join(tmp, "tools", "_marco.txt"), "w", encoding="utf-8").write("marco")
    subprocess.run(G + ["add", "-A"], cwd=tmp, capture_output=True)
    subprocess.run(G + ["commit", "-q", "-m", "marco"], cwd=tmp, capture_output=True)
    return os.path.join(tmp, "tools", "squad_gate.py"), os.path.join(tmp, "tools", "test_squad_gate.py")


# Os testes que provam o fail-closed. A prova so vale se ELES estiverem vivos no baseline: se um
# deles ja falhasse por ambiente, a mutacao correspondente nao teria como ser detectada e a
# "sabotagem morta" seria ilusao. Esta lista e' conferida contra o canario a cada execucao.
TESTES_DO_BLOCO = (
    # --- rodadas 36 a 38: conteudo antes do commit, excecao do auto-carimbo, uniao ---
    "test_blobs_conteudo_IGUAL_ao_revisado_cobre",
    "test_blobs_conteudo_DIFERENTE_do_revisado_NAO_cobre",
    "test_blobs_path_avaliado_SEM_carimbo_NAO_cobre",
    "test_blobs_NAO_dispensam_sha_revisado_valido",
    "test_veredito_cobre_o_PROPRIO_artefato_sem_carimbo",
    "test_veredito_NAO_cobre_artefato_de_OUTRO_veredito",
    "test_excecao_do_artefato_NAO_alcanca_codigo",
    "test_veredito_SEM_arquivo_nao_tem_excecao",
    "test_uniao_dois_vereditos_parciais_cobrem_o_conjunto",
    "test_uniao_NAO_cobre_caminho_que_ninguem_revisou",
    "test_uniao_NAO_aceita_veredito_sem_atestacao",
    "test_uniao_NAO_aceita_veredito_sem_escopo",
    "test_uniao_NAO_atravessa_reprovacao_vigente",
    "test_aprovativo_com_ALTA_aberto_NAO_passa",
    "test_aprovativo_com_ALTA_corrigido_passa",
    "test_severidade_reconhecida_em_TODAS_as_grafias_do_ledger",
    "test_grafia_DESCONHECIDA_bloqueia_fail_closed",
    "test_severidade_AUSENTE_bloqueia",
    "test_estado_AUSENTE_bloqueia_em_veredito_do_SCHEMA_NOVO",
    "test_veredito_LEGADO_ENUMERADO_nao_e_cobrado_mas_e_DECLARADO",
    "test_legado_SOBRESCRITO_perde_a_isencao",
    "test_legado_SEM_hash_nao_e_legado",
    "test_hash_dos_legados_BATE_com_o_disco",
    "test_OMITIR_estado_NAO_compra_isencao",
    "test_legado_FORJADO_por_nome_inventado_nao_passa",
    "test_problemas_MALFORMADO_bloqueia_em_vez_de_isentar",
    "test_main_IMPRIME_a_divida_legada",
    "test_severidade_LEVE_em_aberto_nao_bloqueia",
    "test_ALTA_aceita_exige_ASSINATURA_de_quem_assumiu",
    "test_nenhum_veredito_do_ledger_quebra_com_a_regra",
    # defesas da CHAVE do container — ficaram de fora da 1a versao desta lista, e eram
    # justamente as unicas que matam as duas mutacoes de chave (achado da 5a rodada)
    "test_chave_canonica_DECLARADA_vazia_ou_nula_passa",
    "test_LEDGER_REAL_so_usa_a_chave_canonica",
    "test_HOMOGLIFO_na_chave_nao_esconde_o_achado",
    "test_chave_problemas_AUSENTE_bloqueia",
    "test_problemas_VAZIO_declarado_passa",
    # defesas da 6a rodada: allowlist de campos e assinatura visivel
    "test_chave_homoglifa_UNICODE_ao_lado_da_canonica_nao_esconde",
    "test_campo_de_topo_DESCONHECIDO_bloqueia",
    "test_LEDGER_REAL_so_usa_campos_conhecidos",
    "test_assinatura_INVISIVEL_nao_encerra_achado_bloqueante",
    # defesas da 7a rodada: allowlist no achado, assinatura por script, atestacao tipada
    "test_achado_ANINHADO_dentro_de_achado_leve_nao_escapa",
    "test_campo_DESCONHECIDO_dentro_do_achado_bloqueia",
    "test_LEDGER_REAL_so_usa_campos_de_achado_conhecidos",
    "test_assinatura_exige_letra_LATINA_nao_so_categoria_L",
    "test_atestacao_MALFORMADA_bloqueia_sem_derrubar_o_gate",
    # defesas da 8a rodada: reprovacao vigente e assinatura sem placeholder
    "test_REPROVACAO_vigente_invalida_aprovativo_do_mesmo_escopo",
    "test_reprovacao_de_OUTRO_sha_nao_invalida",
    "test_assinatura_recusa_PLACEHOLDER_e_ate_a_frase_que_NEGA",
    # defesas da 9a rodada: escopo ausente cobre tudo, sha normalizado, e o papel irmao
    "test_listado_explicitamente_tambem_normaliza_a_caixa",
    "test_cobre_NAO_se_deixa_enganar_pela_caixa_do_escopo",
    "test_TODA_forma_de_ilegivel_trava_o_gate",
    "test_reprovacao_ILEGIVEL_nao_deixa_o_aprovativo_passar",
    "test_chave_JSON_duplicada_nao_apaga_achado",
    "test_matriz_cobre_os_INTERRUPTORES_do_proprio_mecanismo",
    "test_classify_normaliza_o_prefixo_ponto_barra",
    "test_classify_NAO_se_deixa_enganar_pela_caixa_do_path",
    "test_norm_modelo_funde_separador_AUSENTE_sem_colidir_modelos_reais",
    "test_autoatestacao_disfarcada_por_caixa_espaco_ou_invisivel",
    "test_git_que_FALHA_nao_e_o_mesmo_que_nada_staged",
    "test_atestacao_SEM_campo_autor_nao_prova_isolamento",
    "test_reprovacao_SEM_achado_estruturado_ainda_veta",
    "test_sha_revisado_SIMBOLICO_nao_vale_como_hash",
    "test_reprovacao_JA_TRATADA_nao_trava_o_proprio_bloco",
    "test_reprovacao_SEM_escopo_paths_cobre_tudo",
    "test_reprovacao_com_sha_CURTO_e_detectada",
    "test_juncao_de_RELEASE_nao_fecha_com_reprovacao_aberta_do_mesmo_release",
)


def _nomes_que_falharam(proc):
    """Nomes dos testes que falharam (o canario imprime 'FAIL <nome>')."""
    saida = proc.stdout.decode("utf-8", "replace")
    return {l.split(None, 1)[1].strip()
            for l in saida.splitlines() if l.startswith("FAIL ") and len(l.split(None, 1)) > 1}


def _falhas(proc) -> int:
    """Quantos testes falharam na execucao do canario. -1 se nao der para ler o resultado."""
    import re
    saida = proc.stdout.decode("utf-8", "replace")
    m = re.search(r"RESULTADO:\s*(\d+)\s*PASS\s*/\s*(\d+)\s*FAIL", saida)
    return int(m.group(2)) if m else -1


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    with tempfile.TemporaryDirectory(prefix="mut-squad-gate-") as tmp:
        alvo, canario = _monta_arvore(tmp)
        orig = io.open(alvo, encoding="utf-8").read()
        # cwd = tmp: a copia tem git proprio, entao o `git rev-parse HEAD` do canario resolve
        # para o commit da copia. O import resolve para a COPIA porque o script esta em tmp/tools/.
        # roda SO os testes do bloco: o canario inteiro roda uma vez por mutacao, e a prova
        # so precisa saber se as defesas DESTE ADR mordem. Corta a suite em ~4x (regua §0-b).
        env = dict(os.environ, PYTHONIOENCODING="utf-8",
                   SQUAD_GATE_TESTES=",".join(TESTES_DO_BLOCO))

        base = subprocess.run([sys.executable, canario], cwd=tmp, capture_output=True, env=env)
        n_base = _falhas(base)
        if n_base < 0:
            print("FAIL baseline: o canario nao imprimiu resultado — prova invalida")
            print(base.stdout.decode("utf-8", "replace")[-900:])
            return 1

        # Com o filtro, os testes de evidencia/escopo (que dependem de estado de repositorio que
        # a copia nao reproduz) ficam de fora, e o baseline VOLTA a poder ser ZERO. Baseline sujo
        # seria prova medindo o ambiente, nao a sabotagem.
        if n_base != 0:
            print("FAIL baseline: %d falha(s) nos testes DO BLOCO sem mutacao — a mutacao "
                  "correspondente nao teria como ser detectada" % n_base)
            print(base.stdout.decode("utf-8", "replace")[-900:])
            return 1
        print("baseline: 0 falhas; os %d testes do fail-closed estao VIVOS" % len(TESTES_DO_BLOCO))

        # Alvo desalinhado ja' e' tratado no laco (imprime ALVO SUMIU e conta como nao-morta),
        # mas so' depois de rodar o canario inteiro uma vez por mutacao. Como isso ja' aconteceu
        # TRES vezes neste bloco — refatorei a funcao e esqueci o alvo — a checagem sobe para antes
        # do laco: falha em 1 segundo em vez de em 2 minutos, e a mensagem diz qual realinhar.
        sumidos = [nome for nome, de, _ in MUTACOES if de not in orig]
        if sumidos:
            print("FAIL alvo(s) de mutacao nao existem mais no fonte — realinhe antes de confiar "
                  "nesta prova:")
            for nome in sumidos:
                print("   -", nome)
            return 1

        vivos = []
        for nome, de, para in MUTACOES:
            if de not in orig:
                print("  %-62s ALVO SUMIU" % nome)
                vivos.append(nome)
                continue
            io.open(alvo, "w", encoding="utf-8").write(orig.replace(de, para, 1))
            r = subprocess.run([sys.executable, canario], cwd=tmp, capture_output=True, env=env)
            n_mut = _falhas(r)
            # -1 = o canario nem imprimiu resultado (crashou). Conta como MORREU? Nao: prova por
            # crash nao vale (ADR-106). Exigimos falha CONTADA, que so acontece por assercao.
            morreu = n_mut > n_base
            print("  %-62s %s (%s)"
                  % (nome, "MORREU" if morreu else "SOBREVIVEU",
                     "%d->%d falhas" % (n_base, n_mut) if n_mut >= 0
                     else "canario CRASHOU — nao conta como morte (ADR-106)"))
            if not morreu:
                vivos.append(nome)
            io.open(alvo, "w", encoding="utf-8").write(orig)   # restaura a COPIA

    # Nada foi escrito no repositorio: se este processo morrer aqui, o pior que acontece e' um
    # diretorio temporario orfao — nunca um gate sabotado em disco.
    print("-" * 50)
    print("RESULTADO: %s (%d/%d mutacoes mortas)"
          % ("PASS" if not vivos else "FAIL", len(MUTACOES) - len(vivos), len(MUTACOES)))
    for v in vivos:
        print("  SOBREVIVEU: %s" % v)
    return 1 if vivos else 0


if __name__ == "__main__":
    sys.exit(main())
