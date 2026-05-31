#!/usr/bin/env python3
"""Valida o frontmatter das skills contra o contrato mínimo (ADR-013, v1.14.0).

Gate de CI / pré-merge no ambiente IDE. Espelha o auto-check de 1 linha do chat:
mesma regra, mecanismo diferente (P3 §5 — sem prometer paridade).

Uso:
    python tools/validate_skills.py                # valida o conjunto padrão
    python tools/validate_skills.py <arquivo.md>...  # valida arquivos específicos

Saída: PASS/FAIL por arquivo + resumo. Exit 0 se tudo PASS; exit 1 se qualquer FAIL.
Sem dependências externas: parser de frontmatter e validador de schema são embutidos
(evita exigir PyYAML/jsonschema num repo que é majoritariamente markdown).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(ROOT, "tools", "framework-schema.json")

# Conjunto sob contrato: APENAS os papéis de processo (PMO->release).
# _shared/ são módulos de regra invariante (alvos de `shared_refs`), não papéis do
# pipeline — têm shape próprio (`metadata: type/version/adr`) e ficam FORA do contrato
# de role para não forçar campos que não preencheriam de verdade (P3 §6, régua §0).
DEFAULT_GLOBS = [
    ".agent/skills/*/SKILL.md",
    # Aplicações de domínio bundladas (ADR-023): também honram o contrato de 8 campos.
    "exemplos/*/*/SKILL.md",
]


def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def extract_frontmatter(text):
    """Extrai o bloco YAML entre as primeiras linhas '---'. Retorna (dict, erro)."""
    if not text.startswith("---"):
        return None, "sem frontmatter (arquivo nao comeca com '---')"
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None, "frontmatter nao fechado (falta '---' de fechamento)"
    return parse_simple_yaml(m.group(1)), None


def parse_simple_yaml(block):
    """Parser YAML mínimo suficiente para frontmatter de skill.

    Suporta: chave: valor escalar; chave: (bloco) seguido de '- item' (lista);
    valores entre aspas; booleanos; inteiros; null/~; mapeamentos rasos de 1 nível
    (enforcement: {ide:..., chat:...} tanto inline quanto indentado).
    Não é um YAML completo — é deliberadamente pequeno (régua §0).
    """
    data = {}
    lines = block.split("\n")
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        # chave de topo (sem indentação)
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "" or val == "|" or val == ">" or val == ">-" or val == "|-":
            # pode ser lista, mapa indentado, ou string multilinha; olhar adiante
            j = i + 1
            items = []
            submap = {}
            buf = []
            mode = None
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() == "" and mode != "block":
                    j += 1
                    continue
                indent = len(nxt) - len(nxt.lstrip())
                if indent == 0:
                    break
                s = nxt.strip()
                if s.startswith("- "):
                    mode = "list"
                    items.append(_scalar(s[2:].strip()))
                elif re.match(r"^[A-Za-z_][\w-]*:\s*.*$", s) and mode in (None, "map"):
                    mode = "map"
                    km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", s)
                    submap[km.group(1)] = _scalar(km.group(2).strip())
                else:
                    mode = "block"
                    buf.append(s)
                j += 1
            if mode == "list":
                data[key] = items
            elif mode == "map":
                data[key] = submap
            elif mode == "block":
                data[key] = " ".join(buf)
            else:
                data[key] = ""
            i = j
            continue
        # valor inline
        if val.startswith("{") and val.endswith("}"):
            data[key] = _inline_map(val)
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [_scalar(x.strip()) for x in inner.split(",")] if inner else []
        else:
            data[key] = _scalar(val)
        i += 1
    return data


def _inline_map(val):
    out = {}
    inner = val[1:-1].strip()
    if not inner:
        return out
    for part in inner.split(","):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = _scalar(v.strip())
    return out


def _scalar(v):
    if v == "" :
        return ""
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    if v in ("true", "True"):
        return True
    if v in ("false", "False"):
        return False
    if v in ("null", "~", "None"):
        return None
    if re.match(r"^-?\d+$", v):
        return int(v)
    return v


def validate_against_schema(data, schema):
    """Validador mínimo de JSON Schema (subset: required, type, pattern, maxLength,
    minLength, minimum, maximum, enum, minItems, additionalProperties (raiz e sub-esquema),
    properties, + extensões do contrato: noXmlTags, checkPathExists)."""
    errors = []
    props = schema.get("properties", {})
    required = schema.get("required", [])
    for key in required:
        if key not in data or data[key] is None and key != "role_order":
            errors.append(f"campo obrigatorio ausente: '{key}'")
    if not schema.get("additionalProperties", True):
        for key in data:
            if key not in props:
                errors.append(f"campo nao permitido (additionalProperties=false): '{key}'")
    for key, spec in props.items():
        if key not in data:
            continue
        val = data[key]
        errors.extend(_check_value(key, val, spec))
    return errors


def _check_value(key, val, spec):
    errs = []
    types = spec.get("type")
    if types is not None:
        if isinstance(types, str):
            types = [types]
        if not _type_ok(val, types):
            errs.append(f"'{key}': tipo invalido (esperado {types}, obtido {type(val).__name__})")
            return errs
    if isinstance(val, str):
        if "pattern" in spec and not re.match(spec["pattern"], val):
            errs.append(f"'{key}': nao casa pattern {spec['pattern']}")
        if "maxLength" in spec and len(val) > spec["maxLength"]:
            errs.append(f"'{key}': excede maxLength {spec['maxLength']}")
        if "minLength" in spec and len(val) < spec["minLength"]:
            errs.append(f"'{key}': abaixo de minLength {spec['minLength']}")
        if "enum" in spec and val not in spec["enum"]:
            errs.append(f"'{key}': valor '{val}' fora do enum {spec['enum']}")
        # regra do ADR-013: description sem tags XML (qa-critic round 1 BAIXO)
        if spec.get("noXmlTags") and re.search(r"<[^>]+>", val):
            errs.append(f"'{key}': contem tag XML (proibido pelo contrato)")
    if isinstance(val, int) and not isinstance(val, bool):
        # minimum/maximum (qa-critic round 1 MEDIO: role_order:-1 passava)
        if "minimum" in spec and val < spec["minimum"]:
            errs.append(f"'{key}': abaixo de minimum {spec['minimum']}")
        if "maximum" in spec and val > spec["maximum"]:
            errs.append(f"'{key}': acima de maximum {spec['maximum']}")
    if isinstance(val, list):
        if "minItems" in spec and len(val) < spec["minItems"]:
            errs.append(f"'{key}': lista com menos de minItems {spec['minItems']}")
        # shared_refs deve apontar para dirs existentes (REQ-4; qa-critic round 1 BAIXO)
        if spec.get("checkPathExists"):
            for item in val:
                if isinstance(item, str) and item and not os.path.isdir(os.path.join(ROOT, item)):
                    errs.append(f"'{key}': caminho inexistente '{item}'")
    if isinstance(val, dict):
        # additionalProperties=false em sub-esquema (ex.: enforcement) — qa-critic round 1 BAIXO
        subprops = spec.get("properties")
        if subprops is not None and spec.get("additionalProperties") is False:
            for k in val:
                if k not in subprops:
                    errs.append(f"'{key}.{k}': sub-campo nao permitido")
    return errs


def _type_ok(val, types):
    for t in types:
        if t == "string" and isinstance(val, str):
            return True
        if t == "integer" and isinstance(val, int) and not isinstance(val, bool):
            return True
        if t == "boolean" and isinstance(val, bool):
            return True
        if t == "array" and isinstance(val, list):
            return True
        if t == "object" and isinstance(val, dict):
            return True
        if t == "null" and val is None:
            return True
    return False


def glob_default():
    import glob
    files = []
    for pat in DEFAULT_GLOBS:
        files.extend(glob.glob(os.path.join(ROOT, pat)))
    # _template é molde inerte; valida estrutura mas não bloqueia se faltar conteúdo de domínio
    return sorted(f for f in files if "_template" not in f)


def main(argv):
    schema = load_schema()
    targets = argv[1:] if len(argv) > 1 else glob_default()
    if not targets:
        print("nenhuma skill encontrada para validar", file=sys.stderr)
        return 1
    any_fail = False
    for path in targets:
        try:
            rel = os.path.relpath(path, ROOT)
        except ValueError:
            rel = path  # caminho em outro drive (ex.: teste negativo em C:\temp)
        try:
            with open(path, encoding="utf-8-sig") as fh:
                text = fh.read()
        except OSError as e:
            print(f"FAIL {rel}: {e}")
            any_fail = True
            continue
        data, err = extract_frontmatter(text)
        if err:
            print(f"FAIL {rel}: {err}")
            any_fail = True
            continue
        errors = validate_against_schema(data, schema)
        # name deve = nome da pasta (ADR-013) — só para skills sob .agent/skills/
        # (qa-critic round 1 MEDIO: name divergente da pasta passava)
        norm = path.replace("\\", "/")
        if "/.agent/skills/" in norm:
            folder = os.path.basename(os.path.dirname(os.path.abspath(path)))
            if data.get("name") not in (folder, None) and folder != "_template":
                errors.append(f"'name': '{data.get('name')}' difere do nome da pasta '{folder}'")
        if errors:
            any_fail = True
            print(f"FAIL {rel}:")
            for e in errors:
                print(f"     - {e}")
        else:
            print(f"PASS {rel}")
    print("-" * 40)
    print("RESULTADO:", "FAIL (gate bloqueia merge)" if any_fail else "PASS (todas as skills conformes)")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
