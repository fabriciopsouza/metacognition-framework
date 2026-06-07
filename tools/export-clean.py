#!/usr/bin/env python3
"""Pipeline de EXPORT privado → público (determinístico, auto-verificável).

Produz uma árvore LIMPA publicável a partir da fonte privada full:
  1. copia a árvore (sem .git);
  2. remove o cofre `docs/_private/` (não vai ao público);
  3. anonimiza via `tools/anonymize.py` (regras determinísticas);
  4. GATE: `check_core_agnostic.py --sensitive` — se QUALQUER token de cliente sobreviver,
     ABORTA (exit 1). É o que garante que o "automático" nunca publica vazamento;
  5. remove a infra de limpeza (denylist/map/scripts contêm os tokens reais).

Uso:
    python tools/export-clean.py <out-dir>

Exit 0 + árvore limpa em <out-dir>; exit 1 se o gate falhar (adicione regra em anonymize-map.txt).
Sem dependências externas (stdlib).
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.path.dirname(HERE)

STRIP_BEFORE = ["docs/_private", ".git"]            # cofre + história não vão ao público
STRIP_AFTER_VERIFY = [                               # infra de limpeza: carrega tokens reais
    "tools/sensitive-denylist.txt",
    "tools/anonymize-map.txt",
    "tools/anonymize.py",
    "tools/export-clean.py",
    "tools/test_core_agnostic.py",                   # canário interno: tokens split + dep da denylist
    "tools/test_premium_tier.py",                    # canário interno: testa o pipeline de tiering (depende de export-clean)
    ".github/workflows/publish-clean.yml",
]

# Camada PREMIUM (ADR-049): removida nas distribuições BASELINE (public/non-admin), MANTIDA na premium.
# É só EXPERIÊNCIA (proposta proativa de produto + UX premium); NÃO toca análise/discovery/QA (core).
PREMIUM_STRIP_FILES = [
    "exemplos/dominio-software/blueprint.md",
    "exemplos/dominio-processo/blueprint.md",
    "exemplos/dominio-projeto/blueprint.md",
    # ADR-050 — elaboração de documentos premium (gerador + canário + templates):
    "tools/gen_exec_doc.py",
    "tools/test_gen_exec_doc.py",
    "docs/specs/_template-documentos",
    # ADR-050 emenda — piso de validação (gate premium). make_index é BASELINE (usabilidade) e fica.
    "tools/check_delivery_floor.py",
    "tools/test_delivery_floor.py",
]
# Arquivos com seções premium marcadas (<!-- premium:start --> ... <!-- premium:end -->).
PREMIUM_MARKER_FILES = [
    ".agent/skills/discovery/SKILL.md",
    "exemplos/dominio-software/ux-designer/SKILL.md",
]


def strip_premium_markers(path):
    """Remove linhas entre <!-- premium:start --> e <!-- premium:end --> (inclusive)."""
    if not os.path.isfile(path):
        return
    out, skip = [], False
    for ln in open(path, encoding="utf-8").read().splitlines(keepends=True):
        low = ln.lower()
        if "premium:start" in low:
            skip = True
            continue
        if "premium:end" in low:
            skip = False
            continue
        if not skip:
            out.append(ln)
    with open(path, "w", encoding="utf-8") as fh:
        fh.writelines(out)


def strip_premium(out_root):
    """Aplica o strip da camada premium na árvore de export (baseline)."""
    for rel in PREMIUM_STRIP_FILES:
        _rm(os.path.join(out_root, *rel.split("/")))
    for rel in PREMIUM_MARKER_FILES:
        strip_premium_markers(os.path.join(out_root, *rel.split("/")))


def rewrite_repo_urls(out_root, target):
    """Self-reference por distribuição: após anonymize (tudo vira `-public`), aponta clone/releases/raw
    para o repo DESTA distribuição. github.io (site Pages) fica em `-public` (site compartilhado)."""
    src = "fabriciopsouza/metacognition-framework-public"          # estado pós-anonymize
    dst = f"fabriciopsouza/{target}"
    if src == dst:
        return
    for dirpath, dirnames, files in os.walk(out_root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in files:
            p = os.path.join(dirpath, fn)
            try:
                txt = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue                                           # binário/ilegível: pula
            if src in txt:                                         # não casa github.io (path sem `owner/`)
                open(p, "w", encoding="utf-8").write(txt.replace(src, dst))


def strip_pycache(root):
    """Remove todo __pycache__ (bytecode cacheado vaza caminhos internos; nunca distribuir)."""
    for dirpath, dirnames, _ in os.walk(root):
        for d in list(dirnames):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(dirpath, d))
                dirnames.remove(d)


def _rm(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def run(cmd, cwd=None):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd).returncode


def stamp_shadow_identity(out_root):
    """TRAVA FISICA (ADR-070): carimba .repo-identity.json como role=shadow no export.
    Assim TODO export/sombra se auto-identifica -> repo_identity.py classifica SOMBRA-EXPORT,
    nunca MASTER-CANONICO. Fecha o falso-MASTER (uma sombra que copiasse o marker do master
    seria classificada master). O carimbo sobrescreve qualquer marker herdado da copia."""
    import json
    remote = "https://github.com/fabriciopsouza/metacognition-framework"
    branch, owner = "main", "claude"
    try:
        with open(os.path.join(SRC_ROOT, ".repo-identity.json"), encoding="utf-8") as fh:
            m = json.load(fh)
        remote = m.get("canonical_remote", remote)
        branch = m.get("canonical_branch", branch)
        owner = m.get("ai_owner", owner)
    except Exception:
        pass
    shadow = {
        "schema_version": "1.0",
        "role": "shadow",
        "ai_owner": owner,
        "canonical_remote": remote,
        "canonical_branch": branch,
        "derived_from": "metacognition-framework (master)",
        "note": "Distribuicao derivada via export-clean (ADR-049/070). NAO e master; deriva do "
                "master sem vida propria. repo_identity classifica SOMBRA-EXPORT; escrita exige confirmacao.",
    }
    with open(os.path.join(out_root, ".repo-identity.json"), "w", encoding="utf-8") as fh:
        json.dump(shadow, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    nonadmin = ("--nonadmin" in argv) or ("nonadmin" in argv and "--variant" in argv)
    premium = "--premium" in argv
    web = ("--web" in argv) or ("web" in args)
    if not args:
        print("uso: python tools/export-clean.py <out-dir> [--nonadmin | --premium | --web]", file=sys.stderr)
        return 2

    # PROFILE WEB (ADR-054/057): forma de saída distinta (prompts/skills chat, não repo full).
    # Delega ao gerador dedicado web_export (determinístico, com gate anti-JARVIS).
    if web:
        sys.path.insert(0, HERE)
        import web_export
        out_web = os.path.abspath(args[0])
        return web_export.main(["web_export", out_web])
    out = os.path.abspath(args[0])
    if os.path.abspath(out) == os.path.abspath(SRC_ROOT):
        print("out-dir nao pode ser a propria fonte", file=sys.stderr)
        return 2
    if os.path.exists(out):
        shutil.rmtree(out)

    # 1. copia
    shutil.copytree(SRC_ROOT, out, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    strip_pycache(out)
    # 2. strip cofre/história
    for rel in STRIP_BEFORE:
        _rm(os.path.join(out, *rel.split("/")))
    # 3. anonimiza
    py = sys.executable
    if run([py, os.path.join(out, "tools", "anonymize.py"), out]) != 0:
        print("anonymize falhou", file=sys.stderr)
        return 1
    # 4. GATE determinístico — denylist ainda presente em out/tools/
    if run([py, "tools/check_core_agnostic.py", "--sensitive"], cwd=out) != 0:
        print("\nGATE FALHOU: token de cliente sobreviveu ao anonymize.", file=sys.stderr)
        print("Adicione a regra correspondente em tools/anonymize-map.txt e rode de novo.", file=sys.stderr)
        return 1
    # 5. strip infra de limpeza (contém tokens reais)
    for rel in STRIP_AFTER_VERIFY:
        _rm(os.path.join(out, *rel.split("/")))

    # 6. GATE de transparência (ADR-044) na árvore PÓS-STRIP — o estado que o público recebe.
    #    Sem isto, o público pode receber um LIMITS.md que falha o próprio --check (canário interno
    #    removido no passo 5 desincronizava o doc). build_limits trata canário interno como
    #    determinístico (não-distribuído), então aqui deve passar; se falhar, NÃO publica.
    if run([py, "tools/build_limits.py", "--check"], cwd=out) != 0:
        print("\nGATE FALHOU: LIMITS.md fora de sync na arvore publica. Regenere (build_limits.py --out LIMITS.md).", file=sys.stderr)
        return 1
    if run([py, "tools/test_marketing_claims.py"], cwd=out) != 0:
        print("\nGATE FALHOU: claim de marketing orfao / LIMITS desync no pacote publico.", file=sys.stderr)
        return 1

    # 6a-bis. INDICE DE CAPACIDADES no shadow (ADR-072/070, PROCESSO — nao remendo): poda entradas
    #   cujo ponteiro foi stripado (ex.: doc em docs/_private/cross-ai) + regenera o CAPABILITIES.md +
    #   valida (canario). Assim o shadow recebe um indice HONESTO e verde a CADA publish (o premium/
    #   public ganha index+guards automaticamente, sem cross-IA, conforme o design).
    if run([py, "tools/build_capabilities.py", "--prune"], cwd=out) != 0:
        print("\nGATE FALHOU: prune do indice de capacidades para o shadow.", file=sys.stderr)
        return 1
    if run([py, "tools/test_capabilities.py"], cwd=out) != 0:
        print("\nGATE FALHOU: indice de capacidades inconsistente no pacote shadow.", file=sys.stderr)
        return 1

    # 6b. TIER (ADR-049): BASELINE (public/non-admin) remove a camada PREMIUM; a distribuição PREMIUM mantém.
    #     Premium = só EXPERIÊNCIA (proposta proativa + UX premium); análise/discovery/QA/segurança = core (ficam em todas).
    if premium:
        print("TIER: PREMIUM (camada premium mantida — ADR-049).")
        rewrite_repo_urls(out, "metacognition-framework-premium")
    else:
        strip_premium(out)
        print("TIER: BASELINE (camada premium removida: blueprints + seções premium).")

    # 7. VARIANTE non-admin (ADR-047): mesma fonte, característica própria = settings.json SEM hooks.
    #    Single-source -> multi-distribuicao: o admin mantem os hooks; o non-admin inicia sob restricao.
    if nonadmin:
        settings = os.path.join(out, ".claude", "settings.json")
        os.makedirs(os.path.dirname(settings), exist_ok=True)
        with open(settings, "w", encoding="utf-8") as fh:
            fh.write('{\n  "$schema": "https://json.schemastore.org/claude-code-settings.json"\n}\n')
        _rm(os.path.join(out, ".claude", "settings.nonadmin.json"))  # redundante no pacote non-admin
        rewrite_repo_urls(out, "metacognition-framework-public-nonadmin")
        print("VARIANTE: NON-ADMIN (settings.json sem hooks; gates anunciados pelo agente — ADR-047).")

    # 8. TRAVA FISICA de identidade (ADR-070): a arvore exportada se auto-declara SOMBRA.
    stamp_shadow_identity(out)
    print("IDENTITY: .repo-identity.json carimbado role=shadow (ADR-070).")

    print(f"\nEXPORT OK: arvore limpa publicavel em {out}{' [NON-ADMIN]' if nonadmin else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
