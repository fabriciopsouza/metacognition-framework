#!/usr/bin/env python3
"""cross-ai-gate (ADR-069) — TRAVA FÍSICA anti-loop da troca cross-IA.

Valida, de forma DETERMINÍSTICA e checável por máquina, o `manifest.json` do hub cross-IA
(lista de mensagens com frontmatter estruturado) e GARANTE TERMINAÇÃO da crítica mútua —
fecha o achado ALTO do qa-critic: "dedup por mensagem + teto por thread NÃO impedem loop
infinito inter-ciclos / persuasão → mudança → nova rodada".

Por que dedup-de-mensagem e teto-por-thread falham (e o que este gate faz no lugar):
  - dedup por report_id só evita reprocessar a MESMA mensagem; um novo report sobre o mesmo
    tópico tem novo id → passa. Aqui agrupamos por `topic_fingerprint`, não por mensagem.
  - teto por thread é burlável criando novo thread_id. Aqui o teto é por TÓPICO.
  - "regra do novo argumento" em prosa é indecidível. Aqui é checável: uma rodada só é
    válida se RESOLVE uma claim aberta, INTRODUZ claim nova, ou traz EVIDÊNCIA nova (hash).
    Repetir (mesmas claims, mesmos vereditos, mesma evidência) = restating = REJEITADO.

Mecanismos (todos sobre campos do frontmatter — nada de julgar conteúdo livre):
  1. MONOTONICIDADE / ponto-fixo: round>1 deve trazer progresso (resolve claim | claim nova |
     evidência nova). Restating puro → VIOLAÇÃO. É o quebra-loop principal (quiescência).
  2. CONVERGÊNCIA→SELAR: sem claim aberta (todas ACEITO/REJEITADO) → o tópico DEVE estar sealed.
  3. TETO POR TÓPICO + ESCALADA: round > MAX_ROUNDS exige escalation∈{pending,resolved} (gate
     humano físico: humano vira 'resolved'); senão VIOLAÇÃO.
  4. FINALIDADE / imutabilidade: tópico sealed só reabre com chave humana (`reopen_token`) OU
     nova evidência externa (`reopen_evidence_sha256` inédito). Persuasão de IA sozinha não reabre.
  5. SELAR SEM CROSS-WRITE (fecha ALTO #5): `status:sealed` é declarado pelo PRÓPRIO autor na sua
     mensagem; o ARQUIVAMENTO (mover p/ archive/) é ação da CI do hub, não da IA receptora.
     Este gate só LÊ status — nenhuma IA escreve no arquivo da outra.

Uso:
    python tools/cross_ai_gate.py <manifest.json>      # exit 0 = ok; 2 = violações; 1 = erro
    python tools/cross_ai_gate.py <manifest.json> --json
Sem dependências externas (stdlib).
"""
import json
import sys

MAX_ROUNDS = 3                      # teto POR TÓPICO (não por thread)
RESOLVED = {"ACEITO", "REJEITADO"}  # vereditos terminais; OPEN/DEFERIDO = aberto


def _evidence(msg):
    return {c.get("evidence_sha256") for c in msg.get("claims", []) if c.get("evidence_sha256")}


def _claim_ids(msg):
    return {c.get("claim_id") for c in msg.get("claims", []) if c.get("claim_id")}


