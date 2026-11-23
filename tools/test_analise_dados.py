#!/usr/bin/env python3
"""Canário da fiação da análise acompanhada (ADR-134).

Prova que a análise acompanhada não é só prosa:
 (a) a skill `.agent/skills/analise-dados/SKILL.md` existe, com gatilho (dado, indicador, métrica, modelo),
     exclusão (tarefa sem dado), padrão acompanhado e ordem de autônomo na `description`;
 (b) o corpo da skill traz as 7 classes de decisão que param o acompanhado e os 7 itens do painel mínimo;
 (c) a regra de uma linha da fonte global `.claude/global/CLAUDE-global.md` aponta a skill e o padrão acompanhado;
 (d) a tabela de sub-modos do discovery tem a linha `produto-de-dados.md` e o companion existe;
 (e) a skill entra no pacote web premium (LATERAL de tools/web_export.py);
 (f) a seção 3 da skill aponta `tools/conferir_invariante.py`, que existe, e o `qa-critic` aponta a seção 8 da skill e a
     ferramenta (B2 do plano).
Autoteste: cada verificação roda também sobre uma cópia sabotada e tem de reprovar (canário cego reprova aqui).

Uso: python tools/test_analise_dados.py   (exit 0 PASS; 1 se falha)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, ".agent", "skills", "analise-dados", "SKILL.md")
GLOBAL = os.path.join(ROOT, ".claude", "global", "CLAUDE-global.md")
DISC = os.path.join(ROOT, ".agent", "skills", "discovery", "SKILL.md")
COMPANION = os.path.join(ROOT, ".agent", "skills", "discovery", "produto-de-dados.md")
QA = os.path.join(ROOT, ".agent", "skills", "qa-critic", "SKILL.md")
FERRAMENTA = os.path.join(ROOT, "tools", "conferir_invariante.py")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GATILHO = [r"toda tarefa que toque dado, indicador, m[ée]trica ou modelo",
           r"an[áa]lise explorat[óo]ria, confer[êe]ncia de n[úu]mero, regra de indicador",
           r"N[ÃA]O ativar em tarefa sem dado",
           r"ACOMPANHADO", r"AUT[ÔO]NOMO", r"dali em diante na sess[ãa]o"]
CLASSES = ["Escopo e população", "Métrica e janela", "Exclusão e outlier", "Dado faltante",
           "Método e modelo", "Aceite", "Número publicado"]
PAINEL = [r"modo vigente e origem", r"dado e procedimento", r"problemas de dados", r"decis[õo]es abertas",
          r"invariantes conferidas", r"confian[çc]a \(CONFIRMADO", r"o que preciso de voc[êe]"]


def _ler(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _description(txt):
    m = re.search(r'^description:\s*"(.*)"\s*$', txt, re.M)
    return m.group(1) if m else ""


def checar_skill(txt):
    fails = []
    desc = _description(txt)
    if not desc:
        fails.append("skill sem description")
    for rx in GATILHO:
        if not re.search(rx, desc, re.I if rx not in ("ACOMPANHADO",) else 0):
            fails.append(f"description sem gatilho/regra: {rx}")
    corpo = txt.split("## 4. Classes de decisão", 1)
    secao4 = corpo[1].split("\n## ", 1)[0] if len(corpo) == 2 else ""
    if not secao4:
        fails.append("skill sem a seção '## 4. Classes de decisão'")
    for c in CLASSES:
        if not re.search(r"^\|\s*" + re.escape(c) + r"\s*\|", secao4, re.M):
            fails.append(f"classe de decisão ausente na tabela da seção 4: {c}")
    ciclo = txt.split("## 2. Ciclo por fase", 1)
    secao2 = ciclo[1].split("\n## ", 1)[0] if len(ciclo) == 2 else ""
    if not secao2:
        fails.append("skill sem a seção '## 2. Ciclo por fase'")
    for rx in PAINEL:
        if not re.search(rx, secao2, re.I):
            fails.append(f"item do painel mínimo ausente na seção 2: {rx}")
    return fails


# Limite declarado: confere a FORMA textual da regra (gatilho, comando de carregar, padrão, duração), não o
# comportamento do modelo; a ativação é provada pelo teste 3/3 e 0/3 (ADR-134).
REGRA_GLOBAL = [
    (r"[Tt]arefa que toque dado, indicador, m[ée]trica ou modelo", "gatilho da regra global"),
    (r"(?<![Nn]ão )carregar a skill `analise-dados`", "comando de carregar a skill"),
    (r"modo acompanhado at[ée] a primeira ordem de aut[ôo]nomo", "padrão acompanhado até ordem de autônomo"),
    (r"dali em diante na sess[ãa]o", "duração da ordem de autônomo"),
]


def checar_global(txt):
    linhas = [ln for ln in txt.splitlines() if "`analise-dados`" in ln]
    if not linhas:
        return ["regra global sem a skill `analise-dados`"]
    ln = " ".join(linhas)
    return [f"regra global sem: {nome}" for rx, nome in REGRA_GLOBAL if not re.search(rx, ln)]


def checar_discovery(txt, companion_existe):
    fails = []
    if not re.search(r"^\|\s*\*\*Produto de dados\*\*.*`produto-de-dados\.md`", txt, re.M):
        fails.append("tabela de sub-modos do discovery sem a linha `produto-de-dados.md`")
    if not companion_existe:
        fails.append("companion .agent/skills/discovery/produto-de-dados.md ausente")
    return fails


def checar_conferencia(skill, qa, ferramenta_existe):
    fails = []
    sec3 = skill.split("## 3. Invariante por operação", 1)
    sec3 = sec3[1].split("\n## ", 1)[0] if len(sec3) == 2 else ""
    if "tools/conferir_invariante.py" not in sec3:
        fails.append("seção 3 da skill sem `tools/conferir_invariante.py`")
    if not ferramenta_existe:
        fails.append("tools/conferir_invariante.py ausente")
    linha = " ".join(ln for ln in qa.split("\n\n") if "Análise de dados" in ln)
    if not linha:
        fails.append("qa-critic sem o item 'Análise de dados'")
    elif "seção 8" not in linha or "`analise-dados`" not in linha or "conferir_invariante.py" not in linha:
        fails.append("item 'Análise de dados' do qa-critic sem a seção 8 da skill ou sem a ferramenta")
    return fails


def checar_web(lateral):
    return [] if "analise-dados" in lateral else ["pacote web: analise-dados fora de LATERAL em tools/web_export.py"]


def autoteste(skill, glob, disc, qa):
    """Cada sabotagem tem de reprovar; se passar, o canário é cego."""
    cegos = []
    sab = [
        ("skill sem 'Número publicado'", lambda: checar_skill(skill.replace("| Número publicado |", "| X |"))),
        ("skill sem 'Dado faltante'", lambda: checar_skill(skill.replace("| Dado faltante |", "| X |"))),
        ("painel sem 'invariantes conferidas'",
         lambda: checar_skill(skill.replace("invariantes conferidas", "itens"))),
        ("description sem exclusão", lambda: checar_skill(skill.replace("NÃO ativar em tarefa sem dado", "x"))),
        ("description sem gatilho", lambda: checar_skill(
            skill.replace("toda tarefa que toque dado, indicador, métrica ou modelo", "x"))),
        ("description sem a lista de tarefas", lambda: checar_skill(
            skill.replace("análise exploratória, conferência de número, regra de indicador", "x"))),
        ("regra global sem analise-dados", lambda: checar_global(glob.replace("`analise-dados`", "`x`"))),
        ("regra global sem gatilho", lambda: checar_global(
            glob.replace("Tarefa que toque dado, indicador, métrica ou modelo", "Tarefa"))),
        ("regra global com padrão invertido", lambda: checar_global(glob.replace(
            "modo acompanhado até a primeira ordem de autônomo", "modo autônomo até a primeira ordem de acompanhado"))),
        ("regra global sem 'carregar'", lambda: checar_global(
            glob.replace("carregar a skill `analise-dados`", "não carregar a skill `analise-dados`"))),
        ("discovery sem a linha do sub-modo",
         lambda: checar_discovery(disc.replace("`produto-de-dados.md`", "`x.md`"), True)),
        ("companion ausente", lambda: checar_discovery(disc, False)),
        ("skill sem a ferramenta na seção 3", lambda: checar_conferencia(
            skill.replace("tools/conferir_invariante.py", "tools/x.py"), qa, True)),
        ("ferramenta ausente", lambda: checar_conferencia(skill, qa, False)),
        ("qa-critic sem a seção 8", lambda: checar_conferencia(skill, qa.replace("seção 8 da skill", "skill"), True)),
        ("qa-critic sem o item", lambda: checar_conferencia(skill, qa.replace("Análise de dados", "X"), True)),
    ]
    for nome, f in sab:
        if not f():
            cegos.append(nome)
    return cegos


def main():
    fails = []
    for p in (SKILL, GLOBAL, DISC, QA):
        if not os.path.isfile(p):
            print(f"RESULTADO: FAIL (arquivo ausente: {p})")
            return 1
    skill, glob, disc = _ler(SKILL), _ler(GLOBAL), _ler(DISC)
    fails += checar_skill(skill)
    fails += checar_global(glob)
    fails += checar_discovery(disc, os.path.isfile(COMPANION))
    qa = _ler(QA)
    fails += checar_conferencia(skill, qa, os.path.isfile(FERRAMENTA))
    # (e) pacote web: a skill entra no tier premium como papel lateral (ADR-134, decisão 8)
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import web_export  # noqa: E402
    fails += checar_web(web_export.LATERAL)
    if checar_web([x for x in web_export.LATERAL if x != "analise-dados"]) == []:
        fails.append("autoteste: sabotagem NÃO reprovou (LATERAL sem analise-dados)")
    cegos = autoteste(skill, glob, disc, qa)
    fails += [f"autoteste: sabotagem NÃO reprovou ({c})" for c in cegos]

    print(f"analise-dados: skill, 7 classes, 7 itens do painel, regra global, sub-modo, pacote web, conferência por invariante; autoteste 17 sabotagens — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (fiação da análise acompanhada presente)" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
