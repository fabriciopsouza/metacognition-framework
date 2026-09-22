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
existe para pegar. O git-hook local EXISTE e E' trava: `.git/hooks/pre-commit`, instalado por
`tools/install_git_hooks.py`, roda este script a cada commit e bloqueia quando falta
evidencia. [CORRIGIDO na 16a rodada: esta linha dizia o contrario — "nao existe nesta
maquina (.git/hooks vazio) e nunca foi trava" — escrita em 13/08/2026, tres dias ANTES do
gancho ser instalado, e nunca revista. Quinze rodadas de QA reeditaram este arquivo e
passaram por cima da linha. E' a mesma classe que o paragrafo acima denuncia: mecanismo
mente quando o comentario envelhece. Verificado por inspecao, nao por memoria:
`install_git_hooks.py --verificar` confirma, e o arquivo e' byte-identico ao template.]
Escapatoria declarada: `git commit --no-verify` contorna o gancho, e o proprio texto do
bloqueio diz isso — trava local e' atrito consciente, nao prisao.

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

# --- Severidade: o ledger usa MUITAS grafias para a mesma gravidade (ALTA, ALTO, CRITICO,
# BLOQUEANTE, GRAVE, MEDIA-ALTA, ALTO-EVITADO...), e uma regra que casasse so com "ALTA" deixaria
# passar a maioria delas. Quantos exatamente, com a data da medicao e o comando que a refaz, esta
# no ADR-115 — aqui NAO, de proposito: comentario nao tem quem o recalcule, e este mesmo numero ja
# ficou para tras QUATRO vezes neste arquivo. Por isso normaliza-se, e o que NAO for leve conta como
# BLOQUEANTE: fail-closed. Vocabulario novo que ninguem previu tem de travar o gate e pedir
# classificacao, nunca passar como inocuo.
SEVERIDADE_LEVE = {
    "MEDIA", "MEDIO", "MEDIA-BAIXA", "BAIXA", "BAIXO", "PEQUENO", "MENOR",
    "INFORMACIONAL", "INFORMATIVO", "OBSERVACAO", "RESSALVA", "NENHUMA", "N/A",
}
# String vazia NAO entra na lista de leves de proposito: achado sem severidade declarada nao
# pode ser classificado como inocuo — quem nao declarou nao classificou. Medido em 13/09/2026:
# zero achados historicos sem severidade, entao a regra fecha a porta sem reescrever o passado.
# Estados que ENCERRAM um achado bloqueante. 'aceito' NAO basta sozinho para bloqueante:
# risco alto assumido exige assinatura do dono no campo `aceito_por`.
ESTADO_RESOLVIDO = {"corrigido", "corrigida", "resolvido", "resolvida"}


def _norm(x) -> str:
    return str(x or "").strip().upper().replace("Í", "I").replace("Ó", "O").replace("É", "E")


# A defesa da chave do container passou por tres formas, e as duas primeiras viraram CODIGO MORTO
# quando a terceira chegou: `CHAVES_ACHADOS` (lista de grafias) e `_chave_norm` foram REMOVIDOS,
# nao mantidos "por garantia". Quem denunciou foi a prova por mutacao — sabotagem em ramo
# inalcancavel nunca morre. A allowlist `CAMPOS_CONHECIDOS` os absorve: qualquer grafia diferente
# da canonica ja e' campo desconhecido, e campo desconhecido bloqueia.

def _bloqueante(problema) -> bool:
    """True se o achado e' de severidade que impede aprovacao (fail-closed no desconhecido)."""
    return _norm(problema.get("severidade")) not in SEVERIDADE_LEVE


# Os 20 vereditos aprovativos anteriores ao campo `estado`, enumerados COM O HASH DO CONTEUDO.
# Precedente: o ADR-108 listou nominalmente os 34 vereditos sem procedencia.
#
# TRES versoes desta regra foram derrubadas pela revisao adversarial, cada uma um nivel abaixo:
#   1. por SCHEMA  — "nenhum achado declara `estado`": o autor controla se o campo existe,
#      entao bastava OMITI-LO. Bypass reproduzido contra o binario real, exit 0.
#   2. por NOME    — lista de arquivos: o autor controla o nome, e `qa_evidence.write_artifact()`
#      grava sem checar existencia, entao bastava SOBRESCREVER um dos 20. Idem, exit 0.
#   3. por CONTEUDO (esta) — o hash congela o que foi de fato auditado. Sobrescrever o arquivo
#      muda o hash e a isencao cai: o veredito volta a ser cobrado como qualquer outro.
#
# Enquanto a identidade do legado for algo que o avaliado consegue PRODUZIR, a isencao continua
# autodeclarada. Hash e' a primeira forma que ele nao consegue forjar sem mudar o conteudo.
VEREDITOS_LEGADOS = {
    "adr-100-registro-de-trabalhos-handoff-persistente.json": "e051f3c6fa64d064",
    "adr-102-padrao-do-conjunto-documental-de-projeto.json": "a4cb65c6c47e93a1",
    "adr-108-procedencia-do-veredito.json": "e6b0eca74e4b4573",
    "emenda-squad-gate-arquivo-novo.json": "99fb6d31cfb45ff7",
    "passivo-lote-4-registro-sem-enforcement.json": "2174fa40b9da21d2",
    "release-1.80.0-prova-de-mutacao-adr-106.json": "968dc486a57a94f9",
    "release-1.81.0-rotacao-do-history.json": "5dd5686f6c7c655a",
    "release-1.82.0-instalador-do-gancho-do-squad-gate.json": "22d28fa86a67fe1d",
    "release-1.84.0-conformance-de-topologia.json": "8b722861ece4c827",
    "release-1.85.0-quadro-de-gestao-e-canarios-que-mentiam.json": "7754c3745f8bf265",
    "release-1.86.0-vitrine-com-numeros-verificados.json": "0314dc0493ce9a36",
    "release-1.87.0-alarme-de-deriva-das-distribuicoes.json": "c3308b01946c417b",
    "release-1.89.0-passivo-do-registro-acabou.json": "331ef0d1e5e78368",
    "release-1.90.0-procedencia-do-veredito.json": "c1e814271ee81ebc",
    "v1.54.0-release.json": "c9e15bbe16cd3be2",
    "v1.57.0-adr-078.json": "0a67ca693e49f30c",
    "v1.58.0-adr-079-080.json": "239305b94429fc62",
    "v1.58.1-boot-barato.json": "a62a875b9e5df3f6",
    "v1.74.0-hitl-corte-score-6.json": "32f6effa3c70bcd1",
    "v1.75.0-path-resolve-no-destinatario.json": "47f272359c9d9b96",
}


def sha_do_veredito(caminho) -> str:
    """sha256 (16 primeiros hex) do CONTEUDO do arquivo, com fim de linha normalizado.

    NORMALIZA CRLF->LF ANTES DE HASHEAR (achado da CI em 22/09/2026, e o primeiro defeito
    deste bloco que so' aparecia FORA do Windows).

    Os 20 pinos foram calculados numa maquina Windows, a partir dos bytes com CRLF que o
    `core.autocrlf` entrega no checkout. O repositorio guarda LF. Consequencia: no Windows o
    checkout converte de volta e o pino bate; no macOS e no Linux o arquivo fica LF e o hash
    NUNCA bate. O canario dos vereditos legados so' podia passar numa plataforma — e ninguem
    percebeu porque estes arquivos entraram no repositorio agora, entao esta foi a primeira
    vez que a CI multiplataforma os viu.

    A correcao e' o que o pino sempre quis medir: o CONTEUDO. Fim de linha e' convencao de
    checkout, nao bytes do veredito — dois arquivos que so' diferem nisso dizem a mesma coisa,
    e um mecanismo de integridade que os chama de diferentes esta' medindo o sistema de
    arquivos, nao a evidencia.
    """
    import hashlib
    try:
        with open(caminho, "rb") as fh:
            return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()[:16]
    except Exception:
        return ""


def veredito_legado(v) -> bool:
    """True so para os 20 vereditos enumerados E com o conteudo original intacto.

    Nome fora da lista: nao e' legado. Nome na lista mas conteudo alterado: NAO e' legado —
    sobrescrever um arquivo legado nao herda a isencao dele. Veredito sem `_sha256` (sintetico,
    de teste, ou vindo de fora do ledger): nao e' legado. Fail-closed em todos os casos.
    """
    nome = os.path.basename(str(v.get("_arquivo") or ""))
    esperado = VEREDITOS_LEGADOS.get(nome)
    return bool(esperado) and str(v.get("_sha256") or "") == esperado


# Campos de topo que um veredito pode ter. Fechar o conjunto do CERTO, em vez de enumerar o
# ERRADO, e' a licao das seis rodadas: `Problemas` (4a) foi barrada por lista de grafias, e
# `probIemas` (5a) escapou dela; a chave virou obrigatoria, e `problemаs` com 'a' CIRILICO
# escapou de novo — bastava declarar a canonica vazia e esconder o achado na irma invisivel.
#
# Nao ha grafia inventavel que passe por um conjunto FECHADO. Campo desconhecido bloqueia e pede
# declaracao, exatamente como severidade desconhecida. Levantado dos 66 vereditos do ledger em
# 13/09/2026: campo novo legitimo custa uma linha aqui — do lado certo do atrito.
CAMPOS_CONHECIDOS = frozenset({
    "bloco", "papel", "rodada", "passou", "recomendacao", "veredito", "data", "release",
    "juncao", "postura", "resumo", "problemas", "verificacoes_executadas", "atestacao",
    "escopo_paths", "sha_revisado", "nao_verificado", "steelman", "recomendacao_do_critico",
    "nota_do_autor", "veredito_1a_rodada", "autor", "critico", "canarios", "observacao",
    "suite_apos_rebase", "autor_modelo", "critico_modelo", "heterogeneo", "rodadas",
    "achado_principal", "refutado_pelo_critico", "ressalvas_aceitas", "LACUNA_DE_PROCEDENCIA",
    "o_que_NAO_verifiquei",
    # A CADEIA DE SUBSTITUICAO (17/09/2026). `write_artifact` passou a encadear o
    # veredito anterior do mesmo bloco em vez de sobrescreve-lo em silencio — antes,
    # uma segunda gravacao apagava a reprovacao e o ledger contava uma historia em
    # que ela nunca existiu.
    #
    # Os dois campos sao ESCRITOS PELA FERRAMENTA, nunca digitados por um critico.
    # E foram criados sem serem declarados aqui: o gate, corretamente, tratou-os
    # como "achado escondido numa chave que eu nao leio" e barrou o primeiro
    # veredito que os carregava. A allowlist fez o trabalho dela contra o proprio
    # autor dela — que e' exatamente o ponto de ela existir.
    "substitui", "substitui_reprovacao",
    # O CONTEUDO QUE O CRITICO DE FATO VIU (21/09/2026, achado ALTA da 36a rodada).
    # `sha_revisado` e' um COMMIT, e commit nenhum descreve conteudo que ainda nao foi
    # commitado. Como o gate roda no pre-commit — quando, por definicao, todo arquivo do
    # bloco esta' fora do HEAD — a checagem de recencia por ancestralidade ficava inerte
    # justamente para o bloco que entra. Medido: tres vereditos aprovativos de AGOSTO
    # ainda contavam como recentes para arquivos editados em SETEMBRO.
    # Este campo grava o hash do BLOB indexado de cada caminho de `escopo_paths`, que e'
    # a unica coisa que descreve conteudo nao commitado. Escrito pela ferramenta, nunca
    # digitado. Veredito sem ele nao e' invalido: cai na regra antiga e entra no relatorio
    # de divida declarada, mesmo molde dos 20 anteriores ao campo `estado` — campo novo
    # nao e' retroativo, e fabricar procedencia para veredito velho seria o teatro que
    # este ADR combate.
    "blobs_revisados",
    # marcados por load_evidence a partir do disco, nunca vindos do JSON
    "_arquivo", "_sha256",
})

# Campos que um ACHADO pode ter. Mesma licao da allowlist de topo, um nivel abaixo: a 7a rodada
# escondeu um CRITICO/aberto DENTRO de um achado leve, numa chave arbitraria (`sub_achado`), e o
# gate — que so itera a lista e le os campos que conhece — nunca o viu. A allowlist foi
# LEVANTADA do ledger inteiro em 14/09/2026 e deu 7 chaves, nenhuma surpresa. O total de
# achados fica fora do comentario de proposito: ele cresce a cada rodada de QA e nao tem
# quem o recalcule (licao da 12a rodada); o que importa aqui e' a lista, nao o denominador.
CAMPOS_DO_ACHADO = frozenset({
    "severidade", "descricao", "local", "estado", "cenario_de_falha", "status", "fix",
    "aceito_por",
})


def campos_de_achado_desconhecidos(p):
    return sorted(k for k in p.keys() if k not in CAMPOS_DO_ACHADO)


# Textos que TEM letra latina e mesmo assim nao sao assinatura — inclusive os que NEGAM a
# assinatura. A 8a rodada mostrou que `aceito_por: "nao assinado"` passava: a frase que nega o
# consentimento satisfazia o teste de que ha consentimento.
#
# LIMITE DECLARADO, e o mais importante deste ADR: `aceito_por` e' um campo de texto que o AUTOR
# preenche. Nenhuma checagem de forma prova que o dono assinou — no maximo dificulta o descuido.
# Assinatura autoatestada e' da mesma familia de "o autor escolhe o prompt do critico": o gate
# cobra a forma, nao a autenticidade. Fechar isso de verdade exigiria assinatura fora do alcance
# do autor, e esta fora do escopo desta ADR.
NAO_SAO_ASSINATURA = frozenset({
    "", "x", "xx", "n a", "na", "nao", "nao assinado", "nao assinada", "sem assinatura",
    "none", "null", "nil", "tbd", "pendente", "a definir", "ninguem", "anonimo",
    "autor", "eu", "?", "??", "???", "sim", "ok", "aceito", "assinado", "dono",
})


def assinatura_valida(x) -> bool:
    """True se ha assinatura DE VERDADE: pelo menos uma letra LATINA.

    Tres tentativas ate acertar a natureza da regra:
      1. `.strip()` — nao remove zero-width space; `​` assinava.
      2. remover uma lista de invisiveis — blocklist: U+3164, U+2800 e U+180E ficaram de fora.
      3. exigir categoria L — ainda frouxo: U+3164 HANGUL FILLER TEM categoria `Lo`. Para o
         Unicode ele e' letra; para o olho, e' vazio.
    A regra que fecha e' de SCRIPT, nao de categoria: assinatura aqui e' nome proprio em
    portugues, e nome em portugues tem letra latina. `LATIN CAPITAL LETTER F` passa,
    `HANGUL FILLER` nao.

    LIMITE DECLARADO: assinatura em cirilico, arabe, han ou qualquer script nao-latino e'
    recusada. E' restricao cultural consciente, nao descuido — se um dia houver dono cujo nome
    nao se escreve em latino, amplia-se aqui, de propria vontade e por escrito.
    """
    import unicodedata
    s = str(x or "").strip()
    if not any(unicodedata.name(c, "").startswith("LATIN") for c in s):
        return False
    # "nao assinado" TEM letra latina e NEGA a assinatura. Script resolve o invisivel, nao o
    # conteudo. Aqui a blocklist e' inevitavel — e' semantica, nao forma — e vem com o limite
    # declarado abaixo.
    norm = "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")
    norm = " ".join(norm.replace("/", " ").replace("-", " ").replace(".", " ").split())
    return norm not in NAO_SAO_ASSINATURA and len(norm) >= 2


