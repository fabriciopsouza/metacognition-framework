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
