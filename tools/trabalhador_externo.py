#!/usr/bin/env python3
"""trabalhador_externo.py — executor de trabalhador FORA do Claude Code (ADR-131).

Chama, por programa, um modelo que o subagente do Claude Code nao alcanca: CLI sem tela
(`agy`, modo plano + sandbox; `codex`, sandbox so leitura) ou modelo local (Ollama). Os trabalhadores e as classes de dado
sao DADO em `tools/model-policy.json` -> `trabalhadores_externos`; este arquivo nao nomeia
nenhum modelo.

Garantias (cada uma com canario em tools/test_trabalhador_externo.py):
  1. Portao de dado FAIL-CLOSED: o repositorio declara a classe em `.agent/classe-de-dado.json`;
     sem declaracao, ou com valor desconhecido, vale a classe mais restrita. Trabalhador que nao
     aceita a classe e' RECUSADO antes de qualquer chamada (rc 3).
  2. So sai o que foi pedido: o trabalhador roda numa pasta vazia e descartavel, sem acesso ao
     repositorio; o conteudo vai na mensagem, montado so com os arquivos passados por --arquivo,
     e cada arquivo tem de estar DENTRO do repositorio (sem `..` nem link para fora).
  3. Saida validada: com --esquema, resposta fora do esquema e' INVALIDA (rc 4), nunca aceita.
  4. Rastro sem conteudo: cada chamada vira uma linha em ~/.claude/estado/trabalhadores/registro.jsonl
     com tokens, duracao, status e o sha256 da mensagem — nunca o texto.
  5. Consultivo: toda saida diz que nao substitui o qa-critic (ADR-108), exceto a do trabalhador
     com `revisor_formal` (Codex, emenda de 31/10/2026), que diz que vale na rodada alternada.

Uso:
  python tools/trabalhador_externo.py listar
  python tools/trabalhador_externo.py classe --repo <pasta>
  python tools/trabalhador_externo.py rodar --trabalhador <id> --repo <pasta> --pedido <arquivo.md>
         [--arquivo <caminho> ...] [--esquema <schema.json>] [--timeout 300]
Saida: JSON em stdout. rc 0 ok · 2 erro de uso/execucao · 3 recusado pelo portao · 4 saida invalida.
"""
import argparse
import datetime as _dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLICY_PATH = os.path.join(ROOT, "tools", "model-policy.json")
DECLARACAO = os.path.join(".agent", "classe-de-dado.json")
AVISO = ("Saida CONSULTIVA de trabalhador externo (ADR-131): nao substitui o qa-critic nem o veredito "
         "de juncao (ADR-108); confira por execucao antes de usar.")
AVISO_FORMAL = ("Saida de REVISOR FORMAL (emenda do ADR-131, 31/10/2026): vale como qa-critic na rodada "
                "alternada (model-policy.json revisao_alternada); o veredito grava atestacao.registro = id.")
LIMITE_BYTES = 2_000_000  # teto do material enviado numa chamada

RC_OK, RC_ERRO, RC_RECUSADO, RC_INVALIDO = 0, 2, 3, 4


class Recusado(Exception):
    pass


def carregar_politica(caminho=POLICY_PATH):
    with open(caminho, encoding="utf-8") as f:
        pol = json.load(f)
    te = pol.get("trabalhadores_externos")
    if not isinstance(te, dict):
        raise ValueError("model-policy.json sem 'trabalhadores_externos' (ADR-131)")
    return te


def classe_do_repo(repo, te):
    """Classe declarada pelo repositorio; sem declaracao valida, a mais restrita (fail-closed)."""
    ordem = te["classes_de_dado"]["ordem"]
    padrao = te.get("sem_declaracao") or ordem[-1]
    caminho = os.path.join(repo, DECLARACAO)
    try:
        with open(caminho, encoding="utf-8") as f:
            dado = json.load(f)
        classe = str(dado.get("classe", "")).strip().lower()
    except (OSError, ValueError, AttributeError):
        return padrao, f"sem declaracao valida em {DECLARACAO}: vale '{padrao}'"
    if classe not in ordem:
        return padrao, f"classe '{classe}' desconhecida em {DECLARACAO}: vale '{padrao}'"
    return classe, f"declarada em {DECLARACAO}"


