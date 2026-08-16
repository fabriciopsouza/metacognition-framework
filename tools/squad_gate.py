#!/usr/bin/env python3
"""squad_gate.py — GATE deterministico do squad (ADR-092). Dada a mudanca STAGED, exige a evidencia
ATESTADA dos papeis obrigatorios (matriz em behaviors/manifest.json).

ESTADO (ADR-104, 13/08/2026 — leia antes de confiar no que vem abaixo):
Este script e' fail-closed NA PROPRIA LOGICA: invocado direto, sai com exit != 0 quando falta
evidencia. Mas a ATIVACAO como bloqueio de merge foi DESACOPLADA: o passo do CI roda com
`continue-on-error: true` e apenas AVISA (`::warning::`), nao reprova o check. Ou seja:
**hoje ele nao barra ninguem** — e' advisory, coerente com `capabilities.json`
(`enforcement: advisory`) e com o CHANGELOG. Condicao para reativar esta escrita no ADR-104.
Este cabecalho ja afirmou "fail-closed" e "reprova o check" em tempo presente DEPOIS do
desacoplamento: as rodadas 4-6 corrigiram essa classe no CHANGELOG e no history e esqueceram o
proprio mecanismo (achado da 7a rodada). Mecanismo tambem mente quando o comentario envelhece.

Corrige o "teatro" (qa-critic C2): evidencia de qa-critic so conta com ATESTACAO DE ISOLAMENTO —
`atestacao.agentId` nao-vazio (subagente isolado) E `atestacao.modelo` != autor do bloco (ADR-074).
String solta / auto-atestacao nao passa.

Onde ele roda: o STEP DE CI em .github/workflows/ci.yml executa
`squad_gate --paths-from <diff do PR>` em pull_request — mas em modo ADVISORY (ver acima).
Uma versao anterior deste cabecalho citava post_canary_status.py como "a trava" — FALSO:
aquele script roda run_canaries.py, que executa test_squad_gate.py (canario de LOGICA), nunca
a avaliacao do diff real. Era overclaim de mecanismo, a mesma classe de defeito que este gate
existe para pegar. O git-hook local nao existe nesta maquina (.git/hooks vazio) e nunca foi trava.

LIMITE DECLARADO: so roda em `pull_request`. Push direto numa branch nao aciona nada — a
protecao contra isso e' exigir PR na configuracao do repositorio, que e' do dono, nao deste script.

CLI:
  python tools/squad_gate.py            # avalia o que esta staged (git diff --cached) -> exit!=0 se faltar
  python tools/squad_gate.py --paths a.py docs/adr/x.md   # avalia paths dados (teste/CI)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "behaviors", "manifest.json")
QA_DIR = os.path.join(ROOT, "_meta", "qa")
APPROVING = {"aprovar", "aprovar_com_ressalvas"}

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def load_manifest(path: str = MANIFEST) -> dict:
    return json.load(open(path, encoding="utf-8"))


def classify(paths, manifest) -> set:
    """Path(s) staged -> conjunto de papeis OBRIGATORIOS (deterministico por match de path)."""
    req: set = set()
    for p in paths:
        p = p.replace("\\", "/").strip()
        for item in manifest.get("matriz", []):
            m = item.get("match", {})
            hit = (("suffix" in m and p.endswith(m["suffix"]))
                   or ("prefix" in m and p.startswith(m["prefix"]))
                   or ("exact" in m and p == m["exact"]))
            if hit:
                req.update(item.get("exige", []))
    return req


def load_evidence(qa_dir: str = QA_DIR) -> list:
    out = []
    if os.path.isdir(qa_dir):
        for f in os.listdir(qa_dir):
            if f.endswith(".json"):
                try:
                    out.append(json.load(open(os.path.join(qa_dir, f), encoding="utf-8")))
                except Exception:
                    pass
    return out


def _atestacao_valida(v) -> bool:
    """Veredito aprovativo COM atestacao de isolamento (agentId + modelo != autor)."""
    if v.get("recomendacao") not in APPROVING:
        return False
    at = v.get("atestacao") or {}
    agent = str(at.get("agentId", "")).strip()
    modelo = str(at.get("modelo", "")).strip()
    autor = str(at.get("autor", "") or at.get("modelo_autor", "")).strip()
    return bool(agent and modelo and (not autor or modelo != autor))


def _cobre(escopo, path: str) -> bool:
    """O escopo declarado no veredito cobre este path? Prefixo exato ou path exato."""
    p = path.replace("\\", "/").strip()
    for e in escopo:
        e = str(e).replace("\\", "/").strip()
        if not e:
            continue
        if e.endswith("/"):
            if p.startswith(e):
                return True
        elif p == e or p.startswith(e + "/"):
            return True
    return False


def _git(*args):
    """git no ROOT. Devolve stdout limpo, ou None se o comando falhar/git ausente."""
    import subprocess
    try:
        r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    except (OSError, ValueError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def _recente_o_bastante(v, paths) -> bool:
    """O veredito cobre o ESTADO ATUAL dos paths, ou e' anterior a eles? (ADR-103 emenda 3)

    Achado BLOQUEANTE da 7a rodada (2026-08-14), reproduzido ao vivo: o gate conferia
    recomendacao aprovativa, atestacao e ESCOPO — e nada mais. Um veredito gravado as 22:50
    seguia liberando `tools/test_squad_gate.py` e `tools/run_canaries.py` depois de eles
    serem modificados as 22:55, indefinidamente. Escopo diz O QUE foi revisado; nao diz
    QUANDO. Sem esta checagem, "revisado uma vez" virava "liberado para sempre" — a mesma
    doenca dos achados B2/B2-r2 e da emenda 2, agora no papel `qa_critic`.

    Criterio: **ancestralidade de commit, nao timestamp.** Timestamp se reordena em rebase e
    depende do relogio de quem gravou; ancestralidade e' fato do grafo. Para cada path
    avaliado, o ultimo commit que o tocou tem de ser ancestral-ou-igual ao `sha_revisado`
    declarado no veredito.

    Fail-closed: veredito SEM `sha_revisado` nao passa. Evidencia que nao diz sobre qual
    estado do codigo foi emitida nao e' evidencia — e' data sem denominador.
    """
    sha = str(v.get("sha_revisado", "") or "").strip()
    if not sha:
        return False
    if _git("cat-file", "-e", sha + "^{commit}") is None:
        return False  # sha declarado nao existe neste repo -> nao serve de prova
    for p in paths:
        ultimo = _git("log", "-1", "--format=%H", "--", p)
        if ultimo is None:
            return False          # sem git/erro -> fail-closed
        if not ultimo:
            # Path SEM historico no git (arquivo novo, staged ou untracked). A 8a rodada
            # pegou aqui o gemeo do defeito que esta funcao conserta: antes isto era
            # `continue`, e um veredito de escopo amplo (ex.: "tools/") com sha valido
            # liberava um arquivo que NENHUM critico jamais viu — "revisado uma vez =
            # liberado para sempre" virava "nunca revisado = liberado mesmo assim".
            # Conteudo que nao existe em nenhum commit nao pode estar coberto por um
            # veredito ancorado num commit. Fail-closed.
            return False
        if _git("merge-base", "--is-ancestor", ultimo, sha) is None:
            return False          # ultimo commit do path NAO e' ancestral do revisado
    return True


def _qa_critic_attested(artifacts, paths=None) -> bool:
    """Existe veredito qa-critic APROVATIVO, ATESTADO **e ESCOPADO** aos paths avaliados?

    ADR-103 emenda 1 (achado BLOQUEANTE 2 da 2a rodada, 2026-08-13): a versao anterior varria
    TODOS os .json de _meta/qa/ e bastava UM veredito aprovativo em qualquer lugar do historico
    para liberar QUALQUER mudanca futura. Uma vez commitada a evidencia, o gate nunca mais
    barrava nada — "gate que se auto-libera para sempre".

    Agora o veredito precisa DECLARAR o que revisou (`escopo_paths`) e o escopo precisa COBRIR
    todos os paths avaliados. Veredito SEM `escopo_paths` NAO conta (fail-closed): evidencia
    antiga nao vale como carta-branca retroativa.
    """
    if paths is None:
        paths = []
    alvo = [str(p).replace("\\", "/").strip() for p in paths if str(p).strip()]
    for v in artifacts:
        if not _atestacao_valida(v):
            continue
        escopo = v.get("escopo_paths") or []
        if not escopo:
            continue  # sem escopo declarado -> nao serve de evidencia (fail-closed)
        if not all(_cobre(escopo, p) for p in alvo):
            continue
        # escopo cobre, mas o veredito e' anterior as edicoes? (emenda 3, 7a rodada)
        if _recente_o_bastante(v, alvo):
            return True
    return False


def _paths_sem_cobertura(artifacts, paths) -> list:
    """Quais paths avaliados NENHUM veredito atestado cobre — para a mensagem de erro ser util."""
    escopos = [v.get("escopo_paths") or [] for v in artifacts if _atestacao_valida(v)]
    orfaos = []
    for p in paths:
        p = str(p).replace("\\", "/").strip()
        if not any(_cobre(e, p) for e in escopos if e):
            orfaos.append(p)
    return orfaos


def _release_junction_closed(artifacts=None) -> bool:
    """Existe junção de FECHAMENTO (PC ou J6) **ainda válida** para o release do topo do CHANGELOG?

    ADR-103: enquanto o gate era advisory, `juncao_release` ficava sempre False ("delegado").
    Ao ATIVAR o gate isso vira bloqueio permanente de todo release — defeito que só a ativação
    revela. Aqui o papel passa a ser VERIFICÁVEL: lê o ledger de junções (ADR-077) e exige o
    fechamento declarado para a versão que o CHANGELOG está publicando.

    ADR-103 emenda 2 (achado BLOQUEANTE da 3a rodada, 2026-08-13): a versão anterior olhava só a
    PRESENÇA do registro no ledger. Como o ledger é append-only e o registro é escrito UMA vez,
    um PC gravado no primeiro commit da série continuava liberando o papel depois de o QA
    REPROVAR o release — sem noção de recência nem de invalidação. Foi reproduzido ao vivo neste
    próprio repo: o único registro de `v1.79.0` foi escrito em `4faf971` (1o commit), seu campo
    `evidencia` diz "REPROVOU a 1a rodada", vieram 10 commits e 2 reprovações depois, e
    `squad_gate --paths CHANGELOG.md` respondia OK. É a mesma classe do achado B2/B2-r2
    (evidência antiga virando carta-branca permanente), reaberta no papel irmão.

    Agora o fechamento exige DUAS coisas, não uma: (a) o registro PC/J6 no ledger **e** (b) um
    veredito APROVATIVO E ATESTADO cujo `release` seja essa mesma versão. Reprovação vigente
    invalida a junção — que é o que "fechamento" sempre quis dizer. Fail-closed: sem veredito
    aprovativo para a versão, o papel não passa, mesmo com o registro no ledger.
    """
    ch = os.path.join(ROOT, "CHANGELOG.md")
    if not os.path.isfile(ch):
        return False
    m = re.search(r"^##\s*\[(\d+\.\d+\.\d+)\]", open(ch, encoding="utf-8").read(), re.M)
    if not m:
        return False
    versao = m.group(1)
    # ANCORADO (achado GRAVE 3 da 2a rodada): substring livre casava versao errada —
    # "1.79.0" in "release-21.79.0-x" e True, e "1.7" casaria dentro de "1.79.0".
    # Exige inicio do bloco, com "v" opcional, e um separador (ou fim) logo apos a versao.
    padrao = re.compile(r"^v?" + re.escape(versao) + r"(?![\d.])")
    led_dir = os.path.join(QA_DIR, "junctions")
    if not os.path.isdir(led_dir):
        return False
    for fn in os.listdir(led_dir):
        if not fn.endswith(".jsonl"):
            continue
        for line in open(os.path.join(led_dir, fn), encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue  # fail-closed em linha corrompida: não conta como fechamento
            if rec.get("junction") in ("PC", "J6") and padrao.match(str(rec.get("bloco", ""))):
                # (b) o registro só vale se o veredito VIGENTE do release for aprovativo e atestado.
                return _release_verdict_approving(artifacts or [], padrao)
    return False


def _release_verdict_approving(artifacts, padrao) -> bool:
    """Algum veredito ATESTADO e APROVATIVO declara este release? (emenda 2 do ADR-103)

    `padrao` já vem ancorado na versão do topo do CHANGELOG. Casa contra o campo `release` do
    veredito (gravado como "1.79.0") e, por tolerância, contra `bloco` (gravado como
    "release-1.79.0-..."), sem cair em substring solta.
    """
    for v in artifacts:
        if not _atestacao_valida(v):        # já exige recomendacao aprovativa + agentId + modelo != autor
            continue
        rel = str(v.get("release", "")).strip()
        if rel and padrao.match(rel):
            return True
        bloco = str(v.get("bloco", "")).strip()
        if bloco.startswith("release-") and padrao.match(bloco[len("release-"):]):
            return True
    return False


def evaluate(paths, manifest, artifacts):
    """Retorna (faltam, detalhe). faltam=[] => gate PASSA."""
    required = classify(paths, manifest)
    faltam, detalhe = [], {}
    for role in sorted(required):
        if role == "qa_critic":
            ok = _qa_critic_attested(artifacts, paths)
        elif role == "architect":
            ok = any(str(p).replace("\\", "/").startswith("docs/adr/") for p in paths)
        elif role == "juncao_release":
            ok = _release_junction_closed(artifacts)
        else:
            # research_ou_ratificacao: delegado (research_evidence.py).
            # Marca como EXIGIDO-nao-verificavel-localmente -> falta (fail-closed) ate o check proprio rodar.
            ok = False
        detalhe[role] = ok
        if not ok:
            faltam.append(role)
    return faltam, detalhe


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", nargs="*", help="paths a avaliar (default: git diff --cached)")
    ap.add_argument("--paths-from", help="arquivo com 1 path por linha. Preferir no CI: imune a "
                                         "espaco em nome de arquivo e ao limite de argv "
                                         "(achado MEDIO 4 da 2a rodada)")
    a = ap.parse_args(argv)
    paths = a.paths
    if a.paths_from:
        with open(a.paths_from, encoding="utf-8") as fh:
            paths = [x.strip() for x in fh if x.strip()]
    if paths is None:
        r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                           capture_output=True, text=True, cwd=ROOT)
        paths = [x for x in r.stdout.splitlines() if x.strip()]
    manifest = load_manifest()
    artifacts = load_evidence()
    faltam, detalhe = evaluate(paths, manifest, artifacts)
    req = classify(paths, manifest)
    print(f"[squad-gate] {len(paths)} path(s) staged -> papeis exigidos: {sorted(req) or 'nenhum'}")
    for role, ok in detalhe.items():
        print(f"   {'OK ' if ok else 'FALTA'} {role}")
    if faltam:
        print(f"[squad-gate] BLOQUEADO (fail-closed): faltam evidencias atestadas: {faltam}")
        if "qa_critic" in faltam:
            orfaos = _paths_sem_cobertura(artifacts, paths)
            if orfaos:
                print(f"   paths SEM veredito que os cubra ({len(orfaos)}): {orfaos[:10]}")
            else:
                print("   ha veredito atestado, mas nenhum DECLARA escopo_paths cobrindo estes paths.")
        print("   -> rode o papel (ex.: qa-critic isolado) e registre via tools/qa_evidence.py")
        print("      com atestacao E com o campo escopo_paths listando o que foi revisado.")
        return 1
    print("[squad-gate] OK — evidencia atestada presente para os papeis exigidos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
