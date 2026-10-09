#!/usr/bin/env python3
"""Canário do kit regulado (ADR-119) — `tools/regulado.py`.

Prova, com um perfil SINTÉTICO próprio (valores literais aqui, nunca lidos do motor):
  (a) VERDE — especificação completa (3 requisitos, 2 riscos, 4 testes) passa em `verificar`;
  (b) SABOTAGENS — cada regra, quebrada isoladamente, reprova com o achado dela;
  (c) EXCEÇÕES LEGÍTIMAS — não reprovam (inclusive o modo `--planejamento`);
  (d) MATRIZ — requisito -> risco -> teste -> evidência, com a lacuna de cada linha;
  (e) KIT — peças pelo perfil e categoria; sem registro de impacto e perfil, recusa;
  (f) NEUTRALIDADE — o motor não contém órgão, norma ou sigla de domínio;
  (g) PERFIL REAL — perfis do repositório carregam; no farma, a categoria 3 NÃO traz a especificação
      de configuração e a 4 traz (critério 1 do plano B3).

Uso: python tools/test_regulado.py   (exit 0 PASS; 1 FAIL)
"""
import json
import os
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import regulado  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

PERFIL = {
    "profile": "teste-sintetico",
    "normas_revogadas": [{"padrao": r"NORMA\s*9/1999", "substituida_por": "NORMA 1/2020"}],
    "categorias_software": {"kit_comum": ["TAP", "especificacao"], "3": ["peca-c3"],
                            "4": ["peca-c4a", "peca-c4b"], "5": ["peca-c5"]},
    "categoria_padrao_por_sistema": {"ERPX": "4"},
    "testes_obrigatorios_com_impacto": ["integridade de dados", "trilha de auditoria"],
}

BASE = """<!-- spec-unico:v1 -->
# caso — Especificação

# Parte A — Requisitos
- **Impacto regulado:** sim — afeta dado de qualidade
- **Perfil regulado:** teste-sintetico
- **Sistema:** ERPX módulo MM
- **Categoria de software:** 4
- **Requisitos confirmados por:** Área de Qualidade, 18/09/2026

- REQ-01: registrar lote com validade
- REQ-02: bloquear lote vencido
- REQ-03: registrar quem alterou a validade

# Parte B — Aceite
| 1 | ok | ok | ☐ |

# Parte F — Riscos
| Risco | Requisito | Falha | Impacto | Probabilidade | Detecção | Classe | Mitigação | Teste |
|---|---|---|---|---|---|---|---|---|
| RISCO-01 | REQ-02 | lote vencido liberado | produto fora da validade | média | só na expedição | alto | bloqueio automático | TESTE-02 |
| RISCO-02 | REQ-01 | validade digitada errada | etiqueta errada | alta | conferência | médio | dupla conferência | TESTE-01 |

# Parte G — Testes e evidências
| Teste | Requisito | Categoria | Roteiro | Esperado | Resultado | Evidência | Nome e data |
|---|---|---|---|---|---|---|---|
| TESTE-01 | REQ-01 | integridade de dados | criar lote | validade gravada | aprovado | evid/t01.png | Ana Lima, 20/09/2026 |
| TESTE-02 | REQ-02 | funcional \\| bloqueio | tentar liberar | bloqueado | aprovado | evid/t02.xlsx | Ana Lima, 21/09/2026 |
| TESTE-03 | REQ-03 | trilha de auditoria | alterar validade | alteração registrada | aprovado | evid/t03.png | Ana Lima, 21/09/2026 |
| TESTE-04 | REQ-01, REQ-03 | controle de acesso | usuário sem perfil tenta | negado | aprovado | evid/t04.png | Ana Lima, 22/09/2026 |
"""

falhas = []


def check(nome, cond, detalhe=""):
    print(("  PASS " if cond else "  FAIL ") + nome + ("" if cond else f" — {detalhe}"))
    if not cond:
        falhas.append(nome)


def rodar(texto, fn="verificar", **kw):
    with tempfile.TemporaryDirectory() as d:
        spec = os.path.join(d, "spec.md")
        with open(spec, "w", encoding="utf-8") as fh:
            fh.write(texto)
        try:
            return getattr(regulado, fn)(spec, **kw)
        except regulado.Recusa as e:
            return f"RECUSA: {e}"


