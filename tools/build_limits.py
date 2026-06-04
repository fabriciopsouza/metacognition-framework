#!/usr/bin/env python3
"""build_limits.py — gera LIMITS.md a partir do estado real dos canários (ADR-044).

Honestidade MECANIZADA: cada claim do framework vira uma linha com status derivado do canário que
a prova. canário existe (e o CI roda toda a suíte verde) -> PROVADO; ausente -> EM DESENVOLVIMENTO.
Cada linha carrega o que É mecanizado e o que NÃO é (limite declarado, vindo dos ADRs). O `--check`
compara o LIMITS.md em disco com o gerado e falha (exit 1) se divergir — **o doc não pode mentir**.

Uso:
    python tools/build_limits.py            # imprime o LIMITS.md gerado
    python tools/build_limits.py --out LIMITS.md
    python tools/build_limits.py --check    # exit 1 se LIMITS.md em disco != gerado

Status: PROVADO (canário verde no CI) · PARCIAL · EM DESENVOLVIMENTO (canário ausente).
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")

# (claim, canário, mecanizado, NÃO-mecanizado/limite, ADR)
CLAIMS = [
    ("Elicitação cobre as dimensões de produto antes de codar", "test_spec_depth.py",
     "cobertura de dimensão (gate barra J1)", "qualidade sênior do default (adversarial)", "033"),
    ("Entrega cobre cada quantificador do pedido", "test_completeness.py",
     "quantificadores do lexicon vs validation", "quantificador fora do lexicon", "034"),
    ("Mapeamento de campo-fonte é decisão registrada", "test_oracle_bias.py",
     "exigência de registro (confirmação+justificativa)", "correção semântica do mapeamento", "035"),
    ("Gate reprova número-alvo com erro plantado (anti-sicofância)", "test_sycophancy.py",
     "catch do erro plantado conhecido", "sicofância em caso novo (adversarial)", "041"),
    ("Entry-point roda pela porta do usuário (sem TTY)", "test_entrypoint_no_tty.py",
     "input() bloqueante = FAIL", "—", "036"),
    ("Requirements instalam em ambiente limpo", "test_clean_env.py",
     "resolução offline (--dry-run --no-index)", "venv real depende de rede/PyPI", "036"),
    ("Não sobrescreve artefato não-lido/não-criado na sessão", "test_overwrite_guard.py",
     "bloqueio (exit 2) de overwrite cego", "paridade .sh provada só na matriz CI", "037"),
    ("Execution-report auto + token honesto", "test_execution_report.py",
     "report+placar+anti-fabricação (NÃO MEDIDO)", "telemetria de token real-time (dep. do host)", "038"),
    ("Backstop por efeito (4+ famílias) com anti-falso-positivo", "test_effect_gate.py",
     "deny T3 / ask T2 por família", "OWASP LLM06 🟢 só após matriz CI 3 SOs + paridade 100%", "039"),
    ("Paridade de veredito .ps1 ↔ .sh", "test_parity.py",
     "decisão idêntica (provada na matriz CI)", "SKIP local sem jq — prova é no CI", "040"),
    ("Discovery cobre dimensões (eval EXECUTADO, não design-time)", "test_discovery_eval.py",
     "cobertura + discriminação raso×sênior", "qualidade sênior do default", "042"),
    ("Cobertura regulada da denylist", "test_regulatory_coverage.py",
     "famílias conhecidas têm representante", "denylist NÃO-EXAUSTIVA por design", "043"),
    ("Auto-detecção + validação de arquivos de entrada (dicionário-contrato)", "test_input_contract.py",
     "arquivos detectados na pasta + colunas obrigatórias validadas", "mapeamento semântico correto (qa-critic)", "046"),
    ("Pesquisa de contexto + verificação de âncora antes de codar (sob stake)", "test_context_brief.py",
     "context-brief presente + tabela de âncora (gate barra J1 sob sinal de stake) ou exceção consciente",
     "qualidade/correção da pesquisa (adversarial); sinais não-exaustivos", "051"),
    ("Modo non-admin inicia sob restrição de scripts (gates anunciados)", "test_nonadmin.py",
     "settings sem hooks + doutrina + bootstrap.py (sem PowerShell)", "enforcement anunciado depende do agente (não hook)", "047"),
    ("3 distribuições de fonte única (premium/baseline) — core do discovery preservado", "test_premium_tier.py",
     "premium marcado e stripável; core intacto no baseline", "feature premium nova precisa ser marcada (senão vaza)", "049"),
    ("Núcleo sem termo de domínio/cliente", "test_core_agnostic.py",
     "tier norma + tier sensível (export)", "vazamento semântico novo (qa-critic é o backstop)", "020"),
    ("Entrega navegável: índice guiado, auto-verificado (sem link órfão/pro vazio)", "test_make_index.py",
     "html+txt, ordem de leitura, lista só o que existe, resumo anti-fabricação", "estética do índice (não medida)", "050"),
    ("Vitrine honesta: sem overclaim + anti-drift de versão/link + prompt web fail-closed", "test_marketing_claims.py",
     "léxico absoluto-sem-hedge na vitrine; prompt web derivado de PUBLIC_SRC (fail-closed); versão/link da "
     "vitrine == main; disclosure de alucinação residual (proximidade)",
     "paráfrase de overclaim (léxico não-exaustivo, anti-FP > recall); qa-critic é o backstop", "059"),
    ("Corpus público de aprendizado anonimizado (learnings) com fail-closed + opt-in", "test_execution_report.py",
     "anonymize + gate sensitive-denylist (recusa se map/denylist ausente, regex inválida ou token sobrevive) + consent opt-in no CLI",
     "anonimização por regex NÃO-exaustiva: token fora do map E da denylist passa — revisão humana antes do push", "062"),
]


# Canários INTERNOS removidos da distribuição pública (export-clean STRIP_AFTER_VERIFY) porque
# reconstroem fragmentos de token de cliente para testar o linter sensível. Rodam na FONTE e no CI,
# não no pacote → o status NÃO pode depender da presença do arquivo (senão o LIMITS.md gerado no
# export diverge do committed e o --check falha no público; ADR-044/020). Determinístico em ambas as árvores.
INTERNAL_ONLY = {"test_core_agnostic.py", "test_premium_tier.py"}


def status_for(canary):
    if canary in INTERNAL_ONLY:
        return "PROVADO"  # roda na fonte/CI; não distribuído (por isso pode faltar no export limpo)
    path = os.path.join(TOOLS, canary)
    if not os.path.isfile(path):
        return "EM DESENVOLVIMENTO"
    return "PROVADO"


def build():
    L = []
    L.append("# LIMITS.md — o que o framework GARANTE, prova, e o que NÃO faz (gerado por tools/build_limits.py, ADR-044)")
    L.append("")
    L.append("> **Honestidade mecanizada.** Cada linha tem status derivado do **canário** que a prova "
             "(verde na matriz CI = PROVADO; ausente = EM DESENVOLVIMENTO). O `build_limits.py --check` "
             "falha o CI se este arquivo divergir dos canários — **o doc não pode mentir**. "
             "`PROVADO` = há canário e a suíte roda verde no CI (ADR-040). NÃO confunda com certificação.")
    L.append("")
    L.append("## O que entrega hoje")
    L.append("| Capacidade | Status | Canário (prova) | Mecanizado | NÃO-mecanizado (limite) | ADR |")
    L.append("|---|---|---|---|---|---|")
    for claim, canary, mec, nao, adr in CLAIMS:
        st = status_for(canary)
        badge = {"PROVADO": "✅ PROVADO", "PARCIAL": "🟡 PARCIAL",
                 "EM DESENVOLVIMENTO": "⏳ EM DESENVOLVIMENTO"}[st]
        canary_cell = f"`tools/{canary}`" + (" (interno¹)" if canary in INTERNAL_ONLY else "")
        L.append(f"| {claim} | {badge} | {canary_cell} | {mec} | {nao} | ADR-{adr} |")
    L.append("")
    if any(c in INTERNAL_ONLY for _, c, *_ in CLAIMS):
        L.append("> ¹ **canário interno**: roda na fonte e no CI, mas é **removido da distribuição pública** "
                 "(reconstrói fragmentos de token de cliente para testar o linter sensível — não pode ser publicado). "
                 "O status PROVADO reflete a fonte/CI; no pacote público o arquivo não existe **por design**.")
        L.append("")
    L.append("## O que NÃO fazemos (anti-overclaim)")
    L.append("- **Não certificamos conformidade.** Os perfis de `exemplos/dominio-regulado/` são **andaime "
             "de partida**, não auditoria — a adequação à norma concreta é do dono + revisão humana (HITL).")
    L.append("- **Não medimos tokens em tempo real** sem telemetria exposta pelo host — nesse caso o "
             "execution-report diz literalmente `NÃO MEDIDO` (nunca fabricamos número).")
    L.append("- **Não garantimos ausência de viés/sicofância em casos novos** — provamos o catch do erro "
             "plantado conhecido; o resto é o protocolo adversarial do qa-critic (ADR-018).")
    L.append("- **Não prometemos detecção exaustiva** de normas (denylist não-exaustiva) nem de comandos "
             "destrutivos (effect-gate é backstop conservador, não classificador completo).")
    L.append("- **Não substituímos o gate humano** em decisão irreversível/regulada (high-stakes-gate).")
    L.append("- **Não geramos documentos com polimento visual** (gráficos, branding, capa formatada): a "
             "geração automatizada (`gen_exec_doc`, premium) produz a **estrutura correta** e pagina o "
             "conteúdo — formatação fina é manual ou ADR futuro (ADR-050 §limite).")
    L.append("")
    L.append("> Gerado de `tools/build_limits.py`. Para atualizar: adicione o canário e rode o gerador; "
             "não edite à mão (o `--check` reprova divergência).")
    return "\n".join(L) + "\n"


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv[1:])
    content = build()
    target = os.path.join(ROOT, "LIMITS.md")
    if args.check:
        if not os.path.isfile(target):
            print("FAIL: LIMITS.md ausente — rode build_limits.py --out LIMITS.md")
            return 1
        disk = open(target, encoding="utf-8-sig").read()
        if disk.strip() != content.strip():
            print("FAIL: LIMITS.md fora de sync com os canários — regenere (build_limits.py --out LIMITS.md)")
            return 1
        print("PASS: LIMITS.md em sync com os canários")
        return 0
    if args.out:
        with open(os.path.join(ROOT, args.out), "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"LIMITS escrito em {args.out}")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
