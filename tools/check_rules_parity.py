#!/usr/bin/env python3
"""check_rules_parity.py — anti-drift / anti-dual-authority das 4 REGRAS INVIOLAVEIS (E3 do plano
anti-bypass; mecaniza o erro #4 do Gemini — "dual prompt authority / silent drift" — no idioma DESTE
framework).

PRINCIPIO QUE HONRA (AGENT-FRAMEWORK §6.5): "Single source of truth — `_shared/` e a fonte... Ninguem
recopia regra." Logo NAO checa paridade byte-a-byte de blocos DUPLICADOS (isso violaria §6.5 e exigiria
duplicacao). Checa DRIFT entre os DIGESTOS que os arquivos de autoridade ja mantem por referencia:

  (1) CLAUDE.md tem o bloco "## Regras inviolaveis" com EXATAMENTE 4 itens numerados, cobrindo os 4
      conceitos canonicos (classificacao · anti-rename · file-first · anti-alucinacao/NAO SEI).
  (2) AGENT-FRAMEWORK.md, onde cita "N regras inviolaveis", usa o MESMO N (=4) e nomeia os 4 conceitos
      (pega o drift real achado em 2026-06-10: dizia "releitura forcada" no lugar de "NAO SEI").
  (3) AGENTS.md ("## Regras sempre ativas") REFERENCIA a SSoT (`_shared/` ou `.agent/rules/`) em vez de
      redefinir as regras inline — guarda direta contra dual-authority (principio 5).

Domain-agnostico no metodo; os ponteiros (CLAUDE/AGENTS/AGENT-FRAMEWORK) sao convencao deste repo.
Uso: python tools/check_rules_parity.py   (exit 0 PASS; 1 se drift)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Os 4 conceitos canonicos das regras inviolaveis (fonte autoritativa: CLAUDE.md global + AGENT-FRAMEWORK
# §6.1). Assinatura = alternativas que identificam o conceito (tolerante a redacao, intolerante a sumico).
CANON = [
    ("classificacao", r"classifica|CONFIRMADO|INFERIDO|DESCONHECIDO"),
    ("anti-rename", r"anti-rename|renomear"),
    ("file-first", r"file-first|ler/inspecionar|inspecionar antes|inspecionar"),
    ("anti-alucinacao", r"N[ÃA]O SEI|nunca inventar|jamais inventar|anti-aluc"),
]
N_CANON = len(CANON)

# Regras permanentes do dono que valem em TODA pasta (fonte versionada -> ~/.claude/CLAUDE.md pelo
# sync-global). Sem elas, em projeto de fora o agente so le a instrucao generica do harness ("nao chame
# subagente sem pedido"; "link relativo a raiz do workspace") e a ordem do dono some. Cada assinatura
# e' uma clausula cuja perda ja' custou reincidencia medida.
GLOBAL_SRC = os.path.join(".claude", "global", "CLAUDE-global.md")
GLOBAL_INSTALLER = os.path.join(".claude", "hooks", "sync-global.ps1")
# Rota non-admin (ADR-047): onde PowerShell e' vetado, so o bootstrap.py instala. Sem esta guarda a
# regra "chegava em toda pasta" so' nas maquinas em que ela ja chegava (achado ALTA do QA 25/09).
GLOBAL_INSTALLER_PY = "bootstrap.py"
# Ancorada no INICIO do comando (opcionalmente com atribuicao): o nome dentro de uma string — print,
# f-string, docstring — nao e' chamada. Antes casava `print("seria chamado: instalar_regras_globais(")`.
GLOBAL_INSTALLER_PY_CALL = (r"(?m)^[ \t]+(?:[A-Za-z_]\w*(?:[ \t]*,[ \t]*[A-Za-z_]\w*)*[ \t]*=[ \t]*)?"
                            r"instalar_regras_globais\(")
# Implementacao UNICA em bootstrap.py; os outros pontos de entrada so' a CHAMAM (duas copias da
# logica divergiram tres vezes na revisao de 25/09). Cada um precisa da chamada em linha de codigo.
# A regex exige o comando EXECUTADO (operador & no PS; o interpretador no inicio da linha no sh). Texto
# de ajuda que so' MENCIONA o comando (echo "rode ... --regras-globais") passava — furo confirmado
# por mutacao em 25/09: apagar a chamada real e deixar so' a mensagem mantinha o canario verde.
GLOBAL_CALLERS = [
    # PS: a linha COMECA pela atribuicao do resultado da chamada; dentro de Write-Host "..." nao casa.
    (GLOBAL_INSTALLER, r"(?m)^[ \t]*\$\w+[ \t]*=[ \t]*&[ \t]*\$py\.Source[ \t]+\$bootPy[ \t]+--regras-globais"),
    ("bootstrap.sh", r"(?m)^[ \t]*\"\$PY_BIN\"[ \t]+\"[^\"\r\n]*bootstrap\.py\"[ \t]+--regras-globais"),
]
GLOBAL_RULES = [
    ("marcador-inicio", r"<!-- framework:global:inicio"),
    ("marcador-fim", r"<!-- framework:global:fim -->"),
    ("revisao-em-subagente", r"qa-critic"),
    ("haiku-nunca-autor", r"Haiku nunca [ée] autor"),
    ("autocritica-nao-substitui", r"Autocr[ií]tica n[ãa]o substitui"),
    ("falha-relata-erro-real", r"erro real"),
    ("caminho-absoluto", r"caminho absoluto"),
    ("alvo-file-uri", r"file:///"),
    ("vence-link-relativo", r"link relativo"),
    ("escada-anti-excesso", r"primeiro degrau que resolve"),
    ("estilo-sobre-output-style", r"prevalece sobre o estilo de sa[ií]da"),
    ("fontes-em-arquivo", r"Nada fica s[oó] no chat"),
    ("plano-nao-expira", r"Plano aprovado n[aã]o expira"),
    ("comando-nao-apaga-plano", r"Comando de sess[aã]o nunca apaga"),
]


def _read(rel, root=ROOT):
    return open(os.path.join(root, rel), encoding="utf-8-sig").read()


def _block(text, header_pat):
    """Extrai a secao de um heading ## ate o proximo ## (ou fim)."""
    m = re.search(header_pat, text)
    if not m:
        return None
    start = m.end()
    nxt = re.search(r"(?m)^##\s", text[start:])
    return text[start:start + nxt.start()] if nxt else text[start:]