def checar_portao(trab_id, te, classe):
    trabs = te.get("trabalhadores") or {}
    if trab_id not in trabs:
        raise Recusado(f"trabalhador '{trab_id}' nao existe na politica")
    t = trabs[trab_id]
    if classe not in (t.get("dados_aceitos") or []):
        raise Recusado(f"RECUSADO: o repositorio e' de classe '{classe}' e o trabalhador '{trab_id}' "
                       f"so aceita {t.get('dados_aceitos')} (sai_da_maquina={t.get('sai_da_maquina')})")
    return t


def _dentro(repo, caminho):
    base = os.path.realpath(repo)
    alvo = os.path.realpath(caminho if os.path.isabs(caminho) else os.path.join(repo, caminho))
    try:
        return os.path.commonpath([base, alvo]) == base, alvo
    except ValueError:  # discos diferentes no Windows
        return False, alvo


LIMITE_PEDIDO = 20_000  # bytes; o pedido e' instrucao, nao material — material vai por --arquivo


def pasta_pedidos():
    """Pasta PROPRIA de pedidos fora de repositorio. [QA r2 N7] antes valia o %TEMP% inteiro,
    onde ficam rascunhos de outras sessoes, inclusive de repositorios de classe empresa."""
    return os.environ.get("TRABALHADOR_PEDIDOS") or os.path.join(tempfile.gettempdir(), "trab-pedidos")


def resolver_pedido(repo, caminho):
    """Resolve o caminho do pedido UMA vez e devolve o caminho absoluto que sera aberto.
    [QA r1 Q1 + r2 N1] relativo e' resolvido contra a pasta corrente (o que `open` faria) e so
    entao conferido: abre-se exatamente o caminho conferido, nunca outro."""
    alvo = os.path.realpath(os.path.abspath(caminho))
    pasta = pasta_pedidos()
    if os.path.isdir(pasta) and os.path.normcase(os.path.realpath(pasta)) != os.path.normcase(os.path.abspath(pasta)):
        raise Recusado("RECUSADO: a pasta de pedidos e' link para outro lugar")  # [QA r3 A6]
    if os.path.isfile(alvo) and os.stat(alvo).st_nlink > 1:
        raise Recusado(f"RECUSADO: pedido '{caminho}' tem mais de um nome (hardlink)")  # [QA r3 A6]
    for raiz in (repo, pasta):
        ok, _ = _dentro(raiz, alvo)
        if ok:
            return alvo
    raise Recusado(f"RECUSADO: pedido '{caminho}' fora do repositorio e da pasta de pedidos ({pasta_pedidos()})")


def checar_pedido_path(repo, caminho):
    resolver_pedido(repo, caminho)


def montar_mensagem(repo, pedido, arquivos):
    if len(pedido.encode("utf-8")) > LIMITE_PEDIDO:
        raise Recusado(f"RECUSADO: pedido de {len(pedido.encode('utf-8'))} bytes passa do teto "
                       f"{LIMITE_PEDIDO}; material vai por --arquivo, que passa pelo portao")
    partes = [pedido.rstrip(), ""]
    for a in arquivos or []:
        ok, alvo = _dentro(repo, a)
        if not ok:
            raise Recusado(f"RECUSADO: '{a}' fica fora do repositorio; so sai o que esta dentro dele")
        if os.path.isfile(alvo) and os.stat(alvo).st_nlink > 1:  # [QA r3 A6]
            raise Recusado(f"RECUSADO: '{a}' tem mais de um nome (hardlink); pode ser arquivo de fora")
        try:
            with open(alvo, encoding="utf-8", errors="replace") as f:
                conteudo = f.read()
        except OSError as e:  # [QA r1 Q9] inexistente ou pasta: recusa declarada, nunca traceback
            raise Recusado(f"RECUSADO: '{a}' nao pode ser lido ({type(e).__name__})")
        rel = os.path.relpath(alvo, os.path.realpath(repo)).replace(os.sep, "/")
        partes += [f"===== ARQUIVO: {rel} =====", conteudo, f"===== FIM: {rel} =====", ""]
    msg = "\n".join(partes)
    if len(msg.encode("utf-8")) > LIMITE_BYTES:
        raise Recusado(f"RECUSADO: material de {len(msg.encode('utf-8'))} bytes passa do teto {LIMITE_BYTES}")
    return msg