def campos_desconhecidos(v):
    """Chaves de topo fora do conjunto conhecido — cada uma e' um esconderijo em potencial."""
    return sorted(k for k in v.keys() if k not in CAMPOS_CONHECIDOS)


def _problemas_bem_formados(v):
    """(lista, motivo_do_erro). `problemas` tem de ser lista de objetos.

    A revisao adversarial mostrou que `problemas` como dict, ou como lista de strings, caia
    no ramo de isencao sem crash — `"estado" in p` faz SUBSTRING quando p e' string. Schema
    malformado agora BLOQUEIA em vez de virar passe livre.

    E mostrou, tres rodadas depois, que a CHAVE tambem era bypass — `Problemas`, depois
    `probIemas` (homoglifo I/l), depois `problemаs` com 'a' CIRILICO ao lado da canonica limpa.
    Enumerar grafia errada nunca fechou; o que fechou foi a allowlist `CAMPOS_CONHECIDOS`.
    """
    # A chave canonica e' OBRIGATORIA. Antes, "chave ausente" e "chave numa grafia que eu nao
    # reconheco" colapsavam no mesmo ramo permissivo — e bastava um homoglifo para esconder o
    # achado inteiro: `probIemas` (I maiusculo no lugar do l minusculo) nao colide com PROBLEMAS
    # no .upper(), escapava da lista de grafias conhecidas e saia como "nada a cobrar". Exit 0
    # com um CRITICO em aberto, reproduzido contra o binario real.
    #
    # Perseguir homoglifo e' corrida perdida: depois de I/l vem O/0, depois cirilico, depois
    # zero-width. Exigir o campo mata a classe de uma vez — nenhuma grafia inventada substitui
    # um campo exigido. Medido em 13/09/2026: os vereditos do ledger ja declaram `problemas`,
    # zero quebram.
    estranhos = campos_desconhecidos(v)
    if estranhos:
        return None, ("campo(s) de topo desconhecido(s) no veredito: %s. Um achado escondido numa "
                      "chave que o gate nao le e' invisivel — se o campo e' legitimo, declare-o "
                      "em CAMPOS_CONHECIDOS" % estranhos)
    if "problemas" not in v:
        return None, ("veredito sem a chave `problemas` — declare-a explicitamente, mesmo que "
                      "vazia (`\"problemas\": []`). Ausencia de campo nao e' ausencia de achado")
    ps = v.get("problemas")
    if ps is None:
        return [], ""                       # chave presente com null: nada a cobrar
    if not isinstance(ps, list):
        return None, "campo `problemas` nao e' lista (e' %s)" % type(ps).__name__
    ruins = [i for i, p in enumerate(ps) if not isinstance(p, dict)]
    if ruins:
        return None, "achados nao sao objetos nos indices %s" % ruins
    estranhos_no_achado = [(i, campos_de_achado_desconhecidos(p)) for i, p in enumerate(ps)
                           if campos_de_achado_desconhecidos(p)]
    if estranhos_no_achado:
        return None, ("campo(s) desconhecido(s) DENTRO de achado: %s. Achado aninhado numa chave "
                      "que o gate nao le e' invisivel — declare-o como achado proprio na lista, "
                      "ou registre o campo em CAMPOS_DO_ACHADO" % estranhos_no_achado)
    return ps, ""


