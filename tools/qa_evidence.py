#!/usr/bin/env python3
"""qa_evidence.py — persiste o VEREDITO do qa-critic (subagente isolado, read-only) como ARTEFATO
auditavel em `_meta/qa/<bloco>.{json,md}`. Mecaniza "o qa-critic rodou no bloco" (ADR-074 emenda 2).

Cerne prosa->mecanismo: o subagente qa-critic NAO tem Write (so valida); o orquestrador canaliza o
JSON do veredito por aqui. O artefato e a EVIDENCIA que `test_qa_evidence.py` (fail-closed no master)
exige por release — fechando o gap "qa-critic e disciplina minha, nao processo" (sessao 2026-06-07).

Schema do veredito (compativel com o Output JSON do qa-critic SKILL):
  bloco                   str   id do bloco revisado (vira slug do arquivo)
  passou                  bool  veredito binario do protocolo de turno unico
  recomendacao            str   reverter|corrigir|aprovar_com_ressalvas|aprovar  (eixo de acao)
  problemas               list  [{severidade, local, descricao, ...}]
  verificacoes_executadas list  comandos/canarios rodados -> resultado (anti-fabricacao)
  release        (opcional) str versao que este veredito FECHA (ex.: "1.51.0"). So o veredito
                                 final do bloco (process-critic aprovativo) carrega isto -> e o que
                                 o gate de release exige. SE presente, `postura` torna-se OBRIGATORIO.
  postura        (cond.)    dict EVIDENCIA DE POSTURA (ADR-074 emenda 3 / posture-gate). Preenchida
                                 pelo qa-critic ADVERSARIAL (subagente isolado, nao auto-atestada pelo
                                 gerador). Campos: discovery (str nao-vazia: path do artefato OU
                                 "inline: <justificativa>"), rrc ("PASSA"|"FALHA"|"N/A: <razao>"),
                                 metodo_senior ("aplicado: <path>"|"N/A: <razao>"). Para fechar release,
                                 rrc DEVE ser PASSA.
  steelman       (opcional) str
  data           (auto)     str ISO UTC (preenchido se ausente)

CLI:
  python tools/qa_evidence.py --from-json <f|->   le veredito (arquivo ou '-'=stdin) e grava artefato
  python tools/qa_evidence.py --list              lista artefatos existentes
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA_DIR = os.path.join(ROOT, "_meta", "qa")
REQUIRED = ["bloco", "passou", "recomendacao", "problemas", "verificacoes_executadas"]
APPROVING = {"aprovar", "aprovar_com_ressalvas"}
# Ledger de juncoes (P3/ADR-077): ordem canonica do fluxo bicelular (ADR-011 + J6/ADR-045).
JUNCTION_ORDER = {"J0": 0, "J1": 1, "J2": 2, "J3": 3, "J4": 4, "J5": 5, "PC": 6, "J6": 7}

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _slug(s):
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", str(s).strip().lower())
    s = re.sub(r"-+", "-", s).strip("-.")
    return s or "bloco"


def _now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def render_md(v):
    L = [f"# QA-evidence — {v['bloco']}", ""]
    L.append(f"- **Data:** {v.get('data', '?')}")
    L.append(f"- **Veredito (passou):** {v['passou']}")
    L.append(f"- **Recomendacao:** {v['recomendacao']}")
    if v.get("release"):
        L.append(f"- **Fecha release:** v{v['release']}")
    if v.get("postura"):
        p = v["postura"]
        L += ["", "## Postura (posture-gate — atestada pelo qa-critic adversarial)"]
        L.append(f"- **Discovery:** {p.get('discovery', '—')}")
        L.append(f"- **RRC:** {p.get('rrc', '—')}")
        L.append(f"- **Metodo-senior:** {p.get('metodo_senior', '—')}")
    if v.get("steelman"):
        L += ["", "## Steelman", v["steelman"]]
    L += ["", "## Problemas", ""]
    probs = v.get("problemas") or []
    if not probs:
        L.append("_nenhum_")
    else:
        L += ["| Sev | Local | Descricao |", "|---|---|---|"]
        for p in probs:
            sev = p.get("severidade", "?")
            loc = str(p.get("local", "")).replace("|", "\\|")
            desc = str(p.get("descricao", "")).replace("|", "\\|").replace("\n", " ")
            L.append(f"| {sev} | {loc} | {desc} |")
    L += ["", "## Verificacoes executadas (anti-fabricacao)", ""]
    for x in (v.get("verificacoes_executadas") or []):
        L.append(f"- {x}")
    L.append("")
    return "\n".join(L)


def validate_postura(postura, for_release=False):
    """Valida o bloco de evidencia de postura. Retorna lista de problemas (vazia = OK)."""
    probs = []
    if not isinstance(postura, dict):
        return ["postura ausente ou nao-dict"]
    disc = str(postura.get("discovery", "")).strip()
    if not disc:
        probs.append("postura.discovery vazio (path do artefato OU 'inline: <justificativa>')")
    rrc = str(postura.get("rrc", "")).strip()
    if not rrc:
        probs.append("postura.rrc ausente (PASSA|FALHA|N/A: <razao>)")
    elif for_release and not rrc.upper().startswith("PASSA"):
        probs.append(f"postura.rrc='{rrc}' — release exige RRC PASSA")
    ms = str(postura.get("metodo_senior", "")).strip()
    if not ms:
        probs.append("postura.metodo_senior ausente ('aplicado: <path>' | 'N/A: <razao>')")
    # Gatilho DETERMINISTICO (ADR-009/010 mecanizado): fonte canonica/ADR nova -> metodo-senior
    # EXIGIDO, nao opcional. `fonte_canonica` e atestado pelo qa-critic adversarial (anti-JARVIS).
    if postura.get("fonte_canonica") and not ms.lower().startswith("aplicado"):
        probs.append("postura.fonte_canonica=true (norma/spec/ADR) -> metodo_senior DEVE ser "
                     "'aplicado: <path>' (gatilho deterministico, nao N/A)")
    return probs


def validate_problemas(problemas):
    """Valida CADA item de `problemas`. Retorna lista de erros (vazia = OK).

    ADR-104 (4a rodada de revisao, 13/08/2026): `write_artifact` so validava as chaves de TOPO.
    Um veredito com itens fora do schema (`titulo`/`situacao` em vez de `local`/`descricao`)
    passava, e `render_md` emitia a tabela com TODAS as celulas VAZIAS — sem erro, sem aviso.
    O .md, que e' o que humano le, ficava sem os achados. Falha silenciosa: fail-closed agora.
    """
    erros = []
    for i, p in enumerate(problemas or []):
        if not isinstance(p, dict):
            erros.append(f"problemas[{i}] nao e' objeto")
            continue
        faltam = [k for k in ("severidade", "local", "descricao") if not str(p.get(k, "")).strip()]
        if faltam:
            erros.append(f"problemas[{i}] sem {faltam} (schema: severidade, local, descricao)")
    return erros


def _head_sha():
    """SHA do HEAD deste repo, ou None se git nao responder."""
    import subprocess
    try:
        r = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           stdin=subprocess.DEVNULL)
    except (OSError, ValueError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def write_artifact(verdict, when=None):
    missing = [k for k in REQUIRED if k not in verdict]
    if missing:
        raise ValueError(f"veredito invalido — campos ausentes: {missing}")
    pe = validate_problemas(verdict.get("problemas"))
    if pe:
        raise ValueError("veredito invalido — itens de 'problemas' fora do schema: " + "; ".join(pe))
    # ADR-074 emenda 3 (posture-gate): veredito que FECHA release exige bloco de postura valido.
    if verdict.get("release"):
        pp = validate_postura(verdict.get("postura"), for_release=True)
        if pp:
            raise ValueError(f"veredito de release sem postura valida: {pp}")
    verdict.setdefault("data", when or _now_iso())
    # ADR-103 emenda 3 (7a rodada): carimba SOBRE QUAL ESTADO do codigo o veredito foi
    # emitido. Sem isto o squad_gate nao tem como saber se a evidencia e' anterior as
    # edicoes que ela diz cobrir — e "revisado uma vez" virava "liberado para sempre".
    # O campo ja existia no schema e nao era escrito por ninguem: decoracao.
    if not str(verdict.get("sha_revisado", "") or "").strip():
        verdict["sha_revisado"] = _head_sha() or ""
    os.makedirs(QA_DIR, exist_ok=True)
    slug = _slug(verdict["bloco"])
    jpath = os.path.join(QA_DIR, slug + ".json")
    mpath = os.path.join(QA_DIR, slug + ".md")
    json.dump(verdict, open(jpath, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(mpath, "w", encoding="utf-8").write(render_md(verdict))
    return jpath, mpath


def _validar_prova(prova):
    """Devolve o ponteiro se ele RESOLVE; levanta ValueError se nao (ADR-097 mecanismo ii).

    Tres formas aceitas, todas conferiveis por terceiro que tenha o repo:
      · caminho de arquivo que existe            -> `_meta/qa/x.json`
      · objeto git que existe                     -> `a1b2c3d` (commit, tag, blob)
      · digest declarado com o algoritmo          -> `sha256:<64 hex>`

    Por que validar na ESCRITA e nao so' na leitura: ponteiro quebrado gravado hoje vira
    "evidencia" que ninguem confere amanha.

    O QUE ISTO **NAO** GARANTE — dito sem rodeio, porque chamar de "ponteiro verificavel" sem a
    ressalva seria o proprio overclaim que este repo persegue (achado do qa-critic, 2026-08-16):
      · NAO confere RELEVANCIA. `CLAUDE.md` e' aceito como prova de qualquer juncao.
      · NAO confere CORRESPONDENCIA. Um `sha256:<64 hex>` inventado passa: ninguem calcula o
        digest de nada para comparar.
    O que ele garante e' menor e ainda assim util: o ponteiro **resolve** — existe arquivo, existe
    objeto git, ou o digest esta bem-formado. Elimina o campo preenchido com prosa ou com caminho
    que nunca existiu. Nao elimina o teto de auto-atestacao; estreita o buraco.
    """
    p = str(prova).strip()
    if not p:
        raise ValueError("`prova` vazia — use caminho de arquivo, sha de commit ou sha256:<hex>")
    if p.lower().startswith("sha256:"):
        h = p.split(":", 1)[1].strip()
        if len(h) == 64 and all(c in "0123456789abcdefABCDEF" for c in h):
            return p
        raise ValueError(f"`prova` sha256 malformada ({h[:16]}...): esperado 64 digitos hex")
    if os.path.isfile(os.path.join(ROOT, p)) or os.path.isfile(p):
        return p
    if 7 <= len(p) <= 40 and all(c in "0123456789abcdefABCDEF" for c in p):
        try:
            r = subprocess.run(["git", "-C", ROOT, "cat-file", "-e", p + "^{object}"],
                               capture_output=True, timeout=20)
            if r.returncode == 0:
                return p
        except (OSError, subprocess.SubprocessError):
            pass
        raise ValueError(f"`prova` parece sha ({p}) mas nao existe neste repositorio")
    raise ValueError(f"`prova` ({p}) nao resolve: nao e' arquivo existente, nem objeto git, "
                     f"nem sha256:<hex>. Ponteiro que nao resolve nao e' prova.")


def append_junction(bloco, junction, artefato, evidencia,
                    validation=None, justificativa=None, rewind=False, when=None,
                    resource=None, prova=None):
    """Ledger de juncoes (P3/P4, ADR-077): 1 linha JSONL por gate PASS declarado em /handoff.

    Da rastro mecanico a J0-J3 (antes prosa pura) e materia-prima objetiva a dim (iv)
    'process compliance' do process-critic. Regras:
      - forward-only (ADR-011): juncao anterior a ultima registrada exige rewind=True
        (rewind cascata do PC e legitimo; regressao silenciosa nao e);
      - J3 (P4): exige validation (path EXISTENTE de validation.md) OU justificativa
        explicita — fecha a clausula frouxa 'testes/spec se aplicavel' sem registro.
    Retorna o path do ledger. Levanta ValueError em violacao (fail-closed)."""
    j = str(junction).upper().strip()
    if j not in JUNCTION_ORDER:
        raise ValueError(f"juncao invalida '{junction}' — validas: {sorted(JUNCTION_ORDER)}")
    if not str(bloco).strip():
        raise ValueError("bloco vazio")
    if not str(evidencia).strip():
        raise ValueError("evidencia vazia (criterio binario + prova objetiva — ADR-011)")
    if j == "J3":
        ok_val = validation and os.path.isfile(os.path.join(ROOT, validation)) \
            or (validation and os.path.isfile(validation))
        if not ok_val and not (justificativa and str(justificativa).strip()):
            raise ValueError("J3 exige --validation <validation.md existente> OU --justificativa "
                             "explicita (P4/ADR-077: 'se aplicavel' sem registro = REPROVADO)")
    led_dir = os.path.join(QA_DIR, "junctions")
    os.makedirs(led_dir, exist_ok=True)
    path = os.path.join(led_dir, _slug(bloco) + ".jsonl")
    last = None
    if os.path.isfile(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    last = json.loads(line).get("junction")
                except Exception:
                    # fail-closed em corrupcao (achado BAIXO do process-critic v1.56.0): linha
                    # iliegivel zeraria o forward-only silenciosamente — recusar e mandar investigar.
                    raise ValueError(f"ledger corrompido ({os.path.basename(path)}: linha nao-JSON) — "
                                     f"investigue/restaure antes de registrar nova juncao")
    if last in JUNCTION_ORDER and JUNCTION_ORDER[j] < JUNCTION_ORDER[last] and not rewind:
        raise ValueError(f"forward-only violado: ultima juncao registrada {last}, tentando {j} "
                         f"sem --rewind (rewind cascata do PC deve ser explicito — ADR-011)")
    rec = {"junction": j, "bloco": bloco, "artefato": artefato or "", "evidencia": evidencia,
           "data": when or _now_iso(),
           # ADR-097 mecanismo (i): `status` EXPLICITO. Antes o PASS era implicito — existir o
           # registro significava ter passado. Implicito nao se audita: um log onde so' o sucesso
           # aparece nao distingue "passou" de "ninguem registrou", e o rewind ficava invisivel.
           "status": "REPROVADO_REWIND" if rewind else "PASS",
           # ADR-097 mecanismo (i): `resource` — QUEM produziu este PASS. Sem isto o event log nao
           # responde a pergunta mais basica do process mining, e a atestacao anti-auto-aprovacao
           # (modelo != autor) nao tem como ser conferida no fluxo, so' no artefato.
           "resource": str(resource or "").strip() or "nao-declarado"}
    if prova:
        # ADR-097 mecanismo (ii): `evidencia` e' prosa e continua sendo (o criterio binario, para
        # humano ler). `prova` e' o PONTEIRO VERIFICAVEL — sem ele a topologia e' falsificavel pelo
        # proprio agente que a registra (achado A3 do qa-critic sobre o ADR). Validado na hora:
        # ponteiro que nao resolve nao entra no ledger.
        rec["prova"] = _validar_prova(prova)
    if validation:
        rec["validation"] = validation
    if justificativa:
        rec["justificativa"] = justificativa
    if rewind:
        rec["rewind"] = True
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Persiste veredito qa-critic em _meta/qa/ (ADR-074).")
    ap.add_argument("--from-json", help="arquivo JSON do veredito, ou '-' para stdin")
    ap.add_argument("--list", action="store_true", help="lista artefatos existentes")
    ap.add_argument("--junction", help="registra gate PASS de juncao (J0..J5|PC|J6) no ledger (ADR-077)")
    ap.add_argument("--bloco", help="id do bloco (com --junction)")
    ap.add_argument("--artefato", default="", help="path/link do artefato-gate (com --junction)")
    ap.add_argument("--evidencia", default="", help="criterio binario + prova objetiva (com --junction)")
    ap.add_argument("--resource", default="", help="QUEM produziu o PASS: modelo/agente (ADR-097)")
    ap.add_argument("--prova", default="", help="ponteiro VERIFICAVEL: caminho de arquivo, sha de "
                                                "commit, ou sha256:<hex> (ADR-097)")
    ap.add_argument("--validation", help="path do validation.md (exigido em J3, ou --justificativa)")
    ap.add_argument("--justificativa", help="justificativa explicita quando J3 sem validation.md")
    ap.add_argument("--rewind", action="store_true", help="declara rewind cascata (permite voltar juncao)")
    args = ap.parse_args(argv)

    if args.junction:
        if not args.bloco:
            ap.error("--junction exige --bloco")
        try:
            path = append_junction(args.bloco, args.junction, args.artefato, args.evidencia,
                                   validation=args.validation, justificativa=args.justificativa,
                                   rewind=args.rewind, resource=args.resource, prova=args.prova)
        except ValueError as e:
            print(f"[junction-ledger] RECUSADO: {e}")
            return 1
        print(f"[junction-ledger] registrado: {args.junction} de '{args.bloco}' -> "
              f"{os.path.relpath(path, ROOT)}")
        return 0

    if args.list:
        if not os.path.isdir(QA_DIR):
            print("_meta/qa/ ausente — nenhum artefato.")
            return 0
        for f in sorted(os.listdir(QA_DIR)):
            if f.endswith(".json"):
                v = json.load(open(os.path.join(QA_DIR, f), encoding="utf-8"))
                rel = f" release=v{v['release']}" if v.get("release") else ""
                print(f"{f}: passou={v.get('passou')} rec={v.get('recomendacao')}{rel} "
                      f"problemas={len(v.get('problemas') or [])}")
        return 0

    if not args.from_json:
        ap.error("informe --from-json <f|-> ou --list")
    raw = sys.stdin.read() if args.from_json == "-" else open(args.from_json, encoding="utf-8").read()
    verdict = json.loads(raw)
    jpath, mpath = write_artifact(verdict)
    print(f"[qa-evidence] gravado: {os.path.relpath(jpath, ROOT)} + {os.path.relpath(mpath, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