# ---------- validacao de esquema (subconjunto do JSON Schema, sem dependencia) ----------
# [QA r1 Q3/Q4] FAIL-CLOSED: palavra-chave fora do subconjunto e' recusada ANTES da chamada,
# em vez de ignorada em silencio (que deixava resposta invalida passar como OK).
SUPORTADAS = {"type", "properties", "required", "items", "enum", "additionalProperties",
              "minItems", "maxItems", "minLength", "maxLength", "description", "title", "$schema"}
_TIPOS_OK = {"object", "array", "string", "boolean", "number", "integer", "null"}


def checar_esquema(esquema, caminho="$"):
    """Devolve a lista de problemas do PROPRIO esquema (vazia = suportado)."""
    if not isinstance(esquema, dict):
        return [f"{caminho}: esquema tem de ser objeto"]
    probs = [f"{caminho}: palavra-chave '{k}' nao suportada" for k in esquema if k not in SUPORTADAS]
    # [QA r2 N3] o TIPO de cada palavra-chave e' conferido, para nada estourar depois da chamada
    tipos = esquema.get("type")
    lista = tipos if isinstance(tipos, list) else [tipos] if tipos is not None else []
    for t in lista:
        if not isinstance(t, str) or t not in _TIPOS_OK:
            probs.append(f"{caminho}: type {t!r} desconhecido")
    ap = esquema.get("additionalProperties")
    if ap is not None and not isinstance(ap, bool):
        probs.append(f"{caminho}: additionalProperties so como booleano")
    for k in ("minItems", "maxItems", "minLength", "maxLength"):
        v = esquema.get(k)
        if v is not None and (isinstance(v, bool) or not isinstance(v, int) or v < 0):
            probs.append(f"{caminho}: {k} tem de ser inteiro >= 0")
    if "required" in esquema and not (isinstance(esquema["required"], list)
                                      and all(isinstance(x, str) for x in esquema["required"])):
        probs.append(f"{caminho}: required tem de ser lista de textos")
    if "enum" in esquema and not isinstance(esquema["enum"], list):
        probs.append(f"{caminho}: enum tem de ser lista")
    props = esquema.get("properties")
    if props is not None and not isinstance(props, dict):
        return probs + [f"{caminho}: properties tem de ser objeto"]
    for k, sub in (props or {}).items():
        probs += checar_esquema(sub, f"{caminho}.{k}")
    if "items" in esquema:
        probs += checar_esquema(esquema["items"], f"{caminho}[]")
    return probs


def _casa_tipo(valor, tipo):
    if tipo == "null":
        return valor is None
    if tipo == "boolean":
        return isinstance(valor, bool)
    if tipo in ("number", "integer"):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            return False
        return tipo == "number" or isinstance(valor, int) or float(valor).is_integer()
    return isinstance(valor, {"object": dict, "array": list, "string": str}[tipo])


def validar(valor, esquema, caminho="$"):
    erros = []
    tipo = esquema.get("type")
    if tipo is not None:
        tipos = tipo if isinstance(tipo, list) else [tipo]
        if not any(_casa_tipo(valor, t) for t in tipos):
            return [f"{caminho}: esperava {tipo}"]
    if "enum" in esquema and valor not in esquema["enum"]:
        erros.append(f"{caminho}: {valor!r} fora de {esquema['enum']}")
    if isinstance(valor, str):
        if len(valor) < esquema.get("minLength", 0):
            erros.append(f"{caminho}: texto curto demais")
        if "maxLength" in esquema and len(valor) > esquema["maxLength"]:
            erros.append(f"{caminho}: texto longo demais")
    if isinstance(valor, dict):
        for chave in esquema.get("required", []):
            if chave not in valor:
                erros.append(f"{caminho}: falta '{chave}'")
        props = esquema.get("properties") or {}
        for chave, sub in props.items():
            if chave in valor:
                erros += validar(valor[chave], sub, f"{caminho}.{chave}")
        if esquema.get("additionalProperties") is False:
            erros += [f"{caminho}: chave '{k}' nao prevista" for k in valor if k not in props]
    if isinstance(valor, list):
        if len(valor) < esquema.get("minItems", 0):
            erros.append(f"{caminho}: menos itens que o minimo")
        if "maxItems" in esquema and len(valor) > esquema["maxItems"]:
            erros.append(f"{caminho}: mais itens que o maximo")
        if isinstance(esquema.get("items"), dict):
            for i, item in enumerate(valor):
                erros += validar(item, esquema["items"], f"{caminho}[{i}]")
    return erros