def achados_bloqueantes_abertos(v):
    """Achados BLOQUEANTES que o veredito aprovativo nao resolveu.

    O gate exigia apenas o ROTULO aprovativo e a atestacao de isolamento — nunca olhava a
    severidade nem o estado dos achados. Um 'aprovar_com_ressalvas' carregando um ALTA em
    aberto passava, e em 13/09/2026 havia um veredito real nessa forma.

    Vereditos legados (ver `veredito_legado`) nao sao cobrados, mas TAMBEM nao passam mudos:
    `legados_declarados()` os lista, para a divida ficar visivel em vez de perdoada em
    silencio — mesmo tratamento que o ADR-108 deu aos 34 vereditos sem procedencia.
    """
    if veredito_legado(v):
        return []
    ps, erro = _problemas_bem_formados(v)
    if ps is None:
        return [{"severidade": "BLOQUEANTE", "estado": "aberto",
                 "descricao": "schema de `problemas` invalido: %s" % erro}]
    fora = []
    for p in ps:
        if not _bloqueante(p):
            continue
        estado = str(p.get("estado") or "").strip().lower()
        if estado in ESTADO_RESOLVIDO:
            continue
        if estado == "aceito" and assinatura_valida(p.get("aceito_por")):
            continue            # risco alto assumido, COM assinatura de quem assumiu
        fora.append(p)
    return fora


def legados_declarados():
    """[(arquivo, n_achados_bloqueantes)] dos vereditos aprovativos de schema antigo."""
    import glob
    import json
    out = []
    for f in sorted(glob.glob(os.path.join(QA_DIR, "*.json"))):
        try:
            with open(f, encoding="utf-8") as fh:
                v = json.load(fh, object_pairs_hook=_sem_chave_duplicada)
        except Exception as e:
            # ALTA da 26a rodada, e o achado e' contra o AUTOR, nao contra o codigo: o veredito da
            # 25a afirmava que esta denuncia ja existia ("CORRIGIDO com denuncia por nome"), e ela
            # NAO existia — o `except` seguia mudo. Rotulo divergindo de conteudo, dentro do ADR
            # que existe para impedir isso. Agora existe de verdade.
            #
            # NAO bloqueia, de proposito: esta funcao alimenta o RELATORIO de divida legada, nao a
            # decisao do gate. Mas sumir calado contradizia a paridade que o veredito afirmava.
            print("[squad-gate] divida legada: %s ignorado (%s: %s)" % (os.path.basename(f),
                                                                        type(e).__name__, e))
            continue
        v["_arquivo"] = os.path.basename(f)
        v["_sha256"] = sha_do_veredito(f)
        if v.get("recomendacao") in APPROVING and veredito_legado(v):
            n = sum(1 for p in (v.get("problemas") or []) if _bloqueante(p))
            if n:
                out.append((os.path.basename(f), n))
    return out

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def load_manifest(path: str = MANIFEST) -> dict:
    return json_estrito(path)


def classify(paths, manifest) -> set:
    """Path(s) staged -> conjunto de papeis OBRIGATORIOS (deterministico por match de path)."""
    req: set = set()
    for p in paths:
        p = p.replace("\\", "/").strip()
        for item in manifest.get("matriz", []):
            m = item.get("match", {})
            # Caixa NAO distingue path para efeito de enforcement. CRITICO da 15a rodada, e o
            # mais barato dos quinze: `tools/backdoor.PY` nao casava com o suffix `.py`, entao
            # `classify` devolvia conjunto VAZIO, `evaluate` devolvia faltam=[] com ledger vazio, e
            # um arquivo Python NOVO entrava sem exigir papel nenhum. Sem forjar atestacao, sem
            # Unicode, sem homoglifo — so' trocando a caixa da extensao. Valia para toda a matriz:
            # `Docs/ADR/`, `_SHARED/`, `CLAUDE.MD`, `behaviors/Manifest.json`.
            #
            # A licao central deste ADR ja estava aplicada a severidade (`_norm`), a campo de JSON
            # (`CAMPOS_CONHECIDOS`) e a assinatura (`assinatura_valida`) — e nunca ao primeiro
            # filtro de tudo, que decide QUAL PATH exige QUAL PAPEL.
            #
            # Casar mais e' o lado seguro: no maximo exige-se papel de um arquivo que talvez nao
            # precisasse. Casar de menos e' o que deixava passar.
            pb = p[2:] if p.startswith("./") else p
            pb = pb.casefold()
            hit = (("suffix" in m and pb.endswith(str(m["suffix"]).casefold()))
                   or ("prefix" in m and pb.startswith(str(m["prefix"]).casefold()))
                   or ("exact" in m and pb == str(m["exact"]).casefold()))
            if hit:
                req.update(item.get("exige", []))
    return req


class ChaveDuplicada(ValueError):
    """JSON com a MESMA chave duas vezes. Achado CRITICO da 24a rodada, e o mais barato de todos.

    `json.load` resolve chave duplicada em silencio: a segunda ocorrencia vence, a primeira
    desaparece sem erro. Isso acontece ANTES de qualquer validacao deste arquivo rodar, entao
    `CAMPOS_CONHECIDOS`, `CAMPOS_DO_ACHADO`, a chave obrigatoria `problemas` e toda a defesa contra
    homoglifo sao inuteis: o dict que o gate recebe ja chega com uma unica chave, de nome canonico,
    tipo correto, sem nada de anomalo para a allowlist reprovar.

    Duas formas, ambas reproduzidas contra o binario real:

        {"problemas": [{...CRITICO aberto...}], "problemas": []}   -> o achado inteiro some
        {"severidade": "CRITICO", "estado": "aberto", "estado": "corrigido"}  -> o achado "fecha"

    A segunda e' a pior: um unico achado, uma chave duplicada, e `achados_bloqueantes_abertos`
    devolve lista vazia. O arquivo em `_meta/qa/` mostra o CRITICO em texto puro para qualquer
    humano que o abra, e o gate imprime OK e sai 0.

    Nao precisa de Unicode, homoglifo, zero-width nem cirilico — nenhuma das armas que as rodadas 4
    a 8 precisaram. E' JSON ASCII valido, do jeito que sai de copiar um template e esquecer de
    apagar o bloco anterior. Mesma familia de "nao precisa de ma-fe, esquecer basta" que a 13a
    rodada documentou para o campo `autor` ausente.
    """


def _sem_chave_duplicada(pares):
    visto = {}
    for chave, valor in pares:
        if chave in visto:
            raise ChaveDuplicada(chave)
        visto[chave] = valor
    return visto


def json_estrito(caminho):
    """Le JSON recusando chave duplicada. Usado em TODA leitura de ledger e de manifesto.

    Nao basta aplicar no veredito: o manifesto tambem decide comportamento do gate, e uma `matriz`
    duplicada ali apagaria metade das entradas sem aviso.
    """
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh, object_pairs_hook=_sem_chave_duplicada)


