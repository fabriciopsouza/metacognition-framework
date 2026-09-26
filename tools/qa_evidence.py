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
    # A CADEIA TEM DE APARECER NO QUE O HUMANO LE.
    #
    # O `.md` e' o artefato que gente abre — e ele nao mostrava nada de
    # `substitui`/`substitui_reprovacao`. Consertar a cadeia so' no JSON deixava
    # a informacao existindo para a maquina e invisivel para quem decide: um
    # veredito aprovativo que APAGOU uma reprovacao parecia um aprovativo
    # comum. [achado ALTA do QA de 17/09/2026]
    antecedentes = v.get("substitui") or []
    if antecedentes:
        L += ["", "## Substitui vereditos anteriores deste bloco", ""]
        if v.get("substitui_reprovacao"):
            L.append("> **ATENCAO: este veredito substitui uma REPROVACAO.** "
                     "Leia os antecedentes antes de tratar o bloco como aprovado.")
            L.append("")
        for a in antecedentes:
            L.append(f"- rodada {a.get('rodada', '?')} · {a.get('data', '?')} · "
                     f"**{a.get('recomendacao') or a.get('veredito') or '?'}** · "
                     f"sha `{str(a.get('sha_revisado'))[:12]}` · "
                     f"agentId `{a.get('agentId') or '—'}`")
            cobria = a.get("escopo_paths")
            if cobria is not None:
                L.append(f"  - cobria {len(cobria)} caminho(s)"
                         + (f": {', '.join(cobria[:4])}" if cobria else " (nenhum)")
                         + (" …" if len(cobria) > 4 else ""))
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


def validate_substitui(valor):
    """(erros). Mesma disciplina que `validate_problemas`, e pela mesma razao.

    `list(anterior.get("substitui") or [])` aceita uma STRING e a fragmenta em
    caracteres, sem erro naquela linha. O crash so' aparece depois, em
    `render_md` — e a essa altura o `json.dump` JA' GRAVOU o JSON corrompido,
    porque ele roda antes. A cada nova tentativa a lista de fragmentos cresce e
    nunca converge; o `.md` fica permanentemente desatualizado.

    Este arquivo ja' tinha aprendido isso com `problemas` (item fora do schema
    passava e o `.md` saia com celulas vazias, sem erro). A licao nao foi
    generalizada para `substitui`, que a correcao anterior acabou de tornar o
    campo central da cadeia. [achado do QA de 17/09/2026]
    """
    if valor is None:
        return []
    if not isinstance(valor, list):
        return [f"precisa ser lista, veio {type(valor).__name__}"]
    erros = []
    for i, item in enumerate(valor):
        if not isinstance(item, dict):
            erros.append(f"item {i} precisa ser objeto, veio "
                         f"{type(item).__name__}: {str(item)[:40]!r}")
            continue
        # AS CHAVES, e nao so' o tipo do container.
        #
        # A 1a versao checava apenas `isinstance(item, dict)` — e o docstring
        # dizia "mesma disciplina que `validate_problemas`", o que era FALSO:
        # aquele exige as chaves e recusa vazio. Entao `{}` e `{"foo": "bar"}`
        # passavam, e o `.md` saia com uma linha de interrogacoes:
        #
        #     - rodada ? · ? · **?** · sha `None` · agentId `—`
        #
        # E' o MESMO bug que este arquivo ja' tinha corrigido para `problemas`,
        # sobrevivendo dentro do conserto que alegava te-lo generalizado.
        # [achado do QA de 17/09/2026]
        faltando = [c for c in ("rodada", "data", "recomendacao") if not item.get(c)]
        if "escopo_paths" not in item:
            faltando.append("escopo_paths")
        if faltando:
            erros.append(f"item {i} sem {', '.join(faltando)} — antecedente sem "
                         f"identificacao vira linha de interrogacoes no .md")
    return erros


