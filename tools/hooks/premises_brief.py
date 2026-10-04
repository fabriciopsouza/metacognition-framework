#!/usr/bin/env python3
"""premises_brief.py - SessionStart: inventario do QUE JA FOI DECIDIDO (ADR-109).

GAP DE CAMPO (dono, 2026-08-23): *"este comportamento de recuperar premissas, ver git, ler tudo
e ter certeza para nao reinventar a roda DEVE ser comportamento padrao"* - dito depois de o
agente afirmar como CONFIRMADO uma premissa de origem de dado que CONTRARIAVA definicao ja
tomada, e de reprocessar trabalho ja fechado mudando regra acordada.

ESCOPO DESTE HOOK - duas camadas, nao tres:
  1. MEMORIA (propria E dos projetos irmaos). Lacuna real: nenhum inventario do framework
     olhava para `~/.claude/projects/*/memory/`. Na sessao que originou a ADR, a memoria do
     proprio projeto estava VAZIA e a premissa vivia na memoria de um projeto IRMAO - o agente
     concluiu "nao ha registro" de uma busca que nunca cobriu o lugar certo.
  3. ARTEFATOS DE DECISAO do repo (mission, requirements, ADRs, glossario, provas).

A camada 2 (procedencia do trabalho: branch defasada, retrato congelado) NAO esta aqui de
proposito: `check_repo_sync.py::baseline_staleness` (ADR-084) ja mede HEAD..origin/main para
feature branch com upstream proprio em dia, persiste marker e o route-gate repete por turno.
Reimplementar seria duplicacao mais fraca - rejeitada pela regua de ganho liquido (ADR-007).

MECANISMO: lista ONDE a premissa mora (ponteiro, nunca conteudo - ADR-029 nao queima contexto).
Fail-open: o boot nunca quebra por causa dele.
"""
import json
import os
import re
import sys

MAX_LIST = 12
MAX_IRMAOS = 8
# Convencao do harness para o nome da pasta em ~/.claude/projects: todo caractere que nao seja
# alfanumerico vira '-'. CONFIRMADO por pasta real com espaco, hifen e underscore no path:
#   C:\Users\zdvn\VIBRA\NMCV - Documentos\Indicador\Homologacoes\Gerar_Dados
#   -> c--Users-zdvn-VIBRA-NMCV---Documentos-Indicador-Homologacoes-Gerar-Dados
_NAO_ALNUM = re.compile(r"[^a-zA-Z0-9]")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# (rotulo, caminho relativo, o que este arquivo DECIDE)
ARQUIVOS = [
    ("briefing", "docs/briefing.md", "objetivo, escopo IN/OUT, criterio de aceite"),
    ("mission", "mission.md", "product_type + escopo declarado"),
    ("mission", "docs/mission.md", "product_type + escopo declarado"),
    ("requirements", "docs/requirements.md", "spec elicitada pelo discovery"),
    ("glossario", ".agent/rules/00-glossario.md", "nomes = fonte da verdade (anti-rename)"),
    ("handoff", "HANDOFF.md", "onde paramos e qual o proximo passo"),
    ("handoff", "docs/HANDOFF.md", "onde paramos e qual o proximo passo"),
    ("mapa de fontes", "MAPA-DE-FONTES.md", "quem e dono de dizer o que"),
    ("ambiente", ".agent/environment.json", "premissas de ambiente ja verificadas"),
    ("correlacoes", ".agent/correlations.json", "artefatos que mudam juntos"),
]
DIRETORIOS = [
    ("decisoes (ADR)", "docs/adr", "decisoes ja tomadas - NAO reabrir sem ADR novo"),
    ("regras sempre-ativas", ".agent/rules", "regras do projeto"),
    ("provas", "provas", "o que ja foi verificado, com a consulta reproduzivel"),
]


def emit(ctx):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart", "additionalContext": ctx}}, ensure_ascii=False))


def stamp_liveness(cwd, key, session_id):
    """Prova de liveness (ADR-060/061): grava .claude/.hooklive/<key>=<session_id>.

    O hooks-manifest.json so pode listar hook que CARIMBA - sem isto o route-gate declararia
    este gate ausente TODA sessao (falso-alarme que ensina o dono a ignorar o aviso).
    So escreve dentro de diretorio EXISTENTE: cwd vem do stdin e nao e de confianca - carimbar
    em cwd invalido materializava arvore fantasma dentro do repo.
    """
    try:
        import time
        if not (isinstance(cwd, str) and os.path.isdir(cwd)):
            return
        d = os.path.join(cwd, ".claude", ".hooklive")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, key), "w", encoding="utf-8") as f:
            f.write(session_id or f"epoch:{int(time.time())}")
    except Exception:
        pass


def slug_projeto(caminho):
    """Nome da pasta em ~/.claude/projects para um cwd. Ver _NAO_ALNUM."""
    return _NAO_ALNUM.sub("-", caminho)


def _conta_registros(idx):
    """Registros do MEMORY.md. Aceita '-', '*' e lista numerada - contar so '- [' produzia
    falso 'memoria vazia' para indice escrito em outro estilo."""
    n = 0
    try:
        for ln in open(idx, encoding="utf-8", errors="replace"):
            s = ln.strip()
            if re.match(r"^(?:[-*+]|\d+[.)])\s+\S", s):
                n += 1
    except OSError:
        return 0
    return n