def load_evidence(qa_dir: str = QA_DIR) -> list:
    out = []
    if os.path.isdir(qa_dir):
        for f in os.listdir(qa_dir):
            if f.endswith(".json"):
                try:
                    _p = os.path.join(qa_dir, f)
                    try:
                        _v = json_estrito(_p)
                    except ChaveDuplicada as e:
                        # NAO descarta: MARCA. Achado CRITICO da 25a rodada, e uma correcao minha
                        # que criou um furo novo do lado oposto.
                        #
                        # A 24a fechou a chave duplicada recusando o arquivo e denunciando por nome.
                        # Mas denuncia e' `print`, e `print` NAO e' bloqueio: uma reprovacao
                        # LEGITIMA — CRITICO aberto correto, mesmo `sha_revisado`, mesmo escopo —
                        # sumia do julgamento inteiro por causa de uma chave duplicada num campo
                        # IRRELEVANTE como `resumo`, e o aprovativo ao lado passava sozinho. Isso e'
                        # exatamente o cenario que as rodadas 8, 9 e 10 fecharam, reaberto pelo
                        # remedio: o gate jogava fora a PROVA do bloqueio em vez de trata-la COMO
                        # bloqueio.
                        #
                        # A regra certa e' "nao consigo confirmar => nao passa". O artefato ilegivel
                        # entra no ledger como bloqueio sintetico e `evaluate` trava tudo ate alguem
                        # corrigir o arquivo — que a mensagem nomeia.
                        print("[squad-gate] EVIDENCIA ILEGIVEL: %s tem a chave %r duas vezes. "
                              "JSON duplicado e' resolvido em silencio pelo parser e pode apagar um "
                              "achado inteiro antes de qualquer validacao. O gate BLOQUEIA ate o "
                              "arquivo ser corrigido." % (f, str(e)))
                        out.append({"_recusado": f, "_motivo": "chave duplicada: %s" % e})
                        continue
                    if not isinstance(_v, dict):
                        # JSON valido cujo topo NAO e' objeto (`null`, lista, numero). Antes era
                        # anexado cru ao ledger e, dependendo da ordem de os.listdir(), derrubava
                        # `_atestacao_valida` com AttributeError. Bloqueava por CRASH — e este
                        # arquivo ja declara, noutro ponto, que "fail-closed por crash nao e'
                        # fail-closed": falta a mensagem que nomeia o arquivo a corrigir.
                        print("[squad-gate] EVIDENCIA ILEGIVEL: %s nao contem um objeto JSON no "
                              "topo (achei %s). O gate BLOQUEIA ate o arquivo ser corrigido."
                              % (f, type(_v).__name__))
                        out.append({"_recusado": f,
                                    "_motivo": "topo nao e' objeto: %s" % type(_v).__name__})
                        continue
                    if isinstance(_v, dict):
                        # marca ORIGEM e CONTEUDO: e' o par que distingue legado genuino de
                        # arquivo legado sobrescrito com conteudo novo
                        _v["_arquivo"] = f
                        _v["_sha256"] = sha_do_veredito(_p)
                    out.append(_v)
                except Exception as e:
                    # CRITICO da 26a rodada, e a MESMA correcao pela metade pela segunda vez.
                    #
                    # A 25a mudou a regra para "nao consigo confirmar => nao passa" — e implementou
                    # isso SO' para `ChaveDuplicada`. Todo o resto do JSON malformado continuava
                    # caindo aqui e sumindo em silencio: arquivo TRUNCADO, vazio, encoding invalido,
                    # permissao negada. E uma reprovacao legitima que caisse nisso desaparecia do
                    # julgamento, deixando o aprovativo ao lado passar — exatamente o furo que a 25a
                    # dizia ter fechado.
                    #
                    # O vetor nao e' hipotetico: `qa_evidence.write_artifact()` grava com
                    # `json.dump` direto no arquivo final, SEM temp-file + rename. Qualquer
                    # interrupcao durante a escrita (processo morto, disco cheio, taskkill — a mesma
                    # familia que a 3a rodada deste ADR documentou para o script de mutacao) deixa
                    # um .json truncado no ledger. Marcador de merge malconduzido faz o mesmo.
                    #
                    # Agora TODA forma de ilegivel marca e bloqueia, com o motivo real na mensagem.
                    print("[squad-gate] EVIDENCIA ILEGIVEL: %s nao pode ser lido (%s: %s). O gate "
                          "BLOQUEIA ate o arquivo ser corrigido."
                          % (f, type(e).__name__, e))
                    out.append({"_recusado": f, "_motivo": "%s: %s" % (type(e).__name__, e)})
    return out


def _atestacao_valida(v) -> bool:
    """Veredito aprovativo, COM atestacao de isolamento e SEM achado bloqueante em aberto."""
    if v.get("recomendacao") not in APPROVING:
        return False
    if achados_bloqueantes_abertos(v):
        return False
    at = v.get("atestacao") or {}
    if not isinstance(at, dict):
        return False        # atestacao malformada bloqueia; antes derrubava o processo inteiro
                            # com AttributeError, e um unico .json ruim em _meta/qa/ travava o
                            # gate para todo commit — fail-closed por crash nao e' fail-closed
    agent = str(at.get("agentId", "")).strip()
    modelo = str(at.get("modelo", "")).strip()
    autor = str(at.get("autor", "") or at.get("modelo_autor", "")).strip()
    # `autor` OBRIGATORIO — achado CRITICO da 13a rodada, e o bypass mais barato dos treze.
    #
    # A versao anterior era `(not autor or modelo != autor)`: com o campo AUSENTE, `not autor` e'
    # True e a expressao inteira e' True. A checagem "modelo do critico != autor do bloco" so'
    # rodava para quem se desse ao trabalho de preencher o campo. Ou seja: o autor podia escrever
    # o proprio veredito aprovativo do proprio codigo, sem mentir em NADA — bastava nao escrever
    # uma linha — e o gate imprimia "OK, evidencia atestada presente".
    #
    # Nao precisa de homoglifo, Unicode, encoding, escopo nem sha malformado: nenhuma das tecnicas
    # que as doze rodadas anteriores precisaram. Basta uma omissao, e nem de ma-fe — esquecer o
    # campo ja bastava. E estava na checagem que da NOME ao mecanismo: a defesa anti-teatro.
    #
    # O cabecalho deste arquivo e o ADR-092 afirmavam a garantia como incondicional; nao era. Nao
    # era limite aceito, era buraco nao percebido — por isso fecha, em vez de virar declaracao.
    #
    # Raio de explosao medido antes de fechar: NENHUM veredito atestado do ledger deixava de
    # declarar `autor` ou `modelo_autor`. O numero absoluto fica FORA do comentario de
    # proposito — ele cresce a cada rodada de QA e nao tem quem o recalcule (licao da 12a
    # rodada). Para refazer a conta, o comando esta no ADR-115.
    #
    # Ausencia deixa de significar "isolamento nao contestado" e passa a significar "isolamento nao
    # comprovado", que e' o default de todo o resto deste arquivo.
    return bool(agent and modelo and autor and _norm_modelo(modelo) != _norm_modelo(autor))


def _norm_modelo(x) -> str:
    """Normaliza nome de modelo para a comparacao `modelo != autor`. CRITICO da 14a rodada.

    A comparacao era de string CRUA, entao `Claude-Sonnet-5` != `claude-sonnet-5` e a
    autoatestacao passava com o mesmo modelo escrito duas vezes de jeitos diferentes: caixa
    diferente, espaco duplo interno, ou um zero-width space invisivel colado no fim. Nem precisava
    de homoglifo — a tecnica mais cara, que as rodadas 4 a 7 precisaram.

    A funcao vizinha `assinatura_valida`, no MESMO arquivo, ja fazia toda essa normalizacao contra
    exatamente estes truques. Quinta vez neste bloco que a defesa existia num irmao e faltava no
    outro — e desta vez o irmao esquecido era o coracao da defesa anti-teatro.

    Raio de explosao medido antes de fechar: NENHUM veredito atestado do ledger dependia de
    caixa, espaco ou invisivel para se distinguir; todos usavam pares legitimamente diferentes
    (sonnet/opus, sonnet/fable), em minuscula consistente. Sem numero absoluto aqui de
    proposito — a populacao do ledger cresce a cada rodada (licao da 12a rodada).
    """
    import unicodedata
    s = unicodedata.normalize("NFKC", str(x or ""))
    # Cf = formatacao invisivel (zero-width, RLM/LRM); Mn = acento combinante. Nenhum dos dois
    # distingue dois nomes de modelo para um olho humano, entao nao pode distinguir para o gate.
    s = "".join(c for c in s if unicodedata.category(c) not in ("Cf", "Mn"))
    # Separador e espaco sao REMOVIDOS, nao trocados por espaco. A 14a rodada trocava por espaco,
    # e isso so' funde quando os DOIS lados tem separador: `gpt-4` virava "gpt 4" e `gpt4` continuava
    # "gpt4" — dois modelos diferentes para o gate, o mesmo modelo para qualquer pessoa. Bypass
    # ainda mais barato que os da 14a: basta OMITIR um hifen num dos dois campos. Achado CRITICO da
    # 15a rodada, que reabriu pelo angulo vizinho a defesa que a 14a acabara de fechar.
    for sep in ("-", "_", ".", "/", " "):
        s = s.replace(sep, "")
    return s.casefold()


