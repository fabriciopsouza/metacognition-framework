#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prova de mutacao do pacote controle_* — exit 0 = PASS, exit 1 = FAIL.

POR QUE ESTE ARQUIVO EXISTE.

A documentacao do pacote afirmava "N defeitos provados por mutacao". A afirmacao era VERDADEIRA —
cada defeito foi mesmo reintroduzido e o canario ficou vermelho — mas a prova morava num script de
rascunho, fora do repositorio. O QA cobrou, e com razao: o numero aparecia ao lado de dois outros
("138 verificacoes", "11 sabotagens") que SAO medidos mecanicamente, dando a impressao de que os
tres vinham da mesma fonte. Nao vinham. Alegacao precisa sem mecanismo e' divida, mesmo quando e'
verdadeira — e a regua deste framework poe determinismo antes de prosa.

Entao a prova virou ferramenta: cada defeito ja corrigido vira uma MUTACAO declarada aqui, o teste
reintroduz o defeito e EXIGE que o canario correspondente reprove. Se algum dia uma correcao for
desfeita e o canario continuar verde, este arquivo acusa.

SEGURANCA: nada e' escrito no repositorio. O pacote inteiro e' COPIADO para uma pasta temporaria, a
mutacao e' aplicada na copia, e o canario roda contra a copia. Um teste que edita o proprio
repositorio para depois restaurar deixa a arvore quebrada se morrer no meio — e este e' um repo com
trabalho nao-commitado com frequencia.

Rodar: python tools/test_mutacao_controle.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                    # pragma: no cover
    pass

TOOLS = Path(__file__).resolve().parent
# `test_controle_projeto.py` LE `test_numeros_controle.py` (checagem estrutural de duplicacao da
# moldura historica), entao ele tem de estar na copia — senao o canario morre por arquivo ausente e
# o vermelho nao significaria mutacao nenhuma. A primeira versao esqueceu, e a guarda "a copia
# intacta passa" pegou na hora: e' para isso que ela existe.
MODULOS = ["controle_base.py", "controle_projeto.py", "controle_sharepoint.py",
           "test_controle_base.py", "test_controle_projeto.py", "test_controle_sharepoint.py",
           "test_numeros_controle.py",
           # e ele MESMO: `test_numeros_controle.py` importa este arquivo para contar quantas
           # mutacoes estao declaradas. Circular, mas so na copia — e sem ele o canario de numeros
           # nasce vermelho la por arquivo ausente.
           "test_mutacao_controle.py"]

# Os documentos que `test_numeros_controle.py` confere. Vao para a copia com o mesmo caminho
# relativo, senao aquele canario nasce vermelho la por arquivo ausente.
DOCUMENTOS = [
    "CHANGELOG.md",
    "_shared/controle-projeto/SKILL.md",
    ".claude/commands/controle-projeto.md",
    ".claude/commands/controle-sharepoint.md",
] + [f"docs/adr/{a.name}" for a in sorted((Path(__file__).resolve().parent.parent
                                           / "docs" / "adr").glob("113-*.md"))]

