#!/usr/bin/env python3
"""Canário do isolamento entre empresas na biblioteca de conhecimento (emenda do ADR-120).

Regra do dono (27/09/2026): o conhecimento de uma empresa nunca aparece no trabalho de outra; só o saber puro de
assunto é compartilhado. Duas empresas FALSAS (alfa e beta) com o mesmo termo e a mesma consulta, e uma camada
`assuntos/`. Prova:
  (b) RECORTE — `--recall` e `verificar` com `--empresa alfa` não devolvem nem leem beta; devolvem assuntos; empresa
      resolvida pelo índice a partir do diretório; sem resolução, recusa (exit 2) sem ler nada;
  (c) RELAÇÕES E CAMINHOS — relação para termo de outra empresa e caminho de projeto de outra empresa reprovam;
      relação para termo de assunto passa; assunto não aponta para empresa;
  (d) ASSUNTO SEM DADO DE EMPRESA — cada identificador reprova: nome da empresa, valor de `## Identificadores`,
      caminho e repositório do índice, objeto e campo de cliente, tipo de movimento de cliente, caminho de usuário;
      o valor de empresa fora do recorte não aparece na mensagem; saber puro de assunto passa;
  (e) OUTRA MÁQUINA — `verificar --empresa alfa` não reprova por caminho inexistente de beta.

Uso: python tools/test_conhecimento_isolamento.py   (exit 0 PASS; 1 FAIL)
"""
import json
import os
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

falhas = []


def check(nome, cond, detalhe=""):
    print(("  PASS " if cond else "  FAIL ") + nome + ("" if cond else f" — {detalhe}"))
    if not cond:
        falhas.append(nome)


CAB = "- **Fonte:** reunião de teste\n- **Verificado em:** 20/09/2026\n- **Confiança:** CONFIRMADO por equipe\n"


def termo(nome, definicao, rel=""):
    return f"## {nome}\n- **Tipo:** termo\n- **Definição:** {definicao}\n" + (f"- **Relações:** {rel}\n" if rel else "") + CAB + "\n"


def consulta(nome, pergunta, extra=""):
    return (f"## {nome}\n- **Tipo:** consulta\n- **Pergunta:** {pergunta}\n- **Sistema:** ERPX\n- **Versão:** 1\n"
            + extra + CAB + "\n```sql\nSELECT MATERIAL, SUM(QTD) FROM ESTOQUE GROUP BY MATERIAL;\n```\n\n")


def escrever(p, texto):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(texto)


def montar():
    """Biblioteca com alfa e beta, cada uma com projeto próprio no índice; beta aponta para arquivo que só existe
    na máquina dela (caminho inexistente aqui)."""
    base = tempfile.mkdtemp()
    raiz = os.path.join(base, "biblioteca")
    proj_a, proj_b = os.path.join(base, "projeto-alfa"), os.path.join(base, "projeto-beta")
    os.makedirs(os.path.join(proj_a, "sub"))
    os.makedirs(proj_b)
    escrever(os.path.join(proj_a, "consulta.sql"), "select 1;")
    escrever(os.path.join(raiz, "conhecimento.json"), '{"versoes_atuais": {"ERPX": "1"}}')
    escrever(os.path.join(raiz, "INDICE-PROJETOS.md"),
             "| Projeto | Empresa | Perfil regulado | Caminho | Repositório | Estado | Especificação | Dicionário |\n"
             "|---|---|---|---|---|---|---|---|\n"
             f"| Estoque A | alfa | — | {proj_a} | repo-alfa-estoque | aberto | — | — |\n"
             f"| Estoque B | beta | — | {proj_b} | repo-beta-estoque | aberto | — | — |\n")
    escrever(os.path.join(raiz, "assuntos", "erp-estoque", "DICIONARIO.md"),
             "# erp-estoque\n\n" + termo("material", "item controlado em estoque"))
    escrever(os.path.join(raiz, "assuntos", "erp-estoque", "estoque.md"),
             "# erp-estoque · estoque\n\n" + consulta("A-C1 saldo por material genérico",
                                                    "qual o saldo de estoque por material no padrão?"))
    escrever(os.path.join(raiz, "empresas", "alfa", "DICIONARIO.md"),
             "# alfa\n\n" + termo("centro", "centro produtivo da alfa", "é um: material")
             + "## Identificadores\n- **Tipo:** identificadores\n- **Valores:** 7001; ALFA-X1\n" + CAB + "\n")
    escrever(os.path.join(raiz, "empresas", "alfa", "estoque", "consultas.md"),
             "# alfa · estoque\n\n" + consulta("AL-C1 estoque consulta por centro alfa",
                                             "estoque consulta por centro na alfa?",
                                             f"- **Aponta para:** {os.path.join(proj_a, 'consulta.sql')}\n"))
    escrever(os.path.join(raiz, "empresas", "beta", "DICIONARIO.md"),
             "# beta\n\n" + termo("centro", "centro logístico da beta")
             + termo("doca", "doca de recebimento da beta")
             + "## Identificadores\n- **Tipo:** identificadores\n- **Valores:** 8802; BETA-Q7\n" + CAB + "\n")
    escrever(os.path.join(raiz, "empresas", "beta", "estoque", "consultas.md"),
             "# beta · estoque\n\n" + consulta("BE-C1 estoque consulta por centro beta",
                                             "estoque consulta por centro na beta?",
                                             f"- **Aponta para:** {os.path.join(proj_b, 'so-na-maquina-da-beta.sql')}\n"))
    k.publicar_identificadores(raiz, "alfa")
    k.publicar_identificadores(raiz, "beta")
    return base, raiz, proj_a, proj_b