def _cobre(escopo, path: str) -> bool:
    """O escopo declarado no veredito cobre este path? Prefixo exato ou path exato.

    CASEFOLD — achado CRITICO da 18a rodada, e a OITAVA vez neste bloco em que a defesa existia
    num irmao e faltava no outro. `classify()` recebeu `.casefold()` na 15a rodada (achado
    `backdoor.PY`) e esta funcao, que compara path exatamente do mesmo jeito, nao recebeu.

    O caminho que isso destravava e' o pior possivel, porque `_cobre` e' usada pelos DOIS lados:
    `_qa_critic_attested` (o aprovativo cobre o alvo?) e `_reprovacao_vigente` (a reprovacao cobre
    o mesmo escopo?). Uma reprovacao com CRITICO em aberto, no MESMO `sha_revisado` e sobre o MESMO
    arquivo, deixava de invalidar o aprovativo se quem escreveu `escopo_paths` digitou
    `Tools/Squad_Gate.py` em vez de `tools/squad_gate.py`. Em sistema de arquivos case-insensitive
    — o desta maquina — isso nao exige ma-fe nenhuma.

    ESTE CASEFOLD CORTA PARA OS DOIS LADOS, e isso precisa ser dito: ele faz a reprovacao morder
    MAIS (fail-closed) e tambem faz o aprovativo cobrir MAIS (fail-open). Nao e' escolha entre os
    dois — e' correcao de um erro anterior. `Tools/X.py` e `tools/x.py` sao O MESMO ARQUIVO; trata-
    los como dois quebrava as duas direcoes ao mesmo tempo. Medido no ledger real em 14/09/2026:
    ZERO paths mudam de cobertura com a normalizacao — nenhum veredito existente passa a cobrir
    nada que nao cobrisse.
    """
    p = path.replace("\\", "/").strip().casefold()
    for e in escopo:
        e = str(e).replace("\\", "/").strip().casefold()
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


def _listado_explicitamente(v, path: str) -> bool:
    """O path esta NOMEADO em `escopo_paths`, e nao coberto por prefixo de diretorio?

    CASEFOLD — achado MEDIA da 19a rodada, e a NONA assimetria entre irmaos deste bloco. A 18a
    rodada deu `.casefold()` a `_cobre()`, e esta funcao — que faz a MESMA pergunta semantica
    ("este path esta declarado no escopo?"), so' que exigindo mencao nominal — ficou sem.

    Esta e' a PRIMEIRA da serie de nove cuja direcao e' puramente FAIL-CLOSED: ela nao deixa passar
    nada; ela REJEITA cobertura legitima. Um critico que revisa um arquivo Python novo e grava
    `escopo_paths: ["Tools/Foo.py"]` tem o veredito recusado, e a unica saida que sobra e'
    `git commit --no-verify` — que a emenda de 18/08/2026, poucas linhas acima, chama de "pior que
    o buraco que ela fecha". Gate que empurra o operador para a escapatoria esta se desarmando
    sozinho, com mais passos.

    Medido antes de fechar (14/09/2026): nenhum `escopo_paths` do ledger depende de diferenca de
    caixa para casar com um arquivo real. Raio nulo.
    """
    p = path.replace("\\", "/").strip().casefold()
    return any(str(e).replace("\\", "/").strip().casefold() == p
               for e in (v.get("escopo_paths") or []))

def _artefato_do_proprio_veredito(v, p) -> bool:
    """`p` e' um dos DOIS arquivos deste mesmo veredito (o .json e o .md irmao)?

    Estreito de proposito: compara com o `_arquivo` que o carregador carimbou, entao um
    veredito nunca pode usar esta porta para cobrir o artefato de OUTRO — e muito menos
    codigo. Veredito sem `_arquivo` (sintetico, de teste, vindo de fora do ledger) nao
    tem artefato proprio e portanto nao tem excecao: fail-closed.
    """
    nome = os.path.basename(str(v.get("_arquivo") or "")).strip()
    if not nome.endswith(".json"):
        return False
    base = nome[:-5]
    alvo = str(p).replace("\\", "/")
    return alvo in ("_meta/qa/" + base + ".json", "_meta/qa/" + base + ".md")


def _blob_indexado(p):
    """Hash do blob de `p` COMO ESTA' NO INDICE, ou None se o git nao responder.

    `git rev-parse :<path>` le o estagio 0 do indice — o conteudo que sera' commitado,
    que e' exatamente o que o critico precisa ter revisado. Cai para `hash-object` no
    arquivo do disco quando o caminho nao esta' indexado (untracked), porque tambem
    nesse caso existe conteudo real a comparar.

    Fail-closed por omissao: devolver None faz o chamador reprovar.

    NORMALIZA O SEPARADOR (achado ALTA da 37a rodada). `git rev-parse :tools\\foo.py` NAO
    resolve contra o indice, e a funcao caia no fallback — que le o DISCO. Num arquivo em
    estado `MM` (staged diferente do disco) isso devolvia o conteudo NAO revisado, que e'
    exatamente o defeito que ja' mordeu este bloco em 16 arquivos. Path com barra invertida
    e' a forma NATIVA no Windows, onde este repo roda: o risco nao e' exotico. Medido: dos
    502 `escopo_paths` do ledger, zero usam barra invertida hoje — risco prospectivo, nao
    passado, e e' por isso que se fecha agora e nao depois.
    """
    p = str(p).replace("\\", "/")
    do_indice = _git("rev-parse", ":" + p)
    if do_indice and _eh_sha_hex(do_indice):
        return do_indice
    do_disco = _git("hash-object", p)
    return do_disco if (do_disco and _eh_sha_hex(do_disco)) else None