def validate(manifest):
    """Recebe o dict do manifest; devolve lista de violações (vazia = PASS)."""
    violations = []
    messages = manifest.get("messages", [])

    # report_id único (dedup estrutural)
    seen_ids = {}
    for m in messages:
        rid = m.get("report_id")
        if rid in seen_ids:
            violations.append(f"report_id duplicado: {rid}")
        seen_ids[rid] = m

    # agrupa por topico
    topics = {}
    for m in messages:
        topics.setdefault(m.get("topic_fingerprint"), []).append(m)

    for topic, msgs in topics.items():
        if topic is None:
            violations.append("mensagem sem topic_fingerprint (agrupamento por topico impossivel)")
            continue
        # ordena por round; empate por report_id p/ determinismo
        msgs = sorted(msgs, key=lambda x: (x.get("round", 0), str(x.get("report_id"))))

        verdicts = {}              # estado acumulado claim_id -> veredito
        seen_evidence = set()
        seen_claims = set()        # claims DECLARADAS em claims[] (com evidência)
        declared = set()           # todos os claim_id já declarados em claims[]
        all_verdict_keys = set()   # todos os claim_id que receberam veredito
        sealed = False

        for i, m in enumerate(msgs):
            rid = m.get("report_id", "?")
            rnd = m.get("round", 0)
            mclaims = _claim_ids(m)
            mevidence = _evidence(m)
            mverdicts = m.get("verdict_per_claim", {})

            # (4) FINALIDADE: tópico selado só reabre com chave humana ou evidência inédita
            if sealed:
                token = m.get("reopen_token")
                new_ev = m.get("reopen_evidence_sha256")
                valid_reopen = bool(token) or (new_ev and new_ev not in seen_evidence)
                if not valid_reopen:
                    violations.append(
                        f"[{topic[:8]}] msg {rid}: escreve em TOPICO SELADO sem reabertura valida "
                        f"(exige reopen_token humano ou reopen_evidence_sha256 inedito) — persuasao de IA nao reabre")
                    continue
                sealed = False
                if new_ev:
                    seen_evidence.add(new_ev)

            # (3) TETO POR TÓPICO + escalada humana
            if rnd > MAX_ROUNDS and m.get("escalation") not in ("pending", "resolved"):
                violations.append(
                    f"[{topic[:8]}] msg {rid}: round {rnd} > teto {MAX_ROUNDS} sem escalation "
                    f"(exige escalada a humano: escalation=pending|resolved)")

            # claims novas SÓ contam como progresso se tiverem evidência (âncora) — qa-critic MÉDIO:
            # senão a IA estende rodadas inventando claims vazias.
            new_anchored = {c.get("claim_id") for c in m.get("claims", [])
                            if c.get("claim_id") and c.get("evidence_sha256")}

            # (1) MONOTONICIDADE / quiescência: round>1 precisa de PROGRESSO
            if i > 0:
                resolves = any(v in RESOLVED and verdicts.get(cid) not in RESOLVED
                               for cid, v in mverdicts.items())
                new_claim = bool(new_anchored - declared)
                new_ev = bool(mevidence - seen_evidence)
                if not (resolves or new_claim or new_ev):
                    violations.append(
                        f"[{topic[:8]}] msg {rid}: SEM PROGRESSO (nao resolve claim aberta, nao "
                        f"introduz claim nova ANCORADA, nao traz evidencia nova) = restating/loop — REJEITADO")

            # aplica estado
            verdicts.update(mverdicts)
            seen_claims |= new_anchored
            declared |= mclaims
            all_verdict_keys |= set(mverdicts.keys())
            seen_evidence |= mevidence
            if m.get("status") == "sealed":
                sealed = True

        # GHOST CLAIMS (qa-critic ALTO): veredito sobre claim_id nunca declarada em claims[]
        # -> convergencia/seal falso. Rejeita.
        ghost = all_verdict_keys - declared
        if ghost:
            violations.append(
                f"[{topic[:8]}] GHOST CLAIM: veredito sobre claim_id nao declarada em claims[]: "
                f"{sorted(ghost)} — convergencia/seal invalido")

        # (2) CONVERGÊNCIA→SELAR: só considera claims DECLARADAS; sem aberta -> deve estar sealed
        relevant = {cid: v for cid, v in verdicts.items() if cid in declared}
        open_claims = [cid for cid, v in relevant.items() if v not in RESOLVED]
        if relevant and not open_claims and not sealed:
            violations.append(
                f"[{topic[:8]}] CONVERGIU (todas as claims declaradas resolvidas) mas o topico NAO "
                f"esta sealed — deve selar (status:sealed) para travar a finalidade")

    return violations


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("uso: python tools/cross_ai_gate.py <manifest.json> [--json]", file=sys.stderr)
        return 1
    try:
        with open(args[0], encoding="utf-8") as fh:
            manifest = json.load(fh)
    except Exception as e:
        print(f"erro lendo manifest: {e}", file=sys.stderr)
        return 1

    violations = validate(manifest)
    if "--json" in argv:
        print(json.dumps({"ok": not violations, "violations": violations}, ensure_ascii=False, indent=2))
    else:
        if not violations:
            print("[cross-ai-gate] PASS — terminacao garantida (sem loop, finalidade travada).")
        else:
            print(f"[cross-ai-gate] FAIL — {len(violations)} violacao(oes):")
            for v in violations:
                print(f"  - {v}")
    return 0 if not violations else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
