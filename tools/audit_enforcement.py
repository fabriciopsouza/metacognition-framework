#!/usr/bin/env python3
"""
audit_enforcement.py — o auditor do auditor (ADR-106, emenda ao ADR-015).

O QUE RESOLVE
`capabilities.json` deixava declarar `enforcement: fail-closed` sem que ninguem jamais
tivesse verificado que o canario da capacidade sabe ficar VERMELHO. Verde nunca foi
evidencia: em 3 ocorrencias confirmadas (ADR-096 A2, v1.79.0, projeto externo 2026-08-14)
um canario continuou verde com o mecanismo sabotado.

A REGRA (rule #12 do qa-critic)
Capacidade que declara `fail-closed` declara TAMBEM a mutacao que faz o canario dela
falhar. O modo `--provar` aplica essa mutacao num worktree isolado e EXIGE falha.

EMENDA 1 (2026-08-15) — falha PELO MOTIVO CERTO, nao qualquer falha.
O ADR-106 secao "Exigencias", item 2, manda conferir "a mensagem ou o codigo especifico,
nunca so [o returncode]" — e esta implementacao conferia so o returncode. Medido: uma
mutacao que trocava `import argparse` por `imprt argparse` (quebra de sintaxe, nada a ver
com a logica do gate) era carimbada [PROVADO]. Era o achado 1 do proprio ADR reencarnado
no auditor que o combate. A prova agora exige as tres coisas:
  1. o canario esta VERDE antes da mutacao;
  2. fica VERMELHO depois;
  3. com a mensagem declarada em `mutacao.espera` na saida — mensagem que NAO podia
     ja aparecer antes (senao qualquer palavra do cabecalho serviria).
E recusa "vermelho por crash": se o canario morre carregando o arquivo sabotado
(SyntaxError e afins citando o proprio arquivo), a prova e' invalida — quebrar o arquivo
nao prova que o gate detecta.

DECISAO DO DONO (2026-08-14), que este script mecaniza:
  (a) capacidade NOVA  -> fail-closed. Sem `mutacao` declarada, sai 1 e barra.
  (b) passivo herdado  -> advisory. Reporta, nao barra. O passivo esta congelado em
      `_meta/enforcement-baseline.json`; quem nao esta la e' novo.

Uso:
    python tools/audit_enforcement.py                  # modo declaracao (rapido; CI)
    python tools/audit_enforcement.py --passivo        # relatorio do modo (b)
    python tools/audit_enforcement.py --provar --id X  # aplica a mutacao e exige VERMELHO
    python tools/audit_enforcement.py --gerar-baseline # congela o passivo (1x, ja feito)

Codigos de saida: 0 OK · 1 capacidade nova sem prova · 2 mutacao NAO derrubou o canario.
NAO usa IA.
"""
import argparse
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CAPS = RAIZ / "capabilities.json"
BASELINE = RAIZ / "_meta" / "enforcement-baseline.json"

# Campos que uma `mutacao` precisa ter para ser executavel — nao aceita prosa.
# `espera` entrou na emenda 1 (2026-08-15): sem ela, a prova conferia so `returncode != 0`,
# que e' a fraude do achado 1 do proprio ADR-106 ("o canario aferia so o returncode").
# Medido: uma mutacao que apenas quebrava a SINTAXE do mecanismo era carimbada [PROVADO].
CAMPOS_MUTACAO = ("arquivo", "de", "para", "canario", "espera")