# ---------- vias ----------
def _agy_bin():
    exe = os.environ.get("AGY_BIN") or shutil.which("agy")
    if exe:
        return exe
    pacote = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    if os.path.isdir(pacote):
        for nome in os.listdir(pacote):
            if nome.startswith("Google.AntigravityCLI"):
                cand = os.path.join(pacote, nome, "agy.exe")
                if os.path.isfile(cand):
                    return cand
    raise RuntimeError("agy nao encontrado (instale o Antigravity CLI ou defina AGY_BIN)")


def via_agy(trab, mensagem, esquema_path, timeout):
    """Pasta vazia + modo plano + sandbox; conteudo pela entrada em NDJSON (sem limite de argumento)."""
    with tempfile.TemporaryDirectory(prefix="trab-agy-") as vazia:
        cmd = [_agy_bin(), "-p=", "--input-format", "stream-json", "--output-format", "stream-json",
               "--model", trab["modelo"], "--mode", "plan", "--sandbox", "--print-timeout", f"{timeout}s"]
        if esquema_path:
            cmd += ["--json-schema", os.path.abspath(esquema_path)]
        linha = json.dumps({"event": "user", "message": {"content": mensagem}}, ensure_ascii=False)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, encoding="utf-8", cwd=vazia)
        try:
            saida, erro = p.communicate(linha + "\n", timeout=timeout + 60)
        except subprocess.TimeoutExpired:
            _matar_arvore(p)  # [QA r1 Q11b] neto que segura o pipe nao pode travar a chamada
            saida, erro = p.communicate(timeout=30)
            raise RuntimeError(f"agy passou de {timeout + 60} s e foi encerrado")
    r = subprocess.CompletedProcess(cmd, p.returncode, saida, erro)
    resultado = None
    for ln in (r.stdout or "").splitlines():
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if ev.get("event") == "result":
            resultado = ev.get("result") or {}
    if resultado is None:
        raise RuntimeError(f"agy sem evento result (rc {r.returncode}): {(r.stderr or '')[:400]}")
    uso = resultado.get("usage") or {}
    return {
        "status_via": resultado.get("status"),
        "texto": resultado.get("response") or "",
        "estruturado": resultado.get("structured_output"),
        "negado": resultado.get("denied_actions") or [],
        "tokens_entrada": uso.get("input_tokens"),
        "tokens_saida": uso.get("output_tokens"),
        "erro_via": resultado.get("error"),
    }


def _matar_arvore(p):
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
    else:
        p.kill()


def ollama_base():
    return os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")


def checar_local(trab):
    """[QA r1 Q2] trabalhador declarado como local so pode falar com a propria maquina."""
    if trab.get("sai_da_maquina") is False and trab.get("via") == "ollama":
        host = (urllib.parse.urlsplit(ollama_base()).hostname or "").lower()
        if host not in ("127.0.0.1", "localhost", "::1"):
            raise Recusado(f"RECUSADO: trabalhador local apontado para '{host}' (OLLAMA_URL); "
                           "local so fala com 127.0.0.1, ::1 ou localhost")