# Cada entrada: (rotulo, arquivo mutado, canario que tem de reprovar, trecho, substituto).
# O rotulo diz de que rodada de critica o defeito veio — o historico e' a razao de cada linha.
MUTACOES = [
    ("marcador casado por substring", "controle_projeto.py", "test_controle_projeto.py",
     "        if alvo.startswith(mu) and (len(alvo) == len(mu) or not alvo[len(mu)].isalnum()):",
     "        if mu in alvo:"),
    ("identidade de executor por string crua", "controle_projeto.py", "test_controle_projeto.py",
     '            carga[_chave_executor(i["responsavel"])] = \\\n'
     '                carga.get(_chave_executor(i["responsavel"]), 0) + 1\n',
     '            carga[i["responsavel"].strip()] = carga.get(i["responsavel"].strip(), 0) + 1\n'),
    ("prazo comparado como texto no filtro", "controle_projeto.py", "test_controle_projeto.py",
     "    return ini <= prazo <= fim",
     '    return sprint["inicio"] <= (item.get("prazo") or "") <= sprint["fim"]'),
    ("prazo comparado como texto na ordem", "controle_projeto.py", "test_controle_projeto.py",
     '                _data(i.get("prazo")) or "9999-12-31",',
     '                i.get("prazo") or "9999",'),
    ("prioridade 0 caindo como falsy", "controle_projeto.py", "test_controle_projeto.py",
     "        pr = _num(i.get(\"prioridade\"))\n        return (999 if pr is None else pr,",
     "        pr = _num(i.get(\"prioridade\"))\n        return (pr or 999,"),
    ("janela de sprint ilegivel calada", "controle_projeto.py", "test_controle_projeto.py",
     '        if cru and _data(cru) is None:\n            ruins.append(f"sprint.{campo}={cru!r}")',
     '        if False:\n            ruins.append(f"sprint.{campo}={cru!r}")'),
    ("forma do sprint nao validada", "controle_projeto.py", "test_controle_projeto.py",
     '    for fonte in (estado.get("sprint"), projeto.get("sprint")):\n'
     '        if isinstance(fonte, dict) and fonte:\n            return fonte\n    return {}',
     '    return estado.get("sprint") or projeto.get("sprint") or {}'),
    ("teto de configuracao lido cru", "controle_base.py", "test_controle_base.py",
     "    n = _num(cru)\n    if n is None:",
     "    n = cru\n    if n is None:"),
    ("exit 0 com dado sujo", "controle_projeto.py", "test_controle_projeto.py",
     "    if janela or ruins or pri_ruins:", "    if False:"),
    ("marcador customizado descartado", "controle_projeto.py", "test_controle_projeto.py",
     "    marcadores, _ruim = lista_de(projeto.get(\"marcadores_de_ausencia\"),",
     "    marcadores, _ruim = ([\"A DEFINIR\", \"PENDENTE\", \"TBD\", \"N/A\", \"-\"], None)\n"
     "    _ignorado = (projeto.get(\"marcadores_de_ausencia\"),"),
    ("nan e inf atravessando a fronteira", "controle_base.py", "test_controle_base.py",
     "    return f if math.isfinite(f) else None", "    return f"),
    ("dia do mes inexistente aceito", "controle_base.py", "test_controle_base.py",
     "    try:\n        dt.date(a, m, d)          # dia do mes de VERDADE: \"2026-02-30\" nao existe\n"
     "    except ValueError:\n        return None",
     "    if not (1 <= m <= 12 and 1 <= d <= 31):\n        return None"),
    ("Unicode nao normalizado (NFC x NFD)", "controle_base.py", "test_controle_base.py",
     '    return unicodedata.normalize("NFKC", " ".join((nome or "").split())).casefold()',
     '    return " ".join((nome or "").split()).casefold()'),
    ("JSON malformado sem guarda", "controle_base.py", "test_controle_base.py",
     "    try:\n        return json.loads(bruto)", "    if True:\n        return json.loads(bruto)"),
    # A guarda de encoding MUDOU DE LUGAR na rodada 9 — foi para `ler_texto`, que hoje serve JSON e
    # CSV — e a entrada "leitura de texto sem guarda (JSON e CSV)" cobre exatamente este defeito.
    # A entrada antiga foi removida, e não silenciada: o canário acusou a âncora órfã na primeira
    # execução depois da mudança, que é o comportamento certo dele.
    ("--iniciar fora da fronteira", "controle_projeto.py", "test_controle_projeto.py",
     '    raiz = _caminho(caminho, "o caminho passado em --iniciar")',
     "    raiz = Path(caminho).resolve()"),
    # [ACHADO ALTA DO QA RODADA 11] a fronteira só olhava a ENTRADA. Estas duas cobrem o lado da
    # escrita e o falso positivo do gate de atribuição — ambos achados na mesma rodada.
    ("escrita sem guarda (o lado que faltava da fronteira)", "controle_base.py",
     "test_controle_base.py",
     "    except OSError as e:\n        raise ProjetoInvalido(\n"
     "            f\"nao consegui gravar {rotulo}",
     "    except KeyboardInterrupt as e:\n        raise ProjetoInvalido(\n"
     "            f\"nao consegui gravar {rotulo}"),
    # A entrada "atribuicao de numero por substring" foi ABSORVIDA: a rodada 12 trocou a fronteira
    # ASCII por `\w` Unicode, e a mutacao "fronteira de palavra so em ASCII" (abaixo) reintroduz o
    # substring puro pelo mesmo caminho. Duas entradas para o mesmo defeito seria ruido — e o
    # canario acusou a ancora orfa assim que a correcao mudou de forma, que e' o esperado dele.
    ("atribuicao de numero por substring", "test_numeros_controle.py", "test_numeros_controle.py",
     '        for m in re.finditer(r"(?<!\\w)" + re.escape(chave) + r"(?!\\w)", antes):\n'
     "            achados.append((m.start(), quem))",
     "        if antes.rfind(chave) >= 0:\n"
     "            achados.append((antes.rfind(chave), quem))"),
    # [ACHADOS ALTA DA RODADA 12] escrita nao-atomica, caminho sem contencao, fronteira ASCII.
    ("escrita nao-atomica (trunca antes de gravar)", "controle_base.py", "test_controle_base.py",
     "        os.replace(tmp, caminho)", "        pass  # os.replace(tmp, caminho)"),
    ("caminho da declaracao sem contencao", "controle_base.py", "test_controle_base.py",
     "    if not dentro:", "    if False:"),
    ("fronteira de palavra so em ASCII", "test_numeros_controle.py", "test_numeros_controle.py",
     '        for m in re.finditer(r"(?<!\\w)" + re.escape(chave) + r"(?!\\w)", antes):',
     '        for m in re.finditer(r"(?<![0-9a-z_])" + re.escape(chave) + r"(?![0-9a-z_])", antes):'),
    ("bool aceito onde se espera int", "controle_base.py", "test_controle_base.py",
     "        elif esperado is not bool and isinstance(c[chave], bool):", "        elif False:"),
    ("guarda assimetrica em config_num", "controle_base.py", "test_controle_base.py",
     "        cru = estado.get(alternativa) if isinstance(estado, dict) else None",
     "        cru = estado.get(alternativa)"),
    ("forma declarada malformada sem guarda", "controle_base.py", "test_controle_base.py",
     '        if not (esperado == "numero" or isinstance(esperado, type)):', "        if False:"),
    # [ACHADO ALTA DO QA RODADA 9] a mutacao antiga so era detectada em Python 3.12: o gatilho
    # (NUL no caminho) levanta ValueError la e NAO levanta nada no 3.14, e esta maquina tem os dois.
    # Prova que muda de resultado conforme o interpretador nao e' prova. TypeError vale em qualquer
    # versao, entao a mutacao passa a ser detectavel em qualquer uma.
    ("caminho invalido sem guarda", "controle_base.py", "test_controle_base.py",
     "        return Path(cru).resolve()\n    except (ValueError, OSError, TypeError) as e:",
     "        return Path(cru).resolve()\n    except (KeyboardInterrupt,) as e:"),
    ("leitura de texto sem guarda (JSON e CSV)", "controle_base.py", "test_controle_base.py",
     '        return caminho.read_text(encoding="utf-8-sig")\n    except UnicodeDecodeError as e:',
     '        return caminho.read_text(encoding="utf-8-sig")\n    except KeyboardInterrupt as e:'),
    ("frozenset recusado", "controle_base.py", "test_controle_base.py",
     "    if isinstance(valor, (list, tuple, set, frozenset)):",
     "    if isinstance(valor, (list, tuple, set)):"),
    ("resolucao por variavel de ambiente quebrada", "controle_base.py", "test_controle_base.py",
     '        return p, f"variavel de ambiente {ENV_PROJETO}"', '        return p, "indicado no comando"'),
    ("fallback de titulo na cadeia do mapa", "controle_sharepoint.py", "test_controle_sharepoint.py",
     '    for origem in str(mapa.get(campo, campo)).split("|"):',
     '    for origem in [str(mapa.get(campo, campo)).split("|")[0]]:'),
    ("corte zero caindo como falsy", "controle_sharepoint.py", "test_controle_sharepoint.py",
     "            return v if limite is None else v[:limite]",
     "            return v[:limite] if limite else v"),
    ("fronteira do --receber (prioridade)", "controle_sharepoint.py", "test_controle_sharepoint.py",
     "                n = CP._num(valor)\n                if n is None:",
     "                n = int(valor) if valor.isdigit() else None\n                if n is None and False:"),
    ("situacao nao mapeada sumindo", "controle_sharepoint.py", "test_controle_sharepoint.py",
     "                if nova is None:", "                if False:"),
    ("declaracao da List sem checagem de tipo", "controle_sharepoint.py",
     "test_controle_sharepoint.py",
     '    return CB.exigir_forma(c, FORMA, "sharepoint.list")', "    return c"),
    ("detalhe.json lido cru", "controle_sharepoint.py", "test_controle_sharepoint.py",
     "    d = CB._ler_json(arq)", '    d = json.loads(arq.read_text(encoding="utf-8"))'),
    ("pessoas.json lido cru", "controle_sharepoint.py", "test_controle_sharepoint.py",
     "    d = CB._ler_json(arq_pes)",
     '    d = json.loads(arq_pes.read_text(encoding="utf-8"))'),
]

