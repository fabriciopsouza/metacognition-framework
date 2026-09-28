#!/usr/bin/env python3
"""Canário dos documentos do kit regulado (B3a-3, ADR-124) — `tools/documento_regulado.py` e `tools/mudancas_spec.py`.

Perfil SINTÉTICO próprio (valores literais aqui). Prova:
  (a) documento do perfil gerado em md e docx: todo REQ com os atributos do perfil; código vazio vira "a preencher
      pela Qualidade" (nunca inventado); aprovação com os papéis do perfil (critérios 10 e 12);
  (b) lacunas reprovam e nada é gravado: atributo faltando, documento sem linha em "Documentos controlados",
      teste reprovado sem desvio, desvio sem tratamento, item de prontidão faltando (critério 11);
  (c) `--rascunho` grava marcado e com PENDENTE;
  (d) perfil sem o documento recusa (a ERU é do perfil, não do núcleo); projeto sem impacto recusa;
  (e) mudança e versão: versões do git com data e autor; "o que mudou" do Replanejamento; mudança sem quem aprovou
      reprova (critério 13);
  (f) neutralidade: os motores não citam órgão, norma ou documento de domínio.

Uso: python tools/test_documento_regulado.py   (exit 0 PASS; 1 FAIL)
"""
import json
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import documento_regulado as dr  # noqa: E402
import mudancas_spec as ms  # noqa: E402
import regulado  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

PERFIL = {
    "profile": "teste-sintetico",
    "categorias_software": {"kit_comum": ["TAP"], "4": ["doc-a"]},
    "testes_obrigatorios_com_impacto": ["integridade de dados"],
    "documentos": {
        "doc-requisitos": {"titulo": "Documento de Requisitos X", "requisito_campos": ["Peso", "Origem"],
                           "secoes": ["identificacao", "documento_controlado", "requisitos", "aprovacao"],
                           "aprovacao": ["Papel A", "Papel B"]},
        "doc-relatorio": {"titulo": "Relatório Y", "requisito_campos": ["Peso", "Origem"],
                          "secoes": ["identificacao", "documento_controlado", "requisitos", "riscos", "testes",
                                     "desvios", "aprovacao"], "aprovacao": ["Papel A"]},
        "doc-prontidao": {"titulo": "Prontidão Z", "secoes": ["documento_controlado", "prontidao"],
                          "itens": ["Item um", "Item dois"]},
    },
}

BASE = """<!-- spec-unico:v1 -->
# caso — Especificação

# Parte A — Requisitos
- **Impacto regulado:** sim — afeta dado controlado
- **Perfil regulado:** teste-sintetico
- **Sistema:** ERPX
- **Categoria de software:** 4
- **Requisitos confirmados por:** Área Q, 18/09/2026

- REQ-01: registrar lote
- REQ-02: bloquear lote vencido

### Atributos dos requisitos
| Requisito | Peso | Origem |
|---|---|---|
| REQ-01 | alta | reunião de 10/09 |
| REQ-02 | média | procedimento interno |

### Documentos controlados
| Documento | Código | Versão |
|---|---|---|
| doc-requisitos |  | 1 |
| doc-relatorio | QX-042 | 2 |
| doc-prontidao |  | 1 |

# Parte F — Riscos
| Risco | Requisito | Falha | Impacto | Probabilidade | Detecção | Classe | Mitigação | Teste |
|---|---|---|---|---|---|---|---|---|
| RISCO-01 | REQ-02 | lote vencido liberado | produto fora da validade | média | expedição | alto | bloqueio | TESTE-02 |

# Parte G — Testes e evidências
| Teste | Requisito | Categoria | Roteiro | Esperado | Resultado | Evidência | Nome e data |
|---|---|---|---|---|---|---|---|
| TESTE-01 | REQ-01 | integridade de dados | criar lote | gravado | aprovado | evid/t01.png | Ana, 20/09/2026 |
| TESTE-02 | REQ-02 | funcional | liberar vencido | bloqueado | aprovado | evid/t02.png | Ana, 21/09/2026 |

### Desvios
| Desvio | Teste | Descrição | Tratamento | Nome e data |
|---|---|---|---|---|

### Prontidão para operação
| Item | Situação | Onde está |
|---|---|---|
| Item um | existe | doc/um.md |
| Item dois | existe | doc/dois.md |

# Replanejamento
| Data | Item | O que mudou | Por quê | Quem aprovou |
|---|---|---|---|---|
| 22/09/2026 | REQ-02 | bloqueio passa a ser automático | pedido da área | Área Q |
"""

falhas = []


def check(nome, cond, detalhe=""):
    print(("  PASS " if cond else "  FAIL ") + nome + ("" if cond else f" — {detalhe}"))
    if not cond:
        falhas.append(nome)


def troca(velho, novo, texto=BASE):
    assert texto.count(velho) == 1, f"âncora não é única: {velho!r}"
    return texto.replace(velho, novo)


