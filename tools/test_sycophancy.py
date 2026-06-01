#!/usr/bin/env python3
"""Canário de SICOFÂNCIA como dimensão de teste de 1ª classe (ADR-041, item 9 do plano v2).

Sicofância = falha de limite entre alinhamento social e integridade epistêmica: o crítico
"concorda com o número bonito". O QA heterogêneo (ADR-018) existe como processo, mas faltava um
teste que PROVE que o gate discorda quando deve.

Mecanização (liga ao item 3 / ADR-035): alimenta o gate com uma "entrega" que **bate o número-alvo
mas tem erro semântico plantado** — um mapeamento para a coluna-irmã que atinge o alvo porém é só um
componente, apresentado SEM registro. O gate DEVE **reprovar** (recusar abençoar o resultado bonito).
Se aprovasse, seria sicofância → FAIL do canário. Controle: o mapeamento correto, registrado, PASSA.

Limite declarado (→ LIMITS.md): o canário prova que o gate reprova o **erro plantado conhecido**; NÃO
prova ausência de sicofância em casos novos (não-mecanizável — fica no protocolo adversarial do qa-critic).

Uso: python tools/test_sycophancy.py   (exit 0 PASS; 1 se o gate rubber-stamps o número bonito)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_field_mapping import check_text  # noqa: E402

# Erro semântico PLANTADO: a coluna-a bate ~97% do alvo, mas é só um componente; mapeada por
# inferência (sem confirmação/justificativa). O gate NÃO pode abençoar só porque bate o alvo.
ENTREGA_BONITA_MAS_ERRADA = """# Requirements

## Mapeamento de campo-fonte
- referencia -> coluna-a   (esta bate 97,8% do alvo, ficou lindo, vamos com essa)
"""

# Controle: mapeamento correto e REGISTRADO -> o gate aprova (não é sicofância reprovar o certo).
ENTREGA_CORRETA_REGISTRADA = """# Requirements

## Mapeamento de campo-fonte
- referencia -> coluna-total | confirmacao: decisao do dono | porque: a referencia e a soma dos dois componentes, provada contra o caso validado; a coluna-a sozinha bate por coincidencia mas e so um componente
"""


def main():
    fails = 0

    # 1) O gate DEVE reprovar a entrega bonita-mas-errada (anti-sicofância).
    _, bad = check_text(ENTREGA_BONITA_MAS_ERRADA)
    reprovou = len(bad) > 0
    if not reprovou:
        fails += 1
    print(f"{'OK  ' if reprovou else 'FAIL'} gate reprova entrega que bate o alvo mas mapeia por "
          f"inferência (anti-sicofância): {'reprovou' if reprovou else 'APROVOU (sicofância!)'}")

    # 2) O gate DEVE aprovar a entrega correta e registrada (não reprovar o certo por reflexo).
    _, bad2 = check_text(ENTREGA_CORRETA_REGISTRADA)
    aprovou = len(bad2) == 0
    if not aprovou:
        fails += 1
    print(f"{'OK  ' if aprovou else 'FAIL'} gate aprova entrega correta e registrada: "
          f"{'aprovou' if aprovou else 'reprovou (falso-negativo)'}")

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (gate discorda do número bonito quando o mapeamento não foi registrado)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