def divida_sem_blobs():
    """Vereditos aprovativos que NAO carregam `blobs_revisados`, com quantos paths cobrem.

    Mesmo molde de `legados_declarados()`: campo novo nao invalida veredito antigo — ele
    vira DIVIDA DECLARADA, listada por nome, impressa sem bloquear. Fabricar o hash
    retroativamente seria inventar a procedencia que o campo existe para provar.
    """
    import glob
    import json
    fora = []
    for f in sorted(glob.glob(os.path.join(QA_DIR, "*.json"))):
        try:
            with open(f, encoding="utf-8") as fh:
                v = json.load(fh, object_pairs_hook=_sem_chave_duplicada)
        except Exception as e:
            # DENUNCIA POR NOME, como a irma `legados_declarados()` (achado MEDIA da 37a
            # rodada). A versao anterior tinha um comentario dizendo "ilegivel NAO some daqui
            # em silencio" sobre um `except: continue` que fazia exatamente isso sumir —
            # rotulo divergindo de conteudo, e a DECIMA vez que a assimetria entre funcoes
            # irmas vira achado neste bloco. Em `main()` o sumico ficava mascarado porque a
            # irma denuncia o mesmo arquivo por perto, mas isso e' acidente de ordem de
            # chamada, nao contrato: quem chamar esta funcao isolada nao veria nada.
            # Nao bloqueia, de proposito — quem trava por evidencia ilegivel e' `evaluate`.
            print("[squad-gate] divida sem blobs: %s ignorado (%s: %s)"
                  % (os.path.basename(f), type(e).__name__, e))
            continue
        if v.get("recomendacao") in APPROVING:
            b = v.get("blobs_revisados")
            if not (isinstance(b, dict) and b):
                fora.append((os.path.basename(f), len(v.get("escopo_paths") or [])))
    return sorted(fora)


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
    # CONTEUDO ANTES DE COMMIT (achado ALTA da 36a rodada, 21/09/2026).
    #
    # Tudo abaixo desta guarda mede ANCESTRALIDADE DE COMMIT — e no pre-commit de um bloco
    # isso e' medir o que nao muda: por definicao, todo arquivo do bloco esta' fora do HEAD,
    # entao `merge-base --is-ancestor` responde a mesma coisa antes e depois de qualquer
    # edicao nao commitada. Reproduzido: tres vereditos aprovativos de AGOSTO seguiam
    # "recentes" para `tools/run_canaries.py` e `tools/projeto_docs.py` editados em SETEMBRO.
    #
    # O hash do blob indexado e' a unica coisa que descreve conteudo nao commitado. Quando o
    # veredito o carrega, ele SUBSTITUI a ancestralidade em vez de somar-se a ela: hash igual
    # prova que o conteudo e' byte a byte o que o critico leu, o que e' estritamente mais
    # forte do que "o commit que tocou o arquivo e' ancestral do revisado".
    #
    # Sem o campo, cai na regra antiga — e entra no relatorio de `divida_sem_blobs()`. Campo
    # novo nao e' retroativo; fabricar hash para veredito velho seria inventar procedencia.
    # PISO INEGOCIAVEL, ANTES do atalho (achado CRITICO da 37a rodada, reproduzido ao vivo).
    #
    # A 1a versao deste bloco vinha ANTES da validacao de `sha_revisado`, e o `return True`
    # pulava tanto `_eh_sha_hex` quanto o `cat-file -e`. Parecia inofensivo — "o hash de
    # conteudo e' mais forte que a ancestralidade" — e era falso, porque `sha_revisado` NAO
    # serve so' a esta funcao: e' a CHAVE que `_reprovacao_vigente` usa para achar a
    # reprovacao irma do MESMO estado do codigo. Com sha invalido, `_sha_pleno` devolve ""
    # e a comparacao nunca casa: uma reprovacao legitima, com CRITICO aberto no mesmo
    # escopo, deixava de invalidar o aprovativo. Reproduzido pelo critico com
    # `sha_revisado: "HEAD"` (que o proprio comentario de `_eh_sha_hex` chama de erro de
    # digitacao plausivel) e tambem com "deadbeef": `_qa_critic_attested` devolveu True.
    #
    # E' a reabertura do defeito que as rodadas 8, 9 e 10 levaram tres tentativas para
    # fechar. O atalho novo pode dispensar a ANCESTRALIDADE; nao pode dispensar a
    # IDENTIDADE do commit revisado.
    sha = str(v.get("sha_revisado", "") or "").strip()
    if not _eh_sha_hex(sha):
        return False
    if _git("cat-file", "-e", sha + "^{commit}") is None:
        return False

    blobs = v.get("blobs_revisados")
    if isinstance(blobs, dict) and blobs:
        for p in paths:
            gravado = str(blobs.get(p, "") or "").strip()
            if _artefato_do_proprio_veredito(v, p):
                # A REGRESSAO INFINITA, quebrada onde o repo ja' a quebrava.
                #
                # O artefato de um veredito nao pode carregar o hash de si mesmo: no
                # instante em que `write_artifact` carimba, o arquivo ainda nao existe —
                # e quando existe, por ser uma REgravacao, o que se carimba e' o conteudo
                # ANTERIOR, que a gravacao seguinte torna obsoleto no mesmo segundo. Por
                # isso a excecao ignora o carimbo em vez de exigir a ausencia dele: um
                # auto-carimbo e' sempre stale por construcao, nunca prova nada, e
                # `write_artifact` deixou de grava-lo.
                # Cobri-lo por um veredito seguinte apenas empurra o problema — o artefato
                # DAQUELE ficaria descoberto, e assim para sempre.
                #
                # Este repo ja' quebra a regressao por convencao: 15 vereditos declaram os
                # proprios `_meta/qa/*.json|.md` em `escopo_paths`. A regra de conteudo nao
                # pode tornar impossivel o que a regra antiga permitia, senao o efeito
                # pratico e' empurrar para `--no-verify`. Entao a excecao e' EXPLICITA e
                # ESTREITA: vale so' para os dois arquivos do PROPRIO veredito, nunca para
                # o artefato de outro, e nunca para codigo. [37a rodada]
                continue
            if not _eh_sha_hex(gravado):
                return False      # path avaliado que o veredito nao carimbou: fail-closed
            atual = _blob_indexado(p)
            if atual is None or atual != gravado:
                return False      # conteudo mudou depois da revisao, ou git nao respondeu
        return True

    # (`sha` ja' foi validado no piso acima: hex de verdade E commit existente neste repo —
    #  ausente ou simbolico ("HEAD", "main") reprovou la', achado da 10a rodada.)
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
            #
            # EMENDA (2026-08-18): o `return False` seco tinha um efeito nao-intencionado —
            # tornava TODO arquivo novo permanentemente nao-commitavel, sem caminho legitimo
            # para o primeiro commit. Medido ao adicionar `tools/test_skill_contract.py`: o
            # arquivo FOI revisado pelo qa-critic, estava no `escopo_paths`, e mesmo assim o
            # unico jeito de commitar seria `--no-verify` — ou seja, a regra empurrava para o
            # bypass, que e' pior do que o buraco que ela fecha.
            #
            # O criterio que separa os dois casos e' o TIPO de cobertura, nao a existencia de
            # historico: escopo AMPLO (prefixo `tools/`) nao pode alcancar arquivo que nunca
            # existiu — e' exatamente a lavagem que a 8a rodada barrou. Escopo EXPLICITO (o
            # path exato, digitado no veredito) so pode ter sido escrito por quem sabia que
            # aquele arquivo existe: e' declaracao de que o critico o viu.
            if not _listado_explicitamente(v, p):
                return False
            # Achado ALTO do qa-critic (2026-08-18): so o path explicito NAO basta. Sem
            # `ultimo` nao existe `merge-base --is-ancestor` para rodar, entao neste ramo o
            # `sha_revisado` ficava DECORATIVO — um veredito com o sha do primeiro commit da
            # historia liberava um arquivo novo (reproduzido ao vivo pelo critico). Era a
            # versao estreita do "revisado uma vez = liberado para sempre" que este arquivo
            # ja tratou como bloqueante duas vezes (B2/B2-r2 e 7a rodada).
            #
            # Sem commit do arquivo para ancorar, a unica aproximacao de "o veredito e' atual"
            # e' "foi emitido na ponta corrente da branch".
            #
            # LIMITE DECLARADO: isto NAO cobre edicao do arquivo DEPOIS do veredito e ANTES do
            # commit — sem historico, o git nao tem como registrar essa mudanca. Fechar isso
            # exigiria carimbar hash de CONTEUDO no veredito e compara-lo aqui; fica como
            # debito explicito, nao como propriedade que este gate finge ter.
            # Normaliza os DOIS lados: os vereditos reais gravam sha CURTO (7 chars) e
            # `rev-parse HEAD` devolve os 40. Comparar as strings cruas reprovava veredito
            # legitimo — pego ao usar a emenda pela primeira vez, minutos depois de escreve-la.
            if _git("rev-parse", sha) != _git("rev-parse", "HEAD"):
                return False
            continue
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
    if _um_veredito_cobre(artifacts, alvo):
        return True
    # UNIAO POR CAMINHO (achado MEDIA da 36a rodada, fechado na 37a).
    #
    # A regra anterior exigia UM veredito cujo escopo cobrisse TODOS os caminhos avaliados,
    # e nunca a uniao entre eles. O efeito pratico era o inverso do pretendido: para fechar
    # um bloco de 91 caminhos era preciso um veredito que DECLARASSE os 91 — e nenhum
    # critico sozinho revisou 91 arquivos. A regra fabricava o veredito-cobertor, cuja forma
    # sugere um exame unico que nao houve. O proprio veredito da 36a registrou isso contra si.
    #
    # PRECISAO SOBRE O QUE MUDA — corrigida pelo critico da 38a rodada, e a correcao e' contra
    # mim: a 1a versao deste comentario dizia "mais estrito que avaliar o conjunto", e isso e'
    # FALSO numa dimensao que ele reproduziu contra o binario. `_reprovacao_vigente` usa
    # `any()` sobre o alvo; avaliada por caminho, ela deixa de desqualificar um veredito por
    # causa de reprovacao que cai sobre OUTRO caminho do mesmo escopo amplo. O veto fica mais
    # CIRURGICO — nao contamina vizinhos —, e isso nao e' a mesma coisa que mais estrito.
    #
    # Nao vira bypass, e ele provou por execucao: o caminho de fato reprovado continua falhando
    # o proprio `_um_veredito_cobre`, e o `all()` abaixo exige TODOS os caminhos staged — o
    # commit segue bloqueado. Cada caminho continua exigindo veredito aprovativo, atestado,
    # escopado, recente e sem reprovacao vigente SOBRE ELE. O que a uniao remove e' o incentivo
    # a inflar `escopo_paths`, que era o unico jeito de passar.
    if not alvo:
        return False
    return all(_um_veredito_cobre(artifacts, [p]) for p in alvo)


def _um_veredito_cobre(artifacts, alvo) -> bool:
    """Existe UM veredito valido cujo escopo cobre TODOS os caminhos de `alvo`?

    Alvo VAZIO devolve False (achado BAIXA da 38a rodada). `all(... for p in [])` e' verdade
    por vacuidade, entao a versao anterior devolvia True sempre que houvesse QUALQUER veredito
    valido no ledger, com QUALQUER escopo. Nao era exploravel — o unico chamador real passa o
    que esta' staged, e `classify()` nunca exige `qa_critic` para lista vazia — e e' anterior
    a uniao, herdado intacto na extracao. Fecha-se assim mesmo: vacuidade logica num gate e'
    divida que so' cobra juros quando alguem acrescentar o segundo chamador.
    """
    if not alvo:
        return False
    for v in artifacts:
        if not _atestacao_valida(v):
            continue
        escopo = v.get("escopo_paths") or []
        if not escopo:
            continue  # sem escopo declarado -> nao serve de evidencia (fail-closed)
        if not all(_cobre(escopo, p) for p in alvo):
            continue
        # escopo cobre, mas o veredito e' anterior as edicoes? (emenda 3, 7a rodada)
        if not _recente_o_bastante(v, alvo):
            continue
        # ha REPROVACAO vigente para o mesmo estado do codigo e o mesmo escopo? (ADR-115, 8a rodada)
        if _reprovacao_vigente(artifacts, v, alvo):
            continue
        return True
    return False


