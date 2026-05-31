#!/usr/bin/env python3
"""Canário do linter de agnosticismo (ADR-020). Prova COM EFEITO que check_core_agnostic.py:
  (1) PASSA no núcleo real (estado limpo atual);
  (2) PEGA um vazamento plantado (exit 1);
  (3) ISENTA linha com o sentinela `lint-agnostic:allow`;
  (4) detecta CADA padrão da denylist individualmente (ruleset realmente conectado).

Estilo e contrato iguais a test_effect_gate.py: imprime OK/FAIL por caso, exit 0 se tudo passar.
Sem dependências externas. Não escreve no núcleo: usa arquivos temporários fora do escopo.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_core_agnostic as lint  # noqa: E402

PATTERNS = lint.load_patterns()
fails = 0


def check(desc, condition):
    global fails
    status = "OK  " if condition else "FAIL"
    if not condition:
        fails += 1
    print(f"{status} {desc}")


def scan_text(text):
    """Escreve text em arquivo temporário e roda o scanner; retorna nº de violações."""
    fd, path = tempfile.mkstemp(suffix=".md")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        return len(lint.scan_file(path, PATTERNS))
    finally:
        os.remove(path)


# (1) núcleo real limpo -> main() retorna 0
rc_core = lint.main(["check_core_agnostic.py"])
check("[1] nucleo real PASSA (sem vazamento) -> exit 0", rc_core == 0)

# (2) vazamento plantado -> detecta
check("[2] vazamento 'ALCOA+/ANVISA' detectado", scan_text("deve seguir ALCOA+ e ANVISA\n") >= 1)

# (3) sentinela isenta a MESMA linha
check("[3] sentinela 'lint-agnostic:allow' isenta a linha", scan_text("refs ALCOA+ lint-agnostic:allow legitimo\n") == 0)

# (3b) sentinela isenta SÓ a sua linha, não a de baixo
two = "linha com ALCOA+ lint-agnostic:allow\noutra linha com ANVISA sem sentinela\n"
check("[3b] sentinela nao isenta linhas vizinhas", scan_text(two) == 1)

# (4) cada padrão da denylist é detectável por um exemplar canônico
SAMPLES = {
    r"\bALCOA(?:\+|\b)": "ALCOA+", r"\bANVISA\b": "ANVISA", r"\bANP\b": "ANP", r"\bFDA\b": "FDA",
    r"\bBACEN\b": "BACEN", r"\bGAMP\b": "GAMP", r"\bHIPAA\b": "HIPAA", r"\bLGPD\b": "LGPD",
    r"\bGDPR\b": "GDPR", r"\bGxP\b": "GxP", r"21\s*CFR": "21 CFR", r"\bPCI-?DSS\b": "PCI-DSS",
    # Expansão v1.30.0 (ADR-043) — famílias reguladas comuns:
    r"\bSOX\b": "SOX", r"\bISO[ -]?13485\b": "ISO 13485", r"\bISO[ -]?27001\b": "ISO 27001",
    r"\bISO[ -]?9001\b": "ISO 9001", r"\bCOBIT\b": "COBIT", r"\bITIL\b": "ITIL",
    r"\bBasel\s?(I{1,3}|IV)\b": "Basel III", r"\bSOC ?2\b": "SOC 2", r"\bNIST\b": "NIST",
    r"\bCLIA\b": "CLIA", r"\bSarbanes-?Oxley\b": "Sarbanes-Oxley",
}
sources = {src for _, src in PATTERNS}
for src in sources:
    sample = SAMPLES.get(src)
    if sample is None:
        check(f"[4] denylist tem amostra de teste p/ padrao {src!r}", False)
        continue
    check(f"[4] padrao {src!r} detecta '{sample}'", scan_text(f"texto {sample} aqui\n") >= 1)

# (5) texto agnóstico genuíno NÃO dispara falso-positivo
clean = "Em dominios regulados, rastreabilidade e validacao costumam ser mandatorias.\n"
check("[5] texto agnostico (sem norma nomeada) nao dispara falso-positivo", scan_text(clean) == 0)

# (5b) regressão (qa-critic round 2): 'ALCOA' como subpalavra NÃO dispara; 'ALCOA' norma E 'ALCOA+' SIM
check("[5b] 'alcoacorp' NAO e falso-positivo (boundary correto)", scan_text("empresa alcoacorp ltda\n") == 0)
check("[5b] 'ALCOA' (norma, sem +) ainda detecta", scan_text("principio ALCOA aqui\n") >= 1)

# (6) TIER SENSÍVEL (EMENDA v1.22.x): denylist de cliente/caso/repo, escopo repo-inteiro
SENS = lint.load_patterns(lint.SENSITIVE_DENYLIST_PATH)


def scan_sens(text):
    fd, path = tempfile.mkstemp(suffix=".md")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        return len(lint.scan_file(path, SENS, lint.SENSITIVE_SENTINEL))
    finally:
        os.remove(path)


# Tokens reais construídos em runtime — o arquivo-fonte distribuído NÃO pode conter o literal
# (senão o próprio tier sensível o pegaria; comprovado em campo 2026-05-31).
TOK_CLIENTE = "Vi" + "bra"
TOK_REPO = "LIMITES-" + "BATENTES-" + "RECALC"
check("[6] denylist sensivel carrega padroes", len(SENS) >= 1)
check("[6] token de cliente detectado", scan_sens(f"projeto da {TOK_CLIENTE} aqui\n") >= 1)
check("[6] nome de repo de caso detectado", scan_sens(f"no repo {TOK_REPO}\n") >= 1)
check("[6] sentinela 'lint-sensitive:allow' isenta a linha", scan_sens(f"ref {TOK_CLIENTE} lint-sensitive:allow legitimo\n") == 0)
check("[6] AUTOR != CLIENTE: handle do mantenedor NAO e sensivel", scan_sens("copyright fabriciopsouza no LICENSE\n") == 0)
check("[6] texto agnostico nao dispara tier sensivel", scan_sens("framework agnostico de dominio\n") == 0)

print("-" * 40)
print("RESULTADO:", "FAIL" if fails else "PASS (linter de agnosticismo fura o que devia; nao trava agnostico)")
sys.exit(1 if fails else 0)