def inventario_memoria(cwd, home):
    """Camada 1: memoria do projeto E dos irmaos."""
    base = os.path.join(home, ".claude", "projects")
    if not os.path.isdir(base):
        return []
    alvo = slug_projeto(cwd).lower()
    propria, irmaos = None, []
    try:
        for nome in sorted(os.listdir(base)):
            idx = os.path.join(base, nome, "memory", "MEMORY.md")
            if not os.path.isfile(idx):
                continue
            n = _conta_registros(idx)
            if nome.lower() == alvo:
                propria = (idx, n)
            else:
                irmaos.append((nome, n))
    except OSError:
        return []

    linhas = []
    if propria and propria[1] > 0:
        linhas.append(f"- **memoria deste projeto** - `{propria[0]}` ({propria[1]} registro(s))")
    else:
        linhas.append(
            "- **memoria deste projeto** - VAZIA ou ausente. "
            "**Memoria vazia NAO e ausencia de premissa** (ADR-109): procure nos irmaos abaixo.")
    if irmaos:
        top = ", ".join(f"`{n}`({c})" for n, c in irmaos[:MAX_IRMAOS])
        mais = f" (+{len(irmaos) - MAX_IRMAOS})" if len(irmaos) > MAX_IRMAOS else ""
        linhas.append(f"- **memoria de projetos irmaos** - em `{base}`: {top}{mais}")
    return linhas


def inventario_decisoes(cwd):
    """Camada 3: artefatos de decisao do repo."""
    linhas, vistos = [], set()
    for rotulo, rel, decide in ARQUIVOS:
        p = os.path.join(cwd, rel.replace("/", os.sep))
        if os.path.isfile(p) and rotulo not in vistos:
            vistos.add(rotulo)
            linhas.append(f"- **{rotulo}** - `{rel}` (decide: {decide})")
    for rotulo, rel, decide in DIRETORIOS:
        d = os.path.join(cwd, rel.replace("/", os.sep))
        if not os.path.isdir(d):
            continue
        try:
            fs = sorted(f for f in os.listdir(d) if f.lower().endswith(".md"))
        except OSError:
            continue
        if not fs:
            continue
        # Mostra os MAIS RECENTES. ADR é numerada em ordem crescente: truncar pelo inicio
        # escondia justamente as decisoes vigentes e apontava para a arqueologia.
        recentes = fs[-MAX_LIST:]
        shown = ", ".join(f"`{f}`" for f in recentes)
        mais = f" (+{len(fs) - MAX_LIST} mais antigos em `{rel}/`)" if len(fs) > MAX_LIST else ""
        linhas.append(f"- **{rotulo}** - {shown}{mais} (decide: {decide})")
    return linhas


def main():
    try:
        cwd, sid = None, ""
        try:
            raw = sys.stdin.read()
        except Exception:
            raw = ""
        if raw:
            try:
                h = json.loads(raw)
                c = h.get("cwd")
                if isinstance(c, str) and os.path.isdir(c):
                    cwd = c
                sid = str(h.get("session_id") or "")
            except Exception:
                pass
        if cwd is None:
            pd = os.environ.get("CLAUDE_PROJECT_DIR")
            cwd = pd if (pd and os.path.isdir(pd)) else None

        # Sem cwd confiavel: silencio. Emitir o inventario do repo onde o hook MORA seria
        # apontar premissas de outro projeto como se fossem deste - a versao boot do defeito
        # que esta ADR combate.
        if cwd is None:
            emit("")
            return 0

        # ADR-061: carimba ANTES de qualquer saida antecipada (carimbo = "o hook executou").
        stamp_liveness(cwd, "premises-brief", sid)
        home = os.environ.get("USERPROFILE") or os.environ.get("HOME") or os.path.expanduser("~")

        decidido = inventario_decisoes(cwd)
        memoria = inventario_memoria(cwd, home)
        if not (decidido or memoria):
            emit("")
            return 0

        blocos = ["# [premises-brief ADR-109] RECUPERE AS PREMISSAS ANTES DE DECIDIR", "",
                  "Nao reinvente o que ja foi decidido. Antes do primeiro tool call de dominio, "
                  "consulte o que for pertinente **e diga o que consultou**."]
        if memoria:
            blocos += ["", "## Memoria (onde a premissa costuma morar)", ""] + memoria
        if decidido:
            blocos += ["", "## Ja decidido neste projeto", ""] + decidido
        blocos += [
            "", "## Regra (ADR-109)", "",
            "- **Ausencia de evidencia NAO e evidencia de ausencia.** Nao achou registro? "
            "Isso e `[A-DEFINIR]`, nunca `[CONFIRMADO]` na direcao que lhe convem.",
            "- **Diga o que procurou** ao elicitar. \"Nao encontrei X em A, B, C - onde esta?\" "
            "e resposta legitima; presumir no lugar do dono nao e.",
            "- **Regra ja acordada nao muda sem confirmacao**, mesmo que voce a julgue "
            "tecnicamente melhor (canonico-prevalece, `_shared/traceability` Regra 6).",
            "- **Procedencia do codigo que voce le** (branch defasada, retrato congelado) vem do "
            "`check-repo-sync` (ADR-019/084) - leia o aviso dele, nao presuma estar em dia.",
        ]
        emit("\n".join(blocos) + "\n")
        return 0
    except Exception as e:  # noqa: BLE001 - boot nunca crasha
        sys.stderr.write(f"[premises-brief] warning (nao-bloqueante): {e}\n")
        emit("")
        return 0


if __name__ == "__main__":
    sys.exit(main())