falhou = []


def checar(nome, condicao, detalhe=""):
    if condicao:
        print(f"  ok   {nome}")
    else:
        print(f"  FAIL {nome} {detalhe}")
        falhou.append(nome)


def main() -> int:
    print(f"Reintroduzindo {len(MUTACOES)} defeito(s) ja corrigido(s), um por vez.")
    print("Cada um roda numa COPIA do pacote: o repositorio nao e' tocado.\n")

    with tempfile.TemporaryDirectory() as tmp:
        raiz_copia = Path(tmp)
        copia = raiz_copia / "tools"
        copia.mkdir()
        for m in MODULOS:
            shutil.copy2(TOOLS / m, copia / m)
        # `test_numeros_controle.py` confere a prosa contra o medido, entao le os DOCUMENTOS. Sem
        # eles a copia nasce vermelha por arquivo ausente, e vermelho por ausencia nao prova
        # mutacao nenhuma. [pergunta do QA rodada 11, respondida pelo proprio mecanismo]
        for rel in DOCUMENTOS:
            origem = TOOLS.parent / rel
            if not origem.is_file():
                continue
            destino = raiz_copia / rel
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, destino)

        # o canario tem de estar VERDE na copia antes de qualquer mutacao — senao um vermelho
        # depois nao provaria nada sobre a mutacao.
        for canario in sorted({c for _r, _a, c, _d, _p in MUTACOES}):
            r = subprocess.run([sys.executable, str(copia / canario)],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            checar(f"a copia intacta passa em {canario}", r.returncode == 0,
                   f"-> saiu {r.returncode}; sem isto, vermelho nao prova mutacao")
        if falhou:
            print("\nFAIL — a copia ja nasce vermelha; nao da' para provar mutacao nenhuma.")
            return 1
        print()

        for rotulo, arquivo, canario, de, para in MUTACOES:
            alvo = copia / arquivo
            original = alvo.read_text(encoding="utf-8")
            if original.count(de) != 1:
                checar(f"{rotulo}", False,
                       f"-> ANCORA: {original.count(de)} ocorrencia(s) em {arquivo}; a correcao "
                       f"mudou de forma e esta mutacao parou de descrever o defeito")
                continue
            try:
                alvo.write_text(original.replace(de, para, 1), encoding="utf-8")
                r = subprocess.run([sys.executable, str(copia / canario)],
                                   capture_output=True, text=True, encoding="utf-8",
                                   errors="replace")
                primeira = next((l.strip() for l in (r.stdout or "").splitlines()
                                 if l.strip().startswith("FAIL ") and not l.startswith("FAIL —")),
                                "")
                checar(f"{rotulo}", r.returncode != 0,
                       f"-> {canario} continuou VERDE com o defeito vivo; a correcao nao tem rede")
                if r.returncode != 0 and primeira:
                    print(f"         {primeira[:96]}")
            finally:
                alvo.write_text(original, encoding="utf-8")

    print()
    if falhou:
        print(f"FAIL — {len(falhou)} mutacao(oes) nao foram detectadas: {falhou}")
        return 1
    print(f"PASS — as {len(MUTACOES)} mutacoes foram detectadas, e o repositorio nao foi tocado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
