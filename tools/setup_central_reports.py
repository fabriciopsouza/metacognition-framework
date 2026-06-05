#!/usr/bin/env python3
"""setup_central_reports.py — setup do repo central de relatórios em 1 comando, GUIADO (ADR-064).

Para o DONO rodar 1x. Faz tudo: cria o repo público, instala o CI validador, liga auto-merge,
e grava o slug no seu consent.json (para o auto-publish saber onde publicar). ORIENTA em cada passo
e FALHA-SOFT com instrução clara (ex.: se faltar `gh auth login`, diz exatamente o que fazer).

Uso:  python tools/setup_central_reports.py [--name metacognition-exec-reports] [--yes]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys


def say(msg):
    print(msg)


def run(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="metacognition-exec-reports", help="nome do repo central")
    ap.add_argument("--yes", action="store_true", help="não perguntar confirmação")
    a = ap.parse_args(argv[1:])
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    say("=" * 64)
    say("  SETUP DO REPO CENTRAL DE RELATÓRIOS (ADR-064) — 1 comando, guiado")
    say("=" * 64)
    say("  O que isto faz, automaticamente:")
    say(f"   1) cria o repo PÚBLICO '{a.name}' na sua conta (onde os relatórios anonimizados chegam);")
    say("   2) instala o CI que re-valida cada contribuição (append-only + anti-PII);")
    say("   3) liga o AUTO-MERGE (PR válido entra sozinho);")
    say("   4) grava o endereço do repo no seu opt-in (para o envio automático saber o destino).")
    say("  Nada é destrutivo. Pode rodar de novo (idempotente).")
    say("-" * 64)

    # Passo 0 — pré-requisito: gh instalado e autenticado. ORIENTA se faltar.
    if not shutil.which("gh"):
        say("✗ Falta o GitHub CLI (`gh`). Instale: https://cli.github.com  — depois rode este comando de novo.")
        return 1
    if run(["gh", "auth", "status"]).returncode != 0:
        say("✗ Você não está logado no GitHub CLI. Rode:  gh auth login   — e depois este comando de novo.")
        return 1
    me = run(["gh", "api", "user", "-q", ".login"]).stdout.strip()
    if not me:
        say("✗ Não consegui identificar seu usuário GitHub. Verifique `gh auth status` e tente de novo.")
        return 1
    slug = f"{me}/{a.name}"
    say(f"✓ GitHub CLI ok — usuário '{me}'. Repo alvo: {slug}")

    if not a.yes:
        try:
            if input(f"  Criar/configurar '{slug}' agora? [s/N] ").strip().lower() not in ("s", "sim", "y"):
                say("  Cancelado. Nada foi feito."); return 0
        except EOFError:
            say("  (não-interativo: use --yes para confirmar)"); return 1

    # Passo 1 — criar o repo (idempotente: ignora 'já existe').
    r = run(["gh", "repo", "create", slug, "--public",
             "--description", "Corpus de relatórios de execução anonimizados (ADR-063/064)"])
    if r.returncode != 0 and "already exists" not in (r.stderr + r.stdout).lower() and "name already" not in (r.stderr + r.stdout).lower():
        say(f"✗ Falha ao criar o repo: {r.stderr.strip()[:200]}\n  (Se já existe, ok. Senão, verifique permissões e tente de novo.)")
    else:
        say(f"✓ Repo '{slug}' pronto.")

    # Passo 2 — instalar o CI validador (do template) no repo central, via API.
    tpl = os.path.join(here, "tools", "templates", "central-reports-ci.yml")
    try:
        import base64
        content = base64.b64encode(open(tpl, encoding="utf-8").read().encode("utf-8")).decode("ascii")
        run(["gh", "api", "--method", "PUT", f"repos/{slug}/contents/.github/workflows/ci.yml",
             "-f", "message=CI validador de relatórios (ADR-064)", "-f", f"content={content}"])
        say("✓ CI validador instalado (.github/workflows/ci.yml).")
    except Exception as e:
        say(f"⚠ Não instalei o CI automaticamente ({e}). Copie manualmente:\n    {tpl}\n  para `.github/workflows/ci.yml` no repo {slug}.")

    # Passo 3 — ligar auto-merge no repo (best-effort; orienta se falhar).
    am = run(["gh", "api", "--method", "PATCH", f"repos/{slug}",
              "-F", "allow_auto_merge=true", "-F", "delete_branch_on_merge=true"])
    if am.returncode == 0:
        say("✓ Auto-merge ligado.")
    else:
        say(f"⚠ Não liguei o auto-merge via API. Ligue à mão: {slug} → Settings → General → marque 'Allow auto-merge'.")
    say(f"  (Opcional, recomendado: Settings → Branches → proteja a 'main' exigindo o check 'validate-reports'.)")

    # Passo 4 — gravar o slug no consent.json (para o auto-publish saber o destino).
    cpath = os.path.join(os.path.expanduser("~"), ".claude", "exec-report-consent.json")
    try:
        data = {}
        if os.path.isfile(cpath):
            data = json.load(open(cpath, encoding="utf-8"))
        data["central_repo"] = slug
        os.makedirs(os.path.dirname(cpath), exist_ok=True)
        json.dump(data, open(cpath, "w", encoding="utf-8"), ensure_ascii=True, indent=2)
        say(f"✓ Destino salvo no seu opt-in ({cpath}).")
    except Exception as e:
        say(f"⚠ Não gravei o destino no consent.json ({e}). Defina o env FRAMEWORK_REPORTS_REPO={slug}.")

    say("-" * 64)
    say(f"  PRONTO. A partir de agora, no fim de cada sessão (se opt-in), seus relatórios")
    say(f"  anonimizados vão sozinhos para  https://github.com/{slug}  — você não faz mais nada.")
    say("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