def via_ollama(trab, mensagem, esquema_path, timeout):
    checar_local(trab)  # defesa em profundidade: o portao ja checou em rodar()
    url = ollama_base() + "/api/generate"
    corpo = {"model": trab["modelo"], "prompt": mensagem, "stream": False,
             "options": {"num_ctx": int(trab.get("num_ctx", 32768))}}
    if esquema_path:
        with open(esquema_path, encoding="utf-8") as f:
            corpo["format"] = json.load(f)
    req = urllib.request.Request(url, data=json.dumps(corpo).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    # [QA r2 N2] sem proxy: HTTP_PROXY do sistema mandaria a mensagem de classe empresa para fora
    sem_proxy = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with sem_proxy.open(req, timeout=timeout) as resp:
        dado = json.loads(resp.read().decode("utf-8"))
    texto = dado.get("response") or ""
    estruturado = None
    if esquema_path:
        try:
            estruturado = json.loads(texto)
        except ValueError:
            estruturado = None
    return {"status_via": "SUCCESS" if dado.get("done") else "INCOMPLETO", "texto": texto,
            "estruturado": estruturado, "negado": [],
            "tokens_entrada": dado.get("prompt_eval_count"), "tokens_saida": dado.get("eval_count"),
            "erro_via": None}


def _codex_bin():
    exe = os.environ.get("CODEX_BIN") or shutil.which("codex")
    if exe:
        return exe
    ext = os.path.join(os.path.expanduser("~"), ".vscode", "extensions")
    if os.path.isdir(ext):  # binario da extensao openai.chatgpt do VS Code; a versao mais nova
        for nome in sorted((n for n in os.listdir(ext) if n.startswith("openai.chatgpt-")), reverse=True):
            cand = os.path.join(ext, nome, "bin", "windows-x86_64", "codex.exe")
            if os.path.isfile(cand):
                return cand
    raise RuntimeError("codex nao encontrado (instale o codex-cli ou defina CODEX_BIN)")


def via_codex(trab, mensagem, esquema_path, timeout):
    """Pasta vazia + sandbox so leitura + sem config e regras do usuario; conteudo pela entrada."""
    with tempfile.TemporaryDirectory(prefix="trab-codex-") as vazia:
        saida_arq = os.path.join(vazia, "ultima.txt")
        cmd = [_codex_bin(), "exec", "--ignore-user-config", "--ignore-rules", "--ephemeral",
               "--skip-git-repo-check", "--json", "-s", "read-only", "-C", vazia, "-o", saida_arq,
               "-m", trab["modelo"]]
        if esquema_path:
            cmd += ["--output-schema", os.path.abspath(esquema_path)]
        cmd.append("-")
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, encoding="utf-8", cwd=vazia)
        try:
            eventos, erro = p.communicate(mensagem, timeout=timeout)
        except subprocess.TimeoutExpired:
            _matar_arvore(p)
            p.communicate(timeout=30)
            raise RuntimeError(f"codex passou de {timeout} s e foi encerrado")
        texto = ""
        if os.path.isfile(saida_arq):
            with open(saida_arq, encoding="utf-8") as f:
                texto = f.read().strip()
    estruturado = None
    if esquema_path and texto:
        try:
            estruturado = json.loads(texto)
        except ValueError:
            pass  # rodar() marca INVALIDO: resposta sem JSON estruturado
    uso = {}
    for ln in (eventos or "").splitlines():  # tokens vem no evento turn.completed do --json
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if isinstance(ev, dict) and ev.get("type") == "turn.completed":
            uso = ev.get("usage") or {}
    ok = p.returncode == 0 and bool(texto)  # resposta vazia nunca e' SUCCESS
    return {"status_via": "SUCCESS" if ok else "ERRO", "texto": texto, "estruturado": estruturado,
            "negado": [], "tokens_entrada": uso.get("input_tokens"), "tokens_saida": uso.get("output_tokens"),
            "erro_via": None if ok else f"rc {p.returncode}, resposta {'vazia' if not texto else 'ok'}: "
                                         f"{(erro or '')[-400:]}"}


VIAS = {"agy": via_agy, "ollama": via_ollama, "codex": via_codex}


def _registro_path():
    return os.environ.get("TRABALHADOR_REGISTRO") or os.path.join(
        os.path.expanduser("~"), ".claude", "estado", "trabalhadores", "registro.jsonl")


RESUMO_MAX = 280  # caracteres da resposta que entram na trilha; a integra fica no arquivo da chamada


def resumir(texto, estruturado=None):
    if estruturado is not None:
        texto = json.dumps(estruturado, ensure_ascii=False)
    texto = " ".join((texto or "").split())
    return texto if len(texto) <= RESUMO_MAX else texto[:RESUMO_MAX - 1] + "…"