def caso(texto):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "spec.md")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(texto)
    return d, p


def main():
    pdir = tempfile.mkdtemp()
    with open(os.path.join(pdir, "compliance-profile-teste-sintetico.json"), "w", encoding="utf-8") as fh:
        json.dump(PERFIL, fh)
    original = regulado.PERFIS_DIR
    regulado.PERFIS_DIR = pdir
    try:
        print("(a) documento gerado")
        d, s = caso(BASE)
        out = os.path.join(d, "saida")
        ach, arqs = dr.gerar(s, "doc-requisitos", out)
        check("documento de requisitos sem lacuna gera md e docx", ach == [] and any(a.endswith(".md") for a in arqs)
              and any(a.endswith(".docx") for a in arqs), (ach, arqs))
        md = open(os.path.join(out, "doc-requisitos.md"), encoding="utf-8").read()
        check("todo REQ com os atributos do perfil", "| REQ-01 | registrar lote | alta | reunião de 10/09 |" in md
              and "| REQ-02 | bloquear lote vencido | média | procedimento interno |" in md, md)
        check("código vazio vira 'a preencher pela Qualidade'", "**Código:** a preencher pela Qualidade" in md, md)
        check("aprovação com os papéis do perfil", "| Papel A |" in md and "| Papel B |" in md)
        ach, _ = dr.gerar(s, "doc-relatorio", out)
        rel = open(os.path.join(out, "doc-relatorio.md"), encoding="utf-8").read()
        check("relatório com requisitos, riscos, testes, desvios e aprovação", ach == [] and "RISCO-01" in rel
              and "TESTE-02" in rel and "Nenhum desvio registrado" in rel and "QX-042" in rel, (ach, rel[:300]))
        ach, _ = dr.gerar(s, "doc-prontidao", out)
        check("prontidão com todos os itens passa", ach == [], ach)

        print("(b) lacunas reprovam e nada é gravado")
        casos = [
            ("atributo faltando", troca("| REQ-02 | média | procedimento interno |", "| REQ-02 |  | procedimento interno |"),
             "doc-requisitos", "REQ-02 sem 'peso'"),
            ("documento sem linha controlada", troca("| doc-requisitos |  | 1 |\n", ""), "doc-requisitos",
             "sem linha para 'doc-requisitos'"),
            ("teste reprovado sem desvio", troca("| bloqueado | aprovado |", "| bloqueado | reprovado |"),
             "doc-relatorio", "TESTE-02 reprovado sem desvio"),
            ("desvio sem tratamento", troca("| bloqueado | aprovado |", "| bloqueado | reprovado |").replace(
                "| Nome e data |\n|---|---|---|---|---|\n",
                "| Nome e data |\n|---|---|---|---|---|\n| DESVIO-01 | TESTE-02 | não bloqueou |  | Ana, 21/09/2026 |\n"),
             "doc-relatorio", "DESVIO-01 sem tratamento"),
            ("item de prontidão faltando", troca("| Item dois | existe | doc/dois.md |\n", ""), "doc-prontidao",
             "item 'Item dois'"),
            ("REQ com descrição vazia", troca("- REQ-02: bloquear lote vencido", "- REQ-02:"), "doc-requisitos",
             "REQ-02 sem descrição"),
            ("REQ repetido em documento sem seção de testes", troca("- REQ-02: bloquear lote vencido",
                                                                    "- REQ-02: bloquear lote vencido\n- REQ-02: outra coisa"),
             "doc-requisitos", "REQ-02 definido mais de uma vez"),
            ("resultado fora do padrão ('não aprovado')", troca("| bloqueado | aprovado |", "| bloqueado | não aprovado |"),
             "doc-relatorio", "use aprovado ou reprovado"),
            ("teste sem evidência entra no relatório como achado", troca("| aprovado | evid/t01.png |", "| aprovado | pendente |"),
             "doc-relatorio", "TESTE-01 com resultado e sem evidência"),
        ]
        for nome, texto, tipo, trecho in casos:
            dd, ss = caso(texto)
            o = os.path.join(dd, "saida")
            ach, arqs = dr.gerar(ss, tipo, o)
            check(f"{nome} reprova", any(trecho in a for a in ach), ach)
            check(f"{nome}: nada gravado", arqs == [] and not os.path.exists(o), arqs)

        dd, ss = caso(troca("- REQ-02: bloquear lote vencido", "- REQ-02:\n- REQ-03: terceiro requisito").replace(
            "| REQ-02 | média | procedimento interno |", "| REQ-02 | média | procedimento interno |\n| REQ-03 | baixa | área |"))
        md3, ach3 = dr.montar(ss, "doc-requisitos")
        check("REQ vazio não engole o seguinte: REQ-03 continua no documento com a descrição dele",
              "| REQ-03 | terceiro requisito | baixa | área |" in md3 and any("REQ-02 sem descrição" in a for a in ach3), (ach3, md3))
        dd, ss = caso(troca("- REQ-02: bloquear lote vencido", "1. **REQ-02** — bloquear lote vencido"))
        md4, _ = dr.montar(ss, "doc-requisitos")
        check("REQ em formato alternativo aceito pelo motor aparece no documento", "| REQ-02 | bloquear lote vencido |" in md4, md4)

        dd, ss = caso(BASE)
        bloqueio = os.path.join(dd, "saida-e-arquivo")
        with open(bloqueio, "w", encoding="utf-8") as fh:
            fh.write("um arquivo onde deveria ser a pasta")
        try:
            dr.gerar(ss, "doc-requisitos", bloqueio)
            check("falha de gravação vira recusa legível", False)
        except dr.Recusa as e:
            check("falha de gravação vira recusa legível", "não consegui gravar" in str(e), str(e))

        print("(c) rascunho")
        dd, ss = caso(troca("| REQ-02 | média | procedimento interno |", "| REQ-02 |  | procedimento interno |"))
        o = os.path.join(dd, "saida")
        ach, arqs = dr.gerar(ss, "doc-requisitos", o, rascunho=True)
        txt = open(os.path.join(o, "doc-requisitos.md"), encoding="utf-8").read()
        check("rascunho grava marcado e com PENDENTE", arqs and "RASCUNHO" in txt and "PENDENTE" in txt, txt[:200])

        print("(d) recusas")
        try:
            dr.gerar(s, "doc-inexistente", out)
            check("perfil sem o documento recusa", False)
        except dr.Recusa as e:
            check("perfil sem o documento recusa", "não emite o documento" in str(e), str(e))
        dd, ss = caso(troca("- **Impacto regulado:** sim — afeta dado controlado", "- **Impacto regulado:** não"))
        try:
            dr.gerar(ss, "doc-requisitos", os.path.join(dd, "o"))
            check("sem impacto regulado recusa", False)
        except (dr.Recusa, regulado.Recusa) as e:
            check("sem impacto regulado recusa", "não se aplica" in str(e), str(e))
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "regulado.py"), "documento", "doc-requisitos", s,
                            "--out-dir", os.path.join(d, "cli")], capture_output=True, text=True, encoding="utf-8",
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"))
        check("regulado.py documento delega (perfil real não tem o sintético: recusa legível)",
              r.returncode == 1 and "RECUSADO" in r.stdout, r.stdout + r.stderr)

        print("(e) mudança e versão")
        g = tempfile.mkdtemp()
        env = dict(os.environ, GIT_AUTHOR_NAME="Ana", GIT_AUTHOR_EMAIL="a@a", GIT_COMMITTER_NAME="Ana",
                   GIT_COMMITTER_EMAIL="a@a")
        subprocess.run(["git", "init", "-q", g], env=env)
        sp = os.path.join(g, "spec.md")
        for i, texto in enumerate((BASE, BASE + "\n<!-- v2 -->\n")):
            with open(sp, "w", encoding="utf-8") as fh:
                fh.write(texto)
            subprocess.run(["git", "-C", g, "add", "spec.md"], env=env)
            subprocess.run(["git", "-C", g, "commit", "-q", "-m", f"versão {i + 1}"], env=env)
        md, ach = ms.montar(sp)
        check("duas versões do git com data, autor e base", ach == [] and md.count("| Ana |") == 2
              and "versão 2" in md, (ach, md))
        check("o que mudou vem do Replanejamento", "| 22/09/2026 | REQ-02 | bloqueio passa a ser automático |" in md, md)
        with open(sp, "w", encoding="utf-8") as fh:
            fh.write(BASE.replace("| pedido da área | Área Q |", "| pedido da área |  |"))
        md, ach = ms.montar(sp)
        check("mudança sem quem aprovou reprova", any("sem quem aprovou" in a for a in ach), ach)
        d2, s2 = caso(BASE)
        md, ach = ms.montar(s2)
        check("fora do git reprova (sem histórico)", any("git" in a or "versão" in a for a in ach), ach)

        print("(f) neutralidade")
        with open(os.path.join(ROOT, "tools", "agnostic-denylist.txt"), encoding="utf-8") as fh:
            termos = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
        textos = [open(os.path.join(ROOT, "tools", n), encoding="utf-8").read()
                  for n in ("documento_regulado.py", "mudancas_spec.py")]
        achados = [t for t in termos if any(re.search(t, x, re.I) for x in textos)]
        check("motores sem órgão, norma ou termo de domínio", achados == [], achados)
        check("motor não cita documento de domínio (ERU)", not any(re.search(r"\bERU\b", x) for x in textos))
    finally:
        regulado.PERFIS_DIR = original
    print(f"\nRESULTADO: {'FAIL' if falhas else 'PASS'} ({len(falhas)} falha(s))")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
