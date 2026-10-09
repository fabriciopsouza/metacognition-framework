#!/usr/bin/env python3
"""Canário da biblioteca de conhecimento (ADR-120) — `tools/conhecimento.py` + busca do `knowledge_catalog`.

Prova, sobre uma cópia do modelo `exemplos/conhecimento/_modelo/` num diretório temporário:
  (a) VERDE — o modelo passa em `verificar` e nada vence na data do modelo;
  (b) SABOTAGENS — cada regra, quebrada isoladamente, reprova com o achado dela (critérios 17 e 18 do plano B3 e
      1, 3, 7 do DB1): termo sem fonte/data, relação para termo inexistente, termo em dois níveis, CONFIRMADO sem
      quem, estrutura, credencial, CPF, ponteiro quebrado, índice com caminho inexistente, projeto com trabalho aberto
      sem linha no índice, formato não reconhecido;
  (c) EXCEÇÕES LEGÍTIMAS — valor em R$ passa; retrato antigo não vence; campo dentro de bloco de código não é campo;
  (d) VENCIDOS — versão do sistema mudou; configuração com mais de 6 meses; contestado; retrato nunca;
  (e) BUSCA — `knowledge_catalog --recall --conhecimento` devolve a entrada certa e o retrato sai com a data;
      sem `--conhecimento`, a busca não lê a biblioteca (nada carregado por padrão);
  (f) NEUTRALIDADE — o modelo e o verificador não têm termo da lista de neutralidade do núcleo.

Uso: python tools/test_conhecimento.py   (exit 0 PASS; 1 FAIL)
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import conhecimento as k  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

MODELO = os.path.join(ROOT, "exemplos", "conhecimento", "_modelo")
HOJE = datetime.date(2026, 9, 27)
ASSUNTO = "empresas/empresa-exemplo/area-exemplo/assunto-exemplo.md"
DIC_EMP = "empresas/empresa-exemplo/DICIONARIO.md"
falhas = []


def check(nome, cond, detalhe=""):
    print(("  PASS " if cond else "  FAIL ") + nome + ("" if cond else f" — {detalhe}"))
    if not cond:
        falhas.append(nome)


def copia():
    d = tempfile.mkdtemp()
    raiz = os.path.join(d, "bib")
    shutil.copytree(MODELO, raiz)
    return raiz


def troca(raiz, rel, velho, novo):
    p = os.path.join(raiz, rel)
    t = open(p, encoding="utf-8").read()
    assert t.count(velho) == 1, f"âncora do teste não é única em {rel}: {velho!r}"
    open(p, "w", encoding="utf-8").write(t.replace(velho, novo))


def acrescenta(raiz, rel, texto):
    p = os.path.join(raiz, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(texto)


def sabotado(mudanca, esperado, trabalhos=None):
    raiz = copia()
    mudanca(raiz)
    ach = k.verificar(raiz, trabalhos, HOJE)
    return any(re.search(esperado, a) for a in ach), ach


def _git(pasta, *args, env=None):
    return subprocess.run(["git", *args], cwd=pasta, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                          env=dict(os.environ, **(env or {})))


LINHA = "| Projeto A | {e} | — | {c} | proj-a | aberto | — | — |\n"


def _emenda3(casa):
    os.makedirs(os.path.join(casa, "proj-a", "sub"))
    os.makedirs(os.path.join(casa, "outra"))
    check("~\\ e ~/ expandem para a pasta do usuário",
          k._expandir("~\\proj-a\\sub") == os.path.join(casa, "proj-a", "sub")
          and k._expandir("`~/proj-a`") == os.path.join(casa, "proj-a"), k._expandir("~\\proj-a\\sub"))
    check("caminho absoluto e '~nome' ficam como estão",
          k._expandir("C:\\x\\y") == "C:\\x\\y" and k._expandir("~nome/x") == "~nome/x")

    raiz = copia()
    acrescenta(raiz, "INDICE-PROJETOS.md", LINHA.format(e="empresa-exemplo", c="~\\proj-a"))
    check("índice com ~\\ não acusa caminho inexistente",
          not any("Projeto A" in a for a in k.verificar(raiz, None, HOJE)), k.verificar(raiz, None, HOJE))
    ctx = k.contexto(raiz, os.path.join(casa, "proj-a", "sub"), data_fonte=lambda p: None)
    check("subpasta de projeto do índice → EMPRESA", ctx["estado"] == k.EMPRESA
          and ctx["empresa"] == "empresa-exemplo" and ctx["projeto"] == "Projeto A", ctx)
    check("biblioteca da empresa apontada", ctx.get("biblioteca") == os.path.join(raiz, "empresas", "empresa-exemplo"), ctx)
    check("resolver_empresa aceita o ~\\ do índice",
          k.resolver_empresa(raiz, os.path.join(casa, "proj-a"))[0] == "empresa-exemplo")
    ctx = k.contexto(raiz, os.path.join(casa, "outra"))
    check("pasta fora do índice → FORA-DO-ÍNDICE com a instrução do 1º turno",
          ctx["estado"] == k.FORA and "pergunte ao dono a empresa" in k.texto_contexto(ctx), ctx)
    check("FORA-DO-ÍNDICE não cita nome de empresa (isolamento)", "empresa-exemplo" not in k.texto_contexto(ctx),
          k.texto_contexto(ctx))
    raiz3 = copia()
    acrescenta(raiz3, "INDICE-PROJETOS.md", LINHA.format(e="empresa-exemplo", c=os.path.join(k.ROOT, "tools")))
    check("projeto do índice sob a pasta do framework → EMPRESA, não produto próprio",
          k.contexto(raiz3, os.path.join(k.ROOT, "tools"), data_fonte=lambda p: None)["estado"] == k.EMPRESA)
    check("prefixo de nome não é subpasta (proj-a-velho ≠ proj-a)",
          k.contexto(raiz, os.path.join(casa, "proj-a-velho"))["estado"] == k.FORA)
    check("pasta do framework → PRODUTO-PRÓPRIO", k.contexto(raiz, k.ROOT)["estado"] == k.PROPRIO)
    troca(raiz, "conhecimento.json", '"empresa": "empresa-exemplo",', '"empresa": "empresa-exemplo", "sem_empresa": ["~/outra"],')
    check("pasta declarada em sem_empresa → PRODUTO-PRÓPRIO",
          k.contexto(raiz, os.path.join(casa, "outra"))["estado"] == k.PROPRIO)
    check("sem biblioteca → SEM-BIBLIOTECA",
          k.contexto(os.path.join(casa, "nao-existe"), os.path.join(casa, "proj-a"))["estado"] == k.SEM_BIBLIOTECA)
    raiz2 = copia()
    acrescenta(raiz2, "INDICE-PROJETOS.md", LINHA.format(e="empresa-exemplo", c="~\\proj-a")
               + LINHA.format(e="outra-empresa", c="~/proj-a"))
    check("mesmo caminho em duas empresas → AMBÍGUO",
          k.contexto(raiz2, os.path.join(casa, "proj-a"))["estado"] == k.AMBIGUO)
    check("célula com dois caminhos (;) confere cada um",
          sabotado(lambda r: acrescenta(r, "INDICE-PROJETOS.md",
                                        "| P | empresa-exemplo | — | — | p | aberto | README.md; nao-existe.md | — |\n"),
                   r"especificação não existe \(nao-existe\.md\)")[0]
          and not sabotado(lambda r: acrescenta(r, "INDICE-PROJETOS.md",
                                                "| P | empresa-exemplo | — | — | p | aberto | README.md; README.md | — |\n"),
                           r"especificação não existe")[0])

    regra = os.path.join(casa, "proj-a", "regra.md")
    open(regra, "w", encoding="utf-8").write("regra\n")
    entrada = ("\n## F-09 regra do projeto\n- **Tipo:** fato\n- **Classe:** regra de negócio\n"
               "- **Fonte:** ~\\proj-a\\regra.md, §2\n- **Verificado em:** 26/09/2026\n- **Confiança:** INFERIDO\n\ntexto\n")
    acrescenta(raiz, ASSUNTO, entrada)
    novo = lambda p: datetime.date(2026, 9, 30)  # noqa: E731
    velho = lambda p: datetime.date(2026, 9, 20)  # noqa: E731
    mot = {e["nome"]: m for e, m in k.vencidos(raiz, HOJE, data_fonte=novo)}
    check("fonte alterada depois da verificação → a reverificar",
          "fonte alterada em 30/09/2026" in mot.get("F-09 regra do projeto", ""), mot)
    check("fonte anterior à verificação não acusa",
          "F-09 regra do projeto" not in {e["nome"] for e, _ in k.vencidos(raiz, HOJE, data_fonte=velho)})
    check("retrato não vence por fonte alterada", "F-01 lotes bloqueados" not in mot, mot)
    os.makedirs(os.path.join(casa, "pasta com espaco"))
    open(os.path.join(casa, "pasta com espaco", "spec.md"), "w", encoding="utf-8").write("x\n")
    acrescenta(raiz, ASSUNTO, entrada.replace("F-09", "F-10").replace("~\\proj-a\\regra.md, §2",
                                                                      "~\\pasta com espaco\\spec.md linha 12."))
    mot = {e["nome"]: m for e, m in k.vencidos(raiz, HOJE, data_fonte=novo)}
    check("fonte com espaço no caminho e texto depois do arquivo é achada", "F-10 regra do projeto" in mot, mot)
    acrescenta(raiz, ASSUNTO, entrada.replace("F-09", "F-11").replace(
        "~\\proj-a\\regra.md, §2", "~\\nao-existe.md e ~\\pasta com espaco\\spec.md"))
    mot = {e["nome"]: m for e, m in k.vencidos(raiz, HOJE, data_fonte=novo)}
    check("fonte 'A e B': B é conferido mesmo com A ausente", "F-11 regra do projeto" in mot, mot)
    ss = open(os.path.join(ROOT, ".agent", "workflows", "start-session.md"), encoding="utf-8").read()
    check("start-session chama o boot_check por caminho absoluto, nunca relativo",
          "python tools/boot_check.py" not in ss and '"{{FRAMEWORK_ROOT}}\\tools\\boot_check.py"' in ss)
    rep = os.path.join(casa, "rep")
    os.makedirs(rep)
    open(os.path.join(rep, "r.md"), "w", encoding="utf-8").write("a\n")
    for args in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"), ("add", "-A"),
                 ("commit", "-q", "-m", "x")):
        _git(rep, *args, env={"GIT_AUTHOR_DATE": "2020-01-01T00:00:00", "GIT_COMMITTER_DATE": "2020-01-01T00:00:00"})
    check("data_da_fonte = último commit", k.data_da_fonte(os.path.join(rep, "r.md")) == datetime.date(2020, 1, 1))
    open(os.path.join(rep, "r.md"), "a", encoding="utf-8").write("b\n")
    check("edição não commitada conta como mudança de hoje",
          k.data_da_fonte(os.path.join(rep, "r.md")) == datetime.date.today())
    os.remove(regra)
    check("fonte que não existe nesta máquina não acusa",
          "F-09 regra do projeto" not in {e["nome"] for e, _ in k.vencidos(raiz, HOJE, data_fonte=novo)})

    # encerramento: a biblioteca vira repositório git com remoto local
    raiz = copia()
    acrescenta(raiz, "INDICE-PROJETOS.md", LINHA.format(e="empresa-exemplo", c="~\\proj-a"))
    remoto = os.path.join(casa, "remoto.git")
    _git(casa, "init", "-q", "--bare", remoto)
    antigo = {"GIT_AUTHOR_DATE": "2020-01-01T00:00:00", "GIT_COMMITTER_DATE": "2020-01-01T00:00:00"}
    for args in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
                 ("add", "-A"), ("commit", "-q", "-m", "base"),
                 ("remote", "add", "origin", remoto), ("push", "-q", "-u", "origin", "HEAD")):
        _git(raiz, *args, env=antigo)  # commit-base antigo: `--since` filtra pela data do COMMIT
    pa, desde = os.path.join(casa, "proj-a"), datetime.date.today()
    rc, out = k.encerramento(raiz, desde, pa)
    check("sem registro nem declaração → FAIL (1)", rc == 1 and "nenhum registro" in out[-1], out)
    rc, out = k.encerramento(raiz, desde, pa, declarar="só leitura")
    check("declaração → PASS (0)", rc == 0 and "nada a registrar" in out[-1], out)
    lib = os.path.join(raiz, "empresas", "empresa-exemplo")
    acrescenta(raiz, DIC_EMP, "\n")
    rc, out = k.encerramento(raiz, desde, pa, declarar="só leitura")
    check("alteração não commitada → FAIL mesmo com declaração", rc == 1 and "não commitadas" in " ".join(out), out)
    _git(lib, "commit", "-qam", "registro")
    rc, out = k.encerramento(raiz, desde, pa)
    check("commit sem push → FAIL", rc == 1 and "sem push" in out[-1], out)
    _git(raiz, "push", "-q")
    rc, out = k.encerramento(raiz, desde, pa)
    check("commit com push → PASS", rc == 0 and "registrado" in " ".join(out), out)
    acrescenta(raiz, "README.md", "\n")
    _git(raiz, "commit", "-qam", "fora da biblioteca, sem push")
    rc, out = k.encerramento(raiz, desde, pa)
    check("commit sem push FORA da pasta da biblioteca não reprova", rc == 0, out)
    depois = datetime.datetime.now() + datetime.timedelta(hours=1)
    rc, out = k.encerramento(raiz, depois, pa)
    check("--desde com hora: commit anterior ao início não conta", rc == 1 and "nenhum registro" in out[-1], out)
    check("produto próprio → PASS sem biblioteca", k.encerramento(raiz, desde, k.ROOT)[0] == 0)
    check("fora do índice → RECUSADO (2)", k.encerramento(raiz, desde, os.path.join(casa, "outra"))[0] == 2)
    cli = os.path.join(ROOT, "tools", "conhecimento.py")
    r = subprocess.run([sys.executable, cli, "encerramento", "--desde", "04/10/2026", "14:30", "--cwd", ROOT],
                       capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    check("CLI: --desde com hora sem aspas", r.returncode == 0 and "produto próprio" in r.stdout, r.stdout + r.stderr)
    r = subprocess.run([sys.executable, cli, "encerramento", "--desde", "04/10/2026 25:00", "--cwd", ROOT],
                       capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    check("CLI: hora inválida → RECUSADO (2)", r.returncode == 2 and "hora inválida" in r.stdout, r.stdout)
    raiz4 = copia()
    troca(raiz4, "conhecimento.json", '"empresa": "empresa-exemplo",', '"empresa": "empresa-exemplo", "sem_empresa": [""],')
    check("sem_empresa vazio não vira a raiz inteira",
          k.contexto(raiz4, os.path.join(raiz4, "empresas"))["estado"] == k.FORA)


def main():
    print("(a) verde")
    raiz = copia()
    ach = k.verificar(raiz, None, HOJE)
    check("modelo passa em verificar", ach == [], ach)
    check("nada vence na data do modelo", k.vencidos(raiz, HOJE) == [], k.vencidos(raiz, HOJE))

    print("(b) sabotagens")
    casos = [
        ("termo sem fonte", lambda r: troca(r, DIC_EMP, "- **Fonte:** glossário do projeto-exemplo, linha 10\n", ""),
         r"lote: falta \*\*Fonte:\*\*"),
        ("termo sem data", lambda r: troca(r, DIC_EMP, "- **Verificado em:** 26/09/2026\n", ""),
         r"lote: falta \*\*Verificado em:\*\*"),
        ("data impossível", lambda r: troca(r, DIC_EMP, "26/09/2026", "31/02/2026"), r"sem data válida"),
        ("data no futuro", lambda r: troca(r, DIC_EMP, "26/09/2026", "01/01/2030"), r"no futuro"),
        ("relação para termo inexistente", lambda r: troca(r, DIC_EMP, "regulado por: registro controlado",
                                                             "regulado por: termo que nao existe"),
         r"aponta para termo inexistente 'termo que nao existe'"),
        ("relação de tipo desconhecido", lambda r: troca(r, DIC_EMP, "regulado por:", "depende de:"),
         r"relação 'depende de' desconhecida"),
        ("termo em dois níveis", lambda r: acrescenta(r, DIC_EMP, "\n## registro controlado\n- **Tipo:** termo\n"
                                                      "- **Definição:** outra\n- **Fonte:** x\n"
                                                      "- **Verificado em:** 26/09/2026\n- **Confiança:** INFERIDO\n"),
         r"definido em dois níveis"),
        ("termo duas vezes no mesmo nível", lambda r: acrescenta(r, DIC_EMP, "\n## lote\n- **Tipo:** termo\n"
                                                                 "- **Definição:** outra\n- **Fonte:** x\n"
                                                                 "- **Verificado em:** 26/09/2026\n"
                                                                 "- **Confiança:** INFERIDO\n"),
         r"'lote' definido duas vezes"),
        ("CONFIRMADO sem quem", lambda r: troca(r, DIC_EMP, "CONFIRMADO por área de qualidade", "CONFIRMADO"),
         r"Confiança:\*\* use 'CONFIRMADO por <quem>'"),
        ("consulta sem versão", lambda r: troca(r, ASSUNTO, "- **Versão:** 2024\n", ""),
         r"falta \*\*Versão:\*\*"),
        ("consulta sem texto pronto", lambda r: troca(r, ASSUNTO, "```sql\nSELECT SITUACAO, COUNT(*) AS LOTES\n"
                                                      "FROM LOTES\nGROUP BY SITUACAO;\n```\n", ""),
         r"consulta sem bloco de código"),
        ("sistema sem versão atual declarada", lambda r: troca(r, "conhecimento.json", '"SISTEMA-X": "2024"',
                                                               '"OUTRO": "1"'),
         r"versão atual do sistema 'SISTEMA-X' não declarada"),
        ("classe desconhecida", lambda r: troca(r, ASSUNTO, "- **Classe:** retrato", "- **Classe:** palpite"),
         r"classe 'palpite' desconhecida"),
        ("fato de estrutura sem sistema e versão", lambda r: troca(r, ASSUNTO, "- **Classe:** retrato",
                                                                    "- **Classe:** estrutura"),
         r"F-01 lotes bloqueados: classe estrutura exige \*\*Sistema:\*\* e \*\*Versão:\*\*"),
        ("tipo desconhecido", lambda r: troca(r, ASSUNTO, "- **Tipo:** runbook", "- **Tipo:** receita"),
         r"tipo 'receita' desconhecido"),
        ("formato não reconhecido", lambda r: acrescenta(r, ASSUNTO, "\n## solto\ntexto sem campos\n"),
         r"solto: formato não reconhecido"),
        ("campo com nome errado", lambda r: troca(r, ASSUNTO, "- **Pergunta:** quantos", "- **Questao:** quantos"),
         r"campo \*\*Questao:\*\* não reconhecido"),
        ("placeholder", lambda r: troca(r, ASSUNTO, "- **Sistema:** SISTEMA-X", "- **Sistema:** <sistema>"),
         r"vazio ou placeholder"),
        ("termo em arquivo de assunto", lambda r: acrescenta(r, ASSUNTO, "\n## solto2\n- **Tipo:** termo\n"
                                                             "- **Definição:** d\n- **Fonte:** x\n"
                                                             "- **Verificado em:** 26/09/2026\n"
                                                             "- **Confiança:** INFERIDO\n"),
         r"termo mora no DICIONARIO.md"),
        ("arquivo fora da estrutura", lambda r: acrescenta(r, "empresas/empresa-exemplo/solto.md", "# x\n"),
         r"solto.md: fora da estrutura"),
        ("credencial", lambda r: acrescenta(r, ASSUNTO, "\nsenha: abc123\n"), r"contém credencial"),
        ("token", lambda r: acrescenta(r, ASSUNTO, "\napi_key = XYZ\n"), r"contém credencial"),
        ("CPF", lambda r: acrescenta(r, DIC_EMP, "\n123.456.789-09\n"), r"documento de identificação"),
        ("ponteiro quebrado", lambda r: troca(r, ASSUNTO, "- **Fonte:** execução da C-01\n",
                                               "- **Fonte:** execução da C-01\n- **Evidência:** C:/nao/existe.xlsx\n"),
         r"Evidência:\*\* aponta para caminho que não existe"),
        ("índice com caminho inexistente", lambda r: acrescenta(r, "INDICE-PROJETOS.md",
                                                               "| p1 | e | nenhum | C:/nao/existe | repo-p1 | ativo | — | — |\n"),
         r"p1: caminho não existe"),
        ("índice com colunas a menos", lambda r: acrescenta(r, "INDICE-PROJETOS.md", "| p2 | e |\n"),
         r"linha com 2 colunas"),
        ("configuração sem arquivo", lambda r: os.remove(os.path.join(r, "conhecimento.json")),
         r"falta conhecimento.json"),
        # rodada 1 do QA isolado (26/09/2026): formas que sumiam em silêncio
        ("campos antes do primeiro ##", lambda r: troca(r, ASSUNTO, "# area-exemplo · assunto-exemplo\n",
                                                        "# area-exemplo · assunto-exemplo\n- **Tipo:** consulta\n"),
         r"campos antes do primeiro `## <nome>`"),
        ("entrada com ### fundida à anterior", lambda r: acrescenta(r, ASSUNTO, "\n### F-02 outro fato\n"
                                                                    "- **Tipo:** fato\n- **Classe:** retrato\n"),
         r"campo \*\*Tipo:\*\* depois do corpo"),
        ("credencial em URL", lambda r: acrescenta(r, ASSUNTO, "\nhttps://servidor/api?token=abc123\n"),
         r"credencial em URL"),
        ("credencial entre aspas", lambda r: acrescenta(r, ASSUNTO, '\nPASSWORD = "x9y8"\n'), r"contém credencial"),
        # rodada 2 do QA isolado
        ("credencial com anotação à direita", lambda r: acrescenta(r, ASSUNTO, "\nsenha: abc123 (trocar)\n"),
         r"contém credencial"),
        ("cabeçalho de autorização", lambda r: acrescenta(r, ASSUNTO, "\nAuthorization: Bearer eyJabc.def\n"),
         r"cabeçalho de autorização"),
    ]
    for nome, mudanca, esperado in casos:
        ok, ach = sabotado(mudanca, esperado)
        check(nome, ok, ach)
    trab = tempfile.mkdtemp()
    with open(os.path.join(trab, "t1.md"), "w", encoding="utf-8") as fh:
        fh.write("---\ntrabalho: x\nrepo: C:\\Users\\alguem\\projeto-sem-linha\nstatus: aberto\n---\n")
    with open(os.path.join(trab, "t2.md"), "w", encoding="utf-8") as fh:
        fh.write("---\ntrabalho: y\nrepo: projeto-fechado\nstatus: tratado\n---\n")
    with open(os.path.join(trab, "t3.md"), "w", encoding="utf-8") as fh:
        fh.write("---\ntrabalho: z\nrepo: metacognition-framework\nstatus: aberto\n---\n")
    ok, ach = sabotado(lambda r: None, r"'projeto-sem-linha' tem trabalho aberto", trabalhos=trab)
    check("projeto com trabalho aberto sem linha no índice", ok, ach)
    check("trabalho tratado não é cobrado", not any("projeto-fechado" in a for a in ach), ach)
    check("trabalho do próprio framework não é cobrado como projeto",
          not any("metacognition-framework" in a for a in ach), ach)

    print("(c) exceções legítimas")
    ok, ach = sabotado(lambda r: acrescenta(r, ASSUNTO, "\nValor medido: R$ 1.234.567,89 em 26/09/2026.\n"), r".")
    check("valor em R$ passa", ach == [], ach)
    ok, ach = sabotado(lambda r: troca(r, ASSUNTO, "SELECT SITUACAO,", "- **Tipo:** termo\nSELECT SITUACAO,"), r".")
    check("campo dentro de bloco de código não é campo", ach == [], ach)
    ok, ach = sabotado(lambda r: acrescenta(r, DIC_EMP, "\nO campo token: armazena o identificador da sessão.\n"), r".")
    check("prosa que descreve um campo chamado token passa", ach == [], ach)
    ok, ach = sabotado(lambda r: acrescenta(r, ASSUNTO, "\n### passo opcional\ntexto do runbook sem campo\n"), r".")
    check("sub-título só com texto no corpo passa", ach == [], ach)
    raiz_ev = copia()
    troca(raiz_ev, ASSUNTO, "GROUP BY SITUACAO;\n```\n", f"GROUP BY SITUACAO;\n```\n- **Evidência:** {raiz_ev}\n")
    ach = k.verificar(raiz_ev, None, HOJE)
    ent = next(e for e in k.carregar(raiz_ev)[1] if e["nome"].startswith("C-01"))
    check("campo depois do bloco de código da consulta passa e é lido", ach == [] and "Evidência" in ent["campos"],
          (ach, ent["campos"]))
    ok, ach = sabotado(lambda r: acrescenta(r, "INDICE-PROJETOS.md",
                                            f"| p3 | e | nenhum | {r} | repo-p3 | ativo | — | — |\n"), r".")
    check("linha de índice com caminho existente passa", ach == [], ach)

    print("(d) vencidos")
    raiz = copia()
    longe = datetime.date(2027, 12, 1)
    motivos = {e["nome"]: m for e, m in k.vencidos(raiz, longe)}
    check("retrato antigo não vence", "F-01 lotes bloqueados" not in motivos, motivos)
    check("termo com mais de 12 meses vence", "lote" in motivos, motivos)
    check("runbook (configuração) com mais de 6 meses vence", "R-01 como exportar o resultado da C-01" in motivos, motivos)
    check("consulta com versão atual não vence por tempo", "C-01 lotes por situação" not in motivos, motivos)
    troca(raiz, "conhecimento.json", '"SISTEMA-X": "2024"', '"SISTEMA-X": "2025"')
    motivos = {e["nome"]: m for e, m in k.vencidos(raiz, HOJE)}
    check("consulta vence quando a versão do sistema muda",
          "versão do sistema mudou" in motivos.get("C-01 lotes por situação", ""), motivos)
    raiz = copia()
    troca(raiz, ASSUNTO, "- **Classe:** retrato\n", "- **Classe:** retrato\n- **Contestado em:** 27/09/2026\n")
    motivos = {e["nome"]: m for e, m in k.vencidos(raiz, HOJE)}
    check("contestado vira a reverificar, mesmo sendo retrato", "F-01 lotes bloqueados" in motivos, motivos)

    print("(e) busca")
    raiz = copia()
    vazio = tempfile.mkdtemp()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    kc = os.path.join(ROOT, "tools", "knowledge_catalog.py")
    r = subprocess.run([sys.executable, kc, "--recall", "--context", "lotes bloqueados", "--out-dir", vazio,
                        "--conhecimento", raiz, "--empresa", "todas"], capture_output=True, text=True, encoding="utf-8", env=env)
    linha = next((ln for ln in r.stdout.splitlines() if "F-01" in ln), "")
    check("recall com a biblioteca devolve a entrada", r.returncode == 0 and bool(linha), r.stdout + r.stderr)
    check("retrato sai com a data", "em 26/09/2026: 120 lotes" in linha, linha)
    r = subprocess.run([sys.executable, kc, "--recall", "--context", "lotes bloqueados", "--out-dir", vazio],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    check("sem --conhecimento a biblioteca não é lida", r.returncode == 2 and "F-01" not in r.stdout,
          r.stdout + r.stderr)
    vazia = tempfile.mkdtemp()
    r = subprocess.run([sys.executable, kc, "--recall", "--context", "x", "--out-dir", vazio, "--conhecimento", vazia,
                        "--empresa", "nenhuma"],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    check("biblioteca vazia responde 'nada encontrado' sem erro", r.returncode == 0 and "nada encontrado" in r.stdout,
          r.stdout + r.stderr)

    print("(g) emenda 3 — contexto da pasta, fonte alterada, encerramento")
    casa = tempfile.mkdtemp()
    antes = {v: os.environ.get(v) for v in ("HOME", "USERPROFILE")}
    os.environ["HOME"] = os.environ["USERPROFILE"] = casa  # `~` desta prova = pasta temporária
    try:
        _emenda3(casa)
    finally:
        for v, x in antes.items():
            if x is None:
                os.environ.pop(v, None)
            else:
                os.environ[v] = x

    print("(f) neutralidade")
    with open(os.path.join(ROOT, "tools", "agnostic-denylist.txt"), encoding="utf-8") as fh:
        termos = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    textos = [open(os.path.join(ROOT, "tools", "conhecimento.py"), encoding="utf-8").read()]
    for base, _d, arquivos in os.walk(MODELO):
        textos += [open(os.path.join(base, f), encoding="utf-8").read() for f in arquivos]
    achados = [t for t in termos if any(re.search(t, x, re.I) for x in textos)]
    check("modelo e verificador sem termo de domínio", achados == [], achados)

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({len(falhas)})" if falhas else "PASS")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
