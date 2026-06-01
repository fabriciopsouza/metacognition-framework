#!/usr/bin/env python3
"""check_input_contract.py — auto-detecção + validação de arquivos de entrada por dicionário (ADR-046).

GAP de campo: produtos de dados entregues sem **validação de arquivos** — o usuário não sabe quais
arquivos baixar, o produto não detecta nem valida, e um join silencioso a zero (chave `5123.0` float
vs `5123` int) passa despercebido. O antídoto agnóstico: um **dicionário-contrato** (data-dictionary)
que DECLARA os arquivos de entrada esperados + suas colunas obrigatórias; este gate **auto-detecta**
os arquivos numa pasta e **valida** que as colunas obrigatórias existem.

NÃO é do domínio: o dicionário (quais arquivos/colunas) é do PROJETO; este tool só verifica o
contrato. Mecaniza "arquivos detectados nas pastas e validados" — o resto (mapeamento semântico
correto, regras de prioridade antes/depois) é julgamento, declarado no dicionário e revisado pelo qa-critic.

Formato do dicionário (machine-readable):
    ### arquivo: <glob>  [| obrigatório | opcional]
    | coluna | tipo | obrigatória |
    |---|---|---|
    | Sigla | string | sim |

Uso:
    python tools/check_input_contract.py <data-dictionary.md> <pasta-de-dados>
Exit 0 se todo arquivo obrigatório foi detectado e tem as colunas obrigatórias; 1 caso contrário.
CSV: stdlib. XLSX: openpyxl (se ausente, a validação de colunas do xlsx degrada para 'não-verificado', declarado).
"""
import csv
import glob as globmod
import os
import re
import sys


def parse_dictionary(text):
    """Retorna lista de {glob, required(bool), columns:[(nome, obrigatoria_bool)]}."""
    files = []
    cur = None
    for ln in text.splitlines():
        h = re.match(r"^#{2,6}\s*arquivo:\s*(.+?)\s*$", ln, re.IGNORECASE)
        if h:
            spec = h.group(1)
            parts = [p.strip() for p in spec.split("|")]
            glob = parts[0]
            required = not any(p.lower().startswith("opcional") for p in parts[1:])
            cur = {"glob": glob, "required": required, "columns": []}
            files.append(cur)
            continue
        if cur is not None and ln.strip().startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) >= 1 and cells[0] and cells[0].lower() not in ("coluna", "column"):
                if set(cells[0]) <= {"-", ":", " "}:
                    continue  # separador
                obrig = True
                if len(cells) >= 3:
                    obrig = cells[2].lower() in ("sim", "s", "yes", "true", "obrigatória", "obrigatoria")
                cur["columns"].append((cells[0], obrig))
        elif cur is not None and ln.strip() and not ln.strip().startswith("|") and not ln.startswith("#"):
            pass  # texto livre entre tabela e próximo arquivo — ignora
    return files


def read_headers(path):
    """Cabeçalho (lista de nomes de coluna). CSV: stdlib. XLSX: openpyxl se disponível, senão None."""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".txt"):
        with open(path, encoding="utf-8-sig", newline="") as fh:
            for row in csv.reader(fh):
                return [c.strip() for c in row]
        return []
    if ext in (".xlsx", ".xlsm"):
        try:
            import openpyxl  # type: ignore
        except Exception:
            return None  # validação de coluna não-verificável sem openpyxl (declarado)
        wb = openpyxl.load_workbook(path, read_only=True)
        ws = wb.active
        for row in ws.iter_rows(min_row=1, max_row=1, values_only=True):
            return [str(c).strip() for c in row if c is not None]
        return []
    return None


def check(dict_path, folder):
    """Retorna (ok, problemas:list[str])."""
    try:
        text = open(dict_path, encoding="utf-8-sig").read()
    except OSError as e:
        return False, [f"dicionário ilegível: {e}"]
    files = parse_dictionary(text)
    if not files:
        return True, ["nenhum 'arquivo:' declarado no dicionário — nada a validar"]
    problems = []
    for f in files:
        matches = globmod.glob(os.path.join(folder, f["glob"]))
        if not matches:
            if f["required"]:
                problems.append(f"arquivo obrigatório não detectado na pasta: '{f['glob']}'")
            continue
        target = matches[0]
        headers = read_headers(target)
        if headers is None:
            problems.append(f"'{os.path.basename(target)}': colunas não-verificáveis "
                            f"(formato sem leitor; instale openpyxl p/ xlsx) — declarado, não falha")
            continue
        norm = {h.strip().lower() for h in headers}
        for col, obrig in f["columns"]:
            if obrig and col.strip().lower() not in norm:
                problems.append(f"'{os.path.basename(target)}': coluna obrigatória ausente: '{col}'")
    # problemas que NÃO são FAIL (apenas avisos declarados)
    hard = [p for p in problems if "não-verificáveis" not in p and "nada a validar" not in p]
    return (len(hard) == 0), problems


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(argv) < 3:
        print("uso: check_input_contract.py <data-dictionary.md> <pasta-de-dados>", file=sys.stderr)
        return 2
    ok, problems = check(argv[1], argv[2])
    for p in problems:
        print(("AVISO: " if "não-verificáveis" in p or "nada a validar" in p else "FALTA: ") + p)
    print("-" * 50)
    print("RESULTADO:", "PASS (arquivos detectados e colunas obrigatórias presentes)" if ok
          else "FAIL (arquivo/coluna obrigatório ausente — entrega não-pronta)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
