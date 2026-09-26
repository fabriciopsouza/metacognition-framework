#!/usr/bin/env python3
"""Canário do arquivo único de especificação (ADR-117) — a condição do dono, executável.

O dono decidiu (25/09/2026): um arquivo só **se nenhum mecanismo quebrar e nenhuma informação se
perder**; se houver perda, 3 arquivos + espelho. Este canário é essa condição virando prova:

  (a) MESMO VEREDITO — cada especificação real (formato antigo) é convertida para o arquivo único, e
      os 4 gates (profundidade, mapeamento de campo, completude, contexto) têm de devolver exatamente
      o mesmo resultado nos dois formatos, achado por achado;
  (b) CASOS QUE REPROVAM — os mesmos gates, em casos sintéticos feitos para reprovar em cada um, têm
      de reprovar igual nos dois formatos (as reais quase só passam no mapeamento de campo, e um gate
      que só vê casos verdes não prova nada);
  (c) PERDA ZERO — toda linha de cada arquivo de origem aparece no arquivo único, na mesma ordem;
  (d) PARTES ISOLADAS — texto de uma parte não conta para outra; `#` dentro de bloco de código não
      encerra parte; parte ausente reprova em vez de passar;
  (e) RECUSA — o conversor recusa a forma que não comporta sem perda.

Uso: python tools/test_spec_unico.py   (exit 0 PASS; 1 FAIL)
"""
import os
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import spec_fonte  # noqa: E402
import spec_unificar  # noqa: E402
import check_spec_depth as csd  # noqa: E402
import check_field_mapping as cfm  # noqa: E402
import check_completeness as cc  # noqa: E402
import check_context_brief as ccb  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

DIMS = csd.load_bank()
SINAIS = ccb.load_signals()


def _ler(p):
    with open(p, encoding="utf-8-sig") as fh:
        return fh.read()


def veredito_antigo(pasta):
    req, val = os.path.join(pasta, "requirements.md"), os.path.join(pasta, "validation.md")
    v = {"profundidade": csd.check_spec(req, DIMS), "mapeamento": cfm.check_spec(req),
         "contexto": ccb.check_spec(req, SINAIS)}
    try:
        v["completude"] = cc.check(_ler(req), _ler(val))
    except OSError:
        v["completude"] = "sem-arquivo"
    missao = os.path.join(pasta, "mission.md")
    if os.path.isfile(missao):
        v["contexto-missao"] = ccb.check_spec(missao, SINAIS)
    return v


def veredito_unico(spec):
    v = {"profundidade": csd.check_spec(spec, DIMS), "mapeamento": cfm.check_spec(spec),
         "contexto": ccb.check_spec(spec, SINAIS, "requisitos")}
    rq, vl = spec_fonte.ler_parte(spec, "requisitos"), spec_fonte.ler_parte(spec, "aceite")
    v["completude"] = "sem-arquivo" if rq is None or vl is None else cc.check(rq, vl)
    if spec_fonte.ler_parte(spec, "missao") is not None:
        v["contexto-missao"] = ccb.check_spec(spec, SINAIS, "missao")
    return v


def converter_para(pasta, destino_dir):
    os.makedirs(destino_dir, exist_ok=True)
    spec = os.path.join(destino_dir, spec_fonte.ARQUIVO_UNICO)
    with open(spec, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(spec_unificar.unificar(pasta))
    return spec


def _sem_vazias_no_fim(linhas):
    while linhas and not linhas[-1].strip():
        linhas = linhas[:-1]
    return linhas


def perda_de_linhas(pasta, spec):
    """Diferenças entre cada arquivo de origem e a SUA parte no arquivo único (lista vazia = perda zero).

    Igualdade EXATA, parte por parte: a parte tem de ser a linha de origem `<!-- origem -->` seguida
    do arquivo inteiro, com só o título de nível 1 trocado por comentário. A versão anterior buscava
    cada linha no arquivo único INTEIRO, e uma linha perdida na Parte A casava com a mesma linha na
    Parte D — a revisão de 25/09 reproduziu "perda zero" com conteúdo faltando."""
    texto = _ler(spec)
    diferencas = []
    for parte in spec_fonte.PARTES:
        fonte = spec_unificar._fonte_da_parte(pasta, parte)
        if not fonte:
            continue
        rel = os.path.relpath(fonte, pasta).replace("\\", "/")
        esperado = [f"<!-- origem: {rel} -->"]
        for ln, _fora, titulo in spec_fonte._linhas_classificadas(_ler(fonte)):
            esperado.append(spec_unificar.titulo_como_comentario(ln) if titulo else ln)
        obtido = (spec_fonte.extrair_parte(texto, parte) or "").splitlines()
        esperado, obtido = _sem_vazias_no_fim(esperado), _sem_vazias_no_fim(obtido)
        if esperado != obtido:
            n = next((i for i, (a, b) in enumerate(zip(esperado, obtido)) if a != b),
                     min(len(esperado), len(obtido)))
            diferencas.append(f"{os.path.basename(fonte)} (parte {parte}): difere na linha {n}; "
                              f"esperado {len(esperado)} linhas, obtido {len(obtido)}")
    return diferencas


def escrever(pasta, nome, texto):
    os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(pasta, nome), "w", encoding="utf-8") as fh:
        fh.write(texto)