def _blob_indexado(p):
    """Hash do blob de `p` como esta' no INDICE (estagio 0), ou None.

    Indice e nao disco: o indice e' o que sera' commitado, e portanto o que o veredito
    precisa descrever. Cai para o disco quando o caminho nao esta' indexado, porque ai'
    tambem ha' conteudo real. None quando o git nao responde — o chamador simplesmente
    nao carimba aquele caminho, e o gate trata a ausencia como fail-closed.

    NORMALIZA O SEPARADOR, pela mesma razao que o gemeo em `squad_gate.py` (achado ALTA da
    37a rodada): `git rev-parse :tools\\foo.py` nao resolve contra o indice, a funcao caia no
    fallback que le o DISCO, e num arquivo `MM` o carimbo gravado seria o do conteudo NAO
    revisado. Aqui o estrago seria pior que no gemeo — carimbar uma coisa e commitar outra,
    em silencio, do lado de quem ESCREVE a prova.
    """
    import subprocess
    p = str(p).replace("\\", "/")
    for args in (["rev-parse", ":" + p], ["hash-object", p]):
        try:
            r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
        except (OSError, ValueError):
            return None
        saida = (r.stdout or "").strip()
        if r.returncode == 0 and len(saida) == 40 and all(c in "0123456789abcdef" for c in saida):
            return saida
    return None


# Circuit breaker do laço de QA (ADR-118, decisões do dono de 25/09/2026).
LIMITE_REPROVACOES_SEGUIDAS = 3   # D1: 3 rodadas não-aprovativas seguidas -> redesenho ou decisão do dono
RODADAS_SEM_PROGRESSO = 2          # D2: 2 rodadas não-aprovativas seguidas com os MESMOS achados


def _achados_fp(v):
    """Impressão digital dos achados de uma rodada: severidade + local. Duas rodadas com a mesma
    impressão = o autor não mudou nada que o revisor tenha visto."""
    fp = set()
    for p in (v.get("problemas") or []):
        if isinstance(p, dict):
            fp.add(f"{str(p.get('severidade', '')).strip().upper()}|"
                   f"{str(p.get('local', '')).strip().lower()[:60]}")
    return sorted(fp)


MIN_REDESENHO = 20          # "x" não descreve redesenho nenhum
MIN_PALAVRAS_REDESENHO = 4  # "x" * 20 também não (QA de 26/09, rodada 2)


def _tem_data_real(texto):
    """True se o texto contém uma data de calendário válida dd/mm/aaaa (99/99/9999 não é data)."""
    import datetime
    for d, m, a in re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", texto):
        try:
            datetime.date(int(a), int(m), int(d))
            return True
        except ValueError:
            continue
    return False


def destrava_breaker(verdict):
    """True se a rodada traz redesenho descrito (≥ MIN_REDESENHO caracteres e ≥ MIN_PALAVRAS_REDESENHO
    palavras distintas) ou ordem do dono com data real dd/mm/aaaa. Prova forma, não autoria — o
    limite está declarado no ADR-118."""
    red = str(verdict.get("redesenho") or "").strip()
    dono = str(verdict.get("override_dono") or "").strip()
    redesenho_ok = len(red) >= MIN_REDESENHO and len(set(red.lower().split())) >= MIN_PALAVRAS_REDESENHO
    return redesenho_ok or _tem_data_real(dono)


def motivo_circuit_breaker(historico):
    """Motivo do disparo, ou "" — lido do histórico de rodadas JÁ gravadas do bloco (mais antiga
    primeiro). Conta a sequência final de rodadas não-aprovativas; uma rodada gravada com redesenho
    ou ordem do dono (`reinicio`) recomeça a contagem."""
    seq = []
    for h in historico:
        if not isinstance(h, dict):
            continue
        if h.get("reinicio"):
            seq = []
        if str(h.get("recomendacao", "")).lower() in APPROVING:
            seq = []
        else:
            seq.append(h)
    if len(seq) >= LIMITE_REPROVACOES_SEGUIDAS:
        return (f"{len(seq)} rodadas seguidas sem aprovação (limite "
                f"{LIMITE_REPROVACOES_SEGUIDAS}) — repetir a revisão não converge")
    if len(seq) >= RODADAS_SEM_PROGRESSO:
        ult = seq[-RODADAS_SEM_PROGRESSO:]
        fps = [h.get("achados_fp") for h in ult]
        if all(f for f in fps) and all(f == fps[0] for f in fps):
            return (f"{RODADAS_SEM_PROGRESSO} rodadas seguidas com os mesmos achados — sem progresso")
    return ""