def recall(raiz, cwd, *extra):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    vazio = tempfile.mkdtemp()
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "knowledge_catalog.py"), "--recall", "--context",
                        "estoque consulta por centro", "--out-dir", vazio, "--conhecimento", raiz, *extra],
                       capture_output=True, text=True, encoding="utf-8", env=env, cwd=cwd)
    shutil.rmtree(vazio, ignore_errors=True)
    return r


def acrescentar(p, texto):
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(texto)


def main():
    base, raiz, proj_a, proj_b = montar()
    try:
        print("(b) recorte por empresa")
        r = recall(raiz, ROOT, "--empresa", "alfa")
        check("--empresa alfa devolve alfa e o assunto", r.returncode == 0 and "AL-C1" in r.stdout
              and "A-C1" in r.stdout, r.stdout + r.stderr)
        check("--empresa alfa não devolve nada da beta", "BE-C1" not in r.stdout and "beta" not in r.stdout.lower(),
              r.stdout)
        check("a lista de identificadores não sai na busca", "7001" not in r.stdout, r.stdout)
        r = recall(raiz, os.path.join(proj_a, "sub"))
        check("sem --empresa, dentro do projeto da alfa, resolve alfa pelo índice", r.returncode == 0
              and "empresa: alfa (resolvida pelo INDICE" in r.stdout and "BE-C1" not in r.stdout, r.stdout + r.stderr)
        r = recall(raiz, ROOT)
        check("sem --empresa e fora de projeto: recusa (exit 2) sem devolver nada", r.returncode == 2
              and "AL-C1" not in r.stdout and "BE-C1" not in r.stdout and "RECUSADO" in r.stderr, r.stdout + r.stderr)
        r = recall(raiz, ROOT, "--empresa", "nenhuma")
        check("--empresa nenhuma devolve só assunto", r.returncode == 0 and "A-C1" in r.stdout
              and "AL-C1" not in r.stdout and "BE-C1" not in r.stdout, r.stdout)
        vistos = {e["arquivo"].split("/")[1] for e in k.carregar(raiz, "alfa")[1] if e["arquivo"].startswith("empresas/")}
        check("carregar(alfa) não abre arquivo da beta", vistos == {"alfa"}, vistos)
        r2 = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "conhecimento.py"), "verificar", raiz],
                            capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"))
        check("verificar sem --empresa e fora de projeto: recusa (exit 2)", r2.returncode == 2 and "RECUSADO" in r2.stdout,
              r2.stdout)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        cli = [sys.executable, os.path.join(ROOT, "tools", "conhecimento.py")]
        r3 = subprocess.run(cli + ["verificar", raiz, "--empresa", "alfa"], capture_output=True, text=True,
                            encoding="utf-8", cwd=ROOT, env=env)
        check("CLI verificar --empresa alfa passa (a beta não é verificada)", r3.returncode == 0
              and "beta" not in r3.stdout.lower(), r3.stdout)
        r4 = subprocess.run(cli + ["verificar", raiz], capture_output=True, text=True, encoding="utf-8",
                            cwd=proj_b, env=env)
        check("CLI verificar dentro do projeto da beta resolve beta e só a beta", "empresa: beta (resolvida" in r4.stdout
              and "so-na-maquina-da-beta" in r4.stdout and "alfa" not in r4.stdout.lower().replace("empresa: beta", ""),
              r4.stdout)
        r5 = subprocess.run(cli + ["vencidos", raiz, "--empresa", "nenhuma", "--hoje", "01/01/2030"],
                            capture_output=True, text=True, encoding="utf-8", cwd=ROOT, env=env)
        check("CLI vencidos --empresa nenhuma não lista entrada de empresa", "empresas/" not in r5.stdout, r5.stdout)
        check("dois projetos de empresas diferentes no mesmo caminho: recusa", "mais de uma empresa" in _recusa(
            lambda: k.resolver_empresa(_indice_duplo(raiz, proj_a), proj_a)))

        print("(e) outra máquina")
        ach_a = k.verificar(raiz, empresa="alfa")
        check("verificar --empresa alfa passa (caminho inexistente da beta não reprova a alfa)", ach_a == [], ach_a)
        ach_t = k.verificar(raiz, empresa="todas")
        check("na manutenção (todas), o caminho da beta que não está nesta máquina aparece",
              any("so-na-maquina-da-beta" in a for a in ach_t), ach_t)

        print("(c) relações e caminhos")
        casos = [
            ("relação de alfa para termo só da beta", os.path.join(raiz, "empresas", "alfa", "DICIONARIO.md"),
             termo("rampa", "rampa da alfa", "parte de: doca"), "alfa", "fora do escopo"),
            ("assunto apontando para termo de empresa", os.path.join(raiz, "assuntos", "erp-estoque", "DICIONARIO.md"),
             termo("lote", "lote genérico", "parte de: centro"), "nenhuma", "fora do escopo"),
            ("alfa apontando para caminho do projeto da beta", os.path.join(raiz, "empresas", "alfa", "estoque", "consultas.md"),
             consulta("AL-C2 cruzada", "consulta cruzada?", f"- **Aponta para:** {os.path.join(proj_b, 'x.sql')}\n"),
             "alfa", "caminho de projeto de outra empresa"),
        ]
        for nome, arq, texto, emp, trecho in casos:
            original = open(arq, encoding="utf-8").read()
            acrescentar(arq, texto)
            ach = k.verificar(raiz, empresa=emp)
            check(nome + " reprova (bloqueante)", any(trecho in a and "bloqueante" in a for a in ach), ach)
            check(nome + ": a mensagem não expõe a outra empresa", not any("beta" in a.lower() for a in ach), ach)
            escrever(arq, original)
        arq = os.path.join(raiz, "empresas", "alfa", "DICIONARIO.md")
        original = open(arq, encoding="utf-8").read()
        acrescentar(arq, termo("peça", "peça da alfa", "é um: material"))
        check("relação de empresa para termo de assunto passa", k.verificar(raiz, empresa="alfa") == [],
              k.verificar(raiz, empresa="alfa"))
        escrever(arq, original)
        check("mesmo termo em duas empresas não é achado", not any("termo 'centro'" in a for a in ach_t), ach_t)
        trab = tempfile.mkdtemp()
        escrever(os.path.join(trab, "t.md"), "---\nrepo: repo-gama-sem-indice\nstatus: aberto\n---\n")
        check("trabalho aberto sem linha no índice não é citado no recorte de uma empresa",
              not any("repo-gama" in a for a in k.verificar(raiz, trab, empresa="alfa")))
        check("... e é citado na manutenção (todas)", any("repo-gama" in a for a in k.verificar(raiz, trab, empresa="todas")))
        shutil.rmtree(trab, ignore_errors=True)
        escrever(os.path.join(raiz, "empresas", "alfa", "conhecimento.json"), '{"versoes_atuais": {"ERPA": "7"}}')
        arq = os.path.join(raiz, "empresas", "alfa", "estoque", "consultas.md")
        original = open(arq, encoding="utf-8").read()
        acrescentar(arq, consulta("AL-C3 versão própria", "consulta no sistema da alfa?").replace("ERPX", "ERPA"))
        check("versão de sistema da empresa vem do conhecimento.json dela", k.verificar(raiz, empresa="alfa") == [],
              k.verificar(raiz, empresa="alfa"))
        escrever(arq, original)
        os.remove(os.path.join(raiz, "empresas", "alfa", "conhecimento.json"))

        print("(d) assunto sem dado de empresa")
        arq = os.path.join(raiz, "assuntos", "erp-estoque", "estoque.md")
        original = open(arq, encoding="utf-8").read()
        sujos = [
            ("nome de empresa", "O relatório da Beta usa este saldo.", "identificador de empresa"),
            ("valor de ## Identificadores", "Filtrar o centro 8802 no relatório.", "identificador de empresa"),
            ("repositório do índice", "Ver repo-beta-estoque para exemplos.", "identificador de empresa"),
            ("caminho de projeto do índice", f"Arquivo em {os.path.join(proj_b, 'q.sql')}.", "identificador de empresa"),
            ("objeto de cliente Z*", "Rodar o programa ZMM001 antes.", "namespace de cliente"),
            ("objeto de cliente com sublinhado", "Tabela Z_ESTOQUE guarda o saldo.", "namespace de cliente"),
            ("tabela de cliente sem dígito", "A tabela ZMARA estende o cadastro.", "namespace de cliente"),
            ("campo de cliente ZZ*", "O campo ZZLOCAL indica a doca.", "campo de cliente"),
            ("campo de cliente YY*", "O campo YYORIGEM indica a origem.", "campo de cliente"),
            ("tipo de movimento 9xx", "Usar o tipo de movimento 951 na baixa.", "tipo de movimento"),
            ("tipo de movimento X/Y/Z", "BWART: Z01 para transferência.", "tipo de movimento"),
            ("caminho de usuário", r"Salvar em C:\Users\fulano\projeto\saida.xlsx", "caminho"),
        ]
        for nome, frase, trecho in sujos:
            escrever(arq, original + frase + "\n")
            ach = k.verificar(raiz, empresa="alfa")
            check(f"assunto com {nome} reprova", any("assuntos/" in a and trecho in a and "bloqueante" in a for a in ach), ach)
        escrever(arq, original + "Usar o tipo de movimento 951 na baixa.\nFiltrar o centro 8802.\n")
        ach = k.verificar(raiz, empresa="alfa")
        check("valor de empresa fora do recorte não aparece na mensagem", not any("8802" in a for a in ach)
              and any("valor omitido" in a for a in ach), ach)
        limpos = ["Formato de data YYYY-MM-DD no arquivo.", "Movimento 101 é a entrada de mercadoria padrão.",
                  "ZIP e YES não são objetos; ZERO é zero; YEAR é ano.", "Do eixo X ao eixo Z, de A a Z.",
                  "O preço é 951 reais e a página 920.", r"Salvar em C:\Users\<usuario>\projeto\saida.xlsx",
                  "A transação padrão de estoque lista o saldo por material."]
        escrever(arq, original + "\n".join(limpos) + "\n")
        ach = k.verificar(raiz, empresa="alfa")
        check("saber puro de assunto passa (sem falso positivo)", ach == [], ach)
        escrever(arq, original)

        print("achados da revisão do código (27/09)")
        escrever(os.path.join(raiz, "empresas", "alfa2", "DICIONARIO.md"), "# alfa2\n\n" + termo("esteira", "esteira da alfa2"))
        r = recall(raiz, ROOT, "--empresa", "alfa")
        vistos = {e["arquivo"].split("/")[1] for e in k.carregar(raiz, "alfa")[1] if e["arquivo"].startswith("empresas/")}
        check("--empresa alfa não lê empresas/alfa2 (nome que começa igual)", vistos == {"alfa"}, vistos)
        shutil.rmtree(os.path.join(raiz, "empresas", "alfa2"))
        os.rename(os.path.join(raiz, "empresas", "beta"), os.path.join(raiz, "empresas", "Beta"))
        cfg_b, ents_b, ach_b = k.carregar(raiz, "beta")
        check("pasta 'Beta' com --empresa beta: lê a própria empresa e acusa a maiúscula (sem falso PASS)",
              any(e["nome"].startswith("BE-C1") for e in ents_b) and any("maiúscula" in a for a in ach_b),
              ([e["nome"] for e in ents_b], ach_b))
        os.rename(os.path.join(raiz, "empresas", "Beta"), os.path.join(raiz, "empresas", "beta"))
        arq = os.path.join(raiz, "empresas", "alfa", "DICIONARIO.md")
        original = open(arq, encoding="utf-8").read()
        escrever(arq, original.replace("- **Valores:** 7001; ALFA-X1", "- **Valores:** 7001; ALFA-X1; MM"))
        ach = k.verificar(raiz, empresa="alfa")
        check("identificador curto (sigla de módulo) é recusado na declaração", any("curtos demais" in a and "MM" in a
                                                                                   for a in ach), ach)
        arq2 = os.path.join(raiz, "assuntos", "erp-estoque", "estoque.md")
        orig2 = open(arq2, encoding="utf-8").read()
        escrever(arq2, orig2 + "Como o MM trata a reserva no padrão.\n")
        check("... e não reprova saber puro que cita o módulo", not any("assuntos/" in a for a in k.verificar(raiz, empresa="alfa")))
        escrever(arq2, orig2)
        escrever(arq, original)

        print("emenda 2: biblioteca externa, hash e relatórios")
        ext = os.path.join(base, "conhecimento-negocio", "empresas", "gama")
        escrever(os.path.join(ext, k.MARCADOR), "gama\n")
        escrever(os.path.join(ext, "DICIONARIO.md"), "# gama\n\n" + termo("silo", "silo da gama")
                 + "## Identificadores\n- **Tipo:** identificadores\n- **Valores:** GAMA-77; 9911\n" + CAB + "\n")
        escrever(os.path.join(ext, "logistica", "consultas.md"), "# gama\n\n" + consulta("GA-C1 estoque consulta por centro gama",
                                                                                   "estoque consulta por centro na gama?"))
        escrever(os.path.join(ext, "README.md"), "# biblioteca da gama\n")
        cfg_p = os.path.join(raiz, "conhecimento.json")
        cfg_orig = open(cfg_p, encoding="utf-8").read()
        escrever(cfg_p, '{"versoes_atuais": {"ERPX": "1"}, "bibliotecas": ["../conhecimento-negocio"]}')
        check("biblioteca externa achada pelo marcador", k.bibliotecas_externas(raiz) == {"gama": ext}, k.bibliotecas_externas(raiz))
        r = recall(raiz, ROOT, "--empresa", "gama")
        check("--empresa gama lê a biblioteca externa e não a alfa", "GA-C1" in r.stdout and "AL-C1" not in r.stdout, r.stdout)
        r = recall(raiz, ROOT, "--empresa", "alfa")
        check("--empresa alfa não lê a biblioteca externa da gama", "GA-C1" not in r.stdout, r.stdout)
        check("verificar da gama acusa a lista em hash não publicada",
              any("gama não publicados" in a for a in k.verificar(raiz, empresa="gama")))
        k.publicar_identificadores(raiz, "gama")
        check("verificar da gama passa depois de publicar", k.verificar(raiz, empresa="gama") == [], k.verificar(raiz, empresa="gama"))
        # a gama sai desta máquina: só a lista em hash fica; o assunto que cita o código dela ainda reprova
        shutil.move(os.path.join(base, "conhecimento-negocio"), os.path.join(base, "fora-da-maquina"))
        arq = os.path.join(raiz, "assuntos", "erp-estoque", "estoque.md")
        orig = open(arq, encoding="utf-8").read()
        escrever(arq, orig + "Na doca GAMA-77 o saldo vira.\n")
        ach = k.verificar(raiz, empresa="alfa")
        check("empresa ausente da máquina: identificador em hash reprova o assunto, sem mostrar o valor",
              any("lista publicada em hash" in a for a in ach) and not any("GAMA-77" in a or "gama-77" in a for a in ach), ach)
        escrever(arq, orig)
        pred = k.mencao_de_outra_empresa(raiz, "alfa")
        check("relatório que cita código de empresa ausente é filtrado", pred("sessão no centro 9911 da outra"))
        check("relatório que cita outra empresa presente (beta) é filtrado", pred("ajuste feito na Beta ontem"))
        check("relatório que cita só a própria empresa não é filtrado", not pred("ajuste no centro 7001 da alfa"))
        check("hash ignora maiúsculas e espaços", k._hash(" GAMA-77 ") == k._hash("gama-77"))
        check("'todas' não filtra relatório", not k.mencao_de_outra_empresa(raiz, "todas")("centro 9911 da beta"))
        ach = k.verificar(raiz, empresa="gama")
        check("empresa sem biblioteca nesta máquina: verificar reprova (sem falso PASS)",
              any("não encontrada nesta máquina" in a for a in ach), ach)
        r = recall(raiz, ROOT, "--empresa", "gama")
        check("... e o --recall avisa que só leu assuntos e perfis", "AVISO: a biblioteca de gama não está" in r.stdout, r.stdout)
        cat = tempfile.mkdtemp()
        rel_out = [{"report_id": "r1", "source": "docs/_intake/execution-report-2026-09-12-beta-estrategia.md",
                    "date": "2026-09-12", "gaps": [], "melhorias": ["estoque consulta por centro melhorou"],
                    "boas_praticas": [], "detecao": [], "licoes": {}, "placar": []},
                   {"report_id": "r2", "source": "docs/_intake/execution-report-2026-09-13-geral.md",
                    "date": "2026-09-13", "gaps": [], "melhorias": ["estoque consulta por centro revisada"],
                    "boas_praticas": [], "detecao": [], "licoes": {}, "placar": []}]
        with open(os.path.join(cat, "catalog.json"), "w", encoding="utf-8") as fh:
            json.dump(rel_out, fh)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "knowledge_catalog.py"), "--recall", "--context",
                            "estoque consulta por centro", "--out-dir", cat, "--conhecimento", raiz, "--empresa", "alfa"],
                           capture_output=True, text=True, encoding="utf-8", env=env, cwd=ROOT)
        check("relatório cujo NOME de arquivo cita outra empresa é omitido", "beta-estrategia" not in r.stdout
              and "execution-report-2026-09-13-geral" in r.stdout and "1 omitido" in r.stdout, r.stdout + r.stderr)
        shutil.rmtree(cat, ignore_errors=True)
        shutil.move(os.path.join(base, "fora-da-maquina"), os.path.join(base, "conhecimento-negocio"))
        escrever(cfg_p, cfg_orig)
        for nome in os.listdir(os.path.join(raiz, k.DIR_HASHES)):
            if os.path.normcase(os.path.join(raiz, k.DIR_HASHES, nome)) == os.path.normcase(k.arquivo_hashes(raiz, "gama")):
                os.remove(os.path.join(raiz, k.DIR_HASHES, nome))

        print("emenda 4: caminho com ~ (perfis de usuário diferentes; bloqueio de outra empresa)")
        casa = os.path.join(base, "casa")
        os.makedirs(os.path.join(casa, "proj-alfa-casa", "sub"))
        os.makedirs(os.path.join(casa, "proj-beta-casa"))
        escrever(os.path.join(casa, "proj-alfa-casa", "q.sql"), "select 1;")
        env_orig = {v: os.environ.get(v) for v in ("USERPROFILE", "HOME")}
        os.environ["USERPROFILE"] = os.environ["HOME"] = casa
        idx = os.path.join(raiz, "INDICE-PROJETOS.md")
        idx_orig = open(idx, encoding="utf-8").read()
        acrescentar(idx, "| Casa A | alfa | — | ~\\proj-alfa-casa | repo-alfa-casa | aberto | ~/proj-alfa-casa/q.sql | — |\n"
                         "| Casa B | beta | — | ~/proj-beta-casa | repo-beta-casa | aberto | — | — |\n")
        k.publicar_identificadores(raiz, "alfa")  # o repositório novo da alfa é identificador dela
        arq = os.path.join(raiz, "empresas", "alfa", "estoque", "consultas.md")
        original = open(arq, encoding="utf-8").read()
        try:
            check("~ no índice: diretório dentro do projeto resolve a empresa",
                  k.resolver_empresa(raiz, os.path.join(casa, "proj-alfa-casa", "sub"))[0] == "alfa")
            check("~ no índice: o caminho e a especificação existem nesta máquina (sem achado)",
                  k.verificar(raiz, empresa="alfa") == [], k.verificar(raiz, empresa="alfa"))
            acrescentar(arq, consulta("AL-C4 com til", "consulta com til?", "- **Aponta para:** ~\\proj-alfa-casa\\q.sql\n"))
            check("Aponta para com ~ que existe passa", k.verificar(raiz, empresa="alfa") == [], k.verificar(raiz, empresa="alfa"))
            escrever(arq, original)
            acrescentar(arq, consulta("AL-C5 til inexistente", "consulta?", "- **Aponta para:** ~/proj-alfa-casa/nao.sql\n"))
            check("Aponta para com ~ que não existe reprova",
                  any("AL-C5" in a and "não existe" in a for a in k.verificar(raiz, empresa="alfa")))
            escrever(arq, original)
            acrescentar(arq, consulta("AL-C6 til cruzado", "consulta?", "- **Evidência:** ~\\proj-beta-casa\\x.sql\n"))
            ach = k.verificar(raiz, empresa="alfa")
            check("~ apontando para projeto de outra empresa é bloqueante e não cita a outra",
                  any("AL-C6" in a and "outra empresa" in a and "bloqueante" in a for a in ach)
                  and not any("beta" in a.lower() for a in ach), ach)
        finally:
            escrever(arq, original)
            escrever(idx, idx_orig)
            k.publicar_identificadores(raiz, "alfa")
            for v, val in env_orig.items():
                if val is None:
                    os.environ.pop(v, None)
                else:
                    os.environ[v] = val

        print("emenda 4: atalho de pasta (macOS /var -> /private/var; unidade mapeada no Windows)")
        # atalho SIMULADO: realpath troca o prefixo da pasta temporária por outro (sem criar link de verdade)
        base_n = os.path.normcase(os.path.normpath(os.path.abspath(base)))
        base_real = os.path.join(tempfile.gettempdir(), "atalho-simulado-" + os.path.basename(base))
        real_orig = os.path.realpath

        def real_falso(p, *a, **kw):
            n = os.path.normcase(os.path.normpath(os.path.abspath(p)))
            if n == base_n or n.startswith(base_n + os.sep):
                return base_real + n[len(base_n):]
            nb = os.path.normcase(base_real)
            if n == nb or n.startswith(nb + os.sep):
                return n  # já está na forma "resolvida": o realpath real expandiria nome curto (RUNNER~1) ou /var
            return real_orig(p, *a, **kw)
        os.path.realpath = real_falso
        try:
            try:
                emp_atalho = k.resolver_empresa(raiz, os.path.join(base_real, "projeto-alfa", "sub"))[0]
            except k.Recusa as e:
                emp_atalho = f"RECUSA: {e}"
            check("pasta na forma resolvida (atalho) resolve a empresa pelo índice escrito", emp_atalho == "alfa",
                  emp_atalho)
            idents = k.identificadores_de_empresa(raiz)
            check("identificador guarda o caminho ESCRITO do índice, não o resolvido",
                  os.path.normcase(os.path.normpath(proj_b)) in idents and not any(v.startswith(os.path.normcase(base_real))
                                                                                     for v in idents), list(idents))
            check("texto de assunto com o caminho escrito continua reprovando",
                  bool(k.verificar_assunto(f"Arquivo em {os.path.join(proj_b, 'q.sql')}.", idents, "alfa")))
        finally:
            os.path.realpath = real_orig

        print("identificadores")
        arq = os.path.join(raiz, "assuntos", "erp-estoque", "DICIONARIO.md")
        original = open(arq, encoding="utf-8").read()
        acrescentar(arq, "## Identificadores\n- **Tipo:** identificadores\n- **Valores:** X\n" + CAB)
        check("tipo identificadores fora do DICIONARIO de empresa reprova",
              any("identificadores só mora" in a for a in k.verificar(raiz, empresa="alfa")))
        escrever(arq, original)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print(f"\nRESULTADO: {'FAIL' if falhas else 'PASS'} ({len(falhas)} falha(s))")
    return 1 if falhas else 0


def _indice_duplo(raiz, caminho):
    """Cópia da biblioteca com dois projetos de empresas diferentes no mesmo caminho."""
    d = tempfile.mkdtemp()
    escrever(os.path.join(d, "INDICE-PROJETOS.md"),
             "| Projeto | Empresa | Perfil regulado | Caminho | Repositório | Estado | Especificação | Dicionário |\n"
             "|---|---|---|---|---|---|---|---|\n"
             f"| P1 | alfa | — | {caminho} | r1 | aberto | — | — |\n| P2 | beta | — | {caminho} | r2 | aberto | — | — |\n")
    return d


def _recusa(fn):
    try:
        fn()
    except k.Recusa as e:
        return str(e)
    return ""


if __name__ == "__main__":
    sys.exit(main())