def _reprovacao_vigente(artifacts, aprovativo, alvo) -> bool:
    """Existe veredito REPROVATIVO cobrindo os mesmos paths, no mesmo `sha_revisado`?

    O laco acima devolvia True no PRIMEIRO aprovativo que encontrasse, sem olhar se havia uma
    reprovacao ao lado para o mesmo estado do codigo. Bastava depositar em _meta/qa/ um segundo
    JSON aprovativo, vazio de achados, com o mesmo escopo e o mesmo sha, para o gate liberar o
    commit com um CRITICO em aberto na porta ao lado — o aprovativo vencia sempre, ate quando era
    o mais fraco.

    RETRATACAO (9a rodada): a versao anterior deste docstring afirmava que "o mecanismo ja existia
    para o papel `juncao_release` e nunca havia sido estendido ao `qa_critic`". Isso era FALSO.
    Nunca existiu em lugar nenhum — eu inferi a existencia pelo NOME de um teste
    (`test_juncao_release_REPROVACAO_POSTERIOR_invalida_o_PC`) que na verdade cobre outro caso, e
    entreguei a inferencia como fato no codigo e no ADR. `_release_verdict_approving` tinha o mesmo
    buraco e foi corrigido na mesma rodada.

    Duas formas de escapar, ambas reproduzidas contra o binario real na 9a rodada, ambas
    dependentes de pratica JA DOMINANTE no ledger, nao de malicia:

    1. **Reprovacao sem `escopo_paths`.** O campo e' opcional (`qa_evidence.py` nao o exige), e a
       versao anterior fazia `if escopo_r and ...`: sem escopo, a reprovacao nao "cobria" nada e
       nunca invalidava. Agora escopo ausente/vazio **cobre tudo** — fail-closed. Reprovacao que
       nao delimita o que revisou e' mais ampla, nao mais estreita.
    2. **Sha curto x longo.** `_recente_o_bastante` ja normalizava (27 dos 29 vereditos com
       `sha_revisado` gravam a forma de 7 caracteres; `rev-parse HEAD` devolve 40) e esta funcao
       nao recebeu a mesma correcao — comparava string crua. Mesmo commit, grafias diferentes,
       deteccao perdida. Agora ambos os lados passam por `_sha_pleno`.
    3. **Reprovacao JA TRATADA travava para sempre** (achado do proprio autor, entre a 9a e a 10a
       rodada). A funcao contava qualquer reprovacao de mesmo sha+escopo, sem olhar se restava
       achado bloqueante ABERTO — enquanto o irmao `_reprovacao_de_release_vigente`, escrito na
       mesma rodada, tres funcoes abaixo, ja olhava. Assimetria entre irmaos pela terceira vez
       neste ADR, agora dentro do mesmo commit. Importa porque neste fluxo a correcao acontece na
       ARVORE DE TRABALHO: o commit nao muda, logo reprovacao e aprovativo compartilham o
       `sha_revisado`, e o gate travaria o proprio bloco que corrigiu tudo. Fail-closed vira
       travado, que nao e' a mesma coisa.

    LIMITE DECLARADO — reprovacao SEM `sha_revisado` nao e' considerada vigente. Nao da' para saber
    a que estado do codigo ela se refere, e trata-la como universal bloquearia todo commit do
    repositorio ate alguem resolver ou assinar achados antigos. Medido em 15/09/2026: DEZENAS de reprovacoes nao declaram sha (o numero
    cresce a cada rodada de QA, por isso nao vale congela-lo aqui), e entre as que ainda tem achado
    bloqueante ABERTO ha UMA (`v1.49-1.50-process-evidence-review.json`, de 08/06/2026, schema
    antigo sem o campo `estado`) que tambem nao declara escopo — sozinha, ela bloquearia o repositorio inteiro. Fechar esta porta
    e' decisao do dono, com esse custo na mesa, nao do autor.
    """
    sha = _sha_pleno(aprovativo.get("sha_revisado"))
    if not sha:
        return False                       # aprovativo sem sha nao passa em _recente_o_bastante
    for r in artifacts:
        if not isinstance(r, dict) or r is aprovativo:
            continue
        if str(r.get("recomendacao") or "").strip() in APPROVING:
            continue                       # so reprovacoes interessam aqui
        if _sha_pleno(r.get("sha_revisado")) != sha:
            continue                       # reprovacao de outro estado do codigo nao vale
        if _reprovacao_tratada(r):
            continue                       # reprovacao ja tratada nao trava (ver docstring)
        escopo_r = r.get("escopo_paths") or []
        if not escopo_r or any(_cobre(escopo_r, p) for p in alvo):
            return True                    # sem escopo declarado => cobre tudo (fail-closed)
    return False


def _eh_sha_hex(s) -> bool:
    """`sha_revisado` e' um HASH, nao uma referencia. Achado CRITICO da 10a rodada.

    `rev-parse --verify <x>^{commit}` resolve QUALQUER ref valida: `HEAD`, `main`, uma tag. E ref
    simbolica SE MOVE. Um veredito com `sha_revisado: "HEAD"` nunca envelhece — a cada execucao do
    gate, "HEAD" vira o HEAD daquele momento, e o veredito passa a cobrir codigo que ninguem
    revisou. Isso reabre exatamente o B2/B2-r2 ("revisado uma vez = liberado para sempre") que
    `_recente_o_bastante` existe para fechar, agora pela porta do FORMATO em vez da ausencia.

    Nao precisa de malicia: `sha_revisado: "HEAD"` e' erro de digitacao plausivel. E a licao deste
    ADR inteiro se aplica de novo — nao adianta enumerar as refs proibidas (`HEAD`, `main`, tags,
    `@`, `HEAD~1`...); enumera-se a forma CERTA: hexadecimal, de 7 a 40 caracteres.
    """
    s = str(s or "").strip()
    return 7 <= len(s) <= 40 and all(c in "0123456789abcdefABCDEF" for c in s)