def troca(velho, novo, texto=BASE):
    assert texto.count(velho) == 1, f"âncora do teste não é única: {velho!r}"
    return texto.replace(velho, novo)


def main():
    pdir = tempfile.mkdtemp()
    with open(os.path.join(pdir, "compliance-profile-teste-sintetico.json"), "w", encoding="utf-8") as fh:
        json.dump(PERFIL, fh)
    original = regulado.PERFIS_DIR
    regulado.PERFIS_DIR = pdir
    try:
        print("(a) verde")
        ach = rodar(BASE)
        check("especificação completa passa", ach == [], ach)

        print("(b) sabotagens — cada uma tem de reprovar com o achado dela")
        t01 = "| aprovado | evid/t01.png | Ana Lima, 20/09/2026 |"
        casos = [
            ("requisito sem teste", troca("| TESTE-03 | REQ-03 |", "| TESTE-03 | REQ-02 |").replace(
                "| REQ-01, REQ-03 |", "| REQ-01 |"), r"REQ-03 sem teste"),
            ("risco alto sem mitigação", troca("| alto | bloqueio automático |", "| alto | pendente |"),
             r"RISCO-01 \(alto\) sem mitigação"),
            ("risco alto sem teste", troca("| bloqueio automático | TESTE-02 |", "| bloqueio automático | - |"),
             r"RISCO-01 \(alto\) sem teste"),
            ("classe fora da escala escapa do risco alto", troca("| alto | bloqueio", "| crítico | bloqueio"),
             r"RISCO-01 com classe 'crítico'"),
            ("teste sem resultado", troca(t01, "| pendente | pendente | pendente |"), r"TESTE-01 sem resultado"),
            ("resultado sem evidência", troca("| evid/t01.png |", "| pendente |"),
             r"TESTE-01 com resultado e sem evidência"),
            ("execução sem data", troca("Ana Lima, 20/09/2026", "Ana Lima"),
             r"TESTE-01 com resultado sem nome e data"),
            ("execução sem nome", troca("Ana Lima, 20/09/2026", "20/09/2026"),
             r"TESTE-01 com resultado sem nome e data"),
            ("execução com data impossível", troca("Ana Lima, 20/09/2026", "Ana Lima, 31/02/2026"),
             r"TESTE-01 com resultado sem nome e data"),
            ("confirmação dos requisitos sem nome e data",
             troca("Área de Qualidade, 18/09/2026", "Área de Qualidade"), r"confirmação dos requisitos sem nome e data"),
            ("norma revogada citada", troca("- REQ-02: bloquear lote vencido",
                                            "- REQ-02: bloquear lote vencido conforme NORMA 9/1999"),
             r"cita norma revogada \(usar NORMA 1/2020\)"),
            ("impacto não registrado", troca("- **Impacto regulado:** sim — afeta dado de qualidade\n", ""),
             r"impacto regulado não registrado"),
            ("impacto placeholder", troca("sim — afeta dado de qualidade", "sim | não — <por quê>"),
             r"impacto regulado não registrado"),
            ("perfil não registrado", troca("- **Perfil regulado:** teste-sintetico\n", ""),
             r"perfil regulado não registrado"),
            ("perfil inexistente", troca("teste-sintetico\n", "nao-existe\n"), r"perfil 'nao-existe' sem arquivo"),
            ("perfil como caminho", troca("teste-sintetico\n", "../../etc\n"), r"perfil regulado não registrado"),
            ("impacto sem perfil", troca("teste-sintetico\n", "nenhum\n"),
             r"impacto regulado declarado sem perfil regulado"),
            ("categoria fora do perfil", troca("**Categoria de software:** 4", "**Categoria de software:** 2"),
             r"categoria de software '2' ausente ou fora do perfil"),
            ("sistema com categoria ≠ padrão sem registro",
             troca("**Categoria de software:** 4", "**Categoria de software:** 5"),
             r"sistema ERPX com categoria 5 \(padrão 4\) sem registro"),
            ("categoria de teste obrigatória ausente", troca("| trilha de auditoria |", "| funcional |"),
             r"categoria de teste obrigatória ausente: trilha de auditoria"),
            ("risco aponta requisito inexistente", troca("| RISCO-02 | REQ-01 |", "| RISCO-02 | REQ-09 |"),
             r"RISCO-02 aponta para REQ-09"),
            ("risco aponta teste inexistente", troca("| bloqueio automático | TESTE-02 |",
                                                     "| bloqueio automático | TESTE-07 |"),
             r"RISCO-01 aponta para TESTE-07"),
            ("tabela com colunas a menos", troca("| Ana Lima, 22/09/2026 |", "|"), r"TESTE-04: 7 colunas"),
            ("tabela com colunas a mais", troca("| Ana Lima, 22/09/2026 |", "| Ana Lima, 22/09/2026 | x |"),
             r"TESTE-04: 9 colunas"),
            # rodada 1 do QA isolado (26/09/2026): formas que sumiam em silêncio
            ("requisito em formato desconhecido é acusado",
             troca("- REQ-02: bloquear lote vencido", "- REQ-02: bloquear lote vencido\n> REQ-04 é o registro de lote"),
             r"REQ-04 citado na Parte A sem linha de definição"),
            ("requisito com '*' sem teste reprova", troca("- REQ-02: bloquear lote vencido",
                                                        "- REQ-02: bloquear lote vencido\n* REQ-04: rotular lote"),
             r"REQ-04 sem teste"),
            ("requisito em negrito sem teste reprova", troca("- REQ-02: bloquear lote vencido",
                                                            "- REQ-02: bloquear lote vencido\n- **REQ-04:** rotular"),
             r"REQ-04 sem teste"),
            ("requisito definido duas vezes", troca("- REQ-02: bloquear lote vencido",
                                                    "- REQ-02: bloquear lote vencido\n- REQ-02: outro texto"),
             r"REQ-02 definido mais de uma vez"),
            ("Parte F sem risco", re.sub(r"(?m)^\| RISCO-.*\n", "", BASE), r"Parte F sem risco registrado"),
            ("Parte G sem teste", re.sub(r"(?m)^\| TESTE-.*\n", "", BASE), r"Parte G sem teste registrado"),
            ("nenhum requisito na Parte A", re.sub(r"(?m)^- REQ-.*\n", "", BASE), r"nenhum requisito numerado"),
            ("campo duplicado", troca("- **Sistema:** ERPX módulo MM", "- **Sistema:** <sistema>\n"
                                      "- **Sistema:** ERPX módulo MM"), r"campo \*\*Sistema:\*\* aparece mais de uma vez"),
        ]
        for nome, texto, esperado in casos:
            ach = rodar(texto)
            check(nome, isinstance(ach, list) and any(re.search(esperado, a) for a in ach), ach)

        print("(c) exceções legítimas — não podem reprovar")
        ok7 = troca("**Categoria de software:** 4", "**Categoria de software:** 5\n"
                    "- **Categoria decidida por:** Ana Lima, 19/09/2026 — customização pesada")
        check("categoria ≠ padrão com registro datado passa", rodar(ok7) == [], rodar(ok7))
        ok5 = troca("- REQ-02: bloquear lote vencido", "- REQ-02: bloquear lote vencido (a NORMA 9/1999 foi revogada)")
        check("norma revogada citada como revogada passa", rodar(ok5) == [], rodar(ok5))
        nao = troca("sim — afeta dado de qualidade", "não — relatório interno").replace("teste-sintetico\n", "nenhum\n")
        check("sem impacto regulado: kit regulado não se aplica", rodar(nao) == [], rodar(nao))
        pend = troca(t01, "| pendente | pendente | pendente |")
        check("--planejamento aceita teste não executado", rodar(pend, planejamento=True) == [],
              rodar(pend, planejamento=True))
        sem_conf = troca("Área de Qualidade, 18/09/2026", "<pendente>")
        check("--planejamento aceita confirmação ainda não dada", rodar(sem_conf, planejamento=True) == [],
              rodar(sem_conf, planejamento=True))
        check("--planejamento continua cobrando rastreabilidade",
              any("RISCO-01 (alto) sem mitigação" in a for a in
                  rodar(troca("| alto | bloqueio automático |", "| alto | - |"), planejamento=True)))

        print("(d) matriz — 3 requisitos, 2 riscos, 4 testes")
        m = rodar(BASE, "matriz")
        check("REQ-02 -> RISCO-01 -> TESTE-02 -> evid/t02.xlsx",
              re.search(r"\| REQ-02 \| RISCO-01 \| TESTE-02 \| aprovado \| evid/t02\.xlsx \|  \|", m), m)
        check("REQ-03 ligado a TESTE-03 e TESTE-04", re.search(r"\| REQ-03 \| — \| TESTE-03, TESTE-04 \|", m), m)
        check("3 linhas de requisito", len(re.findall(r"^\| REQ-", m, re.M)) == 3, m)
        pend2 = troca("| aprovado | evid/t02.xlsx | Ana Lima, 21/09/2026 |", "| pendente | pendente | pendente |")
        check("lacuna 'não executado' aparece",
              re.search(r"\| REQ-02 \|.*não executado \|", rodar(pend2, "matriz")), rodar(pend2, "matriz"))
        check("requisito com 1 de 2 testes executado não tem lacuna",
              re.search(r"\| REQ-01 \|.*\|  \|$", rodar(pend, "matriz"), re.M), rodar(pend, "matriz"))
        sem = troca("| TESTE-03 | REQ-03 |", "| TESTE-03 | REQ-02 |").replace("| REQ-01, REQ-03 |", "| REQ-01 |")
        check("lacuna 'sem teste' aparece", re.search(r"\| REQ-03 \|.*sem teste \|", rodar(sem, "matriz")))

        print("(e) kit")
        check("categoria 4 com impacto = comum + peças da 4",
              rodar(BASE, "kit") == ["TAP", "especificacao", "peca-c4a", "peca-c4b"], rodar(BASE, "kit"))
        check("sem perfil = kit comum embutido",
              rodar(nao, "kit") == ["TAP", "especificacao", "HANDOFF", "glossario", "cronograma"], rodar(nao, "kit"))
        nao_perfil = troca("sim — afeta dado de qualidade", "não — relatório interno")
        check("sem impacto, com perfil = só o kit comum do perfil",
              rodar(nao_perfil, "kit") == ["TAP", "especificacao"], rodar(nao_perfil, "kit"))
        sem_reg = troca("- **Impacto regulado:** sim — afeta dado de qualidade\n", "")
        check("sem registro de impacto, o kit é recusado",
              str(rodar(sem_reg, "kit")).startswith("RECUSA"), rodar(sem_reg, "kit"))
        print("(e2) perfil mínimo — sem testes obrigatórios nem normas revogadas")
        with open(os.path.join(pdir, "compliance-profile-minimo.json"), "w", encoding="utf-8") as fh:
            json.dump({"profile": "minimo", "categorias_software": {"kit_comum": ["TAP"], "4": ["x"]}}, fh)
        vazio = ("<!-- spec-unico:v1 -->\n# c\n\n# Parte A — Requisitos\n- **Impacto regulado:** sim\n"
                 "- **Perfil regulado:** minimo\n- **Categoria de software:** 4\n"
                 "- **Requisitos confirmados por:** Ana, 01/09/2026\n\n# Parte F — Riscos\n\n# Parte G — Testes e evidências\n")
        ach = rodar(vazio)
        check("sem requisitos, riscos e testes não passa com perfil mínimo",
              {"nenhum requisito numerado na Parte A (formato `- REQ-01: ...`)", "Parte F sem risco registrado",
               "Parte G sem teste registrado"} <= set(ach), ach)

        print("(i) camada privada da empresa (ADR-128)")
        raiz = tempfile.mkdtemp()
        with open(os.path.join(raiz, "conhecimento.json"), "w", encoding="utf-8") as fh:
            json.dump({}, fh)
        os.makedirs(os.path.join(raiz, "empresas", "acme", "perfis"))
        with open(os.path.join(raiz, "empresas", "acme", "perfis", "compliance-profile-teste-sintetico.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"profile": "teste-sintetico", "testes_obrigatorios_com_impacto": ["procedimento interno X"],
                       "categorias_software": {"4": ["peca-interna"]}}, fh)
        os.makedirs(os.path.join(raiz, "empresas", "beta"))
        raiz_orig = regulado.RAIZ_CONHECIMENTO
        regulado.RAIZ_CONHECIMENTO = raiz
        try:
            com = troca("- **Sistema:**", "- **Empresa:** acme\n- **Sistema:**")
            ach = rodar(com)
            check("camada privada soma teste obrigatório da empresa",
                  "categoria de teste obrigatória ausente: procedimento interno X" in ach, ach)
            check("camada privada soma peça ao kit, sem repetir as públicas",
                  rodar(com, "kit") == ["TAP", "especificacao", "peca-c4a", "peca-c4b", "peca-interna"], rodar(com, "kit"))
            check("sem **Empresa:** a camada privada não é lida", rodar(BASE) == [], rodar(BASE))
            ach = rodar(com.replace("**Empresa:** acme", "**Empresa:** beta"))
            check("empresa sem camada para o perfil = só o perfil público", ach == [], ach)
            ach = rodar(com.replace("**Empresa:** acme", "**Empresa:** ausente"))
            check("empresa declarada sem biblioteca na máquina reprova",
                  any("não está nesta máquina" in a for a in ach), ach)
            check("... e o kit é recusado", str(rodar(com.replace("**Empresa:** acme", "**Empresa:** ausente"), "kit"))
                  .startswith("RECUSA"))
            with open(os.path.join(raiz, "empresas", "beta", "compliance-profile-x.json"), "w") as fh:
                fh.write("{}")
            os.makedirs(os.path.join(raiz, "empresas", "beta", "perfis"))
            with open(os.path.join(raiz, "empresas", "beta", "perfis", "compliance-profile-teste-sintetico.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"profile": "outro-perfil"}, fh)
            ach = rodar(com.replace("**Empresa:** acme", "**Empresa:** beta"))
            check("camada de outro perfil reprova", any("não de 'teste-sintetico'" in a for a in ach), ach)
            base = {"a": {"b": [1, {"c": 2}]}, "l": [{"padrao": "x"}], "s": "pub"}
            foto = json.dumps(base, sort_keys=True)
            soma, conf = regulado._somar(base, {"a": {"b": [3], "d": 4}, "l": [{"padrao": "y"}, {"padrao": "x"}],
                                                "s": "pub", "n": "novo"})
            check("soma não altera o perfil público (aninhado)", json.dumps(base, sort_keys=True) == foto, base)
            check("soma une listas sem repetir e acrescenta chave nova, sem conflito",
                  soma == {"a": {"b": [1, {"c": 2}, 3], "d": 4}, "l": [{"padrao": "x"}, {"padrao": "y"}], "s": "pub",
                           "n": "novo"} and conf == [], (soma, conf))
            for extra, trecho in (({"l": None}, "l nulo"), ({"a": {"b": None}}, "a.b nulo"), ({"s": "priv"}, "s ('pub'"),
                                  ({"l": {"x": 1}}, "l ("), ({"a": ["lista"]}, "a (")):
                soma, conf = regulado._somar(base, extra)
                check(f"camada não enfraquece o público: {extra} vira conflito e o público fica",
                      any(trecho in c for c in conf) and json.dumps(soma, sort_keys=True) == foto, (soma, conf))
            meta = {"_doc": "p", "note": "p", "orgao": "p"}
            soma, conf = regulado._somar(meta, {"_doc": "c", "note": "c", "orgao": "c", "_x": ["peça"]})
            check("metadados divergentes (_doc, note, orgao, _x) ficam fora da soma, sem conflito",
                  conf == [] and soma == meta, (soma, conf))
            with open(os.path.join(raiz, "empresas", "acme", "perfis", "compliance-profile-teste-sintetico.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"profile": "teste-sintetico", "testes_obrigatorios_com_impacto": None}, fh)
            ach = rodar(com)
            check("camada com testes obrigatórios nulos reprova (não apaga a exigência pública)",
                  any("só pode acrescentar" in a for a in ach), ach)
            with tempfile.TemporaryDirectory() as dd:
                sp = os.path.join(dd, "spec.md")
                with open(sp, "w", encoding="utf-8") as fh:
                    fh.write(com)
                publico = regulado.carregar(sp)["perfil"]  # com a camada nula já gravada
            check("após conflito, o perfil carregado mantém a exigência pública",
                  bool(publico.get("testes_obrigatorios_com_impacto")), publico.get("testes_obrigatorios_com_impacto"))
            with open(os.path.join(raiz, "empresas", "acme", "perfis", "compliance-profile-teste-sintetico.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"profile": "Teste-Sintetico", "note": "camada da empresa", "_doc": "procedimentos internos",
                           "testes_obrigatorios_com_impacto": ["procedimento interno X"]}, fh)
            ach = rodar(com)
            check("metadados da camada (_doc, note, profile em maiúsculas) não viram conflito",
                  not any("só pode acrescentar" in a for a in ach)
                  and "categoria de teste obrigatória ausente: procedimento interno X" in ach, ach)
            with open(os.path.join(raiz, "empresas", "acme", "perfis", "compliance-profile-teste-sintetico.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"profile": 5}, fh)
            ach = rodar(com)
            check("camada com 'profile' não textual reprova sem traceback", any("não de 'teste-sintetico'" in a for a in ach), ach)
            with open(os.path.join(raiz, "empresas", "acme", "perfis", "compliance-profile-teste-sintetico.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"profile": "teste-sintetico", "testes_obrigatorios_com_impacto": ["procedimento interno X"],
                           "categorias_software": {"4": ["peca-interna"]}}, fh)
            for valor in ("Acme Ltda", "café", "acme|beta", "<acme", "acme>", "<a> | outra", "acme - filial"):
                ach = rodar(com.replace("**Empresa:** acme", f"**Empresa:** {valor}"))
                check(f"empresa fora do formato ('{valor}') reprova, não some",
                      any("fora do formato da biblioteca" in a for a in ach), ach)
            ach = rodar(com.replace("**Empresa:** acme", "**Empresa:** acme — matriz"))
            check("travessão separa comentário: 'acme — matriz' é a empresa acme",
                  "categoria de teste obrigatória ausente: procedimento interno X" in ach, ach)
            import contextlib
            import io
            with tempfile.TemporaryDirectory() as dd:
                sp = os.path.join(dd, "spec.md")
                with open(sp, "w", encoding="utf-8") as fh:
                    fh.write(com)
                saida = io.StringIO()
                with contextlib.redirect_stdout(saida):
                    regulado.main(["regulado.py", "kit", sp])
            check("a saída diz qual camada privada foi usada", "camada privada:" in saida.getvalue()
                  and "(empresa acme)" in saida.getvalue(), saida.getvalue())
            modelo = open(os.path.join(ROOT, "docs", "specs", "_template-spec-unico", "spec.md"), encoding="utf-8").read()
            linha_modelo = next(ln for ln in modelo.splitlines() if ln.lstrip("- ").startswith("**Empresa:**"))
            ach = rodar(com.replace("- **Empresa:** acme", linha_modelo))
            check("placeholder do modelo em **Empresa:** = não declarada, sem achado", ach == [], ach)
            ach = rodar(com.replace("- **Empresa:** acme", "- **Empresa:**"))
            check("**Empresa:** vazia não lê a linha do campo seguinte", ach == [], ach)
            check("campo vazio devolve vazio, não o campo seguinte",
                  regulado._campo("- **Empresa:**\n- **Sistema:** X", "Empresa") == "")
            with open(os.path.join(raiz, "empresas", "beta", "perfis", "compliance-profile-teste-sintetico.json"), "w",
                      encoding="utf-8") as fh:
                json.dump(["não", "é", "objeto"], fh)
            ach = rodar(com.replace("**Empresa:** acme", "**Empresa:** beta"))
            check("camada que não é objeto JSON vira achado, não exceção",
                  any("não é um objeto JSON" in a for a in ach), ach)
        finally:
            regulado.RAIZ_CONHECIMENTO = raiz_orig
    finally:
        regulado.PERFIS_DIR = original

    print("(f) neutralidade do motor")
    with open(os.path.join(ROOT, "tools", "agnostic-denylist.txt"), encoding="utf-8") as fh:
        termos = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    with open(os.path.join(ROOT, "tools", "regulado.py"), encoding="utf-8") as fh:
        motor = fh.read()
    achados = [t for t in termos + [r"\bRDC\b", r"\bIN\s+n", r"\bBPF\b"] if re.search(t, motor)]
    check("regulado.py sem órgão, norma ou sigla de domínio", achados == [], achados)

    print("(g) perfis reais do repositório")
    for f in sorted(os.listdir(regulado.PERFIS_DIR)):
        if not (f.startswith("compliance-profile-") and f.endswith(".json")):
            continue
        with open(os.path.join(regulado.PERFIS_DIR, f), encoding="utf-8") as fh:
            p = json.load(fh)
        if "categorias_software" not in p:
            continue  # perfil anterior ao kit (ADR-043), sem peças por categoria
        cats = p["categorias_software"]
        check(f"{f}: kit_comum e ao menos uma categoria", "kit_comum" in cats and len(cats) > 2, list(cats))
        for nr in p.get("normas_revogadas", []):
            try:
                re.compile(nr["padrao"])
                ok = bool(nr.get("substituida_por"))
            except re.error:
                ok = False
            check(f"{f}: regex de norma revogada válida e com substituta", ok, nr)
    farma = os.path.join(regulado.PERFIS_DIR, "compliance-profile-farma-anvisa.json")
    if os.path.isfile(farma):
        c = json.load(open(farma, encoding="utf-8"))["categorias_software"]
        check("farma: categoria 3 sem especificação de configuração/funcional",
              not any(re.search(r"especificacao-(de-configuracao|funcional)", x) for x in c["3"]), c["3"])
        check("farma: categoria 4 com especificação de configuração",
              "especificacao-de-configuracao" in c["4"], c["4"])

    anp = os.path.join(regulado.PERFIS_DIR, "compliance-profile-anp-combustiveis.json")
    if os.path.isfile(anp):
        p = json.load(open(anp, encoding="utf-8"))
        pecas = regulado.pecas_do_perfil(p)
        check("anp: sem peça de validação de sistema importada do farma (D3)",
              not any(re.search(r"(?i)^eru$|validacao|matriz|roteiro-de-testes", x) for x in pecas), pecas)
        check("anp: trilha de auditoria não exigida", p["controls"]["audit_trail"]["required"] is False)

    print("(h) mapa peça -> norma ao lado do perfil")
    for f in sorted(os.listdir(regulado.PERFIS_DIR)):
        if f.startswith("compliance-profile-") and f.endswith(".json"):
            p = os.path.join(regulado.PERFIS_DIR, f)
            if "categorias_software" in json.load(open(p, encoding="utf-8")):
                ach = regulado.verificar_mapa(p)
                check(f"{f}: toda peça tem artigo no mapa", ach == [], ach)
    if os.path.isfile(farma):
        mapa_real = open(os.path.join(regulado.PERFIS_DIR, "farma-anvisa-mapa-normas.md"), encoding="utf-8").read()
        d = tempfile.mkdtemp()
        shutil.copy(farma, d)
        alvo = os.path.join(d, os.path.basename(farma))

        def mapa_com(texto):
            with open(os.path.join(d, "farma-anvisa-mapa-normas.md"), "w", encoding="utf-8") as fh:
                fh.write(texto)
            return regulado.verificar_mapa(alvo)

        def sem_linhas(peca):
            return "\n".join(ln for ln in mapa_real.splitlines() if not ln.startswith(f"| `{peca}` |"))

        sabot = [
            ("peça sem linha", sem_linhas("inventario"), "peça do perfil sem linha no mapa: inventario"),
            ("item de documento sem linha", sem_linhas("Treinamento"), "sem linha no mapa: Treinamento"),
            ("marca inválida", mapa_real.replace(
                "disponibilizada sempre que solicitado.\" | CONFIRMADO |",
                "disponibilizada sempre que solicitado.\" | OK |", 1), "inventario: marca 'OK'"),
            ("citada sem artigo", mapa_real.replace("| `inventario` | IN134 | art. 18 |", "| `inventario` | IN134 | — |", 1),
             "inventario: marca CONFIRMADO sem norma e artigo"),
            ("linha de peça inexistente", mapa_real + "\n| `peca-fantasma` | — | — | x | NÃO SE APLICA |\n",
             "peça que o perfil não tem: peca-fantasma"),
            ("barra vertical sem escape no trecho", mapa_real.replace("| `inventario` | IN134 | art. 18 | \"Um",
                                                                     "| `inventario` | IN134 | art. 18 | \"a | b\" \"Um", 1),
             "inventario: 6 colunas"),
        ]
        for nome, texto, trecho in sabot:
            ach = mapa_com(texto)
            check(f"mapa: {nome} reprova", any(trecho in a for a in ach), ach)
        with open(os.path.join(d, "farma-anvisa-mapa-normas.md"), "w", encoding="cp1252", errors="replace") as fh:
            fh.write(mapa_real)
        ach = regulado.verificar_mapa(alvo)
        check("mapa fora de UTF-8 vira achado, não exceção", any("não está em UTF-8" in a for a in ach), ach)
        os.remove(os.path.join(d, "farma-anvisa-mapa-normas.md"))
        ach = regulado.verificar_mapa(alvo)
        check("mapa ausente reprova", any("mapa peça -> norma ausente" in a for a in ach), ach)

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({len(falhas)})" if falhas else "PASS")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