def audit(root=ROOT):
    issues = []

    # (1) CLAUDE.md — bloco digesto com 4 itens cobrindo os 4 conceitos
    try:
        claude = _read("CLAUDE.md", root)
        blk = _block(claude, r"(?im)^##\s+Regras invioláveis")
        if blk is None:
            issues.append("CLAUDE.md: bloco '## Regras invioláveis' ausente")
        else:
            n_items = len(re.findall(r"(?m)^\s*\d+\.\s", blk))
            if n_items != N_CANON:
                issues.append(f"CLAUDE.md: bloco lista {n_items} regras, esperado {N_CANON} "
                              f"(drift: regra adicionada/removida)")
            for label, sig in CANON:
                if not re.search(sig, blk, re.I):
                    issues.append(f"CLAUDE.md: conceito '{label}' ausente do bloco de regras (drift)")
    except Exception as e:
        issues.append(f"CLAUDE.md ilegivel: {e}")

    # (2) AGENT-FRAMEWORK.md — "N regras invioláveis" com N==4 e os 4 conceitos nomeados perto
    try:
        af = _read("AGENT-FRAMEWORK.md", root)
        m = re.search(r"(\d+)\s+regras invioláveis", af, re.I)
        if not m:
            issues.append("AGENT-FRAMEWORK.md: nao cita 'N regras invioláveis' (referencia ao digesto sumiu)")
        else:
            n = int(m.group(1))
            if n != N_CANON:
                issues.append(f"AGENT-FRAMEWORK.md: cita {n} regras invioláveis, CLAUDE.md tem {N_CANON} "
                              f"(contagem divergente entre arquivos de autoridade)")
            window = af[m.end():m.end() + 280]  # o parentetico que nomeia os 4 conceitos
            for label, sig in CANON:
                if not re.search(sig, window, re.I):
                    issues.append(f"AGENT-FRAMEWORK.md: conceito '{label}' nao nomeado junto a "
                                  f"'{n} regras invioláveis' (drift vs CLAUDE.md)")
    except Exception as e:
        issues.append(f"AGENT-FRAMEWORK.md ilegivel: {e}")

    # (3) AGENTS.md — REFERENCIA a SSoT (nao redefine) — guarda anti dual-authority (principio 5)
    try:
        agents = _read("AGENTS.md", root)
        blk = _block(agents, r"(?im)^##\s+Regras sempre ativas")
        if blk is None:
            issues.append("AGENTS.md: secao '## Regras sempre ativas' ausente")
        elif not re.search(r"_shared|\.agent/rules", blk):
            issues.append("AGENTS.md: '## Regras sempre ativas' nao referencia a SSoT (_shared/ ou "
                          ".agent/rules/) — risco de dual-authority (principio 5: ninguem recopia regra)")
    except Exception as e:
        issues.append(f"AGENTS.md ilegivel: {e}")

    # (4) [ADR-111] GUARDA DE PONTEIRO MORTO. Regra citada por nome num arquivo de autoridade tem
    # de existir em `.agent/rules/`. Nao exigimos que TODA regra seja nomeada — o ponteiro generico
    # para o diretorio e' o desenho deste repo (so `00-glossario` era nomeada antes desta versao) —
    # mas quem e' nomeada fica presa: apagar o arquivo e deixar o ponteiro, ou renomear o arquivo e
    # esquecer o ponteiro, passa a reprovar. E' o que faz uma regra VIAJAR para projeto novo em vez
    # de virar link quebrado no README de outra pessoa.
    citados = set()
    for nome in ("CLAUDE.md", "AGENTS.md", "AGENT-FRAMEWORK.md"):
        try:
            # [QA de juncao 19/08/2026, achado BAIXA] ponteiro citado DENTRO de bloco de
            # codigo e ilustracao, nao promessa — nao pode gerar falso positivo.
            _txt = re.sub(r"```.*?```", "", _read(nome, root), flags=re.S)
            for m in re.finditer(r"\.agent/rules/([A-Za-z0-9._-]+\.md)", _txt):
                citados.add((nome, m.group(1)))
        except Exception:
            pass
    for origem, arq in sorted(citados):
        if not os.path.isfile(os.path.join(root, ".agent", "rules", arq)):
            issues.append(f"{origem} aponta para `.agent/rules/{arq}`, que NAO existe — ponteiro morto: "
                          f"a regra nao viaja, e quem clonar o projeto le uma promessa vazia")

    # (5) Regras globais do dono: a fonte existe, carrega cada clausula, e o instalador ainda a instala.
    try:
        glob_txt = _read(GLOBAL_SRC, root)
        for label, sig in GLOBAL_RULES:
            if not re.search(sig, glob_txt, re.I):
                issues.append(f"{GLOBAL_SRC}: clausula '{label}' ausente — a regra do dono deixa de "
                              f"valer fora deste repo")
    except Exception as e:
        issues.append(f"{GLOBAL_SRC} ilegivel ou ausente ({e}) — sem ele nada leva as regras do dono "
                      f"para outros projetos")
    # Linha de CODIGO, nao substring: o comentario de cabecalho do instalador tambem cita o arquivo,
    # e apagar a logica mantendo o comentario passava (achado MEDIA do QA de 25/09/2026).
    for arq, chamada in GLOBAL_CALLERS:
        try:
            if not re.search(chamada, _read(arq, root)):
                issues.append(f"{arq} nao instala mais CLAUDE-global.md (sem chamada a "
                              f"`bootstrap.py --regras-globais`) — a fonte existe mas nao chega a "
                              f"~/.claude/CLAUDE.md por este caminho")
        except Exception as e:
            issues.append(f"{arq} ilegivel ou ausente ({e})")
    try:
        if not re.search(GLOBAL_INSTALLER_PY_CALL, _read(GLOBAL_INSTALLER_PY, root)):
            issues.append(f"{GLOBAL_INSTALLER_PY} nao instala mais CLAUDE-global.md (sem chamada a "
                          f"instalar_regras_globais) — na rota non-admin as regras do dono nao chegam")
    except Exception as e:
        issues.append(f"{GLOBAL_INSTALLER_PY} ilegivel ou ausente ({e})")

    return issues


def main():
    issues = audit()
    print(f"4 regras invioláveis: digesto CLAUDE × referencia AGENT-FRAMEWORK × delegacao AGENTS — "
          f"{'OK' if not issues else 'DRIFT'}")
    for i in issues:
        print("  -", i)
    print("-" * 50)
    print("RESULTADO:", "PASS (sem drift entre arquivos de autoridade; SSoT preservada)" if not issues
          else f"FAIL ({len(issues)} drift)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
