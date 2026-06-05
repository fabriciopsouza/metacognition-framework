#!/usr/bin/env python3
"""web_export.py — gera o PACOTE WEB do framework a partir do main (ADR-054/056/057).

Chamado por `export-clean.py --profile web` (ou direto). Produz, de forma DETERMINÍSTICA, a
encarnação chat-sem-filesystem do framework, em dois tiers:

  PÚBLICO  -> out/publico/prompt-web-publico.md
             (o prompt autocontido canônico `PROMPT-CHAT-WEB-v4.4.md`, carimbado com a versão do main)

  PREMIUM  -> out/premium/prompt-web-premium.md  +  out/premium/skills/<nome>/SKILL.md
             skills ENXUTAS geradas do FRONT-MATTER (description = gatilho de auto-trigger;
             pass_criteria = checkpoint declarado; encadeamento = ordem do pipeline). O corpo IDE
             NÃO é copiado (referencia hooks/tools/_shared — inerte no chat); o método detalhado
             vive no prompt público. Premium agrega AUTO-TRIGGER + encadeamento de papéis.

Doutrina enforcement.chat / anti-JARVIS (ADR-054): vocabulário de enforcement é reescrito via
`web-phrasing-map.txt`; um GATE final (FORBIDDEN do mapa) FALHA o build se sobrar asserção de
mecanismo que o chat não executa. Determinístico: sem relógio; iteração ordenada.

Uso: python tools/web_export.py <out-dir>     # exit 0 ok; 1 gate/erro
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.path.dirname(HERE)
MAP_PATH = os.path.join(HERE, "web-phrasing-map.txt")
PUBLIC_SRC = os.path.join(SRC_ROOT, "PROMPT-CHAT-WEB-v4.4.md")

# Pipeline canônico (ADR-056): ordem fixa; explorer é lateral (read-only, sem sucessor).
PIPELINE = ["pmo", "discovery", "architect", "developer", "qa-critic", "docops"]
LATERAL = ["explorer"]
# Transversais _shared (atômicos, referenciados — não encadeiam). doc-intake/execution-modes
# NÃO entram (substituídos por declaração no chat — ADR-056).
SHARED = ["anti-hallucination", "confidence-classification", "traceability", "output-format",
          "metacognition-core", "action-safety", "high-stakes-gate", "observability"]


def load_map(path=MAP_PATH):
    """Retorna (rules, forbidden). rules = [(regex, repl)]; forbidden = [regex]."""
    rules, forbidden = [], []
    if not os.path.isfile(path):
        return rules, forbidden
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" not in line:
            continue
        a, b = line.split("\t", 1)
        if a == "FORBIDDEN":
            forbidden.append(re.compile(b, re.IGNORECASE))
        else:
            try:
                rules.append((re.compile(a, re.IGNORECASE), b))
            except re.error:
                pass
    return rules, forbidden


def phrase(text, rules):
    for rx, repl in rules:
        text = rx.sub(repl, text)
    return text


def main_version():
    """Lê 'Versão: X.Y.Z' do README do main (carimbo anti-defasagem — REQ-CASCADE-5)."""
    try:
        txt = open(os.path.join(SRC_ROOT, "README.md"), encoding="utf-8").read()
        m = re.search(r"Vers[ãa]o:\**\s*([0-9]+\.[0-9]+\.[0-9]+)", txt)
        if m:
            return m.group(1)
    except OSError:
        pass
    return "0.0.0"


def read_frontmatter(path):
    """Parse mínimo do front-matter YAML (name/description/pass_criteria/role_order)."""
    fm = {}
    if not os.path.isfile(path):
        return fm
    lines = open(path, encoding="utf-8").read().splitlines()
    if not lines or lines[0].strip() != "---":
        return fm
    for ln in lines[1:]:
        if ln.strip() == "---":
            break
        m = re.match(r'^(name|description|pass_criteria|role_order):\s*"?(.*?)"?\s*$', ln)
        if m:
            fm[m.group(1)] = m.group(2)
    return fm


def skill_path(name):
    """Papel vive em .agent/skills/; transversal em _shared/."""
    role = os.path.join(SRC_ROOT, ".agent", "skills", name, "SKILL.md")
    return role if os.path.isfile(role) else os.path.join(SRC_ROOT, "_shared", name, "SKILL.md")


def discovery_submodes():
    """Lista os companions do discovery (sub-modos) a partir dos nomes de arquivo (determinístico)."""
    d = os.path.join(SRC_ROOT, ".agent", "skills", "discovery")
    if not os.path.isdir(d):
        return []
    return sorted(f[:-3] for f in os.listdir(d) if f.endswith(".md") and f != "SKILL.md")


def gen_role_skill(name, version, rules):
    fm = read_frontmatter(skill_path(name))
    desc = phrase(fm.get("description", f"papel {name} do framework"), rules)
    crit = phrase(fm.get("pass_criteria", "entrega cobre o objetivo declarado"), rules)
    # encadeamento determinístico
    if name in PIPELINE:
        i = PIPELINE.index(name)
        nxt = PIPELINE[i + 1] if i + 1 < len(PIPELINE) else None
    else:
        nxt = None
    L = ["---", f"name: {name}", f'description: "{desc}"', "---",
         f"# {name} — papel do framework (chat) · v{version}", "",
         "## Quando aplicar (gatilho)", desc, "",
         "## Critério de conclusão (checkpoint declarado, não enforcement)",
         f"{crit}",
         "> Ressalva de ambiente: no chat isto é um checkpoint declarado — não há gate automático "
         "(ver Matriz de ambiente do prompt público). Efeito T3 (irreversível/alto impacto) sempre confirma.", "",
         "## Encadeamento (chat)"]
    if name == "discovery":
        subs = discovery_submodes()
        L.append(f"- Sub-modos (roteie internamente por intenção): {', '.join(subs)}.")
    if nxt:
        L.append(f"- Próxima: **{nxt}** (condição: PASS do critério acima).")
    if name == "developer":
        L.append("- **NUNCA** trate a entrega como final: aplique **qa-critic** antes de qualquer aprovação (hipótese default = há bug).")
    if name in PIPELINE and PIPELINE.index(name) > 0:
        L.append(f"- Rewind declarado: se o critério falhar, volte ao papel anterior (**{PIPELINE[PIPELINE.index(name)-1]}**).")
    if not nxt and name in PIPELINE:
        L.append("- Fim do pipeline: encerrar bloco (checkpoint de release declarado).")
    L.append("- explorer é chamável lateralmente para leitura (read-only), sem sucessor fixo.")
    return "\n".join(L) + "\n"


def gen_shared_skill(name, version, rules):
    fm = read_frontmatter(skill_path(name))
    desc = phrase(fm.get("description", f"regra transversal {name}"), rules)
    L = ["---", f"name: {name}", f'description: "{desc}"', "---",
         f"# {name} — regra transversal do framework (chat) · v{version}", "",
         "## Quando aplicar", desc, "",
         "## Natureza", "Regra transversal **atômica**: referenciada por todos os papéis, nunca recopiada. "
         "É invariante (não é gate de runtime; vale por leitura). Anti-alucinação e preservação não cedem.", ""]
    return "\n".join(L) + "\n"


def gen_orchestrator(version, rules):
    roles = " → ".join(PIPELINE)
    L = [f"# Orquestrador Premium — Pacote Web do Framework Metacognitivo · v{version}", "",
         "> Tier PREMIUM: este prompt é ENXUTO — **referencia** as skills instaladas, não recopia regra.",
         "> Pré-requisito: o prompt público (tier base) cobre o método/validação/precedência; este apenas",
         "> orquestra os papéis via skills nativas. Sem filesystem: papéis/subagentes SIMULADOS (anti-JARVIS).", "",
         "## Roteamento", "- Pontual técnico → modo metacognição (decompor → classificar → validar → refletir).",
         f"- Multi-etapa → modo squad (papéis encadeados): **{roles}**; explorer lateral (leitura).",
         "- Cada skill declara seu gatilho (auto-trigger por intenção) e o próximo papel (encadeamento).", "",
         "## Skills deste pacote",
         "**Papéis:** " + ", ".join(PIPELINE + LATERAL) + ".",
         "**Transversais (sempre ativas, referenciadas):** " + ", ".join(SHARED) + ".", "",
         "## Invariantes (enforcement.chat)",
         "- Onde a IDE barra, aqui declaro checkpoint + ressalva; **nunca finjo mecanismo** (anti-JARVIS).",
         "- Anti-alucinação e preservação de trabalho aprovado não cedem.",
         "- Efeito T3 (irreversível/alto impacto) sempre pede confirmação informada, em qualquer postura.",
         "- 'avançado' é postura de execução; profundidade de discovery é universal/reforço-sênior (não confundir).", ""]
    return "\n".join(L) + "\n"


def anti_jarvis_gate(out_dir, forbidden):
    """Falha (lista de violações) se algum padrão FORBIDDEN sobrevive no output gerado."""
    violations = []
    for dirpath, _, files in os.walk(out_dir):
        for fn in sorted(files):
            p = os.path.join(dirpath, fn)
            try:
                txt = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            for rx in forbidden:
                for m in rx.finditer(txt):
                    rel = os.path.relpath(p, out_dir)
                    violations.append(f"{rel}: '{m.group(0)[:60]}'")
    return violations


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


def build(out_dir):
    rules, forbidden = load_map()
    version = main_version()

    # PÚBLICO — prompt canônico carimbado
    if os.path.isfile(PUBLIC_SRC):
        pub = phrase(open(PUBLIC_SRC, encoding="utf-8").read(), rules)
        pub = re.sub(r"(tier público autocontido\.)", rf"\1 (gerado do main v{version})", pub, count=1)
    else:
        pub = f"# prompt-web-publico (FONTE AUSENTE: {os.path.basename(PUBLIC_SRC)})\n"
    write(os.path.join(out_dir, "publico", "prompt-web-publico.md"), pub)

    # PREMIUM — orquestrador + skills
    write(os.path.join(out_dir, "premium", "prompt-web-premium.md"), gen_orchestrator(version, rules))
    for name in PIPELINE + LATERAL:
        write(os.path.join(out_dir, "premium", "skills", name, "SKILL.md"),
              gen_role_skill(name, version, rules))
    for name in SHARED:
        write(os.path.join(out_dir, "premium", "skills", name, "SKILL.md"),
              gen_shared_skill(name, version, rules))

    # READMEs — um por tier (cada dir é um REPO-ROOT distinto: publico/=público, premium/=PRIVADO/pago).
    # Espelha o split não-web (-public × -premium; ADR-049). ADR-054 emendado (ADR-058).
    write(os.path.join(out_dir, "publico", "README.md"),
          f"# metacognition-framework-web · v{version} (tier PÚBLICO — chat, sem filesystem)\n\n"
          "> **GERADO do repo main** (`tools/web_export.py`). **Não editar à mão** (sentido único; ADR-054/057/058).\n\n"
          "Encarnação **chat** do Framework Metacognitivo para ambientes **sem filesystem** (Claude.ai, "
          "Gemini, ChatGPT). Autocontido, grátis (CC BY 4.0).\n\n"
          "## Como usar (3 passos)\n"
          "1. Abra um chat com instruções de projeto: **Claude.ai** (Projects → Instruções), **Gemini** "
          "(Gem → Instruções) ou **ChatGPT** (Custom GPT → Instructions).\n"
          "2. **Cole o conteúdo de `prompt-web-publico.md`** como a instrução de sistema/projeto.\n"
          "3. Converse — o método (classificar confiança, file-first, anti-alucinação, validação, decisões "
          "registradas) já governa as respostas. **Sem instalar nada.**\n\n"
          "## O que esperar (e o que NÃO)\n"
          "- ✅ Método metacognitivo: confiança (CONFIRMADO/INFERIDO/NÃO SEI), validação, anti-fabricação.\n"
          "- ❌ **Sem gates de runtime** (hooks/effect-gate/sync): no chat não há filesystem nem execução — "
          "o método vale por LEITURA, não por mecanismo. Efeito irreversível **sempre pede sua confirmação** "
          "(doutrina anti-JARVIS: nunca finge mecanismo que o chat não executa).\n\n"
          "## Quer mais?\n"
          "- **Squad por papéis no chat** → tier PREMIUM (pago): repo `metacognition-framework-web-premium`.\n"
          "- **Framework COMPLETO (clona e roda, com hooks/tools/gates reais)** → repo "
          "`metacognition-framework` — **esta aqui é só a versão chat, não o full.**\n")
    write(os.path.join(out_dir, "premium", "README.md"),
          f"# metacognition-framework-web-premium · v{version} (tier PREMIUM — chat, PRIVADO/pago)\n\n"
          "> ⚠️ **Esta é a versão CHAT (sem filesystem)** — orquestrador + skills para COLAR no Claude.ai/Gemini.\n"
          "> **Para o framework COMPLETO que clona-e-roda (hooks, tools, gates, bootstrap), use o repo "
          "`metacognition-framework-premium`** (não este).\n"
          "> GERADO do repo main (`tools/web_export.py`) — **não editar à mão**. Privado (acesso pago) — não publicar.\n\n"
          "Tier premium do pacote web: **orquestrador enxuto + 15 skills** (7 papéis + 8 transversais), com "
          "auto-trigger por intenção e encadeamento de papéis.\n\n"
          "## Como usar — Claude.ai Projects (recomendado)\n"
          "1. Crie um **Projeto** no Claude.ai.\n"
          "2. **Instruções do projeto:** cole `prompt-web-premium.md` (o orquestrador).\n"
          "3. **Conhecimento do projeto:** adicione os arquivos `skills/<nome>/SKILL.md` (arraste a pasta "
          "`skills/`). O orquestrador os referencia por nome (auto-trigger).\n"
          "4. Converse: ele roteia (pontual→metacognição · multi-etapa→squad "
          "pmo→discovery→architect→developer→qa-critic→docops) e encadeia os papéis.\n\n"
          "## Gemini / ChatGPT\n"
          "Cole `prompt-web-premium.md` como instrução do Gem/GPT; cole as `SKILL.md` relevantes na conversa "
          "(não têm 'conhecimento de projeto' persistente como o Claude.ai Projects).\n\n"
          "## Config / limites\n"
          "- **Sem filesystem** → papéis/subagentes SIMULADOS (anti-JARVIS: declara checkpoint, **nunca finge** "
          "gate de runtime); efeito irreversível sempre confirma.\n"
          "- Pré-requisito de método: o tier público cobre o transversal; este orquestra.\n"
          "- **Framework FULL (clone-e-roda)** = repo `metacognition-framework-premium`.\n")

    violations = anti_jarvis_gate(out_dir, forbidden)
    return version, violations


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("uso: python tools/web_export.py <out-dir>", file=sys.stderr)
        return 2
    out_dir = os.path.abspath(args[0])
    if out_dir == os.path.abspath(SRC_ROOT):
        print("out-dir nao pode ser a propria fonte", file=sys.stderr)
        return 2
    import shutil
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    version, violations = build(out_dir)
    if violations:
        print("GATE anti-JARVIS FALHOU — asserção de enforcement no output web:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        print("Reescreva em tools/web-phrasing-map.txt e regenere.", file=sys.stderr)
        return 1
    n = len(PIPELINE) + len(LATERAL) + len(SHARED)
    print(f"WEB EXPORT OK (v{version}): publico/prompt-web-publico.md + premium/ ({n} skills) em {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