# Sinais de que o canario MORREU processando o arquivo sabotado em vez de DETECTAR a sabotagem.
# Quebrar o arquivo nao prova que o gate detecta coisa alguma — prova que Python nao le arquivo
# invalido, o que ja se sabia.
#
# A 1a versao desta lista so cobria erro de INTERPRETADOR e ainda exigia o nome do arquivo no
# traceback. O qa-critic (Sonnet, 2026-08-15) derrubou as duas coisas: mecanismo `.json`/`.md`
# quebra com `JSONDecodeError`, cujo traceback cita `json/decoder.py` e NUNCA o arquivo de dados
# — a recusa nao disparava. E `model-policy` e' exatamente isso: mecanismo `tools/model-policy.json`.
# Agora a deteccao e' por DELTA: marca que aparece DEPOIS e nao aparecia ANTES.
MARCAS_DE_CRASH = ("Traceback (most recent call last)", "SyntaxError", "IndentationError",
                   "ModuleNotFoundError", "ImportError", "JSONDecodeError",
                   "UnicodeDecodeError", "ParserError")

# A prova NAO pode depender de cache de bytecode. O Python decide reusar um `.pyc` comparando
# TAMANHO e HORARIO do fonte, e o horario tem resolucao de 1 SEGUNDO. A execucao "antes" compila
# o mecanismo; se a sabotagem for gravada dentro do mesmo segundo E mantiver o mesmo numero de
# bytes, o interpretador reusa o bytecode velho e roda o codigo NAO sabotado — o canario fica
# verde e o auditor conclui "nao prova nada" sobre codigo que nunca executou.
#
# Medido em 2026-08-15 com `autonomy-retry-policy`: a mutacao trocava a ordem de 4 nomes numa
# lista, 48 bytes antes e 48 depois. O resultado alternava entre correto e errado conforme a
# maquina ganhasse ou perdesse a corrida do relogio — uma prova INTERMITENTE, que e' pior que
# uma prova ausente, porque parece funcionar.
#
# Duas travas, porque uma so seria confianca: nao escrever bytecode nenhum, e apagar o que
# porventura exista antes de rodar o canario sabotado.
# Emenda 4 (2026-08-16): `PYTHONDONTWRITEBYTECODE` impede ESCREVER, nao impede LER um `.pyc`
# pre-existente — ressalva MEDIA do qa-critic, confirmada depois pelo canario do
# `run_canaries.py`, que reprovou a mesma correcao la'. `PYTHONPYCACHEPREFIX` apontando para
# um diretorio VAZIO fecha a leitura: com o prefixo definido, o interpretador procura cache
# SO' ali. O prefixo e' criado por execucao e removido na saida.
_PREFIXO_CACHE = tempfile.mkdtemp(prefix="prova-pyc-")
atexit.register(shutil.rmtree, _PREFIXO_CACHE, True)
ENV_SEM_BYTECODE = {**os.environ,
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONPYCACHEPREFIX": _PREFIXO_CACHE}


def _purgar_bytecode(raiz_wt):
    """Remove todo `__pycache__` sob o worktree — cinto e suspensorio do ENV acima."""
    for cache in Path(raiz_wt).rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


# Tamanho minimo de `mutacao.espera`. Achado ALTO do mesmo qa-critic: sem piso, `espera: "Error"`
# casa com o texto de praticamente qualquer excecao — o sinal declarado vira curinga e a prova
# volta a ser "saiu diferente de zero" com outro nome.
ESPERA_MIN = 12


def carregar_caps(p: Path):
    d = json.loads(p.read_text(encoding="utf-8"))
    return list(d.get("capabilities", d) if isinstance(d, dict) else d)


def valida_mutacao(m, cap=None):
    """(ok, motivo). Mutacao precisa ser aplicavel por maquina, nao descricao.

    `cap` permite o cross-check com o mecanismo REAL da capacidade: sem ele, dava para
    declarar uma mutacao num arquivo qualquer, sem relacao com o que a capacidade diz
    proteger, e a "prova" provaria algo irrelevante (achado 3 do qa-critic, 2026-08-14).
    """
    if not isinstance(m, dict):
        return False, "campo `mutacao` nao e' objeto"
    faltando = [c for c in CAMPOS_MUTACAO if not m.get(c)]
    if faltando:
        return False, f"`mutacao` sem os campos: {', '.join(faltando)}"
    if m["de"] == m["para"]:
        return False, "`mutacao` com `de` == `para` nao sabota nada"
    esp = str(m["espera"]).strip()
    if len(esp) < ESPERA_MIN:
        return False, (f"`mutacao.espera` ({esp!r}) tem {len(esp)} caractere(s) — minimo "
                       f"{ESPERA_MIN}. Sinal curto casa por acidente: 'Error' aparece no texto "
                       f"de quase toda excecao, e a prova volta a nao provar nada")
    colide = [mk for mk in MARCAS_DE_CRASH if mk.lower() in esp.lower()]
    if colide:
        return False, (f"`mutacao.espera` contem sinal de CRASH ({colide[0]!r}) — prova por crash "
                       f"nao vale. Declare a mensagem que o gate imprime ao DETECTAR a sabotagem, "
                       f"nao a excecao que ele levanta ao engasgar com ela")
    if cap is not None:
        mec, tst = cap.get("mechanism"), cap.get("test")
        # Ausencia de `mechanism`/`test` NAO pode desligar o cross-check em silencio:
        # bastaria omitir os dois campos para a "prova" provar qualquer arquivo
        # (achado 3 residual do qa-critic, rodada 2, 2026-08-14). Falta de campo e' falha.
        faltam = [k for k, v in (("mechanism", mec), ("test", tst)) if not v]
        if faltam:
            return False, (f"capacidade `fail-closed` sem {' e sem '.join(faltam)} declarado — "
                           f"sem isso a `mutacao` nao pode ser cruzada com o mecanismo real")
        if m["arquivo"] != mec:
            return False, (f"`mutacao.arquivo` ({m['arquivo']}) nao e' o mecanismo "
                           f"declarado da capacidade ({mec}) — provaria outra coisa")
        if m["canario"] != tst:
            return False, (f"`mutacao.canario` ({m['canario']}) nao e' o canario "
                           f"declarado da capacidade ({tst}) — provaria outra coisa")
    return True, ""


def modo_declaracao(caps, baseline, so_passivo=False):
    """Regra (a) fail-closed para capacidade nova; regra (b) advisory para o passivo."""
    novas_sem_prova, passivo, ok = [], [], 0
    for c in caps:
        cid = c.get("id", "?")
        herdada = cid in baseline
        enf = c.get("enforcement")
        problema = None
        if not enf:
            problema = "sem campo `enforcement` — invisivel a auditoria"
        elif enf == "fail-closed":
            m = c.get("mutacao")
            if m is None:
                problema = "declara `fail-closed` sem `mutacao` declarada"
            else:
                bom, motivo = valida_mutacao(m, c)
                if not bom:
                    problema = motivo
        if problema is None:
            ok += 1
        elif herdada:
            passivo.append((cid, enf or "(ausente)", problema))
        else:
            novas_sem_prova.append((cid, enf or "(ausente)", problema))

    if so_passivo:
        print(f"# PASSIVO (modo b — advisory, nao barra): {len(passivo)} capacidade(s)")
        for cid, enf, prob in sorted(passivo):
            print(f"  · {cid} [{enf}] — {prob}")
        print(f"\n{ok} capacidade(s) em conformidade · {len(passivo)} no passivo "
              f"· {len(novas_sem_prova)} nova(s) sem prova")
        return 0

    if novas_sem_prova:
        print(f"[FALHA] {len(novas_sem_prova)} capacidade(s) NOVA(s) sem prova de mutacao:")
        for cid, enf, prob in sorted(novas_sem_prova):
            print(f"  - {cid} [{enf}]: {prob}")
        print("\nCapacidade nova declara a mutacao que faz o canario dela FALHAR "
              f"(campos: {', '.join(CAMPOS_MUTACAO)}).")
        print("Sem isso, 'verde' nao e' evidencia de nada — ver rule #12 do qa-critic.")
        return 1

    print(f"OK: {ok} capacidade(s) em conformidade, nenhuma nova sem prova "
          f"({len(passivo)} no passivo herdado — rode --passivo para ver).")
    return 0


def modo_provar(caps, alvo, raiz=RAIZ):
    """Aplica a mutacao num worktree isolado e EXIGE que o canario fique vermelho.

    `raiz` e' parametro (nao constante de modulo) para que o proprio canario possa
    exercitar este modo contra um repo-fixture — a licao da auditoria de 2026-08-14:
    mecanismo preso a uma raiz fixa nao e' testavel, e o que nao e' testavel passa
    por acidente.
    """
    escolhidas = [c for c in caps if c.get("mutacao") and (not alvo or c.get("id") == alvo)]
    if not escolhidas:
        print(f"[ERRO] nenhuma capacidade com `mutacao` declarada"
              f"{f' para o id {alvo!r}' if alvo else ''}.")
        return 1

    with tempfile.TemporaryDirectory(prefix="prova-mutacao-") as tmp:
        wt = Path(tmp) / "wt"
        # limpa worktree orfao de execucao anterior morta no meio (achado 8, qa-critic)
        subprocess.run(["git", "worktree", "prune"], capture_output=True, cwd=str(raiz))
        r = subprocess.run(["git", "worktree", "add", "--detach", str(wt), "HEAD"],
                           capture_output=True, text=True, cwd=str(raiz))
        if r.returncode != 0:
            print("[SKIP declarado] worktree isolado indisponivel — prova NAO executada.")
            print(f"  git disse: {(r.stderr or '').strip()[:200]}")
            return 0
        try:
            falhas = []
            for c in escolhidas:
                cid, m = c.get("id", "?"), c["mutacao"]
                bom, motivo = valida_mutacao(m, c)
                if not bom:
                    falhas.append((cid, motivo))
                    continue
                alvo_f = wt / m["arquivo"]
                canario = wt / m["canario"]
                if not alvo_f.is_file() or not canario.is_file():
                    falhas.append((cid, f"arquivo ou canario inexistente no HEAD: "
                                        f"{m['arquivo']} / {m['canario']}"))
                    continue
                original = alvo_f.read_text(encoding="utf-8")
                if m["de"] not in original:
                    falhas.append((cid, f"trecho `de` nao encontrado em {m['arquivo']} "
                                        f"— mutacao esta obsoleta"))
                    continue
                # 1) o canario passa ANTES da mutacao?
                antes = subprocess.run([sys.executable, "-X", "utf8", str(canario)],
                                       capture_output=True, text=True, cwd=str(wt),
                                       env=ENV_SEM_BYTECODE)
                saida_antes = (antes.stdout or "") + (antes.stderr or "")
                if antes.returncode != 0:
                    falhas.append((cid, "canario ja estava VERMELHO antes da mutacao "
                                        "— a prova nao diz nada"))
                    continue
                # A mensagem esperada nao pode ser algo que o canario ja imprime sempre:
                # senao bastaria declarar uma palavra do cabecalho e a checagem seria vazia.
                if m["espera"] in saida_antes:
                    falhas.append((cid, f"`espera` ({m['espera']!r}) ja aparece na saida ANTES "
                                        f"da mutacao — nao distingue detectado de rotina"))
                    continue
                # 2) sabota e exige vermelho PELO MOTIVO DECLARADO
                alvo_f.write_text(original.replace(m["de"], m["para"], 1), encoding="utf-8")
                _purgar_bytecode(wt)
                dep = subprocess.run([sys.executable, "-X", "utf8", str(canario)],
                                     capture_output=True, text=True, cwd=str(wt),
                                     env=ENV_SEM_BYTECODE)
                alvo_f.write_text(original, encoding="utf-8")
                saida_dep = (dep.stdout or "") + (dep.stderr or "")
                # Deteccao por DELTA, nao por nome de arquivo: marca de crash que NAO existia
                # antes da mutacao e passou a existir depois. Nao depende de o traceback citar
                # o arquivo — que era a escapatoria dos mecanismos `.json`/`.md`.
                novas = [mk for mk in MARCAS_DE_CRASH if mk in saida_dep and mk not in saida_antes]
                if dep.returncode == 0:
                    falhas.append((cid, f"canario `{m['canario']}` continuou VERDE com "
                                        f"`{m['arquivo']}` sabotado — nao prova nada"))
                elif novas:
                    falhas.append((cid, f"canario MORREU processando `{m['arquivo']}` sabotado "
                                        f"({novas[0]} apareceu so depois da mutacao): crash, nao "
                                        f"deteccao — quebrar o arquivo nao prova que o gate "
                                        f"detecta; sabote a LOGICA, nao a sintaxe"))
                elif m["espera"] not in saida_dep:
                    falhas.append((cid, f"canario ficou vermelho, mas NAO pelo motivo declarado: "
                                        f"`espera` ({m['espera']!r}) ausente da saida"))
                else:
                    print(f"  [PROVADO] {cid}: mutacao em {m['arquivo']} deixou "
                          f"{m['canario']} vermelho (codigo {dep.returncode}) "
                          f"pelo motivo declarado ({m['espera']!r})")
            if falhas:
                print(f"\n[FALHA] {len(falhas)} prova(s) de mutacao invalida(s):")
                for cid, motivo in falhas:
                    print(f"  - {cid}: {motivo}")
                return 2
            print(f"\nOK: {len(escolhidas)} prova(s) de mutacao — todos os canarios "
                  f"ficaram vermelhos quando o mecanismo foi sabotado.")
            return 0
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                           capture_output=True, cwd=str(raiz))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--capabilities", default=str(CAPS))
    ap.add_argument("--baseline", default=str(BASELINE))
    ap.add_argument("--passivo", action="store_true", help="relatorio do modo (b)")
    ap.add_argument("--provar", action="store_true", help="aplica a mutacao e exige vermelho")
    ap.add_argument("--id", help="restringe --provar a uma capacidade")
    ap.add_argument("--raiz", default=str(RAIZ),
                    help="repo git onde a mutacao sera aplicada (default: este repo)")
    ap.add_argument("--gerar-baseline", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    pc = Path(args.capabilities)
    if not pc.is_file():
        print(f"[ERRO] registro de capacidades nao encontrado: {pc}")
        return 1
    try:
        caps = carregar_caps(pc)
    except json.JSONDecodeError as e:
        print(f"[ERRO] `{pc.name}` nao e' JSON valido: linha {e.lineno}, coluna {e.colno} — {e.msg}")
        return 1

    if args.gerar_baseline:
        ids = sorted(c.get("id", "?") for c in caps)
        pb = Path(args.baseline)
        pb.parent.mkdir(parents=True, exist_ok=True)
        pb.write_text(json.dumps({
            "note": "Passivo congelado na adocao do ADR-106 (2026-08-14). Modo (b): estas "
                    "capacidades sao auditadas por relatorio, nao barram o CI. Quem NAO esta "
                    "nesta lista e' capacidade NOVA e cai no modo (a), fail-closed.",
            "congelado_em": "2026-08-14",
            "ids": ids,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        # caminho relativo so quando o destino esta DENTRO do repo — fora dele,
        # `relative_to` levanta ValueError DEPOIS de gravar o arquivo (bug achado
        # pela cobertura nova de --gerar-baseline, 2026-08-14)
        try:
            onde = pb.relative_to(RAIZ)
        except ValueError:
            onde = pb
        print(f"OK: passivo congelado com {len(ids)} id(s) em {onde}")
        return 0

    pb = Path(args.baseline)
    if not pb.is_file():
        print(f"[ERRO] baseline do passivo nao encontrado: {pb}")
        print("Rode uma vez: python tools/audit_enforcement.py --gerar-baseline")
        return 1
    baseline = set(json.loads(pb.read_text(encoding="utf-8")).get("ids", []))

    if args.provar:
        return modo_provar(caps, args.id, Path(args.raiz))
    return modo_declaracao(caps, baseline, so_passivo=args.passivo)


if __name__ == "__main__":
    sys.exit(main())