def _sha_pleno(sha) -> str:
    """Resolve `sha_revisado` para a forma de 40 caracteres, para comparar mesmo commit escrito
    de duas maneiras. Sem git, ou sha que nao existe aqui, devolve a string normalizada — assim
    duas grafias iguais ainda casam e o fail-closed nao vira fail-open por falta de ferramenta.

    Entrada que nao tem forma de hash e' recusada antes de chegar ao git (ver `_eh_sha_hex`)."""
    s = str(sha or "").strip()
    if not _eh_sha_hex(s):
        return ""
    pleno = _git("rev-parse", "--verify", "--quiet", s + "^{commit}")
    return pleno or s


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

    9a RODADA: esta funcao devolvia True no PRIMEIRO aprovativo que declarasse o release, sem olhar
    se havia REPROVACAO do mesmo release ao lado, com achado bloqueante em aberto. Era o buraco da
    8a rodada, intacto no papel irmao — o que porteia releases INTEIROS. O teste que parecia cobrir
    isso (`test_juncao_release_REPROVACAO_POSTERIOR_invalida_o_PC`) cobre outro caso: reprovacao
    SOZINHA, sem aprovativo, que ja nao fecharia de qualquer forma. Nome de teste nao e' cobertura.
    """
    for v in artifacts:
        if not _atestacao_valida(v):        # já exige recomendacao aprovativa + agentId + modelo != autor
            continue
        if not (_declara_release(v, padrao)):
            continue
        if _reprovacao_de_release_vigente(artifacts, v, padrao):
            continue                        # ha reprovacao aberta para o MESMO release
        return True
    return False


def _declara_release(v, padrao) -> bool:
    """O veredito fala deste release? Casa `release` ("1.79.0") e, por tolerancia, `bloco`
    ("release-1.79.0-..."), sem cair em substring solta."""
    rel = str(v.get("release", "")).strip()
    if rel and padrao.match(rel):
        return True
    bloco = str(v.get("bloco", "")).strip()
    return bool(bloco.startswith("release-") and padrao.match(bloco[len("release-"):]))


def _reprovacao_de_release_vigente(artifacts, aprovativo, padrao) -> bool:
    """Ha veredito REPROVATIVO do mesmo release com achado bloqueante em aberto?

    Irmao de `_reprovacao_vigente`, separado porque a identidade aqui e' o RELEASE, nao o par
    (sha, escopo). Mesma regra: aprovativo nao vence reprovacao coexistente."""
    for r in artifacts:
        if not isinstance(r, dict) or r is aprovativo:
            continue
        if str(r.get("recomendacao") or "").strip() in APPROVING:
            continue
        if _declara_release(r, padrao) and not _reprovacao_tratada(r):
            return True
    return False


def _reprovacao_tratada(r) -> bool:
    """A reprovacao ja foi resolvida, ou ainda pesa? Achado CRITICO da 11a rodada.

    A versao anterior perguntava so `achados_bloqueantes_abertos(r)`, e uma reprovacao que NUNCA
    declarou achado estruturado — `recomendacao: "reprovar"`, motivo escrito em `resumo`, campo
    `problemas` vazio ou ausente — caia no mesmo ramo de "ja tratada" e nao vetava NADA. E' este
    ADR ao contrario: as dez rodadas anteriores perseguiram o aprovativo que esconde achado, e
    sobrou o inverso, a reprovacao que nao mostra achado nenhum e por isso e' lida como inofensiva.

    A regra certa separa "resolvida" de "muda": so' esta tratada quem DECLAROU achados e nao
    deixou nenhum bloqueante em aberto. Reprovacao sem achado estruturado diz "reprovo" e nao diz
    do que; concluir dai' que foi resolvida e' fail-open.

    Raio de explosao medido antes de fechar: NENHUMA reprovacao do ledger deixava de declarar
    `problemas`. Nenhum trabalho legitimo passa a ser barrado. Sem numero absoluto aqui — a
    populacao muda a cada rodada e comentario nao tem quem o recalcule (licao da 12a rodada).

    Usada pelos DOIS irmaos, `_reprovacao_vigente` e `_reprovacao_de_release_vigente`, na mesma
    edicao. Este ADR ja registrou tres vezes a correcao aplicada num irmao e esquecida no outro;
    na quarta, o predicado nasce compartilhado em vez de duplicado.
    """
    p = r.get("problemas")
    if not isinstance(p, list) or not p:
        return False                       # sem achado declarado nao ha' como saber que foi tratada
    return not achados_bloqueantes_abertos(r)


def _research_atestada(paths) -> bool:
    """Delega ao `research_evidence.py` — a ferramenta que o manifesto nomeia como `check`.

    Roda como SUBPROCESSO de proposito: o contrato entre os dois e' o codigo de saida, o mesmo
    que a CI e o gancho de pre-commit consomem. Importar a funcao acoplaria os dois modulos e
    faria este gate testar um caminho diferente do que roda de verdade.

    Ferramenta ausente ou quebrada => False (fail-closed). Aqui o silencio nao libera: o papel
    so' e' exigido para numero regulado, e passar por omissao seria pior que barrar.
    """
    alvo = os.path.join(ROOT, "tools", "research_evidence.py")
    if not os.path.isfile(alvo):
        return False
    try:
        r = subprocess.run([sys.executable, alvo, "--paths", *[str(p) for p in paths]],
                           capture_output=True, text=True, cwd=ROOT, timeout=60,
                           stdin=subprocess.DEVNULL)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def evaluate(paths, manifest, artifacts):
    """Retorna (faltam, detalhe). faltam=[] => gate PASSA."""
    required = classify(paths, manifest)
    faltam, detalhe = [], {}

    # Evidencia ILEGIVEL trava o gate inteiro, antes de qualquer papel ser avaliado (25a rodada).
    # Nao da' para decidir com o ledger corrompido: o arquivo ruim pode ser justamente a reprovacao
    # que derrubaria o aprovativo. "Nao consigo confirmar" e' NAO PASSA, nunca "segue sem ela".
    _ilegiveis = [a.get("_recusado") for a in artifacts
                  if isinstance(a, dict) and a.get("_recusado")]
    if _ilegiveis:
        detalhe["evidencia_integra"] = False
        return ["evidencia_integra"], detalhe
    for role in sorted(required):
        if role == "qa_critic":
            ok = _qa_critic_attested(artifacts, paths)
        elif role == "architect":
            # DECIMA assimetria entre irmaos (20a rodada): `classify()` casefolda o path antes
            # de decidir se `architect` e' EXIGIDO, e esta linha — que decide se ele foi
            # SATISFEITO — comparava cru. Um ADR salvo como `Docs/ADR/199-foo.md` era classificado
            # como exigindo architect e nunca podia satisfaze-lo. Direcao fail-closed, igual a nona:
            # nao deixa passar nada, recusa cobertura legitima e empurra para `--no-verify`.
            ok = any(str(p).replace("\\", "/").casefold().startswith("docs/adr/") for p in paths)
        elif role == "juncao_release":
            ok = _release_junction_closed(artifacts)
        else:
            # research_ou_ratificacao / busca_exaustiva: delegado a `research_evidence.py`,
            # conforme o campo `check` do proprio manifesto. Ate 2026-08-16 a ferramenta nao
            # existia e este ramo devolvia False fixo — fail-closed correto, mas SEM caminho
            # para passar: quem mexesse num numero regulado ficava barrado para sempre.
            ok = _research_atestada(paths)
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
        try:
            r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                               capture_output=True, text=True, cwd=ROOT)
        except OSError as e:
            # git ausente do PATH levantava FileNotFoundError e o processo morria com traceback.
            # O efeito liquido ja era fail-closed (exit != 0), mas a mensagem era ilegivel e
            # diferente da do irmao `_git()`, que sempre capturou OSError. BAIXA da 15a rodada.
            print("[squad-gate] BLOQUEADO (fail-closed): nao consegui executar o git (%s)." % e)
            return 1
        # CRITICO da 14a rodada, e o mais grave do bloco: a versao anterior lia `r.stdout` sem
        # olhar `r.returncode`. Git que FALHA devolve stdout vazio — e "nao consegui perguntar"
        # virava "nao ha nada staged". Sem papel exigido, o gate imprimia OK e saia 0.
        #
        # O agravante esta no consumidor: `tools/install_git_hooks.py` instala exatamente esta
        # invocacao como pre-commit e so' inspeciona a mensagem quando o codigo e' != 0. Com 0 ele
        # libera direto. O commit passava sem nenhuma evidencia avaliada e SEM AVISO.
        #
        # Nao e' hipotese de laboratorio: `fatal: detected dubious ownership in repository` (git
        # >= 2.35.2, pos-CVE-2022-24765) acontece em drive de rede, container, CI e em qualquer
        # checkout cujo dono nao bate com quem roda — que e' o caso de metade das maquinas deste
        # projeto. Indice corrompido e checkout incompleto dao o mesmo par (stdout vazio, rc != 0).
        #
        # O helper `_git()` deste mesmo arquivo SEMPRE conferiu o returncode. A licao "assimetria
        # entre irmaos" pela quinta vez: o padrao certo existia a 400 linhas de distancia.
        if r.returncode != 0:
            print("[squad-gate] BLOQUEADO (fail-closed): nao consegui perguntar ao git o que esta "
                  "staged (git saiu %d)." % r.returncode)
            erro = (r.stderr or "").strip().splitlines()
            if erro:
                print("   git disse: %s" % erro[0])
            print("   Silenciar isso como 'nada staged' liberaria o commit sem avaliar evidencia "
                  "nenhuma. Conserte o git (ex.: `git config --global --add safe.directory <repo>`) "
                  "e rode de novo.")
            return 1
        paths = [x for x in r.stdout.splitlines() if x.strip()]
    manifest = load_manifest()
    artifacts = load_evidence()
    faltam, detalhe = evaluate(paths, manifest, artifacts)
    req = classify(paths, manifest)
    print(f"[squad-gate] {len(paths)} path(s) staged -> papeis exigidos: {sorted(req) or 'nenhum'}")
    for role, ok in detalhe.items():
        print(f"   {'OK ' if ok else 'FALTA'} {role}")
    # A divida legada e' IMPRESSA, nao so calculavel: o ADR afirma que ela "fica visivel em vez
    # de perdoada em silencio", e afirmacao de documento tem de ser verdadeira no mecanismo que
    # de fato roda. A revisao adversarial pegou a funcao existindo sem nenhum chamador real.
    #
    # ANTES da decisao de passar ou bloquear, de proposito (achado do autor na 20a rodada): a
    # versao anterior imprimia so' no caminho de SUCESSO, o que tornava a afirmacao do ADR uma
    # meia-verdade — e na metade errada, porque quem esta BLOQUEADO e' justamente quem mais
    # precisa ver o passivo que o repositorio carrega. Quem descobriu foi o teste que passou a
    # EXECUTAR `main()` em vez de grepar o fonte: ele ficou vermelho no baseline da prova por
    # mutacao, onde o gate bloqueia.
    _leg = legados_declarados()
    if _leg:
        print("[squad-gate] divida legada declarada (ADR-115): %d veredito(s) aprovativo(s) "
              "anteriores ao campo `estado`, com %d achado(s) bloqueante(s) nao rastreados "
              "por campo." % (len(_leg), sum(n for _, n in _leg)))
        for _f, _n in _leg:
            print("             · %-58s %d" % (_f, _n))
    _sb = divida_sem_blobs()
    if _sb:
        print("[squad-gate] divida declarada (36a rodada): %d veredito(s) aprovativo(s) sem "
              "`blobs_revisados` — cobrem por ancestralidade de commit, que nao enxerga "
              "edicao nao commitada." % len(_sb))
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