def registrar(linha, saida_completa=None):
    """Acrescenta uma linha a trilha. A integra da resposta (nunca a mensagem enviada) vai para
    saidas/<id>.json, local e fora de qualquer repositorio. Depois regera o monitor (fail-soft)."""
    caminho = _registro_path()
    pasta = os.path.dirname(caminho)
    os.makedirs(pasta, exist_ok=True)
    linha.setdefault("id", _dt.datetime.now().strftime("%Y%m%d-%H%M%S-") + os.urandom(3).hex())
    if saida_completa is not None:
        os.makedirs(os.path.join(pasta, "saidas"), exist_ok=True)
        arq = os.path.join(pasta, "saidas", linha["id"] + ".json")
        try:
            texto = json.dumps(saida_completa, ensure_ascii=False, indent=1)
        except (RecursionError, ValueError, TypeError) as e:  # [QA r3 A1] resposta patologica
            texto = json.dumps({"erro_ao_gravar": f"{type(e).__name__}", "status": saida_completa.get("status")})
        with open(arq, "w", encoding="utf-8") as f:
            f.write(texto)
        linha["saida"] = arq
    with open(caminho, "a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    try:  # o monitor nunca derruba a chamada
        import monitor_trabalhadores
        monitor_trabalhadores.gerar(caminho)
    except Exception:
        pass
    return linha["id"]


def rodar(trab_id, repo, pedido, arquivos=None, esquema_path=None, timeout=300, te=None, vias=None,
          trabalho=None, etapa=None, spec=None, pedido_path=None):
    """Executa uma chamada. Devolve (rc, saida_dict). `vias` injetavel para teste.
    `trabalho` (slug do registro de trabalhos, ADR-100), `etapa` e `spec` so rotulam a trilha."""
    te = te or carregar_politica()
    vias = vias or VIAS
    classe, origem = classe_do_repo(repo, te)
    rotulo = {"trabalho": trabalho or "-", "etapa": etapa or "-", "spec": spec}
    base = {"trabalhador": trab_id, "repo": os.path.basename(os.path.abspath(repo)),
            "classe": classe, "classe_origem": origem, **rotulo,
            "aviso": AVISO_FORMAL if ((te.get("trabalhadores") or {}).get(trab_id) or {}).get("revisor_formal")
            else AVISO}
    esquema = None
    try:  # TUDO que pode recusar acontece aqui, antes de qualquer byte sair
        trab = checar_portao(trab_id, te, classe)
        checar_local(trab)
        if pedido_path:
            checar_pedido_path(repo, pedido_path)
        if esquema_path:
            try:
                with open(esquema_path, encoding="utf-8") as f:
                    esquema = json.load(f)
            except (OSError, ValueError, RecursionError) as e:  # [QA r3 A2]
                raise Recusado(f"RECUSADO: esquema ilegivel ({type(e).__name__})")
            try:
                probs = checar_esquema(esquema)
            except Exception as e:  # esquema malformado vira recusa registrada, nunca traceback
                probs = [f"esquema malformado ({type(e).__name__})"]
            if probs:
                raise Recusado("RECUSADO: esquema fora do subconjunto suportado: " + "; ".join(probs[:5]))
        mensagem = montar_mensagem(repo, pedido, arquivos)
    except Recusado as e:
        registrar({**_carimbo(), **rotulo, "via": "portao", "trabalhador": trab_id, "repo": base["repo"],
                   "classe": classe, "status": "RECUSADO", "resumo": resumir(str(e))})
        return RC_RECUSADO, {**base, "status": "RECUSADO", "motivo": str(e)}
    t0 = time.monotonic()
    try:
        r = vias[trab["via"]](trab, mensagem, esquema_path, timeout)
    except Exception as e:  # erro da via vira resultado declarado, nunca silencio
        motivo = f"{type(e).__name__}: {e}"
        registrar({**_carimbo(), **rotulo, "via": trab["via"], "trabalhador": trab_id, "modelo": trab["modelo"],
                   "repo": base["repo"], "classe": classe, "status": "ERRO",
                   "segundos": round(time.monotonic() - t0, 1), "resumo": resumir(motivo)})
        return RC_ERRO, {**base, "status": "ERRO", "motivo": motivo}
    seg = round(time.monotonic() - t0, 1)
    status, rc, erros = "OK", RC_OK, []
    if r.get("status_via") != "SUCCESS":
        status, rc = "ERRO", RC_ERRO
        erros = [f"via devolveu status {r.get('status_via')}: {r.get('erro_via')}"]
    elif esquema is not None:
        if r.get("estruturado") is None:
            status, rc, erros = "INVALIDO", RC_INVALIDO, ["resposta sem JSON estruturado"]
        else:
            try:
                erros = validar(r["estruturado"], esquema)
            except Exception as e:  # a chamada ja aconteceu: o rastro tem de ficar
                erros = [f"validacao falhou: {type(e).__name__}: {e}"]
            if erros:
                status, rc = "INVALIDO", RC_INVALIDO
    saida = {**base, "status": status, "modelo": trab["modelo"], "familia": trab.get("familia"),
             "segundos": seg, "tokens_entrada": r.get("tokens_entrada"), "tokens_saida": r.get("tokens_saida"),
             "erros": erros, "acoes_negadas": r.get("negado"), "resposta": r.get("texto"),
             "estruturado": r.get("estruturado")}
    resumo = resumir("; ".join(erros)) if erros else resumir(r.get("texto"), r.get("estruturado"))
    saida["id"] = registrar(
        {**_carimbo(), **rotulo, "via": trab["via"], "trabalhador": trab_id, "modelo": trab["modelo"],
         "familia": trab.get("familia"), "repo": base["repo"], "classe": classe, "status": status,
         "segundos": seg, "tokens_entrada": r.get("tokens_entrada"), "tokens_saida": r.get("tokens_saida"),
         "sha256_mensagem": hashlib.sha256(mensagem.encode("utf-8")).hexdigest(), "resumo": resumo},
        saida_completa=saida)
    return rc, saida


def _carimbo():
    return {"quando": _dt.datetime.now().astimezone().isoformat(timespec="seconds")}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Executor de trabalhador externo (ADR-131)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar")
    c = sub.add_parser("classe")
    c.add_argument("--repo", required=True)
    r = sub.add_parser("rodar")
    r.add_argument("--trabalhador", required=True)
    r.add_argument("--repo", required=True)
    r.add_argument("--pedido", required=True, help="arquivo com a instrucao")
    r.add_argument("--arquivo", action="append", default=[], help="arquivo do repositorio a enviar")
    r.add_argument("--esquema", help="JSON Schema da resposta")
    r.add_argument("--timeout", type=int, default=300)
    r.add_argument("--trabalho", help="slug do trabalho (registro de trabalhos, ADR-100)")
    r.add_argument("--etapa", help="rotulo da etapa na trilha, ex.: 'pre-revisao PR 164'")
    r.add_argument("--spec", help="caminho da especificacao que a etapa atende")
    a = ap.parse_args(argv)
    te = carregar_politica()
    if a.cmd == "listar":
        print(json.dumps(te["trabalhadores"], ensure_ascii=False, indent=1))
        return RC_OK
    if a.cmd == "classe":
        classe, origem = classe_do_repo(a.repo, te)
        print(json.dumps({"classe": classe, "origem": origem}, ensure_ascii=False))
        return RC_OK
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        caminho_pedido = resolver_pedido(a.repo, a.pedido)  # arquivo de fora nem e' aberto
        with open(caminho_pedido, encoding="utf-8") as f:  # [QA r2 N1] abre exatamente o conferido
            pedido = f.read()
    except (Recusado, OSError, ValueError) as e:
        # [QA r2 N4] a recusa da linha de comando tambem fica na trilha
        motivo = str(e) if isinstance(e, Recusado) else f"RECUSADO: pedido ilegivel ({type(e).__name__})"
        registrar({**_carimbo(), "trabalho": a.trabalho or "-", "etapa": a.etapa or "-", "via": "portao",
                   "trabalhador": a.trabalhador, "repo": os.path.basename(os.path.abspath(a.repo)),
                   "status": "RECUSADO", "resumo": resumir(motivo)})
        print(json.dumps({"status": "RECUSADO", "motivo": motivo, "aviso": AVISO}, ensure_ascii=False))
        return RC_RECUSADO
    rc, saida = rodar(a.trabalhador, a.repo, pedido, a.arquivo, a.esquema, a.timeout, te=te,
                      trabalho=a.trabalho, etapa=a.etapa, spec=a.spec, pedido_path=caminho_pedido)
    print(json.dumps(saida, ensure_ascii=False, indent=1))
    return rc


if __name__ == "__main__":
    sys.exit(main())