def main():
    falhas, conferidas = [], 0
    specs = sorted(r for r, _, fs in os.walk(os.path.join(ROOT, "docs", "specs"))
                   if "requirements.md" in fs)
    if len(specs) < 5:
        falhas.append(f"só {len(specs)} especificações reais encontradas — a prova ficaria vazia")

    with tempfile.TemporaryDirectory() as tmp:
        # (a) + (c) especificações reais
        for i, pasta in enumerate(specs):
            nome = os.path.relpath(pasta, ROOT)
            spec = converter_para(pasta, os.path.join(tmp, f"real{i}"))
            a, u = veredito_antigo(pasta), veredito_unico(spec)
            if a != u:
                falhas.append(f"(a) veredito difere em {nome}: antigo={a} unico={u}")
            perdidas = perda_de_linhas(pasta, spec)
            if perdidas:
                falhas.append(f"(c) {nome}: {len(perdidas)} linha(s) perdida(s), ex.: {perdidas[:2]}")
            conferidas += 1

        # (b) casos sintéticos que REPROVAM em cada gate, e um que passa em profundidade
        dims_ok = "\n".join(f"- {d['key']}: decidido pelo dono" for d in DIMS)
        sinal = SINAIS[0] if SINAIS else "regulado"
        casos = {
            "profundidade-reprova": ("# r\n\n## Dimensões de elicitação\n- operador: <preencher>\n",
                                     "# v\n| 1 | x | y | ☐ |\n"),
            "profundidade-passa": (f"# r\n\n## Dimensões de elicitação\n{dims_ok}\n",
                                   "# v\n| 1 | x | y | ☐ |\n"),
            "mapeamento-reprova": ("# r\n\n## Mapeamento de campo-fonte\n- total -> coluna VALOR\n",
                                   "# v\n"),
            "completude-reprova": ("# r\n\nCalcular cada unidade mes a mes e o acumulado.\n",
                                   "# v\n| 1 | soma bate | somar | ☐ |\n"),
            "contexto-reprova": (f"# r\n\nProjeto {sinal} com decisao de alto impacto.\n", "# v\n"),
        }
        reprovados = {"profundidade": 0, "mapeamento": 0, "completude": 0, "contexto": 0}
        for nome, (req, val) in casos.items():
            pasta = os.path.join(tmp, "antigo-" + nome)
            escrever(pasta, "requirements.md", req)
            escrever(pasta, "validation.md", val)
            spec = converter_para(pasta, os.path.join(tmp, "unico-" + nome))
            a, u = veredito_antigo(pasta), veredito_unico(spec)
            if a != u:
                falhas.append(f"(b) caso {nome}: antigo={a} unico={u}")
            gate = nome.split("-")[0]
            ok = a[gate][0] if isinstance(a[gate], tuple) and gate != "completude" else None
            if gate == "completude":
                ok = not (a[gate][1] or a[gate][2]) if isinstance(a[gate], tuple) else None
            if nome.endswith("reprova"):
                if ok is not False:
                    falhas.append(f"(b) o caso {nome} deveria REPROVAR no formato antigo e nao reprovou: {a[gate]}")
                else:
                    reprovados[gate] += 1
            elif ok is not True:
                falhas.append(f"(b) o caso {nome} deveria PASSAR e nao passou: {a[gate]}")
        if min(reprovados.values()) < 1:
            falhas.append(f"(b) algum gate ficou sem caso reprovado: {reprovados}")

        # (d) partes isoladas, cerca de código, parte ausente
        m = spec_fonte.MARCA
        isolado = os.path.join(tmp, "isolado", "spec.md")
        escrever(os.path.dirname(isolado), "spec.md",
                 f"{m}\n# t\n# Parte A — Requisitos\nsem dimensoes aqui\n"
                 f"# Parte B — Aceite\n## Dimensões de elicitação\n{dims_ok}\n")
        if csd.check_spec(isolado, DIMS)[0] is not False:
            falhas.append("(d) dimensões escritas na parte Aceite contaram para Requisitos")
        cerca = os.path.join(tmp, "cerca", "spec.md")
        escrever(os.path.dirname(cerca), "spec.md",
                 f"{m}\n# Parte A — Requisitos\n```bash\n# um comentario de shell\n```\n"
                 f"## Dimensões de elicitação\n{dims_ok}\n# Parte B — Aceite\n| 1 | x | y | ☐ |\n")
        if csd.check_spec(cerca, DIMS)[0] is not True:
            falhas.append("(d) `#` dentro de bloco de código encerrou a parte Requisitos")
        sem_a = os.path.join(tmp, "sem-a", "spec.md")
        escrever(os.path.dirname(sem_a), "spec.md", f"{m}\n# Parte B — Aceite\n| 1 | x | y | ☐ |\n")
        if csd.check_spec(sem_a, DIMS)[0] is not False or cfm.check_spec(sem_a)[0] is not False:
            falhas.append("(d) arquivo único SEM a parte Requisitos passou num gate (tinha de reprovar)")

        # (d2) forma que faria uma parte engolir outra é RECUSADA, não aceita em silêncio (QA 25/09)
        aberta = os.path.join(tmp, "cerca-aberta", "spec.md")
        escrever(os.path.dirname(aberta), "spec.md",
                 f"{m}\n# Parte A — Requisitos\n```\ncodigo sem fechar\n# Parte B — Aceite\n| 1 | x |\n")
        r = csd.check_spec(aberta, DIMS)
        if r[0] is not False or "aberto" not in " ".join(r[1]):
            falhas.append(f"(d2) cerca de código aberta não foi recusada: {r}")
        recuo = os.path.join(tmp, "recuo", "spec.md")
        escrever(os.path.dirname(recuo), "spec.md",
                 f"{m}\n# Parte A — Requisitos\nreq\n  # Parte B — Aceite\n| 1 | x |\n")
        if spec_fonte.ler_parte(recuo, "aceite") is None or "Parte B" in spec_fonte.ler_parte(recuo, "requisitos"):
            falhas.append("(d2) título de parte com recuo de 2 espaços não foi reconhecido como parte")
        dupla = os.path.join(tmp, "dupla", "spec.md")
        escrever(os.path.dirname(dupla), "spec.md",
                 f"{m}\n# Parte A — Requisitos\num\n# Parte A — Requisitos\ndois\n")
        if csd.check_spec(dupla, DIMS)[0] is not False or cfm.check_spec(dupla)[0] is not False:
            falhas.append("(d2) 'Parte A' repetida foi aceita (a segunda seria descartada em silêncio)")

        # (c2) a própria prova de perda pega linha perdida mesmo que ela exista em OUTRA parte
        dup = os.path.join(tmp, "linha-duplicada")
        escrever(dup, "requirements.md", "# r\n- LINHA CRITICA confirmada\n")
        escrever(dup, "mission.md", "# m\n- LINHA CRITICA confirmada\n")
        spec_dup = converter_para(dup, os.path.join(tmp, "linha-duplicada-unico"))
        texto_dup = _ler(spec_dup)
        corte = texto_dup.find("- LINHA CRITICA confirmada")  # a 1ª ocorrência é a da Parte A
        if corte < 0:  # sem esconder: se o conversor não trouxe a linha, isso é o achado
            falhas.append("(c2) o conversor não trouxe '- LINHA CRITICA confirmada' para o arquivo único")
        else:
            escrever(os.path.dirname(spec_dup), "spec.md",
                     texto_dup[:corte] + texto_dup[corte + len("- LINHA CRITICA confirmada\n"):])
            if not perda_de_linhas(dup, spec_dup):
                falhas.append("(c2) linha perdida na Parte A não foi pega porque existe igual na Parte D")

        # (g) coexistência: pasta com o arquivo único E os antigos conta UMA vez na varredura
        raiz_g = os.path.join(tmp, "raiz-g")
        pasta_g = os.path.join(raiz_g, "docs", "specs", "feature-x")
        escrever(pasta_g, "requirements.md", "# r\nalgo\n")
        escrever(pasta_g, "validation.md", "# v\n| 1 | x | y | ☐ |\n")
        converter_para(pasta_g, pasta_g)
        if not spec_fonte.sombreado_por_unico(os.path.join(pasta_g, "requirements.md")):
            falhas.append("(g) requirements.md numa pasta com spec.md único não foi marcado como sombreado")
        raiz_orig = cc.ROOT
        try:
            cc.ROOT = raiz_g
            pares = cc._resolve([])
        finally:
            cc.ROOT = raiz_orig
        if len(pares) != 1 or not pares[0][0].endswith(spec_fonte.ARQUIVO_UNICO):
            falhas.append(f"(g) varredura de completude contou a mesma feature {len(pares)} vez(es): {pares}")

        # (h) Parte C incompleta com context-brief.md válido ao lado: reprova e DIZ que o do lado é ignorado
        pasta_h = os.path.join(tmp, "contexto-h")
        escrever(pasta_h, "context-brief.md",
                 "# b\n| ancora | vigencia | pertinencia |\nfonte 2025 http://x\nCONFIRMADO\n")
        escrever(pasta_h, "spec.md",
                 f"{m}\n# Parte A — Requisitos\nProjeto {sinal} com decisao.\n"
                 f"# Parte C — Contexto e âncoras\n(preencher depois)\n")
        rh = ccb.check_spec(os.path.join(pasta_h, "spec.md"), SINAIS, "requisitos")
        if rh[0] is not False or "ignorado" not in rh[1]:
            falhas.append(f"(h) Parte C incompleta com brief ao lado: esperado reprovar avisando, veio {rh}")

        # (i) mapeamento de campo com confirmação PENDENTE reprova (PASS falso achado em 25/09, ADR-118)
        for estado in ("pendente (D6)", "a confirmar", "aguardando o dono", "não", "?"):
            linha = f"- total -> coluna VALOR | confirmação: {estado} | porque: coluna do modelo\n"
            pasta_i = os.path.join(tmp, "mapa-" + str(abs(hash(estado))))
            escrever(pasta_i, "spec.md", f"{m}\n# Parte A — Requisitos\n## Mapeamento de campo-fonte\n{linha}")
            if cfm.check_spec(os.path.join(pasta_i, "spec.md"))[0] is not False:
                falhas.append(f"(i) mapeamento com 'confirmação: {estado}' passou como confirmado")
        ok_i = os.path.join(tmp, "mapa-ok")
        escrever(ok_i, "spec.md", f"{m}\n# Parte A — Requisitos\n## Mapeamento de campo-fonte\n"
                                  f"- total -> coluna VALOR | confirmação: [CONFIRMADO] pelo dono em 25/09 | porque: x\n")
        if cfm.check_spec(os.path.join(ok_i, "spec.md"))[0] is not True:
            falhas.append("(i) mapeamento confirmado de verdade foi recusado (falso negativo)")

        # (f) a junção J3 não aceita um spec.md único SEM a parte Aceite como evidência (ele passaria
        # só por existir). Só o caso de recusa: ele falha antes de gravar, então não suja o ledger real.
        import qa_evidence  # noqa: E402
        so_req = os.path.join(tmp, "so-requisitos", "spec.md")
        escrever(os.path.dirname(so_req), "spec.md", f"{m}\n# Parte A — Requisitos\nalgo\n")
        try:
            qa_evidence.append_junction("teste-spec-unico-sem-aceite", "J3", "x", "evidencia",
                                        validation=so_req)
            falhas.append("(f) a J3 aceitou um spec.md único sem a Parte B — Aceite")
        except ValueError as e:
            if "Parte B" not in str(e):
                falhas.append(f"(f) a J3 recusou pelo motivo errado: {e}")
        # (f2) spec.md MALFORMADO na J3: recusa limpa (ValueError com o motivo), não traceback
        try:
            qa_evidence.append_junction("teste-spec-unico-malformado", "J3", "x", "evidencia",
                                        validation=aberta)
            falhas.append("(f2) a J3 aceitou um spec.md único com bloco de código aberto")
        except ValueError as e:
            if "invalido" not in str(e):
                falhas.append(f"(f2) a J3 recusou pelo motivo errado: {e}")
        except Exception as e:  # o defeito da rodada 2: SpecInvalida escapava como erro não tratado
            falhas.append(f"(f2) a J3 estourou {type(e).__name__} em vez de recusar limpo: {e}")

        # (e) o conversor recusa dois títulos de nível 1 fora de código
        dois = os.path.join(tmp, "dois-h1")
        escrever(dois, "requirements.md", "# um\ntexto\n# dois\n")
        try:
            spec_unificar.unificar(dois)
            falhas.append("(e) o conversor aceitou dois títulos de nível 1 (perderia a separação)")
        except spec_unificar.ConversaoRecusada:
            pass

    print(f"{conferidas} especificações reais conferidas (mesmo veredito + perda zero); "
          f"casos sintéticos por gate que reprovam: {reprovados}")
    for f in falhas:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (arquivo único: mesmo veredito dos gates e nenhuma linha perdida)"
          if not falhas else f"FAIL ({len(falhas)})")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