def write_artifact(verdict, when=None):
    missing = [k for k in REQUIRED if k not in verdict]
    if missing:
        raise ValueError(f"veredito invalido — campos ausentes: {missing}")
    pe = validate_problemas(verdict.get("problemas"))
    if pe:
        raise ValueError("veredito invalido — itens de 'problemas' fora do schema: " + "; ".join(pe))
    se = validate_substitui(verdict.get("substitui"))
    if se:
        raise ValueError("veredito invalido — `substitui` fora do schema: " + "; ".join(se))
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
    # O CONTEUDO QUE O CRITICO VIU, e nao so' o commit em que ele olhou (ALTA da 36a rodada).
    # `sha_revisado` e' um commit, e commit nenhum descreve conteudo ainda nao commitado — no
    # pre-commit de um bloco, TODO arquivo esta' fora do HEAD, entao a recencia por
    # ancestralidade ficava inerte para o proprio bloco que entra. Carimbar o hash do blob
    # INDEXADO de cada caminho de `escopo_paths` e' o que permite ao gate dizer "isto ainda e'
    # byte a byte o que foi revisado". Escrito aqui, nunca digitado por um critico.
    if not verdict.get("blobs_revisados"):
        blobs = {}
        # Os DOIS arquivos deste proprio veredito nunca sao carimbados: o .json/.md ainda
        # nao existem quando este codigo roda, e numa REgravacao o que se carimbaria e' o
        # conteudo ANTERIOR — obsoleto no mesmo segundo em que o `json.dump` abaixo grava.
        # Auto-carimbo e' sempre stale por construcao e nao prova nada; deixar de grava-lo
        # e' mais honesto que gravar um hash que o gate teria de aprender a ignorar.
        _meu = "_meta/qa/" + _slug(verdict["bloco"])
        _proprios = {_meu + ".json", _meu + ".md"}
        for p in (verdict.get("escopo_paths") or []):
            if str(p).replace("\\", "/") in _proprios:
                continue
            h = _blob_indexado(p)
            if h:
                # CHAVE normalizada tambem, nao so' a consulta: o leitor
                # (`squad_gate._recente_o_bastante`) recebe os paths ja' com barra normal,
                # entao uma chave gravada com barra invertida NUNCA seria encontrada — o
                # veredito bloquearia para sempre e empurraria para `--no-verify`, que este
                # repo trata como pior que o buraco que fecha. [ALTA da 37a rodada]
                blobs[str(p).replace("\\", "/")] = h
        if blobs:
            verdict["blobs_revisados"] = blobs
    os.makedirs(QA_DIR, exist_ok=True)
    slug = _slug(verdict["bloco"])
    jpath = os.path.join(QA_DIR, slug + ".json")
    mpath = os.path.join(QA_DIR, slug + ".md")
    # NAO SOBRESCREVE VEREDITO ATESTADO EM SILENCIO.
    #
    # `open(jpath, "w")` cru apagava o veredito anterior do MESMO bloco sem
    # checar existencia nem encadear: um segundo registro com o mesmo `bloco`
    # triturava a reprovacao que veio antes, e o ledger passava a contar uma
    # historia em que ela nunca existiu. Achado CRITICO do QA adversarial
    # (bloco adr-115, artefato `adr-115-rodada-27-o-escritor-do-ledger-e-o-
    # triturador.json`), reaberto e confirmado em 17/09/2026: a linha ainda era
    # `open(jpath, "w", ...)`.
    #
    # O ledger e' a memoria de quem reprovou o que. Ferramenta que o reescreve
    # sem deixar rastro derruba a cadeia inteira que o ADR-115 existe para
    # proteger — e nao adianta o gate ser fail-closed se o registro que ele le
    # pode ser trocado por baixo.
    if os.path.isfile(jpath):
        try:
            anterior = json.load(open(jpath, encoding="utf-8"))
        except (ValueError, OSError):
            anterior = None
        if anterior:
            # FUNDE O HISTORICO DO ANTERIOR, nao so' o do veredito que entra.
            #
            # `verdict.get("substitui")` e' quase sempre VAZIO: quem escreve o
            # JSON e' o qa-critic, que nao carrega historico nenhum. Ler dali e
            # anexar so' o antecedente imediato deixava a cadeia presa em
            # profundidade 1 PARA SEMPRE — na 3a gravacao do mesmo bloco, a
            # rodada 1 sumia do artefato, porque o arquivo inteiro e' reescrito.
            #
            # Num bloco com 30 rodadas registradas, o artefato final mostraria
            # um unico elo. A pergunta e' "a historia INTEIRA persiste atraves de
            # N regravacoes?", e a versao anterior media "existe UM antecedente
            # nesta gravacao?" — proxy que passa mesmo com a historia funda ja'
            # descartada. [achado CRITICO do QA de 17/09/2026]
            # O que esta' NO DISCO tambem passa: artefato de versao antiga,
            # editado a mao, ou escrito por ferramenta que nao passe por aqui.
            # Recusar ANTES de gravar — `json.dump` vem antes de `render_md`,
            # entao "crashar no render" ja' deixou o ledger corrompido no disco.
            no_disco = validate_substitui(anterior.get("substitui"))
            if no_disco:
                raise ValueError(
                    f"o veredito ja' gravado em {jpath} tem `substitui` fora do schema "
                    f"({'; '.join(no_disco)}) — conserte o arquivo antes de regravar; "
                    f"mesclar por cima corromperia a cadeia")
            historico = list(anterior.get("substitui") or [])
            for antigo in (verdict.get("substitui") or []):
                if antigo not in historico:
                    historico.append(antigo)
            # `recomendacao` e' o campo OBRIGATORIO do schema (REQUIRED) e e' o
            # que o `squad_gate` le. `veredito` e' chave paralela OPCIONAL que
            # esta ferramenta nunca escreve — 30 dos 87 artefatos reais nao a
            # tem. Perguntar por ela era perguntar ao campo errado, e o campo
            # errado responde `None` quase sempre: a guarda contra apagar uma
            # reprovacao NUNCA disparava. [achado CRITICO do QA de 17/09/2026]
            decisao_anterior = anterior.get("recomendacao") or anterior.get("veredito")
            # O `escopo_paths` ENTRA na assinatura. Escopo e' FONTE, nao metadado.
            #
            # A 1a versao guardava rodada, data, recomendacao, sha e agentId — a
            # IDENTIDADE do veredito anterior — e perdia exatamente o dado que
            # decide se substitui-lo e' seguro: O QUE ELE COBRIA. Quem ler a
            # cadeia depois nao tem como saber se a substituicao ESTREITOU a
            # cobertura do bloco.
            #
            # Aqui nao houve dano (o anterior era reprovacao, que nunca conta
            # como cobertura, entao nao havia o que estreitar). Mas na proxima
            # vez que um APROVATIVO de escopo amplo for substituido por um de
            # escopo menor, a cadeia registra a troca como limpa e so' o
            # `squad_gate` denuncia depois — quando ja' e' tarde para saber que o
            # encolhimento foi silencioso.
            #
            # Mesma Regra 4 de rastreabilidade: decisao -> FONTE -> versao.
            # [achado ALTA do QA de 18/09/2026, levantado pelo autor e confirmado
            #  pelo critico]
            assinatura = {
                "rodada": anterior.get("rodada"),
                "data": anterior.get("data"),
                "recomendacao": decisao_anterior,
                "sha_revisado": anterior.get("sha_revisado"),
                "agentId": (anterior.get("atestacao") or {}).get("agentId"),
                "escopo_paths": list(anterior.get("escopo_paths") or []),
                # circuit breaker (ADR-118): o que o breaker precisa ler da rodada anterior
                "achados_fp": _achados_fp(anterior),
                "reinicio": destrava_breaker(anterior),
            }
            if assinatura not in historico:
                historico.append(assinatura)
            verdict["substitui"] = historico
            # Reprovacao nao se apaga por regravacao: ela vira ANTECEDENTE
            # explicito do veredito novo, e quem ler sabe que houve.
            if str(decisao_anterior).lower() in ("reprovar", "corrigir") and \
                    not verdict.get("substitui_reprovacao"):
                verdict["substitui_reprovacao"] = True
            # CIRCUIT BREAKER (ADR-118): recusa ANTES de gravar a rodada que continuaria um laço
            # autor <-> revisor já estourado. A rodada que dispara foi gravada; a seguinte só entra
            # com `redesenho` ou `override_dono` (registrados no artefato, no momento do ato).
            # Aprovação SEMPRE entra: é ela que encerra o laço (QA de 26/09: o breaker recusava a
            # aprovação e obrigava a inventar um "redesenho" só para registrar o PASS).
            motivo = motivo_circuit_breaker(historico)
            aprova = str(verdict.get("recomendacao", "")).lower() in APPROVING
            if motivo and not aprova and not destrava_breaker(verdict):
                raise ValueError(f"CIRCUIT BREAKER em '{verdict['bloco']}': {motivo}. Pare o laço: "
                                 f"registre o redesenho (--redesenho \"o que mudou no desenho\", "
                                 f"≥ {MIN_REDESENHO} caracteres) ou a ordem do dono (--override-dono "
                                 f"\"frase literal, dd/mm/aaaa\")")

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
        # ADR-117: arquivo unico so vale como evidencia de J3 se TEM a Parte B — Aceite; um spec.md
        # sem aceite passaria so' por existir, que e' o "se aplicavel" silencioso de novo.
        if ok_val:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import spec_fonte  # noqa: E402
            vpath = validation if os.path.isfile(validation) else os.path.join(ROOT, validation)
            if spec_fonte.eh_unico(vpath):
                try:
                    aceite = spec_fonte.ler_parte(vpath, "aceite")
                except spec_fonte.SpecInvalida as e:  # recusa LIMPA, nao traceback (QA 25/09)
                    raise ValueError(f"J3: o spec.md unico informado e' invalido ({e})")
                if aceite is None:
                    raise ValueError("J3: o spec.md unico informado nao tem a 'Parte B — Aceite' — "
                                     "escreva o aceite binario antes de registrar J3")
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
    ap.add_argument("--redesenho", help="circuit breaker (ADR-118): o que mudou no DESENHO depois das "
                                        "rodadas reprovadas; reinicia a contagem")
    ap.add_argument("--override-dono", help="circuit breaker (ADR-118): frase LITERAL do dono + data "
                                            "(ex.: 'sem limite de rodadas de QA, 25/09/2026')")
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
    if args.redesenho:
        verdict["redesenho"] = args.redesenho
    if args.override_dono:
        verdict["override_dono"] = args.override_dono
    try:
        jpath, mpath = write_artifact(verdict)
    except ValueError as e:
        print(f"[qa-evidence] RECUSADO: {e}")
        return 3 if "CIRCUIT BREAKER" in str(e) else 1
    print(f"[qa-evidence] gravado: {os.path.relpath(jpath, ROOT)} + {os.path.relpath(mpath, ROOT)}")
    # Avisa AGORA se esta gravação encheu o breaker (a próxima rodada será recusada) e declara o
    # débito, para que o laço interrompido não suma quando a sessão acabar.
    gravado = json.load(open(jpath, encoding="utf-8"))
    atual = {"recomendacao": gravado.get("recomendacao"), "achados_fp": _achados_fp(gravado),
             "reinicio": destrava_breaker(gravado)}
    motivo = motivo_circuit_breaker(list(gravado.get("substitui") or []) + [atual])
    if motivo:
        print(f"[qa-evidence] CIRCUIT BREAKER armado em '{gravado['bloco']}': {motivo}. A próxima "
              f"rodada exige --redesenho ou --override-dono.")
        slug = "circuit-breaker-" + _slug(gravado["bloco"])
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "trabalhos.py"), "registrar",
                               "--slug", slug, "--repo", os.path.basename(ROOT),
                               "--nome", f"Circuit breaker de QA disparado em {gravado['bloco']}",
                               "--objetivo", "Decidir redesenho ou ordem do dono antes de nova rodada de QA",
                               "--pendente", motivo,
                               "--proximo", "Redesenhar (registrar com --redesenho) ou levar ao dono"],
                              capture_output=True, text=True)
        if proc.returncode == 0:
            print(f"[qa-evidence] débito declarado: trabalho '{slug}' (reaparece em toda sessão).")
        else:  # não afirmar débito que não foi gravado (QA de 26/09)
            print(f"[qa-evidence] AVISO: débito NÃO declarado ({(proc.stdout + proc.stderr).strip()[:200]}). "
                  f"Registre à mão: python tools/trabalhos.py registrar --slug {slug} ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
